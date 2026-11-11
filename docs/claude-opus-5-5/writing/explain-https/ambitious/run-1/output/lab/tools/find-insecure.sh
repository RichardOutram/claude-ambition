#!/usr/bin/env bash
# Find places where TLS certificate verification is switched off.
# Use it on your own repo, in a pre-commit hook, or as a CI step (exit 1 = findings).
#
#   tools/find-insecure.sh [path ...]          default: current directory
#
# Suppress a reviewed, justified line with a trailing comment:  tls-insecure-ok: <reason>
set -uo pipefail
PATTERNS=(
  '(^|[^A-Za-z_])verify(_ssl)?[[:space:]]*=[[:space:]]*False' # Python requests / httpx / old aiohttp
  '(^|[^A-Za-z_])ssl[[:space:]]*=[[:space:]]*False'         # aiohttp
  '_create_unverified_context'                              # Python stdlib
  'CERT_NONE'                                               # Python ssl
  'check_hostname[[:space:]]*=[[:space:]]*False'            # Python ssl
  'PYTHONHTTPSVERIFY[^A-Za-z0-9]*0'                         # Python env
  'disable_warnings\([^)]*InsecureRequestWarning'           # silencing the warning = hiding the problem
  'rejectUnauthorized["'"'"']?[[:space:]]*:[[:space:]]*false' # Node https/tls/axios
  'NODE_TLS_REJECT_UNAUTHORIZED[^A-Za-z0-9]*0'              # Node env
  'strictSSL["'"'"']?[[:space:]]*[:=][[:space:]]*false'     # npm / request
  'strict-ssl[[:space:]]*=?[[:space:]]*false'               # npm config / .npmrc
  'InsecureSkipVerify[[:space:]]*:[[:space:]]*true'         # Go
  '[Ii]nsecure_?[Ss]kip_?[Vv]erify["'"'"']?[[:space:]]*[:=][[:space:]]*[Tt]rue' # YAML/TOML configs (Prometheus, Grafana, ...)
  'checkServerIdentity["'"'"']?[[:space:]]*:[[:space:]]*(\([[:space:]]*\)|function[[:space:]]*\([[:space:]]*\))' # Node: no-op identity check
  '[Hh]ostnameVerifier[^;]*->[[:space:]]*true'              # Java lambda accepting any host
  'curl[[:space:]](.*[[:space:]])?(-[A-Za-z]*k[A-Za-z]*|--insecure)([[:space:]]|$)' # curl CLI, incl. -sk, -fsSLk
  'CURLOPT_SSL_VERIFY(PEER|HOST)[^;]*(false|0)'             # libcurl / PHP
  'http\.sslVerify[[:space:]]*=?[[:space:]]*false'          # git
  'GIT_SSL_NO_VERIFY'                                       # git env
  'wget .*--no-check-certificate'                           # wget
  'TrustAllCerts|trustAllCerts|X509TrustManager[^}]*\{[[:space:]]*\}' # Java
  'NoopHostnameVerifier|ALLOW_ALL_HOSTNAME_VERIFIER'        # Java Apache HttpClient
  'ServerCertificateCustomValidationCallback[[:space:]]*=.*=>[[:space:]]*true' # .NET
  'DangerousAcceptAnyServerCertificateValidator'            # .NET
  '--trusted-host'                                          # pip (skips TLS for that host)
  'sslmode=(disable|allow|prefer|require)'                  # Postgres: only verify-ca / verify-full check the cert
)
ALT="$(IFS='|'; echo "${PATTERNS[*]}")"
[ $# -eq 0 ] && set -- .
hits="$(grep -rInE --exclude-dir={.git,node_modules,.venv,venv,vendor,dist,build} \
        --exclude=find-insecure.sh -e "$ALT" "$@" 2>/dev/null | grep -v 'tls-insecure-ok:')"
if [ -n "$hits" ]; then
  echo "TLS verification appears to be disabled here:"; echo "$hits" | sed 's/^/  /'
  echo; echo "Fix the certificate problem instead (see HTTPS-for-developers.md, section 6)."
  exit 1
fi
echo "No disabled TLS verification found."
