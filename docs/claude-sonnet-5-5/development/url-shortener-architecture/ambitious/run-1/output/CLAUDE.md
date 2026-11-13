# URL shortener architecture

Deliverable: `url-shortener-architecture.md` (design for 10k req/s; Section 8 stretches to 100k).

Re-validate after any edit: `python3 -I check_architecture.py url-shortener-architecture.md --run --links`
(expect `FAIL 0`). It re-runs the embedded scripts and compares their printed output with the document,
checks prose figures against that output, cross-references, tables, links, and that every decision and
check has an owner and date. Without `--run` it needs no data files or network.

If an assumption changes (read:write ratio, hit rate, row size), edit the constants in script A1,
re-run it, and update the figures it feeds (Section 2 tables); the check flags prose that no longer matches.
Keep the document free of process history (no "earlier draft" wording); the check enforces this.
