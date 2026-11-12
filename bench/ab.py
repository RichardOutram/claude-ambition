#!/usr/bin/env python3
"""A/B harness for claude-ambition: same prompt, same model, same conditions, with and without the plugin.

  python3 bench/ab.py list
  python3 bench/ab.py run     <slug> --arms not-ambitious   # the plain baseline, once per example
  python3 bench/ab.py run     <slug> --arms ambitious       # one /be-ambitious run of the same prompt
  python3 bench/ab.py review  <slug>                        # evidence for the side-by-side review
  python3 bench/ab.py verdict <slug> --run N --gate pass --result win --note "..."
  python3 bench/ab.py report

Arms:
  not-ambitious  the prompt, exactly as written: the baseline
  ambitious      /be-ambitious (arms the session, unseen by Claude), then the same prompt with the plugin

Each run works in a throwaway container with a real browser. If a run asks a question, a stand-in user
(the same model, knowing only the prompt) answers as the person who typed it would, and pushes on at the checkpoint.
Nothing is judged automatically: `review` gathers the evidence and we record the verdict.
Results go to examples/<model>/<category>/<name>/<arm>/run-<n>/. `report` writes examples/RESULTS.md
and the GitHub Pages site in docs/. See bench/README.md.
"""
import argparse
import base64
import functools
import http.server
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BENCH = REPO / "bench"
EXAMPLES = REPO / "examples"
PROMPTS = EXAMPLES / "PROMPTS.md"
FIXTURES = EXAMPLES / "fixtures"
METRICS = REPO / "scripts" / "ambition-metrics.py"
HOME = str(Path.home())

REPO_URL = "https://github.com/RichardOutram/claude-ambition"
SITE_URL = "https://richardoutram.github.io/claude-ambition/"
ARMS = ("not-ambitious", "ambitious")
DEFAULT_ARMS = "not-ambitious,ambitious"  # same prompt, with and without the plugin
CATEGORIES = {"dev": "development", "data": "data-analysis", "design": "design",
              "plan": "planning", "elec": "electronics", "write": "writing"}

# --host mode only (debugging the harness, never results). Identical for every arm. Edits are auto-accepted.
# Every Bash command is allowed, but only inside the OS sandbox (writes confined to the run folder, network allowlisted):
# allowUnsandboxedCommands=False removes the escape hatch, so nothing can retry outside it.
SETTINGS = {
    "permissions": {"defaultMode": "acceptEdits", "allow": ["Bash", "WebSearch", "WebFetch"]},
    "sandbox": {
        "enabled": True,
        "autoAllowBashIfSandboxed": True,
        "allowUnsandboxedCommands": False,
        "network": {"allowLocalBinding": True, "allowedDomains": [
            "pypi.org", "files.pythonhosted.org", "registry.npmjs.org", "github.com",
            "raw.githubusercontent.com", "objects.githubusercontent.com", "codeload.github.com"]},
    },
}

# Runs work inside a throwaway container by default: a normal machine where Claude can install
# things and drive a real browser, as it would on a user's computer, with nothing of yours inside.
DOCKER_IMAGE = "claude-ambition-bench:2.1.322-r2"  # claude version, then image revision (r2: Chromium on the PATH)
DOCKERFILE = BENCH / "docker"
DOCKER_SETTINGS = {"permissions": {"defaultMode": "acceptEdits", "allow": ["Bash", "WebSearch", "WebFetch"]}}
PLUGIN_PARTS = (".claude-plugin", "commands", "hooks", "scripts", "skills")

CLIENT_PROMPT = """You are the person who typed the request below to Claude, and you are using it the way a real user would. Below are your request and Claude's latest message. Nothing else about you or the task is written down: you know what you asked for, and you have taste and judgement. Every arm of the test gets this same stand-in.

First decide whether Claude's message is waiting on you before it can continue: a question, a request to confirm or approve, or a choice.
- If it is not waiting on you, or is only offering optional extras after delivering what you asked for, reply with exactly: DONE
- If it offers a choice between stopping here and pushing the work further, reply with exactly: Push it further.
- If it asks you questions, answer every one properly, as the person who made this request would. Think about what someone asking for exactly this would most plausibly want, and decide. Pick from its options when one fits, or say what you actually want. Be specific and give a short reason, the way a thoughtful user does. Don't defer ("you decide", "use your judgement") and don't repeat boilerplate: a real user answers.
- If it asks you to confirm a restatement or plan, read it as that user. Approve it if it serves what you asked for; otherwise say briefly what to change. Then tell it to proceed and finish the work without stopping.
Answer in a few sentences, in plain words. Never do the work, review the work or design the solution for it.

<request>
{prompt}
</request>

<assistant_message>
{message}
</assistant_message>"""

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


def ensure_image():
    if subprocess.run(["docker", "image", "inspect", DOCKER_IMAGE], capture_output=True).returncode:
        subprocess.run(["docker", "build", "-t", DOCKER_IMAGE, str(DOCKERFILE)], check=True)


def plugin_version():
    """Which plugin a run used: the commit, whether the plugin files had uncommitted changes, and a hash of
    the plugin's own files, so a page can tell when a run no longer reflects the current plugin."""
    h = hashlib.sha256()
    for part in PLUGIN_PARTS:
        for f in sorted((REPO / part).rglob("*")):
            if f.is_file() and f.name != ".DS_Store" and "__pycache__" not in f.parts:
                h.update(f.relative_to(REPO).as_posix().encode() + b"\0" + f.read_bytes())
    git = lambda *a: subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()  # noqa: E731
    return {"commit": git("rev-parse", "--short", "HEAD"), "dirty": bool(git("status", "--porcelain", "--", *PLUGIN_PARTS)),
            "hash": h.hexdigest()[:12]}


def staged_plugin():
    """Only the plugin itself goes into the container, never the bench, examples or baselines."""
    dest = BENCH / ".cache" / "plugin"
    shutil.rmtree(dest, ignore_errors=True)
    for part in PLUGIN_PARTS:
        shutil.copytree(REPO / part, dest / part, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
    return dest


def in_docker(args, ws, env, plugin=None):
    """Wrap claude args to run in a fresh container: workspace at /work, the bench config at /cfg."""
    settings = BENCH / ".client" / "docker-settings.json"
    settings.write_text(json.dumps(DOCKER_SETTINGS, indent=2))
    inner = list(args)
    inner[inner.index("--settings") + 1] = "/settings.json"
    if plugin:
        inner[inner.index("--plugin-dir") + 1] = "/plugin"
    cmd = ["docker", "run", "--rm", "-i", "--init", "--shm-size=1g",
           "-v", f"{ws}:/work", "-v", f"{config_dir(env)}:/cfg", "-v", f"{settings}:/settings.json:ro"]
    if plugin:
        cmd += ["-v", f"{plugin}:/plugin:ro"]
    for k in ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY"):
        if env.get(k):
            cmd += ["-e", k]
    return cmd + [DOCKER_IMAGE] + inner


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


def workspace_env(env, ws):
    """Package-manager caches live in the workspace: the sandbox only allows writes there."""
    cache = Path(ws) / ".cache"
    return dict(env, XDG_CACHE_HOME=str(cache), npm_config_cache=str(cache / "npm"), PIP_CACHE_DIR=str(cache / "pip"))


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
    text = re.sub(r"(?<![\w.-])/work(?=[/\"'\s`]|$)", "<workspace>", text)
    text = text.replace("/home/pwuser", "~")
    text = text.replace(HOME, "~")
    return EMAIL.sub("<email>", text) if emails else text


IMAGE_DATA = re.compile(r'("data"\s*:\s*")[A-Za-z0-9+/=]{500,}(")')


def copy_scrubbed(src, dst, workspace, env):
    """Saves a transcript, scrubbed. Images the run looked at are replaced by a note: they're the bulk of
    the file, and the review captures its own frames."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    text = IMAGE_DATA.sub(r"\1[image omitted]\2", src.read_text(encoding="utf-8", errors="replace"))
    dst.write_text(scrub(text, workspace, env), encoding="utf-8")


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

def save_spec(spec, model):
    """The prompt, brief and check the example ran with, kept beside its results."""
    path = EXAMPLES / model / spec["category"] / spec["name"] / "spec.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({k: spec[k] for k in ("slug", "prompt", "brief", "check", "fixture")}, indent=2), encoding="utf-8")


def next_run_dir(arm_dir):
    """Always after the highest existing run, so a new run never fills a gap left by a deleted one."""
    taken = [int(d.name.split("-")[1]) for d in arm_dir.glob("run-*") if d.name.split("-")[1].isdigit()]
    return arm_dir / f"run-{max(taken, default=0) + 1}"


def client_answer(spec, message, env, settings, model, effort):
    """The stand-in user: the same model as the run, thinking as the person who typed the prompt."""
    ws = BENCH / ".client"
    ws.mkdir(exist_ok=True)
    args = base_args(model, effort, 1, settings) + ["--tools", ""]
    res = claude(args, ws, env, CLIENT_PROMPT.format(prompt=spec["prompt"], message=message[-8000:]), 600)
    return (res.get("result") or "DONE").strip(), res.get("total_cost_usd") or 0


ARM = "/be-ambitious"  # sent on its own first: the plugin's hook blocks it before Claude sees it and arms the session


def run_arm(spec, arm, run, a, env, isolation, settings):
    public, _ = fixture_dirs(spec)
    if public == "missing":
        return f"skip {spec['slug']}: needs fixture ({spec['fixture']}) at examples/fixtures/{spec['slug']}/public/"
    sid = str(uuid.uuid4())
    version = plugin_version()  # as the run starts: the plugin can change while a long run is going
    args = base_args(a.model, a.effort, a.max_turns, settings)
    plugin = None
    if arm == "ambitious":
        plugin = staged_plugin() if a.docker else REPO
        args += ["--plugin-dir", str(plugin)]
    if a.dry_run:
        return f"[dry-run] {run.relative_to(REPO)}\n  {' '.join(args + ['--session-id', sid])}\n  prompt: {(ARM + ' then ') if arm == 'ambitious' else ''}{spec['prompt']!r}"

    out = scratch()
    if public:
        shutil.copytree(public, out, dirs_exist_ok=True)
    # The run works outside the repo (parent CLAUDE.md files would leak bench context into it),
    # but a `live` link in its example folder lets you watch it build in place.
    run.mkdir(parents=True, exist_ok=True)
    live = run / "live"
    live.unlink(missing_ok=True)
    live.symlink_to(out, target_is_directory=True)
    print(f"live: {live}  ->  {out}", flush=True)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    t0 = time.monotonic()
    armed = False
    if arm == "ambitious":
        flag = ["--session-id", sid]
        call = in_docker(args + flag, out, env, plugin) if a.docker else args + flag
        res = claude(call, out, env if a.docker else workspace_env(env, out), ARM)
        if "blocked by hook" not in (res.get("result") or ""):
            live.unlink(missing_ok=True)
            shutil.rmtree(out, ignore_errors=True)
            return f"FAIL {spec['slug']} {arm}: {ARM} didn't arm the session: {str(res.get('result'))[:300]}"
        armed = True
    messages, results, client_cost, exchanges = [spec["prompt"]], [], 0.0, []
    for turn in range(a.max_exchanges + 1):
        flag = ["--resume", sid] if turn or armed else ["--session-id", sid]
        call = in_docker(args + flag, out, env, plugin if arm == "ambitious" else None) if a.docker else args + flag
        res = claude(call, out, env if a.docker else workspace_env(env, out), messages[-1])
        results.append(res)
        exchanges.append({"n": turn + 1, "minutes": round((time.monotonic() - t0) / 60, 2), "cost_usd": round(res.get("total_cost_usd") or 0, 4)})
        snapshot_turn(out, run, turn + 1)
        print(f"  [{spec['slug']} {arm} {run.name}] exchange {turn + 1} done at {round((time.monotonic() - t0) / 60, 1)} min, "
              f"${res.get('total_cost_usd') or 0:.2f}{' ERROR ' + str(res.get('result'))[:200] if res.get('is_error') else ''}", flush=True)
        if res.get("is_error") and not res.get("session_id") or turn == a.max_exchanges:
            break
        answer, cost = client_answer(spec, res.get("result") or "", env, settings, a.model, a.effort)
        client_cost += cost
        if answer.upper().startswith("DONE"):
            break
        messages.append(answer)

    wall_end = time.monotonic()
    live.unlink(missing_ok=True)
    save_work(out, run / "output")
    shutil.rmtree(out, ignore_errors=True)

    # prompt.md: every message the user side sent
    sent = (f"## Before the prompt\n\n{ARM}\n\n(blocked by the plugin's hook before Claude sees it; it arms the session)\n\n" if armed else "") + "\n\n".join(f"## {'Prompt' if i == 0 else f'Client reply {i}'}\n\n{m}" for i, m in enumerate(messages))
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
    if arm == "ambitious":
        check = check_turn1(run, spec, a.model)
        if check:
            print(f"  turn-1 input: {'identical to the baseline (gate pass)' if check['identical'] else 'DIFFERS from the baseline (gate fail), see turn1-input.json'}", flush=True)

    # metrics: exact figures from the headless JSON, plus the plugin's format. A resumed session reports
    # its cost and usage cumulatively, so the last exchange's figures are the run's totals; summing them
    # would count early turns again for every later one.
    models = {}
    for r in results[-1:]:
        for model, u in (r.get("modelUsage") or {}).items():
            acc = models.setdefault(model, {})
            for k, v in u.items():
                if isinstance(v, (int, float)) and k not in ("contextWindow", "maxOutputTokens"):
                    acc[k] = acc.get(k, 0) + v
    metrics = {
        "slug": spec["slug"], "arm": arm, "model": a.model, "effort": a.effort, "isolation": "docker" if a.docker else isolation,
        "started": started, "session_id": sid, "exchanges": len(messages),
        "cost_usd": round(results[-1].get("total_cost_usd") or 0, 4),
        "client_cost_usd": round(client_cost, 4),
        # Wall clock, including the stand-in user's replies. The JSON's own duration_ms undercounts
        # runs with several exchanges and subagents, so it's kept only for reference.
        "wall_ms": round((wall_end - t0) * 1000),
        "duration_ms": sum(r.get("duration_ms") or 0 for r in results),
        "num_turns": sum(r.get("num_turns") or 0 for r in results),
        "errors": [r.get("result", "")[:300] for r in results if r.get("is_error")],
        "permission_denials": [{"tool": d.get("tool_name"), "input": scrub(json.dumps(d.get("tool_input", {}))[:300], out, env)}
                               for r in results for d in (r.get("permission_denials") or [])],
        "by_model": models,
        "exchange_log": exchanges,  # per turn: cumulative minutes at its end, and that turn's cost
        "plugin": version,
        "plugin_commit": version["commit"],
        "claude_version": subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip(),
    }
    (run / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    if (tdir / "session.jsonl").exists():
        txt = subprocess.run([sys.executable, str(METRICS), str(tdir / "session.jsonl")], capture_output=True, text=True).stdout
        (run / "metrics.txt").write_text(f"cost ${metrics['cost_usd']} · {metrics['wall_ms'] / 1000:.0f}s · "
                                         f"{metrics['num_turns']} turns · {metrics['exchanges']} exchanges\n{txt}", encoding="utf-8")
    measure(run)
    return f"done {run.relative_to(REPO)} · ${metrics['cost_usd']} · {metrics['wall_ms'] / 1000:.0f}s"


# ---------- measuring (outside the sandbox, identical for every arm) ----------

CHROME = os.environ.get("CHROME_PATH") or next((p for p in (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome",
    "/usr/bin/chromium") if Path(p).exists()), None)
LIGHTHOUSE = "lighthouse@12.2.1"
# Headless Chrome won't lay out narrower than 500px, so the 375px mobile shots come from Lighthouse's device emulation.
VIEWPORTS = {"desktop": (1280, 800)}
MOBILE = ["--screenEmulation.mobile=true", "--screenEmulation.width=375", "--screenEmulation.height=812",
          "--screenEmulation.deviceScaleFactor=2"]
# Tool output (test reports, coverage) is not a page the user asked for.
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", ".claude", ".cache", "test-results", "playwright-report",
             "coverage", "lighthouse-report", "dist-test"}


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def html_pages(output, limit=4):
    """The pages worth showing: the deliverable first, then the plugin's first version. Other working copies
    under .ambition/ (judge copies, variants) are skipped."""
    def keep(rel):
        return not SKIP_DIRS & set(rel.parts) and (rel.parts[0] != ".ambition" or rel.parts[1:2] in (("first",), ("direct",)))
    pages = [p for p in output.rglob("*.html") if keep(p.relative_to(output))]
    pages.sort(key=lambda p: (p.relative_to(output).parts[0] == ".ambition", p.name != "index.html",
                              len(p.relative_to(output).parts), str(p)))
    return pages[:limit]


def lighthouse(url, dest):
    """Mobile Lighthouse run: category scores, key metrics, failed accessibility audits, full-page screenshot."""
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "lh.json"
        env = dict(os.environ, CHROME_PATH=CHROME, npm_config_cache=str(BENCH / ".cache" / "npm"))
        subprocess.run(["npx", "-y", LIGHTHOUSE, url, "--quiet", "--chrome-flags=--headless=new", "--form-factor=mobile",
                        "--only-categories=performance,accessibility,best-practices,seo", "--output=json",
                        f"--output-path={report}", *MOBILE], env=env, capture_output=True, timeout=300)
        if not report.exists():
            return {}, {}
        d = json.loads(report.read_text())
    audits = d.get("audits", {})
    a11y = [audits[r["id"]]["title"] for r in d["categories"].get("accessibility", {}).get("auditRefs", [])
            if r.get("weight") and audits.get(r["id"], {}).get("score") == 0]
    out = {"scores": {k: None if v.get("score") is None else round(v["score"] * 100) for k, v in d["categories"].items()},
           "metrics": {k: audits[k].get("displayValue") for k in ("largest-contentful-paint", "cumulative-layout-shift",
                                                                  "total-blocking-time", "total-byte-weight") if k in audits},
           "failed_accessibility_audits": a11y}
    shots = {}
    # Full-page capture at the emulated 375px width (the viewport "final-screenshot" is only a thumbnail).
    for name, data in (("mobile", ((d.get("fullPageScreenshot") or {}).get("screenshot") or {}).get("data", "")),):
        m = re.match(r"data:image/(\w+);base64,(.*)", data, re.S)
        if m:
            shot = dest.with_name(f"{dest.name}-{name}." + m[1].replace("jpeg", "jpg"))
            shot.write_bytes(base64.b64decode(m[2]))
            shots[name] = shot.name
    return out, shots


def measure(run):
    """Screenshots and Lighthouse for every HTML page a run produced. A browser can't start inside the sandbox,
    so the harness does this afterwards, the same way for every arm. Cached in run/checks/."""
    output, checks = run / "output", run / "checks"
    pages = html_pages(output) if output.exists() else []
    if not pages or (checks / "checks.json").exists():
        return
    if not CHROME or not shutil.which("npx"):
        print(f"ab: Chrome or npx not found, so {run.relative_to(REPO)} has no screenshots or Lighthouse scores", file=sys.stderr)
        return
    checks.mkdir(exist_ok=True)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_QuietHandler, directory=str(output)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    results = []
    try:
        for page in pages:
            rel = page.relative_to(output).as_posix()
            url = f"http://127.0.0.1:{srv.server_address[1]}/{urllib.parse.quote(rel)}"
            stem = re.sub(r"[^\w.-]", "_", rel.rsplit(".", 1)[0])
            entry = {"page": rel, "screenshots": {}}
            with tempfile.TemporaryDirectory() as profile:
                for name, (w, h) in VIEWPORTS.items():
                    png = checks / f"{stem}-{name}.png"
                    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--no-first-run", f"--user-data-dir={profile}",
                                    f"--window-size={w},{h}", f"--screenshot={png}", url], capture_output=True, timeout=120)
                    if png.exists():
                        entry["screenshots"][name] = png.name
            entry["lighthouse"], shots = lighthouse(url, checks / stem)
            entry["screenshots"] = {**shots, **entry["screenshots"]}
            results.append(entry)
    finally:
        srv.shutdown()
    (checks / "checks.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


def cmd_run(a):
    env, isolation = load_env()
    if isolation != "clean-config":
        print("ab: no CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY, so using your normal config. Both arms stay "
              "identical, but your CLAUDE.md and user-level commands load. See bench/README.md for clean runs.")
    settings = settings_file()
    if a.docker and not a.dry_run:
        ensure_image()
    jobs = []
    for s in select(load_specs(), a.target):
        if not a.dry_run:
            save_spec(s, a.model)
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


# ---------- figures ----------

def wall_minutes(run, m):
    """Wall-clock minutes: recorded by the harness, else from transcript timestamps (older runs)."""
    if m.get("wall_ms"):
        return m["wall_ms"] / 60000
    stamps = []
    session = run / "transcript" / "session.jsonl"
    if session.exists():
        for line in session.read_text(encoding="utf-8").splitlines():
            t = re.search(r'"timestamp":\s*"([^"]+)"', line)
            if t:
                stamps.append(t[1])
    if len(stamps) > 1:
        from datetime import datetime
        parse = lambda x: datetime.fromisoformat(x.replace("Z", "+00:00"))  # noqa: E731
        return (parse(max(stamps)) - parse(min(stamps))).total_seconds() / 60
    return m["duration_ms"] / 60000


def run_figures(run):
    m = json.loads((run / "metrics.json").read_text())
    return {"cost_usd": m["cost_usd"], "minutes": wall_minutes(run, m), "exchanges": m["exchanges"],
            "turns": m["num_turns"], "output_tokens": sum(u.get("outputTokens", 0) for u in m["by_model"].values())}


# ---------- review: evidence for the side-by-side, the same way for every version ----------

REVIEW_JS = BENCH / "review" / "capture.mjs"
REVIEW_NODE = BENCH / ".cache" / "review-node"
SUBJECT_NAME = {"baseline": "Baseline", "first": "First version", "final": "Final"}


def subjects(run, arm):
    """The versions a reviewer compares. The baseline run has one; an ambitious run has its first version
    (made in turn 1, before the checkpoint) and its final. Values are page paths inside output/."""
    output = run / "output"
    pages = [pg.relative_to(output).as_posix() for pg in html_pages(output, limit=50)] if output.exists() else []
    if arm == "not-ambitious":
        return {"baseline": pages[0]} if pages else {}
    out = {}
    first = [pg for pg in pages if pg.startswith((".ambition/first/", ".ambition/direct/"))]  # direct/: older runs
    final = [pg for pg in pages if not pg.startswith(".ambition/")]
    if first:
        out["first"] = first[0]
    if final:
        out["final"] = final[0]
    return out


def ensure_review_node():
    if not (REVIEW_NODE / "node_modules" / "playwright").exists():
        REVIEW_NODE.mkdir(parents=True, exist_ok=True)
        subprocess.run(["docker", "run", "--rm", "-v", f"{REVIEW_NODE}:/node", "-w", "/node", DOCKER_IMAGE, "bash", "-lc",
                        "npm init -y >/dev/null && npm i --silent playwright@1.52.0 pngjs@7.0.0"], check=True)


WORK_SKIP = ("_tools", "shots", "frames", "judgeview", ".DS_Store", ".cc-writes")  # a run's own screenshots and tooling
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def save_work(src, dest):
    """Copies what a run made, for publishing: the work, not its scaffolding. Leaves out dependencies,
    screenshot and tooling folders, and images inside .ambition/ (the plugin's working area, where the
    judge and the run keep their looks at the work). The same rule applies to every arm."""
    src = Path(src)
    def ignore(d, names):
        rel = Path(d).resolve().relative_to(src.resolve())
        working = rel.parts[:1] == (".ambition",)
        return {n for n in names if n in SKIP_DIRS or n in WORK_SKIP or working and Path(n).suffix.lower() in IMAGE_EXT}
    shutil.copytree(src, dest, dirs_exist_ok=True, symlinks=False, ignore_dangling_symlinks=True, ignore=ignore)


def snapshot_turn(ws, run, n):
    """Saves the work as it stood at the end of turn n into run/turns/turn-<n>/, so the example can show the
    progression. Skipped when nothing changed since the last saved turn, or when there's no page to show."""
    dest = run / "turns" / f"turn-{n}"
    shutil.rmtree(dest, ignore_errors=True)
    save_work(ws, dest)
    def digest(d):
        h = hashlib.sha256()
        for f in sorted(p for p in d.rglob("*") if p.is_file()):
            h.update(f.relative_to(d).as_posix().encode()); h.update(f.read_bytes())
        return h.hexdigest()
    earlier = sorted((run / "turns").glob("turn-*"), key=lambda d: int(d.name.split("-")[1]))
    earlier = [d for d in earlier if int(d.name.split("-")[1]) < n]
    if not html_pages(dest, limit=1) or earlier and digest(earlier[-1]) == digest(dest):
        shutil.rmtree(dest)
        return None
    return dest


def turn_subjects(run):
    """{turn number: page} for each saved turn. The page is the deliverable, or the first version before one exists."""
    out = {}
    for d in (run / "turns").glob("turn-*") if (run / "turns").exists() else []:
        pages = html_pages(d, limit=1)
        if pages:
            out[int(d.name.split("-")[1])] = pages[0].relative_to(d).as_posix()
    return dict(sorted(out.items()))


# A turn is a step of the method. Turn 1 is the plain first version (up to the checkpoint); push.md has the
# model open every later step with a fixed marker line and copy the work to .ambition/steps/<n>/ at its end.
STEP_MARK = re.compile(r"^\W{0,3}Step (\d)/8 · ([^\n]+?)\s*$", re.M)
STEP_NAMES = {1: "First version", 2: "Altitude", 3: "Depth", 4: "Challenge", 5: "Range", 6: "Judge", 7: "Stretch", 8: "Lock"}
# Relative token prices (input, output, cache write, cache read); the same ratios across current Claude models.
TOKEN_WEIGHT = {"input_tokens": 1.0, "output_tokens": 5.0, "cache_creation_input_tokens": 1.25, "cache_read_input_tokens": 0.1}


def _ts(s):
    from datetime import datetime
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def step_log(run, m):
    """[{n, name, minutes, cost_usd}] at the end of each step, cumulative, read from the run's transcript.
    Step 1 is turn 1 as the harness measured it. After that, time is split by the step markers' timestamps and
    cost by the tokens each step's API calls used, both scaled so the last step ends at the run's totals.
    Empty when the run wrote no markers (runs made before them): the site then falls back to exchanges."""
    session = run / "transcript" / "session.jsonl"
    log = m.get("exchange_log") or []
    if not log or not session.exists():
        return []
    push, marks, calls, last = None, {}, {}, None
    for line in session.read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        ts = d.get("timestamp")
        if not ts:
            continue
        msg = d.get("message") or {}
        c = msg.get("content")
        if d.get("type") == "user" and not d.get("isMeta") and push is None:
            text = c if isinstance(c, str) else " ".join(b.get("text", "") for b in c or [] if b.get("type") == "text")
            if text.strip().lower().startswith("push it further"):
                push = _ts(ts)
        if d.get("type") == "assistant":
            last = _ts(ts)
            if push is None:
                continue
            u = msg.get("usage") or {}
            calls[msg.get("id") or ts] = (_ts(ts), sum(w * (u.get(k) or 0) for k, w in TOKEN_WEIGHT.items()))
            for b in c if isinstance(c, list) else []:
                if b.get("type") == "text":
                    for mk in STEP_MARK.finditer(b.get("text", "")):
                        marks.setdefault(int(mk.group(1)), _ts(ts))
    starts = sorted((n, t) for n, t in marks.items() if n >= 3)
    if push is None or not starts or last is None or last <= push:
        return []
    m1, c1 = log[0]["minutes"], log[0]["cost_usd"]
    total_min, total_cost = m.get("minutes") or log[-1]["minutes"], m.get("cost_usd") or log[-1]["cost_usd"]
    units = sum(w for _, w in calls.values()) or 1.0
    def at(t):
        spent = sum(w for ct, w in calls.values() if ct < t)
        return (round(m1 + (total_min - m1) * (t - push) / (last - push), 2),
                round(c1 + (total_cost - c1) * spent / units, 4))
    rows = [{"n": 1, "name": STEP_NAMES[1], "minutes": m1, "cost_usd": c1}]
    ends = [(starts[i - 1][0] if i else 2, t) for i, (_, t) in enumerate(starts)] + [(starts[-1][0], None)]
    for n, t in ends:
        mins, cost = at(t) if t else (round(total_min, 2), round(total_cost, 4))
        rows.append({"n": n, "name": STEP_NAMES.get(n, f"Step {n}"), "minutes": mins, "cost_usd": cost})
    return rows


def step_subjects(run):
    """{step number: page} for each step the run copied to .ambition/steps/<n>/."""
    root = run / "output" / ".ambition" / "steps"
    out = {}
    for d in root.iterdir() if root.exists() else []:
        if d.is_dir() and d.name.isdigit():
            pages = html_pages(d, limit=1)
            if pages:
                out[int(d.name)] = pages[0].relative_to(d).as_posix()
    return dict(sorted(out.items()))


def contact_sheet(folder, view, cap):
    """One image showing the whole loop: every captured frame, left to right, top to bottom."""
    from PIL import Image
    frames = [folder / f["file"] for f in cap["views"][view]["frames"]]
    if not frames:
        return None
    w, h = (480, 300) if view == "desktop" else (180, 390)
    cols = 4 if view == "desktop" else 6
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * h), "black")
    for i, f in enumerate(frames):
        sheet.paste(Image.open(f).convert("RGB").resize((w, h)), ((i % cols) * w, (i // cols) * h))
    name = f"sheet-{view}.jpg"
    sheet.save(folder / name, quality=82)
    return name


def review_subject(run, key, page, seconds, site=None):
    folder = run / "review" / key
    if (folder / "capture.json").exists():
        return json.loads((folder / "capture.json").read_text())
    folder.mkdir(parents=True, exist_ok=True)
    p = subprocess.run(["docker", "run", "--rm", "-v", f"{site or run / 'output'}:/site:ro", "-v", f"{folder}:/out",
                        "-v", f"{REVIEW_JS.parent}:/review:ro", "-v", f"{REVIEW_NODE}:/node:ro", DOCKER_IMAGE,
                        "node", "/review/capture.mjs", "/site", page, "/out", str(seconds)],
                       capture_output=True, text=True, timeout=1800)
    if not (folder / "capture.json").exists():
        print(f"  review failed for {run.relative_to(REPO)} {key}: {(p.stderr or p.stdout)[-600:]}", file=sys.stderr)
        return None
    cap = json.loads((folder / "capture.json").read_text())
    from PIL import Image
    for view in cap["views"].values():  # keep the published frames small
        for f in view["frames"]:
            png = folder / f["file"]
            f["file"] = png.with_suffix(".webp").name
            Image.open(png).save(folder / f["file"], quality=80)
            png.unlink()
    cap["page"], cap["subject"] = page, key
    for view in cap["views"]:
        cap["views"][view]["sheet"] = contact_sheet(folder, view, cap)
    (folder / "capture.json").write_text(json.dumps(cap, indent=2), encoding="utf-8")
    return cap


def seam_text(v):
    import site_builder
    return site_builder.seam_words(v)[0]


def cmd_review(a):
    ensure_image()
    ensure_review_node()
    for spec in select(load_specs(), a.target):
        ex = EXAMPLES / a.model / spec["category"] / spec["name"]
        said = re.search(r"(\d+)\s*-?\s*second", spec["prompt"])
        seconds = int(said.group(1)) if said else a.seconds
        jobs, runs, reuse = [], [], []
        for arm in ARMS:
            for run in sorted(ex.glob(f"{arm}/run-*")):
                if a.run and arm == "ambitious" and run.name != f"run-{a.run}" or not (run / "metrics.json").exists():
                    continue
                runs.append(run)
                subj = subjects(run, arm)
                jobs += [(run, key, page, None) for key, page in subj.items()]
                for n, page in turn_subjects(run).items():
                    # a turn that left the first version or the final as it is reuses that capture
                    body = (run / "turns" / f"turn-{n}" / page).read_bytes()
                    same = [k for k, pg in subj.items() if (run / "output" / pg).read_bytes() == body]
                    if same:
                        reuse.append((run / "review" / same[0], run / "review" / f"turn-{n}"))
                    else:
                        jobs.append((run, f"turn-{n}", page, run / "turns" / f"turn-{n}"))
                steps = run / "output" / ".ambition" / "steps"
                for n, page in step_subjects(run).items():
                    # a step that left the work as the first version or the final reuses that capture
                    body = (steps / str(n) / page).read_bytes()
                    same = [k for k, pg in subj.items() if (run / "output" / pg).read_bytes() == body]
                    if same:
                        reuse.append((run / "review" / same[0], run / "review" / f"step-{n}"))
                    else:
                        jobs.append((run, f"step-{n}", page, steps / str(n)))
        # Two captures at a time, plus Lighthouse on the host: each capture is a CPU-bound container.
        with ThreadPoolExecutor(max_workers=3) as pool:
            measured = pool.submit(lambda: [measure(r) for r in runs])
            caps = list(pool.map(lambda j: review_subject(j[0], j[1], j[2], seconds, j[3]), jobs))
            measured.result()
        for src, dst in reuse:
            if (src / "capture.json").exists():
                shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(src, dst)
        for (run, key, page, _), cap in zip(jobs, caps):
            if cap and key in SUBJECT_NAME:
                views = "; ".join(f"{n}: {seam_text(v)}, {len(v['errors'])} console errors" for n, v in cap["views"].items())
                print(f"{run.relative_to(REPO)} · {SUBJECT_NAME[key]} ({page}) · {views}")


DATE_LINE = re.compile(r"Today's date is \d{4}-\d{2}-\d{2}\.?")


def turn1_input(session):
    """What the model was sent in the run's first API call, from the saved (scrubbed) transcript: the request
    shape (system prompt and tools), the parameters, and every message block, with only the date normalised."""
    shape, params, blobs = None, None, []
    for line in Path(session).read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        if d.get("type") == "api-request-shape" and shape is None:
            shape = d.get("shapeHash")
        elif d.get("type") == "api-request-blob":
            blobs.append(DATE_LINE.sub("<date>", json.dumps(d.get("message"), sort_keys=True)))
        elif d.get("type") == "api-request":
            params = d.get("params")
            break  # the first call: everything it was sent is above this line
    return {"shape": shape, "params": params, "messages": sorted(blobs)}


def check_turn1(run, spec, model):
    """The gate: turn 1 of the ambitious run must be sent exactly what the baseline was sent. Writes
    turn1-input.json with the verdict and, if they differ, a diff of what differs."""
    base = EXAMPLES / model / spec["category"] / spec["name"] / "not-ambitious" / "run-1" / "transcript" / "session.jsonl"
    mine = run / "transcript" / "session.jsonl"
    if not base.exists() or not mine.exists():
        return None
    a, b = turn1_input(base), turn1_input(mine)
    result = {"identical": a == b, "against": base.relative_to(REPO).as_posix(),
              "same_shape": a["shape"] == b["shape"], "same_params": a["params"] == b["params"],
              "same_messages": a["messages"] == b["messages"]}
    if not result["identical"]:
        import difflib
        result["diff"] = list(difflib.unified_diff("\n".join(a["messages"]).split("\\n"), "\n".join(b["messages"]).split("\\n"),
                                                   "baseline", "ambitious", lineterm="", n=1))[:400]
    (run / "turn1-input.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def cmd_verdict(a):
    """Records our decision for one ambitious run. Nothing in the bench decides this automatically."""
    spec = select(load_specs(), a.target)[0]
    run = EXAMPLES / a.model / spec["category"] / spec["name"] / "ambitious" / f"run-{a.run}"
    if not (run / "metrics.json").exists():
        sys.exit(f"ab: no run at {run.relative_to(REPO)}")
    gate = a.gate
    if not gate:
        check = json.loads((run / "turn1-input.json").read_text()) if (run / "turn1-input.json").exists() else None
        if check is None:
            sys.exit("ab: no turn1-input.json for this run; pass --gate after checking turn 1's input by hand")
        gate = "pass" if check["identical"] else "fail"
    verdict = {"gate": gate, "result": a.result, "preview_worth": a.preview, "push_worth": a.push,
               "summary": a.note, "decided_by": a.by, "date": time.strftime("%Y-%m-%d"),
               "plugin": json.loads((run / "metrics.json").read_text()).get("plugin")}
    (run / "verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    if a.notes:
        shutil.copy2(a.notes, run / "review.md")
    print(f"wrote {(run / 'verdict.json').relative_to(REPO)}")


# ---------- reporting ----------

def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0


def restatement(run):
    """The run's own restatement block (You asked for / Genre bar / Aiming at ...), if it wrote one."""
    t = run / "transcript.md"
    if not t.exists():
        return ""
    m = re.search(r"```[a-z]*\n(You asked for:.*?)```", t.read_text(encoding="utf-8"), re.S)
    return m.group(1).strip() if m else ""


def load_run(run, arm, current):
    m = json.loads((run / "metrics.json").read_text())
    plugin = m.get("plugin") or {"commit": m.get("plugin_commit"), "dirty": None, "hash": None}
    reviews = {}
    for key in subjects(run, arm):
        cf = run / "review" / key / "capture.json"
        if cf.exists():
            reviews[key] = json.loads(cf.read_text())
    cj = run / "checks" / "checks.json"
    return {"dir": run, "n": int(run.name.split("-")[1]), "arm": arm, "metrics": m, **run_figures(run),
            "exchange_log": m.get("exchange_log") or [], "plugin": plugin,
            "outdated": arm == "ambitious" and plugin.get("hash") != current,
            "subjects": subjects(run, arm), "reviews": reviews,
            "checks": json.loads(cj.read_text()) if cj.exists() else [],
            "verdict": json.loads((run / "verdict.json").read_text()) if (run / "verdict.json").exists() else None,
            "restatement": restatement(run) if arm == "ambitious" else "",
            # the work at the end of each turn that changed it: page, and its capture once reviewed
            "turns": [{"n": n, "page": page, "capture": json.loads(cf.read_text()) if (cf := run / "review" / f"turn-{n}" / "capture.json").exists() else None}
                      for n, page in turn_subjects(run).items()],
            # each step of the method: when it ended, what it cost, and its copy of the work once reviewed
            "steps": step_log(run, {**m, **run_figures(run)}),
            "step_pages": {n: {"page": page, "capture": json.loads(cf.read_text()) if (cf := run / "review" / f"step-{n}" / "capture.json").exists() else None}
                           for n, page in step_subjects(run).items()}}


def collect():
    """Everything the results page and the site show, read from examples/<model>/<category>/<name>/."""
    specs = {s["slug"]: s for s in load_specs().values()}
    current = plugin_version()["hash"]
    out = []
    for ex in sorted(EXAMPLES.glob("*/*/*")):
        if not ex.is_dir() or ex.relative_to(EXAMPLES).parts[0] == "archive":
            continue
        runs = {arm: [load_run(m.parent, arm, current) for m in sorted(ex.glob(f"{arm}/run-*/metrics.json"),
                                                                       key=lambda m: int(m.parent.name.split("-")[1]))]
                for arm in ARMS}
        if not any(runs.values()):
            continue
        slug = (runs["ambitious"] or runs["not-ambitious"])[0]["metrics"]["slug"]
        if not (ex / "spec.json").exists() and slug in specs:
            save_spec(specs[slug], ex.parent.parent.name)
        spec = json.loads((ex / "spec.json").read_text()) if (ex / "spec.json").exists() else {}
        out.append({"dir": ex, "model": ex.parent.parent.name, "category": ex.parent.name, "name": ex.name,
                    "slug": slug, "spec": spec, "baseline": (runs["not-ambitious"] or [None])[-1],
                    "runs": runs["ambitious"][::-1], "plugin_now": current})
    return out


def preview_figures(r):
    """Turn 1 of an ambitious run is the cheap preview (first version and checkpoint)."""
    log = r["exchange_log"]
    return (log[0]["cost_usd"], log[0]["minutes"]) if log else (None, None)


RESULT_WORD = {"win": "Beats the baseline", "tie": "Ties the baseline", "loss": "Loses to the baseline"}


def results_markdown(data):
    lines = ["# Results", "",
             "Each example has one **baseline**: the prompt exactly as a user would type it, on the same model, in "
             "the same container with a real browser. The plugin passes an example only when a single "
             "`/be-ambitious` run of the *same prompt* beats it. Turn 1 of that run makes a first version and stops "
             "at a checkpoint. The gate: turn 1 must be sent exactly what the baseline was sent (system prompt, tools, "
             "parameters and messages, checked from the transcripts), so it's a second plain sample. The final must beat "
             "the better of the two plain versions. Nothing else is judged "
             "automatically: we review frames, screenshots and the live pages side by side, and record the verdict. "
             "Runs made with an older plugin are marked outdated. [How the bench works](../bench/README.md).", "",
             f"Visual results, with every page live: [results site]({SITE_URL}).", ""]
    for model in sorted({e["model"] for e in data}):
        lines += [f"## {model}", "", "| Example | Verdict | Gate (turn 1) | Baseline | Preview (turn 1) | Full run | Plugin |",
                  "|---|---|---|---|---|---|---|"]
        for e in (x for x in data if x["model"] == model):
            b = e["baseline"]
            base = f"${b['cost_usd']:.2f} · {b['minutes']:.1f} min" if b else "–"
            if not e["runs"]:
                lines.append(f"| {e['slug']} | no plugin run yet | – | {base} | – | – | – |")
                continue
            r = e["runs"][0]
            v = r["verdict"] or {}
            pc, pm = preview_figures(r)
            prev = f"${pc:.2f} · {pm:.1f} min" if pc is not None else "–"
            full = f"${r['cost_usd']:.2f} · {r['minutes']:.1f} min"
            if b:
                full += f" ({r['cost_usd'] / b['cost_usd']:.1f}× cost)"
            plug = (r["plugin"].get("commit") or "?") + (" · outdated" if r["outdated"] else "")
            lines.append(f"| {e['slug']} | {RESULT_WORD.get(v.get('result'), 'not reviewed')} | {v.get('gate', '–')} | "
                         f"{base} | {prev} | {full} | {plug} |")
        lines.append("")
        for e in (x for x in data if x["model"] == model):
            rel = e["dir"].relative_to(EXAMPLES).as_posix()
            lines += [f"### {e['slug']}", "", f"> {e['spec'].get('prompt', '')}", ""]
            for r in e["runs"]:
                v = r["verdict"]
                if v:
                    lines += [f"**Run {r['n']}:** {RESULT_WORD.get(v['result'], v['result'])}, gate {v['gate']}. {v.get('summary') or ''}", ""]
            lines += [f"[Files]({rel}/) · [Visual view]({SITE_URL}{rel}/)", ""]
    return "\n".join(lines)


def cmd_report(a):
    data = collect()
    (EXAMPLES / "RESULTS.md").write_text(results_markdown(data), encoding="utf-8")
    sys.path.insert(0, str(BENCH))
    import site_builder
    site_builder.build(data, REPO / "docs", SITE_URL, REPO_URL)
    print(f"wrote examples/RESULTS.md and docs/ ({len(data)} examples)")


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
    for name in ("run", "review", "verdict", "report"):
        sp = sub.add_parser(name)
        if name != "report":
            sp.add_argument("target")
        sp.add_argument("--model", default="claude-opus-5-5")
        if name == "run":
            sp.add_argument("--effort", default="medium")  # the recommended reasoning effort, pinned so every run matches
            sp.add_argument("--max-turns", type=int, default=80)
            sp.add_argument("--runs", type=int, default=1)
            sp.add_argument("--arms", default=DEFAULT_ARMS)
            sp.add_argument("--max-exchanges", type=int, default=6)
            sp.add_argument("--parallel", type=int, default=1)
            sp.add_argument("--dry-run", action="store_true")
            sp.add_argument("--host", dest="docker", action="store_false",
                            help="run on this machine in the Claude Code sandbox instead of a container (no browser)")
        if name == "review":
            sp.add_argument("--run", type=int, default=None, help="only this ambitious run (the baseline is always included)")
            sp.add_argument("--seconds", type=int, default=10, help="how long to capture, when the prompt doesn't say")
        if name == "verdict":
            sp.add_argument("--run", type=int, required=True)
            sp.add_argument("--gate", choices=("pass", "fail"), help="was turn 1 sent exactly what the baseline was? Defaults to the run's turn1-input.json")
            sp.add_argument("--result", choices=("win", "tie", "loss"), required=True, help="the final against the baseline")
            sp.add_argument("--preview", choices=("yes", "no", "na"), default="na", help="was the turn-1 preview worth its cost?")
            sp.add_argument("--push", choices=("yes", "no", "na"), default="na", help="was pushing on worth its extra cost?")
            sp.add_argument("--note", required=True, help="one or two sentences: why")
            sp.add_argument("--notes", default=None, help="a Markdown file with the full side-by-side review")
            sp.add_argument("--by", default="user", help="who made the call")
    a = p.parse_args()
    {"list": cmd_list, "run": cmd_run, "review": cmd_review, "verdict": cmd_verdict, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
