# data/heat-pump · ambitious

### User

Work out whether switching from my gas boiler to a heat pump would save me money, as a Markdown file

**→ Bash** `{"command": "ls -la \"<workspace>\" | head -50"}`

<details><summary>result</summary>

```
total 1
drwx------@ 2 admin  staff  64 13 Nov 01:31 .
drwxr-xr-x  1 admin  staff   0  1 Jan  1970 ..
```

</details>

**→ Write** `{"file_path": "<workspace>/heat-pump-vs-gas-boiler.md", "content": "# Would a heat pump save me money versus my gas boiler?\n\n**Short answer: it depends mainly on two numbers, and I don't have yours.** Your folder had no bills or home details, so the figures below are an *illustrative example* with assumptions you should replace (UK-style prices in \u00a3, a typical semi-detached home). Section 4 … [5279 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/heat-pump-vs-gas-boiler.md (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

I wrote the analysis to `<workspace>/heat-pump-vs-gas-boiler.md`. It's based on assumed figures, because the folder had no bills or home details. The prices are rough UK estimates in £ and weren't looked up, so check them against current rates.

On those assumptions (12,000 kWh of gas a year, an 85%-efficient boiler, a typical semi-detached home):

- **Standard electricity tariff (25p/kWh):** running costs come out about even. A heat pump needs an efficiency (SCOP) of about 3.4 to break even. At a typical SCOP of 3.2 it costs about £40 a year more to run. Dropping the gas standing charge turns that into roughly £70 a year saved.
- **Heat-pump or time-of-use tariff (18p/kWh):** it saves about £180–£380 a year, depending on the heat pump's efficiency and whether you disconnect gas.
- **Payback:** about 15–20 years on running costs alone, after a £7,500 grant. It's shorter if your boiler is due for replacement anyway.

The file also has the break-even formula and a step-by-step way to rerun it with your own numbers.

For a real answer, I need:
- Your annual gas kWh.
- Your gas and electricity unit rates and the gas standing charge.
- Your country.
- Any installer quote, especially its predicted SCOP.

With those I can update the file.

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

**Plan or build.** If the user said plan or build, or plan mode is on, that decides it. Words like "plan", "design", "approach", "strategy", "proposal", "options" or a request for a document mean plan; imperatives like "build", "fix", "add", "make", "ship", or an approved plan to carry out, mean build. If it's unclear, make it your first question.

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

**→ Bash** `{"command": "cd \"<workspace>\" && mkdir -p .ambition/first && cp heat-pump-vs-gas-boiler.md .ambition/first/ && ls .ambition/first"}`

<details><summary>result</summary>

```
heat-pump-vs-gas-boiler.md
```

</details>

### Assistant

I've saved a copy of the file in `.ambition/first/`. There's no `.gitignore` in this folder, so I didn't change one.

Do you want to stop here or push it further?

- **Stop here:** keep the file as it is.
- **Push it further:** I'd go after three things.
  1. **Your own numbers.** I'd ask about your home, tariffs and any installer quote, then work out a real saving and payback instead of an illustrative one.
  2. **A runnable calculator.** This would be a small script or spreadsheet instead of hand-worked tables, with a sensitivity check on SCOP, tariff and price changes.
  3. **Checked prices and grants.** I'd look up current gas and electricity rates and grant rules instead of using my rough estimates.

  The cost is modest compared with what's been spent so far: a few short questions from me, then one or two more rounds of work.

### User

Push it further.

### Assistant

▸ Step 2/8 · Altitude

First question: what is this analysis for, and what should happen once it's done?

1. **Decide whether to get a heat pump.** You want a clear yes or no, based on your own house.
2. **Prepare for installer quotes.** You want to know what SCOP and tariff a quote needs to beat to be worth it.
3. **Compare with other options.** For example, replacing the boiler like-for-like, or adding solar or a battery.
4. **Something else.** Tell me what.

### User

Option 1: I want to decide whether to get a heat pump. I'd like a clear yes or no for my own house, with the reasoning behind it, so I can act on it rather than just have numbers. If it's close, tell me what would tip it either way.

### Assistant

Second question: what would make the result unmistakably excellent? Pick the closest, or describe your own.

1. **A firm verdict with a margin.** It says yes, no or too close, and states how confident it is. It also lists the 2–3 facts that would flip the answer, for example "yes if your quote's SCOP is 3.4 or higher".
2. **Verdict plus a plan.** It's the same as option 1, plus the next steps if the answer is yes (what to ask installers, which grant to apply for, which tariff to switch to).
3. **Verdict plus a 10–15 year cash-flow view.** It's the same as option 1, with cumulative cost against keeping the boiler, including boiler replacement and price scenarios.
4. **Something else.** Tell me what.

I'd also hold the file to a reading standard: one-page answer first, working underneath, no jargon without a plain explanation. Tell me if you'd weigh that differently.

### User

Option 3 is closest, but with the verdict first. I want a clear yes, no or too close, with how confident you are, and the few facts that would flip it. Then underneath, the 10–15 year cost comparison against keeping the boiler, including when the boiler would need replacing. I'm trying to decide whether to spend the money, so the long-run picture matters more than a to-do list.

Your reading standard is fine: a one-page answer first, working underneath, and plain explanations of any jargon.

### Assistant

Third question: what could check this other than me? Pick what you can get, or several.

1. **Your real bills and an installer quote.** I'd compare my modelled gas use against your actual meter readings. The quote's heat-loss figure and predicted SCOP would replace my assumptions.
2. **Published reference data.** This means the official Ofgem price cap and typical-use figures, and trial results from field studies of UK heat pumps. I'd check my numbers against these.
3. **A runnable model.** A script that recomputes every figure in the file from a single set of inputs. You could change an input and see the verdict move, and it would let me test the verdict against its own scenarios.
4. **Something else.** Tell me what.

I'd suggest 2 and 3 together, plus 1 if you can share your bills.

### User

I'd go with 2 and 3 together. Use the official Ofgem price cap figures and the UK field-trial results for heat pump efficiency, and give me a small script that recomputes every number in the Markdown file from one set of inputs, so I can change things like my gas use or electricity price and see whether the verdict changes. I don't have an installer quote yet, and I can't easily dig out my bills right now, so go with typical figures for a UK home and flag clearly which numbers are assumptions.

**→ ToolSearch** `{"query": "select:WebSearch,WebFetch", "max_results": 2}`

<details><summary>result</summary>

```


```

</details>

### Assistant

Web search and fetch are now available, so no access is missing. I'll fetch the Ofgem and field-trial figures once you've confirmed this.

```
You asked for:   Would switching from my gas boiler to a heat pump save me money, as a Markdown file
Raises all of:   - "Would it save money": a firm yes / no / too close verdict for a typical UK home,
                   with stated confidence, instead of a table of scenarios.
                 - "As a Markdown file": still one readable .md file, not an app or a spreadsheet.
Genre bar:       A decision memo a non-expert can act on. It leads with the answer on one page and
                 puts the working underneath. Jargon (SCOP, standing charge, flow temperature) is
                 explained in plain words. Assumptions are visibly flagged, and the reader can
                 trust it without a calculator.
Aiming at:       You deciding whether to spend the money, because the long-run picture
                 matters more than a to-do list.
Excellent means: 1. Page one: verdict (yes / no / too close), confidence, and the 2–3 facts that
                    would flip it, each with a threshold (e.g. "yes if SCOP ≥ X").
                 2. A 10–15 year cumulative cost comparison against keeping the boiler,
                    including when the boiler would need replacing, plus price scenarios.
                 3. Inputs from Ofgem's price cap and UK field-trial SCOP data, with sources
                    cited. Every assumption is labelled as one.
                 4. A small script that recomputes every number in the file from one set of
                    inputs, so changing gas use or electricity price shows whether the verdict
                    changes.
Proven by:       - The script regenerates every figure in the file with no mismatches.
                 - Inputs are cross-checked against the Ofgem cap and the field-trial results.
                 - The verdict is tested against its own scenarios, to show how stable it is.
                 - I read the final file through as a first-time reader, against the first
                   version. It must be at least as clear and readable as that version.
Needs access to: Web (now loaded). Not available: your bills or an installer quote, so typical
                 UK figures are used and flagged.
Mode:            build · answerer: you · reviewer: none (no step-by-step review requested)
```

Is this right? Reply "confirmed", or tell me what to change.

### User

Confirmed. One note: assume a typical 3-bed semi in England on the current Ofgem price cap, with an air-source heat pump costing about £7,500 after the Boiler Upgrade Scheme grant. Please keep it to a single .md file, with the verdict up top and the script's output pasted in at the bottom. Go ahead and finish without stopping.

**→ Bash** `{"command": "cd \"<workspace>\" && mkdir -p .ambition/steps/2 && cp heat-pump-vs-gas-boiler.md .ambition/steps/2/"}`

<details><summary>result</summary>

```
(Bash completed with no output)
```

</details>

**→ WebSearch** `{"query": "Ofgem energy price cap October to December 2026 unit rates electricity gas standing charge", "mode": "standard"}`

**→ WebSearch** `{"query": "Electrification of Heat demonstration project final report seasonal performance factor air source heat pumps median SPF", "mode": "standard"}`

<details><summary>result</summary>

```
Web search results for query: "Electrification of Heat demonstration project final report seasonal performance factor air source heat pumps median SPF"

Links: [{"title":"www.hvpmag.co.uk","url":"https://www.hvpmag.co.uk/Heat-pumps-three-times-more-efficient-than-gas-boilers-Electrification-of-Heat-interim-report-finds/16678"},{"title":"Heat pumps shown to be three times more efficient than gas boilers","url":"https://es.catapult.org.uk/news/heat-pumps-shown-to-be-three-times-more-efficient-than-gas-boilers/"},{"title":"Electrification of Heat Demonstration Report highlights improvement","url":"https://www.acrjournal.uk/heat-pumps/electrification-of-heat-demonstration-report-highlights-improvement"},{"title":"Improvement in Heat Pump Performance highlighted by new Electrification of Heat Demonstration Report","url":"https://heatpumps.org.uk/?p=7172"},{"title":"9050 eoh Interim insights from heat pump performance data","url":"https://doc.ukdataservice.ac.uk/doc/9050/mrdoc/pdf/9050_eoh_Interim_insights_from_heat_pump_performance_data.pdf"},{"title":"hvpmag.co.uk","url":"https://www.hvpmag.co.uk/Heat-pumps-can-perform-in-all-types-of-UK-homes/16820"},{"title":"CEC 500 2025 026","url":"https://www.energy.ca.gov/sites/default/files/2025-06/CEC-500-2025-026.pdf"},{"title":"heat pump performance highlighted by eoh report","url":"https://www.acr-news.com/heat-pump-performance-highlighted-by-eoh-report"},{"title":"Know what you want? Try our 'Supplier Directory'","url":"https://www.heatingandventilating.net/improvement-in-heat-pump-performance-highlighted-by-new-electrification-of-heat-demonstration-report"},{"title":"Improvement in Heat Pump Performance highlighted by new Electrification of Heat Demonstration Report","url":"https://prevbackup.hpauk.org.uk/?p=273"}]

The search turned up only interim results from the Electrification of Heat project, not a final report.

- **Median ASHP SPF:** The interim figure is about 2.80 (280%) observed in air source heat pump (ASHP) sys … [1633 more chars]
```

</details>

<details><summary>result</summary>

```
Web search results for query: "Ofgem energy price cap October to December 2026 unit rates electricity gas standing charge"

Links: [{"title":"Energy price cap unit rates and standing charges","url":"https://www.ofgem.gov.uk/node/176588/"},{"title":"Energy price cap unit rates and standing charges","url":"https://ofgem.gov.uk/your-energy-supply/your-energy-bill/energy-price-cap-unit-rates-and-standing-charges"},{"title":"energy price cap october 2026","url":"https://www.edfenergy.com/energywise/energy-price-cap-october-2026"},{"title":"Energy Price Cap 2026: Latest Ofgem Rates & History","url":"https://heatable.co.uk/boiler-advice/history-of-ofgems-energy-price-cap"},{"title":"Changes to energy price cap between 1 October and 31 December 2026","url":"https://ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026"},{"title":"Changes to energy price cap between 1 October and 31 December 2026","url":"https://www.ofgem.gov.uk/publications/changes-energy-price-cap-between-1-october-and-31-december-2026"},{"title":"www.edfenergy.com","url":"https://www.edfenergy.com/node/124019"},{"title":"Energy price cap October 2026: Ofgem confirms 4% increase","url":"https://www.uswitch.com/gas-electricity/news/october-energy-price-cap-to-increase-by-four-percent/"},{"title":"Summary of changes to energy price cap 1 October to 31 December 2026","url":"https://www.ofgem.gov.uk/sites/default/files/2026-08/Summary-of-changes-to-energy-price-cap-1-October-to-31-December-2026.pdf"},{"title":"moneytothemasses.com","url":"https://moneytothemasses.com/?p=139438"},{"title":"Energy price cap will rise by 4% from October 2026","url":"https://ofgem.gov.uk/press-release/energy-price-cap-will-rise-4-october-2026"},{"title":"132 what is the energy price cap","url":"https://www.eonnext.com/blog/132-what-is-the-energy-price-cap"},{"title":"october 2026 energy price cap should i fix my tariff","url":"https://octopus.energy/blog/october-2026-energy-price-cap-should-i-fix-my-tar … [2535 more chars]
```

</details>

**→ WebFetch** `{"url": "https://www.ofgem.gov.uk/energy-advice-for-household-consumers/energy-price-cap-unit-rates-and-standing-charges", "prompt": "Give the 1 Oct-31 Dec 2026 energy price cap national average (England, Scotland, Wales) Direct Debit electricity and gas unit rates and standing charges, and England-specific if shown. Also Ofgem typical consumption values (kWh gas and electricity)."}`

<details><summary>result</summary>

```
The server returned HTTP 404 Not Found.

The response body was not retrieved. If this URL requires authentication, use an authenticated tool (e.g. `gh` for GitHub, or an MCP-provided fetch tool) instead of WebFetch.
```

</details>

**→ WebFetch** `{"url": "https://es.catapult.org.uk/news/heat-pumps-shown-to-be-three-times-more-efficient-than-gas-boilers/", "prompt": "Report the median SPF for air source heat pumps, range/quartiles, sample size, and what SPF boundary (SPFH2/H4) was used. Also any comment on running costs vs gas."}`

**→ WebSearch** `{"query": "Nesta heat pump monitoring 2025 median SCOP air source heat pump running cost vs gas boiler Octopus Cosy tariff", "mode": "standard"}`

**→ WebSearch** `{"query": "Boiler Upgrade Scheme grant \u00a37,500 air source heat pump England 2026 extended", "mode": "standard"}`

<details><summary>result</summary>

```
**Median SPF for air source heat pumps (ASHPs):** 2.80 (280%). The page says this is up about 0.3 to 0.4 since the 2011–2014 RHPP trial.

**Range/quartiles:** Not reported. The page says performance variation "remains high" but gives no figures.

**Sample size:** Not specified for the SPF result. The project installed 742 heat pumps in total, across all types, and the page doesn't give the ASHP-only count.

**SPF boundary:** SPFH4. The page's footnote says it accounts for electricity used by and heat produced by the heat pump, immersion heater, back-up heater, and circulation pump. SPFH2 isn't mentioned.

**Running costs vs. gas:** The page gives no running cost figures in pounds or any cost comparison. Its only gas comparison is efficiency. Energy Systems Catapult says heat pumps are "three times more efficient than gas boilers," but that is an efficiency claim, not a cost one. Hybrid systems were set to run cost-optimally, switching to whichever option was cheapest at a given time, but the page doesn't report the resulting costs.
```

</details>

<details><summary>result</summary>

```
Web search results for query: "Boiler Upgrade Scheme grant £7,500 air source heat pump England 2026 extended"

Links: [{"title":"Somerset Council","url":"https://content.govdelivery.com/landing_pages/54128/96ab4703d642451fb0e2e37cb9fe543c"},{"title":"Boiler Upgrade Scheme 2026: What's Changing for Installers and Grant Claims","url":"https://www.autarc.energy/wissen/boiler-upgrade-scheme-2026-installers"},{"title":"airqualitynews.com","url":"https://airqualitynews.com/?p=47636"},{"title":"Air source heat pump: government expands grants to pump tech that heats, cools - and cuts installation costs","url":"https://www.yorkshirepost.co.uk/business/consumer/air-source-heat-pump-government-grants-installation-costs-5405844"},{"title":"Air source heat pump: government expands grants to pump tech that heats, cools - and cuts installation costs","url":"https://www.thestar.co.uk/business/consumer/air-source-heat-pump-government-grants-installation-costs-5405844"},{"title":"Air source heat pump: government expands grants to pump tech that heats, cools - and cuts installation costs","url":"https://www.yorkshireeveningpost.co.uk/business/consumer/air-source-heat-pump-government-grants-installation-costs-5405844"},{"title":"heat pump grant extra 120m vouchers open until april 2027","url":"https://selectra.co.uk/energy/news/heat-pump-grant-extra-120m-vouchers-open-until-april-2027"},{"title":"Boiler Upgrade Scheme","url":"https://www.hart.gov.uk/index%2ephp/home-grants/boiler-upgrade-scheme"},{"title":"Boiler Upgrade Scheme","url":"https://www.augustapp.com/dictionary/boiler-upgrade-scheme"},{"title":"jameswild.org.uk","url":"https://jameswild.org.uk/node/2067"},{"title":"Increased government heat pump grants mean families can save on heating costs by choosing heat pumps over gas boilers","url":"https://www.pbctoday.co.uk/news/energy-news/heat-pump-grants-up-50-uk/133730/"},{"title":"www.hvpmag.co.uk","url":"https://www.hvpmag.co.uk/Boiler-Upgrade-Scheme-grants-increase-by-50-per-c … [2546 more chars]
```

</details>

<details><summary>result</summary>

```
Web search results for query: "Nesta heat pump monitoring 2025 median SCOP air source heat pump running cost vs gas boiler Octopus Cosy tariff"

Links: [{"title":"About Nesta","url":"https://www.nesta.org.uk/report/how-to-make-heat-pumps-more-affordable/scenario-1-high-innovation/"},{"title":"About Nesta","url":"https://www.nesta.org.uk/report/how-to-make-heat-pumps-more-affordable/scenario-3-high-subsidy/"},{"title":"How much difference do the different factors make?","url":"https://nesta.org.uk/report/how-to-make-heat-pumps-more-affordable/how-much-difference-do-the-different-factors-make"},{"title":"heat pump running cost oct23","url":"https://octopus.energy/blog/heat-pump-running-cost-oct23/"},{"title":"About Nesta","url":"https://www.nesta.org.uk/report/how-to-make-heat-pumps-more-affordable/scenario-2-cheaper-electricity/"},{"title":"heat pump run cost savings","url":"https://octopus.energy/blog/heat-pump-run-cost-savings/"},{"title":"About Nesta","url":"https://www.nesta.org.uk/feature/energy-affordability/establish-price-ratio-target/"},{"title":"About Nesta","url":"https://nesta.org.uk/report/how-the-energy-crisis-affects-the-case-for-heat-pumps/full"},{"title":"About Nesta","url":"https://www.nesta.org.uk/report/how-the-energy-crisis-affects-the-case-for-heat-pumps/how-the-costs-of-heat-pumps-compare-to-gas-boilers-since-the-energy-crisis-2/"},{"title":"heat pump running cost july23","url":"https://octopus.energy/blog/heat-pump-running-cost-july23"},{"title":"• Home Home","url":"https://www.thecooldown.com/?p=823489"},{"title":"About Nesta","url":"https://www.nesta.org.uk/report/how-to-make-heat-pumps-more-affordable/assumptions-and-methods/"},{"title":"etkhpcorderapi.extweb.sp.se","url":"https://etkhpcorderapi.extweb.sp.se/api/file/3225"},{"title":"About Nesta","url":"https://www.nesta.org.uk/report/how-to-make-heat-pumps-more-affordable/"},{"title":"factcheck what it really costs to heat a home in the uk with a heat pump","url":"https://www.carbonbrief.o … [1937 more chars]
```

</details>

**→ WebFetch** `{"url": "https://www.ofgem.gov.uk/node/176588/", "prompt": "Give the 1 Oct-31 Dec 2026 price cap electricity and gas unit rates (p/kWh) and standing charges (p/day) for England average / Direct Debit, and say whether VAT is included. Also typical consumption values."}`

<details><summary>result</summary>

```
**Average Direct Debit prices, 1 October to 31 December 2026:**

- **Electricity:** 26.32 p/kWh unit rate and 54.83 p/day standing charge
- **Gas:** 7.97 p/kWh unit rate and 29.68 p/day standing charge

**VAT:** Gas prices include 5% VAT. Electricity has no VAT from 1 October 2026 to 31 March 2027, as the page notes that "Figures are rounded to two decimal places and include 5% VAT on gas."

**Note on "England":** The page says the average figure is based on people paying by Direct Debit "in England, Scotland and Wales." It is not an England-only figure. The England-specific regional rates are in the Direct Debit table on the page, which doesn't show its data in this content.

**Typical consumption values:** The page doesn't include them.
```

</details>

**→ WebSearch** `{"query": "Octopus Cosy tariff rates 2026 p/kWh cheap rate peak standard average heat pump", "mode": "standard"}`

**→ WebSearch** `{"query": "Ofgem typical domestic consumption values 2026 gas 11,500 kWh electricity 2,700 kWh medium", "mode": "standard"}`

<details><summary>result</summary>

```
Web search results for query: "Ofgem typical domestic consumption values 2026 gas 11,500 kWh electricity 2,700 kWh medium"

Links: [{"title":"Energy UK Explains Typical Domestic Consumption Values","url":"https://www.energy-uk.org.uk/wp-content/uploads/2026/05/Energy-UK-Explains-Typical-Domestic-Consumption-Values.pdf"},{"title":"Summary of changes to energy price cap 1 July to 30 September 2026 revised TDCV","url":"https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026-revised-TDCV.pdf"},{"title":"27 May 2026","url":"https://www.energy-uk.org.uk/publications/energy-uk-explains-typical-domestic-consumption-values-2/"},{"title":"Summary of changes to energy price cap 1 July to 30 September 2026","url":"https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026.pdf"},{"title":"Summary of changes to energy price cap 1 July to 30 September 2026","url":"https://www.ofgem.gov.uk/sites/default/files/2026-05/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026.pdf"},{"title":"Summary of changes to energy price cap 1 January to 31 March 2026","url":"https://www.ofgem.gov.uk/sites/default/files/2025-11/Summary-of-changes-to-energy-price-cap-1-January-to-31-March-2026.pdf"},{"title":"Summary of changes to energy price cap 1 October to 31 December 2026","url":"https://www.ofgem.gov.uk/sites/default/files/2026-08/Summary-of-changes-to-energy-price-cap-1-October-to-31-December-2026.pdf"},{"title":"www.cornwall insight","url":"https://www.cornwall-insight.com/?p=11765"},{"title":"Energy Price Cap Details","url":"https://blog.theenergyshop.com/articles/energy-price-cap"},{"title":"Energy UK Review of typical domestic consumption values response 20 April 2026","url":"https://www.energy-uk.org.uk/wp-content/uploads/2026/05/Energy-UK-Review-of-typical-domestic-consumption-values-response-20-April-2026.pdf"},{"title":"Summary of changes to energy p … [3167 more chars]
```

</details>

<details><summary>result</summary>

```
Web search results for query: "Octopus Cosy tariff rates 2026 p/kWh cheap rate peak standard average heat pump"

Links: [{"title":"Octopus Cosy Heat Pump Fleet Performance Dashboard","url":"https://octopus.energy/cosy-heat-pump-performance"},{"title":"Best Electricity Tariffs for Heat Pumps (UK)","url":"https://heatpumpmath.pages.dev/heat-pump-electricity-tariffs"},{"title":"octopus intelligent go vs cosy vs agile 2026","url":"https://electrical-london.pages.dev/blog/octopus-intelligent-go-vs-cosy-vs-agile-2026"},{"title":"In this article","url":"https://chargecostlab.pages.dev/blog/heat-pump-plus-ev-home-energy-cost-savings-2026"},{"title":"46267 best electric tariff now that ovo are ending the heat pump plus in february 2026","url":"https://forum.buildhub.org.uk/topic/46267-best-electric-tariff-now-that-ovo-are-ending-the-heat-pump-plus-in-february-2026"},{"title":"Octopus Energy launches new off peak rate for heat pump customers","url":"https://octopus.energy/press/Octopus-Energy-launches-new-off-peak-rate-for-heat-pump-customers/"},{"title":"Book a demo","url":"https://reonic.com/en-gb/blog/heat-pump-tariff-uk/"},{"title":"Octopus Energy tariffs August 2026 — every deal, ranked","url":"https://www.energyplus.co.uk/suppliers/octopus-energy/tariffs"},{"title":"๐Ÿ™ MontyGroup","url":"https://montygroup-astro.pages.dev/energy-providers"},{"title":"heat pump running costs vs gas","url":"https://bristolheatpump.pages.dev/blog/heat-pump-running-costs-vs-gas"},{"title":"Octopus Cosy tariff review (UK, 2026): is it worth it?","url":"https://www.energyplus.co.uk/costsavingadvice/octopus-cosy-tariff-review-uk-2026"},{"title":"99 of octopus cosy heat pump owners pay less to heat their homes than they would with gas","url":"https://octopus.energy/press/more-news-press-releases/99-of-octopus-cosy-heat-pump-owners-pay-less-to-heat-their-homes-than-they-would-with-gas/"},{"title":"Best heat pump electricity tariff in the UK — August 2026","url":"https://www.energyplus.co.uk/gu … [2207 more chars]
```

</details>

**→ Write** `{"file_path": "<workspace>/heatpump_model.py", "content": "#!/usr/bin/env python3\n\"\"\"Heat pump vs gas boiler: 15-year cost model for a typical English 3-bed semi.\n\nEvery number in heat-pump-vs-gas-boiler.md is produced by this script.\n\n  python3 heatpump_model.py                          print the summary\n  python3 heatpump_model.py --set gas_kwh=12000      change any input (repeatable)\n … [24261 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/heatpump_model.py (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

I've written the model script. Next I'll run it to see the numbers.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I heatpump_model.py"}`

<details><summary>result</summary>

```
VERDICT: NO on a standard tariff; TOO CLOSE on a heat-pump tariff
CONFIDENCE: Moderate (89% of 54 stress scenarios agree)
Check: Ofgem typical-use bill from these prices = £1,724 (Ofgem published £1,723)
Useful heat needed per year: 7,735 kWh
Year-1 running cost, keep boiler (incl. service, gas standing charge): £965
Year-1 running cost, heat pump on standard tariff:  £894  (saving +£71)
Year-1 running cost, heat pump on heat-pump tariff: £731  (saving +£234)
15-year position vs keeping boiler (positive = heat pump cheaper):
  standard tariff    -£3,327 cash,  -£4,082 in today's money; does not break even
  heat-pump tariff     -£296 cash,  -£1,798 in today's money; does not break even
Break-even thresholds (heat pump = boiler over the period):
  SCOP needed, standard tariff: 4.07
  SCOP needed, heat-pump tariff: 3.10
  Heat-pump tariff price needed at SCOP 3.0: 19.4p/kWh
  Net heat pump cost needed, standard tariff: £4,173; heat-pump tariff: £7,204
  Gas use needed, standard tariff: n/a
  Gas use needed, heat-pump tariff: 10,255 kWh/yr
Stress test (54 scenarios: SCOP 2.6-3.6 x 3 price paths x boiler due in 1/5/10 yrs):
  heat pump cheaper in 6 on standard tariff, 27 on heat-pump tariff
Sensitivity (advantage over the period, standard tariff | heat-pump tariff):
  Base case                                                       -£3,327 |    -£296
  Heat pump efficiency poor (SCOP 2.6)                            -£5,269 |  -£1,772
  Heat pump efficiency good (SCOP 3.5)                            -£1,524 |  +£1,074
  Heat pump efficiency excellent (SCOP 4.0)                         -£172 |  +£2,101
  Home uses more gas (12,000 kWh)                                 -£3,179 |    +£685
  Home uses less gas (7,500 kWh)                                  -£3,445 |  -£1,081
  Boiler dies now (replace in year 0)                             -£3,458 |    -£427
  Boiler lasts 10 more years                                      -£3,175 |    -£144
  Heat pump costs £9,000 net          … [472 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\nimport re\ns=open('heatpump_model.py').read()\ns=s.replace('''    \"horizon\": (15,''','''    \"boiler_life\": (15, \"Boiler lifespan (years)\", \"ASSUMPTION\", \"Used to credit remaining life at the end of the period.\"),\n    \"hp_life\": (18, \"Heat pump lifespan (years)\", \"ASSUMPTION\", \"Typically quoted as 15-20 years.\"),\n    \"horizo … [1400 more chars]`

<details><summary>result</summary>

```
VERDICT: NO on a standard tariff; TOO CLOSE on a heat-pump tariff
CONFIDENCE: Moderate (89% of 54 stress scenarios agree)
Check: Ofgem typical-use bill from these prices = £1,724 (Ofgem published £1,723)
Useful heat needed per year: 7,735 kWh
Year-1 running cost, keep boiler (incl. service, gas standing charge): £965
Year-1 running cost, heat pump on standard tariff:  £894  (saving +£71)
Year-1 running cost, heat pump on heat-pump tariff: £731  (saving +£234)
15-year position vs keeping boiler (positive = heat pump cheaper):
  standard tariff    -£3,077 cash,  -£3,932 in today's money; does not break even
  heat-pump tariff      -£46 cash,  -£1,649 in today's money; does not break even
Break-even thresholds (heat pump = boiler over the period):
  SCOP needed, standard tariff: 3.97
  SCOP needed, heat-pump tariff: 3.01
  Heat-pump tariff price needed at SCOP 3.0: 19.9p/kWh
  Net heat pump cost needed, standard tariff: £4,423; heat-pump tariff: £7,454
  Gas use needed, standard tariff: n/a
  Gas use needed, heat-pump tariff: 9,618 kWh/yr
Stress test (54 scenarios: SCOP 2.6-3.6 x 3 price paths x boiler due in 1/5/10 yrs):
  heat pump cheaper in 6 on standard tariff, 27 on heat-pump tariff
Sensitivity (advantage over the period, standard tariff | heat-pump tariff):
  Base case                                                       -£3,077 |     -£46
  Heat pump efficiency poor (SCOP 2.6)                            -£5,019 |  -£1,522
  Heat pump efficiency good (SCOP 3.5)                            -£1,274 |  +£1,324
  Heat pump efficiency excellent (SCOP 4.0)                          +£78 |  +£2,351
  Home uses more gas (12,000 kWh)                                 -£2,929 |    +£935
  Home uses less gas (7,500 kWh)                                  -£3,195 |    -£831
  Boiler dies now (replace in year 0)                             -£2,208 |    +£823
  Boiler lasts 10 more years                                      -£3,925 |    -£894
  Boiler never needs replacing in the  … [556 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I heatpump_model.py --write heat-pump-vs-gas-boiler.md && python3 -I heatpump_model.py --check heat-pump-vs-gas-boiler.md && python3 -I heatpump_model.py --set gas_kwh=12000 --check heat-pump-vs-gas-boiler.md; sed -n 1,60p heat-pump-vs-gas-boiler.md"}`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
MISMATCH: regenerate with --write (using the same --set options)
# Should I swap my gas boiler for a heat pump?

*Typical English 3-bed semi on the Ofgem price cap (Oct-Dec 2026). Prices and efficiency come from the sources at the bottom; everything else is a flagged assumption. Every figure below is generated by `heatpump_model.py`, so you can change an input and regenerate the file (see 'Re-run it').*

## The answer

> **Verdict: NO on a standard tariff; TOO CLOSE on a heat-pump tariff**  
> **Confidence: Moderate (89% of 54 stress scenarios agree)**

- **Over 15 years, a heat pump on a standard tariff ends up £3,077 worse off than keeping a gas boiler** (-£3,932 in today's money). On a heat-pump tariff the gap is -£46 (-£1,649 in today's money).
- **Running costs are not the problem; the up-front cost is.** In year 1 the heat pump saves +£71 on a standard tariff or +£234 on a heat-pump tariff, but you pay £7,500 after the grant. Keeping the boiler means paying £3,000 for a new one in year 5, which narrows the gap but doesn't close it.
- **The main reason it's close at all:** electricity costs 3.3x as much per kWh as gas, and a heat pump only makes back about 3.0x as much heat per kWh of electricity.

### What would flip it

| If... | Today's assumption | It becomes a clear 'yes' (or close to it) when... |
|---|---|---|
| Your installer's **predicted SCOP** (efficiency) is higher | 3.0 | 3.97 on a standard tariff, 3.01 on a heat-pump tariff |
| You get a **cheaper electricity tariff** for heating | 26.3p standard; 20p assumed heat-pump tariff | 19.9p/kWh blended or lower, at SCOP 3.0 |
| The **installed price** is lower | £7,500 | £4,423 (standard tariff) or £7,454 (heat-pump tariff) |
| Your home uses more **gas** | 9,500 kWh/yr | never (within the modelled range) (standard tariff), 9,618 kWh/yr (heat-pump tariff) |
| Your **boiler is failing soon** | replaced in year 5 | see 'Boiler dies now' in the sen … [2455 more chars]
```

</details>

### Assistant

The report matches the model, and the check correctly fails when inputs differ. I'll tidy the page-one wording next: sign handling, a clearer bottom line, and the clumsy "never" cell.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert a in s, a[:50]\n    s=s.replace(a,b)\nrep('''    o.append(f\"- **Over {H} years, a heat pump on a standard tariff ends up {money(abs(c['adv']))} \"\n             f\"{'better off' if c['adv'] > 0 else 'worse off'} than keeping a gas boiler** \"\n             f\"({money(c … [3838 more chars]`

<details><summary>result</summary>

```
Traceback (most recent call last):
  File "<stdin>", line 26, in <module>
  File "<stdin>", line 4, in rep
AssertionError: "It becomes a clear 'yes' (or close to it) when...
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
# Should I swap my gas boiler for a heat pump?

*Typical English 3-bed semi on the Ofgem price cap (Oct-Dec 2026). Prices and efficiency come from the sources at the bottom; everything else is a flagged assumption. Every figure below is generated by `heatpump_model.py`, so you can change an input and regenerate the file (see 'Re-run it').*

## The answer

> **Verdict: NO on a standard tariff; TOO CLOSE on a heat-pump tariff**  
> **Confidence: Moderate (89% of 54 stress scenarios agree)**

- **Over 15 years, a heat pump on a standard tariff ends up £3,077 worse off than keeping a gas boiler** (-£3,932 in today's money). On a heat-pump tariff the gap is -£46 (-£1,649 in today's money).
- **Running costs are not the problem; the up-front cost is.** In year 1 the heat pump saves +£71 on a standard tariff or +£234 on a heat-pump tariff, but you pay £7,500 after the grant. Keeping the boiler means paying £3,000 for a new one in year 5, which narrows the gap but doesn't close it.
- **The main reason it's close at all:** electricity costs 3.3x as much per kWh as gas, and a heat pump only makes back about 3.0x as much heat per kWh of electricity.

### What would flip it

| If... | Today's assumption | It becomes a clear 'yes' (or close to it) when... |
|---|---|---|
| Your installer's **predicted SCOP** (efficiency) is higher | 3.0 | 3.97 on a standard tariff, 3.01 on a heat-pump tariff |
| You get a **cheaper electricity tariff** for heating | 26.3p standard; 20p assumed heat-pump tariff | 19.9p/kWh blended or lower, at SCOP 3.0 |
| The **installed price** is lower | £7,500 | £4,423 (standard tariff) or £7,454 (heat-pump tariff) |
| Your home uses more **gas** | 9,500 kWh/yr | never (within the modelled range) (standard tariff), 9,618 kWh/yr ( … [8426 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert a in s, a[:60]\n    s=s.replace(a,b)\nrep('''    o.append(f\"- **Over {H} years, a heat pump on a standard tariff ends up {money(abs(c['adv']))} \"\n             f\"{'better off' if c['adv'] > 0 else 'worse off'} than keeping a gas boiler** \"\n             f\"({money(c … [4411 more chars]`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
# Should I swap my gas boiler for a heat pump?

*Typical English 3-bed semi on the Ofgem price cap (Oct-Dec 2026). Prices and efficiency come from the sources at the bottom; everything else is a flagged assumption. Every figure below is generated by `heatpump_model.py`, so you can change an input and regenerate the file (see 'Re-run it').*

## The answer

> **Verdict: NO on a standard tariff; TOO CLOSE on a heat-pump tariff**  
> **Confidence: Moderate (89% of 54 stress scenarios agree)**

- **Bottom line:** don't do it just to save money on a standard tariff. On a heat-pump tariff it roughly breaks even, so it comes down to the efficiency your installer predicts and whether you value the non-financial benefits.
- **Over 15 years, a heat pump on a standard tariff leaves you £3,077 worse off than keeping a gas boiler** (£3,932 worse off in today's money). On a heat-pump tariff you'd be £46 worse off (£1,649 worse off in today's money).
- **Running costs barely differ; the up-front cost is what decides it.** In year 1 the heat pump's bills are £71 lower on a standard tariff or £234 lower on a heat-pump tariff, but you pay £7,500 after the grant. Keeping the boiler means paying £3,000 for a new one in year 5, which narrows the gap but doesn't close it.
- **Why bills are so similar:** a kWh of heat costs about 9.4p from your gas boiler and 8.8p from a heat pump at SCOP 3.0 on the standard tariff. Electricity costs 3.3x as much per kWh as gas, which cancels out most of the heat pump's efficiency.

### What would flip it

| If... | Today's assumption | The heat pump breaks even over the period when... |
|---|---|---|
| Your installer's **predicted SCOP** (efficiency) is higher | 3.0 | 3.97 on a standard tariff, 3.01 on a heat-pump tariff |
| You get a **cheaper electricity tariff** for heating | 26.3p standard; 20p assumed heat-pump tariff | 19.9p/kWh blended or lower, at SCOP 3.0 |
| The **installed price** is l … [425 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I heatpump_model.py --set scop=4.2 --set gas_kwh=13000 | head -9; python3 -I heatpump_model.py --check heat-pump-vs-gas-boiler.md; diff -q heat-pump-vs-gas-boiler.md .ambition/first/heat-pump-vs-gas-boiler.md"}`

<details><summary>result</summary>

```
VERDICT: YES
CONFIDENCE: Low (24% of 54 stress scenarios agree)
Check: Ofgem typical-use bill from these prices = £1,724 (Ofgem published £1,723)
Useful heat needed per year: 10,710 kWh
Year-1 running cost, keep boiler (incl. service, gas standing charge): £1,244
Year-1 running cost, heat pump on standard tariff:  £887  (saving +£357)
Year-1 running cost, heat pump on heat-pump tariff: £726  (saving +£519)
15-year position vs keeping boiler (positive = heat pump cheaper):
  standard tariff    +£2,124 cash,      -£7 in today's money; breaks even in year 12
OK: file matches the model
Files heat-pump-vs-gas-boiler.md and .ambition/first/heat-pump-vs-gas-boiler.md differ
```

</details>

### Assistant

The stress grid used fixed SCOP values. If you changed your SCOP, the confidence figure would measure the wrong thing. I'll centre the grid on your own inputs.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b,n=1):\n    global s\n    assert s.count(a)==n,(a[:50],s.count(a))\n    s=s.replace(a,b)\nrep(\"STRESS_SCOPS = [2.6, 2.8, 3.0, 3.2, 3.4, 3.6]\",\"STRESS_SCOP_OFFSETS = [-0.4, -0.2, 0.0, 0.2, 0.4, 0.6]  # around your own SCOP input\")\nrep(\"    for s in STRESS_SCOPS:\\n\",\"    for s in [p['scop']  … [356 more chars]`

<details><summary>result</summary>

```
Traceback (most recent call last):
  File "<stdin>", line 8, in <module>
  File "<stdin>", line 4, in rep
AssertionError: ('(SCOP 2.6-3.6 x 3 price paths', 0)
214:    L.append(f"Stress test ({s['cap'][1]} scenarios: SCOP 2.6-3.6 x 3 price paths x boiler due in 1/5/10 yrs):")
302:    o.append(f"\n**Stress test:** I ran {s['cap'][1]} combinations (SCOP from 2.6 to 3.6, three fuel-price paths, boiler replacement due in year 1, 5 or 10). "
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:50],s.count(a))\n    s=s.replace(a,b)\nrep(\"STRESS_SCOPS = [2.6, 2.8, 3.0, 3.2, 3.4, 3.6]\",\"STRESS_SCOP_OFFSETS = [-0.4, -0.2, 0.0, 0.2, 0.4, 0.6]  # around your own SCOP input\")\nrep(\"    for s in STRESS_SCOPS:\\n\",\"    for s in [p['scop'] + d  … [602 more chars]`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
VERDICT: YES
CONFIDENCE: Moderate (81% of 54 stress scenarios agree)
8:> **Confidence: Moderate (89% of 54 stress scenarios agree)**
67:**Stress test:** I ran 54 combinations (SCOP from 2.6 to 3.6, three fuel-price paths, boiler replacement due in year 1, 5 or 10). The heat pump finished cheaper in **6** of them on a standard tariff and **27** on a heat-pump tariff. This is a spread of possibilities, not a probability.
137:CONFIDENCE: Moderate (89% of 54 stress scenarios agree)
153:Stress test (54 scenarios: SCOP 2.6-3.6 x 3 price paths x boiler due in 1/5/10 yrs):
[This command modified 2 files you've previously read: heat-pump-vs-gas-boiler.md, heatpump_model.py. Call Read before editing.]
```

</details>

### Assistant

The heat pump doesn't pay for itself on the standard price cap, and on a heat-pump tariff it's too close to call. It's written up in `<workspace>/heat-pump-vs-gas-boiler.md`, with the verdict at the top. The model behind it is `heatpump_model.py` in the same folder, and the script's output is pasted at the bottom of the Markdown file, as you asked.

**Verdict:** on a standard tariff the answer is no, with moderate confidence. The heat pump finished cheaper in 6 of 54 stress scenarios, so 89% agree on "no". On a heat-pump tariff it's too close: after 15 years it's £46 worse off. Most of the cost is the up-front £7,500, which is why it doesn't pay back. In year 1 the heat pump's running costs are only £71 lower than the boiler's on a standard tariff, or £234 lower on a heat-pump tariff.

**Over 15 years** (heat pump installed now, versus keeping the boiler and replacing it in year 5):

| Tariff | Heat pump vs keeping the boiler |
|---|---|
| Standard (price cap) | £3,077 worse off |
| Heat-pump tariff | £46 worse off |

**What would flip it**, each worked out in the file:
- **Efficiency (SCOP):** a predicted SCOP of about 4.0 on a standard tariff, or about 3.0 on a heat-pump tariff.
- **Electricity price:** a heat-pump tariff blended at 19.9p/kWh or lower.
- **Boiler:** a boiler that fails soon tips a heat-pump tariff to about £820 ahead. A boiler that never needs replacing in the period makes it worse.
- **Gas use:** 12,000 kWh a year instead of 9,500, on a heat-pump tariff, makes it about £940 ahead.

**Checks:**
- **Ofgem bill:** the Ofgem prices and typical use reproduce Ofgem's published £1,723 typical bill to within £1.
- **Regeneration:** `--set` changes any input, `--write` rebuilds the file, and `--check` confirms the file matches the model. Changing the inputs does change the verdict.

**Which numbers are assumptions:** they're flagged in the file's assumptions table. The main ones are:
- A SCOP of 3.0, a 20p blended heat-pump tariff, and a £3,000 replacement boiler.
- The boiler's age, and service costs.
- Both fuels rising 3% a year.

I used 9,500 kWh of gas a year, which is Ofgem's new typical figure, so it may understate a 3-bed semi. I took that figure from Energy UK's summary, not Ofgem's own page, which I couldn't open.

**What I couldn't confirm:**
- **Electricity VAT:** Ofgem's page lists no VAT on electricity until March 2027, and I couldn't find what happens after. The base case ignores a return of VAT, and one sensitivity row models it.
- **Efficiency data:** the 2.8 median is from interim results of the Electrification of Heat trial, because I found no final report.
- **Grant end date:** I didn't confirm when the grant ends.

Your first version is untouched in `.ambition/first/`, as the hook asked. The other pipeline steps (depth, challenge, range and so on) aren't run, since you asked me to finish in one go.

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

First I'll re-read the current code so the edits land exactly.

**→ Bash** `{"command": "cd \"<workspace>\" && grep -n \"STRESS\\|stress\\|SENS\\|^def \\|^import\\|VERDICT_BAND\" heatpump_model.py"}`

<details><summary>result</summary>

```
14:import sys
53:STRESS_SCOP_OFFSETS = [-0.4, -0.2, 0.0, 0.2, 0.4, 0.6]  # around your own SCOP input
54:STRESS_PRICES = [(0.03, 0.03), (0.04, 0.02), (0.02, 0.04)]  # (gas, electricity) yearly rise
55:STRESS_BOILER_YEARS = [1, 5, 10]
56:VERDICT_BAND = 1000  # within +/- this many GBP over the horizon counts as "too close"
59:def defaults():
63:def money(x, sign=False):
70:def run(p, tariff="cap"):
112:def solve(f, lo, hi):
125:def label(adv):
126:    return "YES" if adv > VERDICT_BAND else "NO" if adv < -VERDICT_BAND else "TOO CLOSE"
129:def analyse(p):
137:    # stress test
139:    for s in [p['scop'] + d for d in STRESS_SCOP_OFFSETS]:
140:        for gi, ei in STRESS_PRICES:
141:            for by in STRESS_BOILER_YEARS:
146:    out["stress"] = n
150:SENS = [
169:def verdict_text(p, a):
176:    s = a["stress"]["cap"]
182:        ("High" if agree >= .9 else "Moderate" if agree >= .7 else "Low") + f" ({agree:.0%} of {s[1]} stress scenarios agree)"
186:def summary(p):
213:    s = a["stress"]
217:    for nm, ov in SENS:
223:def bottom(A, B):
235:def report(p):
298:    for nm, ov in SENS:
301:    s = a["stress"]
350:def parse(argv):
```

</details>

**→ Read** `{"file_path": "<workspace>/heatpump_model.py", "offset": 129, "limit": 100}`

<details><summary>result</summary>

```
129	def analyse(p):
130	    r = {"cap": run(p, "cap"), "hp": run(p, "hp")}
131	    out = {"base": r}
132	    adv_scop = lambda tar: (lambda s: run({**p, "scop": s}, tar)["adv"])
133	    out["be_scop"] = {t: solve(adv_scop(t), 1.5, 8.0) for t in ("cap", "hp")}
134	    out["be_hp_price"] = solve(lambda u: run({**p, "hp_tariff_unit": u}, "hp")["adv"], 0.02, 0.60)
135	    out["be_net_cost"] = {t: p["hp_net_cost"] + r[t]["adv"] for t in ("cap", "hp")}
136	    out["be_gas_kwh"] = {t: solve(lambda g: run({**p, "gas_kwh": g}, t)["adv"], 3000, 60000) for t in ("cap", "hp")}
137	    # stress test
138	    n = {"cap": [0, 0], "hp": [0, 0]}
139	    for s in [p['scop'] + d for d in STRESS_SCOP_OFFSETS]:
140	        for gi, ei in STRESS_PRICES:
141	            for by in STRESS_BOILER_YEARS:
142	                for t in ("cap", "hp"):
143	                    q = {**p, "scop": s, "gas_inflation": gi, "elec_inflation": ei, "boiler_replace_year": by}
144	                    n[t][1] += 1
145	                    n[t][0] += run(q, t)["adv"] > 0
146	    out["stress"] = n
147	    return out
148	
149	
150	SENS = [
151	    ("Base case", {}),
152	    ("Heat pump efficiency poor (SCOP 2.6)", {"scop": 2.6}),
153	    ("Heat pump efficiency good (SCOP 3.5)", {"scop": 3.5}),
154	    ("Heat pump efficiency excellent (SCOP 4.0)", {"scop": 4.0}),
155	    ("Home uses more gas (12,000 kWh)", {"gas_kwh": 12000}),
156	    ("Home uses less gas (7,500 kWh)", {"gas_kwh": 7500}),
157	    ("Boiler dies now (replace in year 0)", {"boiler_replace_year": 0}),
158	    ("Boiler lasts 10 more years", {"boiler_replace_year": 10}),
159	    ("Boiler never needs replacing in the period", {"boiler_replace_year": 99}),
160	    ("Heat pump costs £9,000 net", {"hp_net_cost": 9000}),
161	    ("Heat pump costs £6,000 net", {"hp_net_cost": 6000}),
162	    ("5% VAT returns on electricity", {"elec_vat": 0.05}),
163	    ("Electricity gets relatively cheaper (gas +4%/yr, elec +2%/yr)", {"gas_inflation": 0.04, "elec_inflation": 0. … [3928 more chars]
```

</details>

**→ Read** `{"file_path": "<workspace>/heatpump_model.py", "offset": 288, "limit": 20}`

<details><summary>result</summary>

```
288	    o.append(f"The heat pump starts {money(p['hp_net_cost'])} behind and claws it back through lower bills. "
289	             f"Standard tariff: {'breaks even in year %d' % c['breakeven_year'] if c['breakeven_year'] is not None else 'never breaks even'} within {H} years. "
290	             f"Heat-pump tariff: {'breaks even in year %d' % h['breakeven_year'] if h['breakeven_year'] is not None else 'never breaks even'} within {H} years. "
291	             f"The step in the 'keep boiler' column at year {ry} is the replacement boiler. "
292	             "Remaining life of each system at the end is credited at what you paid, spread evenly over its lifespan (a notional value, not a sale price).\n")
293	
294	    o.append("## How well does the answer hold up?\n")
295	    o.append("Each row changes one thing from the base case. Positive means the heat pump is ahead after the full period.\n")
296	    o.append("| Change | Standard tariff | Heat-pump tariff |")
297	    o.append("|---|---|---|")
298	    for nm, ov in SENS:
299	        q = {**p, **ov}
300	        o.append(f"| {nm} | {money(run(q,'cap')['adv'], True)} | {money(run(q,'hp')['adv'], True)} |")
301	    s = a["stress"]
302	    o.append(f"\n**Stress test:** I ran {s['cap'][1]} combinations (SCOP from {p['scop']-0.4:.1f} to {p['scop']+0.6:.1f}, three fuel-price paths, boiler replacement due in year 1, 5 or 10). "
303	             f"The heat pump finished cheaper in **{s['cap'][0]}** of them on a standard tariff and **{s['hp'][0]}** on a heat-pump tariff. "
304	             "This is a spread of possibilities, not a probability.\n")
305	
306	    o.append("## Assumptions and sources\n")
307	    o.append("`SOURCE` = taken from a cited source (some figures are still estimates). `ASSUMPTION` = my estimate; replace it if you know better.\n")
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:60],s.count(a))\n    s=s.replace(a,b)\n\nrep(\"import sys\\n\",\"import random\\nimport sys\\n\")\nrep('''STRESS_SCOP_OFFSETS = [-0.4, -0.2, 0.0, 0.2, 0.4, 0.6]  # around your own SCOP input\nSTRESS_PRICES = [(0.03, 0.03), (0.04, 0.02), (0.02, 0.04)]   … [10475 more chars]`

<details><summary>result</summary>

```
VERDICT: NO on a standard tariff; TOO CLOSE on a heat-pump tariff
CONFIDENCE: High (on a standard tariff the simulation agrees with this in 95% of 5,000 draws)
Check: Ofgem typical-use bill from these prices = £1,724 (Ofgem published £1,723)
Useful heat needed per year: 7,735 kWh
Year-1 running cost, keep boiler (incl. service, gas standing charge): £965
Year-1 running cost, heat pump on standard tariff:  £894  (saving +£71)
Year-1 running cost, heat pump on heat-pump tariff: £731  (saving +£234)
15-year position vs keeping boiler (positive = heat pump cheaper):
  standard tariff    -£3,077 cash,  -£3,932 in today's money; does not break even
  heat-pump tariff      -£46 cash,  -£1,649 in today's money; does not break even
Break-even thresholds (heat pump = boiler over the period):
  SCOP needed, standard tariff: 3.97
  SCOP needed, heat-pump tariff: 3.01
  Heat-pump tariff price needed at SCOP 3.0: 19.9p/kWh
  Net heat pump cost needed, standard tariff: £4,423; heat-pump tariff: £7,454
  Gas use needed, standard tariff: n/a
  Gas use needed, heat-pump tariff: 9,618 kWh/yr
Simulation (5,000 draws, seed 20261113; every uncertain input varied together around your inputs):
  standard tariff   heat pump cheaper in 5% of draws; median -£3,336, 80% range -£6,187 to -£675
  heat-pump tariff  heat pump cheaper in 41% of draws; median -£484, 80% range -£3,264 to +£2,298
Biggest drivers (advantage over the period at each extreme: standard tariff | heat-pump tariff; ranked by swing):
  Heat pump efficiency (SCOP 2.6 to 4.0)
       -£5,019 to     +£78  |   -£1,522 to  +£2,351
  Fuel price paths (elec dearer: gas +2%/elec +4% to elec cheaper: gas +4%/elec +2%)
       -£5,238 to    -£905  |   -£1,975 to  +£1,913
  Heat-pump tariff blended price (25p to 16p; heat-pump tariff only)
       -£3,077 to  -£3,077  |   -£2,444 to  +£1,872
  When the boiler would need replacing (never in period to now)
       -£4,748 to  -£2,208  |   -£1,718 to    +£823
  Net installed price (£9,000 to £6 … [826 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:60],s.count(a))\n    s=s.replace(a,b)\nrep('''res.append((\"Nesta running-cost parity (ratio 3.3, efficiency 2.8, boiler 85%)\", abs(r[\"y1B\"] - r[\"y1H\"]) < 1.0,''','''res.append((\"Nesta running-cost parity (ratio 3.3, efficiency 2.8, boiler 85%; N … [831 more chars]`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
  PASS  Ofgem typical bill reproduced within £1 [£1,724 vs £1,723]
  PASS  Nesta running-cost parity (ratio 3.3, efficiency 2.8, boiler 85%; Nesta rounds, so within 1%) [boiler £950 vs heat pump £952]
  PASS  Hand-derived flat-price case [model +£1,000 vs by hand +£1,000]
  PASS  Higher efficiency never hurts
## The answer

> **Verdict: NO on a standard tariff; TOO CLOSE on a heat-pump tariff**  
> **Confidence: High (on a standard tariff the simulation agrees with this in 95% of 5,000 draws)**

- **Bottom line:** don't do it just to save money on a standard tariff. On a heat-pump tariff it roughly breaks even, so it comes down to the efficiency your installer predicts and whether you value the non-financial benefits.
- **Over 15 years, a heat pump on a standard tariff leaves you £3,077 worse off than keeping a gas boiler** (£3,932 worse off in today's money). On a heat-pump tariff you'd be £46 worse off (£1,649 worse off in today's money).
- **Running costs barely differ; the up-front cost is what decides it.** In year 1 the heat pump's bills are £71 lower on a standard tariff or £234 lower on a heat-pump tariff, but you pay £7,500 after the grant. Keeping the boiler means paying £3,000 for a new one in year 5, which narrows the gap but doesn't close it.
- **Why bills are so similar:** a kWh of heat costs about 9.4p from your gas boiler and 8.8p from a heat pump at SCOP 3.0 on the standard tariff. Electricity costs 3.3x as much per kWh as gas, which cancels out most of the heat pump's efficiency.

### What would flip it

| If... | Today's assumption | The heat pump breaks even over the period when... |
|---|---|---|
| Your installer's **predicted SCOP** (efficiency) is higher | 3.0 | 3.97 on a standard tariff, 3.01 on a heat-pump tariff |
| You get a **cheaper electricity tariff** for heating | 26.3p standard; 20p assumed heat-pump tariff | 19.9p/kWh blended or lower, at SCOP 3.0 |
| The **installed price* … [3773 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\na='''\"The first and third are things you can find out before buying.\\\\n\")'''\nassert a in s\ns=s.replace(a,'''\"Of all the inputs, efficiency and tariff price can be pinned down before you buy; future fuel prices can't.\\\\n\")''')\nopen('heatpump_model.py','w').write(s)\nEOF\npython3 -I heatpump_model.py … [228 more chars]`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
heat-pump-vs-gas-boiler.md
heatpump_model.py
[This command modified 2 files you've previously read: heat-pump-vs-gas-boiler.md, heatpump_model.py. Call Read before editing.]
```

</details>

### Assistant

**Step 3 report: Depth**

**Did:**
- **Simulation:** I replaced the hand-picked 54-scenario grid with a seeded simulation of 5,000 draws. It varies efficiency, gas use, installed price, boiler age and cost, fuel price rises, tariff price and VAT together. The ranges are my judgement, centred on your inputs.
- **Driver ranking:** I added a table that moves each input between plausible extremes and ranks them by how far they move the result.
- **Self-test:** I built a self-test into the script. It checks the model against Ofgem's £1,723 typical bill, Nesta's published running-cost parity figure, a hand-derived flat-price case, and the rule that better efficiency never hurts. All four pass, and the output is pasted at the bottom of the file.

**Found:**
- **Standard tariff:** the heat pump is cheaper in only 5% of draws, so the "no" verdict is now High confidence (95%). The median is £3,336 worse off.
- **Heat-pump tariff:** the heat pump is cheaper in 41% of draws, with an 80% range of about £3,260 worse off to £2,300 better off. That's why it stays "too close".
- **Biggest drivers:** efficiency, future fuel prices, and the price you pay on a heat-pump tariff move the result most. The efficiency and the tariff price are the two you can pin down before buying, so a written efficiency prediction and a quoted tariff would settle most of the uncertainty.
- **Boiler timing:** this matters more than I'd have guessed. A boiler that fails now turns the heat-pump-tariff case from about £50 worse off to about £820 ahead.

**Changed course:**
- **Nesta check:** it first failed by £2 on £950. I traced that to Nesta rounding the price ratio, not a model error, and allowed 1% tolerance, labelled in the check.
- **Verdict wording:** the page-one verdict, bottom line and thresholds are unchanged. Only the confidence figure is now better grounded.
- **Copies:** I saved the file and script to `.ambition/steps/3/`, leaving `.ambition/first/` untouched.

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

Assumptions I'm resting the verdict on, riskiest first, with who set each one:

| # | Assumption | Set by | Test |
|---|---|---|---|
| 1 | A "typical" home uses 9,500 kWh of gas a year | Me (Ofgem average) | Check against real consumption data for semi-detached homes |
| 2 | A heat-pump tariff blends to 20p/kWh | Me | Check against the tariff's published rates |
| 3 | SCOP of 3.0 | Me, anchored to Nesta and the field trial | Check against field data and design values |
| 4 | Net price £7,500 and a £3,000 replacement boiler | You set the first and I set the second | Check against published installed costs |
| 5 | Both fuels rise 3% a year together | Me | Check against forecasts |
| 6 | Grant is available and gas can be disconnected cheaply | Me | Check the scheme rules |

I'll start with the first four tests.

**→ WebSearch** `{"query": "NEED National Energy Efficiency Data-Framework median gas consumption by property type semi-detached kWh 2024", "mode": "standard"}`

**→ WebFetch** `{"url": "https://octopus.energy/smart/cosy-octopus/", "prompt": "Give the current Cosy Octopus unit rates (cheap, day, peak p/kWh), time windows and standing charge, and the date/region they apply to."}`

**→ WebSearch** `{"query": "Cornwall Insight January 2027 price cap forecast electricity gas unit rates heat pump price ratio", "mode": "standard"}`

**→ WebSearch** `{"query": "cost of new gas boiler installed UK 2026 Energy Saving Trust and air source heat pump installed cost before grant average", "mode": "standard"}`

<details><summary>result</summary>

```
The page doesn't give the actual unit rates or standing charge, so I can't provide those figures.

- **Cheap rate:** Not stated in p/kWh. The page says it is 51% cheaper than the Day rate in your region.
- **Day rate:** Not stated. It is the baseline the other rates are calculated from.
- **Peak rate:** Not stated in p/kWh. The page says it is 50% above the Day rate in your region.
- **Time windows:**
  - Cheap: 04:00-07:00, 13:00-16:00, and 22:00-00:00 daily
  - Peak: 16:00-19:00 daily
  - The remaining hours fall under the Day rate.
- **Standing charge:** Not mentioned.
- **Date and region:** The page doesn't list rates for a specific region. A savings note refers to rates "available from March 17th," but it gives no year. Rates vary by region, and you can check yours using the postcode tool on the page.
```

</details>

<details><summary>result</summary>

```
Web search results for query: "NEED National Energy Efficiency Data-Framework median gas consumption by property type semi-detached kWh 2024"

Links: [{"title":"nd need 2026 report","url":"https://assets.publishing.service.gov.uk/media/6abcf5f355bc01d752a7f136/nd-need-2026-report.pdf"},{"title":"annex b overview of data tables 2026","url":"https://assets.publishing.service.gov.uk/media/6a282027db0592d809052b0e/annex-b-overview-of-data-tables-2026.pdf"},{"title":"National Energy Efficiency Data Framework  NEED  Main Report","url":"https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/532535/National_Energy_Efficiency_Data-Framework__NEED__Main_Report.pdf"},{"title":"Annex B   Quality Assurance","url":"https://assets.publishing.service.gov.uk/media/5a7cb94de5274a38e57565c1/Annex_B_-_Quality_Assurance.pdf"},{"title":"National Energy Efficiency Data Framework  NEED  Main Report","url":"https://assets.publishing.service.gov.uk/media/5a81a473e5274a2e87dbeba8/National_Energy_Efficiency_Data-Framework__NEED__Main_Report.pdf"},{"title":"6872 need report annex d","url":"https://assets.publishing.service.gov.uk/media/5a797028e5274a2acd18cd47/6872-need-report-annex-d.pdf"},{"title":"NEED report june 2024","url":"https://assets.publishing.service.gov.uk/media/667c2ca85b0d63b556a4b3ca/NEED-report-june-2024.pdf"},{"title":"ND NEED 2024 report","url":"https://assets.publishing.service.gov.uk/media/66b4dfe6ab418ab055593520/ND-NEED-2024-report.pdf"},{"title":"National Energy Efficiency Data Framework (NEED) report: Summary of analysis 2026 (accessible webpage)","url":"https://www.gov.uk/government/statistics/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026-accessible-webpage"},{"title":"annex c comparisons with other sources 2026","url":"https://assets.publishing.service.gov.uk/media/6a2823256d178a6fb7e31f9a/annex-c-comparisons-with-ot … [2843 more chars]
```

</details>

<details><summary>result</summary>

```
Web search results for query: "Cornwall Insight January 2027 price cap forecast electricity gas unit rates heat pump price ratio"

Links: [{"title":"moneytothemasses.com","url":"https://moneytothemasses.com/?p=140709"},{"title":"energy bills to rise again in january 2027","url":"https://moneytothemasses.com/news/energy-bills-to-rise-again-in-january-2027"},{"title":"moneytothemasses.com","url":"https://moneytothemasses.com/news/energy-bills-to-rise-again-in-january-2027/amp"},{"title":"energy bills forecast to hit nearly 2000 a year from january 2027","url":"https://restless.co.uk/money/everyday-finance/energy-bills-forecast-to-hit-nearly-2000-a-year-from-january-2027/"},{"title":"UK Energy Bills Could Soar by £442 in January: How To Avoid Paying More as Prices Climb","url":"https://www.ibtimes.co.uk/january-2027-energy-price-cap-forecasts-1822143"},{"title":"Personal Finance","url":"https://www.nimblefins.co.uk/node/2023"},{"title":"cornwall insight","url":"https://cornwall-insight.com/"},{"title":"UK energy bills forecast to jump again in January","url":"https://streamlinefeed.co.ke/news/uk-energy-bills-forecast-to-jump-again-in-january"},{"title":"Get Free Solar Panel Quotes","url":"https://www.theecoexperts.co.uk/news/cornwall-insight-energy-price-cap-prediction"},{"title":"Energy bills predicted to fall from April","url":"https://moneytothemasses.com/news/energy-bills-predicted-to-fall-from-april/amp"},{"title":"energy bills predicted to fall from april","url":"https://moneytothemasses.com/news/energy-bills-predicted-to-fall-from-april"},{"title":"Energy prices: Ofgem price cap may fall by 1% in January 2026 - Cornwall Insight predictions","url":"https://www.thestar.co.uk/business/consumer/energy-prices-ofgem-price-cap-january-2026-cornwall-insight-predictions-5406957"},{"title":"www.cornwall insight","url":"https://www.cornwall-insight.com/?p=11759"},{"title":"Energy price cap: Ofgem confirms January 2026 UK bill rise despite predictions of a fall - how does i … [2107 more chars]
```

</details>

<details><summary>result</summary>

```
Web search results for query: "cost of new gas boiler installed UK 2026 Energy Saving Trust and air source heat pump installed cost before grant average"

Links: [{"title":"new boiler cost","url":"https://www.clearscore.com/learn/managing-money/new-boiler-cost"},{"title":"New boiler cost · key figures (2026)","url":"https://selectra.co.uk/energy/guides/boiler/new-boiler-cost"},{"title":"Average Cost of New Boilers","url":"https://www.nimblefins.co.uk/node/1933"},{"title":"New Boiler & Heating Costs 2026: What Government Data Really Shows","url":"https://firewall.heatable.co.uk/new-boilers/advice/boiler-costs-government-data"},{"title":"new boiler cost","url":"https://www.expertsure.com/uk/boilers/new-boiler-cost/"},{"title":"air source heat pump cost","url":"https://www.expertsure.com/uk/heat-pumps/air-source-heat-pump-cost/"},{"title":"UK 2026 / May 2026","url":"https://boilerreplacementcost.pages.dev/vs-heat-pump/"},{"title":"How Much Does a Heat Pump Cost in the UK in 2026? (Reading Edition)","url":"https://readingheatpumps.pages.dev/guides/heat-pump-cost-uk-2026/"},{"title":"New Boiler Cost 2026: UK Installation & Replacement Prices","url":"https://heatable.co.uk/boiler-advice/how-much-do-new-boilers-cost"},{"title":"air source heating pump","url":"https://www.myjobquote.co.uk/costs/air-source-heating-pump.md"},{"title":"air source heat pump cost uk 2026 installation prices running costs grants payback times","url":"https://www.bookabuilderuk.com/blog/air-source-heat-pump-cost-uk-2026-installation-prices-running-costs-grants-payback-times"},{"title":"Blog>Cost Guides>How much does it cost to replace a boiler with a heat pump?","url":"https://www.checkatrade.com/blog/cost-guides/cost-replace-boiler-heat-pump/"},{"title":"UK 2026 cost guide / Updated May 2026","url":"https://boilerreplacementcost.pages.dev/"},{"title":"New Boiler Costs UK 2026: Prices by Type","url":"https://heatable.co.uk/boiler-advice/uk-boiler-installation-prices-in-2018-costs-and-averages-by-p … [2135 more chars]
```

</details>

**→ WebFetch** `{"url": "https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026", "prompt": "What does it say about VAT on electricity and gas, and any end date? Quote the relevant sentences. Also unit rates and the change vs July-September 2026."}`

**→ WebFetch** `{"url": "https://www.gov.uk/government/news/heat-pump-grants-increased-by-50-per-cent", "prompt": "State the grant amount for an air source heat pump, who is eligible, whether the scheme end date is given, and any requirement about the old boiler or gas disconnection."}`

<details><summary>result</summary>

```
- **Grant amount:** £7,500 for an air source heat pump, up from £5,000.
- **Eligibility:** The page doesn't list full criteria. It says people can check whether their home is eligible on GOV.UK. Applicants don't apply directly: "Customers do not have to apply for the grants." They agree a quote with an MCS-certified installer, who handles the paperwork.
- **End date:** Yes. The scheme has been extended by three years, to 2028.
- **Old boiler or gas disconnection:** The page doesn't mention this. It does say the government will exempt homes from the 2035 fossil fuel boiler phase-out if a heat pump isn't suitable, but it sets no requirement to remove the old boiler or disconnect the gas.
```

</details>

<details><summary>result</summary>

```
**VAT:** Electricity VAT is removed until 31 March 2027, and gas stays at 5%.

- "The government has removed VAT from electricity bills from 1 October 2026 to 31 March 2027." (end date: 31 March 2027)
- "It does not include VAT from 1 October 2026 to 31 March 2027." (electricity rate)
- "You will still pay 5% VAT for gas." (gas)

**Unit rates (1 October to 31 December 2026, averages for England, Scotland and Wales, Direct Debit, default tariff):**

- **Electricity:** 26.32p per kWh, standing charge 54.83p per day (excludes VAT)
- **Gas:** 7.97p per kWh, standing charge 29.68p per day (includes 5% VAT)

**Change vs July to September 2026:** The page doesn't give the July to September unit rates, so I can't calculate the change per unit. It says a typical household's energy prices will rise by 4% for this period, and that the rise is due to higher wholesale gas prices. It also warns that costs can't be compared directly with previous periods because of the VAT change. The page links to a unit rates comparison tool for both periods.
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && grep -n \"hp_tariff_unit\\|elec_vat\" heatpump_model.py"}`

<details><summary>result</summary>

```
30:    "elec_vat": (0.0, "VAT added to electricity (fraction)", "ASSUMPTION",
35:    "hp_tariff_unit": (0.20, "Blended price on a heat-pump tariff (GBP/kWh)", "ASSUMPTION",
65:    ("Heat-pump tariff blended price (25p to 16p; heat-pump tariff only)", {"hp_tariff_unit": (0.25, 0.16)}),
66:    ("VAT on electricity (5% to 0%)", {"elec_vat": (0.05, 0.0)}),
95:    uc = p["elec_unit"] * (1 + p["elec_vat"])
96:    uh = (p["hp_tariff_unit"] * (1 + p["elec_vat"])) if tariff == "hp" else uc
148:    out["be_hp_price"] = solve(lambda u: run({**p, "hp_tariff_unit": u}, "hp")["adv"], 0.02, 0.60)
185:             "hp_tariff_unit": tri(rng, p["hp_tariff_unit"] * 0.8, p["hp_tariff_unit"], p["hp_tariff_unit"] * 1.25),
186:             "elec_vat": 0.05 if rng.random() < 0.5 else 0.0,
334:             f"{p['hp_tariff_unit']*100:.0f}p assumed heat-pump tariff | {a['be_hp_price']*100:.1f}p/kWh blended or lower, at SCOP {p['scop']:.1f} |")
389:        vs = f"{v:.2%}" if k in ("gas_inflation", "elec_inflation", "discount") else (f"{v:.0%}" if k in ("boiler_eff", "new_boiler_eff") else f"{v:.2f}" if k == "hp_tariff_unit" else f"{v:,}" if isinstance(v, int) else str(v))
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && sed -n 28,40p heatpump_model.py && sed -n 330,336p heatpump_model.py && grep -n \"Ofgem 2026 'medium'\\|boiler_replace_cost\\\": (3000\\|\\\"hp_net_cost\\\": (9000\\|Net installed price\\|Replacement boiler cost\" heatpump_model.py"}`

<details><summary>result</summary>

```
    "gas_sc": (0.2968, "Gas standing charge (GBP/day)", "SOURCE", "Ofgem cap, Oct-Dec 2026."),
    "elec_unit": (0.2632, "Electricity unit price (GBP/kWh)", "SOURCE", "Ofgem cap, Oct-Dec 2026, no VAT currently."),
    "elec_vat": (0.0, "VAT added to electricity (fraction)", "ASSUMPTION",
                 "0 = as published. Ofgem lists no VAT on electricity for Oct 2026-Mar 2027; "
                 "I could not confirm what happens after. See sensitivity table."),
    "scop": (3.0, "Heat pump seasonal efficiency (SCOP/SPF)", "ASSUMPTION",
             "Field trial median 2.8 (older installs); Nesta models 3.0. No survey of your house yet."),
    "hp_tariff_unit": (0.20, "Blended price on a heat-pump tariff (GBP/kWh)", "ASSUMPTION",
                       "Octopus Cosy-style: ~13p cheap, ~26p day, ~39p peak, weighted by when heat pumps run."),
    "hp_net_cost": (7500, "Heat pump net cost after grant (GBP)", "SOURCE", "Your figure; Boiler Upgrade Scheme is up to GBP 7,500."),
    "hp_service": (150, "Heat pump annual service (GBP)", "ASSUMPTION", ""),
    "boiler_service": (100, "Boiler annual service (GBP)", "ASSUMPTION", ""),
    "boiler_replace_year": (5, "Year existing boiler would be replaced", "ASSUMPTION",
    o.append("|---|---|---|")
    o.append(f"| Your installer's **predicted SCOP** (efficiency) is higher | {p['scop']:.1f} | "
             f"{f(be['cap'], '{:.2f}')} on a standard tariff, {f(be['hp'], '{:.2f}')} on a heat-pump tariff |")
    o.append(f"| You get a **cheaper electricity tariff** for heating | {p['elec_unit']*100:.1f}p standard; "
             f"{p['hp_tariff_unit']*100:.0f}p assumed heat-pump tariff | {a['be_hp_price']*100:.1f}p/kWh blended or lower, at SCOP {p['scop']:.1f} |")
    o.append(f"| The **installed price** is lower | {money(p['hp_net_cost'])} | {money(a['be_net_cost']['cap'])} (standard tariff) or "
             f"{money(a['be_net_cost']['hp'])} (heat-pump tariff) |")
21:                "Ofgem 2026 'medium' typical use. Many 3-be … [296 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\nimport re\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:70],s.count(a))\n    s=s.replace(a,b)\n\n# gas use\ni=s.index('    \"gas_kwh\": ('); j=s.index('    \"cooking_gas_kwh\"')\ns=s[:i]+'''    \"gas_kwh\": (10500, \"Gas used per year (kWh)\", \"ASSUMPTION\",\n                \"NEED (DESNZ) 2024  … [5095 more chars]`

<details><summary>result</summary>

```
VERDICT: NO
CONFIDENCE: High (on a standard tariff the simulation agrees with this in 94% of 5,000 draws)
Check: Ofgem typical-use bill from these prices = £1,724 (Ofgem published £1,723)
Useful heat needed per year: 8,585 kWh
Year-1 running cost, keep boiler (incl. service, gas standing charge): £1,045
Year-1 running cost, heat pump on standard tariff:  £1,010  (saving +£35)
Year-1 running cost, heat pump on heat-pump tariff: £852  (saving +£193)
15-year position vs keeping boiler (positive = heat pump cheaper):
  standard tariff    -£4,113 cash,  -£4,781 in today's money; does not break even
  heat-pump tariff   -£1,171 cash,  -£2,565 in today's money; does not break even
Break-even thresholds (heat pump = boiler over the period):
  SCOP needed, standard tariff: 4.16
  SCOP needed, heat-pump tariff: 3.33
  Heat-pump tariff price needed at SCOP 3.0: 19.9p/kWh (72% of the standard rate)
  Net heat pump cost needed, standard tariff: £3,387; heat-pump tariff: £6,329
  Gas use needed, standard tariff: n/a
  Gas use needed, heat-pump tariff: 14,664 kWh/yr
Simulation (5,000 draws, seed 20261113; every uncertain input varied together around your inputs):
  standard tariff   heat pump cheaper in 6% of draws; median -£3,509, 80% range -£6,495 to -£652
  heat-pump tariff  heat pump cheaper in 44% of draws; median -£326, 80% range -£3,162 to +£2,621
Biggest drivers (advantage over the period at each extreme: standard tariff | heat-pump tariff; ranked by swing):
  Heat pump efficiency (SCOP 2.6 to 4.0)
       -£6,376 to    -£435  |   -£2,981 to  +£1,771
  Fuel price paths (elec dearer: gas +2%/elec +4% to elec cheaper: gas +4%/elec +2%)
       -£6,539 to  -£1,680  |   -£3,372 to  +£1,056
  Heat-pump tariff price (no load shifting to mostly shifted; heat-pump tariff only)
       -£4,113 to  -£4,113  |   -£2,642 to  +£1,477
  Net installed price (£9,000 to £5,500)
       -£5,363 to  -£2,446  |   -£2,421 to    +£496
  When the boiler would need replacing (never in period to now)
 … [881 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && grep -n \"Heat-pump tariff: Octopus\\|def bottom\\|bottom(c\\|label(A)\\|A, B = a\\[\\|Price cap: \\[Ofgem\" heatpump_model.py && sed -n '/^def verdict_text/,/^    return head, conf/p' heatpump_model.py | head -12 && sed -n '/^def bottom/,/^def report/p' heatpump_model.py"}`

<details><summary>result</summary>

```
230:    A, B = a["base"]["cap"]["adv"], a["base"]["hp"]["adv"]
231:    lc, lh = label(A), label(B)
290:def bottom(A, B):
291:    lc, lh = label(A), label(B)
319:    o.append(f"- **Bottom line:** {bottom(c['adv'], h['adv'])}")
396:- Price cap: [Ofgem unit rates and standing charges](https://www.ofgem.gov.uk/node/176588/), average Direct Debit, Oct-Dec 2026 (electricity 26.32p/kWh + 54.83p/day; gas 7.97p/kWh + 29.68p/day). Official. These are averages across England, Scotland and Wales, not England-only, and the price cap changes every quarter.
400:- Heat-pump tariff: Octopus [publishes average Cosy rates](https://octopus.energy/press/Octopus-Energy-launches-new-off-peak-rate-for-heat-pump-customers/) (cheap about 13p, day about 26p, peak about 40p). My 20p blended price is my own weighting of those, and current rates vary by region. Check live rates before relying on it.
def verdict_text(p, a):
    A, B = a["base"]["cap"]["adv"], a["base"]["hp"]["adv"]
    lc, lh = label(A), label(B)
    if lc == lh:
        head = lc
    else:
        head = f"{lc} on a standard tariff; {lh} on a heat-pump tariff"
    m = a["mc"]["cap"]
    if lc == "NO": agree = 1 - m["p_cheaper"]
    elif lc == "YES": agree = m["p_cheaper"]
    else: agree = None
    if agree is None:
def bottom(A, B):
    lc, lh = label(A), label(B)
    if lc == "YES":
        return "go ahead: it should pay for itself even on a standard tariff."
    if lh == "YES":
        return "only worth it if you switch to a heat-pump tariff; on a standard tariff it won't pay back."
    if lh == "TOO CLOSE":
        return ("don't do it just to save money on a standard tariff. On a heat-pump tariff it roughly breaks even, "
                "so it comes down to the efficiency your installer predicts and whether you value the non-financial benefits.")
    return "don't do it to save money; it costs more over the period on either tariff."


def report(p):
```

</details>

### Assistant

I'm adding the combined verdict labels and the evidence-checks section to the report, then regenerating and verifying it.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:70],s.count(a))\n    s=s.replace(a,b)\n\n# combined labels: point estimate and simulation median must agree, otherwise TOO CLOSE\nrep('''def verdict_text(p, a):\n    A, B = a[\"base\"][\"cap\"][\"adv\"], a[\"base\"][\"hp\"][\"adv\"]\n    lc, lh = label … [6395 more chars]`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
VERDICT: NO on a standard tariff; TOO CLOSE on a heat-pump tariff
CONFIDENCE: High (on a standard tariff the simulation agrees with this in 94% of 5,000 draws)
Check: Ofgem typical-use bill from these prices = £1,724 (Ofgem published £1,723)
## The answer

> **Verdict: NO on a standard tariff; TOO CLOSE on a heat-pump tariff**  
> **Confidence: High (on a standard tariff the simulation agrees with this in 94% of 5,000 draws)**

- **Bottom line:** don't do it just to save money on a standard tariff. On a heat-pump tariff it roughly breaks even, so it comes down to the efficiency your installer predicts and whether you value the non-financial benefits.
- **Over 15 years, a heat pump on a standard tariff leaves you £4,113 worse off than keeping a gas boiler** (£4,781 worse off in today's money). On a heat-pump tariff you'd be £1,171 worse off (£2,565 worse off in today's money).
- **Running costs barely differ; the up-front cost is what decides it.** In year 1 the heat pump's bills are £35 lower on a standard tariff or £193 lower on a heat-pump tariff, but you pay £7,500 after the grant. Keeping the boiler means paying £2,500 for a new one in year 5, which narrows the gap but doesn't close it.
- **Why bills are so similar:** a kWh of heat costs about 9.4p from your gas boiler and 8.8p from a heat pump at SCOP 3.0 on the standard tariff. Electricity costs 3.3x as much per kWh as gas, which cancels out most of the heat pump's efficiency.

### What would flip it

78:## What I checked against evidence
79-
80-I tested the main assumptions against source material instead of trusting my first guess. Items marked **changed** moved the base case.
81-
82-| Assumption | What the evidence says | Result |
83-|---|---|---|
84-| Electricity price stays at the published 26.32p | [Ofgem](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026): that rate excludes VAT, and VAT is removed on … [3440 more chars]
```

</details>

### Assistant

Two wording problems to fix: the page-one price figures still ignore VAT, and I called the installed price "third biggest driver" when it ranks fourth.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:70],s.count(a))\n    s=s.replace(a,b)\nrep(\"and {p['elec_unit']/p['scop']*100:.1f}p from a heat pump\",\"and {p['elec_unit']*(1+p['elec_vat'])/p['scop']*100:.1f}p from a heat pump\")\nrep(\"f\\\"Electricity costs {p['elec_unit']/p['gas_unit']:.1f}x as … [1077 more chars]`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
13:- **Why bills are so similar:** a kWh of heat costs about 9.4p from your gas boiler and 9.2p from a heat pump at SCOP 3.0 on the standard tariff. Electricity (with VAT) costs 3.5x as much per kWh as gas, which cancels out most of the heat pump's efficiency.
0
heat-pump-vs-gas-boiler.md
heatpump_model.py
[This command modified 2 files you've previously read: heat-pump-vs-gas-boiler.md, heatpump_model.py. Call Read before editing.]
```

</details>

### Assistant

**Step 4 report: Challenge**

**Did:** I tested each assumption against real material, riskiest first, and added a "What I checked against evidence" section to the file. It lists each assumption, what the evidence says, and what changed.

**Found:**
- **The blind spot:** the base case treated a temporary electricity VAT holiday as permanent. Ofgem's page says VAT is removed only from October 2026 to 31 March 2027, so the 26.32p rate I used is VAT-free. With VAT the price is 27.64p, and electricity costs 3.5 times as much as gas per kWh, not 3.3. That quietly flattered the heat pump for 15 years.
- **Gas use:** the government's household energy dataset (NEED) puts the median at 10,000 kWh, and the semi-detached mean at about 11,700 kWh. My 9,500 was too low.
- **Boiler cost:** the typical replacement is £2,000–£3,500, so my £3,000 was a little high.
- **Heat-pump tariff price:** my flat 20p was a guess. I replaced it with the tariff's own published structure. The price depends on when you run the heat pump, from about 18p to 24p.
- **Your £7,500 price:** published data suggests the market median is about £5,500 net, so your figure is above it. At £5,500 the heat-pump-tariff case flips to about £500 ahead, so get quotes.
- **Grant:** confirmed at £7,500, extended to 2028, with no requirement to disconnect gas.
- **Not tested:** I couldn't test the efficiency spread against household-level data. I also found no source for future fuel prices or the cost of disconnecting gas. The first two are the largest drivers, and the file says so.

**Changed course:**
- **Base inputs:**
  - electricity VAT is 5%
  - gas use is 10,500 kWh
  - the replacement boiler costs £2,500
  - the heat-pump tariff is 80% of the standard rate
- **Verdict labels:** the heat pump on a heat-pump tariff is now £1,171 worse off on the point estimate, which would read as "no". The simulation's median is near break-even, though. Where the two disagree, the label now says "too close".
- **Overall verdict:** it's the same as before, with the numbers now better grounded. On a standard tariff it's no, with high confidence (94% of 5,000 draws). On a heat-pump tariff it's too close. That's about £4,100 worse off on a standard tariff and £1,170 worse off on a heat-pump tariff.
- **Self-test:** all four checks still pass, and I saved a copy to `.ambition/steps/4/`.

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

**What this is really doing, as verbs.** It helps a homeowner **decide** whether to commit about £7,500 under uncertainty. To do that it has to **answer** the money question, **explain** the answer in plain words, **show** its working so the reader can trust it, **compare** against doing nothing, and **tell them what would change the answer**. Those are the genre's own verbs (a decision memo), and the deliverable stays one Markdown memo.

**Fields and what I borrowed from each:**

| Field | What they actually do | Direction taken |
|---|---|---|
| Decision-memo editor (the genre's best practitioner) | Pre-commit to decision rules before the facts arrive, so a reader can act on them | A **quote test**: grids of efficiency against installed price that say yes / close / no, so the installer's numbers settle it |
| Personal-finance adviser | Express an outlay as a rate of return and set it against alternatives | The **return on the extra money**, as a yearly percentage |
| Insurance actuary | Look at the tails and regret, not just the average | The chance of being more than £2,000 worse off or better off |
| Superforecaster (the field I wouldn't normally consider) | Write down dated tripwires that trigger a re-forecast | A **when to re-check** list with real dates |
| Red team: consumer-protection reviewer | Look for misuse, mis-reading and harm | Tested below by running bad inputs |

**The edge I took:** a reader could act on this memo in one sitting. The quote test and the return figure let them judge a real installer quote on the day it arrives.

I'll start with the red team and run some bad inputs against the model.

**→ Bash** `{"command": "cd \"<workspace>\" && for a in \"scop=0\" \"gas_kwh=300\" \"gas_kwh=900\" \"horizon=0\" \"scop=-2\" \"boiler_life=0\"; do echo \"--- $a\"; python3 -I heatpump_model.py --set $a 2>&1 | head -3; done"}`

<details><summary>result</summary>

```
--- scop=0
Traceback (most recent call last):
  File "<workspace>/heatpump_model.py", line 485, in <module>
    print(summary(params)[0])
--- gas_kwh=300
Traceback (most recent call last):
  File "<workspace>/heatpump_model.py", line 485, in <module>
    print(summary(params)[0])
--- gas_kwh=900
Traceback (most recent call last):
  File "<workspace>/heatpump_model.py", line 485, in <module>
    print(summary(params)[0])
--- horizon=0
Traceback (most recent call last):
  File "<workspace>/heatpump_model.py", line 485, in <module>
    print(summary(params)[0])
--- scop=-2
Traceback (most recent call last):
  File "<workspace>/heatpump_model.py", line 485, in <module>
    print(summary(params)[0])
--- boiler_life=0
Traceback (most recent call last):
  File "<workspace>/heatpump_model.py", line 485, in <module>
    print(summary(params)[0])
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && grep -n \"Rule of thumb\\|Over {H} years, a heat pump\\|out\\[t\\] = {\\|def parse\\|params, mode, path = parse\\|o.append(\\\"## The answer\\|Typical English 3-bed\\|\\\"p_cheaper\\\"\\|return {\\\"cumB\\\"\" heatpump_model.py && sed -n '/^def parse/,$p' heatpump_model.py"}`

<details><summary>result</summary>

```
124:    return {"cumB": cumB, "cumH": cumH, "adv": cumB[H] - cumH[H], "pv": pv, "breakeven_year": be,
196:        out[t] = {"p_cheaper": sum(x > 0 for x in v) / len(v), "p10": v[len(v) // 10], "median": v[len(v) // 2],
245:    if lc == "NO": agree = 1 - m["p_cheaper"]
246:    elif lc == "YES": agree = m["p_cheaper"]
320:    o.append("*Typical English 3-bed semi on the Ofgem price cap (Oct-Dec 2026). Prices and efficiency come from the sources at the "
323:    o.append("## The answer\n")
327:    o.append(f"- **Over {H} years, a heat pump on a standard tariff leaves you {gap(c['adv'])} than keeping a gas boiler** "
352:    o.append("Rule of thumb: ask installers for a written heat-loss calculation and a predicted SCOP. If it is below the SCOP "
463:def parse(argv):
483:    params, mode, path = parse(sys.argv[1:])
def parse(argv):
    p, mode, path, i = defaults(), "print", None, 0
    while i < len(argv):
        a = argv[i]
        if a == "--set":
            k, _, v = argv[i + 1].partition("=")
            if k not in INPUTS: sys.exit(f"unknown input '{k}' (see --list)")
            p[k] = type(INPUTS[k][0])(float(v)) if not isinstance(INPUTS[k][0], float) else float(v)
            i += 2
        elif a in ("--write", "--check"):
            mode, path, i = a[2:], argv[i + 1], i + 2
        elif a == "--list":
            for k, (v, lab, kind, _) in INPUTS.items(): print(f"{k:22s} {v!s:>8}  {lab} [{kind}]")
            sys.exit(0)
        else:
            sys.exit(__doc__)
    return p, mode, path


if __name__ == "__main__":
    params, mode, path = parse(sys.argv[1:])
    if mode == "print":
        print(summary(params)[0])
    elif mode == "write":
        open(path, "w").write(report(params)); print(f"wrote {path}")
    else:
        ok = open(path).read() == report(params)
        print("OK: file matches the model" if ok else "MISMATCH: regenerate with --write (using the same --set options)")
        sys.exit(0 if ok else 1)
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && sed -n 120,127p heatpump_model.py && sed -n 192,200p heatpump_model.py && sed -n 318,324p heatpump_model.py && sed -n 350,356p heatpump_model.py"}`

<details><summary>result</summary>

```
        cumB.append(a); cumH.append(b)
    d = p["discount"]
    pv = sum((cashB[t] - cashH[t]) / (1 + d) ** t for t in range(H + 1))
    be = next((t for t in range(H + 1) if cumH[t] <= cumB[t]), None)
    return {"cumB": cumB, "cumH": cumH, "adv": cumB[H] - cumH[H], "pv": pv, "breakeven_year": be,
            "y1B": cashB[1], "y1H": cashH[1], "heat": heat}


            res[t].append(run(q, t)["adv"])
    out = {}
    for t, v in res.items():
        v.sort()
        out[t] = {"p_cheaper": sum(x > 0 for x in v) / len(v), "p10": v[len(v) // 10], "median": v[len(v) // 2],
                  "p90": v[9 * len(v) // 10]}
    return out


    o = []
    o.append("# Should I swap my gas boiler for a heat pump?\n")
    o.append("*Typical English 3-bed semi on the Ofgem price cap (Oct-Dec 2026). Prices and efficiency come from the sources at the "
             "bottom; everything else is a flagged assumption. Every figure below is generated by `heatpump_model.py`, so you can "
             "change an input and regenerate the file (see 'Re-run it').*\n")
    o.append("## The answer\n")
    o.append(f"> **Verdict: {head}**  \n> **Confidence: {conf}**\n")
    o.append(f"The simulation below says the three things that move the result most are: {top[0]}, {top[1]}, and {top[2]}. "
             "Of all the inputs, efficiency and tariff price can be pinned down before you buy; future fuel prices can't.\n")
    o.append("Rule of thumb: ask installers for a written heat-loss calculation and a predicted SCOP. If it is below the SCOP "
             "in the first row, the heat pump is unlikely to pay back on running costs alone.\n")

    o.append(f"## The {H}-year picture\n")
    o.append(f"Total cash spent from today (heat pump installed now vs. keeping the boiler and replacing it in year {ry}). "
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:70],s.count(a))\n    s=s.replace(a,b)\n\n# --- run(): cash-flow difference for return calculation\nrep('''    return {\"cumB\": cumB, \"cumH\": cumH, \"adv\": cumB[H] - cumH[H], \"pv\": pv, \"breakeven_year\": be,\n            \"y1B\": cashB[1], \"y1H\ … [9262 more chars]`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
--- scop=0
Input problem:
  scop must be between 1 and 10 (typical 2.5-4)
--- gas_kwh=300
Input problem:
  gas_kwh must be more than cooking_gas_kwh (is it in kWh?)
--- horizon=0
Input problem:
  horizon must be 5-40 years
--- boiler_life=0
Input problem:
  boiler_life must be above 0
--- m3 mistake
Traceback (most recent call last):
  File "<workspace>/heatpump_model.py", line 567, in <module>
    print(summary(params)[0])
[This command modified 2 files you've previously read: heat-pump-vs-gas-boiler.md, heatpump_model.py. Call Read before editing.]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I heatpump_model.py --set gas_kwh=1000 2>&1 | tail -6"}`

<details><summary>result</summary>

```
    print(summary(params)[0])
          ~~~~~~~^^^^^^^^
  File "<workspace>/heatpump_model.py", line 323, in summary
    L.append(f"  Heat-pump tariff price needed at SCOP {p['scop']}: {a['be_hp_price']*p['elec_unit']*(1+p['elec_vat'])*100:.1f}p/kWh ({a['be_hp_price']:.0%} of the standard rate)")
                                                                     ~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~
TypeError: unsupported operand type(s) for *: 'NoneType' and 'float'
```

</details>

### Assistant

The m³ mistake (1,000 entered as kWh) doesn't just give a wrong answer, it crashes when no break-even tariff price exists. I'll handle that case, then check what the report says for this input.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:70],s.count(a))\n    s=s.replace(a,b)\nrep('''    L.append(f\"  Heat-pump tariff price needed at SCOP {p['scop']}: {a['be_hp_price']*p['elec_unit']*(1+p['elec_vat'])*100:.1f}p/kWh ({a['be_hp_price']:.0%} of the standard rate)\")''','''    bp = a[\"be_h … [918 more chars]`

<details><summary>result</summary>

```
WARNING: gas_kwh = 1,000 is unusual. Bills are in kWh. If your meter shows cubic metres (m3), multiply by about 11.2 to get kWh.
VERDICT: NO
CONFIDENCE: High (on a standard tariff the simulation agrees with this in 100% of 5,000 draws)
Check: Ofgem typical-use bill from these prices = £1,724 (Ofgem published £1,723)
# Should I swap my gas boiler for a heat pump?

*Typical English 3-bed semi on the Ofgem price cap (Oct-Dec 2026). Prices and efficiency come from the sources at the bottom; everything else is a flagged assumption. Every figure below is generated by `heatpump_model.py`, so you can change an input and regenerate the file (see 'Re-run it').*

*Who this is for: an owner-occupier in England with a mains-gas boiler and a wet (radiator) system, deciding on money. It will mislead you if your home is off the gas grid, is a flat, is in Scotland, Wales or Northern Ireland, or if carbon, comfort or future boiler rules matter more to you than cost. Figures are rounded: this is a forecast, not a quote.*

> **Check your inputs:** gas_kwh = 1,000 is unusual. Bills are in kWh. If your meter shows cubic metres (m3), multiply by about 11.2 to get kWh.

## The answer
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
[This command modified 2 files you've previously read: heat-pump-vs-gas-boiler.md, heatpump_model.py. Call Read before editing.]
```

</details>

### Assistant

The misuse case is now caught with a plain warning. I'll read the new sections of the file as a first-time reader would.

**→ Bash** `{"command": "cd \"<workspace>\" && sed -n 1,75p heat-pump-vs-gas-boiler.md"}`

<details><summary>result</summary>

```
# Should I swap my gas boiler for a heat pump?

*Typical English 3-bed semi on the Ofgem price cap (Oct-Dec 2026). Prices and efficiency come from the sources at the bottom; everything else is a flagged assumption. Every figure below is generated by `heatpump_model.py`, so you can change an input and regenerate the file (see 'Re-run it').*

*Who this is for: an owner-occupier in England with a mains-gas boiler and a wet (radiator) system, deciding on money. It will mislead you if your home is off the gas grid, is a flat, is in Scotland, Wales or Northern Ireland, or if carbon, comfort or future boiler rules matter more to you than cost. Figures are rounded: this is a forecast, not a quote.*

## The answer

> **Verdict: NO on a standard tariff; TOO CLOSE on a heat-pump tariff**  
> **Confidence: High (on a standard tariff the simulation agrees with this in 94% of 5,000 draws)**

- **Bottom line:** don't do it just to save money on a standard tariff. On a heat-pump tariff it roughly breaks even, so it comes down to the efficiency your installer predicts and whether you value the non-financial benefits.
- **Over 15 years, a heat pump on a standard tariff leaves you £4,100 worse off than keeping a gas boiler** (£4,800 worse off in today's money). On a heat-pump tariff you'd be £1,150 worse off (£2,550 worse off in today's money).
- **As an investment:** the extra money you put in earns about -10% a year on a standard tariff and -2% a year on a heat-pump tariff over 15 years. Compare that with what the same money would earn in savings or by paying down debt.
- **Running costs barely differ; the up-front cost is what decides it.** In year 1 the heat pump's bills are £35 lower on a standard tariff or £190 lower on a heat-pump tariff, but you pay £7,500 after the grant. Keeping the boiler means paying £2,500 for a new one in year 5, which narrows the gap but doesn't close it.
- **Why bills are so similar:** a kWh of heat costs about 9.4p from your gas boiler and 9.2p from a … [3836 more chars]
```

</details>

### Assistant

One wording fix: a negative return should read as "loses about 10% a year", not "earns about -10%".

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\na=s.index('    fr = lambda r:'); b=s.index('    o.append(f\"- **Running costs barely differ;')\ns=s[:a]+'''    fr = lambda r: \"loses more than 30%\" if r is None else (f\"loses about {abs(r):.0%}\" if r < -0.005 else f\"earns about {r:.0%}\")\n    o.append(f\"- **As an investment:** over {H} years the extra  … [736 more chars]`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
14:- **As an investment:** over 15 years the extra money you put into the heat pump loses about 10% a year on a standard tariff and loses about 2% a year on a heat-pump tariff. Compare that with what the same money would earn in savings or by paying down debt.
87-
88-**Simulation.** I varied every uncertain input at once (5,000 random draws around your inputs: efficiency, gas use, installed price, boiler age and cost, fuel price rises, tariff price, whether VAT returns). The ranges are my judgement, centred on the base case and spelled out in `monte_carlo()`; they are not measured spreads.
89-
90:| | Heat pump cheaper in... | Typical result (median) | 80% of draws fall between | More than £2,000 worse off | More than £2,000 better off |
0
heat-pump-vs-gas-boiler.md
heatpump_model.py
[This command modified 2 files you've previously read: heat-pump-vs-gas-boiler.md, heatpump_model.py. Call Read before editing.]
```

</details>

### Assistant

**Step 5 report: Range**

**Did:** I borrowed one method from each field and applied it to the file, as listed in the table above.
- **Quote test:** two grids of predicted efficiency against installed price, giving yes / close / no, for a standard tariff and for a heat-pump tariff.
- **Return on the extra money:** a yearly percentage to compare with savings.
- **Chance of a big loss or gain:** the share of simulated outcomes more than £2,000 worse off or better off.
- **Dated re-check list:** Ofgem's January cap, the 31 March 2027 VAT end, and boiler failure.

**Found (red team):**
- **Crashes:** a zero SCOP, a gas figure below the cooking allowance, a zero horizon and a zero boiler life all crashed with tracebacks.
- **Silent harm:** entering a gas meter's m³ reading as kWh gave a confident "no" at 100%, and then crashed on an edge case. That is the most likely real-world misuse.
- **False precision:** figures like £4,113 implied accuracy the inputs don't have.
- **Mis-reading:** a "no" could be read as "never", or applied to homes the model doesn't cover (flats, off-gas, Scotland and Wales).

**Changed course:**
- **Input checks:** impossible inputs now stop with a plain message, and odd-looking ones (such as gas under 4,000 kWh) get a warning that mentions the ×11.2 m³ conversion.
- **Rounding:** report figures are rounded (to £50 above £1,000). The pasted script output stays exact.
- **Scope note:** a note at the top says who the memo is for and who it will mislead.
- **Verdict:** unchanged. On a standard tariff the extra money loses about 10% a year, and on a heat-pump tariff about 2% a year.
- **Self-test:** all four checks still pass, and I saved a copy to `.ambition/steps/5/`.

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

First I'll define the outside check, so the work is held to something that isn't me. These are the promises it has to meet:

1. One Markdown file, with the verdict first and the script's output pasted verbatim at the bottom.
2. A yes / no / too-close verdict with confidence and the facts that would flip it.
3. A 15-year comparison that includes boiler replacement.
4. Sources cited and assumptions flagged.
5. Every number regenerated from one set of inputs.
6. Plain explanations of jargon.

I'll check what I can reach from here before building the checker.

**→ Bash** `{"command": "cd \"<workspace>\" && grep -o 'https\\?://[^) ]*' heat-pump-vs-gas-boiler.md | sort -u; echo ---; curl -s -o /dev/null -w \"%{http_code}\\n\" -m 10 https://www.ofgem.gov.uk/node/176588/ 2>&1 | head -2"}`

<details><summary>result</summary>

```
https://es.catapult.org.uk/news/heat-pumps-shown-to-be-three-times-more-efficient-than-gas-boilers/
https://octopus.energy/press/Octopus-Energy-launches-new-off-peak-rate-for-heat-pump-customers/
https://octopus.energy/smart/cosy-octopus/
https://www.carbonbrief.org/factcheck-what-it-really-costs-to-heat-a-home-in-the-uk-with-a-heat-pump
https://www.energy-uk.org.uk/wp-content/uploads/2026/05/Energy-UK-Explains-Typical-Domestic-Consumption-Values.pdf
https://www.gov.uk/government/news/heat-pump-grants-increased-by-50-per-cent
https://www.gov.uk/government/statistics/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026-accessible-webpage
https://www.nesta.org.uk/report/how-to-make-heat-pumps-more-affordable/assumptions-and-methods/
https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026
https://www.ofgem.gov.uk/node/176588/
---
301
```

</details>

**→ Write** `{"file_path": "<workspace>/.ambition/judge/judge.py", "content": "#!/usr/bin/env python3\n\"\"\"Outside check for heat-pump-vs-gas-boiler.md. Not part of the deliverable.\nUsage: python3 -I judge.py REPORT.md MODEL.py\nEach check prints PASS/FAIL. Exit code 1 if any FAIL.\n\"\"\"\nimport importlib.util, re, subprocess, sys, urllib.request, urllib.error\n\nreport_path, model_path = sys.argv[1], sys … [10388 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/.ambition/judge/judge.py (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

Two of my own checks were weak: one is a no-op that always passes, and another has a pointless clause. I'll replace them with a real traceability listing before running anything.

**→ bash** `{"command": "cd \"<workspace>/.ambition/judge\" && python3 - <<'EOF'\ns=open('judge.py').read()\na=s.index(\"# ---------- 4. Every number regenerates\"); b=s.index(\"# ---------- 5. Stale text\")\ns=s[:a]+'''# ---------- 4. Every number regenerates: perturb inputs; list prose lines with \u00a3 figures that do NOT move ----------\nalt = M.report({**M.defaults(), \"gas_kwh\": 13000, \"scop\": 3.6, \ … [991 more chars]`

<details><summary>result</summary>

```
<tool_use_error>Error: No such tool available: bash. Tool names are case-sensitive: call Bash instead.</tool_use_error>
```

</details>

**→ Bash** `{"command": "cd \"<workspace>/.ambition/judge\" && python3 - <<'EOF'\ns=open('judge.py').read()\na=s.index(\"# ---------- 4. Every number regenerates\"); b=s.index(\"# ---------- 5. Stale text\")\ns=s[:a]+'''# ---------- 4. Every number regenerates: perturb inputs; list prose lines with \u00a3 figures that do NOT move ----------\nalt = M.report({**M.defaults(), \"gas_kwh\": 13000, \"scop\": 3.6, \ … [911 more chars]`

<details><summary>result</summary>

```
Exit code 1
PASS Independent re-implementation agrees with the model (6 input sets x 2 tariffs)  [worst gap £0.0000]
PASS File matches regenerated model output
PASS Script output block present at the bottom
PASS Pasted output equals a fresh run of the script
PASS Verdict appears before any working
PASS Verdict is one of yes / no / too close
PASS Confidence stated
PASS Flip facts table with thresholds
PASS Long-run comparison runs 10-15 years incl. year 15
PASS Boiler replacement timing modelled and explained
PASS Section order: answer, 15-year picture, robustness, assumptions, script output
PASS Assumptions are flagged (ASSUMPTION and SOURCE tags in table)
FAIL Answer section is short enough to read in about two minutes (<= 900 words incl. quote grids)  [1032 words]
PASS Page one before the flip table is under 300 words  [276 words]
     prose lines with money/pence figures that do not change when inputs change (review by eye: must be cited constants only):
       - **On a standard tariff** (yes = clearly cheaper over 15 years; close = within £1,000; no = clearly dearer)
       - **On a heat-pump tariff** (yes = clearly cheaper over 15 years; close = within £1,000; no = clearly dearer)
       - - Pass: Ofgem typical bill reproduced within £1 (£1,724 vs £1,723)
       - - Pass: Nesta running-cost parity (ratio 3.3, efficiency 2.8, boiler 85%; Nesta rounds, so within 1%) (boiler £1,050 vs heat pump £1,052)
       - - Pass: Hand-derived flat-price case (model +£1,000 vs by hand +£1,000)
       - - Price cap: [Ofgem unit rates and standing charges](https://www.ofgem.gov.uk/node/176588/), average Direct Debit, Oct-Dec 2026 (electricity 26.32p/kWh + 54.83p/day; gas 
       - - Typical use (9,500 kWh gas, 2,500 kWh electricity): Ofgem's 2026 review, as reported by [Energy UK](https://www.energy-uk.org.uk/wp-content/uploads/2026/05/Energy-UK-Ex
       - - Grant: [GOV.UK, Boiler Upgrade Scheme grants](https://www.gov.uk/government/news/heat-pump-grants-increased-by-50-per-ce … [3424 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:70],s.count(a))\n    s=s.replace(a,b)\n# (a) correct break-even price\nrep('''out[\"be_net_cost\"] = {t: p[\"hp_net_cost\"] + r[t][\"adv\"] for t in (\"cap\", \"hp\")}''','''out[\"be_net_cost\"] = {t: solve(lambda c: run({**p, \"hp_net_cost\": c}, t)[\ … [2781 more chars]`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
7:## The answer
18:### What would flip it
32:## The 15-year picture
50:## How well does the answer hold up?
81:## Using this with an installer quote
109:## When to re-check
117:## What I checked against evidence
142:## Assumptions and sources
181:## Plain-English glossary
196:## Limits
202:## Re-run it
211:## Script output (verbatim)
[This command modified 2 files you've previously read: heatpump_model.py, heat-pump-vs-gas-boiler.md. Call Read before editing.]
```

</details>

### Assistant

Now I'll update the checker to measure the answer section and the per-section table changes properly, then rerun it.

**→ Bash** `{"command": "cd \"<workspace>/.ambition/judge\" && python3 - <<'EOF'\ns=open('judge.py').read()\na=s.index(\"words_before_picture =\"); b=s.index(\"bullets_to_flip =\")\ns=s[:a]+'''ans = md[md.index(\"## The answer\"):md.index(\"## The 15-year picture\")]\nwords_answer = len(re.sub(r\"\\\\|[-| ]+\\\\|\", \"\", ans).split())\ncheck(\"'The answer' section is readable in about two minutes (<= 600 wor … [1149 more chars]`

<details><summary>result</summary>

```
FAIL Every result row regenerates when inputs change: How well does the answer hold up?  [12/13 rows changed]

54/55 checks passed
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 -I - <<'EOF'\nimport importlib.util\nspec=importlib.util.spec_from_file_location(\"m\",\"heatpump_model.py\");M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)\nmd=open(\"heat-pump-vs-gas-boiler.md\").read().splitlines()\nalt=set(M.report({**M.defaults(),\"gas_kwh\":13000,\"scop\":3.6,\"hp_net_cost\":6400,\"gas_inflation\":0.04}).splitlin … [221 more chars]`

<details><summary>result</summary>

```
| | Heat pump cheaper in... | Typical result (median) | 80% of draws fall between | More than £2,000 worse off | More than £2,000 better off |
| Input (extremes tested) | Standard tariff | Heat-pump tariff |
```

</details>

**→ Bash** `{"command": "cd \"<workspace>/.ambition/judge\" && python3 - <<'EOF'\ns=open('judge.py').read()\na=s.index(\"    rows_ = [l for l in section(md, h)\"); b=s.index(\"    moved =\")\ns=s[:a]+'''    sec = section(md, h).splitlines()\n    rows_ = [l for k, l in enumerate(sec[:-1]) if l.startswith(\"| \") and not sec[k + 1].startswith(\"|---\") and not sec[k + 1].startswith(\"| ---\")]\n    rows_ = [l f … [378 more chars]`

**→ WebFetch** `{"url": "https://www.gov.uk/government/statistics/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026-accessible-webpage", "prompt": "Quote the sentences giving median and mean domestic gas consumption in 2024, and any figure for semi-detached homes. Be exact about numbers and years."}`

**→ WebFetch** `{"url": "https://www.nesta.org.uk/report/how-to-make-heat-pumps-more-affordable/assumptions-and-methods/", "prompt": "What SCOP/seasonal efficiency does Nesta assume for heat pumps, and what does it say about running costs vs gas boilers? Quote exact sentences."}`

**→ WebFetch** `{"url": "https://www.carbonbrief.org/factcheck-what-it-really-costs-to-heat-a-home-in-the-uk-with-a-heat-pump", "prompt": "What does it say about the Heat Pump Monitor average SCOP (3.9?) and whether that sample is representative/self-selected? Quote exact sentences."}`

<details><summary>result</summary>

```
45
55/55 checks passed
```

</details>

<details><summary>result</summary>

```
The page assumes a **coefficient of performance (COP) of 3** for heat pumps in the baseline, rising to **3.3** in the optimistic scenario. It doesn't mention seasonal efficiency (SCOP) directly.

- Heat pumps: "heat pumps have a coefficient of performance of 3 (baseline)", which "can increase over time to 3.3 (optimistic scenario)"
- Gas boilers: "Gas boiler efficiency is set to 0.85."
- Comparison: "This means that gas boilers use approximately more than 3.5x more energy to produce one unit of heat (baseline)."

The page doesn't give a direct running-cost comparison. It does note that electricity is "still about 4.1x higher per unit than gas," which offsets the heat pump's efficiency advantage in running costs.
```

</details>

<details><summary>result</summary>

```
The article reports the 3.9 figure but does not assess whether the Heat Pump Monitor sample is representative or self-selected.

**What it says about the 3.9 SCoP:**
- Heat Pump Monitor offers "Detailed, real-time data on hundreds of heat pump systems around the UK," and its average is "much higher" than the 2.8 used in the government's trial data.
- The figure is "a SCoP of 3.9," and the article uses it for a Carbon Brief estimate that a typical household could save nearly £200 a year on a standard tariff.
- A chart compares the trial's efficiency distribution with Heat Pump Monitor's, sourced to Heat Pump Monitor.

**Representativeness and self-selection:**
- The article doesn't explain how systems are recruited or whether owners opt in, so self-selection can't be assessed from it.
- It doesn't discuss whether the "hundreds" of systems reflect UK installations overall.
- It does suggest the sample may skew toward well-installed systems. Trystan Lea, Heat Pump Monitor's co-founder, argues that results should not come from "poorly configured installs." Rosenow's research is cited as showing that well-installed systems perform about 64% better than early trials.
- Lea's comments are the article's main defence of the figure, but they are advocacy from the platform's co-founder, not an independent check on the sample.
```

</details>

<details><summary>result</summary>

```
**Median gas consumption, England and Wales (2024):**
The report states: "median domestic gas consumption in England and Wales was 10,000 kWh" (Section 2).

**Mean gas consumption, England and Wales (2024):**
No sentence gives this. Table 2.1 lists a mean of 11,200 kWh for gas.

**Median gas consumption, Scotland (2024):**
The report states: "In 2024, the median domestic gas consumption in Scotland was 10,600 kWh." Table 2.2 lists a mean of 11,800 kWh for Scotland.

**Semi-detached homes:**
The text gives no gas consumption figure specific to semi-detached homes. Footnote 3 defines "houses" as including "detached, semi-detached, bungalow, end-terraced and mid-terraced" properties. Those houses are said to represent 75% of properties in England and Wales as at 31 March 2025. Figure 2.11 covers consumption by property type, but its values are in an image and aren't reproduced in the text.
```

</details>

**→ WebFetch** `{"url": "https://www.nesta.org.uk/feature/energy-affordability/establish-price-ratio-target/", "prompt": "Quote exactly what it says about the electricity-to-gas price ratio at which a heat pump costs the same to run as a gas boiler, including the COP and boiler efficiency assumed (e.g. 3.3, 2.8, 85%)."}`

<details><summary>result</summary>

```
At a price ratio of 3.3 or lower, a heat pump costs the same to run as a gas boiler. The article says, "a heat pump meeting a basic level of efficiency (a Coefficient of Performance, or COP, of 2.8)" matches a boiler's running cost. That boiler is assumed to be about 85% efficient, as the article puts it: "will cost the same to run as a typical gas boiler (which is around 85% efficient)".
```

</details>

### Assistant

Nesta's parity claim is confirmed exactly (ratio 3.3, COP 2.8, boiler 85%), so the self-test stands. I'll correct the three overstated claims and cite the Nesta parity page properly.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:70],s.count(a))\n    s=s.replace(a,b)\nrep('''\"NEED (DESNZ) 2024 median for all homes 10,000; semi-detached mean 11,715 (2023). 10,500 is my estimate between them. \"\n                \"Ofgem's 'typical' 9,500 is lower.\"''','''\"NEED (DESNZ), England … [2268 more chars]`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
56/56 checks passed
[This command modified 2 files you've previously read: heatpump_model.py, heat-pump-vs-gas-boiler.md. Call Read before editing.]
```

</details>

### Assistant

All 56 checks pass. Now the cold read: the whole file, start to finish, as the person deciding would read it.

**→ Read** `{"file_path": "<workspace>/heat-pump-vs-gas-boiler.md", "limit": 150}`

<details><summary>result</summary>

```
1	# Should I swap my gas boiler for a heat pump?
2	
3	*Typical English 3-bed semi on the Ofgem price cap (Oct-Dec 2026). Prices and efficiency come from the sources at the bottom; everything else is a flagged assumption. Every figure below is generated by `heatpump_model.py`, so you can change an input and regenerate the file (see 'Re-run it').*
4	
5	*Who this is for: an owner-occupier in England with a mains-gas boiler and a wet (radiator) system, deciding on money. It will mislead you if your home is off the gas grid, is a flat, is in Scotland, Wales or Northern Ireland, or if carbon, comfort or future boiler rules matter more to you than cost. Figures are rounded: this is a forecast, not a quote.*
6	
7	## The answer
8	
9	> **Verdict: NO on a standard tariff; TOO CLOSE on a heat-pump tariff**  
10	> **Confidence: High (on a standard tariff the simulation agrees with this in 94% of 5,000 draws)**
11	
12	- **Bottom line:** don't do it just to save money on a standard tariff. On a heat-pump tariff it roughly breaks even, so it comes down to the efficiency your installer predicts and whether you value the non-financial benefits.
13	- **Over 15 years, a heat pump on a standard tariff leaves you £4,100 worse off than keeping a gas boiler** (£4,800 worse off in today's money). On a heat-pump tariff you'd be £1,150 worse off (£2,550 worse off in today's money).
14	- **As an investment:** over 15 years the extra money you put into the heat pump loses about 10% a year on a standard tariff and loses about 2% a year on a heat-pump tariff. Compare that with what the same money would earn in savings or by paying down debt.
15	- **Running costs barely differ; the up-front cost is what decides it.** In year 1 the heat pump's bills are £35 lower on a standard tariff or £190 lower on a heat-pump tariff, but you pay £7,500 after the grant. Keeping the boiler means paying £2,500 for a new one in year 5, which narrows the gap but doesn't close it.
16	- **Why bills are so similar:** a  … [11630 more chars]
```

</details>

**→ Read** `{"file_path": "<workspace>/heat-pump-vs-gas-boiler.md", "offset": 170, "limit": 48}`

<details><summary>result</summary>

```
170	| Disconnect gas when heat pump goes in (1=yes, 0=no) | 1 | ASSUMPTION |  |
171	
172	**Sources and how far to trust them**
173	
174	- Price cap: [Ofgem unit rates and standing charges](https://www.ofgem.gov.uk/node/176588/), average Direct Debit, Oct-Dec 2026 (electricity 26.32p/kWh + 54.83p/day; gas 7.97p/kWh + 29.68p/day). Official. Note the electricity rate excludes VAT, which is removed only until 31 March 2027; the model adds 5% back. These are averages across England, Scotland and Wales, not England-only, and the price cap changes every quarter.
175	- Typical use (9,500 kWh gas, 2,500 kWh electricity): Ofgem's 2026 review, as reported by [Energy UK](https://www.energy-uk.org.uk/wp-content/uploads/2026/05/Energy-UK-Explains-Typical-Domestic-Consumption-Values.pdf). I could not open Ofgem's own decision page, but these figures with the cap prices reproduce Ofgem's £1,723 typical bill to within £1 (see the check in the script output).
176	- Heat pump efficiency: [Electrification of Heat trial](https://es.catapult.org.uk/news/heat-pumps-shown-to-be-three-times-more-efficient-than-gas-boilers/) (Energy Systems Catapult), median seasonal efficiency 2.8 for air-source heat pumps. These are interim results from the 742-home trial; I did not find the final report. [Nesta](https://www.nesta.org.uk/report/how-to-make-heat-pumps-more-affordable/assumptions-and-methods/) assumes a baseline of 3 rising to 3.3. [Carbon Brief](https://www.carbonbrief.org/factcheck-what-it-really-costs-to-heat-a-home-in-the-uk-with-a-heat-pump) reports that the Heat Pump Monitor site shows about 3.9; the article doesn't say how those systems were recruited and the figure is defended by the site's co-founder, so I treated 3.9 as an upper case, not the typical one.
177	- Grant: [GOV.UK, Boiler Upgrade Scheme grants](https://www.gov.uk/government/news/heat-pump-grants-increased-by-50-per-cent): up to £7,500 for an air-source heat pump in England and Wales. I did not confirm the scheme's end d … [4134 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:70],s.count(a))\n    s=s.replace(a,b)\n# 1 plain-terms line\nrep('''    for w in warnings(p):\n        o.append(f\"> **Check your inputs:**''','''    o.append(\"*In plain terms: **SCOP** is how many units of heat a heat pump delivers per unit of electr … [3211 more chars]`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
OK: file matches the model
[This command modified 2 files you've previously read: heat-pump-vs-gas-boiler.md, heatpump_model.py. Call Read before editing.]
```

</details>

### Assistant

I'll update the checker for the new wording and add checks for the issues the cold read found. Then I'll run the same checks on the first version for comparison.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\np='.ambition/judge/judge.py'\ns=open(p).read()\na=s.index(\"check(\\\"'never breaks even' text agrees\"); b=s.index(\"a = M.analyse(M.defaults())\")\ns=s[:a]+'''both_neg = neg(c[\"adv\"]) and neg(h[\"adv\"])\ncheck(\"Break-even sentence agrees with year-15 table sign\",\n      (\"Neither tariff breaks even\" in md) == both_neg and (both_neg or  … [1490 more chars]`

<details><summary>result</summary>

```
FAIL Flip facts table with thresholds
64/65 checks passed
=== same promises, first version ===
verdict at top: 0
cited source links: 0
10-15yr comparison: 2
regenerable from one set of inputs: 0
assumptions flagged: 2
words:      902
final words:     4177
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && sed -i 's/\\\\| .\\*SCOP.\\* \\\\| .\\*\\\\d\\\\.\\\\d\\\\d on a standard/\\\\| .*SCOP.* \\\\| .*\\\\d\\\\.\\\\d\\\\d or more on a standard/' .ambition/judge/judge.py && python3 -I .ambition/judge/judge.py heat-pump-vs-gas-boiler.md heatpump_model.py | grep \"FAIL\\|checks passed\"; python3 -I heatpump_model.py --check heat-pump-vs-gas-boiler.md; mkdir -p .ambiti … [106 more chars]`

<details><summary>result</summary>

```
sed: 1: ".ambition/judge/judge.py
": invalid command code .
OK: file matches the model
heat-pump-vs-gas-boiler.md
heatpump_model.py
```

</details>

### Assistant

`sed` failed on macOS, so the checker didn't run. I'll make the one-line fix in Python and run it.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\np='.ambition/judge/judge.py'\ns=open(p).read()\nold=r'\\d\\.\\d\\d on a standard'\nassert old in s\ns=s.replace(old, r'\\d\\.\\d\\d or more on a standard')\nopen(p,'w').write(s)\nEOF\npython3 -I .ambition/judge/judge.py heat-pump-vs-gas-boiler.md heatpump_model.py | grep \"FAIL\\|checks passed\"; diff -q heat-pump-vs-gas-boiler.md .ambition/ste … [68 more chars]`

<details><summary>result</summary>

```
65/65 checks passed
step-6 copy is current
```

</details>

### Assistant

**Step 6 report: Judge**

**Did:** I built an outside checker, `.ambition/judge/judge.py`, and ran the file through it until it passed. It covers:
- **Independent reimplementation:** a differently written version of the cost model, run on 6 input sets and both tariffs.
- **Structure:** whether the file matches what the script generates, and whether the pasted output is verbatim.
- **Promises:** the original ask and the restatement.
- **Readability:** word counts per section, jargon, stale text, and contradictions.
- **Links:** whether each source link loads.
- **Quote grids:** whether they behave sensibly.

I also gave the file a cold read from top to bottom. It passes all 65 checks.

**Found:**
- **Model bug:** the checker caught an error in the "installed price needed to break even" figure, which used a linear shortcut that ignored the remaining-life credit. That figure is now solved properly, and the break-even prices rose slightly.
- **Overstated claims:** I checked three sources I had only seen through search summaries, and each said less than I claimed:
  - **NEED:** the dataset gives no semi-detached figure.
  - **Carbon Brief:** the article doesn't say the monitor sample is self-selected.
  - **Nesta:** the page doesn't say what I attributed to it about bills.

  I corrected all three. Nesta's parity claim (ratio 3.3, COP 2.8, boiler 85%) is confirmed exactly.
- **Cold-read issues:** the reader would have hit several things.
  - **Page one:** SCOP and "heat-pump tariff" appeared with no gloss.
  - **Contradiction:** the sources section said the grant's end date was unconfirmed while another section stated it.
  - **Process leak:** the evidence section said "my first version".
  - **Page length:** the answer section ran to about 1,030 words.
  - **Repetition and wording:** one sentence repeated itself, and the flip-table cells lacked "or more" and "or less".

**Changed course:**
- **Page layout:** the quote grids and the re-check list moved out of "The answer", which is now about 560 words, with page one under 300.
- **Glossary:** it now covers simulation draws, median, cylinder, SPF and MCS.
- **Verdict:** unchanged.
- **Versus the first version:** the first version had no verdict at the top, no source links, no regenerable numbers and only two flagged assumptions. The final has all of those.
- **Length cost:** the file grew from about 900 to about 4,200 words, but most of that is reference material below the answer.
- **Not checked:** how a real reader finds the length. I saved a copy to `.ambition/steps/6/`.

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

**The brief:** a yes / no / too-close verdict for a typical English 3-bed semi, in one Markdown file, with a script that recomputes it. That's done and passing.

**The stretch target:** your own verdict from three numbers, in one command and under about 10 seconds, with no knowledge of the model. The three numbers are your gas kWh (or m³) from your bill, the SCOP an installer predicts, and their price after the grant. That's several times easier than today's list of `--set` options, and it works on the day a quote arrives.

**Fallback:** the file as it stands, with `--set` for full control.

**Where it would likely break:**
- **Gas meter units:** m³ versus kWh is the likeliest failure.
- **Inputs outside the model:** the three-number shortcut can't handle fixed deals or unusual homes.
- **Speed:** the 5,000-draw simulation might be too slow.

I'll measure the current speed first.

**→ Bash** `{"command": "cd \"<workspace>\" && time python3 -I heatpump_model.py >/dev/null; sed -n '/^def parse/,/^    return p, mode, path/p' heatpump_model.py | head -30"}`

<details><summary>result</summary>

```
python3 -I heatpump_model.py > /dev/null  0.11s user 0.01s system 95% cpu 0.119 total
def parse(argv):
    p, mode, path, i = defaults(), "print", None, 0
    while i < len(argv):
        a = argv[i]
        if a == "--set":
            k, _, v = argv[i + 1].partition("=")
            if k not in INPUTS: sys.exit(f"unknown input '{k}' (see --list)")
            p[k] = type(INPUTS[k][0])(float(v)) if not isinstance(INPUTS[k][0], float) else float(v)
            i += 2
        elif a in ("--write", "--check"):
            mode, path, i = a[2:], argv[i + 1], i + 2
        elif a == "--list":
            for k, (v, lab, kind, _) in INPUTS.items(): print(f"{k:22s} {v!s:>8}  {lab} [{kind}]")
            sys.exit(0)
        else:
            sys.exit(__doc__)
    return p, mode, path
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && cp heatpump_model.py .ambition/before_step7_model.py && cp heat-pump-vs-gas-boiler.md .ambition/before_step7.md && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:70],s.count(a))\n    s=s.replace(a,b)\n\n# docstring\nrep('''  python3 heatpump_model.py --list                   list every input name\n … [5186 more chars]`

<details><summary>result</summary>

```
Exit code 1
You gave:      gas 12,800 kWh/yr | installer SCOP 3.4 | net price £8,200
VERDICT:       NO on a standard tariff; TOO CLOSE on a heat-pump tariff
Over 15 years vs keeping your boiler (negative = heat pump costs more):
  standard tariff:   -£2,600   (heat pump cheaper in 21% of 5,000 simulated futures)
  heat-pump tariff:    +£590   (heat pump cheaper in 73% of 5,000 simulated futures)
To break even on a heat-pump tariff you would need: SCOP 3.25 or more, a net price of £8,900 or less
This is a money-only forecast on typical tariffs; see heat-pump-vs-gas-boiler.md for the working and what could change it.
python3 -I heatpump_model.py --me --gas-kwh 12800 --scop 3.4 --price 8200  0.10s user 0.00s system 98% cpu 0.107 total
You gave:      gas 12,768 kWh/yr | installer SCOP 3.0 | net price £8,200
Typical used:  efficiency (SCOP), plus Ofgem Oct-Dec 2026 cap prices and the other assumptions in the report
VERDICT:       NO on a standard tariff; TOO CLOSE on a heat-pump tariff
Over 15 years vs keeping your boiler (negative = heat pump costs more):
--me needs at least one of --gas-kwh (or --gas-m3), --scop, --price
--scop needs a number
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\na=\"(yes = clearly cheaper over {H} years; close = within {money(VERDICT_BAND)}; no = clearly dearer)\"\nassert a in s\ns=s.replace(a,\"(yes = clearly cheaper over {H} years; close = too near to call, within {money(VERDICT_BAND)} or the simulation disagrees with the point estimate; no = clearly dearer)\")\nop … [2908 more chars]`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
python3 -I heatpump_model.py --write heat-pump-vs-gas-boiler.md  5.99s user 0.01s system 99% cpu 5.995 total
OK: file matches the model
PASS Grid cells equal the verdict the personal mode would give (70 cells)
PASS --me runs in under 10 seconds  [0.12s]
PASS --me verdict for a grid point matches the grid's heat-pump-tariff cell  [grid says close]
PASS --me with no numbers is refused politely
PASS --me with garbage is refused politely
PASS --me with an impossible value is refused politely
PASS --me warns for m3 entered as kWh
74/74 checks passed
[This command modified 3 files you've previously read: .ambition/judge/judge.py, heat-pump-vs-gas-boiler.md, heatpump_model.py. Call Read before editing.]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && diff <(sed -n '/## Using this with an installer quote/,/## When to re-check/p' .ambition/before_step7.md) <(sed -n '/## Using this with an installer quote/,/## When to re-check/p' heat-pump-vs-gas-boiler.md); echo ---; diff <(sed -n '1,/## Using this/p' .ambition/before_step7.md) <(sed -n '1,/## Using this/p' heat-pump-vs-gas-boiler.md) | head; grep -n \"Re-run i … [49 more chars]`

<details><summary>result</summary>

```
5c5
< **On a standard tariff** (yes = clearly cheaper over 15 years; close = within £1,000; no = clearly dearer)
---
> **On a standard tariff** (yes = clearly cheaper over 15 years; close = too near to call, within £1,000 or the simulation disagrees with the point estimate; no = clearly dearer)
12,14c12,14
< | 3.2 | no | no | no | no | no |
< | 3.5 | close | no | no | no | no |
< | 3.8 | close | close | no | no | no |
---
> | 3.2 | close | no | no | no | no |
> | 3.5 | close | close | no | no | no |
> | 3.8 | close | close | close | no | no |
17c17
< **On a heat-pump tariff** (yes = clearly cheaper over 15 years; close = within £1,000; no = clearly dearer)
---
> **On a heat-pump tariff** (yes = clearly cheaper over 15 years; close = too near to call, within £1,000 or the simulation disagrees with the point estimate; no = clearly dearer)
21,25c21,25
< | 2.6 | no | no | no | no | no |
< | 2.8 | close | no | no | no | no |
< | 3.0 | close | close | no | no | no |
< | 3.2 | yes | close | close | no | no |
< | 3.5 | yes | yes | close | close | no |
---
> | 2.6 | close | no | no | no | no |
> | 2.8 | close | close | no | no | no |
> | 3.0 | close | close | close | no | no |
> | 3.2 | yes | close | close | close | no |
> | 3.5 | yes | yes | close | close | close |
---
3:*Typical English 3-bed semi on the Ofgem price cap (Oct-Dec 2026). Prices and efficiency come from the sources at the bottom; everything else is a flagged assumption. Every figure below is generated by `heatpump_model.py`, so you can change an input and regenerate the file (see 'Re-run it').*
4-
5-*Who this is for: an owner-occupier in England with a mains-gas boiler and a wet (radiator) system, deciding on money. It will mislead you if your home is off the gas grid, is a flat, is in Scotland, Wales or Northern Ireland, or if carbon, comfort or future boiler rules matter more to you than cost. Figures are rounded: this is a forecast, not a quote.*
6-
7-*In plain terms: **SCOP** is how many units of heat a h … [883 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && grep -n \"\\-\\-me\" heat-pump-vs-gas-boiler.md | head -4; mkdir -p .ambition/steps/7 && cp heat-pump-vs-gas-boiler.md heatpump_model.py .ambition/steps/7/ && ls .ambition/steps/7"}`

<details><summary>result</summary>

```
208:python3 heatpump_model.py --me --gas-kwh 12800 --scop 3.4 --price 8200   # your verdict from up to three numbers
209:python3 heatpump_model.py --me --gas-m3 1140 --price 8200               # meter in cubic metres; SCOP left typical
heat-pump-vs-gas-boiler.md
heatpump_model.py
```

</details>

### Assistant

**Step 7 report: Stretch**

**Did:** I met the stretch target. `python3 heatpump_model.py --me --gas-kwh 12800 --scop 3.4 --price 8200` now gives your own verdict from up to three numbers in about 0.1 seconds. The target was under 10 seconds. It accepts gas in m³ (`--gas-m3`) as well as kWh.
- **Output:** it prints the verdict, the 15-year result on each tariff, how often the heat pump wins across the 5,000 simulated futures, and the SCOP and price you'd need to break even.
- **Where it's documented:** the file's "Re-run it" section shows the command.
- **Fallback:** the `--set` mode, the full report and the earlier steps' checks all still work.

**Found:**
- **A consistency bug:** the quote grids and the headline verdict used different rules. A quote could be "yes" in the grid but "too close" in the personal verdict. The grids now use the same rule, and the checker confirms all 70 cells match.
- **Effect on the grids:** they are more cautious. For example, SCOP 3.2 at £5,500 on a standard tariff moved from "no" to "close". Page one is unchanged.
- **Cost:** regenerating the full report now takes about 6 seconds instead of 0.1, because every grid cell runs its own simulation. The personal mode is unaffected.
- **Checker:** it now has 74 checks and all pass. The new ones cover:
  - the m³ conversion
  - the speed
  - polite refusals of missing, garbage or impossible inputs
  - the warning when m³ is entered as kWh

**Where it would break:**
- **Fixed deals:** the shortcut assumes the Ofgem cap prices. If you're on a fixed deal, you'll need `--set` to enter your own rates.
- **The 11.2 m³ conversion:** it is an approximation that varies slightly by supplier.
- **SCOP quality:** the verdict is only as good as the SCOP the installer predicts.
- **Not attempted:** predicting a SCOP from a home's flow temperature. I had no data to check it against.

I saved a copy to `.ambition/steps/7/`.

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

Run started: 2026-11-13T01:31:37Z
Metrics command for the end: python3 /plugin/scripts/ambition-metrics.py 4127e89e-eef0-4f60-bb1a-4c8caf8427a6 --since 2026-11-13T01:31:37Z

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

This is a build, so I'll skip plan approval. I'll make the file stand alone (no process story, each thing said once) and add the open decisions with owners and dates. Then I'll lock in the checker, a short `CLAUDE.md` and one project command. First, the section of the generator I need to rewrite.

**→ Bash** `{"command": "cd \"<workspace>\" && grep -n \"What I checked against evidence\\|What a heat-pump tariff really costs\\|Rule of thumb\\|## Limits\\|## Re-run it\\|## Script output\\|## Plain-English\" heatpump_model.py && sed -n '/Rule of thumb/,/+2p' heatpump_model.py | head -4"}`

<details><summary>result</summary>

```
457:    o.append("Rule of thumb: ask installers for a written heat-loss calculation and a predicted SCOP. If it is below the SCOP "
518:    o.append("## What I checked against evidence\n")
534:    o.append("**What a heat-pump tariff really costs depends on when you use power.** Octopus Cosy's cheap rate is 49% of the day rate and its peak is 150%, with cheap windows 4-7am, 1-4pm and 10pm-midnight and peak 4-7pm:\n")
564:    o.append("## Plain-English glossary\n")
577:    o.append("## Limits\n")
581:    o.append("## Re-run it\n")
590:    o.append("## Script output (verbatim)\n")
sed: 1: "/Rule of thumb/,/+2p
": unterminated regular expression
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && sed -n 455,460p heatpump_model.py && sed -n 516,534p heatpump_model.py && sed -n 575,592p heatpump_model.py"}`

<details><summary>result</summary>

```
    o.append(f"The simulation below says the three things that move the result most are: {top[0]}, {top[1]}, and {top[2]}. "
             "Of all the inputs, efficiency and tariff price can be pinned down before you buy; future fuel prices can't.\n")
    o.append("Rule of thumb: ask installers for a written heat-loss calculation and a predicted SCOP. If it is below the SCOP "
             "in the first row, the heat pump is unlikely to pay back on running costs alone.\n")

    o.append(f"## The {H}-year picture\n")


    o.append("## What I checked against evidence\n")
    o.append("Each main assumption was tested against source material. Items marked **Changed** replaced my starting estimate in all the figures above.\n")
    mk = lambda **kw: run({**p, **kw}, "hp")["adv"]
    ratio = p["elec_unit"] * (1 + p["elec_vat"]) / p["gas_unit"]
    o.append("| Starting assumption | What the evidence says | Result |")
    o.append("|---|---|---|")
    o.append(f"| Electricity price stays at the published 26.32p | [Ofgem](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026): that rate excludes VAT, and VAT is removed only until 31 March 2027. With VAT it is {p['elec_unit']*1.05*100:.2f}p, so the electricity-to-gas price ratio is {p['elec_unit']*1.05/p['gas_unit']:.2f}, not {p['elec_unit']/p['gas_unit']:.2f}. | **Changed.** Treating a six-month tax holiday as permanent would flatter the heat pump for 15 years, so the base adds 5% VAT back. The holiday made permanent is shown as a row in the drivers table. |")
    o.append(f"| A typical home uses 9,500 kWh of gas | The government's [NEED dataset](https://www.gov.uk/government/statistics/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026-accessible-webpage) puts the 2024 median for all homes in England and Wales at 10,000 kWh and the mean at 11,200 kWh. It gives no figure for semi-d … [4030 more chars]
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:70],s.count(a))\n    s=s.replace(a,b)\n\n# remove duplicated rule of thumb\ni=s.index('    o.append(\"Rule of thumb: ask installers'); j=s.index('    o.append(f\"## The {H}-year picture\\\\n\")')\ns=s[:i]+\"\\n\"+s[j:]\n\n# evidence section -> stand-al … [6839 more chars]`

<details><summary>result</summary>

```
wrote heat-pump-vs-gas-boiler.md
[This command modified 2 files you've previously read: heat-pump-vs-gas-boiler.md, heatpump_model.py. Call Read before editing.]
```

</details>

### Assistant

Three figures in the decisions table are hard-coded, and they'd go stale if inputs change. I'll make them computed, then lock the checker in beside the deliverable with updated expectations.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\ns=open('heatpump_model.py').read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,(a[:70],s.count(a))\n    s=s.replace(a,b)\nrep('''    o.append(\"| 2 | If you proceed: which tariff? | A. Standard tariff. B. Heat-pump or time-of-use tariff. | A: simple, but about \u00a34,100 worse off over 15 years at current prices.''','''    keep_cost … [1916 more chars]`

<details><summary>result</summary>

```
hile you learn how the heat pump performs. | B, then disconnect if the first winter goes well. | You | 31 Mar 2028, if installed in 2027 |")
wrote heat-pump-vs-gas-boiler.md
39:| 1 | £1,050 | £8,500 | -£7,450 | £8,350 | -£7,300 |
40:| 2 | £2,100 | £9,550 | -£7,450 | £9,200 | -£7,100 |
41:| 3 | £3,200 | £10,600 | -£7,400 | £10,100 | -£6,900 |
113:| 1 | Buy a heat pump to save money? | A. Keep the boiler and revisit when it fails. B. Collect 2-3 quotes, then decide using the quote grids. C. Commit now. | A: costs nothing and loses nothing on today's figures, but the grant may end. B: a few hours' wo
114:| 2 | If you proceed: which tariff? | A. Standard tariff. B. Heat-pump or time-of-use tariff. | A: simple, but £4,100 worse off over 15 years at current prices. B: cheaper only if the heat pump runs mostly in the cheap windows; rates vary by region. | B, o
115:| 3 | Disconnect gas after installing? | A. Disconnect at once. B. Keep it connected through the first winter. | A: stops the standing charge (about £110 a year) but needs an electric hob and removes the fallback. B: costs about £1,300 over 15 years on a s
[This command modified 2 files you've previously read: heat-pump-vs-gas-boiler.md, heatpump_model.py. Call Read before editing.]
```

</details>

### Assistant

Now to lock in the checker, the `CLAUDE.md` note and the project command. I'll update the checker's expectations for the restructured sections first.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\nj=open('.ambition/judge/judge.py').read()\nj=j.replace('\"## When to re-check\", \"## What I checked against evidence\"','\"## Decisions and next checks\", \"## Evidence behind the key inputs\"')\nj=j.replace('for bad in (\"my first version\",','for bad in (\"Rule of thumb\", \"What I checked\", \"Starting assumption\", \"starting estimate\", \ … [2885 more chars]`

<details><summary>result</summary>

```
OK: file matches the model
84/84 checks passed
```

</details>

### Assistant

All 84 checks pass. One last scan for leftover process language, then I'll save the step copy.

**→ Bash** `{"command": "cd \"<workspace>\" && grep -n -i \"earlier version\\|first version\\|originally\\|used to\\|previously\\|changed to\\|step [0-9]\" heat-pump-vs-gas-boiler.md | head; sed -n '/## Decisions and next checks/,/## Evidence behind/p' heat-pump-vs-gas-boiler.md | cut -c1-200; mkdir -p .ambition/steps/8 && cp heat-pump-vs-gas-boiler.md heatpump_model.py check_report.py CLAUDE.md .ambition/ste … [37 more chars]`

<details><summary>result</summary>

```
171:| Boiler lifespan (years) | 15 | ASSUMPTION | Used to credit remaining life at the end of the period. |
## Decisions and next checks

| # | Decision | Options | For / against | Pick | Owner | Decide by |
|---|---|---|---|---|---|---|
| 1 | Buy a heat pump to save money? | A. Keep the boiler and revisit when it fails. B. Collect 2-3 quotes, then decide using the quote grids. C. Commit now. | A: costs nothing and loses nothing on to
| 2 | If you proceed: which tariff? | A. Standard tariff. B. Heat-pump or time-of-use tariff. | A: simple, but £4,100 worse off over 15 years at current prices. B: cheaper only if the heat pump runs m
| 3 | Disconnect gas after installing? | A. Disconnect at once. B. Keep it connected through the first winter. | A: stops the standing charge (about £110 a year) but needs an electric hob and removes 

| Next check | Owner | Date |
|---|---|---|
| Replace the typical gas use with your own: `--me --gas-kwh <last 12 months from your bills>` | You | 20 Nov 2026 |
| Re-run with the January-March price cap (Ofgem confirmation reported due by 25 November) | You | 27 Nov 2026 |
| Test each installer quote (heat-loss calculation, predicted SCOP at your design flow temperature, price after grant, radiators and cylinder included) in the quote grids, then with `--me` | You | 31 
| Electricity VAT holiday ends 31 March 2027 unless extended; if extended, set `elec_vat=0` and re-run | You | 7 Apr 2027 |
| If your boiler fails before you decide, set `boiler_replace_year=0` and re-run; that is the case most favourable to the heat pump | You | When it happens |
| On a fixed-price deal, enter your own unit rates with `--set` | You | When you have the quotes |

## Evidence behind the key inputs
check_report.py
CLAUDE.md
heat-pump-vs-gas-boiler.md
heatpump_model.py
__pycache__
check_report.py
CLAUDE.md
heat-pump-vs-gas-boiler.md
heatpump_model.py
```

</details>

**→ Bash** `{"command": "cd \"<workspace>\" && rm -rf __pycache__ && python3 /plugin/scripts/ambition-metrics.py 4127e89e-eef0-4f60-bb1a-4c8caf8427a6 --since 2026-11-13T01:31:37Z"}`

<details><summary>result</summary>

```
Metrics since 2026-11-13T01:31:37Z (cost: /cost, or total_cost_usd in headless JSON)
total   in 166 · out 129.8k (think 54.0k) · cache read 10.75M · write 228.6k · hit 98% · 77 calls
model   sonnet-5-5: in 166 · out 129.8k (think 54.0k) · cache read 10.75M · write 228.6k · hit 98% · 77 calls
```

</details>

### Assistant

I've finished all eight steps. Your own verdict now takes one command and about 0.1 seconds: `python3 heatpump_model.py --me --gas-kwh N --scop X --price P`.

**On typical figures for a 3-bed semi in England, the heat pump doesn't save money.** On a standard tariff it is about £4,100 worse off after 15 years, and the simulation agrees in 94% of 5,000 runs. On a heat-pump tariff it is too close to call (about £1,150 worse off).

## You asked for → it became
- **"Would a heat pump save me money?"** became a yes / no / too-close verdict with confidence. It also gives the efficiency, price and gas use at which it would flip, and a 15-year comparison that includes when the boiler would need replacing.
- **"As a Markdown file"** stayed one file, `heat-pump-vs-gas-boiler.md`, with the verdict first and the script's output pasted at the bottom. A recompute script now sits beside it.
- **"My gas boiler"** became a typical English 3-bed semi on the Ofgem price cap, as you specified. You can swap in your own gas use, SCOP and price with `--me`.

## Against the first version
- **Better:** the first version had no verdict at the top, no source links, no regenerable numbers and only two flagged assumptions. The final has all of those, plus tested thresholds, quote-checking grids, decisions and next checks.
- **Gave up:** length. The file went from about 900 to about 4,200 words, though page one stays under 300 words and the rest is reference.
- **Check on both:** the same checks found the first version failing the verdict-first, sources and regenerable-numbers tests. The final passes all 84.

## Outside check
`check_report.py` ran 84 checks and all pass. They include:
- An independent reimplementation of the cost model that matches to the penny across six input sets and both tariffs.
- The pasted output matching a fresh run.
- Ofgem's £1,723 typical bill reproduced within £1, and Nesta's published parity result.
- Every source link loading.
- A cold read of the whole file.

It caught a real bug in the break-even price, which is now fixed. Source checks also made me correct three claims I had overstated.

## Stretch
The target was a personal verdict from three numbers, in under 10 seconds. It reached about 0.1 seconds, and `--gas-m3` handles meter readings. It breaks on fixed-price deals, where you need `--set` to enter your own rates, and I couldn't predict SCOP from flow temperature without data to check it against.

## Locked in
In `<workspace>`:
- `heat-pump-vs-gas-boiler.md`: the deliverable.
- `heatpump_model.py`: the model that generates it.
- `check_report.py`: the independent checks.
- `CLAUDE.md`: how to rerun and what counts as done.
- `.claude/commands/heat-pump.md`: the `/heat-pump` command.

To rerun everything, use `python3 heatpump_model.py --write heat-pump-vs-gas-boiler.md`, then `--check`, then `python3 -I check_report.py heat-pump-vs-gas-boiler.md heatpump_model.py`. A copy of each step is in `.ambition/steps/`, and the first version is in `.ambition/first/`.

## Assumptions made
I used your instruction to finish without stopping. The assumptions are flagged in the file's assumptions table:
- 10,500 kWh of gas a year.
- SCOP 3.0.
- A heat-pump tariff at 80% of the standard rate.
- A £2,500 replacement boiler replaced in year 5.
- Both fuels rising 3% a year.
- 5% VAT on electricity from April 2027.

## Decisions
All three are in the file with owners and dates. The most urgent is the first.

1. **Whether to buy.** The options are:
   - Keep the boiler and revisit when it fails.
   - Collect 2–3 quotes first.
   - Commit now.

   Keeping the boiler costs nothing but the grant may end. Quotes turn the two biggest unknowns into facts. Committing now stakes £7,500 on typical figures. I'd collect quotes, and default to keeping the boiler unless a quote lands in a "yes" cell. You decide by 31 January 2027.
2. **Tariff, if you proceed.** A standard tariff is simple but about £4,100 worse off. A heat-pump tariff is cheaper only if the heat pump runs mostly in the cheap windows. I'd choose the heat-pump tariff, but only with the installer's written plan for when the heat pump runs. You decide by 31 January 2027.
3. **Disconnecting gas.** Disconnecting at once stops the standing charge (about £110 a year) but removes your fallback. Keeping it costs about £1,300 over 15 years if kept for good. I'd keep it through the first winter, then disconnect if the heat pump performs well. You decide by 31 March 2028, if installed in 2027.

Your first next check is to run `--me` with your real gas kWh from your last 12 months of bills, by 20 November 2026.

## Metrics
```
Metrics since 2026-11-13T01:31:37Z (cost: /cost, or total_cost_usd in headless JSON)
total   in 166 · out 129.8k (think 54.0k) · cache read 10.75M · write 228.6k · hit 98% · 77 calls
model   sonnet-5-5: in 166 · out 129.8k (think 54.0k) · cache read 10.75M · write 228.6k · hit 98% · 77 calls
```
