import os
import sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

# Let's inspect slice_1_rtl.png and slice_5_rtl.png
# We can check the dimensions and see which one has the end of ayah or which word
s1 = Image.open("dist/line1_words/slice_1_rtl.png")
s5 = Image.open("dist/line1_words/slice_5_rtl.png")

print(f"Slice 1 (Rightmost) size: {s1.size}")
print(f"Slice 5 (Leftmost) size: {s5.size}")

# Let's see: in eps_page21_stream.json:
# What glyphs are at X > 440?
import json
with open("extracted_data/eps_page21/eps_page21_stream.json", "r", encoding="utf-8") as f:
    evs = json.load(f)

line1_evs = [e for e in evs if abs(e["y"] - 169.73) < 3.0 and "Bangali" not in e["base_font"]]
right_evs = [e for e in line1_evs if e["x"] > 440]
left_evs = [e for e in line1_evs if e["x"] < 160]

print("\n--- গ্লিফসমূহ ডান প্রান্তে (X > 440): ---")
for e in sorted(right_evs, key=lambda x: -x["x"]):
    print(f"  X={e['x']:6.2f} | {e['base_font'].replace('AnicaKariSAKQ', '')}:{e['glyph']}")

print("\n--- গ্লিফসমূহ বাম প্রান্তে (X < 160): ---")
for e in sorted(left_evs, key=lambda x: -x["x"]):
    print(f"  X={e['x']:6.2f} | {e['base_font'].replace('AnicaKariSAKQ', '')}:{e['glyph']}")
