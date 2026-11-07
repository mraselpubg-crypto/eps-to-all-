import os
import sys
from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding="utf-8")

OTF_PATH = r"user_reference\DigitalKhattIndoPak.otf"
font = TTFont(OTF_PATH)

print("=================== Digital Khatt IndoPak ওপেনটাইপ ডিপ-ডাইভ ===================")

# 1. Glyphs and Classes
glyph_order = font.getGlyphOrder()
print(f"মোট গ্লিফ সংখ্যা: {len(glyph_order)}")

# Inspect glyph naming patterns
patterns = {}
for g in glyph_order:
    parts = g.split(".")
    ext = parts[-1] if len(parts) > 1 else "base"
    patterns[ext] = patterns.get(ext, 0) + 1

print("\nগ্লিফ এক্সটেনশন ও প্যাটার্ন পরিসংখ্যান:")
for ext, count in sorted(patterns.items(), key=lambda x: -x[1])[:15]:
    print(f"  .{ext:15s}: {count:4d} গ্লিফ")

# 2. GSUB Features and Lookups
if "GSUB" in font:
    gsub = font["GSUB"].table
    print("\n--- GSUB ফিচার তালিকা ---")
    for f_rec in gsub.FeatureList.FeatureRecord:
        print(f"  ফিচার: {f_rec.FeatureTag} (লুকআপ ইনডেক্স: {list(f_rec.Feature.LookupListIndex)})")
        
    print("\n--- প্রথম ১০টি GSUB লুকআপ টাইপ ---")
    for l_idx, lookup in enumerate(gsub.LookupList.Lookup[:10]):
        print(f"  Lookup {l_idx}: Type {lookup.LookupType}, Flag {lookup.LookupFlag}, SubTable count: {len(lookup.SubTable)}")

# 3. GPOS Features and Lookups
if "GPOS" in font:
    gpos = font["GPOS"].table
    print("\n--- GPOS ফিচার তালিকা ---")
    for f_rec in gpos.FeatureList.FeatureRecord:
        print(f"  ফিচার: {f_rec.FeatureTag} (লুকআপ ইনডেক্স: {list(f_rec.Feature.LookupListIndex)})")

    print(f"\nমোট GPOS লুকআপ সংখ্যা: {len(gpos.LookupList.Lookup)}")
    # Check mark-to-base and mark-to-mark
    mark_base_count = sum(1 for l in gpos.LookupList.Lookup if l.LookupType == 4)
    mark_mark_count = sum(1 for l in gpos.LookupList.Lookup if l.LookupType == 6)
    cursive_count = sum(1 for l in gpos.LookupList.Lookup if l.LookupType == 3)
    print(f"  MarkToBase (Type 4): {mark_base_count}")
    print(f"  MarkToMark (Type 6): {mark_mark_count}")
    print(f"  Cursive Attachment (Type 3): {cursive_count}")
