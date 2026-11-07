import os
import sys
from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding="utf-8")

for path in ["reference_fonts/KFGQPCNastaleeq-Regular.ttf", "reference_fonts/DigitalKhattIndoPak.otf"]:
    print(f"\n=================== {os.path.basename(path)} ===================")
    font = TTFont(path)
    print("Tables:", list(font.keys()))
    print("Glyph count:", len(font.getGlyphOrder()))
    
    # Check GSUB
    if "GSUB" in font:
        gsub = font["GSUB"].table
        scripts = [s.ScriptTag for s in gsub.ScriptList.ScriptRecord]
        features = [f.FeatureTag for f in gsub.FeatureList.FeatureRecord]
        print("GSUB Scripts:", scripts)
        print("GSUB Features:", set(features))
        print("GSUB Feature Count:", len(gsub.FeatureList.FeatureRecord))
        print("GSUB Lookup Count:", len(gsub.LookupList.Lookup))
    else:
        print("No GSUB table")
        
    # Check GPOS
    if "GPOS" in font:
        gpos = font["GPOS"].table
        features = [f.FeatureTag for f in gpos.FeatureList.FeatureRecord]
        print("GPOS Features:", set(features))
        print("GPOS Lookup Count:", len(gpos.LookupList.Lookup))
    else:
        print("No GPOS table")
        
    # Check cmap
    cmap = font.getBestCmap()
    if cmap:
        print(f"Mapped Unicode characters: {len(cmap)}")
        # Check Arabic range 0x0600 - 0x06FF
        arabic_chars = [c for c in cmap if 0x0600 <= c <= 0x06FF or 0x08A0 <= c <= 0x08FF or 0xFB50 <= c <= 0xFDFF or 0xFE70 <= c <= 0xFEFF]
        print(f"Arabic characters mapped: {len(arabic_chars)}")
