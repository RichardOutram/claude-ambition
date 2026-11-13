#!/usr/bin/env python3
"""Heat pump vs gas boiler: 15-year cost model for a typical English 3-bed semi.

Every number in heat-pump-vs-gas-boiler.md is produced by this script.

  python3 heatpump_model.py                          print the summary
  python3 heatpump_model.py --set gas_kwh=12000      change any input (repeatable)
  python3 heatpump_model.py --write FILE.md          regenerate the whole report
  python3 heatpump_model.py --check FILE.md          confirm FILE.md matches the model
  python3 heatpump_model.py --list                   list every input name
  python3 heatpump_model.py --me --gas-kwh 12800 --scop 3.4 --price 8200
                                                     your own verdict from up to three numbers
                                                     (use --gas-m3 if your meter shows cubic metres)

Pass the same --set options to --write and --check. Standard library only.
"""
import random
import sys

# name: (value, label, kind, note)   kind: SOURCE = taken from a cited source,
#                                          ASSUMPTION = my estimate, change it freely
INPUTS = {
    "gas_kwh": (10500, "Gas used per year (kWh)", "ASSUMPTION",
                "NEED (DESNZ), England and Wales 2024: median 10,000, mean 11,200 for all homes. 10,500 is my estimate for a 3-bed semi. "
                "Ofgem's 'typical' 9,500 is lower."),
    "cooking_gas_kwh": (400, "...of which gas cooking (kWh)", "ASSUMPTION", "Rest is heating + hot water."),
    "cooking_elec_kwh": (250, "Electricity for cooking if gas is disconnected (kWh)", "ASSUMPTION",
                         "Induction hob/oven."),
    "boiler_eff": (0.85, "Existing boiler real-world efficiency", "ASSUMPTION", "Older condensing boiler."),
    "new_boiler_eff": (0.88, "Replacement boiler real-world efficiency", "ASSUMPTION", "New condensing boiler."),
    "gas_unit": (0.0797, "Gas unit price (GBP/kWh)", "SOURCE", "Ofgem cap, Oct-Dec 2026, incl. 5% VAT."),
    "gas_sc": (0.2968, "Gas standing charge (GBP/day)", "SOURCE", "Ofgem cap, Oct-Dec 2026."),
    "elec_unit": (0.2632, "Electricity unit price (GBP/kWh)", "SOURCE", "Ofgem cap, Oct-Dec 2026. EXCLUDES VAT (temporary holiday)."),
    "elec_vat": (0.05, "VAT added to electricity (fraction)", "SOURCE",
                 "Ofgem: VAT removed from electricity only 1 Oct 2026 to 31 Mar 2027, so 5% is the long-run price (27.64p). "
                 "0 = holiday made permanent."),
    "scop": (3.0, "Heat pump seasonal efficiency (SCOP/SPF)", "ASSUMPTION",
             "Field trial median 2.8 (older installs); Nesta models 3.0. No survey of your house yet."),
    "hp_tariff_factor": (0.80, "Heat-pump tariff price as a fraction of the standard tariff", "ASSUMPTION",
                         "From Octopus Cosy's structure (cheap = 49% of day rate, peak = 150%): avoiding 4-7pm and running ~40% of the time "
                         "in cheap windows gives 0.80. Assumes the Cosy day rate is about the standard rate."),
    "hp_net_cost": (7500, "Heat pump net cost after grant (GBP)", "SOURCE", "Your figure. Grant is GBP 7,500 (GOV.UK). Market median is nearer GBP 5,500 net (see checks)."),
    "hp_service": (150, "Heat pump annual service (GBP)", "ASSUMPTION", ""),
    "boiler_service": (100, "Boiler annual service (GBP)", "ASSUMPTION", ""),
    "boiler_replace_year": (5, "Year existing boiler would be replaced", "ASSUMPTION",
                            "Boiler assumed ~10 years old with a ~15 year life. 0 = it is dying now."),
    "boiler_replace_cost": (2500, "New boiler installed cost (GBP)", "ASSUMPTION", "Published 2026 range GBP 2,000-3,500; median combi swap about 2,300."),
    "boiler_life": (15, "Boiler lifespan (years)", "ASSUMPTION", "Used to credit remaining life at the end of the period."),
    "hp_life": (18, "Heat pump lifespan (years)", "ASSUMPTION", "Typically quoted as 15-20 years."),
    "horizon": (15, "Years compared", "ASSUMPTION", ""),
    "gas_inflation": (0.03, "Gas price rise per year", "ASSUMPTION", "Both fuels rise together in the base case."),
    "elec_inflation": (0.03, "Electricity price rise per year", "ASSUMPTION", ""),
    "discount": (0.035, "Discount rate for 'today's money' view", "ASSUMPTION", "HM Treasury Green Book rate."),
    "disconnect_gas": (1, "Disconnect gas when heat pump goes in (1=yes, 0=no)", "ASSUMPTION", ""),
}
# Used only to cross-check my price inputs against Ofgem's published typical bill.
CHECK_ELEC_KWH, CHECK_ELEC_SC, CHECK_GAS_KWH, OFGEM_TYPICAL_BILL = 2500, 0.5483, 9500, 1723

MC_DRAWS, MC_SEED = 5000, 20261113  # fixed seed: same inputs always give the same answer
# One-at-a-time ranges for the driver table: (label, {input: (low-case value, high-case value)}).
# "low" and "high" are the plausible extremes of the input, not good/bad for the heat pump.
TORNADO = [
    ("Heat pump efficiency (SCOP 2.6 to 4.0)", {"scop": (2.6, 4.0)}),
    ("Net installed price (£9,000 to £5,500)", {"hp_net_cost": (9000, 5500)}),
    ("Home's gas use (8,000 to 13,000 kWh/yr)", {"gas_kwh": (8000, 13000)}),
    ("When the boiler would need replacing (never in period to now)", {"boiler_replace_year": (99, 0)}),
    ("Replacement boiler cost (£2,000 to £3,500)", {"boiler_replace_cost": (2000, 3500)}),
    ("Fuel price paths (elec dearer: gas +2%/elec +4% to elec cheaper: gas +4%/elec +2%)",
     {"gas_inflation": (0.02, 0.04), "elec_inflation": (0.04, 0.02)}),
    ("Heat-pump tariff price (no load shifting to mostly shifted; heat-pump tariff only)", {"hp_tariff_factor": (0.90, 0.62)}),
    ("VAT on electricity (5% returns, to holiday made permanent)", {"elec_vat": (0.05, 0.0)}),
    ("Existing boiler efficiency (90% to 78%)", {"boiler_eff": (0.90, 0.78)}),
    ("Keep gas connected (yes to no)", {"disconnect_gas": (0, 1)}),
]
REGRET = 2000  # 'a lot better/worse off' for the simulation table
VERDICT_BAND = 1000  # within +/- this many GBP over the horizon counts as "too close"


def defaults():
    return {k: v[0] for k, v in INPUTS.items()}


def money(x, sign=False):
    s = f"{abs(x):,.0f}"
    if x < -0.5:
        return f"-£{s}"
    return (f"+£{s}" if sign and x > 0.5 else f"£{s}")


def run(p, tariff="cap"):
    """tariff 'cap' = heat pump on the standard price-cap rate; 'hp' = on a heat-pump tariff."""
    H = int(p["horizon"])
    cook_g = p["cooking_gas_kwh"]
    heat = (p["gas_kwh"] - cook_g) * p["boiler_eff"]  # useful heat needed per year (kWh)
    ry = int(p["boiler_replace_year"])
    cashB = [0.0] * (H + 1)
    cashH = [0.0] * (H + 1)
    cashH[0] = p["hp_net_cost"]
    if ry == 0:
        cashB[0] = p["boiler_replace_cost"]
    uc = p["elec_unit"] * (1 + p["elec_vat"])
    uh = uc * p["hp_tariff_factor"] if tariff == "hp" else uc
    for t in range(1, H + 1):
        fg = (1 + p["gas_inflation"]) ** (t - 1)
        fe = (1 + p["elec_inflation"]) ** (t - 1)
        eff = p["boiler_eff"] if t <= ry else p["new_boiler_eff"]
        gas_sc = p["gas_sc"] * 365 * fg
        cashB[t] = (heat / eff + cook_g) * p["gas_unit"] * fg + gas_sc + p["boiler_service"]
        if t == ry and ry > 0:
            cashB[t] += p["boiler_replace_cost"]
        h = heat / p["scop"] * uh * fe + p["hp_service"]
        if p["disconnect_gas"]:
            h += p["cooking_elec_kwh"] * uc * fe
        else:
            h += cook_g * p["gas_unit"] * fg + gas_sc
        cashH[t] = h
    # Remaining life at the end is credited at what was paid, straight-line (a notional value, not a sale price).
    if 0 <= ry <= H:
        cashB[H] -= p["boiler_replace_cost"] * max(0, p["boiler_life"] - (H - ry)) / p["boiler_life"]
    cashH[H] -= p["hp_net_cost"] * max(0, p["hp_life"] - H) / p["hp_life"]
    cumB, cumH, a, b = [], [], 0.0, 0.0
    for t in range(H + 1):
        a += cashB[t]; b += cashH[t]
        cumB.append(a); cumH.append(b)
    d = p["discount"]
    pv = sum((cashB[t] - cashH[t]) / (1 + d) ** t for t in range(H + 1))
    be = next((t for t in range(H + 1) if cumH[t] <= cumB[t]), None)
    flows = [cashB[t] - cashH[t] for t in range(H + 1)]  # heat pump minus boiler, per year
    return {"cumB": cumB, "cumH": cumH, "adv": cumB[H] - cumH[H], "pv": pv, "breakeven_year": be,
            "y1B": cashB[1], "y1H": cashH[1], "heat": heat, "flows": flows}


def annual_return(flows):
    """Yearly rate of return on the extra money put into the heat pump (IRR); None if outside -30%..+30%."""
    npv = lambda r: sum(f / (1 + r) ** t for t, f in enumerate(flows))
    return solve(npv, -0.30, 0.30)


def solve(f, lo, hi):
    """Root of f on [lo, hi] by bisection; None if there is no sign change."""
    flo, fhi = f(lo), f(hi)
    if flo == 0: return lo
    if flo * fhi > 0: return None
    for _ in range(80):
        mid = (lo + hi) / 2
        fm = f(mid)
        if flo * fm <= 0: hi = mid
        else: lo, flo = mid, fm
    return (lo + hi) / 2


def label(adv):
    return "YES" if adv > VERDICT_BAND else "NO" if adv < -VERDICT_BAND else "TOO CLOSE"


def analyse(p):
    r = {"cap": run(p, "cap"), "hp": run(p, "hp")}
    out = {"base": r}
    adv_scop = lambda tar: (lambda s: run({**p, "scop": s}, tar)["adv"])
    out["be_scop"] = {t: solve(adv_scop(t), 1.5, 8.0) for t in ("cap", "hp")}
    out["be_hp_price"] = solve(lambda u: run({**p, "hp_tariff_factor": u}, "hp")["adv"], 0.05, 1.5)
    out["be_net_cost"] = {t: solve(lambda c: run({**p, "hp_net_cost": c}, t)["adv"], 0, 200000) for t in ("cap", "hp")}
    out["be_gas_kwh"] = {t: solve(lambda g: run({**p, "gas_kwh": g}, t)["adv"], 3000, 60000) for t in ("cap", "hp")}
    out["mc"] = monte_carlo(p)
    out["tornado"] = tornado(p)
    return out


def tornado(p):
    rows = []
    for nm, ch in TORNADO:
        lo = {**p, **{k: v[0] for k, v in ch.items()}}
        hi = {**p, **{k: v[1] for k, v in ch.items()}}
        res = {t: (run(lo, t)["adv"], run(hi, t)["adv"]) for t in ("cap", "hp")}
        swing = max(abs(res[t][1] - res[t][0]) for t in ("cap", "hp") if not (t == "cap" and "tariff" in nm))
        rows.append((swing, nm, res))
    return sorted(rows, key=lambda r: -r[0])


def tri(rng, lo, mode, hi):
    return rng.triangular(lo, hi, mode)


def monte_carlo(p):
    """Draw uncertain inputs from stated ranges (centred on your inputs); report how the heat pump fares."""
    rng = random.Random(MC_SEED)
    sc, gk = p["scop"], p["gas_kwh"]
    res = {"cap": [], "hp": []}
    for _ in range(MC_DRAWS):
        z1, z2 = rng.gauss(0, 1), rng.gauss(0, 1)
        q = {**p,
             "scop": tri(rng, sc - 0.6, sc, sc + 1.0),
             "gas_kwh": tri(rng, gk * 0.75, gk, gk * 1.35),
             "hp_net_cost": tri(rng, p["hp_net_cost"] * 0.7, p["hp_net_cost"], p["hp_net_cost"] * 1.35),
             "boiler_replace_year": rng.randint(0, int(p["horizon"]) - 1),
             "boiler_replace_cost": tri(rng, p["boiler_replace_cost"] * 0.75, p["boiler_replace_cost"], p["boiler_replace_cost"] * 1.5),
             "boiler_eff": tri(rng, p["boiler_eff"] - 0.07, p["boiler_eff"], p["boiler_eff"] + 0.05),
             "hp_tariff_factor": tri(rng, 0.62, p["hp_tariff_factor"], 0.90),
             "elec_vat": 0.0 if rng.random() < 0.25 else p["elec_vat"],  # 25%: VAT holiday gets extended for good
             "gas_inflation": min(0.10, max(-0.02, p["gas_inflation"] + 0.012 * z1)),
             "elec_inflation": min(0.10, max(-0.02, p["elec_inflation"] + 0.012 * (0.6 * z1 + 0.8 * z2)))}
        for t in ("cap", "hp"):
            res[t].append(run(q, t)["adv"])
    out = {}
    for t, v in res.items():
        v.sort()
        out[t] = {"p_cheaper": sum(x > 0 for x in v) / len(v), "p10": v[len(v) // 10], "median": v[len(v) // 2],
                  "p90": v[9 * len(v) // 10],
                  "p_win": sum(x > REGRET for x in v) / len(v), "p_lose": sum(x < -REGRET for x in v) / len(v)}
    return out


def selftest():
    """Independent checks that don't depend on the model agreeing with itself."""
    d = defaults()
    res = []
    # 1. Ofgem's published typical bill (£1,723) from the cap rates and typical use.
    bill = CHECK_GAS_KWH * d["gas_unit"] + d["gas_sc"] * 365 + CHECK_ELEC_KWH * d["elec_unit"] + CHECK_ELEC_SC * 365
    res.append(("Ofgem typical bill reproduced within £1", abs(bill - OFGEM_TYPICAL_BILL) < 1.0, f"{money(bill)} vs {money(OFGEM_TYPICAL_BILL)}"))
    # 2. Nesta: at a price ratio of 3.3 a heat pump with efficiency 2.8 costs the same to run as an 85% gas boiler.
    q = {**d, "gas_unit": 0.10, "elec_unit": 0.33, "scop": 2.8, "boiler_eff": 0.85, "gas_sc": 0.0, "boiler_service": 0.0,
         "hp_service": 0.0, "cooking_gas_kwh": 0.0, "cooking_elec_kwh": 0.0, "boiler_replace_year": 99, "elec_vat": 0.0}
    r = run(q, "cap")
    res.append(("Nesta running-cost parity (ratio 3.3, efficiency 2.8, boiler 85%; Nesta rounds, so within 1%)",
                abs(r["y1B"] - r["y1H"]) < 0.01 * r["y1B"],
                f"boiler {money(r['y1B'])} vs heat pump {money(r['y1H'])}"))
    # 3. Hand-derived case: flat prices, no growth, no services, no residual -> advantage = H*(saving) - net cost.
    q = {**d, "gas_inflation": 0.0, "elec_inflation": 0.0, "boiler_service": 0.0, "hp_service": 0.0, "boiler_replace_year": 99,
         "cooking_gas_kwh": 0.0, "cooking_elec_kwh": 0.0, "gas_sc": 0.0, "boiler_life": 1e9, "hp_life": float(d["horizon"]),
         "gas_kwh": 10000, "boiler_eff": 0.8, "scop": 4.0, "gas_unit": 0.08, "elec_unit": 0.20, "hp_net_cost": 5000, "elec_vat": 0.0}
    saving = 10000 * 0.08 - (10000 * 0.8 / 4.0) * 0.20  # 800 - 400 = 400 a year
    want = q["horizon"] * saving - 5000
    got = run(q, "cap")["adv"]
    res.append(("Hand-derived flat-price case", abs(got - want) < 0.01, f"model {money(got, True)} vs by hand {money(want, True)}"))
    # 4. Monotonic: better efficiency never makes the heat pump worse off.
    a = [run({**d, "scop": x}, "cap")["adv"] for x in (2.0, 2.5, 3.0, 3.5, 4.0)]
    res.append(("Higher efficiency never hurts", all(a[i] < a[i + 1] for i in range(4)), ""))
    return res


def validate(p):
    """Hard errors for inputs that would make the model meaningless."""
    bad = []
    if not 1.0 <= p["scop"] <= 10: bad.append("scop must be between 1 and 10 (typical 2.5-4)")
    if p["gas_kwh"] <= p["cooking_gas_kwh"]: bad.append("gas_kwh must be more than cooking_gas_kwh (is it in kWh?)")
    if not 5 <= p["horizon"] <= 40: bad.append("horizon must be 5-40 years")
    for k in ("boiler_eff", "new_boiler_eff"):
        if not 0.3 <= p[k] <= 1.0: bad.append(f"{k} must be between 0.3 and 1.0")
    for k in ("boiler_life", "hp_life", "gas_unit", "elec_unit", "hp_tariff_factor"):
        if p[k] <= 0: bad.append(f"{k} must be above 0")
    if p["elec_vat"] < 0 or p["gas_sc"] < 0 or p["hp_net_cost"] < 0: bad.append("vat, standing charge and cost can't be negative")
    if bad: sys.exit("Input problem:\n  " + "\n  ".join(bad))


def warnings(p):
    """Soft warnings for inputs that run but look like a mistake."""
    w = []
    if p["gas_kwh"] < 4000 or p["gas_kwh"] > 25000:
        w.append(f"gas_kwh = {p['gas_kwh']:,.0f} is unusual. Bills are in kWh. If your meter shows cubic metres (m3), multiply by about 11.2 to get kWh.")
    if p["scop"] > 4.5: w.append(f"SCOP {p['scop']} is above what most UK homes achieve; use the installer's predicted figure for your house.")
    if p["hp_net_cost"] < 3000 or p["hp_net_cost"] > 15000: w.append(f"Net heat pump price {money(p['hp_net_cost'])} is outside the usual range; is it after the grant?")
    if p["elec_unit"] / p["gas_unit"] < 2 or p["elec_unit"] / p["gas_unit"] > 6: w.append("Electricity-to-gas price ratio is outside 2-6; check the unit prices are in GBP per kWh.")
    return w


def verdict_for(p):
    """(standard-tariff label, heat-pump-tariff label, simulation results): the same rule as the headline verdict."""
    a = {"base": {t: run(p, t) for t in ("cap", "hp")}, "mc": monte_carlo(p)}
    return labels(a) + [a]


def quote_grid(p, tariff):
    """Verdict for each combination of predicted SCOP and net installed price (everything else as in the inputs)."""
    scops, prices = [2.6, 2.8, 3.0, 3.2, 3.5, 3.8, 4.2], [5500, 6500, 7500, 8500, 9500]
    word = {"YES": "yes", "NO": "no", "TOO CLOSE": "close"}
    k = 0 if tariff == "cap" else 1
    rows = [[word[verdict_for({**p, "scop": sc, "hp_net_cost": pr})[k]] for pr in prices] for sc in scops]
    return scops, prices, rows


def labels(a):
    """Verdict per tariff. Point estimate and simulation median must agree, otherwise it is 'too close'."""
    out = []
    for t in ("cap", "hp"):
        x, y = label(a["base"][t]["adv"]), label(a["mc"][t]["median"])
        out.append(x if x == y else "TOO CLOSE")
    return out


def verdict_text(p, a):
    lc, lh = labels(a)
    if lc == lh:
        head = lc
    else:
        head = f"{lc} on a standard tariff; {lh} on a heat-pump tariff"
    m = a["mc"]["cap"]
    if lc == "NO": agree = 1 - m["p_cheaper"]
    elif lc == "YES": agree = m["p_cheaper"]
    else: agree = None
    if agree is None:
        conf = "n/a (the result sits inside the ±£1,000 'too close' band)"
    else:
        conf = ("High" if agree >= .9 else "Moderate" if agree >= .7 else "Low") + \
            f" (on a standard tariff the simulation agrees with this in {agree:.0%} of {MC_DRAWS:,} draws)"
    return head, conf


def summary(p):
    a = analyse(p)
    c, h = a["base"]["cap"], a["base"]["hp"]
    head, conf = verdict_text(p, a)
    typical = CHECK_GAS_KWH * p["gas_unit"] + p["gas_sc"] * 365 + CHECK_ELEC_KWH * p["elec_unit"] + CHECK_ELEC_SC * 365
    L = [f"WARNING: {w}" for w in warnings(p)]
    L.append(f"VERDICT: {head}")
    L.append(f"CONFIDENCE: {conf}")
    L.append(f"Check: Ofgem typical-use bill from these prices = {money(typical)} (Ofgem published {money(OFGEM_TYPICAL_BILL)})")
    L.append(f"Useful heat needed per year: {c['heat']:,.0f} kWh")
    L.append(f"Year-1 running cost, keep boiler (incl. service, gas standing charge): {money(c['y1B'])}")
    L.append(f"Year-1 running cost, heat pump on standard tariff:  {money(c['y1H'])}  (saving {money(c['y1B']-c['y1H'], True)})")
    L.append(f"Year-1 running cost, heat pump on heat-pump tariff: {money(h['y1H'])}  (saving {money(c['y1B']-h['y1H'], True)})")
    H = int(p["horizon"])
    L.append(f"{H}-year position vs keeping boiler (positive = heat pump cheaper):")
    for name, x in (("standard tariff", c), ("heat-pump tariff", h)):
        be = f"breaks even in year {x['breakeven_year']}" if x["breakeven_year"] is not None else "does not break even"
        L.append(f"  {name:17s} {money(x['adv'], True):>8s} cash, {money(x['pv'], True):>8s} in today's money; {be}")
    for t, nm in (("cap", "standard tariff"), ("hp", "heat-pump tariff")):
        r = annual_return(a["base"][t]["flows"])
        L.append(f"  Return on the extra money, {nm}: " + ("outside -30%..+30% a year" if r is None else f"{r:+.1%} a year"))
    L.append("Break-even thresholds (heat pump = boiler over the period):")
    for t, nm in (("cap", "standard tariff"), ("hp", "heat-pump tariff")):
        v = a["be_scop"][t]
        L.append(f"  SCOP needed, {nm}: {'n/a' if v is None else f'{v:.2f}'}")
    bp = a["be_hp_price"]
    L.append(f"  Heat-pump tariff price needed at SCOP {p['scop']}: " + ("none within 5%-150% of the standard rate" if bp is None else
             f"{bp*p['elec_unit']*(1+p['elec_vat'])*100:.1f}p/kWh ({bp:.0%} of the standard rate)"))
    nc = lambda v: "none" if v is None else money(v)
    L.append(f"  Net heat pump cost needed, standard tariff: {nc(a['be_net_cost']['cap'])}; heat-pump tariff: {nc(a['be_net_cost']['hp'])}")
    for t, nm in (("cap", "standard tariff"), ("hp", "heat-pump tariff")):
        v = a["be_gas_kwh"][t]
        L.append(f"  Gas use needed, {nm}: {'n/a' if v is None else f'{v:,.0f} kWh/yr'}")
    L.append(f"Simulation ({MC_DRAWS:,} draws, seed {MC_SEED}; every uncertain input varied together around your inputs):")
    for t, nm in (("cap", "standard tariff"), ("hp", "heat-pump tariff")):
        m = a["mc"][t]
        L.append(f"  {nm:17s} heat pump cheaper in {m['p_cheaper']:.0%} of draws; "
                 f"median {money(m['median'], True)}, 80% range {money(m['p10'], True)} to {money(m['p90'], True)}; "
                 f"more than {money(REGRET)} worse off in {m['p_lose']:.0%}, more than {money(REGRET)} better off in {m['p_win']:.0%}")
    L.append("Biggest drivers (advantage over the period at each extreme: standard tariff | heat-pump tariff; ranked by swing):")
    for swing, nm, res in a["tornado"]:
        L.append(f"  {nm}")
        L.append(f"      {money(res['cap'][0], True):>8s} to {money(res['cap'][1], True):>8s}  |  {money(res['hp'][0], True):>8s} to {money(res['hp'][1], True):>8s}")
    L.append("Self-test (independent checks):")
    for nm, ok, detail in selftest():
        L.append(f"  {'PASS' if ok else 'FAIL'}  {nm}" + (f" [{detail}]" if detail else ""))
    return "\n".join(L), a


GAS_M3_TO_KWH = 11.2  # typical: volume correction x calorific value / 3.6


def me_summary(p, given):
    """Short plain-English verdict for someone's own numbers."""
    a = analyse(p)
    head, conf = verdict_text(p, a)
    lc, lh = labels(a)
    c, h = a["base"]["cap"], a["base"]["hp"]
    H = int(p["horizon"])
    typical = [nm for k, nm in (("gas_kwh", "gas use"), ("scop", "efficiency (SCOP)"), ("hp_net_cost", "price")) if k not in given]
    L = [f"WARNING: {w}" for w in warnings(p)]
    L.append(f"You gave:      gas {p['gas_kwh']:,.0f} kWh/yr | installer SCOP {p['scop']:.1f} | net price {money_round(p['hp_net_cost'])}")
    if typical:
        L.append(f"Typical used:  {', '.join(typical)}, plus Ofgem Oct-Dec 2026 cap prices and the other assumptions in the report")
    L.append(f"VERDICT:       {head}")
    L.append(f"Over {H} years vs keeping your boiler (negative = heat pump costs more):")
    L.append(f"  standard tariff:  {money_round(c['adv'], True):>8s}   (heat pump cheaper in {a['mc']['cap']['p_cheaper']:.0%} of 5,000 simulated futures)")
    L.append(f"  heat-pump tariff: {money_round(h['adv'], True):>8s}   (heat pump cheaper in {a['mc']['hp']['p_cheaper']:.0%} of 5,000 simulated futures)")
    sc, pc = a["be_scop"]["hp"], a["be_net_cost"]["hp"]
    L.append("To break even on a heat-pump tariff you would need: " + ", ".join(
        x for x in (None if sc is None else f"SCOP {sc:.2f} or more", None if pc is None else f"a net price of {money_round(pc)} or less") if x))
    L.append("This is a money-only forecast on typical tariffs; see heat-pump-vs-gas-boiler.md for the working and what could change it.")
    return "\n".join(L)


def bottom(lc, lh):
    if lc == "YES":
        return "go ahead: it should pay for itself even on a standard tariff."
    if lh == "YES":
        return "only worth it if you switch to a heat-pump tariff; on a standard tariff it won't pay back."
    if lh == "TOO CLOSE":
        return ("don't do it just to save money on a standard tariff. On a heat-pump tariff it roughly breaks even, "
                "so it comes down to the efficiency your installer predicts and whether you value the non-financial benefits.")
    return "don't do it to save money; it costs more over the period on either tariff."


def money_round(x, sign=False):
    """Report figures are rounded: this is a forecast, not an invoice."""
    x = round(x / 50) * 50 if abs(x) >= 1000 else round(x / 10) * 10 if abs(x) >= 100 else x
    return money(x, sign)


def report(p):
    money = money_round  # noqa: all £ figures in the report are rounded; exact values are in the script output
    text, a = summary(p)
    c, h = a["base"]["cap"], a["base"]["hp"]
    head, conf = verdict_text(p, a)
    H = int(p["horizon"])
    be = a["be_scop"]
    f = lambda v, fmt: "never (within the modelled range)" if v is None else fmt.format(v)
    ry = int(p["boiler_replace_year"])
    g = lambda v: "no realistic level" if v is None else f"{v:,.0f} kWh/yr"
    o = []
    o.append("# Should I swap my gas boiler for a heat pump?\n")
    o.append("*Typical English 3-bed semi on the Ofgem price cap (Oct-Dec 2026). Prices and efficiency come from the sources at the "
             "bottom; everything else is a flagged assumption. Every figure below is generated by `heatpump_model.py`, so you can "
             "change an input and regenerate the file (see 'Re-run it').*\n")
    o.append("*Who this is for: an owner-occupier in England with a mains-gas boiler and a wet (radiator) system, deciding on money. "
             "It will mislead you if your home is off the gas grid, is a flat, is in Scotland, Wales or Northern Ireland, or if carbon, comfort or "
             "future boiler rules matter more to you than cost. Figures are rounded: this is a forecast, not a quote.*\n")
    o.append("*In plain terms: **SCOP** is how many units of heat a heat pump delivers per unit of electricity (3.0 means 3). "
             "A **heat-pump tariff** is electricity priced lower at certain times of day. More terms are explained in the glossary near the end.*\n")
    for w in warnings(p):
        o.append(f"> **Check your inputs:** {w}\n")
    o.append("## The answer\n")
    o.append(f"> **Verdict: {head}**  \n> **Confidence: {conf}**\n")
    gap = lambda x: f"{money(abs(x))} {'better off' if x > 0 else 'worse off'}"
    o.append(f"- **Bottom line:** {bottom(*labels(a))}")
    o.append(f"- **Over {H} years, a heat pump on a standard tariff leaves you {gap(c['adv'])} than keeping a gas boiler** "
             f"({gap(c['pv'])} in today's money). On a heat-pump tariff you'd be {gap(h['adv'])} "
             f"({gap(h['pv'])} in today's money).")
    ir = {t: annual_return(a["base"][t]["flows"]) for t in ("cap", "hp")}
    fr = lambda r: "loses more than 30%" if r is None else (f"loses about {abs(r):.0%}" if r < -0.005 else f"earns about {r:.0%}")
    o.append(f"- **As an investment:** over {H} years the extra money you put into the heat pump {fr(ir['cap'])} a year on a standard tariff "
             f"and {fr(ir['hp'])} a year on a heat-pump tariff. Compare that with what the same money would earn in savings "
             "or by paying down debt.")
    o.append(f"- **Running costs barely differ; the up-front cost is what decides it.** In year 1 the heat pump's bills are "
             f"{money(c['y1B']-c['y1H'])} lower on a standard tariff or {money(c['y1B']-h['y1H'])} lower on a heat-pump tariff, "
             f"but you pay {money(p['hp_net_cost'])} after the grant. Keeping the boiler means paying "
             f"{money(p['boiler_replace_cost'])} for a new one in year {ry}, which narrows the gap but doesn't close it.")
    o.append(f"- **Why bills are so similar:** a kWh of heat costs about {p['gas_unit']/p['boiler_eff']*100:.1f}p from your gas boiler "
             f"and {p['elec_unit']*(1+p['elec_vat'])/p['scop']*100:.1f}p from a heat pump at SCOP {p['scop']:.1f} on the standard tariff. "
             f"Electricity (with VAT) costs {p['elec_unit']*(1+p['elec_vat'])/p['gas_unit']:.1f}x as much per kWh as gas, which cancels out most of the heat pump's efficiency.\n")
    o.append("### What would flip it\n")
    o.append("| If... | Today's assumption | The heat pump breaks even over the period when... |")
    o.append("|---|---|---|")
    o.append(f"| Your installer's **predicted SCOP** (efficiency) is higher | {p['scop']:.1f} | "
             f"{f(be['cap'], '{:.2f}')} or more on a standard tariff, {f(be['hp'], '{:.2f}')} or more on a heat-pump tariff |")
    o.append(f"| You get a **cheaper electricity tariff** for heating | {p['elec_unit']*(1+p['elec_vat'])*100:.1f}p standard; "
             f"{p['elec_unit']*p['hp_tariff_factor']*(1+p['elec_vat'])*100:.1f}p assumed heat-pump tariff | {('no realistic price' if a['be_hp_price'] is None else '%.1fp/kWh blended or lower' % (a['be_hp_price']*p['elec_unit']*(1+p['elec_vat'])*100))}, at SCOP {p['scop']:.1f} |")
    nc = lambda v: "no price" if v is None else money(v)
    o.append(f"| The **installed price** is lower | {money(p['hp_net_cost'])} | {nc(a['be_net_cost']['cap'])} or less (standard tariff), "
             f"{nc(a['be_net_cost']['hp'])} or less (heat-pump tariff) |")
    o.append(f"| Your home uses more **gas** | {p['gas_kwh']:,.0f} kWh/yr | "
             f"{g(a['be_gas_kwh']['cap'])}{'' if a['be_gas_kwh']['cap'] is None else ' or more'} (standard tariff), {g(a['be_gas_kwh']['hp'])}{'' if a['be_gas_kwh']['hp'] is None else ' or more'} (heat-pump tariff) |")
    o.append(f"| Your **boiler is failing soon** | replaced in year {ry} | see the 'when the boiler would need replacing' row in the drivers table |\n")
    top = [nm.split(" (")[0].lower() for _, nm, _ in a["tornado"][:3]]
    o.append(f"The simulation below says the three things that move the result most are: {top[0]}, {top[1]}, and {top[2]}. "
             "Of all the inputs, efficiency and tariff price can be pinned down before you buy; future fuel prices can't.\n")

    o.append(f"## The {H}-year picture\n")
    o.append(f"Total cash spent from today (heat pump installed now vs. keeping the boiler and replacing it in year {ry}). "
             "Prices rise each year as set in the assumptions. A positive 'heat pump ahead by' means the heat pump has cost less in total.\n")
    o.append("| Year | Keep boiler: total spent | Heat pump (standard tariff): total spent | Heat pump ahead by | Heat pump (heat-pump tariff): total spent | Heat pump ahead by |")
    o.append("|---|---|---|---|---|---|")
    for t in [0, 1, 2, 3, 5, 7, 10, 12, H]:
        if t > H: continue
        o.append(f"| {t} | {money(c['cumB'][t])} | {money(c['cumH'][t])} | {money(c['cumB'][t]-c['cumH'][t], True)} | "
                 f"{money(h['cumH'][t])} | {money(h['cumB'][t]-h['cumH'][t], True)} |")
    o.append("")
    o.append(f"The heat pump starts {money(p['hp_net_cost'])} behind and claws it back through lower bills. "
             + ("Neither tariff breaks even within %d years. " % H if c['breakeven_year'] is None and h['breakeven_year'] is None else
                f"Standard tariff: {'breaks even in year %d' % c['breakeven_year'] if c['breakeven_year'] is not None else 'never breaks even'} within {H} years. "
                f"Heat-pump tariff: {'breaks even in year %d' % h['breakeven_year'] if h['breakeven_year'] is not None else 'never breaks even'} within {H} years. ") +
             f"The step in the 'keep boiler' column at year {ry} is the replacement boiler. "
             "Remaining life of each system at the end is credited at what you paid, spread evenly over its lifespan (a notional value, not a sale price).\n")

    o.append("## How well does the answer hold up?\n")
    m = a["mc"]
    o.append(f"**Simulation.** I varied every uncertain input at once ({MC_DRAWS:,} random draws around your inputs: efficiency, gas use, "
             "installed price, boiler age and cost, fuel price rises, tariff price, whether VAT returns). The ranges are my judgement, "
             "centred on the base case and spelled out in `monte_carlo()`; they are not measured spreads.\n")
    o.append(f"| | Heat pump cheaper in... | Typical result (median) | 80% of draws fall between | More than {money(REGRET)} worse off | More than {money(REGRET)} better off |")
    o.append("|---|---|---|---|---|---|")
    for t, nm in (("cap", "Standard tariff"), ("hp", "Heat-pump tariff")):
        x = m[t]
        o.append(f"| {nm} | {x['p_cheaper']:.0%} of draws | {money(x['median'], True)} | {money(x['p10'], True)} to {money(x['p90'], True)} | {x['p_lose']:.0%} | {x['p_win']:.0%} |")
    o.append("\n**What matters most.** Each row moves one input between plausible extremes and shows the heat pump's advantage at each end "
             "(positive = heat pump ahead after the full period). Rows are ranked by how far they move the result.\n")
    o.append("| Input (extremes tested) | Standard tariff | Heat-pump tariff |")
    o.append("|---|---|---|")
    for swing, nm, res in a["tornado"]:
        o.append(f"| {nm} | {money(res['cap'][0], True)} to {money(res['cap'][1], True)} | {money(res['hp'][0], True)} to {money(res['hp'][1], True)} |")
    o.append("\n**Self-test.** The model must reproduce numbers it didn't make up:\n")
    for nm, ok, detail in selftest():
        o.append(f"- {'Pass' if ok else '**FAIL**'}: {nm}" + (f" ({detail})" if detail else ""))
    o.append("")

    o.append("## Using this with an installer quote\n")
    o.append("Ask each installer for: (1) a room-by-room heat-loss calculation, (2) the predicted SCOP at your design flow temperature, "
             "(3) the total price with the grant already deducted, and (4) whether radiators or a hot-water cylinder need replacing and are "
             "included. Then look up their SCOP and price below. Everything else is as in the base case.\n")
    for t, nm in (("cap", "On a standard tariff"), ("hp", "On a heat-pump tariff")):
        sc, pr, rows = quote_grid(p, t)
        o.append(f"**{nm}** (yes = clearly cheaper over {H} years; close = too near to call, within {money(VERDICT_BAND)} or the simulation disagrees with the point estimate; no = clearly dearer)\n")
        o.append("| Predicted SCOP \\ Net price | " + " | ".join(money(x) for x in pr) + " |")
        o.append("|---|" + "---|" * len(pr))
        for s_, r_ in zip(sc, rows):
            o.append(f"| {s_:.1f} | " + " | ".join(r_) + " |")
        o.append("")
    o.append("## Decisions and next checks\n")
    o.append("| # | Decision | Options | For / against | Pick | Owner | Decide by |")
    o.append("|---|---|---|---|---|---|---|")
    o.append("| 1 | Buy a heat pump to save money? | A. Keep the boiler and revisit when it fails. B. Collect 2-3 quotes, then decide using the quote grids. C. Commit now. | A: costs nothing and loses nothing on today's figures, but the grant may end. B: a few hours' work turns the two biggest unknowns (efficiency, price) into facts. C: commits £7,500 on typical assumptions. | B, defaulting to A unless a quote lands in a 'yes' cell. | You | 31 Jan 2027 |")
    keep_cost = c["adv"] - run({**p, "disconnect_gas": 0}, "cap")["adv"]
    o.append(f"| 2 | If you proceed: which tariff? | A. Standard tariff. B. Heat-pump or time-of-use tariff. | A: simple, but {money(abs(c['adv']))} {'worse' if c['adv'] < 0 else 'better'} off over {H} years at current prices. B: cheaper only if the heat pump runs mostly in the cheap windows; rates vary by region. | B, only with the installer's written plan for when the heat pump runs. | You, with the installer | 31 Jan 2027 |")
    o.append(f"| 3 | Disconnect gas after installing? | A. Disconnect at once. B. Keep it connected through the first winter. | A: stops the standing charge (about {money(p['gas_sc'] * 365)} a year) but needs an electric hob and removes the fallback. B: costs about {money(keep_cost)} over {H} years on a standard tariff if kept for good, and keeps a fallback while you learn how the heat pump performs. | B, then disconnect if the first winter goes well. | You | 31 Mar 2028, if installed in 2027 |")
    o.append("")
    o.append("| Next check | Owner | Date |")
    o.append("|---|---|---|")
    o.append("| Replace the typical gas use with your own: `--me --gas-kwh <last 12 months from your bills>` | You | 20 Nov 2026 |")
    o.append("| Re-run with the January-March price cap (Ofgem confirmation reported due by 25 November) | You | 27 Nov 2026 |")
    o.append("| Test each installer quote (heat-loss calculation, predicted SCOP at your design flow temperature, price after grant, radiators and cylinder included) in the quote grids, then with `--me` | You | 31 Jan 2027 |")
    o.append("| Electricity VAT holiday ends 31 March 2027 unless extended; if extended, set `elec_vat=0` and re-run | You | 7 Apr 2027 |")
    o.append("| If your boiler fails before you decide, set `boiler_replace_year=0` and re-run; that is the case most favourable to the heat pump | You | When it happens |")
    o.append("| On a fixed-price deal, enter your own unit rates with `--set` | You | When you have the quotes |")
    o.append("")
    o.append("## Evidence behind the key inputs\n")
    mk = lambda **kw: run({**p, **kw}, "hp")["adv"]
    o.append("| Input | Evidence | How it is used |")
    o.append("|---|---|---|")
    o.append(f"| Electricity price | [Ofgem](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026): the published 26.32p excludes VAT, which is removed only until 31 March 2027. With VAT it is {p['elec_unit']*1.05*100:.2f}p, so electricity costs {p['elec_unit']*1.05/p['gas_unit']:.2f} times as much as gas per kWh, not {p['elec_unit']/p['gas_unit']:.2f}. | 5% VAT is included for all {H} years. The holiday made permanent is a row in the drivers table. |")
    o.append(f"| Gas use | The government's [NEED dataset](https://www.gov.uk/government/statistics/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026-accessible-webpage) gives a 2024 median of 10,000 kWh and a mean of 11,200 kWh for all homes in England and Wales, and no figure for semi-detached homes. Ofgem's pricing convention is 9,500 kWh. | {p['gas_kwh']:,.0f} kWh, an estimate for a 3-bed semi between the median and the mean. Ofgem's 9,500 is used only for the bill check. |")
    o.append(f"| Replacement boiler cost | Published 2026 guides give £2,000-£3,500, with a median combi swap about £2,300 (commercial sources). | £{p['boiler_replace_cost']:,.0f}. |")
    o.append(f"| Heat pump net price | A secondary source citing Boiler Upgrade Scheme data gives a median installed price of about £13,000 before the grant, so about £5,500 net. At £5,500 net the heat-pump-tariff result would be {money(mk(hp_net_cost=5500), True)}. | {money(p['hp_net_cost'])}, the price you gave. Quotes will replace it. |")
    o.append("| Grant | [GOV.UK](https://www.gov.uk/government/news/heat-pump-grants-increased-by-50-per-cent): £7,500 for an air-source heat pump, scheme extended to 2028, no requirement to disconnect gas. | Keeping gas connected is an option and is a row in the drivers table. |")
    o.append("| Heat-pump tariff price | Octopus's published Cosy structure gives relative prices (table below) but no current unit rates. | 80% of the standard rate. |")
    o.append("| Heat pump efficiency (SCOP) | The Electrification of Heat median is 2.8 (interim). Household-level data was not available, so the spread is a judgement. | 3.0, varied in the simulation. It is the largest driver, so the installer's predicted figure matters most. |")
    o.append("| Future fuel prices | Cornwall Insight forecasts a January 2027 cap of about £1,999 (reported), with no electricity/gas split. | Both fuels rise 3% a year, varied in the simulation. It is the second-largest driver. |")
    o.append("| Cost of disconnecting gas | No source found. | Assumed free. |")
    o.append("")
    o.append("**What a heat-pump tariff really costs depends on when you use power.** Octopus Cosy's cheap rate is 49% of the day rate and its peak is 150%, with cheap windows 4-7am, 1-4pm and 10pm-midnight and peak 4-7pm:\n")
    o.append("| How the heat pump is run | Price as a share of the standard rate | Pence per kWh now |")
    o.append("|---|---|---|")
    uc = p["elec_unit"] * (1 + p["elec_vat"]) * 100
    for nm, ch, dy, pk in (("Left on all day with no shifting", 9/24, 12/24, 3/24),
                           ("Avoids 4-7pm, otherwise evenly spread", 9/21, 12/21, 0.0),
                           ("Avoids 4-7pm, 40% in cheap windows (assumed in the model)", 0.4, 0.6, 0.0),
                           ("Heavily shifted: 70% in cheap windows", 0.7, 0.3, 0.0)):
        fct = ch * 0.49 + dy + pk * 1.5
        o.append(f"| {nm} | {fct:.0%} | {fct*uc:.1f}p |")
    o.append("")
    o.append("## Assumptions and sources\n")
    o.append("`SOURCE` = taken from a cited source (some figures are still estimates). `ASSUMPTION` = my estimate; replace it if you know better.\n")
    o.append("| Input | Value | Type | Note |")
    o.append("|---|---|---|---|")
    for k, (_, lab, kind, note) in INPUTS.items():
        v = p[k]
        vs = f"{v:.2%}" if k in ("gas_inflation", "elec_inflation", "discount") else (f"{v:.0%}" if k in ("boiler_eff", "new_boiler_eff") else f"{v:.2f}" if k == "hp_tariff_factor" else f"{v:,}" if isinstance(v, int) else str(v))
        o.append(f"| {lab} | {vs} | {kind} | {note} |")
    o.append("""
**Sources and how far to trust them**

- Price cap: [Ofgem unit rates and standing charges](https://www.ofgem.gov.uk/node/176588/), average Direct Debit, Oct-Dec 2026 (electricity 26.32p/kWh + 54.83p/day; gas 7.97p/kWh + 29.68p/day). Official. Note the electricity rate excludes VAT, which is removed only until 31 March 2027; the model adds 5% back. These are averages across England, Scotland and Wales, not England-only, and the price cap changes every quarter.
- Typical use (9,500 kWh gas, 2,500 kWh electricity): Ofgem's 2026 review, as reported by [Energy UK](https://www.energy-uk.org.uk/wp-content/uploads/2026/05/Energy-UK-Explains-Typical-Domestic-Consumption-Values.pdf). I could not open Ofgem's own decision page, but these figures with the cap prices reproduce Ofgem's £1,723 typical bill to within £1 (see the check in the script output).
- Heat pump efficiency: [Electrification of Heat trial](https://es.catapult.org.uk/news/heat-pumps-shown-to-be-three-times-more-efficient-than-gas-boilers/) (Energy Systems Catapult), median seasonal efficiency 2.8 for air-source heat pumps. These are interim results from the 742-home trial; I did not find the final report. [Nesta](https://www.nesta.org.uk/report/how-to-make-heat-pumps-more-affordable/assumptions-and-methods/) assumes a baseline of 3 rising to 3.3. [Carbon Brief](https://www.carbonbrief.org/factcheck-what-it-really-costs-to-heat-a-home-in-the-uk-with-a-heat-pump) reports that the Heat Pump Monitor site shows about 3.9; the article doesn't say how those systems were recruited and the figure is defended by the site's co-founder, so I treated 3.9 as an upper case, not the typical one.
- Grant: [GOV.UK, Boiler Upgrade Scheme grants](https://www.gov.uk/government/news/heat-pump-grants-increased-by-50-per-cent): up to £7,500 for an air-source heat pump in England and Wales. The GOV.UK page says the scheme was extended to 2028; an installer blog says it was overhauled in April 2026 and runs longer, which I could not confirm. Check GOV.UK for the current end date. The £7,500 net cost is your figure.
- Heat-pump tariff: [Octopus Cosy](https://octopus.energy/smart/cosy-octopus/) publishes its structure (cheap rate 51% below the day rate, peak 50% above it, peak window 4-7pm) and [average rates](https://octopus.energy/press/Octopus-Energy-launches-new-off-peak-rate-for-heat-pump-customers/) (about 13p / 26p / 40p). The page doesn't state current unit rates, so I use only the ratios and assume the day rate is close to the standard rate. Check live rates for your region before relying on it.
- Running-cost parity check: [Nesta](https://www.nesta.org.uk/feature/energy-affordability/establish-price-ratio-target/) states that at a price ratio of 3.3 a heat pump with efficiency 2.8 costs the same to run as an 85%-efficient gas boiler; the self-test reproduces that.
- Not sourced at all: boiler and heat pump lifetimes, replacement boiler cost, service costs, future price rises.
""")
    o.append("## Plain-English glossary\n")
    o.append("- **SCOP / seasonal efficiency:** units of heat delivered per unit of electricity over a year. 3.0 means 1 kWh of electricity gives 3 kWh of heat. A gas boiler delivers about 0.85-0.9 kWh of heat per kWh of gas.")
    o.append("- **kWh:** the unit your meter and bills use for energy.")
    o.append("- **Standing charge:** a fixed daily fee for being connected. If you disconnect gas completely you stop paying the gas one, which is worth roughly £108 a year; the electricity one stays.")
    o.append("- **Price cap:** Ofgem's limit on the unit rates and standing charges suppliers can charge on standard tariffs. It is not a limit on your total bill.")
    o.append("- **Boiler Upgrade Scheme:** a government grant that comes off the installer's price.")
    o.append("- **Heat-pump tariff:** electricity that is cheap at certain times of day. It only helps if your heat pump and hot-water heating can run mostly in the cheap windows.")
    o.append("- **Simulation / draws:** the model is run 5,000 times, each time with every uncertain input nudged to a different plausible value (a 'draw'). The share of runs where the heat pump wins is a guide to how safe the verdict is.")
    o.append("- **Median:** the middle result when all the runs are lined up from worst to best.")
    o.append("- **Hot-water cylinder:** the insulated tank a heat pump needs to store hot water, replacing the combi boiler's instant hot water. It is usually part of the installed price.")
    o.append("- **SPF vs SCOP:** SPF is efficiency measured in a real home over a year; SCOP is the predicted figure for a design. Both mean units of heat per unit of electricity.")
    o.append("- **MCS / heat-loss calculation:** MCS is the certification scheme installers need for the grant. A heat-loss calculation is the room-by-room estimate of how much heat your house loses, which sizes the heat pump and predicts its SCOP.")
    o.append("- **Today's money:** future savings reduced slightly because £100 later is worth less than £100 now.\n")
    o.append("## Limits\n")
    o.append("- This is a model with typical inputs, not a survey of your house. An installer's heat-loss calculation gives a better efficiency estimate than the one used here.")
    o.append("- Not counted: higher home value, carbon savings, any radiator or pipework upgrades beyond the net price you gave, installation disruption, extra running cost of a hot-water cylinder, solar panels, and what happens if the grant ends.")
    o.append("- Electricity standing charge is the same in both cases, so it's left out.\n")
    o.append("## Re-run it\n")
    o.append("```")
    o.append("python3 heatpump_model.py --me --gas-kwh 12800 --scop 3.4 --price 8200   # your verdict from up to three numbers")
    o.append("python3 heatpump_model.py --me --gas-m3 1140 --price 8200               # meter in cubic metres; SCOP left typical")
    o.append("python3 heatpump_model.py --list                          # see every input")
    o.append("python3 heatpump_model.py --set gas_kwh=12000 --set scop=3.4   # try your own numbers")
    o.append("python3 heatpump_model.py --set gas_kwh=12000 --write heat-pump-vs-gas-boiler.md   # regenerate this file")
    o.append("python3 heatpump_model.py --check heat-pump-vs-gas-boiler.md   # confirm the file matches the model")
    o.append("python3 check_report.py heat-pump-vs-gas-boiler.md heatpump_model.py   # independent checks on the file")
    o.append("```\n")
    o.append("## Script output (verbatim)\n")
    o.append("```")
    o.append(text)
    o.append("```")
    return "\n".join(o) + "\n"


def parse(argv):
    p, mode, path, i, given = defaults(), "print", None, 0, set()
    while i < len(argv):
        a = argv[i]
        if a == "--set":
            k, _, v = argv[i + 1].partition("=")
            if k not in INPUTS: sys.exit(f"unknown input '{k}' (see --list)")
            p[k] = type(INPUTS[k][0])(float(v)) if not isinstance(INPUTS[k][0], float) else float(v)
            i += 2
        elif a == "--me":
            mode, i = "me", i + 1
        elif a in ("--gas-kwh", "--gas-m3", "--scop", "--price"):
            try: v = float(argv[i + 1])
            except (IndexError, ValueError): sys.exit(f"{a} needs a number")
            key = {"--gas-kwh": "gas_kwh", "--gas-m3": "gas_kwh", "--scop": "scop", "--price": "hp_net_cost"}[a]
            p[key] = v * GAS_M3_TO_KWH if a == "--gas-m3" else v
            given.add(key)
            i += 2
        elif a in ("--write", "--check"):
            mode, path, i = a[2:], argv[i + 1], i + 2
        elif a == "--list":
            for k, (v, lab, kind, _) in INPUTS.items(): print(f"{k:22s} {v!s:>8}  {lab} [{kind}]")
            sys.exit(0)
        else:
            sys.exit(__doc__)
    if given and mode != "me": sys.exit("--gas-kwh/--gas-m3/--scop/--price are for --me mode")
    if mode == "me" and not given: sys.exit("--me needs at least one of --gas-kwh (or --gas-m3), --scop, --price")
    return p, mode, path, given


if __name__ == "__main__":
    params, mode, path, given = parse(sys.argv[1:])
    validate(params)
    if mode == "me":
        print(me_summary(params, given))
    elif mode == "print":
        print(summary(params)[0])
    elif mode == "write":
        open(path, "w").write(report(params)); print(f"wrote {path}")
    else:
        ok = open(path).read() == report(params)
        print("OK: file matches the model" if ok else "MISMATCH: regenerate with --write (using the same --set options)")
        sys.exit(0 if ok else 1)
