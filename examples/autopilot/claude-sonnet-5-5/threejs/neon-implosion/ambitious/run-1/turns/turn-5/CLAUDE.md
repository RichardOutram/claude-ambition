# solar-implosion.html

Single-file three.js page (three@0.160 from unpkg): neon solar system that implodes and rebirths in a seamless 10 s loop; the pointer is a gravity well with a fading trail; click sends a shockwave.

- Check after any edit: `cd check && npm install && npm run check` (18 checks, ~5 min, needs Chrome). `npm run frames` writes a 10-frame contact sheet to `.ambition/shots/now.png`; look at it, since the check cannot see blocky bloom or garish colour.
- URL hooks for tests: `?still` (no pointer, no adaptive quality), `?q=1.5` (particle multiplier). Page opens at loop time `T0` (8.7 s); the check reads it from the file.
- Proof so far: 18/18 checks pass. Same measurements on the first version: whiteout in 32/100 frames (new: 1), saturation 0.16 (0.28), 0 shockwave hue bins (6), trail light +3.8 (+11.9).
- Rejected on evidence: quarter-resolution bloom (blocky halos) and 1.5x particles (washes colour). Do not retry without a new bloom approach.
- Never edit `.ambition/first/` or `.ambition/steps/*`.
