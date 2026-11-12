# Results

Each example has one **baseline**: the prompt exactly as a user would type it, on the same model, in the same container with a real browser. The plugin passes an example only when a single `/be-ambitious` run of the *same prompt* beats it. Turn 1 of that run makes a first version and stops at a checkpoint. The gate: turn 1 must be sent exactly what the baseline was sent (system prompt, tools, parameters and messages, checked from the transcripts), so it's a second plain sample. The final must beat the better of the two plain versions. Nothing else is judged automatically: we review frames, screenshots and the live pages side by side, and record the verdict. Runs made with an older plugin are marked outdated. [How the bench works](../bench/README.md).

Visual results, with every page live: [results site](https://richardoutram.github.io/claude-ambition/).

## claude-opus-5-5

| Example | Verdict | Gate (turn 1) | Baseline | Preview (turn 1) | Full run | Plugin |
|---|---|---|---|---|---|---|
| threejs/neon-implosion | no plugin run yet | – | $1.08 · 5.0 min | – | – | – |

### threejs/neon-implosion

> Create a vivid pointer interactive abstract neon art solar system particle implosion, a 10 second looping animation in three.js, as a single web page.

[Files](claude-opus-5-5/threejs/neon-implosion/) · [Visual view](https://richardoutram.github.io/claude-ambition/claude-opus-5-5/threejs/neon-implosion/)
