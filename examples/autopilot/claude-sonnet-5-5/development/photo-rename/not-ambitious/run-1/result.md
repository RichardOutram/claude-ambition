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