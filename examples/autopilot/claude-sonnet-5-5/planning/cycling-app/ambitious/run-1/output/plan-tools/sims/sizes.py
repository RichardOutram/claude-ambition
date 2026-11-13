import json, gzip, math, random
random.seed(7)
# 60 min at ~6 m/s with the spike's 10 m distance filter -> a point about every 10 m
pts, lat, lon, hdg, alt, t = [], 52.0, 4.0, 0.0, 10.0, 1_700_000_000_000
for i in range(2160):
    hdg += random.gauss(0, 0.05)
    lat += 10 * math.cos(hdg) / 111_320
    lon += 10 * math.sin(hdg) / (111_320 * math.cos(math.radians(lat)))
    alt += random.gauss(0, 0.4)
    t += int(random.gauss(1700, 250))
    pts.append(dict(t=t, lat=round(lat, 7), lon=round(lon, 7), alt=round(alt, 1), speed=round(random.gauss(6, 1), 2), acc=round(random.uniform(3, 9), 1)))
raw = json.dumps(pts, separators=(",", ":")).encode()
print("points", len(pts), "raw json KB", len(raw) // 1024, "gzip KB", len(gzip.compress(raw)) // 1024)
# compact columnar + delta-coded ints before gzip
cols = []
pl = pts[0]
for p in pts:
    cols.append((round((p["lat"] - pl["lat"]) * 1e7), round((p["lon"] - pl["lon"]) * 1e7), p["t"] - pl["t"], round(p["alt"] * 10), round(p["speed"] * 100), round(p["acc"] * 10)))
    pl = p
cb = json.dumps(cols, separators=(",", ":")).encode()
print("delta-coded gzip KB", len(gzip.compress(cb)) // 1024)
# simplified polyline (Douglas-Peucker 5 m) encoded
def dp(a, eps):
    if len(a) < 3: return a
    ax, ay, bx, by = a[0][0], a[0][1], a[-1][0], a[-1][1]
    dmax, idx = 0, 0
    for i in range(1, len(a) - 1):
        x, y = a[i]
        d = abs((by - ay) * x - (bx - ax) * y + bx * ay - by * ax) / (math.hypot(by - ay, bx - ax) or 1e-9)
        if d > dmax: dmax, idx = d, i
    if dmax > eps: return dp(a[:idx + 1], eps)[:-1] + dp(a[idx:], eps)
    return [a[0], a[-1]]
xy = [((p["lon"] - pts[0]["lon"]) * 111_320 * math.cos(math.radians(52)), (p["lat"] - pts[0]["lat"]) * 111_320) for p in pts]
s = dp(xy, 5)
def enc(vals):
    out, prev = "", 0
    for v in vals:
        v = round(v * 1e5); d = v - prev; prev = v; d = ~(d << 1) if d < 0 else d << 1
        while d >= 0x20: out += chr((0x20 | (d & 0x1f)) + 63); d >>= 5
        out += chr(d + 63)
    return out
poly = enc([(pts[0]["lat"] if False else 0)])  # placeholder to keep function used
simp_ll = [(pts[0]["lat"] + y / 111_320, pts[0]["lon"] + x / (111_320 * math.cos(math.radians(52)))) for x, y in s]
flat = []
for la, lo in simp_ll: flat += [la, lo]
print("simplified points", len(s), "of", len(pts), "polyline bytes ~", len(enc(flat)))
