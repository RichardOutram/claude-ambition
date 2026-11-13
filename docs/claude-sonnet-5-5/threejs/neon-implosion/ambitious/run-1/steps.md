| Step | What it did | New or changed in the work |
|---|---|---|
| 1 · First version | Plain Claude's page, unseen. | A three.js page with about 90,000 particles. It was never looked at, and the implosion was a white blob for about 2.5 s. |
| 2 · Altitude | Asked three questions. The stand-in ranked: the collapse and rebirth first, then the pointer, first impression and performance. | Nothing in the page. It set the goal: a showcase people replay. |
| 3 · Depth | Rebuilt the loop as an animator would (anticipation, impact, follow-through), rendering frames to look at. | **Added:** a detonation with a flash and camera kick; a rainbow shockwave; a gravity-well pointer with a fading trail; click shockwaves; a ghost pointer until you move yours; ACES grading; particle count scaled to the device. **Found and fixed** the whiteout (three render-and-look rounds). Built capture, contact-sheet and seam tools. 537 → 1,047 words. |
| 4 · Challenge | Tested five assumptions against the real page. | **Found** the climax was a third the size on a desktop or Retina screen (sized in raw pixels), and the camera framing broke on tall phones. Both fixed. |
| 5 · Range | Borrowed from a colourist, a game-feel designer and sound design, plus a red team. | **Added:** a white-hot core with a violet halo, a cursor ripple, touch wording, a reduced-motion mode, and a clear message if three.js or WebGL fails. **Found** a near-white full-screen strobe (5% to 98% brightness in two frames) and softened it. Sound was considered and not built. |
| 6 · Judge | Built an 18-point check that renders the page in Chrome and scores each promise against the first version. | **Fixed** hint contrast (3.8:1 to 11.4:1), washed-out colour and a dull opening frame. Whiteout frames 32 → 1; saturation 0.15 → 0.28. |
| 7 · Stretch | Aimed for 3× the particles at the same frame cost. | **Missed and reverted.** It measured where the time goes; quarter-resolution bloom saved 20% but looked blocky, which only looking at the frames showed. |
| 8 · Lock | Report, plus `npm run check` to re-run the 18 checks. | The check is left in the project. |

**Value added:** the plain page was never looked at, and the method found its main failure (the whiteout). The rest is real polish and robustness. Range added the reduced-motion mode and the strobe fix.
