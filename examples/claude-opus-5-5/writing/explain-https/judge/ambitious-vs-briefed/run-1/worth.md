cheaper = briefed, dearer = ambitious

**1. What the dearer response delivers that the cheaper one doesn't, with evidence behind it**

- **A correctness fix that matters in practice.** The cheaper response tells the reader to point `verify=` or `REQUESTS_CA_BUNDLE` at the corporate CA file. That replaces certifi's default roots. Both judges flagged it. A junior following that advice would trade the "it doesn't work" error for a different breakage on every public site. They would then be likely to fall back to `verify=False`, the very habit the request is trying to break. The dearer response warns about this and shows how to build a combined bundle.
- **The "same error" point, stated outright.** The dearer response says directly that the error you get from an attacker is identical to the one you get from a misconfigured proxy, so the error message can't tell you which you're facing. This is the core argument against "just disable it". The cheaper response only implies it, and its reader got half marks on that question in both comprehension tests.
- **A demo that ran and did what it claimed.** With verification off, the demo leaked the token and swapped the payout account while the app still saw HTTP 200. With verification on, it was blocked. This was verified in both reports, and the selftest passed 10/10 in one of them.
- **Lab and CI scanner.** The lab gives hands-on practice. The scanner could stop the habit from reaching code review. One judge noted the scanner gets noisy on prose.
- **Measured uplift.** Comprehension was 5/5 against roughly 4–4.5/5, and accuracy was 5 against 4 in both orders.

For a junior who keeps disabling verification, the goal is a change in behaviour, not just understanding. Being shown the leak working, plus a correct fix for the corporate proxy, is what is most likely to stop the habit. This is a recurring security risk, and possibly a real credential leak.

**2. What it costs**

- $4.02 more: $4.15 against $0.13.
- About 14 more minutes of waiting.
- Three more user messages, so the user had to steer the work.
- Much more for the junior to read and run (a guide, a lab, servers to start, a scanner), compared with a single handout.

**3. Weighing it**

About $4 and 14 minutes is trivial next to one leaked production token, or a habit that would otherwise keep recurring across a codebase. The cheaper response is decent, but its proxy fix is a trap that likely sends this particular reader back to `verify=False`. The dearer response fixes that and adds runnable proof that a lecture can't match.

Two things weigh against it: the extra user messages and the heavier material. A lighter middle option would have captured much of the gain at low cost: the cheaper response plus the combined-bundle fix and an explicit "identical error" line. Even so, the demo is the persuasive part, and it was verified to work.

```json
{"uplift": "material", "worth_it": "yes", "reason": "For a junior who habitually disables verification, the dearer response fixes the cheaper one's bundle-replacement trap (which would push them back to verify=False), states the attack-vs-misconfig 'identical error' point outright, and adds a verified runnable MITM demo that makes the risk visible, all for about $4 and 14 minutes against a recurring credential-leak risk.", "use_when": "The goal is to change a risky habit or teach a team, where a runnable demonstration and copy-paste-correct fixes will be reused or shared and a mistake has security consequences.", "skip_when": "The reader just wants a conceptual explanation of HTTPS for reading, with no habit to break, or a short handout is enough; then a compact answer with the combined-bundle fix and the identical-error point added covers most of the value."}
```