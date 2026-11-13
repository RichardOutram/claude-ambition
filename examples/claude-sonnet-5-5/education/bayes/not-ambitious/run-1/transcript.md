# learn/bayes · not-ambitious

### User

Explain Bayes' theorem with an interactive visualisation, as a single web page

**→ Write** `{"file_path": "<workspace>/bayes.html", "content": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n<title>Bayes' Theorem, Interactively</title>\n<style>\n  :root{\n    --bg:#fafaf8; --fg:#1c1c1a; --muted:#66655f; --card:#fff; --line:#dcdbd4;\n    --h:#2a6fdb;      /* hypothesis true, evidence positive … [12288 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/bayes.html (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

I've written the page to `<workspace>/bayes.html`. Open it in any browser. It's a single self-contained file with no dependencies. I haven't opened it in a browser, so the layout and behaviour are untested.

**What's on the page**
1. **Scenario controls.** Three sliders set the prior P(H), the hit rate P(E|H), and the false-alarm rate P(E|¬H). Four presets load worked examples: a rare disease test, a spam filter, a very accurate test for a very rare condition, and a two-headed coin. The posterior P(H|E) is shown large, with a bar that marks prior against posterior.
2. **1,000-people dot grid.** This shows the same calculation as counts. True hits are blue and false alarms are orange. In the default scenario (1% prevalence, 90% hit rate, 9% false alarms), about 9 true hits sit among about 98 false alarms, so a positive result means only about 8% chance of disease.
3. **Area diagram.** Width is the prior and height is the likelihood. The posterior is the blue area divided by blue plus orange.
4. **The formula with your numbers.** It shows the theorem, then your values substituted in, then a step-by-step breakdown. A short note explains the base-rate fallacy.

The page follows your system's light or dark setting and works on narrow screens.

One thing to check when you open it: the small "E rows" label beside the area diagram is my own addition. It repeats the posterior percentage and may be redundant, so cut it if it looks cluttered.

### User

Push it further.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\np='bayes.html'\ns=open(p).read()\n\n# CSS\ns=s.replace(\"</style>\",\"\"\"  .chips{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:10px 0;font-variant-numeric:tabular-nums}\n  .chip{padding:3px 10px;border-radius:999px;background:var(--bg);border:1px solid var(--line);font-size:.9rem}\n  .chip.pos{border-color:var(--h)} .chip.n … [10765 more chars]`

<details><summary>result</summary>

```
3
syntax ok
```

</details>

### Assistant

I've extended `bayes.html` with five new sections. It parses without syntax errors, but I haven't opened it in a browser, so the layout and interactions are untested.

- **Draggable area diagram (section 3).** You can now drag the diagram itself.
  - The vertical divider sets the prior.
  - Dragging up or down in the left column sets the hit rate.
  - Dragging up or down in the right column sets the false-alarm rate.
  - Everything else on the page updates live while you drag.
- **Sequential updating (section 5).** "Observe E" and "Observe no E" feed each posterior back in as the next prior, so you can watch belief build up or fall back. A row of chips records the path. This assumes each observation is independent given H.
- **Odds form (section 6).** This shows prior odds × likelihood ratio = posterior odds, with a plain-language note on whether the evidence supports H, counts against it, or tells you nothing.
- **Posterior vs. prior curve (section 7).** It plots the posterior against every possible prior, with a dashed "no update" diagonal and your current point marked. This makes it clear why a rare hypothesis stays unlikely even after a positive result.
- **Simulation (section 8).** Buttons add 100 or 1,000 random people drawn from your probabilities. It keeps only those showing the evidence and tallies how many really are H, with a bar that converges on the theoretical posterior. It resets whenever you change a parameter.

I also changed the prior handling so chained updates carry the exact value rather than a value rounded to the slider's step. Moving a slider, dragging the diagram, or choosing a preset clears the chain.
