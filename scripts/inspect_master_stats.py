import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

MASTER_JSON = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs\master_973_all_glyphs.json"

with open(MASTER_JSON, "r", encoding="utf-8") as f:
    master = json.load(f)

print(f"মোট ফন্ট ফ্যামিলি সংখ্যা: {len(master)}")
total_glyphs = 0
for k, v in sorted(master.items()):
    glyphs = v.get("glyphs", {})
    count = len(glyphs)
    total_glyphs += count
    print(f"{k:32s}: {count:4d} গ্লিফ")

print(f"\nসর্বমোট ইউনিক গ্লিফ এন্ট্রি: {total_glyphs}")
