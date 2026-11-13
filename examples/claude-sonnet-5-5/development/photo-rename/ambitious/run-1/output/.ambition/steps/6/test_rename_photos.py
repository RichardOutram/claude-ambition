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


def make_photo(path, taken=None, color=(10, 20, 30), fmt=None, mtime=None, subsec=None, tag=0x9003):
    """Write a tiny image, optionally with an EXIF date ('YYYY:MM:DD HH:MM:SS') in the given tag."""
    img = Image.new("RGB", (8, 8), color)
    exif = Image.Exif()
    if taken:
        if tag == 0x0132:
            exif[0x0132] = taken
        else:
            exif.get_ifd(rp.EXIF_IFD)[tag] = taken
        if subsec is not None:
            exif.get_ifd(rp.EXIF_IFD)[0x9291] = str(subsec)
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


class Depth(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.d = Path(self._t.name)

    def tearDown(self):
        self._t.cleanup()

    def report(self):
        return sorted((self.d / rp.LOG_DIR).glob("*.report.txt"))[-1].read_text()

    # ---- companions
    def test_live_photo_and_sidecars_travel_with_the_photo(self):
        make_photo(self.d / "IMG_0001.HEIC.jpg".replace(".HEIC", ""), "2021:05:04 10:11:12")
        (self.d / "IMG_0001.MOV").write_bytes(b"movie")
        (self.d / "IMG_0001.AAE").write_bytes(b"edits")
        (self.d / "IMG_0002.MOV").write_bytes(b"orphan video, no photo")
        run(self.d, "--apply")
        self.assertEqual(names(self.d), ["2021-05-04_10-11-12.aae", "2021-05-04_10-11-12.jpg",
                                         "2021-05-04_10-11-12.mov", "IMG_0002.MOV"])
        run(self.d, "--undo", "--apply")
        self.assertEqual(names(self.d), ["IMG_0001.AAE", "IMG_0001.MOV", "IMG_0001.jpg", "IMG_0002.MOV"])

    def test_raw_jpg_pair_stays_matched_when_second_pair_collides(self):
        for stem, c in (("A", (1, 1, 1)), ("B", (2, 2, 2))):
            make_photo(self.d / f"{stem}.JPG", "2021:05:04 10:11:12", color=c)
            (self.d / f"{stem}.CR2").write_bytes(b"raw " + stem.encode())
        run(self.d, "--apply")
        self.assertEqual(names(self.d), ["2021-05-04_10-11-12.cr2", "2021-05-04_10-11-12.jpg",
                                         "2021-05-04_10-11-12_1.cr2", "2021-05-04_10-11-12_1.jpg"])
        self.assertEqual((self.d / "2021-05-04_10-11-12_1.cr2").read_bytes(), b"raw B")  # B's raw stays with B's jpg

    def test_companion_name_taken_bumps_the_whole_group(self):
        make_photo(self.d / "A.JPG", "2021:05:04 10:11:12")
        (self.d / "A.MOV").write_bytes(b"movie")
        (self.d / "2021-05-04_10-11-12.mov").write_bytes(b"someone else's movie")
        run(self.d, "--apply")
        self.assertEqual((self.d / "2021-05-04_10-11-12.mov").read_bytes(), b"someone else's movie")
        self.assertEqual((self.d / "2021-05-04_10-11-12_1.mov").read_bytes(), b"movie")
        self.assertTrue((self.d / "2021-05-04_10-11-12_1.jpg").exists())  # photo and movie share a suffix

    # ---- dates
    def test_burst_is_ordered_by_subsecond_not_by_filename(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12", color=(1, 1, 1), subsec=900)
        make_photo(self.d / "b.jpg", "2021:05:04 10:11:12", color=(2, 2, 2), subsec=100)
        b = (self.d / "b.jpg").read_bytes()
        run(self.d, "--apply")
        self.assertEqual((self.d / "2021-05-04_10-11-12.jpg").read_bytes(), b)  # b was shot first

    def test_only_file_changed_tag_is_used_but_flagged(self):
        make_photo(self.d / "x.jpg", "2020:07:16 10:47:47", tag=0x0132)
        run(self.d, "--apply")
        self.assertEqual(names(self.d), ["2020-07-16_10-47-47.jpg"])
        self.assertIn("file changed", self.report())

    def test_original_date_beats_a_later_edit_date(self):
        img = Image.new("RGB", (8, 8))
        exif = Image.Exif()
        exif.get_ifd(rp.EXIF_IFD)[0x9003] = "2019:11:06 20:33:19"
        exif[0x0132] = "2020:07:16 10:47:47"
        img.save(self.d / "x.jpg", exif=exif)
        run(self.d, "--apply")
        self.assertEqual(names(self.d), ["2019-11-06_20-33-19.jpg"])
        self.assertNotIn("FLAGGED: please check these dates ==\n  x", self.report())

    def test_malformed_exif_date_is_named_as_such(self):
        make_photo(self.d / "x.jpg", "2019:05:20 14:05:92", mtime=1_600_000_000)
        run(self.d, "--apply")
        self.assertIn("malformed", self.report())

    def test_undo_finishes_a_rename_cut_off_half_way(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        before = snapshot(self.d, False)
        run(self.d, "--apply")
        os.link(self.d / "2021-05-04_10-11-12.jpg", self.d / "a.jpg")  # both names, one file
        code, _ = run(self.d, "--undo", "--apply")
        self.assertEqual(code, 0)
        self.assertEqual(names(self.d), ["a.jpg"])
        clean = {k: v for k, v in snapshot(self.d, False).items() if rp.LOG_DIR not in k}
        self.assertEqual(before, clean)

    def test_report_calls_out_two_names_for_one_file(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        os.link(self.d / "a.jpg", self.d / "2021-05-04_10-11-12.jpg")
        make_photo(self.d / "z.jpg", "2022:01:01 01:01:01")
        run(self.d, "--apply")
        self.assertIn("SAME file", self.report())
        self.assertTrue((self.d / "a.jpg").exists() and (self.d / "2021-05-04_10-11-12.jpg").exists())

    def test_lying_directory_listing_cannot_cause_an_overwrite(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        blocker = self.d / "2021-05-04_10-11-12.jpg"
        blocker.write_bytes(b"exists, but the listing does not show it")
        real = os.listdir
        rp.os.listdir = lambda p: [n for n in real(p) if not n.startswith("2021")]
        try:
            run(self.d, "--apply")
        finally:
            rp.os.listdir = real
        self.assertEqual(blocker.read_bytes(), b"exists, but the listing does not show it")
        self.assertTrue((self.d / "2021-05-04_10-11-12_1.jpg").exists())

    # ---- found by challenging the assumptions
    def test_refuses_without_pillow_instead_of_naming_everything_by_mtime(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        saved, rp.Image = rp.Image, None
        try:
            code, out = run(self.d, "--apply")
            self.assertEqual(code, 2)
            self.assertIn("Nothing was changed", out)
            self.assertEqual(names(self.d), ["a.jpg"])
            code, _ = run(self.d, "--apply", "--allow-mtime")  # explicit opt-in still works
            self.assertEqual(code, 0)
        finally:
            rp.Image = saved
        self.assertNotEqual(names(self.d), ["a.jpg"])

    def test_refuses_heic_without_pillow_heif(self):
        (self.d / "IMG_1.HEIC").write_bytes(b"heic bytes")
        saved, rp.HEIF_OK = rp.HEIF_OK, False
        try:
            code, out = run(self.d, "--apply")
        finally:
            rp.HEIF_OK = saved
        self.assertEqual(code, 2)
        self.assertIn("pillow-heif", out)
        self.assertEqual(names(self.d), ["IMG_1.HEIC"])

    def test_never_enters_photo_library_packages(self):
        lib = self.d / "Photos Library.photoslibrary" / "originals"
        lib.mkdir(parents=True)
        make_photo(lib / "ABCD.jpg", "2021:05:04 10:11:12")
        before = snapshot(self.d, False)
        run(self.d, "-r", "--apply")
        self.assertEqual(before, snapshot(self.d, False))
        code, out = run(self.d / "Photos Library.photoslibrary", "-r", "--apply")
        self.assertEqual(code, 2)
        self.assertEqual(before, snapshot(self.d, False))

    def test_huge_panorama_keeps_its_exif_date(self):
        exif = Image.Exif()
        exif.get_ifd(rp.EXIF_IFD)[0x9003] = "2018:08:09 07:06:05"
        Image.new("L", (14000, 13000), 128).save(self.d / "pano.jpg", exif=exif, quality=50)  # 182 Mpx
        run(self.d, "--apply")
        self.assertEqual(names(self.d), ["2018-08-09_07-06-05.jpg"])

    def test_same_file_imported_twice_without_exif_is_a_duplicate(self):
        make_photo(self.d / "wa.jpg", color=(9, 9, 9), mtime=1_600_000_000)
        run(self.d, "--apply")
        first = names(self.d)
        (self.d / "wa_again.jpg").write_bytes((self.d / first[0]).read_bytes())
        os.utime(self.d / "wa_again.jpg", (1_605_000_000, 1_605_000_000))  # copied a week later
        run(self.d, "--apply")
        self.assertEqual(names(self.d), sorted(first + ["wa_again.jpg"]))
        self.assertIn("wa_again.jpg is identical to", self.report())

    def test_repeated_duplicate_only_runs_keep_a_single_report(self):
        make_photo(self.d / "wa.jpg", color=(9, 9, 9), mtime=1_600_000_000)
        run(self.d, "--apply")
        (self.d / "again.jpg").write_bytes((next(self.d.glob("2020*"))).read_bytes())
        for _ in range(4):
            run(self.d, "--apply")
        reports = list((self.d / rp.LOG_DIR).glob("*.report.txt"))
        self.assertEqual(len(reports), 2)  # the real run's report + one duplicates-only report
        self.assertIn("again.jpg", self.report())
        self.assertEqual(len(list((self.d / rp.LOG_DIR).glob("run-*.jsonl"))), 1)

    def test_identical_new_files_in_one_run_keep_exactly_one_renamed(self):
        make_photo(self.d / "a.jpg", color=(9, 9, 9), mtime=1_600_000_000)
        (self.d / "b.jpg").write_bytes((self.d / "a.jpg").read_bytes())
        os.utime(self.d / "b.jpg", (1_605_000_000, 1_605_000_000))
        run(self.d, "--apply")
        left = names(self.d)
        self.assertEqual(sum(n.startswith("2020") for n in left), 1)  # one renamed, one left as a duplicate
        self.assertEqual(len(left), 2)

    def test_clock_reset_signature_is_flagged_but_date_is_kept(self):
        make_photo(self.d / "x.jpg", "2000:01:01 00:00:03")
        run(self.d, "--apply")
        self.assertEqual(names(self.d), ["2000-01-01_00-00-03.jpg"])
        self.assertIn("clock reset", self.report())

    # ---- red team
    def test_tampered_log_cannot_move_files_outside_the_folder(self):
        moved_name = f"moved_{os.getpid()}_{id(self)}.txt"
        outside = Path(tempfile.mkdtemp())
        victim = outside / "victim.txt"
        victim.write_text("precious")
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        run(self.d, "--apply")
        log = next((self.d / rp.LOG_DIR).glob("run-*.jsonl"))
        for old, new in ((f"../{moved_name}", str(victim)), ("ok.jpg", "../victim.txt"), (str(victim), "x.jpg")):
            log.write_text('{"type":"run"}\n' + rp.json.dumps({"old": old, "new": new}) + "\n")
            code, out = run(self.d, "--undo", "--apply")
            self.assertEqual(code, 2, out)
            self.assertEqual(victim.read_text(), "precious")
        self.assertFalse((self.d.parent / moved_name).exists())

    def test_garbage_log_is_refused_cleanly(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        run(self.d, "--apply")
        next((self.d / rp.LOG_DIR).glob("run-*.jsonl")).write_text("{not json")
        code, out = run(self.d, "--undo", "--apply")
        self.assertEqual(code, 2)
        self.assertIn("not a valid run log", out)

    def test_symlinked_folder_pointing_outside_is_not_followed(self):
        outside = Path(tempfile.mkdtemp())
        make_photo(outside / "secret.jpg", "2020:01:01 12:00:00")
        (self.d / "link").symlink_to(outside, target_is_directory=True)
        run(self.d, "-r", "--apply")
        self.assertEqual(names(outside), ["secret.jpg"])

    def test_undo_refuses_to_restore_a_replaced_file_unless_forced(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        run(self.d, "--apply")
        new = self.d / "2021-05-04_10-11-12.jpg"
        new.unlink()
        new.write_bytes(b"an impostor with a different identity")
        code, out = run(self.d, "--undo", "--apply")
        self.assertEqual(code, 1)
        self.assertIn("not the file that was renamed", out)
        self.assertEqual(names(self.d), ["2021-05-04_10-11-12.jpg"])
        code, _ = run(self.d, "--undo", "--apply", "--force")
        self.assertEqual(code, 0)
        self.assertEqual(names(self.d), ["a.jpg"])

    def test_undo_restores_a_file_that_is_unchanged_even_after_a_noop_run(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12", mtime=1_500_000_000)
        run(self.d, "--apply")
        run(self.d, "--apply")
        code, _ = run(self.d, "--undo", "--apply")
        self.assertEqual(code, 0)

    def test_read_only_folder_gives_a_clean_message_not_a_traceback(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        os.chmod(self.d, 0o555)
        try:
            code, out = run(self.d, "--apply")
        finally:
            os.chmod(self.d, 0o755)
        self.assertEqual(code, 2)
        self.assertIn("Nothing was changed", out)
        self.assertEqual(names(self.d), ["a.jpg"])

    def test_live_lock_blocks_a_second_run_and_stale_lock_is_cleared(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        lock = self.d / ".rename_photos.lock"
        lock.write_text(str(os.getpid()))  # this very process is alive
        code, out = run(self.d, "--apply")
        self.assertEqual(code, 2)
        self.assertIn("Another run", out)
        self.assertEqual([n for n in names(self.d) if not n.startswith(".")], ["a.jpg"])
        lock.write_text("999999999")  # no such process: a leftover from a crash
        code, _ = run(self.d, "--apply")
        self.assertEqual(code, 0)
        self.assertFalse(lock.exists())  # and it is released afterwards

    def test_safe_rename_never_replaces_an_existing_file(self):
        (self.d / "a").write_text("A")
        (self.d / "b").write_text("B")
        with self.assertRaises(FileExistsError):
            rp.safe_rename(self.d / "a", self.d / "b")
        self.assertEqual((self.d / "b").read_text(), "B")
        self.assertEqual((self.d / "a").read_text(), "A")

    def test_name_taken_at_the_last_instant_is_skipped_not_overwritten(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        real = rp.safe_rename

        def sneaky(src, dst):  # someone else creates the target between planning and renaming
            Path(dst).write_bytes(b"someone else's file")
            real(src, dst)
        rp.safe_rename = sneaky
        try:
            code, out = run(self.d, "--apply")
        finally:
            rp.safe_rename = real
        self.assertEqual((self.d / "2021-05-04_10-11-12.jpg").read_bytes(), b"someone else's file")
        self.assertTrue((self.d / "a.jpg").exists())
        self.assertIn("target appeared", next((self.d / rp.LOG_DIR).glob("*.report.txt")).read_text())
        code, out = run(self.d, "--undo", "--apply")  # the never-moved entry must not poison undo
        self.assertEqual(code, 0, out)

    def test_refuses_recursive_search_of_home_and_root(self):
        for target in (Path.home(), Path("/")):
            code, out = run(target, "-r")
            self.assertEqual(code, 2)
            self.assertIn("too broad", out)

    def test_report_says_where_each_date_came_from(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12")
        make_photo(self.d / "b.jpg", mtime=1_600_000_000)
        (self.d / "a.MOV").write_bytes(b"m")
        run(self.d, "--apply")
        r = self.report()
        self.assertIn("[EXIF taken]", r)
        self.assertIn("[file modified time]", r)
        self.assertIn("[travels with a.jpg]", r)

    # ---- crash safety: kill the run at every possible point, then undo
    def _crash_at(self, k, after):
        class Crash(BaseException):
            pass
        real, calls = rp.safe_rename, [0]

        def rename(a, b):
            calls[0] += 1
            if calls[0] == k and not after:
                raise Crash()
            real(a, b)
            if calls[0] == k and after:
                raise Crash()
        rp.safe_rename = rename
        try:
            run(self.d, "--apply")
        except Crash:
            pass
        finally:
            rp.safe_rename = real

    def test_crash_at_every_point_is_fully_recoverable(self):
        make_photo(self.d / "a.jpg", "2021:05:04 10:11:12", color=(1, 1, 1), mtime=1_500_000_000)
        make_photo(self.d / "b.jpg", "2021:05:04 10:11:12", color=(2, 2, 2), mtime=1_500_000_001)
        make_photo(self.d / "c.jpg", mtime=1_600_000_000)
        (self.d / "a.mov").write_bytes(b"m")
        before = snapshot(self.d, False)
        total = 4
        for k in range(1, total + 1):
            for after in (False, True):
                with self.subTest(k=k, after=after):
                    self._crash_at(k, after)
                    code, _ = run(self.d, "--undo", "--apply")
                    self.assertEqual(code, 0)
                    clean = {a: b for a, b in snapshot(self.d, False).items() if rp.LOG_DIR not in a}
                    self.assertEqual(before, clean)
                    for f in (self.d / rp.LOG_DIR).glob("*"):
                        f.unlink()


class Fuzz(unittest.TestCase):
    """Random add / apply / re-apply / undo sequences; invariants are checked after every step."""

    def one_scenario(self, seed):
        import random
        rnd = random.Random(seed)
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            counter = 0
            for _ in range(rnd.randint(2, 5)):
                existing = [p for p in d.iterdir() if p.is_file() and p.suffix == ".jpg"]
                for _ in range(rnd.randint(0, 6)):
                    counter += 1
                    kind = rnd.choice(["exif", "exif", "noexif", "dup", "mov"])
                    stamp = f"2021:05:0{rnd.randint(1, 2)} 10:00:0{rnd.randint(0, 2)}"
                    name = f"IMG_{rnd.randint(0, 9999):04d}_{counter}.jpg"
                    if kind == "dup" and existing:
                        (d / name).write_bytes(rnd.choice(existing).read_bytes())
                    elif kind == "noexif":
                        make_photo(d / name, color=(rnd.randint(0, 3),) * 3, mtime=1_600_000_000 + rnd.randint(0, 2))
                    else:
                        make_photo(d / name, stamp, color=(rnd.randint(0, 3), rnd.randint(0, 3), counter % 250))
                        if kind == "mov":
                            (d / (name[:-4] + ".MOV")).write_bytes(b"mov%d" % counter)
                before = snapshot(d, False)
                run(d, "--apply")
                after = snapshot(d)
                payloads = lambda snap: sorted(h for h, _ in snap.values())
                clean_before = {k: v for k, v in before.items() if rp.LOG_DIR not in k}
                # no file lost, overwritten or created
                assert payloads(clean_before) == payloads(after), f"seed {seed}: content changed"
                # re-run changes nothing
                run(d, "--apply")
                assert after == snapshot(d), f"seed {seed}: second run not a no-op"
                if after.keys() != clean_before.keys() and rnd.random() < 0.5:  # (only if this run changed something) undo restores names, bytes and mtimes exactly
                    run(d, "--undo", "--apply")
                    got = {k: v for k, v in snapshot(d, False).items() if rp.LOG_DIR not in k}
                    assert got == clean_before, f"seed {seed}: undo mismatch"

    def test_random_sequences(self):
        for seed in range(150):
            self.one_scenario(seed)


if __name__ == "__main__":
    unittest.main()
