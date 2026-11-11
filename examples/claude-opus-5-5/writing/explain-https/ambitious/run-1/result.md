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