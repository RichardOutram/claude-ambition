"""Outside check: runs an implementation as a user would (subprocess) and compares to reference answers.
usage: acceptance.py PATH_TO_rename_photos.py [label]"""
import hashlib, os, random, re, shutil, signal, subprocess, sys, tempfile, time
from datetime import datetime
from pathlib import Path
sys.path.insert(0, "/Volumes/My Shared Files/work")
from PIL import Image
import rename_photos as _rp   # only for the EXIF tag number constant

IMPL = sys.argv[1]; LABEL = sys.argv[2] if len(sys.argv) > 2 else IMPL
PY = "/Volumes/My Shared Files/work/.venv/bin/python"
REAL_HEIC = Path("/System/Library/Desktop Pictures/iMac Blue.heic")
results, outputs = [], []

def photo(path, taken=None, color=(1, 2, 3), mtime=None):
    img = Image.new("RGB", (8, 8), color); ex = Image.Exif()
    if taken: ex.get_ifd(0x8769)[0x9003] = taken; img.save(path, exif=ex)
    else: img.save(path)
    if mtime: os.utime(path, (mtime, mtime))

def snap(d):
    return {str(p.relative_to(d)): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in sorted(Path(d).rglob("*")) if p.is_file() and "_rename_logs" not in p.parts and not p.name.startswith(".rename")}

def run(d, *args, py=PY, record=True):
    r = subprocess.run([py, IMPL, str(d), *args], capture_output=True, text=True)
    if record: outputs.append((" ".join(args) or "(preview)", r.returncode, r.stdout, r.stderr))
    return r

def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))

def tmp(): return Path(tempfile.mkdtemp(prefix="judge_"))
def names(d): return sorted(p.name for p in Path(d).iterdir() if p.is_file())

# ---- ask: rename by date taken (reference = the dates we wrote into the files)
d = tmp(); rnd = random.Random(7); expected = []
for i in range(12):
    t = datetime(rnd.randint(2008, 2025), rnd.randint(1, 12), rnd.randint(1, 28), rnd.randint(0, 23), rnd.randint(0, 59), rnd.randint(0, 59))
    photo(d / f"IMG_{i:04d}.JPG", t.strftime("%Y:%m:%d %H:%M:%S"), color=(i, i, i)); expected.append(t.strftime("%Y-%m-%d_%H-%M-%S") + ".jpg")
before = snap(d)
r = run(d)   # preview
check("ASK  preview (no --apply) changes nothing", snap(d) == before and not (d / "_rename_logs").exists())
r = run(d, "--apply")
check("ASK  renames 12 photos to their EXIF date-taken", names(d) == sorted(expected), f"got {names(d)[:3]}...")
a1 = snap(d)
run(d, "--apply")
check("GOAL re-run on the same folder changes nothing", snap(d) == a1)
r = run(d, "--undo", "--apply")
check("GOAL undo restores names, bytes and mtimes exactly", snap(d) == before, f"rc={r.returncode}")

# ---- real HEIC/JPEG files: the new name's date must literally appear in the file's own bytes
d = tmp(); real = [p for p in map(Path, open("/tmp/real_candidates.txt").read().split("\n")) if p.exists()][:400]
for i, p in enumerate(real):
    shutil.copyfile(p, d / f"R{i:03d}{p.suffix}"); os.utime(d / f"R{i:03d}{p.suffix}", (p.stat().st_atime, p.stat().st_mtime))
before = snap(d); r = run(d, "--apply"); after = snap(d)
bad = 0; checked = 0
for p in d.iterdir():
    m = re.match(r"(\d{4})-(\d\d)-(\d\d)_(\d\d)-(\d\d)-(\d\d)", p.name)
    if m:
        s = f"{m[1]}:{m[2]}:{m[3]} {m[4]}:{m[5]}:{m[6]}".encode()
        if s in p.read_bytes(): checked += 1
        else: bad += 1   # name's date not found in the file's EXIF bytes -> came from mtime (should be flagged)
renamed = sum(1 for p in d.iterdir() if re.match(r"\d{4}-", p.name))
rep = list((d / "_rename_logs").glob("*.report.txt"))
flagged_txt = rep[0].read_text() if rep else ""
def unflagged_wrong():
    cnt = 0
    for p in d.iterdir():
        m = re.match(r"(\d{4})-(\d\d)-(\d\d)_(\d\d)-(\d\d)-(\d\d)", p.name)
        if m and f"{m[1]}:{m[2]}:{m[3]} {m[4]}:{m[5]}:{m[6]}".encode() not in p.read_bytes():
            # allowed only if the report flags it
            if p.name not in flagged_txt: cnt += 1
    return cnt
check(f"ASK  real photos: every name's date is in the file's own EXIF bytes or is flagged ({renamed} renamed, {checked} verified in bytes)",
      rep and unflagged_wrong() == 0, f"unflagged-wrong={unflagged_wrong() if rep else 'no report'}")
r = run(d, "--undo", "--apply")
check("GOAL real-photo round trip (apply then undo) is byte-for-byte identical", snap(d) == before, f"rc={r.returncode}")

# ---- collisions, duplicates, no-clobber
d = tmp()
for n, c in (("a.jpg", (1, 1, 1)), ("b.jpg", (2, 2, 2)), ("c.jpg", (3, 3, 3))): photo(d / n, "2021:05:04 10:11:12", color=c)
(d / "dup.jpg").write_bytes((d / "a.jpg").read_bytes())
photo(d / "wa.jpg", color=(9, 9, 9), mtime=1_600_000_000)
(d / "wa_again.jpg").write_bytes((d / "wa.jpg").read_bytes()); os.utime(d / "wa_again.jpg", (1_605_000_000,) * 2)
before = snap(d); blobs = sorted(h for h, _ in before.values())
run(d, "--apply"); after = snap(d)
check("GOAL three different photos in the same second all survive with suffixes",
      {"2021-05-04_10-11-12.jpg", "2021-05-04_10-11-12_1.jpg", "2021-05-04_10-11-12_2.jpg"} <= set(names(d)))
check("GOAL nothing lost or overwritten (every byte-content still present, same count)",
      sorted(h for h, _ in after.values()) == blobs)
check("GOAL exact duplicates are left un-renamed, with or without EXIF (dup.jpg, wa_again.jpg)",
      "dup.jpg" in names(d) and sum(n.startswith("2020") for n in names(d)) == 1)
check("GOAL a readable report lists the flagged (no-EXIF) file and the duplicates",
      any(("wa" in f.read_text() and "dup.jpg" in f.read_text()) for f in d.rglob("*.txt")))
run(d, "--undo", "--apply")
check("GOAL undo of that messy run is exact", snap(d) == before)

d = tmp(); photo(d / "a.jpg", "2021:05:04 10:11:12"); (d / "2021-05-04_10-11-12.jpg").write_bytes(b"precious unrelated file")
run(d, "--apply")
check("ASK  never overwrites an existing file at the target name", (d / "2021-05-04_10-11-12.jpg").read_bytes() == b"precious unrelated file" and len(names(d)) == 2)

d = tmp(); photo(d / "IMG_1.jpg", "2021:05:04 10:11:12"); (d / "IMG_1.MOV").write_bytes(b"live photo video")
run(d, "--apply")
check("GOAL a Live Photo's video stays paired with its photo", "2021-05-04_10-11-12.mov" in names(d))

# ---- dates that are missing or wrong
d = tmp(); photo(d / "none.jpg", color=(5, 5, 5), mtime=1_600_000_000); photo(d / "wrong.jpg", "1970:01:01 00:00:00", color=(6, 6, 6), mtime=1_610_000_000)
run(d, "--apply"); txt = " ".join(f.read_text() for f in d.rglob("*.txt"))
check("ASK  no/wrong EXIF date falls back to modified time", sum(n.startswith("2020") or n.startswith("2021") for n in names(d)) == 2)
check("GOAL ...and both are flagged for the user to check", "none.jpg" in txt and "wrong.jpg" in txt)

# ---- environment honesty
d = tmp(); photo(d / "a.jpg", "2019:03:03 08:08:08")
r = run(d, "--apply", py="python3")   # the plain command a user would type, no Pillow
check("GOAL without Pillow it must not silently name by file time (name must be 2019-... or refuse)",
      names(d) == ["a.jpg"] or names(d) == ["2019-03-03_08-08-08.jpg"], f"got {names(d)} rc={r.returncode}")

# ---- the big one: real kill -9 mid-run, then recover
for base in ("/tmp", "/Volumes/My Shared Files/work/.ambition/judge"):
    ok_all = True; detail = ""
    for extra in (300, 1200, 2200):   # kill once this many files have been renamed
        d = Path(tempfile.mkdtemp(prefix="kill_", dir=base))
        for i in range(2500): photo(d / f"IMG_{i:05d}.jpg", f"2020:06:{1 + i % 28:02d} 1{i % 10}:{i // 100 % 60:02d}:{i % 60:02d}", color=(i % 256, i // 256, (i * 7) % 256))
        os.sync(); time.sleep(1.0)   # let the volume finalise timestamps of the files just written
        before = snap(d)
        pr = subprocess.Popen([PY, IMPL, str(d), "--apply"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.time()
        while time.time() - t0 < 120 and sum(p.name.startswith("2020") for p in d.iterdir()) < extra: time.sleep(0.005)
        pr.send_signal(signal.SIGKILL); pr.wait()
        moved = sum(1 for p in d.iterdir() if p.name.startswith("2020"))
        r = run(d, "--undo", "--apply", record=False)
        back = snap(d) == before
        why = ""
        if not back:
            why = f" undo#1 rc={r.returncode} out={(r.stdout.strip().splitlines() or [''])[-1][:80]!r} err={r.stderr[-120:]!r};"
            r = run(d, "--undo", "--apply", record=False); back = snap(d) == before
            now = snap(d); why += f" undo#2 rc={r.returncode} out={(r.stdout.strip().splitlines() or [''])[-1][:60]!r}; missing={len([k for k in before if k not in now])} extra={len([k for k in now if k not in before])} changed={len([k for k in before if k in now and now[k]!=before[k]])} detail={[(k, before[k][0]==now[k][0], now[k][1]-before[k][1]) for k in before if k in now and now[k]!=before[k]][:4]}"
            print("DIAG", why, file=sys.stderr)
        mid = 0 < moved < 2500
        ok_all &= back and mid; detail += f" [{Path(base).name} kill after {extra}: {moved}/2500 renamed{'' if mid else ' (NOT mid-run: test void)'}, restored={back}]"
        shutil.rmtree(d, ignore_errors=True)
    check(f"GOAL kill -9 mid-run on 2500 files, then undo restores everything{detail}", ok_all)

# ---- scale
d = tmp()
for i in range(3000): photo(d / f"IMG_{i:04d}.jpg", f"2020:06:{1 + i % 28:02d} 1{i % 10}:00:{i % 60:02d}", color=(i % 256, i // 256, (i * 3) % 256))
t0 = time.time(); run(d, "--apply", record=False); t1 = time.time() - t0
t0 = time.time(); run(d, "--apply", record=False); t2 = time.time() - t0
check(f"GOAL 3000 photos: apply {t1:.1f}s, no-op re-run {t2:.1f}s (both under 30s)", t1 < 30 and t2 < 30)

# ---- genre: never a traceback, ever
tb = [o for o in outputs if "Traceback" in o[3] or "Traceback" in o[2]]
check("GENRE no traceback in any output", not tb, str([o[0] for o in tb]))

print(f"\n===== {LABEL} =====")
for name, ok, detail in results: print(("PASS " if ok else "FAIL ") + name + (f"   <- {detail}" if not ok and detail else ""))
print(f"\n{sum(ok for _, ok, _ in results)}/{len(results)} passed")
import json; json.dump(outputs, open(f"/Volumes/My Shared Files/work/.ambition/judge/outputs_{Path(LABEL).name.replace('/','_')}.json", "w"))
