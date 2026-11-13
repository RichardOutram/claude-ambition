"""Second attack: extend each published track's first segment BACKWARDS; the rays meet near home.
Roads curve, so heading at the cut point = departure heading + noise that grows with distance."""
import math, random
random.seed(21)
def lsq_intersection(rays):  # point minimising squared distance to all rays (p, unit direction d)
    a = b = c = e = f = 0.0
    for (px, py), (dx, dy) in rays:
        m11, m12, m22 = 1 - dx * dx, -dx * dy, 1 - dy * dy
        a += m11; b += m12; c += m22; e += m11 * px + m12 * py; f += m12 * px + m22 * py
    det = a * c - b * b
    return ((c * e - b * f) / det, (a * f - b * e) / det) if abs(det) > 1e-9 else (0, 0)

def trial(k, radius_fn, offset, curve):
    rays = []
    for _ in range(k):
        ang = random.uniform(0, 2 * math.pi) if random.random() < .5 else random.gauss(.8, .5)
        dx, dy = math.cos(ang), math.sin(ang)
        r = radius_fn()
        # cut where the ray from home leaves the circle of radius r centred at `offset`
        b = -(dx * offset[0] + dy * offset[1]); cc = offset[0] ** 2 + offset[1] ** 2 - r * r
        t = -b + math.sqrt(b * b - cc)
        h = ang + random.gauss(0, curve * math.sqrt(t / 200))  # observed heading at cut point
        rays.append(((t * dx, t * dy), (math.cos(h), math.sin(h))))
    x, y = lsq_intersection([((p[0], p[1]), (-d[0], -d[1])) for p, d in rays])
    return math.hypot(x, y)

for curve in (0.15, 0.4):
    print(f"road curvature noise {curve} rad per 200 m")
    for name, rf, off in (("A  R=200 fixed      ", lambda: 200, (0, 0)),
                          ("B  R=200..320 +offset", lambda: random.uniform(200, 320), (70, -50)),
                          ("C  R=400..640 +offset", lambda: random.uniform(400, 640), (140, -100))):
        for k in (5, 30):
            e = sorted(trial(k, rf, off, curve) for _ in range(400))
            print(f"   {name} rides={k:2d} median err {e[200]:6.0f} m   90th pct {e[360]:6.0f} m")
