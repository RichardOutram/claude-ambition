#!/usr/bin/env python3
"""Compact token metrics for a Claude Code session, including its subagents.

Usage:
  ambition-metrics.py <session-id | path/to/session.jsonl> [--since ISO8601] [--json]

It reads the session transcript under ~/.claude/projects and the subagent
transcripts beside it, de-duplicates API calls by message id, and prints a
short summary. Cost in USD isn't recorded in transcripts: use /cost in an
interactive session, or `total_cost_usd` from `claude -p --output-format json`.
"""
import glob
import json
import os
import sys
from collections import defaultdict

FIELDS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


def find_transcript(arg):
    if arg.endswith(".jsonl") and os.path.isfile(arg):
        return arg
    hits = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{arg}.jsonl"))
    if not hits:
        sys.exit(f"ambition-metrics: no transcript found for session {arg}")
    return max(hits, key=os.path.getmtime)


def read_calls(path, since):
    """Return {message_id: (model, usage, thinking)}, keeping the last line per id."""
    calls = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            m = d.get("message")
            if d.get("type") != "assistant" or not isinstance(m, dict) or not m.get("usage"):
                continue
            if since and d.get("timestamp", "") < since:
                continue
            u = m["usage"]
            thinking = (u.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0
            calls[m.get("id") or d.get("uuid")] = (m.get("model", "?"), u, thinking)
    return calls


def add(acc, usage, thinking):
    for f in FIELDS:
        acc[f] += usage.get(f, 0) or 0
    acc["thinking"] += thinking
    acc["calls"] += 1


def fmt(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def line(a):
    total_in = a["input_tokens"] + a["cache_read_input_tokens"] + a["cache_creation_input_tokens"]
    hit = 100 * a["cache_read_input_tokens"] / total_in if total_in else 0
    return (f"in {fmt(a['input_tokens'])} · out {fmt(a['output_tokens'])} (think {fmt(a['thinking'])}) · "
            f"cache read {fmt(a['cache_read_input_tokens'])} · write {fmt(a['cache_creation_input_tokens'])} · "
            f"hit {hit:.0f}% · {a['calls']} calls")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return
    since = argv[argv.index("--since") + 1] if "--since" in argv else None
    as_json = "--json" in argv
    main_path = find_transcript(argv[0])

    new = lambda: defaultdict(int)  # noqa: E731
    total, by_model, by_agent = new(), defaultdict(new), defaultdict(new)

    sources = [(main_path, "main")]
    for sub in sorted(glob.glob(os.path.join(main_path[:-6], "subagents", "*.jsonl"))):
        agent = "subagent"
        try:
            with open(sub[:-6] + ".meta.json", encoding="utf-8") as fh:
                agent = json.load(fh).get("agentType") or agent
        except (OSError, ValueError):
            pass
        sources.append((sub, agent))

    spawned = defaultdict(int)
    for path, agent in sources:
        calls = read_calls(path, since)
        if calls and agent != "main":
            spawned[agent] += 1
        for model, usage, thinking in calls.values():
            for acc in (total, by_model[model], by_agent[agent]):
                add(acc, usage, thinking)

    if as_json:
        print(json.dumps({"total": total, "by_model": by_model, "by_agent": by_agent,
                          "agents_spawned": spawned, "since": since}, separators=(",", ":")))
        return

    print(f"Metrics{' since ' + since if since else ''} (cost: /cost, or total_cost_usd in headless JSON)")
    print("total   " + line(total))
    for model, acc in sorted(by_model.items(), key=lambda kv: -kv[1]["output_tokens"]):
        print(f"model   {model.replace('claude-', '')}: " + line(acc))
    if len(by_agent) > 1:
        for agent, acc in sorted(by_agent.items(), key=lambda kv: -kv[1]["output_tokens"]):
            count = f" ×{spawned[agent]}" if agent in spawned else ""
            print(f"agent   {agent}{count}: " + line(acc))


if __name__ == "__main__":
    main(sys.argv[1:])
