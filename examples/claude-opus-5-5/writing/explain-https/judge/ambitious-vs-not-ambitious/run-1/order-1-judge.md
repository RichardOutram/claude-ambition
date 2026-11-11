A = not-ambitious, B = ambitious (the judge did not know this)

B wins. A gives an accurate explanation of how HTTPS works, but it never deals with the junior developer turning off certificate checks. B is built around that habit, and its demo and lab actually run.

**Checks run (both responses got the same ones where it made sense)**
- **Files:** A is a single 654-word answer. B is a 763-word summary plus a 4,208-word guide (`HTTPS-for-developers.md`) and a runnable lab. There was no `hidden/` folder, so there was no answer key to compare against.
- **B's lab, run in a copy (`tmph2edy8yi/work`):**
  - **`python3 mitm_demo.py`:** with checks off, the request succeeds with no error while the fake attacker logs the API token and swaps the bank account number. With checks on, it fails with `unable to get local issuer certificate` and nothing is sent. This matches what B claimed.
  - **`./setup.sh`, then `servers.py`, then `check.py`:** 0 of 5 scenarios fixed at the start, and the fake attacker's server stays blocked. The error messages from Python, curl and Node match the ones quoted in the guide.
  - **`tools/selftest.sh`:** all 10 checks pass. That includes the reference fixes solving 5 of 5, trusting the attacker's certificate being caught, and the scanner for disabled checks flagging all 31 bad samples and none of the 13 good ones.
- **Comprehension test:** a fresh agent got only one document each (A's answer, or B's guide) and answered the same 5 questions.
  - **A: 4 of 5.** It answered the three guarantees, why encryption alone isn't enough, the certificate checks and forward secrecy well. On "what to do about `unable to get local issuer certificate` on a corporate network" it said the document doesn't cover it.
  - **B: 5 of 5.** The corporate-network answer was the right one: get the company's root certificate from IT, confirm its fingerprint through a separate channel, and add that one certificate where each tool looks for trusted ones. On forward secrecy it explained the mechanism but said the guide doesn't explain why TLS 1.3 was designed that way.
- **Accuracy review:** both handshake descriptions are correct. In B, I spot-checked the per-tool details (Node's `NODE_EXTRA_CA_CERTS`, Python `requests` replacing rather than adding to its certificate list, the Java `keytool` command, Python 3.13's stricter checks, the 200-day certificate limit from March 2026) and found nothing wrong. A is correct but has nothing on fixing errors.

**Scores**

| Criterion | A | B |
|---|---|---|
| Technical accuracy | 5: handshake, forward secrecy, what HTTPS doesn't hide, all correct | 5: same core content plus correct per-tool fixes; demo and lab confirmed by running them |
| Changes the verification habit | 2: one sentence ("encryption alone doesn't help if you're encrypting to the wrong party"); never mentions `verify=False` or what to do instead | 5: a demo showing the token being stolen, a playbook for each error, and a scanner for CI; it makes the case that an attack gives the same error as a misconfiguration |
| Comprehension test | 4: 4 of 5; the corporate-network question wasn't covered | 5: 5 of 5, including the right corporate fix |

B is much longer, and I didn't score it higher for that. It wins because it is the only one that answers the question behind the request (what to do instead of turning checks off), and its claims held up when I ran them.

```json
{"winner": "B", "confidence": "high", "scores": {"A": {"technical_accuracy": 5, "behaviour_change": 2, "comprehension": 4}, "B": {"technical_accuracy": 5, "behaviour_change": 5, "comprehension": 5}}, "summary": "Both are accurate, but only B tackles the disable-verification habit; its demo and lab ran as claimed (selftest 10/10) and it scored 5/5 on comprehension vs A's 4/5."}
```