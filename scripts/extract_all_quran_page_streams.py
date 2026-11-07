import os
import sys
import json
import time
import pymupdf

sys.stdout.reconfigure(encoding="utf-8")

PDF_PATH = r"C:\Users\Rasel Gazi\OneDrive\Documents\kariana quran full.pdf"
OUT_DIR = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\all_pages_streams"
os.makedirs(OUT_DIR, exist_ok=True)

# MacRoman / AGL map for special characters
MAC_GLYPH_NAMES = {
    0x017D: "Zcaron",
    0xF8FF: "apple",
    0x00DA: "Uacute",
    0x00D3: "Oacute",
    0x00DB: "Ucircumflex",
    0x00D4: "Ocircumflex",
    0x00C9: "Eacute",
    0x00CA: "Ecircumflex",
    0x00CB: "Edieresis",
    0x00C8: "Egrave",
    0x00CD: "Iacute",
    0x00CE: "Icircumflex",
    0x00CF: "Idieresis",
    0x00CC: "Igrave",
    0x00C0: "Agrave",
    0x00C1: "Aacute",
    0x00C2: "Acircumflex",
    0x00C3: "Atilde",
    0x00C4: "Adieresis",
    0x00C5: "Aring",
    0x00C7: "Ccedilla",
    0x00D1: "Ntilde",
    0x00D2: "Ograve",
    0x00D5: "Otilde",
    0x00D6: "Odieresis",
    0x00D8: "Oslash",
    0x00DC: "Udieresis",
    0x00E0: "agrave",
    0x00E1: "aacute",
    0x00E2: "acircumflex",
    0x00E3: "atilde",
    0x00E4: "adieresis",
    0x00E5: "aring",
    0x00E7: "ccedilla",
    0x00E8: "egrave",
    0x00E9: "eacute",
    0x00EA: "ecircumflex",
    0x00EB: "edieresis",
    0x00EC: "igrave",
    0x00ED: "iacute",
    0x00EE: "icircumflex",
    0x00EF: "idieresis",
    0x00F1: "ntilde",
    0x00F2: "ograve",
    0x00F3: "oacute",
    0x00F4: "ocircumflex",
    0x00F5: "otilde",
    0x00F6: "odieresis",
    0x00F8: "oslash",
    0x00F9: "ugrave",
    0x00FA: "uacute",
    0x00FB: "ucircumflex",
    0x00FC: "udieresis",
    0x00D0: "Eth",
    0x00F0: "eth",
    0x0141: "Lslash",
    0x0142: "lslash",
    0x00AB: "guillemotleft",
    0x00BB: "guillemotright",
    0x00BC: "onequarter",
    0x00BD: "onehalf",
    0x00BE: "threequarters",
    0x00B1: "plusminus",
    0x00F7: "divide",
    0x00D7: "multiply",
    0x00DF: "germandbls",
    0x00E6: "ae",
    0x00C6: "AE",
    0x00A7: "section",
    0x00B6: "paragraph",
    0x00A9: "copyright",
    0x00AE: "registered",
    0x2018: "quoteleft",
    0x2019: "quoteright",
    0x201C: "quotedblleft",
    0x201D: "quotedblright",
    0x2022: "bullet",
    0x2026: "ellipsis",
    0x20AC: "Euro",
    0x00A0: "space",
    0x0020: "space"
}

def get_glyph_name(ch):
    o = ord(ch)
    if o in MAC_GLYPH_NAMES:
        return MAC_GLYPH_NAMES[o]
    if 33 <= o <= 126:
        # Standard ASCII
        return ch
    return f"uni{o:04X}"

print("=== সম্পূর্ণ ৯৭৩ পৃষ্ঠার কুরআন গ্লিফ-স্ট্রিম অটো-এক্সট্রাকশন পাইপলাইন চালু ===")
doc = pymupdf.open(PDF_PATH)
t0 = time.time()

# Extract from Page 11 (Surah Fatiha) to Page 973
total_extracted_pages = 0
total_events = 0

master_catalog = []

for pdf_idx in range(10, len(doc)):
    printed_page = pdf_idx - 9  # Page 11 is printed page 1 (Surah Fatiha)
    page = doc[pdf_idx]
    
    text_data = page.get_text("rawjson")
    page_json = json.loads(text_data)
    
    events = []
    
    for block in page_json.get("blocks", []):
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                font_name = span.get("font", "").split("+")[-1]
                if not font_name.startswith("AnicaKariSAKQ") and not font_name.startswith("KariSAKQ"):
                    continue
                size = span.get("size", 26.5)
                for c in span.get("chars", []):
                    ch = c.get("c", "")
                    if not ch:
                        continue
                    gname = get_glyph_name(ch)
                    events.append({
                        "x": round(c["origin"][0], 3),
                        "y": round(c["origin"][1], 3),
                        "base_font": font_name,
                        "glyph": gname,
                        "char_code": ord(ch)
                    })
                    
    total_events += len(events)
    total_extracted_pages += 1
    
    # Save individual page JSON
    out_file = os.path.join(OUT_DIR, f"page_{printed_page:03d}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False)
        
    master_catalog.append({
        "printed_page": printed_page,
        "pdf_page": pdf_idx + 1,
        "events_count": len(events)
    })
    
    if total_extracted_pages % 100 == 0:
        print(f"  -> {total_extracted_pages}টি পৃষ্ঠা এক্সট্র্যাক্ট সম্পন্ন (মোট ইভেন্ট: {total_events:,}টি, সময়: {time.time()-t0:.1f}s)")

elapsed = time.time() - t0
print(f"\n✓ আলহামদুলিল্লাহ! সম্পূর্ণ {total_extracted_pages}টি পৃষ্ঠার গ্লিফ-স্ট্রিম এক্সট্রাকশন সফলভাবে সম্পন্ন!")
print(f"  মোট প্রক্রিয়াকৃত ইভেন্ট: {total_events:,}টি")
print(f"  মোট সময় লেগেছে: {elapsed:.2f} সেকেন্ড!")

# Save master catalog
catalog_path = os.path.join(OUT_DIR, "master_pages_catalog.json")
with open(catalog_path, "w", encoding="utf-8") as f:
    json.dump(master_catalog, f, indent=2, ensure_ascii=False)

print(f"  মাস্টার ক্যাটালগ সেভ হয়েছে: {catalog_path}")
