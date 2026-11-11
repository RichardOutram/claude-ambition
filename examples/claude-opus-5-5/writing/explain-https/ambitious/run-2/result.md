I wrote the guide on how HTTPS works, `HTTPS-for-developers.md`, and a hands-on `lab/` where the junior fixes 5 real certificate errors without turning verification off. Both are built around one idea: encryption is only worth something if you know who is on the other end, and verification is what tells you.

**You asked for → it became:**
- **You asked:** "Explain how HTTPS works." Sections 2–4 of the guide cover it in full: what HTTPS guarantees, the TLS 1.3 handshake step by step (including where verification happens), certificates, the chain of trust and trust stores.
- **It became:** material for a junior who keeps disabling verification, so they stop and fix errors properly instead.
  - **Hook:** `mitm_demo.py`. With verification off, a fake attacker silently steals an API token and swaps the bank account in the reply. With it on, the request is never sent.
  - **Error playbook:** for missing intermediate, self-signed, wrong hostname, expired and corporate proxy, the cause, how to diagnose it and the proper fix. It quotes the error messages exactly as Python, curl and Node print them, and shows how to trust an extra CA in Node, Python, pip, curl, git, Java, Go, Docker and on each OS.
  - **A 60-second triage flowchart:** which check failed, then which cause.
  - **The lab:** `check.py` tests every scenario through Python, curl and Node. A server signed by an "attacker" CA must stay blocked; if it ever connects, every fix counts for nothing.
- **Key finding:** in the lab, the attacker's certificate gives exactly the same error as the corporate proxy and the missing intermediate: `unable to get local issuer certificate`. So when you turn verification off, you can't know whether you're working around a config bug or being attacked. The guide is built around this.

**Outside check:**
- **Independent judge:** an independent judge agent solved the lab using only the guide and hints, without reading the solutions, and confirmed the attacker check and the demo work. Its verdict was pass with issues. It found:
  - **Scanner misses:** the guardrail script missed `curl -sk` and Postgres `sslmode=require`.
  - **Loophole:** scenario 5 could be passed with a server-side fix, skipping the client-side lesson.
  - **Outdated fact:** the certificate-lifetime statement was out of date for 2026. Since March 2026 the maximum is 200 days.
  - **Smaller inaccuracies:** browser trust stores, sending the root certificate, and the Java trust-store path.
- **After fixing all of them:** `lab/tools/selftest.sh` passes all 10 checks.
  - **Errors reproduce:** every error appears for real in all three clients.
  - **Cheats are caught:** trusting the attacker CA trips the check, and a server-side "fix" of the corporate proxy is reported as `WRONG FIX`.
  - **Reference fixes work:** they fix 5 of 5.
  - **The demo works:** the token leaks with verification off and is blocked with it on.
  - **The scanner holds:** it flags all 31 insecure samples, with no false positives on 13 safe ones.
- **Not re-run:** I didn't send the fixed version back to the judge.

**Stretch:** the aim was proving every claim by running it, across three languages, with cheats caught automatically. It falls short in four places:
- **Two stacks unchecked:** there are no Java or Go clients in the lab, so those instructions are researched rather than run.
- **TLS 1.3 not demonstrable:** macOS's built-in Python only speaks TLS 1.2, so the TLS 1.3 handshake is explained but can't be shown live.
- **Browser behaviour not demonstrable:** "works in the browser, fails in my code" depends on browsers fetching missing intermediates, which the lab can't reproduce.
- **No real junior has tried it:** the judge stood in for one.

**Locked in:**
- **Rerun the lab:** `cd lab && ./setup.sh`, then `python3 servers.py` in one terminal and `python3 check.py -v` in another.
- **After editing:** run `tools/selftest.sh` with the servers running (it should show 10 passes), then `./setup.sh` to reset the lab for learners.
- **Guardrail:** `lab/tools/find-insecure.sh` scans any repo for disabled verification and exits non-zero, so it can go in CI or a pre-commit hook.
- **Maintenance notes:** `CLAUDE.md` says how to re-check everything and when to refresh the quoted error messages.
- **State:** the lab is reset to its broken starting state and the servers are stopped.

**For you to decide:** whether to hand the junior the guide first or the lab first. I'd start with the 20-second demo (`python3 lab/mitm_demo.py`) and ask them to run `find-insecure.sh` on their own repo.

Files are in the working directory:
- `HTTPS-for-developers.md`
- `CLAUDE.md`
- `lab/README.md`
- `lab/setup.sh`
- `lab/servers.py`
- `lab/check.py`
- `lab/mitm_demo.py`
- `lab/solutions.sh`
- `lab/tools/find-insecure.sh`