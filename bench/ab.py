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
import shlex
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
# Runs where vanilla Claude plays the user (types the prompt, answers questions, says "Push it further."), and
# runs a person drove (ab.py drive). Same layout under each: <model>/<category>/<name>/<arm>/run-N.
AUTOPILOT = EXAMPLES / "autopilot"
DRIVEN_DIR = EXAMPLES / "driven"
METRICS = REPO / "scripts" / "ambition-metrics.py"
HOME = str(Path.home())

REPO_URL = "https://github.com/RichardOutram/claude-ambition"
SITE_URL = "https://richardoutram.github.io/claude-ambition/"
ARMS = ("not-ambitious", "ambitious")
DEFAULT_ARMS = "not-ambitious,ambitious"  # same prompt, with and without the plugin
CATEGORIES = {"dev": "development", "data": "data-analysis", "design": "design",
              "plan": "planning", "elec": "electronics", "write": "writing",
              "game": "games", "learn": "education"}

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
# The method itself: what decides whether a run is outdated. The process around it (hooks, push.md's step
# plumbing, the checkpoint) can change without making earlier runs stand for a different method.
METHOD_PARTS = ("commands", "skills/ambition-method/SKILL.md", "skills/ambition-method/reference")

# The default: runs work in a throwaway macOS VM (Tart), a clone of a bench image made from a plain developer Mac
# (tahoe-dev: Homebrew, Node, Python, git, ripgrep, Chrome) plus the pinned Claude Code. WebGL runs on the Mac's GPU
# through Apple's paravirtual device, so a run sees and times its work as Claude on a MacBook would. Each run gets
# its own clone, booted once and deleted afterwards; host folders appear at /work, /cfg, /plugin and /bench through
# /etc/synthetic.conf links into the VM's shared-folder mount. See bench/vm/README.md for how the images are built.
VM_BASE = "ambition-bench"
VM_CLAUDE = "2.1.322"  # the Claude Code version installed in VM_BASE
VM_KEY = Path(HOME) / ".tart" / "tahoe-dev_ed25519"
VM_SHARE = Path(HOME) / ".cache" / "claude-ambition-vm"  # per-run settings for the VM, outside the repo
REVIEW_NODE_MAC = BENCH / ".cache" / "review-node-mac"
SSH_OPTS = ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-o", "LogLevel=ERROR",
            "-o", "ServerAliveInterval=30"]


class VM:
    """One throwaway clone of VM_BASE, booted headless with host folders shared at /<name>. Use as a context
    manager: it's cloned and booted on entry, stopped and deleted on exit, whatever happened in between."""

    def __init__(self, dirs, label="run"):
        self.dirs, self.name, self.proc, self.ip = dirs, f"ambition-{label}-{uuid.uuid4().hex[:8]}", None, None

    def __enter__(self):
        subprocess.run(["tart", "clone", VM_BASE, self.name], check=True)
        args = ["tart", "run", self.name, "--no-graphics"]
        for name, (path, ro) in self.dirs.items():
            args += ["--dir", f"{name}:{path}" + (":ro" if ro else "")]
        self.proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            ip = subprocess.run(["tart", "ip", self.name], capture_output=True, text=True).stdout.strip()
            if ip and subprocess.run(["ssh", "-i", str(VM_KEY), *SSH_OPTS, "-o", "ConnectTimeout=3", f"admin@{ip}",
                                      "test -d /work || test -d /examples"], capture_output=True).returncode == 0:
                self.ip = ip
                return self
            time.sleep(2)
        self.__exit__(None, None, None)
        raise RuntimeError(f"VM {self.name} didn't come up")

    def ssh(self, command):
        """The ssh argv that runs `command` in a login shell in the VM (stdin passes through)."""
        return ["ssh", "-i", str(VM_KEY), *SSH_OPTS, f"admin@{self.ip}", "zsh -lc " + shlex.quote(command)]

    def __exit__(self, *_):
        subprocess.run(["tart", "stop", self.name, "--timeout", "20"], capture_output=True)
        if self.proc:
            try:
                self.proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        subprocess.run(["tart", "delete", self.name], capture_output=True)


def in_vm(vm, args, env, plugin=None):
    """Wrap claude args to run in the run's VM: workspace at /work, the bench config at /cfg."""
    inner = list(args)
    inner[inner.index("--settings") + 1] = "/bench/settings.json"
    if plugin:
        inner[inner.index("--plugin-dir") + 1] = "/plugin"
    keys = " ".join(f"{k}={shlex.quote(env[k])}" for k in ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY") if env.get(k))
    return vm.ssh(f"cd /work && env CLAUDE_CONFIG_DIR=/cfg DISABLE_AUTOUPDATER=1 {keys} " + " ".join(shlex.quote(x) for x in inner))


def vm_share():
    """The settings the run's Claude reads, shared read-only at /bench."""
    VM_SHARE.mkdir(parents=True, exist_ok=True)
    (VM_SHARE / "settings.json").write_text(json.dumps(DOCKER_SETTINGS, indent=2))
    # plan-mode examples: the permission host, so headless Claude gets the plan approval step (vm/permission-host.mjs)
    shutil.copy2(BENCH / "vm" / "permission-host.mjs", VM_SHARE / "permission-host.mjs")
    (VM_SHARE / "mcp.json").write_text(json.dumps({"mcpServers": {"bench": {
        "command": "/opt/homebrew/bin/node", "args": ["/bench/permission-host.mjs"]}}}, indent=2))
    return VM_SHARE


PLAN_HOST = ["--mcp-config", "/bench/mcp.json", "--permission-prompt-tool", "mcp__bench__approve"]


def ensure_vm():
    if VM_BASE not in subprocess.run(["tart", "list", "--quiet"], capture_output=True, text=True).stdout.split():
        sys.exit(f"ab: no {VM_BASE} VM. Build it first: see bench/vm/README.md")

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

def parse_walk(text):
    """A **Walk:** line, e.g. "phone · Sign in / Log in → key ArrowRight x2 → scroll → wait 3", as the steps
    capture.mjs follows. None when the example has no walk."""
    text = " ".join(text.split())
    if not text:
        return None
    view = "desktop"
    m = re.match(r"(phone|desktop)\s*·\s*", text)
    if m:
        view, text = m.group(1), text[m.end():]
    steps = []
    for raw in (s.strip() for s in text.split("→")):
        if not raw:
            continue
        k = re.fullmatch(r"key (\S+)(?: x(\d+))?", raw)
        w = re.fullmatch(r"wait (\d+(?:\.\d+)?)", raw)
        if k:
            steps.append({"label": raw, "key": k.group(1), "times": int(k.group(2) or 1)})
        elif w:
            steps.append({"label": raw, "wait": float(w.group(1))})
        elif raw == "scroll":
            steps.append({"label": raw, "scroll": True})
        else:  # "A / B x4": click whichever matches, up to 4 times while one is still showing (multi-screen onboarding)
            c = re.fullmatch(r"(.+?) x(\d+)", raw)
            alts, times = (c.group(1), int(c.group(2))) if c else (raw, 1)
            steps.append({"label": raw, "click": [s.strip() for s in alts.split(" / ") if s.strip()], "times": times})
    return {"view": view, "steps": steps}


def load_specs():
    # examples/PROMPTS.md, plus any private idea prompts in ideas/*.md (gitignored, same format)
    blocks = [b for f in [PROMPTS, *sorted((REPO / "ideas").glob("*.md"))]
              for b in re.split(r"^### ", f.read_text(encoding="utf-8"), flags=re.M)[1:]]
    specs = {}
    for block in blocks:
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
            # plan: the prompt goes in with plan mode on, as a user who presses shift+tab first; later turns don't
            "mode": field("Mode").strip().lower(),
            "fixture": fixture.group(1).strip() if fixture else None,
            "walk": parse_walk(field("Walk")),
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


def _files_hash(parts):
    h = hashlib.sha256()
    for part in parts:
        p = REPO / part
        for f in sorted(p.rglob("*")) if p.is_dir() else [p]:
            if f.is_file() and f.name != ".DS_Store" and "__pycache__" not in f.parts:
                h.update(f.relative_to(REPO).as_posix().encode() + b"\0" + f.read_bytes())
    return h.hexdigest()[:12]


def plugin_version():
    """Which plugin a run used: the commit, whether the plugin files had uncommitted changes, a hash of the
    plugin's own files, and a hash of the method alone, which is what `outdated` compares."""
    git = lambda *a: subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()  # noqa: E731
    return {"commit": git("rev-parse", "--short", "HEAD"), "dirty": bool(git("status", "--porcelain", "--", *PLUGIN_PARTS)),
            "hash": _files_hash(PLUGIN_PARTS), "method": _files_hash(METHOD_PARTS)}


@functools.cache
def method_at(commit):
    """The method hash at a commit, for runs recorded before `method` was: rebuilt from git, the same way."""
    if not commit:
        return None
    git = lambda *a: subprocess.run(["git", "-C", str(REPO), *a], capture_output=True).stdout  # noqa: E731
    files = [f for f in git("ls-tree", "-r", "--name-only", commit, "--", *METHOD_PARTS).decode().splitlines()
             if not f.endswith(".DS_Store") and "__pycache__" not in f]
    if not files:
        return None
    h = hashlib.sha256()
    for part in METHOD_PARTS:  # same order as _files_hash: by part, then sorted path
        for f in sorted(x for x in files if x == part or x.startswith(part + "/")):
            h.update(f.encode() + b"\0" + git("show", f"{commit}:{f}"))
    return h.hexdigest()[:12]


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


def _with_cwd(call_env, cwd):
    argv, env = call_env
    return argv, cwd, env


def claude(args, cwd, env, prompt, timeout=4 * 3600):  # one exchange can hold the whole push (steps 2-8)
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
    text = text.replace("/Volumes/My Shared Files/work", "<workspace>")
    text = text.replace("/home/pwuser", "~").replace("/Users/admin", "~")
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

def save_spec(spec, model, root=None):
    """The prompt, brief and check the example ran with, kept beside its results."""
    path = (root or AUTOPILOT) / model / spec["category"] / spec["name"] / "spec.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({k: spec[k] for k in ("slug", "prompt", "mode", "brief", "check", "fixture")}, indent=2), encoding="utf-8")


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
# The baseline's second turn: when plain Claude is done, the user asks for more in the same words the plugin arm
# uses, with no plugin. It separates what the method adds from just asking again and spending more.
PLAIN_PUSH = "Push it further."
PLAIN_FIRST = Path(".plain") / "first"  # where the baseline's work from before the plain push is kept, in output/


def run_arm(spec, arm, run, a, env, isolation, settings):
    public, _ = fixture_dirs(spec)
    if public == "missing":
        return f"skip {spec['slug']}: needs fixture ({spec['fixture']}) at examples/fixtures/{spec['slug']}/public/"
    sid = str(uuid.uuid4())
    version = plugin_version()  # as the run starts: the plugin can change while a long run is going
    args = base_args(a.model, a.effort, a.max_turns, settings)
    if spec.get("mode") == "plan":  # every exchange of both arms, so the plan approval step exists as it does interactively
        if a.where != "vm":
            return f"skip {spec['slug']}: plan-mode examples run in the VM (the permission host lives there)"
        args += PLAN_HOST
    plugin = None
    if arm == "ambitious":
        plugin = staged_plugin() if a.where != "host" else REPO
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
    vm = None
    if a.where == "vm":  # one VM for the whole run, as one Mac for one chat; booting it isn't counted in its time
        dirs = {"work": (out, False), "cfg": (config_dir(env), False), "bench": (vm_share(), True)}
        if plugin:
            dirs["plugin"] = (plugin, True)
        vm = VM(dirs).__enter__()
    try:
        return _run_arm(spec, arm, run, a, env, isolation, settings, sid, version, args, plugin, out, live, vm)
    finally:
        if vm:
            vm.__exit__(None, None, None)


def _run_arm(spec, arm, run, a, env, isolation, settings, sid, version, args, plugin, out, live, vm):
    def call(extra, with_plugin):
        if a.where == "vm":
            return in_vm(vm, args + extra, env, plugin if with_plugin else None), env
        if a.where == "docker":
            return in_docker(args + extra, out, env, plugin if with_plugin else None), env
        return args + extra, workspace_env(env, out)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    t0, t_wall0 = time.monotonic(), time.time()
    armed = False
    if arm == "ambitious":
        res = claude(*_with_cwd(call(["--session-id", sid], True), out), ARM)
        if "blocked by hook" not in (res.get("result") or ""):
            live.unlink(missing_ok=True)
            shutil.rmtree(out, ignore_errors=True)
            return f"FAIL {spec['slug']} {arm}: {ARM} didn't arm the session: {str(res.get('result'))[:300]}"
        armed = True
    messages, results, client_cost, exchanges = [spec["prompt"]], [], 0.0, []
    plain_first, pushed_after = run / ".plain-first", None
    for turn in range(a.max_exchanges + 1):
        flag = ["--resume", sid] if turn or armed else ["--session-id", sid]
        if turn == 0 and spec.get("mode") == "plan":
            flag += ["--permission-mode", "plan"]
        res = claude(*_with_cwd(call(flag, arm == "ambitious"), out), messages[-1])
        results.append(res)
        exchanges.append({"n": turn + 1, "minutes": round((time.monotonic() - t0) / 60, 2), "cost_usd": round(res.get("total_cost_usd") or 0, 4)})
        snapshot_turn(out, run, turn + 1)
        save_plans(env, run, turn + 1, t_wall0)
        print(f"  [{spec['slug']} {arm} {run.name}] exchange {turn + 1} done at {round((time.monotonic() - t0) / 60, 1)} min, "
              f"${res.get('total_cost_usd') or 0:.2f}{' ERROR ' + str(res.get('result'))[:200] if res.get('is_error') else ''}", flush=True)
        if res.get("is_error") and not res.get("session_id") or turn == a.max_exchanges:
            break
        if arm == "ambitious" and any((out / ".ambition" / "steps" / "8").glob("*")):
            break  # Lock's reply is the final output: the stand-in never answers it (an approval there let it build)
        answer, cost = client_answer(spec, res.get("result") or "", env, settings, a.model, a.effort)
        client_cost += cost
        push = answer.lower().startswith(PLAIN_PUSH.lower().rstrip("."))
        done = answer.upper().startswith("DONE")
        if push and any(m == PLAIN_PUSH for m in messages[1:]):
            break  # one push per run, in both arms: a second would be the stand-in asking again, not the user
        if arm == "not-ambitious" and (push or done) and not pushed_after:
            # plain Claude is done (or offered more): keep its work as the baseline, then ask for more as a user would
            pushed_after = turn + 1
            shutil.rmtree(plain_first, ignore_errors=True)
            save_work(out, plain_first)
            answer = PLAIN_PUSH
        elif push:
            answer = PLAIN_PUSH
        elif done:
            break
        messages.append(answer)

    wall_end = time.monotonic()
    live.unlink(missing_ok=True)
    save_work(out, run / "output")
    shutil.rmtree(out, ignore_errors=True)
    if plain_first.exists():  # kept on the host while the run went on, so the run never saw it
        shutil.copytree(plain_first, run / "output" / PLAIN_FIRST, dirs_exist_ok=True)
        shutil.rmtree(plain_first)
    publish_plans(run, pushed_after)

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
        print(f"  steps: {step_check(run)}", flush=True)

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
        "slug": spec["slug"], "arm": arm, "model": a.model, "effort": a.effort, "isolation": a.where if a.where != "host" else isolation,
        "environment": {"vm": f"{VM_BASE} (macOS, Apple paravirtual GPU)", "docker": DOCKER_IMAGE}.get(a.where, "host"),
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
        "plain_push_after": pushed_after,  # baseline: exchanges before "Push it further." (the plain answer)
        "plugin": version,
        "plugin_commit": version["commit"],
        "claude_version": VM_CLAUDE if a.where == "vm" else subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip(),
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
        return not SKIP_DIRS & set(rel.parts) and (rel.parts[0] not in (".ambition", ".plain") or rel.parts[1:2] in (("first",), ("direct",)))
    pages = [p for p in output.rglob("*.html") if keep(p.relative_to(output))]
    pages.sort(key=lambda p: (p.relative_to(output).parts[0] in (".ambition", ".plain"), p.name != "index.html",
                              len(p.relative_to(output).parts), str(p)))
    return pages[:limit]


CODE_SUFFIXES = {".py", ".js", ".ts", ".sh", ".rb", ".go"}


def work_pages(output, limit=4):
    """The work to compare: its web pages, or, for a deliverable with none (a plan, an essay), its Markdown
    documents, or, failing those, its main script; shortest name first so the main one leads. CLAUDE.md notes,
    tests and working copies are left out."""
    pages = html_pages(output, limit)
    if pages:
        return pages
    def keep(rel):
        return (rel.name != "CLAUDE.md" and not SKIP_DIRS & set(rel.parts)
                and (rel.parts[0] not in (".ambition", ".plain") or rel.parts[1:2] in (("first",), ("direct",))))
    docs = [p for p in output.rglob("*.md") if keep(p.relative_to(output))]
    if not docs:
        # A script deliverable: its main code file, not the tests or check scripts made around it.
        docs = [p for p in output.rglob("*") if p.suffix in CODE_SUFFIXES and keep(p.relative_to(output))
                and not p.name.startswith(("test_", "check", "acceptance")) and not p.stem.endswith(("_test", ".test"))]
    docs.sort(key=lambda p: (p.relative_to(output).parts[0] in (".ambition", ".plain"), len(p.relative_to(output).parts),
                             len(p.stem), p.name))
    return docs[:limit]


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
    if a.where == "docker" and not a.dry_run:
        ensure_image()
    if a.where == "vm" and not a.dry_run:
        ensure_vm()
        if a.parallel > 1:
            sys.exit("ab: VM runs go one at a time (macOS allows two VMs, and each needs 6 GB)")
    jobs = []
    for s in select(load_specs(), a.target):
        if not a.dry_run:
            save_spec(s, a.model)
        for arm in a.arms.split(","):
            arm_dir = AUTOPILOT / a.model / s["category"] / s["name"] / arm
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
SUBJECT_NAME = {"baseline": "Baseline", "pushed": "Plain push", "first": "First version", "final": "Final"}


def subjects(run, arm):
    """The versions a reviewer compares. The baseline run has the plain answer and, since runs had a second
    turn, the plain push ("Push it further." with no plugin); an ambitious run has its first version (made in
    turn 1, before the checkpoint) and its final. Values are page paths inside output/."""
    output = run / "output"
    pages = [pg.relative_to(output).as_posix() for pg in work_pages(output, limit=50)] if output.exists() else []
    if arm == "not-ambitious":
        first = [pg for pg in pages if pg.startswith(PLAIN_FIRST.as_posix() + "/")]
        final = [pg for pg in pages if not pg.startswith(".plain/")]
        if first:
            return {"baseline": first[0], **({"pushed": final[0]} if final else {})}
        return {"baseline": final[0]} if final else {}
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
        venv = {n for n in names if (Path(d) / n / "pyvenv.cfg").exists()}  # virtualenvs are dependencies too
        return venv | {n for n in names if n in SKIP_DIRS or n in WORK_SKIP or working and Path(n).suffix.lower() in IMAGE_EXT}
    shutil.copytree(src, dest, dirs_exist_ok=True, symlinks=False, ignore_dangling_symlinks=True, ignore=ignore)
    prune_large(dest)


MAX_SAVED_BYTES = 10_000_000
NOT_SAVED = "NOT-SAVED.txt"


def prune_large(dest):
    """Leaves out files over 10 MB, such as raw data a run downloaded to test against, and lists them in
    NOT-SAVED.txt so readers know what the run had. The work itself is never that large."""
    dest = Path(dest)
    big = sorted(p for p in dest.rglob("*") if p.is_file() and not p.is_symlink() and p.stat().st_size > MAX_SAVED_BYTES)
    if not big:
        return
    lines = [f"{p.relative_to(dest).as_posix()}  {p.stat().st_size / 1e6:.1f} MB" for p in big]
    for p in big:
        p.unlink()
    note = dest / NOT_SAVED
    old = note.read_text().splitlines()[2:] if note.exists() else []
    note.write_text("Files the run had but that aren't saved here, because each is over 10 MB:\n\n"
                    + "\n".join(sorted(set(old + lines))) + "\n")


def save_plans(env, run, n, since):
    """Plan mode writes its plan to Claude's plans folder, outside the workspace. Keeps each plan file this run
    has written or changed by the end of exchange n in run/plans/turn-<n>/ (on the host, unseen by the run)."""
    plans = [p for p in (config_dir(env) / "plans").glob("*.md") if p.stat().st_mtime >= since - 1]
    if plans:
        dest = run / "plans" / f"turn-{n}"
        dest.mkdir(parents=True, exist_ok=True)
        for p in plans:
            shutil.copy2(p, dest / p.name)


def publish_plans(run, pushed_after):
    """In plan mode Claude keeps its plan in its plans folder, outside the workspace, and may never copy it into
    the project. The plan is the deliverable, so it's published with the work: the last version in output/, and for
    the baseline the version from before the plain push in output/.plain/first/. A plan file the run also wrote
    into the project stays where it put it."""
    turns = sorted((run / "plans").glob("turn-*"), key=lambda d: int(d.name.split("-")[1]))
    if not turns:
        return
    for f in turns[-1].glob("*.md"):
        shutil.copy2(f, run / "output" / f.name)
    if pushed_after:
        before = [d for d in turns if int(d.name.split("-")[1]) <= pushed_after]
        if before:
            (run / "output" / PLAIN_FIRST).mkdir(parents=True, exist_ok=True)
            for f in before[-1].glob("*.md"):
                shutil.copy2(f, run / "output" / PLAIN_FIRST / f.name)


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
        pages = work_pages(d, limit=1)
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
            # a driven run answers the checkpoint in the question picker: its answer comes back as a tool result
            picked = " ".join(str(b.get("content", "")) for b in c if isinstance(b, dict) and b.get("type") == "tool_result"
                              ) if isinstance(c, list) else ""
            if text.strip().lower().startswith("push it further") or re.search(r'="Push it further', picked):
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


def step_check(run):
    """A tripwire for a push that skipped the one-step-at-a-time structure: the step markers Claude wrote
    and whether its step copies differ. Copies that are all identical usually mean they were made in one go."""
    session = run / "transcript" / "session.jsonl"
    marks = set()
    for line in session.read_text(encoding="utf-8").splitlines() if session.exists() else []:
        if '"assistant"' in line and "/8 · " in line:
            d = json.loads(line)
            for b in (d.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "text":
                    marks |= {int(mk.group(1)) for mk in STEP_MARK.finditer(b.get("text", ""))}
    root = run / "output" / ".ambition" / "steps"
    copies = {int(d.name): hashlib.sha256(b"".join(f.read_bytes() for f in sorted(d.rglob("*")) if f.is_file())).hexdigest()
              for d in (root.iterdir() if root.exists() else []) if d.is_dir() and d.name.isdigit()}
    if not marks and not copies:
        return "no push"
    problems = [f"no marker for step {', '.join(map(str, sorted(set(range(2, 9)) - marks)))}" if set(range(2, 9)) - marks else "",
                f"no copy for step {', '.join(map(str, sorted(set(range(2, 9)) - set(copies))))}" if set(range(2, 9)) - set(copies) else "",
                "every step copy is identical" if len(copies) > 2 and len(set(copies.values())) == 1 else ""]
    problems = [p for p in problems if p]
    changed = len(set(copies.values()))
    return ("WARNING " + "; ".join(problems)) if problems else f"all 7 marked and copied, {changed} distinct versions"


def step_subjects(run):
    """{step number: page} for each step the run copied to .ambition/steps/<n>/."""
    root = run / "output" / ".ambition" / "steps"
    out = {}
    for d in root.iterdir() if root.exists() else []:
        if d.is_dir() and d.name.isdigit():
            pages = work_pages(d, limit=1)
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


def review_subject(run, key, page, seconds, site=None, vm=None):
    folder = run / "review" / key
    if (folder / "capture.json").exists():
        return json.loads((folder / "capture.json").read_text())
    folder.mkdir(parents=True, exist_ok=True)
    if vm:  # the review VM sees examples/ at /examples, and renders on the GPU through the installed Chrome
        inside = lambda d: "/examples/" + Path(d).resolve().relative_to(EXAMPLES.resolve()).as_posix()  # noqa: E731
        cmd = vm.ssh("PLAYWRIGHT=/node/node_modules/playwright-core/index.mjs CAPTURE_CHANNEL=chrome node /review/capture.mjs "
                     + " ".join(shlex.quote(x) for x in (inside(site or run / "output"), page, inside(folder), str(seconds))))
    else:
        cmd = ["docker", "run", "--rm", "-v", f"{site or run / 'output'}:/site:ro", "-v", f"{folder}:/out",
               "-v", f"{REVIEW_JS.parent}:/review:ro", "-v", f"{REVIEW_NODE}:/node:ro", DOCKER_IMAGE,
               "node", "/review/capture.mjs", "/site", page, "/out", str(seconds)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
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


def walk_subject(run, key, page, walk, vm=None):
    """Click through the example's fixed walk on one version: run/review/<key>/walk/walk.json plus a
    screenshot per step. Kept until the walk changes."""
    folder = run / "review" / key / "walk"
    spec_file = folder / "spec.json"
    if (folder / "walk.json").exists() and spec_file.exists() and json.loads(spec_file.read_text()) == walk:
        return json.loads((folder / "walk.json").read_text())
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    spec_file.write_text(json.dumps(walk, indent=2), encoding="utf-8")
    if vm:
        inside = lambda d: "/examples/" + Path(d).resolve().relative_to(EXAMPLES.resolve()).as_posix()  # noqa: E731
        cmd = vm.ssh("PLAYWRIGHT=/node/node_modules/playwright-core/index.mjs CAPTURE_CHANNEL=chrome node /review/capture.mjs "
                     + " ".join(shlex.quote(x) for x in (inside(run / "output"), page, inside(folder), "0", inside(spec_file))))
    else:
        cmd = ["docker", "run", "--rm", "-v", f"{run / 'output'}:/site:ro", "-v", f"{folder}:/out",
               "-v", f"{REVIEW_JS.parent}:/review:ro", "-v", f"{REVIEW_NODE}:/node:ro", DOCKER_IMAGE,
               "node", "/review/capture.mjs", "/site", page, "/out", "0", "/out/spec.json"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if not (folder / "walk.json").exists():
        print(f"  walk failed for {run.relative_to(REPO)} {key}: {(p.stderr or p.stdout)[-600:]}", file=sys.stderr)
        return None
    res = json.loads((folder / "walk.json").read_text())
    from PIL import Image
    for s in res["steps"]:
        if s.get("file"):
            png = folder / s["file"]
            s["file"] = png.with_suffix(".webp").name
            Image.open(png).save(folder / s["file"], quality=80)
            png.unlink()
    (folder / "walk.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    return res


def seam_text(v):
    import site_builder
    return site_builder.seam_words(v)[0]


def cmd_review(a):
    if a.where == "vm":
        ensure_vm()
        REVIEW_NODE_MAC.mkdir(parents=True, exist_ok=True)
        dirs = {"examples": (EXAMPLES, False), "review": (REVIEW_JS.parent, True), "node": (REVIEW_NODE_MAC, False)}
        with VM(dirs, label="review") as vm:
            if not (REVIEW_NODE_MAC / "node_modules" / "playwright-core").exists():
                subprocess.run(vm.ssh("cd /node && npm init -y >/dev/null && npm i --silent playwright-core@1.52.0 pngjs@7.0.0"), check=True)
            return _review(a, vm)
    ensure_image()
    ensure_review_node()
    return _review(a, None)


def _review(a, vm):
    for spec in select(load_specs(), a.target):
        ex = (DRIVEN_DIR if a.driven else AUTOPILOT) / a.model / spec["category"] / spec["name"]
        said = re.search(r"(\d+)\s*-?\s*second", spec["prompt"])
        seconds = int(said.group(1)) if said else a.seconds
        jobs, runs, reuse = [], [], []
        for arm in ARMS:
            for run in sorted(ex.glob(f"{arm}/run-*")):
                if a.run and arm == "ambitious" and run.name != f"run-{a.run}" or not (run / "metrics.json").exists():
                    continue
                runs.append(run)
                subj = subjects(run, arm)
                jobs += [(run, key, page, None) for key, page in subj.items() if page.endswith(".html")]
                for n, page in turn_subjects(run).items():
                    if not page.endswith(".html"):
                        continue  # documents are read on the site, not captured
                    # a turn that left the first version or the final as it is reuses that capture
                    body = (run / "turns" / f"turn-{n}" / page).read_bytes()
                    same = [k for k, pg in subj.items() if (run / "output" / pg).read_bytes() == body]
                    if same:
                        reuse.append((run / "review" / same[0], run / "review" / f"turn-{n}"))
                    else:
                        jobs.append((run, f"turn-{n}", page, run / "turns" / f"turn-{n}"))
                steps = run / "output" / ".ambition" / "steps"
                for n, page in step_subjects(run).items():
                    if not page.endswith(".html"):
                        continue
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
            caps = list(pool.map(lambda j: review_subject(j[0], j[1], j[2], seconds, j[3], vm), jobs))
            measured.result()
        for src, dst in reuse:
            if (src / "capture.json").exists():
                shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(src, dst)
        if spec.get("walk"):  # the four versions a reader compares, clicked through the same fixed path
            walks = [(run, key, page) for run in runs for key, page in subjects(run, run.parent.name).items() if page.endswith(".html")]
            with ThreadPoolExecutor(max_workers=2) as pool:
                for (run, key, page), res in zip(walks, pool.map(lambda w: walk_subject(*w, spec["walk"], vm), walks)):
                    if res:
                        missed = sum(1 for s in res["steps"] if not s.get("file"))
                        print(f"{run.relative_to(REPO)} · {SUBJECT_NAME.get(key, key)} walk: {len(res['steps']) - 1 - missed} steps done, {missed} not in this version, {len(res['errors'])} console errors")
        for (run, key, page, _), cap in zip(jobs, caps):
            if cap and key in SUBJECT_NAME:
                views = "; ".join(f"{n}: {seam_text(v)}, {len(v['errors'])} console errors" for n, v in cap["views"].items())
                print(f"{run.relative_to(REPO)} · {SUBJECT_NAME[key]} ({page}) · {views}")


DATE_LINE = re.compile(r"Today's date is \d{4}-\d{2}-\d{2}\.?")
PLAN_NAME = re.compile(r"/plans/[a-z0-9-]+\.md")  # plan mode names each session's plan file at random


def turn1_input(session):
    """What the model was sent in the run's first API call, from the saved (scrubbed) transcript: the request
    shape (system prompt and tools), the parameters, and every message block, with only the date and plan mode's random plan file name normalised."""
    shape, params, blobs = None, None, []
    for line in Path(session).read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        if d.get("type") == "api-request-shape" and shape is None:
            shape = d.get("shapeHash")
        elif d.get("type") == "api-request-blob":
            blobs.append(PLAN_NAME.sub("/plans/<plan>.md", DATE_LINE.sub("<date>", json.dumps(d.get("message"), sort_keys=True))))
        elif d.get("type") == "api-request":
            params = d.get("params")
            break  # the first call: everything it was sent is above this line
    return {"shape": shape, "params": params, "messages": sorted(blobs)}


def check_turn1(run, spec, model):
    """The gate: turn 1 of the ambitious run must be sent exactly what the baseline was sent. Writes
    turn1-input.json with the verdict and, if they differ, a diff of what differs."""
    base = AUTOPILOT / model / spec["category"] / spec["name"] / "not-ambitious" / "run-1" / "transcript" / "session.jsonl"
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
    run = (DRIVEN_DIR if a.driven else AUTOPILOT) / a.model / spec["category"] / spec["name"] / "ambitious" / f"run-{a.run}"
    if not (run / "metrics.json").exists():
        sys.exit(f"ab: no run at {run.relative_to(REPO)}")
    gate = a.gate
    if not gate and a.driven:
        gate = "na"  # a person typed turn 1, so there is no stand-in baseline to match
    if not gate:
        check = json.loads((run / "turn1-input.json").read_text()) if (run / "turn1-input.json").exists() else None
        if check is None:
            sys.exit("ab: no turn1-input.json for this run; pass --gate after checking turn 1's input by hand")
        gate = "pass" if check["identical"] else "fail"
    if a.steps_only:  # add or replace the step summary without touching the recorded verdict
        if not a.steps:
            sys.exit("ab: --steps-only needs --steps")
        shutil.copy2(a.steps, run / "steps.md")
        print(f"wrote {(run / 'steps.md').relative_to(REPO)}")
        return
    if not a.result or not a.note:
        sys.exit("ab: verdict needs --result and --note")
    verdict = {"gate": gate, "result": a.result, "preview_worth": a.preview, "push_worth": a.push,
               "summary": a.note, "decided_by": a.by, "date": time.strftime("%Y-%m-%d"),
               "plugin": json.loads((run / "metrics.json").read_text()).get("plugin")}
    (run / "verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    if a.notes:
        shutil.copy2(a.notes, run / "review.md")
    if a.steps:
        shutil.copy2(a.steps, run / "steps.md")
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
    found = [b for b in re.findall(r"```[a-z]*\n(You asked for:.*?)```", t.read_text(encoding="utf-8"), re.S)
             if "<original>" not in b]  # not the template the hook sends
    return found[0].strip() if found else ""


def load_run(run, arm, current):
    m = json.loads((run / "metrics.json").read_text())
    if m.get("driven") and (run / "transcript" / "session.jsonl").exists():  # derived, so fixes to the split apply
        m["exchange_log"] = session_exchanges(run / "transcript" / "session.jsonl", m["cost_usd"])
        m["exchanges"] = len(m["exchange_log"])
    plugin = m.get("plugin") or {"commit": m.get("plugin_commit"), "dirty": None, "hash": None}
    reviews = {}
    for key in subjects(run, arm):
        cf = run / "review" / key / "capture.json"
        if cf.exists():
            reviews[key] = json.loads(cf.read_text())
    walks = {key: json.loads(wf.read_text()) for key in subjects(run, arm) if (wf := run / "review" / key / "walk" / "walk.json").exists()}
    cj = run / "checks" / "checks.json"
    return {"dir": run, "n": int(run.name.split("-")[1]), "arm": arm, "metrics": m, **run_figures(run),
            "exchange_log": m.get("exchange_log") or [], "plugin": plugin,
            "plain": plain_figures({"metrics": m, "exchange_log": m.get("exchange_log") or [], **run_figures(run)}),
            "outdated": arm == "ambitious" and (plugin.get("method") or method_at(plugin.get("commit"))) != current,
            "subjects": subjects(run, arm), "reviews": reviews, "walks": walks,
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
    """Everything the results page and the site show, read from examples/autopilot/<model>/<category>/<name>/,
    with any driven runs of the same example from examples/driven/."""
    specs = {s["slug"]: s for s in load_specs().values()}
    current = plugin_version()["method"]
    out = []
    def arm_runs(root):
        return {arm: [load_run(m.parent, arm, current) for m in sorted(root.glob(f"{arm}/run-*/metrics.json"),
                                                                      key=lambda m: int(m.parent.name.split("-")[1]))]
                for arm in ARMS}
    # every example with autopilot runs, driven runs or both; an idea someone only drove still gets a page
    rels = sorted({d.relative_to(root) for root in (AUTOPILOT, DRIVEN_DIR) for d in root.glob("*/*/*") if d.is_dir()})
    for rel in rels:
        ex = AUTOPILOT / rel
        runs, driven = arm_runs(ex), arm_runs(DRIVEN_DIR / rel)
        if not any(runs.values()) and not any(driven.values()):
            continue
        home = AUTOPILOT if any(runs.values()) else DRIVEN_DIR  # where its spec.json lives
        first = (runs["ambitious"] or runs["not-ambitious"] or driven["ambitious"] or driven["not-ambitious"])[0]
        slug = first["metrics"]["slug"]
        if not (home / rel / "spec.json").exists() and slug in specs:
            save_spec(specs[slug], rel.parts[0], home)
        spec = json.loads((home / rel / "spec.json").read_text()) if (home / rel / "spec.json").exists() else {}
        out.append({"dir": ex, "model": rel.parts[0], "category": rel.parts[1], "name": rel.parts[2],
                    "slug": slug, "spec": spec, "baseline": (runs["not-ambitious"] or [None])[-1],
                    "runs": runs["ambitious"][::-1], "plugin_now": current,
                    # runs a person drove (ab.py drive): shown on their own page, never mixed with the autopilot runs
                    "driven": {"baseline": (driven["not-ambitious"] or [None])[-1], "runs": driven["ambitious"][::-1]}
                    if any(driven.values()) else None})
    return out


def plain_figures(b):
    """Cost and minutes of the baseline's plain answer, before its plain push (all of it for older baselines)."""
    k, log = b["metrics"].get("plain_push_after"), b["exchange_log"]
    return (log[k - 1]["cost_usd"], log[k - 1]["minutes"]) if k and len(log) >= k else (b["cost_usd"], b["minutes"])


def preview_figures(r):
    """Turn 1 of an ambitious run is the cheap preview (first version and checkpoint)."""
    log = r["exchange_log"]
    return (log[0]["cost_usd"], log[0]["minutes"]) if log else (None, None)


RESULT_WORD = {"win": "Beats the baseline", "tie": "Ties the baseline", "loss": "Loses to the baseline"}


def results_markdown(data):
    lines = ["# Results", "",
             "Each example has one **baseline**: the prompt exactly as a user would type it, on the same model, in "
             "the same macOS VM with a real browser, followed in the same chat by \"Push it further.\" with no plugin "
             "(the **plain push**). The plugin passes an example only when a single `/be-ambitious` run of the *same "
             "prompt* beats both. Turn 1 of that run makes a first version and stops at a checkpoint, where it gets the "
             "same \"Push it further.\". The gate: turn 1 must be sent exactly what the baseline was sent (system prompt, "
             "tools, parameters and messages, checked from the transcripts), so it's a second plain sample. The final must "
             "beat the baseline, the plain push and the first version. Nothing else is judged "
             "automatically: we review frames, screenshots and the live pages side by side, and record the verdict. "
             "Runs made with an older plugin are marked outdated. [How the bench works](../bench/README.md).", "",
             f"Visual results, with every page live: [results site]({SITE_URL}).", ""]
    for model in sorted({e["model"] for e in data}):
        lines += [f"## {model}", "", "| Example | Verdict | Gate (turn 1) | Baseline | Plain push | Preview (turn 1) | Full run | Plugin |",
                  "|---|---|---|---|---|---|---|---|"]
        for e in (x for x in data if x["model"] == model):
            b = e["baseline"]
            bc, bm = plain_figures(b) if b else (None, None)
            base = f"${bc:.2f} · {bm:.1f} min" if b else "–"
            push = f"${b['cost_usd']:.2f} · {b['minutes']:.1f} min" if b and b["metrics"].get("plain_push_after") else "–"
            if not e["runs"]:
                lines.append(f"| {e['slug']} | no plugin run yet | – | {base} | {push} | – | – | – |")
                continue
            r = e["runs"][0]
            v = r["verdict"] or {}
            pc, pm = preview_figures(r)
            prev = f"${pc:.2f} · {pm:.1f} min" if pc is not None else "–"
            full = f"${r['cost_usd']:.2f} · {r['minutes']:.1f} min"
            if b:
                full += f" ({r['cost_usd'] / b['cost_usd']:.1f}× the plain push)"
            plug = (r["plugin"].get("commit") or "?") + (" · outdated" if r["outdated"] else "")
            lines.append(f"| {e['slug']} | {RESULT_WORD.get(v.get('result'), 'not reviewed')} | {v.get('gate', '–')} | "
                         f"{base} | {push} | {prev} | {full} | {plug} |")
        lines.append("")
        for e in (x for x in data if x["model"] == model):
            rel = e["dir"].relative_to(EXAMPLES).as_posix()
            site = e["dir"].relative_to(AUTOPILOT).as_posix()  # the site keeps <model>/<category>/<name>/
            lines += [f"### {e['slug']}", "", f"> {e['spec'].get('prompt', '')}", ""]
            for r in e["runs"]:
                v = r["verdict"]
                if v:
                    lines += [f"**Run {r['n']}:** {RESULT_WORD.get(v['result'], v['result'])}, gate {v['gate']}. {v.get('summary') or ''}", ""]
            lines += [f"[Files]({rel}/) · [Visual view]({SITE_URL}{site}/)", ""]
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


# ---------- driven runs: a person types every message, in the same VM ----------



def session_exchanges(jsonl, total_cost):
    """[{n, minutes, cost_usd}] per input from the person (a typed message or a question-picker answer), both cumulative at the end of that exchange, as a
    stand-in run's exchange_log is: minutes since the first message, and the session's real total cost split
    by the tokens each exchange's API calls used (input, cache and output weighted roughly as billed)."""
    rows, t0, units, seen, asks = [], None, [], set(), set()
    for line in Path(jsonl).read_text(encoding="utf-8").splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        ts = _ts(d["timestamp"]) if d.get("timestamp") else None
        msg = d.get("message") or {}
        content = msg.get("content")
        text = content if isinstance(content, str) else " ".join(
            c.get("text", "") for c in content or [] if isinstance(c, dict) and c.get("type") == "text")
        # a person's message: origin is missing or human (task notifications carry another kind), and not a local
        # command like /usage or /exit, which makes no API call
        typed = (d.get("type") == "user" and not d.get("isMeta") and not d.get("isSidechain") and text.strip()
                 and (d.get("origin") or {}).get("kind", "human") == "human"
                 and not text.lstrip().startswith(("<command-name>", "<local-command")))
        if d.get("type") == "assistant" and isinstance(content, list):
            asks |= {c.get("id") for c in content if isinstance(c, dict) and c.get("name") == "AskUserQuestion"}
        # the person answering a question picker is their input too, where a stand-in would have typed it
        typed = typed or (d.get("type") == "user" and isinstance(content, list) and any(
            isinstance(c, dict) and c.get("type") == "tool_result" and c.get("tool_use_id") in asks for c in content))
        if typed and ts:
            t0 = t0 or ts
            rows.append({"n": len(rows) + 1, "end": ts})
            units.append(0.0)
        elif rows and ts:
            rows[-1]["end"] = ts
            u = msg.get("usage") or {}
            if d.get("type") == "assistant" and u and msg.get("id") not in seen:  # one API call can span several lines
                seen.add(msg.get("id"))
                units[-1] += (u.get("input_tokens", 0) + 2.0 * u.get("cache_creation_input_tokens", 0)
                              + 0.1 * u.get("cache_read_input_tokens", 0) + 5 * u.get("output_tokens", 0))
    whole, acc, out = sum(units) or 1, 0.0, []
    for r, u in zip(rows, units):  # cumulative, as a resumed headless session reports it
        acc += u
        out.append({"n": r["n"], "minutes": round((r["end"] - t0) / 60, 2), "cost_usd": round(total_cost * acc / whole, 4)})
    return out


def cmd_drive(a):
    """You are the user: the same fresh VM, model, effort, settings and plugin sharing as a stand-in run, but an
    interactive Claude Code session in this terminal, so you type the prompt, answer its questions and decide when
    to push. Everything after (saving the work, the transcript, steps, cost and the site) works as for any run."""
    spec = select(load_specs(), a.target)[0]
    arm = a.arm
    public, _ = fixture_dirs(spec)
    if public == "missing":
        sys.exit(f"ab: {spec['slug']} needs its fixture at examples/fixtures/{spec['slug']}/public/")
    if a.where != "vm":
        sys.exit("ab: driven runs use the VM only")
    ensure_vm()
    env, isolation = load_env()
    if isolation != "clean-config":
        sys.exit("ab: drive needs CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY in bench/.env, as VM runs do (see bench/README.md)")
    arm_dir = DRIVEN_DIR / a.model / spec["category"] / spec["name"] / arm
    # an attempt that stopped before its session started left only the prompt file: reuse its folder
    unfinished = sorted(d for d in arm_dir.glob("run-*") if not (d / "metrics.json").exists()
                        and {f.name for f in d.iterdir()} <= {"prompt-to-type.txt"})
    run = unfinished[0] if unfinished else next_run_dir(arm_dir)
    sid, version = str(uuid.uuid4()), plugin_version()
    plugin = staged_plugin() if arm == "ambitious" else None
    args = ["claude", "--model", a.model, "--effort", a.effort, "--settings", "x", "--setting-sources", "project", "--strict-mcp-config"]
    if plugin:
        args += ["--plugin-dir", str(plugin)]
    out = scratch()
    if public:
        shutil.copytree(public, out, dirs_exist_ok=True)
    run.mkdir(parents=True, exist_ok=True)
    print(f"\nDriving {spec['slug']} · {arm} · {a.model} at {a.effort} effort.\n"
          f"Type this prompt exactly (it's also in {run.relative_to(REPO)}/prompt-to-type.txt):\n\n    {spec['prompt']}\n")
    (run / "prompt-to-type.txt").write_text(spec["prompt"] + "\n", encoding="utf-8")
    if spec.get("mode") == "plan":
        print("This example is in plan mode: press shift+tab until plan mode is on before you send the prompt.\n")
    if arm == "ambitious":
        print(f"Send {ARM} on its own first, then the prompt. Answer its questions as yourself. It runs to step 8 (Lock); exit with /exit after its last reply.\n")
    else:
        print("When plain Claude is done, exit with /exit. The bench saves that answer, then reopens the same chat:\n"
              f"type “{PLAIN_PUSH}” (or what you'd really say to get more), and /exit when it's done.\n")
    input("Press Enter to boot the VM… ")
    dirs = {"work": (out, False), "cfg": (config_dir(env), False), "bench": (vm_share(), True)}
    if plugin:
        dirs["plugin"] = (plugin, True)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    pushed_after = None
    with VM(dirs, label="drive") as vm:
        def session(flag):
            argv = in_vm(vm, args + flag, env, plugin)
            argv.insert(1, "-t")  # a real terminal for the interactive session
            subprocess.run(argv)
        t0 = time.monotonic()
        session(["--session-id", sid])
        session_file = lambda: next(iter(config_dir(env).glob(f"projects/*/{sid}.jsonl")), None)  # noqa: E731
        if arm == "not-ambitious" and session_file():
            pushed_after = len(session_exchanges(session_file(), 0))
            save_work(out, run / ".plain-first")
            input(f"\nSaved the plain answer. Press Enter to reopen the chat for the push ({PLAIN_PUSH})… ")
            session(["--resume", sid])
        wall_end = time.monotonic()
        # The session's real total cost: a resumed -p session reports it, and /cost makes no model call
        res = claude(in_vm(vm, base_args(a.model, a.effort, 1, "x") + ["--resume", sid], env), out, env, "/cost")
    if not session_file():
        shutil.rmtree(out, ignore_errors=True)
        sys.exit("ab: no session was recorded (nothing was sent?)")
    save_work(out, run / "output")
    shutil.rmtree(out, ignore_errors=True)
    if (run / ".plain-first").exists():
        shutil.copytree(run / ".plain-first", run / "output" / PLAIN_FIRST, dirs_exist_ok=True)
        shutil.rmtree(run / ".plain-first")
    tdir = run / "transcript"
    found = session_file()
    copy_scrubbed(found, tdir / "session.jsonl", out, env)
    for sub in (found.with_suffix("") / "subagents").glob("*"):
        copy_scrubbed(sub, tdir / "session" / "subagents" / sub.name, out, env)
    (run / "transcript.md").write_text(render_transcript(tdir / "session.jsonl", f"{spec['slug']} · {arm} · driven"), encoding="utf-8")
    cost = round(res.get("total_cost_usd") or 0, 4)
    exchanges = session_exchanges(tdir / "session.jsonl", cost)
    (run / "prompt.md").write_text(f"# {spec['slug']} · {arm} · driven by a person\n\nEvery message is in transcript.md.\n", encoding="utf-8")
    models = {}
    for model, u in (res.get("modelUsage") or {}).items():
        models[model] = {k: v for k, v in u.items() if isinstance(v, (int, float)) and k not in ("contextWindow", "maxOutputTokens")}
    metrics = {
        "slug": spec["slug"], "arm": arm, "model": a.model, "effort": a.effort, "isolation": "vm", "driven": True,
        "environment": f"{VM_BASE} (macOS, Apple paravirtual GPU)", "started": started, "session_id": sid,
        "exchanges": len(exchanges), "cost_usd": cost, "client_cost_usd": 0,
        # Wall clock of the whole session, including the person's own reading and typing time
        "wall_ms": round((wall_end - t0) * 1000), "duration_ms": 0, "num_turns": 0, "errors": [],
        "permission_denials": [], "by_model": models, "exchange_log": exchanges, "plain_push_after": pushed_after,
        "plugin": version, "plugin_commit": version["commit"], "claude_version": VM_CLAUDE,
    }
    (run / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    txt = subprocess.run([sys.executable, str(METRICS), str(tdir / "session.jsonl")], capture_output=True, text=True).stdout
    (run / "metrics.txt").write_text(f"cost ${cost} · {metrics['wall_ms'] / 1000:.0f}s · {len(exchanges)} messages typed\n{txt}", encoding="utf-8")
    if arm == "ambitious":
        print(f"  steps: {step_check(run)}", flush=True)
    measure(run)
    print(f"done {run.relative_to(REPO)} · ${cost} · {metrics['wall_ms'] / 60000:.0f} min. Next: python3 bench/ab.py review {spec['slug']} --model {a.model} --driven")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    dp = sub.add_parser("drive", help="drive one arm yourself in an interactive session in the VM")
    dp.add_argument("target")
    dp.add_argument("--arm", choices=ARMS, required=True)
    dp.add_argument("--model", default="claude-opus-5-5")
    dp.add_argument("--effort", default="medium")
    dp.add_argument("--where", choices=("vm",), default="vm")
    for name in ("run", "review", "verdict", "report"):
        sp = sub.add_parser(name)
        if name != "report":
            sp.add_argument("target")
        sp.add_argument("--model", default="claude-opus-5-5")
        if name == "run":
            sp.add_argument("--effort", default="medium")  # the recommended reasoning effort, pinned so every run matches
            sp.add_argument("--max-turns", type=int, default=300)  # per claude -p call; the push runs steps 3-8 in one call through Stop-hook continuations
            sp.add_argument("--runs", type=int, default=1)
            sp.add_argument("--arms", default=DEFAULT_ARMS)
            sp.add_argument("--max-exchanges", type=int, default=10)
            sp.add_argument("--parallel", type=int, default=1)
            sp.add_argument("--dry-run", action="store_true")
            sp.add_argument("--where", choices=("vm", "docker", "host"), default="vm",
                            help="vm: a throwaway macOS VM with the GPU (default, for results); docker: the older Linux "
                                 "container with software rendering; host: this machine in the sandbox, for debugging only")
        if name in ("review", "verdict"):
            sp.add_argument("--driven", action="store_true", help="the runs you drove yourself (ab.py drive), not the stand-in runs")
        if name == "review":
            sp.add_argument("--run", type=int, default=None, help="only this ambitious run (the baseline is always included)")
            sp.add_argument("--seconds", type=int, default=10, help="how long to capture, when the prompt doesn't say")
            sp.add_argument("--where", choices=("vm", "docker"), default="vm", help="where captures render: vm (GPU) or docker (software)")
        if name == "verdict":
            sp.add_argument("--run", type=int, required=True)
            sp.add_argument("--gate", choices=("pass", "fail"), help="was turn 1 sent exactly what the baseline was? Defaults to the run's turn1-input.json")
            sp.add_argument("--result", choices=("win", "tie", "loss"), help="the final against the baseline (required unless --steps-only)")
            sp.add_argument("--preview", choices=("yes", "no", "na"), default="na", help="was the turn-1 preview worth its cost?")
            sp.add_argument("--push", choices=("yes", "no", "na"), default="na", help="was pushing on worth its extra cost?")
            sp.add_argument("--note", help="one or two sentences: why (required unless --steps-only)")
            sp.add_argument("--notes", default=None, help="a Markdown file with the full side-by-side review")
            sp.add_argument("--by", default="user", help="who made the call")
            sp.add_argument("--steps", default=None, help="a Markdown file: what each step of the run did, added, found or removed")
            sp.add_argument("--steps-only", action="store_true", help="only add or replace the step summary; keep the verdict as recorded")
    a = p.parse_args()
    {"list": cmd_list, "drive": cmd_drive, "run": cmd_run, "review": cmd_review, "verdict": cmd_verdict, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
