# data/heat-pump · not-ambitious

### User

Work out whether switching from my gas boiler to a heat pump would save me money, as a Markdown file

**→ Write** `{"file_path": "<workspace>/heat-pump-vs-gas-boiler.md", "content": "# Would a heat pump save me money versus my gas boiler?\n\n**Short answer: it depends mainly on one number, your electricity-to-gas price ratio, compared with the heat pump's efficiency.** I don't have your bills, location or home details, so this file gives you the break-even test and a worked example. Fill in your own figures in … [5824 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/heat-pump-vs-gas-boiler.md (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

I've written the analysis to `<workspace>/heat-pump-vs-gas-boiler.md`. It can't give you a firm yes or no yet, because I don't have your bills, location or home details. All the prices in it are illustrative assumptions, not quotes or real tariffs.

- **The test:** a heat pump is cheaper to run when your electricity price divided by your gas price is below the heat pump's seasonal efficiency (SCOP) multiplied by your boiler's efficiency. For example, SCOP 3.2 × 0.85 gives 2.7.
- **Worked example:** with gas at 0.07 per kWh, a standard electricity price of 0.25 per kWh gives roughly break-even at SCOP 3.0 and modest savings at SCOP 3.5–4.0. At 0.15 per kWh the savings are larger, around 300–450 a year. These figures come from an assumed 12,000 kWh of gas use a year and an 85% efficient boiler.
- **Payback:** installation costs and grants usually matter more than running costs. In my example, a net cost of 6,000, avoided boiler cost of 2,500 and savings of 300 a year give a payback of about 12 years.
- **Verdict:** a heat pump probably saves money if you can get cheap electricity (a heat pump or time-of-use tariff, or solar) and your boiler is due for replacement anyway. On a standard tariff with a working boiler, it often doesn't pay back on running costs alone.

The file also has a section where you fill in your own numbers. If you send me your gas and electricity bills, your region and a rough description of the house, I'll fill it in for your situation.

### User

I'm in the UK, in a 3-bed 1990s semi-detached house of about 95 m² with cavity wall insulation and a 100 mm loft. Last year I used about 11,500 kWh of gas and 2,900 kWh of electricity. I pay roughly 6p per kWh for gas and 26p per kWh for electricity on a standard variable tariff, plus a standing charge on each. My boiler is a 12-year-old combi that's still working fine. I don't have solar, but I'd consider a heat pump tariff if it makes the sums work. Please fill in your section with these numbers, include the grant I'd get here (the £7,500 Boiler Upgrade Scheme, if it's still available), and give me a clear yes or no.

**→ ToolSearch** `{"query": "select:WebSearch", "max_results": 1}`

<details><summary>result</summary>

```

```

</details>

**→ WebSearch** `{"query": "Boiler Upgrade Scheme grant \u00a37,500 air source heat pump current status November 2026", "mode": "standard"}`

**→ WebSearch** `{"query": "heat pump tariff unit rate p/kWh Octopus Cosy British Gas heat pump tariff 2026", "mode": "standard"}`

<details><summary>result</summary>

```
Web search results for query: "Boiler Upgrade Scheme grant £7,500 air source heat pump current status November 2026"

Links: [{"title":"It's time for an update","url":"https://www.vaillant.co.uk/advice/upgrade-your-heating/the-boiler-upgrade-scheme/"},{"title":"Installer Directory","url":"https://www.renewableenergyhub.co.uk/main/heat-pumps-information/bus-boiler-upgrade-scheme-heat-pumps/"},{"title":"Free Boiler Scheme/Grants 2026 - UPDATED","url":"https://iheat.co.uk/boiler-help/free-boiler-scheme-grants"},{"title":"There are different amounts of funding depending on what heating system you install:","url":"https://energysavingtrust.org.uk/.../boiler-upgrade-scheme/"},{"title":"Boiler Upgrade Scheme","url":"https://www.augustapp.com/dictionary/boiler-upgrade-scheme"},{"title":"There are different amounts of funding depending on what heating system you install:","url":"https://energysavingtrust.org.uk/advice/boiler-upgrade-scheme/"},{"title":"heat pump grant support","url":"https://www.cheltenham.gov.uk/environment/climate-action/heat-pumps/heat-pump-grant-support/"},{"title":"Air source heat pump: government expands grants to pump tech that heats, cools - and cuts installation costs","url":"https://www.yorkshireeveningpost.co.uk/business/consumer/air-source-heat-pump-government-grants-installation-costs-5405844"},{"title":"Air source heat pump: government expands grants to pump tech that heats, cools - and cuts installation costs","url":"https://www.yorkshirepost.co.uk/business/consumer/air-source-heat-pump-government-grants-installation-costs-5405844"},{"title":"off grid homes","url":"https://www.daikin.co.uk/en_gb/installer/support/off-grid-homes.html"},{"title":"Boiler Upgrade Scheme (BUS)","url":"https://www.ofgem.gov.uk/environmental-and-social-schemes/boiler-upgrade-scheme"},{"title":"Boiler Upgrade Scheme 2026: What's Changing for Installers and Grant Claims","url":"https://www.autarc.energy/gb/knowledge/boiler-upgrade-scheme-2026-installers"},{"title":"Hea … [2828 more chars]
```

</details>

<details><summary>result</summary>

```
Web search results for query: "heat pump tariff unit rate p/kWh Octopus Cosy British Gas heat pump tariff 2026"

Links: [{"title":"How Much Does a Heat Pump Cost to Run in the UK in 2026?","url":"https://readingheatpumps.pages.dev/guides/heat-pump-running-cost-uk-2026/"},{"title":"Book a demo","url":"https://reonic.com/en-gb/blog/heat-pump-tariff-uk/"},{"title":"Best Electricity Tariffs for Heat Pumps (UK)","url":"https://heatpumpmath.pages.dev/heat-pump-electricity-tariffs"},{"title":"renewableheatinghub.co.uk","url":"https://renewableheatinghub.co.uk/forums/electricity-providers/whos-your-electricity-provider-and-whats-your-tariff/paged/54/"},{"title":"Best Electricity Tariffs for Heat Pumps — UK 2026","url":"https://heatpumpcheck-uk-eb8.pages.dev/heat-pump-tariffs/"},{"title":"heat pump tariffs compared","url":"https://heatpumpsaver.pages.dev/blog/heat-pump-tariffs-compared/"},{"title":"heat pump running costs vs gas","url":"https://bristolheatpump.pages.dev/blog/heat-pump-running-costs-vs-gas"},{"title":"Cheapest heat pump electricity tariff UK – August 2026 rates compared","url":"https://www.energyplus.co.uk/costsavingadvice/heat-pump-electricity-tariff-uk-cheapest-rates"},{"title":"Heat Pump Running Costs — What You'll Actually Pay Per Year","url":"https://heatpumpcheck-uk.pages.dev/heat-pump-running-costs"},{"title":"46267 best electric tariff now that ovo are ending the heat pump plus in february 2026","url":"https://forum.buildhub.org.uk/topic/46267-best-electric-tariff-now-that-ovo-are-ending-the-heat-pump-plus-in-february-2026"},{"title":"Octopus Cosy Heat Pump Fleet Performance Dashboard","url":"https://octopus.energy/cosy-heat-pump-performance"},{"title":"Octopus Energy tariffs August 2026 — every deal, ranked","url":"https://www.energyplus.co.uk/suppliers/octopus-energy/tariffs"},{"title":"energy crisis fuels heat pump boom as octopus unveils cosy performance hub","url":"https://octopus.energy/press/energy-crisis-fuels-heat-pump-boom-as-octopus-unveils … [1827 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && n=$(grep -n '^## 5. Your numbers' heat-pump-vs-gas-boiler.md | cut -d: -f1) && head -n $((n-1)) heat-pump-vs-gas-boiler.md > /tmp/hp_head.md && sed -i '' 's/^\\*\\*Short answer: it depends.*/**Short answer for your house (sections 5\u20136): yes, but only if you move to a heat pump tariff. On your current standard variable tariff the answer is no.** The general m … [6868 more chars]`

<details><summary>result</summary>

```
7:## 1. The break-even rule
22:## 2. Worked example (assumptions)
52:## 3. Upfront cost and payback
69:## 4. Factors that move the answer
79:## 5. Your numbers (UK, 3-bed 1990s semi, 95 m²)
137:## 6. Verdict
**Short answer for your house (sections 5–6): yes, but only if you move to a heat pump tariff. On your current standard variable tariff the answer is no.** The general method and example are in sections 1–4.
[This command modified 1 file you've previously read: heat-pump-vs-gas-boiler.md. Call Read before editing.]
```

</details>

### Assistant

**Yes, but only if you move to a heat pump tariff. On your current 26p tariff the answer is no.** I've filled in sections 5 and 6 of `<workspace>/heat-pump-vs-gas-boiler.md`.

Some of the inputs below are my own estimates, not figures from your bills or from quotes:
- **Boiler efficiency:** I assumed 82% for a 12-year-old combi.
- **Installation cost:** I assumed about £12,500 installed, plus about £1,500 for radiator upgrades.
- **Heat pump efficiency (SCOP):** I used 3.0 to 3.6. SCOP is how many units of heat you get per unit of electricity, averaged over a year.
- **Heat pump tariff:** I used 14p/kWh as a placeholder. The tariff sites I found disagreed, from 7p to 17p, and they were mostly low-quality comparison sites. Check the live rate with the supplier.
- **Standing charges:** I assumed about £110 a year for gas, and about £37 a year more for electricity on a heat pump tariff.

Your gas costs £690 a year and your electricity £754, so you pay £1,444 today.

- **Standard tariff at 26p:** the heat pump costs about £50 to £130 a year more than gas at SCOP 3.0 to 3.3. At SCOP 3.6 it is roughly break-even. Your electricity costs 4.3 times as much as gas per kWh, and the heat pump needs that ratio to be below about 2.5 to 3.0 to win.
- **Heat pump tariff at about 14p:** you'd save about £560 to £640 a year. A heat pump tariff applies to your other 2,900 kWh of household electricity too, and that is where about half the saving comes from.
- **Heat pump tariff at 17p:** you'd save about £380 to £470 a year.
- **Payback:** with the £7,500 grant, the net cost is about £6,500. That pays back in about 9 to 12 years at 14p, or about 15 years at 17p. The 9-year case assumes you also disconnect gas, which saves about £110 a year. I haven't counted an avoided boiler replacement, which would shorten these by several years.

Your boiler works fine, so this is a good-value move rather than an urgent one. The strongest moment is when the boiler fails, if the grant is still available then.

**The grant.** The £7,500 Boiler Upgrade Scheme was still current in the sources I found, which date from mid-2026. I couldn't confirm anything newer, so check [Ofgem](https://www.ofgem.gov.uk/environmental-and-social-schemes/boiler-upgrade-scheme) and [gov.uk](https://www.gov.uk/government/publications/boiler-upgrade-scheme-regulations-approved-standards-grant-categories-and-grant-levels/notice-of-approved-grant-categories-and-values-for-the-boiler-upgrade-scheme--2). The £9,000 uplift is for off-gas homes, so it doesn't apply to you.

**Before committing:**
- **Quotes:** get 2 to 3 MCS-certified quotes with a room-by-room heat loss survey and a stated SCOP. Aim for a net cost under about £7,000 and a SCOP of 3.2 or better.
- **Loft:** top it up to 270 mm first. It costs a few hundred pounds and makes the heat pump's job easier.

Tariff sources: [Energy Plus](https://www.energyplus.co.uk/costsavingadvice/heat-pump-electricity-tariff-uk-cheapest-rates) and [Octopus Cosy performance page](https://octopus.energy/cosy-heat-pump-performance).

### User

Push it further.

**→ Read** `{"file_path": "<workspace>/heat-pump-vs-gas-boiler.md", "offset": 75}`

<details><summary>result</summary>

```
75	- **Maintenance.** Heat pumps need an annual service, much like a boiler. Costs are similar.
76	- **Non-financial factors.** Carbon emissions fall substantially, especially as the grid decarbonises. Comfort is steady but slower to respond. Outdoor space and noise rules apply.
77	- **Price risk.** Electricity-to-gas price ratios differ by country and change over time. A policy shift that moves levies from electricity to gas would improve the case.
78	
79	## 5. Your numbers (UK, 3-bed 1990s semi, 95 m²)
80	
81	### Inputs you gave me
82	
83	| Input | Value |
84	|---|---|
85	| Gas use | 11,500 kWh/year at 6p = **£690** (plus standing charge) |
86	| Electricity use | 2,900 kWh/year at 26p = **£754** (plus standing charge) |
87	| Boiler | 12-year-old combi, working fine |
88	| Home | cavity wall insulation, 100 mm loft, about 95 m² |
89	| Solar | none |
90	
91	### Assumptions I added (check these)
92	
93	- **Boiler efficiency in real use: 82%.** That is typical for a 12-year-old combi, so useful heat is 11,500 × 0.82 ≈ **9,430 kWh**.
94	- **Gas standing charge: about 30p/day (about £110/year).** You only save it if you disconnect gas completely, which needs no gas hob or fire and costs a disconnection fee I haven't included.
95	- **Heat pump tariff: 14p/kWh flat across all your electricity**, with a standing charge about 10p/day higher (about £37/year). Heat pump tariffs apply to the whole house meter, so your 2,900 kWh of other electricity gets cheaper too.
96	- **SCOP (seasonal efficiency):** 3.0 cautious, 3.3 central, 3.6 good. 1990s radiators are often sized for 70 °C flow, and 100 mm of loft insulation is below the current 270 mm recommendation, so I wouldn't assume above 3.5 without a proper survey.
97	- **Upfront cost:** about £12,500 installed (a 5–6 kW air-source unit, a new hot water cylinder since a combi has none, controls, commissioning), plus about £1,500 for radiator upgrades. Real quotes vary between about £11,000 and £14,000.
98	- **Grant:** £7,500 Boi … [4807 more chars]
```

</details>

**→ Bash** `{"command": "mkdir -p /tmp/hpmodel && cat > /tmp/hpmodel/model.py <<'EOF'\ngas_kwh=11500; eff=0.82; heat=gas_kwh*eff; elec_kwh=2900\ngas_p=0.06; base_e=0.26; sc_extra=37; gas_sc=110\ndef annual(scop, t, disc_gas=False, maint=50):\n    hp=heat/scop\n    before=gas_kwh*gas_p+elec_kwh*base_e\n    after=(hp+elec_kwh)*t+sc_extra+maint-(gas_sc if disc_gas else 0)\n    return before-after\ndef npv(sav, n … [2463 more chars]`

<details><summary>result</summary>

```
heat 9430.0
== annual saving (with 50 maint penalty) ==
0.1 [753, 781, 805] [863, 891, 915]
0.12 [632, 666, 695] [742, 776, 805]
0.14 [511, 551, 584] [621, 661, 694]
0.17 [330, 378, 419] [440, 488, 529]
0.2 [148, 205, 253] [258, 315, 363]
0.24 [-93, -25, 32] [17, 85, 142]
0.26 [-214, -140, -78] [-104, -30, 32]
== breakeven tariff (saving=0) ==
3.0 22.45
3.3 23.57
3.6 24.59
== tariff at which NPV15=0, net 6500 ==
3.0 None 13.12
3.0 5 16.14
3.3 None 13.77
3.3 5 16.94
3.6 None 14.36
3.6 5 17.67
== NPV15 table (real, 3.5%) net 6500, no boiler credit / with boiler credit yr5 ==
0.14 3.0 511 -615 1490
0.14 3.3 551 -155 1950
0.14 3.6 584 229 2334
0.17 3.0 330 -2703 -599
0.17 3.3 378 -2144 -39
0.17 3.6 419 -1678 427
0.2 3.0 148 -4792 -2687
0.2 3.3 205 -4133 -2028
0.2 3.6 253 -3585 -1480
== cost sensitivity at 14p/3.3 and 17p/3.3 ==
5000 [1345, -644] [3450, 1461]
6500 [-155, -2144] [1950, -39]
8000 [-1655, -3644] [450, -1539]
9500 [-3155, -5144] [-1050, -3039]
== gas-price-rise relative to elec: esc on saving ==
0 -155 -2144
0.01 334 -1809
0.02 868 -1442
== Cosy-like ToU: heat pump 70% in cheap 13p, 30% peak/standard 28p; other elec 26p->blended 20p ==
3.0 222
3.3 268
3.6 305
== fair baseline: stay on gas but switch to 24p fixed ==
3.0 453
3.3 493
3.6 526
== loft ==
0.03 21 12
0.05 34 20
co2 gas 2104.5 hp 200.03030303030303
Shell cwd was reset to <workspace>
```

</details>

**→ Edit** `{"replace_all": false, "file_path": "<workspace>/heat-pump-vs-gas-boiler.md", "old_string": "**Yes, switch, but only with a heat pump tariff.** The main reason is not cheaper heating. It is that a heat pump tariff makes your whole household electricity cheaper.\n\n- **Standard variable tariff (26p):** **No.** Your electricity-to-gas price ratio is 4.3 (26p / 6p), and a heat pump at SCOP 3.0\u20133 … [1961 more chars]`

<details><summary>result</summary>

```
The file <workspace>/heat-pump-vs-gas-boiler.md has been updated successfully.
```

</details>

**→ Edit** `{"replace_all": false, "file_path": "<workspace>/heat-pump-vs-gas-boiler.md", "old_string": "4. **Top up your loft insulation to 270 mm first.** It costs a few hundred pounds, reduces the heat the pump must supply, and helps the SCOP.", "new_string": "4. **Consider topping up your loft insulation to 270 mm.** It costs a few hundred pounds and mainly helps comfort and the heat pump's sizing. As a m … [84 more chars]`

<details><summary>result</summary>

```
The file <workspace>/heat-pump-vs-gas-boiler.md has been updated successfully.
```

</details>

**→ Edit** `{"replace_all": false, "file_path": "<workspace>/heat-pump-vs-gas-boiler.md", "old_string": "### Sources and caveats\n", "new_string": "## 7. Stress test\n\nThis section tightens the section 5 numbers. Changes from before:\n\n- A 15-year life for the heat pump, with savings discounted at 3.5% a year in real terms.\n- An extra \u00a350 a year for servicing (a heat pump service plus cylinder checks, … [4037 more chars]`

<details><summary>result</summary>

```
The file <workspace>/heat-pump-vs-gas-boiler.md has been updated successfully.
```

</details>

### Assistant

I stress-tested the numbers, and they change my answer. I've updated `<workspace>/heat-pump-vs-gas-boiler.md` with a new section 7 and a revised verdict in section 6.

**Revised answer: not now on money alone. Yes when the boiler needs replacing, or now only if you can lock in a heat pump tariff of about 14p or less.** My first "yes" relied on simple payback, which flatters the case. The new model uses a 15-year heat pump life, discounts savings at 3.5% a year in real terms, and adds £50 a year for servicing. It also assumes the gas standing charge stays (it's only saved if you disconnect gas).

- **Where the tariff stops saving money:** the heat pump costs less to run than your current setup only below about 23.6p (SCOP 3.3).
- **Where the £6,500 pays back over 15 years:**
  - **Ignoring the boiler:** you need about 13.8p.
  - **Counting a £2,500 boiler replacement avoided in year 5:** you need about 16.9p.
- **15-year net present value at 14p and SCOP 3.3:** about −£155 without the boiler credit, and about +£1,950 with it.
- **At 17p:** about −£2,100 without the boiler credit, and roughly zero with it.
- **Biggest sensitivities:**
  - **Installation price:** every £1,500 off the net cost adds £1,500 to the 15-year value.
  - **Tariff:** each 1p shifts the annual saving by about £65 to £75.
  - **Gas vs electricity prices:** if gas rises 1% a year faster than electricity, the 14p case goes from −£155 to +£334. The reverse would hurt it.

Three smaller findings:
- **Loft top-up:** I previously suggested doing this first. It only saves about £20 to £35 a year, so it's a comfort measure, not a payback one. I've changed the text.
- **Household electricity saving:** I credited you with the whole drop from 26p to 14p on your other 2,900 kWh. Against a fair alternative, staying on gas and fixing at about 24p, the saving is about £58 a year lower.
- **Carbon:** the switch saves roughly 1.7 to 1.8 tonnes of CO₂ a year. If that matters to you, it's worth more than the financial margin here.

I'd change my mind if a quote nets below about £5,500 after the grant, you can lock in 12p or less, your boiler fails, or a survey supports a SCOP of 3.6.

The tariff figures are still the weakest input, because my search results for heat pump tariffs ranged from 7p to 17p. A confirmed live rate from a supplier would move the verdict more than any other single fact.
