I pushed the animation further in `<workspace>/solar-implosion.html`. I haven't opened it in a browser, so none of it has been run or checked visually. A script applied the edits, and the only check I ran was a `grep` confirming the new post-processing import is in the file.

**What's new**
- **Density:** the sun and planets have more particles. A spiral galaxy of dust arms (40k particles) now wraps the system. The total is roughly 190k particles.
- **Comets:** 14 comets follow tilted orbits. Each has a white-hot head and a long fading tail.
- **Colour cycling:** hues drift across the loop and shift with distance from the centre. The loop still repeats exactly every 10 seconds.
- **Afterimage trails:** motion leaves glowing streaks behind it.
- **Chromatic aberration and vignette:** the colour split intensifies at the implosion peak.
- **Shockwave rings:** two colour-shifting rings expand through the system after the burst.
- **Click shockwave:** pressing the pointer also sends a ripple through the particles from the cursor. Holding still pulls them in as before.

If it runs slowly, lowering the particle counts (the sun's 30000 and the galaxy's 40000) is the easiest fix. I'd also reduce the bloom strength if the centre blows out to white.