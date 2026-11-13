#!/usr/bin/env python3
"""Rename photos by the date they were taken. Safe to run again and again.

    rename_photos.py FOLDER                 preview only (nothing is changed)
    rename_photos.py FOLDER --apply         rename for real, write a log + report
    rename_photos.py FOLDER --undo          preview undoing the latest run
    rename_photos.py FOLDER --undo --apply  undo the latest run
    rename_photos.py FOLDER --undo LOG --apply   undo a specific run's log

Guarantees
  * Never overwrites a file and never deletes a photo.
  * Files already named by date are left alone, so re-running is a no-op.
  * Photos taken in the same second get _1, _2, ... suffixes (stable order).
  * A photo whose content is identical to one already there is NOT renamed;
    it is left in place and listed as a duplicate for you to deal with.
  * Date comes from EXIF. If it is missing or implausible, the file's modified
    time is used and the file is flagged in the report so you can check it.
  * Every run that renames something writes an undo log and a readable report to
    FOLDER/_rename_logs/. A run that only finds duplicates writes just the report.
  * Live Photo videos, .AAE/.xmp sidecars and RAW files travel with their photo.
  * Photo-library packages (.photoslibrary etc.) are never entered.

Needs Pillow and pillow-heif:  python3 -m venv .venv && .venv/bin/pip install Pillow pillow-heif
"""
import argparse
import contextlib
import ctypes
import errno
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

    Image.MAX_IMAGE_PIXELS = None  # we only read metadata, never decode pixels; big panoramas are fine
except ImportError:
    Image = None
try:
    import pillow_heif

    pillow_heif.register_heif_opener()
    HEIF_OK = True
except Exception:
    HEIF_OK = False

EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".heif", ".webp"}
LOG_DIR = "_rename_logs"
MIN_YEAR = 1995  # camera clocks that were never set often read 1970/1980/2000
COMPANION_EXTS = {".mov", ".mp4", ".aae", ".xmp", ".thm",
                  ".dng", ".cr2", ".cr3", ".nef", ".arw", ".raf", ".orf", ".rw2"}
PACKAGE_SUFFIXES = (".photoslibrary", ".aplibrary", ".migratedphotolibrary", ".lrlibrary", ".lrdata", ".tvlibrary")
EXIF_IFD = 0x8769
Item = namedtuple("Item", "src dst date why label")  # why is None when EXIF was used; label = where the date came from


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
    """Return (datetime, why, subsec, label). why is None when a trustworthy EXIF date was used;
    label says which source produced the date, for the report.

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
            return d, "only the EXIF 'file changed' date was available (may be an edit date)", subsec, "EXIF file-changed date"
        if d.month == 1 and d.day == 1 and d.hour == 0 and d.minute < 10:
            return d, "looks like a camera clock reset (Jan 1, just after midnight)", subsec, "EXIF taken"
        return d, None, subsec, "EXIF taken" if tag == 0x9003 else "EXIF digitized"
    mtime = datetime.fromtimestamp(path.stat().st_mtime).replace(microsecond=0)
    return mtime, f"{why}; used file modified time", 0, "file modified time"


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


def inside(folder, rel):
    """True if folder/rel stays inside folder (no '..', absolute paths or symlinked parents leading out)."""
    if os.path.isabs(rel):
        return False
    p = os.path.normpath(os.path.join(folder, rel))
    root, parent = os.path.realpath(folder), os.path.realpath(os.path.dirname(p))
    return parent == root or parent.startswith(root + os.sep)


try:  # macOS atomic "rename, but fail if the target exists"; looked up once
    _renamex = ctypes.CDLL(None, use_errno=True).renamex_np if sys.platform == "darwin" else None
except (OSError, AttributeError):
    _renamex = None


def safe_rename(src, dst):
    """Rename without ever replacing an existing file (atomic on macOS where supported)."""
    if _renamex is not None:
        r = _renamex(os.fsencode(src), os.fsencode(dst), 0x4)  # RENAME_EXCL
        if r == 0:
            return
        err = ctypes.get_errno()
        if err == errno.EEXIST:
            raise FileExistsError(errno.EEXIST, "target exists", str(dst))
        if err not in (errno.ENOTSUP, errno.EINVAL, errno.ENOSYS):  # else: this filesystem lacks it; fall back
            raise OSError(err, os.strerror(err), str(src))
    if os.path.lexists(dst):
        raise FileExistsError(errno.EEXIST, "target exists", str(dst))
    os.rename(src, dst)


class SetupError(Exception):
    pass


class RunLock:
    """One changing run per folder at a time."""

    def __init__(self, folder):
        self.path = folder / ".rename_photos.lock"

    def __enter__(self):
        for _ in range(2):
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return self
            except FileExistsError:
                if not self._stale():
                    raise SetupError(f"Another run seems to be in progress in this folder ({self.path.name}). "
                                     "If you are sure it is not, delete that file.")
                try:
                    os.unlink(self.path)
                except FileNotFoundError:
                    pass
            except OSError as e:
                raise SetupError(f"Cannot write to {self.path.parent} ({e.strerror}). Nothing was changed.")
        raise SetupError("Could not take the folder lock.")

    def __exit__(self, *exc):
        try:
            os.unlink(self.path)
        except OSError:
            pass

    def _stale(self):
        try:
            pid = int(self.path.read_text().strip())
            os.kill(pid, 0)
        except (ProcessLookupError, ValueError):
            return True
        except (OSError, PermissionError):
            return False
        return False


def collect(folder, recursive):
    it = folder.rglob("*") if recursive else folder.iterdir()
    for p in sorted(it):
        parts = p.relative_to(folder).parts
        if LOG_DIR in parts or any(x.startswith(".") for x in parts):
            continue
        if any(x.lower().endswith(PACKAGE_SUFFIXES) for x in parts):
            continue  # app-managed library: renaming inside it corrupts it
        if p.is_file() and not p.is_symlink() and p.suffix.lower() in EXTS \
                and inside(folder, str(p.relative_to(folder))):
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
        d, why, sub, label = read_date(p)
        todo.append((str(p.parent), d, sub, p.name, p, why, label))
    todo.sort(key=lambda e: e[:4])  # stable: folder, date, sub-second (true shot order), name

    kept = {}  # size -> files that stay (already named, or planned earlier): candidates for "same content"
    by_digest, indexed = {}, set()  # content hash -> file, filled lazily and only for files sharing a size

    def twin_of(p, size):
        peers = kept.get(size)
        if not peers:
            return None
        try:
            for q in peers:  # hash each same-size peer once, not once per comparison
                if q not in indexed:
                    indexed.add(q)
                    by_digest.setdefault(hasher.digest(q), q)
            return by_digest.get(hasher.digest(p))
        except OSError:
            return None

    for q in skipped:
        kept.setdefault(q.stat().st_size, []).append(q)
    occupied, renames, dups, claimed = {}, [], [], set()
    for _, d, _, _, p, why, label in todo:
        parent = p.parent
        size = p.stat().st_size
        twin = twin_of(p, size)
        if twin is not None:  # identical bytes already present under another name
            dups.append((p, twin))
            continue
        kept.setdefault(size, []).append(p)
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
                kept[size].remove(p)
                claimed.difference_update(comps)  # nothing moves, so the companions stay put
                break
            if all(o is None for o in others):
                for (src, _), name in zip(group, names):
                    occ[name.lower()] = src  # reserve (same content as the file that will move)
                    renames.append(Item(src, parent / name, d, why if src is p else None,
                                        label if src is p else f"travels with {p.name}"))
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
        f"Flagged - please check these dates: {len(flagged)}",
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
    L += [f"  {rel(i.src)} -> {rel(i.dst)}   [{i.label}]" for i in renames] or ["  none"]
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------- apply
def apply_plan(folder, renames, dups, skipped):
    logdir = folder / LOG_DIR
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    if not renames:  # no-op runs leave no undo log (so --undo always targets a real run) ...
        path = None
        if dups:  # ... but duplicates still deserve a readable list
            logdir.mkdir(exist_ok=True)
            for old in logdir.glob("run-*.report.txt"):  # replace the previous duplicates-only report
                if not old.with_name(old.name[:-len(".report.txt")] + ".jsonl").exists() and not \
                        old.with_name(old.name[:-len(".report.txt")] + ".undone.jsonl").exists():
                    old.unlink()
            path = logdir / f"run-{run_id}.report.txt"
            path.write_text(build_report(folder, [], dups, skipped, True, f"Photo rename report {run_id}"))
        return None, [], [], [], path
    log = logdir / f"run-{run_id}.jsonl"
    try:
        logdir.mkdir(exist_ok=True)
        f = open(log, "x")
    except OSError as e:
        raise SetupError(f"Cannot write the undo log in {logdir} ({e.strerror}). Nothing was changed.")
    done, failed = [], []
    with f:
        f.write(json.dumps({"type": "run", "folder": str(folder), "at": run_id}) + "\n")
        for it in renames:
            rel_old = str(it.src.relative_to(folder))
            try:
                st = os.lstat(it.src)  # the file's identity, so undo can tell it from an impostor
                fingerprint = {"size": st.st_size, "mtime_ns": st.st_mtime_ns, "ino": st.st_ino}
            except OSError:
                fingerprint = {}
            # log first (and force it to disk) so a crash can always be undone
            f.write(json.dumps({"old": rel_old, "new": str(it.dst.relative_to(folder)), **fingerprint}) + "\n")
            f.flush()
            os.fsync(f.fileno())
            try:
                safe_rename(it.src, it.dst)  # never replaces an existing file
                done.append(it)
            except OSError as e:
                failed.append((it, "target appeared" if isinstance(e, FileExistsError) else str(e)))
                f.write(json.dumps({"skipped": rel_old}) + "\n")  # tells undo this one never moved
                f.flush()
    suspect = [it for it in done if os.path.lexists(it.src) or not os.path.lexists(it.dst)]
    report = build_report(folder, done, dups, skipped, True, f"Photo rename report {run_id}")
    if suspect:
        report += "\n== CHECK THESE: after renaming, the old or new name looked wrong ==\n" + "".join(
            f"  {i.src.name} -> {i.dst.name}\n" for i in suspect)
    if failed:
        report += "\n== FAILED (not renamed) ==\n" + "".join(
            f"  {i.src.name}: {why}\n" for i, why in failed)
    (logdir / f"run-{run_id}.report.txt").write_text(report)
    return log, done, failed, suspect, log.with_suffix('.report.txt')


def find_log(folder, given):
    if given:
        return Path(given)
    logs = [p for p in sorted((folder / LOG_DIR).glob("run-*.jsonl"))
            if not p.name.endswith(".undone.jsonl")]
    return logs[-1] if logs else None


def undo(folder, given, apply_, force=False):
    log = find_log(folder, given)
    if not log or not log.exists():
        print("No run log found to undo.")
        return 1
    try:
        lines = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
        never_moved = {e["skipped"] for e in lines if "skipped" in e}
        entries = [e for e in lines if "old" in e and e["old"] not in never_moved]
        outside = [x for e in entries for x in (e["old"], e["new"]) if not inside(folder, x)]
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"{log.name} is not a valid run log ({e}). Nothing was changed.")
        return 2
    if outside:
        print(f"Refusing: {log.name} refers to paths outside {folder} (e.g. {outside[0]}). Nothing was changed.")
        return 2
    when = datetime.strptime(log.name[4:].split(".")[0][:22], "%Y%m%d-%H%M%S-%f") if re.match(
        r"run-\d{8}-\d{6}-\d{6}", log.name) else None
    print(f"{'Undoing' if apply_ else 'Would undo'} the run from {when:%Y-%m-%d %H:%M:%S}"
          f" ({len(entries)} renames):\n" if when else f"Undoing {log.name}:\n")
    restored = already = problems = 0
    for e in reversed(entries):
        old, new = folder / e["old"], folder / e["new"]
        if os.path.lexists(new) and not os.path.lexists(old):
            if "ino" in e and not force:
                st = os.lstat(new)
                if (st.st_size, st.st_mtime_ns, st.st_ino) != (e["size"], e["mtime_ns"], e["ino"]):
                    print(f"SKIPPED (not the file that was renamed - changed or replaced since; "
                          f"use --force to restore anyway): {e['new']}")
                    problems += 1
                    continue
            print(f"{e['new']} -> {e['old']}")
            if apply_:
                try:
                    safe_rename(new, old)
                except OSError as err:
                    print(f"SKIPPED ({err.strerror}): {e['old']}")
                    problems += 1
                    continue
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
HOW_TO_FIX = ("Install them in a virtual environment, then run the script with that Python:\n"
              "    python3 -m venv .venv && .venv/bin/pip install Pillow pillow-heif\n"
              "    .venv/bin/python rename_photos.py FOLDER\n"
              "Or pass --allow-mtime to name those files by their modified time (they will be flagged).")


def preflight(folder, recursive):
    """Refuse to guess: without these libraries real EXIF dates would be silently ignored."""
    if Image is None:
        return "Pillow is not installed, so photo dates cannot be read."
    if not HEIF_OK and any(p.suffix.lower() in (".heic", ".heif") for p in collect(folder, recursive)):
        return "This folder has HEIC/HEIF photos but pillow-heif is not installed, so their dates cannot be read."
    return None

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path, help="the folder of photos")
    ap.add_argument("--apply", action="store_true", help="make changes (default is preview only)")
    ap.add_argument("-r", "--recursive", action="store_true", help="also rename photos in subfolders")
    ap.add_argument("--format", default="%Y-%m-%d_%H-%M-%S", help="strftime format for new names")
    ap.add_argument("--allow-mtime", action="store_true",
                    help="proceed even if EXIF cannot be read (names come from modified time, all flagged)")
    ap.add_argument("--force", action="store_true",
                    help="with --undo: restore files even if they changed since they were renamed")
    ap.add_argument("--undo", nargs="?", const=True, metavar="LOG", help="undo the latest run, or the given log")
    args = ap.parse_args(argv)

    folder = args.folder.resolve()
    if not folder.is_dir():
        print(f"Not a directory: {args.folder}")
        return 2
    if args.recursive and (folder == Path.home() or folder.parent == folder or len(folder.parts) <= 2):
        print(f"Refusing to search {folder} recursively - that is far too broad. Point at a photo folder.")
        return 2
    if args.undo:
        try:
            with RunLock(folder) if args.apply else contextlib.nullcontext():
                return undo(folder, None if args.undo is True else args.undo, args.apply, args.force)
        except SetupError as e:
            print(e)
            return 2
    if folder.name.lower().endswith(PACKAGE_SUFFIXES):
        print(f"{folder.name} is an app-managed photo library; renaming inside it would corrupt it. Refusing.")
        return 2
    problem = preflight(folder, args.recursive)
    if problem and not args.allow_mtime:
        print(f"{problem}\nNothing was changed.\n{HOW_TO_FIX}")
        return 2
    if problem:
        print(f"Note: {problem} Using modified time for those files.\n")

    try:
        with RunLock(folder) if args.apply else contextlib.nullcontext():
            renames, dups, skipped = make_plan(folder, args.recursive, args.format)
            result = apply_plan(folder, renames, dups, skipped) if args.apply else None
    except SetupError as e:
        print(e)
        return 2
    if args.apply:
        log, done, failed, suspect, report_path = result
        if log is None:
            print(f"Nothing to rename ({len(skipped)} already named, {len(dups)} duplicates).")
            if report_path:
                print(f"Duplicates are listed in: {report_path}")
            return 0
        for it in done:
            print(f"{it.src.relative_to(folder)} -> {it.dst.name}")
        print(f"\nRenamed {len(done)}, already named {len(skipped)}, duplicates {len(dups)}, "
              f"flagged {sum(1 for i in done if i.why)}, failed {len(failed)}.")
        if suspect:
            print(f"WARNING: {len(suspect)} files did not look right after renaming; see the report.")
        print(f"Report: {report_path}\nUndo:   {sys.argv[0]} {folder} --undo --apply")
    else:
        print(build_report(folder, renames, dups, skipped, False, "PREVIEW - nothing has been changed"))
        print("Re-run with --apply to do it.")
        print("Note: if these photos are managed by Lightroom, Capture One or a Photos library, rename them "
              "inside that app - renaming outside it breaks its links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
