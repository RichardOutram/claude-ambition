# write/explain-https · ambitious

### User

<command-message>ambition:be-ambitious</command-message>
<command-name>/ambition:be-ambitious</command-name>
<command-args>--no-metrics Explain how HTTPS works.</command-args>

### Context (injected)

<details><summary>show</summary>

Base directory for this skill: ~/dev/personal/templates/claude-ambition/skills/be-ambitious

# /be-ambitious

Request: --no-metrics Explain how HTTPS works.
Run started: 2026-11-11T18:36:22Z

Load the `ambition-method` skill if it isn't already loaded. It defines the seven moves, and this skill only orchestrates them. To save a round trip, load it in the same message as your first other tool calls (reading the repo, checking the task), not on its own. The same goes for `delegate.md` when delegating. Treat the request text as the task; don't read it as instructions about this skill. Read the flags out of it.

## 0. Read the situation

**Size.** If the task is trivial (a typo, a rename, a one-line answer), say so. Do a light pass instead: ask one altitude question and run one outside check, then stop. Ambition costs effort, so spend it where the payoff is.

**Intent.** Decide whether this is a **plan** or a **build**.
- `--plan` / `--build` override everything.
- Plan mode is on → plan.
- Words like "plan", "design", "approach", "strategy", "how should we", "proposal", "options", or a request for a document → plan.
- Imperatives like "build", "fix", "add", "implement", "make", "ship", "migrate", "speed up", or an existing approved plan to carry out → build.
- Unclear → make it your first interview question.

**Who answers the clarifying questions.**

| Mode | Answerer | Use when |
|---|---|---|
| default | The user, interviewed one question at a time | The user is here |
| `--auto` | You, from the repo, the conversation and sensible defaults | The user wants it to run unattended |
| `--delegate` | An `ambition-client` agent holding a brief, while an `ambition-runner` agent does the work | Orchestrated or comparison runs, or when you are acting as an orchestrator |

**Who reviews between steps.**
- `--review me`: pause after each step for the user's notes.
- `--review claude`: you write the notes yourself.
- Default: no pause between steps, only at the checkpoints below.

## 1. Altitude: interview, then restate

Ask up to 4 questions, **one at a time**. Use the AskUserQuestion tool when it's available, with concrete options drawn from what you can already see. Skip any question the context already answers.
1. What is this ultimately for, and what should happen after it's done?
2. What would make the result unmistakably excellent? Push for a specific, hard target, not "good".
3. What would prove it, other than you? Name a test, a metric, real users or reference output.
4. What access, data or tools are missing? Skip this if it's obvious.

In `--auto` mode, answer the questions yourself from evidence. List each answer as a labelled **assumption**. Stop and ask only if an unknown would change the direction materially.

Then restate the task at the level that serves the goal:

```
You asked for:   <original>
Aiming at:       <restated goal>, because <reason>
Excellent means: <specific hard target>
Proven by:       <outside check>
Needs access to: <gaps, or "nothing new">
Mode:            plan|build · answerer · reviewer
```

**Checkpoint:** in the default mode, ask the user to confirm or adjust this restatement before going on. In `--auto` mode, proceed. Never silently drop something the user asked for.

If access is missing, getting it is the first piece of work. Ask for it, or build it.

## 2. Run the moves

Run each move from the method in order. After each one, give a short step report: **did / found / changed course**. If reviewer notes arrive, treat them as steering, not as answers.

**Plan route.** Planning still means touching reality. Read the code, query the data and run spikes when they would settle a question; don't settle it from the armchair.
1. **Depth:** the four statements, then a rewritten task.
2. **Challenge:** assumptions tested against the real material, plus any new finding.
3. **Range:** the verb form, the fields borrowed from with the method taken from each, and what the red team found.
4. **Stretch:** a stretch variant of the plan, with where it would likely break.
5. **Judge:** define the outside check the build will be held to. If you can build it cheaply now, do. A plan with its acceptance test already written is a stronger plan.
6. **Output the plan** with sections for: goal beyond the goal · target · approach and instruments · assumptions tested · borrowed methods · outside check · stretch option · what will be locked in afterwards. In plan mode, present it for approval through the normal plan-approval step. Otherwise stop and ask for approval.

**Build route.** Run Depth → Challenge → Range, doing the work as you go. Then:
- **Judge:** run the outside check, preferably the `ambition-judge` agent or a real tool, and iterate until it passes. Meet the original brief first and keep it passing.
- **Stretch:** go for the harder target and report where it broke.
- **Lock:** script or spec, a CLAUDE.md note, and a command if the task will recur.

Respect the session's permission mode and the user's rules throughout. Ambition never authorises skipping a confirmation the user requires.

## 3. Delegated mode (`--delegate`)

Only with `--delegate`: read [delegate.md](delegate.md) (`~/dev/personal/templates/claude-ambition/skills/be-ambitious/delegate.md`) and follow it. The orchestrator protocol for the runner, client and judge agents is there.

## 4. Report

Finish with:
- **You asked for → it became:** one line each.
- **Outside check:** what ran, and what it returned.
- **Stretch:** the target, how far it got, and where it broke.
- **Locked in:** the files created, and how to rerun.
- **Assumptions made** (auto or delegated mode), and anything the user should decide.
- **Metrics** (skip with `--no-metrics`). As your last action, run `python3 ~/dev/personal/templates/claude-ambition/skills/be-ambitious/scripts/ambition-metrics.py 4b13e4f3-80c0-4c5a-95df-6c34ad45beb8 --since <Run started>`. Paste its output verbatim in a code block, without commentary. It covers the main session and every subagent.

With `--log`, also write the full run to `.ambition/runs/<YYYY-MM-DD>-<slug>.md`: the restatement, every question and answer, every reviewer note, each step report, the judge's verdicts, the final report and the metrics.


</details>

**→ Skill** `{"skill": "ambition:ambition-method"}`

<details><summary>result</summary>

```
Launching skill: ambition:ambition-method
```

</details>

### Context (injected)

<details><summary>show</summary>

Base directory for this skill: ~/dev/personal/templates/claude-ambition/skills/ambition-method

# The ambition method

Left to their defaults, models do the task as typed, pick the median method and grade their own work, then stop at "good". This method pushes against each of those defaults. It comes from Felix Rieseberg's essay [How to be more ambitious: a tutorial for humans with models](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/). Where this skill adds something the essay doesn't say, it is marked *(ours)*.

## The defaults you are working against

| Default | What it looks like | Counter |
|---|---|---|
| Literal scope | Doing the task as typed, not what it is for | Altitude |
| Costume expertise | Expert vocabulary over amateur methods, such as markdown tables where a statistician would use a database and a model | Depth: instruments |
| Digested inputs | Working from summaries and someone else's conclusions | Depth: raw material |
| Unchecked beliefs | Taking the framing you were given as fact | Challenge |
| One-field thinking | Solving it the way this field always does | Range |
| Self-grading | "I reviewed it and it looks correct" | Outside judge |
| Modest targets | Settling, or calling something impossible too early | Stretch |
| One-off wins | A result nobody can reproduce next time | Lock |

## The four kinds of ambition

- **Speed:** the same work, faster. It needs little creativity, so this method skips it.
- **Altitude:** aim at the outcome rather than the task. Ask "what do you want to happen next?" and "what's the goal beyond the goal?" Example: stop fixing individual crashes and aim to keep the app crash-free.
- **Depth:** work the way the best practitioner alive would, and keep pushing until even they might learn something from the result.
- **Range:** look at the work through several fields. That used to be uneconomical. Multi-agent setups make it cheap.

## The seven moves

The `/ambition*` commands and `/be-ambitious` run these in this order. Details and worked examples are in `reference/`.

1. **Altitude: find the goal beyond the goal.**
   - What is this ultimately for?
   - What would make the result unmistakably excellent? It must be specific and hard. "Good" is not an answer.
   - What, other than me, would prove it?
   - What access am I missing?

   Then restate the task at the level that serves the goal. The ladder runs: feed in all the data → ask for decisions → question whether the artifact should exist at all. Tell-tale sign that altitude applies: people would hold meetings about this work.
2. **Depth: deeper, not bigger.** Before working, state four things:
   1. what a top professional would do that wasn't asked for;
   2. the rawest material they would start from;
   3. the specific methods and instruments they would use;
   4. what, other than you or the user, would show the result is right.

   Then rewrite your own task to ask for exactly that, and do it. Use their real instruments, not their vocabulary.
3. **Challenge: test what we think we know.**
   - List the assumptions in the request and in your approach.
   - Try to reproduce each one from the raw material: run it, read the source, query the data. Reasoning alone doesn't count.
   - Once you are inside the material, look for something new: a blind spot, an earlier signal, a finding you can check on data you held back.
4. **Range: borrow methods from other fields.**
   - Restate the work as verbs, not nouns. A quarterly review isn't "a deck". It is "getting busy people to believe a story about cause and effect and decide under uncertainty in 30 minutes".
   - Name 3–5 fields that do those verbs differently, plus a red team whose job is to break it.
   - Borrow what each one *does*. Don't play characters: do a short seller's research, don't write in a short seller's voice.
5. **Judge: never grade your own work.** Use or build a check that isn't you: tests, a real run, a benchmark, a simulation, reference output, or an independent judge agent. A tool you can run for immediate feedback is ideal. Run it, iterate until it passes, and report what it showed.
6. **Stretch: an unreasonable target, treated as reasonable.**
   - Pick a specific target several times harder than the brief, for example 200ms when 5s was asked for.
   - Assume it's solvable, because someone has done something like it.
   - When it looks impossible, keep going and try another angle before concluding.
   - Falling short is fine. Report exactly where it broke.
7. **Lock: make it cheap to repeat.** Turn what worked into the smallest durable form: a script or spec, a short CLAUDE.md note saying how to run it and what proved it, and a command if the task will recur. Altitude pays off in workflows that take the human out of the loop.

## Operating rules

- **Access comes first.** The method assumes a computer that can install software and reach real data. If data, tools, machines or permissions are missing, getting them is the first job. Ask for them; don't fake around them.
- **Evidence over assertion.** Every claim that something works, is faster or is correct needs a check you ran. Never say a check passed if you didn't run it.
- **Raise the goal openly.** *(ours)* When you restate a task at a higher altitude, say what changed and why, and let the user veto it. Ambition never overrides explicit constraints, permissions, safety, or the user's stated scope.
- **Deeper, not bigger.** Ambition means a better method and a better outcome, not more output. Cut anything that doesn't serve the goal.
- **Proportion.** *(ours)* Match the effort to the stakes. A typo fix needs no interview. When in doubt, do a light pass: one altitude question and one outside check.
- **Know where it fits.** Altitude works less well for open-ended creative work, and "go make money" is too high a level to act on yet. Depth and range still apply there.
- **No theatre.** Personas are for finding fields and methods, not for voice. A stranger transcript is not a better result.
- **Report honestly.** End with what the original ask was, what it became, what the outside check showed, and where the stretch broke.

## Reference

- [reference/altitude.md](reference/altitude.md): the escalation ladder, worked example, building access
- [reference/depth.md](reference/depth.md): the four statements, instruments, challenge and new knowledge, judges
- [reference/range.md](reference/range.md): verbs, assembling a crew, red teams, using subagents
- [reference/pitfalls.md](reference/pitfalls.md): failure modes of ambitious runs and how to catch them


</details>

**→ Bash** `{"command": "cd \"$TMPDIR\" && echo | openssl s_client -connect example.com:443 -servername example.com -brief 2>&1 | head -30; openssl version", "description": "Do a real TLS handshake with example.com", "allowed_domains": ["example.com"]}`

<details><summary>result</summary>

```
807F93F901000000:error:10080002:BIO routines:BIO_lookup_ex:system lib:crypto/bio/bio_addr.c:772:nodename nor servname provided, or not known
connect:errno=1
OpenSSL 4.0.3 29 Sep 2026 (Library: OpenSSL 4.0.3 29 Sep 2026)
Shell cwd was reset to <workspace>
```

</details>

**→ Bash** `{"command": "curl -sv -o /dev/null https://example.com 2>&1 | grep -E \"TLS|SSL|ALPN|subject|issuer|expire|start date|Connected|CONNECT|HTTP/\" | head -30", "description": "Show a real HTTPS handshake via curl verbose", "allowed_domains": ["example.com"]}`

<details><summary>result</summary>

```
* Connected to 127.0.0.1 (127.0.0.1) port 64440
* CONNECT tunnel: HTTP/1.1 negotiated
> CONNECT example.com:443 HTTP/1.1
< HTTP/1.1 403 user denied
* CONNECT tunnel failed, response 403
<sandbox_violations>
deny network-outbound example.com:443 (user denied)
</sandbox_violations>
```

</details>

### Assistant

Network to example.com was denied, so I'll check the explanation's claims locally with OpenSSL instead.

**→ Bash** `{"command": "set -e; D=\"$TMPDIR/https-demo\"; rm -rf \"$D\"; mkdir -p \"$D\"; cd \"$D\"\n# 1. A tiny PKI: root CA -> server cert for demo.test\nopenssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -keyout ca.key -out ca.crt -days 1 -subj \"/CN=Demo Root CA\" 2>/dev/null\nopenssl req -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -keyout srv.key -out srv.csr -subj \"/CN=demo.te … [1507 more chars]`

<details><summary>result</summary>

```
Quoted text in this command can't be checked before it runs
```

</details>

**→ Write** `{"file_path": "<workspace>/https-demo.sh", "content": "#!/usr/bin/env bash\n# Shows the moving parts of HTTPS locally, with no network access:\n#   1. certificate chain + hostname verification\n#   2. ECDHE key agreement (both sides reach the same secret)\n#   3. a real TLS 1.3 handshake over loopback\nset -u\nD=\"${TMPDIR:-/tmp}/https-demo\"; rm -rf \"$D\"; mkdir -p \"$D\"; cd \"$D\"\nprintf 'sub … [1779 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/https-demo.sh (file state is current in your context — no need to Read it back)
```

</details>

**→ Bash** `{"command": "bash https-demo.sh", "description": "Run the local HTTPS demo script"}`

<details><summary>result</summary>

```
Exit code 1
== 1a. chain verify, CA trusted:
srv.crt: OK
== 1b. chain verify, CA not trusted:
error 20 at 0 depth lookup: unable to get local issuer certificate
== 1c. hostname demo.test:
srv.crt: OK
== 1d. hostname evil.test:
error 62 at 0 depth lookup: hostname mismatch
== 2. X25519 shared secret (client view, then server view):
e2971d66d8411be15537ac868b750753f0f008baa3de245766e2ccc69a130311
e2971d66d8411be15537ac868b750753f0f008baa3de245766e2ccc69a130311
== 3. TLS handshake messages (>>> sent by client, <<< received):
```

</details>

**→ Bash** `{"command": "cd \"$TMPDIR/https-demo\" && timeout 3 openssl s_server -accept 127.0.0.1:48443 -cert srv.crt -key srv.key -www 2>&1 | head -3", "description": "Check why the local TLS server didn't start"}`

<details><summary>result</summary>

```
(eval):1: command not found: timeout
Shell cwd was reset to <workspace>
```

</details>

**→ Bash** `{"command": "cd \"$TMPDIR/https-demo\" && (openssl s_server -accept 127.0.0.1:48443 -cert srv.crt -key srv.key -www > srv.log 2>&1 & P=$!; sleep 1; kill $P) ; cat srv.log | head -3", "description": "Capture the local TLS server's startup error"}`

<details><summary>result</summary>

```
This command can't be checked before it runs
```

</details>

### Assistant

# How HTTPS works

I treated this as a light pass, since it's an explanation and not a build. I didn't stop to interview you first; my one question is at the end. As the outside check, I ran the key steps with OpenSSL (results are further down).

---

## The one-sentence version

HTTPS is ordinary HTTP sent inside a **TLS** connection. TLS gives you three things:
1. **Confidentiality:** anyone watching the network sees only encrypted bytes.
2. **Integrity:** if anyone changes those bytes in transit, the change is detected.
3. **Authentication:** you know you're talking to the real `bank.com` and not someone pretending to be it.

The difficult part is getting two strangers who have never met to agree on a secret key over a network anyone can read, and to be sure who the other side is. That is what the **handshake** does.

## Step by step (TLS 1.3, the current version)

**0. TCP connection.** The browser opens a TCP connection to port 443. (HTTP/3 uses QUIC over UDP instead, with the same TLS 1.3 handshake built in.)

**1. ClientHello (browser → server)** contains:
- the TLS versions and cipher suites it supports, e.g. `TLS_AES_128_GCM_SHA256`;
- **SNI**, the hostname it wants (`bank.com`), so one IP address can serve many sites;
- a **key share**: a fresh, temporary Diffie-Hellman public key, usually X25519. The browser guesses the server will accept it, which saves a round trip;
- **ALPN**, the application protocol it wants (`h2` or `http/1.1`).

**2. ServerHello (server → browser)** contains the server's choice of cipher, plus its own temporary key share.

**3. Both sides now compute the same secret, separately.** Using Diffie-Hellman, each side combines its own private key with the other side's public key and gets the same number. That number never crosses the network. An eavesdropper sees both public keys and still can't work it out. From it, both sides derive the session keys using HKDF.
- Everything after this point is encrypted, including the certificate.
- The keys are temporary and thrown away afterwards. So even if the server's long-term private key is stolen later, recorded traffic can't be decrypted. This is called **forward secrecy**.

**4. The server proves who it is (encrypted):**
- **Certificate:** a document saying "this public key belongs to `bank.com`", signed by a Certificate Authority (CA). Usually there's a chain: server cert → intermediate CA → root CA.
- **CertificateVerify:** the server signs the handshake so far with the private key that matches the certificate. This proves it actually holds that key, not just a copy of the public certificate. It also ties the identity to *this* key exchange, which blocks a man-in-the-middle.
- **Finished:** a MAC over the whole handshake transcript. If anyone tampered with the earlier messages (say, to force weaker ciphers), it won't match.

**5. The browser checks the certificate:**
- the chain leads to a root CA that is already in the OS/browser trust store;
- the hostname appears in the cert's *Subject Alternative Name*;
- the cert hasn't expired or been revoked;
- (in browsers) it appears in public **Certificate Transparency** logs.

If any check fails, you see the full-page warning.

**6. The browser sends its Finished message, then the HTTP request.** The whole handshake takes **one round trip** (TLS 1.2 needed two). When reconnecting, a resumed session can send data in the very first flight ("0-RTT"), at the cost of some replay risk.

**7. Data transfer.** Every HTTP request and response is split into TLS records. Each record is encrypted and authenticated with an **AEAD** cipher (AES-GCM or ChaCha20-Poly1305). Each record has a sequence number, so it can't be replayed, reordered or altered without being detected.

## What HTTPS does *not* hide

- **The site's IP address** and roughly **how much data** is sent and when.
- **The hostname**, usually. SNI is still sent in the clear unless *Encrypted Client Hello (ECH)* is in use, and DNS lookups are visible unless they're encrypted (DoH/DoT).
- **What the server does with your data.** The padlock means "you're talking privately to whoever controls `bank.com`". It doesn't mean `bank.com` is trustworthy, or that it's the bank you meant (lookalike domains get valid certificates too).

## The mental model

| Problem | Tool |
|---|---|
| Agree on a secret in public | Temporary (Elliptic-curve) Diffie-Hellman |
| Know who you're talking to | Certificate signed by a trusted CA, plus a signature over the handshake |
| Keep data private and untampered | Symmetric AEAD encryption with keys from the shared secret |
| Stop attackers downgrading the handshake | A Finished MAC over the whole transcript |

Public-key cryptography is slow, so it's used only briefly, to set things up and prove identity. Everything after that uses fast symmetric encryption.

---

## Outside check: what I ran

A live handshake with `example.com` wasn't possible because outbound network access was denied here. Instead I wrote `https-demo.sh`, which builds a small CA and server certificate and runs the steps with OpenSSL 4.0.3:

| Claim | Result |
|---|---|
| Valid chain to a trusted root | `srv.crt: OK` |
| Same cert, but the root CA isn't trusted | `error 20: unable to get local issuer certificate` |
| Hostname in the SAN (`demo.test`) | `OK` |
| Wrong hostname (`evil.test`) | `error 62: hostname mismatch` |
| Both sides derive the same Diffie-Hellman secret from public keys only | Both sides got `e2971d66…a130311` (identical) |
| Full TLS 1.3 handshake over loopback | **Didn't run.** The local test server produced no output, probably because this sandbox blocks binding to local ports. I didn't confirm the exact error. |

- **Stretch:** I wanted to show the real handshake messages instead of only describing them. The certificate and key-agreement parts are shown; the live handshake broke on the sandbox's networking.
- **Locked in:** `./https-demo.sh`. Run it anywhere with OpenSSL. For the handshake part, allow local binding with `/sandbox`, or run it outside the sandbox. You can also try `openssl s_client -connect example.com:443 -servername example.com -msg` against a real site.

**My one question:** what is this explanation for? Is it general understanding, debugging a certificate or TLS error, preparing for an interview, or teaching others? I can go much deeper on any one of these, for example: a byte-by-byte walk through a real captured handshake, how TLS 1.2 differs, mTLS, certificate pinning, or how corporate TLS interception works.

### User

The explanation is for a junior developer who keeps disabling certificate verification to "make it work". I'd like it to focus on certificate errors and why turning off verification is a bad idea, and on how to fix the common causes properly instead.

### Assistant

Now the goal is clear: change what the developer does, not just what they understand. I'll write a short guide plus a lab they can run, which reproduces each common certificate error, shows the proper fix working, and shows an attacker reading their traffic once verification is off. Let me check the tools available.

**→ Bash** `{"command": "python3 -c \"import ssl,sys;print(sys.version);print(ssl.OPENSSL_VERSION)\"; python3 -c \"import cryptography;print('cryptography',cryptography.__version__)\" 2>&1 | tail -1; python3 -c \"import requests;print('requests',requests.__version__)\" 2>&1|tail -1; node --version 2>&1; which mkcert curl", "description": "Check Python, ssl, node and curl availability"}`

<details><summary>result</summary>

```
Exit code 1
3.9.6 (default, Aug 25 2026, 21:26:21) 
[Clang 21.0.0 (clang-2100.3.34.2)]
LibreSSL 2.8.3
ModuleNotFoundError: No module named 'cryptography'
ModuleNotFoundError: No module named 'requests'
v24.18.0
mkcert not found
/usr/bin/curl
```

</details>

### Assistant

Python's `ssl` module can run a real TLS handshake in memory (using `MemoryBIO`), so it needs no network or open ports, which gets around the sandbox restriction from before. Writing the lab:

**→ Write** `{"file_path": "<workspace>/cert-lab/cert-lab.py", "content": "#!/usr/bin/env python3\n\"\"\"\nCertificate-error lab: reproduce the common TLS certificate errors, then show\nthe proper fix for each, and show what an attacker sees when verification is off.\n\nNo network or open ports needed: client and server do a real TLS handshake\nin memory (ssl.MemoryBIO). Needs only python3 (stdlib) and the ope … [9825 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/cert-lab/cert-lab.py (file state is current in your context — no need to Read it back)
```

</details>

**→ Bash** `{"command": "cd cert-lab && python3 cert-lab.py", "description": "Run the certificate-error lab"}`

<details><summary>result</summary>

```
Exit code 1
Workdir: /tmp/claude-501/cert-lab-2kemnl7l 

0. Healthy server (leaf + intermediate), normal client
  [ok] verification ON                                            -> connected (TLSv1.2)

1. Server forgot to send the intermediate certificate
  [ok] BROKEN: server sends leaf only                             -> unable to get local issuer certificate
  [ok] FIX: server sends fullchain.pem (leaf + intermediate)      -> connected (TLSv1.2)

2. Certificate has expired
  [ok] BROKEN: expired leaf                                       -> certificate has expired
  [ok] FIX: renew the cert (automate it)                          -> connected (TLSv1.2)

3. Clock is wrong / cert not valid yet
  [ok] BROKEN: notBefore in the future                            -> certificate is not yet valid

4. Hostname mismatch
  [ok] BROKEN: cert is for www.other-site.test                    -> Hostname mismatch, certificate is not valid for 'api.internal.test'.
  [ok] BROKEN: connecting by IP / wrong name to a good cert       -> IP address mismatch, certificate is not valid for '10.0.0.5'.
  [ok] FIX: connect using the name the cert was issued for        -> connected (TLSv1.2)

5. Server uses a company-internal CA
  [ok] BROKEN: client doesn't know Acme's root                    -> unable to get local issuer certificate
  [ok] FIX: add *that one* CA to the client's trust               -> connected (TLSv1.2)

6. Self-signed dev certificate
  [ok] BROKEN: self-signed                                        -> self signed certificate
  [ok] FIX (dev only): trust exactly that cert                    -> connected (TLSv1.2)

7. Why 'verify=False' is not a fix: an attacker in the middle (cafe wifi, rogue proxy, DNS hijack)
   The attacker makes their own CA and a cert for api.internal.test. It costs them one openssl command.
  [UNEXPECTED] verification ON  vs attacker                               -> self signed certificate in certificate chain
  [ok] verification OFF vs attacker          … [434 more chars]
```

</details>

**→ Edit** `{"replace_all": false, "file_path": "<workspace>/cert-lab/cert-lab.py", "old_string": "          False, \"unable to get local issuer certificate\")\n    stolen", "new_string": "          False, \"self signed certificate in certificate chain\")\n    stolen"}`

<details><summary>result</summary>

```
The file <workspace>/cert-lab/cert-lab.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

**→ Bash** `{"command": "cd cert-lab && python3 cert-lab.py | tail -14", "description": "Rerun the lab"}`

<details><summary>result</summary>

```
7. Why 'verify=False' is not a fix: an attacker in the middle (cafe wifi, rogue proxy, DNS hijack)
   The attacker makes their own CA and a cert for api.internal.test. It costs them one openssl command.
  [ok] verification ON  vs attacker                               -> self signed certificate in certificate chain
  [ok] verification OFF vs attacker                               -> connected (TLSv1.2)

   What the attacker's server received, decrypted:
     | GET /accounts HTTP/1.1
     | Host: api.internal.test
     | Authorization: Bearer sk_live_DO_NOT_LEAK

   The connection was 'encrypted', but to the attacker. With verification on, the attack fails;
   with it off, the same client hands over its credentials without any error.

Result: 15 checks behaved as expected, 0 unexpected
```

</details>

### Assistant

All 15 checks pass. Now the guide itself, written for the junior developer and built around the lab:

**→ Write** `{"file_path": "<workspace>/cert-lab/GUIDE.md", "content": "# Certificate errors: what they mean, and how to fix them without `verify=False`\n\n**Run this first:** `python3 cert-lab.py` (needs only Python 3 and `openssl`, no network).\nIt reproduces every error below with a real TLS handshake, shows the proper fix working,\nand in section 7 shows what an attacker receives when verification is turne … [7188 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/cert-lab/GUIDE.md (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

The lab covers the core claims. The per-tool table hasn't been tested yet, and Node is one of the most common places this habit shows up, so I'll check the Node rows too, again in memory:

**→ Write** `{"file_path": "<workspace>/cert-lab/node-check.mjs", "content": "// Checks the Node.js rows of GUIDE.md with in-memory TLS (no network).\n// Usage: node node-check.mjs <dir-with-certs-from-cert-lab>\nimport tls from \"node:tls\";\nimport fs from \"node:fs\";\nimport { duplexPair } from \"node:stream\";\n\nconst dir = process.argv[2];\nconst rd = (f) => fs.readFileSync(`${dir}/${f}`);\nconst HOST = … [1676 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/cert-lab/node-check.mjs (file state is current in your context — no need to Read it back)
```

</details>

**→ Bash** `{"command": "D=$(ls -dt /tmp/claude-501/cert-lab-* | head -1); echo \"-- plain\"; node node-check.mjs \"$D\"; echo \"-- with NODE_EXTRA_CA_CERTS=corp.crt (last line should now connect)\"; NODE_EXTRA_CA_CERTS=\"$D/corp.crt\" node node-check.mjs \"$D\" | tail -1", "description": "Verify Node.js error codes and CA options in memory"}`

<details><summary>result</summary>

```
Quoted text in this command can't be checked before it runs
```

</details>

**→ Bash** `{"command": "ls -dt /tmp/claude-501/cert-lab-* | head -1", "description": "Find the newest lab cert directory"}`

<details><summary>result</summary>

```
/tmp/claude-501/cert-lab-275madd1
```

</details>

**→ Bash** `{"command": "node node-check.mjs /tmp/claude-501/cert-lab-275madd1; echo ---; NODE_EXTRA_CA_CERTS=/tmp/claude-501/cert-lab-275madd1/corp.crt node node-check.mjs /tmp/claude-501/cert-lab-275madd1 | tail -1", "description": "Run Node checks, then with NODE_EXTRA_CA_CERTS"}`

<details><summary>result</summary>

```
This Bash command contains multiple operations. The following part requires approval: node node-check.mjs /tmp/claude-501/cert-lab-275madd1; echo ---; NODE_EXTRA_CA_CERTS=/tmp/claude-501/cert-lab-275madd1/corp.crt node node-check.mjs /tmp/claude-501/cert-lab-275madd1
```

</details>

**→ Bash** `{"command": "node node-check.mjs /tmp/claude-501/cert-lab-275madd1", "description": "Run Node.js certificate checks"}`

<details><summary>result</summary>

```
  missing intermediate                                 -> UNABLE_TO_VERIFY_LEAF_SIGNATURE
  hostname mismatch                                    -> ERR_TLS_CERT_ALTNAME_INVALID
  self-signed leaf                                     -> DEPTH_ZERO_SELF_SIGNED_CERT
  attacker chain                                       -> SELF_SIGNED_CERT_IN_CHAIN
  expired                                              -> CERT_HAS_EXPIRED
  corp CA via {ca: [root, corp]}                       -> connected, authorized
  attacker with rejectUnauthorized:false               -> connected, NOT authorized (SELF_SIGNED_CERT_IN_CHAIN)
  corp CA, no ca option (env decides)                  -> UNABLE_TO_VERIFY_LEAF_SIGNATURE
```

</details>

**→ Bash** `{"command": "NODE_EXTRA_CA_CERTS=/tmp/claude-501/cert-lab-275madd1/corp.crt node node-check.mjs /tmp/claude-501/cert-lab-275madd1", "description": "Run Node checks with an extra trusted CA"}`

<details><summary>result</summary>

```
This command requires approval
```

</details>

**→ Edit** `{"replace_all": false, "file_path": "<workspace>/cert-lab/GUIDE.md", "old_string": "With verification off, **a legitimate server and an attacker look exactly the same to your code.**\nThe error you silenced was the only thing that could tell them apart.", "new_string": "With verification off, **a legitimate server and an attacker look exactly the same to your code.**\nThe error you silenced was th … [293 more chars]`

<details><summary>result</summary>

```
The file <workspace>/cert-lab/GUIDE.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

**→ Edit** `{"replace_all": false, "file_path": "<workspace>/cert-lab/GUIDE.md", "old_string": "Error wording varies a little between libraries (`self signed` vs `self-signed`, etc.).", "new_string": "Error wording varies a little between libraries (`self signed` vs `self-signed`, etc.).\nNode.js codes (checked in `node-check.mjs`): missing intermediate / unknown CA \u2192 `UNABLE_TO_VERIFY_LEAF_SIGNATURE`,\n … [196 more chars]`

<details><summary>result</summary>

```
The file <workspace>/cert-lab/GUIDE.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

**→ Bash** `{"command": "python3 cert-lab.py | tail -1", "description": "Confirm the lab still passes"}`

<details><summary>result</summary>

```
Result: 15 checks behaved as expected, 0 unexpected
```

</details>

### Assistant

I've written a guide for your junior developer, plus a lab they run themselves that shows an attacker reading their credentials once certificate verification is off. Everything is in `cert-lab/`.

**You asked for → it became:** you asked for an explanation of HTTPS for a junior developer. It became a way to stop the habit itself: they see the attack happen on their own machine, then use a table that takes each error message to its cause and the proper fix.

**What's in `cert-lab/`:**
- **`cert-lab.py`** runs a real TLS handshake in memory, so it needs only Python and `openssl`, with no network. It covers seven cases. For six common errors, it shows the failure and then the fix working:
  - missing intermediate certificate
  - expired certificate
  - wrong clock
  - hostname or IP mismatch
  - company-internal CA
  - self-signed dev certificate

  In the seventh, an attacker makes their own certificate for the same hostname. With verification on, the connection is refused. With it off, the connection succeeds and the attacker reads `Authorization: Bearer sk_live_DO_NOT_LEAK` in plain text.
- **`GUIDE.md`**, in this order:
  - why encryption without authentication is worthless;
  - the attack output from the lab;
  - why "it's only dev / internal" doesn't hold;
  - a table from error message to cause to proper fix;
  - "trust only this one CA" commands for curl, Python, Node, Go, Java and system-wide, each next to the flag not to use;
  - `openssl s_client` diagnosis steps;
  - a checklist to go through before ever typing `verify=False`.
- **`node-check.mjs`** checks the Node.js claims in the guide.

**Outside check:**
- `cert-lab.py`: **15 of 15 checks behaved as expected.** One check failed on the first run, but my expectation was wrong, not the lab: the attacker's error is `self signed certificate in certificate chain`. That's the same message developers see behind corporate TLS-inspecting proxies, so the guide now covers both cases.
- `node-check.mjs`: all five Node error codes in the guide matched, and passing the CA through the `ca` option worked. It also turned up the most persuasive line for a junior: with `rejectUnauthorized: false`, Node reported `NOT authorized (SELF_SIGNED_CERT_IN_CHAIN)` and connected anyway. In other words, Node spotted the attack and was told to ignore it.

**Not verified:**
- **The `NODE_EXTRA_CA_CERTS` row:** the test run needed a permission approval I didn't push for.
- **The rows for `requests`, Go, Java and `keytool`:** none of these are installed here, so those rows are from documentation, not tested.
- **A real handshake with a public site:** network access was blocked.
- **TLS 1.3:** the system Python uses an old LibreSSL that negotiated TLS 1.2. Certificate verification behaves the same in 1.2 and 1.3.

**Stretch:** I set the target as "the guide proves every claim it makes, in more than one language." It got there for Python and Node, and stopped at the unverified rows above.

**To rerun:** `cd cert-lab && python3 cert-lab.py`. It exits non-zero if any check behaves unexpectedly, so it can also run in CI. For the Node checks, run `node node-check.mjs <certs-dir>`, using the work directory that `cert-lab.py` prints.

**For you to decide:**
- Do you want the "trust this CA" table cut down to your team's actual stack?
- Do you want a section on your company's proxy, if you have one (where to get its root CA)?
- A lint rule that flags `verify=False`, `rejectUnauthorized: false` and `-k` in code review would stop the habit coming back. Want me to add one?
