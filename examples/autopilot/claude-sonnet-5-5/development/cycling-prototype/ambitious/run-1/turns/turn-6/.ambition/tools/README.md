Checks for prototype.html (run from this folder; needs Chrome + `npm i playwright-core`):
  node audit.js ../../prototype.html   # clicks every control on every screen; flags dead taps + console errors
  node flow.js  ../../prototype.html   # cold-start core loop: sign in -> record -> XP/badge -> challenge
  node fixes.js ../../prototype.html   # notification, share, + New club, settings, post-ride CTA
Known benign audit hits: re-tapping the tab or segment you are already on does nothing by design.
  node depth.js ../../prototype.html        # axe-core (WCAG A/AA) + 44px tap targets + overflow at 375x667
  node consistency.js ../../prototype.html  # speed=km/time, XP breakdown sums, segment rank matches leaderboard
  node probe.js ../../prototype.html        # edge cases: instant finish, challenge completion, streak card, level-up, reset, pricing label
  node redteam.js ../../prototype.html      # injection, overflow, discard/privacy/paywall guards, sign-out mid-ride, session log, next-up
  sh judge.sh                               # runs everything above + core loop + plan.md MVP coverage (node corpus.js a.html out.txt)
  node primary.js ../../prototype.html      # stretch T1: taps only the most prominent button; must reach the challenge screen in <=5 taps, <9 s
  node fuzz.js ../../prototype.html 1,2,3,4,5 800   # stretch T2: seeded random taps + nasty text + resizes + macro rides, with invariants (~4 min). Not in judge.sh because it is slow.
  Fuzz limits: catches uncapped counters and XP decreases (mutation-tested); the km and elevation challenge caps need far longer rides than the fuzz makes.
