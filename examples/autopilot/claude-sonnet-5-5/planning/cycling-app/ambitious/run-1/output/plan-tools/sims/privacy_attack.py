"""Red team: can an attacker recover a rider's home from the *published* (privacy-truncated) tracks?
Attack: every published track starts where it leaves the privacy circle. Those cut points lie on a
circle of known radius around home -> fit the circle centre (least squares)."""
import math, random
random.seed(11)
R_PUBLIC = 200.0  # default zone radius (metres)

def fit_center(points, radius):
    # Gauss-Newton on sum (|p-c| - radius)^2, starting at the centroid of the cut points shifted inward
    cx = sum(p[0] for p in points) / len(points); cy = sum(p[1] for p in points) / len(points)
    for _ in range(60):
        jtj = [[0, 0], [0, 0]]; jtr = [0, 0]
        for x, y in points:
            dx, dy = cx - x, cy - y; d = math.hypot(dx, dy) or 1e-9
            r = d - radius; jx, jy = dx / d, dy / d
            jtj[0][0] += jx * jx; jtj[0][1] += jx * jy; jtj[1][1] += jy * jy
            jtr[0] += jx * r; jtr[1] += jy * r
        jtj[1][0] = jtj[0][1]
        det = jtj[0][0] * jtj[1][1] - jtj[0][1] ** 2
        if abs(det) < 1e-9: break
        cx -= (jtj[1][1] * jtr[0] - jtj[0][1] * jtr[1]) / det
        cy -= (-jtj[1][0] * jtr[0] + jtj[0][0] * jtr[1]) / det
    return cx, cy

def rides(n, publish):
    """Return the published cut points for n rides leaving home (0,0) in random directions."""
    cuts = []
    for _ in range(n):
        ang = random.uniform(0, 2 * math.pi) if random.random() < 0.5 else random.gauss(0.8, 0.5)  # favourite roads
        cuts.append(publish(ang))
    return cuts

# Defence A (current plan): fixed centre, fixed radius
fixed = lambda ang: (R_PUBLIC * math.cos(ang), R_PUBLIC * math.sin(ang))
# Defence B: secret per-user centre offset (up to 0.6R) + per-ride radius jitter (R..1.6R); attacker knows R only
OFF = (random.uniform(-1, 1), random.uniform(-1, 1)); n = math.hypot(*OFF); OFFV = (0.6 * R_PUBLIC * OFF[0] / n * random.random(), 0.6 * R_PUBLIC * OFF[1] / n * random.random())
def jittered(ang):
    r = R_PUBLIC * random.uniform(1.0, 1.6)  # circle around the secret centre; cut where the ride leaves it
    # ride leaves home along direction ang; intersect ray from home with circle centred at OFFV radius r
    dx, dy = math.cos(ang), math.sin(ang); b = -(dx * OFFV[0] + dy * OFFV[1]); c = OFFV[0] ** 2 + OFFV[1] ** 2 - r * r
    t = -b + math.sqrt(b * b - c)
    return (t * dx, t * dy)

for name, f in (("A fixed centre+radius", fixed), ("B secret offset + radius jitter", jittered)):
    for k in (3, 5, 10, 30):
        errs = []
        for _ in range(300):
            pts = rides(k, f)
            cx, cy = fit_center(pts, R_PUBLIC)
            errs.append(math.hypot(cx, cy))
        errs.sort()
        print(f"{name:34s} rides={k:2d}  median error {errs[len(errs)//2]:7.1f} m   90th pct {errs[int(.9*len(errs))]:7.1f} m")
