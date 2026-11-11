#!/usr/bin/env bash
# Print the four things that matter in every certificate in a PEM file:
#   who it is for (subject + SAN), who vouches for it (issuer), when it is valid.
# Usage: tools/show-chain.sh servers/missing-intermediate/cert.pem
#    or: tools/show-chain.sh host:port   (fetches what a live server actually sends)
set -euo pipefail
SRC="$1"
if [ ! -f "$SRC" ]; then
  # Live server: capture exactly the chain it presents (like a client sees it).
  HOST="${SRC%:*}"
  PEM="$(openssl s_client -connect "$SRC" -servername "$HOST" -showcerts </dev/null 2>/dev/null \
        | sed -n '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/p')"
else
  PEM="$(cat "$SRC")"
fi
n=0
while IFS= read -r line; do
  buf="${buf:-}$line"$'\n'
  if [ "$line" = "-----END CERTIFICATE-----" ]; then
    echo "[$n] $(printf '%s' "$buf" | openssl x509 -noout -subject)"
    printf '%s' "$buf" | openssl x509 -noout -issuer  | sed 's/^/    /'
    printf '%s' "$buf" | openssl x509 -noout -startdate -enddate | sed 's/^/    /'
    san="$(printf '%s' "$buf" | openssl x509 -noout -text | grep -A1 'Subject Alternative Name' | tail -1 | sed 's/^ *//' || true)"
    echo "    SAN: ${san:-<none>}"
    n=$((n+1)); buf=""
  fi
done <<< "$PEM"
echo "($n certificate(s) presented)"
