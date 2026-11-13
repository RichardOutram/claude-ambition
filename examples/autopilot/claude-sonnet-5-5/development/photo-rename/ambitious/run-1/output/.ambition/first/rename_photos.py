#!/usr/bin/env python3
"""Rename photos by the date they were taken.

Uses EXIF DateTimeOriginal when available (needs Pillow), otherwise falls
back to the file's modification time. Dry-run by default.

Usage:
    python3 rename_photos.py /path/to/photos            # preview
    python3 rename_photos.py /path/to/photos --apply    # rename for real
    python3 rename_photos.py /path/to/photos -r --format "%Y-%m-%d_%H%M%S"
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".webp"}
EXIF_IFD = 0x8769
DATETIME_ORIGINAL = 0x9003
DATETIME_DIGITIZED = 0x9004
DATETIME = 0x0132


def exif_date(path):
    if Image is None:
        return None
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            candidates = []
            try:
                ifd = exif.get_ifd(EXIF_IFD)
                candidates += [ifd.get(DATETIME_ORIGINAL), ifd.get(DATETIME_DIGITIZED)]
            except Exception:
                pass
            candidates.append(exif.get(DATETIME))
            for value in candidates:
                if value:
                    try:
                        return datetime.strptime(str(value).strip(), "%Y:%m:%d %H:%M:%S")
                    except ValueError:
                        continue
    except Exception:
        pass
    return None


def taken_date(path):
    return exif_date(path) or datetime.fromtimestamp(path.stat().st_mtime)


def unique_target(path, new_stem, taken):
    target = path.with_name(new_stem + path.suffix.lower())
    n = 1
    while (target.exists() and target != path) or target in taken:
        target = path.with_name(f"{new_stem}_{n}{path.suffix.lower()}")
        n += 1
    return target


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path)
    ap.add_argument("--apply", action="store_true", help="actually rename (default is preview only)")
    ap.add_argument("-r", "--recursive", action="store_true")
    ap.add_argument("--format", default="%Y-%m-%d_%H-%M-%S", help="strftime format for new name")
    args = ap.parse_args()

    if not args.folder.is_dir():
        sys.exit(f"Not a directory: {args.folder}")
    if Image is None:
        print("Note: Pillow not installed (pip install Pillow); using file modified time.\n")

    it = args.folder.rglob("*") if args.recursive else args.folder.iterdir()
    files = sorted(p for p in it if p.is_file() and p.suffix.lower() in EXTS and not p.name.startswith("."))

    taken, count = set(), 0
    for p in files:
        target = unique_target(p, taken_date(p).strftime(args.format), taken)
        if target == p:
            continue
        taken.add(target)
        print(f"{p.name} -> {target.name}")
        if args.apply:
            p.rename(target)
        count += 1

    verb = "Renamed" if args.apply else "Would rename"
    print(f"\n{verb} {count} of {len(files)} photos." + ("" if args.apply else " Re-run with --apply to do it."))


if __name__ == "__main__":
    main()
