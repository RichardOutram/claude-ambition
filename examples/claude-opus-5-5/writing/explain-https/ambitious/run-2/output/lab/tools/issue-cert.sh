#!/usr/bin/env bash
# The lab's "certificate desk": issue a server certificate from a lab CA.
# In real life this is Let's Encrypt / ACME, your company's internal CA,
# cert-manager, or mkcert for local dev. Same idea: a CA your clients
# already trust vouches that this key belongs to these hostnames.
#
# Usage:
#   tools/issue-cert.sh <out-dir> <SAN> [--ca public|corp|evil] [--expired] [--no-chain]
#
#   <out-dir>   where to write key.pem and cert.pem (e.g. servers/expired)
#   <SAN>       subjectAltName, e.g. "DNS:localhost,IP:127.0.0.1"
#   --ca        which CA signs it (default: public = the lab's "public" CA via its intermediate)
#   --expired   issue a cert whose validity ended in 2021 (for the broken scenario)
#   --no-chain  write ONLY the leaf into cert.pem (the classic misconfiguration)
#
# cert.pem is what the server sends: leaf first, then intermediate(s). Never the root.
set -euo pipefail
LAB="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$1"; SAN="$2"; shift 2
CA=public; EXPIRED=0; CHAIN=1
while [ $# -gt 0 ]; do
  case "$1" in
    --ca) CA="$2"; shift 2;;
    --expired) EXPIRED=1; shift;;
    --no-chain) CHAIN=0; shift;;
    *) echo "unknown option $1" >&2; exit 2;;
  esac
done
case "$CA" in
  public) SIGNER="$LAB/pki/public-intermediate";;
  corp)   SIGNER="$LAB/pki/corp-proxy-ca";;
  evil)   SIGNER="$LAB/pki/evil-ca";;
  *) echo "unknown CA $CA" >&2; exit 2;;
esac
mkdir -p "$OUT"
CN="${SAN%%,*}"; CN="${CN#*:}"
TMP="$LAB/.tmp.$$"; mkdir -p "$TMP"; trap 'rm -rf "$TMP"' EXIT
CA_DIR="$SIGNER" SAN="$SAN" openssl req -new -newkey rsa:2048 -nodes -keyout "$OUT/key.pem" -out "$TMP/req.csr" \
  -config "$LAB/openssl.cnf" -subj "/CN=$CN" 2>/dev/null
DATES=()
if [ "$EXPIRED" = 1 ]; then DATES=(-startdate 20200101000000Z -enddate 20210101000000Z); fi
CA_DIR="$SIGNER" SAN="$SAN" openssl ca -batch -config "$LAB/openssl.cnf" -extensions v3_server \
  -in "$TMP/req.csr" -out "$TMP/leaf.pem" -notext ${DATES[@]+"${DATES[@]}"} 2>/dev/null
cp "$TMP/leaf.pem" "$OUT/cert.pem"
if [ "$CHAIN" = 1 ] && [ "$CA" = public ]; then
  cat "$SIGNER/ca.pem" >> "$OUT/cert.pem"      # leaf + intermediate = "fullchain"
fi
chmod 600 "$OUT/key.pem"
echo "issued $OUT/cert.pem  (CA=$CA SAN=$SAN expired=$EXPIRED chain=$CHAIN)"
