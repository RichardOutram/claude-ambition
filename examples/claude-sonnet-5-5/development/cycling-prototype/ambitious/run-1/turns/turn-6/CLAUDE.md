# Cycling app prototype
`prototype.html` is a single-file clickable prototype of `plan.md` (open it in a browser; no build). `rider-test-script.md` is the script for sessions with riders.

**After any edit to prototype.html run `sh checks/run.sh`** (first time: `cd checks && npm install`; needs Chrome, override with `CHROME=`). It must print ALL CHECKS PASSED. See `checks/README.md` for what each script proves. Run `sh checks/run.sh ../prototype.html fuzz` before handing it to riders.

Keep: one file, no network; every tap does something; tap targets 44 px+; check at 375x667. Numbers (8 XP/km, 500 XP/level, prices) are placeholders, not from plan.md.

## Open decisions (owner: you)
- Real XP / level / pricing values: keep placeholders until riders have used it. Decide by 2026-11-27.
- Freeze tokens are earned by completing a challenge (plan.md doesn't say how): confirm or change by 2026-11-20.
- Pro vs free club boundary: watch in rider sessions; decide by 2026-11-27.
- Next check: run 3-5 rider sessions with `rider-test-script.md` and read the Session log, by 2026-11-20.
