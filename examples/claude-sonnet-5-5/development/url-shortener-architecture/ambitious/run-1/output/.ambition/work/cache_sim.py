"""Zipf cache simulation (pure Python, no deps): python3 cache_sim.py
Links ranked 1..N, P(rank k) ~ 1/k^s. Reports hit rate of
 (a) ideal static cache holding the top-C links (upper bound), and
 (b) a real LRU, simulated with random requests.
"""
import bisect, itertools, random
from collections import OrderedDict

def cdf(n, s):
    w = [1 / k**s for k in range(1, n + 1)]
    tot = sum(w)
    return [x / tot for x in itertools.accumulate(w)]

N = 1_000_000          # catalog size simulated (scale-invariant in C/N)
REQS = 1_000_000
random.seed(1)
print(f"catalog N={N:,}; cache sized as % of catalog")
print(f"{'s':>5} {'cache%':>7} {'ideal':>7} {'LRU':>7}")
for s in (0.6, 0.8, 1.0, 1.2):
    c = cdf(N, s)
    for pct in (0.1, 1, 5, 20):
        C = int(N * pct / 100)
        ideal = c[C - 1]
        lru, hits = OrderedDict(), 0
        for _ in range(REQS):
            k = bisect.bisect_left(c, random.random())
            if k in lru:
                hits += 1
                lru.move_to_end(k)
            else:
                lru[k] = 1
                if len(lru) > C:
                    lru.popitem(last=False)
        print(f"{s:>5} {pct:>6}% {ideal:>7.1%} {hits/REQS:>7.1%}")
