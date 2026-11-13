import os, sys, time, signal, subprocess, tempfile, shutil, hashlib, json
from pathlib import Path
sys.path.insert(0, "/Volumes/My Shared Files/work/.ambition/judge")
sys.argv = ["x", "rename_photos.py"]
from PIL import Image
PY="/Volumes/My Shared Files/work/.venv/bin/python"; IMPL="/Volumes/My Shared Files/work/rename_photos.py"
base = sys.argv[1] if len(sys.argv) > 1 else "/Volumes/My Shared Files/work/.ambition/judge"
d = Path(tempfile.mkdtemp(prefix="kd_", dir="/Volumes/My Shared Files/work/.ambition/judge"))
for i in range(2500):
    img = Image.new("RGB",(8,8),(i%256,i//256,(i*7)%256)); ex=Image.Exif(); ex.get_ifd(0x8769)[0x9003]=f"2020:06:{1+i%28:02d} 1{i%10}:{i//100%60:02d}:{i%60:02d}"; img.save(d/f"IMG_{i:05d}.jpg", exif=ex)
orig = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in d.iterdir()}
pr = subprocess.Popen([PY, IMPL, str(d), "--apply"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
while not any(p.name.startswith("2020") for p in d.iterdir()): time.sleep(0.02)
time.sleep(0.6); pr.send_signal(signal.SIGKILL); pr.wait()
log = next((d/"_rename_logs").glob("run-*.jsonl"))
raw = log.read_text(); lines = raw.splitlines()
print("log lines:", len(lines), "| ends with newline:", raw.endswith("\n"))
try: [json.loads(l) for l in lines]; print("all log lines parse")
except Exception as e: print("LOG CORRUPT:", e, "| last line:", lines[-1][:100])
for attempt in (1, 2):
    r = subprocess.run([PY, IMPL, str(d), "--undo", "--apply"], capture_output=True, text=True)
    print(f"undo #{attempt}: rc={r.returncode}", "|", r.stdout.strip().splitlines()[-1][:110] if r.stdout.strip() else r.stderr[-200:])
now = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in d.iterdir() if p.is_file()}
missing = [n for n in orig if n not in now]; extra = [n for n in now if n not in orig]
print("original names missing:", len(missing), "| unexpected names:", len(extra), extra[:3])
direct = [n for n in missing if os.path.exists(d/n)]
print("of the missing, found by direct lookup (stale listing):", len(direct))
print(open(d/"_rename_logs"/(log.name)).read()[:0] if False else "")
