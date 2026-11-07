import os
import sys
import json
from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding="utf-8")

FONT_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\dist\KarianaDigitalKhat.ttf"
STREAM_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\eps_page21\eps_page21_stream.json"

font = TTFont(FONT_PATH)
cmap = font.getBestCmap()
# Reverse cmap: glyph_name -> unicode
rev_cmap = {v: k for k, v in cmap.items()}

with open(STREAM_PATH, "r", encoding="utf-8") as f:
    events = json.load(f)

# Baseline for line 1
line1 = [e for e in events if abs(e["y"] - 169.73) < 3.0 and "Bangali" not in e["base_font"]]
line1.sort(key=lambda e: -e["x"])

# Map each event to canonical glyph name in our font
prefix_map = {
    "AnicaKariSAKQPlain": "ar",
    "AnicaKariSAKQPlainExtra": "ar_ex",
    "AnicaKariSAKQPlainSpare": "ar_sp",
    "AnicaKariSAKQHarkat": "hrk",
    "AnicaKariSAKQHarkatExtra": "hrk_ex",
    "AnicaKariSAKQHarkatSpare": "hrk_sp",
    "AnicaKariSAKQS1": "taj_s1",
    "AnicaKariSAKQS2": "taj_s2",
    "AnicaKariSAKQS3": "taj_s3",
    "AnicaKariSAKQS4": "taj_s4",
    "AnicaKariSAKQA4": "taj_a4",
    "AnicaKariSAKQAW": "wqf_aw",
    "AnicaKariSAKQLW": "wqf_lw"
}

char_codes = []
missing_glyphs = []

for e in line1:
    f_base = e["base_font"]
    prefix = prefix_map.get(f_base)
    gname = e["glyph"]
    canonical = f"{prefix}_{gname}"
    
    if canonical in rev_cmap:
        u_code = rev_cmap[canonical]
        char_codes.append(chr(u_code))
    else:
        missing_glyphs.append(canonical)

print(f"লাইন ১ মোট ইভেন্ট: {len(line1)}")
print(f"ম্যাপ করা গ্লিফ ক্যারেক্টার: {len(char_codes)}")
print(f"মিসিং গ্লিফ: {missing_glyphs}")

pua_string = "".join(char_codes)
print(f"PUA স্ট্রিং দৈর্ঘ্য: {len(pua_string)}")

# Save to a test file
with open("dist/line1_exact_pua.txt", "w", encoding="utf-8") as f:
    f.write(pua_string)

print("dist/line1_exact_pua.txt সেভ সম্পন্ন!")
