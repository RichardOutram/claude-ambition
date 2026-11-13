p = 'PLAN.md'
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:70]
    s = s.replace(old, new)

rep("A spike app is at `/Volumes/My Shared Files/work/spike-gps/` (see its README).", "A spike app is in `spike-gps/` (see its README).")
rep("""- **Dependency check:** `python3 -I "/Volumes/My Shared Files/work/plan-tools/check_tickets.py" /cfg/plans/make-a-plan-for-jaunty-wren.md` — exits non-zero on cycles, unknown prerequisites, or tickets listed before their prerequisites.""",
    """- **Whole plan:** `python3 -I plan-tools/plan_lint.py PLAN.md` runs every check below plus the ticket checker (`plan-tools/check_tickets.py`: cycles, unknown or late prerequisites, missing sizes or acceptance criteria) and the release calculator (`plan-tools/releases.py`). It exits non-zero on any failure. `python3 -I plan-tools/lint_selftest.py` proves the lint can fail.""")
rep("the fixed-centre, fixed-radius zone first drafted here was recovered to **0.0 m** from just 3 published rides by fitting a circle to the cut points (`plan-tools/sims/privacy_attack.py`). Shipped design:",
    "a fixed-centre, fixed-radius zone is recovered to **0.0 m** from just 3 published rides by fitting a circle to the cut points (`plan-tools/sims/privacy_attack.py`), so it is not used. The design is:")
rep("The first draft (`100·n^1.5`, no cap) put a keen rider at L167 and a commuter at L1 after ride 1, so it was dropped. The riders are assumptions, not user data.",
    "The common alternative `100·n^1.5` without a cap puts a keen rider at L167 and a commuter at L1 after ride 1, so it is not used. The rider types are assumptions, not user data.")
rep("figure is my assumption, not data.", "figure is an assumption, not data.")
rep("The sizes are my estimates (dev-days incl. tests);", "The sizes are estimates (dev-days incl. tests);")
rep("not re-fetched; you have no paid Apple account yet, needed before TestFlight", "not re-fetched; no paid Apple account exists yet and it is needed before TestFlight")
rep("The page did not cover organization accounts — check which account type you will use.", "Google's page does not cover organization accounts — check which account type the team will use.")

i = s.index("## 11. Open items")
s = s[:i] + """## 11. Open decisions and next checks
Dates assume day 1 is Monday **2026-11-23** and shift one-for-one if it moves. Owners are roles; put names against them at kickoff.

### Decisions
| # | Decision | Options (for / against) | Pick | Owner | Decide by |
|---|---|---|---|---|---|
| D1 | Team size | **3 devs:** S1 in 5.0 wk, S2 in 11.0 wk, full v1 in 12.7 wk (cheaper, lower burn) / **4 devs:** S1 in 4.0 wk, S2 in 8.3 wk, with zero margin (faster, extra salary, S1 still fragile) | 3 devs, commit to S1 at 5 weeks and S2 at 11; add a fourth only if a launch date is fixed | Product owner | 2026-11-20 |
| D2 | Release shape | **S1 → S2 → v1.1** (riders and the Play clock start early; S2 has no push) / **one full v1** (everything at once; 13 weeks to any user, Play gate last) | S1 → S2; push notifications are the first v1.1 item | Product owner | 2026-11-20 |
| D3 | Account type for Play and Apple | **Personal:** quick, but needs 12 testers for 14 days / **Organization:** rule not documented on the page read, may need company verification | Whatever exists today; if personal, recruit the 12 testers in week 1 | Product owner | 2026-11-20 |
| D4 | Recording stack | **Expo location + task manager** (free, in Expo) / **Transistorsoft** (motion-aware, battery-conscious, paid release licence, price unknown) | Expo, unless the spike misses a §3 criterion on either phone | Mobile lead | 2026-11-27 |
| D5 | Minimum user age | **13+** (widest reach; strictest children's-data duties) / **16+** (simpler consent in most regions) / **18+** (safest; loses young riders) | 16+, subject to counsel | Product owner with counsel | 2026-12-11 |
| D6 | Monetisation | **None in v1** (focus on retention) / **Premium at launch** (revenue early, slows growth, needs billing work) | None in v1; revisit when T-054's retention result is in | Product owner | 2027-03-05 |

### Next checks
| # | Check | Passes when | Owner | Date |
|---|---|---|---|---|
| C1 | Developers re-size every ticket and read the acceptance criteria cold | Ambiguities listed and fixed; `plan_lint.py` still passes | Tech lead | 2026-11-25 |
| C2 | Spike on iPhone and Android, 45+ min rides | §3 criteria met, §10 table filled, D4 closed | Mobile lead | 2026-11-27 |
| C3 | Re-fetch pricing; price Supabase compute above Micro, Sentry and PostHog limits; price Transistorsoft if D4 needs it | §4 updated with dates | Backend lead | 2026-12-04 |
| C4 | Privacy-attack scripts running in CI against the shipped 400 m zone (T-022) | Median error ≥ 50 m on both attacks | Backend lead | 2026-12-18 |
| C5 | S1 gate: 12 riders recording real rides | Ride-save success ≥ 98%, no data-loss reports, spike criteria hold in the field | Product owner | 2026-12-28 |
| C6 | Replace the invented rider types in the XP and quest simulations with real ride data | Level and quest completion ranges re-run; constants in §6 adjusted | Product owner | 2027-01-29 |
| C7 | Counsel on children's privacy and GDPR basis for precise tracks | Written advice; D5 closed | Product owner | 2026-12-11 |
"""
rep("### Spike results (fill in)", """### What is verified and what is not
| Claim | Evidence | Status |
|---|---|---|
| Costs, schedule, XP examples, quest and privacy figures | Recomputed by `plan_lint.py` | Verified (code and fetched pricing) |
| Spike app compiles against the real Expo packages | `tsc` clean; analyzer tests pass | Verified; **never built or run on a device** |
| Background recording holds on real phones | — | **Unverified** (C2) |
| Storage per ride | Synthetic one-hour ride | Estimate; re-measure with spike data |
| Ticket sizes, thresholds in §3, rides per user per month | Estimates | Calibrate (C1, C5) |
| XP and quest fairness | Invented rider types | Design check only (C6) |

### Spike results (fill in)""")
for w in (" my ", " I ", " me ", "first draft", "Moved out", "the earlier MVP"):
    assert w not in s, w
open(p, 'w').write(s)
