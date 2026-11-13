"""Outside check for url-shortener-architecture.md (no model involved).
usage: python3 -I check_architecture.py url-shortener-architecture.md [--run] [--links] [--baseline=<older.md>]
  default  structure, cross-references, tables, promises, no-process-story, decisions have owner+date
  --run    re-run every embedded script and compare with its printed output (A4 and A6 need the two
           input files named in the appendix, placed under .ambition/data/pv and .ambition/data/api)
  --links  fetch every cited URL"""
import os, re, subprocess, sys, tempfile

doc, flags = sys.argv[1], set(sys.argv[2:])
T = open(doc, encoding="utf-8").read()
L = T.split("\n")
fails, passes = [], []
def ok(name, cond, detail=""):
    (passes if cond else fails).append(f"{name}{(' - ' + detail) if detail and not cond else ''}")

# ---------- structure ----------
ok("code fences balanced", T.count("```") % 2 == 0)
heads = [l for l in L if re.match(r"#{1,4} ", l)]
ok("no duplicate headings", len(heads) == len(set(heads)), str([h for h in heads if heads.count(h) > 1]))
secs = set(re.findall(r"^## (\d+)\.", T, re.M))
bad = [s for s in re.findall(r"Section (\d+)", T) if s not in secs]
ok("every 'Section N' reference exists", not bad, str(set(bad)))
apps = set(re.findall(r"^### (A\d)\.", T, re.M))
bad = [a for a in set(re.findall(r"\bA(\d)\b", T)) if "A" + a not in apps and "A" + a not in ("A1",)]
ok("every 'A<n>' reference has an appendix entry", not bad, str(bad))
decs = set(re.findall(r"^### (D\d)\.", T, re.M))
bad = [d for d in set(re.findall(r"\b(D\d)\b", T)) if d not in decs]
ok("every 'D<n>' reference has a decision record", not bad, str(bad))

# table shape: all rows in a table have the same number of cells (ignoring cells inside code spans)
def cells(row):
    row = re.sub(r"`[^`]*`", "X", row)
    return len(row.strip().strip("|").split("|"))
in_fence = False; tbl = []; bad_t = []
for i, l in enumerate(L, 1):
    if l.startswith("```"): in_fence = not in_fence
    if in_fence: continue
    if l.startswith("|"): tbl.append((i, cells(l)))
    else:
        if tbl and len({c for _, c in tbl}) > 1: bad_t.append(tbl[0][0])
        tbl = []
ok("markdown tables have consistent columns", not bad_t, f"tables starting at lines {bad_t}")

# ---------- stale-claim scan ----------
BODY = T.split("## 8. Stretch")[0]
for phrase in ("8 redirect instances", "3 shards", "3 primaries"):
    n = BODY.count(phrase)
    ok(f"no stale/meta phrase '{phrase}'", n == 0, f"{n} occurrence(s)")
ok("no 'I ' voice in the opening paragraph", not re.search(r"\bI\b|\bmy\b", "\n".join(L[:4])))

for phrase in ("first draft", "First draft", "Revision notes", "earlier assumption", "found while", "I attacked", "This section asks"):
    ok(f"no process story: '{phrase}'", phrase not in T, f"{T.count(phrase)} occurrence(s)")
ok("opens without first person", not re.search(r"\bI\b|\bmy\b", "\n".join(L[:4])))
ok("ends with open decisions", T.index("## 9. Open decisions") > T.index("## 8. Stretch") and T.index("## 9. Open decisions") < T.index("## Appendix A"))
rows = [r for r in T.split("### Decisions")[1].split("### Next checks")[0].split("\n") if re.match(r"\| \d", r)]
ok("every decision has an owner, a date and a pick", len(rows) >= 5 and all(re.search(r"20\d\d-\d\d-\d\d", r) for r in rows), f"{len(rows)} rows")
rows = [r for r in T.split("### Next checks")[1].split("\n") if r.startswith("|") and "---" not in r][1:]
ok("every next check has an owner and a date", len(rows) >= 4 and all(re.search(r"20\d\d-\d\d-\d\d|launch \+", r) for r in rows), f"{len(rows)} rows")

# ---------- original ask, intact ----------
ask = {
    "is a Markdown file": doc.endswith(".md"),
    "names 10k req/s": "10k" in T,
    "architecture diagram": "┌" in T,
    "load balancer": "load bal" in T.lower() or "L7 LB" in T,
    "cache layer": "Redis" in T,
    "datastore": "KV store" in T or "datastore" in T,
    "short-code generation": "short code" in T.lower() or "Short code" in T,
    "API": "POST /api/v1/links" in T and "GET /{code}" in T,
    "analytics": "ClickHouse" in T,
    "failure handling": "Failure" in T,
    "capacity numbers": "Storage" in T and "req/s" in T,
}
for k, v in ask.items(): ok(f"original ask: {k}", v)

# ---------- promises in the restatement ----------
promise = {
    "summary + one diagram up front": T.find("## 1. Summary") < T.find("```") < T.find("## 2."),
    "decision records for key generation, SQL vs NoSQL, cache strategy, 301/302":
        all(re.search(p, T) for p in (r"### D1\. Redirect status", r"### D2\. Short code", r"### D3\. Datastore", r"### D4\. Cache")),
    "every decision names what flips it": all(("Flips to" in sec) for sec in re.split(r"(?=^### D\d\.)", T, flags=re.M)[1:5]),
    "every decision lists rejected alternatives": all(("Rejected" in sec or "Against" in sec) for sec in re.split(r"(?=^### D\d\.)", T, flags=re.M)[1:5]),
    "numbers show derivation (table with Derivation column)": "| Derivation |" in T,
    "assumptions are marked [A]": T.count("**[A]**") >= 5,
    "cache-down and database-down covered": "| Redis down |" in T and "| DB fully unavailable |" in T,
    "scripts embedded (capacity, cache, ids)": all(f"### A{n}." in T for n in (1, 2, 3)),
    "short sources list": "## Appendix B" in T,
    "red-team / abuse analysis": "## 6. Abuse" in T,
    "hit rate no longer claimed as 95%": not re.search(r"hit rate (of )?>?9[5-9]%", T.split("## Revision notes")[0].replace("95% hit rate needs", "").replace("sizing Redis for a 95% hit rate", "")),
}
for k, v in promise.items(): ok(f"promise: {k}", bool(v))

# ---------- prose numbers vs script output ----------
def run(code, args=()):
    d = tempfile.mkdtemp(); p = os.path.join(d, "s.py"); open(p, "w").write(code)
    r = subprocess.run(["python3", "-I", p, *args], capture_output=True, text=True, timeout=300)
    return r.stdout, r.returncode, r.stderr
blocks = re.findall(r"```python\n(.*?)```\n(?:Output[^\n]*\n)?```\n(.*?)```", T, re.S)
if "--run" in flags:
    W = os.path.dirname(os.path.abspath(doc)) + "/.ambition/data/"
    argsets = {1: (), 2: (), 3: (), 4: (W + "pv/pageviews-20261001-120000.gz", W + "pv/pageviews-20261001-130000.gz"),
               5: (W + "api/hourly.json", W + "pv/pageviews-20261001-120000.gz"), 6: (), 7: ()}
    allout = ""
    for n, (code, shown) in enumerate(blocks, 1):
        out, rc, err = run(code, argsets.get(n, ()))
        ok(f"script #{n} runs (exit 0)", rc == 0, err[-200:])
        allout += out
        lines = [x.rstrip() for x in shown.strip("\n").split("\n") if x.strip() and not x.startswith("R4")]
        got = {x.rstrip() for x in out.split("\n")}
        missing = [x for x in lines if x not in got]
        ok(f"script #{n} printed output matches the document", not missing, f"{len(missing)} line(s) differ, first: {missing[:1]}")
    # prose figures that must appear in real script output
    pairs = [("9,901", "peak reads/s=9,901"), ("5.2B", "5.20B"), ("2.6 TB", "5y=2.60 TB"), ("0.15%", "0.148%"),
             ("4,950", None), ("736,000", "736,026"), ("12,000", "11,871"), ("0.085%", "P(collision)=0.085%"),
             ("34.3%", "34.3%"), ("23.5%", "23.5%"), ("1.33", "1.33"), ("3.7%", "3.74%"), ("297", "297 concurrent"),
             ("124%", "124%"), ("49,505", "49,505"), ("2,970", "2,970"), ("62%", "62%"), ("21.6", "21.6 min"), ("259", "259 min"), ("17.5 TB", "17.5 TB"), ("2.2%", "2.19%"), ("51%", "51.0%")]
    for doc_s, out_s in pairs:
        ok(f"prose figure {doc_s!r} present", doc_s in T)
        if out_s: ok(f"prose figure {doc_s!r} backed by script output", out_s in allout)
    ok("4,950 = 9,901 x 0.5", abs(9901 * 0.5 - 4950.5) < 1)

# ---------- nothing lost versus a baseline ----------
for a in sys.argv[2:]:
    if a.startswith("--baseline="):
        B = open(a.split("=", 1)[1], encoding="utf-8").read()
        caps = ["CDN", "rate limit", "Idempotency", "expires_at", "Kafka", "ClickHouse", "DELETE /api/v1/links", "/stats", "HSTS",
                "Safe Browsing", "single-flight", "p99", "owner_id", "status", "Multi-AZ", "negative", "Synthetic probes",
                "409", "422", "429", "410", "TTL", "jitter", "WAF", "alias", "SSRF", "circuit breaker", "burn"]
        lost = [c for c in caps if c.lower() in B.lower() and c.lower() not in T.lower()]
        ok("nothing from the baseline is lost (capability terms)", not lost, str(lost))
        gained = [c for c in ("Flips to", "Rejected", "[A]", "Appendix", "red team", "SLO") if c.lower() in T.lower() and c.lower() not in B.lower()]
        print("terms present now but absent in baseline:", gained)

# ---------- links ----------
if "--links" in flags:
    urls = sorted(set(re.findall(r"\]\((https?://[^)\s]+)\)", T)))
    for u in urls:
        r = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-L", "-m", "20", "-w", "%{http_code}", u], capture_output=True, text=True)
        ok(f"link {u[:70]}", r.stdout.strip().startswith(("2", "3")), f"HTTP {r.stdout.strip() or r.stderr.strip()[:60]}")

print(f"PASS {len(passes)}  FAIL {len(fails)}")
for f in fails: print("  FAIL:", f)
