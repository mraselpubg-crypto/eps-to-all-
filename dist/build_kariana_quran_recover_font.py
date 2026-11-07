#!/usr/bin/env python3
"""
Kariana Quran Recover Font builder.

Reads the decrypted original vectors (master_973_all_glyphs.json) and compiles
  dist/KarianaQuranRecoverFont.otf   (CFF, lossless cubic curves)
  dist/KarianaQuranRecoverFont.ttf   (glyf, cubic->quadratic, max error 0.5 unit)
plus dist/kariana_recover_pua_map.json  (family/glyph -> PUA code point).

Only the 16 core AnicaKariSAKQ* families are used (no outside glyphs).
Every (family, glyph) keeps its own glyph, so the original 973-page layout
can be reproduced glyph-for-glyph through the PUA map.
"""
import json
import os
import re
import sys

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path

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
TOP_BAND_FAMILIES = {"AnicaKariSAKQS1", "AnicaKariSAKQS2", "AnicaKariSAKQS3",
                     "AnicaKariSAKQS4", "AnicaKariSAKQA4"}


def short(fam):
    return fam.replace("AnicaKariSAKQ", "")


def safe_name(fam, gname):
    base = re.sub(r"[^A-Za-z0-9._]", "_", f"{short(fam)}.{gname}")
    return base[:63]


def main():
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

    for fam in CORE_ORDER:
        glyphs = master[fam]["glyphs"]
        for gname in sorted(glyphs):
            if gname == ".notdef":
                continue
            variants = glyphs[gname]
            assert len(variants) == 1, f"{fam}/{gname}: multi-variant"
            gv = next(iter(variants.values()))
            name = safe_name(fam, gname)
            assert name not in dup_name_guard, name
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
    assert code <= 0xF8FF, "PUA overflow"

    # Plain 'space' also answers to U+0020 for convenience
    if "Plain.space" in widths:
        cmap[0x0020] = "Plain.space"

    def outline(name, pen):
        d = paths[name]
        if d:
            parse_path(d, pen)

    # ---------- OTF (CFF) ----------
    cs = {}
    for n in order:
        pen = T2CharStringPen(widths[n], None)
        outline(n, pen)
        cs[n] = pen.getCharString()
    fb = FontBuilder(UPM, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupCFF(PS_NAME, {"FullName": FAMILY, "FamilyName": FAMILY, "Weight": "Regular"},
                cs, {"defaultWidthX": 0, "nominalWidthX": 0})
    common(fb, order, widths)
    add_gdef(fb.font, base_glyphs, top_band)
    otf_path = os.path.join(DIST, "KarianaQuranRecoverFont.otf")
    fb.save(otf_path)

    # ---------- TTF (glyf) ----------
    glyf = {}
    for n in order:
        pen = TTGlyphPen(None)
        outline(n, Cu2QuPen(pen, 0.5, reverse_direction=True))
        glyf[n] = pen.glyph()
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf)
    common(fb, order, widths, ttf=True)
    add_gdef(fb.font, base_glyphs, top_band)
    ttf_path = os.path.join(DIST, "KarianaQuranRecoverFont.ttf")
    fb.save(ttf_path)

    with open(os.path.join(DIST, "kariana_recover_pua_map.json"), "w", encoding="utf-8") as f:
        json.dump(pua_map, f, ensure_ascii=False, indent=1)

    zero_ok = sum(1 for n in top_band if widths[n] == 0)
    print(f"glyphs: {len(order)}  cmap entries: {len(cmap)}  PUA used: U+E000..U+{code-1:04X}")
    print(f"top-band glyphs: {len(top_band)} (advance 0: {zero_ok})")
    print(f"wrote {otf_path} ({os.path.getsize(otf_path)} B)")
    print(f"wrote {ttf_path} ({os.path.getsize(ttf_path)} B)")


def common(fb, order, widths, ttf=False):
    # glyph bounds for lsb come from the outlines automatically in TTF; for CFF use 0
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


def add_gdef(font, bases, marks):
    fea = (
        "@BASES = [" + " ".join(bases) + "];\n"
        "@MARKS = [" + " ".join(marks) + "];\n"
        "table GDEF { GlyphClassDef @BASES, , @MARKS, ; } GDEF;\n"
    )
    addOpenTypeFeaturesFromString(font, fea, tables=["GDEF"])


if __name__ == "__main__":
    sys.exit(main())
