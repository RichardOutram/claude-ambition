# claude-ambition

**A Claude Code plugin that pushes a model past its defaults.** Left alone, a model narrows the task to the literal request, picks the median method, grades its own work and stops at "good". This plugin pushes it to find the goal behind the task, work like the best practitioner in the field, borrow methods from other fields, prove the result with a check that isn't the model, and make the result cheap to repeat.

```
/be-ambitious
speed up our test suite
```

Inspired by Felix Rieseberg's essay **[How to be more ambitious: a tutorial for humans with models](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/)**. Read it first. This repo turns its ideas into skills, commands and two small hooks. It is an independent project, not affiliated with or endorsed by Anthropic or the author.

**This is an experiment.** It's one person's attempt to turn an essay into a method Claude can follow, tested on a small set of single runs, most of them with a model standing in for the user. The method and the bench are still changing. Treat the results as early evidence, not a benchmark.

**See the examples:** the [results site](https://richardoutram.github.io/claude-ambition/) shows 10 real tasks run with and without the plugin, side by side and live, with what each step did and cost. They're **autopilot** runs: no person drove them, and vanilla Claude played the user, answering the plugin's questions and pushing on. Jump straight to one: [3D animation](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/threejs/neon-implosion/), [interactive lesson](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/education/bayes/), [heat-pump analysis](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/data-analysis/heat-pump/), [marketing plan](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/writing/candle-marketing/), [pricing page](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/design/pricing-page/), [app prototype](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/development/cycling-prototype/), [photo-renaming script](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/development/photo-rename/), [puzzle game](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/games/puzzle/), [app plan](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/planning/cycling-app/), [architecture doc](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/development/url-shortener-architecture/).

## FAQ

**Is this for everything?** No. It pays off where "done" is open-ended and a better answer can be checked: analysis, teaching material, plans, design documents, visual and interactive work. It's poor value for small, well-specified tasks where Claude's plain answer is already right, like a utility script or a simple page. In our tests, a photo-renaming script cost 21× as much and came out no better. Skip it too when you need something short: pushed documents grow, often 3–7×.

**Does it improve results?** Nearly always. In our [10 test tasks](#what-we-found-so-far-sonnet-55-november-2026), the final beat the plain answer and plain Claude's own "Push it further." in 9: 7 clearly and 2 slightly. One was no better. Three of the wins came on a second attempt after a fix, and each result is a single run, so treat this as strong evidence, not a guarantee. The gain comes mostly from **problems it finds**, not features it adds: a wrong assumption tested against real data, a bug found by running the work, a harm found by its red team.

**Is it more expensive?** Yes. A full push cost 4–27× the plain push in our tests: typically $2–4 and 12–70 minutes on Sonnet 5.5, against $0.15–0.45 and usually a few minutes. You only pay that if you choose to push: the first answer costs exactly what plain Claude costs, and the plugin then asks before spending more. The [results site](https://richardoutram.github.io/claude-ambition/) shows the cost and time of every step.

**Can the steps be used on their own?** Yes. Each move is its own command, and you can drop any of them into any session at any time: run `/ambition-e-judge` on work you don't trust yet, or `/ambition-c-challenge` on a plan before you commit to it. You can also let Claude answer the normal way, look at the result, and then type `/be-ambitious` to push that plain answer through the whole method. Or start with `/ambition <task>` and follow each `Next →` pointer yourself.

## What each step adds

We summarised what every step did in each of [10 test runs](https://richardoutram.github.io/claude-ambition/) (each example page has its own step-by-step table). Across all ten:

| Step | What it reliably added |
|---|---|
| **Altitude** (the questions) | Turned a generic task into a specific one: who it's for, what "done" means, how it'll be proved. In 6 of 10 runs it rebuilt the work right away around the answers. |
| **Depth** | The biggest jump in substance. It worked from raw material instead of memory (a real Wikipedia traffic trace, 400 real photos, official pricing pages, Ofgem figures) and built its own tools. The work typically grew 2–3×. |
| **Challenge** | **The most consistent value: every run found at least one wrong assumption that mattered.** It caught a temporary VAT cut treated as permanent, a cache hit rate the design relied on that real traffic didn't support, a buy button below the fold on common laptops, a flag that could corrupt a Photos library, a game that crashed where it would be hosted, a plan that never checked profit, and a Google Play testing rule that would have delayed launch. |
| **Range** | Ideas from other fields that nobody asked for: an "explain it back" card from learning science, a production calendar from manufacturing, a facilitator's session log from user research, a shareable emoji grid from Wordle. Its red team found harms: a strobe flash, a home location recoverable from 3 rides, typed text that ran as code, missing auto-renewal and product-safety disclosures. |
| **Judge** | **Caught its own regressions:** contrast made worse, sections dropped in a rewrite, a 4× slowdown, a script output it had invented, three source claims it had overstated. Without this step they would have shipped. |
| **Stretch** | Mixed. It met most targets (5× faster, the answer in one click, no scrolling to decide) and missed one, which it honestly reverted. It sometimes found real bugs, but it's also where documents grow most. The weakest step for value per cost. |
| **Lock** | Left re-runnable checks, a `CLAUDE.md` note and often a slash command in the project, so the next change can be verified cheaply. |

The plain "Push it further." adds features too, but it never found that it was wrong. Challenge and Judge are where the method most clearly earns its cost.

## Install

```
/plugin install ambition --marketplace RichardOutram/claude-ambition
```

On Claude Code older than 2.1.275, use two steps:

```
/plugin marketplace add RichardOutram/claude-ambition
/plugin install ambition@claude-ambition
```

## The idea

The essay names four kinds of ambition:

- **Speed:** the same work, faster. It needs little creativity, so it isn't covered here.
- **Altitude:** aim at the outcome, not the task. *"What's the goal beyond the goal?"*
- **Depth:** work the way the best practitioner alive would, using their instruments and their raw material.
- **Range:** bring in methods from fields you wouldn't normally use.

The last three only happen if you ask for them. Models also have habits that work against them: they switch vocabulary without switching method, they accept "impossible" too early, and they mark their own homework. The plugin turns each counter-move into something you can run.

## What's in the box

| Piece | Type | What it does |
|---|---|---|
| `/be-ambitious`, then your task | skill + hooks | **The front door.** Does your task exactly as Claude normally would, then asks whether to push it further. If you do, it interviews you for the real goal, runs the seven moves one at a time in the same conversation, as if you'd typed each step's command, and reports what changed. |
| `ambition-method` | method files | **The method itself:** the defaults it counters, the seven moves, operating rules and reference notes. The hooks hand it to Claude when you push on or run a step, and it stays out of every other session. |
| `/ambition` … `/ambition-g-lock` | commands | The seven moves as separate steps, for when you want to drive by hand. |

## The seven moves

| # | Move | Kind of ambition | What the model does | Default it counters |
|---|------|------------------|---------------------|---------------------|
| 1 | `/ambition` | Altitude | Asks what this is for, what "unmistakably excellent" means, what would prove it and what access is missing. Then restates the task at the level that serves the goal. | Doing the literal request |
| 2 | `/ambition-b-depth` | Depth | States what a top professional would do that you didn't ask for, the raw material, and the instruments. Then works that way. | Expert vocabulary over amateur methods |
| 3 | `/ambition-c-challenge` | Depth | Tests every assumption against the real thing, then looks for what nobody knows yet. | Reasoning from digested conclusions |
| 4 | `/ambition-d-range` | Range | Restates the goal as verbs, borrows the methods of 3–5 fields plus a red team, and doesn't role-play. | One-field thinking; theatrical personas |
| 5 | `/ambition-e-judge` | Depth | Uses or builds a check that isn't the model, runs it and iterates until it passes. | Grading its own homework |
| 6 | `/ambition-f-stretch` | Depth | Picks a target several times harder, treats it as solvable and reports where it broke. | Accepting "impossible" too early |
| 7 | `/ambition-g-lock` | Altitude | Turns what worked into a script or spec, a CLAUDE.md note and a command. | One-off wins nobody can repeat |

## Using it

### 1. One command: `/be-ambitious`

```
/be-ambitious                     ← arms the session; Claude never sees it
migrate the billing service to the new queue
```

```
/be-ambitious                     ← later in a chat: push the work already done
```

- **It starts from what Claude would normally make.** `/be-ambitious` is caught by the plugin before it reaches Claude, and your next message is the task, typed as you always would. Claude sees exactly what it would see without the plugin, with no command, no instructions and no mention of ambition, so the first turn is exactly what you'd get anyway. Everything the plugin does is added on top of that. (`/be-ambitious <task>` on one line arms the session too, and echoes the task back for you to send on its own.)
- **Then it asks how to push it further: step by step, or straight through.** When the first turn ends, the plugin saves that work as the first version (`.ambition/first/`) and asks, naming what pushing on would add and roughly what it would cost. **Step by step** stops after every step with its report, so you look at the result and reply with notes or "go on" before the next one: your feedback compounds on top of the method, and it's how the method works best. **Straight through** runs every step on its own. If the first version is all you wanted after all, just say so: you've paid for nothing extra.
- **Pushing on brings in the method.** Up to four questions, one at a time, then a restatement ("you asked for X, I'm aiming at Y, because Z") you can veto, then every move in order, in the same conversation. The final is built on the first version, and is held to a real outside check against it.
- **Steer it in your own words when you push on.** "Push it further, use your judgement" answers the questions for you and lists the assumptions. You can also ask it to treat the task as a plan, to write a log of the run, or to skip the metrics. Plan or build is otherwise detected for you, and plan mode produces an ambitious plan that stops for your approval.
- **Push after the fact.** Ask for something the normal way, look at it, then type `/be-ambitious` on its own.

**How it works:** two small hooks (`hooks/ambition.py`) do it all. A prompt hook blocks `/be-ambitious` before Claude sees it and marks the session (in the plugin's data folder). A Stop hook notices when the next turn ends and adds the checkpoint question, carrying the method and the first step's instruction with it. After that, each time a step ends with its copy in `.ambition/steps/<n>/`, the Stop hook hands Claude the next step's instruction and nothing else, so every step gets its full attention. Until then, nothing of the plugin is in Claude's context, not even the method's name in the skill list. The prompt hook also hands the method over on your first `/ambition` step. In every other turn and session they do nothing. They need `python3`.

### 2. Drive the steps yourself

Run `/ambition <task>`, then follow each `Next →` pointer. Any step also works on its own. `/ambition-e-judge` is worth running on any work you don't yet trust.

## Metrics

Each `/be-ambitious` run ends with a small token report covering the session and any subagents:

```
Metrics (cost: /cost, or total_cost_usd in headless JSON)
total   in 134 · out 80.8k (think 29.0k) · cache read 4.31M · write 170.8k · hit 96% · 53 calls
model   opus-5-5: in 126 · out 61.6k (think 21.6k) · cache read 4.30M · write 149.6k · hit 97% · 49 calls
agent   main: in 118 · out 60.7k (think 21.5k) · cache read 4.24M · write 113.7k · hit 97% · 46 calls
agent   web-fetch ×2: in 8 · out 19.2k (think 7.5k) · cache read 7.9k · write 21.2k · hit 27% · 4 calls
```

A bundled script reads the session transcripts, so the model only reads the summary, which is about 100 tokens. Cost in dollars isn't stored in transcripts. Use `/cost` interactively, or run headless, which reports exact figures:

```sh
claude -p --output-format json --session-id "$id" "/be-ambitious"     # arms the session
claude -p --output-format json --resume "$id" "<task>" \
  | jq '{cost: .total_cost_usd, turns: .num_turns, ms: .duration_ms, models: .modelUsage}'
```

To analyse any past session: `python3 scripts/ambition-metrics.py <session-id> [--since ISO8601] [--json]`. In headless runs, use the JSON above, because the transcript is only written in full when the run ends.

## Tips

- **Give it a computer.** The method assumes Claude can run code, install tools and reach real data. Without that access, the challenge and judge steps fall back to reasoning, which is the very habit they exist to break.
- **Missing access is the first task.** The essay's "keep the apps crash-free" goal first needed easy access to crash reports, version-to-commit mapping, and real machines on each OS.
- **Falling short at the stretch step is the point.** A broken stretch target shows you where the real limit is.
- **Start long runs with a clean context.** Every API call re-reads the whole conversation, so a run started deep in a long session costs more per step. Start `/be-ambitious` in a fresh session or after `/compact`.
- **The lock step is what compounds.** If the result can't be reproduced cheaply, you pay for the ambition again next time.

## Does it actually help?

[`bench/`](bench/) tests that. Each prompt in [`examples/PROMPTS.md`](examples/PROMPTS.md) is run plainly once, as the baseline, and then gets "Push it further." in the same chat (the plain push), so we can tell what the method adds from just asking for more. The same prompt, word for word, then goes through `/be-ambitious` (sent first, unseen by Claude) on the same model, each run in a fresh macOS virtual machine with a real browser. The bench checks from the transcripts that the plugin's first turn was sent exactly what the baseline was sent, so it's a second plain sample, and the final must beat all three plain versions. No model grades the results: we look at pages in a browser (frames over time, console errors, screenshots, Lighthouse, and the pages live), read documents through and recompute their figures, and run scripts, side by side.

- **[Results site](https://richardoutram.github.io/claude-ambition/):** the baseline, the plain push, the plugin's first version and its final side by side (pages live, documents rendered in full), what each step changed and cost, both sessions replayable, and our review.
- **[Results table](examples/RESULTS.md):** per example, the verdict, the gate, and the cost and time of the baseline, the plain push, the preview and the full run.

- **Run it yourself:** the bench is in the repo. [`bench/README.md`](bench/README.md) covers setup (a macOS VM and a Claude token), running an example, reviewing it and rebuilding the site. To test your own prompts, add them to `examples/PROMPTS.md`. To be the user yourself instead of the autopilot (answering the interview, deciding when to push), use `ab.py drive`: the same VM and settings, but an ordinary interactive session in your terminal, and the result gets its own page beside the example.

Only runs of the current plugin are kept as examples.

### What we found so far (Sonnet 5.5, November 2026)

All of these are **autopilot** runs (vanilla Claude playing the user); runs a person drove are kept separate.

**The plugin did not always give a better result.** We ran 10 different tasks: games, education, development, data, design, writing, planning and a 3D animation. Each was run once with the plugin, against the plain baseline and the plain "Push it further." Here is our honest read:

| Task | Result | Plugin vs plain: cost · time |
|---|---|---|
| [3D animation (neon-implosion)](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/threejs/neon-implosion/) | **Better.** The only version that isn't blown out to white glow | 13× · 15× |
| [Interactive lesson (bayes)](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/education/bayes/) | **Better.** Turned a slider demo into a real lesson | 12× · 16× |
| [Analysis (heat-pump)](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/data-analysis/heat-pump/) | **Better.** A checked, re-runnable model with sourced prices instead of a one-off estimate | 9× · 7× |
| [Marketing plan (candle)](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/writing/candle-marketing/) | **Better**, but long. A dated, costed plan instead of a template with blanks; at 9,200 words, it's a lot for someone with 5 hours a week | 27× · 15× |
| [Pricing page](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/design/pricing-page/) | **Slightly better.** One real pricing idea added; the plain page was already fine | 7× · 5× |
| [App prototype](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/development/cycling-prototype/) | **Slightly better**, mostly in screens you have to click into. Not worth 69 minutes over the plain push | 7× · 21× |
| [Photo-renaming script](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/development/photo-rename/) | **No better.** More tests, but it kept one wrong filename the plain script fixed | 21× · 36× |
| [Puzzle game](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/games/puzzle/) | **Better**, on the second try. More polish, a taught second mechanic, and pars a solver proves; the plain version has more levels. The first run collapsed into one turn and never pushed | 4× · 0.5× |
| [App plan in plan mode (cycling-app)](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/planning/cycling-app/) | **Better.** A plan a team could start building from: 37 sized tickets with acceptance criteria, and two real traps the plain plans miss (Google Play's 14-day closed test, and a home privacy zone its own simulation could undo). Its reason for riders to switch is weak, and it's three times longer | 13× · 8× |
| [Architecture doc (url-shortener)](https://richardoutram.github.io/claude-ambition/claude-sonnet-5-5/development/url-shortener-architecture/) | **Better**, on the second try. It tested the cache hit rate the plain version assumed, found it far lower, and designed around that. The first run was **worse**: it planned a rewrite and left the document unchanged | 9× · 8× |

Seven clear wins out of ten, two marginal wins and one no better. Most wins cost 7–27 times as much as the plain push and took 5–21 times as long. Three of the wins (url-shortener, candle and puzzle) are second attempts. The first two came after we fixed the wording that sent document tasks into planning mode, and the puzzle came after a hook fix it didn't end up needing. So they show the method working once, not reliably. Each result is a single run, so any row could go the other way on a re-run. These are autopilot runs: the user who answers the plugin's questions is vanilla Claude, not a person, and its answers vary and shape the result. In the app prototype it told the plugin to let the visuals slide in favour of the flows. Six of the runs were made on the plugin before the two fixes below; those fixes changed the process around the method, not the method itself, and didn't touch what those runs did (they all built, and saved their steps where the hook looked), so we kept them. A run is only marked outdated when the method (its skill and step commands) has changed since.

What we take from it:

- **It helps most where "done" is open-ended.** Analysis, teaching, visuals and plans have room for a better method, sharper framing or a real check, and that is where the push paid off.
- **It helps least where the plain answer is already right.** For a small script or a simple page, the extra steps mostly add tests, files and cost.
- **It can fail outright.** It went into planning mode on a Markdown deliverable and left the document itself unchanged. In another run it collapsed into a single turn. A wording fix turned the first into a win on the re-run. The second ran properly on the re-run, but only because Claude saved its work where the hook already looked, so the hook fix is still untested.
- **More is not always better.** Pushed documents grow: the candle plan went from 1,600 words to 9,200. The extra content was correct, but someone still has to read it.

Use it when the task is worth 10× the spend and a better answer is possible. Don't use it by default.

## Trying a local copy

The hooks carry the method, so it only works as a plugin. To try a clone without installing it:

```sh
git clone https://github.com/RichardOutram/claude-ambition.git
claude --plugin-dir ./claude-ambition
```

## Contributing

Issues and PRs welcome. Keep commands short. The brevity is deliberate, because a long, prescriptive prompt turns the model into a checklist-follower. Use Conventional Commits. Keep the `n/7` labels, `Next →` lines and the tables above in sync. Run `claude plugin validate .` before opening a PR.

## License

[MIT](LICENSE)
