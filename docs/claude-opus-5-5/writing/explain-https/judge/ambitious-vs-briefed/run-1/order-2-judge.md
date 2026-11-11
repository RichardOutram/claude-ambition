A = ambitious, B = briefed (the judge did not know this)

# HTTPS explainer judgment: A beats B

A wins. Both explanations are accurate and both go after the habit of turning verification off. A backs its claims with a demo and a lab that actually run, and its reader got all 5 comprehension questions right. B's reader got about 4.

## Checks run

**A's material runs and does what it says.**
- **Attacker demo (`python3 lab/mitm_demo.py`):** works. With verification off, the fake API token leaks, the account number in the reply is swapped, and the app sees HTTP 200. With it on, the client fails with `unable to get local issuer certificate` and the request is never sent.
- **Lab checker (`python3 check.py`, servers running):** in the starting state, 0/5 scenarios are fixed and the attacker server stays blocked. Errors reproduce in Python, curl and Node.
- **Self-test (`tools/selftest.sh`):** 10/10 PASS. That covers the attacker canary, rejecting the wrong fix on the corporate-proxy scenario, the reference fixes solving 5/5, and the scanner flagging all 31 insecure samples with no false positives.
- **Clean-up:** I reset the lab with `./setup.sh` and stopped the servers.
- **A's scanner on B's file (`tools/find-insecure.sh`):** it flagged the "don't do this" lines in B's prose, including B's title line. That's harmless in docs but shows the scanner is noisy outside code.

B is a single document, so there was nothing of B's to run.

## Comprehension test
A fresh agent read only the explanation and answered 5 questions. For A that was the guide, `HTTPS-for-developers.md`; for B it was `RESPONSE.md`.

| Question | A | B |
|---|---|---|
| 1. What you keep and lose with verification off | ✔ | ✔ |
| 2. What proves the private key; what the client checks | ✔ (CertificateVerify, plus a 4th check) | ✔ |
| 3. Fails in Python but works in the browser: causes, and how to tell | ✔ (AIA fetching, separate trust stores) | ½: two causes and how to diagnose, but "why the browser works" is not covered |
| 4. Fix behind a corporate proxy, in Node and Python | ✔ (warns that `REQUESTS_CA_BUNDLE` replaces certifi) | ✔ |
| 5. Why the error message alone doesn't prove a config issue | ✔ (stated directly: the attacker's error is identical) | ½: had to be pieced together; the doc never says it outright |
| **Score** | **5/5** | **~4/5** |

## Accuracy notes
- **A:** I found no errors. The TLS 1.3 message order is right, the trust-store details per runtime are right, and the 2026 certificate-lifetime figure is current.
- **B:**
  - It's mostly accurate.
  - The Python fix of setting `verify=` (or `REQUESTS_CA_BUNDLE`) to the corporate root alone throws away the certifi roots. That can break other connections, especially off the corporate network.
  - Its "server signs its part" wording for the handshake describes TLS 1.2 rather than 1.3. That's fine as a simplification.

## Scores

| Criterion | A | B |
|---|---|---|
| Technical accuracy | 5: no errors found; runnable checks back the claims | 4: correct overall, but the corp-CA advice for requests replaces the default roots |
| Changes behaviour | 5: a working demo shows the token theft, the guide shows that "config bug" and "attack" give the same error, and there is a CI scanner | 4: clear "❌ vs ✔" fixes for each stack and the man-in-the-middle argument, but nothing hands-on |
| Comprehension | 5: 5/5 answered from the text | 4: about 4/5; Q3 and Q5 only partly covered |

Length isn't why A wins: B is the quicker read and a perfectly good handout. A wins because its central argument is shown working, not just stated: you can't tell an attack from a misconfiguration by the error message alone. That speaks directly to the habit, and the comprehension test picked up the difference.

```json
{"winner": "A", "confidence": "medium", "scores": {"A": {"technical_accuracy": 5, "changes_behaviour": 5, "comprehension": 5}, "B": {"technical_accuracy": 4, "changes_behaviour": 4, "comprehension": 4}}, "summary": "Both are accurate and both target the verify=False habit, but A's runnable attacker demo and lab (selftest 10/10) prove the 'same error as an attack' point and its reader scored 5/5 vs about 4/5 for B."}
```