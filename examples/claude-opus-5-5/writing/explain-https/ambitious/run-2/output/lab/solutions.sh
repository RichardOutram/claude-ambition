#!/usr/bin/env bash
# Reference fixes. Try every scenario yourself first, then compare.
# None of them turns verification off; check.py's canary would catch it if one did.
set -euo pipefail
cd "$(dirname "$0")"
GOOD="DNS:localhost,IP:127.0.0.1"

echo "1. missing-intermediate: SERVER fix. Serve leaf + intermediate (\"fullchain\"), never just the leaf."
cat servers/missing-intermediate/cert.pem pki/public-intermediate/ca.pem > servers/missing-intermediate/cert.new
mv servers/missing-intermediate/cert.new servers/missing-intermediate/cert.pem

echo "2. self-signed: get a cert from a CA clients already trust (ACME / internal CA / mkcert for local dev)."
tools/issue-cert.sh servers/self-signed "$GOOD" >/dev/null

echo "3. wrong-host: re-issue with every name clients actually use in the SAN."
tools/issue-cert.sh servers/wrong-host "DNS:staging.lab.test,$GOOD" >/dev/null

echo "4. expired: renew (and automate renewal so it never happens again)."
tools/issue-cert.sh servers/expired "$GOOD" >/dev/null

echo "5. corp-proxy: CLIENT fix. Trust the ONE extra CA your IT team vouches for. Check its fingerprint first:"
openssl x509 -in pki/corp-proxy-ca/ca.pem -noout -subject -fingerprint -sha256 | sed 's/^/     /'
grep -q "$(sed -n 2p pki/corp-proxy-ca/ca.pem)" trust/ca-bundle.pem || cat pki/corp-proxy-ca/ca.pem >> trust/ca-bundle.pem

echo; python3 check.py
