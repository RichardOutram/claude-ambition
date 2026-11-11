# claude-ambition

**A Claude Code plugin that pushes a model past its defaults.** Left alone, a model narrows the task to the literal request, picks the median method, grades its own work and stops at "good". This plugin pushes it to find the goal behind the task, work like the best practitioner in the field, borrow methods from other fields, prove the result with a check that isn't the model, and make the result cheap to repeat.

```
/be-ambitious speed up our test suite
```

Inspired by Felix Rieseberg's essay **[How to be more ambitious: a tutorial for humans with models](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/)**. Read it first. This repo turns its ideas into skills, commands and agents. It is an independent project, not affiliated with or endorsed by Anthropic or the author.

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
| `/be-ambitious <task>` | skill | **The front door.** Works out whether you want a plan or a build, interviews you for the real goal, runs the whole sequence and reports what changed. |
| `ambition-method` | skill (Claude only) | **The method itself:** the defaults it counters, the seven moves, operating rules and reference notes. It loads whenever ambition is in play and can be preloaded into any agent. |
| `/ambition` … `/ambition-g-lock` | commands | The seven moves as separate steps, for when you want to drive by hand. |
| `ambition-direct` | agent | Makes the first version straight from your request, with only the core of the method. It's the cheap preview, and the floor every later step must beat. |
| `ambition-runner` | agent (Opus) | Does the work one step at a time under an orchestrator, with the method preloaded. |
| `ambition-client` | agent | Stands in for you: answers the runner's questions from a written brief, and never invents answers. |
| `ambition-judge` | agent (Opus) | The outside judge. It sees only the goal, the acceptance criteria and the output, never the reasoning. It runs real checks and cannot edit the work. |

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
/be-ambitious migrate the billing service to the new queue
/be-ambitious --plan how should we approach offline support?
/be-ambitious --auto make the CLI start faster
```

- **Plan or build is detected for you.** Asking for a plan, design or strategy, or being in plan mode, produces an ambitious plan. That plan names its outside check and a stretch option, and stops for your approval. Asking for work produces the full build. `--plan` and `--build` override the detection.
- **A cheap first version first.** Before any question, it makes a first version straight from your request, then stops and asks: stop here, or push it further? It names what pushing on would add and roughly what it would cost. If the first version is all you wanted, you've paid for one quick pass.
- **Then it interviews you.** If you push on, that is up to four questions, one at a time. Your answers set the bar, so "make it good" gets you good, while a specific, hard target gets something closer to it. The final is built on the first version and has to beat it.
- **It always says what changed.** You'll see "you asked for X, I'm aiming at Y, because Z" before any work starts, and you can veto it.
- **Small tasks get a light pass.** A typo fix won't trigger a seven-step run.

| Flag | Effect |
|---|---|
| `--plan` / `--build` | Force the route |
| `--auto` | No checkpoint and no interview. Claude pushes on, answers from the repo and context, lists every assumption, and stops only on high-stakes unknowns. |
| `--delegate` | Orchestrated run using the runner, client and judge agents (below) |
| `--brief <file>` | The brief the client agent answers from |
| `--review me` / `--review claude` | Pause after every step for notes from you, or from the orchestrator |
| `--log` | Write the full run to `.ambition/runs/<date>-<slug>.md` |
| `--no-metrics` | Skip the token metrics block at the end |

You don't always have to type the command. The skill's description tells Claude to use it when you explicitly ask it to "be ambitious about this" or "aim much higher", so phrasing like that can trigger it. Typing `/be-ambitious` is the reliable way.

### 2. Drive the steps yourself

Run `/ambition <task>`, then follow each `Next →` pointer. Any step also works on its own. `/ambition-e-judge` is worth running on any work you don't yet trust.

### 3. Orchestrated: `--delegate`

For runs without you in the loop, comparison runs, or Claude orchestrating other Claudes:

```
            ┌──────── question ────────┐
            ▼                          │
   ambition-client ── answer ──▶  orchestrator ──STEP / ANSWER / NOTES──▶  ambition-runner
   (holds the brief)              (you, or main     ◀── QUESTION / STEP DONE ──  (Opus, method preloaded)
                                   Claude session)
                                        │ goal + criteria only
                                        ▼
                                  ambition-judge ── VERDICT ──▶ back to the runner until PASS
```

There are three roles, and each can be filled by a person or a model:

- **Doer:** the runner.
- **Answerer:** for clarifying questions. That's you, or a client agent holding a brief.
- **Reviewer:** adds notes between steps. That's you, the orchestrator, or nobody.

The runner treats reviewer notes as steering, never as answers. The judge never sees the runner's reasoning.

Because `ambition-method` is a normal skill, any agent you write can preload it:

```yaml
---
name: my-agent
skills:
  - ambition-method
---
```

## Metrics

Each `/be-ambitious` run ends with a small token report covering the main session and every subagent:

```
Metrics (cost: /cost, or total_cost_usd in headless JSON)
total   in 134 · out 80.8k (think 29.0k) · cache read 4.31M · write 170.8k · hit 96% · 53 calls
model   opus-5-5: in 126 · out 61.6k (think 21.6k) · cache read 4.30M · write 149.6k · hit 97% · 49 calls
agent   main: in 118 · out 60.7k (think 21.5k) · cache read 4.24M · write 113.7k · hit 97% · 46 calls
agent   web-fetch ×2: in 8 · out 19.2k (think 7.5k) · cache read 7.9k · write 21.2k · hit 27% · 4 calls
```

A bundled script reads the session transcripts, so the model only reads the summary, which is about 100 tokens. Cost in dollars isn't stored in transcripts. Use `/cost` interactively, or run headless, which reports exact figures:

```sh
claude -p --output-format json "/be-ambitious --auto <task>" \
  | jq '{cost: .total_cost_usd, turns: .num_turns, ms: .duration_ms, models: .modelUsage}'
```

To analyse any past session: `python3 skills/be-ambitious/scripts/ambition-metrics.py <session-id> [--since ISO8601] [--json]`. In headless runs, use the JSON above, because the transcript is only written in full when the run ends.

## Tips

- **Give it a computer.** The method assumes Claude can run code, install tools and reach real data. Without that access, the challenge and judge steps fall back to reasoning, which is the very habit they exist to break.
- **Missing access is the first task.** The essay's "keep the apps crash-free" goal first needed easy access to crash reports, version-to-commit mapping, and real machines on each OS.
- **Falling short at the stretch step is the point.** A broken stretch target shows you where the real limit is.
- **Start long runs with a clean context.** Every API call re-reads the whole conversation, so a run started deep in a long session costs more per step. Start `/be-ambitious` in a fresh session or after `/compact`. Alternatively use `--delegate`, so the heavy work happens in a runner with a fresh context.
- **The lock step is what compounds.** If the result can't be reproduced cheaply, you pay for the ambition again next time.

## Does it actually help?

[`bench/`](bench/) tests that. Each prompt in [`examples/PROMPTS.md`](examples/PROMPTS.md) is run plainly once, as the baseline, then through `/be-ambitious`, word for word, on the same model in the same fresh container with a real browser. The plugin's cheap first version must already match the baseline, and the final must beat it, by enough to justify its extra cost. We judge by looking: the harness captures every version the same way (frames over time, a loop-seam check, console errors, screenshots and Lighthouse), and we compare them side by side and live.

- **[Results site](https://richardoutram.github.io/claude-ambition/):** baseline, first version and final side by side, each live, with cost and time per turn and our review.
- **[Results table](examples/RESULTS.md):** per example, the verdict, the gate, and the cost and time of the baseline, the preview and the full run.

Only runs of the current plugin are kept as examples.

## Manual install (without the plugin system)

```sh
git clone https://github.com/RichardOutram/claude-ambition.git && cd claude-ambition
mkdir -p ~/.claude/commands ~/.claude/skills ~/.claude/agents
ln -sf "$PWD"/commands/ambition*.md ~/.claude/commands/
ln -sf "$PWD"/skills/* ~/.claude/skills/
ln -sf "$PWD"/agents/*.md ~/.claude/agents/
```

## Contributing

Issues and PRs welcome. Keep commands short. The brevity is deliberate, because a long, prescriptive prompt turns the model into a checklist-follower. Use Conventional Commits. Keep the `n/7` labels, `Next →` lines and the tables above in sync. Run `claude plugin validate .` before opening a PR.

## License

[MIT](LICENSE)
