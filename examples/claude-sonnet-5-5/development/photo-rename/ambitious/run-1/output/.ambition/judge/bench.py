import sys, time, tempfile, io, contextlib, shutil, cProfile, pstats
import os
sys.path.insert(0, os.environ.get("IMPL_DIR", "/Volumes/My Shared Files/work"))
sys.path.insert(1, "/Volumes/My Shared Files/work")
from pathlib import Path
import test_rename_photos as t, rename_photos as rp
N = int(sys.argv[1]); prof = len(sys.argv) > 2
base = Path(tempfile.mkdtemp(prefix="bench_"))
# realistic-ish: distinct sizes via varying image dimensions
for i in range(N):
    from PIL import Image
    img = Image.new("RGB", (8 + i % 40, 8 + i % 23), (i % 256, i // 256 % 256, (i * 3) % 256)); ex = Image.Exif()
    ex.get_ifd(0x8769)[0x9003] = f"20{10 + i % 15}:{1 + i % 12:02d}:{1 + i % 28:02d} {i % 24:02d}:{i // 24 % 60:02d}:{i % 60:02d}"
    img.save(base / f"IMG_{i:05d}.jpg", exif=ex)
import os; os.sync(); time.sleep(0.5)
def go(*a):
    t0 = time.time()
    with contextlib.redirect_stdout(io.StringIO()): rp.main([str(base), *a])
    return time.time() - t0
if prof:
    pr = cProfile.Profile(); pr.enable(); el = go("--apply"); pr.disable()
    print(f"apply {el:.2f}s"); pstats.Stats(pr).sort_stats("tottime").print_stats(9)
else:
    a = go("--apply"); b = go("--apply"); c = go("--undo", "--apply")
    print(f"N={N}: apply {a:.2f}s | no-op re-run {b:.2f}s | undo {c:.2f}s")
shutil.rmtree(base, ignore_errors=True)
