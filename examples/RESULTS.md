# Results

Each example has one **baseline**: the prompt exactly as a user would type it, on the same model, in the same container with a real browser. The plugin passes an example only when a single `/be-ambitious` run of the *same prompt* beats it. Turn 1 of that run makes a first version and stops at a checkpoint; it must already be at least as good as the baseline (the gate). Nothing is judged automatically: we review frames, screenshots and the live pages side by side, and record the verdict. Runs made with an older plugin are marked outdated. [How the bench works](../bench/README.md).

Visual results, with every page live: [results site](https://richardoutram.github.io/claude-ambition/).

## claude-opus-5-5

| Example | Verdict | Gate (turn 1) | Baseline | Preview (turn 1) | Full run | Plugin |
|---|---|---|---|---|---|---|
| threejs/neon-implosion | not reviewed | – | $0.45 · 2.4 min | $1.54 · 10.6 min | $4.65 · 37.8 min (10.2× cost) | 6128ee8 |

### threejs/neon-implosion

> Create a vivid neon art solar system particle implosion, a 10 second looping animation in three.js, as a single web page.

[Files](claude-opus-5-5/threejs/neon-implosion/) · [Visual view](https://richardoutram.github.io/claude-ambition/claude-opus-5-5/threejs/neon-implosion/)
