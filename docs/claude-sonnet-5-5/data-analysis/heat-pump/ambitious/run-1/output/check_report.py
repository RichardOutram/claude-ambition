#!/usr/bin/env python3
"""Outside check for heat-pump-vs-gas-boiler.md. Not part of the deliverable.
Usage: python3 -I check_report.py REPORT.md MODEL.py
Each check prints PASS/FAIL. Exit code 1 if any FAIL.
"""
import importlib.util, re, subprocess, sys, urllib.request, urllib.error

report_path, model_path = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("model", model_path)
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
md = open(report_path).read()
lines = md.splitlines()
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


# ---------- 1. Independent reimplementation of the cost model (closed-form geometric sums) ----------
def independent_adv(p, tariff):
    H = int(p["horizon"]); ry = int(p["boiler_replace_year"])
    heat = (p["gas_kwh"] - p["cooking_gas_kwh"]) * p["boiler_eff"]
    gi, ei = 1 + p["gas_inflation"], 1 + p["elec_inflation"]
    geo = lambda r, a, b: sum(r ** (t - 1) for t in range(a, b + 1)) if b >= a else 0.0   # sum of r^(t-1), t=a..b
    uc = p["elec_unit"] * (1 + p["elec_vat"])
    uh = uc * p["hp_tariff_factor"] if tariff == "hp" else uc
    # boiler path
    old_end = min(ry, H)
    gas_old = (heat / p["boiler_eff"] + p["cooking_gas_kwh"]) * p["gas_unit"] * geo(gi, 1, old_end)
    gas_new = (heat / p["new_boiler_eff"] + p["cooking_gas_kwh"]) * p["gas_unit"] * geo(gi, old_end + 1, H)
    sc_b = p["gas_sc"] * 365 * geo(gi, 1, H)
    boiler = gas_old + gas_new + sc_b + p["boiler_service"] * H
    if ry <= H:
        boiler += p["boiler_replace_cost"] - p["boiler_replace_cost"] * max(0, p["boiler_life"] - (H - ry)) / p["boiler_life"]
    # heat pump path
    hp = p["hp_net_cost"] + p["hp_service"] * H + heat / p["scop"] * uh * geo(ei, 1, H)
    if p["disconnect_gas"]:
        hp += p["cooking_elec_kwh"] * uc * geo(ei, 1, H)
    else:
        hp += p["cooking_gas_kwh"] * p["gas_unit"] * geo(gi, 1, H) + sc_b
    hp -= p["hp_net_cost"] * max(0, p["hp_life"] - H) / p["hp_life"]
    return boiler - hp


cases = [{}, {"scop": 3.8}, {"gas_kwh": 13000, "boiler_replace_year": 0}, {"disconnect_gas": 0, "elec_vat": 0.0},
         {"boiler_replace_year": 99, "gas_inflation": 0.05, "elec_inflation": 0.01}, {"horizon": 12, "hp_net_cost": 5500}]
worst = 0.0
for c in cases:
    p = {**M.defaults(), **c}
    for t in ("cap", "hp"):
        worst = max(worst, abs(independent_adv(p, t) - M.run(p, t)["adv"]))
check("Independent re-implementation agrees with the model (6 input sets x 2 tariffs)", worst < 0.01, f"worst gap £{worst:.4f}")

# ---------- 2. The file is exactly what the model generates; the pasted output is verbatim ----------
check("File matches regenerated model output", md == M.report(M.defaults()))
m = re.search(r"## Script output \(verbatim\)\n\n```\n(.*?)\n```", md, re.S)
check("Script output block present at the bottom", bool(m) and md.rstrip().endswith("```"))
check("Pasted output equals a fresh run of the script", bool(m) and m.group(1) == M.summary(M.defaults())[0])

# ---------- 3. Original ask + restatement promises ----------
first_h2 = next(i for i, l in enumerate(lines) if l.startswith("## "))
verdict_line = next(i for i, l in enumerate(lines) if "**Verdict:" in l)
check("Verdict appears before any working", verdict_line < first_h2 + 6 and lines[first_h2] == "## The answer")
check("Verdict is one of yes / no / too close", re.search(r"\*\*Verdict: (YES|NO|TOO CLOSE)", md) is not None)
check("Confidence stated", "**Confidence:" in md)
dec = md[md.index("## Decisions and next checks"):md.index("## Evidence behind the key inputs")]
check("Decisions have options, for/against, pick, owner and date", dec.count("| You") >= 3 and all(w in dec for w in ("Options", "For / against", "Pick", "Owner", "Decide by")) and re.search(r"\b20(26|27|28)\b", dec) is not None)
check("Every next check has an owner and a date", all(("You" in l and re.search(r"20\d\d|When", l)) for l in dec.splitlines() if l.startswith("| ") and not l.startswith("| #") and not l.startswith("| Next") and not l.startswith("|---") and not re.match(r"\| \d \|", l)))
check("Every file the report points to exists beside it", all(__import__("os").path.exists(__import__("os").path.join(__import__("os").path.dirname(report_path) or ".", f)) for f in ("heatpump_model.py", "check_report.py")))
check("Plain-terms gloss for SCOP and heat-pump tariff comes before the verdict", md.index("In plain terms") < md.index("**Verdict:"))
check("Grant end-date statements do not contradict each other", not ("extended to 2028" in md and "did not confirm the scheme" in md))
check("Flip facts table with thresholds", "What would flip it" in md and re.search(r"\| .*SCOP.* \| .*\d\.\d\d or more on a standard", md) is not None)
check("Long-run comparison runs 10-15 years incl. year 15", re.search(r"\| 15 \|", md) is not None and "| 10 |" in md)
check("Boiler replacement timing modelled and explained", "replacing it in year" in md and "when the boiler would need replacing" in md.lower())
check("Section order: answer, 15-year picture, robustness, assumptions, script output",
      [md.index(h) for h in ("## The answer", "## The 15-year picture", "## How well does the answer hold up?",
                              "## Using this with an installer quote", "## Decisions and next checks", "## Evidence behind the key inputs", "## Assumptions and sources", "## Script output")] == sorted(
          md.index(h) for h in ("## The answer", "## The 15-year picture", "## How well does the answer hold up?",
                                 "## Using this with an installer quote", "## Decisions and next checks", "## Evidence behind the key inputs", "## Assumptions and sources", "## Script output")))
check("Assumptions are flagged (ASSUMPTION and SOURCE tags in table)", md.count("| ASSUMPTION |") >= 10 and md.count("| SOURCE |") >= 4)
ans = md[md.index("## The answer"):md.index("## The 15-year picture")]
words_answer = len(re.sub(r"\|[-| ]+\|", "", ans).split())
check("'The answer' section is readable in about two minutes (<= 600 words)", words_answer <= 600, f"{words_answer} words")
bullets_to_flip = md[md.index("## The answer"):md.index("### What would flip it")]
check("Page one before the flip table is under 300 words", len(bullets_to_flip.split()) < 300, f"{len(bullets_to_flip.split())} words")

# ---------- 4. Every number regenerates: perturb inputs; list prose lines with £ figures that do NOT move ----------
alt = M.report({**M.defaults(), "gas_kwh": 13000, "scop": 3.6, "hp_net_cost": 6400, "gas_inflation": 0.04})
alt_lines = set(alt.splitlines())
unchanged = [l for l in lines if re.search(r"£\d|\d+p\b", l) and l in alt_lines and not l.startswith("|") and not l.startswith("```")]
print("     prose lines with money/pence figures that do not change when inputs change (review by eye: must be cited constants only):")
for l in unchanged:
    print("       - " + l[:170])
def section(text, h):
    i = text.index(h); j = text.find("\n## ", i + 3)
    return text[i:j if j > 0 else len(text)]
for h in ("## The 15-year picture", "## How well does the answer hold up?"):
    sec = section(md, h).splitlines()
    rows_ = [l for k, l in enumerate(sec[:-1]) if l.startswith("| ") and not sec[k + 1].startswith("|---") and not sec[k + 1].startswith("| ---")]
    rows_ = [l for l in rows_ if not l.startswith("| ---")]
    moved = [l for l in rows_ if l not in alt_lines]
    check(f"Every result row regenerates when inputs change: {h[3:]}", len(moved) == len(rows_), f"{len(moved)}/{len(rows_)} rows changed")

# ---------- 5. Stale text from earlier versions ----------
for bad in ("Rule of thumb", "What I checked", "Starting assumption", "starting estimate", "**Changed**", "When to re-check", "my efficiency assumption", "my first version", "My first version", "I did not confirm the scheme's end date", "trusting my first guess", "or more or more", "self-selected, often enthusiast", "semi-detached mean 11,715", "hp_tariff_unit", "20p assumed", "Sensitivity (", "stress scenarios", "3.3x as much", "£3,000 for a new", "n/a (the result", "26.3p standard"):
    check(f"No stale text: {bad!r}", bad not in md)

# ---------- 6. Contradictions between prose, tables and thresholds ----------
c, h = M.run(M.defaults(), "cap"), M.run(M.defaults(), "hp")
neg = lambda x: x < 0
both_neg = neg(c["adv"]) and neg(h["adv"])
check("Break-even sentence agrees with year-15 table sign",
      ("Neither tariff breaks even" in md) == both_neg and (both_neg or "never breaks even" in md or "breaks even in year" in md))
a = M.analyse(M.defaults())
check("Flip thresholds really flip the verdict (SCOP, price, gas use)",
      abs(M.run({**M.defaults(), "scop": a["be_scop"]["hp"]}, "hp")["adv"]) < 1 and
      abs(M.run({**M.defaults(), "hp_net_cost": a["be_net_cost"]["hp"]}, "hp")["adv"]) < 1 and
      abs(M.run({**M.defaults(), "gas_kwh": a["be_gas_kwh"]["hp"]}, "hp")["adv"]) < 1)
sc, pr, rows = M.quote_grid(M.defaults(), "hp")
check("Quote grid is monotone: better efficiency or lower price never worsens a cell",
      all({"no": 0, "close": 1, "yes": 2}[rows[i][j]] <= {"no": 0, "close": 1, "yes": 2}[rows[i + 1][j]]
                                                     for i in range(len(sc) - 1) for j in range(len(pr))) and
      all({"no": 0, "close": 1, "yes": 2}[rows[i][j]] >= {"no": 0, "close": 1, "yes": 2}[rows[i][j + 1]] for i in range(len(sc)) for j in range(len(pr) - 1)))
# Monte Carlo reproducibility
check("Simulation is reproducible (same seed, same answer)", M.monte_carlo(M.defaults()) == M.monte_carlo(M.defaults()))

# ---------- 6b. Personal (--me) mode: agrees with the grids, converts units, fails safely, is fast ----------
import time
word = {"YES": "yes", "NO": "no", "TOO CLOSE": "close"}
ok_all, n = True, 0
for t_i, t in enumerate(("cap", "hp")):
    scs, prs, grid_rows = M.quote_grid(M.defaults(), t)
    for i_, sc_ in enumerate(scs):
        for j_, pr_ in enumerate(prs):
            n += 1
            ok_all &= word[M.verdict_for({**M.defaults(), "scop": sc_, "hp_net_cost": pr_})[t_i]] == grid_rows[i_][j_]
check("Grid cells equal the verdict the personal mode would give (70 cells)", ok_all and n == 70)
def cli(*args):
    t0 = time.time()
    r = subprocess.run([sys.executable, "-I", model_path, *args], capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout + r.stderr, time.time() - t0
rc, out, dt = cli("--me", "--gas-kwh", "12800", "--scop", "3.4", "--price", "8200")
check("--me runs in under 10 seconds", rc == 0 and dt < 10, f"{dt:.2f}s")
sc_i, pr_i = 3.5, 7500
rc, out, _ = cli("--me", "--scop", str(sc_i), "--price", str(pr_i), "--gas-kwh", "10500")
scs, prs, grid_rows = M.quote_grid(M.defaults(), "hp")
cell = grid_rows[scs.index(sc_i)][prs.index(pr_i)]
check("--me verdict for a grid point matches the grid's heat-pump-tariff cell", ("TOO CLOSE on a heat-pump tariff" in out or "VERDICT:       " in out) and
      {"yes": "YES", "no": "NO", "close": "TOO CLOSE"}[cell] in out.split("VERDICT:")[1].splitlines()[0] , f"grid says {cell}")
rc1, o1, _ = cli("--me", "--gas-m3", "1000")
rc2, o2, _ = cli("--me", "--gas-kwh", "11200")
check("--gas-m3 converts at 11.2 kWh per m3", rc1 == 0 and rc2 == 0 and o1 == o2)
check("--me with no numbers is refused politely", cli("--me")[0] != 0 and "needs at least one" in cli("--me")[1])
check("--me with garbage is refused politely", cli("--me", "--scop", "abc")[0] != 0 and "Traceback" not in cli("--me", "--scop", "abc")[1])
check("--me with an impossible value is refused politely", cli("--me", "--scop", "0.2")[0] != 0 and "Traceback" not in cli("--me", "--scop", "0.2")[1])
check("--me warns for m3 entered as kWh", "WARNING" in cli("--me", "--gas-kwh", "1000")[1])
check("Usual --set / --check modes still work", cli("--set", "scop=3.4")[0] == 0 and cli("--check", report_path)[0] == 0)

# ---------- 7. Jargon: each technical term used must be explained ----------
gloss = md[md.index("## Plain-English glossary"):md.index("## Limits")]
terms = {"SCOP": "SCOP", "kWh": "kWh", "Standing charge": "standing charge", "Price cap": "price cap",
         "Boiler Upgrade Scheme": "Boiler Upgrade Scheme", "heat-pump tariff": "Heat-pump tariff", "today's money": "Today's money"}
for label_, t in terms.items():
    check(f"Glossary explains {label_}", t.lower() in gloss.lower())
needs_gloss = {"MCS": "MCS", "heat-loss calculation": "heat-loss", "flow temperature": "flow temperature", "simulation draws": "draws",
               "median": "median", "NEED": "NEED", "TDCV": "TDCV", "cylinder": "cylinder", "SPF": "SPF", "IRR": "IRR"}
for label_, t in needs_gloss.items():
    used = t in md.split("## Plain-English glossary")[0] or t in md.split("## Limits")[1]
    explained = t.lower() in gloss.lower() or re.search(re.escape(t) + r"[^.\n]{0,60}\(", md) is not None
    check(f"Jargon {label_!r}: used => explained", (not used) or explained)

# ---------- 8. Links resolve ----------
urls = sorted(set(re.findall(r"\]\((https?://[^)]+)\)", md)))
for u in urls:
    try:
        out = subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "-m", "20", "-A", "Mozilla/5.0", "-w", "%{http_code}", u],
                             capture_output=True, text=True, timeout=30).stdout
    except Exception as e:  # noqa
        out = "ERR"
    check(f"Link resolves: {u[:80]}", out.startswith("2") or out in ("403", "429"), f"HTTP {out}")

print(f"\n{sum(results)}/{len(results)} checks passed")
sys.exit(0 if all(results) else 1)
