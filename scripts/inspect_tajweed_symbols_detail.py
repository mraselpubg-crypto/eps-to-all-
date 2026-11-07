import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

MASTER_JSON = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs\master_973_all_glyphs.json"

with open(MASTER_JSON, "r", encoding="utf-8") as f:
    master = json.load(f)

print("=================== টপ তাজবীদ প্রতীক বিশ্লেষণ (S1, S2, S3, S4, A4) ===================")
for fam in ["AnicaKariSAKQS1", "AnicaKariSAKQS2", "AnicaKariSAKQS3", "AnicaKariSAKQS4", "AnicaKariSAKQA4"]:
    glyphs = master.get(fam, {}).get("glyphs", {})
    print(f"\n--- {fam} ({len(glyphs)} টি গ্লিফ) ---")
    for gname, vdict in sorted(glyphs.items()):
        if gname == ".notdef": continue
        gv = next(iter(vdict.values()))
        w = gv["width"]
        bounds = gv["bounds"]
        print(f"  {gname:20s}: advance_width={w:4.1f}, bounds={bounds}")
