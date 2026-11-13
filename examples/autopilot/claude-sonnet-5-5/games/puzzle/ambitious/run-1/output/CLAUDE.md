
## Mirror Twins (`mirror-twins.html`)
Single-file browser puzzle game. Do not edit the HTML by hand: edit `mirror-twins-tools/template.html` (page), `logic.js` (rules, shared by page and solver) or `final_levels.json` (levels), then rebuild.
- Setup once: `cd mirror-twins-tools && npm i` (needs Google Chrome; set `CHROME` to its binary elsewhere).
- Rebuild: `npm run build` (inlines logic and levels, computes pars with the solver, writes `../mirror-twins.html`).
- Prove it: `npm run check` — 19 checks: solver (solvable, par optimal, each chapter's new element required), real Chrome playthrough of every level, stars, share, layout at 320x568 to 1440x900, contrast, frame time, zero console errors. Must print `19/19`.
- New levels: `npm run gen` (random search into `levels.json`), then `npm run prune` (removes objects that aren't load-bearing) and copy chosen levels into `final_levels.json`.
- Level rules: chars `# . x f g A B a b`; `f` flips orange's left-right rule, `g` its up-down rule.
