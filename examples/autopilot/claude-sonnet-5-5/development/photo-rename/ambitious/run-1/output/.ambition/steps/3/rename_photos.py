#!/usr/bin/env python3
"""Rename photos by the date they were taken. Safe to run again and again.

    rename_photos.py FOLDER                 preview only (nothing is changed)
    rename_photos.py FOLDER --apply         rename for real, write a log + report
    rename_photos.py FOLDER --undo          preview undoing the latest run
    rename_photos.py FOLDER --undo --apply  undo the latest run
    rename_photos.py FOLDER --undo LOG --apply   undo a specific run's log

Guarantees
  * Never overwrites or deletes a file.
  * Files already named by date are left alone, so re-running is a no-op.
  * Photos taken in the same second get _1, _2, ... suffixes (stable order).
  * A photo whose content is identical to one already there is NOT renamed;
    it is left in place and listed as a duplicate for you to deal with.
  * Date comes from EXIF. If it is missing or implausible, the file's modified
    time is used and the file is flagged in the report so you can check it.
  * Every run writes a log and a readable report to FOLDER/_rename_logs/.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from collections import namedtuple
from datetime import datetime, timedelta
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # still works, but every date falls back to modified time
    Image = None
try:
    import pillow_heif

    pillow_heif.register_heif_opener()
except Exception:
    pass

EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".heif", ".webp"}
LOG_DIR = "_rename_logs"
MIN_YEAR = 1995  # camera clocks that were never set often read 1970/1980/2000
COMPANION_EXTS = {".mov", ".mp4", ".aae", ".xmp", ".thm",
                  ".dng", ".cr2", ".cr3", ".nef", ".arw", ".raf", ".orf", ".rw2"}
EXIF_IFD = 0x8769
Item = namedtuple("Item", "src dst date why")  # why is None when EXIF was used


# --------------------------------------------------------------------- dates
def plausible(d):
    return d.year >= MIN_YEAR and d <= datetime.now() + timedelta(days=1)


def _parse(v):
    """('ok', datetime) | ('bad', text) | None for an EXIF date string."""
    if not v:
        return None
    text = str(v).strip().strip("\x00")
    try:
        return "ok", datetime.strptime(text[:19], "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return ("bad", text) if text.strip(": 0") else None  # all-zero dates = unset


def read_date(path):
    """Return (datetime, why, subsec). why is None when a trustworthy EXIF date was used.

    Trust order: DateTimeOriginal (taken) > DateTimeDigitized > DateTime. The last is the
    'file changed' tag that editing software rewrites, so it is used but flagged.
    """
    why, found, subsec = "no EXIF date found", [], 0
    if Image is None:
        why = "Pillow not installed"
    else:
        try:
            with Image.open(path) as img:
                exif = img.getexif()
                try:
                    ifd = exif.get_ifd(EXIF_IFD)
                except Exception:
                    ifd = {}
                found = [(0x9003, ifd.get(0x9003)), (0x9004, ifd.get(0x9004)), (0x0132, exif.get(0x0132))]
                try:
                    subsec = int(str(ifd.get(0x9291, 0)).strip() or 0)
                except ValueError:
                    subsec = 0
        except Exception as e:
            why = f"could not read image ({type(e).__name__})"
    for tag, v in found:
        r = _parse(v)
        if r is None:
            continue
        if r[0] == "bad":
            why = f"EXIF date is malformed ({r[1]!r})"
            continue
        d = r[1]
        if not plausible(d):
            why = f"EXIF date {d:%Y-%m-%d %H:%M:%S} looks wrong"
            break
        if tag == 0x0132:
            return d, "only the EXIF 'file changed' date was available (may be an edit date)", subsec
        return d, None, subsec
    mtime = datetime.fromtimestamp(path.stat().st_mtime).replace(microsecond=0)
    return mtime, f"{why}; used file modified time", 0


# ------------------------------------------------------------------ planning
_SUFFIX = re.compile(r"_\d+$")


def already_named(stem, fmt):
    for s in (stem, _SUFFIX.sub("", stem)):
        try:
            datetime.strptime(s, fmt)
            return True
        except ValueError:
            pass
    return False


class Hasher:
    def __init__(self):
        self.cache = {}

    def digest(self, p):
        if p not in self.cache:
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            self.cache[p] = h.hexdigest()
        return self.cache[p]

    def same(self, a, b):
        try:
            if not (a.is_file() and b.is_file()) or a.stat().st_size != b.stat().st_size:
                return False
            return self.digest(a) == self.digest(b)
        except OSError:
            return False


def collect(folder, recursive):
    it = folder.rglob("*") if recursive else folder.iterdir()
    for p in sorted(it):
        parts = p.relative_to(folder).parts
        if LOG_DIR in parts or any(x.startswith(".") for x in parts):
            continue
        if p.is_file() and not p.is_symlink() and p.suffix.lower() in EXTS:
            yield p


def occupant(occ, parent, name):
    """Who holds this name? Trust the listing, but confirm free names by direct lookup:
    directory listings on some shared volumes (seen on VirtioFS) can omit files that exist."""
    hit = occ.get(name.lower())
    if hit is None and os.path.lexists(parent / name):
        hit = parent / name
    return hit


def make_plan(folder, recursive, fmt):
    """Return (renames, duplicates, already_named_files)."""
    hasher = Hasher()
    todo, skipped = [], []
    for p in collect(folder, recursive):
        if already_named(p.stem, fmt):
            skipped.append(p)
            continue
        d, why, sub = read_date(p)
        todo.append((str(p.parent), d, sub, p.name, p, why))
    todo.sort(key=lambda e: e[:4])  # stable: folder, date, sub-second (true shot order), name

    occupied, renames, dups, claimed = {}, [], [], set()
    for _, d, _, _, p, why in todo:
        parent = p.parent
        occ = occupied.get(parent)
        if occ is None:
            occ = occupied[parent] = {n.lower(): parent / n for n in os.listdir(parent)}
        # companions travel with their photo: Live Photo .MOV, .AAE/.xmp sidecars, RAW of a RAW+JPG
        comps = [c for n, c in occ.items()
                 if c not in claimed and c.suffix.lower() in COMPANION_EXTS
                 and c.stem.lower() == p.stem.lower() and c.is_file()]
        claimed.update(comps)
        stem, n = d.strftime(fmt), 0
        group = [(p, p.suffix.lower())] + sorted((c, c.suffix.lower()) for c in comps)
        while True:
            suffix = "" if n == 0 else f"_{n}"
            names = [f"{stem}{suffix}{e}" for _, e in group]
            others = [occupant(occ, parent, x) for x in names]
            if others[0] is not None and hasher.same(p, others[0]):
                dups.append((p, others[0]))
                claimed.difference_update(comps)  # nothing moves, so the companions stay put
                break
            if all(o is None for o in others):
                for (src, _), name in zip(group, names):
                    occ[name.lower()] = src  # reserve (same content as the file that will move)
                    renames.append(Item(src, parent / name, d, why if src is p else None))
                break
            n += 1
    return renames, dups, skipped


# -------------------------------------------------------------------- report
def build_report(folder, renames, dups, skipped, applied, title):
    moved = {it.src: it.dst for it in renames}
    flagged = [it for it in renames if it.why]
    rel = lambda p: str(Path(p).relative_to(folder))
    L = [title, f"Folder: {folder}", ""]
    L += [
        f"{'Renamed' if applied else 'Would rename'}: {len(renames)}",
        f"Already named (left alone): {len(skipped)}",
        f"Duplicates (left in place): {len(dups)}",
        f"Flagged - date not from EXIF, please check: {len(flagged)}",
        "",
    ]
    L.append("== FLAGGED: please check these dates ==")
    L += [f"  {rel(i.src)} -> {rel(i.dst)}\n      {i.why}" for i in flagged] or ["  none"]
    L += ["", "== DUPLICATES: identical content, not renamed, nothing deleted =="]
    for p, other in dups:
        o = moved.get(other, other)
        if p.exists() and Path(o).exists() and os.path.samefile(p, o):
            L.append(f"  {rel(p)} and {rel(o)} are the SAME file (a cut-off rename?) - run --undo --apply to repair")
        else:
            L.append(f"  {rel(p)} is identical to {rel(o)}")
    if not dups:
        L.append("  none")
    L += ["", "== ALL RENAMES =="]
    L += [f"  {rel(i.src)} -> {rel(i.dst)}" for i in renames] or ["  none"]
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------- apply
def apply_plan(folder, renames, dups, skipped):
    if not renames:  # no-op runs leave no log, so --undo always targets a real run
        return None, [], [], []
    logdir = folder / LOG_DIR
    logdir.mkdir(exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    log = logdir / f"run-{run_id}.jsonl"
    done, failed = [], []
    with open(log, "x") as f:
        f.write(json.dumps({"type": "run", "folder": str(folder), "at": run_id}) + "\n")
        for it in renames:
            if os.path.lexists(it.dst):  # last-moment guard; never overwrite
                failed.append((it, "target appeared"))
                continue
            # log first (and force it to disk) so a crash can always be undone
            f.write(json.dumps({"old": str(it.src.relative_to(folder)),
                                "new": str(it.dst.relative_to(folder))}) + "\n")
            f.flush()
            os.fsync(f.fileno())
            try:
                os.rename(it.src, it.dst)
                done.append(it)
            except OSError as e:
                failed.append((it, str(e)))
    suspect = [it for it in done if os.path.lexists(it.src) or not os.path.lexists(it.dst)]
    report = build_report(folder, done, dups, skipped, True, f"Photo rename report {run_id}")
    if suspect:
        report += "\n== CHECK THESE: after renaming, the old or new name looked wrong ==\n" + "".join(
            f"  {i.src.name} -> {i.dst.name}\n" for i in suspect)
    if failed:
        report += "\n== FAILED (not renamed) ==\n" + "".join(
            f"  {i.src.name}: {why}\n" for i, why in failed)
    (logdir / f"run-{run_id}.report.txt").write_text(report)
    return log, done, failed, suspect


def find_log(folder, given):
    if given:
        return Path(given)
    logs = [p for p in sorted((folder / LOG_DIR).glob("run-*.jsonl"))
            if not p.name.endswith(".undone.jsonl")]
    return logs[-1] if logs else None


def undo(folder, given, apply_):
    log = find_log(folder, given)
    if not log or not log.exists():
        print("No run log found to undo.")
        return 1
    lines = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
    entries = [e for e in lines if "old" in e]
    when = datetime.strptime(log.name[4:].split(".")[0][:22], "%Y%m%d-%H%M%S-%f") if re.match(
        r"run-\d{8}-\d{6}-\d{6}", log.name) else None
    print(f"{'Undoing' if apply_ else 'Would undo'} the run from {when:%Y-%m-%d %H:%M:%S}"
          f" ({len(entries)} renames):\n" if when else f"Undoing {log.name}:\n")
    restored = already = problems = 0
    for e in reversed(entries):
        old, new = folder / e["old"], folder / e["new"]
        if os.path.lexists(new) and not os.path.lexists(old):
            print(f"{e['new']} -> {e['old']}")
            if apply_:
                os.rename(new, old)
            restored += 1
        elif os.path.lexists(old) and not os.path.lexists(new):
            already += 1
        elif os.path.lexists(old) and os.path.lexists(new):
            if os.path.samefile(old, new):  # a rename that was cut off half-way: one file, two names
                print(f"{e['new']} -> {e['old']}  (finishing an interrupted rename)")
                if apply_:
                    try:
                        os.unlink(new)  # only removes the extra name; the file itself stays
                    except FileNotFoundError:  # already gone (stale directory listing)
                        pass
                restored += 1
            else:
                print(f"SKIPPED (both exist, not touching): {e['old']} / {e['new']}")
                problems += 1
        else:
            print(f"SKIPPED (neither exists): {e['old']} / {e['new']}")
            problems += 1
    verb = "Restored" if apply_ else "Would restore"
    print(f"\n{verb} {restored} files ({already} already restored, {problems} problems). Log: {log.name}")
    if apply_ and not problems:
        log.rename(log.with_name(log.name[:-len(".jsonl")] + ".undone.jsonl"))
    elif not apply_:
        print("Re-run with --apply to do it.")
    return 1 if problems else 0


# ---------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path)
    ap.add_argument("--apply", action="store_true", help="make changes (default is preview only)")
    ap.add_argument("-r", "--recursive", action="store_true")
    ap.add_argument("--format", default="%Y-%m-%d_%H-%M-%S", help="strftime format for new names")
    ap.add_argument("--undo", nargs="?", const=True, metavar="LOG", help="undo the latest run, or the given log")
    args = ap.parse_args(argv)

    folder = args.folder.resolve()
    if not folder.is_dir():
        print(f"Not a directory: {folder}")
        return 2
    if args.undo:
        return undo(folder, None if args.undo is True else args.undo, args.apply)
    if Image is None:
        print("Note: Pillow not installed; every file will use its modified time and be flagged.\n")

    renames, dups, skipped = make_plan(folder, args.recursive, args.format)
    if args.apply:
        log, done, failed, suspect = apply_plan(folder, renames, dups, skipped)
        if log is None:
            print(f"Nothing to rename ({len(skipped)} already named, {len(dups)} duplicates).")
            return 0
        for it in done:
            print(f"{it.src.relative_to(folder)} -> {it.dst.name}")
        print(f"\nRenamed {len(done)}, already named {len(skipped)}, duplicates {len(dups)}, "
              f"flagged {sum(1 for i in done if i.why)}, failed {len(failed)}.")
        if suspect:
            print(f"WARNING: {len(suspect)} files did not look right after renaming; see the report.")
        print(f"Report: {log.with_suffix('.report.txt')}\nUndo:   {sys.argv[0]} {folder} --undo --apply")
    else:
        print(build_report(folder, renames, dups, skipped, False, "PREVIEW - nothing has been changed"))
        print("Re-run with --apply to do it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
