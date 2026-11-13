#!/usr/bin/env python3
"""Compute what a sub-release costs. Usage: python3 -I releases.py PLAN.md

Reads blocks like this from the plan:
  ### Release S1 · Title
  Include: T-001, T-002, ...
  Resize: T-004=2, T-011=2          (smaller version of the ticket for this release)
  Unlink: T-013!T-010               (drop a dependency: start at risk / in parallel)
  Link: T-018>T-013                 (add a dependency)
Fails if an included ticket depends on one that is not included."""
import importlib.util, os, re, sys

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ct", os.path.join(here, "check_tickets.py"))
ct = importlib.util.module_from_spec(spec); spec.loader.exec_module(ct)

def releases(path):
    text = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"^### Release (\w+) · (.+?)\n(.*?)(?=^#{2,3} |\Z)", text, re.M | re.S):
        body = m.group(3)
        g = lambda k: re.search(rf"^{k}:\s*(.*)$", body, re.M)
        inc = re.findall(r"T-\d+", g("Include").group(1)) if g("Include") else []
        rs = dict((a, int(b)) for a, b in re.findall(r"(T-\d+)=(\d+)", g("Resize").group(1))) if g("Resize") else {}
        un = re.findall(r"(T-\d+)!(T-\d+)", g("Unlink").group(1)) if g("Unlink") else []
        ln = re.findall(r"(T-\d+)>(T-\d+)", g("Link").group(1)) if g("Link") else []
        out.append((m.group(1), m.group(2), inc, rs, un, ln))
    return out

def evaluate(tickets, inc, rs, un, ln):
    errs, deps, size = [], {}, {}
    for t in inc:
        if t not in tickets: errs.append(f"{t}: not a ticket"); continue
        d = [x for x in tickets[t]["deps"] if (t, x) not in un]
        d += [b for a, b in ln if a == t and b not in d]
        deps[t] = d; size[t] = rs.get(t, tickets[t]["size"])
    for t, d in deps.items():
        for x in d:
            if x not in deps: errs.append(f"{t}: depends on {x}, which is not in the release")
    memo = {}
    def fin(t, stack=()):
        if t in memo: return memo[t]
        if t in stack: errs.append(f"cycle at {t}"); return 0
        memo[t] = size[t] + max([fin(x, stack + (t,)) for x in deps[t] if x in deps] or [0]); return memo[t]
    cp = max((fin(t) for t in deps), default=0)
    return errs, sum(size.values()), cp, len(deps)

def weeks(effort, cp, devs, focus):
    return max(cp, effort / devs) / focus / 5

if __name__ == "__main__":
    tickets, _ = ct.parse(sys.argv[1])
    bad = 0
    for rid, title, inc, rs, un, ln in releases(sys.argv[1]):
        errs, eff, cp, n = evaluate(tickets, inc, rs, un, ln)
        print(f"{rid} · {title}: {n} tickets, {eff} dev-days, critical path {cp} days")
        for d in (3, 4):
            print(f"   {d} devs: {weeks(eff, cp, d, 1):.1f} wk at 100% focus, {weeks(eff, cp, d, .7):.1f} wk at 70%")
        for e in errs: print("   ERROR", e); bad = 1
    sys.exit(bad)
