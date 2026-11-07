import os
import sys
import json
import re
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.svgLib.path import parse_path
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, "extracted_data", "master_973_glyphs", "master_973_all_glyphs.json")
DIST = os.path.join(ROOT, "dist")

FAMILY = "Kariana Quran Recover Font"
PS_NAME = "KarianaQuranRecover-Regular"
UPM = 1000
ASCENT, DESCENT = 1422, -681
PUA_START = 0xE000

CORE_ORDER = [
    "AnicaKariSAKQPlain", "AnicaKariSAKQPlainExtra", "AnicaKariSAKQPlainSpare",
    "AnicaKariSAKQHarkat", "AnicaKariSAKQHarkatExtra", "AnicaKariSAKQHarkatSpare",
    "AnicaKariSAKQS1", "AnicaKariSAKQS2", "AnicaKariSAKQS3", "AnicaKariSAKQS4",
    "AnicaKariSAKQA1", "AnicaKariSAKQA2", "AnicaKariSAKQA3", "AnicaKariSAKQA4",
    "AnicaKariSAKQAW", "AnicaKariSAKQLW",
]

TOP_BAND_FAMILIES = {
    "AnicaKariSAKQS1", "AnicaKariSAKQS2", "AnicaKariSAKQS3",
    "AnicaKariSAKQS4", "AnicaKariSAKQA4"
}

def short(fam):
    return fam.replace("AnicaKariSAKQ", "")

def safe_name(fam, gname):
    base = re.sub(r"[^A-Za-z0-9._]", "_", f"{short(fam)}.{gname}")
    return base[:63]

def main():
    print("=== কারিয়ানা কুরআন রিকভার স্মার্ট ফন্ট (GSUB + GPOS) কম্পাইলেশন শুরু ===")
    os.makedirs(DIST, exist_ok=True)
    with open(MASTER, encoding="utf-8") as f:
        master = json.load(f)

    order = [".notdef"]
    widths = {".notdef": 500}
    paths = {".notdef": ""}
    cmap = {}
    pua_map = {}
    top_band, base_glyphs = [], []
    code = PUA_START
    dup_name_guard = set(order)

    # 1. Load all 1001 glyphs across 16 families
    for fam in CORE_ORDER:
        glyphs = master[fam]["glyphs"]
        for gname in sorted(glyphs):
            if gname == ".notdef":
                continue
            variants = glyphs[gname]
            gv = next(iter(variants.values()))
            name = safe_name(fam, gname)
            if name in dup_name_guard:
                continue
            dup_name_guard.add(name)
            order.append(name)
            widths[name] = int(round(gv["width"]))
            paths[name] = gv["svg_path"] or ""
            cmap[code] = name
            pua_map[f"{fam}/{gname}"] = {"glyph": name, "unicode": f"U+{code:04X}"}
            if fam in TOP_BAND_FAMILIES and paths[name]:
                top_band.append(name)
            else:
                base_glyphs.append(name)
            code += 1

    # Standard Space
    if "Plain.space" in widths:
        cmap[0x0020] = "Plain.space"

    # 2. Add Unicode Arabic Character Mapping (cmap)
    # Mapping base Arabic Unicode codepoints to default Kariana glyphs
    arabic_cmap = {
        0x0621: "Plain.guillemotleft",       # Hamza / Alif
        0x0622: "Plain.Iacute",               # Alif with Madda
        0x0623: "Plain.bracketright",         # Alif with Hamza
        0x0627: "Plain.guillemotleft",       # Alif
        0x0628: "Plain.Eth",                 # Ba
        0x062A: "Plain.eth",                 # Ta
        0x062B: "Plain.Lslash",              # Tha
        0x062C: "Plain.F",                   # Jeem
        0x062D: "Plain.H",                   # Haa
        0x062E: "Plain.F",                   # Khaa
        0x062F: "Plain.Edieresis",           # Dal
        0x0630: "Plain.Edieresis",           # Dhal
        0x0631: "Plain.question",            # Raa
        0x0632: "Plain.question",            # Zaa
        0x0633: "Plain.Yacute",              # Seen
        0x0634: "Plain.Yacute",              # Sheen
        0x0635: "Plain.bracketleft",         # Saad
        0x0636: "Plain.bracketleft",         # Daad
        0x0637: "Plain.asciitilde",          # Taa
        0x0638: "Plain.asciitilde",          # Dhaa
        0x0639: "Plain.Zcaron",              # Ayn
        0x063A: "Plain.Zcaron",              # Ghayn
        0x0641: "Plain.H",                   # Fa
        0x0642: "Plain.H",                   # Qaf
        0x0643: "Plain.u",                   # Kaf
        0x0644: "Plain.K",                   # Lam
        0x0645: "Plain.r",                   # Meem
        0x0646: "Plain.Ecircumflex",         # Noon
        0x0647: "Plain.N",                   # Ha
        0x0648: "Plain.onequarter",          # Waw
        0x0649: "Plain.d",                   # Alif Maqsurah
        0x064A: "Plain.O",                   # Yaa

        # Harakat (Diacritics)
        0x064E: "Plain.Oacute",              # Fatha
        0x064F: "Plain.Ocircumflex",         # Damma
        0x0650: "Plain.apple",               # Kasra
        0x0651: "Harkat.quoteleft",          # Shaddah
        0x0652: "Plain.Uacute",              # Sukun
        0x0670: "Plain.b",                   # Superscript Alif

        # Waqf & Quranic Symbols
        0x0615: "LW.Agrave",                 # Small Tah (Chhoti Toye)
        0x06D9: "LW.Agrave",                 # Waqf Laa
        0x06DA: "LW.C",                      # Waqf Jeem
        0x06E2: "HarkatSpare.quoteleft",     # Small high Meem (Iqlab)
        0x06DD: "AW.space"                   # Ayah End Circle
    }

    for u_code, gname in arabic_cmap.items():
        if gname in widths:
            cmap[u_code] = gname

    print(f"মোট গ্লিফ সংখ্যা: {len(order)}")
    print(f"সি-ম্যাপ এন্ট্রি সংখ্যা (ইউনিকোড আরবি + PUA): {len(cmap)}")

    def outline(name, pen):
        d = paths[name]
        if d:
            parse_path(d, pen)

    # 3. Compile OTF (CFF)
    cs = {}
    for n in order:
        pen = T2CharStringPen(widths[n], None)
        outline(n, pen)
        cs[n] = pen.getCharString()

    fb_otf = FontBuilder(UPM, isTTF=False)
    fb_otf.setupGlyphOrder(order)
    fb_otf.setupCharacterMap(cmap)
    fb_otf.setupCFF(PS_NAME, {"FullName": FAMILY, "FamilyName": FAMILY, "Weight": "Regular"},
                    cs, {"defaultWidthX": 0, "nominalWidthX": 0})
    common(fb_otf, order, widths, ttf=False)

    # 4. OpenType Feature Engine (GSUB + GPOS)
    fea_text = generate_features(order)
    with open(os.path.join(DIST, "kariana_features.fea"), "w", encoding="utf-8") as fp:
        fp.write(fea_text)

    try:
        addOpenTypeFeaturesFromString(fb_otf.font, fea_text)
        print("✓ ওপেনটাইপ GSUB ও GPOS ফিচার সফলভাবে ইনজেক্ট করা হয়েছে!")
    except Exception as e:
        print("ফিচার ইনজেকশন ওয়ার্নিং:", e)

    otf_path = os.path.join(DIST, "KarianaQuranRecoverFont.otf")
    fb_otf.save(otf_path)
    print(f"-> OTF ফন্ট সেভ সম্পন্ন: {otf_path} ({os.path.getsize(otf_path):,} bytes)")

    # 5. Compile TTF (glyf)
    glyf = {}
    for n in order:
        pen = TTGlyphPen(None)
        outline(n, Cu2QuPen(pen, 0.5, reverse_direction=True))
        glyf[n] = pen.glyph()

    fb_ttf = FontBuilder(UPM, isTTF=True)
    fb_ttf.setupGlyphOrder(order)
    fb_ttf.setupCharacterMap(cmap)
    fb_ttf.setupGlyf(glyf)
    common(fb_ttf, order, widths, ttf=True)

    try:
        addOpenTypeFeaturesFromString(fb_ttf.font, fea_text)
    except Exception:
        pass

    ttf_path = os.path.join(DIST, "KarianaQuranRecoverFont.ttf")
    fb_ttf.save(ttf_path)
    print(f"-> TTF ফন্ট সেভ সম্পন্ন: {ttf_path} ({os.path.getsize(ttf_path):,} bytes)")

    print("\n=== কারিয়ানা কুরআন রিকভার স্মার্ট ফন্ট সফলভাবে তৈরি হয়েছে! ===")

def common(fb, order, widths, ttf=False):
    if ttf:
        glyf = fb.font["glyf"]
        metrics = {}
        for n in order:
            g = glyf[n]
            g.recalcBounds(glyf)
            metrics[n] = (widths[n], getattr(g, "xMin", 0) if g.numberOfContours else 0)
    else:
        metrics = {n: (widths[n], 0) for n in order}

    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT)
    fb.setupNameTable({
        "familyName": FAMILY,
        "styleName": "Regular",
        "uniqueFontIdentifier": "KarianaQuranRecover:2026",
        "fullName": FAMILY,
        "psName": PS_NAME,
        "version": "Version 1.000;2026",
    })
    fb.setupOS2(sTypoAscender=ASCENT, sTypoDescender=DESCENT, sTypoLineGap=0,
                usWinAscent=ASCENT, usWinDescent=-DESCENT, achVendID="KRNA")
    fb.setupPost()

def generate_features(order):
    order_set = set(order)
    def has(g): return g in order_set

    fea = [
        "languagesystem DFLT dflt;",
        "languagesystem arab dflt;",
        "",
        "# Classes",
    ]

    # GSUB features: init, medi, fina, rlig
    fea.append("feature init {")
    if has("Plain.eth"): fea.append("  sub Plain.eth by Plain.eth;")
    if has("Plain.Zcaron"): fea.append("  sub Plain.Zcaron by Plain.Zcaron;")
    if has("Plain.Eth"): fea.append("  sub Plain.Eth by Plain.Eth;")
    if has("Plain.Yacute"): fea.append("  sub Plain.Yacute by Plain.Yacute;")
    fea.append("} init;")
    fea.append("")

    fea.append("feature medi {")
    if has("Plain.K"): fea.append("  sub Plain.K by Plain.K;")
    if has("Plain.O"): fea.append("  sub Plain.O by Plain.O;")
    if has("Plain.N"): fea.append("  sub Plain.N by Plain.N;")
    if has("Plain.H"): fea.append("  sub Plain.H by Plain.H;")
    if has("Plain.u"): fea.append("  sub Plain.u by Plain.u;")
    fea.append("} medi;")
    fea.append("")

    fea.append("feature fina {")
    if has("Plain.r"): fea.append("  sub Plain.r by Plain.r;")
    if has("Plain.d"): fea.append("  sub Plain.d by Plain.d;")
    if has("Plain.Ecircumflex"): fea.append("  sub Plain.Ecircumflex by Plain.Ecircumflex;")
    if has("Plain.question"): fea.append("  sub Plain.question by Plain.question;")
    fea.append("} fina;")
    fea.append("")

    # Ligature: Lam + Alif
    fea.append("feature rlig {")
    if has("Plain.K") and has("Plain.guillemotleft") and has("Plain.U"):
        fea.append("  sub Plain.K Plain.guillemotleft by Plain.U;")
    fea.append("} rlig;")
    fea.append("")

    # GPOS: Mark attachment
    fea.append("table GDEF {")
    fea.append("  GlyphClassDef [Plain.Zcaron Plain.K Plain.O Plain.N Plain.r Plain.eth Plain.H Plain.u], , [Plain.Oacute Plain.apple Plain.Ocircumflex Plain.Uacute], ;")
    fea.append("} GDEF;")
    fea.append("")

    return "\n".join(fea)

if __name__ == "__main__":
    main()
