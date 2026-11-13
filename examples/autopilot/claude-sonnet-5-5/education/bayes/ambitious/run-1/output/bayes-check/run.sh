#!/bin/sh
# Runs every check on ../bayes.html. Needs Node 22+ and Chrome (set CHROME=... if not at the macOS default). ~3 min.
cd "$(dirname "$0")" || exit 1
fail=0
run() { printf '%-34s' "$1"; out=$(node "$2" 2>&1); code=$?; echo "$out" | tail -n 3 | tr '\n' ' ' | cut -c1-90; echo; [ $code -eq 0 ] || { fail=1; echo "$out" | grep -E '^FAIL' | head -5; }; }
run "exact maths (4,096 settings)"   check.mjs
run "interaction (typing, clicks)"   drive.mjs
run "hostile input + spoilers"       red.mjs
run "proportion bar fills its row"   barw.mjs
run "Play it for me (<=12.5 s)"      play.mjs
[ -f ../.ambition/first/bayes.html ] && { echo; node judge.mjs; }
[ $fail -eq 0 ] && echo "ALL PASS" || { echo "FAILED"; exit 1; }
