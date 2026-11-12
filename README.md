# claude-ambition

**A Claude Code plugin that pushes a model past its defaults.** Left alone, a model narrows the task to the literal request, picks the median method, grades its own work and stops at "good". This plugin pushes it to find the goal behind the task, work like the best practitioner in the field, borrow methods from other fields, prove the result with a check that isn't the model, and make the result cheap to repeat.

```
/be-ambitious
speed up our test suite
```

Inspired by Felix Rieseberg's essay **[How to be more ambitious: a tutorial for humans with models](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/)**. Read it first. This repo turns its ideas into skills, commands and two small hooks. It is an independent project, not affiliated with or endorsed by Anthropic or the author.

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
- **Then it asks: stop here, or push it further?** When the first turn ends, the plugin saves that work as the first version (`.ambition/first/`) and asks, naming what pushing on would add and roughly what it would cost. If the first version is all you wanted, you've paid for nothing extra.
- **Pushing on brings in the method.** Up to four questions, one at a time, then a restatement ("you asked for X, I'm aiming at Y, because Z") you can veto, then every move in order, in the same conversation. The final is built on the first version, and is held to a real outside check against it.
- **Steer it in your own words when you push on.** "Push it further, use your judgement" answers the questions for you and lists the assumptions. You can also ask it to treat the task as a plan, to pause after each step for your notes, to write a log of the run, or to skip the metrics. Plan or build is otherwise detected for you, and plan mode produces an ambitious plan that stops for your approval.
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

[`bench/`](bench/) tests that. Each prompt in [`examples/PROMPTS.md`](examples/PROMPTS.md) is run plainly once, as the baseline, then through `/be-ambitious` (sent first, unseen by Claude) with the same prompt, word for word, on the same model in the same fresh container with a real browser. The bench checks from the transcripts that the plugin's first turn was sent exactly what the baseline was sent, so it's a second plain sample, and the final must beat the better of the two plain versions, by enough to justify its extra cost. We judge by looking: the harness captures every version the same way (frames over time, a loop-seam check, console errors, screenshots and Lighthouse), and we compare them side by side and live.

- **[Results site](https://richardoutram.github.io/claude-ambition/):** baseline, first version and final side by side, each live, with cost and time per turn and our review.
- **[Results table](examples/RESULTS.md):** per example, the verdict, the gate, and the cost and time of the baseline, the preview and the full run.

Only runs of the current plugin are kept as examples.

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
