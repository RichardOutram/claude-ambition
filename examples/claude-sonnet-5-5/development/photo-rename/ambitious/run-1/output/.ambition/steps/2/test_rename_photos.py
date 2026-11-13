"""Synthetic tests for rename_photos.py.  Run:  .venv/bin/python -m unittest -v test_rename_photos"""
import contextlib
import hashlib
import io
import os
import tempfile
import unittest
from pathlib import Path

from PIL import Image

import rename_photos as rp

try:
    import pillow_heif  # noqa: F401
    HEIF = True
except Exception:
    HEIF = False


def make_photo(path, taken=None, color=(10, 20, 30), fmt=None, mtime=None):
    """Write a tiny image, optionally with an EXIF DateTimeOriginal ('YYYY:MM:DD HH:MM:SS')."""
    img = Image.new("RGB", (8, 8), color)
    exif = Image.Exif()
    if taken:
        exif.get_ifd(rp.EXIF_IFD)[0x9003] = taken
    img.save(path, format=fmt, exif=exif) if taken else img.save(path, format=fmt)
    if mtime:
        os.utime(path, (mtime, mtime))
    return Path(path)


def snapshot(folder, skip_logs=True):
    """relative path -> (sha256, mtime_ns) for every file."""
    out = {}
    for p in sorted(Path(folder).rglob("*")):
        if p.is_file() and not (skip_logs and rp.LOG_DIR in p.parts):
            out[str(p.relative_to(folder))] = (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
    return out


def run(*args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = rp.main([str(a) for a in args])
    return code, buf.getvalue()


def names(folder):
    return sorted(p.name for p in Path(folder).iterdir() if p.is_file())


class T(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.d = Path(self._t.name)

    def tearDown(self):
        self._t.cleanup()

    def test_dry_run_changes_nothing(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        before = snapshot(self.d, False)
        run(self.d)
        self.assertEqual(before, snapshot(self.d, False))
        self.assertFalse((self.d / rp.LOG_DIR).exists())

    def test_exif_date_used(self):
        make_photo(self.d / "IMG_1.JPG", "2021:05:04 10:11:12")
        run(self.d, "--apply")
        self.assertEqual(names(self.d), ["2021-05-04_10-11-12.jpg"])

    def test_missing_date_falls_back_to_mtime_and_is_flagged(self):
        make_photo(self.d / "x.jpg", mtime=1_600_000_000)
        run(self.d, "--apply")
        expected = rp.datetime.fromtimestamp(1_600_000_000).strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
        self.assertEqual(names(self.d), [expected])
        report = next((self.d / rp.LOG_DIR).glob("*.report.txt")).read_text()
        flagged = report.split("== FLAGGED")[1].split("== DUPLICATES")[0]
        self.assertIn(expected, flagged)
        self.assertIn("no EXIF date", flagged)

    def test_implausible_date_is_flagged_not_trusted(self):
        make_photo(self.d / "x.jpg", "1970:01:01 00:00:00", mtime=1_600_000_000)
        run(self.d, "--apply")
        self.assertNotIn("1970", names(self.d)[0])
        report = next((self.d / rp.LOG_DIR).glob("*.report.txt")).read_text()
        self.assertIn("looks wrong", report)

    def test_unreadable_file_is_flagged_and_still_renamed_safely(self):
        (self.d / "broken.jpg").write_bytes(b"not an image")
        os.utime(self.d / "broken.jpg", (1_600_000_000, 1_600_000_000))
        run(self.d, "--apply")
        report = next((self.d / rp.LOG_DIR).glob("*.report.txt")).read_text()
        self.assertIn("could not read image", report)

    def test_rerun_is_a_noop(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12", color=(1, 1, 1))
        make_photo(self.d / "b.jpg", "2021:05:04 10:11:12", color=(2, 2, 2))
        make_photo(self.d / "c.jpg", mtime=1_600_000_000)
        run(self.d, "--apply")
        after_first = snapshot(self.d)
        code, out = run(self.d, "--apply")
        self.assertEqual(after_first, snapshot(self.d))
        self.assertIn("Nothing to rename", out)
        self.assertEqual(len(list((self.d / rp.LOG_DIR).glob("run-*.jsonl"))), 1)  # no-op run left no log

    def test_undo_after_noop_rerun_still_undoes_the_real_run(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        before = snapshot(self.d, False)
        run(self.d, "--apply")
        run(self.d, "--apply")  # no-op
        run(self.d, "--undo", "--apply")
        self.assertEqual(before, {k: v for k, v in snapshot(self.d, False).items() if rp.LOG_DIR not in k})

    def test_same_second_different_photos_get_stable_suffixes(self):
        for name, c in (("b.jpg", (2, 2, 2)), ("a.jpg", (1, 1, 1)), ("c.jpg", (3, 3, 3))):
            make_photo(self.d / name, "2021:05:04 10:11:12", color=c)
        a_bytes = (self.d / "a.jpg").read_bytes()
        run(self.d, "--apply")
        self.assertEqual(names(self.d), ["2021-05-04_10-11-12.jpg", "2021-05-04_10-11-12_1.jpg",
                                         "2021-05-04_10-11-12_2.jpg"])
        # ordered by original filename: a -> base, b -> _1, c -> _2
        self.assertEqual((self.d / "2021-05-04_10-11-12.jpg").read_bytes(), a_bytes)

    def test_exact_duplicate_not_renamed_not_deleted(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        (self.d / "copy.jpg").write_bytes((self.d / "a.jpg").read_bytes())
        run(self.d, "--apply")
        self.assertEqual(names(self.d), ["2021-05-04_10-11-12.jpg", "copy.jpg"])
        report = next((self.d / rp.LOG_DIR).glob("*.report.txt")).read_text()
        self.assertIn("copy.jpg is identical to 2021-05-04_10-11-12.jpg", report)

    def test_duplicate_of_photo_renamed_in_an_earlier_run(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        run(self.d, "--apply")
        (self.d / "again.jpg").write_bytes((self.d / "2021-05-04_10-11-12.jpg").read_bytes())
        run(self.d, "--apply")
        self.assertEqual(names(self.d), ["2021-05-04_10-11-12.jpg", "again.jpg"])

    def test_new_batch_colliding_with_earlier_run_never_touches_existing(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12", color=(1, 1, 1))
        run(self.d, "--apply")
        existing = (self.d / "2021-05-04_10-11-12.jpg").read_bytes()
        make_photo(self.d / "new.jpg", "2021:05:04 10:11:12", color=(9, 9, 9))
        run(self.d, "--apply")
        self.assertEqual(names(self.d), ["2021-05-04_10-11-12.jpg", "2021-05-04_10-11-12_1.jpg"])
        self.assertEqual((self.d / "2021-05-04_10-11-12.jpg").read_bytes(), existing)

    def test_never_clobbers_unrelated_file_at_target_name(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        blocker = self.d / "2021-05-04_10-11-12.jpg"
        blocker.write_bytes(b"precious, different content")
        run(self.d, "--apply")
        self.assertEqual(blocker.read_bytes(), b"precious, different content")
        self.assertIn("2021-05-04_10-11-12_1.jpg", names(self.d))

    def test_undo_restores_everything_byte_for_byte(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12", color=(1, 1, 1), mtime=1_500_000_000)
        make_photo(self.d / "b.jpg", "2021:05:04 10:11:12", color=(2, 2, 2), mtime=1_500_000_001)
        make_photo(self.d / "c.jpg", mtime=1_600_000_000)
        (self.d / "dup.jpg").write_bytes((self.d / "a.jpg").read_bytes())
        (self.d / "notes.txt").write_text("not a photo")
        before = snapshot(self.d, False)
        run(self.d, "--apply")
        self.assertNotEqual(before.keys(), snapshot(self.d).keys())
        code, _ = run(self.d, "--undo", "--apply")
        self.assertEqual(code, 0)
        self.assertEqual(before, snapshot(self.d))  # names, contents AND mtimes

    def test_undo_only_reverses_latest_run_and_is_repeatable_safe(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        run(self.d, "--apply")
        make_photo(self.d / "b.jpg", "2022:01:01 01:01:01")
        run(self.d, "--apply")
        run(self.d, "--undo", "--apply")
        self.assertEqual(names(self.d), ["2021-05-04_10-11-12.jpg", "b.jpg"])
        run(self.d, "--undo", "--apply")  # second undo targets the first run
        self.assertEqual(names(self.d), ["a.jpg", "b.jpg"])
        code, _ = run(self.d, "--undo", "--apply")  # nothing left
        self.assertEqual(code, 1)

    def test_undo_refuses_to_overwrite(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        run(self.d, "--apply")
        (self.d / "a.jpg").write_bytes(b"new file that appeared at the old name")
        code, out = run(self.d, "--undo", "--apply")
        self.assertEqual(code, 1)
        self.assertEqual((self.d / "a.jpg").read_bytes(), b"new file that appeared at the old name")
        self.assertTrue((self.d / "2021-05-04_10-11-12.jpg").exists())

    def test_undo_preview_changes_nothing(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        run(self.d, "--apply")
        before = snapshot(self.d, False)
        run(self.d, "--undo")
        self.assertEqual(before, snapshot(self.d, False))

    def test_recursive_and_non_recursive(self):
        (self.d / "sub").mkdir()
        make_photo(self.d / "sub" / "a.jpg", "2021:05:04 10:11:12")
        run(self.d, "--apply")
        self.assertTrue((self.d / "sub" / "a.jpg").exists())
        run(self.d, "-r", "--apply")
        self.assertTrue((self.d / "sub" / "2021-05-04_10-11-12.jpg").exists())
        run(self.d, "-r", "--undo", "--apply")
        self.assertTrue((self.d / "sub" / "a.jpg").exists())

    def test_log_folder_and_hidden_files_are_ignored(self):
        make_photo(self.d / ".hidden.jpg", "2021:05:04 10:11:12")
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        run(self.d, "--apply")
        run(self.d, "-r", "--apply")
        self.assertTrue((self.d / ".hidden.jpg").exists())

    @unittest.skipUnless(HEIF, "pillow-heif not installed")
    def test_heic_exif_date(self):
        img = Image.new("RGB", (16, 16), (5, 5, 5))
        exif = Image.Exif()
        exif.get_ifd(rp.EXIF_IFD)[0x9003] = "2019:12:31 23:59:58"
        try:
            img.save(self.d / "IMG_0001.HEIC", format="HEIF", exif=exif)
        except Exception as e:
            self.skipTest(f"cannot write HEIC here: {e}")
        run(self.d, "--apply")
        self.assertEqual(names(self.d), ["2019-12-31_23-59-58.heic"])


if __name__ == "__main__":
    unittest.main()
