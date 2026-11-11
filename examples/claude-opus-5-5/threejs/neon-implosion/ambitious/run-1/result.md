The animation is finished: **`<workspace>/final/index.html`**, a single page that loads three.js from a CDN, so it needs internet. Open it in a browser. Space pauses it, and adding `?t=6.05` (or any time) to the address freezes it on that moment.

An outside judge compared it with the first version without being told which was which, and it passed on every criterion twice. It still has a few small flaws, listed below.

**What it does:** about 250,000 neon particles make up a sun, 8 planets with orbit lines, an asteroid belt and dust.
- **0–3 s:** the system orbits normally.
- **3–5.6 s:** everything spirals into the sun.
- **5.6–6 s:** the swirl contracts and the scene dims.
- **6 s:** it collapses to a pinpoint and a cyan starburst fires.
- **After 6 s:** shockwave rings spread out and the planets reform before the loop restarts.

**Compared with the first version** (`.ambition/direct/index.html`, left unchanged):
- **Colour:** the background is now true black instead of purple-grey haze, and the colours stay fully saturated. Before, bright areas washed out to white; now only the flash itself goes white.
- **Planets:** they keep their own colours (lime, orange, cyan, blue) as they streak into the sun. Before, they turned into white smears.
- **The collapse:** the 6 s moment is now a sharp pinpoint and starburst, where before it was a screen-filling white bloom.
- **The rebuild:** from 7.5 to 8.5 s the planets come back as coloured bodies instead of muddy haze.
- **Kept:** same particle count, same timeline, same shockwave rings, and the loop still has no visible jump.
- **Gave up:** nothing the judge could find.

**Checks:**
- The judge rendered its own frames at about 20 moments for both versions in headless Chromium and looked at them.
- The first and last frames differ by 1.5 out of 255 on average (target 3 or less; the first version was 2.2).
- There are no console errors on desktop or on a phone-sized portrait screen.
- I haven't measured the frame rate on a real graphics card, because the headless browser renders in software.

**Remaining flaws, all brief:**
- Around 4.5–5 s, the outer swirl brushes the frame edges.
- At about 6.3 s, two planets smear into flat-looking teal and blue shapes for around 0.3 s.
- Around 7.5 s, the planets nearest the camera are soft and a little cropped.

**I didn't attempt** a harder version, such as a guaranteed 60 fps on a phone or an exported video file. Nor did I make a reusable script or command for repeat runs. I can do any of those if you want.

**Assumptions I made:** it's an art piece to share or watch on repeat, desktop is the main screen and phones should also work, and loading three.js from a CDN is fine.

**Other files** are in `<workspace>/.ambition/`:
- `shots/`: frame-by-frame screenshots of both versions, with a contact sheet for each.
- `tools/shoot.mjs`: the screenshot script, so you can re-render frames.
- `judgeview/`: the judge's contact sheets.