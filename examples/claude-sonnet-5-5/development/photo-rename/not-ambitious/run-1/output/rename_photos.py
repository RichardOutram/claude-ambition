#!/usr/bin/env python3
"""Rename (and optionally organize) photos and videos by the date they were taken.

Date sources, in order of trust:
  1. EXIF DateTimeOriginal / DateTime          (photos)
  2. Container creation_time via ffprobe       (videos, if ffprobe is installed)
  3. A timestamp in the filename               (IMG_20240714_153208.jpg, Screenshot 2024-07-14 at 15.32.08.png)
  4. File modification time                    (skipped with --skip-undated)

Companion files that share a name (IMG_0001.xmp, IMG_0001.aae, Live Photo IMG_0001.mov)
are renamed together with their photo so they stay paired.

Usage:
    rename_photos.py DIR                       # dry run, preview only
    rename_photos.py DIR --apply               # rename
    rename_photos.py DIR -r --apply            # include subfolders
    rename_photos.py DIR --organize "%Y/%m" --apply   # also move into 2024/07/ folders
    rename_photos.py DIR --format "%Y%m%d_%H%M%S" --apply
    rename_photos.py DIR --dedupe              # report byte-identical duplicates, leave them alone
    rename_photos.py --undo DIR/.rename_log_XXXX.json  # reverse a previous --apply

Optional: pip install Pillow pillow-heif   (Pillow needed for EXIF; pillow-heif for HEIC)
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".heif", ".webp", ".gif"}
VIDEO_EXTS = {".mov", ".mp4", ".m4v", ".avi", ".mkv", ".3gp"}
SIDECAR_EXTS = {".xmp", ".aae", ".json", ".thm", ".dop"}
EXIF_IFD, DATETIME_ORIGINAL, DATETIME = 0x8769, 0x9003, 0x0132

FILENAME_DATE = re.compile(
    r"(?<!\d)(20\d{2}|19\d{2})[-_.]?(\d{2})[-_.]?(\d{2})"
    r"(?:[-_ T.]*(?:at[ ])?(\d{2})[-_.:]?(\d{2})[-_.:]?(\d{2}))?(?!\d)"
)


# ---------------------------------------------------------------- date lookup
def exif_date(path: Path):
    if Image is None:
        return None
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            raw = exif.get_ifd(EXIF_IFD).get(DATETIME_ORIGINAL) or exif.get(DATETIME)
            if raw:
                return datetime.strptime(str(raw).strip("\x00 "), "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return None


def video_date(path: Path):
    if not shutil.which("ffprobe"):
        return None
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_entries", "format_tags=creation_time", str(path)],
            capture_output=True, text=True, timeout=15).stdout
        raw = json.loads(out)["format"]["tags"]["creation_time"]
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.astimezone().replace(tzinfo=None) if dt.tzinfo else dt
    except Exception:
        return None


def filename_date(path: Path):
    m = FILENAME_DATE.search(path.stem)
    if not m:
        return None
    y, mo, d, h, mi, s = (int(g) if g else 0 for g in m.groups())
    try:
        return datetime(y, mo, d, h, mi, s)
    except ValueError:
        return None


def taken_date(path: Path):
    """Return (datetime, source)."""
    finders = [("exif", exif_date)] if path.suffix.lower() in IMAGE_EXTS else [("video", video_date)]
    finders.append(("filename", filename_date))
    for source, fn in finders:
        dt = fn(path)
        if dt:
            return dt, source
    return datetime.fromtimestamp(path.stat().st_mtime), "mtime"


# ------------------------------------------------------------------- grouping
def build_groups(files):
    """Group files sharing dir+stem. Primary = the image (or video); the rest are companions."""
    by_key = {}
    for f in files:
        by_key.setdefault((f.parent, f.stem.lower()), []).append(f)
    groups = []
    for members in by_key.values():
        members.sort(key=lambda p: p.name)
        primary = next((m for m in members if m.suffix.lower() in IMAGE_EXTS), None) \
            or next((m for m in members if m.suffix.lower() in VIDEO_EXTS), None)
        if primary:
            groups.append((primary, members))
    groups.sort(key=lambda g: g[0])
    return groups


# ----------------------------------------------------------------- duplicates
def file_hash(path: Path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def identical(a: Path, b: Path):
    return a.stat().st_size == b.stat().st_size and file_hash(a) == file_hash(b)


# --------------------------------------------------------------------- rename
def plan_targets(members, dest_dir, stem, reserved, dedupe):
    """Find a free numeric suffix so every file in the group has a free target.
    Returns (targets, duplicate_of). `reserved` maps planned target -> source."""
    n = 0
    while True:
        name = stem if n == 0 else f"{stem}_{n}"
        targets = [dest_dir / (name + m.suffix.lower()) for m in members]
        clash = False
        for src, tgt in zip(members, targets):
            if tgt == src:
                continue
            other = reserved.get(tgt) or (tgt if tgt.exists() else None)
            if other is None:
                continue
            if other == src:
                continue
            if dedupe and src.suffix.lower() in IMAGE_EXTS | VIDEO_EXTS:
                # `other` is the original source path of a planned rename; if it has
                # already moved (apply mode) its content now lives at `tgt`.
                existing = other if other.exists() else tgt
                if identical(src, existing):
                    return None, existing
            clash = True
            break
        if not clash:
            return targets, None
        n += 1


def do_undo(log_path: Path):
    entries = json.loads(log_path.read_text())
    restored = 0
    for e in reversed(entries):
        src, dst = Path(e["from"]), Path(e["to"])
        if not dst.exists():
            print(f"skip (missing): {dst}")
        elif src.exists():
            print(f"skip (original name taken): {src}")
        else:
            src.parent.mkdir(parents=True, exist_ok=True)
            dst.rename(src)
            restored += 1
            try:
                dst.parent.rmdir()  # remove folders we created, if now empty
            except OSError:
                pass
    print(f"Restored {restored} of {len(entries)} files.")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("folder", type=Path, nargs="?")
    p.add_argument("--apply", action="store_true", help="perform the rename (default is dry run)")
    p.add_argument("-r", "--recursive", action="store_true")
    p.add_argument("--format", default="%Y-%m-%d_%H-%M-%S", help="strftime pattern for the new name")
    p.add_argument("--organize", metavar="PATTERN", help='move into subfolders by date, e.g. "%%Y/%%m"')
    p.add_argument("--dedupe", action="store_true", help="skip files byte-identical to one already at the target")
    p.add_argument("--skip-undated", action="store_true", help="don't rename files that only have a modification time")
    p.add_argument("--undo", type=Path, metavar="LOG", help="reverse a previous run using its log file")
    args = p.parse_args()

    if args.undo:
        return do_undo(args.undo)
    if not args.folder or not args.folder.is_dir():
        p.error("provide an existing folder")

    root = args.folder.resolve()
    walk = root.rglob("*") if args.recursive else root.iterdir()
    media = IMAGE_EXTS | VIDEO_EXTS | SIDECAR_EXTS
    files = [f for f in walk if f.is_file() and not f.name.startswith(".") and f.suffix.lower() in media]
    groups = build_groups(files)

    if Image is None:
        print("Note: Pillow not installed; EXIF dates unavailable (pip install Pillow).", file=sys.stderr)

    reserved, log = {}, []
    renamed = dupes = skipped = 0
    try:
        for primary, members in groups:
            dt, source = taken_date(primary)
            if source == "mtime" and args.skip_undated:
                print(f"{primary.name}: no embedded date, skipped")
                skipped += 1
                continue
            stem = dt.strftime(args.format)
            dest_dir = root / dt.strftime(args.organize) if args.organize else primary.parent

            targets, dup_of = plan_targets(members, dest_dir, stem, reserved, args.dedupe)
            if targets is None:
                print(f"{primary.name}: duplicate of {dup_of.name}, left alone")
                dupes += 1
                continue
            if all(t == m for t, m in zip(targets, members)):
                continue  # already correct

            note = {"exif": "", "video": "", "filename": "  (date from filename)",
                    "mtime": "  (no embedded date, used file date)"}[source]
            for src, tgt in zip(members, targets):
                reserved[tgt] = src
                if src == tgt:
                    continue
                print(f"{src.relative_to(root)} -> {tgt.relative_to(root)}{note}")
                note = ""
                if args.apply:
                    tgt.parent.mkdir(parents=True, exist_ok=True)
                    src.rename(tgt)
                log.append({"from": str(src), "to": str(tgt)})
            renamed += 1
    finally:
        # Written even if something fails midway, so a partial run can still be undone.
        if args.apply and log:
            log_path = root / f".rename_log_{datetime.now():%Y%m%d_%H%M%S}.json"
            log_path.write_text(json.dumps(log, indent=2))
            print(f"Undo with: {Path(sys.argv[0]).name} --undo '{log_path}'")

    verb = "Renamed" if args.apply else "Would rename"
    print(f"\n{verb} {renamed} of {len(groups)} items"
          f" ({dupes} duplicates, {skipped} skipped).")
    if not args.apply and renamed:
        print("Dry run only. Re-run with --apply to rename.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
