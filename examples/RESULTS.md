# Results

Every example runs three ways on the same model, under identical conditions: the **plain prompt**, a **briefed prompt** (the prompt plus the context the user had in their head), and **`/be-ambitious`**. A blind judge compares `/be-ambitious` against each, twice with the labels swapped. A disagreement counts as a tie. Only then does a separate step see the costs and decide whether the improvement was worth paying for. [How the bench works](../bench/README.md).

Browse the outputs, screenshots and judge reports on the [results site](https://richardoutram.github.io/claude-ambition/).

## claude-opus-5-5

| Example | Runs | vs plain prompt | vs briefed prompt | Cost per run (plain · briefed · ambitious) | Minutes (plain · ambitious) | Worth the extra cost? (vs plain) | Worth it vs briefed? |
|---|---|---|---|---|---|---|---|
| [write/explain-https](#writeexplain-https) | 1 | Won 1 of 1 (high/high confidence) | Won 1 of 1 (high/medium confidence) | $0.11 · $0.13 · $4.15 | 0.3 · 14.4 | Yes (major uplift, 38.1x cost) | Yes (material uplift, 32.9x cost) |

### write/explain-https

> Explain how HTTPS works.

**vs plain prompt, run 1:** Won 1 of 1 (high/high confidence). Judge, with A = plain prompt and B = /be-ambitious: Both are accurate, but only B tackles the disable-verification habit; its demo and lab ran as claimed (selftest 10/10) and it scored 5/5 on comprehension vs A's 4/5.

- **Worth it:** yes (major uplift for 38.1x the cost and 56.4x the time). Only the dearer response addresses the junior's verify=False habit, with a working MITM demo, fixes for each error including corporate CAs, and a CI scanner, all confirmed by running them, for about $4 and 14 minutes.
- **Use it when:** The explanation is meant to change a risky habit or unblock real errors, especially when mentoring a team where a runnable demo and CI guardrail will be reused.
- **Skip it when:** The user only wants a conceptual overview of HTTPS, for an interview or general curiosity, with no specific practice to correct.

**vs briefed prompt, run 1:** Won 1 of 1 (high/medium confidence). Judge, with A = briefed prompt and B = /be-ambitious: Both accurate. B's runnable MITM demo (verified to leak the token with verify off), lab and CI scanner plus the identical-error insight change the habit more directly, and it scored 5/5 vs 4.5/5 on comprehension. A's REQUESTS_CA_BUNDLE advice silently replaces certifi.

- **Worth it:** yes (material uplift for 32.9x the cost and 35.3x the time). For a junior who habitually disables verification, the dearer response fixes the cheaper one's bundle-replacement trap (which would push them back to verify=False), states the attack-vs-misconfig 'identical error' point outright, and adds a verified runnable MITM demo that makes the risk visible, all for about $4 and 14 minutes against a recurring credential-leak risk.
- **Use it when:** The goal is to change a risky habit or teach a team, where a runnable demonstration and copy-paste-correct fixes will be reused or shared and a mistake has security consequences.
- **Skip it when:** The reader just wants a conceptual explanation of HTTPS for reading, with no habit to break, or a short handout is enough; then a compact answer with the combined-bundle fix and the identical-error point added covers most of the value.

[Outputs and judge reports](claude-opus-5-5/writing/explain-https/) · [Visual view](https://richardoutram.github.io/claude-ambition/claude-opus-5-5/writing/explain-https/)

Single runs can be luck. Treat any example with one run as an illustration, not a measurement.
