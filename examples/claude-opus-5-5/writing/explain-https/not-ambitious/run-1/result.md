HTTPS is ordinary HTTP sent through an encrypted, authenticated channel called **TLS** (Transport Layer Security). TLS gives you three things:

1. **Confidentiality.** People watching the network can't read the traffic.
2. **Integrity.** Nobody can change the traffic in transit without it being detected.
3. **Authentication.** You know you're talking to the real `example.com` and not an impostor.

## Step by step (TLS 1.3, the current standard)

### 1. TCP connection
The browser opens a TCP connection to the server on port 443. With HTTP/3, QUIC over UDP is used instead, but the TLS part is the same.

### 2. ClientHello
The browser sends:
- the TLS versions and cipher suites it supports (e.g. `TLS_AES_128_GCM_SHA256`)
- a random value
- a **key share**, which is its half of a Diffie-Hellman key exchange (usually X25519, and increasingly a hybrid with the post-quantum ML-KEM)
- **SNI** (Server Name Indication), the hostname it wants, so one IP address can host many sites

### 3. ServerHello and the server's proof of identity
The server:
- picks a cipher suite and sends its own **key share**
- combines both key shares so that each side independently computes the **same shared secret**. Someone watching sees both public halves but can't work out the secret. That's the core idea of Diffie-Hellman.
- sends everything after this point encrypted, including:
  - its **certificate chain**
  - a **CertificateVerify** message: a signature over the handshake so far, made with the certificate's private key
  - a **Finished** message: a MAC over the whole handshake

### 4. The browser checks the certificate
This step stops impostors:
- **Chain of trust:** the site's certificate is signed by an intermediate CA, which is signed by a root CA. The browser or OS ships with a list of trusted roots.
- **Hostname:** the certificate's Subject Alternative Name must match the domain you asked for.
- **Validity:** the certificate must not be expired or revoked. Browsers also require **Certificate Transparency** logs.
- **Proof of possession:** the CertificateVerify signature shows the server actually holds the private key, not just a copy of the public certificate.

Without this check, an attacker in the middle could run Diffie-Hellman with you directly. Encryption alone doesn't help if you're encrypting to the wrong party.

### 5. The browser finishes
The browser sends its own Finished message. Both sides derive symmetric **session keys** from the shared secret using HKDF. The handshake takes **one round trip**, or zero when resuming a session (0-RTT).

### 6. Encrypted HTTP
Ordinary HTTP requests and responses now flow inside TLS records encrypted with a fast symmetric **AEAD** cipher such as AES-GCM or ChaCha20-Poly1305. AEAD encrypts the data and also authenticates it, so any tampering is detected.

## Why two kinds of cryptography?
- **Asymmetric** cryptography (key exchange, signatures) solves the problem of agreeing on a secret with a stranger and proving identity. It's slow, so it's used only during the handshake.
- **Symmetric** cryptography (AES or ChaCha) is fast, so it carries the bulk data.

## Forward secrecy
TLS 1.3 always uses fresh, ephemeral Diffie-Hellman keys for each connection. If the server's private key is stolen later, recorded traffic from the past still can't be decrypted, because that key was only ever used for signing, never for encryption.

## What HTTPS doesn't hide
- The **IP addresses** of both ends.
- The **domain name**, which is usually visible via SNI and DNS. Encrypted Client Hello (ECH) and DNS-over-HTTPS are closing this gap.
- **Traffic timing and size**.
- It also says nothing about whether the site itself is trustworthy. It only proves you're talking to whoever controls that domain.

## Diagram

```
Client                                         Server
  |--- ClientHello (key share, SNI) ------------>|
  |<-- ServerHello (key share) ------------------|
  |<-- {Certificate, CertificateVerify, Finished}|  ← encrypted
  |--- {Finished} ------------------------------>|
  |<========== encrypted HTTP traffic ==========>|
```

I can go further into any part: Diffie-Hellman math, how certificates and CAs work, TLS 1.2 vs 1.3, or HTTP/3 and QUIC.