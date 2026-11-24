#!/usr/bin/env python3
"""The hooks behind /be-ambitious and the /ambition steps. They keep the plugin invisible to Claude until
it's needed, so the first turn is exactly what Claude makes from a plain prompt.

  prompt  /be-ambitious [task] at the start of a session is blocked before it reaches Claude, so Claude never
          sees it, and the session is armed. The user's next message is the task, typed as they always would.
          Later in a session, /be-ambitious on its own pushes the work already done, or, mid-push, picks the
          push up where it is. The first /ambition step in a session gets the working rules every step follows.
  stop    When the armed session's first turn ends, continue it once: ask how to push it further (step by
          step, or straight through). When Claude ends a message with the line naming the choice, continue
          with step 2's instruction. After that, each time Claude ends with `▪ Step n/8 done`, continue with
          step n+1's instruction and nothing else, like a person typing the next command. `▪ Step n/8 · over
          to you` means the user is reviewing the step: stay quiet until Claude ends a later turn with done.
Everything else passes straight through.

The hand-offs are `additionalContext`, never a block: a block shows the user its whole text as a red "Stop hook
error". `additionalContext` is cut to a 2 KB preview past about 10,000 characters, so every hand-off stays under
LIMIT. Claude never gets the method as a whole (SKILL.md, reference/): each step gets only its own short
instruction, like the essay's one prompt at a time. Sending the whole method was measured on the bench
(design/pricing-page, Sonnet, run-4 against run-5) and was slower and no better.
Instructions travel as hook text, never as file paths: reading plugin files from a project needs permission.
Nothing is copied into the user's project. The bench sets AMBITION_SNAPSHOT=1, and then the hook itself
snapshots the project to .ambition/first/ and .ambition/steps/<n>/ as evidence, with Claude told nothing.
"""
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone

ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METHOD = os.path.join(ROOT, "skills", "ambition-method")
METRICS = os.path.join(ROOT, "scripts", "ambition-metrics.py")
COMMANDS = os.path.join(ROOT, "commands")
# Steps 2-8 of a push: (name, the manual command whose instruction it runs). Altitude's is push.md's own.
STEPS = {2: ("Altitude", None), 3: ("Depth", "ambition-b-depth"), 4: ("Challenge", "ambition-c-challenge"),
         5: ("Range", "ambition-d-range"), 6: ("Judge", "ambition-e-judge"), 7: ("Stretch", "ambition-f-stretch"),
         8: ("Lock", "ambition-g-lock")}
# Per-session marks. The plugin's data folder survives between calls (and between the bench's containers).
STATE = os.path.join(os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(tempfile.gettempdir(), "claude-ambition"), "sessions")
FRONT = re.compile(r"/(?:[\w-]+:)?be-ambitious(?:\s+(.*))?", re.S)
STEP = re.compile(r"/(?:[\w-]+:)?ambition(?:-[a-g]-[\w-]+)?(?:\s.*)?", re.S)
# The lines Claude ends a message with. Matched loosely (bold, a trailing full stop) in the last few lines.
CHOICE = re.compile(r"▪\W*Push:\s*(step by step|straight through)", re.I)
DONE = re.compile(r"▪\W*Step\s*(\d)\s*/\s*8\W*done\b", re.I)
WAITING = re.compile(r"▪\W*Step\s*(\d)\s*/\s*8\W*over to you\b", re.I)
LIMIT = 9500  # a hand-off longer than ~10,000 characters reaches Claude as a 2 KB preview and a file path
SNAPSHOT_SKIP = {".ambition", ".plain", ".git", "node_modules", ".venv", "venv", "__pycache__", ".cache", ".next"}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def mark(session, kind):
    safe = re.sub(r"[^\w-]", "-", session or "none")
    return os.path.join(STATE, f"{safe}.{kind}")


def write_mark(session, kind, text=""):
    os.makedirs(STATE, exist_ok=True)
    with open(mark(session, kind), "w") as f:
        f.write(text)


def last_prompt(path):
    """The user's latest real prompt in the transcript, with its timestamp: not a tool result, not text
    Claude Code adds itself (expanded command bodies, hook feedback,
    local commands such as /model)."""
    found, local = (None, None), False
    if not path or not os.path.exists(path):
        return found
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"type":"user"' not in line or '"tool_result"' in line:  # cheap filter before parsing
                continue
            m = json.loads(line)
            if m.get("type") != "user":
                continue
            c = m.get("message", {}).get("content")
            text = (c if isinstance(c, str) else " ".join(b.get("text", "") for b in c or [] if b.get("type") == "text")).strip()
            # A local command (/model, /plugin, ...) is a caveat, the command and its output, the last two
            # without isMeta. They aren't prompts: counting them made /be-ambitious push instead of arming.
            # Prompt commands (/bugfix X) carry no caveat, so they still count as work.
            if text.startswith("<local-command-caveat>"):
                local = True
                continue
            if m.get("isMeta") or text.startswith(("<local-command-stdout>", "<local-command-stderr>")):
                continue
            if local and "<command-name>" in text:
                local = False
                continue
            local = False
            found = (text, m.get("timestamp"))
    return found


def last_reply(data):
    """The end of Claude's last message: the Stop input carries it; older versions only have the transcript."""
    text = data.get("last_assistant_message")
    if text is None:
        text, path = "", data.get("transcript_path")
        if path and os.path.exists(path):
            with open(path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if '"type":"assistant"' in line:
                        blocks = json.loads(line).get("message", {}).get("content") or []
                        said = "\n".join(b.get("text", "") for b in blocks if isinstance(b, dict) and b.get("type") == "text")
                        text = said or text
    return "\n".join((text or "").strip().splitlines()[-4:])


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def push_parts():
    """push.md split into its preamble, its Every step rules and {n: that step's section}."""
    head, *rest = re.split(r"^## Step (\d) · [^\n]*$", read(os.path.join(METHOD, "push.md")), flags=re.M)
    preamble, every = head.split("## Every step", 1)
    return preamble.strip(), every.strip(), {int(n): body.strip() for n, body in zip(rest[::2], rest[1::2])}


def rules_text():
    """push.md's Every step rules for the manual /ambition steps, minus the one about a push's step-by-step review."""
    every = push_parts()[1]
    keep = [b for b in re.split(r"\n(?=- )", every) if not b.startswith("- **Reviewing.**")]
    return ("How to work on the /ambition steps in this conversation. Each step's instruction is the command the user "
            "types.\n\n" + "\n".join(keep))


def command_text(name):
    """A manual step's instruction as the user would get it by typing the command, minus its pointers."""
    body = re.sub(r"\A---\n.*?\n---\n", "", read(os.path.join(COMMANDS, name + ".md")), count=1, flags=re.S)
    skip = ("Apply to:", "End with:")
    return "\n".join(l for l in body.splitlines() if not l.startswith(skip)).strip()


def step_text(n, session, started, reviewing=False):
    """Everything Claude gets for step n of a push, and nothing about the other steps."""
    name, command = STEPS[n]
    _, every, sections = push_parts()
    parts = [f"Step {n} of pushing the work further: {name}. Open your first message with this line on its own, "
             f"exactly: `▸ Step {n}/8 · {name}`. Write that line nowhere else."]
    if command:
        parts.append(command_text(command))
    parts.append(sections[n])
    if n == 8:
        parts.append(f"Run started: {started}\nMetrics command for the end: python3 {METRICS} {session} --since {started}")
    if reviewing:
        parts.append(f"The user is reviewing each step. When this step is finished, end with a short step report (did / "
                     f"found / changed course) and this line on its own, as the very last line: `▪ Step {n}/8 · over to "
                     f"you`, and stop. Their reply is notes to steer by or a go-ahead: act on it, then end with `▪ Step "
                     f"{n}/8 done`. " + ("The push ends there." if n == 8 else "The next instruction arrives then.")
                     + " While you're waiting on the user for anything else (a question, an approval), end with neither line.")
    else:
        parts.append(f"When this step is finished, end with a short step report (did / found / changed course) and this "
                     f"line on its own, as the very last line: `▪ Step {n}/8 done`. "
                     + ("The push ends there." if n == 8 else "The next instruction arrives then.")
                     + f" If the user asks to review each step, end it with `▪ Step {n}/8 · over to you` instead and stop; "
                     f"after their reply, end with done. While you're waiting on the user for anything else (a question, "
                     f"an approval), end with neither line.")
    return "\n\n".join(parts) + "\n\n## Every step\n\n" + every


def push_text(session, started, reviewing=False):
    """push.md's preamble and step 2: all Claude needs to begin pushing on. Like the essay, each step is a short
    prompt of its own; the method as a whole (SKILL.md, reference/) isn't sent, so no step sees the others.
    (Sending the whole method first was tried on the bench, design/pricing-page run-4: slower, no better.)"""
    return push_parts()[0] + "\n\n---\n\n" + step_text(2, session, started, reviewing)


def begin_push(session, started, mode):
    """Step 2 is under way: from here the Stop hook hands out the later steps."""
    write_mark(session, "step", f"2 {started} {mode}")
    for k in ["checkpoint", "replied", "nudged-choice"] + [f"nudged-{i}" for i in STEPS]:
        if os.path.exists(mark(session, k)):
            os.remove(mark(session, k))


def end_push(session):
    for k in ["step", "checkpoint", "replied", "nudged-choice", "waiting"] + [f"nudged-{i}" for i in STEPS]:
        if os.path.exists(mark(session, k)):
            os.remove(mark(session, k))


def snapshot(data, name):
    """Bench only (AMBITION_SNAPSHOT=1): copy the project to .ambition/<name>/ as evidence. Claude isn't told."""
    if os.environ.get("AMBITION_SNAPSHOT") != "1":
        return
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    dest = os.path.join(root, ".ambition", name)
    import shutil
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(root, dest, symlinks=True, ignore=lambda d, names: [n for n in names if n in SNAPSHOT_SKIP])


def checkpoint():
    return (
        "Before you finish, unless the task was trivial (a typo, a rename, a one-line answer), end with one "
        "question, using AskUserQuestion when it's available:\n"
        "- Push it further, step by step: they see each step's result and reply with notes or a go-ahead before "
        "the next one.\n"
        "- Push it further: the steps run straight through.\n"
        "Above the question, name the two or three improvements you'd go after, and roughly what pushing on costs "
        "against what's been spent so far. Ask nothing else. Keep this brief: your reply about the work is already "
        "above.\n\n"
        "If they choose to push on, end your next message with exactly one of these lines, on its own, as its very "
        "last line, and stop: `▪ Push: step by step` or `▪ Push: straight through`. The instructions arrive then. "
        "If they'd rather stop, stop."
    )


def context(event, text):
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


def on_prompt(data):
    prompt, session = (data.get("prompt") or "").strip(), data.get("session_id")
    front = FRONT.fullmatch(prompt)
    if front:
        task = (front.group(1) or "").strip()
        if not task and os.path.exists(mark(session, "step")):
            n, started, *mode = read(mark(session, "step")).split()
            n = int(n)
            return ("The user typed /be-ambitious while a push of the work is under way, at step "
                     f"{n}/8 · {STEPS[n][0]}. Tell them that in one line, then carry on with that step.\n\n"
                     + step_text(n, session, started, mode[:1] == ["review"]))
        if not task and last_prompt(data.get("transcript_path"))[0]:
            started = now()
            begin_push(session, started, "straight")
            return ("The user wants the work already done in this conversation pushed further with the ambition "
                     "method. That work is the first version. Follow these instructions.\n\n" + push_text(session, started))
        write_mark(session, "armed", now())
        reason = ("Ambition is on for your next message. Send the task as you normally would: Claude does it "
                  "exactly as it would without the plugin, then asks how to push it further.")
        if task:
            reason = ("Ambition is on for your next message. Send the task on its own, so Claude sees exactly "
                      "what it would without the plugin:\n\n" + task)
        return {"decision": "block", "reason": reason, "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit", "suppressOriginalPrompt": True}}
    if os.path.exists(mark(session, "checkpoint")):  # a reply to the checkpoint question
        write_mark(session, "replied")
    waiting = mark(session, "waiting")
    if os.path.exists(waiting):  # the user is replying to a step they were reviewing
        n = int(read(waiting) or 0)
        os.remove(waiting)
        if n in STEPS and os.path.exists(mark(session, "step")):
            return (f"This replies to your step {n}/8 report. Act on it, then end with `▪ Step {n}/8 done` so the "
                     f"next step can start. Only if the user asked to see the result again first, end with "
                     f"`▪ Step {n}/8 · over to you` instead.")
    if STEP.fullmatch(prompt) and not os.path.exists(mark(session, "rules")):
        write_mark(session, "rules")
        return rules_text()
    return None


def on_stop(data):
    session = data.get("session_id")
    if os.path.exists(mark(session, "armed")) and not data.get("stop_hook_active"):
        os.remove(mark(session, "armed"))  # once per arming
        ts = last_prompt(data.get("transcript_path"))[1]
        write_mark(session, "checkpoint", ts[:19] + "Z" if ts else now())
        snapshot(data, "first")
        return checkpoint()
    reply = last_reply(data)
    if os.path.exists(mark(session, "checkpoint")):
        choice = CHOICE.search(reply)
        if not choice:
            # they're still deciding, or they stopped. Once they've replied, check Claude didn't miss the line.
            if os.path.exists(mark(session, "replied")) and not os.path.exists(mark(session, "nudged-choice")):
                write_mark(session, "nudged-choice")
                return ("If the user chose to push the work further, end your message with exactly one of these lines, "
                         "on its own, as its very last line, and stop: `▪ Push: step by step` or `▪ Push: straight "
                         "through`. The instructions arrive then. If they didn't, just stop.")
            return None
        started = read(mark(session, "checkpoint"))
        reviewing = choice.group(1).lower() == "step by step"
        begin_push(session, started, "review" if reviewing else "straight")
        return push_text(session, started, reviewing)
    if not os.path.exists(mark(session, "step")):
        return None
    n, started, *mode = read(mark(session, "step")).split()
    n, reviewing = int(n), mode[:1] == ["review"]
    done = DONE.search(reply)
    if done and int(done.group(1)) == n:
        snapshot(data, f"steps/{n}")
        if n >= 8:  # the push is over
            end_push(session)
            return None
        write_mark(session, "step", f"{n + 1} {started} {'review' if reviewing else 'straight'}")
        return step_text(n + 1, session, started, reviewing)
    if WAITING.search(reply):
        write_mark(session, "waiting", str(n))
        return None
    nudged = mark(session, f"nudged-{n}")
    # once per step; Altitude stops for answers by design, and step by step every step waits for the user
    if n > 2 and not reviewing and not os.path.exists(nudged):
        write_mark(session, f"nudged-{n}")
        return (f"If step {n} is finished, end with its step report and the line `▪ Step {n}/8 done` as the "
                 "very last line. If you're waiting for the user, just stop.")
    return None


def answer(event, data):
    """The hook's answer: None, a full JSON output, or the text for additionalContext."""
    return on_prompt(data) if event == "prompt" else on_stop(data) if event == "stop" else None


def main():
    event = sys.argv[1]
    data = json.loads(sys.stdin.buffer.read())
    out = answer(event, data)
    if isinstance(out, str):
        out = context("UserPromptSubmit" if event == "prompt" else "Stop", out[:LIMIT])
    if out:
        print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # never get in the way of a session: a broken hook just means no hand-off
        try:  # but leave the evidence, in the plugin's data folder
            import traceback
            os.makedirs(STATE, exist_ok=True)
            with open(os.path.join(STATE, "errors.log"), "a") as f:
                f.write(f"{now()} {' '.join(sys.argv[1:])}\n{traceback.format_exc()}\n")
        except Exception:
            pass
