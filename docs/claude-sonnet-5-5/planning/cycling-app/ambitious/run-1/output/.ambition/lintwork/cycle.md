# SpokeQuest — Build Blueprint (React Native + Expo, social gamified cycling tracker)

Working name: **SpokeQuest** (placeholder). Target: a small team ships a public v1 on iOS and Android.
Pricing and package versions below were fetched on **2026-11-13** (sources in §4).

## 1. Context and goal
Strava owns tracking and social for cyclists, but its game layer is thin. SpokeQuest is cycling-only: record a ride, get XP, keep a weekly streak, finish weekly quests, and compete with friends. Everything depends on **reliable background ride recording**, so that is gated first (§3) and built first (Phase 1).

**v1 success bar (beta, ~20 riders):** crash-free sessions ≥ 99%; ride-save success ≥ 98%; ≥ 40% of new users record a second ride within 14 days. (Targets are starting points to calibrate, not measured facts.)

## 1b. Product principles (the edge over Strava-style apps)
Riders choose this app because it is **fair, safe and private by default**. Each principle was tested (scripts in `plan-tools/sims/`) and is enforced by a ticket's acceptance criteria.
1. **Never reward speed or risk.** XP comes from distance and climbing with a weekly soft cap; no segments, KOMs or speed leaderboards in v1; max speed is shown only to the rider on their own summary, never in the feed.
2. **Hands-off while moving.** Reward reveals appear only after a ride is finished; our own notifications are suppressed while recording; the record screen has large controls and works with the screen locked.
3. **Private by default.** Following requires the rider's approval; ride maps are visible only to approved followers; no public discovery of rides; no live-location sharing in v1.
4. **Fair quests.** Targets are personal (110% of the rider's trailing 4-week median), not fixed. A fixed "climb 800 m" quest is completed 0% of weeks by commuters and 100% by keen riders (`plan-tools/sims/quests.py`); personalised targets land every rider type at 35–46%.
5. **Honest privacy zones.** A hidden start/end is a speed bump, not a guarantee (see §6 and §9), so access control, not geometry, is the main protection.

## 2. Decisions (settled — do not reopen without new evidence)
| Area | Decision | Why |
|---|---|---|
| Framework | Expo SDK 58 (current: `expo` 58.0.25), TypeScript, Expo Router, **EAS dev builds** | Background location needs a dev build; Expo Go can't do it on either OS (Expo docs) |
| State | Zustand (ride/UI) + TanStack Query (server) | Small, no boilerplate |
| Maps | **Mapbox** via `@rnmapbox/maps` 10.3.18 | Free to 25k MAU, then $4/1k MAU; custom route styling. Google Maps rejected: weaker styling, no cost advantage at our scale |
| Recording | `expo-location` + `expo-task-manager` + `expo-sqlite` buffer | Free, in Expo. **Fallback (only if spike fails §3):** Transistorsoft `react-native-background-geolocation` 5.8.2 — release builds need a paid licence (price not on repo page; check their purchase page) |
| Backend | **Supabase** (Postgres + PostGIS, Auth, Storage, Realtime) on **Pro, $25/mo, from launch** | Geo + relational + RLS in one place. Firebase rejected: weak relational/geo queries for leaderboards and feed |
| Scoring | **Postgres RPC `finalize_ride`** (plpgsql), not an Edge Function | One fewer moving part; testable with pgTAP; XP is computed server-side; a faked but plausible track can still earn XP, which is why leaderboards are friends-only (limits the harm) |
| Scheduled jobs | `pg_cron` + one Edge Function for push | Weekly quest rotation, streak reminders |
| Auth | Sign in with Apple + Google | App Store guideline 4.8 (read 2026-11-13) requires an *equivalent* login service that limits data to name/email, lets the user hide their email, and doesn't track for ads — it does not name Apple, but Sign in with Apple is the ready-made fit. Email deferred |
| Push | `expo-notifications` | |
| Observability | Sentry + PostHog (free tiers; limits not re-verified) | |
| CI/CD | GitHub Actions + EAS Build/Submit; **Expo Starter plan** at launch | See §4 |

## 3. Recording reliability — **UNVERIFIED** (the gate)
Not yet run on a real phone. A spike app is at `/Volumes/My Shared Files/work/spike-gps/` (see its README). Ticket **T-010** is the decision gate: do not start T-013 until it is closed.

What the Expo docs say that shapes the design (read 2026-11-13):
- If the user force-quits the app, background location **stops** and does not resume until relaunch; on Android a terminated app is **not** restarted by location events; behaviour on swipe-from-recents varies by vendor. → The recorder must survive a kill gracefully: on relaunch, detect an unfinished ride in SQLite and offer *Resume* or *Finish*; the gap is recorded, not hidden.
- Android 14+ needs `FOREGROUND_SERVICE_LOCATION`; new builds with background location need **Google Play review** → draft the justification and demo video as soon as M1 exists (after T-018) and finish them in T-053.
- iOS "Allow Once" makes a later background-permission request fail silently → the permission flow must detect it and send the user to Settings (T-014).
- Background task must be defined at module top level (`TaskManager.defineTask`).

**Pass criteria for the spike** (45+ min ride, screen locked, app in background, both phones; thresholds are proposals to calibrate):
1. Dropout time (gaps > 20 s while speed > 2 m/s) < 2% of moving time, and no gap > 60 s while moving.
2. Distance within ±3% of a reference (Apple Fitness / Strava / bike computer).
3. Battery drain ≤ 10% per hour on each phone.
4. After a force-quit mid-ride, the ride up to the kill is intact in SQLite.

If 1–3 fail on either OS after tuning accuracy/interval: adopt the Transistorsoft fallback (add its licence cost to §4) and re-estimate T-013. If only 4 fails, keep the Expo stack and fix the SQLite write/recovery path in T-013.

## 4. Cost model (monthly, USD)
Fetched 2026-11-13: [Supabase](https://supabase.com/pricing), [Mapbox](https://www.mapbox.com/pricing), [Expo](https://expo.dev/pricing).

| Line | 1k MAU | 10k MAU | 50k MAU | Basis |
|---|---|---|---|---|
| Supabase Pro | 25 | 25 | 25 | Includes 100k MAU, 8 GB DB, 100 GB storage, 250 GB egress |
| Mapbox Mobile Maps | 0 | 0 | 100 | Free to 25k MAU; 25k × $4/1k = $100 |
| Expo plan (+ EAS Update) | 19 | 54 | 199 | Starter $19 + $0.005/MAU beyond 3,000 ($35 at 10k); at 50k, Production $199 (50k included) beats Starter ($254) |
| **Subtotal (verified lines)** | **44** | **79** | **324** | |

Not in the subtotal:
- **Supabase compute upgrade** beyond Micro (covered by the $10 credit): price not fetched. Budget extra at 10k+ MAU — **unverified**.
- Apple Developer $99/yr and Google Play $25 one-time (standard fees, not re-fetched; you have no paid Apple account yet, needed before TestFlight).
- Storage/DB growth: measured on a synthetic 60-min ride (2,160 points at a 10 m filter, `plan-tools/sims/sizes.py`): raw JSON 182 KB → **39 KB gzipped** (21 KB if delta-coded); simplified polyline ≈ 1.3 KB, so ~3 KB per ride in the DB. Real tracks are noisier — re-measure with spike data. The **8 rides/MAU/month** figure is my assumption, not data. At 50k MAU that is ≈ 1.2 GB DB and 16 GB storage per month; overage is cents-to-dollars (DB $0.125/GB, storage $0.0213/GB), so cost is insensitive to this guess.
- Lever: EAS Update is the largest Expo line; shipping via store releases only would drop it, at the price of slower hotfixes.

## 5. v1 scope (ruthless cut)
**In:** Apple/Google sign-in; profile + home privacy zone; background ride recording with crash recovery; ride summary map; XP, levels, weekly streak (1 freeze/month); 3 weekly quests; 8 badges; follow requests (rider-approved) + feed + kudos; block/report; friends weekly leaderboard; push (streak-at-risk, kudos); onboarding; account deletion/export; Sentry/PostHog.

**Deferred, with reasons**
| Deferred | Reason |
|---|---|
| Clubs + club leaderboards | Needs moderation/roles; friends leaderboard tests the social loop first |
| Comments | Moderation and notifications cost; kudos gives the feedback loop |
| Bike garage / maintenance | Not part of the core loop |
| Explorer map / territory "Zones" | Needs tile model and balancing; validate retention first |
| BLE sensors (HR/power/cadence) | Native module risk; GPS-only covers most riders |
| Segments / KOMs | Matching engine and anti-cheat surface; large |
| Strava/Garmin/Health import | Cold-start help but heavy API and policy work |
| Share cards | Nice-to-have; not needed to learn if the loop works |
| Email login | Two providers suffice; less to secure |
| Premium tier | No monetisation before retention is proven |

## 6. Architecture notes
- Ride recorder: state machine idle → recording → paused → finished; points written to SQLite as they arrive; on finish, Douglas-Peucker simplified polyline + gzipped raw points uploaded through an offline queue with retry.
- `finalize_ride` RPC validates (min distance/time, speed and teleport checks, flagged rides excluded from leaderboards), awards XP/streak/quest/badges in one transaction, and truncates public geometry inside the user's privacy zone.
- **XP rules (starting values, tune with beta data; implemented as code in `plan-tools/sims/xp_rules.py`, which is the reference for the T-030 tests).** Per counted ride: `base = min(600, round(10·km + 0.2·elevation_m))`. Then: the part of a week's base XP above 1,500 counts at 25%; then × `(1 + 5% × previous consecutive active weeks, max 5)` (so up to +25%); then +300 on the rider's first ever counted ride. Quest completion is a flat +100 (no cap, no bonus). Flagged rides earn 0.

  | Worked example | Base | Awarded |
  |---|---|---|
  | 1. First ever ride, 8 km / 40 m | 88 | 388 (reaches level 2) |
  | 2. Long hilly ride, 60 km / 600 m | 600 (per-ride cap) | 600 |
  | 3. Third 600-base ride in a week (1,200 already earned) | 600 | 375 (300 at 100% + 300 at 25%) |
  | 4. 25 km / 150 m in the 4th consecutive active week | 280 | 322 (+15%) |
  | 5. Quest completed | — | 100 |

- **Levels:** cumulative threshold `xp_for_level(n) = round(60·n²)` for n ≥ 2 (L2 = 240, L10 = 6,000, L20 = 24,000, L30 = 54,000, L50 = 150,000). Simulated over 52 weeks for four invented rider types: casual → L12, commuter → L23, weekend → L32, keen → L46; every type reaches L2 on ride 1. The first draft (`100·n^1.5`, no cap) put a keen rider at L167 and a commuter at L1 after ride 1, so it was dropped. The riders are assumptions, not user data. Golden-value tests keep the SQL and TS mirror identical.
- **Badges (8, no XP attached; starting set):** First Ride; Half Century (one ride ≥ 50 km); Climber (≥ 1,000 m climbed in a week); Early Bird (a ride starting 04:00–07:00 local time); 4-Week Streak; 12-Week Streak; Odometer (500 km lifetime); Well Liked (10 kudos received). Each is awarded once.
- RLS on every table; feed reads only the privacy-truncated geometry, and only for approved followers.
- **Privacy zone design (tested against two attacks):** the fixed-centre, fixed-radius zone first drafted here was recovered to **0.0 m** from just 3 published rides by fitting a circle to the cut points (`plan-tools/sims/privacy_attack.py`). Shipped design: default radius **400 m**, a secret per-user centre offset up to 0.4 × radius, and a per-ride radius jitter of 1.0–1.6 ×. A second attack that extends each track's heading backwards (`plan-tools/sims/privacy_attack2.py`) still located home to ~17–61 m after 30 rides with a 200 m zone and ~55–175 m with a 400 m zone. Hence: geometry is secondary, approval-gated visibility is primary, and the UI says the zone "reduces, but doesn't eliminate" exposure. Raw tracks live in a private storage bucket, owner-only.

## 7. Tickets
Format is machine-checked by `plan-tools/check_tickets.py` — keep the `### T-nnn` and `Depends:` lines exactly as written. Order = a valid build order; critical path in §8.

### Phase 0 — Foundations

### T-001 · App skeleton
Depends: T-054
Size: 2d
- Expo SDK 58 + TS + Expo Router, ESLint/Prettier, Jest, GitHub Actions running lint + test.
- AC: `npm run lint` and `npm test` pass in CI on a clean clone.

### T-002 · EAS dev builds
Depends: T-001
Size: 2d
- AC: `development` profile builds install and launch on one iPhone (free provisioning) and one Android phone.

### T-003 · Supabase project and local dev
Depends: T-001
Size: 2d
- Supabase CLI, migrations folder, `seed.sql`, PostGIS enabled, CI step applying migrations to a clean DB.
- AC: `supabase db reset` succeeds locally and in CI.

### T-004 · Design tokens and base UI
Depends: T-001
Size: 4d
- Colors, type scale, spacing; Button, Card, StatTile, Badge; light/dark.
- AC: a storybook-style screen shows every component at 360 and 430 pt widths with no clipping.

### T-005 · Auth (Apple + Google)
Depends: T-002, T-003
Size: 4d
- AC: sign in/out works on both OSes; session survives app restart; a `profiles` row is created exactly once per user.

### T-006 · Profile setup and privacy zone
Depends: T-005, T-004
Size: 3d
- Username (unique, 3–20 chars), optional avatar, home location + radius (default 400 m), plus a per-ride "hide map" option.
- AC: duplicate username is rejected with a clear message; privacy zone persists and can be edited.

### T-007 · Developer accounts and Play closed-test enrolment
Depends: none
Size: 2d
- Enrol in the Apple Developer Program ($99/yr) and Google Play. Google's rule (read 2026-11-13): **personal accounts created after 2023-11-13 must run a closed test with ≥ 12 testers opted in continuously for ≥ 14 days before production access**. The page did not cover organization accounts — check which account type you will use.
- Recruit ≥ 12 Android testers (use the same list for TestFlight).
- AC: both accounts active; account type recorded; 12 named Android testers confirmed.

### Phase 1 — Recording and backend core

### T-010 · GPS spike gate (human)
Depends: T-002
Size: 3d
- Run `spike-gps` per its README on iPhone and Android; analyze logs against §3 criteria; record results in this file and decide: Expo stack or Transistorsoft fallback.
- AC: §3 table of results filled in for both OSes; decision written down.

### T-011 · Geo library
Depends: T-001
Size: 4d
- Haversine distance, accuracy filter (drop > 30 m), elevation smoothing, Douglas-Peucker, polyline encode/decode, moving-time with stop detection.
- AC: unit tests on fixture tracks (steady ride, stop-and-go, GPS jump) pass; distance on the steady fixture within 0.5% of the known value.

### T-012 · Recorder state machine
Depends: T-011
Size: 2d
- States idle/recording/paused/finished; auto-pause after 10 s below 1 m/s.
- AC: transition table covered by tests; invalid transitions throw.

### T-013 · Background location task and SQLite buffer
Depends: T-012, T-010
Size: 6d
- Top-level `defineTask`; points inserted on arrival; unfinished-ride detection on launch with Resume/Finish.
- AC: on a real device with screen locked for 20 min, point count matches the T-010 spike result for the same device within 5%; force-quit then relaunch offers recovery with all prior points intact.

### T-014 · Permission flow
Depends: T-002, T-004
Size: 4d
- When-in-use → Always escalation with rationale screens; handles denied, "Allow Once", and Android background-permission steps.
- AC: each of the five permission states reaches a screen that either proceeds or explains how to fix it; no silent dead end.

### T-015 · Record screen
Depends: T-013, T-014, T-004
Size: 4d
- Live distance/time/speed, start/pause/finish, Android foreground-service notification.
- AC: start→finish works with the screen locked; notification shows while recording on Android; stats update at least every 5 s in the foreground; start/pause/finish are single large controls (no scrolling or text input while recording).

### T-016 · Map component
Depends: T-002, T-004
Size: 4d
- Mapbox view with route polyline layer; live-follow and fit-to-route modes.
- AC: renders a 5,000-point route at ≥ 30 fps on a mid-range Android phone (judge on device, not simulator).

### T-020 · Schema v1 and RLS
Depends: T-003
Size: 3d
- Tables: profiles, rides, xp_events, quests, user_quests, badges, user_badges, follows, kudos, streaks, push_tokens.
- AC: migration applies clean; every table has RLS enabled.

### T-021 · RLS tests
Depends: T-020
Size: 3d
- pgTAP tests: users read public rides of anyone, private data only their own, write only their own.
- AC: suite passes in CI; removing a policy makes a test fail.

### T-022 · `finalize_ride` RPC
Depends: T-020
Size: 6d
- Validation, flagging, privacy-zone truncation, idempotency.
- Privacy truncation per §6 (400 m default, secret offset, radius jitter).
- AC: fixtures — normal ride accepted; 60 km/h average flagged; 1 km teleport flagged; ride inside privacy zone has truncated public geometry. Attack scripts (`plan-tools/sims/privacy_attack*.py`, ported into CI) run on the published geometry of 30 synthetic rides: the old fixed-zone control is recovered to < 5 m, the shipped config shows ≥ 50 m median error on both attacks (re-measure; the circle-fit result for the 400 m config was not run).

### T-017 · Ride finalize and upload queue
Depends: T-013, T-005, T-022
Size: 5d
- Simplify, encode, upload, call `finalize_ride`; retry with backoff; idempotent via client ride id.
- AC: airplane-mode ride uploads once on reconnect; double-submit creates one ride.

### T-018 · Ride summary screen
Depends: T-016, T-017
Size: 3d
- Map, distance, moving time, elevation gain, avg/max speed, km splits.
- AC: values equal the server-stored values; screen opens in < 1 s from cache.

### Phase 2 — Gamification

### T-030 · XP and levels
Depends: T-022
Size: 2d
- Implements the XP and level rules in §6.
- AC: SQL and TS agree on golden values for levels 1–50 and reproduce the five worked examples in §6 exactly.

### T-031 · Weekly streak with freeze
Depends: T-022
Size: 3d
- AC: tests for a missed week with and without an available freeze; freeze refills monthly.

### T-032 · Weekly quests
Depends: T-022
Size: 4d
- Three quests per week from three kinds (days ridden, distance, climbing), rotated by `pg_cron`, progress updated on finalize. Target = 110% of the rider's trailing 4-week median, floored (≥ 2 days); riders with < 4 weeks of history get fixed starter quests (ride once, ride 2 days, 10 km).
- AC: a ride advances matching quests once; rotation happens Monday 00:00 in the user's timezone; a replay of the simulated rider types (`plan-tools/sims/quests.py` logic ported to a SQL test) gives each type a 30–60% weekly completion rate — tune the multiplier, not the shape.

### T-033 · Badges
Depends: T-022
Size: 3d
- The eight badges listed in §6, awarded in `finalize_ride`.
- AC: each badge has a test that awards it exactly once.

### T-034 · Post-ride reward reveal
Depends: T-018, T-030, T-031, T-032, T-033
Size: 4d
- XP gained, level-up, quest/badge unlocks (Reanimated + haptics).
- AC: appears after every counted ride; skippable; no animation on flagged rides; **never shown while a ride is recording**.

### T-035 · Quests and profile tab
Depends: T-030, T-031, T-032, T-033, T-004
Size: 3d
- Level, streak, quest progress, badge shelf.
- AC: data matches the server; empty states read well for a new user.

### Phase 3 — Social

### T-040 · Follow and user search
Depends: T-020, T-006
Size: 3d
- Follow is a **request the rider approves** by default; search shows username and avatar only (no rides, no locations).
- AC: follow/unfollow idempotent; a pending request exposes nothing; an unapproved user cannot read another user's rides, maps or stats (pgTAP test).

### T-041 · Feed
Depends: T-040, T-022, T-016
Size: 4d
- Rides from followed users, newest first, cursor pagination, privacy-truncated geometry only.
- AC: no raw geometry from inside a privacy zone ever reaches the client (test with a crafted ride); feed cards show distance, time, elevation and average speed, never max speed; only approved followers see the map.

### T-042 · Kudos
Depends: T-041
Size: 2d
- AC: one kudo per user per ride; count updates optimistically and reconciles.

### T-043 · Friends weekly leaderboard
Depends: T-040, T-030
Size: 3d
- Distance and XP, resets weekly, flagged rides excluded.
- AC: totals equal the sum of non-flagged rides for the week.

### T-044 · Push notifications
Depends: T-005, T-031, T-042
Size: 5d
- Token registration; streak-at-risk reminder; kudos received.
- AC: reminder sends only to users with an at-risk streak, max one per day; a user can disable each type; no app notification is delivered while a ride is recording (queued until finish).

### T-045 · Block, report and moderation baseline
Depends: T-040
Size: 4d
- App Store guideline 1.2 (read 2026-11-13) requires, for apps where users share content: a way to filter objectionable material, a report mechanism with timely responses, the ability to block abusive users, and published contact info. Here: block user, report user/ride, basic denylist on usernames, published support email, internal queue to review reports within a documented time.
- AC: a blocked user cannot see or follow the blocker and vanishes from search; a report creates a reviewable record; support contact is linked in-app and in store metadata.

### Phase 4 — Ship

### T-050 · Observability
Depends: T-001
Size: 2d
- Sentry + PostHog; events: ride_started, ride_saved, ride_save_failed, permission_state.
- AC: a forced error and each event appear in the dashboards from a dev build.

### T-051 · Onboarding
Depends: T-006, T-014
Size: 3d
- Three screens plus permission priming.
- AC: a new user reaches their first recording in ≤ 6 taps from install.

### T-052 · Account deletion and data export
Depends: T-020
Size: 3d
- AC: deletion removes profile, rides, and storage objects; export returns a JSON/GPX archive.

### T-053 · Store readiness
Depends: T-015, T-051, T-052, T-007, T-045
Size: 6d
- Store listings, privacy policy (must cover data collected, uses, retention/deletion, consent withdrawal — guideline 5.1.1), background-location justification text and demo video, age rating and a terms-of-service minimum age (**needs legal advice**, see §11), TestFlight and Play internal tracks.
- AC: both builds are installable from the stores' test tracks.

### T-054 · Beta soak (doubles as the Play closed test)
Depends: T-053, T-050, T-044, T-034, T-043, T-007, T-045
Size: 10d
- ≥ 12 Android testers opted in for ≥ 14 consecutive days on the Play closed-testing track, plus TestFlight riders (~20 total). Start the 14-day clock as early as a stable build exists; it is elapsed time, not effort.
- AC: crash-free ≥ 99%, ride-save success ≥ 98%, Play production access granted, results written back into §1.

## 8. Critical path and staffing
Two paths matter (the first is from `check_tickets.py`; the second is the risk path):
- **Longest dependency chain (9 tickets):** T-001 → T-002 → T-005 → T-006 → T-040 → T-041 → T-042 → T-044 → T-054. Auth and profile gate all social work, so start T-005/T-006 early.
- **Riskiest path (8 tickets):** T-001 → T-002 → **T-010** → T-013 → T-017 → T-018 → T-034 → T-054. If T-010 fails, this path grows by the fallback integration.
Backend track (T-003 → T-020 → T-022 → T-030…T-033) runs in parallel and must finish before T-017 and T-034.
Estimate, computed by `plan-tools/check_tickets.py` from the ticket sizes (130 dev-days; critical path 36 working days):
| Team | Lower bound (perfect parallelism) | Realistic (70% focus) |
|---|---|---|
| 2 devs | 13.0 wk | ~19 wk |
| 3 devs (mobile-recording, mobile-UI, backend) | 8.7 wk | **~12 wk** |
| 4 devs | 7.2 wk | ~10 wk |

The sizes are my estimates (dev-days incl. tests); the team should re-size every ticket before committing. Not in the numbers: T-010 needs a real ride on two phones (calendar time), T-054 contains Google's 14-day minimum closed test (elapsed time), and store review waits. Phases in §7 are groupings, not dated sprints. If T-010 fails, add the fallback integration (unsized).

### Milestones (every one is a build the team rides with, on both OSes)
| | After | You can… |
|---|---|---|
| M1 walking skeleton | T-018 | record a ride, save it, see the summary |
| M2 game loop | T-035 | see XP, level, streak, quests, badges |
| M3 social | T-045 | follow (with approval), see a feed, give kudos, compare weekly |
| M4 beta | T-054 | the store tracks are live with 12+ Android testers |
Definition of done for any ticket: acceptance criteria met, tests pass in CI, merged behind a feature flag if user-visible, and checked on a real device build with Sentry clean. Hotfix path: EAS Update channel per milestone.

## 9. Risks
| Risk | Mitigation |
|---|---|
| Background GPS unreliable | Spike gate T-010; Transistorsoft fallback; crash-recovery in T-013 |
| Play review rejects background location | Draft justification + demo video after M1 (T-018), finish in T-053; the 14-day closed test in T-054 leaves room to resubmit |
| iOS free provisioning expires in 7 days | Fine for the spike; paid Apple account needed before TestFlight |
| Battery drain | Tune accuracy/interval during the spike; measured in §3 |
| Privacy exposure of home location | Approval-gated visibility (T-040/T-041) first; geometry hiding second and **tested** against two attacks (§6); honest UI copy |
| Incentives that push riders to speed or distraction | Principles 1–2 in §1b; no speed leaderboards/segments in v1; rewards only after the ride; notifications queued while recording |
| Stalking / harassment through follows | Follow approval, block and report (T-040, T-045) |
| Minors using a location-sharing app | Age rating and terms decided with counsel before T-053; the Apple page read does not set a general minimum age (only 13 for facial-recognition auth) |
| Cheating | Server-side validation + flagging; exclude from leaderboards |
| Cold-start social graph | Friends leaderboard works with 2 people; solo quests still reward |

## 10. Verification
- **Dependency check:** `python3 -I "/Volumes/My Shared Files/work/plan-tools/check_tickets.py" /cfg/plans/make-a-plan-for-jaunty-wren.md` — exits non-zero on cycles, unknown prerequisites, or tickets listed before their prerequisites.
- **Privacy attacks:** `python3 -I plan-tools/sims/privacy_attack.py` and `privacy_attack2.py` reproduce the §6 numbers; T-022 ports them to CI.
- **Quest fairness:** `python3 -I plan-tools/sims/quests.py`.
- **Pricing:** re-fetch the three pricing pages before committing budget; update §4 dates.
- **Spike:** results table below, filled from real rides.
- **Tickets:** each ticket's AC is runnable (test, device check, or dashboard); the dry run by your developers is the final test of ambiguity.

### Spike results (fill in)
| Phone / OS | Duration | Dropout % | Longest moving gap | Distance vs reference | Battery/hr | Force-quit recovery |
|---|---|---|---|---|---|---|
| iPhone | — | — | — | — | — | — |
| Android | — | — | — | — | — | — |

## 11. Open items
- Transistorsoft licence price (only if the fallback triggers).
- Supabase compute pricing for 10k+ MAU.
- Sentry/PostHog free-tier limits.
- Legal: minimum user age and children's-privacy obligations for location sharing; GDPR basis for storing precise tracks (not researched).
- Real rider data to replace the invented personas in the XP and quest simulations.
