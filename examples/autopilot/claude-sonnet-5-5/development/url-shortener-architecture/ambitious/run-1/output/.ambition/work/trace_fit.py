"""Fit Zipf exponent and measure hour-to-hour working-set stability on a real
request-popularity trace (Wikimedia hourly pageviews, en.wikipedia desktop+mobile).
usage: python3 -I trace_fit.py <hourA.gz> <hourB.gz>"""
import gzip, math, sys

def load(path):
    c = {}
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            p = line.split(" ")
            if len(p) >= 3 and p[0] == "en" and p[2].isdigit():   # domain code "en" = en.wikipedia desktop
                c[p[1]] = c.get(p[1], 0) + int(p[2])
    return c

a, b = load(sys.argv[1]), load(sys.argv[2])
cnt = sorted(a.values(), reverse=True)
tot = sum(cnt)
print(f"hour A: {len(cnt):,} distinct pages, {tot:,} views")

# Least-squares slope of log(freq) vs log(rank), over rank windows
def slope(lo, hi):
    xs = [math.log(r) for r in range(lo, min(hi, len(cnt)))]
    ys = [math.log(cnt[r - 1]) for r in range(lo, min(hi, len(cnt)))]
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    return -sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
for lo, hi in ((1, 100), (100, 10_000), (10_000, 100_000), (1, 100_000)):
    print(f"zipf exponent, ranks {lo:,}-{hi:,}: s={slope(lo, hi):.2f}")

# Ideal static cache hit rate = share of views on top-C pages (computed on the empirical counts)
cum = 0; marks = {}
for i, v in enumerate(cnt, 1):
    cum += v
    marks[i] = cum / tot
for pct in (0.1, 1, 5, 20):
    C = max(1, int(len(cnt) * pct / 100))
    print(f"top {pct}% of pages ({C:,}) carry {marks[C]:.1%} of views")

# Stability: cache filled with hour A's top-C, serving hour B's traffic (cold start excluded)
top = sorted(a, key=a.get, reverse=True)
tb = sum(b.values())
for pct in (0.1, 1, 5):
    C = max(1, int(len(a) * pct / 100))
    s = set(top[:C])
    hit = sum(v for k, v in b.items() if k in s) / tb
    print(f"cache = hour A's top {pct}% ({C:,}); hit rate on hour B = {hit:.1%}")
