import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

MAP_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs\glyph_semantic_map.json"

with open(MAP_PATH, "r", encoding="utf-8") as f:
    sem_map = json.load(f)

letters = sem_map.get("arabic_letters", {})
print(f"ম্যাপ করা আরবি অক্ষরের সংখ্যা: {len(letters)}")

# Sample first 30 entries
for k, v in list(letters.items())[:30]:
    print(f"  {k:30s} -> P_Unicode: {v.get('p_unicode', 'None'):8s} | Width: {v.get('width', 0):4.0f} | Bounds: {v.get('bounds')}")
