# Ferrofluid Zoetrope

`ferrofluid-zoetrope.html` is the whole piece: a single page that loads three.js r128 from cdnjs.

## Check it before shipping any change
`cd check && npm install && npm test` (needs Google Chrome; set `CHROME_PATH` if it isn't at the macOS default).
It renders the page in headless Chrome on a virtual clock and runs 23 pass/fail checks. Exit code 0 means all passed.
`node check/accept.js --sheet sheet.png` also writes a contact sheet of 12 desktop frames and 3 phone frames. Look at it: the checks don't judge beauty.

Checks that must keep passing:
- frame 30 and frame 150 are pixel-identical (seamless 10 s loop), including after pointer use
- WCAG 2.3.1: per-region luminance steps < 0.1, at most 3 flashes/s; reduced motion → no flicker
- render p50 ≤ 16 ms at 1280×800@2, 1920×1080@2, 2560×1440@2, 390×844@3
- a tap steers the magnet; vertical swipes still scroll (`touch-action: pan-y`)

Timings from a VM GPU are a stand-in. Confirm on real hardware.
