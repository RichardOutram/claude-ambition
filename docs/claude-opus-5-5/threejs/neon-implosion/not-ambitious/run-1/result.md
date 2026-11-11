I built the animation as one HTML file: **`<workspace>/neon-solar-implosion.html`**. Open it in a browser. It loads three.js from a CDN, so it needs an internet connection.

The JavaScript passes a syntax check, but there was no browser here to run it, so I haven't actually watched it play. The particle sizes, flash brightness and timing are set from calculation and may need tuning once you see it.

**What happens in each 10-second loop:**

| Time | Phase | What you see |
|---|---|---|
| 0–1.6s | **Orbit** | A neon sun made of about 18,000 particles, 8 glowing planets on orbit trails, an asteroid belt, and a ringed planet. The camera drifts slowly. |
| 1.6–5.75s | **Collapse** | All particles spiral inward, flattening into a disk and heating up to white-hot. The camera pushes in and the bloom glow builds. |
| 5.75–7s | **Detonation** | A blinding flash, three shockwave rings (cyan, magenta and yellow) at different angles, and some camera shake. The particles blow out into a nebula that shifts between magenta and cyan. |
| 7–10s | **Rebirth** | The particles curl back into their exact orbits, so the loop restarts without a visible jump. |

**How it works:**
- About 108,000 particles are moved entirely by a vertex shader. Each particle's position is calculated from where it is in the 10-second cycle, so every loop plays identically.
- Each planet completes a whole number of orbits per loop. The camera, glow, flash and twinkle values all start and end at the same value, so nothing jumps when the loop restarts.
- The glow comes from additive blending plus a bloom effect that gets stronger during the collapse and the explosion.
- A small label at the bottom shows the current phase, with a progress bar.