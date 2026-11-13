# Prototype checks
`sh checks/run.sh` runs everything against `prototype.html` (add `fuzz` as the second argument for the ~4 min random-action fuzz).

| Script | What it proves |
|---|---|
| flow | cold-start core loop: sign in, record, XP and badge, challenge |
| core, primary | same loop at 375x667; primary = tapping only the most prominent button reaches the challenge in 5 taps |
| consistency | displayed numbers agree (avg speed, XP breakdown sums, segment rank) |
| probe, fixes | reward edge cases (instant finish, challenge completion, level-up, streak card) and the former dead taps |
| redteam | markup injection, overflow, discard / privacy-zone / paywall guards, sign-out mid-ride, session log |
| depth | axe-core WCAG A/AA, 44 px tap targets, overflow at 375x667 |
| audit | every control on every screen changes something (15 benign re-tap hits) |
| corpus | all 44 MVP items from plan.md appear; text of every screen written to /tmp for a cold read |
| fuzz | seeded random taps, hostile text, resizes and full rides; invariants on XP, challenges, layout |

Fuzz limit: it catches uncapped counters and XP decreases, but its rides are too short to test the km and elevation challenge caps.
