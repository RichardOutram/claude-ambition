#!/usr/bin/env python3
"""The hooks behind /be-ambitious and the /ambition steps. They keep the plugin invisible to Claude until
it's needed, so the first turn is exactly what Claude makes from a plain prompt.

  prompt  /be-ambitious [task] at the start of a session is blocked before it reaches Claude, so Claude never
          sees it, and the session is armed. The user's next message is the task, typed as they always would.
          Later in a session, /be-ambitious on its own pushes the work already done.
          The first /ambition step in a session gets the method attached.
  stop    When the armed session's first turn ends, continue it once: save the result as the first version
          and ask whether to stop there or push it further, with the method and step 2's instruction attached.
          After that, each time Claude stops with the current step copied to .ambition/steps/<n>/, continue
          with the next step's instruction and nothing else, like a person typing the next command.
Everything else passes straight through. Instructions travel as hook text, never as file paths: reading
plugin files from a project needs permission.
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


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def mark(session, kind):
    safe = re.sub(r"[^\w-]", "-", session or "none")
    return os.path.join(STATE, f"{safe}.{kind}")


def last_prompt(path):
    """The user's latest real prompt in the transcript, with its timestamp: not a tool result, not text
    Claude Code adds itself (expanded command bodies, hook feedback)."""
    found = (None, None)
    if not path or not os.path.exists(path):
        return found
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"type":"user"' not in line or '"tool_result"' in line:  # cheap filter before parsing
                continue
            m = json.loads(line)
            if m.get("type") != "user" or m.get("isMeta"):
                continue
            c = m.get("message", {}).get("content")
            text = c if isinstance(c, str) else " ".join(b.get("text", "") for b in c or [] if b.get("type") == "text")
            found = (text, m.get("timestamp"))
    return found


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def method_text():
    """The method's SKILL.md without its frontmatter, then its reference files."""
    body = re.sub(r"\A---\n.*?\n---\n", "", read(os.path.join(METHOD, "SKILL.md")), count=1, flags=re.S)
    ref = os.path.join(METHOD, "reference")
    parts = [body.strip()]
    for name in sorted(os.listdir(ref)) if os.path.isdir(ref) else []:
        if name.endswith(".md"):
            parts.append(f"## reference/{name}\n\n" + read(os.path.join(ref, name)))
    return "\n\n".join(parts)


def push_parts():
    """push.md split into its preamble, its Every step rules and {n: that step's section}."""
    head, *rest = re.split(r"^## Step (\d) · [^\n]*$", read(os.path.join(METHOD, "push.md")), flags=re.M)
    preamble, every = head.split("## Every step", 1)
    return preamble.strip(), every.strip(), {int(n): body.strip() for n, body in zip(rest[::2], rest[1::2])}


def command_text(name):
    """A manual step's instruction as the user would get it by typing the command, minus its pointers."""
    body = re.sub(r"\A---\n.*?\n---\n", "", read(os.path.join(COMMANDS, name + ".md")), count=1, flags=re.S)
    skip = ("Apply to:", "Follow the ambition method.", "End with:")
    return "\n".join(l for l in body.splitlines() if not l.startswith(skip)).strip()


def step_text(n, session, started):
    """Everything Claude gets for step n of a push, and nothing about the other steps."""
    name, command = STEPS[n]
    _, every, sections = push_parts()
    parts = [f"Step {n} of pushing the work further: {name}. Open your first message with this line on its own, "
             f"exactly: `▸ Step {n}/8 · {name}`. Write that line nowhere else."]
    if command:
        parts.append(command_text(command))
    if n == 8:
        parts.append(f"Then copy the deliverable as it stands to `.ambition/steps/{n}/`.")
    parts.append(sections[n])
    if n < 8:
        parts.append(f"When this step is finished, copy the deliverable as it stands to `.ambition/steps/{n}/` (even "
                     "if this step didn't change it, and never edit that copy), end with a short step report (did / "
                     "found / changed course), and stop. The next instruction arrives then.")
    else:
        parts.append(f"Run started: {started}\nMetrics command for the end: python3 {METRICS} {session} --since {started}")
    return "\n\n".join(parts) + "\n\n## Every step\n\n" + every


def push_text(session, started):
    """The method, push.md's preamble and step 2: all Claude needs to begin pushing on."""
    preamble = push_parts()[0]
    return method_text() + "\n\n---\n\n" + preamble + "\n\n---\n\n" + step_text(2, session, started)


def begin_push(session, started):
    """Step 2 is under way: from here the Stop hook hands out the later steps."""
    os.makedirs(STATE, exist_ok=True)
    with open(mark(session, "step"), "w") as f:
        f.write(f"2 {started}")


def step_done(cwd, n, started):
    """Step n is finished when .ambition/steps/<n>/ holds a file written during this push. Look in the project
    folder, not the shell's current one: Claude may have cd'd into a subfolder (we lost steps 7-8 that way)."""
    root = os.environ.get("CLAUDE_PROJECT_DIR") or cwd or os.getcwd()
    since = datetime.strptime(started, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() - 1
    for folder in step_folders(root, n):
        for base, _, files in os.walk(folder):
            if any(os.path.getmtime(os.path.join(base, f)) >= since for f in files):
                return True
    return False


SKIP_WALK = {"node_modules", ".git", ".venv", "venv", "__pycache__", "dist", "build"}


def step_folders(root, n, depth=3):
    """.ambition/steps/<n>/ in the project folder, then in its subfolders up to `depth` levels down: when the
    deliverable lives in a subfolder, Claude may keep .ambition/ beside it (a run stalled at step 2 that way)."""
    yield os.path.join(root, ".ambition", "steps", str(n))
    level = [root]
    for _ in range(depth):
        nxt = []
        for d in level:
            try:
                names = os.listdir(d)
            except OSError:
                continue
            for name in names:
                path = os.path.join(d, name)
                if name.startswith(".") or name in SKIP_WALK or not os.path.isdir(path) or os.path.islink(path):
                    continue
                yield os.path.join(path, ".ambition", "steps", str(n))
                nxt.append(path)
        level = nxt


def checkpoint(session, started):
    return (
        "Before you finish:\n"
        "1. Copy the deliverable you just made into `.ambition/first/`. If the project has a .gitignore that "
        "doesn't cover `.ambition/`, add it. Never edit that folder again.\n"
        "2. Unless the task was trivial (a typo, a rename, a one-line answer), end with one question, using "
        "AskUserQuestion when it's available:\n"
        "   - Stop here: keep it as it is.\n"
        "   - Push it further: name the two or three improvements you'd go after, and roughly what that costs "
        "against what's been spent so far.\n"
        "   Ask nothing else. Keep this brief: your reply about the work is already above.\n"
        "3. If they push on, do the first step below, and only that step.\n\n" + push_text(session, started)
    )


def on_prompt(data):
    prompt, session = (data.get("prompt") or "").strip(), data.get("session_id")
    front = FRONT.fullmatch(prompt)
    if front:
        task = (front.group(1) or "").strip()
        if not task and last_prompt(data.get("transcript_path"))[0]:
            begin_push(session, now())
            return {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": (
                "The user wants the work already done in this conversation pushed further with the ambition "
                "method. That work is the first version. Follow these instructions.\n\n" + push_text(session, now()))}}
        os.makedirs(STATE, exist_ok=True)
        with open(mark(session, "armed"), "w") as f:
            f.write(now())
        reason = ("Ambition is on for your next message. Send the task as you normally would: Claude does it "
                  "exactly as it would without the plugin, then asks whether to push it further.")
        if task:
            reason = ("Ambition is on for your next message. Send the task on its own, so Claude sees exactly "
                      "what it would without the plugin:\n\n" + task)
        return {"decision": "block", "reason": reason, "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit", "suppressOriginalPrompt": True}}
    if STEP.fullmatch(prompt) and not os.path.exists(mark(session, "method")):
        os.makedirs(STATE, exist_ok=True)
        open(mark(session, "method"), "w").close()
        return {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                       "additionalContext": "The ambition method, for the /ambition steps:\n\n" + method_text()}}
    return None


def on_stop(data):
    session = data.get("session_id")
    if os.path.exists(mark(session, "armed")) and not data.get("stop_hook_active"):
        os.remove(mark(session, "armed"))  # once per arming
        ts = last_prompt(data.get("transcript_path"))[1]
        started = ts[:19] + "Z" if ts else now()
        begin_push(session, started)  # harmless if they stop here: nothing happens until steps/2 appears
        return {"decision": "block", "reason": checkpoint(session, started)}
    if not os.path.exists(mark(session, "step")):
        return None
    n, started = read(mark(session, "step")).split()
    n, cwd = int(n), data.get("cwd")
    if step_done(cwd, n, started):
        if n >= 8:  # the push is over: clear its marks
            for k in ["step"] + [f"nudged-{i}" for i in STEPS]:
                if os.path.exists(mark(session, k)):
                    os.remove(mark(session, k))
            return None
        with open(mark(session, "step"), "w") as f:
            f.write(f"{n + 1} {started}")
        return {"decision": "block", "reason": step_text(n + 1, session, started)}
    nudged = mark(session, f"nudged-{n}")
    if n > 2 and not os.path.exists(nudged):  # once per step; Altitude stops for answers by design
        open(nudged, "w").close()
        return {"decision": "block", "reason": (
            f"Step {n} has no copy in `.ambition/steps/{n}/` yet. If the step is finished, copy the deliverable "
            "there and end with the step report. If you're waiting for the user, just stop.")}
    return None


def main():
    event, data = sys.argv[1], json.load(sys.stdin)
    out = on_prompt(data) if event == "prompt" else on_stop(data) if event == "stop" else None
    if out:
        print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # never get in the way of a session: a broken hook just means no checkpoint
        pass
