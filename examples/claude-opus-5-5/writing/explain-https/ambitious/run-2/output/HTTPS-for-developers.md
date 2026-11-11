# How HTTPS works, and how to fix certificate errors without turning verification off

**Who this is for:** developers who know web basics (HTTP, requests, headers, APIs) but not much cryptography. It's especially for anyone who has typed `verify=False`, `rejectUnauthorized: false` or `curl -k` to "make it work".

**What you'll be able to do afterwards:** read any certificate error, name its real cause in under a minute, and fix it properly in Python, Node, curl, Java, Go, Docker or CI.

**Time:** about 30 minutes to read and 30–45 minutes for the hands-on lab in [`lab/`](lab/). It needs only `openssl` and `python3`. `curl` and `node` are optional and add more examples.

---

## 0. The whole thing in one paragraph

HTTPS encrypts your traffic. But **encryption is only worth anything if you know who is on the other end**, because you can have a perfectly encrypted conversation with an attacker. The certificate check is how your client confirms it's really talking to `api.stripe.com` and not to whoever controls the café Wi-Fi. When you disable verification, you keep the encryption and throw away the answer to "encrypted *to whom*?" Certificate errors are almost always a configuration problem with a specific, findable cause. This guide teaches you to find it.

---

## 1. Start here: watch it happen (2 minutes)

```bash
cd lab
./setup.sh            # builds a tiny fake internet: CAs, certificates, a fake bank, an attacker
python3 mitm_demo.py
```

Real output:

```
=== Run 1: verification OFF ===
  app sees:      HTTP 200, encrypted, no errors. Response: {'status': 'ok', 'payout_to': 'LT12 1000 0111 0100 1000 (attacker)'}
  attacker log:  Authorization: Bearer FAKE-prod-api-key-imagine-this-is-real-0000
                 body: {"amount_eur": 48000, "invoice": "INV-2291"}

=== Run 2: verification ON (the default) ===
  app sees:      ssl.SSLCertVerificationError: unable to get local issuer certificate
  attacker log:  nothing. The request was never sent.
```

Look at three things:

1. **Run 1 shows no error at all.** The connection was encrypted and returned HTTP 200. The attacker read your API key, passed the request on to the real bank so everything looked normal, and **changed the account number in the reply**. Nothing in your logs would show it.
2. **Run 2 failed before your request left your machine.** The error that annoyed you is exactly what protected you.
3. **The message is `unable to get local issuer certificate`.** It's the same message you get from a misconfigured server or a corporate proxy. So **you cannot tell "the server is misconfigured" apart from "I'm being attacked" by reading the error message.** You have to look. That's the core reason "just disable it" is never a diagnosis.

"Attacker on the network path" isn't exotic. It covers public Wi-Fi, a compromised home router, DNS hijacking, a malicious browser extension or proxy, a compromised container sidecar, BGP hijacks, and anyone with access to a network your traffic crosses, including inside a cloud VPC.

---

## 2. What HTTPS actually promises

HTTPS is HTTP sent inside a **TLS** connection. TLS gives you three guarantees:

| Guarantee | Meaning | What provides it |
|---|---|---|
| **Confidentiality** | Nobody in between can read the traffic | Encryption with keys negotiated in the handshake |
| **Integrity** | Nobody in between can change it undetected | Authenticated encryption (AEAD: AES-GCM, ChaCha20-Poly1305) |
| **Authentication** | You're talking to the real `example.com` | **The certificate check** |

The first two are only meaningful together with the third. If you don't know who you agreed keys with, you might have agreed them with the attacker. Then the attacker decrypts, reads, edits and re-encrypts, as in Run 1. **`verify=False` keeps the first two guarantees and makes them worthless.**

---

## 3. The handshake, step by step

This is TLS 1.3, the current version, simplified. (TLS 1.2, which the lab's macOS Python speaks, has more round trips but the same logic.)

```
 Client (your app)                                         Server (example.com)
 ─────────────────                                         ────────────────────
 1. ClientHello ─────────────────────────────────────────▶
    "I want example.com (SNI). I support these ciphers.
     Here's my half of a key exchange (ECDHE key share)."

                         ◀──────────────────────────────── 2. ServerHello
                                                    "Here's my half of the key exchange."
             ── both sides now compute the same secret; everything after this is encrypted ──
                         ◀──────────────────────────────── 3. Certificate
                                                    "Here's my certificate chain."
                         ◀──────────────────────────────── 4. CertificateVerify
                                                    "Here's a signature over this whole handshake,
                                                     made with the private key matching my certificate."
                         ◀──────────────────────────────── 5. Finished
 6. ★ VERIFY ★  (this is the step you've been switching off)
    a. Does the chain lead to a root I trust?
    b. Is the certificate valid for "example.com"?
    c. Is it within its validity dates?
    d. Does the step-4 signature check out with the certificate's public key?
 7. Finished ────────────────────────────────────────────▶
 8. HTTP request (headers, cookies, tokens) ─────────────▶   ← only sent if step 6 passed
```

The key ideas:

- **Key exchange (steps 1–2)** uses ephemeral Diffie–Hellman (ECDHE). Both sides combine their own secret with the other side's public share and arrive at the same key, which an eavesdropper can't compute. The keys are thrown away after the connection, so recording traffic today and stealing the server's key later still doesn't decrypt it. That property is called *forward secrecy*.
- **But anyone can do a key exchange**, including an attacker. So far you have an encrypted channel to *someone*.
- **Steps 3–4 are the identity claim.** The certificate says "this public key belongs to example.com, signed by a CA". The CertificateVerify signature proves the server **holds the matching private key**, so it can't just replay someone else's public certificate.
- **Step 6 is where your client decides whether to believe the claim.** If it doesn't check, steps 3–4 are just decoration.
- **Step 8: your secrets are sent only after step 6 passes.** That's why Run 2 in the demo leaked nothing.

---

## 4. Certificates and the chain of trust

### What's in a certificate

You can see this for real with `lab/tools/show-chain.sh lab/servers/ok/cert.pem`:

```
[0] subject=CN=localhost                               ← who it's for (legacy field)
    issuer=CN=Lab Public Intermediate CA               ← who vouches for it
    notBefore=Nov 11 19:36:50 2026 GMT                 ← valid from
    notAfter=Feb  9 19:36:50 2027 GMT                  ← valid until
    SAN: DNS:localhost, IP Address:127.0.0.1           ← the names it is ACTUALLY valid for
[1] subject=CN=Lab Public Intermediate CA
    issuer=CN=Lab Public Root CA
    ...
(2 certificate(s) presented)
```

A certificate is a public key plus a name (or names) plus validity dates, all **signed by an issuer**. Clients match the hostname against the **Subject Alternative Name (SAN)** list. The CN is ignored for this by modern clients.

### The chain

```
 Root CA  (self-signed; preinstalled in your trust store; kept offline)
   └─ signs ─▶ Intermediate CA  (does the day-to-day signing)
                 └─ signs ─▶ Leaf certificate for example.com  (what the server presents)
```

- The **server** must send its **leaf + intermediate(s)**. It doesn't need to send the root: the client must already have it, and a root that arrives over the network proves nothing. Sending it is harmless, just wasted bytes.
- The **client** builds a path from the leaf up to a root that's in its **trust store**, checking each signature on the way.
- A **trust store** is just a file or directory of root certificates you've decided to believe.

### Every runtime has its own trust store

This one fact explains most "works here, fails there" mysteries:

| Runtime | Default trust store |
|---|---|
| Browsers | Chrome and Firefox ship their own root lists; Safari/Edge use the OS. All of them also honour CAs your IT team adds to the OS store |
| macOS / Windows native apps | OS store (Keychain / Windows certificate store) |
| `curl` / `git` / `wget` on Linux | OS bundle, e.g. `/etc/ssl/certs/ca-certificates.crt` |
| Python `requests`, `pip` (older) | **`certifi`** package bundle. Ignores the OS store |
| Python stdlib `ssl` / `urllib` | OpenSSL default paths (`python3 -c "import ssl; print(ssl.get_default_verify_paths())"`) |
| Node.js | **Bundled Mozilla roots** compiled into Node. Ignores the OS store unless told otherwise |
| Java | `$JAVA_HOME/lib/security/cacerts` |
| Go | OS store |
| A Docker image | Whatever is in the image. Slim and distroless images may have **none** |

So "it works in my browser but fails in Python" usually means the CA, intermediate or corporate root is in one trust store and not the other. It does *not* mean Python is broken.

---

## 5. The four checks, and the errors each one produces

| Check | Fails when | Typical error text |
|---|---|---|
| **Chain to a trusted root** | Missing intermediate, self-signed cert, private/corporate CA, attacker | `unable to get local issuer certificate`, `self-signed certificate`, `self signed certificate in certificate chain`, `unable to verify the first certificate`, `PKIX path building failed` (Java), `x509: certificate signed by unknown authority` (Go) |
| **Hostname matches SAN** | Wrong name, IP vs name, missing `www.` or wildcard depth | `Hostname mismatch`, `no alternative certificate subject name matches`, `ERR_TLS_CERT_ALTNAME_INVALID`, `x509: certificate is valid for X, not Y` |
| **Validity dates** | Expired, not yet valid, **or your clock is wrong** | `certificate has expired`, `certificate is not yet valid`, `CERT_HAS_EXPIRED` |
| **Signature / key usage** | Rare: broken cert, wrong key pair, policy violations | `key values mismatch` (server side), `Basic Constraints of CA cert not marked critical` (Python 3.13+ strict mode) |

Notice that **the first row covers four completely different situations, including an attack**, and they all share one error message. The message tells you *which check* failed. To find out *why*, you look at the chain (section 7).

---

## 6. The error playbook

These messages are verbatim from running `lab/check.py -v` with Python 3.9 (LibreSSL), curl 8.7 and Node 24 (OpenSSL 3.5). Exact wording varies a little between library versions.

### 6.1 Missing intermediate: "works in the browser, fails in my code"

```
python  unable to get local issuer certificate
curl    (60) SSL certificate problem: unable to get local issuer certificate
node    UNABLE_TO_VERIFY_LEAF_SIGNATURE: unable to verify the first certificate; if the root CA is installed
        locally, try running Node.js with --use-system-ca
```

- **Cause:** the server sends only its leaf certificate, not the intermediate. Browsers often hide this: Chrome, Edge and Safari fetch the missing intermediate themselves (via the cert's "AIA" URL), and Firefox ships known intermediates. Most libraries don't, so the problem shows up in your code and nowhere else.
- **Diagnose:** `lab/tools/show-chain.sh host:443` shows `(1 certificate(s) presented)`, and the leaf's issuer is an intermediate, not a root. Or run `openssl s_client -connect host:443 -servername host -showcerts </dev/null` and count the `BEGIN CERTIFICATE` blocks.
- **Right fix (server side):** configure the server to send the full chain. For nginx with certbot: `ssl_certificate /etc/letsencrypt/live/host/fullchain.pem;`, **not** `cert.pem`. Apache 2.4.8+: `SSLCertificateFile` pointing to the fullchain. Node: pass the leaf and intermediate concatenated in `cert`. On load balancers (AWS ACM, GCP), upload the chain too.
- **If you don't own the server:** tell its owner. This is their bug, and every non-browser client is hitting it. As a *temporary, explicit* workaround, you may add **that specific intermediate** to your client's trust bundle (see section 6.5 for how). Never disable verification.

### 6.2 Self-signed certificate

```
python  unable to get local issuer certificate          (OpenSSL 3 builds say: self-signed certificate)
curl    (60) SSL certificate problem: unable to get local issuer certificate
node    DEPTH_ZERO_SELF_SIGNED_CERT: self-signed certificate
```

- **Cause:** the certificate signs itself, so nothing you trust vouches for it. This is common for dev servers, appliances, internal tools, and "I generated a cert with one openssl command".
- **Diagnose:** in `show-chain.sh`, `subject` equals `issuer` and there's only one certificate.
- **Right fixes, best first:**
  1. **Get a real certificate.** For anything reachable by a name on the internet, use Let's Encrypt (certbot, Caddy and Traefik do it automatically). For internal services, use your company's internal CA (often through cert-manager in Kubernetes, Vault or AWS Private CA).
  2. **Local development:** use [`mkcert`](https://github.com/FiloSottile/mkcert). It creates a local CA, installs it in your OS and browser trust stores, and issues `localhost` certs that just work. (Node and Python `requests` still need to be pointed at it, see 6.5: `mkcert -CAROOT` shows where it is.)
  3. **Pinning one specific cert**, for example an appliance you can't change: add **that one certificate** to your client's trust bundle for **that one client** (the syntax for each stack is in the table in 6.5). This trusts exactly one key, unlike `verify=False`, which trusts everyone.

### 6.3 Hostname mismatch

```
python  Hostname mismatch, certificate is not valid for 'localhost'.
curl    (60) SSL: no alternative certificate subject name matches target host name 'localhost'
node    ERR_TLS_CERT_ALTNAME_INVALID: Hostname/IP does not match certificate's altnames: Host: localhost. is not in the cert's altnames: DNS:staging.lab.test
```

- **Cause:** the certificate is valid but for a different name. Typical cases: connecting by IP address (`https://10.0.3.7`) to a cert that only lists names; `example.com` vs `www.example.com`; a wildcard `*.example.com` doesn't cover `a.b.example.com` or `example.com` itself; an internal name vs a public name; or a shared IP serving the wrong site because the client didn't send SNI.
- **Diagnose:** compare the URL's host with the `SAN:` line in `show-chain.sh`. Node prints both for you.
- **Right fix:** either **connect using a name that's in the SAN** (fix the URL or config; in tests use `curl --resolve name:443:IP` rather than the bare IP), or **re-issue the certificate with every name clients actually use** in the SAN.
- **Don't** set `check_hostname = False` or use a custom `checkServerIdentity` that returns nothing. A valid certificate for *any* name is trivially easy for an attacker to get: any CA will issue them a cert for `attacker.com`.

### 6.4 Expired (or "not yet valid")

```
python  certificate has expired
curl    (60) SSL certificate problem: certificate has expired
node    CERT_HAS_EXPIRED: certificate has expired
```

- **Cause:** past `notAfter`. Public certificates are short-lived on purpose: since March 2026 the maximum is 200 days, falling to 100 days in 2027 and 47 days in 2029 (CA/Browser Forum ballot SC-081). Let's Encrypt certs last 90 days. Manual renewal is a losing game.
- **Diagnose:** look at `notAfter` in `show-chain.sh`, **and check your own clock** (`date -u`). A VM, container or CI runner with a skewed clock produces "expired" or "not yet valid" errors for perfectly good certificates.
- **Right fix:** renew, then **automate renewal** (ACME / certbot / cert-manager) and add expiry monitoring, such as an alert 14 days before. If the clock is wrong, fix NTP.

### 6.5 Corporate TLS-inspection proxy (Zscaler, Netskope, Palo Alto, Blue Coat…)

```
python  unable to get local issuer certificate
curl    (60) SSL certificate problem: unable to get local issuer certificate
node    UNABLE_TO_VERIFY_LEAF_SIGNATURE: unable to verify the first certificate
```

- **Cause:** your company's network deliberately intercepts TLS. It re-signs every site's certificate with the company's own CA. IT installed that CA in the OS store, so browsers are happy, but Python, Node, Docker images and Java use their **own** stores, as described in section 4.
- **This is technically the same thing as the attack in section 1.** The only difference is that you've **confirmed out-of-band** that this CA belongs to your employer. Run the lab and you'll see the corp-proxy scenario and the attacker canary produce **identical** errors.
- **Diagnose:** the issuer in `show-chain.sh` is something like `CN=Zscaler Root CA` or `CN=<Company> TLS Inspection` instead of a public CA (DigiCert, Let's Encrypt/ISRG, Sectigo, Google Trust Services…). Try the same URL from off the corporate network or VPN: if it works there, it's the proxy.
- **Right fix:** get the corporate root CA certificate from IT (or export it from your OS keychain), **check its SHA-256 fingerprint against one IT gives you over a separate channel** (`openssl x509 -in corp-ca.pem -noout -fingerprint -sha256`), then add **that one CA** to each runtime's trust store.

**Adding one trusted CA, per stack.** This is the client-side tool for 6.1 (temporary), 6.2 (pinning) and 6.5:

| Stack | Add one extra CA (keeps the public roots) |
|---|---|
| **Node** | `export NODE_EXTRA_CA_CERTS=/path/corp-ca.pem` (read at startup). Newer Node: `node --use-system-ca` uses the OS store. In code: `ca: [...tls.rootCertificates, fs.readFileSync('corp-ca.pem')]`, because a bare `ca:` **replaces** the built-in roots |
| **npm** | `npm config set cafile /path/corp-ca.pem` |
| **Python `requests`** | `REQUESTS_CA_BUNDLE` and `verify="..."` **replace** certifi, so build a combined bundle: `cat "$(python -m certifi)" corp-ca.pem > combined.pem` then `export REQUESTS_CA_BUNDLE=$PWD/combined.pem`. Or, on Python 3.10+: `pip install truststore` and `import truststore; truststore.inject_into_ssl()` to use the OS store |
| **Python stdlib / httpx** | `ssl.create_default_context(cafile="combined.pem")`, then pass that context (`httpx.Client(verify=ctx)`). Or `export SSL_CERT_FILE=combined.pem` |
| **pip** | `pip config set global.cert /path/combined.pem` (or `PIP_CERT`). Recent pip on Python 3.10+ can use the OS store via truststore |
| **curl** | `curl --cacert combined.pem …` or `export CURL_CA_BUNDLE=…`. Usually just install into the OS store (below) |
| **git** | `git config --global http.sslCAInfo /path/combined.pem` |
| **Java** (9+) | `keytool -importcert -cacerts -alias corp-ca -file corp-ca.pem -storepass changeit` (default store password). JDK upgrades replace that file, so redo it after upgrading (or bake it into your image). Debian/Ubuntu's packaged Java instead uses `/etc/ssl/certs/java/cacerts`, rebuilt by `update-ca-certificates`. Alternative: your own truststore via `-Djavax.net.ssl.trustStore=…` |
| **Go** | Install into the OS store. On Linux, `SSL_CERT_FILE` / `SSL_CERT_DIR` also work |
| **Debian/Ubuntu/Alpine** | `cp corp-ca.pem /usr/local/share/ca-certificates/corp-ca.crt && update-ca-certificates` (the extension **must** be `.crt`) |
| **RHEL/Fedora** | `cp corp-ca.pem /etc/pki/ca-trust/source/anchors/ && update-ca-trust` |
| **macOS** | `sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain corp-ca.pem` |

**Docker / CI pattern** (Debian-based image):

```dockerfile
COPY corp-ca.crt /usr/local/share/ca-certificates/corp-ca.crt
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
 && update-ca-certificates
# Point runtimes that ignore the OS store at it:
ENV NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/corp-ca.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
```

Only add the corporate CA in images built on and for the corporate network. Production images talking to the public internet shouldn't need it.

### 6.6 Three more you'll meet

- **Every HTTPS call fails inside a container** with `unable to get local issuer certificate`, even to `google.com`. The image has no CA bundle at all, which is common with `-slim`, `alpine` and `scratch` images. Fix: `apt-get install ca-certificates` / `apk add ca-certificates`, or copy `/etc/ssl/certs/ca-certificates.crt` into `scratch` images.
- **Fine on Python 3.12, fails on 3.13** with `Basic Constraints of CA cert not marked critical` or `Missing Authority Key Identifier`. Python 3.13 turned on stricter X.509 checking by default, and some old corporate or appliance CAs are slightly non-compliant. Right fix: have the CA re-issued properly. Temporary, explicit workaround: clear only that flag (`ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT`) on a context that still verifies.
- **Was working, suddenly broke for everyone:** a root or intermediate expired or was distrusted. Update the trust store (`certifi`, OS packages, the Node version) and make sure the server's chain uses the current intermediate.

---

## 7. Your diagnosis kit: three commands

```bash
# 1. What does the server actually send? (chain, names, dates, issuer)
lab/tools/show-chain.sh example.com:443
#   or raw:  openssl s_client -connect example.com:443 -servername example.com -showcerts </dev/null

# 2. What does a client conclude, and why? (shows the handshake and the exact failing check)
curl -v https://example.com/ 2>&1 | grep -E '^\*'

# 3. What is my client trusting?
python3 -c "import ssl; print(ssl.get_default_verify_paths())"
python3 -c "import certifi; print(certifi.where())"
node -p "require('tls').rootCertificates.length"
```

A 60-second triage flow:

```
Which check failed? (read the error, use the table in section 5)
├── hostname   → compare the URL host with the SAN                        → 6.3
├── dates      → check notAfter AND `date -u`                             → 6.4
└── chain      → run show-chain.sh: who is the issuer of the top cert sent?
    ├── a public CA intermediate, only 1 cert sent → missing intermediate → 6.1
    ├── subject == issuer                          → self-signed          → 6.2
    ├── your company's CA / inspection proxy       → corporate proxy      → 6.5
    ├── a public CA, and it fails for every site   → empty trust store    → 6.6
    └── something you don't recognise              → STOP. Don't connect. Ask someone.
                                                     This is the case verification exists for.
```

---

## 8. The lab: break it, then fix it properly

```bash
cd lab
./setup.sh              # (re)builds everything and resets your fixes
python3 servers.py      # terminal 1: seven HTTPS servers on ports 8443–8449
python3 check.py -v     # terminal 2: checks each one with Python, curl AND Node, verification ON
```

`check.py` starts like this, with every error reproduced for real:

```
  [   OK   ] 8443  control: correctly configured server
  [FAILING ] 8444  1. server forgets to send the intermediate
  [FAILING ] 8445  2. self-signed certificate
  [FAILING ] 8446  3. certificate is for a different hostname
  [FAILING ] 8447  4. certificate has expired
  [FAILING ] 8448  5. corporate TLS-inspection proxy
  [BLOCKED ] 8449  canary: attacker's certificate, must stay BLOCKED
```

**Your job:** make scenarios 1–5 say `FIXED` while the canary stays `BLOCKED`. Servers reload certificates on every connection, so you never need to restart them.

What you can touch, just as in real life:

- `servers/<scenario>/cert.pem` and `key.pem`: the server's configuration (scenarios 1–4).
- `tools/issue-cert.sh <dir> "<SAN>"`: the lab's "certificate authority desk", standing in for Let's Encrypt or your internal CA. Run it without extra flags to get a correct, chained certificate from the lab's public CA.
- `pki/public-intermediate/ca.pem`: the intermediate certificate (public information, like on any CA's website).
- `it-helpdesk-email.txt` and `pki/corp-proxy-ca/ca.pem`: what IT sent you for scenario 5, including the fingerprint to check. The proxy itself belongs to IT, so if you "fix" scenario 5 by re-issuing the server's cert, the checker reports `WRONG FIX`.
- `trust/ca-bundle.pem`: **the client's trust store**, used by all three clients (scenario 5).
- `tools/show-chain.sh <file or host:port>`: your diagnostic tool. Use it before every fix.

Rules: verification stays on. If you ever get the canary to connect, the checker prints `CANARY BREACHED` and every fix you've made counts for nothing. That's exactly what happens in real life when you trust the wrong CA or disable checking.

Hints, if you need them:

<details><summary>Scenario 1</summary>A server must send leaf + intermediate. What's in <code>servers/missing-intermediate/cert.pem</code> right now? What should be appended?</details>
<details><summary>Scenario 2</summary>Don't trust the self-signed cert. Get the server a cert from a CA the client already trusts.</details>
<details><summary>Scenario 3</summary>The client connects to <code>localhost</code>. What names does the cert list?</details>
<details><summary>Scenario 5</summary>This is the one fix that belongs on the <i>client</i>. Read <code>it-helpdesk-email.txt</code>, and compare its fingerprint with <code>openssl x509 -in pki/corp-proxy-ca/ca.pem -noout -fingerprint -sha256</code> before trusting anything.</details>

When you're done (or stuck), compare with `./solutions.sh`, which applies the reference fixes and re-runs the checker:

```
  [   OK   ] 8443  control: correctly configured server
  [ FIXED  ] 8444  1. server forgets to send the intermediate
  [ FIXED  ] 8445  2. self-signed certificate
  [ FIXED  ] 8446  3. certificate is for a different hostname
  [ FIXED  ] 8447  4. certificate has expired
  [ FIXED  ] 8448  5. corporate TLS-inspection proxy
  [BLOCKED ] 8449  canary: attacker's certificate, must stay BLOCKED

5/5 scenarios fixed, canary blocked.  All done: you fixed TLS without turning it off.
```

---

## 9. Keep it fixed: a guardrail for your repo

`lab/tools/find-insecure.sh` scans a codebase for 20+ ways of disabling verification across Python, Node, Go, Java, .NET, PHP, curl, wget, git, pip, npm and Postgres connection strings. It exits non-zero if it finds any, so you can use it in CI or a pre-commit hook:

```bash
lab/tools/find-insecure.sh src/ scripts/ Dockerfile .github/
```

```
TLS verification appears to be disabled here:
  src/client.py:14:    r = requests.get(url, verify=False)
```

If a line is genuinely justified (a demo, a test of failure behaviour), mark it so a reviewer can see the decision: `# tls-insecure-ok: <reason>`.

---

## 10. "But…"

- **"It's only internal traffic."** Internal networks are where attackers go after the first foothold (lateral movement), and "internal" APIs usually carry the most sensitive data and credentials. Internal services should use an internal CA. That's what it's for.
- **"It's only dev / only a test."** `verify=False` written in dev gets copied, committed and deployed. It also trains you to click past the one warning that matters. Use mkcert locally.
- **"The error is the library's fault."** It almost never is. In the lab, three different TLS libraries agree on every scenario. The error is telling the truth about a misconfiguration.
- **"Is disabling verification ever OK?"** Honestly: for 30 seconds on your own machine, to answer "is the rest of my code working?", and never committed. Even then, `curl -v` plus `show-chain.sh` usually answers the real question faster.
- **"At least it's still encrypted."** To whom? (Section 1.)

---

## 11. Mini-glossary

- **TLS:** the protocol under HTTPS (the successor to SSL; "SSL" survives only as a name).
- **Certificate / X.509:** a signed statement that a public key belongs to certain names, valid for certain dates.
- **CA (Certificate Authority):** an organisation whose signature clients trust. **Root CA:** one whose certificate is in the trust store. **Intermediate CA:** signed by a root, does the everyday signing.
- **Trust store / CA bundle:** the set of root certificates a client believes.
- **SAN:** the list of hostnames and IPs a certificate is valid for.
- **SNI:** the hostname the client sends in ClientHello, so one IP can serve many sites.
- **Chain / fullchain:** leaf + intermediates, as the server should send them.
- **MITM:** man-in-the-middle, an attacker who relays and can read or modify traffic between you and the server.
- **Pinning:** trusting a specific certificate or key rather than "anything a CA signed".
