A = briefed, B = ambitious (the judge did not know this)

# B is the better explanation, mainly because it does more to change the junior's verification habit

There was no `hidden/` folder, so there was no ground truth to check against. I checked accuracy myself and ran B's lab tools.

## Checks run (the same way on both where it applied)

**1. Technical accuracy.** I reviewed both against how TLS actually works.
- **A** is correct on encryption versus authentication, the three certificate checks, ECDHE with a server signature, the MITM scenario, and the error-to-fix table. Its one flaw is in the corporate-CA fix: `verify="corp.pem"` and `REQUESTS_CA_BUNDLE` replace Python's default certificate bundle (certifi) instead of adding to it. A junior who follows A could then find that every public site stops working.
- **B** is correct and goes deeper.
  - It says outright that a bare `REQUESTS_CA_BUNDLE` or Node `ca:` replaces the default roots, and it shows how to build a combined bundle instead.
  - It covers forward secrecy and CertificateVerify, explains why each runtime has its own trust store, handles clock skew, and has the corporate CA's fingerprint checked through a separate channel.
  - Its certificate-lifetime claim (200 days from March 2026, under CA/Browser Forum ballot SC-081) is correct.
  - The handshake diagram puts verification after the server's Finished message, which is a simplification but not wrong.

**2. Running B's artefacts.**
- `python3 lab/mitm_demo.py` produced exactly the output the guide claims.
  - With verification off, the app gets HTTP 200, the attacker logs the API token, and the payout account is swapped for the attacker's.
  - With verification on, the client raises `unable to get local issuer certificate` and the attacker logs nothing.
- `tools/find-insecure.sh` on the insecure samples flagged `verify=False`, `httpx verify=False`, `_create_unverified_context` and `CERT_NONE`, among others.
- I could not run the secure-sample scan or the full `check.py`/`selftest.sh` run, because the permission prompt blocked those commands. B's claims of "10 passes" and "0 false positives" are therefore its own and not something I re-checked.

**3. Five-question comprehension test.** A fresh agent read only each explanation and answered the same five questions.

| Question | A | B |
|---|---|---|
| 1. Still encrypted? Why isn't that enough? | ✔ | ✔ |
| 2. What the client checks on the certificate | ✔ | ✔ (also named the 4th, signature, check) |
| 3. Corporate proxy: cause and fix | ✔ (but its `REQUESTS_CA_BUNDLE` fix would break public sites) | ✔ (combined bundle, fingerprint check, truststore) |
| 4. Why the error can't tell an attack from a misconfiguration | ½ (A never states it) | ✔ |
| 5. What proves the server owns its certificate | ✔ | ✔ |
| **Score** | **4.5 / 5** | **5 / 5** |

## Scores

| Criterion | A | B |
|---|---|---|
| Technical accuracy | 4 | 5 |
| Changes the verification habit | 3 | 5 |
| Comprehension test | 4 | 5 |

- **Accuracy:** A is correct throughout except that its `verify`/`REQUESTS_CA_BUNDLE` advice replaces certifi without warning. B adds the combined-bundle fix, the per-runtime trust-store differences and the fingerprint check, and I found no errors.
- **Behaviour change:**
  - A argues well against the habit, with a MITM explanation, a cause-to-fix table and the "whispering to a stranger" line. But it is only reading, and the reader has to take it on trust.
  - B gives a demo I confirmed runs and leaks the token with verification off. It also adds a hands-on lab with an "attacker" server that must stay blocked, and a scanner that can run in CI. The point that "the attacker's error is identical to the proxy's" directly undercuts "just disable it".
- **Comprehension:** A missed the identical-error point. B answered all five correctly with concrete commands.

## Verdict

A is a solid, compact explanation that would suit a reader who only wants to read. B wins on what the user actually needed: it makes the cost of turning verification off something the junior can see and act on. B is longer, but that isn't why it wins. It wins because the demo works when you run it, it states the identical-error point outright, and it avoids A's bundle-replacement trap.

```json
{"winner": "B", "confidence": "high", "scores": {"A": {"technical_accuracy": 4, "changes_verification_behaviour": 3, "comprehension_test": 4}, "B": {"technical_accuracy": 5, "changes_verification_behaviour": 5, "comprehension_test": 5}}, "summary": "Both accurate. B's runnable MITM demo (verified to leak the token with verify off), lab and CI scanner plus the identical-error insight change the habit more directly, and it scored 5/5 vs 4.5/5 on comprehension. A's REQUESTS_CA_BUNDLE advice silently replaces certifi."}
```