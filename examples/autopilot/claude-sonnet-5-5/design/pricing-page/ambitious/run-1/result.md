The pricing page, `pricing.html`, is finished and passes 39 of 39 checks plus the stretch target. It is a single self-contained file for a made-up app called Inkwell. I also built the checks that now guard it.

## Report

**You asked for → it became**
- **A pricing page for a freelancer invoicing app, as a single page → a launch-ready page for signups and upgrades.** It is still one file with no dependencies.
- **A free tier, a mid solo plan and a higher plan → plans split by client count.**
  - Starter is $0 for 5 clients.
  - Solo is $15 a month, or $12 billed yearly, for 25 clients, and is the recommended plan.
  - Pro is $35 a month, or $28 billed yearly, with unlimited clients.
- **Visitors find their plan in seconds → an "I work with 1–5 / 6–25 / 26+ clients" selector** that highlights the matching plan, plus a clear "who it's for" line on each card.
- **Doubts about lock-in, fees and export answered by the plans → each plan card carries its own answers.** There's also a worked fee example showing what you take home and a comparison table.
- **Your change: no invented testimonials → removed.** A plain refund line stays, and the FAQ covers trial end, renewal and whether clients need an account to pay.

**Against the first version**
- **Better on:**
  - The first screen now shows the decision, with the Solo button above the fold at 1366×640, 1280×720 and 390×844.
  - The objection answers sit inside each plan card.
  - The prices, fees and table all agree with each other.
  - There are 0 accessibility violations in light and dark mode.
  - Dark mode is clearer, and nothing overflows from 320 to 1280px.
- **Gave up:**
  - The first version's testimonial, on purpose.
  - The cards no longer say "even after you cancel" or "drop back to Starter". Those details now live only in the FAQ.
  - The subheading is hidden below 860px width.
- **Check on both:** the same script gives the final 39/39 and the first version 15/39. Part of that gap reflects numbers and features this run introduced, so it isn't a pure quality measure.

**Outside check**
- **What ran:** real Chrome driven by `puppeteer-core`, plus axe-core for accessibility.
- **What it returned:**
  - The yearly totals, savings and fee examples are all arithmetically correct.
  - The table agrees with the cards.
  - There's no overflow at any width, and axe reports 0 violations.
  - The toggle, selector and signup links work.
  - The controls hide when JavaScript is off.
- **Official pricing pages:** Wave, FreshBooks, Invoice Ninja and Bonsai each confirmed the market range.

**Stretch**
- **Target:** at 1366×640 the first screen shows all three plans, prices, buttons and the three objection answers, and at 375×667 the Solo button is above the fold.
- **How far it got:** all four sizes pass, 1366×640, 375×667, 390×844 and 1280×720.
- **What it cost:** the card wording is shorter, as noted above.

**Locked in**
- `checks/accept.mjs` runs the 39 acceptance checks.
- `checks/stretch.mjs` runs the first-screen check.
- `checks/package.json` lists the two dependencies.
- `CLAUDE.md` explains how to run the checks and what they prove.
- `.claude/commands/check-pricing.md` is the `/check-pricing` command.
- To rerun, use `cd checks && npm install && npm run check`.
- The step snapshots are in `.ambition/steps/2/` through `.ambition/steps/8/`, and the original is in `.ambition/first/`.

**Assumptions made:** you said to use my judgement only to finish without stopping, so I answered no questions on your behalf. The invented product facts are all placeholders: the product name, the 30-day refund, the 7-day renewal email, the two-click cancel, clients paying without an account, two extra team seats on Pro, and API access on Pro.

**Decisions left**

| # | Decision | Options | For / against | My pick | Owner, date |
|---|---|---|---|---|---|
| 1 | Card and bank fee rates (2.9% + 30¢, 0.8% max $5) | Confirm against your processor, or soften the wording | Confirming makes the page's most important claim true. Softening loses the clarity that is the page's edge. | Confirm. | You, by 2026-11-18 |
| 2 | The invented policies listed above | Confirm each, or cut the ones you won't honor | Each confirmed claim builds trust. Each false one is a deceptive-claim risk on a real launch. | Confirm or cut each one before launch. | You, by 2026-11-18 |
| 3 | Prices: Solo $15, Pro $35, Starter 5 clients | Keep, or raise Solo toward $19–23 | Competitors sit at $19–23 for similar plans, so $15 undercuts them. $15 may leave money on the table. | Keep at launch, and revisit after 4 weeks of data. | You, review 2026-12-15 |
| 4 | Signup links (`/signup?plan=…`) | Point at your real signup, or keep the placeholder | A real URL makes the plan and billing choice carry through. | Point them at the real signup. | You, before launch |

The next check is `/check-pricing` after any edit. A run of `npm run check` is the standing proof.

**Metrics**
```
Metrics since 2026-11-13T01:15:54Z (cost: /cost, or total_cost_usd in headless JSON)
total   in 168 · out 75.8k (think 23.6k) · cache read 7.47M · write 146.4k · hit 98% · 77 calls
model   sonnet-5-5: in 168 · out 75.8k (think 23.6k) · cache read 7.47M · write 146.4k · hit 98% · 77 calls
```