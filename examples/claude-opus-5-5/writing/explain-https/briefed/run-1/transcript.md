# write/explain-https · briefed

### User

Explain how HTTPS works.

For a junior developer who keeps disabling certificate verification to "make it work".

### Assistant

# How HTTPS Works (and Why `verify=False` Is Worse Than It Looks)

## The short version

HTTPS does two jobs:

1. **Encryption.** Nobody between you and the server can read or change the traffic.
2. **Authentication.** You are actually talking to the server you meant to reach.

Certificate verification is the part that does job #2. **If you turn it off, job #1 stops protecting you too.** Encrypting your traffic doesn't help if the other end of the encrypted connection is an attacker.

---

## Step by step: what happens when you connect to `https://api.example.com`

### 1. TCP connection
Your client opens an ordinary network connection to the server's IP address. Nothing is secure yet.

### 2. TLS handshake: "Hello"
The client sends a **ClientHello**: the TLS versions and ciphers it supports, plus the hostname it wants (`api.example.com`, sent via SNI).

The server replies with a **ServerHello** that picks the settings, and sends its **certificate**.

### 3. The certificate: the server's ID card
A certificate is a signed document that says roughly:

> "The public key `abc123…` belongs to `api.example.com`. Valid until 2027-03-01.
> — Signed, Let's Encrypt (or DigiCert, or your company's internal CA)"

Anyone can *generate* a certificate claiming to be `api.example.com`. What makes one trustworthy is **who signed it**.

### 4. Verification: the step you've been disabling
Your client checks:

| Check | Question it answers |
|---|---|
| **Chain of trust** | Was this signed by a Certificate Authority I trust? (Your OS/runtime ships a list of trusted root CAs.) Usually it's a chain: root CA → intermediate CA → server cert. |
| **Hostname match** | Does the cert say `api.example.com`, the host I actually asked for? |
| **Validity dates** | Is it expired, or not valid yet? |
| **Proof of possession** | During the handshake, the server has to prove it holds the **private key** that matches the public key in the cert. A thief who copied the cert can't do this. |

If every check passes, you know you're talking to the real `api.example.com`.

### 5. Key exchange
Client and server use a key exchange (usually ECDHE) to agree on a shared secret **that is never sent over the wire**. Someone recording all the traffic still can't work it out.

### 6. Encrypted traffic
Both sides derive symmetric keys from that secret. All HTTP traffic (URLs, headers, cookies, bodies) is encrypted and tamper-proof from here on.

---

## What `verify=False` actually does

Here's the attack it opens up, called a **man-in-the-middle (MITM)**:

```
You  ──TLS──▶  Attacker  ──TLS──▶  Real server
     (attacker's            (attacker acts
      fake cert)             as the client)
```

1. You connect to `api.example.com`, but someone on the network (public Wi-Fi, compromised router, malicious proxy, DNS poisoning) intercepts it.
2. The attacker presents **their own self-made certificate** for `api.example.com`.
3. A client that verifies sees it isn't signed by a trusted CA and **refuses to connect**.
4. A client with `verify=False` **accepts it without complaint**.
5. You now have a fully encrypted connection *to the attacker*. They decrypt everything, read your API keys, passwords and tokens, can change responses, and pass everything on to the real server so nothing looks wrong.

**Key point:** with verification off, the connection still "works" perfectly. You get no error, and that's the danger. You can't tell whether you're being attacked.

---

## "But it's just internal / just dev / just temporary"

- **"It's internal."** Internal networks get compromised too. Attackers who get in move sideways by exactly this kind of interception.
- **"It's just dev."** Code written for dev ends up in production. `verify=False` added "temporarily" is one of the most common findings in security audits.
- **"It's temporary."** It almost never is. Nothing reminds you to remove it, because everything keeps working.

---

## What's actually wrong when verification fails, and the real fix

The error message is telling you something specific. Read it:

| Error (roughly) | Real cause | Proper fix |
|---|---|---|
| `self-signed certificate` / `unable to get local issuer certificate` | Server uses a cert from a CA your client doesn't know, often a **corporate/internal CA** | Give your client that CA's cert (see below) |
| `unable to get local issuer certificate` on a public site | Server isn't sending its **intermediate certificate** | Fix the server config to send the full chain |
| `hostname mismatch` | Cert is for `foo.com`, you connected to `bar.com` or a raw IP | Use the correct hostname, or reissue the cert with the right names (SAN) |
| `certificate has expired` | It expired | Renew it (set up automatic renewal, e.g. Let's Encrypt/cert-manager) |
| Fails on corporate laptop, works at home | A **corporate TLS-inspection proxy** swaps certs | Install your company's root CA into your tool's trust store |
| Old Docker image / old runtime fails | Outdated CA bundle | Update `ca-certificates` / the runtime |

### Trust a specific CA *instead of* trusting everything

**Python (requests):**
```python
# Bad
requests.get(url, verify=False)

# Good: trust your org's CA in addition to normal verification
requests.get(url, verify="/path/to/company-ca.pem")
# or set REQUESTS_CA_BUNDLE=/path/to/ca-bundle.pem
```

**Node.js:**
```bash
# Bad
NODE_TLS_REJECT_UNAUTHORIZED=0

# Good
NODE_EXTRA_CA_CERTS=/path/to/company-ca.pem node app.js
```

**curl:**
```bash
# Bad
curl -k https://internal.example.com

# Good
curl --cacert company-ca.pem https://internal.example.com
```

**Java:** import the CA into a truststore with `keytool -importcert` and point the JVM at it.

### For local development
Use **[mkcert](https://github.com/FiloSottile/mkcert)**. It creates a local CA, installs it into your system trust store, and issues certs for `localhost`. You get real HTTPS locally with verification on.

---

## Debugging tool you should know

```bash
openssl s_client -connect api.example.com:443 -servername api.example.com -showcerts
```

This shows the exact certificate chain the server sends, who issued each cert, and the precise verification error. Five minutes with this usually finds the real problem.

---

## TL;DR

- HTTPS = encryption **plus** proof of identity. Certificates provide the proof.
- Disabling verification keeps the encryption but throws away the proof, so an attacker can sit in the middle and you'll never notice.
- A cert error is a diagnosis, not an obstacle. Read it, find which check failed, and fix that: add the right CA, fix the chain, fix the hostname, or renew the cert.
- **Rule of thumb:** if you're about to type `verify=False`, `-k`, `InsecureSkipVerify: true`, or `rejectUnauthorized: false`, stop and point the client at the right CA instead.
