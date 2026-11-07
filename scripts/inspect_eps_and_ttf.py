import sys
import os
import re
import struct
from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding="utf-8")

eps_path = r"C:\xampp\htdocs\Bipul code craft Api\KariSAKQ_Para-01_21.eps"
with open(eps_path, "rb") as f:
    data = f.read()

magic = data[:4]
ps_offset, ps_len, wmf_off, wmf_len, tiff_off, tiff_len = struct.unpack("<6I", data[4:28])
ps_bytes = data[ps_offset : ps_offset + ps_len]
ps_text = ps_bytes.decode("latin1")

# Inspect one Initial block and one AddGlyphs block in detail
init_match = re.search(r"%ADOBeginSubsetFont:\s*AnicaKariSAKQPlain Initial(.*?)%ADOEndSubsetFont", ps_text, re.S)
if init_match:
    blk = init_match.group(1)
    print("=== Sample Initial Block (AnicaKariSAKQPlain Initial) ===")
    # print ASCII parts cleanly
    print(repr(blk[:1200]))
    print("...")
    print(repr(blk[-400:]))

add_match = re.search(r"%ADOBeginSubsetFont:\s*AnicaKariSAKQPlain AddGlyphs(.*?)%ADOEndSubsetFont", ps_text, re.S)
if add_match:
    blk = add_match.group(1)
    print("\n=== Sample AddGlyphs Block (AnicaKariSAKQPlain AddGlyphs) ===")
    print(repr(blk[:800]))

# Inspect nfnt definitions properly (single or multi-line ASCII array)
nfnts = re.findall(r"/([A-Za-z0-9_\-\*]+)\s*\[\s*((?:[0-9]+\{/\.notdef\}repeat|/[A-Za-z0-9_\.\-]+|\s)+)\]\s*/([A-Za-z0-9_\-]+)\s+nfnt", ps_text)
print(f"\n=== Clean nfnt definitions ({len(nfnts)}) ===")
for subname, enc, base in nfnts[:30]:
    enc_clean = " ".join(enc.split())
    print(f"  {subname} -> {base} : [{enc_clean[:100]}]")

# Inspect page stream operators around the first text drawing commands
idx = ps_text.find("AnicaKariSAKQPlain*1")
if idx != -1:
    print("\n=== Stream around AnicaKariSAKQPlain*1 ===")
    snippet = ps_text[max(0, idx - 300) : idx + 2500]
    # filter out binary font blocks if any
    cleaned = re.sub(r"%ADOBeginSubsetFont:.*?%ADOEndSubsetFont", "[...SUBSET_FONT_BLOCK...]", snippet, flags=re.S)
    print(cleaned)

# Inspect the two subset TTFs
for ttf_name in ["NFKLOO+AnicaKariSAKQPlain.ttf", "NFKLPA+AnicaKariSAKQHarkat.ttf"]:
    p = rf"C:\xampp\htdocs\Bipul code craft Api\{ttf_name}"
    tt = TTFont(p)
    glyphs = tt.getGlyphOrder()
    print(f"\n=== TTF: {ttf_name} ===")
    print(f"  UPM: {tt['head'].unitsPerEm} | Tables: {list(tt.keys())} | Glyphs ({len(glyphs)}): {glyphs}")
    for cmap_table in tt["cmap"].tables:
        if cmap_table.cmap:
            print(f"  cmap (plat={cmap_table.platformID}, enc={cmap_table.platEncID}): {cmap_table.cmap}")
