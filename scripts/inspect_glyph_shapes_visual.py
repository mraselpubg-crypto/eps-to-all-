import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

FONTS_JSON = r"extracted_data\eps_page21\eps_page21_fonts.json"

with open(FONTS_JSON, "r", encoding="utf-8") as f:
    fonts = json.load(f)

plain = fonts.get("AnicaKariSAKQPlain", {}).get("glyphs", {})

for gname in ["Zcaron", "K", "O", "N", "r", "eth", "H", "b", "Edieresis", "onequarter"]:
    ginfo = plain.get(gname, {})
    print(f"Glyph '{gname:12s}': width={ginfo.get('width')}, bounds={ginfo.get('bounds')}")
