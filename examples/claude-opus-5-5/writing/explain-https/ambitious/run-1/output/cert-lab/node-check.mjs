// Checks the Node.js rows of GUIDE.md with in-memory TLS (no network).
// Usage: node node-check.mjs <dir-with-certs-from-cert-lab>
import tls from "node:tls";
import fs from "node:fs";
import { duplexPair } from "node:stream";

const dir = process.argv[2];
const rd = (f) => fs.readFileSync(`${dir}/${f}`);
const HOST = "api.internal.test";

function attempt(label, certs, keyFile, clientOpts) {
  return new Promise((resolve) => {
    const [a, b] = duplexPair();
    const srv = new tls.TLSSocket(b, { isServer: true, cert: certs.map(rd).join(""), key: rd(keyFile) });
    srv.on("error", () => {});
    const cli = tls.connect({ socket: a, servername: HOST, ...clientOpts });
    const done = (msg) => { console.log(`  ${label.padEnd(52)} -> ${msg}`); cli.destroy(); srv.destroy(); resolve(); };
    cli.on("secureConnect", () => done(cli.authorized ? "connected, authorized" : `connected, NOT authorized (${cli.authorizationError})`));
    cli.on("error", (e) => done(`${e.code}`));
  });
}

const root = rd("root.crt");
await attempt("missing intermediate", ["good.crt"], "good.key", { ca: root });
await attempt("hostname mismatch", ["wrongname.crt", "inter.crt"], "wrongname.key", { ca: root });
await attempt("self-signed leaf", ["selfsigned.crt"], "selfsigned.key", { ca: root });
await attempt("attacker chain", ["attacker.crt", "evil.crt"], "attacker.key", { ca: root });
await attempt("expired", ["expired.crt", "inter.crt"], "expired.key", { ca: root });
await attempt("corp CA via {ca: [root, corp]}", ["corpleaf.crt"], "corpleaf.key", { ca: [root, rd("corp.crt")] });
await attempt("attacker with rejectUnauthorized:false", ["attacker.crt", "evil.crt"], "attacker.key", { ca: root, rejectUnauthorized: false });
// NODE_EXTRA_CA_CERTS: no `ca` option, so system roots + extra file are used
await attempt("corp CA, no ca option (env decides)", ["corpleaf.crt"], "corpleaf.key", {});
