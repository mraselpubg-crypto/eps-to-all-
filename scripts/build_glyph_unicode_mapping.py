import os
import sys
import json
import re

sys.stdout.reconfigure(encoding="utf-8")

MASTER_JSON = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs\master_973_all_glyphs.json"
OUT_MAP = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs\glyph_semantic_map.json"

with open(MASTER_JSON, "r", encoding="utf-8") as f:
    master = json.load(f)

# Define semantic mapping structure
mapping = {
    "arabic_letters": {},      # gname -> {font, unicode_base, shape, notes}
    "harakats": {},             # gname -> {font, unicode, name}
    "tajweed_symbols_top": {},  # gname -> {font, private_unicode, tajweed_rule_name}
    "ayah_and_waqf": {},       # gname -> {font, type, unicode_seq}
    "bangla": {}                # gname -> {font, bangla_char}
}

# 1. Tajweed Top Symbols (S1, S2, S3, S4, A4)
# Visual analysis from chart_01:
# S1:
#   Icircumflex: উল্টা পেশ / খাড়া যের জাতীয় তাজবীদ টান বা ১ আলিফ
#   Oacute: লাল ড্রপ/চিহ্ন
#   Ocircumflex: বাঁকা লাল মার্কার
#   Ograve: ত্রিভুজ / ডেল্টা আকৃতির চিহ্ন (ইদগাম/ইখফা)
#   Uacute: ছাতা/খিলান আকৃতির মাদ্দ চিহ্ন
#   apple: বিশেষ পেঁচানো তাজবীদ চিহ্ন
# S2:
#   Idieresis: তিন পাতার মতো সবুজ/লাল চিহ্ন (৩ আলিফ / গুন্নাহ)
#   Oacute: চার পাতার চিহ্ন (৪ আলিফ মাদ্দ)
#   Ocircumflex: বিশেষ চতুর্ভুজ/তাজবীদ প্রতীক
#   apple: বাঁকা হুক
# S3:
#   Icircumflex: তিন পাতার জোড়া চিহ্ন
#   Idieresis: বিশেষ পেঁচানো তাজবীদ প্রতীক
#   Igrave: তিন পাতার গুচ্ছ
#   Oacute: তীর/পাতা
#   Ograve: নিচের দিকে তীর (⬇ সাকিন/ওয়াকফ ড্রপ)
# S4:
#   Icircumflex: ৩ পাতার প্রতীক
#   Igrave: বৃত্তে ঘেরা পেঁচানো চিহ্ন
#   Oacute: খিলান জোড়া
#   apple: তীরসহ বৃত্ত (⬇⑧)

# Let's catalog all S1..S4 and A4 glyphs
p_uni_counter = 0xE001
for fam in ["AnicaKariSAKQS1", "AnicaKariSAKQS2", "AnicaKariSAKQS3", "AnicaKariSAKQS4", "AnicaKariSAKQA4"]:
    if fam in master:
        for gname, vdict in master[fam]["glyphs"].items():
            if gname == ".notdef":
                continue
            gv = next(iter(vdict.values()))
            if gv["bounds"] is not None and gv["bounds"][3] > 800: # Top symbol band
                p_code = f"U+{p_uni_counter:04X}"
                mapping["tajweed_symbols_top"][f"{fam}:{gname}"] = {
                    "font": fam,
                    "glyph": gname,
                    "p_unicode": p_code,
                    "bounds": gv["bounds"],
                    "width": gv["width"],
                    "sample_pages": gv["sample_pages"]
                }
                p_uni_counter += 1

print(f"শনাক্তকৃত টপ তাজবীদ চিহ্ন (S1-S4 & A4 top): {len(mapping['tajweed_symbols_top'])}")

# 2. Waqf and Ayah Markers (AW, LW)
for fam in ["AnicaKariSAKQAW", "AnicaKariSAKQLW"]:
    if fam in master:
        for gname, vdict in master[fam]["glyphs"].items():
            if gname == ".notdef":
                continue
            gv = next(iter(vdict.values()))
            mapping["ayah_and_waqf"][f"{fam}:{gname}"] = {
                "font": fam,
                "glyph": gname,
                "width": gv["width"],
                "bounds": gv["bounds"],
                "sample_pages": gv["sample_pages"]
            }

print(f"শনাক্তকৃত আয়াত ও ওয়াকফ গ্লিফ (AW, LW): {len(mapping['ayah_and_waqf'])}")

# 3. Harakat Layers
for fam in ["AnicaKariSAKQHarkat", "AnicaKariSAKQHarkatExtra", "AnicaKariSAKQHarkatSpare"]:
    if fam in master:
        for gname, vdict in master[fam]["glyphs"].items():
            if gname == ".notdef":
                continue
            gv = next(iter(vdict.values()))
            mapping["harakats"][f"{fam}:{gname}"] = {
                "font": fam,
                "glyph": gname,
                "width": gv["width"],
                "bounds": gv["bounds"],
                "sample_pages": gv["sample_pages"]
            }

print(f"শনাক্তকৃত হরকত গ্লিফ (Harkat*): {len(mapping['harakats'])}")

# 4. Arabic Base & Ligatures (Plain, Extra, Spare)
for fam in ["AnicaKariSAKQPlain", "AnicaKariSAKQPlainExtra", "AnicaKariSAKQPlainSpare"]:
    if fam in master:
        for gname, vdict in master[fam]["glyphs"].items():
            if gname == ".notdef":
                continue
            gv = next(iter(vdict.values()))
            mapping["arabic_letters"][f"{fam}:{gname}"] = {
                "font": fam,
                "glyph": gname,
                "width": gv["width"],
                "bounds": gv["bounds"],
                "sample_pages": gv["sample_pages"]
            }

print(f"শনাক্তকৃত আরবি হরফ ও লিগেচার গ্লিফ (Plain*): {len(mapping['arabic_letters'])}")

# 5. Bangla Glyphs
for fam in ["AnicaBangali", "AnicaBangali-Bold", "KarianaBangali", "KarianaBangali-Bold"]:
    if fam in master:
        for gname, vdict in master[fam]["glyphs"].items():
            if gname == ".notdef":
                continue
            gv = next(iter(vdict.values()))
            mapping["bangla"][f"{fam}:{gname}"] = {
                "font": fam,
                "glyph": gname,
                "width": gv["width"],
                "bounds": gv["bounds"]
            }

print(f"শনাক্তকৃত বাংলা অনুবাদের গ্লিফ: {len(mapping['bangla'])}")

with open(OUT_MAP, "w", encoding="utf-8") as f:
    json.dump(mapping, f, indent=2, ensure_ascii=False)

print(f"\nম্যাপিং ডেটাবেস সংরক্ষিত হয়েছে: {OUT_MAP}")
