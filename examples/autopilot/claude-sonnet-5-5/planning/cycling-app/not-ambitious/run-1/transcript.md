# plan/cycling-app · not-ambitious

### User

Make a plan for a react native expo social gamified fitness tracker app for the cycling niche, and save it to disk

**→ Write** `{"file_path": "/cfg/plans/make-a-plan-for-vectorized-origami.md", "content": "# Cycling Social Fitness App (React Native + Expo) \u2014 Plan\n\n## Context\nBuild a social, gamified fitness tracker for cyclists. Existing apps (Strava) are social but shallow on game mechanics; gamified apps (Zwift) are indoor-focused. Opportunity: outdoor-first ride tracking with territory/segment games, streaks, ch … [6367 more chars]`

<details><summary>result</summary>

```
File created successfully at: /cfg/plans/make-a-plan-for-vectorized-origami.md (file state is current in your context — no need to Read it back)
```

</details>

**→ ToolSearch** `{"query": "select:ExitPlanMode", "max_results": 1}`

<details><summary>result</summary>

```

```

</details>

**→ ExitPlanMode** `{"plan": "# Cycling Social Fitness App (React Native + Expo) \u2014 Plan\n\n## Context\nBuild a social, gamified fitness tracker for cyclists. Existing apps (Strava) are social but shallow on game mechanics; gamified apps (Zwift) are indoor-focused. Opportunity: outdoor-first ride tracking with territory/segment games, streaks, challenges, and club-based social features. Greenfield project (workin … [6367 more chars]`

<details><summary>result</summary>

```
User has approved your plan. You can now start coding. Start with updating your todo list if applicable

Your plan has been saved to: /cfg/plans/make-a-plan-for-vectorized-origami.md
You can refer back to it if needed during implementation.

## Approved Plan:
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
- **App**: Expo SDK (latest) + TypeScript, **Expo Router** (file-based nav), dev builds via **EAS Bu … [4774 more chars]
```

</details>

### Assistant

I've written the plan for the cycling app and saved it to `/cfg/plans/make-a-plan-for-vectorized-origami.md`. Nothing has been built yet.

- **Stack:** Expo with TypeScript and Expo Router, Mapbox for maps, and Supabase (Postgres with PostGIS) as the backend. Background GPS needs EAS dev builds, not Expo Go.
- **MVP:** Ride recording that works offline, a social feed (follows, kudos, comments), XP, levels, streaks, badges, weekly challenges, segments with leaderboards, clubs, and push notifications.
- **v2:** Territory capture on the map, group rides, sensor and health integrations, and safety features.
- **Timeline:** About 16 weeks. Ride recording comes first because background GPS and battery use are the biggest technical risk.
- **Cheating and privacy:** Gamification rules and anti-cheat checks run on the server. Privacy zones hide start and end points.
- **Verification:** Unit tests for the XP, streak and badge rules, database tests for segment matching and access rules, and field rides checked against a bike computer. There is also an end-to-end flow test and a TestFlight/Play internal beta.

The plan lists four open questions, and I assumed Supabase for the fourth:
- Which platforms to launch on (iOS first, or both).
- Whether to focus on road, mountain biking or both.
- How to make money.
- Whether you prefer a different backend.

### User

Here are my answers to the four open questions:

- **Platforms:** Launch on iOS and Android together. Cyclists are split pretty evenly across both, and Expo makes it cheap to do both.
- **Focus:** Road cycling first, including gravel. The segments, leaderboards and streaks fit road riders best, and mountain biking can come later.
- **Money:** Free to use, with an optional paid tier for things like advanced stats, extra challenges and club tools. Core ride recording and the social features stay free so the community can grow.
- **Backend:** Supabase is fine, so keep it.

Please update the plan with these answers and finish it.

**→ Read** `{"file_path": "/cfg/plans/make-a-plan-for-vectorized-origami.md", "offset": 84}`

<details><summary>result</summary>

```
84	- Preference on backend (Supabase assumed).
85	
```

</details>

**→ Edit** `{"replace_all": false, "file_path": "/cfg/plans/make-a-plan-for-vectorized-origami.md", "old_string": "## Open Questions for the user\n- Target launch platforms (iOS-first or both)?\n- Road vs. MTB vs. mixed focus (affects segments, safety, and badges)?\n- Monetization (free + premium for analytics/challenges)?\n- Preference on backend (Supabase assumed).\n", "new_string": "## Decisions (confirmed … [2139 more chars]`

<details><summary>result</summary>

```
The file /cfg/plans/make-a-plan-for-vectorized-origami.md has been updated successfully.
```

</details>

### Assistant

I've updated the plan at `/cfg/plans/make-a-plan-for-vectorized-origami.md` with your four answers, replacing the open-questions section. I haven't started building anything.

- **Platforms:** iOS and Android launch together. Every milestone is tested on both, and Android background-kill testing starts in week 3.
- **Focus:** Road and gravel only for v1. Segments carry a surface tag (paved, gravel or mixed), and the ride type field can take mountain biking later without a migration.
- **Money:** Core recording, the social features, standard challenges and basic club membership stay free. Pro covers advanced stats, extra challenges and club admin tools. RevenueCat handles subscriptions on both stores, and the server enforces Pro-only features.
- **Backend:** Supabase, unchanged.

I also made these changes to the milestones, data model and checks:
- **Milestone 1:** RevenueCat and the App Store and Play Console accounts are set up here.
- **Polish and beta milestone:** It now includes the paywall, subscription management and restore purchases.
- **Data model:** Added a `subscriptions` table, a `ride_type` field on rides, and a `surface` field on segments.
- **Verification:** Added sandbox-purchase tests on both platforms, plus a check that free users are rejected from Pro endpoints while core flows stay open.
- **New risk:** Putting some club tools behind Pro could slow growth. I've noted checking conversion and retention in the beta before fixing the tiers.

I left indoor rides out of v1, which you didn't mention either way. Say so if you want them in.

### User

Push it further.

**→ Edit** `{"replace_all": false, "file_path": "/cfg/plans/make-a-plan-for-vectorized-origami.md", "old_string": "review conversion/retention in beta before finalizing tiers.\n", "new_string": "review conversion/retention in beta before finalizing tiers.\n\n---\n\n# Deep Dive (detailed design)\n\n## A. Gamification design (the differentiator)\n**Principle**: reward consistency and exploration, not just speed … [7922 more chars]`

<details><summary>result</summary>

```
<tool_use_error>String to replace not found in file.
String: review conversion/retention in beta before finalizing tiers.
</tool_use_error>
```

</details>

**→ Bash** `{"command": "tail -c 300 /cfg/plans/make-a-plan-for-vectorized-origami.md | cat -A | tail -3"}`

<details><summary>result</summary>

```
cat: illegal option -- A
usage: cat [-belnstuv] [file ...]
```

</details>

**→ Bash** `{"command": "tail -n 2 /cfg/plans/make-a-plan-for-vectorized-origami.md"}`

<details><summary>result</summary>

```
- Verification: add sandbox-purchase tests on both platforms and a test that Pro endpoints reject free users while core flows remain open.
- Risk: clubs-vs-Pro boundary could hurt growth; mitigate by keeping basic club features free and reviewing conversion/retention in beta before finalizing tiers.
```

</details>

### Assistant

I'll append with a heredoc, since the file's last line has no trailing newline to anchor on.

**→ Bash** `{"command": "cat >> /cfg/plans/make-a-plan-for-vectorized-origami.md <<'EOF'\n\n\n---\n\n# Deep Dive (detailed design)\n\n## A. Gamification design (the differentiator)\n**Principle**: reward consistency and exploration, not just speed, so casual riders and racers both progress. Everything is server-computed from rules tables.\n\n| System | Design |\n|---|---|\n| **XP** | Base 10 XP/km (cap 300/ri … [6750 more chars]`

<details><summary>result</summary>

```
     179 /cfg/plans/make-a-plan-for-vectorized-origami.md
```

</details>

### Assistant

I took "push it further" to mean making the plan more detailed, so I added a "Deep Dive" section to `/cfg/plans/make-a-plan-for-vectorized-origami.md`. The file is now about 180 lines. I haven't built anything.

The new sections cover:
- **Gamification design:** XP rules, a level curve, streak freezes, about 60 launch badges, auto-scaled challenges, and the segment ladders. It also sets guardrails against rewarding risky riding.
- **Screens:** The full MVP screen list, from onboarding through the record flow to the detail and settings screens.
- **Recording engine:** GPS settings, filtering of bad points, auto-pause, recovery after a crash, and an upload queue that survives going offline. Acceptance targets are ±2% distance and under 8% battery per hour.
- **Backend:** The Edge Functions, how the feed is built, moderation, and privacy zones.
- **Metrics, growth, legal and engineering practices:** Targets for activation, retention and Pro conversion. Launch tactics include club invite links, shareable ride cards, Strava import and a one-region soft launch. Also covered are compliance and environments/CI.
- **First two weeks:** A seven-step task list. It ends with a go/no-go spike: record a one-hour ride on two iOS and two Android devices, including Samsung and Xiaomi, before committing to the recording milestone.
- **Open items:** Pro pricing (a starting guess of about $4.99 a month or $39.99 a year), the app name, a Mapbox versus MapLibre cost review, and the Strava API terms.

The numbers in it (XP values, the level curve, retention and conversion targets, the pricing guess) are starting guesses. The beta should tune them.

The file also changed on disk after I wrote to it. I didn't look at what changed, so I've left it as is.

If you want the plan pushed further in a different direction, I could write out the database schema in SQL, wireframe the key screens, or turn the first two weeks into tickets. I could also start scaffolding the Expo project.
