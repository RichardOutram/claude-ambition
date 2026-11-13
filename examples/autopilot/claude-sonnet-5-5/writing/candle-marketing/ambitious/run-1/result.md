## Final report

**You asked for → it became**
- **A marketing plan for my handmade candle shop on Etsy, as a Markdown file → a dated 24-week plan (Nov 16 to Apr 26) for your shop.** It's built on your numbers: about $1,200 a month, 25 listings, 5 hours a week and $150 a month. It aims at steady monthly sales ($2,000 in each of November and December, $3,000 a month by April) and gives you a way to find out what's working.
- **How each part of the ask was raised:**
  - **Generic tactic menu → ranked levers.** Each one has a budget, hours and a kill-or-keep rule.
  - **No numbers → a funnel model.** It shows the arithmetic, and a Week 1 diagnosis tells you whether listings or traffic are the bottleneck.
  - **Revenue only → a margin check.** I found that a $38 two-jar set earns about $4 profit, against about $13 for a plain jar.
  - **No check on feasibility → added production, safety and policy checks.** These cover a production calendar with cure time, ASTM F2058 labeling, FTC gift disclosure, Etsy review and email rules, and Offsite Ads status.
  - **Added a minimum viable week** (2.5 hours or less) so a bad week doesn't end the plan.

**Against the first version**
- **Better:** 14 of the 21 features I tested (dated schedule, arithmetic, scorecard, kill-or-keep rules, margin check, policy and safety, production calendar, shipping dates and others) were missing from the first version and are in the final.
- **Gave up:** nothing that the first version did better. My rewrite had dropped brand positioning and email flows, including a replenish reminder. The judge caught both and I restored them.
- **Cost:** length. The plan is 9,201 words against 1,601. The weekly tables are most of that, and the "Start here" box is the short path. The competitor table also isn't what was promised (see below).
- **Check on both:** the same feature tests ran on each version. The first version passed 8 and the final passed all 21 (13 of those the first version lacked), with no regressions.

**Outside check**
- **`check_plan.py`:** passes. All 24 weeks start on Mondays and sum to their stated hours (none over 5.0). The funnel scenarios, weekly pace, both $150 budget columns, margin, production, stretch and gate tables recompute correctly. All 49 weekday-and-date pairs are real weekdays.
- **`judge.py`:** passes. All 47 tables are well-formed, with no placeholders, no duplicated prose and no malformed links.
- **Known failure:** the competitor table. Etsy returned 403 on every page, and the roundup pages were also unreachable. The plan has three snippet-based sales figures and a worksheet instead. I did not work around the block.
- **Independent review:** a separate agent red-teamed the plan and found 10 problems. I fixed all of them (the 12% Offsite Ads rate, creator-gifting disclosure, safety, ad budget, timing and others).
- **Not checked:** no Markdown viewer was available, so layout was verified by parsing, not by eye. Whether the plan works is untested. The checks cover arithmetic, consistency and coverage.

**Stretch**
- **Target:** $6,000 a month in April 2027, with $3,000 reached by the end of February.
- **How far it got:** the route is built (Section 12). It adds bulk and event orders (6 a month at about $400) to retail of about $3,600, with three gates and eight hours-neutral swaps. The $3,000 fallback is intact.
- **My read:** $6,000 is unlikely. The realistic top end is about $4,000–$5,000, and the low case lands at $3,400.
- **Where it breaks:**
  1. **Bulk demand:** 60 outreach contacts yield roughly 1–4 orders, not 6.
  2. **Your time:** about 15.3 hours a week instead of 10.4.
  3. **Retail traffic:** $60 of ads covers only 6–15% of the extra visits needed.
  4. **Cash:** about $1,900 a month in materials.
  5. **Late bulk orders:** these fall on fixed event dates.

**Locked in**
- **Files:**
  - `plan-tools/check_plan.py`
  - `plan-tools/judge.py`
  - `plan-tools/run_checks.sh`
  - `CLAUDE.md` (a short note on how to run it and what proved it)
  - `.claude/commands/check-plan.md` (the `/check-plan` command)
- **Rerun:** `sh plan-tools/run_checks.sh`, or `/check-plan`, after any change to a number. The one expected FAIL line is the competitor table.
- **Snapshots:** `.ambition/first/` holds the first version (never edited). `.ambition/steps/2` to `.ambition/steps/8` hold each step's copy.

**Assumptions made**
- You never told me to use my judgement, so every answer in the restatement was yours. The plan's own assumptions are listed in Section 11 for you to replace. The main ones are the 1,850 visits, the 2% conversion, the $9 per jar and $8–12 postage costs, and that your 5 hours cover marketing only (Decision 5).

**Decisions (the most urgent left; all five are in Section 13)**
1. **Does your 5 hours include making and packing? (by Mon Nov 16).**
   - *For (a), marketing only:* keeps every task.
   - *For (b), everything:* matches a day-job schedule, but cuts about half the tasks.
   - *Pick:* whichever is true. If it's "everything", ask me for the cut-down plan.
2. **Etsy's free-shipping guarantee (by Tue Nov 24).**
   - *For turning it on now:* may help search placement, but you pay postage and the current effect is unconfirmed.
   - *For leaving it off:* keeps about $13 profit per plain jar.
   - *Pick:* off until at least two bundles earn $12 or more profit with free shipping.
3. **When to start Etsy Ads (Mon Nov 16).**
   - *Week 1:* gets data earliest, but spends on listings that may convert poorly.
   - *Week 3:* lets you fix the top listings first, but loses two weeks of the holiday window.
   - *Pick:* follow the Week 1 diagnosis (Week 1 if conversion is 1.5% or higher, otherwise Week 3).
4. **Insurance (quote by Fri Nov 20, buy by Mon Jan 4).**
   - *For buying before the holidays:* full cover, at a cost I couldn't verify.
   - *For buying before gifting or bulk:* covers the new risks before they start.
   - *Against waiting:* you'd be uninsured while volume rises.
   - *Pick:* get a quote now and buy before gifted sets or bulk orders.
5. **Run the stretch overlay (Mon Dec 28).**
   - *For:* about $184 profit per bulk order.
   - *Against:* about 5 more hours a week of making, and risk of late event orders.
   - *Pick:* only if December is at least $1,800 and you can add that time.

**Metrics**
```
Metrics since 2026-11-13T08:05:03Z (cost: /cost, or total_cost_usd in headless JSON)
total   in 150 · out 172.4k (think 91.8k) · cache read 8.09M · write 279.1k · hit 97% · 67 calls
model   sonnet-5-5: in 150 · out 172.4k (think 91.8k) · cache read 8.09M · write 279.1k · hit 97% · 67 calls
agent   main: in 144 · out 153.6k (think 78.3k) · cache read 8.06M · write 227.6k · hit 97% · 64 calls
agent   general-purpose ×1: in 6 · out 18.8k (think 13.5k) · cache read 36.4k · write 51.5k · hit 41% · 3 calls
```