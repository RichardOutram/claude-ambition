import random
random.seed(3)
def xp_for_level(n): return 0 if n <= 1 else round(60 * n ** 2)
def level(xp):
    n = 1
    while xp >= xp_for_level(n + 1): n += 1
    return n
def ride_xp(km, elev, first=False):
    return min(600, round(10 * km + 0.2 * elev)) + (300 if first else 0)
PERSONAS = {
  "commuter 5x8km":   lambda w: [(8, 40)] * 5,
  "weekend 60+25km":  lambda w: [(60, 600), (25, 150)],
  "casual 1x15km (70% of weeks)": lambda w: [(15, 80)] if random.random() < 0.7 else [],
  "keen 6x45km":      lambda w: [(45, 500)] * 6,
}
QUEST_WEEKLY = 100  # assume one quest completed per active week
for name, f in PERSONAS.items():
    xp, first, hit, active_streak = 0, True, {}, 0
    first_ride_level = None
    for w in range(1, 53):
        rides = f(w)
        if rides: active_streak += 1
        else: active_streak = 0
        wk = 0
        for km, el in rides:
            x = ride_xp(km * random.uniform(0.8, 1.2), el * random.uniform(0.7, 1.3), first)
            if first: first_ride_level = level(x)
            first = False; wk += x
        if wk > 1500: wk = 1500 + round(0.25 * (wk - 1500))
        if rides:
            wk += QUEST_WEEKLY
            wk = round(wk * (1 + 0.05 * min(5, active_streak - 1)))
        xp += wk
        for L in (3, 5, 10, 20, 30):
            if L not in hit and level(xp) >= L: hit[L] = w
    print(f"{name:32s} L-after-1st-ride={first_ride_level}  weeks-to {hit}  level@52w={level(xp)}  xp={xp}")
print("thresholds:", {n: xp_for_level(n) for n in (2, 3, 5, 10, 20, 30, 50)})
