The pricing page is finished: `pricing.html` now passes all 11 of the browser checks in `check-pricing.py`. It had no problems left to fix at the end. Your plan was to swap in your own prices and links later, so those and three invented policy claims still need your input before launch.

**You asked for → it became**
- **Asked for:** a pricing page for a freelancer invoicing app, as a single web page.
- **Became:** a page where a freelancer picks a plan in about 10 seconds and sees the four worries answered (hidden fees, lock-in, data safety, looking professional to clients) without hunting. You ranked those worries first, then the 10-second pick, then polish.
- **How each part was raised:**
  - **Plans:** each has a "Best for" line and a short reassurance under its button.
  - **Billing and currency:** the toggle shows the real yearly charge and the savings, in three currencies.
  - **Comparison table:** regrouped, with screen-reader text on every mark.
  - **FAQ:** ordered around the four worries.
  - **Testimonial and call to action:** the fake "40,000+" claim is gone.
  - **Billing strip:** a new "What happens after you click" strip under the plans.

**Against the first version** (saved at `/tmp/ambition-first/pricing.v1.html`)

| Check | First version | Final |
|---|---|---|
| Worries answered in the first screen, desktop | 0 of 4 | 4 of 4, plus 3 "Best for" lines |
| Phone first screen | no plan prices | all 4 promises and 3 plan rows with prices |
| Browser checks passed | 5 of 11 | 11 of 11 |
| Lighthouse accessibility, best practices, SEO | 100 | 100 |
| Lighthouse performance | 62 | 62, with first paint at 1.0s against 1.5s |

- **What it gave up:** on phones the four worry cards became one-line promises, and the comparison table scrolls sideways with its feature column pinned.
- **Performance score:** Lighthouse measured seconds of blocking time for both versions, which is impossible for this page. It reflects this loaded machine, so I treat it as equal, not as a real score.

**Outside check:** `check-pricing.py` runs the page in headless Chrome and reads the real layout. It checks the first screen on desktop and a 390×700 phone, overflow, prices in every currency and period, and accessibility basics. It passed 11 of 11 on the final page, and a Lighthouse run on the final page scored 100 for accessibility, best practices and SEO. I also compared the page against Basecamp, Linear and Stripe, and none of them answers visitors' worries or recommends a plan as directly. FreshBooks wouldn't load. I did not test with real people, as you said.

**Stretch:** the target was the whole decision on a phone's first screen: all four worries with their explanation, and all three plans with prices. It got there, with about 114px to spare (the plan rows end near 586px of 700). It nearly broke twice: a hidden billing note and a misleading check, both fixed. I haven't looked at the final phone render after the last small change.

**Locked in**
- **`check-pricing.py`:** run `python3 -I check-pricing.py`. It prints PASS or FAIL lines, exits non-zero on any failure, and also counts the `PLACEHOLDER` markers.
- **`CLAUDE.md`:** says what to swap before launch and how to run the check.
- **No project command:** a script is enough for this.

**Assumptions I made** (you answered every question, so these are about content you hadn't specified)
- **Name and tiers:** the app is called "Ledgerly", with three plans at $0, $10 and $24 per month billed yearly. EUR and GBP prices are fixed numbers I chose, not converted rates.
- **Policy claims:** the 14-day trial with no card, a 30-day money-back guarantee, 90 days of read-only access after cancelling, and encryption with daily backups. None of these are real, and three are marked `PLACEHOLDER` in the HTML: the testimonial, the data-protection claim and the billing strip.

**Decisions left**

Owners and dates are my suggestions, and they're yours to change.

| # | Decision | Options and trade-offs | My pick | Owner, date |
|---|---|---|---|---|
| 1 | Confirm the policy claims (security, refund, 90-day read-only, trial emails) | **Keep as written:** fast, but false claims would be a real harm. **Edit to your real terms:** slower, safe. | Edit to real terms. This is the urgent one. | You (with legal if you have it), by 2026-12-01 |
| 2 | Real prices and tiers | **Keep three tiers:** clear and now tested. **Two tiers:** simpler, loses the team option. | Keep three tiers with your real prices. | You, by 2026-12-01 |
| 3 | Card up front or not for trials | **No card:** matches the page's promises and builds trust. **Card required:** likely more paid conversions, but contradicts the page and needs edits in four places. | No card, to match the page's promises. | You, by 2026-12-01 |
| 4 | Default billing period | **Yearly:** lower headline price. **Monthly:** simplest, no annual-charge surprise. | Keep yearly, now with a darker billing line. | You, at launch |
| 5 | Replace the invented testimonial with a real quote, with permission | **Keep placeholder:** cheaper, but it's a fake claim. **Real quote:** takes asking a customer. | Real quote, as soon as you have one. | You, before launch |

**Next check:** run `python3 -I check-pricing.py` after swapping in real prices and links, and again before launch. Owner: whoever edits the page. Date: before launch.

**Metrics**

```
Metrics since 2026-11-24T12:01:37Z (cost: /cost, or total_cost_usd in headless JSON)
total   in 194 · out 83.7k (think 26.9k) · cache read 7.73M · write 140.9k · hit 98% · 85 calls
model   sonnet-5-5: in 194 · out 83.7k (think 26.9k) · cache read 7.73M · write 140.9k · hit 98% · 85 calls
```

▪ Step 8/8 done