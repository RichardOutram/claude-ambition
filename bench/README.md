# bench: testing the ambition plugin against a plain prompt

`ab.py` runs the same prompt on the same model, under the same conditions, once plainly and once through `/be-ambitious`. It saves everything (outputs, transcripts, exact cost and time per turn) and captures the same evidence for every version. People make the call, not a model judge. Plain Python 3; runs happen in Docker.

```sh
python3 bench/ab.py list                                                # examples and fixture status
python3 bench/ab.py run threejs/neon-implosion --arms not-ambitious     # the baseline, once per example
python3 bench/ab.py run threejs/neon-implosion --arms ambitious         # one plugin run, the same prompt
python3 bench/ab.py review threejs/neon-implosion                       # frames, seam, errors, screenshots, Lighthouse
python3 bench/ab.py verdict threejs/neon-implosion --run 1 --gate pass --result win \
    --preview yes --push no --note "One or two sentences on why." --notes review.md
python3 bench/ab.py report                                              # examples/RESULTS.md and the site in docs/
```

Examples are defined in [`examples/PROMPTS.md`](../examples/PROMPTS.md).

## How the plugin is tested

- **One baseline per example.** One plain run of the prompt on Opus 5.5 (`not-ambitious/run-1`), made in the container, is the fixed bar.
- **Single plugin runs.** Each `/be-ambitious` run gets the *same prompt*, word for word. The only difference is the plugin.
- **The first-turn gate.** `/be-ambitious` starts with a cheap first version (the `ambition-direct` agent, in `.ambition/direct/`) and stops at a checkpoint: stop here, or push it further. That first version must already be at least as good as the baseline. We watch each run at the end of turn 1, and if the first version is worse, we stop the run and it's a fail.
- **The bar.** The final must beat the baseline. Faster and cheaper counts in the baseline's favour, so the plugin has to win on quality by enough to justify its cost. We also ask separately whether the preview was worth its cost, and whether pushing on was.
- **Judged by people.** Claude reviews harshly, side by side and live, with the genre bar first and the goal second, then cost and time. The user decides. `verdict` records that decision.
- **Only the current plugin counts.** Every run records the plugin version it used (`plugin` in `metrics.json`: commit, uncommitted changes, and a hash of the plugin's files). The report marks runs from an older plugin as outdated. Clear outdated examples rather than keep them.

## What keeps it fair

- **Identical conditions.** Both arms get the same model, effort, tools, turn limit, settings and container image. Each run gets a fresh throwaway container (`bench/docker/`) with a fresh empty folder as `/work`. The ambitious arm also gets the plugin's own parts, read-only, and nothing else. No run can see the bench, the prompts, the baseline or another arm's output.
- **Runs can see their work.** The image has Chromium (Playwright), Node, Python and git, and every Bash command is allowed, so a run can install packages, serve its page and screenshot it, the way Claude can on your machine. A bench where runs can't look at their work isn't testing Claude as people use it. The container is the boundary; there's no Claude Code sandbox inside it.
- **The same stand-in user.** After every turn, a client (Sonnet, no tools) decides whether the reply is waiting on the user. It knows only the prompt, never the brief. It approves restatements, answers the checkpoint with "Push it further.", and answers anything else with "I don't mind. Use your best judgement, and please finish the work without stopping." Both arms get exactly the same information.
- **Real time and real cost.** Minutes are wall-clock time, including the stand-in's replies (`wall_ms`). `exchange_log` records the cumulative minutes and cost at the end of each turn, so turn 1 is the preview's cost. A resumed session reports its cost and usage cumulatively, so a run's totals are its last turn's figures. The headless JSON's own `duration_ms` and `num_turns` undercount runs with several exchanges and subagents.

## Review evidence

`review` captures every version the same way: the baseline, each ambitious run's first version (`.ambition/direct/`) and final, and the work at the end of each saved turn. Into `run-<n>/review/<baseline|first|final|turn-N>/`. Two captures run at a time, and a turn that left the first version or the final unchanged reuses that capture:

- **Frames across time.** Inside the container, `review/capture.mjs` opens the page at desktop (1280×800) and phone (390×844 @2x) sizes and takes a frame every second. Time is virtual and stepped at 30 fps, so frame t=4 really is 4 seconds in, however slow software rendering is. The length comes from the prompt ("10 second") or `--seconds`.
- **A seam check.** For anything that moves, the last frame is compared with the first, against a typical step between frames. A seamless loop ends where it began.
- **Console errors**, per size.
- **Contact sheets** of the frames, for side-by-side viewing.

`review` also runs `measure()` on the host for every HTML page, into `run-<n>/checks/`: a Lighthouse audit (mobile, 375px) and screenshots at 375px and 1280px. That needs Chrome and `npx`.

None of this decides anything. It's what we look at, beside the live pages.

## Results page and site

`report` writes:

- [`examples/RESULTS.md`](../examples/RESULTS.md): one row per example with the verdict, the gate, the baseline's cost and time, the preview's (turn 1), the full run's and the plugin version.
- `docs/`: the GitHub Pages site (Settings → Pages → deploy from `main`, folder `/docs`). Each example page shows Baseline | First version | Final side by side, with frame sheets, the seam and error checks, Lighthouse, and each version live. Below that: our review, cost and time by turn, how the run restated the task, and every reply and file. It's static HTML, generated in full on every build, with the site's own CSS and JS in `bench/site/`. Never edit `docs/` by hand.

## Setup

Runs need Docker and a token:

```sh
claude setup-token                     # prints a long-lived token
echo 'CLAUDE_CODE_OAUTH_TOKEN=<token>' > bench/.env
```

`bench/.env` is gitignored. Every run uses an empty config folder (`bench/.home/`, also gitignored). The image is built on first use and pins the claude version in its tag, matched to the host. Each run's `metrics.json` records `isolation: docker`. `--host` runs on the host in Claude Code's sandbox, with no browser; it's only for debugging the harness, never for results.

While a run is going, `run-<n>/live` links to its working folder, so you can watch it.

## Output

```
examples/<model>/<category>/<name>/
  spec.json            the prompt, brief and check this example ran with
  <arm>/run-<n>/
    prompt.md          every message sent from the user side (the prompt and the stand-in's replies)
    result.md          Claude's final reply
    output/            the files it produced (for ambitious runs, .ambition/direct/ is the first version)
    turns/turn-<n>/    the work as it stood at the end of each turn that changed it
    transcript.md      readable history, including tool calls
    transcript/        raw session and subagent transcripts (scrubbed)
    metrics.json       cost, tokens per model, time, exchange_log, plugin version, isolation, permission denials
    metrics.txt        the same one-glance format as /be-ambitious
    checks/            Lighthouse and screenshots for HTML pages
    review/            frames, contact sheets and capture.json per version
    verdict.json       our decision (ambitious runs, after review)
    review.md          our side-by-side review, if written
```

Saved work leaves out dependencies, screenshot and tooling folders, and images inside `.ambition/` (where the run and its judge keep their looks at the work), for every arm alike. Before saving, transcripts are scrubbed: your home path becomes `~`, the workspace path becomes `<workspace>`, email addresses are replaced, tokens are redacted, and images the run looked at are replaced by a note.

## Fixtures

Examples marked *(fixture: …)* need files in `examples/fixtures/<category>/<name>/`:

- `public/` is copied into each arm's workspace.
- `hidden/` holds the ground truth, for checking only.
- `generate.py` (optional) creates both. It runs once, then the result is cached.

`list` shows which fixtures are still missing.
