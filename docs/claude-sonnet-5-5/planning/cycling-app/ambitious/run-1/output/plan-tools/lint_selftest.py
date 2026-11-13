#!/usr/bin/env python3
"""Prove plan_lint.py can fail. Usage: python3 -I plan-tools/lint_selftest.py [PLAN.md]
Baseline must pass; each deliberate breakage must make the lint exit non-zero."""
import os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), "PLAN.md")
src = open(PLAN, encoding="utf-8").read()
MUTATIONS = {
    "cost cell changed": ("| Mapbox Mobile Maps | 0 | 0 | 100 |", "| Mapbox Mobile Maps | 0 | 0 | 90 |"),
    "worked XP example changed": ("| 280 | 322 (+15%) |", "| 280 | 330 (+15%) |"),
    "dangling section reference": ("(see §6 and §9)", "(see §99)"),
    "dependency cycle": ("Depends: none", "Depends: T-054"),
    "principle dropped from a ticket": ("never shown while a ride is recording", "shown any time"),
    "false hop in riskiest path": ("T-001 → T-011 → T-012 → **T-013**", "T-001 → T-012 → **T-013**"),
}
def lint(text):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(text); name = f.name
    try:
        return subprocess.run([sys.executable, "-I", os.path.join(HERE, "plan_lint.py"), name], capture_output=True).returncode
    finally:
        os.unlink(name)
bad = []
if lint(src) != 0: bad.append("baseline should pass")
for label, (old, new) in MUTATIONS.items():
    if src.count(old) < 1: bad.append(f"{label}: target text not found"); continue
    if lint(src.replace(old, new, 1)) == 0: bad.append(f"{label}: lint did NOT fail")
print("selftest FAILED:\n  " + "\n  ".join(bad) if bad else f"selftest OK: baseline passes, {len(MUTATIONS)} breakages all caught")
sys.exit(1 if bad else 0)
