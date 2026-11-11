#!/usr/bin/env python3
"""What `verify=False` actually does, in 20 seconds. Self-contained; run ./setup.sh first.  (tls-insecure-ok: demo)

Cast:
  bank API   https://localhost:9442  real server, real (lab-CA-issued) certificate
  attacker   port 9443               sits on the network path (rogue Wi-Fi, poisoned DNS,
                                     compromised router, malicious container sidecar...).
                                     Presents its OWN certificate for "localhost", then
                                     forwards to the real bank so nothing looks wrong.

We make the SAME request twice through the attacker's path:
  1. with certificate verification OFF   (what verify=False / rejectUnauthorized:false does)  tls-insecure-ok: docs
  2. with certificate verification ON    (the default you keep turning off)
"""
import http.client, json, os, socket, ssl, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LAB = os.path.dirname(os.path.abspath(__file__))
BANK_PORT, MITM_PORT = 9442, 9443
TOKEN = "Bearer FAKE-prod-api-key-imagine-this-is-real-0000"
stolen = []


def serve(port, handler, cert_dir):
    class S(ThreadingHTTPServer):
        daemon_threads = True
        def handle_error(self, *a): pass
    srv = S(("127.0.0.1", port), handler)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(os.path.join(cert_dir, "cert.pem"), os.path.join(cert_dir, "key.pem"))
    srv.socket = ctx.wrap_socket(srv.socket, server_side=True, do_handshake_on_connect=False)
    threading.Thread(target=srv.serve_forever, daemon=True).start()


class Bank(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        body = json.dumps({"status": "ok", "payout_to": "GB29 NWBK 6016 1331 9268 19 (Acme Ltd)"}).encode()
        self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a): pass


class Attacker(BaseHTTPRequestHandler):
    def do_POST(self):
        req_body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        stolen.append((self.headers.get("Authorization"), req_body.decode()))      # 1. read everything
        up = http.client.HTTPSConnection("localhost", BANK_PORT,                     # 2. forward to the real bank
             context=ssl.create_default_context(cafile=os.path.join(LAB, "trust", "ca-bundle.pem")))
        up.request("POST", self.path, req_body, {"Authorization": self.headers.get("Authorization"),
                                                  "Content-Type": "application/json"})
        data = json.loads(up.getresponse().read())
        data["payout_to"] = "LT12 1000 0111 0100 1000 (attacker)"                    # 3. quietly change the answer
        body = json.dumps(data).encode()
        self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a): pass


def client(verify):
    if verify:
        ctx = ssl.create_default_context(cafile=os.path.join(LAB, "trust", "ca-bundle.pem"))
    else:  # this is exactly what verify=False, rejectUnauthorized:false, curl -k, InsecureSkipVerify do  tls-insecure-ok: docs
        ctx = ssl.create_default_context()
        ctx.check_hostname = False          # tls-insecure-ok: the demo shows what this costs
        ctx.verify_mode = ssl.CERT_NONE     # tls-insecure-ok: the demo shows what this costs
    # The app thinks it is talking to https://localhost (the bank). The network delivers it to the attacker.
    conn = http.client.HTTPSConnection("localhost", MITM_PORT, context=ctx, timeout=5)
    conn.request("POST", "/v1/payouts", json.dumps({"amount_eur": 48000, "invoice": "INV-2291"}),
                 {"Authorization": TOKEN, "Content-Type": "application/json"})
    return json.loads(conn.getresponse().read())


def main():
    if not os.path.exists(os.path.join(LAB, "pki", "evil-ca")):
        raise SystemExit("Run ./setup.sh first.")
    serve(BANK_PORT, Bank, os.path.join(LAB, "servers", "ok"))
    serve(MITM_PORT, Attacker, os.path.join(LAB, "servers", "canary-evil"))

    print("=== Run 1: verification OFF ===")
    resp = client(verify=False)  # tls-insecure-ok: demo
    print(f"  app sees:      HTTP 200, encrypted, no errors. Response: {resp}")
    auth, body = stolen[-1]
    print(f"  attacker log:  Authorization: {auth}")
    print(f"                 body: {body}")
    print("  The connection WAS encrypted, to the attacker. Your API key is gone and you would")
    print("  now pay EUR 48,000 to the attacker's account. Nothing in your logs looks wrong.\n")

    print("=== Run 2: verification ON (the default) ===")
    before = len(stolen)
    try:
        client(verify=True)
        print("  ...connected?! (this should not happen)")
    except ssl.SSLCertVerificationError as e:
        print(f"  app sees:      ssl.SSLCertVerificationError: {e.verify_message}")
    print(f"  attacker log:  {'nothing. The request was never sent.' if len(stolen) == before else 'CAPTURED (!)'}")
    print("  The error is annoying. It is also the only thing that stood between the attacker and your key.")
    print("  Note the message: the same 'unable to get local issuer certificate' you get from a")
    print("  missing intermediate or a corporate proxy. That's why you can't tell them apart without checking.")


if __name__ == "__main__":
    main()
