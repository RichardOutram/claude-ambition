#!/bin/sh
# Re-run the plan's arithmetic check and its promise/structure judge.
# Usage: plan-tools/run_checks.sh [plan.md]   (default: etsy-candle-marketing-plan.md)
cd "$(dirname "$0")/.." || exit 1
PLAN="${1:-etsy-candle-marketing-plan.md}"
python3 -I plan-tools/check_plan.py "$PLAN" || exit 1
FIRST=.ambition/first/etsy-candle-marketing-plan.md
if [ -f "$FIRST" ]; then python3 -I plan-tools/judge.py "$PLAN" "$FIRST"; else python3 -I plan-tools/judge.py "$PLAN" "$PLAN"; fi
