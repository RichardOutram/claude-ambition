# Results

Each example has one **baseline**: the prompt exactly as a user would type it, on the same model, in the same macOS VM with a real browser, followed in the same chat by "Push it further." with no plugin (the **plain push**). The plugin passes an example only when a single `/be-ambitious` run of the *same prompt* beats both. Turn 1 of that run makes a first version and stops at a checkpoint, where it gets the same "Push it further.". The gate: turn 1 must be sent exactly what the baseline was sent (system prompt, tools, parameters and messages, checked from the transcripts), so it's a second plain sample. The final must beat the baseline, the plain push and the first version. Nothing else is judged automatically: we review frames, screenshots and the live pages side by side, and record the verdict. Runs made with an older plugin are marked outdated. [How the bench works](../bench/README.md).

Visual results, with every page live: [results site](https://richardoutram.github.io/claude-ambition/).

## claude-sonnet-5-5

| Example | Verdict | Gate (turn 1) | Baseline | Plain push | Preview (turn 1) | Full run | Plugin |
|---|---|---|---|---|---|---|---|
| data/heat-pump | Beats the baseline | pass | $0.23 · 1.8 min | $0.37 · 3.0 min | $0.14 · 0.8 min | $3.49 · 20.4 min (9.4× the plain push) | ccf02d5 · outdated |
| design/pricing-page | Beats the baseline | pass | $0.13 · 0.9 min | $0.33 · 2.3 min | $0.18 · 1.0 min | $2.20 · 11.9 min (6.7× the plain push) | ccf02d5 · outdated |
| dev/cycling-prototype | Beats the baseline | pass | $0.20 · 1.4 min | $0.42 · 3.2 min | $0.36 · 2.0 min | $2.97 · 68.9 min (7.0× the plain push) | ccf02d5 · outdated |
| dev/photo-rename | Ties the baseline | pass | $0.04 · 0.3 min | $0.20 · 1.6 min | $0.12 · 0.5 min | $4.21 · 56.9 min (20.5× the plain push) | ccf02d5 · outdated |
| dev/url-shortener-architecture | Beats the baseline | pass | $0.09 · 0.9 min | $0.25 · 2.6 min | $0.18 · 1.0 min | $2.34 · 20.3 min (9.4× the plain push) | aa6de6f |
| learn/bayes | Beats the baseline | pass | $0.12 · 0.9 min | $0.24 · 2.0 min | $0.20 · 1.1 min | $2.96 · 32.7 min (12.5× the plain push) | ccf02d5 · outdated |
| game/puzzle | Beats the baseline | pass | $0.17 · 1.3 min | $0.44 · 28.8 min | $0.20 · 1.2 min | $1.83 · 15.6 min (4.1× the plain push) | aa6de6f |
| plan/cycling-app | Beats the baseline | pass | $0.12 · 1.2 min | $0.24 · 2.4 min | $0.19 · 0.9 min | $3.06 · 19.9 min (12.8× the plain push) | c59ebef |
| threejs/neon-implosion | Beats the baseline | pass | $0.16 · 1.7 min | $0.23 · 2.4 min | $0.20 · 1.1 min | $2.91 · 36.5 min (12.8× the plain push) | ccf02d5 · outdated |
| write/candle-marketing | Beats the baseline | pass | $0.07 · 0.7 min | $0.15 · 1.5 min | $0.16 · 1.0 min | $3.97 · 23.0 min (26.9× the plain push) | aa6de6f |

### data/heat-pump

> Work out whether switching from my gas boiler to a heat pump would save me money, as a Markdown file

**Run 1:** Beats the baseline, gate pass. A regenerable model with 84/84 checks, sourced Ofgem prices with VAT, Monte Carlo and quote grids; hand-recomputed figures hold. The baseline is a one-off estimate.

[Files](claude-sonnet-5-5/data-analysis/heat-pump/) · [Visual view](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/data-analysis/heat-pump/)

### design/pricing-page

> Design a pricing page for an invoicing app for freelancers, as a single web page

**Run 1:** Beats the baseline, gate pass. Both are clean; the final adds a pricing idea (a clients-per-month selector across Starter/Solo/Pro) and trust lines, and stays clean on phone.

[Files](claude-sonnet-5-5/design/pricing-page/) · [Visual view](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/design/pricing-page/)

### dev/cycling-prototype

> Build a clickable prototype of the app in plan.md that I can open as a single html file

**Run 1:** Beats the baseline, gate pass. The final has more behind the same sign-in screen (welcome flow, simulated ride, segment leaderboards, paywall, reset) plus a rider test script and checks, but the visible gain over the plain push is small for 69 min and $2.97; not clicked through screen by screen.

[Files](claude-sonnet-5-5/development/cycling-prototype/) · [Visual view](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/development/cycling-prototype/)

### dev/photo-rename

> Write a Python script that renames my photos by the date they were taken

**Run 1:** Ties the baseline, gate pass. Both are safe with exact undo. The plugin adds 54 tests but keeps a misdated existing name as already named; the baseline renames it but its dry run numbers files differently from the real run.

[Files](claude-sonnet-5-5/development/photo-rename/) · [Visual view](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/development/photo-rename/)

### dev/url-shortener-architecture

> Design the architecture for a URL shortener that handles 10k requests a second, as a Markdown file

**Run 1:** Beats the baseline, gate pass. The plain push assumes over 95% of reads come from cache. The final tests that against a simulation and an hour of real Wikipedia traffic, finds 20–40% more likely, and sizes the database to work with no cache at all. Every decision says what would flip it, it works out that guessing 7-character links finds about 736k live links a day, and it shows where the design breaks at 100k requests a second. Its own check passes 43/43. (A first run got stuck planning a rewrite instead of improving the document; we fixed the method's wording and re-ran.)

[Files](claude-sonnet-5-5/development/url-shortener-architecture/) · [Visual view](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/development/url-shortener-architecture/)

### learn/bayes

> Explain Bayes' theorem with an interactive visualisation, as a single web page

**Run 1:** Beats the baseline, gate pass. The final turns a slider demo into a lesson: asks for a guess first, then steps through why a positive test is usually a false alarm with 1,000 dots and plain-language sliders.

[Files](claude-sonnet-5-5/education/bayes/) · [Visual view](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/education/bayes/)

### game/puzzle

> Make an original puzzle game I can play in the browser, as a single web page

**Run 1:** Beats the baseline, gate pass. A title screen, a first level that teaches the rule, 16 levels in chapters that each add a twist (pads that flip how the second twin moves), stars against a par a solver computes, so every level is proven solvable, and a phone d-pad. The plain push has more levels (22) and more object types, but nothing proves its levels can be solved, and it looks plainer. (A first run collapsed into one turn and never pushed; this is the second.)

[Files](claude-sonnet-5-5/games/puzzle/) · [Visual view](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/games/puzzle/)

### plan/cycling-app

> Make a plan for a react native expo social gamified fitness tracker app for the cycling niche, and save it to disk

**Run 1:** Beats the baseline, gate pass. A plan a team could start building from: 37 sized tickets with acceptance criteria, and two real traps the plain plans miss (Google Play's 14-day closed test, and a home privacy zone its own simulation could undo). Its reason for riders to switch is weak, and it's three times longer.

[Files](claude-sonnet-5-5/planning/cycling-app/) · [Visual view](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/planning/cycling-app/)

### threejs/neon-implosion

> Create a vivid pointer interactive abstract neon art solar system particle implosion, a 10 second looping animation in three.js, as a single web page.

**Run 1:** Beats the baseline, gate pass. Only the final reads as a scene: the baseline, the plain push and the plugin's own first version blow out to white bloom in the captured frames; the final shows orbits, a particle ring and trails, seamless loop, 0 console errors.

[Files](claude-sonnet-5-5/threejs/neon-implosion/) · [Visual view](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/threejs/neon-implosion/)

### write/candle-marketing

> Write a marketing plan for my handmade candle shop on Etsy, as a Markdown file

**Run 1:** Beats the baseline, gate pass. A dated 24-week plan that fits in 5 hours a week. Its margin table shows a $38 two-jar bundle earns about $4, or loses money when an Etsy Offsite Ad gets the sale; it warns that monthly orders swing by about ±6 by chance, and plans pouring around cure time. The plain push is a generic template with [brackets]. Weak point: at 9,200 words it's long for someone with 5 hours a week. (Second run, after the same method fix as url-shortener.)

[Files](claude-sonnet-5-5/writing/candle-marketing/) · [Visual view](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/writing/candle-marketing/)
