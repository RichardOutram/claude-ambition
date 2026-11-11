#!/usr/bin/env python3
"""
Certificate-error lab: reproduce the common TLS certificate errors, then show
the proper fix for each, and show what an attacker sees when verification is off.

No network or open ports needed: client and server do a real TLS handshake
in memory (ssl.MemoryBIO). Needs only python3 (stdlib) and the openssl CLI.

    python3 cert-lab.py
"""
import os, ssl, subprocess, sys, tempfile

HOST = "api.internal.test"
SECRET_REQUEST = b"GET /accounts HTTP/1.1\r\nHost: api.internal.test\r\nAuthorization: Bearer sk_live_DO_NOT_LEAK\r\n\r\n"

W = tempfile.mkdtemp(prefix="cert-lab-")
def p(name): return os.path.join(W, name)

def sh(*args):
    subprocess.run(args, check=True, cwd=W, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def key(name):
    sh("openssl", "genpkey", "-algorithm", "EC", "-pkeyopt", "ec_paramgen_curve:P-256", "-out", p(name + ".key"))

def self_signed_ca(name, cn):
    key(name)
    open(p(name + ".ext"), "w").write("basicConstraints=critical,CA:TRUE\nkeyUsage=critical,keyCertSign,cRLSign\n")
    sh("openssl", "req", "-x509", "-new", "-key", p(name + ".key"), "-out", p(name + ".crt"),
       "-days", "30", "-subj", "/CN=" + cn, "-addext", "basicConstraints=critical,CA:TRUE",
       "-addext", "keyUsage=critical,keyCertSign,cRLSign")

def issue(name, cn, issuer, *, ca=False, san=None, validity=("-days", "30")):
    key(name)
    sh("openssl", "req", "-new", "-key", p(name + ".key"), "-out", p(name + ".csr"), "-subj", "/CN=" + cn)
    ext = "basicConstraints=critical,CA:TRUE\nkeyUsage=critical,keyCertSign,cRLSign\n" if ca else \
          "basicConstraints=CA:FALSE\nextendedKeyUsage=serverAuth\nsubjectAltName=DNS:%s\n" % (san or cn)
    open(p(name + ".ext"), "w").write(ext)
    sh("openssl", "x509", "-req", "-in", p(name + ".csr"), "-CA", p(issuer + ".crt"), "-CAkey", p(issuer + ".key"),
       "-CAcreateserial", "-out", p(name + ".crt"), "-extfile", p(name + ".ext"), *validity)

def cat(out, *names):
    with open(p(out), "w") as f:
        for n in names: f.write(open(p(n)).read())
    return p(out)

def build_pki():
    # The legitimate public-style PKI: Root -> Intermediate -> leaf
    self_signed_ca("root", "Example Trusted Root CA")
    issue("inter", "Example Intermediate CA", "root", ca=True)
    issue("good", HOST, "inter")
    issue("wrongname", "www.other-site.test", "inter")
    issue("expired", HOST, "inter", validity=("-not_before", "20240101000000Z", "-not_after", "20240401000000Z"))
    issue("future", HOST, "inter", validity=("-not_before", "20300101000000Z", "-not_after", "20310101000000Z"))
    # A company's private CA (not in the default trust store)
    self_signed_ca("corp", "Acme Corp Internal Root CA")
    issue("corpleaf", HOST, "corp")
    # A bare self-signed dev cert
    key("selfsigned")
    sh("openssl", "req", "-x509", "-new", "-key", p("selfsigned.key"), "-out", p("selfsigned.crt"), "-days", "30",
       "-subj", "/CN=" + HOST, "-addext", "subjectAltName=DNS:" + HOST)
    # The attacker: their own CA, issuing a cert with the *right* hostname
    self_signed_ca("evil", "Totally Legit CA")
    issue("attacker", HOST, "evil")

def handshake(server_chain, server_key, client_ctx, server_hostname=HOST):
    """Real TLS handshake + one request, all in memory. Returns (ok, detail, what_server_received)."""
    sctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    sctx.load_cert_chain(server_chain, server_key)
    c_in, c_out, s_in, s_out = ssl.MemoryBIO(), ssl.MemoryBIO(), ssl.MemoryBIO(), ssl.MemoryBIO()
    cli = client_ctx.wrap_bio(c_in, c_out, server_side=False, server_hostname=server_hostname)
    srv = sctx.wrap_bio(s_in, s_out, server_side=True)

    def pump():
        moved = False
        for src, dst in ((c_out, s_in), (s_out, c_in)):
            data = src.read()
            if data: dst.write(data); moved = True
        return moved

    done = {"c": False, "s": False}
    for _ in range(50):
        for name, obj in (("c", cli), ("s", srv)):
            if done[name]: continue
            try:
                obj.do_handshake(); done[name] = True
            except (ssl.SSLWantReadError, ssl.SSLWantWriteError):
                pass
            except ssl.SSLCertVerificationError as e:
                return False, e.verify_message, None
            except ssl.SSLError as e:
                if name == "c": return False, e.reason or str(e), None
                pump(); continue  # server sees the client's alert; report the client's view
        if not pump() and all(done.values()): break
    if not all(done.values()):
        return False, "handshake did not complete", None
    cli.write(SECRET_REQUEST); pump()
    return True, "connected (%s)" % cli.version(), srv.read(4096)

# ---- client configurations -------------------------------------------------
def client_default_trust():
    """Stands in for the OS/browser trust store, which contains the public root."""
    ctx = ssl.create_default_context(cafile=p("root.crt"))
    return ctx

def client_with_extra_ca(extra):
    """Proper fix for a private CA: trust the public roots AND that one specific CA."""
    ctx = ssl.create_default_context(cafile=p("root.crt"))
    ctx.load_verify_locations(cafile=p(extra))
    return ctx

def client_verification_off():
    """What `verify=False`, `-k`, `rejectUnauthorized: false`, `InsecureSkipVerify` do."""
    ctx = ssl.create_default_context(cafile=p("root.crt"))
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

# ---- run ---------------------------------------------------------------------
PASS, FAIL = 0, 0
def check(label, result, expect_ok, expect_text=None):
    global PASS, FAIL
    ok, detail, received = result
    good = (ok == expect_ok) and (expect_text is None or expect_text.lower() in (detail or "").lower())
    PASS += good; FAIL += (not good)
    print("  [%s] %-58s -> %s" % ("ok" if good else "UNEXPECTED", label, detail))
    return received

def main():
    build_pki()
    full = cat("good-fullchain.pem", "good.crt", "inter.crt")
    print("Workdir:", W, "\n")

    print("0. Healthy server (leaf + intermediate), normal client")
    check("verification ON", handshake(full, p("good.key"), client_default_trust()), True)

    print("\n1. Server forgot to send the intermediate certificate")
    check("BROKEN: server sends leaf only", handshake(p("good.crt"), p("good.key"), client_default_trust()),
          False, "unable to get local issuer certificate")
    check("FIX: server sends fullchain.pem (leaf + intermediate)", handshake(full, p("good.key"), client_default_trust()), True)

    print("\n2. Certificate has expired")
    check("BROKEN: expired leaf", handshake(cat("exp.pem", "expired.crt", "inter.crt"), p("expired.key"), client_default_trust()),
          False, "expired")
    check("FIX: renew the cert (automate it)", handshake(full, p("good.key"), client_default_trust()), True)

    print("\n3. Clock is wrong / cert not valid yet")
    check("BROKEN: notBefore in the future", handshake(cat("fut.pem", "future.crt", "inter.crt"), p("future.key"), client_default_trust()),
          False, "not yet valid")

    print("\n4. Hostname mismatch")
    check("BROKEN: cert is for www.other-site.test", handshake(cat("wn.pem", "wrongname.crt", "inter.crt"), p("wrongname.key"), client_default_trust()),
          False, "hostname mismatch")
    check("BROKEN: connecting by IP / wrong name to a good cert", handshake(full, p("good.key"), client_default_trust(), server_hostname="10.0.0.5"),
          False, "mismatch")
    check("FIX: connect using the name the cert was issued for", handshake(full, p("good.key"), client_default_trust()), True)

    print("\n5. Server uses a company-internal CA")
    check("BROKEN: client doesn't know Acme's root", handshake(p("corpleaf.crt"), p("corpleaf.key"), client_default_trust()),
          False, "unable to get local issuer certificate")
    check("FIX: add *that one* CA to the client's trust", handshake(p("corpleaf.crt"), p("corpleaf.key"), client_with_extra_ca("corp.crt")), True)

    print("\n6. Self-signed dev certificate")
    check("BROKEN: self-signed", handshake(p("selfsigned.crt"), p("selfsigned.key"), client_default_trust()),
          False, "self signed")
    check("FIX (dev only): trust exactly that cert", handshake(p("selfsigned.crt"), p("selfsigned.key"), client_with_extra_ca("selfsigned.crt")), True)

    print("\n7. Why 'verify=False' is not a fix: an attacker in the middle (cafe wifi, rogue proxy, DNS hijack)")
    print("   The attacker makes their own CA and a cert for %s. It costs them one openssl command." % HOST)
    check("verification ON  vs attacker", handshake(cat("atk.pem", "attacker.crt", "evil.crt"), p("attacker.key"), client_default_trust()),
          False, "self signed certificate in certificate chain")
    stolen = check("verification OFF vs attacker", handshake(cat("atk.pem", "attacker.crt", "evil.crt"), p("attacker.key"), client_verification_off()),
                   True)
    print("\n   What the attacker's server received, decrypted:")
    for line in (stolen or b"").decode().strip().splitlines(): print("     |", line)
    print("\n   The connection was 'encrypted', but to the attacker. With verification on, the attack fails;")
    print("   with it off, the same client hands over its credentials without any error.")

    print("\nResult: %d checks behaved as expected, %d unexpected" % (PASS, FAIL))
    sys.exit(1 if FAIL else 0)

if __name__ == "__main__":
    main()
