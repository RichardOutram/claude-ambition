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