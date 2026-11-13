I've finished all eight steps. Your own verdict now takes one command and about 0.1 seconds: `python3 heatpump_model.py --me --gas-kwh N --scop X --price P`.

**On typical figures for a 3-bed semi in England, the heat pump doesn't save money.** On a standard tariff it is about £4,100 worse off after 15 years, and the simulation agrees in 94% of 5,000 runs. On a heat-pump tariff it is too close to call (about £1,150 worse off).

## You asked for → it became
- **"Would a heat pump save me money?"** became a yes / no / too-close verdict with confidence. It also gives the efficiency, price and gas use at which it would flip, and a 15-year comparison that includes when the boiler would need replacing.
- **"As a Markdown file"** stayed one file, `heat-pump-vs-gas-boiler.md`, with the verdict first and the script's output pasted at the bottom. A recompute script now sits beside it.
- **"My gas boiler"** became a typical English 3-bed semi on the Ofgem price cap, as you specified. You can swap in your own gas use, SCOP and price with `--me`.

## Against the first version
- **Better:** the first version had no verdict at the top, no source links, no regenerable numbers and only two flagged assumptions. The final has all of those, plus tested thresholds, quote-checking grids, decisions and next checks.
- **Gave up:** length. The file went from about 900 to about 4,200 words, though page one stays under 300 words and the rest is reference.
- **Check on both:** the same checks found the first version failing the verdict-first, sources and regenerable-numbers tests. The final passes all 84.

## Outside check
`check_report.py` ran 84 checks and all pass. They include:
- An independent reimplementation of the cost model that matches to the penny across six input sets and both tariffs.
- The pasted output matching a fresh run.
- Ofgem's £1,723 typical bill reproduced within £1, and Nesta's published parity result.
- Every source link loading.
- A cold read of the whole file.

It caught a real bug in the break-even price, which is now fixed. Source checks also made me correct three claims I had overstated.

## Stretch
The target was a personal verdict from three numbers, in under 10 seconds. It reached about 0.1 seconds, and `--gas-m3` handles meter readings. It breaks on fixed-price deals, where you need `--set` to enter your own rates, and I couldn't predict SCOP from flow temperature without data to check it against.

## Locked in
In `<workspace>`:
- `heat-pump-vs-gas-boiler.md`: the deliverable.
- `heatpump_model.py`: the model that generates it.
- `check_report.py`: the independent checks.
- `CLAUDE.md`: how to rerun and what counts as done.
- `.claude/commands/heat-pump.md`: the `/heat-pump` command.

To rerun everything, use `python3 heatpump_model.py --write heat-pump-vs-gas-boiler.md`, then `--check`, then `python3 -I check_report.py heat-pump-vs-gas-boiler.md heatpump_model.py`. A copy of each step is in `.ambition/steps/`, and the first version is in `.ambition/first/`.

## Assumptions made
I used your instruction to finish without stopping. The assumptions are flagged in the file's assumptions table:
- 10,500 kWh of gas a year.
- SCOP 3.0.
- A heat-pump tariff at 80% of the standard rate.
- A £2,500 replacement boiler replaced in year 5.
- Both fuels rising 3% a year.
- 5% VAT on electricity from April 2027.

## Decisions
All three are in the file with owners and dates. The most urgent is the first.

1. **Whether to buy.** The options are:
   - Keep the boiler and revisit when it fails.
   - Collect 2–3 quotes first.
   - Commit now.

   Keeping the boiler costs nothing but the grant may end. Quotes turn the two biggest unknowns into facts. Committing now stakes £7,500 on typical figures. I'd collect quotes, and default to keeping the boiler unless a quote lands in a "yes" cell. You decide by 31 January 2027.
2. **Tariff, if you proceed.** A standard tariff is simple but about £4,100 worse off. A heat-pump tariff is cheaper only if the heat pump runs mostly in the cheap windows. I'd choose the heat-pump tariff, but only with the installer's written plan for when the heat pump runs. You decide by 31 January 2027.
3. **Disconnecting gas.** Disconnecting at once stops the standing charge (about £110 a year) but removes your fallback. Keeping it costs about £1,300 over 15 years if kept for good. I'd keep it through the first winter, then disconnect if the heat pump performs well. You decide by 31 March 2028, if installed in 2027.

Your first next check is to run `--me` with your real gas kWh from your last 12 months of bills, by 20 November 2026.

## Metrics
```
Metrics since 2026-11-13T01:31:37Z (cost: /cost, or total_cost_usd in headless JSON)
total   in 166 · out 129.8k (think 54.0k) · cache read 10.75M · write 228.6k · hit 98% · 77 calls
model   sonnet-5-5: in 166 · out 129.8k (think 54.0k) · cache read 10.75M · write 228.6k · hit 98% · 77 calls
```