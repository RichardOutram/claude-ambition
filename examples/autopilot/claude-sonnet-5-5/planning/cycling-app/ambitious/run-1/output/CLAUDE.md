# Project notes

`PLAN.md` is the build blueprint for the cycling app (Expo + Supabase). Tools live in `plan-tools/`; the GPS spike is in `spike-gps/`.

- **After editing PLAN.md, run:** `python3 -I plan-tools/plan_lint.py PLAN.md` (exit 0 = all checks pass). It recomputes costs, schedule, XP examples, quest and privacy figures from code, and checks tickets (order, prerequisites, sizes, acceptance criteria), cross-references and the release calculator.
- **Proof the lint can fail:** `python3 -I plan-tools/lint_selftest.py` (baseline passes, 6 deliberate breakages are caught). Last run: 49/49 checks, 6/6 breakages caught.
- **Ticket format is machine-read:** keep `### T-nnn · Title`, `Depends:`, `Size: Nd` and a `- AC:` line. Releases in §8b use `Include/Resize/Unlink/Link` lines.
- **Spike analyzer test:** `cd spike-gps && node --experimental-strip-types test-analyze.mjs`. The spike app itself has not been built or run on a device; recording reliability is unverified until `PLAN.md` §10's results table is filled.
- Pricing figures are dated 2026-11-13; re-fetch before committing budget (next check C3 in §11).
