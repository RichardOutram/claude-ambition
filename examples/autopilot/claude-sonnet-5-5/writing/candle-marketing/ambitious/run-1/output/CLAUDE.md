# Etsy candle shop marketing plan

`etsy-candle-marketing-plan.md` is the deliverable: a dated 24-week plan (Nov 16 2026 to Apr 2027) with a $3,000/month goal and a $6,000 stretch track.

## After you change any number in the plan

Run `plan-tools/run_checks.sh`. Both checks must pass:
- `check_plan.py` recomputes the funnel scenarios, weekly hours (each week must sum to its total and stay at 5.0 or less), the $150 budget, the margin and stretch tables, production quantities and every weekday+date pair.
- `judge.py` checks the plan against its promises (targets, 24 dated weeks, scorecard, kill-or-keep rule per tactic, estimates register) and table/link structure.

The one known judge FAIL line, "Competitor comparison has 5-10 shops", is expected: Etsy blocks reading its pages, so the plan ships a worksheet instead. Fill the worksheet with real shops, then update that promise in `judge.py`.

## Rules for editing the plan
- Keep every weekly table at 5.0 hours or less, with a `**Total**` row, and keep the must-do task first and `Weekly scorecard` as a row.
- Mark figures that come from the owner's description as estimates and list them in Section 11. Replace them with real Etsy stats when the owner has them.
- `.ambition/first/` holds the first version. Never edit it.
