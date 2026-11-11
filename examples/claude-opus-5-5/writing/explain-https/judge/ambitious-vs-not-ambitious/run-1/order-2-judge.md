A = ambitious, B = not-ambitious (the judge did not know this)

A is the clear winner. Both explain HTTPS accurately. Only A tackles the junior's real problem, which is switching off certificate verification, and the checks back it up.

**Checks**
- **Ground truth:** there is no `hidden/` directory, so I judged technical accuracy myself.
- **Comprehension test:** two fresh agents each read only one explanation (A's `HTTPS-for-developers.md`, B's `RESPONSE.md`) and answered the same 5 questions. Each was told to say "NOT COVERED" for anything its document didn't cover.
  - **A: 5/5 answered from the text.** One small gap: the reader marked the TLS 1.3 forward-secrecy details as only partly covered.
  - **B: 3/5.** Question 3 (`unable to get local issuer certificate` in Python while the browser works, and what to do instead of `verify=False`) was "mostly NOT COVERED". Question 5 (corporate TLS-inspection proxy) was "NOT COVERED".
- **A's lab:** I ran it on a copy in `$TMPDIR`. `./setup.sh` exited 0, then I started `servers.py`.
  - `mitm_demo.py`: with verification off, the token leaks and the reply is altered. With it on, the request is blocked with `unable to get local issuer certificate`.
  - `check.py`: 0/5 scenarios fixed and the attacker canary blocked. That's the intended starting state; the errors really happen in Python, curl and Node.
  - `tools/selftest.sh`: all 10 checks pass, including canary detection, rejecting a server-side "fix" of the proxy scenario, the reference fixes solving 5/5, and the scanner catching all 31 insecure samples with no false positives.
  - I then stopped the servers.
- **B** produced no files, so it had nothing to run.

**Scores**

| Criterion | A | B |
|---|---|---|
| Technical accuracy | **5:** handshake, the role of CertificateVerify, SAN-only name matching, trust store behaviour for each runtime and the 200-day certificate limit since March 2026 (CA/B Forum SC-081) all check out. | **5:** a correct, current TLS 1.3 walkthrough (hybrid ML-KEM key exchange, Certificate Transparency, HKDF, AEAD, the ECH caveat). |
| Changes behaviour (verification habit) | **5:** opens with a runnable demo where verification off means a leaked API key. Then gives a fix for each error type instead of `verify=False`, a triage flowchart, rebuttals to the usual excuses, and a CI scanner for disabled verification. | **2:** one sentence ("encryption alone doesn't help if you're encrypting to the wrong party") hints at it. It never mentions `verify=False`, real error messages or how to fix them. |
| Comprehension test | **5:** 5/5 answered, with specific, usable fixes. | **3:** 3/5; it fails exactly the two questions about what to do instead of disabling verification. |

B is a good general explanation of HTTPS. A explains the same mechanics just as accurately and also gives this junior a working way to stop bypassing verification. A is much longer, but the extra length is what answers those two questions, and its lab runs.

```json
{"winner": "A", "confidence": "high", "scores": {"A": {"technical_accuracy": 5, "changes_behaviour": 5, "comprehension_test": 5}, "B": {"technical_accuracy": 5, "changes_behaviour": 2, "comprehension_test": 3}}, "summary": "Both are accurate, but only A tackles the verify=False habit (working MITM demo, per-error fixes, lab whose selftest passes 10/10); B's reader couldn't answer the two practical-fix questions."}
```