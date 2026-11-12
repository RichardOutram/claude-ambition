# Pushing on

The user chose to push the work further. The work as it stands is the **first version**: it's in `.ambition/first/` (if it isn't, copy the deliverable there now, and add `.ambition/` to the project's .gitignore if it has one that doesn't cover it) and that folder is never edited again. It is the floor: every later move must beat it, at least as good as the kind of thing asked for and better on the goal.

The ambition method is given with these instructions. It defines the seven moves; these instructions run them.

You do all of the work yourself, in this conversation, the way a person runs `/ambition`, `/ambition-b-depth` … `/ambition-g-lock` one after another in one chat. Each move builds on what the last one found. Don't hand moves to subagents. The only place they're welcome is Range, if several fields are worth exploring at once.

**Steps.** Turn 1 was the first version. From here every move is a step, numbered on from it: 2 Altitude (the questions, the restatement and its checkpoint), 3 Depth, 4 Challenge, 5 Range, 6 Judge, 7 Stretch, 8 Lock. Open each step's first message with its marker line on its own, exactly in this form: `▸ Step 3/8 · Depth`. Write the marker nowhere else. When a step ends, copy the deliverable as it stands to `.ambition/steps/<n>/` (for example `.ambition/steps/3/`), even if that step didn't change it, and never edit those copies.

## 0. Read the situation

**Intent.** Decide whether this is a **plan** or a **build**.
- The user said plan or build → that.
- Plan mode is on → plan.
- Words like "plan", "design", "approach", "strategy", "how should we", "proposal", "options", or a request for a document → plan.
- Imperatives like "build", "fix", "add", "implement", "make", "ship", "migrate", "speed up", or an existing approved plan to carry out → build.
- Unclear → make it your first interview question.

**Who answers.** By default, the user, one question at a time. If they said to use your judgement (now or when pushing on), you answer from the repo, the conversation and sensible defaults, and list each answer as a labelled assumption.

**Who reviews between moves.** If the user asked to review each step, pause after each move for their notes. Default: no pause, only the restatement checkpoint below.

## 1. Altitude

**Altitude (move 1, step 2).** Open with `▸ Step 2/8 · Altitude`. Ask up to 4 questions, **one at a time**, with AskUserQuestion when it's available and concrete options drawn from what you can already see. Skip only the questions the user has already answered in this conversation. If the user says to use your judgement, answer the rest yourself as labelled assumptions and don't ask again.
1. What is this ultimately for, and what should happen after it's done?
2. What would make the result unmistakably excellent, both as this kind of thing and for the goal? Push for a specific, hard target, not "good". Include the qualities that can only be judged by looking at it, reading it or using it.
3. What would prove it, other than you? Name a test, a metric, real users or reference output.
4. What access, data or tools are missing? Skip this if it's obvious.

Then restate the task at the level that serves the goal. Altitude **adds to** the request and never replaces it:

```
You asked for:   <original>
Still delivers:  <the original ask, in full, as the same kind of thing>
Genre bar:       <what this kind of thing is judged on by its users and best practitioners, including qualities judged by perception>
Aiming at:       <restated goal>, because <reason>
Excellent means: <specific hard target, on the genre bar and on the goal>
Proven by:       <the outside check: what will be run or rendered and measured, and the comparison with the first version>
Needs access to: <gaps, or "nothing new">
Mode:            plan|build · answerer · reviewer
```

**Checkpoint:** in the default mode, ask the user to confirm or adjust this restatement. If they said to use your judgement, proceed. Never silently drop something the user asked for. If access is missing, getting it is the first piece of work.

## 2. Run every move, in order

Run moves 2 to 7 from the method, every one, in order, as if the user had typed each command. Each opens with its marker and ends with its copy in `.ambition/steps/<n>/` and a short step report: **did / found / changed course**. Reviewer notes are steering, not answers.

**Build on the first version.** Copy `.ambition/first/` to where the deliverable belongs and improve that copy in place. Keep everything that makes it good as this kind of thing. Each change must make it better for the goal without making it worse as this kind of thing.

**No look, no claim.** Whenever you change something people look at, read or use, perceive the result the way they will: render it at the sizes they use and look, read it through, use it. If you can't, get that access first (install a browser or a renderer). If you still can't, say the genre bar is unchecked and leave how it looks, reads or feels as the first version had it.

**Look efficiently.** Every image you look at stays in this conversation and is re-read on every later step. Look at a contact sheet (many frames or sizes in one image) rather than one image per frame, and take at most about three render-and-look rounds per move. Keep working files (screenshots, scripts) under `.ambition/`, not in the deliverable.

**Plan route.** Planning still means touching reality: read the code, query the data and run spikes when they would settle a question.
1. **Depth:** the four statements, then a rewritten task.
2. **Challenge:** assumptions tested against the real material, plus any new finding.
3. **Range:** the verb form, the fields borrowed from with the method taken from each, and what the red team found.
4. **Judge:** define the outside check the build will be held to. If you can build it cheaply now, do: a plan with its acceptance test already written is a stronger plan. Compare the plan with the first version: it must be at least as clear and usable, and better on the goal.
5. **Stretch:** a stretch variant of the plan, with where it would likely break.
6. **Lock:** what will be scripted, noted in CLAUDE.md or made a command once it's built.
7. **Output the plan** with sections for: the original ask and how the plan delivers it · goal beyond the goal · target · approach and instruments · assumptions tested · borrowed methods · outside check · stretch option · what will be locked in. In plan mode, present it through the normal plan-approval step. Otherwise stop and ask for approval.

**Build route.** Depth → Challenge → Range, doing the work as you go. Then:
- **Judge:** run a check that isn't you, and iterate until it passes. Never ask a model to judge it, including another agent. Use tests, a real run, a benchmark, reference output, or a tool you build that measures it (for something visual: render frames at the sizes its audience uses and measure what matters, such as errors, timing, loop seams, layout and contrast, then look at them). Meet the original ask first and keep it passing. Compare the final with the first version on the same check: it must be at least as good on the genre bar and better on the goal. If it isn't, fix it, or deliver the first version plus the improvements that held up.
- **Stretch:** pick a target several times harder and go for it, on top of a working deliverable. Report exactly where it broke. Never leave the deliverable worse than before the stretch.
- **Lock:** script or spec, a short CLAUDE.md note, and a command if the task will recur. Keep each tiny.

Respect the session's permission mode and the user's rules throughout. Ambition never authorises skipping a confirmation the user requires.

## 3. Report

Finish with the following.
- **You asked for → it became:** one line each, plus where the original ask is delivered in full.
- **Against the first version:** where the final is better, anything it gave up, and what the check showed for both.
- **Outside check:** what ran, and what it returned.
- **Stretch:** the target, how far it got, and where it broke.
- **Locked in:** the files created, and how to rerun.
- **Assumptions made** (auto mode, or where the user said to use your judgement), and anything the user should decide.
- **Metrics** (skip if the user asked for none). As your last action, run the metrics command given with these instructions. Paste its output verbatim in a code block, without commentary.

If the user asked for a log, also write the full run to `.ambition/runs/<YYYY-MM-DD>-<slug>.md`: the restatement, every question and answer, every reviewer note, each step report, what each check returned, the final report and the metrics.
