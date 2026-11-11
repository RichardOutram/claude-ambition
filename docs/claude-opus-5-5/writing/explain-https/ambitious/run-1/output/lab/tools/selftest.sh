#!/usr/bin/env bash
# Proves the lab itself works (run by maintainers, not part of the exercise):
#   1. fresh setup -> 0/5 fixed, canary blocked   (every error really reproduces)
#   2. trusting the attacker CA -> canary BREACHED (the anti-cheat really fires)
#   3. reference solutions -> 5/5 fixed, canary blocked
# Requires servers.py to be running. Leaves the lab in the SOLVED state; run ./setup.sh to reset.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0
expect() { # description expected-exit actual-exit
  if [ "$2" = "$3" ]; then echo "PASS  $1"; else echo "FAIL  $1 (expected exit $2, got $3)"; fail=1; fi
}
./setup.sh >/dev/null
out="$(python3 check.py)"; rc=$?
expect "broken lab: nothing passes" 1 $rc
grep -q "0/5 scenarios fixed" <<<"$out" && echo "PASS  broken lab: 0/5" || { echo "FAIL  broken lab count"; fail=1; }

cp trust/ca-bundle.pem trust/ca-bundle.bak
cat pki/evil-ca/ca.pem >> trust/ca-bundle.pem
python3 check.py >/dev/null; rc=$?
expect "trusting attacker CA trips the canary" 2 $rc
mv trust/ca-bundle.bak trust/ca-bundle.pem

tools/issue-cert.sh servers/corp-proxy "DNS:localhost,IP:127.0.0.1" >/dev/null   # "fix" the proxy server-side
out="$(python3 check.py)"; grep -q "WRONG FIX" <<<"$out"; expect "server-side fix of the corp proxy is rejected" 0 $?
./setup.sh >/dev/null

./solutions.sh >/dev/null; rc=$?
expect "reference solutions: 5/5 fixed, canary blocked" 0 $rc

python3 mitm_demo.py | grep -q "Authorization: Bearer FAKE" ; expect "mitm demo: verify OFF leaks the token" 0 $?
python3 mitm_demo.py | grep -q "nothing. The request was never sent" ; expect "mitm demo: verify ON blocks it" 0 $?

n_bad=$(wc -l < tools/testdata/insecure_samples.txt | tr -d ' ')
n_hit=$(tools/find-insecure.sh tools/testdata/insecure_samples.txt | grep -c insecure_samples)
expect "scanner flags all $n_bad insecure samples" "$n_bad" "$n_hit"
tools/find-insecure.sh tools/testdata/secure_samples.txt >/dev/null; expect "scanner: no false positives on secure samples" 0 $?
tools/find-insecure.sh --exclude-dir=testdata . >/dev/null; expect "lab code itself is clean (outside testdata)" 0 $?
exit $fail
