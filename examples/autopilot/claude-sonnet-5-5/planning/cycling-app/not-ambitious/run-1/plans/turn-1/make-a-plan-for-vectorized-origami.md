# Cycling Social Fitness App (React Native + Expo) — Plan

## Context
Build a social, gamified fitness tracker for cyclists. Existing apps (Strava) are social but shallow on game mechanics; gamified apps (Zwift) are indoor-focused. Opportunity: outdoor-first ride tracking with territory/segment games, streaks, challenges, and club-based social features. Greenfield project (working dir has no existing code), so no reuse constraints.

## Product Scope

### MVP (v1)
1. **Auth & profile**: email/Apple/Google sign-in, bike garage, avatar, level/XP.
2. **Ride recording**: GPS tracking (foreground + background), live stats (speed, distance, elevation, time), auto-pause, offline-safe recording, save as route.
3. **Ride feed**: followed riders' rides, kudos, comments, map thumbnail, photos.
4. **Gamification core**:
   - XP and levels from distance, elevation, consistency
   - Streaks (weekly ride streak, with "freeze" tokens)
   - Badges/achievements (first 100 km, Everesting progress, early bird, etc.)
   - Weekly challenges (distance, climb, rides count) + personal goals
5. **Segments & leaderboards**: user-defined climb/sprint segments, KOM/QOM, friends/club/local leaderboards.
6. **Clubs**: create/join, club feed, club-vs-club monthly challenges.
7. **Push notifications**: kudos, challenge progress, streak-at-risk, segment beaten.

### v2
Territory capture ("claim" map hexes by riding through them), group rides with live location, Apple Health / Health Connect / Garmin / Bluetooth sensors (HR, power, cadence), route planner, seasons with cosmetic rewards, safety features (crash detection, live share).

## Tech Stack
- **App**: Expo SDK (latest) + TypeScript, **Expo Router** (file-based nav), dev builds via **EAS Build** (needed for background location, BLE).
- **State/data**: TanStack Query (server state), Zustand (ride-recording and UI state), MMKV for local cache.
- **Maps**: `@rnmapbox/maps` (offline tiles, route lines, hex layers) — requires dev client.
- **Location**: `expo-location` + `expo-task-manager` for background tracking; store points in `expo-sqlite` so rides survive crashes/kills.
- **Sensors/health**: `react-native-ble-plx` (v2), `react-native-health` / Health Connect (v2).
- **UI**: NativeWind or Tamagui, Reanimated + Skia/Lottie for XP/badge celebrations, `expo-haptics`.
- **Backend**: Supabase (Postgres + PostGIS, Auth, Storage, Realtime, Edge Functions). PostGIS handles segment matching and geo-queries. Alternative considered: custom Node API — more work, no benefit at MVP.
- **Notifications**: `expo-notifications` + Expo push service.
- **Quality**: Jest + React Native Testing Library, Maestro for E2E, ESLint/Prettier, Sentry, PostHog analytics.
- **CI/CD**: GitHub Actions + EAS Build/Submit/Update (OTA).

## Architecture
```
app/                    Expo Router screens
  (auth)/  (tabs)/{feed,record,challenges,clubs,profile}/  ride/[id]  segment/[id]
src/
  features/{recording,feed,gamification,segments,clubs,profile}/
    components/ hooks/ api/ store/
  lib/{supabase,location,sqlite,notifications,analytics}/
  ui/                   design-system primitives
supabase/
  migrations/  functions/ (process-ride, award-xp, weekly-challenges)  seed.sql
```

### Key data model (Postgres/PostGIS)
`profiles`, `bikes`, `rides` (polyline, `geography` linestring, stats), `ride_points` (optional, raw), `follows`, `kudos`, `comments`, `segments` (linestring), `segment_efforts`, `leaderboards` (view/materialized), `xp_events`, `badges`, `user_badges`, `streaks`, `challenges`, `challenge_participants`, `clubs`, `club_members`, `notifications`. Row-Level Security on all tables; privacy zones (hide start/end radius) applied server-side.

### Core flows
- **Ride recording**: background task appends points to SQLite → on finish, simplify (Douglas-Peucker), compute stats, upload → Edge Function `process-ride` does segment matching (`ST_DWithin`/`ST_LineLocatePoint`), awards XP/badges, updates streaks and challenge progress, enqueues push notifications. Idempotent by ride ID so offline retries are safe.
- **Gamification engine**: server-authoritative rules table-driven (XP formulas, badge criteria in JSON) so tuning needs no app release. Anti-cheat: speed/GPS sanity checks, flag e-bike/motor-vehicle speeds, ignore rides with impossible jumps.

## Milestones
1. **Foundations (wk 1–2)**: repo, Expo + TS + Router, EAS dev builds, design system, Supabase project + auth + core schema, CI.
2. **Recording (wk 3–5)**: background GPS, SQLite buffer, live map/stats, ride summary, upload, battery/permission UX. *Highest technical risk — do first.*
3. **Social (wk 6–7)**: profiles, follow, feed, kudos/comments, photos.
4. **Gamification (wk 8–10)**: XP/levels, streaks, badges, challenges, celebration animations.
5. **Segments & clubs (wk 11–13)**: segment creation/matching, leaderboards, clubs, club challenges.
6. **Polish & beta (wk 14–16)**: notifications, onboarding, privacy zones, accessibility, perf, Sentry, TestFlight / Play internal testing.
7. **Launch + v2 backlog**.

## Risks & Mitigations
- **Background location reliability/battery** (iOS & Android OEM killers): prototype in week 3 on real devices; foreground service notification on Android; tune accuracy/distance filters.
- **Store review** for background location: clear usage strings and justification video.
- **Cheating/leaderboard integrity**: server-side validation, flagging, manual review tool.
- **Privacy** (home location): privacy zones, per-ride visibility, GDPR export/delete.
- **Cold-start for social apps**: club/invite links, contact import, local-first challenges that work solo.
- **Map costs**: cap tile usage, offline packs, cache static thumbnails.

## Verification
- Unit tests: XP/streak/badge rules, polyline simplification, stats computation.
- SQL tests (pgTAP) for segment matching and RLS policies.
- Field tests: record real rides on iOS + Android (screen locked, app backgrounded, low-power mode); compare distance with a reference bike computer (±2%).
- Maestro E2E: sign-up → record (mocked GPS route) → ride appears in feed → XP/badge awarded → leaderboard updated.
- Beta via TestFlight/Play internal track with ~20 riders; monitor crash-free rate (>99%) and recording success rate.

## Open Questions for the user
- Target launch platforms (iOS-first or both)?
- Road vs. MTB vs. mixed focus (affects segments, safety, and badges)?
- Monetization (free + premium for analytics/challenges)?
- Preference on backend (Supabase assumed).
