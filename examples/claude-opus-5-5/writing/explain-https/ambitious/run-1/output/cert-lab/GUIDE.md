# Certificate errors: what they mean, and how to fix them without `verify=False`

**Run this first:** `python3 cert-lab.py` (needs only Python 3 and `openssl`, no network).
It reproduces every error below with a real TLS handshake, shows the proper fix working,
and in section 7 shows what an attacker receives when verification is turned off.

---

## 1. What verification actually protects

HTTPS gives you two things, and you need both:

1. **Encryption:** nobody in between can read the traffic.
2. **Authentication:** the other end really is `api.example.com`.

Encryption without authentication is worthless. If you don't check *who* you're talking to,
you can have a perfectly encrypted conversation **with the attacker**, who decrypts it,
reads it, and passes it on to the real server. You won't notice anything, because the request still works.

Certificate verification **is** the authentication. Turning it off doesn't skip a fussy check.
It removes half of what HTTPS is for.

## 2. Why "but it works now" is the dangerous part

From the lab, section 7: the attacker makes their own CA and issues a cert for
`api.internal.test`. That takes one `openssl` command, and anyone can do it.

```
verification ON  vs attacker  -> self signed certificate in certificate chain   (attack blocked)
verification OFF vs attacker  -> connected                                     (attack works)

What the attacker's server received, decrypted:
  | GET /accounts HTTP/1.1
  | Host: api.internal.test
  | Authorization: Bearer sk_live_DO_NOT_LEAK
```

With verification off, **a legitimate server and an attacker look exactly the same to your code.**
The error you silenced was the only thing that could tell them apart.

Node.js makes this very visible (from `node-check.mjs`):

```
attacker with rejectUnauthorized:false -> connected, NOT authorized (SELF_SIGNED_CERT_IN_CHAIN)
```

Node *detected* the attack, and then connected anyway, because it was told to.

Where attackers sit in the middle in practice: public or hotel wifi, a compromised router,
DNS hijacking or poisoning, a malicious proxy, a hostile network inside a cloud or CI environment.

And "it's only dev" / "it's only internal" doesn't hold up:
- `verify=False` copied from a dev script ends up in production. It always does.
- Internal networks get breached; that's how attackers move sideways once they're in.
- The flag is usually set globally (`NODE_TLS_REJECT_UNAUTHORIZED=0`, a shared session, a curl alias),
  so it switches off checking for *every* connection, not only the one you were debugging.

## 3. The rule

> **A certificate error is a message about a specific problem. Read it, find the cause, fix that.**
> The fix is almost never "trust everything". At most it's "trust *this one* CA".

## 4. Triage table

Error wording varies a little between libraries (`self signed` vs `self-signed`, etc.).
Node.js codes (checked in `node-check.mjs`): missing intermediate / unknown CA → `UNABLE_TO_VERIFY_LEAF_SIGNATURE`,
proxy or attacker root → `SELF_SIGNED_CERT_IN_CHAIN`, self-signed → `DEPTH_ZERO_SELF_SIGNED_CERT`,
expired → `CERT_HAS_EXPIRED`, wrong name → `ERR_TLS_CERT_ALTNAME_INVALID`.

| Error message (contains…) | What it means | Usual cause | Proper fix |
|---|---|---|---|
| `unable to get local issuer certificate` / `unable to verify the first certificate` | Client can't build a chain from the server's cert to a root it trusts | **(a)** Server doesn't send its intermediate cert. **(b)** Server uses a private/company CA. **(c)** Your machine or container has no CA bundle | (a) Server must send `fullchain.pem`, not `cert.pem`. (b) Add *that* CA to the client (§5). (c) Install CA certs: `apt-get install ca-certificates`, on macOS Python run `Install Certificates.command` |
| `self signed certificate in certificate chain` | The chain ends in a root you don't trust | Corporate TLS-inspecting proxy (Zscaler, Netskope…), a private CA, **or an attack** | Get the company's root CA from IT and add it (§5). If you're *not* behind such a proxy, stop and investigate |
| `self signed certificate` / `DEPTH_ZERO_SELF_SIGNED_CERT` | The server's cert signed itself | Local dev server, appliance, test env | Dev: use `mkcert` (makes a local CA your machine trusts), or trust that exact cert (§5). Prod: get a real cert (Let's Encrypt is free) |
| `certificate has expired` | Past its `notAfter` date | Renewal not automated or failed | Renew; automate it (certbot / cert-manager / your cloud's managed certs); monitor expiry |
| `certificate is not yet valid` | Before its `notBefore` date | **Your clock is wrong** (VMs, containers, dead CMOS battery), or a cert issued seconds ago | Fix time sync (NTP) |
| `Hostname mismatch` / `ERR_TLS_CERT_ALTNAME_INVALID` / `IP address mismatch` | Cert is valid, but for a different name | Connecting by IP, by an internal alias, or `localhost`, while the cert is for `api.example.com` | Connect using the name in the cert, or reissue the cert with the right name in its SAN list |
| `certificate revoked` | The CA has withdrawn it | Key compromise or mis-issuance | Server must get a new cert. Do not work around this |

## 5. "Trust this one CA". The correct escape hatch, per tool

Get the CA certificate (PEM file) from whoever runs the server or proxy, e.g. `acme-root.pem`.

| Tool | Do this | Not this |
|---|---|---|
| curl | `curl --cacert acme-root.pem https://…` | `curl -k` |
| Python `requests` | `requests.get(url, verify="acme-root.pem")` or env `REQUESTS_CA_BUNDLE=/path/bundle.pem` | `verify=False` |
| Python `ssl` / `httpx` / `urllib` | `ssl.create_default_context(cafile="acme-root.pem")`, or `SSL_CERT_FILE` | `CERT_NONE`, `check_hostname=False` |
| Node.js | env `NODE_EXTRA_CA_CERTS=/path/acme-root.pem` (adds to the defaults) or `{ ca: fs.readFileSync(…) }` | `NODE_TLS_REJECT_UNAUTHORIZED=0`, `rejectUnauthorized: false` |
| Go | add the PEM to an `x509.CertPool` and set `tls.Config{RootCAs: pool}` | `InsecureSkipVerify: true` |
| Java | `keytool -importcert -keystore truststore.jks -file acme-root.pem` and point `javax.net.ssl.trustStore` at it | a trust-all `TrustManager` |
| Whole machine / container | Debian/Ubuntu: copy to `/usr/local/share/ca-certificates/acme.crt` and run `update-ca-certificates` | |

Notes:
- `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` **replace** the default bundle; `NODE_EXTRA_CA_CERTS` **adds** to it.
  If public sites break after setting a replacing variable, build a bundle containing the public roots *plus* yours.
- Trust the CA in the narrowest place that works: this request > this app > this machine.

## 6. How to diagnose, step by step

```bash
# 1. See exactly what the server sends and why verification fails
openssl s_client -connect api.example.com:443 -servername api.example.com -showcerts </dev/null
#    Look at: "Certificate chain" (how many certs? is the intermediate there?),
#    "Verify return code" at the bottom, and the s:/i: (subject/issuer) lines.

# 2. Inspect a cert: names, dates, issuer
openssl x509 -in cert.pem -noout -subject -issuer -dates -ext subjectAltName

# 3. Check your clock
date -u

# 4. Is something intercepting? Compare the issuer you see with what the site really uses.
#    An issuer like "Zscaler Root CA" means a corporate proxy, so get its root from IT.
#    An issuer you can't explain means STOP and tell someone.
```

## 7. Checklist before you ever type `verify=False`

- [ ] I've read the exact error message and matched it in the table above.
- [ ] I've looked at the chain with `openssl s_client -showcerts`.
- [ ] If it's a private or proxy CA, I've added **that CA only**, in the narrowest scope.
- [ ] If it's the server's fault (missing intermediate, expired, wrong name), I've reported it to whoever owns the server.
- [ ] If I still think I need to disable verification, I've asked a senior first. (The answer will almost always be no.)
