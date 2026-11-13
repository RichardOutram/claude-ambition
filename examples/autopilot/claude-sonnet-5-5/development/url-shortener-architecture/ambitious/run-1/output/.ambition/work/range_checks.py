"""Range checks: python3 range_checks.py
 R1 availability budget  R2 queueing/Little's law  R3 guessing exposure  R4 hashed-IP reversibility"""
import hashlib, time

# R1: 99.95% monthly availability budget
SLO = 0.9995
print(f"R1 99.95% over 30 days = {30*24*60*(1-SLO):.1f} min downtime budget")
for n in (3, 4, 5, 6):
    print(f"   {n} hard serial dependencies -> each needs >= {SLO**(1/n):.5f} ({30*24*60*(1-SLO**(1/n)):.1f} min/month each)")
print(f"   same 6 dependencies each at 99.9%: product = {0.999**6:.5f} -> {30*24*60*(1-0.999**6):.0f} min/month")

# R2: Little's law and M/M/1 queueing factor
R = 9901
for name, lat, frac in (("cache-hit path (5 ms budget)", 0.005, 1.0), ("DB-miss path, 100% miss (30 ms)", 0.030, 1.0),
                        ("DB-miss path, 60% miss (30 ms)", 0.030, 0.6)):
    print(f"R2 {name}: in flight = {R*frac:,.0f}/s x {lat*1000:.0f} ms = {R*frac*lat:,.0f} concurrent")
for rho in (0.5, 0.6, 0.7, 0.8, 0.9):
    print(f"   utilisation {rho:.0%}: mean queueing delay = {rho/(1-rho):.1f} x service time")

# R3: guessing exposure at 3B live links, attacker at 10,000 guesses/s (distributed)
LIVE, G = 3e9, 10_000
for chars, alpha in ((7, 62), (8, 62), (11, 62)):
    p = LIVE / alpha**chars
    print(f"R3 {chars}-char codes: P(guess hits a live link)={p:.3e}; at {G:,} guesses/s -> {G*p:.4f} links/s, {G*p*86400:,.0f} links/day")

# R4: how long does it take to reverse an unsalted SHA-256 of an IPv4 address?
N = 300_000; t = time.time()
for i in range(N):
    hashlib.sha256(b"%d.%d.%d.%d" % (i >> 24 & 255, i >> 16 & 255, i >> 8 & 255, i & 255)).digest()
rate = N / (time.time() - t)
print(f"R4 pure-Python SHA-256: {rate:,.0f} hashes/s -> all 2^32 IPv4 addresses in {2**32/rate/3600:.1f} h on one core "
      f"(a GPU does billions/s: seconds)")
