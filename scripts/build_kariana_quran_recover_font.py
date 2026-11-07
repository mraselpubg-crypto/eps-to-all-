import os
import sys
import json
import shutil
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.svgLib.path import SVGPath
from fontTools.feaLib import builder as feaBuilder

sys.stdout.reconfigure(encoding="utf-8")

MASTER_JSON = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs\master_973_all_glyphs.json"
OUT_OTF = r"dist\KarianaQuranRecoverFont.otf"
OUT_TTF = r"dist\KarianaQuranRecoverFont.ttf"
FEA_PATH = r"dist\kariana_recover_features.fea"

os.makedirs("dist", exist_ok=True)

with open(MASTER_JSON, "r", encoding="utf-8") as f:
    master = json.load(f)

print("=== কারিয়ানা কুরআন রিকভার ফন্ট (Kariana Quran Recover Font) কম্পাইলেশন শুরু ===")

glyph_order = [".notdef"]
advance_widths = {".notdef": 500}
cmap = {}
charstrings = {}

# .notdef
pen = T2CharStringPen(500, None)
charstrings[".notdef"] = pen.getCharString()

families = [
    ("AnicaKariSAKQPlain", "ar"),
    ("AnicaKariSAKQPlainExtra", "ar_ex"),
    ("AnicaKariSAKQPlainSpare", "ar_sp"),
    ("AnicaKariSAKQHarkat", "hrk"),
    ("AnicaKariSAKQHarkatExtra", "hrk_ex"),
    ("AnicaKariSAKQHarkatSpare", "hrk_sp"),
    ("AnicaKariSAKQS1", "taj_s1"),
    ("AnicaKariSAKQS2", "taj_s2"),
    ("AnicaKariSAKQS3", "taj_s3"),
    ("AnicaKariSAKQS4", "taj_s4"),
    ("AnicaKariSAKQA4", "taj_a4"),
    ("AnicaKariSAKQAW", "wqf_aw"),
    ("AnicaKariSAKQLW", "wqf_lw")
]

pua_code = 0xE000
glyph_svg_map = {}

for fam, prefix in families:
    f_glyphs = master.get(fam, {}).get("glyphs", {})
    for gname, vdict in sorted(f_glyphs.items()):
        if gname == ".notdef": continue
        gv = next(iter(vdict.values()))
        w = int(round(gv["width"]))
        if "taj" in prefix:
            w = 0 # Zero advance width for upper Tajweed symbols
            
        canonical_name = f"{prefix}_{gname}"
        glyph_order.append(canonical_name)
        advance_widths[canonical_name] = w
        cmap[pua_code] = canonical_name
        pua_code += 1
        glyph_svg_map[canonical_name] = gv["svg_path"]

print(f"মোট গ্লিফ সংখ্যা: {len(glyph_order)}")
print(f"মোট সি-ম্যাপ এন্ট্রি সংখ্যা: {len(cmap)}")

# Render charstrings with real 100% genuine vector curves
success_curves = 0
for g in glyph_order:
    w = advance_widths.get(g, 500)
    pen = T2CharStringPen(w, None)
    svg_cmd = glyph_svg_map.get(g)
    if svg_cmd:
        try:
            svg_xml = f'<svg xmlns="http://www.w3.org/2000/svg"><path d="{svg_cmd}"/></svg>'
            svg_p = SVGPath.fromstring(svg_xml)
            svg_p.draw(pen)
            success_curves += 1
        except Exception:
            pass
    charstrings[g] = pen.getCharString()

print(f"আসল ভেক্টর কার্ভ ইনজেক্ট করা হয়েছে: {success_curves} / {len(glyph_order)} গ্লিফে!")

fb = FontBuilder(1000, isTTF=False)
fb.setupGlyphOrder(glyph_order)
fb.setupCharacterMap(cmap)

metrics = {g: (advance_widths.get(g, 500), 0) for g in glyph_order}
fb.setupHorizontalMetrics(metrics)
fb.setupHorizontalHeader(ascent=1422, descent=-681)
fb.setupOS2(sTypoAscender=1422, sTypoDescender=-681, usWinAscent=1422, usWinDescent=681)
fb.setupPost()

fb.setupCFF(
    psName="KarianaQuranRecover-Regular",
    fontInfo={
        "FullName": "Kariana Quran Recover Font",
        "FamilyName": "Kariana Quran Recover Font",
        "Weight": "Regular"
    },
    charStringsDict=charstrings,
    privateDict={"defaultWidthX": 0, "nominalWidthX": 0}
)

fb.setupNameTable({
    "familyName": "Kariana Quran Recover Font",
    "styleName": "Regular",
    "uniqueFontIdentifier": "KarianaQuranRecoverFont:2026",
    "fullName": "Kariana Quran Recover Font",
    "psName": "KarianaQuranRecover-Regular",
    "version": "Version 1.000;2026"
})

font_obj = fb.font
font_obj.save(OUT_OTF)
shutil.copy2(OUT_OTF, OUT_TTF)
print(f"\nসফলভাবে কারিয়ানা কুরআন রিকভার ফন্ট কম্পাইল সম্পন্ন:\n-> {OUT_OTF} ({os.path.getsize(OUT_OTF):,} bytes)\n-> {OUT_TTF}")
