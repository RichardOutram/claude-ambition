#!/usr/bin/env bash
# Shows the moving parts of HTTPS locally, with no network access:
#   1. certificate chain + hostname verification
#   2. ECDHE key agreement (both sides reach the same secret)
#   3. a real TLS 1.3 handshake over loopback
set -u
D="${TMPDIR:-/tmp}/https-demo"; rm -rf "$D"; mkdir -p "$D"; cd "$D"
printf 'subjectAltName=DNS:demo.test\n' > ext.cnf

openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes \
  -keyout ca.key -out ca.crt -days 1 -subj "/CN=Demo Root CA" 2>/dev/null
openssl req -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes \
  -keyout srv.key -out srv.csr -subj "/CN=demo.test" 2>/dev/null
openssl x509 -req -in srv.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out srv.crt -days 1 -extfile ext.cnf 2>/dev/null

echo "== 1a. chain verify, CA trusted:";   openssl verify -CAfile ca.crt srv.crt
echo "== 1b. chain verify, CA not trusted:"; openssl verify srv.crt 2>&1 | grep -i error | head -1
echo "== 1c. hostname demo.test:"; openssl verify -CAfile ca.crt -verify_hostname demo.test srv.crt
echo "== 1d. hostname evil.test:"; openssl verify -CAfile ca.crt -verify_hostname evil.test srv.crt 2>&1 | grep -i error | head -1

openssl genpkey -algorithm X25519 -out a.key; openssl pkey -in a.key -pubout -out a.pub
openssl genpkey -algorithm X25519 -out b.key; openssl pkey -in b.key -pubout -out b.pub
echo "== 2. X25519 shared secret (client view, then server view):"
openssl pkeyutl -derive -inkey a.key -peerkey b.pub | xxd -p -c64
openssl pkeyutl -derive -inkey b.key -peerkey a.pub | xxd -p -c64

openssl s_server -accept 127.0.0.1:48443 -cert srv.crt -key srv.key -www -quiet >/dev/null 2>&1 &
S=$!; sleep 1
echo "== 3. TLS handshake messages (>>> sent by client, <<< received):"
echo | openssl s_client -connect 127.0.0.1:48443 -servername demo.test \
  -verify_hostname demo.test -CAfile ca.crt -msg 2>&1 \
  | grep -E "^(>>>|<<<)|^Protocol|^Cipher|Verify return code|Verification|Peer signature|Negotiated TLS1.3 group" \
  | sed -E 's/, length = [0-9]+//' | head -40
kill $S 2>/dev/null
