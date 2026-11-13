import { analyze } from './src/analyze.ts';
import assert from 'node:assert/strict';

// Straight ride east at 5 m/s, a point every 5 s, 0.00005 deg lon ~ 5.57 m at lat 0 -> ~1.1 m/s per... use 0.00023 deg ~ 25 m per 5 s.
const mk = (n, skip = []) => {
  const pts = [];
  for (let i = 0; i < n; i++) {
    if (skip.includes(i)) continue;
    pts.push({ t: 1_000_000 + i * 5000, lat: 0, lon: i * 0.000225, acc: 5, speed: 5, recvAt: 1_000_000 + i * 5000 + 1000 });
  }
  return pts;
};
const clean = analyze(mk(600));
assert.ok(clean.passGaps && clean.dropoutPct === 0, 'clean ride should pass');
assert.ok(Math.abs(clean.distanceKm - 599 * 0.025) / (599 * 0.025) < 0.01, 'distance within 1%');

const gappy = analyze(mk(600, [100, 101, 102, 103, 104])); // 30 s hole while moving
assert.ok(gappy.passGaps && gappy.gaps.length === 1 && gappy.longestMovingGapS === 30, '30 s hole is reported but within tolerance (<2%, <=60 s)');
const bad = analyze(mk(600, Array.from({ length: 17 }, (_, i) => 100 + i))); // 90 s hole
assert.ok(!bad.passGaps && bad.longestMovingGapS === 90, '90 s hole must fail');

// Stationary stop: 3 minutes of no points at speed 0 must NOT count as dropout.
const stop = mk(100);
stop.forEach(p => (p.speed = 0));
const mixed = [...mk(100), ...mk(100).map(p => ({ ...p, t: p.t + 100 * 5000 + 180000, lon: 99 * 0.000225, speed: 0 }))];
mixed.push({ ...mixed[99], t: mixed[99].t + 180000, speed: 0 }); // rider stays put 3 min
assert.equal(analyze(mixed).gaps.length, 0, 'a stop must not be a dropout');
console.log('analyze: all tests passed', { clean: clean.distanceKm.toFixed(2) + ' km', gappyDropout: gappy.dropoutPct.toFixed(2) + '%' });
