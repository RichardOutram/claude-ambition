I built it as a single page, **`<workspace>/index.html`**. Open it in a browser; it loads three.js from a CDN, so it needs an internet connection.

I checked it in headless Chrome by taking screenshots at specific moments in the loop and with simulated mouse input. I haven't watched it run in real time, so I haven't confirmed how smooth it is on real hardware.

**The 10-second loop:**
- **0–3.4s, the solar system:** A white-hot sun and seven neon planets (cyan, magenta, lime, orange, a violet ringed giant, blue and red) orbit inside glowing trails of orbit dust. There's also a violet/cyan asteroid belt, an outer nebula halo and twinkling stars.
- **3.4–6.8s, the implosion:** Everything spirals inward, speeding up and shifting toward hot pink and white. The system flattens into a churning disc, a colour-cycling neon ring shrinks in from the edges, and the camera moves in.
- **About 7.15s, the collapse:** All matter reaches a point, then a bright flash with camera shake.
- **7.15–10s, the explosion:** Matter bursts outward, overshoots a little, and settles back into orbit. Two neon shockwave rings spread out at different tilts.

The loop is seamless because every motion repeats exactly every 10 seconds, so the last frame matches the first. The progress bar in the bottom-left tracks the cycle.

**Mouse and touch:**
- **Moving the pointer** pushes particles aside and swirls them in a glowing wake, and tilts the camera slightly toward the pointer.
- **Holding the button down** turns the pointer into a gravity well that pulls nearby matter into a vortex around it.

The motion is calculated on the graphics card for about 120,000 particles. Glow and faint motion trails are added on top.

To check a single moment, add `?t=` with a fraction of the loop to the address, for example `index.html?t=0.715` to freeze on the collapse flash.