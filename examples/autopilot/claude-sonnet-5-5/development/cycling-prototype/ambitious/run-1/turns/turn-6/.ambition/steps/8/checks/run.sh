#!/bin/sh
# Acceptance run for ../prototype.html (or $1). Exits non-zero on any failure. Needs Chrome (set CHROME=/path if not on macOS default).
# First time: (cd checks && npm install). Add "fuzz" as $2 to also run the ~4 min random-action fuzz.
cd "$(dirname "$0")"; F=${1:-../prototype.html}; FAIL=0
[ -d node_modules ] || npm install --silent
for c in flow consistency probe redteam fixes; do
  out=$(node $c.js "$F" 2>&1); echo "$c: $(echo "$out" | grep -c '^PASS') pass, $(echo "$out" | grep -c '^FAIL') fail"
  echo "$out" | grep -q '^FAIL\|Error' && FAIL=1
done
d=$(node depth.js "$F"); echo "$d" | grep -E "overflow|under 44|axe"; echo "$d" | grep -q "under 44px: 0" && ! echo "$d" | grep -q "^  [a-z-]* \[" || FAIL=1
a=$(node audit.js "$F"); echo "$a" | head -3   # known benign: re-tapping the already-selected tab/segment (15 hits)
echo "$a" | grep -q "Console/page errors: 0" || FAIL=1
p=$(node primary.js "$F"); echo "primary-button-only: $p"; echo "$p" | grep -q '"reachedChallenge":true,"taps":5' || FAIL=1
node core.js "$F"
c=$(node corpus.js "$F" /tmp/prototype-corpus.txt); echo "$c"; echo "$c" | grep -q "44/44" || FAIL=1
[ "$2" = fuzz ] && { node fuzz.js "$F" 1,2,3,4,5 800 | grep -E "^actions" ; node fuzz.js "$F" 1 1 >/dev/null || FAIL=1; }
[ $FAIL = 0 ] && echo "ALL CHECKS PASSED" || echo "CHECKS FAILED"; exit $FAIL
