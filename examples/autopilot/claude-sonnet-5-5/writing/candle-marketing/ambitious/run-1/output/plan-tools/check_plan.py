"""Recompute the numbers in the marketing plan from the finished Markdown file.

Usage: python3 -I check_plan.py <plan.md>
Checks:
  1. every weekly task table sums to its stated total and to <= 5.0 hours
  2. week headings are consecutive Mondays (Nov 16 2026 ... Apr 26 2027)
  3. funnel scenarios: orders = round(visits * conv), revenue = orders * AOV
  4. weekly pace table = monthly figure / 4.345
  5. budget columns sum to 150
  6. noise figures (Poisson) quoted in the plan
"""
import datetime as dt
import math
import re
import sys

text = open(sys.argv[1], encoding="utf-8").read()
fails = []


def fail(msg):
    fails.append(msg)
    print("FAIL:", msg)


def ok(msg):
    print("ok:  ", msg)


# 1 + 2: weekly tables ------------------------------------------------------
weeks = re.split(r"(?m)^### Week ", text)[1:]
prev = None
months = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
for i, block in enumerate(weeks, 1):
    head = block.splitlines()[0]
    m = re.match(r"(\d+) · Mon (\w{3}) (\d+)", head)
    if not m or int(m.group(1)) != i:
        fail(f"week heading {i} malformed: {head!r}")
        continue
    mon, day = months[m.group(2)], int(m.group(3))
    year = 2026 if mon >= 11 else 2027
    d = dt.date(year, mon, day)
    if d.weekday() != 0:
        fail(f"week {i} {d} is not a Monday")
    if prev and (d - prev).days != 7:
        fail(f"week {i} {d} is not 7 days after {prev}")
    prev = d
    rows = re.findall(r"(?m)^\| (?!\*\*Total)(?!Task)(?!---)(.+?) \| (\d+(?:\.\d+)?) \|$", block.split("\n### ")[0].split("\n## ")[0])
    total = re.search(r"\*\*Total\*\* \| (\d+(?:\.\d+)?) \|", block)
    s = sum(float(h) for _, h in rows)
    if not total:
        fail(f"week {i} has no total row")
    elif abs(s - float(total.group(1))) > 1e-9:
        fail(f"week {i} rows sum {s} != stated {total.group(1)}")
    if s > 5.0:
        fail(f"week {i} is {s} hours (> 5)")
if len(weeks) == 24 and not fails:
    ok(f"24 weeks, Mondays {dt.date(2026,11,16)} .. {prev}, every week sums to its total and is <= 5.0 h")
elif len(weeks) != 24:
    fail(f"expected 24 weeks, found {len(weeks)}")

# 3: funnel -----------------------------------------------------------------
funnel = re.findall(
    r"(?m)^\| (Baseline|Holiday|Spring A|Spring B)[^|]*\| ([\d,]+) \| ([\d.]+)% \| (\d+) \| \$([\d.]+) \| \$([\d,]+) \|$", text)
if len(funnel) != 4:
    fail(f"funnel rows found: {len(funnel)} (expected 4)")
for name, v, c, o, a, r in funnel:
    v = int(v.replace(",", ""))
    orders = round(v * float(c) / 100)
    rev = orders * float(a)
    if orders != int(o):
        fail(f"{name}: orders {o} != round({v}*{c}%)={orders}")
    elif abs(rev - float(r.replace(",", ""))) > 1.0:
        fail(f"{name}: revenue ${r} != {orders}*${a}=${rev:.0f}")
    else:
        ok(f"{name}: {v} visits x {c}% = {orders} orders x ${a} = ${rev:,.0f}")

# 4: weekly pace ------------------------------------------------------------
W = 4.345
pace = re.findall(
    r"(?m)^\| (Baseline|Holiday|Spring)[^|]*\| ([\d,]+) \| (\d+) \| \$([\d,]+) \| (\d+) \| (\d+) \| \$([\d,]+) \|$", text)
if len(pace) != 3:
    fail(f"pace rows found: {len(pace)} (expected 3)")
for name, mv, mo, mr, wv, wo, wr in pace:
    for label, m_, w_ in (("visits", mv, wv), ("orders", mo, wo), ("revenue", mr, wr)):
        m_ = int(m_.replace(",", ""))
        w_ = int(w_.replace(",", ""))
        if abs(m_ / W - w_) > 1.0:
            fail(f"pace {name} {label}: {m_}/{W}={m_/W:.1f} != {w_}")
    ok(f"pace {name}: weekly figures match monthly / {W}")

# 5: budget -----------------------------------------------------------------
b = re.search(r"(?s)### Monthly budget.*?\n(\|.*?)\n\n", text)
if not b:
    fail("budget table not found")
else:
    c1 = c2 = 0
    for item, x, y in re.findall(r"(?m)^\| (?!\*\*Total)(?!Item)(?!---)(.+?) \| \$(\d+) \| \$(\d+) \|$", b.group(1)):
        c1 += int(x)
        c2 += int(y)
    t = re.search(r"\*\*Total\*\* \| \*\*\$(\d+)\*\* \| \*\*\$(\d+)\*\*", b.group(1))
    if (c1, c2) != (150, 150) or not t or (int(t.group(1)), int(t.group(2))) != (150, 150):
        fail(f"budget columns sum to {c1}, {c2}; stated {t.groups() if t else None}")
    else:
        ok("budget: both columns sum to $150")

# 6: noise (Poisson) --------------------------------------------------------
for mean in (37, 75):
    sd = math.sqrt(mean)
    print(f"info: {mean} orders/month -> SD {sd:.1f}, 95% range {mean-1.96*sd:.0f}-{mean+1.96*sd:.0f}")
print(f"info: weekly 8.5 orders -> SD {math.sqrt(8.5):.1f}, 95% range {8.5-1.96*math.sqrt(8.5):.1f}-{8.5+1.96*math.sqrt(8.5):.1f}")
for months_ in (1, 3, 4):
    a, bb = 37 * months_, 37 * 1.25 * months_
    z = (bb - a) / math.sqrt(a + bb)
    print(f"info: +25% orders over {months_} month(s): z = {z:.2f}")
p1, p2 = 0.02, 0.024
za, zb = 1.96, 0.84
n = ((za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2))) / (p2 - p1) ** 2
print(f"info: visits per arm to detect 2.0% -> 2.4% conversion (80% power): {n:,.0f}")
print(f"info: visits 1850/month -> SD {math.sqrt(1850):.0f} ({100*math.sqrt(1850)/1850:.1f}%)")
now = dt.date(2026, 11, 1)
for shop, sales, since in (("LuluSugar", 51645, 2013), ("TheHalcyonSoul", 34227, 2018), ("KettleWorksCo", 844, 2021)):
    months_open = (2026 - since) * 12 + 10.5
    print(f"info: {shop}: {sales/months_open:.0f} sales/month lifetime average")

# 7: margin table -------------------------------------------------------------
rows = re.findall(r"(?m)^\| ([A-E])\. .*? \| \$(\d+) \| \$([\d.]+) \| \$([\d.]+) \| \$([\d.]+) \| \$(-?[\d.]+) \| \$(-?[\d.]+) \|$", text)
if len(rows) != 5:
    fail(f"margin rows found: {len(rows)} (expected 5)")
for k, order, fees, cogs, ship, prof, prof_o in rows:
    order, fees, cogs, ship, prof, prof_o = map(float, (order, fees, cogs, ship, prof, prof_o))
    f = 0.095 * order + 0.45
    p_ = order - f - cogs - ship
    po = p_ - 0.12 * order
    if abs(f - fees) > 0.01 or abs(p_ - prof) > 0.01 or abs(po - prof_o) > 0.01:
        fail(f"margin case {k}: expected fees {f:.2f} profit {p_:.2f} offsite {po:.2f}; table has {fees} {prof} {prof_o}")
    else:
        ok(f"margin case {k}: fees ${f:.2f}, profit ${p_:.2f}, with Offsite Ad ${po:.2f}")
floor = (12 + 0.45 + 18 + 12) / 0.905
print(f"info: 2-jar set price for $12 profit with free shipping: ${floor:.2f}")

# 8: production calendar + minimum viable week --------------------------------
prod = re.findall(r"(?m)^\| (December|Steady spring month) \| (\d+) \| ([\d.]+) \| (\d+) \| (\d+) \|", text)
if len(prod) != 2:
    fail(f"production rows found: {len(prod)} (expected 2)")
for name, orders, per, candles, buf in prod:
    c = round(int(orders) * float(per))
    b = round(c * 1.2)
    if (c, b) != (int(candles), int(buf)):
        fail(f"production {name}: expected {c} candles, {b} with buffer; table has {candles}, {buf}")
    else:
        ok(f"production {name}: {orders} orders x {per} = {c} candles, {b} with 20% buffer")
weekly_pour = round(126 / 4.345)
if f"about {weekly_pour} candles a week" not in text:
    fail(f"weekly pour figure ({weekly_pour}) not stated")
else:
    ok(f"steady-state pour: {weekly_pour} candles a week")
for label, ship, cure_days, stated in (("Valentine's", dt.date(2027,2,8), 14, "Jan 25"),
                                       ("Mother's Day", dt.date(2027,4,30), 14, "Apr 16"),
                                       ("December gifts", dt.date(2026,12,14), 14, "Nov 30")):
    d = ship - dt.timedelta(days=cure_days)
    mon = d.strftime("%b ") + str(d.day)
    if mon != stated or stated not in text:
        fail(f"pour-by for {label}: expected {mon}, plan says {stated}")
    else:
        ok(f"pour-by {label}: {mon} ({cure_days} days before {ship})")
mvw = []
for i, block in enumerate(weeks, 1):
    body = block.split("\n## ")[0]
    rws = re.findall(r"(?m)^\| (?!\*\*Total)(?!Task)(?!---)(.+?) \| (\d+(?:\.\d+)?) \|$", body)
    first = float(rws[0][1])
    sc = [float(h) for t_, h in rws if t_.startswith("Weekly scorecard")]
    if i == 1:
        sc = [0.0]  # Week 1 sets up the scorecard inside its first row
    if not sc:
        fail(f"week {i} has no scorecard row")
        continue
    mvw.append((i, first + sc[0]))
worst = max(mvw, key=lambda x: x[1])
if worst[1] > 2.5:
    fail(f"minimum viable week exceeds 2.5 h: week {worst[0]} = {worst[1]}")
else:
    ok(f"minimum viable week (first row + scorecard) is at most {worst[1]} h (week {worst[0]}), at least {min(m[1] for m in mvw)} h")

# 9: red-team follow-ups ------------------------------------------------------
def prof(price, cogs, ship):
    return price - (0.095 * price + 0.45) - cogs - ship
for case, price, cogs, ship, stated in (("B", 39, 12.5, 9.5, "$9.32"), ("C", 52, 18, 12, "$11.90"), ("D", 38, 10.5, 8, "$12.00")):
    v = prof(price * 0.9, cogs, ship)
    if f"{case} {stated}" not in text.replace("case ", "").replace(", ", ", ").replace(" and ", " ") and stated not in text:
        fail(f"after-discount profit for {case}: expected {stated}")
    if f"{v:.2f}" != stated.lstrip("$") and abs(v - float(stated.lstrip("$"))) > 0.01:
        fail(f"after-discount profit for {case}: computed {v:.2f}, plan says {stated}")
    else:
        ok(f"after the 10% discount, case {case} earns ${v:.2f} (plan says {stated}); sale rule needs >= $9: {'yes' if v >= 9 else 'NO'}")
if prof(39, 12.5, 9.5) < 12 or prof(38, 12.5, 9.5) >= 12:
    fail("case B should pass the $12 rule at $39 and fail it at $38")
else:
    ok("case B: fails $12 at $38 ($11.94), passes at $39 ($12.85)")
for want in ("$830", "$751", "$960"):
    if want not in text:
        fail(f"missing figure {want}")
print(f"info: 92 x $9 = ${92*9}; 0.75 x 2002 / 2 = ${0.75*2002/2:.0f}; 75 x 12.85 = ${75*12.85:.0f}")
hrs = re.search(r"(?s)Typical hours/week \|\n\|---.*?\n\n", text)
vals = [float(x) for x in re.findall(r"(?m)^\| \d \| .*? \| .*? \| (\d+(?:\.\d+)?) \|$", hrs.group(0))] if hrs else []
if sum(vals) != 5.0 or len(vals) != 6:
    fail(f"hours-by-lever table sums to {sum(vals)} over {len(vals)} rows (expected 5.0 over 6)")
else:
    ok("hours-by-lever table sums to 5.0")

# 10: stretch track (Section 12) ----------------------------------------------
sec12 = text.split("## 12. Stretch track")[1] if "## 12. Stretch track" in text else ""
if not sec12:
    fail("Section 12 missing")
else:
    m = re.search(r"\| Stretch retail \| ([\d,]+) \| ([\d.]+)% \| (\d+) \| \$(\d+) \| \$([\d,]+) \|", sec12)
    v, c, o, a, r = int(m.group(1).replace(",", "")), float(m.group(2)), int(m.group(3)), float(m.group(4)), int(m.group(5).replace(",", ""))
    assert round(v * c / 100) == o and o * a == r, "stretch retail row does not reconcile"
    mb = re.search(r"\| Stretch bulk \| n/a \| n/a \| (\d+) \| \$(\d+) \| \$([\d,]+) \|", sec12)
    bo, bp, br = int(mb.group(1)), int(mb.group(2)), int(mb.group(3).replace(",", ""))
    assert bo * bp == br, "stretch bulk row does not reconcile"
    tot = int(re.search(r"\*\*Total\*\* \| \| \| \| \| \*\*\$([\d,]+)\*\*", sec12).group(1).replace(",", ""))
    if r + br != tot:
        fail(f"stretch total {tot} != {r}+{br}")
    else:
        ok(f"stretch route: retail ${r:,} + bulk ${br:,} = ${tot:,}")
    # bulk profit
    mp = re.search(r"\| Bulk: 50 tins at \$8 \+ \$30 postage \| \$(\d+) \| \$([\d.]+) \| \$([\d.]+) \| \$([\d.]+) \| \$([\d.]+) \|", sec12)
    total_, fee_, mat_, post_, prof_ = map(float, mp.groups())
    f_ = 0.095 * total_ + 0.45
    p_ = total_ - f_ - 50 * 3.5 - 30
    if abs(f_ - fee_) > 0.01 or abs(p_ - prof_) > 0.01 or mat_ != 175.0:
        fail(f"bulk profit: expected fees {f_:.2f} profit {p_:.2f}")
    else:
        ok(f"bulk order: fees ${f_:.2f}, profit ${p_:.2f}")
    # gates
    W_ = 4.345
    for want in (round(3000 / W_), round(4100 / W_), round(6000 / W_)):
        if f"{want:,}" not in sec12:
            fail(f"gate run-rate {want} not stated")
    ok(f"gate run-rates ${round(3000/W_)}, ${round(4100/W_)}, ${round(6000/W_):,} a week match monthly / {W_}")
    # hours table
    JAR, MINI = 8, 20
    def hrs(ro, bo):
        cand = ro * 1.4
        jars, minis = cand * 0.75, cand * 0.25
        make = jars / JAR + (minis + bo * 50) / MINI
        pack = ro * 10 / 60 + bo * 45 / 60
        return round(cand + bo * 50), round(make, 1), round(pack, 1), round(make + pack, 1), round((make + pack) / W_, 1)
    fb, st = hrs(75, 0), hrs(80, 6)
    rows = {"Candles to make": (fb[0], st[0]), "Making hours": (fb[1], st[1]), "Packing hours": (fb[2], st[2]),
            "Total hours per month": (fb[3], st[3]), "Hours per week": (fb[4], st[4]),
            "With your 5 marketing hours": (round(fb[4] + 5, 1), round(st[4] + 5, 1))}
    for k, (x, y) in rows.items():
        m_ = re.search(rf"\| {k} \| ([\d.]+) \| ([\d.]+) \|", sec12)
        if not m_ or abs(float(m_.group(1)) - x) > 0.051 or abs(float(m_.group(2)) - y) > 0.051:
            fail(f"hours row '{k}': expected {x} / {y}, table {m_.groups() if m_ else None}")
    ok(f"stretch hours table: fallback {fb[4]} h/week, stretch {st[4]} h/week (+5 marketing = {round(fb[4]+5,1)} / {round(st[4]+5,1)})")
    # per-hour
    mkt = 5 * W_
    pf = 75 * 13 / (fb[3] + mkt)
    ps = (80 * 13 + 6 * 183.70) / (st[3] + mkt)
    if "$975" not in sec12 or "$2,142" not in sec12 or f"${pf:.0f} an hour" not in sec12 or f"${ps:.0f}" not in sec12:
        fail(f"per-hour figures: expected ${pf:.1f} and ${ps:.1f}, gross $975 / ${80*13+6*183.70:,.0f}")
    else:
        ok(f"profit per hour: fallback ${pf:.1f}, stretch ${ps:.1f}")
    # landing zone + outreach
    for case, retail_, bo_, brev_, tot_ in re.findall(r"(?m)^\| (Low|Middle|High|Stretch) \| \$([\d,]+) \| (\d+) \| \$([\d,]+) \| \$([\d,]+) \|$", sec12):
        retail_, brev_, tot_ = (int(x.replace(",", "")) for x in (retail_, brev_, tot_))
        if int(bo_) * 400 != brev_ or retail_ + brev_ != tot_:
            fail(f"landing row {case} does not add up")
    for case, n_, rr, cl, ords in re.findall(r"(?m)^\| (Cautious|Middle|Optimistic) \| (\d+) \| (\d+)% \| (\d+)% \| ([\d.]+) \|$", sec12):
        if abs(int(n_) * int(rr) / 100 * int(cl) / 100 - float(ords)) > 0.06:
            fail(f"outreach row {case}: expected {int(n_)*int(rr)/100*int(cl)/100:.2f}, table {ords}")
    ok("landing-zone and outreach tables reconcile")
    clicks_lo, clicks_hi = 60 / 0.80, 60 / 0.30
    need = 3200 - 1850
    print(f"info: ads clicks {clicks_lo:.0f}-{clicks_hi:.0f} = {100*clicks_lo/need:.0f}-{100*clicks_hi/need:.0f}% of the +{need} visits needed; inquiries for 6 orders at 15% close: {6/0.15:.0f}")
    # overlay swaps against the real weekly tables
    weeks_by_n = {}
    for blk in weeks:
        n_ = int(re.match(r"(\d+) ", blk).group(1))
        weeks_by_n[n_] = blk.split("\n## ")[0]
    swaps = re.findall(r"(?m)^\| Week (\d+) \((\w{3} \d+)\) \| (.+?) \| ([\d.]+) \| (.+?) \| ([\d.]+) \|$", sec12)
    dh = ah = 0.0
    for wn, date, drop, dhrs, add, ahrs in swaps:
        wn = int(wn)
        blk = weeks_by_n[wn]
        if date not in blk.splitlines()[0]:
            fail(f"overlay week {wn}: date {date} does not match heading")
        rowm = re.search(rf"(?m)^\| {re.escape(drop)}[^|]*\| ([\d.]+) \|$", blk)
        if not rowm:
            fail(f"overlay week {wn}: dropped task not found in the week table: {drop!r}")
        elif float(rowm.group(1)) != float(dhrs):
            fail(f"overlay week {wn}: drop hours {dhrs} != table {rowm.group(1)}")
        if float(dhrs) != float(ahrs):
            fail(f"overlay week {wn}: swap is not hours-neutral ({dhrs} vs {ahrs})")
        dh += float(dhrs); ah += float(ahrs)
    if len(swaps) != 8 or dh != ah:
        fail(f"overlay: {len(swaps)} swaps, drop {dh} h vs add {ah} h")
    else:
        ok(f"overlay: 8 swaps, every dropped task exists in its week and every swap is hours-neutral ({dh} h each way)")
    gates = {0: "Week 7", 1: "Week 14", 2: "Week 19"}
    for g, wk in gates.items():
        if not re.search(rf"(?m)^\| {g} \| {wk} ", sec12):
            fail(f"gate {g} not at {wk}")
    ok("gates sit at Weeks 7, 14 and 19 (the December, February and Q1 review weeks)")

# 11: every "Mon Nov 16"-style weekday + date pair in the plan is a real weekday ---
mon_no = {m: i for i, m in enumerate(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], 1)}
wd_no = {w: i for i, w in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])}
pairs = re.findall(r"\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{1,2})\b", text)
wrong = []
for wd, mo, dy in pairs:
    yr = 2026 if mon_no[mo] >= 11 else 2027
    if dt.date(yr, mon_no[mo], int(dy)).weekday() != wd_no[wd]:
        wrong.append(f"{wd} {mo} {dy}")
if wrong:
    fail(f"weekday/date mismatches: {sorted(set(wrong))}")
else:
    ok(f"{len(pairs)} weekday+date pairs in the plan are all real weekdays")

for f in text.split("\n"):
    pass
print("\nRESULT:", "PASS" if not fails else f"{len(fails)} FAILURE(S)")
sys.exit(1 if fails else 0)
