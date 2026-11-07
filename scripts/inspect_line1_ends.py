import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

STREAM_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\eps_page21\eps_page21_stream.json"

with open(STREAM_PATH, "r", encoding="utf-8") as f:
    events = json.load(f)

line1 = [e for e in events if abs(e["y"] - 169.7) < 5.0 and "Bangali" not in e["base_font"]]
line1.sort(key=lambda e: -e["x"])

print("=== ডান প্রান্ত (Right side: X = 491 to 440) ===")
for e in line1[:15]:
    f_clean = e["base_font"].replace("AnicaKariSAKQ", "")
    print(f"  X={e['x']:5.1f} | Font: {f_clean:12s} | Glyph: {e['glyph']:15s}")

print("\n=== বাম প্রান্ত (Left side: X = 150 to 90) ===")
for e in line1[-15:]:
    f_clean = e["base_font"].replace("AnicaKariSAKQ", "")
    print(f"  X={e['x']:5.1f} | Font: {f_clean:12s} | Glyph: {e['glyph']:15s}")
