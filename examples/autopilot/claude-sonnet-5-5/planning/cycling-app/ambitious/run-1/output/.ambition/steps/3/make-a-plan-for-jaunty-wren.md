# SpokeQuest — Build Blueprint (React Native + Expo, social gamified cycling tracker)

Working name: **SpokeQuest** (placeholder). Target: a small team ships a public v1 on iOS and Android.
Pricing and package versions below were fetched on **2026-11-13** (sources in §4).

## 1. Context and goal
Strava owns tracking and social for cyclists, but its game layer is thin. SpokeQuest is cycling-only: record a ride, get XP, keep a weekly streak, finish weekly quests, and compete with friends. Everything depends on **reliable background ride recording**, so that is gated first (§3) and built first (Phase 1).

**v1 success bar (beta, ~20 riders):** crash-free sessions ≥ 99%; ride-save success ≥ 98%; ≥ 40% of new users record a second ride within 14 days. (Targets are starting points to calibrate, not measured facts.)

## 2. Decisions (settled — do not reopen without new evidence)
| Area | Decision | Why |
|---|---|---|
| Framework | Expo SDK 58 (current: `expo` 58.0.25), TypeScript, Expo Router, **EAS dev builds** | Background location needs a dev build; Expo Go can't do it on either OS (Expo docs) |
| State | Zustand (ride/UI) + TanStack Query (server) | Small, no boilerplate |
| Maps | **Mapbox** via `@rnmapbox/maps` 10.3.18 | Free to 25k MAU, then $4/1k MAU; custom route styling. Google Maps rejected: weaker styling, no cost advantage at our scale |
| Recording | `expo-location` + `expo-task-manager` + `expo-sqlite` buffer | Free, in Expo. **Fallback (only if spike fails §3):** Transistorsoft `react-native-background-geolocation` 5.8.2 — release builds need a paid licence (price not on repo page; check their purchase page) |
| Backend | **Supabase** (Postgres + PostGIS, Auth, Storage, Realtime) on **Pro, $25/mo, from launch** | Geo + relational + RLS in one place. Firebase rejected: weak relational/geo queries for leaderboards and feed |
| Scoring | **Postgres RPC `finalize_ride`** (plpgsql), not an Edge Function | One fewer moving part; testable with pgTAP; XP can't be forged client-side |
| Scheduled jobs | `pg_cron` + one Edge Function for push | Weekly quest rotation, streak reminders |
| Auth | Sign in with Apple + Google | Apple is required on iOS whenever Google sign-in is offered. Email deferred |
| Push | `expo-notifications` | |
| Observability | Sentry + PostHog (free tiers; limits not re-verified) | |
| CI/CD | GitHub Actions + EAS Build/Submit; **Expo Starter plan** at launch | See §4 |

## 3. Recording reliability — **UNVERIFIED** (the gate)
Not yet run on a real phone. A spike app is at `/Volumes/My Shared Files/work/spike-gps/` (see its README). Ticket **T-010** is the decision gate: do not start T-013 until it is closed.

What the Expo docs say that shapes the design (read 2026-11-13):
- If the user force-quits the app, background location **stops** and does not resume until relaunch; on Android a terminated app is **not** restarted by location events; behaviour on swipe-from-recents varies by vendor. → The recorder must survive a kill gracefully: on relaunch, detect an unfinished ride in SQLite and offer *Resume* or *Finish*; the gap is recorded, not hidden.
- Android 14+ needs `FOREGROUND_SERVICE_LOCATION`; new builds with background location need **Google Play review** → start the justification and demo video early (T-053).
- iOS "Allow Once" makes a later background-permission request fail silently → the permission flow must detect it and send the user to Settings (T-014).
- Background task must be defined at module top level (`TaskManager.defineTask`).

**Pass criteria for the spike** (45+ min ride, screen locked, app in background, both phones; thresholds are proposals to calibrate):
1. Dropout time (gaps > 20 s while speed > 2 m/s) < 2% of moving time, and no gap > 60 s while moving.
2. Distance within ±3% of a reference (Apple Fitness / Strava / bike computer).
3. Battery drain ≤ 10% per hour on each phone.
4. After a force-quit mid-ride, the ride up to the kill is intact in SQLite.

If 1–3 fail on either OS after tuning accuracy/interval: adopt the Transistorsoft fallback (add its licence cost to §4) and re-estimate T-013.

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
- Storage/DB growth: at 8 rides/MAU/month, ~12 KB DB + ~40 KB gzipped raw track per ride (estimates). At 50k MAU ≈ 4.8 GB DB and 16 GB storage per month; overage is cents-to-dollars (DB $0.125/GB, storage $0.0213/GB).
- Lever: EAS Update is the largest Expo line; shipping via store releases only would drop it, at the price of slower hotfixes.

## 5. v1 scope (ruthless cut)
**In:** Apple/Google sign-in; profile + home privacy zone; background ride recording with crash recovery; ride summary map; XP, levels, weekly streak (1 freeze/month); 3 weekly quests; 8 badges; follow + feed + kudos; friends weekly leaderboard; push (streak-at-risk, kudos); onboarding; account deletion/export; Sentry/PostHog.

**Deferred, with reasons**
| Deferred | Reason |
|---|---|
| Clubs + club leaderboards | Needs moderation/roles; friends leaderboard tests the social loop first. *(Moved out of the earlier MVP.)* |
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
- Level curve: `xp_for_level(n) = round(100 * n^1.5)`; golden-value tests keep the SQL and the TS mirror identical.
- RLS on every table; feed reads only the privacy-truncated geometry.

## 7. Tickets
Format is machine-checked by `plan-tools/check_tickets.py` — keep the `### T-nnn` and `Depends:` lines exactly as written. Order = a valid build order; critical path in §8.

### Phase 0 — Foundations (week 1)

### T-001 · App skeleton
Depends: none
- Expo SDK 58 + TS + Expo Router, ESLint/Prettier, Jest, GitHub Actions running lint + test.
- AC: `npm run lint` and `npm test` pass in CI on a clean clone.

### T-002 · EAS dev builds
Depends: T-001
- AC: `development` profile builds install and launch on one iPhone (free provisioning) and one Android phone.

### T-003 · Supabase project and local dev
Depends: T-001
- Supabase CLI, migrations folder, `seed.sql`, PostGIS enabled, CI step applying migrations to a clean DB.
- AC: `supabase db reset` succeeds locally and in CI.

### T-004 · Design tokens and base UI
Depends: T-001
- Colors, type scale, spacing; Button, Card, StatTile, Badge; light/dark.
- AC: a storybook-style screen shows every component at 360 and 430 pt widths with no clipping.

### T-005 · Auth (Apple + Google)
Depends: T-002, T-003
- AC: sign in/out works on both OSes; session survives app restart; a `profiles` row is created exactly once per user.

### T-006 · Profile setup and privacy zone
Depends: T-005, T-004
- Username (unique, 3–20 chars), optional avatar, home location + radius (default 200 m).
- AC: duplicate username is rejected with a clear message; privacy zone persists and can be edited.

### Phase 1 — Recording and backend core (weeks 2–5)

### T-010 · GPS spike gate (human)
Depends: T-002
- Run `spike-gps` per its README on iPhone and Android; analyze logs against §3 criteria; record results in this file and decide: Expo stack or Transistorsoft fallback.
- AC: §3 table of results filled in for both OSes; decision written down.

### T-011 · Geo library
Depends: T-001
- Haversine distance, accuracy filter (drop > 30 m), elevation smoothing, Douglas-Peucker, polyline encode/decode, moving-time with stop detection.
- AC: unit tests on fixture tracks (steady ride, stop-and-go, GPS jump) pass; distance on the steady fixture within 0.5% of the known value.

### T-012 · Recorder state machine
Depends: T-011
- States idle/recording/paused/finished; auto-pause after 10 s below 1 m/s.
- AC: transition table covered by tests; invalid transitions throw.

### T-013 · Background location task and SQLite buffer
Depends: T-012, T-010
- Top-level `defineTask`; points inserted on arrival; unfinished-ride detection on launch with Resume/Finish.
- AC: on a real device with screen locked for 20 min, point count matches the spike baseline within 5%; force-quit then relaunch offers recovery with all prior points intact.

### T-014 · Permission flow
Depends: T-002, T-004
- When-in-use → Always escalation with rationale screens; handles denied, "Allow Once", and Android background-permission steps.
- AC: each of the five permission states reaches a screen that either proceeds or explains how to fix it; no silent dead end.

### T-015 · Record screen
Depends: T-013, T-014, T-004
- Live distance/time/speed, start/pause/finish, Android foreground-service notification.
- AC: start→finish works with the screen locked; notification shows while recording on Android; stats update at least every 5 s in the foreground.

### T-016 · Map component
Depends: T-002, T-004
- Mapbox view with route polyline layer; live-follow and fit-to-route modes.
- AC: renders a 5,000-point route at ≥ 30 fps on a mid-range Android phone (judge on device, not simulator).

### T-020 · Schema v1 and RLS
Depends: T-003
- Tables: profiles, rides, xp_events, quests, user_quests, badges, user_badges, follows, kudos, streaks, push_tokens.
- AC: migration applies clean; every table has RLS enabled.

### T-021 · RLS tests
Depends: T-020
- pgTAP tests: users read public rides of anyone, private data only their own, write only their own.
- AC: suite passes in CI; removing a policy makes a test fail.

### T-022 · `finalize_ride` RPC
Depends: T-020
- Validation, flagging, privacy-zone truncation, idempotency.
- AC: fixtures — normal ride accepted; 60 km/h average flagged; 1 km teleport flagged; ride inside privacy zone has truncated public geometry.

### T-017 · Ride finalize and upload queue
Depends: T-013, T-005, T-022
- Simplify, encode, upload, call `finalize_ride`; retry with backoff; idempotent via client ride id.
- AC: airplane-mode ride uploads once on reconnect; double-submit creates one ride.

### T-018 · Ride summary screen
Depends: T-016, T-017
- Map, distance, moving time, elevation gain, avg/max speed, km splits.
- AC: values equal the server-stored values; screen opens in < 1 s from cache.

### Phase 2 — Gamification (weeks 5–7)

### T-030 · XP and levels
Depends: T-022
- AC: SQL and TS implementations agree on golden values for levels 1–50.

### T-031 · Weekly streak with freeze
Depends: T-022
- AC: tests for a missed week with and without an available freeze; freeze refills monthly.

### T-032 · Weekly quests
Depends: T-022
- Three quests per week, rotated by `pg_cron`, progress updated on finalize.
- AC: a ride advances matching quests once; rotation happens Monday 00:00 in the user's timezone.

### T-033 · Badges
Depends: T-022
- Eight fixed badges awarded in `finalize_ride`.
- AC: each badge has a test that awards it exactly once.

### T-034 · Post-ride reward reveal
Depends: T-018, T-030, T-031, T-032, T-033
- XP gained, level-up, quest/badge unlocks (Reanimated + haptics).
- AC: appears after every counted ride; skippable; no animation on flagged rides.

### T-035 · Quests and profile tab
Depends: T-030, T-031, T-032, T-033, T-004
- Level, streak, quest progress, badge shelf.
- AC: data matches the server; empty states read well for a new user.

### Phase 3 — Social (weeks 7–9)

### T-040 · Follow and user search
Depends: T-020, T-006
- AC: follow/unfollow is instant and idempotent; search by username prefix.

### T-041 · Feed
Depends: T-040, T-022, T-016
- Rides from followed users, newest first, cursor pagination, privacy-truncated geometry only.
- AC: no raw geometry from inside a privacy zone ever reaches the client (test with a crafted ride).

### T-042 · Kudos
Depends: T-041
- AC: one kudo per user per ride; count updates optimistically and reconciles.

### T-043 · Friends weekly leaderboard
Depends: T-040, T-030
- Distance and XP, resets weekly, flagged rides excluded.
- AC: totals equal the sum of non-flagged rides for the week.

### T-044 · Push notifications
Depends: T-005, T-031, T-042
- Token registration; streak-at-risk reminder; kudos received.
- AC: reminder sends only to users with an at-risk streak, max one per day; a user can disable each type.

### Phase 4 — Ship (weeks 9–11)

### T-050 · Observability
Depends: T-001
- Sentry + PostHog; events: ride_started, ride_saved, ride_save_failed, permission_state.
- AC: a forced error and each event appear in the dashboards from a dev build.

### T-051 · Onboarding
Depends: T-006, T-014
- Three screens plus permission priming.
- AC: a new user reaches their first recording in ≤ 6 taps from install.

### T-052 · Account deletion and data export
Depends: T-020
- AC: deletion removes profile, rides, and storage objects; export returns a JSON/GPX archive.

### T-053 · Store readiness
Depends: T-015, T-051, T-052
- Store listings, privacy policy, background-location justification text and demo video, TestFlight and Play internal tracks.
- AC: both builds are installable from the stores' test tracks.

### T-054 · Beta soak
Depends: T-053, T-050, T-044, T-034, T-043
- ~20 riders for two weeks.
- AC: crash-free ≥ 99%, ride-save success ≥ 98%, results written back into §1.

## 8. Critical path and staffing
Two paths matter (the first is from `check_tickets.py`; the second is the risk path):
- **Longest dependency chain (9 tickets):** T-001 → T-002 → T-005 → T-006 → T-040 → T-041 → T-042 → T-044 → T-054. Auth and profile gate all social work, so start T-005/T-006 early.
- **Riskiest path (8 tickets):** T-001 → T-002 → **T-010** → T-013 → T-017 → T-018 → T-034 → T-054. If T-010 fails, this path grows by the fallback integration.
Backend track (T-003 → T-020 → T-022 → T-030…T-033) runs in parallel and must finish before T-017 and T-034.
Estimate: ~11 weeks with 3 developers (one mobile-recording, one mobile-UI, one backend). This is a planning estimate, not measured.

## 9. Risks
| Risk | Mitigation |
|---|---|
| Background GPS unreliable | Spike gate T-010; Transistorsoft fallback; crash-recovery in T-013 |
| Play review rejects background location | Justification + demo video prepared in T-053; start review early |
| iOS free provisioning expires in 7 days | Fine for the spike; paid Apple account needed before TestFlight |
| Battery drain | Tune accuracy/interval during the spike; measured in §3 |
| Privacy exposure of home location | Server-side truncation (T-022), tested in T-041 |
| Cheating | Server-side validation + flagging; exclude from leaderboards |
| Cold-start social graph | Friends leaderboard works with 2 people; solo quests still reward |

## 10. Verification
- **Dependency check:** `python3 -I "/Volumes/My Shared Files/work/plan-tools/check_tickets.py" /cfg/plans/make-a-plan-for-jaunty-wren.md` — exits non-zero on cycles, unknown prerequisites, or tickets listed before their prerequisites.
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
