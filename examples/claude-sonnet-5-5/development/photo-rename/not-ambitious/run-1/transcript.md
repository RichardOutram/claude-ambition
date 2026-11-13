# dev/photo-rename · not-ambitious

### User

Write a Python script that renames my photos by the date they were taken

**→ Write** `{"file_path": "<workspace>/rename_photos.py", "content": "#!/usr/bin/env python3\n\"\"\"Rename photos to the date/time they were taken.\n\nUses EXIF DateTimeOriginal (falls back to DateTime, then file modification time).\nNew name format: YYYY-MM-DD_HH-MM-SS.ext  (duplicates get _1, _2, ...)\n\nUsage:\n    python3 rename_photos.py /path/to/photos            # dry run (preview only)\n    python3 re … [2955 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/rename_photos.py (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

I wrote the script to `<workspace>/rename_photos.py`. I haven't run it.

**How it works**
- It reads the EXIF "date taken" from each photo. If a photo has none, it uses the file's modification date and flags that in the output.
- Files are renamed to `YYYY-MM-DD_HH-MM-SS.ext`, for example `2024-07-14_15-32-08.jpg`.
- If two photos share a timestamp, the second gets `_1`, the next `_2`, and so on, so nothing is overwritten.
- It skips files that already have a date name, so running it again is safe.
- It handles jpg, jpeg, png, tif, tiff, heic and webp files.

**Usage**
```bash
pip install Pillow            # plus pillow-heif if you have HEIC files
python3 rename_photos.py ~/Pictures/trip            # preview only
python3 rename_photos.py ~/Pictures/trip --apply    # do the rename
python3 rename_photos.py ~/Pictures/trip -r --apply # include subfolders
```

By default it only prints what it would rename, so run it that way first and check the list.

Tell me if you'd prefer a different name format, such as a folder per month or the original name kept as a suffix.

### User

Push it further.

### Assistant

I'll extend it with the features that matter most for real photo libraries: video support, companion files, better date fallbacks, duplicate detection, folder organizing and an undo log. This time I'll also test it.

**→ Write** `{"file_path": "<workspace>/rename_photos.py", "content": "#!/usr/bin/env python3\n\"\"\"Rename (and optionally organize) photos and videos by the date they were taken.\n\nDate sources, in order of trust:\n  1. EXIF DateTimeOriginal / DateTime          (photos)\n  2. Container creation_time via ffprobe       (videos, if ffprobe is installed)\n  3. A timestamp in the filename               (IMG_2024 … [10004 more chars]`

<details><summary>result</summary>

```
The file <workspace>/rename_photos.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

**→ Bash** `{"command": "python3 -c \"import PIL; print(PIL.__version__)\" 2>&1; which ffprobe"}`

<details><summary>result</summary>

```
Exit code 1
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import PIL; print(PIL.__version__)
    ^^^^^^^^^^
ModuleNotFoundError: No module named 'PIL'
ffprobe not found
```

</details>

### Assistant

Pillow isn't installed, so I'll test in a throwaway virtualenv.

**→ Bash** `{"command": "cd /tmp && python3 -m venv t_venv >/dev/null 2>&1 && ./t_venv/bin/pip install -q Pillow 2>&1 | tail -2\nrm -rf /tmp/ptest && mkdir /tmp/ptest && cd /tmp/ptest\n/tmp/t_venv/bin/python - <<'EOF'\nfrom PIL import Image\nimport os, time\ndef mk(name, dt=None, color=\"red\"):\n    im = Image.new(\"RGB\",(8,8),color)\n    if dt:\n        ex = Image.Exif(); ex[0x0132]=dt\n        ifd = ex.ge … [818 more chars]`

<details><summary>result</summary>

```
[notice] A new release of pip is available: 26.2.2 -> 26.3
[notice] To update, run: /private/tmp/t_venv/bin/python3.15 -m pip install --upgrade pip
== dry
IMG_20230101_090000.png -> 2023-01-01_09-00-00.png  (date from filename)
a.jpg -> 2024-07-14_15-32-08.jpg
a.mov -> 2024-07-14_15-32-08.mov
a.xmp -> 2024-07-14_15-32-08.xmp
b.jpg -> 2024-07-14_15-32-08_1.jpg
c.jpg: duplicate of a.jpg, left alone
nodate.png -> 2026-11-13_02-12-11.png  (no embedded date, used file date)

Would rename 4 of 5 items (1 duplicates, 0 skipped).
Dry run only. Re-run with --apply to rename.
== apply
IMG_20230101_090000.png -> 2023/01/2023-01-01_09-00-00.png  (date from filename)
a.jpg -> 2024/07/2024-07-14_15-32-08.jpg
a.mov -> 2024/07/2024-07-14_15-32-08.mov
a.xmp -> 2024/07/2024-07-14_15-32-08.xmp
Traceback (most recent call last):
  File "<workspace>/rename_photos.py", line 257, in <module>
    sys.exit(main())
             ~~~~^^
  File "<workspace>/rename_photos.py", line 222, in main
    targets, dup_of = plan_targets(members, dest_dir, stem, reserved, args.dedupe)
                      ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<workspace>/rename_photos.py", line 155, in plan_targets
    if dedupe and src.suffix.lower() in IMAGE_EXTS | VIDEO_EXTS and identical(src, other):
                                                                    ~~~~~~~~~^^^^^^^^^^^^
  File "<workspace>/rename_photos.py", line 135, in identical
    return a.stat().st_size == b.stat().st_size and file_hash(a) == file_hash(b)
                               ~~~~~~^^
  File "/opt/homebrew/Cellar/<email>/3.15.2/Frameworks/Python.framework/Versions/3.15/lib/python3.15/pathlib/__init__.py", line 853, in stat
    return os.stat(self, follow_symlinks=follow_symlinks)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/ptest/a.jpg'
./2023/01/2023-01-01_09-00-00.png
./2024/07/2024-07-14_15-32-08.jpg
./2024/07/2024-07 … [335 more chars]
```

</details>

### Assistant

The test found two bugs. In apply mode, the duplicate check compared against a file that had already moved. A crash partway through also left no undo log. I'll fix both.

**→ Edit** `{"replace_all": false, "file_path": "<workspace>/rename_photos.py", "old_string": "            if dedupe and src.suffix.lower() in IMAGE_EXTS | VIDEO_EXTS and identical(src, other):\n                return None, other", "new_string": "            if dedupe and src.suffix.lower() in IMAGE_EXTS | VIDEO_EXTS:\n                # `other` is the original source path of a planned rename; if it has\n      … [223 more chars]`

<details><summary>result</summary>

```
The file <workspace>/rename_photos.py has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

**→ Read** `{"file_path": "<workspace>/rename_photos.py", "offset": 205, "limit": 60}`

<details><summary>result</summary>

```
205	
206	    root = args.folder.resolve()
207	    walk = root.rglob("*") if args.recursive else root.iterdir()
208	    media = IMAGE_EXTS | VIDEO_EXTS | SIDECAR_EXTS
209	    files = [f for f in walk if f.is_file() and not f.name.startswith(".") and f.suffix.lower() in media]
210	    groups = build_groups(files)
211	
212	    if Image is None:
213	        print("Note: Pillow not installed; EXIF dates unavailable (pip install Pillow).", file=sys.stderr)
214	
215	    reserved, log = {}, []
216	    renamed = dupes = skipped = 0
217	    for primary, members in groups:
218	        dt, source = taken_date(primary)
219	        if source == "mtime" and args.skip_undated:
220	            print(f"{primary.name}: no embedded date, skipped")
221	            skipped += 1
222	            continue
223	        stem = dt.strftime(args.format)
224	        dest_dir = root / dt.strftime(args.organize) if args.organize else primary.parent
225	
226	        targets, dup_of = plan_targets(members, dest_dir, stem, reserved, args.dedupe)
227	        if targets is None:
228	            print(f"{primary.name}: duplicate of {dup_of.name}, left alone")
229	            dupes += 1
230	            continue
231	        if all(t == m for t, m in zip(targets, members)):
232	            continue  # already correct
233	
234	        note = {"exif": "", "video": "", "filename": "  (date from filename)",
235	                "mtime": "  (no embedded date, used file date)"}[source]
236	        for src, tgt in zip(members, targets):
237	            reserved[tgt] = src
238	            if src == tgt:
239	                continue
240	            print(f"{src.relative_to(root)} -> {tgt.relative_to(root)}{note}")
241	            note = ""
242	            log.append({"from": str(src), "to": str(tgt)})
243	            if args.apply:
244	                tgt.parent.mkdir(parents=True, exist_ok=True)
245	                src.rename(tgt)
246	        renamed += 1
247	
248	    verb = "Renamed" if args.apply else "Would renam … [565 more chars]
```

</details>

**→ Bash** `{"command": "cd /tmp && python3 - <<'EOF'\np=\"<workspace>/rename_photos.py\"\ns=open(p).read()\nold_loop=s[s.index(\"    reserved, log = {}, []\"):s.index(\"    verb = \")]\nnew_loop='''    reserved, log = {}, []\n    renamed = dupes = skipped = 0\n    try:\n        for primary, members in groups:\n            dt, source = taken_date(primary)\n            if source == \"mtime\" and args.skip_unda … [2049 more chars]`

<details><summary>result</summary>

```
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
Shell cwd was reset to <workspace>
```

</details>

### Assistant

Now I'll rerun the test from a clean state, including undo and a second run to confirm it does nothing.

**→ Bash** `{"command": "cd /tmp/ptest && find . -mindepth 1 -delete\n/tmp/t_venv/bin/python - <<'EOF'\nfrom PIL import Image\ndef mk(name, dt=None, color=\"red\"):\n    im = Image.new(\"RGB\",(8,8),color)\n    if dt:\n        ex = Image.Exif(); ex[0x0132]=dt; ex.get_ifd(0x8769)[0x9003]=dt\n        im.save(name, exif=ex)\n    else: im.save(name)\nmk(\"a.jpg\",\"2024:07:14 15:32:08\"); mk(\"b.jpg\",\"2024:07:1 … [539 more chars]`

<details><summary>result</summary>

```
== apply
IMG_20230101_090000.png -> 2023/01/2023-01-01_09-00-00.png  (date from filename)
a.jpg -> 2024/07/2024-07-14_15-32-08.jpg
a.mov -> 2024/07/2024-07-14_15-32-08.mov
a.xmp -> 2024/07/2024-07-14_15-32-08.xmp
b.jpg -> 2024/07/2024-07-14_15-32-08_1.jpg
c.jpg: duplicate of 2024-07-14_15-32-08.jpg, left alone
nodate.png -> 2026/11/2026-11-13_02-12-26.png  (no embedded date, used file date)
Undo with: rename_photos.py --undo '/private/tmp/ptest/.rename_log_20261113_021226.json'

Renamed 4 of 5 items (1 duplicates, 0 skipped).
./.rename_log_20261113_021226.json
./2023/01/2023-01-01_09-00-00.png
./2024/07/2024-07-14_15-32-08_1.jpg
./2024/07/2024-07-14_15-32-08.jpg
./2024/07/2024-07-14_15-32-08.mov
./2024/07/2024-07-14_15-32-08.xmp
./2026/11/2026-11-13_02-12-26.png
./c.jpg
== rerun (expect no-op)
c.jpg: duplicate of 2024-07-14_15-32-08.jpg, left alone

Would rename 0 of 5 items (1 duplicates, 0 skipped).
== undo
Restored 6 of 6 files.
./.rename_log_20261113_021226.json
./a.jpg
./a.mov
./a.xmp
./b.jpg
./c.jpg
./IMG_20230101_090000.png
./nodate.png
Shell cwd was reset to <workspace>
```

</details>

### Assistant

I extended `rename_photos.py` (in `<workspace>/`) and tested it on a small set of sample files. The test covered rename, duplicate detection, folder organizing, a second run and undo, and all of it worked.

**New features**
- **Video support:** it handles `.mov`, `.mp4`, `.m4v`, `.avi`, `.mkv` and `.3gp`. It reads the creation date with `ffprobe` if that's installed.
- **Companion files stay paired:** `IMG_0001.jpg`, `IMG_0001.xmp`, `IMG_0001.aae` and a Live Photo `IMG_0001.mov` all get the same new name.
- **Better date fallbacks:** it tries EXIF first, then video metadata, then a date in the filename (`IMG_20230101_090000.png`, `Screenshot 2024-07-14 at 15.32.08.png`), and only then the file modification time. Files that fall back to the modification time are flagged. `--skip-undated` leaves them alone.
- **Custom names and folders:** `--format "%Y%m%d_%H%M%S"` changes the name pattern, and `--organize "%Y/%m"` also moves files into `2024/07/` style folders.
- **Duplicate detection:** with `--dedupe`, a file that is byte-identical to one already at the target is reported and left alone. Nothing is deleted. Files that share a timestamp but have different content get `_1`, `_2` and so on.
- **Undo:** every `--apply` run writes a `.rename_log_*.json` file. `--undo <log>` reverses the run and removes any folders it created that are now empty. The log is written even if a run fails partway.

**Bugs the test caught and I fixed**
- The duplicate check compared against a file that had already moved, which crashed `--apply --dedupe`.
- A crash left no undo log, which is why the log is now written even on failure.

**Not tested**
- `ffprobe` isn't installed here, so the video-date lookup hasn't been run. My test `.mov` was a placeholder file. Without `ffprobe`, videos fall back to the filename date and then the modification time.
- HEIC needs `pillow-heif`, which I didn't try.

If you want to go further, I could add a progress bar for large libraries and a setting to copy files instead of moving them. I could also have it read the camera's time zone, so photos taken abroad get local time.
