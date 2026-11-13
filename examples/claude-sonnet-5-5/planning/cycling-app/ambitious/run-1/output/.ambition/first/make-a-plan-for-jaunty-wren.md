# Plan: "Peloton Pals"-style Social Gamified Cycling Tracker (React Native + Expo)

Working name: **SpokeQuest** (placeholder).

## Context
Cyclists use Strava for tracking and social, but its gamification is thin (segments/KOMs, kudos). Casual and commuter cyclists lack motivation hooks like streaks, quests, and team play. SpokeQuest is a cycling-only app that records rides, then layers on XP/levels, quests, territory capture, clubs, and a social feed. Greenfield project in `/Volumes/My Shared Files/work` (currently empty), so no existing code to reuse.

## Target users
Commuters, weekend road/gravel/MTB riders, and club groups. Cycling-specific: elevation, cadence/power (BLE), segments, group rides, bike maintenance.

## MVP scope (v1)
1. Auth and profile (email, Apple, Google), bike garage.
2. GPS ride recording (foreground + background), live stats, auto-pause.
3. Ride summary: map, elevation, splits, XP earned.
4. Gamification: XP, levels, streaks, badges, weekly quests.
5. Social: follow, feed, kudos, comments, clubs, club leaderboards.
6. Push notifications.

Post-MVP: BLE sensors (HR/power/cadence), territory capture ("Zones"), live group rides, segments, Strava/Garmin/Apple Health import, challenges with sponsors, subscription tier, bike maintenance tracker.

## Tech stack
- **Expo SDK (current) + TypeScript**, dev builds via EAS (required for background location and BLE; Expo Go is insufficient).
- Navigation: **Expo Router** (file-based).
- State: **Zustand** (local/ride state) + **TanStack Query** (server state).
- Maps: **react-native-maps** or **@rnmapbox/maps** (Mapbox preferred for custom styling, offline tiles, route layers).
- Location: **expo-location** + **expo-task-manager** (background updates); persist points in **expo-sqlite** during the ride so crashes don't lose data.
- Sensors: **react-native-ble-plx** (post-MVP), **expo-sensors** for barometer/altitude assist.
- Animations/gamification UI: **react-native-reanimated**, **Lottie**, **expo-haptics**.
- Backend: **Supabase** (Postgres + PostGIS, Auth, Storage, Realtime, Edge Functions). Rationale: geo queries, RLS, realtime feed/leaderboards, low ops. Alternative considered: Firebase (weaker geo/relational queries).
- Notifications: **expo-notifications**; Edge Function cron for streak reminders.
- Analytics/crash: PostHog + Sentry.
- Testing: Jest + React Native Testing Library, Maestro for E2E, Vitest/pgTAP for backend logic.
- CI/CD: GitHub Actions + EAS Build/Submit/Update.

## Architecture
```
app/                    Expo Router screens
  (auth)/ (tabs)/{feed,record,quests,clubs,profile}/ ride/[id].tsx
src/
  features/{rides,gamification,social,clubs,garage}/  (components, hooks, api, store)
  services/{location,backgroundTask,ble,notifications,supabase}/
  lib/{geo,units,xp,polyline}/   pure, unit-tested logic
  ui/                    design system (tokens, Button, Card, Badge, StatRing)
supabase/{migrations,functions,seed.sql}
```
Key design points:
- **Ride recorder** is a state machine (idle → recording → paused → finished) in `services/location`; points buffered to SQLite, batch-uploaded on finish with a polyline-simplified track (Douglas-Peucker) plus raw GPX in Storage.
- **XP is computed server-side** (Edge Function on ride insert) to prevent cheating; client shows an optimistic estimate. Anti-cheat: speed/teleport sanity checks, e-bike/vehicle detection via speed profile, flagged rides excluded from leaderboards.
- Offline-first: rides saved locally and synced when online (queue with retry).

## Data model (Postgres/PostGIS)
`profiles`, `bikes`, `rides` (geometry LineString, distance, moving_time, elevation_gain, avg/max speed, status), `ride_points` (optional, archived), `follows`, `kudos`, `comments`, `clubs`, `club_members`, `xp_events`, `badges`, `user_badges`, `quests`, `user_quests`, `streaks`, `notifications`, later `segments`, `segment_efforts`, `zones`, `zone_claims`. RLS on all tables; privacy zones (hide start/end within radius of home) applied server-side before publishing to feed.

## Gamification design
- **XP**: distance, elevation, consistency bonus, first-time routes, quest completion. Level curve ~ `100 * level^1.5`.
- **Streaks**: weekly ride streak (forgiving: 1 freeze/month) rather than daily, to avoid burnout.
- **Quests**: weekly rotating (e.g. "Climb 800 m", "3 rides on different days"), plus seasonal quests.
- **Badges**: distance milestones, climbing, early bird, rain rider, explorer (new geohash tiles).
- **Explorer map**: fog-of-war of visited geohash tiles — visual progress and a post-MVP "Zones" capture mechanic.
- **Clubs**: weekly club goals and leaderboards; club vs club challenges.
- **Leaderboards**: friends, club, local area; weekly resets so newcomers can compete.
- Reward moments: confetti/Lottie on level-up, haptics, shareable ride card image (`react-native-view-shot`).

## Milestones
| Phase | Duration | Deliverable |
|---|---|---|
| 0. Setup | 1 wk | Expo + TS repo, EAS, lint/test/CI, Supabase project, design tokens |
| 1. Recording | 3 wk | Auth, profile, background GPS recorder, SQLite buffer, ride summary + map |
| 2. Gamification core | 2 wk | XP/levels, streaks, badges, weekly quests (server-side logic + UI) |
| 3. Social | 3 wk | Follow, feed, kudos/comments, clubs, leaderboards, privacy zones |
| 4. Polish + beta | 2 wk | Notifications, onboarding, share cards, accessibility, TestFlight / Play internal |
| 5. Launch | 1 wk | Store listings, privacy policy, review submission |
| Post-MVP | ongoing | BLE sensors, Zones, segments, integrations, premium tier |

## Risks and mitigations
- **Background location reliability (iOS/Android battery policies)**: dev-build testing on real devices early (Phase 1), foreground service notification on Android, document battery exemptions.
- **Battery drain**: adaptive accuracy/distance filter by speed.
- **Privacy/GDPR**: privacy zones, private-by-default option, data export/delete, location permission rationale copy.
- **Cheating / vehicle rides**: server-side validation and flagging.
- **Cold-start social graph**: contacts import, clubs-first onboarding, solo-friendly quests.
- **Store review**: background-location justification text and demo video.

## Critical files (to be created)
`app.config.ts` (permissions, background modes), `src/services/location/recorder.ts`, `src/services/backgroundTask/locationTask.ts`, `src/lib/xp/calc.ts`, `supabase/migrations/0001_init.sql`, `supabase/functions/score-ride/index.ts`, `app/(tabs)/record/index.tsx`.

## Verification
- Unit tests: `lib/xp`, `lib/geo` (distance, elevation smoothing, simplification), recorder state machine.
- Backend: pgTAP/RLS tests; Edge Function tests with fixture GPX files (normal ride, car ride, GPS-jump ride).
- Manual device test: 30-min real ride on iOS and Android with screen locked, verify no gaps, correct distance (±2% vs reference device), XP/streak/quest updates.
- E2E (Maestro): sign up → record simulated ride (mock location) → summary → feed post → kudos from second account → club leaderboard update.
- Beta: TestFlight/Play internal with ~20 riders; track crash-free sessions (>99%) and ride-save success rate.

## Open questions for the user
- Solo build or team? (affects timeline)
- Monetization (free + premium vs. fully free)?
- Mapbox vs. Google/Apple maps preference/budget?
- Launch region and iOS-first or both platforms?
