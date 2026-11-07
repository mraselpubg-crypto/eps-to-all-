import os
import sys
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

MASTER_JSON = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs\master_973_all_glyphs.json"

with open(MASTER_JSON, "r", encoding="utf-8") as f:
    master = json.load(f)

# Group glyphs by family
families = [
    "AnicaKariSAKQPlain", "AnicaKariSAKQPlainExtra", "AnicaKariSAKQPlainSpare",
    "AnicaKariSAKQHarkat", "AnicaKariSAKQHarkatExtra", "AnicaKariSAKQHarkatSpare",
    "AnicaKariSAKQS1", "AnicaKariSAKQS2", "AnicaKariSAKQS3", "AnicaKariSAKQS4", "AnicaKariSAKQA4",
    "AnicaKariSAKQAW", "AnicaKariSAKQLW"
]

all_unique_glyphs = {}
category_counts = defaultdict(int)

for fam in families:
    f_glyphs = master.get(fam, {}).get("glyphs", {})
    prefix = fam.replace("AnicaKariSAKQ", "")
    for gname, vdict in sorted(f_glyphs.items()):
        if gname == ".notdef": continue
        gv = next(iter(vdict.values()))
        w = gv["width"]
        bounds = gv["bounds"]
        svg = gv["svg_path"]
        
        # Determine category based on family & bounds
        if prefix in ["S1", "S2", "S3", "S4"] or (prefix == "A4" and w == 0):
            cat = "tajweed_top"
        elif prefix in ["AW", "LW"]:
            cat = "ayah_waqf"
        elif "Harkat" in prefix or (bounds and bounds[1] is not None and bounds[1] > 400 and w == 0):
            cat = "harkat"
        else:
            cat = "arabic_base"
            
        full_id = f"{prefix}_{gname}"
        all_unique_glyphs[full_id] = {
            "family": fam,
            "glyph": gname,
            "width": w,
            "bounds": bounds,
            "category": cat,
            "has_svg": bool(svg)
        }
        category_counts[cat] += 1

print(f"মোট সংগৃহীত ইউনিক গ্লিফ সংখ্যা: {len(all_unique_glyphs)}")
for cat, count in sorted(category_counts.items()):
    print(f"  ক্যাটাগরি '{cat}': {count} টি গ্লিফ")

with open(r"extracted_data\smart_font_glyph_inventory.json", "w", encoding="utf-8") as out:
    json.dump(all_unique_glyphs, out, ensure_ascii=False, indent=2)

print("extracted_data/smart_font_glyph_inventory.json সেভ সম্পন্ন।")
