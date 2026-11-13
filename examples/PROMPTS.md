# Example prompts

The examples the bench runs. Each has three parts:

- **Prompt:** exactly what a user would type. Both runs get this, word for word. It always names the deliverable's form (a single web page, a Markdown file, a script), or the mode does, so both runs make the same kind of thing and get reviewed the same way.
- **Mode** (optional): `plan` sends the prompt with plan mode on in both runs, the way people ask Claude Code for a plan (shift+tab, then the prompt). Only the prompt's turn is in plan mode; the user carries on in the chat after the first plan.
- **Brief:** what the user knows but didn't type. It's context for us when reviewing. The stand-in user never sees it, so both runs get exactly the same information.
- **Check:** what we look at when we review. Objective checks come first, then a rubric.
- **Walk** (optional): for pages whose substance is behind clicks (apps, games, lessons), a fixed path the review clicks through on every version, taking a screenshot after each step. Start with `phone ·` or `desktop ·` for the screen size. Steps are separated by `→`. A step is button or link text, with alternatives separated by ` / ` (the first visible match is clicked, ignoring case), and ` x4` after it clicks again while a match still shows, up to 4 times, for onboarding with several screens; `key ArrowRight x3` presses a key; `scroll` moves down one screen; `wait 3` waits 3 seconds. A step a version has no match for is shown as not in that version, and the walk carries on.

Prompts are deliberately ordinary, the way people actually ask.

Slugs map to `examples/<model>/<category>/<slug>/<arm>/`.

---

## Three.js

### threejs/neon-implosion
**Prompt:** Create a vivid pointer interactive abstract neon art solar system particle implosion, a 10 second looping animation in three.js, as a single web page.
**Brief:** It's for a loop on a portfolio site and social posts. It should look striking full screen on a laptop and a phone.
**Check:** Open it and watch several loops at desktop and phone sizes. It must render without errors, loop seamlessly every 10 seconds with no visible jump, and hold a smooth frame rate. Rubric: how vivid and striking it is, whether it clearly reads as a solar system imploding into particles, and craft (colour, glow, motion, timing).

### threejs/ferrofluid-fauvist
**Prompt:** Pointer-guided ferrofluid spikes in wild fauvist orange and violet, flickering through zoetrope frames as magnets pull, a 10 second looping animation in three.js, as a single web page.
**Brief:** Made from random scraped fragments: ferrofluid · fauvism · zoetrope. To see how the method handles an odd, open-ended art brief.
**Check:** Open it and watch several loops at desktop and phone sizes. It must render without errors, loop seamlessly every 10 seconds with no visible jump, and hold a smooth frame rate. Rubric: how striking it is, whether every named element reads on screen, and craft (colour, motion, timing).

---

## Games

### game/puzzle
**Prompt:** Make an original puzzle game I can play in the browser, as a single web page
**Brief:** For a few minutes of play on a phone or laptop. It should be easy to learn and hard to master.
**Check:** Play it at desktop and phone sizes with mouse, touch and keyboard. No console errors; levels are solvable (solve them, or run any solver it ships). Rubric: originality of the core mechanic, how quickly a new player gets it, difficulty curve, game feel (feedback, animation, sound), and whether you want another go.
**Walk:** desktop · Play / Start → key ArrowRight x2 → Next → key ArrowUp x2 → key ArrowLeft x2 → key ArrowDown x2 → Levels / Level select

---

## Development

### dev/photo-dedupe
**Prompt:** Write a CLI that finds duplicate photos in a folder. *(fixture: hidden test images for the judge only)*
**Brief:** I have about 40k family photos across old phone backups. Many are the same photo resized, re-compressed or with stripped EXIF. Never delete anything automatically. I'm on macOS and comfortable with Python.
**Check:** The fixture has 200 images with 37 planted duplicate groups: exact copies, resized, re-encoded at JPEG quality 60, EXIF stripped, a 2% crop, and some near-identical burst shots that are *not* duplicates. Score precision and recall per group, runtime, and whether it is safe by default. Rubric: usability, and whether it explains why each match was made.

### dev/slow-csv
**Prompt:** This CSV parser is slow, can you speed it up? *(fixture: a naive Python parser plus a 200MB generated CSV)*
**Brief:** It runs in a nightly job that now takes 40 minutes. The output must be byte-identical. We can't add heavy dependencies.
**Check:** A hidden benchmark covering wall time and peak memory, a byte-identical diff on held-out CSVs (quoted newlines, BOM, CRLF, empty fields), and the existing tests.

### dev/rate-limit
**Prompt:** Add rate limiting to this API. *(fixture: a small Express or FastAPI app with 3 routes)*
**Brief:** It's a public API with free and paid tiers, running behind a load balancer on 3 instances. Abuse comes from login brute force.
**Check:** Hidden integration tests: limits hold across instances, login gets stricter limits, 429 responses include Retry-After, and paid tiers get higher limits. The judge also tries to bypass it.

### dev/cycling-prototype
**Prompt:** Build a clickable prototype of the app in plan.md that I can open as a single html file *(fixture: plain Claude's first cycling-app plan)*
**Brief:** To feel the app's core loop on a phone-sized screen before committing to the Expo build, and to show a couple of riders.
**Check:** Open it at phone size (and desktop). No console errors; every tap target leads somewhere; the core loop (record a ride → save → reward → feed → club) works end to end with believable data. Rubric: how true it is to the plan, how much it feels like a real native app, how well the gamification lands, and whether it surfaces problems in the plan.
**Walk:** phone · Sign in / Log in → Allow location / Look around first / Get started / Skip / Not now / Continue x4 → Challenges → Clubs → Profile / You → Record → Start / Start ride / Go → wait 5 → Finish / Stop / End → Save / Save ride / Done

### dev/photo-rename
**Prompt:** Write a Python script that renames my photos by the date they were taken
**Brief:** A few thousand photos from phones and a camera in one folder, some without EXIF, some HEIC. On macOS. Nothing must be lost or overwritten.
**Check:** Run it on a test folder with JPEG, HEIC and PNG files, missing and broken EXIF, two photos taken in the same second and a name that already exists. No file lost or overwritten; a dry run by default or an undo. Rubric: safety, clarity of output, and ease of use.

### dev/url-shortener-architecture
**Prompt:** Design the architecture for a URL shortener that handles 10k requests a second, as a Markdown file
**Brief:** A small team will build and run it on AWS. Reads far outnumber writes; links must never break.
**Check:** Recompute the capacity and storage arithmetic. Check that each component is justified by the load, the failure modes (cache stampede, hot keys, region outage, ID collisions), cost per month, and abuse handling. Rubric: whether a senior engineer would sign it off and whether the team could build from it.

---

## Data analysis

### data/churn-signal
**Prompt:** Here's our subscription data. What's going on with churn? *(fixture: generated CSVs of users, events and billing)*
**Brief:** Leadership believes churn is an onboarding problem. I need something we can act on this quarter.
**Check:** The data has a planted cause. Churn is driven by a billing-retry bug that hits annual-plan renewals in one region, and onboarding is a red herring. A planted early signal appears 3 weeks before churn: support tickets mentioning "card". Score whether it finds the cause, rejects the red herring with evidence, finds the early signal, and validates on held-out data.

### data/sales-dashboard
**Prompt:** Make a dashboard from this sales spreadsheet. *(fixture: 18 months of messy sales xlsx data)*
**Brief:** The weekly sales meeting uses it to decide where to put two sales reps next quarter.
**Check:** Planted issues: duplicate rows, a currency mix-up in one region, and a seasonality trap. Score data cleaning, whether the dashboard answers the actual decision, and correctness against the planted truth.

### data/heat-pump
**Prompt:** Work out whether switching from my gas boiler to a heat pump would save me money, as a Markdown file
**Brief:** A 3-bed semi in the UK, about 12,000 kWh of gas a year, an ageing boiler. Grants exist but the user doesn't know the details.
**Check:** Recompute every figure: efficiency (SCOP), unit prices, standing charges, grants, install cost, payback. Check sources are current and named. Rubric: whether it answers the actual decision, handles uncertainty honestly (ranges, what would change the answer), and says what to measure or ask an installer.

---

## Design

### design/bakery-landing
**Prompt:** Design a landing page for a local bakery that takes pre-orders.
**Brief:** It's a small family bakery and most customers are on mobile. They want to cut phone orders, which tie up staff in the morning rush. Pre-orders close at 6pm for the next day.
**Check:** A single HTML file. Lighthouse scores (performance and accessibility), mobile screenshots at 375px, and whether a pre-order can be completed in fewer than 4 taps. Rubric: visual distinctiveness (not a template look), and whether the copy handles the 6pm cutoff.

### design/settings-screen
**Prompt:** Our app's settings screen is cluttered, redesign it. *(fixture: a screenshot plus a list of 34 settings)*
**Brief:** It's a mobile note-taking app. Support tickets show people can't find export or sync settings.
**Check:** Usability task test: a scripted walk-through finds 5 named settings and the number of steps is counted. Also score accessibility contrast and the rationale given for grouping.

### design/pricing-page
**Prompt:** Design a pricing page for an invoicing app for freelancers, as a single web page
**Brief:** A new product competing with bigger names. Most visitors arrive from a comparison article on a phone.
**Check:** Screenshots at 375px and desktop, Lighthouse (performance and accessibility). Rubric: whether a visitor can pick a plan in seconds, how it handles the comparison with bigger rivals, visual distinctiveness (not a template look), and honest copy.

---

## Planning

### plan/cron-to-queue
**Prompt:** Plan migrating our cron jobs to a job queue. *(fixture: a crontab with 23 jobs and their scripts)*
**Brief:** Jobs silently fail and nobody notices for days. It's a single server and the team is 3 people. There must be zero missed billing runs.
**Check:** The fixture has planted traps: two jobs that must not overlap, one that depends on another's output, and one that is dead code. Score whether the plan catches each trap, the rollback plan, how it verifies "zero missed billing runs", and how failures get noticed.

### plan/oss-launch
**Prompt:** Plan the launch of our open-source CLI tool.
**Brief:** It's a solo maintainer with 5 hours a week. The goal is 20 real users giving feedback within 2 months, not stars.
**Check:** Rubric: whether the plan targets the real goal (users and feedback, not vanity metrics), whether it is realistic at 5 hours a week, and whether it has measurable checkpoints. The judge also red-teams it.

### plan/cycling-app
**Prompt:** Make a plan for a react native expo social gamified fitness tracker app for the cycling niche, and save it to disk
**Mode:** plan
**Brief:** None: the prompt is all there is, typed with plan mode on, as people usually ask Claude Code for a plan. Plan mode is on for the prompt only: the user approves the plan, which ends plan mode and lets Claude save it, then carries on in the chat. Review the plan on how well it serves someone who typed exactly this.
**Check:** Rubric: whether it finds a real reason for cyclists to switch (a wedge Strava and Zwift don't cover) rather than generic badges and leaderboards; whether the Expo specifics hold up (background GPS and battery, BLE sensors such as power meters and heart-rate straps, HealthKit and Health Connect, Strava import, what needs a dev build rather than Expo Go, EAS); app store risks (background location review, privacy zones around home); an MVP small enough for one or two people with measurable milestones; how the gamification avoids rewarding unsafe riding; and how the plan would be checked against real riders before building it all.

### plan/team-offsite
**Prompt:** Plan a 3-day offsite for our team.
**Brief:** 12 engineers, £6k budget, UK. Last offsite was "fun but pointless". This one needs to produce a decision on next year's architecture.
**Check:** Budget arithmetic, whether the agenda produces the decision, and contingencies. Rubric: whether it addresses "pointless".

---

## Electronics

### elec/esp32-supply
**Prompt:** Design a power supply for an ESP32 sensor running on batteries.
**Brief:** Two AA cells. It wakes every 10 minutes and sends one reading over WiFi. Battery life should be as long as possible, and it's hand-soldered on through-hole parts where possible.
**Check:** Run the produced netlist in ngspice: regulator dropout across 2.0–3.2V, quiescent current, and WiFi transmit-burst droop. Check the battery-life calculation against an independent calculation. The real bar is deep-sleep current under 20µA. Score part availability and the BOM.

### elec/buttons
**Prompt:** How do I read 4 buttons on an Arduino?
**Brief:** I only have 1 analog pin free, it's a hobby project, and I want it reliable.
**Check:** Simulate the resistor ladder: worst-case ADC margins with 5% resistors and 5% supply variation, and debounce correctness. The firmware must compile with `arduino-cli`. Score whether it used the one-pin constraint at all.

---

## Writing

### write/readme
**Prompt:** Write a README for this repo. *(fixture: a small real repo with no README)*
**Brief:** It's an internal tool that new joiners struggle to set up.
**Check:** A fresh agent follows only the README to set the repo up from scratch in a clean container. Score whether it succeeds and how many steps it takes. Rubric: accuracy against the code.

### write/explain-https
**Prompt:** Explain how HTTPS works.
**Brief:** For a junior developer who keeps disabling certificate verification to "make it work".
**Check:** Technical accuracy is reviewed by the judge. Score whether it changes the reader's behaviour (does it address the verification habit?). Also run a 5-question comprehension test, answered by a fresh agent that has read only the explanation.

### write/candle-marketing
**Prompt:** Write a marketing plan for my handmade candle shop on Etsy, as a Markdown file
**Brief:** A one-person shop with about 20 sales a month, a few hours a week for marketing and a small budget. The goal is steady sales, not virality.
**Check:** Rubric: whether it fits the time and budget, whether its actions are specific enough to do this week, how it measures what works, Etsy specifics that hold up (search, listings, fees, ads), and whether it finds a real reason buyers choose this shop.

---

## Education

### learn/bayes
**Prompt:** Explain Bayes' theorem with an interactive visualisation, as a single web page
**Brief:** For someone who has heard of it but finds the formula opaque; the classic medical test example confuses them.
**Check:** Open it at desktop and phone sizes and use every control. No console errors; the numbers it shows are correct (check several settings by hand). Rubric: whether someone would understand base rates after using it, clarity, and craft.
**Walk:** desktop · scroll → About 10% / Observe E → Next → Next → Next → scroll → scroll
