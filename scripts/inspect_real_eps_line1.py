import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

STREAM_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\eps_page21\eps_page21_stream.json"

with open(STREAM_PATH, "r", encoding="utf-8") as f:
    events = json.load(f)

# Arabic baseline for line 1 is y ~ 169.73
line1 = [e for e in events if abs(e["y"] - 169.73) < 3.0 and "Bangali" not in e["base_font"]]
# Sort Right-to-Left (x descending)
line1.sort(key=lambda e: -e["x"])

print(f"মূল EPS লাইন ১-এ মোট ইভেন্ট: {len(line1)}\n")
for idx, e in enumerate(line1, 1):
    f_clean = e["base_font"].replace("AnicaKariSAKQ", "")
    print(f"[{idx:2d}] X={e['x']:6.2f} | Font: {f_clean:12s} | Glyph: {e['glyph']:18s} | Width: {e['width']:5.1f}")
