#!/usr/bin/env python3
"""Connect to every lab server the way real clients do, WITH verification on,
using three different stacks (Python, curl, Node) and the same trust store:
trust/ca-bundle.pem.

You are done when every scenario says FIXED and the canary still says BLOCKED.

The canary is a server whose certificate comes from an attacker's CA. If it
ever connects, your "fix" was really "turn off checking" (or trusting a CA you
should not), and the checker fails loudly.

Usage: python3 check.py            # summary
       python3 check.py -v         # also print each stack's exact error message
"""
import os, shutil, socket, ssl, subprocess, sys, http.client

LAB = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.join(LAB, "trust", "ca-bundle.pem")
HOST = "localhost"
SCENARIOS = [
    (8443, "ok", "control: correctly configured server"),
    (8444, "missing-intermediate", "1. server forgets to send the intermediate"),
    (8445, "self-signed", "2. self-signed certificate"),
    (8446, "wrong-host", "3. certificate is for a different hostname"),
    (8447, "expired", "4. certificate has expired"),
    (8448, "corp-proxy", "5. corporate TLS-inspection proxy"),
    (8449, "canary-evil", "canary: attacker's certificate, must stay BLOCKED"),
]

NODE_CLIENT = r"""
const https = require('https'), fs = require('fs');
const [port, ca, host] = process.argv.slice(1);
https.get({host, port: +port, family: 4, path: '/', ca: fs.readFileSync(ca), timeout: 5000}, r => {
  r.resume(); r.on('end', () => console.log('OK ' + r.statusCode));
}).on('error', e => { console.log((e.code ? e.code + ': ' : '') + e.message); process.exit(1); });
"""


def py_client(port):
    ctx = ssl.create_default_context(cafile=BUNDLE)  # verification + hostname check ON (the default)
    try:
        c = http.client.HTTPSConnection(HOST, port, context=ctx, timeout=5)
        c.request("GET", "/")
        return True, f"OK {c.getresponse().status}"
    except ssl.SSLCertVerificationError as e:
        return False, e.verify_message if hasattr(e, "verify_message") else str(e)
    except (ssl.SSLError, OSError) as e:
        return False, str(e)


def curl_client(port):
    p = subprocess.run(["curl", "-sS", "--max-time", "5", "--cacert", BUNDLE, f"https://{HOST}:{port}/"],
                       capture_output=True, text=True)
    return p.returncode == 0, ("OK" if p.returncode == 0 else p.stderr.strip().splitlines()[0].replace("curl: ", ""))


def node_client(port):
    p = subprocess.run(["node", "-e", NODE_CLIENT, str(port), BUNDLE, HOST], capture_output=True, text=True)
    return p.returncode == 0, p.stdout.strip() or p.stderr.strip()


def issued_by_corp_ca():
    """Scenario 5 models a proxy you don't control: its cert must still come from the corporate CA."""
    p = subprocess.run(["openssl", "x509", "-noout", "-issuer", "-in",
                        os.path.join(LAB, "servers", "corp-proxy", "cert.pem")], capture_output=True, text=True)
    return "Corp TLS Inspection CA" in p.stdout


def main():
    verbose = "-v" in sys.argv
    if not os.path.exists(BUNDLE):
        sys.exit("Run ./setup.sh first.")
    try:
        socket.create_connection(("127.0.0.1", 8443), timeout=2).close()
    except OSError:
        sys.exit("Servers are not running. Start them in another terminal:  python3 servers.py")

    clients = [("python", py_client)]
    clients += [("curl", curl_client)] if shutil.which("curl") else []
    clients += [("node", node_client)] if shutil.which("node") else []
    print(f"Trust store: trust/ca-bundle.pem    Clients: {', '.join(n for n, _ in clients)}    Verification: ON\n")

    fixed = total = 0
    canary_breached = False
    for port, name, desc in SCENARIOS:
        results = [(n, *fn(port)) for n, fn in clients]
        all_ok = all(ok for _, ok, _ in results)
        any_ok = any(ok for _, ok, _ in results)
        if name == "canary-evil":
            canary_breached = any_ok
            status = "BREACHED" if any_ok else "BLOCKED"
        elif name == "ok":
            status = "OK" if all_ok else "BROKEN?"
        elif name == "corp-proxy" and all_ok and not issued_by_corp_ca():
            total += 1
            status = "WRONG FIX"
            print(f"  [{status:^8}] {port}  {desc}")
            print("               The proxy belongs to IT; you can't re-issue its certificates. Put the server's")
            print("               original cert back (./setup.sh resets everything) and fix the CLIENT side.")
            continue
        else:
            total += 1
            fixed += all_ok
            status = "FIXED" if all_ok else ("PARTIAL" if any_ok else "FAILING")
        print(f"  [{status:^8}] {port}  {desc}")
        if verbose or (status not in ("OK", "FIXED", "BLOCKED")):
            for n, ok, msg in results:
                print(f"               {n:<6} {'ok' if ok else 'x '}  {msg[:220]}")
    print()
    if canary_breached:
        print("!! CANARY BREACHED: a client accepted the attacker's certificate.")
        print("!! Something disabled verification, or the attacker's CA got into trust/ca-bundle.pem.")
        print("!! Every 'fix' above is void until this says BLOCKED again.")
        sys.exit(2)
    print(f"{fixed}/{total} scenarios fixed, canary blocked."
          + ("  All done: you fixed TLS without turning it off." if fixed == total else ""))
    sys.exit(0 if fixed == total else 1)


if __name__ == "__main__":
    main()
