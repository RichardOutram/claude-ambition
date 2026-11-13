import os, sys, time, signal, subprocess, tempfile, shutil, hashlib, json
from pathlib import Path
sys.path.insert(0, "/Volumes/My Shared Files/work/.ambition/judge")
sys.argv = ["x", "rename_photos.py"]
from PIL import Image
PY="/Volumes/My Shared Files/work/.venv/bin/python"; IMPL="/Volumes/My Shared Files/work/rename_photos.py"
base = sys.argv[1] if len(sys.argv) > 1 else "/Volumes/My Shared Files/work/.ambition/judge"

def snap(d):
    return {p.name:(hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) for p in sorted(Path(d).iterdir()) if p.is_file()}
for trial, extra in enumerate((0.05,0.3,0.6,0.6,0.9,0.6,1.2,0.6)):
    d = Path(tempfile.mkdtemp(prefix="kd_", dir="/Volumes/My Shared Files/work/.ambition/judge"))
    for i in range(2500):
        img = Image.new("RGB",(8,8),(i%256,i//256,(i*7)%256)); ex=Image.Exif(); ex.get_ifd(0x8769)[0x9003]=f"2020:06:{1+i%28:02d} 1{i%10}:{i//100%60:02d}:{i%60:02d}"; img.save(d/f"IMG_{i:05d}.jpg", exif=ex)
    before = snap(d)
    pr = subprocess.Popen([PY, IMPL, str(d), "--apply"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    while not any(p.name.startswith("2020") for p in d.iterdir()): time.sleep(0.02)
    time.sleep(extra); pr.send_signal(signal.SIGKILL); pr.wait()
    moved = sum(1 for p in d.iterdir() if p.name.startswith("2020"))
    outs = []
    for k in range(2):
        r = subprocess.run([PY, IMPL, str(d), "--undo", "--apply"], capture_output=True, text=True)
        outs.append((r.returncode, (r.stdout.strip().splitlines() or [""])[-1][:100]))
        if snap(d) == before: break
    now = snap(d)
    ok = now == before
    print(f"trial {trial} +{extra}s moved={moved} restored={ok} undo={outs}")
    if not ok:
        miss = [n for n in before if n not in now]; extra_n = [n for n in now if n not in before]
        diff = [n for n in before if n in now and now[n] != before[n]]
        print("   missing:", len(miss), miss[:3], "| unexpected:", len(extra_n), extra_n[:3], "| changed hash/mtime:", len(diff), [ (n, before[n][1]-now[n][1], before[n][0]==now[n][0]) for n in diff[:3]])
        print("   direct lookup finds missing:", sum(os.path.exists(d/n) for n in miss))
    else: shutil.rmtree(d, ignore_errors=True)
