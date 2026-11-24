# Pricing page: lean push (run-5) against the full method (run-4)

Same prompt, model (Sonnet 5.5), effort (medium) and VM. Turn 1 identical to the baseline in both (gate pass). The only planned difference: run-4 got the whole method (SKILL.md and reference/, about 20,000 characters) with step 2; run-5 got only each step's own instruction.

**Confound.** The stand-in answered Altitude differently: run-4 heard "a real product launch" (worries first, then the plan pick, polish third); run-5 heard "mainly a design piece, a showcase" (a specific brand, then plan hierarchy). Part of run-5's visual lead comes from that answer. One run each: a strong hint, not proof.

## Rubric

| | Full method (run-4, Ledgerly) | Lean (run-5, Inkwell) |
|---|---|---|
| Plan in seconds, on a phone | Better: worries and three one-line plan rows with prices in the first phone screen; first price at 401px | Freelancer card first on phone, but its price at 843px, below an 812px screen; very clear on desktop; a two-slider plan picker |
| Against bigger rivals | Neither names one. Worries (no hidden fees, no lock-in, data safety, looks professional) at the top: slightly better for a visitor from a comparison article | Fee-markup and refund strip, money-back guarantee, a trial invoice showing $0.00 due today; good but lower down |
| Visual distinctiveness | Template look, close to the baseline | Clearly better: invoice motif, ITEM 01/02/03, serif type, a rubber stamp, a navy featured card |
| Honest copy | Invented policies marked PLACEHOLDER in the HTML; removed an invented user count. Bug: in GBP or EUR, Starter still shows "$0" beside "£8" and "£20" | Invented figures unmarked on the page ("about 6 days faster", "nine days on average"); a footer says it's fictional; "Your pick" shows before the visitor uses the picker |

## Found by our checks

- Run-4: the currency bug above. Its table, testimonial and FAQ fade in on scroll: fine for a visitor (nothing stays hidden after scrolling), blank in full-page captures.
- Run-5: on a phone the comparison table shows only the Starter column, with the others behind an unhinted sideways scroll (its worst flaw for a phone-first audience). Two tags on Freelancer say the same thing, and the stamp overhangs the card.
- Both: no sideways overflow at 375px, 0 console errors, 0 JavaScript errors.

## Lighthouse (local, mobile / desktop)

| | Perf | A11y | Best practices | SEO |
|---|---|---|---|---|
| Baseline | 100 / 100 | 100 | 96 | 100 |
| Plain push | 69 / 98 (4.6 s blocking time, machine noise) | 100 | 96 | 100 |
| Full method | 100 / 100 | 100 | 100 | 100 |
| Lean | 95 / 100 | 100 | 96 | 100 |

The 96s are a missing favicon.

## Cost and time

| | Full method | Lean |
|---|---|---|
| Time | 46.8 min | 18.2 min |
| Cost | $2.21 | $1.92 |
| Output | 187K tokens | 377K tokens |
| Slowest step | Judge, 29.9 min, most of it fighting Lighthouse and headless Chrome | Stretch, 3.1 min |

Lean did more work in less time and didn't skim: its Stretch added a working trial-invoice preview with date maths checked across a year end and a leap year. Neither run showed costume depth, role-play, an artifact swap or self-grading.

## Verdict

Lean (run-5) beats the baseline, the plain push and its own first version: a real brand where all three are generic, a plan picker, an honest fine-print strip. Its phone price sits lower than the baseline's. The full method (run-4) beats them narrowly on worry handling and the phone plan rows, but barely moves visually and shipped the currency bug. Lean is the better page and the better process, and it is now the plugin's default.
