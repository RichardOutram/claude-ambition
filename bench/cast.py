"""Turns a saved (already scrubbed) Claude Code session transcript into an asciicast v2 recording,
drawn the way Claude Code's terminal shows it, for asciinema-player on the results site.
Events keep the session's real timing; the player's idleTimeLimit squeezes the long waits."""
import json
import re
import textwrap
from datetime import datetime
from pathlib import Path

WIDTH, HEIGHT = 110, 24
RESET, BOLD, DIM, ITAL = "\x1b[0m", "\x1b[1m", "\x1b[2m", "\x1b[3m"
FG = {"white": "\x1b[97m", "grey": "\x1b[90m", "green": "\x1b[32m", "orange": "\x1b[38;5;209m",
      "yellow": "\x1b[33m", "cyan": "\x1b[36m", "red": "\x1b[31m", "violet": "\x1b[38;5;141m"}
RESULT_LINES = 3
# Sublime-ish dark palette (Monokai-leaning) so the terminal sits inside the tabbed window.
THEME = {"fg": "#d8dee9", "bg": "#1e1f1c",
         "palette": ":".join(["#272822", "#f92672", "#a6e22e", "#f4bf75", "#66d9ef", "#ae81ff", "#a1efe4", "#f8f8f2",
                              "#75715e", "#f92672", "#a6e22e", "#f4bf75", "#66d9ef", "#ae81ff", "#a1efe4", "#f9f8f5"])}
COMMAND = re.compile(r"<command-name>(/[^<]+)</command-name>\s*<command-args>(.*?)</command-args>", re.S)


def when(stamp):
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()


def wrap(text, first, rest, width=WIDTH):
    """Wraps text to the terminal, with a prefix on the first line and a hanging indent after."""
    out, prefix = [], first
    for para in text.splitlines() or [""]:
        chunks = textwrap.wrap(para, width - visible(prefix), replace_whitespace=False, drop_whitespace=True) or [""]
        for c in chunks:
            out.append(prefix + c)
            prefix = rest
    return out


def visible(s):
    return len(re.sub(r"\x1b\[[0-9;]*m", "", s))


def tool_label(name, args):
    """One line for a tool call, the way Claude Code prints it: Tool(main argument)."""
    a = args or {}
    if name == "Bash":
        arg = (a.get("command") or "").strip().splitlines()[0] if a.get("command") else ""
    elif name in ("Read", "Write", "Edit", "MultiEdit", "NotebookEdit"):
        arg = a.get("file_path") or a.get("notebook_path") or ""
    elif name in ("Glob", "Grep"):
        arg = a.get("pattern") or ""
    elif name == "Skill":
        arg = a.get("skill") or ""
    elif name in ("Agent", "Task"):
        arg = a.get("description") or ""
    elif name == "AskUserQuestion":
        arg = "; ".join(q.get("question", "") for q in a.get("questions") or [])
    elif name == "TodoWrite":
        arg = f"{len(a.get('todos') or [])} todos"
    elif name in ("WebFetch", "WebSearch"):
        arg = a.get("url") or a.get("query") or ""
    else:
        arg = json.dumps(a, ensure_ascii=False)
    return arg


def result_text(block):
    c = block.get("content")
    if isinstance(c, list):
        parts = []
        for x in c:
            if x.get("type") == "text":
                parts.append(x.get("text", ""))
            elif x.get("type") == "image":
                parts.append("[image]")
        c = "\n".join(parts)
    return (c or "").strip() or "(no output)"


def render_block(kind, block):
    """Lines of terminal output for one transcript block."""
    lines = []
    if kind == "prompt":
        text = block
        m = COMMAND.search(text)
        if m:
            text = f"{m.group(1).strip()} {m.group(2).strip()}".strip()
        lines.append("")
        lines += [f"{BOLD}{FG['white']}{l}{RESET}" for l in wrap(text, "❯ ", "  ")]
    elif kind == "hook":
        body = re.sub(r"^Stop hook feedback:\s*", "", block).strip()
        head = body.splitlines()[0] if body else ""
        n = len(body.splitlines())
        lines.append("")
        lines += [f"{FG['yellow']}{l}{RESET}" for l in wrap("Stop hook: " + head, "⚑ ", "  ")]
        if n > 1:
            lines.append(f"{DIM}  ⎿  … +{n - 1} lines of instructions{RESET}")
    elif kind == "text":
        if not block.strip():
            return []
        lines.append("")
        wrapped = wrap(block.strip(), "⏺ ", "  ")
        lines += [f"{FG['white']}{wrapped[0]}{RESET}"] + [f"{FG['white']}{l}{RESET}" for l in wrapped[1:]]
    elif kind == "thinking":
        lines.append("")
        lines.append(f"{DIM}{ITAL}{FG['violet']}✻ Thinking…{RESET}")
    elif kind == "tool":
        name, args = block[:2]
        arg = tool_label(name, args)
        room = WIDTH - len(name) - 5
        if len(arg) > room:
            arg = arg[:room - 1] + "…"
        lines.append("")
        lines.append(f"{FG['green']}⏺{RESET} {BOLD}{name}{RESET}{FG['grey']}({arg}){RESET}")
    elif kind == "result":
        text, error = block[:2]
        rows = text.splitlines()
        shown = []
        for r in rows[:RESULT_LINES]:
            shown += wrap(r, "", "", WIDTH - 6)[:1]
        colour = FG["red"] if error else FG["grey"]
        for i, r in enumerate(shown):
            lines.append(f"{colour}  {'⎿  ' if i == 0 else '   '}{r}{RESET}")
        if len(rows) > RESULT_LINES:
            lines.append(f"{DIM}     … +{len(rows) - RESULT_LINES} lines{RESET}")
    return lines


def events(session):
    """(timestamp, kind, block) for everything worth showing, in order."""
    for raw in Path(session).read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        if d.get("type") not in ("user", "assistant") or not d.get("timestamp"):
            continue
        t = when(d["timestamp"])
        c = (d.get("message") or {}).get("content")
        if d["type"] == "user":
            if isinstance(c, str):
                if c.startswith("Stop hook feedback:"):
                    yield t, "hook", c
                elif not d.get("isMeta") and not c.startswith("<local-command"):
                    yield t, "prompt", c
                continue
            for b in c or []:
                if b.get("type") == "tool_result":
                    yield t, "result", (result_text(b), bool(b.get("is_error")), b.get("tool_use_id"))
                elif b.get("type") == "text" and not d.get("isMeta"):
                    yield t, "prompt", b.get("text", "")
        else:
            for b in c or []:
                if b.get("type") == "text":
                    yield t, "text", b.get("text", "")
                elif b.get("type") == "thinking":
                    yield t, "thinking", None
                elif b.get("type") == "tool_use":
                    yield t, "tool", (b.get("name"), b.get("input"), b.get("id"))


# Routine tool calls fold into one summary line, as Claude Code shows them ("Ran 3 shell commands, read 2 files").
# Anything else (loading a skill, asking the user, starting an agent) keeps its own line.
FOLD = {"Bash": ("ran", "shell command"), "Read": ("read", "file"), "Write": ("wrote", "file"),
        "Edit": ("edited", "file"), "MultiEdit": ("edited", "file"), "NotebookEdit": ("edited", "notebook"),
        "Glob": ("searched for", "pattern"), "Grep": ("searched for", "pattern"), "ToolSearch": ("loaded", "tool"),
        "WebFetch": ("fetched", "page"), "WebSearch": ("ran", "web search"), "TodoWrite": ("updated", "todo list"),
        "BashOutput": ("checked", "background task"), "Monitor": ("started", "monitor"), "TaskStop": ("stopped", "task")}
UP_CLEAR = "\x1b[1A\x1b[2K"


class Fold:
    """A run of routine tool calls, drawn as a summary line plus the latest call, redrawn in place as it grows."""

    def __init__(self):
        self.counts, self.errors, self.latest, self.ids, self.drawn = {}, 0, "", set(), False

    def add(self, name, args, tid):
        verb, noun = FOLD[name]
        self.counts[(verb, noun)] = self.counts.get((verb, noun), 0) + 1
        self.ids.add(tid)
        arg = tool_label(name, args)
        self.latest = f"{name}({arg})"

    def summary(self):
        parts = [f"{verb} {n} {noun}{'' if n == 1 else 's'}" for (verb, noun), n in self.counts.items()]
        text = ", ".join(parts)
        text = text[0].upper() + text[1:]
        err = f"{FG['red']} · {self.errors} failed{RESET}" if self.errors else ""
        latest = self.latest if len(self.latest) <= WIDTH - 8 else self.latest[:WIDTH - 9] + "…"
        return [f"{FG['green']}⏺{RESET} {BOLD}{text}{RESET}{err}", f"{FG['grey']}  ⎿  {latest}{RESET}"]

    def draw(self):
        """Output for the latest state: a fresh block the first time, a redraw of the two lines after."""
        lines = self.summary()
        head = (UP_CLEAR * 2) if self.drawn else "\r\n"
        self.drawn = True
        return head + "\r\n".join(lines) + "\r\n"


def build_cast(session, dest, title=""):
    """Writes dest (.cast). Returns the number of seconds it covers, or None if there was nothing to show."""
    evs = list(events(session))
    if not evs:
        return None
    t0 = evs[0][0]
    header = {"version": 2, "width": WIDTH, "height": HEIGHT, "timestamp": int(t0), "title": title,
              "env": {"TERM": "xterm-256color"}, "theme": THEME}
    out = [json.dumps(header), json.dumps([0.0, "o", "\x1b[?25l"])]  # hide the cursor, as Claude Code does
    last, fold = 0.0, None
    for t, kind, block in evs:
        if kind == "thinking":
            continue
        if kind == "tool" and block[0] in FOLD:
            fold = fold or Fold()
            fold.add(*block)
            text = fold.draw()
        elif kind == "result" and fold and block[2] in fold.ids:
            if not block[1]:
                continue
            fold.errors += 1
            text = fold.draw()
        else:
            fold = None
            lines = render_block(kind, block)
            if not lines:
                continue
            text = "\r\n".join(lines) + "\r\n"
        at = max(last, round(t - t0, 3))  # never go backwards: blocks in one message share a stamp
        out.append(json.dumps([round(at, 3), "o", text], ensure_ascii=False))
        last = at + 0.05
    Path(dest).write_text("\n".join(out) + "\n", encoding="utf-8")
    return last


if __name__ == "__main__":
    import sys
    print(build_cast(sys.argv[1], sys.argv[2]))
