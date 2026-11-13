The prototype is finished and passes every check. It's `prototype.html` in `<workspace>`; the final copy is in `.ambition/steps/8/`.

This session was in build mode, so I did not write a separate plan document for approval. You didn't ask for a run log either, so I didn't write one.

## You asked for → it became
- **A clickable prototype of the app in plan.md, as a single HTML file → the same single file.**
  - **Altitude:** a rider or investor can get from sign-in to XP, the badge and a challenge check with no help.
  - **Depth:** I measured the build with accessibility, tap-target and data-consistency checks.
  - **Challenge:** testing found and fixed six broken assumptions.
  - **Range:** it picked up an in-app session log, destructive-action guards, and fixes for the harms the red-team pass found.
  - **Stretch:** a 5-tap path and a 4,000-action fuzz.
- **Original ask:** all 44 MVP items from plan.md are in. The original build covered 29 on the same fixed check.

## Against the first version
- **Better on:**
  - **Core loop:** 7 taps down to 5, and the app now explains XP.
  - **Accessibility:** 17 axe violations down to 0.
  - **Tap targets:** 42 controls under 44 px down to 0.
  - **Dead taps:** 19 down to 15, all re-taps of the tab or segment you're already on.
  - **Hostile input:** typed text could run as live markup, and now can't.
  - **Reward sheet:** it adds up and shows the next goal.
  - **Recording:** the ride is believable, with a session log for facilitators.
- **Gave up:** nothing I could measure. Visuals are broadly the same, the controls are somewhat larger, and the orange button fill is a darker shade for contrast.
- **First version:** it passes the neutral core loop. Its failures are the numbers above.

## Outside check
`sh checks/run.sh` ends with ALL CHECKS PASSED:
- **Scripted suites:** flow 14, consistency 5, probe 8, redteam 18, fixes 11 passed, and none failed.
- **Quality checks:** axe 0, tap targets under 44 px 0, overflow 0, console errors 0, MVP coverage 44/44.
- **Broken-build control:** a deliberately broken build makes it print CHECKS FAILED.
- **Cold read and render:** I read the text of every screen and looked at rendered screens at 375×667.

## Stretch
- **Target:** cold open to the challenge screen in 5 taps and under 9 s, with a driver that taps only the most prominent button, plus 1,800 clean fuzz actions.
- **Result:** both met. The 5-tap path takes about 4.8 s, and the fuzz ran 4,000 actions with no bugs.
- **Where it broke:** the fuzz can't test the distance and climb challenge caps, because its rides are too short. It also takes about 4 minutes, so it's not in the default run.

## Locked in
- **`checks/`:** 11 check scripts, `run.sh`, `package.json` and a README.
- **`CLAUDE.md`:** how to run the checks and the open decisions.
- **`.claude/commands/check-prototype.md`:** a project command that runs the checks.
- **`rider-test-script.md`:** seven tasks, an observation sheet and a pass bar.
- **Rerun:** `cd checks && npm install` the first time, then `sh checks/run.sh` (add `../prototype.html fuzz` as arguments for the fuzz). Set `CHROME=/path` if Chrome isn't in the macOS default location.

## Assumptions made
You answered every question yourself, and when you said "proceed" I used these defaults:
- The numbers are placeholders: 8 XP/km, 500 XP per level, a 20 XP weekly bonus, freeze tokens earned by completing a challenge, and $5.99/$39.99 pricing. plan.md sets none of them.
- Photos are gradient placeholders, and maps are generated line drawings.

## Decisions left (owner: you)
1. **Real XP, level and price values**
   - **Options:** keep the placeholders; set values from a rules table; test them in the beta.
   - **For and against:** placeholders keep rider sessions about flow, but they can't tell you about pricing.
   - **My pick:** keep the placeholders until riders have used it, and decide by 2026-11-27.
2. **How freeze tokens are earned**
   - **Options:** earned by completing a challenge, bought with XP, or a mix.
   - **For and against:** earning is simple and keeps level and spending separate. Buying cost a level in testing.
   - **My pick:** earned. Confirm by 2026-11-20.
3. **The free versus Pro club boundary** (plan.md's own growth risk)
   - **Options:** basic clubs free, admin tools Pro (current); or gate more.
   - **For and against:** keeping it free helps growth, but gives away less to monetise.
   - **My pick:** keep it, and watch it in rider sessions. Decide by 2026-11-27.
4. **Next check:** run 3–5 rider sessions with `rider-test-script.md` and read each Session log, by 2026-11-20.

**Not checked:** real riders, real phones, and any browser other than Chrome.

```
Metrics since 2026-11-13T03:14:39Z (cost: /cost, or total_cost_usd in headless JSON)
total   in 158 · out 123.1k (think 40.9k) · cache read 9.06M · write 197.8k · hit 98% · 71 calls
model   sonnet-5-5: in 158 · out 123.1k (think 40.9k) · cache read 9.06M · write 197.8k · hit 98% · 74 calls
```