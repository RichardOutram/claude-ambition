#!/bin/sh
# Full acceptance run. Usage: sh judge.sh [html]   (default ../../prototype.html)
F=${1:-../../prototype.html}; cd "$(dirname "$0")"; FAIL=0
for c in flow consistency probe redteam fixes; do
  out=$(node $c.js "$F" 2>&1); echo "$c: $(echo "$out" | grep -c '^PASS') pass, $(echo "$out" | grep -c '^FAIL') fail"; echo "$out" | grep -q '^FAIL\|Error' && FAIL=1
done
echo "depth:"; node depth.js "$F" | grep -E "overflow|under 44|axe"
echo "audit:"; node audit.js "$F" | head -3
echo "primary-button-only driver (stretch T1: <=5 taps, <9 s):"; node primary.js "$F"
echo "core loop:"; node core.js "$F"
echo "coverage:"; node corpus.js "$F" corpus-final.txt
exit $FAIL
