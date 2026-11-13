# Photo renamer

`rename_photos.py` renames photos to `YYYY-MM-DD_HH-MM-SS.ext` by the date taken. Safe to re-run on the same folder; every run that renames something can be undone. Read its `--help` before changing behaviour.

## Run
    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt     # once; system python3 has no Pillow
    .venv/bin/python rename_photos.py FOLDER            # preview only
    .venv/bin/python rename_photos.py FOLDER --apply    # rename; writes FOLDER/_rename_logs/
    .venv/bin/python rename_photos.py FOLDER --undo --apply

## What proves it
- `.venv/bin/python -m unittest test_rename_photos` (54 tests, 3 s)
- `.venv/bin/python acceptance_check.py` (20 checks, ~3 min): runs the script as a user would, uses real macOS photos, and kills it with `kill -9` mid-run. Run both before shipping any change to `rename_photos.py`.

## Rules for changes
- Never overwrite or delete a photo; log each rename to disk before doing it; keep undo exact (names, bytes, modified times).
- A test that cannot fail proves nothing: after changing safety code, break it on purpose and confirm a test fails.
- Not yet run on the owner's real photos (`sample_photos/` was never provided).
