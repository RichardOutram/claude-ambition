"""Stretch: what changes at 100k req/s peak? python3 stretch_checks.py"""
import math
PEAK, RATIO, P2A = 100_000, 100, 3
reads = PEAK * RATIO / (RATIO + 1); writes = PEAK - reads
avg_w = writes / P2A; yr = avg_w * 86400 * 365; n5 = yr * 5
print(f"S1 reads={reads:,.0f}/s writes={writes:,.0f}/s | avg writes {avg_w:,.0f}/s -> {yr/1e9:.1f}B/yr, {n5/1e9:.0f}B in 5y, "
      f"{n5*500/1e12:.0f} TB (peak case {writes*86400*365*5*500/1e12:.0f} TB) | key space used {n5/62**7:.2%}, "
      f"collision/insert at {n5/1e9:.0f}B = {n5/62**7:.2%}")
QUOTA, RRU = 40_000, 0.5
need = reads * RRU
print(f"S2 DB at 100% miss: {need:,.0f} read units/s vs default table quota {QUOTA:,} -> {need/QUOTA:.0%} of quota")
for target in (0.7, 1.0):
    h = max(0, 1 - (QUOTA * target) / need)
    print(f"   to stay under {target:.0%} of the default quota the cache must hit >= {h:.0%}")
print(f"S3 Redis at {reads:,.0f} ops/s vs ~72k (docs, non-pipelined): single instance = {reads/72_000:.0%} of that reference; "
      f"3 shards -> {reads/3:,.0f} ops/s each = {reads/3/72_000:.0%}")
for per, label in ((5_000, "floor 5k/s"), (15_000, "bare path 15k/s")):
    n = math.ceil(reads / (per * 0.6))
    print(f"S4 Redirect instances at 60% CPU target, {label}: {n}; with 1 of 3 AZs lost: {math.ceil(n * 3 / 2)}")
for lat, name in ((0.005, "hit 5 ms"), (0.030, "miss 30 ms")):
    print(f"S5 in flight, {name}: {reads*lat:,.0f} concurrent")
top1 = 0.0374
print(f"S6 hottest key at trace-like skew: {reads*top1:,.0f} reads/s vs ~6,000/s partition ceiling = {reads*top1/6000:.0%}")
print(f"S7 click events: {reads:,.0f}/s x 200 B = {reads*200/1e6:.0f} MB/s; sampling 1-in-10 -> {reads/10:,.0f} events/s")
