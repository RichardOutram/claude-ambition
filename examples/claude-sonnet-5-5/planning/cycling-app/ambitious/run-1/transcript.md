# plan/cycling-app · ambitious

### User

Make a plan for a react native expo social gamified fitness tracker app for the cycling niche, and save it to disk

**→ Write** `{"file_path": "/cfg/plans/make-a-plan-for-jaunty-wren.md", "content": "# Plan: \"Peloton Pals\"-style Social Gamified Cycling Tracker (React Native + Expo)\n\nWorking name: **SpokeQuest** (placeholder).\n\n## Context\nCyclists use Strava for tracking and social, but its gamification is thin (segments/KOMs, kudos). Casual and commuter cyclists lack motivation hooks like streaks, quests, and team pl … [7220 more chars]`

<details><summary>result</summary>

```
File created successfully at: /cfg/plans/make-a-plan-for-jaunty-wren.md (file state is current in your context — no need to Read it back)
```

</details>

**→ ToolSearch** `{"query": "select:ExitPlanMode", "max_results": 1}`

<details><summary>result</summary>

```

```

</details>

**→ ExitPlanMode** `{"plan": "# Plan: \"Peloton Pals\"-style Social Gamified Cycling Tracker (React Native + Expo)\n\nWorking name: **SpokeQuest** (placeholder).\n\n## Context\nCyclists use Strava for tracking and social, but its gamification is thin (segments/KOMs, kudos). Casual and commuter cyclists lack motivation hooks like streaks, quests, and team play. SpokeQuest is a cycling-only app that records rides, then … [7220 more chars]`

<details><summary>result</summary>

```
User has approved your plan. You can now start coding. Start with updating your todo list if applicable

Your plan has been saved to: /cfg/plans/make-a-plan-for-jaunty-wren.md
You can refer back to it if needed during implementation.

## Approved Plan:
# Plan: "Peloton Pals"-style Social Gamified Cycling Tracker (React Native + Expo)

Working name: **SpokeQuest** (placeholder).

## Context
Cyclists use Strava for tracking and social, but its gamification is thin (segments/KOMs, kudos). Casual and commuter cyclists lack motivation hooks like streaks, quests, and team play. SpokeQuest is a cycling-only app that records rides, then layers on XP/levels, quests, territory capture, clubs, and a social feed. Greenfield project in `<workspace>` (currently empty), so no existing code to reuse.

## Target users
Commuters, weekend road/gravel/MTB riders, and club groups. Cycling-specific: elevation, cadence/power (BLE), segments, group rides, bike maintenance.

## MVP scope (v1)
1. Auth and profile (email, Apple, Google), bike garage.
2. GPS ride recording (foreground + background), live stats, auto-pause.
3. Ride summary: map, elevation, splits, XP earned.
4. Gamification: XP, levels, streaks, badges, weekly quests.
5. Social: follow, feed, kudos, comments, clubs, club leaderboards.
6. Push notifications.

Post-MVP: BLE sensors (HR/power/cadence), territory capture ("Zones"), live group rides, segments, Strava/Garmin/Apple Health import, challenges with sponsors, subscription tier, bike maintenance tracker.

## Tech stack
- **Expo SDK (current) + TypeScript**, dev builds via EAS (required for background location and BLE; Expo Go is insufficient).
- Navigation: **Expo Router** (file-based).
- State: **Zustand** (local/ride state) + **TanStack Query** (server state).
- Maps: **react-native-maps** or **@rnmapbox/maps** (Mapbox preferred for custom styling, offline tiles, route layers).
- Location: **expo-location** + **expo-task-manager** (background updates); persist points in  … [5643 more chars]
```

</details>

### Assistant

I've written the plan and saved it to `/cfg/plans/make-a-plan-for-jaunty-wren.md`. The working name is SpokeQuest, which is only a placeholder. I haven't started any code. The working directory was empty, so I didn't explore anything first.

- **MVP:**
  - Auth, a bike garage, and GPS ride recording that keeps working in the background.
  - A ride summary with a map and the XP earned.
  - Gamification through XP, levels, weekly streaks, badges and weekly quests.
  - Social features: a feed, kudos, clubs and leaderboards.
- **Stack:** Expo with TypeScript and Expo Router, Zustand and TanStack Query for state, Mapbox for maps, and a SQLite buffer so a crash doesn't lose a ride. Supabase (Postgres with PostGIS) is the backend. Background location needs EAS dev builds, so Expo Go won't be enough.
- **Anti-cheat and privacy:** XP is calculated on the server, with checks for car rides and GPS jumps. Privacy zones hide the start and end of rides near home.
- **Timeline:** about 12 weeks from setup to store submission, split into phases.
- **After the MVP:** Bluetooth sensors, a territory-capture mechanic, segments, Strava and Garmin imports, and a premium tier.

The plan also covers the data model, risks and how to test it end to end.

The plan ends with four questions that would change it:
- Is this a solo build or a team?
- How will it make money?
- Which map provider, and what budget?
- What launch region, and iOS first or both platforms?

### Context (injected)

<details><summary>show</summary>

Stop hook feedback:
Before you finish:
1. Copy the deliverable you just made into `.ambition/first/`. If the project has a .gitignore that doesn't cover `.ambition/`, add it. Never edit that folder again.
2. Unless the task was trivial (a typo, a rename, a one-line answer), end with one question, using AskUserQuestion when it's available:
   - Stop here: keep it as it is.
   - Push it further: name the two or three improvements you'd go after, and roughly what that costs against what's been spent so far.
   Ask nothing else. Keep this brief: your reply about the work is already above.
3. If they push on, do the first step below, and only that step.

# The ambition method

Left to their defaults, models do the task as typed, pick the median method and grade their own work, then stop at "good". This method pushes against each of those defaults. It comes from Felix Rieseberg's essay [How to be more ambitious: a tutorial for humans with models](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/). Where this skill adds something the essay doesn't say, it is marked *(ours)*.

## The defaults you are working against

| Default | What it looks like | Counter |
|---|---|---|
| Literal scope | Doing the task as typed, not what it is for | Altitude |
| Costume expertise | Expert vocabulary over amateur methods, such as markdown tables where a statistician would use a database and a model | Depth: instruments |
| Digested inputs | Working from summaries and someone else's conclusions | Depth: raw material |
| Unchecked beliefs | Taking the framing you were given as fact | Challenge |
| One-field thinking | Solving it the way this field always does | Range |
| Self-grading | "I reviewed it and it looks correct" | Outside judge |
| Modest targets | Settling, or calling something impossible too early | Stretch |
| One-off wins | A result nobody can reproduce next time | Lock |

## The four kinds of ambition

- **Speed:** the same work, faster. It needs little creativity, so this method skips it.
- **Altitude:** aim at the outcome rather than the task. Ask "what do you want to happen next?" and "what's the goal beyond the goal?" Example: stop fixing individual crashes and aim to keep the app crash-free.
- **Depth:** work the way the best practitioner alive would, and keep pushing until even they might learn something from the result.
- **Range:** look at the work through several fields. That used to be uneconomical. Multi-agent setups make it cheap.

## The floor *(ours)*

The method has to beat what a strong model makes from the plain request. A result that's worse than that is a failure, however much work went into it. The usual way to fail: effort flows to what can be measured, while the qualities the work is really judged on go unnamed and lose every trade-off. Four rules prevent it:

1. **Name the genre bar.** Every request names a kind of thing: a landing page, an essay, a function, a plan, a circuit. Its users and its best practitioners judge it on particular qualities, and some of them can only be judged by perceiving the thing: how it looks, reads, sounds or feels to use. Name them. They are part of the original ask, and they count as much as anything you can measure.
2. **Make the first version first.** Before raising anything, do the request the way you would without this method: the plain answer a strong session gives. `/be-ambitious` makes it before this skill loads. Keep a copy untouched. It is your floor and your reference.
3. **Build on it, and beat it on its own terms.** Start the final from the first version, not from scratch, so its craft carries through. The final must be better on every part of the ask and on the goal, and worse on nothing, the genre bar included. If a move trades genre quality for something measurable, undo that trade. If the final can't beat the first version, deliver the first version plus the improvements that held up.
4. **No look, no claim.** Qualities judged by perception are checked by perceiving: render it and look, read it through, use it. If you can't, get that access before changing them. If you still can't, report them as unchecked and leave them as the first version had them.

## The seven moves

The `/ambition*` commands and `/be-ambitious` run these in this order. Details and worked examples are in `reference/`.

1. **Altitude: find the goal beyond the goal.**
   - What is this ultimately for?
   - What would make the result unmistakably excellent? It must be specific and hard. "Good" is not an answer.
   - What, other than me, would prove it?
   - What access am I missing?

   Then restate the task at the level that serves the goal. That restatement adds to the original ask and raises all of it: every part the request names is done at its best, not just delivered, and the goal beyond comes on top. *(ours)* The noun stays: the raised goal is what the artifact must achieve, not a different artifact. *(ours)* The ladder runs: feed in all the data → ask for decisions → question whether the artifact should exist at all. That last rung is a proposal to the user, never something you do on your own. Tell-tale sign that altitude applies: people would hold meetings about this work.
2. **Depth: deeper, not bigger.** Before working, state four things:
   1. what a top professional would do that wasn't asked for;
   2. the rawest material they would start from;
   3. the specific methods and instruments they would use;
   4. what, other than you or the user, would show the result is right.

   Then rewrite your own task to ask for exactly that, and do it. Use their real instruments, not their vocabulary.
3. **Challenge: test what we think we know.**
   - List the assumptions in the request and in your approach.
   - Try to reproduce each one from the raw material: run it, read the source, query the data. Reasoning alone doesn't count.
   - Once you are inside the material, look for something new: a blind spot, an earlier signal, a finding you can check on data you held back.
4. **Range: borrow methods from other fields.**
   - Restate the work as verbs, not nouns. A quarterly review isn't "a deck". It is "getting busy people to believe a story about cause and effect and decide under uncertainty in 30 minutes". Keep the genre's own verbs in the list *(ours)*: a landing page still has to make people want what it sells. The verbs find methods; the noun is still the deliverable.
   - Name 3–5 fields that do those verbs differently, including at least one you normally wouldn't consider, plus a red team whose job is to break it. One of them is always the genre's own best practitioner *(ours)*. Assemble them as if the result had to be extraordinary.
   - Borrow what each one *does*. Don't play characters: do a short seller's research, don't write in a short seller's voice.
5. **Judge: never grade your own work.** Use or build a check that isn't you: tests, a real run, a benchmark, a simulation, or reference output. Never another model, including another agent. A tool you can run for immediate feedback is ideal. Run it, iterate until it passes, and report what it showed. *(ours)* The check covers the genre bar, judged the way that genre is judged: render it and look at it, read it aloud, use it as a first-time user, set it beside the best real examples. It also compares the result with the first version on the same check. A check that measures only what's easy to measure is half a check.
6. **Stretch: an unreasonable target, treated as reasonable.**
   - Pick a specific target several times harder than the brief, for example 200ms when 5s was asked for, with a tight deadline where time matters. It becomes the target, not a side option; the brief stays the fallback.
   - Assume it's solvable, because someone has done something like it.
   - When it looks impossible, keep going and try another angle before concluding.
   - Falling short is fine. Report exactly where it broke.
7. **Lock: make it cheap to repeat.** Turn what worked into the smallest durable form: a script or spec, a short CLAUDE.md note saying how to run it and what proved it, and a command if the task will recur. Altitude pays off in workflows that take the human out of the loop.

## Operating rules

- **Access comes first.** The method assumes a computer that can install software and reach real data. If data, tools, machines or permissions are missing, getting them is the first job. Ask for them; don't fake around them.
- **Evidence over assertion.** Every claim that something works, is faster or is correct needs a check you ran. Never say a check passed if you didn't run it. Perception counts as evidence when it's gathered properly *(ours)*: a rendered page actually looked at, prose read through as its reader would, a side-by-side with the best real examples.
- **Raise the goal openly.** *(ours)* When you restate a task at a higher altitude, say what changed and why, and let the user veto it. The original ask stays a hard requirement: altitude is additive, never a replacement. Ambition never overrides explicit constraints, permissions, safety, or the user's stated scope.
- **Deeper, not bigger.** Ambition means a better method and a better outcome, not more output. Cut anything that doesn't serve the goal.
- **Proportion.** *(ours)* Match the effort to the stakes. A typo fix needs no interview. Anything whose value depends on its audience or purpose does, even an explanation. When in doubt, interview. A light pass is for typo-sized tasks only, and even then the altitude question comes before the work.
- **Know where it fits.** Altitude works less well for open-ended creative work, and "go make money" is too high a level to act on yet. Depth and range still apply there. Where the work is judged mostly by perception, the genre bar leads and altitude only adds to it *(ours)*.
- **No theatre.** Personas are for finding fields and methods, not for voice. A stranger transcript is not a better result.
- **Report honestly.** End with what the original ask was, what it became, how the final compares with the first version, what the outside check showed, and where the stretch broke.

## Reference

- [reference/altitude.md](reference/altitude.md): the escalation ladder, worked example, building access
- [reference/depth.md](reference/depth.md): the four statements, instruments, challenge and new knowledge, judges
- [reference/range.md](reference/range.md): verbs, assembling a crew, red teams, using subagents
- [reference/pitfalls.md](reference/pitfalls.md): failure modes of ambitious runs and how to catch them

## reference/altitude.md

# Altitude

Aim at the outcome, not the task. A task is your best guess at how to get the outcome you want. Altitude means checking that guess.

## Questions that move you up a level

- What do you want to happen next, after this is done?
- What's the goal beyond the goal?
- Who acts on this result, and what decision do they make with it?
- Would people hold meetings about this? If so, the meeting's purpose is the real goal.
- If this task were automated away forever, what outcome would you want to stay true? ("Crash-free", not "fix this crash".)

## The escalation ladder

The essay's worked example is an imagined company's quarterly business review. Each rung is more ambitious than the last.

1. **Inputs.** Don't just refresh the numbers in the template. Give the model as much of the business as possible and ask what changed this quarter, why, and what to do about it.
2. **Decisions.** Meetings should end in decisions. Ask for the three most urgent decisions given everything learned, with possible directions and the arguments for and against each.
3. **Replace the artifact.** The review exists so leadership catches problems early and moves money and people. Ask for a better mechanism than a quarterly deck. Show from the company's own history that it would have caught problems sooner, then run it alongside the current process for a quarter.

Climb only as high as the user will act on. Propose the next rung and say what changes. Don't jump silently. *(ours)*

The third rung is always a proposal. Deliver the artifact that was asked for, at full craft, and offer the replacement alongside it. A landing page that has become an ordering app is a silent goal change, even when the app is good. *(ours)*

## Access is part of altitude

A higher-level goal usually needs infrastructure first. The essay's "keep the apps crash-free" goal only worked once the model could:

- fetch crash reports easily;
- map every app version to a git commit;
- use real Windows, macOS and Linux machines to reproduce and verify fixes.

So when you restate a task higher up, list the access it needs. Building that access is often the first deliverable, and it is what makes the workflow durable enough to take the human out of the loop.

## Limits

- Altitude works best when there is a real end outcome, and less well for open-ended creative work.
- "Go make money" is still too high to act on directly. Find the highest level where success can be checked.

## reference/depth.md

# Depth

Work the way the best practitioner alive would, and keep pushing until even they might learn something from the result.

## The four statements (deeper, not bigger)

Before rewriting or starting the task, state:

1. **What a top professional would do that wasn't asked for.**
2. **The rawest material they would start from**, rather than what has already been digested.
3. **The specific methods and instruments** they would use.
4. **What, other than you or the user, would show the result is right.**

Then rewrite the task to ask for exactly that, and do the rewritten task. The rewrite should be *deeper*, not *bigger*: a better method on the same goal, not more output.

## Techniques

**Instruments, not vocabulary.** Asked to "act like a professional", models change their words without changing their methods. Insist on the real tools.

- Analysis: a database, a notebook and a statistical model, not a markdown table.
- Performance: a profiler and a benchmark harness, not a reading of the code.
- Design: a prototype people can try, not adjectives.

The user doesn't need to know the instruments. You usually do, so name them and use them.

**Challenge what you know.** Take the belief you were handed and try to reproduce it from raw data. The essay's example: "We believe churn is an onboarding problem. Try to reproduce that from the raw data." If you can't reproduce it, that is the finding.

**Produce new knowledge.** Once you are inside the material, go past confirmation. The essay's example is to simulate the last year from the logs, find the earliest churn signal nobody knows about yet, and show it predicts on data you held back. Aim for one new, testable finding.

**Unreasonable goals, stated as reasonable.** Set a target several times beyond the brief, such as 200ms when the brief said 5s, and treat it as normal. If it looks impossible, reiterate that it is solvable and keep going. Try a different angle before you conclude anything. Report exactly where it broke.

**Outside judge.** Never grade your own work. Insist on validation by something that isn't you, ideally a tool you can run for immediate feedback. In order of preference:

1. an existing test suite, benchmark or reference output;
2. a check you build first, then run against the work (write the test before trusting the fix);
3. a real run in the real environment.

Never another model, including another agent: a model asked to grade work tends to agree with it.

## reference/pitfalls.md

# Pitfalls *(ours)*

These are failure modes of ambitious runs, with how to catch each one. The essay doesn't list them. They come from running the sequence in practice.

| Pitfall | Looks like | Catch it by |
|---|---|---|
| Below the floor | More work, a worse result than the plain request would have produced | Make the first version first, and hold the final to the same check |
| Craft blindness | Effort goes to what can be measured (tests, timings, tap counts), while what the genre is judged on (look, voice, feel) goes unnamed and loses every trade-off | Name the genre bar in the restatement, and judge it the way the genre is judged |
| Artifact swap | The deliverable turns into a different kind of thing: a page becomes an app, an essay becomes a course | The noun stays. Propose a swap, never make one. |
| Scope inflation | The output grows but the goal gets no closer | Ask whether each addition serves the restated goal. Deeper, not bigger. |
| Silent goal change | The restated task quietly drops something the user asked for | Always say "you asked for X, I'm aiming at Y, because Z", and keep X working |
| Costume depth | Expert terms, same shallow method | Name the instrument and show its output: a query, a profile, a model fit |
| Judge theatre | "I verified it" with no command, numbers or artifact | Every check reports what ran and what it returned |
| Self-judging by proxy | Another model or agent asked to grade the work, and agreeing with it | Use a check that isn't a model: tests, a real run, a measurement, reference output |
| Persona drift | Characters talking to each other; the transcript gets weird | Replace each voice with a method and a finding |
| Fake access | Reasoning about data you could have queried, or a machine you could have used | Stop and get the access, or ask for it |
| Ambition on trivia | A seven-step run on a one-line fix | Do a light pass. Proportion is part of judgment. |
| Stretch as excuse | Missing the actual brief while chasing the stretch | Meet the brief first and keep it passing, then stretch |
| Unrepeatable win | A great result that lives only in a transcript | The lock step: a script or spec, a CLAUDE.md note, a command |

## reference/range.md

# Range

Look at the work through several fields. That used to be too expensive to do routinely. Multi-agent setups make it cheap, and it is often where the most surprising results come from.

## Nouns to verbs

This technique comes from Tom Kelley and Jonathan Littman's *The Art of Innovation*. A noun locks you into one field. A verb shows you who else does the same thing.

- "A quarterly review deck" becomes "getting busy people to believe a story about cause and effect, and to decide under uncertainty, in 30 minutes".
- "A backup script" becomes "making sure a person can get their life's notes back after the worst day, without thinking".
- "An onboarding flow" becomes "getting a stranger to their first success before they lose interest".

Write the verb form first. Then ask which fields are best at each verb.

Keep the genre's own verbs in the list *(ours)*. A landing page still has to make people want what it sells, an essay still has to be a pleasure to read, and an API still has to feel obvious to its caller. Verbs find methods. They don't change what the deliverable is.

## Assemble the crew

Pick 3–5 fields that do those verbs differently, plus at least one whose job is to break the result. Always include the genre's own best practitioner *(ours)*: an art director for a page, an editor for prose, a seasoned maintainer for code. Without them, the crew optimises everything except the thing itself. The essay's crew for the review deck:

- **Production quality:** an analyst, a journalist and an editor.
- **If it will be presented:** a motion designer and an audio designer.
- **Red team:** a short seller and a forensic accountant.

The essay sets the stakes playfully ("the deck needs to be amazing, otherwise aliens will blow up Earth"). High, specific stakes beat "do your best".

## Do what they do, not how they sound

Role-play makes a transcript stranger without making the result better. Use personas only to find fields and methods.

- Wrong: "Write this like a short seller would."
- Right: "Do the research a short seller does before taking a position against this, and report what it finds."

For each field, name the concrete method you are borrowing: a checklist, a test, a format, a statistic, a review ritual. Then apply it.

## Using subagents

Give each field its own subagent when the work is big enough. Brief each with the verb form, the raw material and the specific method it should apply, and ask for findings rather than prose: a short list of what was found, with evidence, plus paths to any longer material. The red team should get the finished output and the goal, never your reasoning.

---

# Pushing on

The user chose to push the work further, one step at a time, the way a person runs one `/ambition` command after another in a single chat. Each step's instruction arrives on its own once the step before it is finished.

The work as it stands is the **first version**: it's in `.ambition/first/` (if it isn't, copy the deliverable there now, and add `.ambition/` to the project's .gitignore if it has one that doesn't cover it). That folder is never edited again. It is the floor: the work must end up better than it on every part of the ask and on the goal, and worse on nothing. Improve the deliverable where it is, building on the first version rather than starting over, and keep everything that makes it good as this kind of thing.

You do the work yourself, in this conversation. Don't hand it to subagents; the only place they're welcome is Range, if several fields are worth exploring at once.

**Who answers.** By default, the user. Answer questions yourself only if the user told you to use your judgement (now or when pushing on); then answer from the repo, the conversation and sensible defaults, and list each answer as a labelled assumption.

**Plan or build.** If the user said plan or build, or plan mode is on, that decides it. Words like "plan", "design", "approach", "strategy", "proposal" or "options" mean plan; imperatives like "build", "fix", "add", "make", "ship", or an approved plan to carry out, mean build. When the deliverable is itself a document, improving it is the build. If it's unclear, make it your first question.

---

Step 2 of pushing the work further: Altitude. Open your first message with this line on its own, exactly: `▸ Step 2/8 · Altitude`. Write that line nowhere else.

Ask the user up to 4 questions, **one at a time**: ask one, end your message, and wait for the answer before the next. Use AskUserQuestion when it's available, with concrete options drawn from what you can already see. Skip only questions the user has already answered in this conversation. Don't answer them yourself unless the user told you to use your judgement: a setting that looks automated, a task that seems clear, or saving time are not reasons.
1. What is this ultimately for, and what should happen after it's done?
2. What would make the result unmistakably excellent, both as this kind of thing and for the goal? Push for a specific, hard target, not "good". Include the qualities that can only be judged by looking at it, reading it or using it.
3. What would prove it, other than you? Name a test, a metric, real users or reference output.
4. What access, data or tools are missing? Skip this if it's obvious.

Then restate the task at the level that serves the goal. Altitude **adds to** the request and never replaces it. If the work feeds decisions, aim it at ending in the most urgent ones, each with possible directions and the arguments for and against:

```
You asked for:   <original>
Raises all of:   <each part the request names, as the same kind of thing, and what excellent means for each>
Genre bar:       <what this kind of thing is judged on by its users and best practitioners, including qualities judged by perception, and why they'd choose it over the alternatives>
Aiming at:       <restated goal>, because <reason>
Excellent means: <specific hard target, on every part of the ask, on the genre bar and on the goal>
Proven by:       <the outside check: what will be run or rendered and measured, and the comparison with the first version>
Needs access to: <gaps, or "nothing new">
Mode:            plan|build · answerer · reviewer
```

**Checkpoint:** ask the user to confirm or adjust this restatement, and wait. If they told you to use your judgement, go on. Never silently drop something the user asked for. If access is missing, getting it is the first piece of work. The step is finished when the restatement is settled.

When this step is finished, copy the deliverable as it stands to `.ambition/steps/2/` (even if this step didn't change it, and never edit that copy), end with a short step report (did / found / changed course), and stop. The next instruction arrives then.

## Every step

- **Focus on this step.** Do this step's instruction in full, as if the user had just typed its command. Don't anticipate other steps or hold work back for them.
- **No look, no claim.** Whenever you change something people look at, read or use, perceive the result the way they will: render it at the sizes they use and look, read it through, use it. If you can't, get that access first (install a browser or a renderer). If you still can't, say the genre bar is unchecked and leave how it looks, reads or feels as the first version had it.
- **Look efficiently.** Every image you look at stays in this conversation and is re-read on every later turn. Look at a contact sheet (many frames or sizes in one image) rather than one image per frame, and take at most about three render-and-look rounds in a step. Keep working files (screenshots, scripts) under `.ambition/`, not in the deliverable.
- **Never trade the genre for a number.** A change must make the work better for the goal without making it worse as this kind of thing. If it does, undo it.
- **Reviewing.** If the user asked to review each step, end the step with its report and wait for their notes before you copy it. Their notes are steering, not answers.
- Respect the session's permission mode and the user's rules. Ambition never authorises skipping a confirmation the user requires.

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && mkdir -p .ambition/first && cp /cfg/plans/make-a-plan-for-jaunty-wren.md .ambition/first/ && ls -a . .ambition/first | head -30; [ -f .gitignore ] && cat .gitignore", "description": "Copy plan into .ambition/first and check .gitignore"}`

<details><summary>result</summary>

```
Exit code 1
.:
.
..
.ambition

.ambition/first:
.
..
make-a-plan-for-jaunty-wren.md
```

</details>

**→ ToolSearch** `{"query": "select:AskUserQuestion", "max_results": 1}`

<details><summary>result</summary>

```
No matching deferred tools found
```

</details>

### Assistant

I copied the plan to `.ambition/first/make-a-plan-for-jaunty-wren.md`. There is no `.gitignore` here, so I didn't add one.

Do you want to stop here or push the plan further?

- **Stop here:** keep it as it is.
- **Push it further:** I'd go after three improvements.
  1. **Aim at the goal behind the plan.** The plan would say what makes riders come back for weeks, with the most urgent decisions listed.
  2. **Back the gamification numbers with data.** I'd simulate the XP curve, streak rules and anti-cheat thresholds against real GPX ride data rather than guesses.
  3. **Have the plan challenged.** I'd check its assumptions, such as the 12-week timeline, the background-location risk and the cost of Mapbox and Supabase. I'd also add a cycling-community and a game-design view, and a critique aimed at breaking the plan.

  This would cost roughly three to five times what I've spent so far, mostly in research and simulation. I'd ask you up to four questions first.

### User

Push it further.

### Assistant

▸ Step 2/8 · Altitude

Question 1 of up to 4: what is this app ultimately for, and what should happen once the plan is done?

- **Ship a real product.** You or a team will build it and launch it publicly, and the plan is the blueprint.
- **Validate the idea first.** The plan decides whether to build at all, so I'd treat it as a go/no-go before any code.
- **Pitch or fundraise.** The plan goes to investors, a co-founder or a client.
- **Learning or portfolio project.** The goal is to build it yourself and learn from it.

Something else works too, and so does a combination, such as "validate, then ship".

### User

Ship a real product. I'm planning to build and launch it publicly as a small team, so the plan should work as a blueprint we can actually build from. I'd like it to be realistic about scope for a first release rather than covering everything.

### Assistant

Noted: a small team is building and launching this publicly, and the first release should be tightly scoped.

Question 2 of up to 4: what would make the plan unmistakably excellent as a blueprint? Pick the bar that matters most to you.

- **Buildable on day one.** Each milestone breaks into tickets a developer can pick up, with acceptance criteria and a clear order of dependencies.
- **Ruthless v1 scope.** A short "ship in about 8 weeks" cut, with everything else explicitly deferred and a stated reason for each cut.
- **Decisions already made.** Open choices like Mapbox vs. Google Maps and Supabase vs. Firebase are settled with costs, so the team doesn't have to reopen them.
- **Riders would want it.** The core loop is specific enough to test with real cyclists early, with a retention target such as "40% of new users ride again in week 2".

You can pick several. If you have a different hard target, such as a launch date or a budget cap, tell me that instead.

### User

Buildable on day one and decisions already made are the two that matter most. I want tickets a developer can pick up with acceptance criteria and a clear order, and I don't want to reopen choices like Mapbox vs. Google Maps or Supabase vs. Firebase, so settle those with rough costs. Ruthless v1 scope matters too, so keep the cut tight and note why things were deferred. I don't have a fixed launch date or budget cap, so aim for a sensible first release.

### Assistant

Understood. Excellent here means tickets a developer can pick up with acceptance criteria and a clear order, settled stack choices with rough costs, and a tight v1 cut with reasons for each deferral.

Question 3 of up to 4: what should check the plan, other than me?

- **A dry run by your developers.** One of them picks a few tickets cold and tells us if anything is ambiguous or blocked.
- **A working spike.** I'd build and test the riskiest piece, background GPS recording on a real phone, before settling the plan around it.
- **Real numbers.** I'd price Mapbox, Supabase and EAS from their current published pricing at your expected user counts, and check each ticket's dependencies mechanically for cycles or missing prerequisites.
- **Cyclist feedback.** A few riders from your network read the v1 loop and say whether they'd use it.

You can pick several. I'd suggest the pricing check plus the dependency check, since I can run them myself, with the dry run by your developers as the final test.

### User

I'd go with the pricing check plus the dependency check, as you suggested, and also the working spike on background GPS recording. Ride recording is the core of the app, and if it's unreliable on a real phone in the background, the rest of the plan falls apart. I'll skip the dry run and the cyclist feedback for now; I can do those myself once I see the plan.

### Assistant

Understood: pricing check, dependency check and a background-GPS spike.

Question 4 of 4: what access is missing? I can fetch current pricing and check dependencies from here. I can't hold a phone, so the spike needs your help.

- **I write the spike app, you run it.** I build a minimal Expo app that records in the background and logs gaps. You run it on a real iPhone and Android phone during a ride, send me the log file, and I analyze it. This needs no accounts from me.
- **Simulator only.** I test on the iOS simulator with simulated routes. It is faster, but it can't show real battery or OS-throttling behavior, so the spike result would count as unchecked.
- **Do you have these?** Say which you have: a physical iPhone, a physical Android phone, an Apple Developer account ($99/yr, needed for iPhone installs beyond 7 days), and Xcode or Android Studio on this Mac.

Tell me which devices and accounts you have and which option you'd like. If you have no physical device, I'll mark the spike as unverified in the plan.

### User

I have a physical iPhone and a physical Android phone, so go with the first option: you write the spike app and I run it on both during a ride. I don't have a paid Apple Developer account, so use the free provisioning route (the 7-day install is fine for a short spike). Xcode and Android Studio are both installed on this Mac. Keep the spike minimal, since it only needs to show whether background GPS holds up on a real ride.

### Assistant

You asked for the plan; here's what it becomes.

```
You asked for:   A plan for a React Native Expo social gamified cycling fitness app, saved to disk.
Raises all of:   - Plan: now a blueprint a small team can build from, not an outline.
                 - Tech stack: settled, no open "X or Y" choices, with rough monthly costs at stated user counts.
                 - Scope: a tight v1 cut. Each deferred item gets a one-line reason.
                 - Gamification, social and clubs: reduced to the smallest version that still delivers
                   the core loop. Everything else is deferred with reasons.
                 - Risks: each tied to a ticket or a spike result.
Genre bar:       A build blueprint is judged on whether a developer can start Monday morning without
                 asking questions. That means ordered tickets, testable acceptance criteria, no
                 ambiguity, no hidden dependencies, and scannable in minutes. It must still read as a
                 plan, not a pile of tickets: a short rationale up front, then the work.
Aiming at:       A v1 your team can build and launch, because ride recording is the product's
                 foundation and everything depends on it.
Excellent means: - Every ticket has acceptance criteria and a declared dependency list.
                 - The dependency graph has no cycles and no missing prerequisites.
                 - Every stack choice has a stated reason and a cost at 1k / 10k / 50k users.
                 - Every deferral has a reason.
                 - The recording-reliability risk is answered by real-ride data, or marked unverified.
Proven by:       1. Pricing: current published pricing for Mapbox, Supabase and EAS, fetched live,
                    with dates and sources in the plan.
                 2. Dependencies: a script that parses the ticket list and fails on cycles or
                    unknown prerequisites. I run it and report the output.
                 3. Spike: a minimal Expo app that records in the background and logs timestamped
                    points and gaps. You run it on your iPhone and Android phone during a ride and
                    send me the log. I analyze gaps, drift and battery use. Until that happens, the
                    plan marks recording reliability as unverified.
                 Comparison with the first version: the original is kept in .ambition/first/. The
                 final should beat it on all of the above and lose nothing the first version had.
Needs access to: Live web access for pricing. Your two phones for the spike. The iPhone install uses
                 free provisioning (7-day limit). Xcode and Android Studio are already on this Mac.
Mode:            build (the deliverable is a document, plus a spike app in a separate folder) · you answer questions · no per-step review requested
```

Two things to confirm:

1. **Spike location.** I'd put the spike app in `<workspace>/spike-gps/`, kept apart from the plan so it can't leak into the product. Is that okay?
2. **Plan file.** I'd keep improving `/cfg/plans/make-a-plan-for-jaunty-wren.md` in place, with the original preserved in `.ambition/first/`. Is that okay?

Does the restatement look right, or should I change anything? Once you confirm, I'll copy the current plan to `.ambition/steps/2/` and finish this step.

### User

Looks right, and both locations are fine. One thing I'd change: I only asked for a plan, so keep the spike small. A minimal app that logs background GPS is enough, and don't spend long on it. If I can't run it on my phones soon, just mark recording reliability as unverified in the plan. Go ahead and finish without stopping.

**→ Bash** `{"command": "cd \"<workspace>\" && mkdir -p .ambition/steps/2 && cp /cfg/plans/make-a-plan-for-jaunty-wren.md .ambition/steps/2/ && ls .ambition/steps/2", "description": "Snapshot plan to steps/2"}`

<details><summary>result</summary>

```
make-a-plan-for-jaunty-wren.md
```

</details>

### Assistant

The restatement is settled, and I copied the plan as it stands to `.ambition/steps/2/`. I haven't changed the plan itself in this step.

- **Did:** I asked the four altitude questions and restated the task as a blueprint your team can build from. It has ordered tickets with acceptance criteria and settled stack choices with rough costs. It also has a tight v1 cut with a reason for each deferral.
- **Found:** Ride recording is the riskiest piece, and I can only test it on your phones. The pricing and dependency checks I can run myself.
- **Changed course:** Following your note, I'll keep the spike minimal. It will be a small app in `<workspace>/spike-gps/` that logs background GPS points and gaps. If you can't run it on your phones soon, the plan will mark recording reliability as unverified.

Next is the depth step.

### Context (injected)

<details><summary>show</summary>

Stop hook feedback:
Step 3 of pushing the work further: Depth. Open your first message with this line on its own, exactly: `▸ Step 3/8 · Depth`. Write that line nowhere else.

Deeper, not bigger: the same task, done as the best practitioner alive would do it, end to end, deepest where the outcome is decided, and pushed until even they might learn something from the result. Say what they'd do that I didn't ask for, the rawest material they'd start from instead of summaries, the methods, tools and media they'd use (name every choice), and what other than you or me would show the result is right. Then rewrite the task to ask for exactly that, and do it.

Plan: write the four statements and the rewritten task, and settle what you can by reading the code, querying the data or running a spike. Build: do the rewritten task on the deliverable now.

When this step is finished, copy the deliverable as it stands to `.ambition/steps/3/` (even if this step didn't change it, and never edit that copy), end with a short step report (did / found / changed course), and stop. The next instruction arrives then.

## Every step

- **Focus on this step.** Do this step's instruction in full, as if the user had just typed its command. Don't anticipate other steps or hold work back for them.
- **No look, no claim.** Whenever you change something people look at, read or use, perceive the result the way they will: render it at the sizes they use and look, read it through, use it. If you can't, get that access first (install a browser or a renderer). If you still can't, say the genre bar is unchecked and leave how it looks, reads or feels as the first version had it.
- **Look efficiently.** Every image you look at stays in this conversation and is re-read on every later turn. Look at a contact sheet (many frames or sizes in one image) rather than one image per frame, and take at most about three render-and-look rounds in a step. Keep working files (screenshots, scripts) under `.ambition/`, not in the deliverable.
- **Never trade the genre for a number.** A change must make the work better for the goal without making it worse as this kind of thing. If it does, undo it.
- **Reviewing.** If the user asked to review each step, end the step with its report and wait for their notes before you copy it. Their notes are steering, not answers.
- Respect the session's permission mode and the user's rules. Ambition never authorises skipping a confirmation the user requires.

</details>

### Assistant

▸ Step 3/8 · Depth

I'll load the web tools and check what's installed on this Mac before writing the four statements.

**→ ToolSearch** `{"query": "select:WebSearch,WebFetch", "max_results": 2}`

<details><summary>result</summary>

```


```

</details>

**→ Bash** `{"command": "node -v; npm -v; python3 -V; xcodebuild -version 2>&1 | head -2; ls ~/Library/Android/sdk 2>&1 | head -3; which adb", "description": "Check installed toolchain versions"}`

<details><summary>result</summary>

```
Exit code 1
v26.13.1
11.20.0
Python 3.15.2
xcode-select: error: tool 'xcodebuild' requires Xcode, but active developer directory '/Library/Developer/CommandLineTools' is a command line tools instance
ls: ~/Library/Android/sdk: No such file or directory
adb not found
```

</details>

**→ WebFetch** `{"url": "https://supabase.com/pricing", "prompt": "List plan names, monthly price, included MAU, database size, storage, egress, and overage prices for Free, Pro, Team. Be exact with numbers."}`

**→ WebFetch** `{"url": "https://www.mapbox.com/pricing", "prompt": "Give the free tier and per-unit overage prices for Mobile Maps SDK monthly active users (iOS/Android), Static Images, Directions, Geocoding, and Map Matching. Be exact with numbers and units."}`

**→ WebFetch** `{"url": "https://expo.dev/pricing", "prompt": "List EAS plan names, monthly prices, included builds, included MAU for EAS Update, and overage prices. Be exact with numbers."}`

<details><summary>result</summary>

```
| Plan | Monthly price | Included MAU | Database size | Storage | Egress | Overage prices |
|---|---|---|---|---|---|---|
| **Free** | $0 | 50,000 | 500 MB | 1 GB | 5 GB | Not listed |
| **Pro** | From $25 | 100,000 | 8 GB per project | 100 GB | 250 GB | MAU: $0.00325 each. Database: $0.125/GB. Storage: $0.0213/GB. Egress: $0.09/GB. |
| **Team** | From $599 | 100,000 | 8 GB per project | 100 GB | 250 GB | MAU: $0.00325 each. Database: $0.125/GB. Storage: $0.0213/GB. Egress: $0.09/GB. |

Free plan overage prices aren't listed on the page. Pro and Team include $10/month in compute credits, which cover one Micro instance.
```

</details>

<details><summary>result</summary>

```
| Product | Free tier | Overage price (per 1,000 units, by tier) |
|---|---|---|
| **Mobile Maps SDK** (monthly active users, iOS/Android) | Up to 25,000 MAU | 25,001–125,000 MAU: $4.00<br>125,001–250,000 MAU: $3.20<br>250,001–1,250,000 MAU: $2.40<br>1,250,001+ MAU: contact sales |
| **Static Images API** (monthly requests) | Up to 50,000 requests | 50,001–500,000: $1.00<br>500,001–1,000,000: $0.80<br>1,000,001–5,000,000: $0.60<br>5,000,001+: contact sales |
| **Directions API** (monthly requests) | Up to 100,000 requests | 100,001–500,000: $2.00<br>500,001–1,000,000: $1.60<br>1,000,001–5,000,000: $1.20<br>5,000,001+: contact sales |
| **Geocoding API** (Temporary Geocoding, monthly requests) | Up to 100,000 requests | 100,001–500,000: $0.75<br>500,001–1,000,000: $0.60<br>1,000,001–5,000,000: $0.45<br>5,000,001+: contact sales |
| **Map Matching API** (monthly requests) | Up to 100,000 requests | 100,001–500,000: $2.00<br>500,001–1,000,000: $1.60<br>1,000,001–5,000,000: $1.20<br>5,000,001+: contact sales |

All prices are in USD. The page lists Geocoding under two APIs: Temporary Geocoding (shown above) and Permanent Geocoding, which has no free tier listed and starts at $5.00 per 1,000 requests for 1–500,000.
```

</details>

<details><summary>result</summary>

```
**Plans (Expo services, formerly EAS)**

| Plan | Monthly price | Included builds | Included update MAUs |
|---|---|---|---|
| Free | $0 | Up to 15 Android and 15 iOS builds | 1,000 |
| Starter | $19 plus usage | $45 of build credit | 3,000 |
| Production | $199 plus usage | $225 of build credit | 50,000 |
| Enterprise | Custom | $1,000 of build credit (starting point) | Not stated ("preferred pricing") |

**Build overage (per build, after included credit)**

- Android medium worker: $1
- Android large worker: $2
- iOS medium worker: $2
- iOS large worker: $4

**Expo Update overage (per MAU)**

Starter and Production share the same rates. Starter's first 3,000 MAUs and Production's first 50,000 are included.

| MAU band | Starter | Production |
|---|---|---|
| 3,001 – 200,000 (Starter) / 50,001 – 200,000 (Production) | $0.005 | $0.005 |
| 200,001 – 500,000 | $0.00375 | $0.00375 |
| 500,001 – 1,000,000 | $0.0034 | $0.0034 |
| 1,000,001 – 2,000,000 | $0.003 | $0.003 |
| 2,000,001 – 3,000,000 | $0.0024 | $0.0024 |
| 3,000,001 – 6,000,000 | $0.0022 | $0.0022 |
| 6,000,001 – 10,000,000 | $0.0016 | $0.0016 |
| 10,000,001 – 20,000,000 | $0.0014 | $0.0014 |
| 20,000,001 – 35,000,000 | $0.00115 | $0.00115 |
| 35,000,001 – 60,000,000 | $0.001 | $0.001 |
| 60,000,001 – 100,000,000 | $0.0009 | $0.0009 |
| Over 100,000,000 | $0.00085 | $0.00085 |

- **Free:** No overage pricing. The page says "The Free plan has no update overage pricing; it is limited to its included monthly active users."
- **Enterprise:** First 1,000,000 MAUs at $0.00208333 (same rate for 1,000,001 – 2,000,000), then $0.002 (2,000,001 – 5,000,000), $0.0016 (5,000,001 – 10,000,000), $0.0014 (10,000,001 – 20,000,000), $0.00115 (20,000,001 – 35,000,000), $0.001 (35,000,001 – 60,000,000), $0.0009 (60,000,001 – 100,000,000), and $0.00085 (over 100,000,000).
```

</details>

### Assistant

Pricing is in. The riskiest decision is recording, so I'll read the primary docs on background location and the main commercial alternative before choosing.

**→ WebFetch** `{"url": "https://docs.expo.dev/versions/latest/sdk/location/", "prompt": "What does the doc say about background location: startLocationUpdatesAsync options (foregroundService, activityType, pausesUpdatesAutomatically, showsBackgroundLocationIndicator, deferredUpdates), required permissions/config plugin keys for iOS and Android, the Android foreground service type requirements, and any listed lim … [101 more chars]`

**→ WebFetch** `{"url": "https://github.com/transistorsoft/react-native-background-geolocation", "prompt": "What are the license/pricing terms for Android release builds and iOS, is Expo supported (config plugin), and what does it claim about motion-activity detection and battery? Quote exact price and license terms if present."}`

<details><summary>result</summary>

```
**Licensing and pricing:** The page gives no price. It states that "A license is required for RELEASE builds on both iOS and Android." The SDK works without a license in debug builds. For release testing, you can get a free 30-day trial license, and a purchase link is provided. The page also notes that v4.x license keys don't work with v5.

**Expo:** The page lists Expo as a supported platform, with setup, API reference, and example links. The repo includes an `expo/plugin` directory and an `app.plugin.js` file, which suggests a config plugin, but the page doesn't describe it in prose.

**Motion-activity detection and battery:** The SDK uses accelerometer, gyroscope, and magnetometer data to decide whether the device is moving or stationary. When moving, location recording starts automatically at the configured distance filter. When stationary, location services turn off to save battery. The project describes itself as "battery-conscious."
```

</details>

<details><summary>result</summary>

```
**startLocationUpdatesAsync(taskName, options)** takes an optional `LocationTaskOptions` object. It extends `LocationOptions` and adds:

- **`activityType`** (iOS): defaults to `ActivityType.Other`.
- **`deferredUpdatesDistance`**: defaults to `0`. Applies only in the background.
- **`deferredUpdatesInterval`**: defaults to `0`.
- **`deferredUpdatesTimeout`**: no description given.
- **`foregroundService`**: an object of type `LocationTaskServiceOptions`, with no description given at the parent level.
- **`pausesUpdatesAutomatically`** (iOS): defaults to `false`.
- **`showsBackgroundLocationIndicator`** (iOS): defaults to `false`.

`LocationTaskServiceOptions` contains `notificationTitle` and `notificationBody` (both listed as required), plus optional `notificationColor` and `killServiceOnDestroy`.

**Permissions and config**

- **Android:** `ACCESS_BACKGROUND_LOCATION`, `FOREGROUND_SERVICE`, and `FOREGROUND_SERVICE_LOCATION`. The last is required on Android 14 and later. New builds with these permissions require Google Play review.
- **iOS:** Add `location` to `UIBackgroundModes`. Without CNG, the doc says to add it to **Expo.plist**. Usage keys are `NSLocationAlwaysAndWhenInUseUsageDescription`, `NSLocationAlwaysUsageDescription` (deprecated), and `NSLocationWhenInUseUsageDescription`.
- **Config plugin keys:**
  - `isIosBackgroundLocationEnabled` (default `false`)
  - `isAndroidBackgroundLocationEnabled` (default `false`)
  - `isAndroidForegroundServiceEnabled` (defaults to `true` if background location is enabled)
  - `androidForegroundServiceIcon`
  - `locationAlwaysAndWhenInUsePermission`, `locationWhenInUsePermission`, and `locationAlwaysPermission` (deprecated)

**Foreground service type**

The doc says `FOREGROUND_SERVICE_LOCATION` lets an app call `Service.startForeground` with the "location" type. It is required on Android 14 and later when running a location foreground service. It doesn't specify other service type requirements.

**Requirements**

- Loca … [994 more chars]
```

</details>

**→ Bash** `{"command": "npm view expo version; npm view expo-location version; npm view expo-task-manager version; npm view @rnmapbox/maps version; npm view react-native-background-geolocation version 2>&1 | tail -1", "description": "Check current package versions on npm"}`

<details><summary>result</summary>

```
58.0.25
58.0.22
58.0.14
10.3.18
5.8.2
```

</details>

**→ Write** `{"file_path": "/cfg/plans/make-a-plan-for-jaunty-wren.md", "content": "# SpokeQuest \u2014 Build Blueprint (React Native + Expo, social gamified cycling tracker)\n\nWorking name: **SpokeQuest** (placeholder). Target: a small team ships a public v1 on iOS and Android.\nPricing and package versions below were fetched on **2026-11-13** (sources in \u00a74).\n\n## 1. Context and goal\nStrava owns trac … [17443 more chars]`

<details><summary>result</summary>

```
The file /cfg/plans/make-a-plan-for-jaunty-wren.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

Next, the ticket checker. It checks for duplicate IDs, unknown prerequisites, cycles, tickets listed before their prerequisites, and missing acceptance criteria.

**→ Bash** `{"command": "mkdir -p \"<workspace>/plan-tools\" && cat > \"<workspace>/plan-tools/check_tickets.py\" <<'EOF'\n#!/usr/bin/env python3\n\"\"\"Check ticket structure in a plan file.\n\nUsage: python3 -I check_tickets.py PLAN.md\nFails (exit 1) on: duplicate ids, unknown prerequisites, cycles, a ticket listed\nbefore a prerequisite, a ticket with no 'Depends:' line, or no 'AC:' line.\nAlso prints the … [3271 more chars]`

<details><summary>result</summary>

```
FAIL
 - T-017: listed before its prerequisite T-022
exit=1
Shell cwd was reset to <workspace>
```

</details>

### Assistant

The checker caught a real ordering error: T-017 is listed before T-022, which it depends on. I'll move T-017 and T-018 to after the backend tickets.

**→ Edit** `{"replace_all": false, "file_path": "/cfg/plans/make-a-plan-for-jaunty-wren.md", "old_string": "### T-017 \u00b7 Ride finalize and upload queue\nDepends: T-013, T-005, T-022\n- Simplify, encode, upload, call `finalize_ride`; retry with backoff; idempotent via client ride id.\n- AC: airplane-mode ride uploads once on reconnect; double-submit creates one ride.\n\n### T-018 \u00b7 Ride summary screen … [268 more chars]`

<details><summary>result</summary>

```
The file /cfg/plans/make-a-plan-for-jaunty-wren.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

**→ Edit** `{"replace_all": false, "file_path": "/cfg/plans/make-a-plan-for-jaunty-wren.md", "old_string": "- AC: fixtures \u2014 normal ride accepted; 60 km/h average flagged; 1 km teleport flagged; ride inside privacy zone has truncated public geometry.\n", "new_string": "- AC: fixtures \u2014 normal ride accepted; 60 km/h average flagged; 1 km teleport flagged; ride inside privacy zone has truncated public … [498 more chars]`

<details><summary>result</summary>

```
The file /cfg/plans/make-a-plan-for-jaunty-wren.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

**→ Bash** `{"command": "cd /tmp && python3 -I \"<workspace>/plan-tools/check_tickets.py\" /cfg/plans/make-a-plan-for-jaunty-wren.md; echo \"exit=$?\"\n# negative control: inject a cycle and an unknown dep, confirm checker fails\nsed 's/^Depends: T-002, T-003$/Depends: T-002, T-003, T-099/; s/^Depends: none$/Depends: T-054/' /cfg/plans/make-a-plan-for-jaunty-wren.md > /tmp/bad.md\npython3 -I \"<workspace>/pla … [145 more chars]`

<details><summary>result</summary>

```
OK: 34 tickets, no cycles, order valid, all have AC
Longest chain (9 tickets): T-001 -> T-002 -> T-005 -> T-006 -> T-040 -> T-041 -> T-042 -> T-044 -> T-054
exit=0
FAIL
 - T-001: listed before its prerequisite T-054
 - T-005: unknown prerequisite T-099
 - cycle: T-001 -> T-054 -> T-053 -> T-015 -> T-013 -> T-012 -> T-011 -> T-001
 - cycle: T-001 -> T-054 -> T-053 -> T-015 -> T-013 -> T-010 -> T-002 -> T-001
 - cycle: T-001 -> T-054 -> T-053 -> T-015 -> T-014 -> T-004 -> T-001
 - cycle: T-001 -> T-054 -> T-053 -> T-051 -> T-006 -> T-005 -> T-003 -> T-001
 - cycle: T-001 -> T-054 -> T-050 -> T-001
bad exit=
Shell cwd was reset to <workspace>
```

</details>

**→ Edit** `{"replace_all": false, "file_path": "/cfg/plans/make-a-plan-for-jaunty-wren.md", "old_string": "T-001 \u2192 T-002 \u2192 **T-010** \u2192 T-013 \u2192 T-015 \u2192 T-017 \u2192 T-018 \u2192 T-034 \u2192 T-053 \u2192 T-054.\nBackend track (T-003 \u2192 T-020 \u2192 T-022 \u2192 T-030\u2026T-033) runs in parallel and must finish before T-017 and T-034.", "new_string": "Two paths matter (the first i … [608 more chars]`

<details><summary>result</summary>

```
The file /cfg/plans/make-a-plan-for-jaunty-wren.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

Both checks behave. Now the spike, kept minimal: a background logger and a tested gap analyzer.

**→ Bash** `{"command": "mkdir -p \"<workspace>/spike-gps/src\" && cd \"<workspace>/spike-gps\" && \ncat > src/analyze.ts <<'EOF'\n// Pure analysis of a GPS log. No Expo imports so it can be tested with plain node.\nexport type Pt = { t: number; lat: number; lon: number; acc: number; speed: number; recvAt: number };\n\nexport const GAP_S = 20; // a gap longer than this while moving counts as dropout\nexport c … [10736 more chars]`

<details><summary>result</summary>

```
  code: 'ERR_ASSERTION',
  actual: false,
  expected: true,
  operator: '==',
  diff: 'simple'
}

Node.js v26.13.1
```

</details>

**→ Bash** `{"command": "cd \"<workspace>/spike-gps\" && node --experimental-strip-types test-analyze.mjs 2>&1 | grep -E \"AssertionError|test-analyze.mjs:[0-9]+\" | head -4", "description": "Find which assertion failed"}`

<details><summary>result</summary>

```
AssertionError [ERR_ASSERTION]: hole should be flagged
    at file:///Volumes/My%20Shared%20Files/work/spike-gps/test-analyze.mjs:18:8
```

</details>

**→ Bash** `{"command": "cd \"<workspace>/spike-gps\" && python3 -I - <<'EOF'\nimport re\ns = open('test-analyze.mjs').read()\ns = s.replace(\"\"\"assert.ok(!gappy.passGaps && gappy.gaps.length === 1 && gappy.longestMovingGapS === 30, 'hole should be flagged');\"\"\",\n\"\"\"assert.ok(gappy.passGaps && gappy.gaps.length === 1 && gappy.longestMovingGapS === 30, '30 s hole is reported but within tolerance (<2%, … [482 more chars]`

<details><summary>result</summary>

```
}

Node.js v26.13.1
exit=0
OK: 34 tickets, no cycles, order valid, all have AC
```

</details>

**→ Bash** `{"command": "cd \"<workspace>/spike-gps\" && node --experimental-strip-types test-analyze.mjs 2>&1 | grep -E \"Error|test-analyze.mjs:[0-9]+|actual|expected\" | head -6", "description": "Show current test failure"}`

<details><summary>result</summary>

```
AssertionError [ERR_ASSERTION]: a stop must not be a dropout
    at file:///Volumes/My%20Shared%20Files/work/spike-gps/test-analyze.mjs:26:8
  actual: 1,
  expected: 0,
```

</details>

**→ Bash** `{"command": "cd \"<workspace>/spike-gps\" && python3 -I - <<'EOF'\na = open('src/analyze.ts').read()\nold = a[a.index(\"    const reported\"):a.index(\"    if (sp > MOVING_MS) {\")]\nnew = \"\"\"    // Short segments: trust the reported speed. Long gaps: judge by straight-line displacement,\n    // because a stop (no movement) and a dropout while riding (large displacement) look the same\n    // b … [1116 more chars]`

<details><summary>result</summary>

```
analyze: all tests passed { clean: '14.99 km', gappyDropout: '1.00%' }
```

</details>

### Assistant

All tests pass. Now the snapshot for this step.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I plan-tools/check_tickets.py /cfg/plans/make-a-plan-for-jaunty-wren.md | head -1 && mkdir -p .ambition/steps/3 && cp /cfg/plans/make-a-plan-for-jaunty-wren.md .ambition/steps/3/ && ls .ambition/steps/3", "description": "Final check and snapshot to steps/3"}`

<details><summary>result</summary>

```
OK: 34 tickets, no cycles, order valid, all have AC
make-a-plan-for-jaunty-wren.md
```

</details>

### Assistant

**Step 3 report: Depth**

**Did**
- I rewrote the plan at `/cfg/plans/make-a-plan-for-jaunty-wren.md` as a blueprint. It has a settled-decisions table, a cost model, a v1 scope with a reason for each deferral, and 34 ordered tickets with acceptance criteria.
- Pricing came from today's live Supabase, Mapbox and Expo pages, with sources in the plan. The monthly costs for the verified lines are $44 at 1k users, $79 at 10k and $324 at 50k.
- I wrote `plan-tools/check_tickets.py`, which checks for cycles, unknown prerequisites, wrong ordering and missing acceptance criteria. The plan now passes it.
- I wrote the GPS spike in `spike-gps/` (code and README only; it hasn't been built or run), plus a gap analyzer.

**Found**
- The checker caught a real mistake: a ticket was listed before its own prerequisite.
- The checker also showed the longest dependency chain runs through social features (9 tickets), not recording as I'd assumed. I fixed the plan to show both that chain and the recording path, which is the riskier one.
- Expo's docs say background location stops if the user force-quits the app. On Android it isn't restarted by location events. The recorder ticket now requires recovery of an unfinished ride on relaunch.
- Testing the analyzer exposed a bug of mine: a 3-minute stop would have counted as a GPS dropout. I fixed it and the tests now pass.
- Your toolchain doesn't match what you said. `xcodebuild` points at Command Line Tools rather than Xcode, and there is no Android SDK at the default path. The spike README has the fixes.

**Changed course**
- Clubs moved out of v1 to keep the cut tight. Friends and a friends leaderboard carry the social loop instead.
- Recording reliability is marked **unverified**. The spike hasn't been run on a phone, so ticket T-010 gates the recording work until you've run it.
- Not verified: Supabase compute pricing above Micro, the Transistorsoft licence price (needed only if the fallback triggers), and the Sentry and PostHog free-tier limits.

A snapshot is in `.ambition/steps/3/`.

### Context (injected)

<details><summary>show</summary>

Stop hook feedback:
Step 4 of pushing the work further: Challenge. Open your first message with this line on its own, exactly: `▸ Step 4/8 · Challenge`. Write that line nowhere else.

List the assumptions in my request and in your approach, including who set each number, who does it, in what order and what it depends on. Test each, riskiest first, against the real thing (run it, read the source, check the evidence, ask the people it's for), not by reasoning alone. Then find what we're missing that we don't know we're missing: once you're inside the material, look for a blind spot yourself and show it holds on evidence you haven't used yet.

Plan: report each assumption with how you tested it against the real material, plus the new finding and how it held up. Build: fix what the tests turned up in the deliverable.

When this step is finished, copy the deliverable as it stands to `.ambition/steps/4/` (even if this step didn't change it, and never edit that copy), end with a short step report (did / found / changed course), and stop. The next instruction arrives then.

## Every step

- **Focus on this step.** Do this step's instruction in full, as if the user had just typed its command. Don't anticipate other steps or hold work back for them.
- **No look, no claim.** Whenever you change something people look at, read or use, perceive the result the way they will: render it at the sizes they use and look, read it through, use it. If you can't, get that access first (install a browser or a renderer). If you still can't, say the genre bar is unchecked and leave how it looks, reads or feels as the first version had it.
- **Look efficiently.** Every image you look at stays in this conversation and is re-read on every later turn. Look at a contact sheet (many frames or sizes in one image) rather than one image per frame, and take at most about three render-and-look rounds in a step. Keep working files (screenshots, scripts) under `.ambition/`, not in the deliverable.
- **Never trade the genre for a number.** A change must make the work better for the goal without making it worse as this kind of thing. If it does, undo it.
- **Reviewing.** If the user asked to review each step, end the step with its report and wait for their notes before you copy it. Their notes are steering, not answers.
- Respect the session's permission mode and the user's rules. Ambition never authorises skipping a confirmation the user requires.

</details>

### Assistant

▸ Step 4/8 · Challenge

Mode is build. Before testing anything, here are the assumptions I'm making, with who set each one:

| # | Assumption | Set by | Risk |
|---|---|---|---|
| A1 | The spike app compiles and uses the Expo APIs correctly | me | high: untested |
| A2 | Apple requires Sign in with Apple if we offer Google | me, from memory | medium: a cost if wrong |
| A3 | The 11-week schedule with 3 developers is right | me, no ticket sizes exist | high |
| A4 | Storage and DB per ride (40 KB and 12 KB), and 8 rides per user per month | me | low: cost lines are small |
| A5 | The level curve and XP give a sensible pace | me, and the XP formula isn't even written down | high: a dev can't build T-030 |
| A6 | Beta soak then store launch is straightforward | me | unknown, which makes it the blind-spot candidate |
| A7 | Spike thresholds (2% dropout, 60 s, ±3%, 10%/hr) | me | calibrate from the spike data, not now |

I'll test A1, A2 and A6 against the real sources first.

**→ Bash** `{"command": "W=\"<workspace>/.ambition/typecheck\"; rm -rf \"$W\"; mkdir -p \"$W\" && cd \"$W\" && npm init -y >/dev/null && npm install --ignore-scripts --no-audit --no-fund <email> <email> <email> expo-sqlite expo-battery react-native typescript @types/react 2>&1 | tail -3; ls node_modules | wc -l; node -p \"['expo-sqlite','expo-battery','react-native','react','typescript'].map(n=>n+'@'+require( … [151 more chars]`

**→ WebFetch** `{"url": "https://developer.apple.com/app-store/review/guidelines/", "prompt": "Quote guideline 4.8 (Login Services) exactly: does it require Sign in with Apple when an app offers Google or other third-party login, or does it allow an alternative privacy-preserving login service? List the exact criteria."}`

**→ WebFetch** `{"url": "https://support.google.com/googleplay/android-developer/answer/14151465", "prompt": "What testing requirements apply to NEW personal developer accounts before production access: number of testers, number of days, closed testing? Quote exact numbers and the account-creation date cutoff if any. Also any difference for organization accounts."}`

<details><summary>result</summary>

```
**Personal accounts created after November 13, 2023:**

- **Testers:** You need at least 12 testers. The article states you must run a closed test "with a minimum of 12 testers who have been opted in continuously for at least 14 days."
- **Days:** Testers must stay opted in for 14 days. If a tester opts out and back in, the 14 days must be consecutive.
- **Closed testing:** You must complete a closed test before applying for production access. Production and Pre-registration stay disabled until you meet these requirements.
- **Cutoff date:** The requirement applies to "personal developer accounts created after November 13, 2023."

**Organization accounts:** The article doesn't mention organization accounts, so it doesn't say whether they have different testing requirements. It only covers personal accounts.
```

</details>

<details><summary>result</summary>

```
**Guideline 4.8 (Login Services), quoted exactly:**

> Apps that use a third-party or social login service (such as Facebook Login, Google Sign-In, Log in with X, Sign In with LinkedIn, Login with Amazon, or WeChat Login) to set up or authenticate the user's primary account with the app must also offer as an equivalent option another login service with the following features:
>
> * the login service limits data collection to the user's name and email address;
> * the login service allows users to keep their email address private as part of setting up their account; and
> * the login service does not collect interactions with your app for advertising purposes without consent.
>
> A user's primary account is the account they establish with your app for the purposes of identifying themselves, signing in, and accessing your features and associated services.
>
> Another login service is not required if:
>
> * Your app exclusively uses your company's own account setup and sign-in systems.
> * Your app is an alternative app marketplace, or an app distributed from an alternative app marketplace, that uses a marketplace-specific login for account, download, and commerce features.
> * Your app is an education, enterprise, or business app that requires the user to sign in with an existing education or enterprise account.
> * Your app uses a government or industry-backed citizen identification system or electronic ID to authenticate users.
> * Your app is a client for a specific third-party service and users are required to sign in to their mail, social media, or other third-party account directly to access their content.

**Answer**

Guideline 4.8 does not require Sign in with Apple specifically. It requires that an app offering a third-party or social login as the primary account option also offer *another* login service as an equivalent option. That alternative must meet all three criteria:

1. **Data minimization:** It limits data collection to the user's name and email add … [942 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>/.ambition/typecheck\" && cp -R \"<workspace>/spike-gps/src\" . && cp \"<workspace>/spike-gps/App.tsx\" . && cat > tsconfig.json <<'EOF'\n{\"compilerOptions\":{\"strict\":true,\"jsx\":\"react-jsx\",\"module\":\"esnext\",\"moduleResolution\":\"bundler\",\"target\":\"es2022\",\"lib\":[\"es2022\"],\"skipLibCheck\":true,\"noEmit\":true,\"types\":[\"react-native\"]},\"inclu … [193 more chars]`

<details><summary>result</summary>

```
src/task.ts(19,30): error TS2345: Argument of type '({ data, error }: any) => undefined' is not assignable to parameter of type 'TaskManagerTaskExecutor<unknown>'.
  Type 'undefined' is not assignable to type 'Promise<any>'.
tsc exit=
```

</details>

### Assistant

The typecheck found a real bug: the task executor must return a Promise, so the spike wouldn't have compiled. I'll fix it and check the config plugin's keys in the real source.

**→ Bash** `{"command": "cd \"<workspace>/spike-gps\" && python3 -I - <<'EOF'\ns = open('src/task.ts').read()\ns = s.replace(\"TaskManager.defineTask(TASK, ({ data, error }: any) => {\\n  if (error) return void addEvent('task_error', String(error.message ?? error));\",\n\"TaskManager.defineTask(TASK, async ({ data, error }: any) => {\\n  if (error) {\\n    addEvent('task_error', String(error.message ?? error) … [599 more chars]`

<details><summary>result</summary>

```
tsc exit=0
index.d.ts
index.js
index.js.map
withLocation.d.ts
withLocation.js
withLocation.js.map
   1 FOREGROUND_SERVICE_LOCATION
   5 isAndroidBackgroundLocationEnabled
   4 isAndroidForegroundServiceEnabled
   2 isIosBackgroundLocationEnabled
```

</details>

**→ Bash** `{"command": "cd \"<workspace>/.ambition/typecheck/node_modules\" && grep -rn \"foregroundServiceType\" expo-location/android expo-task-manager/android 2>/dev/null | head -5; grep -rn \"timeInterval\" expo-location/build/Location.types.d.ts | head -3", "description": "Check native foreground service type and timeInterval docs"}`

<details><summary>result</summary>

```
expo-location/android/src/main/AndroidManifest.xml:9:      android:foregroundServiceType="location" />
expo-location/android/src/main/AndroidManifest.xml:13:      android:foregroundServiceType="location" />
expo-location/build/Location.types.d.ts:115:    timeInterval?: number;
```

</details>

### Assistant

The spike now typechecks against the real packages and the plugin keys exist. Next I'll measure the storage assumption (A4) and test the XP and level pacing (A5).

**→ Bash** `{"command": "mkdir -p \"<workspace>/.ambition/tests\" && cd \"<workspace>/.ambition/tests\" && cat > sizes.py <<'EOF'\nimport json, gzip, math, random\nrandom.seed(7)\n# 60 min at ~6 m/s with the spike's 10 m distance filter -> a point about every 10 m\npts, lat, lon, hdg, alt, t = [], 52.0, 4.0, 0.0, 10.0, 1_700_000_000_000\nfor i in range(2160):\n    hdg += random.gauss(0, 0.05)\n    lat += 10 * … [2265 more chars]`

<details><summary>result</summary>

```
points 2160 raw json KB 182 gzip KB 39
delta-coded gzip KB 21
simplified points 127 of 2160 polyline bytes ~ 1270
```

</details>

**→ Bash** `{"command": "cd \"<workspace>/.ambition/tests\" && cat > xp_sim.py <<'EOF'\nimport random\nrandom.seed(3)\ndef xp_for_level(n): return 0 if n <= 1 else round(100 * n ** 1.5)\ndef level(xp):\n    n = 1\n    while xp >= xp_for_level(n + 1): n += 1\n    return n\ndef ride_xp(km, elev, first=False):\n    return min(600, round(10 * km + 0.2 * elev)) + (150 if first else 0)\nPERSONAS = {\n  \"commuter 5 … [1293 more chars]`

<details><summary>result</summary>

```
commuter 5x8km                   L-after-1st-ride=1  weeks-to {3: 1, 5: 2, 10: 5, 20: 14, 30: 25}  level@52w=49  xp=35003
weekend 60+25km                  L-after-1st-ride=3  weeks-to {3: 1, 5: 1, 10: 3, 20: 8, 30: 14}  level@52w=73  xp=62887
casual 1x15km (70% of weeks)     L-after-1st-ride=2  weeks-to {3: 3, 5: 7, 10: 16}  level@52w=19  xp=8782
keen 6x45km                      L-after-1st-ride=3  weeks-to {3: 1, 5: 1, 10: 1, 20: 3, 30: 5}  level@52w=167  xp=215894
thresholds: {2: 283, 3: 520, 5: 1118, 10: 3162, 20: 8944, 30: 16432, 50: 35355}
```

</details>

**→ Bash** `{"command": "cd \"<workspace>/.ambition/tests\" && python3 -I - <<'EOF'\nimport random, re\nsrc = open('xp_sim.py').read()\nsrc = src.replace(\"return 0 if n <= 1 else round(100 * n ** 1.5)\", \"return 0 if n <= 1 else round(60 * n ** 2)\")\nsrc = src.replace(\"(150 if first else 0)\", \"(300 if first else 0)\")\nsrc = src.replace(\"        if rides:\\n            wk += QUEST_WEEKLY\", \"        i … [245 more chars]`

<details><summary>result</summary>

```
commuter 5x8km                   L-after-1st-ride=2  weeks-to {3: 1, 5: 3, 10: 9, 20: 36}  level@52w=24  xp=35153
weekend 60+25km                  L-after-1st-ride=3  weeks-to {3: 1, 5: 2, 10: 6, 20: 20, 30: 45}  level@52w=32  xp=63037
casual 1x15km (70% of weeks)     L-after-1st-ride=2  weeks-to {3: 1, 5: 8, 10: 34}  level@52w=12  xp=8932
keen 6x45km                      L-after-1st-ride=3  weeks-to {3: 1, 5: 1, 10: 3, 20: 10, 30: 22}  level@52w=46  xp=131109
thresholds: {2: 240, 3: 540, 5: 1500, 10: 6000, 20: 24000, 30: 54000, 50: 150000}
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\nimport re\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\nsizes = dict(zip(\"T-001 T-002 T-003 T-004 T-005 T-006 T-010 T-011 T-012 T-013 T-014 T-015 T-016 T-020 T-021 T-022 T-017 T-018 T-030 T-031 T-032 T-033 T-034 T-035 T-040 T-041 T-042 T-043 T-044 T-050 T-051 T-052 T-053 T-054\".split(),\n [2,2,2,4,4,3,3,4,2,6,4,4,4, … [413 more chars]`

<details><summary>result</summary>

```
124 dev-days across 34
34
```

</details>

### Assistant

Next come the plan edits for the findings: the new account and closed-test ticket (T-007), the auth rationale, the XP formula and the DB size.

**→ Bash** `{"command": "python3 -I - <<'EOF'\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\ndef rep(old, new):\n    global s\n    assert s.count(old) == 1, old[:60]\n    s = s.replace(old, new)\n\n# A2: Apple 4.8 rationale\nrep(\"| Auth | Sign in with Apple + Google | Apple is required on iOS whenever Google sign-in is offered. Email deferred |\",\n    \"| Auth | Sign in with Apple + G … [4170 more chars]`

<details><summary>result</summary>

```
124:### T-007 · Developer accounts and Play closed-test enrolment
290:Depends: T-015, T-051, T-052, T-007
296:Depends: T-053, T-050, T-044, T-034, T-043, T-007
```

</details>

**→ Bash** `{"command": "cd \"<workspace>/plan-tools\" && python3 -I - <<'EOF'\ns = open('check_tickets.py').read()\ns = s.replace('Usage: python3 -I check_tickets.py PLAN.md', 'Usage: python3 -I check_tickets.py PLAN.md [DEVS]   (DEVS default 3)')\ns = s.replace('DEP = re.compile(r\"^Depends:\\\\s*(.+)$\")', 'DEP = re.compile(r\"^Depends:\\\\s*(.+)$\")\\nSIZE = re.compile(r\"^Size:\\\\s*(\\\\d+)d\\\\s*$\")') … [2266 more chars]`

<details><summary>result</summary>

```
--- devs=3
OK: 35 tickets, no cycles, order valid, all have AC
Longest chain (9 tickets): T-001 -> T-002 -> T-005 -> T-006 -> T-040 -> T-041 -> T-042 -> T-044 -> T-054
Effort: 126 dev-days total; critical path 36 working days
With 3 devs: lower bound 42 working days = 8.4 weeks (perfect parallelism, zero slack)
At 70% focus: 12.0 weeks
--- devs=2
OK: 35 tickets, no cycles, order valid, all have AC
Longest chain (9 tickets): T-001 -> T-002 -> T-005 -> T-006 -> T-040 -> T-041 -> T-042 -> T-044 -> T-054
Effort: 126 dev-days total; critical path 36 working days
With 2 devs: lower bound 63 working days = 12.6 weeks (perfect parallelism, zero slack)
At 70% focus: 18.0 weeks
--- devs=4
OK: 35 tickets, no cycles, order valid, all have AC
Longest chain (9 tickets): T-001 -> T-002 -> T-005 -> T-006 -> T-040 -> T-041 -> T-042 -> T-044 -> T-054
Effort: 126 dev-days total; critical path 36 working days
With 4 devs: lower bound 36 working days = 7.2 weeks (perfect parallelism, zero slack)
At 70% focus: 10.3 weeks
```

</details>

### Assistant

The schedule claim mostly holds: 11 weeks with 3 developers comes out at about 12 weeks at 70% focus. It collapses with 2 developers (18 weeks). I'll write that into the plan.

**→ Bash** `{"command": "python3 -I - <<'EOF'\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\nold = \"Estimate: ~11 weeks with 3 developers (one mobile-recording, one mobile-UI, one backend). This is a planning estimate, not measured.\"\nassert old in s\nnew = \"\"\"Estimate, computed by `plan-tools/check_tickets.py` from the ticket sizes (126 dev-days; critical path 36 working days):\n| … [1296 more chars]`

<details><summary>result</summary>

```
OK: 35 tickets, no cycles, order valid, all have AC
Longest chain (9 tickets): T-001 -> T-002 -> T-005 -> T-006 -> T-040 -> T-041 -> T-042 -> T-044 -> T-054
True spike-gps/test-analyze.mjs
True .ambition/tests/sizes.py
True .ambition/tests/xp_sim_v2.py
True plan-tools/check_tickets.py
analyze: all tests passed { clean: '14.99 km', gappyDropout: '1.00%' }
```

</details>

### Assistant

**Step 4 report: Challenge**

**Did.** I tested the plan's assumptions against the real sources and fixed what failed. The plan checker (now 35 tickets) and the analyzer test both pass after the fixes.

| Assumption | How I tested it | Result |
|---|---|---|
| The spike app compiles and uses Expo correctly | Installed the real packages (Expo SDK 58) and ran `tsc`; read the location plugin and Android manifest | **Failed, then fixed.** The task executor had to be async. The plugin keys and the `location` foreground-service type exist. Typecheck is clean, but the app is still not built or run on a device. |
| Apple requires Sign in with Apple when Google is offered | Read guideline 4.8 | **Wrong reason.** It requires an equivalent privacy-preserving login, not Apple specifically. The decision stays, with the rationale corrected. |
| 11 weeks with 3 developers | Sized all tickets (126 dev-days) and computed bounds with the checker | **Mostly holds:** about 12 weeks at 70% focus. With 2 developers it is about 18 weeks. The sizes are still my estimates. |
| 40 KB and 12 KB stored per ride | Measured a synthetic one-hour ride | Raw track is 39 KB gzipped, which matches. The DB figure was too high (about 3 KB). Real tracks will be noisier. |
| Level curve and XP | Simulated four rider types over 52 weeks | **Failed.** The plan had no XP formula, a keen rider reached level 167, and a commuter's first ride didn't reach level 2. I replaced it with a steeper curve and a weekly soft cap, which gives levels 12 to 46 at one year. The rider types are invented, so this is a starting point. |

**New finding.** Google Play requires a closed test with at least 12 testers opted in for 14 straight days before a new personal account gets production access. My schedule never mentioned it. I added ticket T-007 (accounts and recruiting 12 Android testers) and made the beta soak double as that test. Google's page didn't say whether organization accounts are exempt, so that is flagged to check.

**Changed course.** The pacing numbers and the 8-rides-per-user-per-month figure remain assumptions, and the plan labels them that way. The 2% / 60 s / ±3% / 10% per hour spike thresholds are still untested.

A snapshot is in `.ambition/steps/4/`.

### Context (injected)

<details><summary>show</summary>

Stop hook feedback:
Step 5 of pushing the work further: Range. Open your first message with this line on its own, exactly: `▸ Step 5/8 · Range`. Write that line nowhere else.

State what this is really trying to do, as verbs, keeping the genre's own verbs. Name 3-5 fields that do the same thing differently, always including the genre's own best practitioner and at least one you normally wouldn't consider, plus one whose job is to break it, misuse it and find who it could harm. Assemble them as if the result had to be extraordinary; let each propose a distinct direction, and name and take the edge those it serves would choose it for. The noun is still the deliverable. Borrow what they actually do. Don't play characters. Use subagents if useful.

Plan: give the verb form, the fields with the method and direction taken from each, the edge you took, and what the red team found, harms included. Build: apply what you borrowed to the deliverable, and fix what the red team broke.

When this step is finished, copy the deliverable as it stands to `.ambition/steps/5/` (even if this step didn't change it, and never edit that copy), end with a short step report (did / found / changed course), and stop. The next instruction arrives then.

## Every step

- **Focus on this step.** Do this step's instruction in full, as if the user had just typed its command. Don't anticipate other steps or hold work back for them.
- **No look, no claim.** Whenever you change something people look at, read or use, perceive the result the way they will: render it at the sizes they use and look, read it through, use it. If you can't, get that access first (install a browser or a renderer). If you still can't, say the genre bar is unchecked and leave how it looks, reads or feels as the first version had it.
- **Look efficiently.** Every image you look at stays in this conversation and is re-read on every later turn. Look at a contact sheet (many frames or sizes in one image) rather than one image per frame, and take at most about three render-and-look rounds in a step. Keep working files (screenshots, scripts) under `.ambition/`, not in the deliverable.
- **Never trade the genre for a number.** A change must make the work better for the goal without making it worse as this kind of thing. If it does, undo it.
- **Reviewing.** If the user asked to review each step, end the step with its report and wait for their notes before you copy it. Their notes are steering, not answers.
- Respect the session's permission mode and the user's rules. Ambition never authorises skipping a confirmation the user requires.

</details>

### Assistant

▸ Step 5/8 · Range

Mode is build. In verbs, the plan has to help a small team do five things:
- **Decide** the stack, scope and order of work, and **estimate** it.
- **Record** a ride reliably.
- **Reward** riders so they come back without pushing them to ride harder or riskier.
- **Share** rides so friends can see and cheer each other.
- **Protect** where riders live.

The first two are the genre's own verbs: a blueprint decides, orders and estimates, and the app must record. These are the fields I'm borrowing from:
- **Lead mobile engineer (the genre's best practitioner).** Method: build a thin working slice end to end first, then widen it.
- **Behavioural game designer.** Method: simulate whether a reward loop works for every kind of rider before committing to it.
- **Road-safety human-factors engineer (the field I wouldn't normally consider).** Method: hazard analysis of the incentives themselves. Which rewards make a rider go faster, take risks or look at a screen while moving?
- **Privacy and OSINT attacker (the red team).** Method: attack the privacy zone with the data it actually publishes, and look for who could be harmed.

Two things can be tested now: the privacy-zone attack and the quest-fairness claim. I'll also check Apple's rules for user-generated content.

**→ Bash** `{"command": "cd \"<workspace>/.ambition/tests\" && cat > privacy_attack.py <<'EOF'\n\"\"\"Red team: can an attacker recover a rider's home from the *published* (privacy-truncated) tracks?\nAttack: every published track starts where it leaves the privacy circle. Those cut points lie on a\ncircle of known radius around home -> fit the circle centre (least squares).\"\"\"\nimport math, random\nrandom … [2650 more chars]`

<details><summary>result</summary>

```
A fixed centre+radius              rides= 3  median error     0.0 m   90th pct     0.0 m
A fixed centre+radius              rides= 5  median error     0.0 m   90th pct     0.0 m
A fixed centre+radius              rides=10  median error     0.0 m   90th pct     0.0 m
A fixed centre+radius              rides=30  median error     0.0 m   90th pct     0.0 m
B secret offset + radius jitter    rides= 3  median error   106.4 m   90th pct   374.1 m
B secret offset + radius jitter    rides= 5  median error    74.7 m   90th pct   144.1 m
B secret offset + radius jitter    rides=10  median error    69.1 m   90th pct   101.5 m
B secret offset + radius jitter    rides=30  median error    65.7 m   90th pct    85.7 m
```

</details>

**→ Bash** `{"command": "cd \"<workspace>/.ambition/tests\" && cat > quests.py <<'EOF'\n\"\"\"Game designer: do fixed weekly quests work for every rider, or only for some?\nWeekly distributions are invented personas (same as xp_sim), so this tests the DESIGN, not real users.\"\"\"\nimport random, statistics\nrandom.seed(5)\nP = {  # (rides/wk mean, km per ride mean, climb m per ride mean)\n \"city commuter (f … [1380 more chars]`

<details><summary>result</summary>

```
FIXED quests - weekly completion rate
  city commuter (flat)   {'ride 3 days': ' 99%', '50 km total': ' 16%', 'climb 800 m': '  0%'}
  casual weekender       {'ride 3 days': ' 16%', '50 km total': ' 13%', 'climb 800 m': '  0%'}
  weekend hill rider     {'ride 3 days': ' 29%', '50 km total': ' 74%', 'climb 800 m': ' 71%'}
  keen club rider        {'ride 3 days': ' 99%', '50 km total': '100%', 'climb 800 m': '100%'}
PERSONALISED quests - target = 110% of the user's trailing 4-week median (floor: days>=2)
  city commuter (flat)   {'days': ' 35%', 'km': ' 37%', 'climb': ' 37%'}
  casual weekender       {'days': ' 37%', 'km': ' 44%', 'climb': ' 46%'}
  weekend hill rider     {'days': ' 40%', 'km': ' 44%', 'climb': ' 44%'}
  keen club rider        {'days': ' 37%', 'km': ' 36%', 'climb': ' 37%'}
```

</details>

**→ WebFetch** `{"url": "https://developer.apple.com/app-store/review/guidelines/", "prompt": "Quote guideline 1.2 (User-Generated Content) exactly, including the required precautions (filter, report, block, contact info). Also quote any guideline text about minimum age / children's data and about location data collection (5.1.1, 5.1.2) that would matter for an app that shares users' ride routes with other users. … [2 more chars]`

<details><summary>result</summary>

```
## Guideline 1.2: User-Generated Content

> Apps that enable users to create, generate, upload, share, or otherwise contribute content present particular challenges, including intellectual property infringement, nonconsensual intimate imagery, and anonymous bullying. This includes social media, user-generated content platforms, and AI content creation apps. To prevent abuse, such apps must include:
>
> * A method for filtering objectionable material from being posted to the app
> * A mechanism to report offensive content and timely responses to concerns
> * The ability to block abusive users from the service
> * Published contact information so users can easily reach you
>
> Apps with user-generated content or services that end up being used primarily for pornographic content, Chatroulette-style experiences, random or anonymous chat, objectification of real people (such as "hot-or-not" voting), making physical threats, or bullying do not belong on the App Store and may be removed without notice. If your app includes user-generated content from a web-based service, it may display incidental mature "NSFW" content, provided that the content is hidden by default and only displayed when the user turns it on via your website.
>
> It is your responsibility to remove content that violates this guideline, your terms of service, or your community standards. Developers who fail to implement appropriate safeguards or fail to remediate identified violations after notice may be considered in violation of the Developer Code of Conduct. [...] Egregious or repeated behavior is grounds for immediate removal of your app from the App Store, and from the Apple Developer Program.

## Guideline 5.1.1: Data Collection and Storage (relevant parts)

**(i) Privacy Policies:**
> All apps must include a link to their privacy policy in the App Store Connect metadata field and within the app in an easily accessible manner. The privacy policy must clearly and explicitly:
> * Identify what data, if … [4961 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>/.ambition/tests\" && cat > privacy_attack2.py <<'EOF'\n\"\"\"Second attack: extend each published track's first segment BACKWARDS; the rays meet near home.\nRoads curve, so heading at the cut point = departure heading + noise that grows with distance.\"\"\"\nimport math, random\nrandom.seed(21)\ndef lsq_intersection(rays):  # point minimising squared distance to all r … [1783 more chars]`

<details><summary>result</summary>

```
road curvature noise 0.15 rad per 200 m
   A  R=200 fixed       rides= 5 median err     26 m   90th pct     53 m
   A  R=200 fixed       rides=30 median err     10 m   90th pct     21 m
   B  R=200..320 +offset rides= 5 median err     35 m   90th pct     82 m
   B  R=200..320 +offset rides=30 median err     17 m   90th pct     33 m
   C  R=400..640 +offset rides= 5 median err    102 m   90th pct    237 m
   C  R=400..640 +offset rides=30 median err     55 m   90th pct     94 m
road curvature noise 0.4 rad per 200 m
   A  R=200 fixed       rides= 5 median err     74 m   90th pct    144 m
   A  R=200 fixed       rides=30 median err     39 m   90th pct     65 m
   B  R=200..320 +offset rides= 5 median err    106 m   90th pct    203 m
   B  R=200..320 +offset rides=30 median err     61 m   90th pct    101 m
   C  R=400..640 +offset rides= 5 median err    271 m   90th pct    472 m
   C  R=400..640 +offset rides=30 median err    175 m   90th pct    269 m
```

</details>

**→ Bash** `{"command": "python3 -I - <<'EOF'\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\ndef rep(old, new):\n    global s\n    assert s.count(old) == 1, old[:70]\n    s = s.replace(old, new)\n\n# Principles (the edge)\nrep(\"## 2. Decisions (settled\", \"\"\"## 1b. Product principles (the edge over Strava-style apps)\nRiders choose this app because it is **fair, safe and private by  … [9560 more chars]`

<details><summary>result</summary>

```
sed: /dev/null: in-place editing only works for regular files
OK: 36 tickets, no cycles, order valid, all have AC
Longest chain (9 tickets): T-001 -> T-002 -> T-005 -> T-006 -> T-040 -> T-041 -> T-042 -> T-044 -> T-054
Effort: 130 dev-days total; critical path 36 working days
With 3 devs: lower bound 43 working days = 8.7 weeks (perfect parallelism, zero slack)
At 70% focus: 12.4 weeks
[This command modified 1 file you've previously read: ../../../cfg/plans/make-a-plan-for-jaunty-wren.md. Call Read before editing.]
```

</details>

### Assistant

The checker passes with 36 tickets. The effort total moved from 126 to 130 dev-days, so I'll update section 8's numbers and then snapshot.

**→ Bash** `{"command": "cd \"<workspace>\" && for d in 2 3 4; do python3 -I plan-tools/check_tickets.py /cfg/plans/make-a-plan-for-jaunty-wren.md $d | sed -n '4,5p' | tr '\\n' ' '; echo; done", "description": "Recompute schedule bounds for 2, 3, 4 devs"}`

<details><summary>result</summary>

```
With 2 devs: lower bound 65 working days = 13.0 weeks (perfect parallelism, zero slack) At 70% focus: 18.6 weeks 
With 3 devs: lower bound 43 working days = 8.7 weeks (perfect parallelism, zero slack) At 70% focus: 12.4 weeks 
With 4 devs: lower bound 36 working days = 7.2 weeks (perfect parallelism, zero slack) At 70% focus: 10.3 weeks
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\nfor old, new in [(\"(126 dev-days; critical path 36 working days)\", \"(130 dev-days; critical path 36 working days)\"),\n                 (\"| 2 devs | 12.6 wk | ~18 wk |\", \"| 2 devs | 13.0 wk | ~19 wk |\"),\n                 (\"| 3 devs (mobile-recording, mobile-UI, bac … [500 more chars]`

<details><summary>result</summary>

```
OK: 36 tickets, no cycles, order valid, all have AC
.ambition/steps/5:
make-a-plan-for-jaunty-wren.md

.ambition/tests:
privacy_attack.py
privacy_attack2.py
quests.py
sizes.py
xp_sim_v2.py
xp_sim.py
```

</details>

### Assistant

**Step 5 report: Range**

**Did.** The plan now has product principles (§1b) that make it fair, safe and private by default. Five of the new or changed tickets enforce them. I borrowed from four fields. I ran the attack and quest simulations myself, so I used no subagents. The plan checker passes with 36 tickets, and I snapshotted the plan to `.ambition/steps/5/`.

| Field | What I borrowed | Edge taken |
|---|---|---|
| Lead mobile engineer | A walking skeleton first, four milestones that are each a ride-able build, a definition of done | Four milestones (M1 to M4) in §8 |
| Behavioural game designer | Simulate each rider type before fixing the reward design | Personalised weekly quests |
| Road-safety human-factors engineer | Hazard analysis of the incentives themselves | No rewards for speed or risk, and nothing shown while moving |
| Privacy attacker (red team) | Attack the published data, and look for who could be harmed | Private by default, with honest privacy-zone copy |

**What the red team found.**
- **The plan's privacy zone was broken.** A fixed-centre, fixed-radius zone gave up the home to 0.0 m error from 3 published rides. A secret offset plus radius jitter helps, but a second attack (extending each track's heading backwards) still finds home within about 17 to 61 m after 30 rides. A 400 m zone raises that to 55 to 175 m. Hiding geometry can't be the main protection.
- **So visibility is now approval-gated.** Follows need the rider's approval, maps go only to approved followers, and there is no public discovery or live location. The shipped zone settings are untested against the circle-fit attack, so ticket T-022 requires that run.
- **Fixed quests are unfair.** "Climb 800 m" is completed 0% of weeks by commuters and 100% by keen riders. Personalised targets give every rider type 35 to 46%.
- **Missing requirement.** Apple guideline 1.2 requires report, block and contact info, so I added ticket T-045. Effort is now 130 dev-days, about 12.4 weeks for 3 developers at 70% focus.

**Not resolved.**
- The minimum age and children's-privacy rules for sharing location need legal advice. Apple's page sets no general minimum age.
- The simulations use invented rider types, so real ride data should replace them.
- I didn't verify the road-safety field's claims from external sources. The principles come from design reasoning, not citations.

### Context (injected)

<details><summary>show</summary>

Stop hook feedback:
Step 6 of pushing the work further: Judge. Open your first message with this line on its own, exactly: `▸ Step 6/8 · Judge`. Write that line nowhere else.

Don't grade your own work, and don't ask another model to grade it. Use or build a check that isn't you (tests, a real run, real people, a simulation, a benchmark, reference output), ideally a tool you can run for immediate feedback. Run it, and iterate until it passes. Check it against the original ask intact and every promise in the restatement, then the genre bar the way that genre is checked: render it and look at what it actually produced, read it through whole as a cold read by its reader, for gaps, contradictions, repeats and anything its reader won't use, use it. Report what it showed.

Meet the original ask first, intact, and every promise in the restatement, and keep them passing. Give the final a cold read as its reader would. For something visual, render frames at the sizes its audience uses and measure what matters (errors, timing, loop seams, layout, contrast), then look at them. Compare the work with the first version on the same check: it must be better on every part of the ask and on the goal, and worse on nothing, the genre bar included. If it isn't, fix it, or go back to the first version plus the improvements that held up.

Plan: define the outside check the build will be held to, and build it now if that's cheap: a plan with its acceptance test already written is a stronger plan. The plan must be better than the first version on every part of the ask and on the goal, and at least as clear and usable.

When this step is finished, copy the deliverable as it stands to `.ambition/steps/6/` (even if this step didn't change it, and never edit that copy), end with a short step report (did / found / changed course), and stop. The next instruction arrives then.

## Every step

- **Focus on this step.** Do this step's instruction in full, as if the user had just typed its command. Don't anticipate other steps or hold work back for them.
- **No look, no claim.** Whenever you change something people look at, read or use, perceive the result the way they will: render it at the sizes they use and look, read it through, use it. If you can't, get that access first (install a browser or a renderer). If you still can't, say the genre bar is unchecked and leave how it looks, reads or feels as the first version had it.
- **Look efficiently.** Every image you look at stays in this conversation and is re-read on every later turn. Look at a contact sheet (many frames or sizes in one image) rather than one image per frame, and take at most about three render-and-look rounds in a step. Keep working files (screenshots, scripts) under `.ambition/`, not in the deliverable.
- **Never trade the genre for a number.** A change must make the work better for the goal without making it worse as this kind of thing. If it does, undo it.
- **Reviewing.** If the user asked to review each step, end the step with its report and wait for their notes before you copy it. Their notes are steering, not answers.
- Respect the session's permission mode and the user's rules. Ambition never authorises skipping a confirmation the user requires.

</details>

### Assistant

▸ Step 6/8 · Judge

Mode is build. Two checks here: a script that holds the plan to its promises, and a full cold read of the plan as your team would meet it. I'll read it first.

**→ Read** `{"file_path": "/cfg/plans/make-a-plan-for-jaunty-wren.md"}`

<details><summary>result</summary>

```
1	# SpokeQuest — Build Blueprint (React Native + Expo, social gamified cycling tracker)
2	
3	Working name: **SpokeQuest** (placeholder). Target: a small team ships a public v1 on iOS and Android.
4	Pricing and package versions below were fetched on **2026-11-13** (sources in §4).
5	
6	## 1. Context and goal
7	Strava owns tracking and social for cyclists, but its game layer is thin. SpokeQuest is cycling-only: record a ride, get XP, keep a weekly streak, finish weekly quests, and compete with friends. Everything depends on **reliable background ride recording**, so that is gated first (§3) and built first (Phase 1).
8	
9	**v1 success bar (beta, ~20 riders):** crash-free sessions ≥ 99%; ride-save success ≥ 98%; ≥ 40% of new users record a second ride within 14 days. (Targets are starting points to calibrate, not measured facts.)
10	
11	## 1b. Product principles (the edge over Strava-style apps)
12	Riders choose this app because it is **fair, safe and private by default**. Each principle was tested (scripts in `.ambition/tests/`) and is enforced by a ticket's acceptance criteria.
13	1. **Never reward speed or risk.** XP comes from distance and climbing with a weekly soft cap; no segments, KOMs or speed leaderboards in v1; max speed is shown only to the rider on their own summary, never in the feed.
14	2. **Hands-off while moving.** Reward reveals appear only after a ride is finished; our own notifications are suppressed while recording; the record screen has large controls and works with the screen locked.
15	3. **Private by default.** Following requires the rider's approval; ride maps are visible only to approved followers; no public discovery of rides; no live-location sharing in v1.
16	4. **Fair quests.** Targets are personal (110% of the rider's trailing 4-week median), not fixed. A fixed "climb 800 m" quest is completed 0% of weeks by commuters and 100% by keen riders (`quests.py`); personalised targets land every rider type at 35–46%.
17	5. **Honest privacy zones … [25461 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && mkdir -p plan-tools/sims && cp .ambition/tests/privacy_attack.py .ambition/tests/privacy_attack2.py .ambition/tests/quests.py .ambition/tests/sizes.py plan-tools/sims/ && cat > plan-tools/sims/xp_rules.py <<'EOF'\n\"\"\"XP and level rules exactly as specified in plan section 6, plus the 52-week persona simulation.\nRun: python3 -I xp_rules.py   (prints worked exa … [2990 more chars]`

<details><summary>result</summary>

```
WORKED EXAMPLES (base, awarded, level)
   ('1 first ever ride, 8 km / 40 m', 88, 388, 2)
   ('2 long hilly ride, 60 km / 600 m (per-ride cap)', 600, 600, None)
   ('3 third 600-XP ride in a week (1,200 already earned)', 600, 375, None)
   ('4 25 km / 150 m in the 4th active week (+15%)', 280, 322, None)
   ('5 quest completed (flat, no cap, no bonus)', 100, 100, None)
thresholds {2: 240, 3: 540, 5: 1500, 10: 6000, 20: 24000, 30: 54000, 50: 150000}
SIMULATION 52 weeks (level after ride 1, level at 52 w, total xp)
  commuter 5x8km                   (2, 23, 33928)
  weekend 60+25km                  (3, 32, 61814)
  casual 1x15km (70% of weeks)     (2, 12, 8705)
  keen 6x45km                      (3, 46, 130126)
```

</details>

### Assistant

The rules now live in code, and the worked examples come from it. The exact spec gives the commuter L23 (earlier I had L24), so the plan gets the corrected figure. Now the plan fixes.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\nimport re\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\ndef rep(old, new, count=1):\n    global s\n    assert s.count(old) == count, (s.count(old), old[:70])\n    s = s.replace(old, new)\n\n# A. script locations\ns = s.replace(\"`.ambition/tests/sizes.py`\", \"`plan-tools/sims/sizes.py`\")\ns = s.replace(\"(scripts in … [5864 more chars]`

<details><summary>result</summary>

```
ok
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && cat > plan-tools/plan_lint.py <<'EOF'\n#!/usr/bin/env python3\n\"\"\"Hold the plan to its promises. Usage: python3 -I plan_lint.py PLAN.md   (exit 1 on any FAIL)\n\nNothing here trusts the plan's own numbers: costs, schedule, XP examples, quest and privacy\nfigures are recomputed from the rules/scripts and compared with what the plan says.\"\"\"\nimport os, re, s … [10227 more chars]`

<details><summary>result</summary>

```
Exit code 1
PASS ask: names React Native, Expo, social, gamified, cycling
PASS ask: fitness/ride tracking present
PASS tickets: order, deps, AC, size valid
PASS refs: every §n points at a real section
PASS refs: every T-nnn mentioned exists
PASS refs: every script/file path in the plan exists
PASS refs: nothing depends on the throwaway .ambition folder
FAIL stale: no dated 'weeks N' labels, no 'MVP' leftovers
PASS cost: Mapbox line recomputed from $4/1k above 25k MAU
PASS cost: Expo line recomputed from plan prices
PASS cost: subtotal = sum of the three lines
PASS cost: unverified items labelled, sources + date given
PASS schedule: dev-days and critical path match the ticket sizes
PASS schedule: 2-dev row matches the checker
PASS schedule: 3-dev row matches the checker
PASS schedule: 4-dev row matches the checker
FAIL xp: the five worked examples equal the code's output   <- code ['388', '600', '375', '322', '100'] vs plan []
FAIL xp: 52-week levels in the plan equal the simulation   <- plan ('12', '23', '32', '46') vs {'commuter': '23', 'weekend': '32', 'keen': '46'}
PASS xp: streak bonus text agrees with code (5% x max 5 = +25%)
PASS quests: personalised completion range equals simulation
PASS quests: fixed 'climb 800 m' 0% commuters / 100% keen as stated
PASS privacy: fixed zone recovered to 0.0 m from 3 rides (as stated)
PASS privacy: heading-attack errors equal simulation (±1 m)
PASS promise: stack decisions settled (no TBD / 'to be decided')
PASS promise: Mapbox and Supabase choices made with rejected alternatives named
PASS promise: every deferral has a reason (>= 15 chars)
PASS promise: recording reliability marked UNVERIFIED while results table is empty
PASS promise: spike gates the recording ticket (T-013 depends on T-010)
PASS principle enforced: T-034 reward reveal
PASS principle enforced: T-041 feed
PASS principle enforced: T-040 follow
PASS principle enforced: T-044 push
PASS principle enforced: T-015 record screen
PASS principle enforced: principle 1
 … [131 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\nold = \" friends leaderboard tests the social loop first. *(Moved out of the earlier MVP.)* |\"\nassert old in s\ns = s.replace(old, \" friends leaderboard tests the social loop first |\")\nopen(p, 'w').write(s)\nl = open('plan-tools/plan_lint.py').read()\nl = l.replace('tb … [736 more chars]`

<details><summary>result</summary>

```
36/36 checks passed
```

</details>

### Assistant

The lint is green at 36/36. A check that never fails proves nothing, so I'll try six deliberate breakages. Then I'll run it on the first version for the comparison.

**→ Bash** `{"command": "cd \"<workspace>\" && mkdir -p .ambition/lintwork && P=/cfg/plans/make-a-plan-for-jaunty-wren.md && W=.ambition/lintwork\nmut() { sed \"$2\" $P > $W/m.md; r=$(python3 -I plan-tools/plan_lint.py $W/m.md | grep -c '^FAIL'); echo \"mutation [$1] -> $r failing check(s)\"; }\nmut \"Mapbox 50k cost 100->90\"       's/| Mapbox Mobile Maps | 0 | 0 | 100 |/| Mapbox Mobile Maps | 0 | 0 | 90 |/' … [727 more chars]`

<details><summary>result</summary>

```
mutation [Mapbox 50k cost 100->90] -> 2 failing check(s)
mutation [worked example 322->330] -> 1 failing check(s)
mutation [commuter level 23->30] -> 1 failing check(s)
mutation [dangling section ref §99] -> 1 failing check(s)
mutation [ticket cycle T-001 dep T-054] -> 0 failing check(s)
mutation [drop principle phrase] -> 1 failing check(s)
--- FIRST VERSION
9/36 checks passed
9
```

</details>

### Assistant

The cycle mutation reporting 0 failures is suspicious: it may mean my mutation didn't apply, or that the lint crashed. I'll check which.

**→ Bash** `{"command": "cd \"<workspace>\" && P=/cfg/plans/make-a-plan-for-jaunty-wren.md && W=.ambition/lintwork\npython3 -I - <<'EOF'\ns = open('/cfg/plans/make-a-plan-for-jaunty-wren.md').read()\ni = s.index(\"Depends: none\")\nopen('.ambition/lintwork/cycle.md', 'w').write(s[:i] + \"Depends: T-054\" + s[i+len(\"Depends: none\"):])\nEOF\npython3 -I plan-tools/plan_lint.py $W/cycle.md 2>&1 | grep -E \"^FAI … [106 more chars]`

<details><summary>result</summary>

```
FAIL tickets: order, deps, AC, size valid   <-  - T-001: listed before its prerequisite T-054
FAIL schedule: dev-days and critical path match the ticket sizes   <- plan ('130', '36') vs (0, 0)
FAIL schedule: 2-dev row matches the checker   <- plan ('13.0', '19') vs None
FAIL schedule: 3-dev row matches the checker   <- plan ('8.7', '12') vs None
FAIL schedule: 4-dev row matches the checker   <- plan ('7.2', '10') vs None
31/36 checks passed
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\ndef rep(old, new):\n    global s\n    assert s.count(old) == 1, old[:60]\n    s = s.replace(old, new)\n\nrep(\"## 1. Context and goal\\n\", \"\"\"## At a glance\n- **What:** an iOS + Android app (React Native, Expo) where cyclists record rides, earn XP and weekly streaks, f … [2559 more chars]`

<details><summary>result</summary>

```
Effort: 133 dev-days total; critical path 36 working days|With 2 devs: lower bound 66 working days = 13.3 weeks (perfect parallelism, zero slack)|At 70% focus: 19.0 weeks|
Effort: 133 dev-days total; critical path 36 working days|With 3 devs: lower bound 44 working days = 8.9 weeks (perfect parallelism, zero slack)|At 70% focus: 12.7 weeks|
Effort: 133 dev-days total; critical path 36 working days|With 4 devs: lower bound 36 working days = 7.2 weeks (perfect parallelism, zero slack)|At 70% focus: 10.3 weeks|
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\nfor old, new in [(\"(130 dev-days; critical path 36 working days)\", \"(133 dev-days; critical path 36 working days)\"),\n                 (\"| 2 devs | 13.0 wk | ~19 wk |\", \"| 2 devs | 13.3 wk | ~19 wk |\"),\n                 (\"| 3 devs (mobile-recording, mobile-UI, bac … [1455 more chars]`

<details><summary>result</summary>

```
39/39 checks passed
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\nold = \"- AC: crash-free \u2265 99%, ride-save success \u2265 98%, Play production access granted, results written back into \u00a71.\"\nassert s.count(old) == 1\ns = s.replace(old, \"- AC: crash-free sessions \u2265 99% (Sentry), ride-save success \u2265 98% (`ride_saved`  … [1108 more chars]`

<details><summary>result</summary>

```
PASS spike: analyzer tests pass

40/40 checks passed
exit=0
lint exit=0
      97 .ambition/first/make-a-plan-for-jaunty-wren.md
     398 .ambition/steps/6/make-a-plan-for-jaunty-wren.md
     495 total
```

</details>

### Assistant

**Step 6 report: Judge**

**Did.** I built `plan-tools/plan_lint.py`, an outside check that holds the plan to its promises. It recomputes the plan's numbers from code and sources: costs, schedule, XP examples, quest and privacy figures. It also resolves every cross-reference, checks the original ask and each restatement promise, and checks that each principle has a ticket enforcing it. The plan passes 40 of 40 checks. The same check gives the first version 9 of 36. I also gave the plan a full cold read, and a snapshot is in `.ambition/steps/6/`.

**What the checks showed.**
- **Mutation controls:** six deliberate breakages (a cost, an XP example, a level, a dangling reference, a dependency cycle, a principle) each tripped the lint, so it can fail. My first cycle attempt used a `sed` form that doesn't work on macOS; the portable version failed correctly.
- **Lint bugs:** two of my first three failures were parsing mistakes in the lint (an indented table, a persona name with parentheses), not plan faults. I fixed the lint.

**Plan faults from the cold read, now fixed:**
- **Streak bonus:** the text said max +20% but the tested simulation used +25%. XP is now defined once, in `plan-tools/sims/xp_rules.py`, which generates the plan's worked examples. This moved the commuter's year-end level from L24 to L23.
- **Missing details:** the eight badges were promised but never listed, and the five worked XP examples were missing. Both are now in the plan.
- **Dependence on throwaway files:** the plan pointed at scripts in `.ambition/`. They're now in `plan-tools/sims/`.
- **Contradictions and gaps:**
  - Dated week labels contradicted the computed schedule.
  - Section 3 said to start the Play review early but pointed at a late ticket.
  - The v1 scope list omitted follow approval and block/report.
  - "XP can't be forged" overclaimed.
  - A stale "earlier MVP" mention referred to a version your team never saw.
  - No ticket measured the 40% second-ride target.
- **Things the first version had and I'd dropped:** target users, end-to-end tests (now T-019), and the launch-region question. I also added km/miles units, which neither version had.
- **Usability:** the plan grew from 97 to 398 lines. To keep it scannable I added an "At a glance" block at the top with the numbers, the biggest risk and the first three actions, and the lint checks those numbers against the real ones.

**Now vs. first version.** The plan is better on every part of the ask and on the goal, and I found nothing it does worse. The first version is shorter and easier to skim, but it couldn't be built from. It is 13 weeks for 3 developers with 37 tickets and 133 dev-days.

**Still unchecked.** A cold read by your developers (you said you'd do that) and the real-phone spike. The sizes and thresholds are still my estimates.

### Context (injected)

<details><summary>show</summary>

Stop hook feedback:
Step 7 of pushing the work further: Stretch. Open your first message with this line on its own, exactly: `▸ Step 7/8 · Stretch`. Write that line nowhere else.

Pick a specific target several times harder than mine, with a tight deadline where time matters, and make it the target, keeping mine as a fallback that fits. Assume it's solvable, since someone has done something like it, and work out how. If it looks impossible, keep going from a different angle before concluding. Falling short is fine; tell me where it broke.

Go for it on top of a working deliverable, and never leave the deliverable worse than before this step: if an attempt doesn't hold up, keep the version from before it. Plan: raise the plan's target to the stretch and rework the plan toward it, keeping the original target as a fallback that fits, and say where it would likely break.

When this step is finished, copy the deliverable as it stands to `.ambition/steps/7/` (even if this step didn't change it, and never edit that copy), end with a short step report (did / found / changed course), and stop. The next instruction arrives then.

## Every step

- **Focus on this step.** Do this step's instruction in full, as if the user had just typed its command. Don't anticipate other steps or hold work back for them.
- **No look, no claim.** Whenever you change something people look at, read or use, perceive the result the way they will: render it at the sizes they use and look, read it through, use it. If you can't, get that access first (install a browser or a renderer). If you still can't, say the genre bar is unchecked and leave how it looks, reads or feels as the first version had it.
- **Look efficiently.** Every image you look at stays in this conversation and is re-read on every later turn. Look at a contact sheet (many frames or sizes in one image) rather than one image per frame, and take at most about three render-and-look rounds in a step. Keep working files (screenshots, scripts) under `.ambition/`, not in the deliverable.
- **Never trade the genre for a number.** A change must make the work better for the goal without making it worse as this kind of thing. If it does, undo it.
- **Reviewing.** If the user asked to review each step, end the step with its report and wait for their notes before you copy it. Their notes are steering, not answers.
- Respect the session's permission mode and the user's rules. Ambition never authorises skipping a confirmation the user requires.

</details>

### Assistant

▸ Step 7/8 · Stretch

Mode is build. The plan's current target is the full v1 in about 13 weeks with 3 developers. The stretch target is **12 riders recording real rides with XP on their own phones by the end of week 4 (3× faster), and a public store launch by week 8 (1.6× faster)**. The current plan stays as the fallback.

To see if that holds, I'll write a tool that takes a sub-release (which tickets are in, which are shrunk, which dependencies are cut) and computes what it costs. First, one thing I noticed while sizing. T-010 (the GPS spike) says it depends on T-002 (EAS builds), but the spike app builds locally with no EAS. That dependency is false, and it delays the riskiest check in the plan.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\nold = \"### T-010 \u00b7 GPS spike gate (human)\\nDepends: T-002\\nSize: 3d\\n- Run `spike-gps` per its README on iPhone and Android;\"\nassert old in s\ns = s.replace(old, \"### T-010 \u00b7 GPS spike gate (human)\\nDepends: none\\nSize: 3d\\n- Needs only the phones and lo … [3313 more chars]`

<details><summary>result</summary>

```
written
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\nmarker = \"## 9. Risks\"\nassert s.count(marker) == 1\nsec = \"\"\"## 8b. Stretch targets and release train\n**Fallback target (the plan above):** the full v1 \u2014 37 tickets, 133 dev-days \u2014 in about 13 weeks with 3 developers.\n\n**Stretch target (3\u00d7 faster to  … [2978 more chars]`

<details><summary>result</summary>

```
S1 · First rides: 18 tickets, 51 dev-days, critical path 16 days
   3 devs: 3.4 wk at 100% focus, 4.9 wk at 70%
   4 devs: 3.2 wk at 100% focus, 4.6 wk at 70%
S2 · Public launch: 34 tickets, 115 dev-days, critical path 24 days
   3 devs: 7.7 wk at 100% focus, 11.0 wk at 70%
   4 devs: 5.8 wk at 100% focus, 8.2 wk at 70%
exit=0
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\ndef rep(old, new):\n    global s\n    assert s.count(old) == 1, old[:60]\n    s = s.replace(old, new)\nrep(\"Resize: T-004=2, T-011=2, T-014=3, T-017=3, T-020=2, T-022=3\\nUnlink: T-013!T-010, T-018!T-017\\nLink: T-018>T-013\",\n    \"Resize: T-004=2, T-011=2, T-013=7, T-01 … [2080 more chars]`

<details><summary>result</summary>

```
S1 · First rides: 18 tickets, 52 dev-days, critical path 14 days
   3 devs: 3.5 wk at 100% focus, 5.0 wk at 70%
   4 devs: 2.8 wk at 100% focus, 4.0 wk at 70%
S2 · Public launch: 34 tickets, 116 dev-days, critical path 24 days
   3 devs: 7.7 wk at 100% focus, 11.0 wk at 70%
   4 devs: 5.8 wk at 100% focus, 8.3 wk at 70%
S1x · Stress test of S1: 18 tickets, 59 dev-days, critical path 21 days
   3 devs: 4.2 wk at 100% focus, 6.0 wk at 70%
   4 devs: 4.2 wk at 100% focus, 6.0 wk at 70%
exit=0
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\nimport re, subprocess\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\ndef rep(old, new):\n    global s\n    assert s.count(old) == 1, old[:60]\n    s = s.replace(old, new)\n\n# lever release S2L\ns2 = re.search(r\"### Release S2 \u00b7 Public launch\\nInclude: (.*)\\n\", s).group(1)\ninc = \", \".join(t for t in s2.spli … [1582 more chars]`

<details><summary>result</summary>

```
S1 · First rides: 18 tickets, 52 dev-days, critical path 14 days
   3 devs: 3.5 wk at 100% focus, 5.0 wk at 70%
   4 devs: 2.8 wk at 100% focus, 4.0 wk at 70%
S2 · Public launch: 34 tickets, 116 dev-days, critical path 24 days
   3 devs: 7.7 wk at 100% focus, 11.0 wk at 70%
   4 devs: 5.8 wk at 100% focus, 8.3 wk at 70%
S2L · Public launch, leaner (lever): 32 tickets, 111 dev-days, critical path 24 days
   3 devs: 7.4 wk at 100% focus, 10.6 wk at 70%
   4 devs: 5.5 wk at 100% focus, 7.9 wk at 70%
S1x · Stress test of S1: 18 tickets, 59 dev-days, critical path 21 days
   3 devs: 4.2 wk at 100% focus, 6.0 wk at 70%
   4 devs: 4.2 wk at 100% focus, 6.0 wk at 70%
```

</details>

### Assistant

Now the "where it breaks" section, the at-a-glance line, and lint checks so the results table can't drift from the tool.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\ndef rep(old, new):\n    global s\n    assert s.count(old) == 1, old[:60]\n    s = s.replace(old, new)\nrep(\"## 9. Risks\", \"\"\"### Verdict and where the stretch breaks\n- **S1 (first riders, 4 weeks) is reachable with 4 developers \u2014 at zero margin.** It needs the sp … [3751 more chars]`

<details><summary>result</summary>

```
PASS stretch: every release is internally consistent (no missing prerequisites)
PASS stretch: results row S1 equals the calculator
PASS stretch: results row S2 equals the calculator
PASS stretch: results row S2L equals the calculator
PASS stretch: results row S1x equals the calculator
PASS stretch: verdict says where it breaks and names the fallback
PASS stretch: fallback row matches the full-plan checker
47/47 checks passed
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I plan-tools/check_tickets.py /cfg/plans/make-a-plan-for-jaunty-wren.md | sed -n '2p'; python3 -I - <<'EOF'\np = '/cfg/plans/make-a-plan-for-jaunty-wren.md'\ns = open(p).read()\nold = \"- **Riskiest path (8 tickets):** T-001 \u2192 T-002 \u2192 **T-010** \u2192 T-013 \u2192 T-017 \u2192 T-018 \u2192 T-034 \u2192 T-054. If T-010 fails, this path grows by  … [1885 more chars]`

<details><summary>result</summary>

```
Longest chain (9 tickets): T-001 -> T-002 -> T-005 -> T-006 -> T-040 -> T-041 -> T-042 -> T-044 -> T-054
Traceback (most recent call last):
  File "<workspace>/plan-tools/plan_lint.py", line 68, in <module>
    okp = bool(hops) and all(a in tdeps[b]["deps"] for a, b in zip(hops, hops[1:]))
                         ^^^
  File "<workspace>/plan-tools/plan_lint.py", line 68, in <genexpr>
    okp = bool(hops) and all(a in tdeps[b]["deps"] for a, b in zip(hops, hops[1:]))
                                  ~~~~~^^^
TypeError: list indices must be integers or slices, not str
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\nl = open('plan-tools/plan_lint.py').read()\nl = l.replace(\"tk, tdeps = ct_parse(plan_path)\", \"tk, _order = ct_parse(plan_path)\").replace('all(a in tdeps[b][\"deps\"] for a, b in zip(hops, hops[1:]))', 'all(a in tk[b][\"deps\"] for a, b in zip(hops, hops[1:]))')\nopen('plan-tools/plan_lint.py', 'w').write(l)\nEOF\npython3 -I plan-tools/pl … [148 more chars]`

<details><summary>result</summary>

```
PASS refs: every script/file path in the plan exists
PASS schedule: the 'longest chain' sentence equals the checker's chain
PASS schedule: every hop of the 'riskiest path' is a real dependency
PASS schedule: dev-days and critical path match the ticket sizes
49/49 checks passed
```

</details>

### Assistant

49 of 49 pass. A quick mutation check on the new hop test, then the snapshot.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\ns = open('/cfg/plans/make-a-plan-for-jaunty-wren.md').read()\nopen('.ambition/lintwork/hop.md', 'w').write(s.replace(\"T-001 \u2192 T-011 \u2192 T-012 \u2192 **T-013**\", \"T-001 \u2192 T-012 \u2192 **T-013**\"))\nopen('.ambition/lintwork/s1.md', 'w').write(s.replace(\"Unlink: T-011!T-001, T-013!T-010, T-015!T-013, T-018!T-017\\nLink: T-015> … [437 more chars]`

<details><summary>result</summary>

```
FAIL schedule: every hop of the 'riskiest path' is a real dependency   <- hops ['T-001', 'T-012', 'T-013', 'T-017', 'T-018', 'T-034', 'T-054']
49/49 checks passed
     456 .ambition/steps/7/make-a-plan-for-jaunty-wren.md
```

</details>

### Assistant

**Step 7 report: Stretch**

**Did.** I raised the plan's target and kept the 13-week full v1 as the fallback. The stretch is 12 riders recording real rides with XP by the end of week 4 (3× faster), and a public store launch by week 8. The plan gets there by shipping two earlier releases. I wrote `plan-tools/releases.py`, which computes each release's effort and schedule and fails if a release includes a ticket whose prerequisite is missing. The plan now passes all 49 lint checks, and I snapshotted it to `.ambition/steps/7/`. The full-v1 tickets are unchanged.

**What the numbers say (70% focus):**

| Release | 3 developers | 4 developers |
|---|---|---|
| S1: first riders | 5.0 weeks | **4.0 weeks** |
| S2: public launch | 11.0 weeks | 8.3 weeks |
| S2 without kudos and the friends leaderboard | 10.6 weeks | 7.9 weeks |
| Full v1 (the fallback) | 12.7 weeks | 10.3 weeks |

**Found.**
- **The first attempt missed.** It gave 4.6–4.9 weeks for S1, held back by the recording path. Three changes fixed that: starting the geo library on day 1 before the app skeleton exists, building the record screen against a mocked recorder while the background task is written, and running the GPS spike on day 1.
- **A false dependency:** T-010 depended on T-002, but the spike builds locally, so the dependency delayed the riskiest check for no reason. I removed it from the full plan too, and fixed the stale "riskiest path" sentence that had relied on it.

**Where it breaks.**
- **S1 hits 4.0 weeks with zero margin, and only with 4 developers.** Each day lost on the critical path costs about 1.4 calendar days.
- **If recording takes twice as long** (for example if the spike fails), S1 lands at 6.0 weeks whatever the team size.
- **S2 misses 8 weeks by 0.3 weeks.** It fits only by dropping kudos and the friends leaderboard, which weakens the "compare with friends" loop. It also has no push notifications, so no streak reminder, which may hurt the 40% second-ride target.
- **Not in the numbers:** your two spike rides in week 1, a paid Apple account on day 1 (free provisioning can't reach testers' iPhones), and store review waits. Starting the parallel work early could also cause rework.

### Context (injected)

<details><summary>show</summary>

Stop hook feedback:
Step 8 of pushing the work further: Lock. Open your first message with this line on its own, exactly: `▸ Step 8/8 · Lock`. Write that line nowhere else.

Make this cheap to repeat. Turn what worked into the smallest durable form: a script or spec that does the work, beside the deliverable, a short note in CLAUDE.md on how to run it and what proved it, and a project command if it will recur. Keep each tiny. End with the open decisions, each with options, for/against and your pick, and each decision and next check with an owner and date. The final stands alone for its reader and says each thing once, enough to act on: no process story, nothing it points to missing.

Then copy the deliverable as it stands to `.ambition/steps/8/`.

Then finish the run.

**Plan:** output the plan, covering where it serves the reader: the original ask and how the plan delivers it · goal beyond the goal · target · approach and instruments · assumptions tested · decisions with directions and for/against · borrowed methods · outside check · stretch target and the fallback · what will be locked in once it's built, ending with the open decisions, each decision and next check with an owner and date. The plan stands alone for its reader and says each thing once, enough to act on: no process story, nothing it points to missing. In plan mode, present it through the normal plan-approval step. Otherwise ask for approval.

**Report** with the following.
- **You asked for → it became:** one line each, plus how each part of the original ask was raised.
- **Against the first version:** where the final is better, anything it gave up, and what the check showed for both.
- **Outside check:** what ran, and what it returned.
- **Stretch:** the target, how far it got, and where it broke.
- **Locked in:** the files created, and how to rerun.
- **Assumptions made** (where the user said to use your judgement).
- **Decisions:** the most urgent ones left, each with directions, the arguments for and against, and which you'd pick.
- **Metrics** (skip if the user asked for none). As your last action, run the metrics command given with this step. Paste its output verbatim in a code block, without commentary.

If the user asked for a log, also write the full run to `.ambition/runs/<YYYY-MM-DD>-<slug>.md`: the restatement, every question and answer, every reviewer note, each step report, what each check returned, the final report and the metrics.

Run started: 2026-11-13T11:16:48Z
Metrics command for the end: python3 /plugin/scripts/ambition-metrics.py 08431a84-1759-442b-a364-db779bbb909f --since 2026-11-13T11:16:48Z

## Every step

- **Focus on this step.** Do this step's instruction in full, as if the user had just typed its command. Don't anticipate other steps or hold work back for them.
- **No look, no claim.** Whenever you change something people look at, read or use, perceive the result the way they will: render it at the sizes they use and look, read it through, use it. If you can't, get that access first (install a browser or a renderer). If you still can't, say the genre bar is unchecked and leave how it looks, reads or feels as the first version had it.
- **Look efficiently.** Every image you look at stays in this conversation and is re-read on every later turn. Look at a contact sheet (many frames or sizes in one image) rather than one image per frame, and take at most about three render-and-look rounds in a step. Keep working files (screenshots, scripts) under `.ambition/`, not in the deliverable.
- **Never trade the genre for a number.** A change must make the work better for the goal without making it worse as this kind of thing. If it does, undo it.
- **Reviewing.** If the user asked to review each step, end the step with its report and wait for their notes before you copy it. Their notes are steering, not answers.
- Respect the session's permission mode and the user's rules. Ambition never authorises skipping a confirmation the user requires.

</details>

### Assistant

▸ Step 8/8 · Lock

Mode is build, since the plan is a document. First I'll make the plan stand alone: move the canonical copy beside its tools, remove process-story phrasing, and replace the open-items list with decisions and checks that have owners and dates.

**→ Bash** `{"command": "cd \"<workspace>\" && cp /cfg/plans/make-a-plan-for-jaunty-wren.md PLAN.md && python3 -I - <<'EOF'\nimport re\np = 'PLAN.md'\ns = open(p).read()\ndef rep(old, new):\n    global s\n    assert s.count(old) == 1, old[:70]\n    s = s.replace(old, new)\n\nrep(\"A spike app is at `<workspace>/spike-gps/` (see its README).\", \"A spike app is in `spike-gps/` (see its README).\")\nrep(\"\"\"- … [6421 more chars]`

<details><summary>result</summary>

```
Traceback (most recent call last):
  File "<stdin>", line 61, in <module>
AssertionError: earlier
49/49 checks passed
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && cat > .ambition/lintwork/lock_edit.py <<'EOF'\np = 'PLAN.md'\ns = open(p).read()\ndef rep(old, new):\n    global s\n    assert s.count(old) == 1, old[:70]\n    s = s.replace(old, new)\n\nrep(\"A spike app is at `<workspace>/spike-gps/` (see its README).\", \"A spike app is in `spike-gps/` (see its README).\")\nrep(\"\"\"- **Dependency check:** `python3 -I \"<work … [6307 more chars]`

<details><summary>result</summary>

```
49/49 checks passed
```

</details>

### Assistant

Next, the durable pieces, each kept tiny: a self-test that proves the lint can fail, a short CLAUDE.md note, and a project command.

**→ Bash** `{"command": "cd \"<workspace>\" && cat > plan-tools/lint_selftest.py <<'EOF'\n#!/usr/bin/env python3\n\"\"\"Prove plan_lint.py can fail. Usage: python3 -I plan-tools/lint_selftest.py [PLAN.md]\nBaseline must pass; each deliberate breakage must make the lint exit non-zero.\"\"\"\nimport os, subprocess, sys, tempfile\nHERE = os.path.dirname(os.path.abspath(__file__))\nPLAN = sys.argv[1] if len(sys.a … [3328 more chars]`

<details><summary>result</summary>

```
selftest OK: baseline passes, 6 breakages all caught
.:
.
..
.ambition
.claude
CLAUDE.md
plan-tools
PLAN.md
spike-gps

.claude/commands:
.
..
check-plan.md

plan-tools:
__pycache__
.
..
check_tickets.py
lint_selftest.py
plan_lint.py
releases.py
sims

plan-tools/sims:
.
..
privacy_attack.py
privacy_attack2.py
quests.py
sizes.py
xp_rules.py
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && rm -rf plan-tools/__pycache__ && sed -i '' 's#(`/cfg/plans/make-a-plan-for-jaunty-wren.md`)#(`PLAN.md`, section 3)#' spike-gps/README.md && grep -n \"PLAN.md\" spike-gps/README.md | head -3 && cp PLAN.md /cfg/plans/make-a-plan-for-jaunty-wren.md && python3 -I plan-tools/plan_lint.py PLAN.md | tail -1 && python3 -I plan-tools/lint_selftest.py && rm -rf plan-tools/ … [242 more chars]`

<details><summary>result</summary>

```
4:section 3 of the plan (`PLAN.md`, section 3).
49/49 checks passed
selftest OK: baseline passes, 6 breakages all caught
copies identical
     482 PLAN.md
[This command modified 1 file you've previously read: ../../../cfg/plans/make-a-plan-for-jaunty-wren.md. Call Read before editing.]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && sed -i '' 's#section 3 of the plan (`PLAN.md`, section 3)#section 3 of `PLAN.md`#' spike-gps/README.md && sed -n '3,5p' spike-gps/README.md", "description": "Tidy redundant wording in spike README"}`

<details><summary>result</summary>

```
Goal: show whether Expo's background location holds up on a real ride. Pass criteria are in
section 3 of `PLAN.md`.
```

</details>

### Assistant

## Report

**You asked for → it became**
- **A plan for a React Native Expo social gamified cycling tracker, saved to disk → `PLAN.md`, a build blueprint a small team can start from.** It has 37 ordered tickets with sizes and acceptance criteria. The stack is settled with costs ($44 / $79 / $324 a month at 1k / 10k / 50k users). v1 is cut tight, with a reason for each deferral.
- **Raised:**
  - Social features are private by default.
  - Rewards never push riders toward speed or risk.
  - Weekly quests are personalised to each rider.
  - The plan has a stretch release train as well as the full v1.

**Against the first version**
- **Better on every part of the ask and the goal.** The first version was a 97-line outline with no sizes, acceptance criteria, costs or tests. The final is 482 lines.
- **What it gave up:** brevity. I added an "At a glance" block at the top to compensate. Clubs also moved out of v1, with a reason.
- **Check on both:** the lint passes 49 of 49 on the final and 9 of 36 on the first version. The first version fails mostly because the things it checks (tickets, costs, sizes) don't exist there.

**Outside check**
- `python3 -I plan-tools/plan_lint.py PLAN.md` returned 49/49.
- `python3 -I plan-tools/lint_selftest.py` returned: baseline passes, 6/6 deliberate breakages caught.
- The analyzer test passes, and the spike app typechecks against the real Expo packages.
- **Never run:** the spike app on a real phone, so recording reliability is still unverified.

**Stretch**
- **Target:** first real riders in 4 weeks, public launch in 8, against 13 weeks for the full v1.
- **How far it got:**
  - S1 hits 4.0 weeks with 4 developers, at zero margin. With 3 developers it's 5.0 weeks.
  - S2 misses 8 weeks: 8.3 weeks with 4 developers and 11.0 with 3.
  - Dropping kudos and the friends leaderboard brings S2 to 7.9 weeks.
- **Where it broke:** a day lost on the critical path costs about 1.4 calendar days. Recording taking twice as long gives 6.0 weeks for S1 whatever the team size. S2 also has no push notifications.

**Locked in** (all in `<workspace>`)
- **Plan:** `PLAN.md`, with an identical copy at `/cfg/plans/make-a-plan-for-jaunty-wren.md`.
- **Checks:** `plan-tools/plan_lint.py`, `check_tickets.py`, `releases.py` and `lint_selftest.py`.
- **Simulations:** `plan-tools/sims/`.
- **Spike:** `spike-gps/`.
- **Notes and command:** `CLAUDE.md` and `.claude/commands/check-plan.md`.
- **Rerun:** `python3 -I plan-tools/plan_lint.py PLAN.md`, or the `/check-plan` command.

**Assumptions made.** You didn't ask me to use my judgement, so I answered none of your questions myself. These are mine and are labelled as estimates in the plan:
- ticket sizes and the 70% focus factor
- the spike pass thresholds
- 8 rides per user per month
- the invented rider types
- day 1 as 2026-11-23

**Decisions** (all in §11 with owners and dates; the two most urgent):
- **Team size (3 or 4 developers), decide by 2026-11-20.** 3 developers is cheaper and lands S1 at 5 weeks and S2 at 11. 4 developers hits the stretch but with no slack. I'd pick 3 and commit to the longer dates.
- **Release shape, decide by 2026-11-20.** Shipping S1 then S2 gets riders and Google's 14-day test started early, but S2 has no push. One full v1 is simpler but takes 13 weeks to reach any user. I'd pick the S1 → S2 train.

The other four are:
- account type (D3)
- recording stack, decided by the spike (D4)
- minimum age (D5)
- monetisation (D6)

Each also has a pick in the plan.

**Metrics**

**→ Bash** `{"command": "python3 /plugin/scripts/ambition-metrics.py 08431a84-1759-442b-a364-db779bbb909f --since 2026-11-13T11:16:48Z", "description": "Run the ambition metrics command"}`

<details><summary>result</summary>

```
Metrics since 2026-11-13T11:16:48Z (cost: /cost, or total_cost_usd in headless JSON)
total   in 158 · out 136.0k (think 56.1k) · cache read 7.87M · write 204.6k · hit 97% · 71 calls
model   sonnet-5-5: in 158 · out 136.0k (think 56.1k) · cache read 7.87M · write 204.6k · hit 97% · 71 calls
```

</details>

### Assistant

```
Metrics since 2026-11-13T11:16:48Z (cost: /cost, or total_cost_usd in headless JSON)
total   in 158 · out 136.0k (think 56.1k) · cache read 7.87M · write 204.6k · hit 97% · 71 calls
model   sonnet-5-5: in 158 · out 136.0k (think 56.1k) · cache read 7.87M · write 204.6k · hit 97% · 71 calls
```
