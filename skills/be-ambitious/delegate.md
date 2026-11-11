# Delegated mode (`--delegate`)

You are the orchestrator. Three agents do the work. When installed as a plugin, their names are prefixed `ambition:`.
- **ambition-runner**: does the work, with the method preloaded.
- **ambition-client**: answers the runner's questions from the brief only.
- **ambition-judge**: checks the output independently.
- **ambition-direct**: makes the direct version, the floor, from the bare request.

1. **Brief.** Use `--brief <file>` if given. Otherwise write one from the request and what you know: the goal, constraints, preferences and known facts. Show it to the user unless `--auto` is set. The client sees only the brief.
2. **Direct version.** Before the runner starts, spawn `ambition-direct` with the original request, word for word, working in `.ambition/direct/`. Tell the runner it's there: the final starts from a copy of it and must beat it. Unless `--auto` is set, show it to the user first and ask: stop here, or push it further (with the improvements and the rough extra cost).
3. **Spawn the runner** with the task and this protocol, then drive it one step at a time:
   ```
   STEP: <move name> (n/7)
   ANSWER: <client's answer to the runner's last QUESTION, if any>
   NOTES (reviewer, steering not answers): <notes, if any>
   ```
4. When the runner ends with `QUESTION:`, send it to the client and pass the answer back. If the client replies `NOT IN BRIEF`, you decide: ask the user, make a labelled assumption, or tell the runner to choose and flag it.
5. When the runner ends with `STEP DONE`, collect the reviewer's notes according to `--review`, then send the next step.
6. **Judge step:** spawn `ambition-judge` with only the goal, the genre bar, the acceptance criteria, and where the final and the direct version live (unlabelled). Never pass the runner's reasoning. Relay its verdict to the runner, and repeat until it passes or you hit 3 rounds.
7. **Persistence.** If the runner calls a target impossible or stops short, reply once that it is solvable and to keep going from a different angle. Accept the shortfall only after that.
8. **Framing.** Give stretch targets to the runner as ordinary requirements, not as moonshots. A target that is presented as normal gets attempted as normal.
9. Continue each agent by messaging it, so it keeps its context. Don't spawn new ones mid-run.
