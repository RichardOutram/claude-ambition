"""Builds the GitHub Pages site (docs/) from examples/. Called by `python3 bench/ab.py report`.

Static HTML, generated in full on every build. Markdown is rendered in the browser (marked + DOMPurify),
and produced web pages are previewed in sandboxed iframes. Never hand-edit docs/: re-run the report.
"""
import html
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARMS = ("not-ambitious", "briefed", "ambitious")
ARM_NAME = {"not-ambitious": "Plain prompt", "briefed": "Briefed prompt", "ambitious": "/be-ambitious"}
ARM_NOTE = {"not-ambitious": "The prompt exactly as a user would type it.",
            "briefed": "The prompt plus the context the user had in their head.",
            "ambitious": "/be-ambitious with the prompt, with the plugin loaded."}
PAIR_NAME = {"ambitious-vs-not-ambitious": "vs the plain prompt", "ambitious-vs-briefed": "vs the briefed prompt"}
SKIP = {".git", "node_modules", ".venv", "__pycache__", ".claude", ".cache"}
KEEP = ("result.md", "prompt.md", "metrics.json", "metrics.txt")
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


def outcome_badge(verdicts, arm="ambitious"):
    if not verdicts:
        return badge("not judged", "muted")
    n = len(verdicts)
    won = sum(v["winner"] == arm for v in verdicts)
    tied = sum(v["winner"] == "tie" for v in verdicts)
    lost = n - won - tied
    if n == 1:
        conf = "/".join(str(o.get("confidence") or "?") for o in verdicts[0]["orders"])
        word = {arm: "Won", "tie": "Tie"}.get(verdicts[0]["winner"], "Lost")
        return badge(word, {"Won": "good", "Tie": "muted"}.get(word, "bad")) + f'<span class="sub">{e(conf)} confidence</span>'
    tone = "good" if won > lost + tied else "bad" if lost > won else "muted"
    return badge(f"{won}–{lost}–{tied}", tone) + '<span class="sub">won–lost–tied</span>'


def worth_badge(verdicts):
    ws = [v["worth"] for v in verdicts if (v.get("worth") or {}).get("worth_it")]
    if not ws:
        return badge("not assessed", "muted")
    tone = {"yes": "good", "marginal": "warn", "no": "bad"}
    if len(ws) == 1:
        w = ws[0]
        return badge(w["worth_it"].capitalize(), tone.get(w["worth_it"], "muted")) + \
            f'<span class="sub">{e(str(w.get("uplift")))} uplift · {w["cost_multiple"]:g}× cost</span>'
    counts = {}
    for w in ws:
        counts[w["worth_it"]] = counts.get(w["worth_it"], 0) + 1
    top = max(counts, key=counts.get)
    return badge(f"{top.capitalize()} {counts[top]}/{len(ws)}", tone.get(top, "muted"))


def money(x):
    return f"${x:.2f}" if x >= 0.995 or x == 0 else f"${x:.3f}".rstrip("0")


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
    for arm, runs in ex["runs"].items():
        for r in runs:
            target = dest / arm / f"run-{r['n']}"
            target.mkdir(parents=True)
            for name in KEEP:
                if (r["dir"] / name).exists():
                    shutil.copy2(r["dir"] / name, target / name)
            for sub in ("output", "checks"):
                if (r["dir"] / sub).exists():
                    shutil.copytree(r["dir"] / sub, target / sub, ignore=ignore)
    for pair, verdicts in ex["pairs"].items():
        for v in verdicts:
            shutil.copytree(v["dir"], dest / "judge" / pair / v["dir"].name)


def files_of(output):
    if not output.exists():
        return []
    found = []
    for p in sorted(output.rglob("*")):
        rel = p.relative_to(output)
        if p.is_file() and not SKIP & set(rel.parts):
            found.append((rel.as_posix(), p.stat().st_size, kind(p, p.stat().st_size)))
    return found


# ---------- example page ----------

def pips(score, arm):
    dots = "".join('<i class="on {}"></i>'.format(arm) if k < round(score) else "<i></i>" for k in range(5))
    return f'<span class="pip-row" aria-hidden="true">{dots}</span>'


def score_table(v):
    """Average each criterion over both orders, mapped from A/B back to arm names."""
    x, y = v["pair"]
    acc = {}
    for o in v["orders"]:
        label = {"A": o["A"], "B": o["B"]}
        for side, crit in (o.get("scores") or {}).items():
            for c, s in (crit or {}).items():
                if isinstance(s, (int, float)) and side in label:
                    acc.setdefault(c.strip().lower().replace(' ', '_'), {}).setdefault(label[side], []).append(s)
    if not acc:
        return ""
    rows = [f'<table class="scores"><thead><tr><th>Criterion (1–5)</th><th>{e(ARM_NAME[x])}</th><th>{e(ARM_NAME[y])}</th></tr></thead><tbody>']
    for c, by in acc.items():  # the two orders name criteria independently, so some rows come from one order
        cells = []
        for arm in (x, y):
            s = mean(by.get(arm, []))
            cells.append(f'<td>{pips(s, arm)} {s:g}</td>')
        note = "" if all(len(by.get(arm, [])) > 1 for arm in (x, y)) else ' <span class="sub">one order only</span>'
        rows.append(f"<tr><th>{e(c.replace('_', ' '))}{note}</th>{''.join(cells)}</tr>")
    rows.append("</tbody></table>")
    return "".join(rows)


def checks_table(v):
    rows = []
    for o in v["orders"]:
        label = {"A": o["A"], "B": o["B"]}
        for c in o.get("checks") or []:
            if isinstance(c, dict):
                rows.append((o["order"], c.get("check", ""), {label["A"]: c.get("A", ""), label["B"]: c.get("B", "")}))
    if not rows:
        return ""
    x, y = v["pair"]
    out = [f'<details class="checks"><summary>Objective checks the judge ran ({len(rows)})</summary><table><thead><tr>'
           f'<th>Order</th><th>Check</th><th>{e(ARM_NAME[x])}</th><th>{e(ARM_NAME[y])}</th></tr></thead><tbody>']
    for order, check, by in rows:
        out.append(f"<tr><td>{order}</td><td>{e(str(check))}</td><td>{e(str(by.get(x, '')))}</td><td>{e(str(by.get(y, '')))}</td></tr>")
    out.append("</tbody></table></details>")
    return "".join(out)


def verdict_card(pair, v):
    w = v.get("worth") or {}
    order_lines = "".join(
        f'<li><b>Order {o["order"]}</b> ({e(ARM_NAME[o["A"]])} shown as A): '
        f'{e(ARM_NAME.get(o["winner"], "Tie"))} · {e(str(o.get("confidence")))} — {e(o.get("summary") or "")}</li>'
        for o in v["orders"])
    worth = ""
    if w.get("worth_it"):
        tone = {"yes": "good", "marginal": "warn", "no": "bad"}.get(w["worth_it"], "muted")
        worth = f"""<div class="worth {tone}">
  <div class="worth-head">{badge("Worth it: " + w["worth_it"], tone)}<span>{e(str(w.get("uplift")))} uplift for
  <b>{w["cost_multiple"]:g}×</b> the cost and <b>{w["time_multiple"]:g}×</b> the time</span></div>
  <p>{e(w.get("reason") or "")}</p>
  <dl><dt>Use it when</dt><dd>{e(w.get("use_when") or "–")}</dd><dt>Skip it when</dt><dd>{e(w.get("skip_when") or "–")}</dd></dl>
  <details data-md-on-open><summary>Full cost-worth reasoning</summary><div class="md" data-md="judge/{pair}/run-{v["run"]}/worth.md"></div></details>
</div>"""
    reports = "".join(
        f'<details data-md-on-open><summary>Judge report, order {o["order"]}</summary>'
        f'<div class="md" data-md="judge/{pair}/run-{v["run"]}/order-{o["order"]}-judge.md"></div></details>'
        for o in v["orders"])
    return f"""<article class="card verdict">
  <header><h3>/be-ambitious {e(PAIR_NAME.get(pair, pair))}</h3><span class="runtag">run {v["run"]}</span>{outcome_badge([v])}</header>
  <ul class="orders">{order_lines}</ul>
  {score_table(v)}
  {checks_table(v)}
  {worth}
  <div class="reports">{reports}</div>
</article>"""


def pages_block(run_rel, checks_dir):
    cj = checks_dir / "checks.json"
    if not cj.exists():
        return ""
    out = ['<section class="pages"><h3 class="label">Pages it produced</h3><p class="hint">Screenshots and mobile Lighthouse scores were taken by the test harness after the run, the same way for every arm.</p>']
    for p in json.loads(cj.read_text()):
        shots = p.get("screenshots", {})
        scores = (p.get("lighthouse") or {}).get("scores") or {}
        chips = "".join(f'<span class="score {"good" if (s or 0) >= 90 else "warn" if (s or 0) >= 50 else "bad"}"><b>{s if s is not None else "–"}</b>{e(k.replace("-", " "))}</span>'
                        for k, s in scores.items())
        fails = (p.get("lighthouse") or {}).get("failed_accessibility_audits") or []
        fail = f'<p class="hint">Failed accessibility audits: {e(", ".join(fails))}</p>' if fails else ""
        imgs = "".join(f'<figure class="shot {name}"><a href="{run_rel}/checks/{e(f)}"><img loading="lazy" src="{run_rel}/checks/{e(f)}" alt="{e(name)} screenshot of {e(p["page"])}"></a><figcaption>{e(name)}</figcaption></figure>'
                       for name, f in sorted(shots.items(), key=lambda kv: kv[0] != "mobile"))
        full = ""
        live = f"{run_rel}/output/{e(p['page'])}"
        out.append(f"""<div class="page-card"><div class="page-head"><code>{e(p["page"])}</code><span>{full}<a href="{live}" target="_blank" rel="noopener">open live ↗</a></span></div>
  <div class="scores-row">{chips}</div>{fail}
  <div class="shots">{imgs}</div>
  <details class="live"><summary>Try it here (phone width)</summary><div class="phone"><iframe loading="lazy" sandbox="allow-scripts allow-forms" src="{live}" title="{e(p["page"])}"></iframe></div></details>
</div>""")
    out.append("</section>")
    return "".join(out)


def run_panel(arm, r, ex, repo):
    run_rel = f"{arm}/run-{r['n']}"
    m = r["metrics"]
    files = files_of(r["dir"] / "output")
    file_list = "".join(
        f'<li><a href="{run_rel}/output/{e(rel)}" data-file="{run_rel}/output/{e(rel)}" data-kind="{k}">{e(rel)}</a><span>{human(size)}</span></li>'
        for rel, size, k in files) or '<li class="hint">No files. The whole answer is the reply above.</li>'
    denials = len(m.get("permission_denials") or [])
    src = f"{repo}/tree/main/examples/{ex['dir'].relative_to(ex['dir'].parents[2]).as_posix()}/{run_rel}"
    return f"""<div class="stats">
  <div><b>{money(r["cost_usd"])}</b><span>cost</span></div>
  <div><b>{r["minutes"]:.1f}</b><span>minutes</span></div>
  <div><b>{r["output_tokens"]:,}</b><span>output tokens</span></div>
  <div><b>{r["turns"]}</b><span>turns</span></div>
  <div><b>{r["exchanges"]}</b><span>user messages</span></div>
  {f'<div><b>{denials}</b><span>tool denials</span></div>' if denials else ''}
</div>
<details data-md-on-open><summary>What the user side sent ({r["exchanges"]} message{"s" if r["exchanges"] != 1 else ""})</summary><div class="md" data-md="{run_rel}/prompt.md"></div></details>
<h3 class="label">Final reply</h3>
<div class="md reply" data-md="{run_rel}/result.md"></div>
{pages_block(run_rel, r["dir"] / "checks")}
<h3 class="label">Files ({len(files)})</h3>
<div class="files"><ul>{file_list}</ul><div class="viewer" hidden><div class="viewer-head"><code></code><a target="_blank" rel="noopener">raw ↗</a></div><div class="viewer-body"></div></div></div>
<p class="hint">Full transcript, including every tool call: <a href="{src}">on GitHub</a>.</p>"""


def demos(ex):
    """The pages each run produced, up front: a screenshot that opens the live page, grouped by arm."""
    groups = []
    for arm in ARMS:
        cards = []
        for r in ex["runs"].get(arm, []):
            cj = r["dir"] / "checks" / "checks.json"
            pages = json.loads(cj.read_text()) if cj.exists() else []
            if not pages:
                continue
            p = pages[0]
            live = f"{arm}/run-{r['n']}/output/{p['page']}"
            shot = p.get("screenshots", {}).get("mobile") or p.get("screenshots", {}).get("desktop")
            img = f'<img loading="lazy" src="{arm}/run-{r["n"]}/checks/{e(shot)}" alt="Screenshot of the page from {e(ARM_NAME[arm])}, run {r["n"]}">' if shot else ""
            sc = (p.get("lighthouse") or {}).get("scores") or {}
            chips = " · ".join(f"{k.replace('-', ' ')} {sc[k]}" for k in ("performance", "accessibility") if sc.get(k) is not None)
            more = f" (+{len(pages) - 1} more)" if len(pages) > 1 else ""
            cards.append(f"""<a class="demo" href="{e(live)}" target="_blank" rel="noopener">
  <span class="demo-shot">{img}</span>
  <span class="demo-cap"><b>{"Run " + str(r["n"]) if len(ex["runs"][arm]) > 1 else "Open the page"} ↗</b><span>{e(p["page"])}{more}</span><span>{e(chips)}</span></span>
</a>""")
        if cards:
            groups.append(f'<div class="demo-group"><h2 class="label"><span class="dot {arm}"></span>{e(ARM_NAME[arm])}</h2><div class="demo-row">{"".join(cards)}</div></div>')
    if not groups:
        return ""
    return f"""<div class="demos"><p class="hint">Each version built a page. Tap a screenshot to open it live, exactly as produced, and try it like a customer would.</p>{"".join(groups)}</div>"""


def example_page(ex, root, repo):
    spec = ex["spec"]
    r = ex["runs"]
    cost_rows = [(ARM_NAME[a], mean(x["cost_usd"] for x in r[a]), a) for a in ARMS if a in r]
    time_rows = [(ARM_NAME[a], mean(x["minutes"] for x in r[a]), a) for a in ARMS if a in r]
    tok_rows = [(ARM_NAME[a], mean(x["output_tokens"] for x in r[a]), a) for a in ARMS if a in r]
    verdicts = "".join(verdict_card(p, v) for p in ("ambitious-vs-not-ambitious", "ambitious-vs-briefed")
                       for v in ex["pairs"].get(p, []))
    tabs, panels = [], []
    for i, arm in enumerate(a for a in ARMS if a in r):
        for j, run in enumerate(r[arm]):
            key = f"{arm}-{run['n']}"
            label = ARM_NAME[arm] + (f" · run {run['n']}" if len(r[arm]) > 1 else "")
            sel = "true" if (i, j) == (0, 0) else "false"
            tabs.append(f'<button role="tab" aria-selected="{sel}" data-tab="{key}" class="{arm}">{e(label)}</button>')
            panels.append(f'<div role="tabpanel" data-panel="{key}"{"" if sel == "true" else " hidden"}><p class="hint">{e(ARM_NOTE[arm])}</p>{run_panel(arm, run, ex, repo)}</div>')
    body = f"""<nav class="crumbs"><a href="{root}index.html">Results</a> / {e(ex["model"])} / {e(ex["category"])}</nav>
<section class="hero ex">
  <p class="eyebrow">{e(ex["slug"])}</p>
  <h1>“{e(spec.get("prompt", ""))}”</h1>
  {demos(ex)}
  <div class="context">
    <div><h2 class="label">What the user knew but didn't type</h2><p>{e(spec.get("brief", ""))}</p></div>
    <div><h2 class="label">How it was judged</h2><p>{e(spec.get("check", ""))}</p></div>
  </div>
</section>
<section class="grid2">
  <div class="card"><h3>Cost per run</h3>{bars(cost_rows, money)}</div>
  <div class="card"><h3>Model time per run</h3>{bars(time_rows, lambda v: f"{v:.1f} min")}<h3 class="mt">Output tokens</h3>{bars(tok_rows, lambda v: f"{v:,.0f}")}</div>
</section>
<section><h2>Verdicts</h2><p class="hint">Quality is judged blind, twice with the labels swapped; a disagreement is a tie. Only then does a separate step see the costs and decide whether the difference was worth paying for.</p>{verdicts or '<p class="hint">Not judged yet.</p>'}</section>
<section><h2>The outputs</h2><div class="tabs" role="tablist">{"".join(tabs)}</div>{"".join(panels)}</section>
"""
    return head(f"{ex['slug']} · claude-ambition", root, spec.get("prompt", "")).replace("{repo}", repo) + body + foot(repo)


# ---------- index ----------

def thumb(ex, root_rel):
    for arm in ("ambitious", "briefed", "not-ambitious"):
        for r in ex["runs"].get(arm, []):
            cj = r["dir"] / "checks" / "checks.json"
            if cj.exists():
                for p in json.loads(cj.read_text()):
                    if "mobile" in p.get("screenshots", {}):
                        return f'<img loading="lazy" src="{root_rel}/{arm}/run-{r["n"]}/checks/{e(p["screenshots"]["mobile"])}" alt="">'
    return ""


def index_page(data, repo):
    rows, cards = [], []
    for ex in data:
        rel = f"{ex['model']}/{ex['category']}/{ex['name']}"
        r = ex["runs"]
        plain = ex["pairs"].get("ambitious-vs-not-ambitious", [])
        briefed = ex["pairs"].get("ambitious-vs-briefed", [])
        costs = " · ".join(money(mean(x["cost_usd"] for x in r[a])) if a in r else "–" for a in ARMS)
        mins = " · ".join(f"{mean(x['minutes'] for x in r[a]):.1f}" if a in r else "–" for a in ("not-ambitious", "ambitious"))
        n = max(len(x) for x in r.values())
        rows.append(f"""<tr><td><a href="{rel}/index.html">{e(ex["slug"])}</a><span class="sub">{e(ex["model"])}</span></td><td>{n}</td>
<td>{outcome_badge(plain)}</td><td>{outcome_badge(briefed)}</td><td class="num">{costs}</td><td class="num">{mins}</td>
<td>{worth_badge(plain)}</td><td>{worth_badge(briefed)}</td></tr>""")
        w = next((v["worth"] for v in plain if (v.get("worth") or {}).get("use_when")), {})
        pic = thumb(ex, rel)
        cards.append(f"""<a class="ex-card" href="{rel}/index.html">
  <div class="ex-visual">{pic or f'<blockquote>“{e(ex["spec"].get("prompt", ""))}”</blockquote>'}</div>
  <div class="ex-body"><p class="eyebrow">{e(ex["category"])}</p><h3>{e(ex["spec"].get("prompt", ex["slug"]))}</h3>
  <p>{e(w.get("use_when", ""))}</p><div class="badges">{outcome_badge(plain)}{worth_badge(plain)}</div></div>
</a>""")
    body = f"""<section class="hero">
  <p class="eyebrow">An open A/B test of the <a href="{repo}">ambition plugin</a> for Claude Code</p>
  <h1>Does asking for more get you more, and is it worth paying for?</h1>
  <p class="lede">Each example is one ordinary request, run three ways on the same model under identical conditions. A blind judge picks the better work. Only then does a separate step look at the bill and decide whether the difference was worth it.</p>
</section>
<section id="results"><h2>Results</h2>
<div class="table-wrap"><table class="results"><thead><tr><th>Example</th><th>Runs</th><th>vs plain prompt</th><th>vs briefed prompt</th><th>Cost per run<span class="sub">plain · briefed · ambitious</span></th><th>Minutes<span class="sub">plain · ambitious</span></th><th>Worth the extra cost?<span class="sub">vs plain</span></th><th>Worth it?<span class="sub">vs briefed</span></th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
<p class="hint">One run can be luck. Examples with a single run are illustrations, not measurements.</p>
</section>
<section><h2>Examples</h2><div class="ex-grid">{"".join(cards)}</div></section>
<section id="method" class="method"><h2>How it's tested</h2>
<ol class="steps">
  <li><b>Three arms.</b> The <span class="dot not-ambitious"></span>plain prompt as typed; a <span class="dot briefed"></span>briefed prompt that adds what the user knew but didn't say; and <span class="dot ambitious"></span><code>/be-ambitious</code>. The briefed arm is the control: it shows whether the method adds anything beyond extracting more context.</li>
  <li><b>Identical conditions.</b> Same model, settings, tools, sandbox and turn limit. Each run starts in an empty folder outside the repo. If any arm asks a question, the same stand-in user answers it from the brief.</li>
  <li><b>A blind judge.</b> A fresh session sees only the request, the context, the check and two outputs labelled A and B. It runs objective checks, then scores a rubric. Each pair is judged twice with the labels swapped, and a disagreement is a tie.</li>
  <li><b>Then the bill.</b> A separate session reads the blind reports plus the cost and time of each output, and decides whether the improvement was worth it for this user: yes, marginal or no, with when to use it and when to skip it.</li>
</ol>
<p class="hint">Code: <a href="{repo}/tree/main/bench">bench/</a> · Raw results: <a href="{repo}/blob/main/examples/RESULTS.md">examples/RESULTS.md</a></p>
</section>
"""
    return head("claude-ambition results", "", "Blind A/B results for the ambition plugin for Claude Code.").replace("{repo}", repo) + body + foot(repo)


def build(data, docs, site_url, repo):
    docs.mkdir(exist_ok=True)
    (docs / ".nojekyll").write_text("")
    (docs / "assets").mkdir(exist_ok=True)
    for name in ("style.css", "app.js"):
        shutil.copy2(HERE / "site" / name, docs / "assets" / name)
    for model in {ex["model"] for ex in data}:
        if (docs / model).exists():
            shutil.rmtree(docs / model)
    for ex in data:
        dest = docs / ex["model"] / ex["category"] / ex["name"]
        copy_example(ex, dest)
        (dest / "index.html").write_text(example_page(ex, "../../../", repo), encoding="utf-8")
    (docs / "index.html").write_text(index_page(data, repo), encoding="utf-8")
