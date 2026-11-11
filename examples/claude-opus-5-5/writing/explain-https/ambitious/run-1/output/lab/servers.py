#!/usr/bin/env python3
"""Run one tiny HTTPS server per scenario. Python stdlib only.

Each server re-reads servers/<scenario>/cert.pem + key.pem on EVERY connection,
so when you fix a certificate you do not need to restart anything.
Ctrl-C to stop.
"""
import os, socket, ssl, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LAB = os.path.dirname(os.path.abspath(__file__))
SCENARIOS = {  # port: scenario  (order matches check.py and the guide)
    8443: "ok",
    8444: "missing-intermediate",
    8445: "self-signed",
    8446: "wrong-host",
    8447: "expired",
    8448: "corp-proxy",
    8449: "canary-evil",
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = f"hello from the '{self.server.scenario}' server\n".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):  # keep the terminal readable
        pass


class TLSServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port, scenario):
        self.scenario = scenario
        super().__init__(("127.0.0.1", port), Handler)

    def get_request(self):
        raw, addr = self.socket.accept()
        d = os.path.join(LAB, "servers", self.scenario)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(os.path.join(d, "cert.pem"), os.path.join(d, "key.pem"))
        return ctx.wrap_socket(raw, server_side=True, do_handshake_on_connect=False), addr

    def handle_error(self, request, client_address):
        pass  # failed handshakes are the whole point of this lab


def main():
    if not os.path.isdir(os.path.join(LAB, "servers")):
        sys.exit("Run ./setup.sh first.")
    for port, name in SCENARIOS.items():
        srv = TLSServer(port, name)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        print(f"  https://localhost:{port}   {name}")
    print("Servers running. Ctrl-C to stop.")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
