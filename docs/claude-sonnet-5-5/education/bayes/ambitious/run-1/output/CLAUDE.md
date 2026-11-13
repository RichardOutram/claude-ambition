# Bayes explainer

`bayes.html` is one self-contained page (no network, no build). Edit it directly; open it in a browser.

**Check after any change:** `./bayes-check/run.sh` (~3 min; needs Node 22+ and Chrome, set `CHROME=` if not at the macOS default). It runs, against real Chrome:
- the page's maths vs exact fractions over 4,096 slider settings plus real screening cases (`check.mjs`)
- typing, keys, clicks, presets, hover (`drive.mjs`); hostile input, URL injection, all corners, spoiler gating (`red.mjs`)
- bar width (`barw.mjs`); "Play it for me" reaches the answer in <= 12.5 s and every manual action cancels it (`play.mjs`)
- `judge.mjs` (only if `.ambition/first/bayes.html` exists): same measures on the first version vs now, including WCAG contrast in light and dark.

Rules the tests encode: the answer must not show before step 4; `MODEL-START/END` in the script is what `check.mjs` extracts, so keep the maths there; dot counts must never contradict the headline % (`resolve()` zooms out for rare cases).

Not covered: Safari/Firefox, real beginners, clinical review of the safety note.
