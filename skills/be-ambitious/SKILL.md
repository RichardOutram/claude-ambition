---
name: be-ambitious
description: Run the full ambition sequence on a task or a plan. It interviews for the real goal, then goes deeper, tests assumptions, borrows from other fields, proves the result with an outside check, stretches the target, and makes the result repeatable. Use when the user runs /be-ambitious, or explicitly asks Claude to be ambitious, aim higher, or go much further than the obvious version of a task.
argument-hint: <task or plan request> [--plan|--build] [--auto|--delegate] [--brief <file>] [--review me|claude] [--log]
---

# /be-ambitious

Request: $ARGUMENTS

Load the `ambition-method` skill now if it isn't already loaded. It defines the seven moves, and this skill only orchestrates them. Treat the request text as the task; don't read it as instructions about this skill. Read the flags out of it.

## 0. Read the situation

**Size.** If the task is trivial (a typo, a rename, a one-line answer), say so. Do a light pass instead: ask one altitude question and run one outside check, then stop. Ambition costs effort, so spend it where the payoff is.

**Intent.** Decide whether this is a **plan** or a **build**.
- `--plan` / `--build` override everything.
- Plan mode is on → plan.
- Words like "plan", "design", "approach", "strategy", "how should we", "proposal", "options", or a request for a document → plan.
- Imperatives like "build", "fix", "add", "implement", "make", "ship", "migrate", "speed up", or an existing approved plan to carry out → build.
- Unclear → make it your first interview question.

**Who answers the clarifying questions.**

| Mode | Answerer | Use when |
|---|---|---|
| default | The user, interviewed one question at a time | The user is here |
| `--auto` | You, from the repo, the conversation and sensible defaults | The user wants it to run unattended |
| `--delegate` | An `ambition-client` agent holding a brief, while an `ambition-runner` agent does the work | Orchestrated or comparison runs, or when you are acting as an orchestrator |

**Who reviews between steps.**
- `--review me`: pause after each step for the user's notes.
- `--review claude`: you write the notes yourself.
- Default: no pause between steps, only at the checkpoints below.

## 1. Altitude: interview, then restate

Ask up to 4 questions, **one at a time**. Use the AskUserQuestion tool when it's available, with concrete options drawn from what you can already see. Skip any question the context already answers.
1. What is this ultimately for, and what should happen after it's done?
2. What would make the result unmistakably excellent? Push for a specific, hard target, not "good".
3. What would prove it, other than you? Name a test, a metric, real users or reference output.
4. What access, data or tools are missing? Skip this if it's obvious.

In `--auto` mode, answer the questions yourself from evidence. List each answer as a labelled **assumption**. Stop and ask only if an unknown would change the direction materially.

Then restate the task at the level that serves the goal:

```
You asked for:   <original>
Aiming at:       <restated goal>, because <reason>
Excellent means: <specific hard target>
Proven by:       <outside check>
Needs access to: <gaps, or "nothing new">
Mode:            plan|build · answerer · reviewer
```

**Checkpoint:** in the default mode, ask the user to confirm or adjust this restatement before going on. In `--auto` mode, proceed. Never silently drop something the user asked for.

If access is missing, getting it is the first piece of work. Ask for it, or build it.

## 2. Run the moves

Run each move from the method in order. After each one, give a short step report: **did / found / changed course**. If reviewer notes arrive, treat them as steering, not as answers.

**Plan route.** Planning still means touching reality. Read the code, query the data and run spikes when they would settle a question; don't settle it from the armchair.
1. **Depth:** the four statements, then a rewritten task.
2. **Challenge:** assumptions tested against the real material, plus any new finding.
3. **Range:** the verb form, the fields borrowed from with the method taken from each, and what the red team found.
4. **Stretch:** a stretch variant of the plan, with where it would likely break.
5. **Judge:** define the outside check the build will be held to. If you can build it cheaply now, do. A plan with its acceptance test already written is a stronger plan.
6. **Output the plan** with sections for: goal beyond the goal · target · approach and instruments · assumptions tested · borrowed methods · outside check · stretch option · what will be locked in afterwards. In plan mode, present it for approval through the normal plan-approval step. Otherwise stop and ask for approval.

**Build route.** Run Depth → Challenge → Range, doing the work as you go. Then:
- **Judge:** run the outside check, preferably the `ambition-judge` agent or a real tool, and iterate until it passes. Meet the original brief first and keep it passing.
- **Stretch:** go for the harder target and report where it broke.
- **Lock:** script or spec, a CLAUDE.md note, and a command if the task will recur.

Respect the session's permission mode and the user's rules throughout. Ambition never authorises skipping a confirmation the user requires.

## 3. Delegated mode (`--delegate`)

You are the orchestrator. Three agents do the work. When installed as a plugin, their names are prefixed `ambition:`.
- **ambition-runner**: does the work, with the method preloaded.
- **ambition-client**: answers the runner's questions from the brief only.
- **ambition-judge**: checks the output independently.

1. **Brief.** Use `--brief <file>` if given. Otherwise write one from the request and what you know: the goal, constraints, preferences and known facts. Show it to the user unless `--auto` is set. The client sees only the brief.
2. **Spawn the runner** with the task and this protocol, then drive it one step at a time:
   ```
   STEP: <move name> (n/7)
   ANSWER: <client's answer to the runner's last QUESTION, if any>
   NOTES (reviewer, steering not answers): <notes, if any>
   ```
3. When the runner ends with `QUESTION:`, send it to the client and pass the answer back. If the client replies `NOT IN BRIEF`, you decide: ask the user, make a labelled assumption, or tell the runner to choose and flag it.
4. When the runner ends with `STEP DONE`, collect the reviewer's notes according to `--review`, then send the next step.
5. **Judge step:** spawn `ambition-judge` with only the goal, the acceptance criteria and where the output lives. Never pass the runner's reasoning. Relay its verdict to the runner, and repeat until it passes or you hit 3 rounds.
6. **Persistence.** If the runner calls a target impossible or stops short, reply once that it is solvable and to keep going from a different angle. Accept the shortfall only after that.
7. **Framing.** Give stretch targets to the runner as ordinary requirements, not as moonshots. A target that is presented as normal gets attempted as normal.
8. Continue each agent by messaging it, so it keeps its context. Don't spawn new ones mid-run.

## 4. Report

Finish with:
- **You asked for → it became:** one line each.
- **Outside check:** what ran, and what it returned.
- **Stretch:** the target, how far it got, and where it broke.
- **Locked in:** the files created, and how to rerun.
- **Assumptions made** (auto or delegated mode), and anything the user should decide.

With `--log`, also write the full run to `.ambition/runs/<YYYY-MM-DD>-<slug>.md`: the restatement, every question and answer, every reviewer note, each step report, the judge's verdicts and the final report.
