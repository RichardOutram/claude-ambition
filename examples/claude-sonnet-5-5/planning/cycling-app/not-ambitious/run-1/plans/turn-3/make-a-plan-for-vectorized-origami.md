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

## Decisions (confirmed by user)
- **Platforms**: iOS and Android launch together. Test every milestone on both; Android OEM background-kill behavior is tested from week 3.
- **Focus**: Road cycling first, including gravel. Ride types: road, gravel, indoor-excluded for v1. Segments, leaderboards, streaks, and badges are tuned for road/gravel (e.g. climb categories, gravel-distance badges, surface tag on segments). MTB is a later expansion; keep the `ride_type` field extensible so adding it needs no migration.
- **Monetization**: Free core with an optional paid tier ("Pro").
  - **Always free**: ride recording, feed, follows, kudos/comments, basic XP/streaks/badges, segments and leaderboards, joining clubs and standard challenges.
  - **Pro (subscription)**: advanced stats (training load, power/climb analysis, trends), extra/premium challenges, club admin tools (analytics, custom challenges, member management beyond basics).
  - **Implementation**: RevenueCat (`react-native-purchases`) for iOS/Android subscriptions; entitlement synced to a `subscriptions` table via webhook Edge Function; RLS and Edge Functions enforce Pro-only features server-side. Paywall UI added in the Polish & beta milestone; Pro features gated behind a single `useEntitlement()` hook. Never gate recording or core social features.
- **Backend**: Supabase, as planned.

## Plan changes from these decisions
- Milestone 1: add RevenueCat and store-account setup (App Store Connect + Play Console) alongside EAS.
- Milestone 6 (Polish & beta): add paywall, subscription management, restore purchases, and store subscription metadata; beta includes both TestFlight and Play internal testing.
- Data model: add `subscriptions` (user_id, entitlement, status, expires_at), `rides.ride_type` (road|gravel, extensible), `segments.surface` (paved|gravel|mixed).
- Verification: add sandbox-purchase tests on both platforms and a test that Pro endpoints reject free users while core flows remain open.
- Risk: clubs-vs-Pro boundary could hurt growth; mitigate by keeping basic club features free and reviewing conversion/retention in beta before finalizing tiers.


---

# Deep Dive (detailed design)

## A. Gamification design (the differentiator)
**Principle**: reward consistency and exploration, not just speed, so casual riders and racers both progress. Everything is server-computed from rules tables.

| System | Design |
|---|---|
| **XP** | Base 10 XP/km (cap 300/ride), +1 XP per 10 m climbed (cap 200), +50 first ride of the day, +25 for newly explored roads (unvisited H3 cells), +100 segment PR, +250 KOM/QOM. Diminishing returns past 3 rides/day. |
| **Levels** | 1–100, curve `xp(n) = 500 * n^1.5`; titles per tier (Commuter → Domestique → Climber → Rouleur → Legend). Level-ups unlock cosmetics (bike icons, map line colors, profile frames). |
| **Streaks** | Weekly (≥1 ride ≥5 km). 1 freeze token earned per 4-week streak, max 2 banked. "Streak at risk" push Saturday evening local time. |
| **Badges** | Distance (100/500/1000 km), climbing (Everesting progress, 1,000 m/ride), gravel (first 50 km gravel), time-of-day (Early Bird), exploration (10 new segments), social (first 10 kudos, club founder), seasonal. ~60 at launch, JSON criteria so new ones ship without releases. |
| **Challenges** | Weekly solo (distance/climb/ride count), monthly club-vs-club, sponsored/Pro. Auto-generated by the `weekly-challenges` cron, scaled to the user's 4-week average (+15%) so goals feel achievable. |
| **Segments** | KOM/QOM, Local Legend (most efforts in 90 days), and a Personal Best ladder so slower riders stay engaged. |
| **Seasons (v2)** | 8-week seasons, leagues (Bronze→Diamond) by weekly XP, promotion/relegation on Mondays. |

**Guardrails**: no XP boosts for risky behavior (night/weather), rest-week freezes, never shame missed streaks in copy.

## B. Screen inventory (MVP)
- **Onboarding**: welcome → riding style (road/gravel) → weekly goal → permission priming (location "Always", notifications, motion) → follow suggestions / join club.
- **Tabs**: Feed · Record · Challenges · Clubs · Profile.
- **Record**: pre-ride (bike picker, segment preview) → live (map, big-number stats, pause, lock-screen controls) → summary (map, splits, XP animation, badges, photos, privacy toggle, share).
- **Detail**: ride, segment (leaderboard tabs: Friends/Club/Local/All-time), challenge, club, user profile, badge shelf, XP history, settings (privacy zones, units, notifications, delete account), paywall.

## C. Recording engine spec (highest risk)
- `expo-location` background task: `Accuracy.BestForNavigation`, `distanceInterval` ~5 m, iOS `activityType = Fitness`, `pausesUpdatesAutomatically=false`; Android foreground service with persistent notification.
- Point filtering: reject accuracy >30 m, reject speed >25 m/s, smooth with Kalman/low-pass, elevation from barometer fused with GPS, server-side DEM correction fallback.
- Auto-pause below 1.5 km/h for 5 s, with resume detection.
- Crash recovery: on launch, detect an unfinished SQLite session and offer Resume / Save / Discard.
- Upload queue: persisted, exponential backoff, resumes on connectivity; client-generated UUID ride ID for idempotency.
- Acceptance: ±2% distance vs reference device, <8% battery/hour with screen off, zero lost rides over 50 test rides including forced app kills.

## D. Backend detail
- **Edge Functions**: `process-ride`, `weekly-challenges` (cron), `revenuecat-webhook`, `delete-account` (GDPR cascade), `export-data`.
- **Feed**: fan-out-on-read via a view joining `follows` and `rides`, keyset pagination, TanStack infinite queries. Move to materialized per-user feeds only if p95 >300 ms.
- **Realtime**: only kudos/comment counts and challenge progress for MVP; no live tracking.
- **Storage**: signed photo uploads with image transforms; static map thumbnails generated once and cached.
- **Moderation**: report/block on all UGC, profanity filter on comments, simple admin review queue.
- **Geo privacy**: privacy zones (default 200 m around home/work) trimmed server-side before publishing; raw data visible only to owner.

## E. Metrics
- North star: weekly active riders completing ≥1 ride.
- Activation: ≥40% of new users record a first ride within 7 days.
- Retention: W1 35%, W4 20%; compare streak holders vs non-holders.
- Social: kudos per ride, % users with ≥3 follows, club join rate.
- Monetization: paywall view → trial → paid; target 3–5% paid conversion.
- Reliability: crash-free sessions >99.5%, ride-save success >99.9%.
- PostHog events from day one: `ride_started`, `ride_saved`, `xp_awarded`, `badge_earned`, `challenge_joined`, `paywall_viewed`.

## F. Growth & launch
- Seed 5–10 local clubs/ambassadors pre-launch; club invite deep links (universal links via Expo Router).
- Shareable ride/badge/level-up cards (`react-native-view-shot`).
- Strava import to remove switching cost (verify API terms before committing; export is optional).
- Waitlist landing page; ASO around "cycling tracker", "gravel", "bike challenges".
- Soft launch in one region to tune challenge difficulty and server load.

## G. Legal & compliance
- Privacy policy and ToS before beta; in-app GDPR/CCPA export and delete; age gate per region.
- Google Play background-location declaration with demo video; accurate iOS usage strings.
- No medical claims. Display Mapbox/OSM attribution.

## H. Engineering practices
- Strict TS, path aliases, feature-folder boundaries (cross-feature imports only via `index.ts`).
- `dev` / `staging` / `prod` Supabase projects mapped to EAS profiles; secrets in EAS and Supabase vault.
- Supabase CLI migrations, generated types committed, zod at API boundaries.
- CI: lint + typecheck + jest + pgTAP on PRs, EAS preview builds; OTA only for JS-safe changes.
- Upgrade the Expo SDK within 4 weeks of each release.

## I. First-two-weeks task breakdown
1. `create-expo-app` (TypeScript, Expo Router); ESLint/Prettier/Husky; path aliases.
2. EAS config (`eas.json` dev/preview/prod), bundle IDs, icons/splash; first dev-client builds on real iOS and Android devices.
3. Three Supabase projects; initial migration (profiles, rides, follows, RLS) + generated types; auth screens (email, Apple, Google).
4. Design tokens and primitives (Button, Card, Stat, Avatar, ProgressBar, Sheet), light/dark themes.
5. Tab shell, navigation, empty states; Sentry + PostHog wired in.
6. GitHub Actions for lint/typecheck/test and EAS preview builds.
7. **Spike (end of week 2, go/no-go)**: bare-bones background recorder to SQLite, run a 1-hour ride on 2 iOS + 2 Android devices (including Samsung and Xiaomi) before committing to milestone 2.

## J. Open items to resolve during build
- Pro pricing (starting hypothesis ~$4.99/mo, ~$39.99/yr; test via RevenueCat experiments).
- App name, branding, bundle IDs.
- Mapbox vs MapLibre cost review once usage projections exist.
- Strava API terms for import/export.
