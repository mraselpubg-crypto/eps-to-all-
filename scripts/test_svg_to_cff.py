import os
import sys
import json
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.svgLib.path import SVGPath

sys.stdout.reconfigure(encoding="utf-8")

MASTER_JSON = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs\master_973_all_glyphs.json"

with open(MASTER_JSON, "r", encoding="utf-8") as f:
    m = json.load(f)

gv = next(iter(m['AnicaKariSAKQPlain']['glyphs']['A'].values()))
svg = gv['svg_path']
svg_xml = f'<svg xmlns="http://www.w3.org/2000/svg"><path d="{svg}"/></svg>'

p = SVGPath.fromstring(svg_xml)
pen = T2CharStringPen(gv['width'], None)
p.draw(pen)
cs = pen.getCharString()

print("CharString program length:", len(cs.program))
print("Sample program tokens:", cs.program[:15])
cs.compile()
print(f"কম্পাইল্ড বাইটকোড দৈর্ঘ্য: {len(cs.bytecode)} বাইট!")
