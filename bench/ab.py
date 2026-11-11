#!/usr/bin/env python3
"""A/B harness for claude-ambition: same prompt, same model, same conditions, with and without the plugin.

  python3 bench/ab.py list
  python3 bench/ab.py run   <slug|category|all> [--runs N] [--arms a,b,c] [--model ID] [--dry-run]
  python3 bench/ab.py judge <slug|category|all> [--pairs ambitious:not-ambitious,...]
  python3 bench/ab.py report

Arms:
  not-ambitious  the prompt, exactly as written
  briefed        the prompt plus the brief (controls for "it only won because it got more information")
  ambitious      /be-ambitious <prompt>

If any arm asks a question, the same brief-only client answers it and the session resumes.
Results go to examples/<model>/<category>/<name>/<arm>/run-<n>/. See bench/README.md.
"""
import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BENCH = REPO / "bench"
EXAMPLES = REPO / "examples"
PROMPTS = EXAMPLES / "PROMPTS.md"
FIXTURES = EXAMPLES / "fixtures"
METRICS = REPO / "skills" / "be-ambitious" / "scripts" / "ambition-metrics.py"
HOME = str(Path.home())

ARMS = ("not-ambitious", "briefed", "ambitious")
DEFAULT_PAIRS = "ambitious:not-ambitious,ambitious:briefed"
CATEGORIES = {"dev": "development", "data": "data-analysis", "design": "design",
              "plan": "planning", "elec": "electronics", "write": "writing"}

# Identical for every arm, the client and the judge. Edits are auto-accepted; Bash runs inside the
# OS sandbox (writes confined to the run folder) and is auto-allowed there.
SETTINGS = {
    "permissions": {"defaultMode": "acceptEdits", "allow": ["WebSearch", "WebFetch"]},
    "sandbox": {
        "enabled": True,
        "autoAllowBashIfSandboxed": True,
        "network": {"allowedDomains": [
            "pypi.org", "files.pythonhosted.org", "registry.npmjs.org", "github.com",
            "raw.githubusercontent.com", "objects.githubusercontent.com", "codeload.github.com"]},
    },
}

CLIENT_PROMPT = """You stand in for a user in a test. Below are the user's original request, their private brief, and the assistant's latest message.

Decide whether the assistant's message is waiting on the user before it can continue: a question, a request to confirm or approve, or a choice to make.
- If it is not waiting on the user, or it has delivered what the request asked for and is only offering optional extras, reply with exactly: DONE
- If the request was for a plan, advice or an explanation, and that has been delivered, reply DONE, even if it asks for approval to go further.
- Otherwise, reply as the user in 1 to 4 plain sentences, using only the brief. If you're asked to confirm a restatement or plan that doesn't contradict the brief, approve it and say to proceed and finish the work. If the brief doesn't cover something, say you don't mind and it should use its best judgment.
Never do the work, review it, or suggest approaches.

<request>
{prompt}
</request>

<brief>
{brief}
</brief>

<assistant_message>
{message}
</assistant_message>"""

JUDGE_PROMPT = """You are judging two responses to the same request. They are labelled A and B. You don't know how either was produced. Judge only the work.

<request>
{prompt}
</request>

<user_context>
Context the user had (they may or may not have stated it): {brief}
</user_context>

<how_to_judge>
{check}
</how_to_judge>

Each response's final message is in A/RESPONSE.md and B/RESPONSE.md, with any files it produced beside it. If the check needs ground truth, it is in hidden/. Neither response ever saw it.

1. Run every objective check you can, the same way on both. Record the commands and results.
2. Score each criterion in the check from 1 to 5 for A and for B, with one line of evidence each.
3. Choose A, B or TIE. Don't reward length, formatting or a confident tone. Reward what actually meets the request and the user's real goal, as shown by your checks.

End with a fenced json block exactly like this:
```json
{{"winner": "A|B|TIE", "confidence": "low|medium|high", "scores": {{"A": {{"<criterion>": 0}}, "B": {{"<criterion>": 0}}}}, "summary": "<one line>"}}
```"""


# ---------- specs ----------

def load_specs():
    text = PROMPTS.read_text(encoding="utf-8")
    specs = {}
    for block in re.split(r"^### ", text, flags=re.M)[1:]:
        slug = block.split("\n", 1)[0].strip()

        def field(name):
            m = re.search(rf"\*\*{name}:\*\*\s*(.+?)(?=\n\*\*\w+:\*\*|\n---|\n## |\Z)", block, re.S)
            return m.group(1).strip() if m else ""

        raw = field("Prompt")
        fixture = re.search(r"\*\(fixture:\s*([^)]*)\)\*", raw)
        prefix, name = slug.split("/", 1)
        specs[slug] = {
            "slug": slug, "category": CATEGORIES.get(prefix, prefix), "name": name,
            "prompt": re.sub(r"\s*\*\(fixture:[^)]*\)\*", "", raw).strip(),
            "brief": field("Brief"), "check": field("Check"),
            "fixture": fixture.group(1).strip() if fixture else None,
        }
    return specs


def select(specs, target):
    if target == "all":
        return list(specs.values())
    if target in specs:
        return [specs[target]]
    hits = [s for s in specs.values() if s["slug"].startswith(target + "/") or s["category"] == target]
    if not hits:
        sys.exit(f"ab: no example or category matches '{target}'. Try: python3 bench/ab.py list")
    return hits


def fixture_dirs(spec):
    """Return (public_dir, hidden_dir) or None if the spec needs a fixture that doesn't exist yet."""
    if not spec["fixture"]:
        return None, None
    root = FIXTURES / spec["slug"]
    gen = root / "generate.py"
    if gen.exists() and not (root / "public").exists():
        subprocess.run([sys.executable, "-I", str(gen), str(root)], check=True)
    public = root / "public" if (root / "public").exists() else None
    hidden = root / "hidden" if (root / "hidden").exists() else None
    if not public and not hidden:
        return "missing", None
    return public, hidden


# ---------- environment ----------

def load_env():
    env = os.environ.copy()
    dotenv = BENCH / ".env"
    if dotenv.exists():
        for line in dotenv.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    if env.get("CLAUDE_CODE_OAUTH_TOKEN") or env.get("ANTHROPIC_API_KEY"):
        cfg = BENCH / ".home"
        cfg.mkdir(exist_ok=True)
        env["CLAUDE_CONFIG_DIR"] = str(cfg)
        isolation = "clean-config"
    else:
        isolation = "shared-user-config"
    env.pop("CLAUDECODE", None)  # allow running from inside a Claude Code session
    return env, isolation


def secrets(env):
    return [v for k, v in env.items() if k in ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY") and v]


def config_dir(env):
    return Path(env.get("CLAUDE_CONFIG_DIR") or Path(HOME) / ".claude")


def settings_file():
    path = BENCH / ".client" / "bench-settings.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(SETTINGS, indent=2))
    return str(path)


def base_args(model, effort, max_turns, settings):
    args = ["claude", "-p", "--output-format", "json", "--model", model, "--max-turns", str(max_turns),
            "--settings", settings, "--setting-sources", "project", "--strict-mcp-config",
            "--disallowedTools", "AskUserQuestion"]
    if effort:
        args += ["--effort", effort]
    return args


def claude(args, cwd, env, prompt, timeout=3600):
    try:
        p = subprocess.run(args, cwd=cwd, env=env, input=prompt, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"is_error": True, "result": f"timeout after {timeout}s"}
    try:
        return json.loads(p.stdout)
    except ValueError:
        return {"is_error": True, "result": (p.stdout[-3000:] + "\n" + p.stderr[-3000:]).strip()}


# ---------- sanitising and rendering ----------

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def scratch():
    """A fresh empty folder outside the repo, so no run can see the plugin, prompts or other arms."""
    root = Path(tempfile.gettempdir()) / "claude-ambition-bench"
    root.mkdir(exist_ok=True)
    return Path(tempfile.mkdtemp(dir=root)).resolve()


def scrub(text, workspace, env, emails=True):
    for s in secrets(env):
        text = text.replace(s, "<redacted>")
    for w in {str(workspace), str(Path(workspace).resolve()), str(workspace).replace("/private/", "/", 1)}:
        text = text.replace(w, "<workspace>")
    text = text.replace(HOME, "~")
    return EMAIL.sub("<email>", text) if emails else text


def copy_scrubbed(src, dst, workspace, env):
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(scrub(src.read_text(encoding="utf-8", errors="replace"), workspace, env), encoding="utf-8")


def render_transcript(jsonl, title):
    out = [f"# {title}\n"]
    clip = lambda s, n: s if len(s) <= n else s[:n] + f" … [{len(s) - n} more chars]"  # noqa: E731
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        m = d.get("message")
        if not isinstance(m, dict) or d.get("type") not in ("user", "assistant"):
            continue
        content = m.get("content")
        blocks = [{"type": "text", "text": content}] if isinstance(content, str) else (content or [])
        for b in blocks:
            kind = b.get("type")
            if kind == "text" and b.get("text", "").strip():
                who = "Assistant" if d["type"] == "assistant" else ("Context (injected)" if d.get("isMeta") else "User")
                body = b["text"] if who != "Context (injected)" else f"<details><summary>show</summary>\n\n{b['text']}\n\n</details>"
                out.append(f"### {who}\n\n{body}\n")
            elif kind == "tool_use":
                out.append(f"**→ {b.get('name')}** `{clip(json.dumps(b.get('input', {})), 400)}`\n")
            elif kind == "tool_result":
                res = b.get("content")
                res = res if isinstance(res, str) else "\n".join(x.get("text", "") for x in (res or []) if isinstance(x, dict))
                out.append(f"<details><summary>result</summary>\n\n```\n{clip(res, 2000)}\n```\n\n</details>\n")
    return "\n".join(out)


# ---------- running ----------

def next_run_dir(arm_dir):
    n = 1
    while (arm_dir / f"run-{n}").exists():
        n += 1
    return arm_dir / f"run-{n}"


def client_answer(spec, message, env, settings):
    ws = BENCH / ".client"
    ws.mkdir(exist_ok=True)
    args = base_args("sonnet", "low", 1, settings) + ["--tools", ""]
    res = claude(args, ws, env, CLIENT_PROMPT.format(prompt=spec["prompt"], brief=spec["brief"], message=message[-8000:]), 600)
    return (res.get("result") or "DONE").strip(), res.get("total_cost_usd") or 0


def arm_prompt(spec, arm):
    if arm == "ambitious":
        return f"/be-ambitious --no-metrics {spec['prompt']}"
    if arm == "briefed":
        return f"{spec['prompt']}\n\n{spec['brief']}"
    return spec["prompt"]


def run_arm(spec, arm, run, a, env, isolation, settings):
    public, _ = fixture_dirs(spec)
    if public == "missing":
        return f"skip {spec['slug']}: needs fixture ({spec['fixture']}) at examples/fixtures/{spec['slug']}/public/"
    sid = str(uuid.uuid4())
    args = base_args(a.model, a.effort, a.max_turns, settings)
    if arm == "ambitious":
        args += ["--plugin-dir", str(REPO)]
    if a.dry_run:
        return f"[dry-run] {run.relative_to(REPO)}\n  {' '.join(args + ['--session-id', sid])}\n  prompt: {arm_prompt(spec, arm)!r}"

    out = scratch()
    if public:
        shutil.copytree(public, out, dirs_exist_ok=True)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    messages, results, client_cost = [arm_prompt(spec, arm)], [], 0.0
    for turn in range(a.max_exchanges + 1):
        flag = ["--session-id", sid] if turn == 0 else ["--resume", sid]
        res = claude(args + flag, out, env, messages[-1])
        results.append(res)
        if res.get("is_error") and not res.get("session_id") or turn == a.max_exchanges:
            break
        answer, cost = client_answer(spec, res.get("result") or "", env, settings)
        client_cost += cost
        if answer.upper().startswith("DONE"):
            break
        messages.append(answer)

    shutil.copytree(out, run / "output", dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", "node_modules", ".venv", "__pycache__"))
    shutil.rmtree(out, ignore_errors=True)

    # prompt.md: every message the user side sent
    sent = "\n\n".join(f"## {'Prompt' if i == 0 else f'Client reply {i}'}\n\n{m}" for i, m in enumerate(messages))
    (run / "prompt.md").write_text(f"# {spec['slug']} · {arm}\n\n{sent}\n", encoding="utf-8")
    (run / "result.md").write_text(scrub(results[-1].get("result") or "", out, env, emails=False), encoding="utf-8")

    # transcript (main + subagents), sanitised
    tdir = run / "transcript"
    found = list(config_dir(env).glob(f"projects/*/{sid}.jsonl"))
    if found:
        copy_scrubbed(found[0], tdir / "session.jsonl", out, env)
        for sub in (found[0].with_suffix("") / "subagents").glob("*"):
            copy_scrubbed(sub, tdir / "session" / "subagents" / sub.name, out, env)
        (run / "transcript.md").write_text(render_transcript(tdir / "session.jsonl", f"{spec['slug']} · {arm}"), encoding="utf-8")

    # metrics: exact figures from the headless JSON, summed over resumed turns, plus the plugin's format
    models = {}
    for r in results:
        for model, u in (r.get("modelUsage") or {}).items():
            acc = models.setdefault(model, {})
            for k, v in u.items():
                if isinstance(v, (int, float)) and k not in ("contextWindow", "maxOutputTokens"):
                    acc[k] = acc.get(k, 0) + v
    metrics = {
        "slug": spec["slug"], "arm": arm, "model": a.model, "effort": a.effort, "isolation": isolation,
        "started": started, "session_id": sid, "exchanges": len(messages),
        "cost_usd": round(sum(r.get("total_cost_usd") or 0 for r in results), 4),
        "client_cost_usd": round(client_cost, 4),
        "duration_ms": sum(r.get("duration_ms") or 0 for r in results),
        "num_turns": sum(r.get("num_turns") or 0 for r in results),
        "errors": [r.get("result", "")[:300] for r in results if r.get("is_error")],
        "by_model": models,
        "plugin_commit": subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                                        capture_output=True, text=True).stdout.strip(),
        "claude_version": subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip(),
    }
    (run / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    if (tdir / "session.jsonl").exists():
        txt = subprocess.run([sys.executable, str(METRICS), str(tdir / "session.jsonl")], capture_output=True, text=True).stdout
        (run / "metrics.txt").write_text(f"cost ${metrics['cost_usd']} · {metrics['duration_ms'] / 1000:.0f}s · "
                                         f"{metrics['num_turns']} turns · {metrics['exchanges']} exchanges\n{txt}", encoding="utf-8")
    return f"done {run.relative_to(REPO)} · ${metrics['cost_usd']} · {metrics['duration_ms'] / 1000:.0f}s"


def cmd_run(a):
    env, isolation = load_env()
    if isolation != "clean-config":
        print("ab: no CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY, so using your normal config. Both arms stay "
              "identical, but your CLAUDE.md and user-level commands load. See bench/README.md for clean runs.")
    settings = settings_file()
    jobs = []
    for s in select(load_specs(), a.target):
        for arm in a.arms.split(","):
            arm_dir = EXAMPLES / a.model / s["category"] / s["name"] / arm
            for _ in range(a.runs):
                run = next_run_dir(arm_dir)
                if not a.dry_run:
                    run.mkdir(parents=True)  # reserve the folder now, so parallel jobs never collide
                jobs.append((s, arm, run))
    work = lambda j: run_arm(j[0], j[1], j[2], a, env, isolation, settings)  # noqa: E731
    if a.parallel > 1 and not a.dry_run:
        with ThreadPoolExecutor(a.parallel) as pool:
            for msg in pool.map(work, jobs):
                print(msg, flush=True)
    else:
        for j in jobs:
            print(work(j), flush=True)


# ---------- judging ----------

def strip_markers(text):
    return re.sub(r"(?i)/?be-ambitious|ambition[-\w]*", "the process", text)


def judge_pair(spec, x, y, n, a, env, settings):
    base = EXAMPLES / a.model / spec["category"] / spec["name"]
    runs = {arm: base / arm / f"run-{n}" for arm in (x, y)}
    if not all((r / "result.md").exists() for r in runs.values()):
        return None
    pair_dir = base / "judge" / f"{x}-vs-{y}" / f"run-{n}"
    if (pair_dir / "verdict.json").exists():
        return json.loads((pair_dir / "verdict.json").read_text())
    _, hidden = fixture_dirs(spec)
    orders = [(x, y), (y, x)]
    random.shuffle(orders)
    verdicts = []
    for k, (arm_a, arm_b) in enumerate(orders, 1):
        ws = scratch()
        for label, arm in (("A", arm_a), ("B", arm_b)):
            shutil.copytree(runs[arm] / "output", ws / label, dirs_exist_ok=True)
            (ws / label / "RESPONSE.md").write_text(strip_markers((runs[arm] / "result.md").read_text()), encoding="utf-8")
        if hidden:
            shutil.copytree(hidden, ws / "hidden", dirs_exist_ok=True)
        prompt = JUDGE_PROMPT.format(prompt=spec["prompt"], brief=spec["brief"], check=spec["check"])
        res = claude(base_args(a.model, a.effort, a.max_turns, settings), ws, env, prompt)
        text = res.get("result") or ""
        (pair_dir / f"order-{k}-judge.md").parent.mkdir(parents=True, exist_ok=True)
        (pair_dir / f"order-{k}-judge.md").write_text(
            f"A = {arm_a}, B = {arm_b} (the judge did not know this)\n\n" + scrub(text, ws, env, emails=False), encoding="utf-8")
        shutil.rmtree(ws, ignore_errors=True)
        m = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.S)
        try:
            v = json.loads(m[-1]) if m else {}
        except ValueError:
            v = {}
        winner = {"A": arm_a, "B": arm_b}.get(str(v.get("winner", "")).upper().strip(), "tie")
        verdicts.append({"order": k, "A": arm_a, "B": arm_b, "winner": winner, "confidence": v.get("confidence"),
                         "summary": v.get("summary"), "scores": v.get("scores"), "cost_usd": res.get("total_cost_usd")})
    final = verdicts[0]["winner"] if verdicts[0]["winner"] == verdicts[1]["winner"] else "tie"
    out = {"slug": spec["slug"], "pair": [x, y], "run": n, "winner": final, "orders": verdicts}
    pair_dir.mkdir(parents=True, exist_ok=True)
    (pair_dir / "verdict.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def cmd_judge(a):
    env, _ = load_env()
    settings = settings_file()
    for spec in select(load_specs(), a.target):
        for pair in a.pairs.split(","):
            x, y = pair.split(":")
            n = 1
            while (EXAMPLES / a.model / spec["category"] / spec["name"] / x / f"run-{n}").exists():
                v = judge_pair(spec, x, y, n, a, env, settings)
                if v:
                    print(f"{spec['slug']} {x} vs {y} run-{n}: {v['winner']}", flush=True)
                n += 1


# ---------- reporting ----------

def cmd_report(a):
    root = EXAMPLES / a.model
    rows, wins = {}, {}
    for mf in sorted(root.glob("*/*/*/run-*/metrics.json")):
        m = json.loads(mf.read_text())
        r = rows.setdefault((m["slug"], m["arm"]), {"runs": 0, "cost": 0, "ms": 0, "turns": 0, "out": 0})
        r["runs"] += 1
        r["cost"] += m["cost_usd"]
        r["ms"] += m["duration_ms"]
        r["turns"] += m["num_turns"]
        r["out"] += sum(u.get("outputTokens", 0) for u in m["by_model"].values())
    for vf in sorted(root.glob("*/*/judge/*/run-*/verdict.json")):
        v = json.loads(vf.read_text())
        w = wins.setdefault((v["slug"], " vs ".join(v["pair"])), {"runs": 0})
        w["runs"] += 1
        w[v["winner"]] = w.get(v["winner"], 0) + 1
    lines = [f"# A/B report · {a.model}\n", "## Cost per run (average)\n",
             "| example | arm | runs | cost $ | output tokens | turns | minutes |", "|---|---|---|---|---|---|---|"]
    for (slug, arm), r in sorted(rows.items()):
        k = r["runs"]
        lines.append(f"| {slug} | {arm} | {k} | {r['cost'] / k:.2f} | {r['out'] / k:,.0f} | {r['turns'] / k:.0f} | {r['ms'] / k / 60000:.1f} |")
    lines += ["\n## Blind judge results\n", "| example | pair | runs | wins | ties |", "|---|---|---|---|---|"]
    for (slug, pair), w in sorted(wins.items()):
        arms_ = pair.split(" vs ")
        lines.append(f"| {slug} | {pair} | {w['runs']} | {' · '.join(f'{x} {w.get(x, 0)}' for x in arms_)} | {w.get('tie', 0)} |")
    report = root / "REPORT.md"
    root.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report.read_text())


def cmd_list(_a):
    for s in load_specs().values():
        state = ""
        if s["fixture"]:
            pub, _ = fixture_dirs(s)
            state = "  [needs fixture]" if pub == "missing" else "  [fixture ready]"
        print(f"{s['slug']:<24} {s['prompt'][:70]}{state}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    for name in ("run", "judge", "report"):
        sp = sub.add_parser(name)
        if name != "report":
            sp.add_argument("target")
        sp.add_argument("--model", default="claude-opus-5-5")
        sp.add_argument("--effort", default=None)
        sp.add_argument("--max-turns", type=int, default=80)
        if name == "run":
            sp.add_argument("--runs", type=int, default=1)
            sp.add_argument("--arms", default=",".join(ARMS))
            sp.add_argument("--max-exchanges", type=int, default=6)
            sp.add_argument("--parallel", type=int, default=1)
            sp.add_argument("--dry-run", action="store_true")
        if name == "judge":
            sp.add_argument("--pairs", default=DEFAULT_PAIRS)
    a = p.parse_args()
    {"list": cmd_list, "run": cmd_run, "judge": cmd_judge, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
