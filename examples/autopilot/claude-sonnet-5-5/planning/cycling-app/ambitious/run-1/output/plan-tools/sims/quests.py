"""Game designer: do fixed weekly quests work for every rider, or only for some?
Weekly distributions are invented personas (same as xp_sim), so this tests the DESIGN, not real users."""
import random, statistics
random.seed(5)
P = {  # (rides/wk mean, km per ride mean, climb m per ride mean)
 "city commuter (flat)": (5, 8, 15), "casual weekender": (1.5, 18, 120),
 "weekend hill rider": (2, 45, 650), "keen club rider": (5, 45, 450)}
FIXED = {"ride 3 days": lambda w: w["days"] >= 3, "50 km total": lambda w: w["km"] >= 50, "climb 800 m": lambda w: w["climb"] >= 800}
def week(p):
    r, km, cl = p; n = max(0, round(random.gauss(r, 1)))
    return {"days": min(7, n), "km": sum(max(2, random.gauss(km, km * .3)) for _ in range(n)), "climb": sum(max(0, random.gauss(cl, cl * .4)) for _ in range(n))}
print("FIXED quests - weekly completion rate")
for name, p in P.items():
    ws = [week(p) for _ in range(2000)]
    print(f"  {name:22s}", {q: f"{100*sum(f(w) for w in ws)/len(ws):3.0f}%" for q, f in FIXED.items()})
print("PERSONALISED quests - target = 110% of the user's trailing 4-week median (floor: days>=2)")
for name, p in P.items():
    hist = [week(p) for _ in range(4)]; ok = {"days": 0, "km": 0, "climb": 0}; N = 2000
    for _ in range(N):
        w = week(p)
        tgt = {k: max(1.1 * statistics.median(h[k] for h in hist), 2 if k == "days" else 0) for k in ok}
        for k in ok: ok[k] += w[k] >= tgt[k]
        hist = hist[1:] + [w]
    print(f"  {name:22s}", {k: f"{100*v/N:3.0f}%" for k, v in ok.items()})
