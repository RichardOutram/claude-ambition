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