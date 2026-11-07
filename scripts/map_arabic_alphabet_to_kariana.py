import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

MASTER_JSON = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs\master_973_all_glyphs.json"

with open(MASTER_JSON, "r", encoding="utf-8") as f:
    master = json.load(f)

plain_glyphs = master.get("AnicaKariSAKQPlain", {}).get("glyphs", {})

print(f"AnicaKariSAKQPlain মোট গ্লিফ: {len(plain_glyphs)}")

# List all glyph names sorted
for gname, vdict in sorted(plain_glyphs.items()):
    if gname == ".notdef": continue
    gv = next(iter(vdict.values()))
    w = gv["width"]
    bounds = gv["bounds"]
    print(f"  {gname:20s}: width={w:4.0f}, bounds={bounds}")
