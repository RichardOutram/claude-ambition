"""Challenge checks. usage: python3 -I challenge_checks.py <hourly.json> <hourA.gz>
 C1 peak:average from a week of real hourly totals
 C2 hot-key share from a real trace vs DynamoDB per-partition read limit
 C3 read:write sensitivity
 C4 how often random base62 codes spell dictionary words"""
import gzip, json, random, sys

# C1
v = [i["views"] for i in json.load(open(sys.argv[1]))["items"]]
print(f"C1 {len(v)} hourly totals: peak/mean = {max(v)/(sum(v)/len(v)):.2f}, min/mean = {min(v)/(sum(v)/len(v)):.2f}")

# C2
c = {}
with gzip.open(sys.argv[2], "rt", encoding="utf-8", errors="replace") as f:
    for line in f:
        p = line.split(" ")
        if len(p) >= 3 and p[0] == "en" and p[2].isdigit():
            c[p[1]] = c.get(p[1], 0) + int(p[2])
cnt = sorted(c.values(), reverse=True); tot = sum(cnt)
RPS = 9901; PART = 6000      # 3,000 RRU/partition / 0.5 per eventually-consistent 4KB read
for k in (1, 10, 100):
    sh = sum(cnt[:k]) / tot
    print(f"C2 top-{k} pages carry {sh:.2%} of views -> at {RPS:,} redirects/s the hottest key sees ~{cnt[0]/tot*RPS:,.0f}/s"
          if k == 1 else f"C2 top-{k} pages carry {sh:.2%} of views")
print(f"   per-partition ceiling ~{PART:,} reads/s (eventually consistent). Hot key needs {PART/RPS:.0%} of all traffic to hit it.")

# C3
print("C3 read:write  writes/s(peak)  avg writes/s  links in 5y  storage 5y @500B")
for r in (10, 14, 50, 100, 1000):
    w = 10000 / (r + 1); a = w / 3
    n = a * 86400 * 365 * 5
    print(f"   {r:>5}:1 {w:>14,.0f} {a:>13,.0f} {n/1e9:>11.1f}B {n*500/1e12:>9.1f} TB  keyspace used {n/62**7:.2%}")

# C4
words = {w.strip().lower() for w in open("/usr/share/dict/words") if w.strip().isalpha() and len(w.strip()) >= 4}
A = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
random.seed(7); N = 200_000; hit = 0
for _ in range(N):
    s = "".join(random.choice(A) for _ in range(7)).lower()
    if any(s[i:i+L] in words for L in (4, 5, 6, 7) for i in range(0, 8 - L)): hit += 1
print(f"C4 {hit/N:.2%} of random 7-char codes contain a 4+ letter dictionary word ({len(words):,} words); "
      f"share of codes with look-alike chars (0 O o 1 l I): {1-(56/62)**7:.1%}")
