// Pure analysis of a GPS log. No Expo imports so it can be tested with plain node.
export type Pt = { t: number; lat: number; lon: number; acc: number; speed: number; recvAt: number };

export const GAP_S = 20; // a gap longer than this while moving counts as dropout
export const MOVING_MS = 2; // m/s, short segments
export const GAP_MOVING_MS = 1; // m/s average displacement that makes a long gap a dropout

export function haversine(a: Pt, b: Pt): number {
  const R = 6371000, rad = Math.PI / 180;
  const dLat = (b.lat - a.lat) * rad, dLon = (b.lon - a.lon) * rad;
  const s = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * rad) * Math.cos(b.lat * rad) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(s));
}

export function analyze(points: Pt[]) {
  const p = [...points].sort((x, y) => x.t - y.t);
  let distance = 0, moving = 0, dropout = 0, longestMovingGap = 0;
  const gaps: { atIso: string; seconds: number }[] = [];
  const delays: number[] = [];
  for (let i = 0; i < p.length; i++) {
    if (p[i].recvAt) delays.push((p[i].recvAt - p[i].t) / 1000);
    if (i === 0) continue;
    const dt = (p[i].t - p[i - 1].t) / 1000;
    if (dt <= 0) continue;
    const d = haversine(p[i - 1], p[i]);
    distance += d;
    // Short segments: trust the reported speed. Long gaps: judge by straight-line displacement,
    // because a stop (no movement) and a dropout while riding (large displacement) look the same
    // by the speed reported at either end.
    const reported = Math.max(p[i - 1].speed, p[i].speed); // -1 when unknown
    const sp = dt > GAP_S ? d / dt : reported >= 0 ? reported : d / dt;
    if (sp > (dt > GAP_S ? GAP_MOVING_MS : MOVING_MS)) {
      moving += dt;
      if (dt > GAP_S) {
        dropout += dt;
        gaps.push({ atIso: new Date(p[i - 1].t).toISOString(), seconds: Math.round(dt) });
      }
      longestMovingGap = Math.max(longestMovingGap, dt > GAP_S ? dt : 0);
    }
  }
  delays.sort((a, b) => a - b);
  const pct = (q: number) => (delays.length ? delays[Math.min(delays.length - 1, Math.floor(q * delays.length))] : 0);
  return {
    points: p.length,
    durationMin: p.length > 1 ? (p[p.length - 1].t - p[0].t) / 60000 : 0,
    distanceKm: distance / 1000,
    movingMin: moving / 60,
    dropoutPct: moving > 0 ? (100 * dropout) / moving : 0,
    longestMovingGapS: Math.round(longestMovingGap),
    gaps: gaps.slice(0, 20),
    deliveryDelayP95S: Math.round(pct(0.95)),
    // PASS criteria 1 from the plan (distance and battery are checked by hand).
    passGaps: moving > 0 && (100 * dropout) / moving < 2 && longestMovingGap <= 60,
  };
}
