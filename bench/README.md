# bench: testing the ambition plugin against a plain prompt

`ab.py` runs the same prompt on the same model, under the same conditions, once plainly and once through `/be-ambitious`. It saves everything (outputs, transcripts, exact cost and time per turn) and captures the same evidence for every version. People make the call, not a model judge. Plain Python 3; each run happens in a fresh macOS VM (Tart).

```sh
python3 bench/ab.py list                                                # examples and fixture status
python3 bench/ab.py run threejs/neon-implosion --arms not-ambitious     # the baseline, once per example
python3 bench/ab.py run threejs/neon-implosion --arms ambitious         # one plugin run, the same prompt
python3 bench/ab.py review threejs/neon-implosion                       # frames, seam, errors, screenshots, Lighthouse
python3 bench/ab.py verdict threejs/neon-implosion --run 1 --result win \
    --preview yes --push no --note "One or two sentences on why." --notes review.md
python3 bench/ab.py report                                              # examples/RESULTS.md and the site in docs/
```

Examples are defined in [`examples/PROMPTS.md`](../examples/PROMPTS.md).

## How the plugin is tested

- **One baseline per example.** One plain run of the prompt (`not-ambitious/run-1`), made in the bench VM, is the fixed bar. When plain Claude is done, the same chat gets `Push it further.`, the words the plugin arm sends at its checkpoint, still with no plugin. That second turn is the **plain push**: what a user gets by just asking for more. Both are kept: the plain answer in `output/.plain/first/` (saved on the host, so the push never sees it) and the plain push in `output/`.
- **Single plugin runs.** Each `/be-ambitious` run gets the *same prompt*, word for word, after the unseen arming message. The only difference is the plugin.
- **The first-turn gate.** The ambitious arm sends `/be-ambitious` on its own first. The plugin's hook blocks it before Claude sees it and arms the session; then the arm sends the prompt exactly as the baseline does, so turn 1 is plain Claude, byte for byte the same input. Its hooks then save that work as the first version (`.ambition/first/`) and ask: stop here, or push it further. The gate is that the input really was identical: after the run, the bench compares turn 1's first API request with the baseline's, from the saved transcripts (the request shape covering the system prompt and tools, the parameters, and every message block, with only the date normalised), and writes `turn1-input.json`. A difference means the plugin leaked into turn 1, and the run fails. If they're identical, the first version is a second plain sample: how it compares with the baseline is run-to-run variation, which we record but don't hold against the plugin.
- **The bar.** The final must beat every plain version: the baseline, the plain push and the run's own first version. The plain push separates what the method adds from just asking again and spending more. Faster and cheaper counts in the baseline's favour, so the plugin has to win on quality by enough to justify its cost. We also ask separately whether the preview was worth its cost, and whether pushing on was.
- **Where the plugin arm ends.** The bench stops at the reply to step 8 (Lock). In plan mode the deliverable is the plan: the push may write checks, simulations or a small spike to test it, but the bench never approves a build, so a plan example compares plans, not builds. When the deliverable is itself a document, improving the document is the build.
- **Judged by people.** Claude reviews harshly, side by side and live, with the genre bar first and the goal second, then cost and time. The user decides. `verdict` records that decision.
- **Only the current plugin counts.** Every run records the plugin version it used (`plugin` in `metrics.json`: commit, uncommitted changes, and a hash of the plugin's files). The report marks runs from an older plugin as outdated. Clear outdated examples rather than keep them.

## What keeps it fair

- **Identical conditions.** Both arms get the same model, effort (medium, the recommended setting, unless `--effort` says otherwise), tools, turn limit, settings and VM image. Each run gets a fresh throwaway macOS VM, a copy-on-write clone of the bench image (see [`vm/README.md`](vm/README.md)), with a fresh empty folder shared in as `/work`. It's booted once for the whole run, as one Mac for one chat, and deleted afterwards; booting isn't counted in the run's time. The ambitious arm also gets the plugin's own parts, read-only, and nothing else. No run can see the bench, the prompts, the baseline or another arm's output.
- **Runs work like Claude on a Mac.** The VM is an ordinary developer Mac: macOS 26, Homebrew, Node, Python, git, ripgrep and Google Chrome, with WebGL on the GPU through Apple's paravirtual device. Every Bash command is allowed, so a run can install packages, serve its page and look at it, and its frame rates are real. A bench where runs can't look at their work isn't testing Claude as people use it. The VM is the boundary; there's no Claude Code sandbox inside it. We checked the renderer: the VM's frames are pixel-identical to the host's GPU at 60 fps. The older Linux container (`--where docker`) drew the same pixels in software but about 6 times slower, so frame-rate checks in runs made there mean little.
- **The same stand-in user.** After every turn, a client (the run's model and effort, no tools) decides whether the reply is waiting on the user. It plays the person who typed the prompt: it answers questions properly, with its own judgement of what that person would most plausibly want, and approves or adjusts restatements. It answers the checkpoint with "Push it further." It knows only the prompt, never the brief, so both arms get exactly the same information.
- **Real time and real cost.** Minutes are wall-clock time, including the stand-in's replies (`wall_ms`). `exchange_log` records the cumulative minutes and cost at the end of each exchange (each message sent to Claude), so the first is the preview's cost. The site reports by **turn**, where a turn is a step of the method: turn 1 is the plain first version up to the checkpoint, turn 2 is altitude (the questions, the answers and the work on them), and turns 3–8 are depth, challenge, range, judge, stretch and lock. The plugin hands Claude one step at a time and opens each with a marker line (`▸ Step 3/8 · Depth`); `run` prints a `steps:` line that warns when a marker or a step's copy is missing, or when every copy is identical; `report` splits time by the markers' timestamps and cost by each step's token use, scaled to the run's measured totals. Runs made before the markers fall back to exchanges. A resumed session reports its cost and usage cumulatively, so a run's totals are its last turn's figures. The headless JSON's own `duration_ms` and `num_turns` undercount runs with several exchanges and subagents.
- **Long runs.** After the checkpoint the whole push (steps 2–8) is one exchange, and a build can take more than an hour, so one exchange may run for up to 4 hours. Wall-clock time keeps counting while the host sleeps, so keep the Mac awake for the length of a run (for example `caffeinate -ims python3 bench/ab.py run …`); a run cut off by sleep or the limit has to be archived and run again.

## Review evidence

`review` captures every version the same way: the baseline and its plain push, each ambitious run's first version (`.ambition/first/`) and final, and the work at the end of each step, which the plugin copies to `.ambition/steps/<n>/` (older runs: each saved exchange). Into `run-<n>/review/<baseline|pushed|first|final|step-N|turn-N>/`. Two captures run at a time, and a step that left the first version or the final unchanged reuses that capture:

- **Frames across time.** In a review VM (one clone for all of a `review`'s captures), `review/capture.mjs` opens the page in Chrome on the GPU at desktop (1280×800) and phone (390×844) sizes and takes a frame every second. Time is virtual and stepped at 60 fps (what a page sees in a real browser, so adaptive-quality pages stay at full quality), and one full loop plays before frames are taken, so frame t=4 really is 4 seconds into a warmed-up loop. The length comes from the prompt ("10 second") or `--seconds`.
- **A seam check.** For anything that moves (reported only when the prompt asks for a loop; elsewhere it's just "moving"), the last frame is compared with the first, against a typical step between frames. A seamless loop ends where it began. Frames are taken from the second loop, after one whole loop has played, so trails and other effects that build up over time have the same history at both ends.
- **Console errors**, per size.
- **Contact sheets** of the frames, for side-by-side viewing.

`review` also runs `measure()` on the host for every HTML page, into `run-<n>/checks/`: a Lighthouse audit (mobile, 375px) and screenshots at 375px and 1280px. That needs Chrome and `npx`.

None of this decides anything. It's what we look at, beside the live pages.

## Results page and site

`report` writes:

- [`examples/RESULTS.md`](../examples/RESULTS.md): one row per example with the verdict, the gate, the baseline's cost and time, the plain push's, the preview's (turn 1), the full run's and the plugin version.
- `docs/`: the GitHub Pages site (Settings → Pages → deploy from `main`, folder `/docs`). Each example page opens with a Sublime Text-style window of session replays under the prompt, one tab per run: `bench/cast.py` turns each saved (scrubbed) transcript into an asciicast that asciinema-player replays in Claude Code's terminal style. Below that, Baseline | First version | Final side by side, with frame sheets, the seam and error checks, Lighthouse, and each version live. Below that: our review, cost and time by turn (step of the method), the work at the end of each step, how the run restated the task, and every reply and file. It's static HTML, generated in full on every build, with the site's own CSS and JS in `bench/site/`. Never edit `docs/` by hand.

## Setup

Runs need the bench VM (build it once, see [`vm/README.md`](vm/README.md)) and a token:

```sh
claude setup-token                     # prints a long-lived token
echo 'CLAUDE_CODE_OAUTH_TOKEN=<token>' > bench/.env
```

`bench/.env` is gitignored. Every run uses an empty config folder (`bench/.home/`, also gitignored). It's shared into each run's VM at `/cfg`; the token travels in the command over SSH and is never written into the VM. Each run's `metrics.json` records `isolation: vm` and the environment. `--where docker` uses the older Linux container (`bench/docker/`, Chromium in software), kept so older results can be reproduced. `--where host` runs on the host in Claude Code's sandbox, with no browser; it's only for debugging the harness, never for results.

While a run is going, `run-<n>/live` links to its working folder, so you can watch it.

## Output

```
examples/<model>/<category>/<name>/
  spec.json            the prompt, brief and check this example ran with
  <arm>/run-<n>/
    prompt.md          every message sent from the user side (the prompt and the stand-in's replies)
    result.md          Claude's final reply
    output/            the files it produced (for ambitious runs, .ambition/first/ is the first version)
    turns/turn-<n>/    the work at the end of each exchange that changed it (steps are in output/.ambition/steps/<n>/)
    transcript.md      readable history, including tool calls
    transcript/        raw session and subagent transcripts (scrubbed)
    metrics.json       cost, tokens per model, time, exchange_log, plugin version, isolation, permission denials
    metrics.txt        the same one-glance format as /be-ambitious
    checks/            Lighthouse and screenshots for HTML pages
    review/            frames, contact sheets and capture.json per version
    verdict.json       our decision (ambitious runs, after review)
    review.md          our side-by-side review, if written
```

Saved work leaves out dependencies (including Python virtualenvs), screenshot and tooling folders, and images inside `.ambition/` (where the run keeps its looks at the work), for every arm alike. Before saving, transcripts are scrubbed: your home path becomes `~`, the workspace path becomes `<workspace>`, email addresses are replaced, tokens are redacted, and images the run looked at are replaced by a note.

## Fixtures

Examples marked *(fixture: …)* need files in `examples/fixtures/<category>/<name>/`:

- `public/` is copied into each arm's workspace.
- `hidden/` holds the ground truth, for checking only.
- `generate.py` (optional) creates both. It runs once, then the result is cached.

`list` shows which fixtures are still missing.
