# HTTPS lab

Companion to [`../HTTPS-for-developers.md`](../HTTPS-for-developers.md). Needs `openssl` and `python3`; `curl` and `node` are optional extra clients. No installs, nothing touches your system trust store.

```bash
./setup.sh             # build fake PKI + broken servers (re-run any time to reset)
python3 mitm_demo.py   # 20 s: what verify=False actually costs   (tls-insecure-ok: docs)
python3 servers.py     # terminal 1
python3 check.py -v    # terminal 2: fix scenarios 1-5 until FIXED; canary must stay BLOCKED
./solutions.sh         # reference fixes (after you've tried)
```

| File | Role |
|---|---|
| `setup.sh` | Creates `pki/` (public root + intermediate, corporate proxy CA, attacker CA), `servers/<scenario>/`, `trust/ca-bundle.pem` |
| `servers.py` | One HTTPS server per scenario, ports 8443–8449; reloads certs per connection |
| `check.py` | Python + curl + Node clients, verification on; canary anti-cheat; exit 0 = all fixed |
| `mitm_demo.py` | Fake bank + attacker proxy: verify off leaks the token and swaps the IBAN; verify on blocks it |
| `tools/issue-cert.sh` | The lab's "CA desk": issue a correct (or deliberately broken) server cert |
| `tools/show-chain.sh` | Print subject / issuer / dates / SAN for a PEM file or a live `host:port` |
| `tools/find-insecure.sh` | Scan any repo for disabled TLS verification (CI / pre-commit) |
| `tools/selftest.sh` | Maintainer check that the lab itself works (needs `servers.py` running) |
