#!/usr/bin/env python3
"""The hooks behind /be-ambitious and the /ambition steps. They keep the plugin invisible to Claude until
it's needed, so the first turn is exactly what Claude makes from a plain prompt.

  prompt  /be-ambitious [task] at the start of a session is blocked before it reaches Claude, so Claude never
          sees it, and the session is armed. The user's next message is the task, typed as they always would.
          Later in a session, /be-ambitious on its own pushes the work already done.
          The first /ambition step in a session gets the method attached.
  stop    When the armed session's first turn ends, continue it once: save the result as the first version
          and ask whether to stop there or push it further, with the method and push.md attached.
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


def push_text(session, started):
    return (method_text() + "\n\n---\n\n" + read(os.path.join(METHOD, "push.md"))
            + f"\n\nRun started: {started}\nMetrics command for the end: python3 {METRICS} {session} --since {started}")


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
        "3. If they push on, follow the instructions below.\n\n" + push_text(session, started)
    )


def on_prompt(data):
    prompt, session = (data.get("prompt") or "").strip(), data.get("session_id")
    front = FRONT.fullmatch(prompt)
    if front:
        task = (front.group(1) or "").strip()
        if not task and last_prompt(data.get("transcript_path"))[0]:
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
    if data.get("stop_hook_active") or not os.path.exists(mark(session, "armed")):
        return None
    os.remove(mark(session, "armed"))  # once per arming
    ts = last_prompt(data.get("transcript_path"))[1]
    started = ts[:19] + "Z" if ts else now()
    return {"decision": "block", "reason": checkpoint(session, started)}


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
