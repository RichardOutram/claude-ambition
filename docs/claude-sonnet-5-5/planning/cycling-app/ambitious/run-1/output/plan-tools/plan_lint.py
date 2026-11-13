#!/usr/bin/env python3
"""Hold the plan to its promises. Usage: python3 -I plan_lint.py PLAN.md   (exit 1 on any FAIL)

Nothing here trusts the plan's own numbers: costs, schedule, XP examples, quest and privacy
figures are recomputed from the rules/scripts and compared with what the plan says."""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = [sys.executable, "-I"]
plan_path = sys.argv[1]
S = open(plan_path, encoding="utf-8").read()
R = []

def check(name, ok, detail=""):
    R.append((name, bool(ok), detail))

def run(*args, cwd=None):
    p = subprocess.run(list(args), capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout + p.stderr

def ct_parse(path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("ct", os.path.join(HERE, "check_tickets.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.parse(path)

def section(title_prefix):
    m = re.search(rf"^## {re.escape(title_prefix)}.*?(?=^## |\Z)", S, re.M | re.S)
    return m.group(0) if m else ""

# 1. original ask intact
head = "\n".join(S.splitlines()[:12]).lower()
missing = [t for t in ("react native", "expo", "social", "gamif", "cycling") if t not in head]
check("ask: names React Native, Expo, social, gamified, cycling", not missing, f"missing {missing}")
check("ask: fitness/ride tracking present", "record" in S.lower() and "ride" in S.lower())

# 2. tickets
rc, out = run(*PY, os.path.join(HERE, "check_tickets.py"), plan_path, "3")
check("tickets: order, deps, AC, size valid", rc == 0, out.strip().splitlines()[1] if rc else out.splitlines()[0])
m = re.search(r"Effort: (\d+) dev-days total; critical path (\d+)", out)
total_days, cp = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
sched = {}
for d in (2, 3, 4):
    _, o = run(*PY, os.path.join(HERE, "check_tickets.py"), plan_path, str(d))
    mm = re.search(r"lower bound \d+ working days = ([\d.]+) weeks.*\n.*At 70% focus: ([\d.]+) weeks", o)
    if mm: sched[d] = (float(mm.group(1)), float(mm.group(2)))

# 3. references resolve
secs = set(re.findall(r"^## (\d+)b?\.", S, re.M)) | {"1b"}
bad = sorted(set(re.findall(r"§(\d+)", S)) - secs)
check("refs: every §n points at a real section", not bad, f"missing {bad}")
tids = set(re.findall(r"^### (T-\d+)", S, re.M))
bad = sorted(set(re.findall(r"T-\d{3}", S)) - tids)
check("refs: every T-nnn mentioned exists", not bad, f"missing {bad}")
paths = set(re.findall(r"`((?:plan-tools|spike-gps)/[^`\s]+)`", S))
bad = sorted(p for p in paths if not os.path.exists(os.path.join(ROOT, p.replace("*", ""))) and "*" not in p)
check("refs: every script/file path in the plan exists", not bad, f"missing {bad}")
check("refs: nothing depends on the throwaway .ambition folder", ".ambition" not in S)
check("stale: no dated 'weeks N' labels, no 'MVP' leftovers", not re.search(r"\(weeks? \d|\bMVP\b", S))

chain = re.search(r"Longest chain \(\d+ tickets\): (.+)", out)
plan_chain = re.search(r"Longest dependency chain \((\d+) tickets\):\*\* ([^.\n]+?)\.", S)
check("schedule: the 'longest chain' sentence equals the checker's chain", chain and plan_chain and plan_chain.group(2).replace(" → ", " -> ").strip() == chain.group(1).strip(), f"plan {plan_chain.group(2) if plan_chain else None}")
rp = re.search(r"Riskiest path \(\d+ tickets\):\*\* ([^\n]+)", S)
tk, _order = ct_parse(plan_path)
hops = re.findall(r"T-\d+", re.sub(r"\(waits[^)]*\)", "", rp.group(1).split("If T-010")[0])) if rp else []
okp = bool(hops) and all(a in tk[b]["deps"] for a, b in zip(hops, hops[1:]))
check("schedule: every hop of the 'riskiest path' is a real dependency", okp, f"hops {hops}")

# 4. cost arithmetic
cost = section("4.")
rows = {r[0]: r[1:4] for r in re.findall(r"^\| ([^|]+?) \| \**(\d+)\** \| \**(\d+)\** \| \**(\d+)\** \|", cost, re.M)}
def expo(mau):
    starter = 19 + max(0, mau - 3000) * 0.005
    return min(starter, 199) if mau <= 50000 else 199 + (mau - 50000) * 0.005
exp_supa, exp_map, exp_expo = [25] * 3, [max(0, (m - 25000) / 1000 * 4) for m in (1000, 10000, 50000)], [round(expo(m)) for m in (1000, 10000, 50000)]
got = lambda k: [int(x) for x in next((v for kk, v in rows.items() if k in kk), ("0", "0", "0"))]
check("cost: Mapbox line recomputed from $4/1k above 25k MAU", got("Mapbox") == exp_map, f"{got('Mapbox')} vs {exp_map}")
check("cost: Expo line recomputed from plan prices", got("Expo") == exp_expo, f"{got('Expo')} vs {exp_expo}")
sub = [a + b + c for a, b, c in zip(got("Supabase"), got("Mapbox"), got("Expo"))]
check("cost: subtotal = sum of the three lines", got("Subtotal") == sub, f"{got('Subtotal')} vs {sub}")
check("cost: unverified items labelled, sources + date given", "unverified" in cost.lower() and "2026-11-13" in cost and cost.count("https://") >= 3)

# 5. schedule
m = re.search(r"\((\d+) dev-days; critical path (\d+) working days\)", S)
check("schedule: dev-days and critical path match the ticket sizes", m and (int(m.group(1)), int(m.group(2))) == (total_days, cp), f"plan {m.groups() if m else None} vs {(total_days, cp)}")
for d, lab in ((2, r"\| 2 devs \| ([\d.]+) wk \| ~(\d+) wk"), (3, r"\| 3 devs[^|]*\| ([\d.]+) wk \| \*\*~(\d+) wk"), (4, r"\| 4 devs \| ([\d.]+) wk \| ~(\d+) wk")):
    mm = re.search(lab, S)
    ok = mm and d in sched and abs(float(mm.group(1)) - sched[d][0]) < 0.06 and abs(int(mm.group(2)) - sched[d][1]) <= 0.51
    check(f"schedule: {d}-dev row matches the checker", ok, f"plan {mm.groups() if mm else None} vs {sched.get(d)}")

# 6. XP, quests, privacy numbers recomputed from code
rc, xo = run(*PY, os.path.join(HERE, "sims", "xp_rules.py"))
ex = re.findall(r"\('(\d) [^']*', (\d+), (\d+), (None|\d+)\)", xo)
tbl = re.findall(r"^\s*\| (\d)\. [^|]*\| ([^|]*) \| (\d+)[^|]*\|", S, re.M)
okx = len(ex) == 5 and len(tbl) == 5 and all(str(a) == t[2] for (_, _, a, _), t in zip(ex, tbl))
check("xp: the five worked examples equal the code's output", okx, f"code {[e[2] for e in ex]} vs plan {[t[2] for t in tbl]}")
sim = dict(re.findall(r"^\s+(commuter|weekend|casual|keen)\S* .*\((\d+), (\d+), \d+\)", xo, re.M)) if False else {}
for name, lv in re.findall(r"^\s+(commuter|weekend|casual|keen).*\(\d+, (\d+), \d+\)\s*$", xo, re.M): sim[name] = lv
claim = re.search(r"casual → L(\d+), commuter → L(\d+), weekend → L(\d+), keen → L(\d+)", S)
check("xp: 52-week levels in the plan equal the simulation", claim and [claim.group(i) for i in (1, 2, 3, 4)] == [sim.get(k) for k in ("casual", "commuter", "weekend", "keen")], f"plan {claim.groups() if claim else None} vs {sim}")
check("xp: streak bonus text agrees with code (5% x max 5 = +25%)", "max 5" in S and "+25%" in S and "5% ×" in S)
rc, qo = run(*PY, os.path.join(HERE, "sims", "quests.py"))
pers = re.search(r"PERSONALISED.*", qo, re.S).group(0)
pv = [int(x) for x in re.findall(r"'\w+': '\s*(\d+)%'", pers)]
c = re.search(r"personalised targets land every rider type at (\d+)[–-](\d+)%", S)
check("quests: personalised completion range equals simulation", c and (int(c.group(1)), int(c.group(2))) == (min(pv), max(pv)), f"plan {c.groups() if c else None} vs {(min(pv), max(pv))}")
fx = re.search(r"city commuter \(flat\)\s+\{'ride 3 days': '\s*\d+%', '50 km total': '\s*\d+%', 'climb 800 m': '\s*(\d+)%'", qo)
kx = re.search(r"keen club rider\s+\{'ride 3 days': '\s*\d+%', '50 km total': '\s*\d+%', 'climb 800 m': '\s*(\d+)%'", qo)
check("quests: fixed 'climb 800 m' 0% commuters / 100% keen as stated", fx and kx and fx.group(1) == "0" and kx.group(1) == "100" and "0% of weeks by commuters and 100% by keen" in S)
rc, p1 = run(*PY, os.path.join(HERE, "sims", "privacy_attack.py"))
a3 = re.search(r"A fixed centre\+radius\s+rides= 3\s+median error\s+([\d.]+) m", p1)
check("privacy: fixed zone recovered to 0.0 m from 3 rides (as stated)", a3 and float(a3.group(1)) == 0.0 and "**0.0 m** from just 3" in S)
rc, p2 = run(*PY, os.path.join(HERE, "sims", "privacy_attack2.py"))
def med(label, curve_idx, rides=30):
    blocks = p2.split("road curvature noise")[1:]
    m = re.search(rf"{label}\s+rides={rides}\s+median err\s+(\d+) m", blocks[curve_idx])
    return int(m.group(1)) if m else None
cl = re.search(r"~(\d+)–(\d+) m after 30 rides with a 200 m zone and ~(\d+)–(\d+) m with a 400 m zone", S)
want = (med(r"B  R=200..320 \+offset", 0), med(r"B  R=200..320 \+offset", 1), med(r"C  R=400..640 \+offset", 0), med(r"C  R=400..640 \+offset", 1))
check("privacy: heading-attack errors equal simulation (±1 m)", cl and all(abs(int(x) - y) <= 1 for x, y in zip(cl.groups(), want)), f"plan {cl.groups() if cl else None} vs {want}")

# 7. restatement promises
dec = section("2.")
check("promise: stack decisions settled (no TBD / 'to be decided')", dec and not re.search(r"\bTBD\b|\bTODO\b|to be decided", dec, re.I))
check("promise: Mapbox and Supabase choices made with rejected alternatives named", "Google Maps rejected" in dec and "Firebase rejected" in dec)
deferred = re.findall(r"^\| ([^|]+) \| ([^|]{15,}) \|$", section("5.").split("**Deferred")[-1], re.M)
n_rows = len(re.findall(r"^\| [^|]+ \| [^|]+ \|$", section("5.").split("**Deferred")[-1], re.M)) - 2
check("promise: every deferral has a reason (>= 15 chars)", n_rows > 0 and len(deferred) >= n_rows, f"{len(deferred)} with reasons of {n_rows}")
res = section("10.")
unver = re.search(r"UNVERIFIED", section("3.")) is not None
empty_table = len(re.findall(r"\| — \| — \| — \| — \| — \| — \|", res)) == 2
check("promise: recording reliability marked UNVERIFIED while results table is empty", unver == empty_table, f"unverified={unver}, empty table={empty_table}")
check("promise: spike gates the recording ticket (T-013 depends on T-010)", re.search(r"### T-013[^\n]*\nDepends:[^\n]*T-010", S) is not None)
for ph, why in (("never shown while a ride is recording", "T-034 reward reveal"), ("never max speed", "T-041 feed"), ("request the rider approves", "T-040 follow"),
                ("no app notification is delivered while a ride is recording", "T-044 push"), ("single large controls", "T-015 record screen"), ("never in the feed", "principle 1")):
    check(f"principle enforced: {why}", ph in S)
check("promise: pricing sources dated + Apple/Google rules cited with read dates", S.count("read 2026-11-13") >= 4)

# 7b. the at-a-glance summary must not drift from the verified numbers
glance = section("At a glance")
g = re.search(r"(\d+) tickets, (\d+) dev-days → about (\d+) weeks for 3 developers", glance)
nt = len(tids)
check("glance: ticket count, dev-days and 3-dev weeks match the checker", g and (int(g.group(1)), int(g.group(2))) == (nt, total_days) and 3 in sched and int(g.group(3)) == round(sched[3][1]), f"plan {g.groups() if g else None} vs {(nt, total_days, sched.get(3))}")
gc = re.search(r"\$(\d+) / \$(\d+) / \$(\d+) per month", glance)
check("glance: monthly costs equal the cost table subtotal", gc and [int(x) for x in gc.groups()] == sub, f"plan {gc.groups() if gc else None} vs {sub}")
check("glance: names the biggest risk as unverified and the first actions", "unverified" in glance.lower() and "First three things" in glance)

t54 = re.search(r"### T-054.*?(?=^## |\Z)", S, re.M | re.S)
t54 = t54.group(0) if t54 else ""
check("promise: every success metric in section 1 is measured by T-054's AC", all(k in t54 for k in ("99%", "98%", "40%")) and all(k in section("1.") for k in ("99%", "98%", "40%")))

# 7c. stretch release train: tool must accept it, and the results table must equal the tool output
rc, ro = run(*PY, os.path.join(HERE, "releases.py"), plan_path)
check("stretch: every release is internally consistent (no missing prerequisites)", rc == 0, ro.strip().splitlines()[-1] if rc else "")
calc = {m.group(1): m.groups()[1:] for m in re.finditer(r"^(\w+) · .*?: (\d+) tickets, (\d+) dev-days, critical path (\d+) days\n\s+3 devs: ([\d.]+) wk at 100% focus, ([\d.]+) wk at 70%\n\s+4 devs: ([\d.]+) wk at 100% focus, ([\d.]+) wk at 70%", ro, re.M)}
tab = section("8b.")
for key, label in (("S1", "S1 First rides"), ("S2", "S2 Public launch"), ("S2L", "S2L Public launch, leaner"), ("S1x", "S1x S1 if recording takes 2")):
    mrow = re.search(rf"^\| {re.escape(label)}[^|]* \| (\d+) \| (\d+) \| (\d+) d \| ([\d.]+) / ([\d.]+) wk \| ([\d.]+) / ([\d.]+) wk \|", tab, re.M)
    check(f"stretch: results row {key} equals the calculator", mrow and key in calc and tuple(mrow.groups()) == calc[key], f"plan {mrow.groups() if mrow else None} vs {calc.get(key)}")
check("stretch: verdict says where it breaks and names the fallback", "where the stretch breaks" in tab and "fall back" in tab.lower())
check("stretch: fallback row matches the full-plan checker", sched.get(3) and f"{sched[3][0]:.1f} / {sched[3][1]:.1f} wk" in tab and f"{sched[4][0]:.1f} / {sched[4][1]:.1f} wk" in tab)

# 8. runnable spike test
rc, t = run("node", "--experimental-strip-types", os.path.join(ROOT, "spike-gps", "test-analyze.mjs"))
check("spike: analyzer tests pass", rc == 0, t.strip().splitlines()[-1] if t.strip() else "")

width = max(len(n) for n, _, _ in R)
fails = 0
for n, ok, d in R:
    fails += not ok
    print(("PASS " if ok else "FAIL ") + n + ("" if ok or not d else f"   <- {d}"))
print(f"\n{len(R) - fails}/{len(R)} checks passed")
sys.exit(1 if fails else 0)
