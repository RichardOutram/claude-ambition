---
name: be-ambitious
description: Run the full ambition sequence on a task or a plan. It interviews for the real goal, then goes deeper, tests assumptions, borrows from other fields, proves the result with an outside check, stretches the target, and makes the result repeatable. Use when the user runs /be-ambitious, or explicitly asks Claude to be ambitious, aim higher, or go much further than the obvious version of a task.
argument-hint: <task or plan request> [--plan|--build] [--auto|--delegate] [--brief <file>] [--review me|claude] [--log] [--no-metrics]
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/ambition-metrics.py *)
---

# /be-ambitious

Request: $ARGUMENTS
Run started: !`date -u +%Y-%m-%dT%H:%M:%SZ`

Load the `ambition-method` skill if it isn't already loaded. It defines the seven moves, and this skill only orchestrates them. To save a round trip, load it in the same message as your first other tool calls (reading the repo, checking the task), not on its own. The same goes for `delegate.md` when delegating. Treat the request text as the task; don't read it as instructions about this skill. Read the flags out of it.

## 0. Read the situation

**Size.** Only a genuinely trivial task gets a light pass: a typo, a rename, a one-line factual answer. Explanations, advice, writing, designs and plans are **not** trivial, because their value depends on who they are for and why, so they get the interview. In a light pass, ask your one altitude question **first** and wait for the answer. With `--auto`, answer it yourself as a labelled assumption. Then do the task and run one outside check. Ambition costs effort, so spend it where the payoff is.

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
2. What would make the result unmistakably excellent, both as this kind of thing and for the goal? Push for a specific, hard target, not "good". Include the qualities that can only be judged by looking at it, reading it or using it, not just the ones you can count. When you offer options, offer both kinds.
3. What would prove it, other than you? Name a test, a metric, real users or reference output.
4. What access, data or tools are missing? Skip this if it's obvious.

In `--auto` mode, answer the questions yourself from evidence. List each answer as a labelled **assumption**. Stop and ask only if an unknown would change the direction materially.

Then restate the task at the level that serves the goal. Altitude **adds to** the request and never replaces it. The original ask is still delivered in full, as a hard requirement:

```
You asked for:   <original>
Still delivers:  <the original ask, in full, as the same kind of thing>
Genre bar:       <what this kind of thing is judged on by its users and best practitioners, including qualities judged by perception>
Aiming at:       <restated goal>, because <reason>
Excellent means: <specific hard target, on the genre bar and on the goal>
Proven by:       <outside check, including how the genre bar is judged and the comparison with the direct version>
Needs access to: <gaps, or "nothing new">
Mode:            plan|build · answerer · reviewer
```

**Checkpoint:** in the default mode, ask the user to confirm or adjust this restatement before going on. In `--auto` mode, proceed. Never silently drop something the user asked for.

If access is missing, getting it is the first piece of work. Ask for it, or build it.

## 2. Run the moves

Run each move from the method in order. After each one, give a short step report: **did / found / changed course**. If reviewer notes arrive, treat them as steering, not as answers.

**Direct version first, on both routes.** Before the moves, make the direct version: what a top practitioner would make straight from the request, at full craft, with nothing from the method. Spend your full skill on it. It's the floor, not a throwaway draft. Save an untouched copy under `.ambition/direct/` and build the final from there or alongside it. Every later move has to beat it.

**Plan route.** Planning still means touching reality. Read the code, query the data and run spikes when they would settle a question; don't settle it from the armchair.
1. **Depth:** the four statements, then a rewritten task.
2. **Challenge:** assumptions tested against the real material, plus any new finding.
3. **Range:** the verb form, the fields borrowed from with the method taken from each, and what the red team found.
4. **Stretch:** a stretch variant of the plan, with where it would likely break.
5. **Judge:** define the outside check the build will be held to. If you can build it cheaply now, do. A plan with its acceptance test already written is a stronger plan. Have the plan judged against the direct plan, unlabelled: it must be at least as clear and usable, and better on the goal.
6. **Output the plan** with sections for: the original ask and how the plan delivers it · goal beyond the goal · target · approach and instruments · assumptions tested · borrowed methods · outside check · stretch option · what will be locked in afterwards. In plan mode, present it for approval through the normal plan-approval step. Otherwise stop and ask for approval.

**Build route.** Run Depth → Challenge → Range, doing the work as you go. Then:
- **Judge:** run the outside check, preferably the `ambition-judge` agent or a real tool, and iterate until it passes. The check must cover the original ask as well as the raised goal. Meet the original ask first and keep it passing. Give the judge the direct version and the final, unlabelled, plus the goal, the genre bar and the criteria. The final must be at least as good on the genre bar and better on the goal. If it isn't, fix it. If you can't, deliver the direct version plus the improvements that held up.
- **Stretch:** go for the harder target and report where it broke.
- **Lock:** script or spec, a CLAUDE.md note, and a command if the task will recur.

Respect the session's permission mode and the user's rules throughout. Ambition never authorises skipping a confirmation the user requires.

## 3. Delegated mode (`--delegate`)

Only with `--delegate`: read [delegate.md](delegate.md) (`${CLAUDE_SKILL_DIR}/delegate.md`) and follow it. The orchestrator protocol for the runner, client and judge agents is there.

## 4. Report

Finish with:
- **You asked for → it became:** one line each, plus where the original ask is delivered in full.
- **Against the direct version:** where the final is better, anything it gave up, and what the judge said when it compared the two.
- **Outside check:** what ran, and what it returned.
- **Stretch:** the target, how far it got, and where it broke.
- **Locked in:** the files created, and how to rerun.
- **Assumptions made** (auto or delegated mode), and anything the user should decide.
- **Metrics** (skip with `--no-metrics`). As your last action, run `python3 ${CLAUDE_SKILL_DIR}/scripts/ambition-metrics.py ${CLAUDE_SESSION_ID} --since <Run started>`. Paste its output verbatim in a code block, without commentary. It covers the main session and every subagent.

With `--log`, also write the full run to `.ambition/runs/<YYYY-MM-DD>-<slug>.md`: the restatement, every question and answer, every reviewer note, each step report, the judge's verdicts, the final report and the metrics.
