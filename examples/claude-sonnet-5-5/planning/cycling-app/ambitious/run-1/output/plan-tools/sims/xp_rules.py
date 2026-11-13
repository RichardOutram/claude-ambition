"""XP and level rules exactly as specified in plan section 6, plus the 52-week persona simulation.
Run: python3 -I xp_rules.py   (prints worked examples, then per-persona results)."""
import random

CAP_WEEK, CAP_RATE, RIDE_CAP, FIRST_BONUS, QUEST_XP = 1500, 0.25, 600, 300, 100
STREAK_STEP, STREAK_MAX_WEEKS = 0.05, 5  # +5% per previous consecutive active week, max +25%

def xp_for_level(n): return 0 if n <= 1 else round(60 * n ** 2)
def level(xp):
    n = 1
    while xp >= xp_for_level(n + 1): n += 1
    return n
def ride_base(km, elev_m): return min(RIDE_CAP, round(10 * km + 0.2 * elev_m))

def award(base, week_raw_so_far, prior_streak_weeks, first_ride=False):
    """XP awarded for one counted ride. Order: base -> weekly soft cap -> streak bonus -> first-ride bonus."""
    room = max(0, CAP_WEEK - week_raw_so_far)
    capped = min(base, room) + CAP_RATE * max(0, base - room)
    mult = 1 + STREAK_STEP * min(STREAK_MAX_WEEKS, prior_streak_weeks)
    return round(capped * mult) + (FIRST_BONUS if first_ride else 0)

def examples():
    ex = []
    b = ride_base(8, 40); a = award(b, 0, 0, True); ex.append(("1 first ever ride, 8 km / 40 m", b, a, level(a)))
    b = ride_base(60, 600); a = award(b, 0, 0); ex.append(("2 long hilly ride, 60 km / 600 m (per-ride cap)", b, a, None))
    a = award(600, 1200, 0); ex.append(("3 third 600-XP ride in a week (1,200 already earned)", 600, a, None))
    b = ride_base(25, 150); a = award(b, 0, 3); ex.append(("4 25 km / 150 m in the 4th active week (+15%)", b, a, None))
    ex.append(("5 quest completed (flat, no cap, no bonus)", QUEST_XP, QUEST_XP, None))
    return ex

PERSONAS = {
    "commuter 5x8km": lambda: [(8, 40)] * 5,
    "weekend 60+25km": lambda: [(60, 600), (25, 150)],
    "casual 1x15km (70% of weeks)": lambda: [(15, 80)] if random.random() < 0.7 else [],
    "keen 6x45km": lambda: [(45, 500)] * 6,
}

def simulate(seed=3):
    random.seed(seed); out = {}
    for name, f in PERSONAS.items():
        xp, first, streak, raw_total_hit = 0, True, 0, {}
        l_after_first = None
        for w in range(1, 53):
            rides = f(); raw, wk = 0, 0
            for km, el in rides:
                base = ride_base(km * random.uniform(0.8, 1.2), el * random.uniform(0.7, 1.3))
                a = award(base, raw, streak, first)
                if first: l_after_first = level(a)
                first = False; raw += base; wk += a
            if rides: wk += QUEST_XP; streak += 1
            else: streak = 0
            xp += wk
        out[name] = (l_after_first, level(xp), xp)
    return out

if __name__ == "__main__":
    print("WORKED EXAMPLES (base, awarded, level)")
    for e in examples(): print("  ", e)
    print("thresholds", {n: xp_for_level(n) for n in (2, 3, 5, 10, 20, 30, 50)})
    print("SIMULATION 52 weeks (level after ride 1, level at 52 w, total xp)")
    for k, v in simulate().items(): print(f"  {k:32s}", v)
