"""ID scheme checks: python3 id_check.py"""
import hashlib, math, random

ALPHA = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEY = b"demo-secret"
HALF = 20                      # 2 x 20 bits = 40-bit domain (1.1e12 < 62^7)
MASK = (1 << HALF) - 1

def f(x, r):
    h = hashlib.blake2b(x.to_bytes(3, "big") + bytes([r]), key=KEY, digest_size=3)
    return int.from_bytes(h.digest(), "big") & MASK

def enc(n):
    l, r = n >> HALF, n & MASK
    for i in range(4):
        l, r = r, l ^ f(r, i)
    return (l << HALF) | r

def dec(n):
    l, r = n >> HALF, n & MASK
    for i in reversed(range(4)):
        l, r = r ^ f(l, i), l
    return (l << HALF) | r

def b62(n):
    s = ""
    while n:
        n, d = divmod(n, 62)
        s = ALPHA[d] + s
    return s.rjust(7, "0")

# 1. Feistel is a bijection: sequential IDs -> unique codes, invertible
N = 2_000_000
codes = set()
for i in range(N):
    e = enc(i)
    assert dec(e) == i
    codes.add(b62(e))
print(f"1. {N:,} sequential IDs -> {len(codes):,} unique 7-char codes (collisions: {N-len(codes)}), all invertible")
print(f"   domain 2^40={2**40:.2e} <= 62^7={62**7:.2e}: max code length {len(b62(2**40-1))}")
print(f"   sample codes for IDs 1..5: {[b62(enc(i)) for i in range(1, 6)]}")

# 2. Random-code + retry: expected extra attempts as the table fills
SPACE = 62**7
print("2. random 7-char code, retry on conflict:")
for filled in (1e9, 3e9, 1e10, 1e11):
    p = filled / SPACE
    print(f"   {filled:.0e} links stored: P(collision)={p:.3%}, expected attempts={1/(1-p):.4f}")

# 3. Truncated hash of URL (birthday bound) for comparison
for bits_chars in (7,):
    n = 3e9
    p = 1 - math.exp(-n * (n - 1) / (2 * SPACE))
    print(f"3. hash-truncate to 7 chars, {n:.0e} links: P(at least one collision)={p:.4f} (certain); "
          f"per-insert collision rate ~{n/SPACE:.3%}")

# 4. Enumeration: chance a random guess hits a live link
print(f"4. random guess hits a live link with p={3e9/SPACE:.4%} at 3e9 links "
      f"(unscrambled sequential codes: guessable at p=1 by incrementing)")
