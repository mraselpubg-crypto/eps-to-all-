import os
import sys
import json
import zipfile
from collections import defaultdict
import pymupdf

sys.stdout.reconfigure(encoding="utf-8")

PDF_PATH = r"C:\Users\Rasel Gazi\OneDrive\Documents\kariana quran full.pdf"
ZIP_PATH = r"C:\Users\Rasel Gazi\OneDrive\KariSAKQ Para-01 Folder.zip"
OUT_DIR = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data"
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Check KariSAKQ Para-01 Folder.zip safely
if os.path.exists(ZIP_PATH):
    try:
        with zipfile.ZipFile(ZIP_PATH, "r") as zf:
            print("=== Contents of KariSAKQ Para-01 Folder.zip ===")
            for info in zf.infolist():
                print(f"  {info.filename} ({info.file_size:,} bytes)")
    except Exception as e:
        print(f"(Skipping OneDrive cloud-only zip: {e})")

# 2. Scan all 973 pages of kariana quran full.pdf for all embedded fonts
print(f"\n=== Scanning all pages of {PDF_PATH} ===")
doc = pymupdf.open(PDF_PATH)
print(f"Total pages: {len(doc)}")

# Map base_font_name -> set of xrefs, pages count, font types
font_xrefs = {}  # xref -> {name, ext, type, subtype, pages: [first, last, count]}
base_families = defaultdict(lambda: {"xrefs": set(), "pages": set(), "types": set()})

for pno in range(len(doc)):
    page = doc[pno]
    for f in page.get_fonts(full=True):
        # f = (xref, ext, type, basefont, name, encoding, referencer)
        xref, ext, ftype, basefont, psname, enc = f[:6]
        clean_base = basefont.split("+", 1)[1] if "+" in basefont else basefont
        base_families[clean_base]["xrefs"].add(xref)
        base_families[clean_base]["pages"].add(pno + 1)
        base_families[clean_base]["types"].add(f"{ftype}/{ext}/{enc}")
        if xref not in font_xrefs:
            font_xrefs[xref] = {
                "xref": xref,
                "basefont": basefont,
                "clean_base": clean_base,
                "ext": ext,
                "type": ftype,
                "encoding": enc,
                "first_page": pno + 1,
                "last_page": pno + 1,
                "page_count": 1,
            }
        else:
            font_xrefs[xref]["last_page"] = pno + 1
            font_xrefs[xref]["page_count"] += 1

print(f"\nTotal unique font xrefs across 973 pages: {len(font_xrefs)}")
print(f"Total unique clean font families across 973 pages: {len(base_families)}\n")

summary = {}
for fam in sorted(base_families.keys()):
    info = base_families[fam]
    pages_sorted = sorted(info["pages"])
    summary[fam] = {
        "xref_count": len(info["xrefs"]),
        "xrefs": sorted(info["xrefs"]),
        "page_count": len(pages_sorted),
        "first_page": pages_sorted[0],
        "last_page": pages_sorted[-1],
        "types": sorted(info["types"]),
    }
    print(
        f"  {fam:32s} | xrefs: {len(info['xrefs']):4d} | pages: {len(pages_sorted):3d} "
        f"(p.{pages_sorted[0]}..p.{pages_sorted[-1]}) | types: {sorted(info['types'])}"
    )

# Inspect how PyMuPDF extracts a sample page's rawdict / trace / content stream on Mushaf Page 21 (find exact PDF page matching KariSAKQ_Para-01_21.eps!)
# Let's check which PDF page corresponds to KariSAKQ_Para-01_21.eps!
# Note: Para 1 Page 21 in Mushaf -> let's check pages 20..35 to find exact match!
doc.close()

with open(os.path.join(OUT_DIR, "pdf_973_font_inventory.json"), "w", encoding="utf-8") as fp:
    json.dump({"families": summary, "xrefs": font_xrefs}, fp, indent=2, ensure_ascii=False)
print(f"\nSaved inventory to {os.path.join(OUT_DIR, 'pdf_973_font_inventory.json')}")
