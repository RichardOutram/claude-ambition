# bench: A/B testing the ambition plugin

`ab.py` runs the same prompt on the same model, under the same conditions, with and without the plugin. It saves everything (outputs, transcripts, exact cost) and has a blind judge pick the better result. Plain Python 3, no dependencies.

```sh
python3 bench/ab.py list                                  # examples and fixture status
python3 bench/ab.py run design/bakery-landing             # all three arms, one run each
python3 bench/ab.py run planning --runs 3 --parallel 3    # a whole category, three runs per arm
python3 bench/ab.py judge design/bakery-landing           # blind pairwise judging
python3 bench/ab.py report                                # examples/<model>/REPORT.md
```

Examples are defined in [`examples/PROMPTS.md`](../examples/PROMPTS.md). Add one by adding a `### category/name` block with **Prompt**, **Brief** and **Check**.

## The arms

| Arm | What Claude receives |
|---|---|
| `not-ambitious` | The prompt, exactly as written |
| `briefed` | The prompt plus the brief: what the user knew but didn't type |
| `ambitious` | `/be-ambitious <prompt>`, with the plugin loaded |

`briefed` is the control. Without it, a win for `ambitious` could just mean "the interview extracted more information". With it, you can see whether the method itself adds anything.

## What keeps it fair

- **Identical conditions.** Every arm gets the same model, effort, tools, turn limit, permission settings and sandbox, and a fresh empty folder outside this repo. No run can see the plugin source, the prompts or another arm's output. The only difference is `--plugin-dir` on the ambitious arm.
- **The same answerer.** After every turn, a brief-only client (Sonnet, no tools) decides whether the reply is waiting on the user. If it is, the client answers from the brief and the session resumes, up to `--max-exchanges`. All arms are treated the same way, so a plain run that asks a question gets an answer too.
- **A blind judge.**
  - The judge is a fresh session on the same model.
  - It sees only the request, the brief, the check, and each output relabelled A or B. It never sees transcripts.
  - Plugin-identifying words are stripped from the final messages.
  - It runs the objective checks, then scores the rubric.
  - Each pair is judged twice with the labels swapped. If the two verdicts disagree, the result is a tie.
- **Repeats.** Use `--runs 3` for anything you publish. One run can be luck.

Known limit: the ambitious output can still be recognisable from its structure, for example a restated goal or a named outside check. The swapped-order judging and the objective checks are the defence against that.

## Clean runs (recommended for published examples)

By default, the runs use your normal Claude Code config. Both arms are still identical, but your own CLAUDE.md and user-level commands load into both. For pristine runs, create a token once:

```sh
claude setup-token                     # prints a long-lived token
echo 'CLAUDE_CODE_OAUTH_TOKEN=<token>' > bench/.env
```

`bench/.env` is gitignored. With a token, every run uses an empty config folder (`bench/.home/`, also gitignored). Each run's `metrics.json` records which mode was used in `isolation`.

## Safety

- Runs auto-accept file edits.
- Bash runs inside Claude Code's OS sandbox, so writes are confined to the run's temp folder.
- Network access is limited to package registries and GitHub. On macOS, sandboxed commands may also start and reach local servers (`allowLocalBinding`), so outside checks can spin up test servers. Those commands can then also reach other services on your localhost.
- `--max-turns` caps each session.
- Nothing runs in this repo's folder.

## Output

```
examples/<model>/<category>/<name>/
  <arm>/run-<n>/
    prompt.md          every message sent from the user side (prompt + client replies)
    result.md          Claude's final reply
    output/            files it produced
    transcript.md      readable history, including tool calls
    transcript/        raw session + subagent transcripts (scrubbed)
    metrics.json       exact cost, tokens per model, turns, time, versions, isolation mode
    metrics.txt        the same one-glance format as /be-ambitious
  judge/<x>-vs-<y>/run-<n>/
    order-1-judge.md   the judge's full reasoning (which arm was A is noted at the top)
    order-2-judge.md
    verdict.json       final winner: an agreed winner, or a tie
```

Before saving, transcripts are scrubbed: your home path becomes `~`, the workspace path becomes `<workspace>`, email addresses are replaced and tokens are redacted.

## Fixtures

Examples marked *(fixture: …)* need files in `examples/fixtures/<category>/<name>/`:

- `public/` is copied into each arm's workspace.
- `hidden/` holds the ground truth, and only the judge sees it.
- `generate.py` (optional) creates both. It runs once, then the result is cached.

`list` shows which fixtures are still missing.

## Prerequisites for some checks

The electronics examples need `ngspice`, and the Arduino one also needs `arduino-cli`. The design examples benefit from Chrome being installed for Lighthouse. Install them with Homebrew before judging those examples.
