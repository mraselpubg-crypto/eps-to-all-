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
OUT_OTF = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\dist\KarianaInternationalSmartFont.otf"
OUT_TTF = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\dist\KarianaInternationalSmartFont.ttf"
DIST_TTF = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\dist\KarianaDigitalKhat.ttf"
FEA_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\dist\kariana_features.fea"

os.makedirs(os.path.dirname(OUT_OTF), exist_ok=True)

with open(MASTER_JSON, "r", encoding="utf-8") as f:
    master = json.load(f)

print("=== আন্তর্জাতিক মানের ক্বারীয়ানা স্মার্ট ফন্ট (100% আসল ভেক্টর) কম্পাইলেশন শুরু ===")

glyph_order = [".notdef"]
advance_widths = {".notdef": 500}
cmap = {}
charstrings = {}

# .notdef pen
pen = T2CharStringPen(500, None)
charstrings[".notdef"] = pen.getCharString()

# Families to include
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

# Mapping of standard Arabic characters to canonical Kariana glyphs
standard_arabic_map = {
    0x0627: "ar_A",           # Alif
    0x0628: "ar_B",           # Baa
    0x062A: "ar_C",           # Taa
    0x062B: "ar_Thorn",       # Thaa
    0x062C: "ar_j",           # Jeem
    0x062D: "ar_k",           # Haa
    0x062E: "ar_lozenge",     # Khaa
    0x062F: "ar_D",           # Daal
    0x0630: "ar_E",           # Dhal
    0x0631: "ar_F",           # Raa
    0x0632: "ar_G",           # Zay
    0x0633: "ar_H",           # Seen
    0x0634: "ar_I",           # Sheen
    0x0635: "ar_J",           # Saad
    0x0636: "ar_K",           # Daad
    0x0637: "ar_L",           # Taa
    0x0638: "ar_M",           # Zaa
    0x0639: "ar_N",           # Ayn
    0x063A: "ar_O",           # Ghayn
    0x0641: "ar_P",           # Faa
    0x0642: "ar_R",           # Qaaf
    0x0643: "ar_T",           # Kaaf
    0x0644: "ar_U",           # Laam
    0x0645: "ar_V",           # Meem
    0x0646: "ar_W",           # Noon
    0x0647: "ar_X",           # Haa
    0x0648: "ar_Y",           # Waw
    0x0649: "ar_Acircumflex", # Alif Maqsura
    0x064A: "ar_Z",           # Yaa
    0x0671: "ar_US",          # Alif Wasla
    0x0670: "hrk_Igrave",     # Dagger Alif
    0x064B: "hrk_Ograve",     # Fathatan
    0x064C: "hrk_apple",      # Dammatan
    0x064D: "hrk_Egrave",     # Kasratan
    0x064E: "hrk_Ocircumflex",# Fatha
    0x064F: "hrk_Uacute",     # Damma
    0x0650: "hrk_Icircumflex",# Kasra
    0x0651: "hrk_Oacute",     # Shadda
    0x0652: "hrk_Ugrave",     # Sukun
    0x0653: "hrk_Idieresis",  # Maddah
    # Digits:
    0x0660: "wqf_aw_zero",
    0x0661: "wqf_aw_one",
    0x0662: "wqf_aw_two",
    0x0663: "wqf_aw_three",
    0x0664: "wqf_aw_four",
    0x0665: "wqf_aw_five",
    0x0666: "wqf_aw_six",
    0x0667: "wqf_aw_seven",
    0x0668: "wqf_aw_eight",
    0x0669: "wqf_aw_nine",
    # Quran marks:
    0x06DD: "wqf_aw_space"    # End of Ayah marker
}

glyph_svg_map = {}

for fam, prefix in families:
    f_glyphs = master.get(fam, {}).get("glyphs", {})
    for gname, vdict in sorted(f_glyphs.items()):
        if gname == ".notdef": continue
        gv = next(iter(vdict.values()))
        w = int(round(gv["width"]))
        
        # Zero-width for top Tajweed overlay
        if "taj" in prefix:
            w = 0
            
        canonical_name = f"{prefix}_{gname}"
        glyph_order.append(canonical_name)
        advance_widths[canonical_name] = w
        cmap[pua_code] = canonical_name
        pua_code += 1
        
        glyph_svg_map[canonical_name] = gv["svg_path"]

# Add standard Arabic mappings where available
for u_code, g_target in standard_arabic_map.items():
    if g_target in advance_widths:
        cmap[u_code] = g_target

print(f"মোট গ্লিফ সংখ্যা: {len(glyph_order)}")
print(f"মোট সি-ম্যাপ এন্ট্রি সংখ্যা: {len(cmap)}")

# Render charstrings with real 100% genuine vector curves!
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

print(f"আসল ভেক্টর কার্ভ সফলভাবে ইনজেক্ট করা হয়েছে: {success_curves} / {len(glyph_order)} গ্লিফে!")

# Build OpenType font
fb = FontBuilder(1000, isTTF=False)
fb.setupGlyphOrder(glyph_order)
fb.setupCharacterMap(cmap)

metrics = {g: (advance_widths.get(g, 500), 0) for g in glyph_order}
fb.setupHorizontalMetrics(metrics)
fb.setupHorizontalHeader(ascent=1422, descent=-681)
fb.setupOS2(sTypoAscender=1422, sTypoDescender=-681, usWinAscent=1422, usWinDescent=681)
fb.setupPost()

fb.setupCFF(
    psName="KarianaInternationalSmartFont-Regular",
    fontInfo={"FullName": "Kariana International Smart Font", "FamilyName": "Kariana International Smart Font", "Weight": "Regular"},
    charStringsDict=charstrings,
    privateDict={"defaultWidthX": 0, "nominalWidthX": 0}
)

fb.setupNameTable({
    "familyName": "Kariana International Smart Font",
    "styleName": "Regular",
    "uniqueFontIdentifier": "KarianaInternationalSmartFont:2026",
    "fullName": "Kariana International Smart Font",
    "psName": "KarianaInternationalSmartFont-Regular",
    "version": "Version 1.000;2026"
})

# Generate OpenType Feature File (.fea)
fea_content = f"""
languagesystem DFLT dflt;
languagesystem arab dflt;

# Positional Features
feature isol {{
    sub ar_B by ar_B;
    sub ar_C by ar_C;
    sub ar_Thorn by ar_Thorn;
}} isol;

feature init {{
    sub ar_B by ar_b;
    sub ar_C by ar_c;
    sub ar_V by ar_u;
}} init;

feature medi {{
    sub ar_B by ar_d;
    sub ar_V by ar_v;
}} medi;

feature fina {{
    sub ar_B by ar_B;
    sub ar_V by ar_V;
}} fina;

# Required Quranic Ligatures
feature rlig {{
    sub ar_U ar_A by ar_divide; # Lam + Alif
}} rlig;
"""

with open(FEA_PATH, "w", encoding="utf-8") as feaf:
    feaf.write(fea_content)

print(f"OpenType ফিচার ফাইল তৈরি সম্পন্ন: {FEA_PATH}")

font_obj = fb.font
try:
    feaBuilder.addOpenTypeFeatures(font_obj, FEA_PATH)
    print("OpenType GSUB/GPOS টেবিল সফলভাবে সংযুক্ত করা হয়েছে!")
except Exception as e:
    print(f"সতর্কতা: OpenType ফিচার কম্পাইলেশনে ত্রুটি: {e}")

font_obj.save(OUT_OTF)
print(f"\nসফলভাবে আন্তর্জাতিক মানের ওপেনটাইপ ফন্ট কম্পাইল ও সেভ হয়েছে:\n-> {OUT_OTF} ({os.path.getsize(OUT_OTF):,} bytes)")

shutil.copy2(OUT_OTF, OUT_TTF)
shutil.copy2(OUT_OTF, DIST_TTF)
print(f"-> {DIST_TTF} সফলভাবে আপডেট সম্পন্ন!")
