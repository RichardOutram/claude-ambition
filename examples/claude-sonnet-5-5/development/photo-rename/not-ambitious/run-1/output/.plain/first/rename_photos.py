#!/usr/bin/env python3
"""Rename photos to the date/time they were taken.

Uses EXIF DateTimeOriginal (falls back to DateTime, then file modification time).
New name format: YYYY-MM-DD_HH-MM-SS.ext  (duplicates get _1, _2, ...)

Usage:
    python3 rename_photos.py /path/to/photos            # dry run (preview only)
    python3 rename_photos.py /path/to/photos --apply    # actually rename
    python3 rename_photos.py /path/to/photos -r --apply # include subfolders

Requires: pip install Pillow
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".webp"}
EXIF_IFD = 0x8769
DATETIME_ORIGINAL = 0x9003
DATETIME = 0x0132


def taken_date(path: Path) -> tuple[datetime, str]:
    """Return (datetime, source) where source is 'exif' or 'mtime'."""
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            raw = exif.get_ifd(EXIF_IFD).get(DATETIME_ORIGINAL) or exif.get(DATETIME)
            if raw:
                return datetime.strptime(str(raw).strip("\x00 "), "%Y:%m:%d %H:%M:%S"), "exif"
    except Exception:
        pass
    return datetime.fromtimestamp(path.stat().st_mtime), "mtime"


def unique_target(path: Path, stem: str, reserved: set[Path]) -> Path:
    ext = path.suffix.lower()
    target = path.with_name(stem + ext)
    n = 0
    while (target.exists() and target != path) or target in reserved:
        n += 1
        target = path.with_name(f"{stem}_{n}{ext}")
    return target


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("folder", type=Path)
    p.add_argument("--apply", action="store_true", help="perform the rename (default is dry run)")
    p.add_argument("-r", "--recursive", action="store_true", help="include subfolders")
    args = p.parse_args()

    if not args.folder.is_dir():
        print(f"Not a folder: {args.folder}", file=sys.stderr)
        return 1

    files = args.folder.rglob("*") if args.recursive else args.folder.iterdir()
    photos = sorted(f for f in files if f.is_file() and f.suffix.lower() in EXTS)

    reserved: set[Path] = set()
    renamed = 0
    for f in photos:
        dt, source = taken_date(f)
        stem = dt.strftime("%Y-%m-%d_%H-%M-%S")
        if f.stem == stem or f.stem.startswith(stem + "_"):
            continue  # already named
        target = unique_target(f, stem, reserved)
        reserved.add(target)
        note = "" if source == "exif" else "  (no EXIF, used file date)"
        print(f"{f.name} -> {target.name}{note}")
        if args.apply:
            f.rename(target)
        renamed += 1

    verb = "Renamed" if args.apply else "Would rename"
    print(f"\n{verb} {renamed} of {len(photos)} photos.")
    if not args.apply and renamed:
        print("Dry run only. Re-run with --apply to rename.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
