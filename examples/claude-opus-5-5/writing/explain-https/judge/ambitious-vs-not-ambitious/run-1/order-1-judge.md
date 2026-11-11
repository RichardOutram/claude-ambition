A = not-ambitious, B = ambitious (the judge did not know this)

**Checks run (the same way for both)**
- **Read both deliverables.** A is a 650-word explanation in RESPONSE.md. B is a RESPONSE.md written to a manager, plus `cert-lab/GUIDE.md`, `cert-lab.py`, `node-check.mjs`, and a `https-demo.sh` that RESPONSE.md never mentions.
- **Ran B's lab** with `python3 -I cert-lab.py`. Exit code 0, and it reported "15 checks behaved as expected, 0 unexpected". Section 7 really does show the attacker reading `Authorization: Bearer sk_live_DO_NOT_LEAK` once verification is off. That backs up B's claims. The handshake ran on TLS 1.2 (LibreSSL), which B had already disclosed.
- **No `hidden/` directory** was present, so I had no ground truth to compare against.
- **Comprehension test.** I gave a fresh agent only A's RESPONSE.md, and another only B's RESPONSE.md plus GUIDE.md, with the same five questions. The first attempt failed because the agents weren't allowed to read the temp directory, so I copied the files into the working directory and ran it again.
  1. What HTTPS guarantees, and which part verification provides. **A: correct. B: correct.**
  2. What `verify=False` makes possible, and why the request still works. **A: partly; the agent inferred the attack from one MITM sentence and said so. B: complete; attacker cert, stolen bearer token, relayed response.**
  3. Fix for "unable to get local issuer" with an internal CA. **A: not covered, a reasonable guess. B: complete, with the exact per-tool commands.**
  4. How the two sides agree on a key. **A: correct (ephemeral Diffie–Hellman / X25519). B: not covered.**
  5. What an observer can still see. **A: correct (IP, SNI, DNS, traffic volume). B: not covered.**
  - **Totals:** about 3.75/5 for A and 3/5 for B.

**Technical accuracy (my review)**
- **A:** correct throughout. TLS 1.3 handshake, `CertificateVerify`, forward secrecy, the 0‑RTT replay caveat, ECH, and the Certificate Transparency requirement are all right.
- **B:** correct. It is right that `REQUESTS_CA_BUNDLE` replaces the default bundle while `NODE_EXTRA_CA_CERTS` adds to it, and its error-to-cause mapping matched the lab output. One overstatement: "ends up in production. It always does."

**Scores**
- **Technical accuracy:** A 5 (no errors found). B 4 (accurate and lab-verified, but it leaves out the mechanism and overstates once).
- **Behaviour change:** A 2 (one sentence on man-in-the-middle; nothing on the verification habit or what to do instead). B 5 (a runnable attack demo, an error-to-fix table, a "trust this one CA instead of `verify=False`" table, and a checklist).
- **Comprehension:** A 4 (3.75/5; solid on the mechanism, weak on the practical questions). B 3 (3/5; strong on the practical questions, nothing on key exchange or metadata).

**Verdict**
B wins on what the user actually needs. A is the better pure explanation of how HTTPS works. But the junior keeps turning verification off, and A never gives them a reason or a way to stop. B does both, and I confirmed its demonstration by running it. B's weaknesses are real, though:
- It explains little of the handshake or key exchange.
- Its RESPONSE.md speaks to a manager rather than to the junior.
- It leaves a stray script, `https-demo.sh`, that nothing references.

```json
{"winner": "B", "confidence": "medium", "scores": {"A": {"technical_accuracy": 5, "behaviour_change": 2, "comprehension": 4}, "B": {"technical_accuracy": 4, "behaviour_change": 5, "comprehension": 3}}, "summary": "A best explains how HTTPS works but ignores the verify=False habit; B's lab (ran: 15/15, shows a stolen bearer token) and fix tables target the habit directly, though it leaves out handshake and key exchange."}
```