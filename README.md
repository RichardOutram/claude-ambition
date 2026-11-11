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
- **It interviews you first.** That is up to four questions, one at a time. Your answers set the bar, so "make it good" gets you good, while a specific, hard target gets something closer to it.
- **It always says what changed.** You'll see "you asked for X, I'm aiming at Y, because Z" before any work starts, and you can veto it.
- **Small tasks get a light pass.** A typo fix won't trigger a seven-step run.

| Flag | Effect |
|---|---|
| `--plan` / `--build` | Force the route |
| `--auto` | No interview. Claude answers from the repo and context, lists every assumption, and stops only on high-stakes unknowns. |
| `--delegate` | Orchestrated run using the runner, client and judge agents (below) |
| `--brief <file>` | The brief the client agent answers from |
| `--review me` / `--review claude` | Pause after every step for notes from you, or from the orchestrator |
| `--log` | Write the full run to `.ambition/runs/<date>-<slug>.md` |

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

## Tips

- **Give it a computer.** The method assumes Claude can run code, install tools and reach real data. Without that access, the challenge and judge steps fall back to reasoning, which is the very habit they exist to break.
- **Missing access is the first task.** The essay's "keep the apps crash-free" goal first needed easy access to crash reports, version-to-commit mapping, and real machines on each OS.
- **Falling short at the stretch step is the point.** A broken stretch target shows you where the real limit is.
- **The lock step is what compounds.** If the result can't be reproduced cheaply, you pay for the ambition again next time.

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
