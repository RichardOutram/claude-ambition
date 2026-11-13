#!/usr/bin/env python3
"""Check ticket structure in a plan file.

Usage: python3 -I check_tickets.py PLAN.md [DEVS]   (DEVS default 3)
Fails (exit 1) on: duplicate ids, unknown prerequisites, cycles, a ticket listed
before a prerequisite, a ticket with no 'Depends:' line, or no 'AC:' line.
Also prints the critical path (longest dependency chain).
"""
import re
import sys

HEAD = re.compile(r"^### (T-\d+) · (.+)$")
DEP = re.compile(r"^Depends:\s*(.+)$")
SIZE = re.compile(r"^Size:\s*(\d+)d\s*$")
AC = re.compile(r"^- AC:")


def parse(path):
    tickets, order, cur = {}, [], None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        m = HEAD.match(line)
        if m:
            tid = m.group(1)
            cur = {"id": tid, "title": m.group(2), "deps": None, "size": None, "ac": False, "dup": tid in tickets}
            tickets.setdefault(tid, cur)
            order.append(tid)
            continue
        if line.startswith("## "):
            cur = None
        if cur is None:
            continue
        m = DEP.match(line)
        if m and cur["deps"] is None:
            raw = m.group(1).strip()
            cur["deps"] = [] if raw.lower() == "none" else re.findall(r"T-\d+", raw)
        m = SIZE.match(line)
        if m:
            cur["size"] = int(m.group(1))
        if AC.match(line):
            cur["ac"] = True
    return tickets, order


def main(path, devs=3):
    tickets, order = parse(path)
    errors = []
    if not tickets:
        errors.append("no tickets found")
    seen = set()
    for tid in order:
        if tid in seen:
            errors.append(f"{tid}: duplicate id")
        seen.add(tid)
    pos = {t: i for i, t in enumerate(dict.fromkeys(order))}
    for tid, t in tickets.items():
        if t["deps"] is None:
            errors.append(f"{tid}: missing 'Depends:' line")
            t["deps"] = []
        if t["size"] is None:
            errors.append(f"{tid}: missing 'Size: Nd' line")
            t["size"] = 0
        if not t["ac"]:
            errors.append(f"{tid}: missing '- AC:' line")
        for d in t["deps"]:
            if d not in tickets:
                errors.append(f"{tid}: unknown prerequisite {d}")
            elif pos[d] >= pos[tid]:
                errors.append(f"{tid}: listed before its prerequisite {d}")
    # cycle detection + longest chain
    state, depth, days = {}, {}, {}

    def visit(t, stack):
        if state.get(t) == 2:
            return depth[t]
        if state.get(t) == 1:
            errors.append("cycle: " + " -> ".join(stack + [t]))
            return 0
        state[t] = 1
        best = 0
        best_days = 0
        for d in tickets[t]["deps"]:
            if d in tickets:
                best = max(best, visit(d, stack + [t]))
                best_days = max(best_days, days.get(d, 0))
        state[t] = 2
        depth[t] = best + 1
        days[t] = best_days + tickets[t]["size"]
        return depth[t]

    for t in tickets:
        visit(t, [])
    if errors:
        print("FAIL")
        for e in dict.fromkeys(errors):
            print(" -", e)
        return 1
    end = max(depth, key=depth.get)
    chain = [end]
    while tickets[chain[-1]]["deps"]:
        chain.append(max(tickets[chain[-1]]["deps"], key=lambda d: depth[d]))
    print(f"OK: {len(tickets)} tickets, no cycles, order valid, all have AC")
    print("Longest chain ({} tickets): {}".format(len(chain), " -> ".join(reversed(chain))))
    total = sum(t["size"] for t in tickets.values())
    cp = max(days.values())
    lower = max(cp, total / devs)
    print(f"Effort: {total} dev-days total; critical path {cp} working days")
    print(f"With {devs} devs: lower bound {lower:.0f} working days = {lower / 5:.1f} weeks (perfect parallelism, zero slack)")
    print(f"At 70% focus: {lower / 0.7 / 5:.1f} weeks")
    return 0


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) == 3 else 3))
