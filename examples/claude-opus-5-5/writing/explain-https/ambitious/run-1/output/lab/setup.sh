#!/usr/bin/env bash
# Builds a miniature internet PKI on your laptop, then breaks it on purpose.
#
#   pki/public-root          "Public" root CA  -> in your trust store (trust/ca-bundle.pem)
#   pki/public-intermediate  signed by root    -> signs normal server certs
#   pki/corp-proxy-ca        your company's TLS-inspection CA -> NOT in your trust store yet
#   pki/evil-ca              an attacker's CA  -> must NEVER be trusted
#
#   servers/<scenario>/cert.pem + key.pem   what each local server presents
#
# Safe to re-run: it wipes and regenerates everything (undoing your fixes).
set -euo pipefail
LAB="$(cd "$(dirname "$0")" && pwd)"; cd "$LAB"
export SAN=DNS:unused CA_DIR=.   # openssl.cnf references these; real values are set per command
rm -rf pki servers trust
mkdir -p pki servers trust

new_ca() { # dir CN
  mkdir -p "$1/issued"; : > "$1/index.txt"; echo 1000 > "$1/serial"
}

# Root CA (self-signed). Its certificate is what gets shipped in trust stores.
new_ca pki/public-root
openssl req -x509 -new -newkey rsa:2048 -nodes -days 3650 -config openssl.cnf -extensions v3_root \
  -subj "/CN=Lab Public Root CA" -keyout pki/public-root/ca.key -out pki/public-root/ca.pem 2>/dev/null

# Intermediate CA: signed by the root. Real CAs keep roots offline and sign with intermediates.
new_ca pki/public-intermediate
openssl req -new -newkey rsa:2048 -nodes -config openssl.cnf -subj "/CN=Lab Public Intermediate CA" \
  -keyout pki/public-intermediate/ca.key -out pki/public-intermediate/ca.csr 2>/dev/null
CA_DIR=pki/public-root SAN=DNS:unused openssl ca -batch -config openssl.cnf -extensions v3_intermediate \
  -days 1825 -notext -in pki/public-intermediate/ca.csr -out pki/public-intermediate/ca.pem 2>/dev/null

# Two more self-signed CAs that are NOT in the client's trust store.
for spec in "corp-proxy-ca:Corp TLS Inspection CA" "evil-ca:Totally Legit Security CA"; do
  d="pki/${spec%%:*}"; new_ca "$d"
  openssl req -x509 -new -newkey rsa:2048 -nodes -days 3650 -config openssl.cnf -extensions v3_root \
    -subj "/CN=${spec#*:}" -keyout "$d/ca.key" -out "$d/ca.pem" 2>/dev/null
done

# The client's trust store: stands in for the OS / certifi / Node bundled roots.
cp pki/public-root/ca.pem trust/ca-bundle.pem

GOOD="DNS:localhost,IP:127.0.0.1"
I=tools/issue-cert.sh
$I servers/ok                   "$GOOD"                         >/dev/null  # control: correct setup
$I servers/missing-intermediate "$GOOD" --no-chain              >/dev/null  # 1. leaf only, no intermediate
# 2. self-signed: what `openssl req -x509` or a framework's "generate dev cert" gives you
mkdir -p servers/self-signed
SAN="$GOOD" openssl req -x509 -new -newkey rsa:2048 -nodes -days 365 -config openssl.cnf \
  -extensions v3_selfsigned -subj "/CN=localhost" \
  -keyout servers/self-signed/key.pem -out servers/self-signed/cert.pem 2>/dev/null
$I servers/wrong-host           "DNS:staging.lab.test"           >/dev/null  # 3. valid cert, wrong name
$I servers/expired              "$GOOD" --expired               >/dev/null  # 4. validity ended 2021
$I servers/corp-proxy           "$GOOD" --ca corp               >/dev/null  # 5. re-signed by corporate proxy CA
$I servers/canary-evil          "$GOOD" --ca evil               >/dev/null  # canary: attacker. Must always FAIL.
chmod 600 pki/*/ca.key

# What a real IT department sends you: where to get the CA, and the fingerprint to check it against.
FP="$(openssl x509 -in pki/corp-proxy-ca/ca.pem -noout -fingerprint -sha256 | sed 's/.*=//')"
cat > it-helpdesk-email.txt <<EOF
From: IT Service Desk
Subject: RE: "certificate errors" from scripts on the office network

Hi! All web traffic on the office network passes through our TLS inspection proxy.
Browsers trust it automatically. Developer tools (Python, Node, Docker, Java...) don't.
Please add our root CA to your tools' trust stores. Do NOT disable certificate checks.

  CA certificate:      pki/corp-proxy-ca/ca.pem   ("Corp TLS Inspection CA")
  SHA-256 fingerprint: $FP

Before trusting the file, check that its fingerprint matches the one above:
  openssl x509 -in pki/corp-proxy-ca/ca.pem -noout -fingerprint -sha256
If it doesn't match, don't use it. Call us.
EOF
echo "Lab ready. Next:  python3 servers.py   (then, in another terminal)  python3 check.py"
