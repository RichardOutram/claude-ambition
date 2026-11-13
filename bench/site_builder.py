"""Builds the GitHub Pages site (docs/) from examples/. Called by `python3 bench/ab.py report`.

Static HTML, generated in full on every build. Markdown is rendered in the browser (marked + DOMPurify),
and produced web pages are previewed in sandboxed iframes. Never hand-edit docs/: re-run the report.
"""
import html
import shutil
from cast import build_cast
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUBJECT = {"baseline": ("Baseline", "The prompt exactly as typed, no plugin.", "not-ambitious"),
           "pushed": ("Plain push", "The baseline, then “Push it further.” in the same chat, still no plugin.", "not-ambitious"),
           "first": ("First version", "Turn 1 of /be-ambitious: the cheap preview, before the checkpoint.", "first"),
           "final": ("Final", "/be-ambitious after pushing on.", "ambitious")}
RESULT = {"win": ("Beats the baseline", "good"), "tie": ("Ties the baseline", "warn"), "loss": ("Loses to the baseline", "bad")}
SKIP = {".git", "node_modules", ".venv", "__pycache__", ".claude", ".cache", "_tools"}
KEEP = ("result.md", "prompt.md", "metrics.json", "metrics.txt", "verdict.json", "review.md", "steps.md")
TEXT_LIMIT = 400_000
IMAGE = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
BINARY = {".pdf", ".zip", ".gz", ".tar", ".db", ".sqlite", ".woff", ".woff2", ".ttf", ".mp4", ".mov", ".wav", ".mp3"}

e = html.escape


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0


def head(title, root, description):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{root}assets/style.css">
<script defer src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/dompurify@3.1.6/dist/purify.min.js"></script>
<script defer src="{root}assets/app.js"></script>
</head>
<body>
<header class="top"><div class="wrap top-in">
  <a class="brand" href="{root}index.html">claude-ambition <span>results</span></a>
  <nav><a href="{root}index.html#method">How it's tested</a><a href="{{repo}}">GitHub</a></nav>
</div></header>
<main class="wrap">
"""


def foot(repo):
    return f"""</main>
<footer class="wrap foot">Generated from <a href="{repo}/tree/main/examples">examples/</a> by <code>bench/ab.py report</code>.
Outputs are shown exactly as produced. Model-made pages run in sandboxed frames.</footer>
</body>
</html>
"""


# ---------- small pieces ----------

def badge(text, tone):
    return f'<span class="badge {tone}">{e(text)}</span>'


def money(x):
    return f"${x:.2f}" if x >= 0.1 or x == 0 else f"${x:.3f}".rstrip("0")  # cents, unless a step costs under 10¢


def plain_split(b):
    """(answer, whole chat): the baseline's plain answer, and that answer plus its plain push."""
    k, log = b["metrics"].get("plain_push_after"), b["exchange_log"]
    whole = (b["cost_usd"], b["minutes"])
    return ((log[k - 1]["cost_usd"], log[k - 1]["minutes"]) if k and len(log) >= k else whole), whole


KINDS = """<section id="kinds" class="method"><h2>Kinds of example</h2>
<p>The prompts cover different kinds of work, and each prompt names the form of what it wants, so both sides make the same kind of thing. How we judge depends on the kind:</p>
<ul class="steps">
  <li><b>Web pages</b> (games, design, education, prototypes, 3D animation). The harness opens every version in a real browser at desktop and phone sizes, records frames over time, checks for console errors and, for looping animations, whether the loop is seamless. We also open each page live and use it. The frames and the live pages are on each example's page.</li>
  <li><b>Documents</b> (analysis, architecture, marketing, written as Markdown). Every version is rendered on the page in full. We read them through, recompute key figures and check that the sources resolve. When a run leaves a script or check beside the document, we run it too.</li>
  <li><b>Scripts</b> (development). The pages show each version's main script in full. We run each version on the same test files, including awkward cases and its undo, and compare what it actually did, not what it says it does.</li>
  <li><b>Plans</b> (planning). The prompt is typed with plan mode on, so the deliverable is the plan itself. Pushing on improves the plan, and may write checks, simulations or a small spike to test it, but the app is never built. We compare the plans as plans: whether someone could act on them, and whether they're right.</li>
</ul>
<p>Every example page also has the full session logs for both sides (replayable), the replies and files from each turn, and, for the plugin, what each step changed and what it cost.</p>
</section>
"""


def bars(rows, fmt):
    """rows: [(label, value, arm)] -> horizontal bars scaled to the largest value."""
    top = max((v for _, v, _ in rows), default=0) or 1
    out = ['<div class="bars">']
    for label, v, arm in rows:
        out.append(f'<div class="bar-row"><span class="bar-label">{e(label)}</span>'
                   f'<span class="bar-track"><span class="bar {arm}" style="width:{max(v / top * 100, 0.6):.1f}%"></span></span>'
                   f'<span class="bar-val">{e(fmt(v))}</span></div>')
    out.append("</div>")
    return "".join(out)


def human(n):
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


def kind(path, size):
    ext = path.suffix.lower()
    if ext in (".md", ".markdown"):
        return "md"
    if ext in (".html", ".htm"):
        return "html"
    if ext in IMAGE:
        return "img"
    if ext in BINARY or size > TEXT_LIMIT:
        return "download"
    return "text"


# ---------- copying ----------

def copy_example(ex, dest):
    if dest.exists():
        shutil.rmtree(dest)
    ignore = shutil.ignore_patterns(*SKIP)
    for r in ([ex["baseline"]] if ex["baseline"] else []) + ex["runs"]:
        target = dest / r["arm"] / f"run-{r['n']}"
        target.mkdir(parents=True)
        for name in KEEP:
            if (r["dir"] / name).exists():
                shutil.copy2(r["dir"] / name, target / name)
        for sub in ("output", "checks", "review", "turns"):
            if (r["dir"] / sub).exists():
                shutil.copytree(r["dir"] / sub, target / sub, ignore=ignore)
        session = r["dir"] / "transcript" / "session.jsonl"
        if session.exists():  # already scrubbed when saved
            build_cast(session, target / "transcript.cast", f"{ex['slug']} · {r['arm']} run {r['n']}")


def files_of(output):
    if not output.exists():
        return []
    found = []
    for p in sorted(output.rglob("*")):
        rel = p.relative_to(output)
        if p.is_file() and not SKIP & set(rel.parts) and not (rel.parts[0] == ".ambition" and rel.parts[1:2] not in (("direct",),)):
            found.append((rel.as_posix(), p.stat().st_size, kind(p, p.stat().st_size)))
    return found


# ---------- the side-by-side ----------

LOOPING = {"on": True}  # set per example page: the seam check only means something when the prompt asks for a loop


def seam_words(v):
    """The loop check in plain words. Figures are the percent of pixels that visibly changed: between the
    last frame and the first, against a typical one-second step. A seamless loop ends where it began."""
    if not v.get("moving"):
        return "still image", "muted"
    if not LOOPING["on"]:
        return "moving", "muted"
    s = v.get("seam") or {}
    first, step = s.get("first_vs_last", 0), s.get("median_step") or 0
    if first <= max(0.05, 0.1 * step):
        return "seamless loop", "good"
    return f"jump at the loop ({first:g}% of pixels change, vs {step:g}% in a typical second)", "bad"


def lighthouse_of(r, page):
    for c in r["checks"]:
        if c["page"] == page:
            return c
    return None


def is_text(page):
    """A document or a script: read in place rather than captured in a browser."""
    return page.endswith(".md") or not page.endswith((".html", ".htm"))


def doc_bits(r, folder_rel, page):
    """For a document (a plan, an essay): the rendered text to read in place, and its size. Other documents
    the version made beside it are linked with their own size (a plan-mode run can leave near-copies, so
    sizes are never summed)."""
    run_rel = f"{r['arm']}/run-{r['n']}"
    path = r["dir"] / folder_rel / page
    docs = sorted(p for p in path.parent.glob("*.md") if p.name != "CLAUDE.md") if path.exists() else []
    words = lambda p: len(p.read_text(encoding="utf-8", errors="replace").split())
    href = f"{run_rel}/{folder_rel}/{e(page)}"
    if not page.endswith(".md"):  # a script: its code, with its length in lines
        lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines()) if path.exists() else 0
        media = f'<div class="md doc-preview" data-md="{href}" data-code></div>'
        return media, [badge(f"{lines:,} lines" if path.exists() else "missing", "muted")]
    media = f'<div class="md doc-preview" data-md="{href}"></div>'
    facts = [badge(f"{words(path):,} words" if path.exists() else "missing", "muted")]
    base = page.rsplit("/", 1)[0] + "/" if "/" in page else ""
    for p in docs:
        if p != path:
            facts.append(f'<a class="badge muted" href="{run_rel}/{folder_rel}/{e(base + p.name)}" target="_blank" rel="noopener">+ {e(p.name)} · {words(p):,} words ↗</a>')
    return media, facts


def subject_card(r, key, cost, minutes):
    """One column of the side-by-side: what this version looks like over time, plus how to open it."""
    name, note, tone = SUBJECT[key]
    page = r["subjects"].get(key)
    if not page:
        return ""
    run_rel = f"{r['arm']}/run-{r['n']}"
    live = f"{run_rel}/output/{e(page)}"
    money_line = f"{money(cost)} · {minutes:.1f} min" if cost is not None else ""
    if is_text(page):
        media, facts = doc_bits(r, "output", page)
        return f"""<article class="subject {tone}">
  <header><h3><span class="dot {tone}"></span>{e(name)}</h3><span class="cost">{e(money_line)}</span></header>
  <p class="hint">{e(note)}</p>
  <div class="subject-media">{media}</div>
  <div class="facts">{"".join(facts)}</div>
  <p class="open"><a href="{live}" target="_blank" rel="noopener">Open it ↗</a> <code>{e(page)}</code></p>
</article>"""
    cap = r["reviews"].get(key)
    media, facts = "", []
    if cap:
        d = cap["views"].get("desktop", {})
        ph = cap["views"].get("phone", {})
        sheet = d.get("sheet")
        if d.get("moving") and sheet:
            media = (f'<a class="sheet" href="{run_rel}/review/{key}/{e(sheet)}"><img loading="lazy" src="{run_rel}/review/{key}/{e(sheet)}" '
                     f'alt="{e(name)}: one frame per second across the loop, desktop"></a>')
        elif d.get("frames"):
            f0 = d["frames"][0]["file"]
            media = f'<img loading="lazy" src="{run_rel}/review/{key}/{e(f0)}" alt="{e(name)}, desktop">'
        for vname, v in (("desktop", d), ("phone", ph)):
            if v:
                words, t = seam_words(v)
                errs = len(v.get("errors") or [])
                facts.append(badge(f"{vname}: {words}", t))
                if errs:
                    facts.append(badge(f"{vname}: {errs} console error{'s' if errs != 1 else ''}", "bad"))
        if ph.get("sheet") and ph.get("moving"):
            media += (f'<details class="phone-sheet"><summary>Phone frames</summary><img loading="lazy" src="{run_rel}/review/{key}/{e(ph["sheet"])}" '
                      f'alt="{e(name)}: one frame per second across the loop, phone"></details>')
    else:
        lh = lighthouse_of(r, page)
        shot = (lh or {}).get("screenshots", {})
        f = shot.get("desktop") or shot.get("mobile")
        if f:
            media = f'<img loading="lazy" src="{run_rel}/checks/{e(f)}" alt="{e(name)} screenshot">'
    lh = lighthouse_of(r, page)
    if lh and (lh.get("lighthouse") or {}).get("scores"):
        sc = lh["lighthouse"]["scores"]
        facts.append(" ".join(f'<span class="score {"good" if (v or 0) >= 90 else "warn" if (v or 0) >= 50 else "bad"}"><b>{v}</b>{e(k.replace("-", " "))}</span>'
                              for k, v in sc.items() if v is not None))
    return f"""<article class="subject {tone}">
  <header><h3><span class="dot {tone}"></span>{e(name)}</h3><span class="cost">{e(money_line)}</span></header>
  <p class="hint">{e(note)}</p>
  <div class="subject-media">{media or '<p class="hint">Not captured yet: run <code>ab.py review</code>.</p>'}</div>
  <div class="facts">{"".join(facts)}</div>
  <p class="open"><a href="{live}" target="_blank" rel="noopener">Open it live ↗</a> <code>{e(page)}</code></p>
  <details class="live"><summary>Play it here</summary><div class="frame"><iframe loading="lazy" sandbox="allow-scripts" src="{live}" title="{e(name)}"></iframe></div></details>
</article>"""


def plain_figures(b):
    """Cost and minutes of the baseline's plain answer, before its plain push (from ab.py's load_run)."""
    return b["plain"]


def baseline_cards(b):
    return [subject_card(b, "baseline", *plain_figures(b)), subject_card(b, "pushed", b["cost_usd"], b["minutes"])]


def trio(ex, r):
    b = ex["baseline"]
    pc, pm = (r["exchange_log"][0]["cost_usd"], r["exchange_log"][0]["minutes"]) if r["exchange_log"] else (None, None)
    cards = [*(baseline_cards(b) if b else []),
             subject_card(r, "first", pc, pm), subject_card(r, "final", r["cost_usd"], r["minutes"])]
    return f'<div class="trio">{"".join(c for c in cards if c)}</div>'


def timeline(ex, r):
    """How the run spent its money: turn 1 is the preview and checkpoint, later turns are pushing on."""
    b = ex["baseline"]
    log = r["exchange_log"]
    steps = r.get("steps") or []
    unit = "step" if steps else "exchange"
    rows, prev, spent = [], 0.0, 0.0  # both logs are cumulative; each bar is what that step added
    for i, t in enumerate(steps or log):
        if i == 0:
            label = "Turn 1 · first version + checkpoint"
        else:
            label = f"Turn {t['n']} · {t['name']}" if steps else f"Exchange {t['n']}"
        rows.append((label, t["cost_usd"] - spent, "first" if i == 0 else "ambitious", t["minutes"] - prev))
        prev, spent = t["minutes"], t["cost_usd"]
    if not rows:
        rows.append(("Whole run", r["cost_usd"], "ambitious", r["minutes"]))
    if b:
        bc, bm = plain_figures(b)
        if "pushed" in b["subjects"]:
            rows.insert(0, ("Baseline + plain push", b["cost_usd"], "not-ambitious", b["minutes"]))
        rows.insert(0, ("Baseline · plain prompt", bc, "not-ambitious", bm))
    cost = bars([(lab, c, t) for lab, c, t, _ in rows], money)
    mins = bars([(lab, m, t) for lab, _, t, m in rows], lambda v: f"{v:.1f} min")
    mult = ""
    if b:
        bc, bm = plain_figures(b)
        mult = f'<p class="hint">Full run: <b>{r["cost_usd"] / bc:.1f}×</b> the baseline\'s cost and <b>{r["minutes"] / bm:.1f}×</b> its time.'
        if "pushed" in b["subjects"]:
            mult += f' The plain push: <b>{b["cost_usd"] / bc:.1f}×</b> and <b>{b["minutes"] / bm:.1f}×</b>.'
        if log:
            mult += f' The preview alone: <b>{log[0]["cost_usd"] / bc:.1f}×</b> and <b>{log[0]["minutes"] / bm:.1f}×</b>.'
        mult += "</p>"
    note = ("" if steps or not log else '<p class="hint">This run is older than the step markers, so it\'s split by exchange '
            '(each message to Claude), not by step of the method.</p>')
    return (f'<div class="grid2"><div class="card"><h3>Cost by {unit}</h3>{cost}</div>'
            f'<div class="card"><h3>Time by {unit}</h3>{mins}</div></div>{mult}{note}')


def step_progression(r):
    """The work at the end of each step of the method that changed it, with what had been spent by then."""
    run_rel = f"{r['arm']}/run-{r['n']}"
    spent = {t["n"]: t for t in r.get("steps") or []}
    pages = {1: {"page": r["subjects"].get("first"), "capture": r["reviews"].get("first"), "dir": "output", "review": "first"}}
    for n, sp in r["step_pages"].items():
        pages[n] = {**sp, "dir": f"output/.ambition/steps/{n}", "review": f"step-{n}"}
    cards, seen = [], set()
    for n in sorted(pages):
        pg = pages[n]
        if not pg["page"]:
            continue
        cap = pg["capture"]
        body = (r["dir"] / pg["dir"] / pg["page"]).read_bytes() if (r["dir"] / pg["dir"] / pg["page"]).exists() else b""
        if body in seen:  # a step that only talked, or checked without changing the work
            continue
        seen.add(body)
        name = f"Turn {n} · {spent[n]['name']}" if n in spent else "Turn 1 · first version" if n == 1 else f"Turn {n}"
        sp = spent.get(n)
        figs = f"{money(sp['cost_usd'])} · {sp['minutes']:.1f} min so far" if sp else ""
        media, facts = "", ""
        if is_text(pg["page"]):
            media, fl = doc_bits(r, pg["dir"], pg["page"])
            facts = "".join(fl)
        if cap:
            d = cap["views"].get("desktop", {})
            src = d.get("sheet") if d.get("moving") else (d.get("frames") or [{}])[0].get("file")
            if src:
                img = f"{run_rel}/review/{pg['review']}/{e(src)}"
                media = f'<a href="{img}"><img loading="lazy" src="{img}" alt="{e(name)}: frames across the loop"></a>'
            words, tone = seam_words(d)
            errs = sum(len(v.get("errors") or []) for v in cap["views"].values())
            facts = badge(words, tone) + (badge(f"{errs} console error{'s' if errs != 1 else ''}", "bad") if errs else "")
        cards.append(f"""<article class="turn">
  <header><b>{e(name)}</b><span>{e(figs)}</span></header>
  <div class="subject-media">{media or '<p class="hint">Not captured yet.</p>'}</div>
  <div class="facts">{facts}</div>
  <p class="open"><a href="{run_rel}/{pg['dir']}/{e(pg["page"])}" target="_blank" rel="noopener">Open turn {n} live ↗</a></p>
</article>""")
    return f"""<h3 class="label">How it got there</h3>
<p class="hint">A turn is a step of the method: turn 1 is the plain first version, turn 2 is altitude (the questions, the answers and the work on them), then depth, challenge, range, judge, stretch and lock. Each card is the work at the end of a turn that changed it, with what had been spent by then.</p>
<div class="turns">{"".join(cards)}</div>"""


def progression(r):
    """The work as it stood at the end of each turn that changed it, so you can see what each turn bought."""
    if r.get("step_pages"):
        return step_progression(r)
    if not r["turns"]:
        return ""
    run_rel = f"{r['arm']}/run-{r['n']}"
    log = {t["n"]: t for t in r["exchange_log"]}
    last = r["turns"][-1]["n"]
    cards = []
    for t in r["turns"]:
        n, cap = t["n"], t["capture"]
        name = "First version · checkpoint" if n == 1 else "Final" if n == last else f"Turn {n}"
        spent = log.get(n)
        figs = f"{money(spent['cost_usd'])} · {spent['minutes']:.1f} min so far" if spent else ""
        media, facts = "", ""
        if is_text(t["page"]):
            media, fl = doc_bits(r, f"turns/turn-{n}", t["page"])
            facts = "".join(fl)
        if cap:
            d = cap["views"].get("desktop", {})
            src = d.get("sheet") if d.get("moving") else (d.get("frames") or [{}])[0].get("file")
            if src:
                media = f'<a href="{run_rel}/review/turn-{n}/{e(src)}"><img loading="lazy" src="{run_rel}/review/turn-{n}/{e(src)}" alt="{e(name)}: frames across the loop"></a>'
            words, tone = seam_words(d)
            errs = sum(len(v.get("errors") or []) for v in cap["views"].values())
            facts = badge(words, tone) + (badge(f"{errs} console error{'s' if errs != 1 else ''}", "bad") if errs else "")
        cards.append(f"""<article class="turn">
  <header><b>{e(name)}</b><span>{e(figs)}</span></header>
  <div class="subject-media">{media or '<p class="hint">Not captured yet.</p>'}</div>
  <div class="facts">{facts}</div>
  <p class="open"><a href="{run_rel}/turns/turn-{n}/{e(t["page"])}" target="_blank" rel="noopener">Open turn {n} live ↗</a></p>
</article>""")
    return f"""<h3 class="label">How it got there</h3>
<p class="hint">This run is older than the step markers, so these are the exchanges (each message to Claude) that changed the work, with what had been spent by then.</p>
<div class="turns">{"".join(cards)}</div>"""


def verdict_banner(r):
    v = r["verdict"]
    if not v:
        return '<div class="banner muted"><b>Not reviewed yet.</b> We compare the versions side by side and record the call with <code>ab.py verdict</code>.</div>'
    word, tone = RESULT.get(v["result"], (v["result"], "muted"))
    worth = {"yes": "worth it", "no": "not worth it", "na": None}
    extra = [x for x in (f"preview {worth[v.get('preview_worth', 'na')]}" if worth.get(v.get("preview_worth", "na")) else None,
                         f"pushing on {worth[v.get('push_worth', 'na')]}" if worth.get(v.get("push_worth", "na")) else None) if x]
    return f"""<div class="banner {tone}">
  <div class="badges">{badge(word, tone)}{badge("Gate " + v["gate"], "good" if v["gate"] == "pass" else "bad")}{"".join(badge(x, "muted") for x in extra)}</div>
  <p>{e(v.get("summary") or "")}</p>
  <p class="hint">Decided by {e(v.get("decided_by", "user"))} on {e(v.get("date", ""))}, after a side-by-side review.</p>
</div>"""


def run_panel(r, repo, ex):
    run_rel = f"{r['arm']}/run-{r['n']}"
    m = r["metrics"]
    files = files_of(r["dir"] / "output")
    file_list = "".join(
        f'<li><a href="{run_rel}/output/{e(rel)}" data-file="{run_rel}/output/{e(rel)}" data-kind="{k}">{e(rel)}</a><span>{human(size)}</span></li>'
        for rel, size, k in files) or '<li class="hint">No files. The whole answer is the reply above.</li>'
    src = f"{repo}/tree/main/examples/{ex['dir'].relative_to(ex['dir'].parents[2]).as_posix()}/{run_rel}"
    denials = len(m.get("permission_denials") or [])
    return f"""<div class="stats">
  <div><b>{money(r["cost_usd"])}</b><span>cost</span></div>
  <div><b>{r["minutes"]:.1f}</b><span>minutes</span></div>
  <div><b>{r["output_tokens"]:,}</b><span>output tokens</span></div>
  <div><b>{r["exchanges"]}</b><span>user messages</span></div>
  {f'<div><b>{denials}</b><span>tool denials</span></div>' if denials else ''}
</div>
<details data-md-on-open><summary>What the user side sent ({r["exchanges"]} message{"s" if r["exchanges"] != 1 else ""})</summary><div class="md" data-md="{run_rel}/prompt.md"></div></details>
<h3 class="label">Final reply</h3>
<div class="md reply" data-md="{run_rel}/result.md"></div>
<h3 class="label">Files ({len(files)})</h3>
<div class="files"><ul>{file_list}</ul><div class="viewer" hidden><div class="viewer-head"><code></code><a target="_blank" rel="noopener">raw ↗</a></div><div class="viewer-body"></div></div></div>
<p class="hint">Replay the session in the terminal at the top of the page, or read the full transcript with every tool call <a href="{src}">on GitHub</a>.</p>"""


def plugin_line(r, ex):
    p = r["plugin"]
    text = f"plugin {p.get('commit') or '?'}" + (" with uncommitted changes" if p.get("dirty") else "")
    if r["outdated"]:
        return f'<div class="banner warn"><b>Outdated.</b> This run used {e(text)}; the plugin has changed since, so it may not reflect what you\'d get today.</div>'
    if p.get("dirty"):
        return (f'<p class="hint">Made with the current plugin. The run recorded {e(text)}; those changes were '
                f'committed afterwards as they were, so the plugin files match.</p>')
    return f'<p class="hint">Made with {e(text)}, the current plugin.</p>'


def terminal(ex):
    """A Sublime Text-style window under the hero: one tab per run, each replaying its session."""
    order = [r for r in ([ex["baseline"]] if ex["baseline"] else []) + ex["runs"]
             if (r["dir"] / "transcript" / "session.jsonl").exists()]
    if not order:
        return ""
    tabs = []
    for i, r in enumerate(order):
        rel = f"{r['arm']}/run-{r['n']}"
        name = "baseline.session" if r["arm"] == "not-ambitious" else f"be-ambitious-{r['n']}.session"
        stats = f"{r['minutes']:.1f} min · {money(r['cost_usd'])} · {r['exchanges']} user message{'s' if r['exchanges'] != 1 else ''}"
        tabs.append(f'<button role="tab" class="{r["arm"]}" aria-selected="{"true" if i == 0 else "false"}" '
                    f'data-cast="{rel}/transcript.cast" data-stats="{e(stats)}">{e(name)}</button>')
    return f"""<section class="term-section" aria-label="Session replays">
  <div class="term">
    <div class="term-bar"><span class="term-dots" aria-hidden="true"><i></i><i></i><i></i></span><div class="term-tabs" role="tablist">{"".join(tabs)}</div></div>
    <div class="term-screen"></div>
    <div class="term-status"><span class="term-stats"></span><span>Replayed from the saved transcript · long waits shortened</span></div>
  </div>
</section>"""


def example_page(ex, root, repo):
    spec = ex["spec"]
    LOOPING["on"] = "loop" in spec.get("prompt", "").lower()
    sections = []
    for r in ex["runs"]:
        method = ""
        if r["restatement"]:
            method = f'<details><summary>How the run restated the task</summary><pre class="restate">{e(r["restatement"])}</pre></details>'
        review = f'<details data-md-on-open open><summary>Our side-by-side review</summary><div class="md" data-md="ambitious/run-{r["n"]}/review.md"></div></details>' \
            if (r["dir"] / "review.md").exists() else ""
        steps = (f'<details class="steps" data-md-on-open open><summary>What each step did</summary><p class="hint">Our summary of each step from the run\'s own reports and the work it left after each step: what it did, what it added, what it found and what it removed.</p>'
                 f'<div class="md" data-md="ambitious/run-{r["n"]}/steps.md"></div></details>') if (r["dir"] / "steps.md").exists() else ""
        sections.append(f"""<section class="run-block" id="run-{r['n']}">
  <h2>/be-ambitious, run {r["n"]}</h2>
  {plugin_line(r, ex)}
  {verdict_banner(r)}
  {trio(ex, r)}
  {review}
  {steps}
  {progression(r)}
  <h3 class="label">Where the time and money went</h3>
  {timeline(ex, r)}
  {method}
</section>""")
    if not ex["runs"] and ex["baseline"]:
        sections.append(f'<section><h2>Baseline only so far</h2>{trio_baseline(ex)}</section>')
    tabs, panels = [], []
    order = ([ex["baseline"]] if ex["baseline"] else []) + ex["runs"]
    for i, r in enumerate(order):
        key = f"{r['arm']}-{r['n']}"
        label = "Baseline" if r["arm"] == "not-ambitious" else f"/be-ambitious · run {r['n']}"
        sel = "true" if i == 0 else "false"
        tabs.append(f'<button role="tab" aria-selected="{sel}" data-tab="{key}" class="{r["arm"]}">{e(label)}</button>')
        panels.append(f'<div role="tabpanel" data-panel="{key}"{"" if i == 0 else " hidden"}>{run_panel(r, repo, ex)}</div>')
    body = f"""<nav class="crumbs"><a href="{root}index.html">Results</a> / {e(ex["model"])} / {e(ex["category"])}</nav>
<section class="hero ex">
  <p class="eyebrow">{e(ex["slug"])}</p>
  <h1>“{e(spec.get("prompt", ""))}”</h1>
  <p class="lede">Both sides got exactly this prompt, then the same words to go on: “Push it further.” The baseline goes on as plain Claude; the plugin runs its method. The plugin's turn 1 is sent exactly what the baseline was sent, checked from the transcripts, so it's a second plain sample. The plugin passes only if its final beats the baseline, the plain push and its own first version.</p>
  <details class="context"><summary>What we look for</summary><p>{e(spec.get("check", ""))}</p></details>
</section>
{terminal(ex)}
{"".join(sections)}
<section><h2>Replies and files</h2><div class="tabs" role="tablist">{"".join(tabs)}</div>{"".join(panels)}</section>
"""
    player = ('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/asciinema-player@3.17.0/dist/bundle/asciinema-player.css">\n'
              '<script defer src="https://cdn.jsdelivr.net/npm/asciinema-player@3.17.0/dist/bundle/asciinema-player.min.js"></script>\n</head>')
    page = head(f"{ex['slug']} · claude-ambition", root, spec.get("prompt", "")).replace("{repo}", repo).replace("</head>", player, 1)
    return page + body + foot(repo)


def trio_baseline(ex):
    b = ex["baseline"]
    return f'<div class="trio">{"".join(baseline_cards(b))}</div>'


# ---------- index ----------

def thumb(ex, rel):
    for r in ex["runs"] + ([ex["baseline"]] if ex["baseline"] else []):
        for key in ("final", "baseline"):
            cap = r["reviews"].get(key)
            if cap:
                d = cap["views"].get("desktop", {})
                frames = d.get("frames") or []
                if frames:
                    pick = frames[len(frames) // 3]["file"]
                    return f'<img loading="lazy" src="{rel}/{r["arm"]}/run-{r["n"]}/review/{key}/{e(pick)}" alt="">'
        for c in r["checks"]:
            f = c.get("screenshots", {}).get("desktop")
            if f:
                return f'<img loading="lazy" src="{rel}/{r["arm"]}/run-{r["n"]}/checks/{e(f)}" alt="">'
    return ""


def index_page(data, repo):
    rows, cards = [], []
    for ex in data:
        rel = f"{ex['model']}/{ex['category']}/{ex['name']}"
        b = ex["baseline"]
        r = ex["runs"][0] if ex["runs"] else None
        v = (r or {}).get("verdict") or {}
        word, tone = RESULT.get(v.get("result"), ("Not reviewed", "muted"))
        if not r:
            word, tone = "No plugin run yet", "muted"
        gate = badge("Gate " + v["gate"], "good" if v["gate"] == "pass" else "bad") if v.get("gate") else "–"
        base = pushed = "–"
        if b:
            (bc, bm), (pc, pm) = plain_split(b)
            base, pushed = f"{money(bc)} · {bm:.1f} min", f"{money(pc)} · {pm:.1f} min"
        prev = full = plug = "–"
        if r:
            if r["exchange_log"]:
                t1 = r["exchange_log"][0]
                prev = f"{money(t1['cost_usd'])} · {t1['minutes']:.1f} min"
            full = f"{money(r['cost_usd'])} · {r['minutes']:.1f} min"
            if b:
                full += f'<span class="sub">{r["cost_usd"] / pc:.1f}× the plain push\'s cost</span>'
            plug = e(r["plugin"].get("commit") or "?") + (" " + badge("outdated", "warn") if r["outdated"] else "")
        rows.append(f"""<tr><td><a href="{rel}/index.html">{e(ex["slug"])}</a><span class="sub">{e(ex["model"])}</span></td>
<td><div class="badges">{badge(word, tone)}{gate if v.get("gate") else ""}</div></td><td class="num">{base}</td><td class="num">{pushed}</td><td class="num">{prev}</td><td class="num">{full}</td><td>{plug}</td></tr>""")
        cards.append(f"""<a class="ex-card" href="{rel}/index.html">
  <div class="ex-visual">{thumb(ex, rel) or f'<blockquote>“{e(ex["spec"].get("prompt", ""))}”</blockquote>'}</div>
  <div class="ex-body"><p class="eyebrow">{e(ex["category"])}</p><h3>{e(ex["spec"].get("prompt", ex["slug"]))}</h3>
  <p>{e(v.get("summary", ""))}</p><div class="badges">{badge(word, tone)}{gate if v.get("gate") else ""}</div></div>
</a>""")
    body = f"""<section class="hero">
  <p class="eyebrow">An open test of the <a href="{repo}">ambition plugin</a> for Claude Code</p>
  <h1>Does <code>/be-ambitious</code> beat the same prompt typed plainly?</h1>
  <p class="lede">Each example is one ordinary request. Plain Claude answers it, then gets “Push it further.” The plugin gets the same prompt and the same words, and runs its seven-step method instead. The plugin wins an example only if its final beats all three plain versions. Every version is on its page.</p>
</section>
<section id="results"><h2>Results</h2>
<div class="table-wrap"><table class="results"><thead><tr><th>Example</th><th>Verdict<span class="sub">and turn-1 gate</span></th><th>Baseline<span class="sub">plain answer</span></th><th>Plain push<span class="sub">answer + “Push it further.”</span></th><th>Preview<span class="sub">plugin turn 1</span></th><th>Full run<span class="sub">plugin, all steps</span></th><th>Plugin</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
<p class="hint">One run per example, judged by us. These are illustrations of the plugin, not measurements. The plugin didn't win every example, and its wins cost many times more than asking plainly: <a href="{repo}#what-we-found-so-far-sonnet-55-november-2026">our overall assessment</a>.</p>
</section>
<section><h2>Examples</h2><div class="ex-grid">{"".join(cards)}</div></section>
{KINDS}
<section id="method" class="method"><h2>How it's tested</h2>
<ol class="steps">
  <li><b>A baseline.</b> The prompt exactly as a user would type it, once per example. In the same chat, plain Claude then gets “Push it further.” (the plain push), which shows what you get by just asking for more.</li>
  <li><b>The same prompt, with the plugin.</b> <code>/be-ambitious</code> gets the same words. Every run works in a fresh throwaway macOS virtual machine with a real browser, the same model, effort and limits, so it can install tools and look at its own work the way Claude can on your machine.</li>
  <li><b>The gate.</b> Turn 1 must be sent exactly what the baseline was sent: the same system prompt, tools, parameters and message, checked from the transcripts. Then it makes a first version and stops at a checkpoint: stop here, or push on. That first version is a second plain sample, so the gap between it and the baseline shows how much plain runs vary.</li>
  <li><b>Pushing on.</b> A stand-in user (the same model, knowing only the prompt) answers the checkpoint with “Push it further.” and answers any question the way someone who typed that prompt most plausibly would. The plugin then runs its steps one at a time; each step's changes and cost are shown on the example's page.</li>
  <li><b>Our review, not an auto judge.</b> No model grades the results. The harness captures every version the same way, and we read, run and use them side by side, as described under <a href="#kinds">Kinds of example</a>, then record the verdict and why.</li>
  <li><b>Only the current plugin counts.</b> Each run records the plugin it used. Runs from an older plugin are marked outdated.</li>
</ol>
<p class="hint">Code: <a href="{repo}/tree/main/bench">bench/</a> · Raw results: <a href="{repo}/blob/main/examples/RESULTS.md">examples/RESULTS.md</a></p>
</section>
"""
    return head("claude-ambition results", "", "Results for the ambition plugin for Claude Code, against a plain-prompt baseline.").replace("{repo}", repo) + body + foot(repo)


def build(data, docs, site_url, repo):
    docs.mkdir(exist_ok=True)
    (docs / ".nojekyll").write_text("")
    (docs / "assets").mkdir(exist_ok=True)
    for name in ("style.css", "app.js"):
        shutil.copy2(HERE / "site" / name, docs / "assets" / name)
    for old in docs.iterdir():  # results only ever show what's in examples/ now
        if old.is_dir() and old.name != "assets":
            shutil.rmtree(old)
    for ex in data:
        dest = docs / ex["model"] / ex["category"] / ex["name"]
        copy_example(ex, dest)
        (dest / "index.html").write_text(example_page(ex, "../../../", repo), encoding="utf-8")
    (docs / "index.html").write_text(index_page(data, repo), encoding="utf-8")
