# How HTTPS works, and why `verify=False` breaks it

## Two separate jobs

HTTPS (HTTP over TLS) does two things, and both are needed:

1. **Encryption**: nobody on the network can read or change the traffic.
2. **Authentication**: you are talking to the real `api.bank.com` and not someone pretending to be it.

When you disable certificate verification, you keep #1 and throw away #2. Without #2, #1 doesn't protect you, because you could have a perfectly encrypted connection to the attacker.

## The handshake, simplified

When your code connects to `https://api.example.com`:

1. **Client hello.** Your client says which TLS versions and ciphers it supports.
2. **Server hello and certificate.** The server picks the settings and sends its **certificate**. The certificate says, roughly: *"This public key belongs to `api.example.com`. Signed, Let's Encrypt (or DigiCert, etc.)."*
3. **Certificate verification.** This is the step you've been turning off. Your client checks:
   - **Is the signature valid and chained to a CA I trust?** Your OS or runtime ships with a list of trusted root Certificate Authorities. The server's cert is signed by an intermediate, which is signed by a root in that list.
   - **Does the name match?** The cert must cover `api.example.com` (in its Subject Alternative Names). A valid cert for `evil.com` doesn't count.
   - **Is it in date?** It must not be expired or not yet valid.
4. **Key exchange.** Client and server use ephemeral Diffie-Hellman to agree on a shared secret. The server signs its part with the private key that matches the certificate. Only the real owner of `api.example.com` has that private key, so this proves who you're talking to.
5. **Encrypted traffic.** Everything after this uses fast symmetric encryption (e.g. AES-GCM or ChaCha20) with keys derived from that shared secret.

The point to remember: **the key exchange only proves you share a secret with whoever holds the key in the certificate.** Step 3 is what makes sure that's the right party.

## What happens when you skip verification

Say you're on coffee-shop Wi-Fi, a compromised corporate network, or a cloud VPC with a misbehaving sidecar. An attacker sits between you and the server:

```
You  ⇄  Attacker  ⇄  api.example.com
```

- You connect. The attacker answers with **their own self-signed certificate**.
- With verification on, your client sees that nobody trusted signed the cert and refuses to connect. The attack fails.
- With verification off, your client says "looks fine" and does a full encrypted handshake **with the attacker**. The attacker opens a second connection to the real server and relays traffic, reading and changing whatever it wants: API keys, passwords, tokens, payment data, the responses you trust.

You still get a padlock and an encrypted connection. It's just encrypted to the wrong party. This is a man-in-the-middle (MITM) attack, and certificate verification is the defence against it.

Disabling verification also fails silently. Nothing tells you it's being exploited, and it tends to get copied from a dev script into production.

## "But it doesn't work otherwise." Fix the real cause

A certificate error is real information. Here are the common causes and the proper fixes:

| Error / situation | Actual cause | Proper fix |
|---|---|---|
| `self-signed certificate` in local dev | Your dev server uses a cert nothing trusts | Use [`mkcert`](https://github.com/FiloSottile/mkcert) to create a local CA and install it in your trust store, or use plain `http://localhost` for local-only dev |
| `unable to get local issuer certificate` behind a corporate network | Corporate proxy re-signs TLS with its own CA | Get the corporate root CA from IT and add it to your trust store (see below) |
| `unable to get local issuer certificate` on a server you control | Server isn't sending the intermediate cert | Fix the server to send the **full chain** (`fullchain.pem`, not `cert.pem`) |
| `hostname mismatch` | Connecting by IP or wrong name; cert doesn't cover it | Use the hostname the cert was issued for, or reissue the cert with the right SANs |
| `certificate has expired` | It expired | Renew it, and automate renewal (certbot, cert-manager) |
| Internal service with a private CA | Your org runs its own CA | Trust **that specific CA** in your client, not "everything" |
| Old Docker image / slim container | No CA bundle installed | `apt-get install ca-certificates` (or the equivalent) |

## Trusting a specific CA instead of turning verification off

The right move is almost always "trust this one extra CA", not "trust everyone".

**Python (requests)**
```python
# ❌ requests.get(url, verify=False)
requests.get(url, verify="/path/to/corp-root-ca.pem")
# or: export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.pem
```

**Node.js**
```bash
# ❌ NODE_TLS_REJECT_UNAUTHORIZED=0
NODE_EXTRA_CA_CERTS=/path/to/corp-root-ca.pem node app.js
```

**curl**
```bash
# ❌ curl -k https://...
curl --cacert /path/to/ca.pem https://internal.example.com
```

**Go**
```go
// ❌ InsecureSkipVerify: true
pool, _ := x509.SystemCertPool()
pool.AppendCertsFromPEM(caPEM)
tlsCfg := &tls.Config{RootCAs: pool}
```

**Java**: import the CA into a truststore with `keytool -importcert` and point the JVM at it. Don't install a `TrustManager` that accepts everything.

## How to debug a certificate error

Look at what the server is actually sending:

```bash
openssl s_client -connect api.example.com:443 -servername api.example.com -showcerts
```

Check:
- the `subject` / SAN: does it match the hostname?
- the `issuer`: who signed it? Is that your corporate proxy?
- `notBefore` / `notAfter`: is it in date?
- `Verify return code`: `0 (ok)` is good. Anything else tells you exactly what's wrong.

## The short version

- Encryption without verification is like whispering a secret to a stranger in a dark room. Nobody else hears it, but you don't know who you told.
- A certificate error means the client caught something wrong. Find out what it is.
- Fix it by trusting the **specific** CA you need or by fixing the server's cert, never with `verify=False`, `-k`, `InsecureSkipVerify`, or `NODE_TLS_REJECT_UNAUTHORIZED=0`.
- If you really must bypass it for a quick throwaway local test, keep it out of committed code. Linters and code review should flag it.