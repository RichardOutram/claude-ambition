# write/explain-https · not-ambitious

### User

Explain how HTTPS works.

### Assistant

HTTPS is ordinary HTTP sent through a **TLS** (Transport Layer Security) connection. TLS provides three things:

1. **Confidentiality.** Anyone watching the traffic, such as your ISP or someone on café Wi‑Fi, can't read it.
2. **Integrity.** Nobody can change the traffic in transit without being detected.
3. **Authentication.** You know you're talking to the real `example.com` and not an impostor.

## Step by step (TLS 1.3, the current version)

### 1. TCP connection
The browser opens a TCP connection to the server on port 443. With HTTP/3 it uses QUIC over UDP instead, but the TLS ideas are the same.

### 2. The handshake (one round trip)

**Client → Server: `ClientHello`**
- The TLS versions and cipher suites the browser supports (e.g. AES‑GCM, ChaCha20‑Poly1305)
- A random value
- A **key share**: the browser's half of an ephemeral Diffie–Hellman exchange, usually X25519. Newer browsers often add a post-quantum hybrid such as X25519+ML‑KEM.
- **SNI** (Server Name Indication): the hostname it wants, so one IP can host many sites

**Server → Client: `ServerHello` + encrypted extras**
- The cipher suite it picked and its own key share
- Both sides now combine the two key shares with **Diffie–Hellman** to get the same shared secret. That secret never crosses the network. Everything after this point is encrypted.
- The server's **certificate chain**
- `CertificateVerify`: a signature over the handshake made with the server's **private key**. This proves the server actually holds the key that matches the certificate.
- `Finished`: a MAC over the whole handshake, which proves nothing was tampered with

**Client → Server: `Finished`**
The browser checks everything (next section), sends its own `Finished`, and HTTP requests can start right away.

### 3. Certificate validation (the authentication part)
The certificate says "this public key belongs to `example.com`" and is signed by a **Certificate Authority (CA)**. The browser checks that:
- the chain leads up to a **root CA** that the OS or browser already trusts
- the hostname matches the certificate's Subject Alternative Name
- the certificate is within its validity dates and hasn't been revoked
- it appears in public **Certificate Transparency** logs (Chrome and Safari require this)

Diffie–Hellman on its own would give you an encrypted channel, but you wouldn't know who is on the other end. The certificate plus the `CertificateVerify` signature is what stops a man-in-the-middle.

### 4. Encrypted data transfer
HTTP requests and responses travel inside TLS "records". These are encrypted with **symmetric AEAD ciphers** (like AES‑GCM) using keys derived from the shared secret. Symmetric crypto is fast; the slower public-key crypto is only used during the handshake.

## Key design points

- **Forward secrecy.** The session keys come from *ephemeral* Diffie–Hellman keys that are thrown away afterward. If the server's long-term private key is stolen later, recorded past traffic still can't be decrypted. (TLS 1.2 with RSA key exchange didn't have this, and TLS 1.3 removed that option.)
- **Session resumption / 0‑RTT.** A returning client can reuse a pre-shared key from an earlier session. This can even send data in the first packet, though 0‑RTT data can be replayed, so it should only be used for safe, idempotent requests.
- **HSTS.** A response header (`Strict-Transport-Security`) that tells browsers to always use HTTPS for that site. This blocks attacks that downgrade the connection to plain HTTP.

## What HTTPS does *not* hide
- **The IP address** you connect to, and roughly how much data and when
- **The hostname**, which is in SNI in plain text unless **Encrypted Client Hello (ECH)** is in use
- **DNS lookups**, unless you use DNS‑over‑HTTPS or DNS‑over‑TLS

The URL path, query string, headers, cookies and body are all encrypted.

## One-line summary
The two sides use Diffie–Hellman to agree on a secret key, the server proves its identity with a CA-signed certificate and a signature, and then all HTTP traffic is encrypted with fast symmetric ciphers using that key.
