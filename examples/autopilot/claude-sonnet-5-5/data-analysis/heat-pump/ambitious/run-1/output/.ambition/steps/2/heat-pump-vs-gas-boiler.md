# Would a heat pump save me money versus my gas boiler?

**Short answer: it depends mainly on two numbers, and I don't have yours.** Your folder had no bills or home details, so the figures below are an *illustrative example* with assumptions you should replace (UK-style prices in £, a typical semi-detached home). Section 4 lets you plug in your own numbers in a couple of minutes.

## 1. The core logic

A boiler turns 1 kWh of gas into about 0.85–0.92 kWh of heat. A heat pump turns 1 kWh of electricity into about 2.5–4 kWh of heat (its efficiency is the **SCOP**, seasonal coefficient of performance).

So heat pump running costs are lower when:

```
electricity price (£/kWh) / SCOP  <  gas price (£/kWh) / boiler efficiency
```

**Break-even SCOP = (electricity price × boiler efficiency) / gas price**

Electricity usually costs about 3.5–4× as much per kWh as gas, so you need a SCOP above roughly 3.3–3.5 to break even on the standard tariff. A cheaper heat-pump or time-of-use tariff lowers that bar sharply.

## 2. Example assumptions (replace with yours)

| Item | Value |
|---|---|
| Annual gas use (heating + hot water) | 12,000 kWh |
| Boiler efficiency | 85% |
| Useful heat delivered | 10,200 kWh/year |
| Gas unit price | 6.3p/kWh |
| Gas standing charge | 30p/day (about £110/year) |
| Standard electricity price | 25p/kWh |
| Heat-pump/off-peak blended electricity price | 18p/kWh (needs a suitable tariff and some load shifting) |
| Installed cost of heat pump | about £12,000 |
| Grant (e.g. England & Wales Boiler Upgrade Scheme) | £7,500 (check you're eligible and the current amount) |
| Net up-front cost | about £4,500–£6,000 |

Current gas cost: 12,000 × £0.063 = **£756/year** (**£866** with standing charge).

## 3. Results for the example

Annual **saving** (negative = costs more). The first figure ignores the gas standing charge; the figure in brackets includes removing it, which only applies if you disconnect gas entirely.

| Electricity price | SCOP 2.8 (poor install / high flow temp) | SCOP 3.2 (typical) | SCOP 3.8 (good) |
|---|---|---|---|
| 25p (standard tariff) | −£155 (−£45) | −£41 (+£69) | +£85 (+£195) |
| 18p (heat-pump tariff) | +£100 (+£210) | +£182 (+£292) | +£273 (+£383) |

Break-even SCOP in the example:

- Standard 25p tariff: **about 3.4** (about 2.9 if you also drop the gas standing charge)
- 18p heat-pump tariff: **about 2.4** (about 2.1 with the standing charge dropped)

### What this means

- **On a standard tariff, running costs are roughly a wash**: slightly worse to modestly better.
- **With a heat-pump or time-of-use tariff and a decent SCOP, you'd save roughly £180–£380 a year.**
- **Payback is long on running costs alone.** £5,000 net ÷ £290 saving is about 17 years. It is shorter if your boiler is due for replacement anyway (a new gas boiler costs roughly £2,500–£3,500, so count only the *extra* cost), or if you use lots of gas.
- Savings scale with usage: a leaky 20,000 kWh house gains more than a 7,000 kWh flat.

## 4. Do it with your numbers

1. **Annual gas kWh** (from a bill or your supplier's app): `G`
2. **Gas unit price** and **standing charge**: `Pg`, `Sg`
3. **Boiler efficiency** (default 0.85 if old, 0.90 if a modern condensing boiler): `E`
4. **Heat needed** = `G × E`
5. **Electricity price** you would actually pay for heat-pump use: `Pe`
6. **SCOP** from the installer's MCS heat-loss calculation (not the brochure's best-case figure): `S`

```
Gas running cost         = G × Pg
Heat pump running cost   = (G × E / S) × Pe
Annual saving            = Gas cost − Heat pump cost   (+ gas standing charge if you disconnect)
Payback (years)          = (Heat pump net cost − boiler replacement avoided) / Annual saving
```

## 5. Things that swing the answer

- **Insulation and emitters.** A heat pump wants low flow temperatures. If you need larger radiators or better insulation to get a SCOP above 3, add that to the cost.
- **Tariff.** This is the biggest lever. Check heat-pump-specific and smart time-of-use tariffs. Solar panels or a battery improve things further.
- **Grant eligibility.** The grant can halve the net cost. Confirm eligibility and amount for your country and date.
- **Hidden extras.** A hot-water cylinder, radiator upgrades, electrical upgrades and removal of the old boiler.
- **Price risk.** Gas/electricity price ratios change. Policy to shift levies from electricity to gas would improve the case; the reverse would worsen it.
- **Non-money factors.** Lower carbon, no gas safety checks if you disconnect, but a different heating style (steady and low rather than short and hot).
- **Maintenance.** About £100–£200 a year of servicing for both, so roughly neutral.

## 6. Verdict template

- If your quote's SCOP is **≥ 3.5** or you can get a **heat-pump tariff** → likely saves money each year.
- If SCOP is **< 3** and you'd be on a **standard tariff** → likely costs more to run; only worth it for non-financial reasons or if the grant covers most of the cost.
- Ask for a **written heat-loss calculation and a predicted SCOP** from at least two MCS-certified installers before deciding.

*Prices above are rounded estimates for illustration, not quotes. Please check current rates, grants and your own bills.*
