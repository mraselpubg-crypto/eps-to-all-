import os
import sys
import json
from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding="utf-8")

FONT_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\dist\KarianaDigitalKhat.ttf"
STREAM_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\eps_page21\eps_page21_stream.json"

font = TTFont(FONT_PATH)
cmap = font.getBestCmap()
rev_cmap = {v: k for k, v in cmap.items()}

with open(STREAM_PATH, "r", encoding="utf-8") as f:
    events = json.load(f)

# Find all 9 Arabic baselines
baselines = [169.73, 234.17, 298.61, 363.05, 427.49, 491.93, 556.37, 620.81, 685.25]

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

page21_exact_lines = []

for l_idx, y_base in enumerate(baselines, 1):
    line_evs = [e for e in events if abs(e["y"] - y_base) < 4.0 and "Bangali" not in e["base_font"]]
    line_evs.sort(key=lambda e: -e["x"]) # RTL
    
    char_codes = []
    for e in line_evs:
        f_base = e["base_font"]
        prefix = prefix_map.get(f_base)
        gname = e["glyph"]
        canonical = f"{prefix}_{gname}"
        
        if canonical in rev_cmap:
            u_code = rev_cmap[canonical]
            char_codes.append(chr(u_code))
            
    pua_str = "".join(char_codes)
    page21_exact_lines.append({
        "line_no": l_idx,
        "event_count": len(line_evs),
        "pua_string": pua_str
    })
    print(f"লাইন {l_idx}: ইভেন্ট {len(line_evs):3d} টি, PUA ক্যারেক্টার {len(pua_str):3d} টি")

with open(r"extracted_data\page21_exact_pua_lines.json", "w", encoding="utf-8") as out:
    json.dump(page21_exact_lines, out, ensure_ascii=False, indent=2)

print("\nextracted_data/page21_exact_pua_lines.json সফলভাবে সেভ হয়েছে!")
