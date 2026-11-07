import os
import sys
import json
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.svgLib.path import parse_path

sys.stdout.reconfigure(encoding="utf-8")

MASTER_JSON = "extracted_data/master_973_glyphs/master_973_all_glyphs.json"
OUT_DIR = "source_fonts"
os.makedirs(OUT_DIR, exist_ok=True)

with open(MASTER_JSON, "r", encoding="utf-8") as f:
    master = json.load(f)

UPM = 1000
ASCENT, DESCENT = 1422, -681

families = ["AnicaKariSAKQS1", "AnicaKariSAKQS2", "AnicaKariSAKQS3", "AnicaKariSAKQS4"]

for fam in families:
    f_glyphs = master.get(fam, {}).get("glyphs", {})
    order = [".notdef"]
    widths = {".notdef": 500}
    paths = {".notdef": ""}
    cmap = {}
    code = 0xE000
    
    for gname, vdict in sorted(f_glyphs.items()):
        if gname == ".notdef":
            continue
        gv = next(iter(vdict.values()))
        order.append(gname)
        widths[gname] = int(round(gv.get("width", 0)))
        paths[gname] = gv.get("svg_path", "") or ""
        cmap[code] = gname
        code += 1
        
    glyf = {}
    for n in order:
        pen = TTGlyphPen(None)
        d = paths[n]
        if d:
            parse_path(d, Cu2QuPen(pen, 0.5, reverse_direction=True))
        glyf[n] = pen.glyph()
        
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf)
    
    metrics = {}
    gtable = fb.font["glyf"]
    for n in order:
        g = gtable[n]
        g.recalcBounds(gtable)
        metrics[n] = (widths[n], getattr(g, "xMin", 0) if g.numberOfContours else 0)
        
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT)
    fb.setupNameTable({
        "familyName": fam,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{fam}:2026",
        "fullName": fam,
        "psName": f"{fam}-Regular",
        "version": "Version 1.000;2026"
    })
    fb.setupOS2(sTypoAscender=ASCENT, sTypoDescender=DESCENT, usWinAscent=ASCENT, usWinDescent=-DESCENT)
    fb.setupPost()
    
    out_path = os.path.join(OUT_DIR, f"{fam}.ttf")
    fb.save(out_path)
    print(f"সফলভাবে তৈরি হয়েছে: {out_path} ({len(order)} গ্লিফ, {os.path.getsize(out_path):,} bytes)")

print("\nS1 থেকে S4-এর ৪টি TTF ফন্ট তৈরি সম্পন্ন!")
