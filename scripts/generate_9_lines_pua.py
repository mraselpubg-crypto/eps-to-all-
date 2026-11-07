import os
import sys
import json
from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding="utf-8")

font = TTFont("dist/KarianaQuranRecoverFont.ttf")
cmap = font.getBestCmap()
rev_cmap = {v: k for k, v in cmap.items()}

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

with open("extracted_data/eps_page21/eps_page21_stream.json", "r", encoding="utf-8") as f:
    events = json.load(f)

ar_events = [e for e in events if e["base_font"].startswith("AnicaKariSAKQ")]
baselines = [169.73, 234.18, 298.63, 363.07, 427.52, 491.97, 556.41, 620.86, 685.31]

lines_data = []

for idx, y_target in enumerate(baselines, 1):
    evs = [e for e in ar_events if abs(e["y"] - y_target) < 3.0]
    # Sort Right to Left (highest x to lowest x)
    evs.sort(key=lambda x: -x["x"])
    
    char_list = []
    mapped_count = 0
    for e in evs:
        prefix = prefix_map.get(e["base_font"])
        canon = f"{prefix}_{e['glyph']}"
        if canon in rev_cmap:
            char_list.append(chr(rev_cmap[canon]))
            mapped_count += 1
        else:
            # If space or missing
            if e["glyph"] == "space":
                char_list.append(" ")
            
    pua_str = "".join(char_list)
    lines_data.append({
        "line_number": idx,
        "y": y_target,
        "total_events": len(evs),
        "mapped_glyphs": mapped_count,
        "pua_string": pua_str
    })
    print(f"লাইন {idx}: মোট গ্লিফ {len(evs)}, ম্যাপ করা হয়েছে {mapped_count}")

with open("dist/page21_9_lines_pua.json", "w", encoding="utf-8") as f:
    json.dump(lines_data, f, indent=2, ensure_ascii=False)

print("\n৯টি লাইনের PUA ডেটা 'dist/page21_9_lines_pua.json'-এ সংরক্ষিত হয়েছে!")
