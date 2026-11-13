# Heat pump vs gas boiler

- `heat-pump-vs-gas-boiler.md` is generated, never hand-edited. Regenerate: `python3 heatpump_model.py --write heat-pump-vs-gas-boiler.md` (about 6 s). Change inputs with `--set name=value` (`--list` shows names); pass the same `--set` options to `--write` and `--check`.
- Quick personal verdict: `python3 heatpump_model.py --me --gas-kwh N --scop X --price P` (or `--gas-m3`). Also `/heat-pump`.
- Done means: `python3 heatpump_model.py --check heat-pump-vs-gas-boiler.md` says OK and `python3 -I check_report.py heat-pump-vs-gas-boiler.md heatpump_model.py` passes every check (independent re-implementation, wording, links, personal-mode agreement; needs network for links).
- When prices change (Ofgem cap each quarter), update the SOURCE inputs in `INPUTS` in `heatpump_model.py`, regenerate, recheck.
