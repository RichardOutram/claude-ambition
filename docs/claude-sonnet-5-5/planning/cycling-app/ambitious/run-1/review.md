## Our review

**Plain answer (1,061 words) and plain push (2,043 words).** A sound, conventional plan: Expo with dev builds, Supabase and PostGIS, background GPS saved to SQLite, XP, streaks, badges, segments and clubs in v1. The push adds an XP table, screens, a recording spec, metrics and a first-two-weeks list. It names the real risks: background GPS, store review for background location, privacy zones and cheating. It has no sizes and no acceptance criteria, and its costs are unpriced. The scope is large for a v1: segments, clubs, a paid tier and 60 badges.

**Plugin final (6,579 words, plus tools).** A build blueprint rather than an outline:
- **37 tickets**, each with a size, its prerequisites and a testable acceptance criterion. A checker confirms the build order and computes the schedule: about 13 weeks for 3 developers, with a release train that reaches 12 real riders sooner.
- **Two things the plain plans miss that would bite a real team.** First, Google Play makes new personal accounts run a 14-day closed test with 12 testers before launch, so the plan recruits those testers in week 1. Second, a simple privacy zone around home can be undone: its own simulation recovers the home point exactly from 3 rides. So it hides home with a secret offset and jitter, puts follower approval first, and says plainly that the zone only reduces exposure. We re-ran both simulations and they reproduce the plan's figures.
- **Safety by design.** No speed leaderboards or segments in v1, rewards shown only after a ride ends, and notifications held while recording. The plain plans keep KOMs.
- **Smaller, fairer scope.** Quests are set from each rider's own history, which its simulation shows keeps completion rates even across rider types.
- **Pricing fetched and dated**, with a cost per month at 1k, 10k and 50k users.
- **A ready GPS spike app** gates the recording work. It has not been run on a phone, and the plan says so.

Its checker (`plan_lint.py`) passes 49/49 when we re-run it.

**Where it falls short:**
- Its reason for cyclists to switch ("fair, safe and private") is a set of principles, not a wedge Strava lacks.
- It defers sensors, Health and Strava import entirely, with reasons. The plain push at least sketches them for v2.
- It is more than three times the length of the plain push.

**Verdict: better.** Someone could start building from it on Monday, which isn't true of the plain plans. It cost $3.06 and 20 minutes, against $0.24 and 2.4 minutes for the plain push.
