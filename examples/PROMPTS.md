# Example prompts

Local only (gitignored). Each example has three parts:

- **Prompt:** exactly what a user would type. Both runs get this, word for word.
- **Brief:** what the user knows but didn't type. The client agent answers `/be-ambitious`'s interview from it, and the optional `briefed` run gets it appended.
- **Check:** how the judge decides. Objective checks come first, then a rubric.

Prompts are deliberately ordinary, the way people actually ask. A planted or measurable ground truth is what makes a judgment fair.

Slugs map to `examples/<model>/<category>/<slug>/<arm>/`.

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

---

## Design

### design/bakery-landing
**Prompt:** Design a landing page for a local bakery that takes pre-orders.
**Brief:** It's a small family bakery and most customers are on mobile. They want to cut phone orders, which tie up staff in the morning rush. Pre-orders close at 6pm for the next day.
**Check:** A single HTML file. Lighthouse scores (performance and accessibility), mobile screenshots at 375px, and whether a pre-order can be completed in fewer than 4 taps. Rubric: visual distinctiveness (not a template look), and whether the copy handles the 6pm cutoff.

### design/settings-screen
**Prompt:** Our app's settings screen is cluttered, redesign it. *(fixture: a screenshot plus a list of 34 settings)*
**Brief:** It's a mobile note-taking app. Support tickets show people can't find export or sync settings.
**Check:** Usability task test: the judge agent finds 5 named settings and the number of steps is counted. Also score accessibility contrast and the rationale given for grouping.

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
