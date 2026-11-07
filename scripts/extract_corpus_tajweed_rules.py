import os
import sys
import json
import pymupdf
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding="utf-8")

PDF_PATH = r"C:\Users\Rasel Gazi\OneDrive\Documents\kariana quran full.pdf"

doc = pymupdf.open(PDF_PATH)
print(f"পিডিএফ লোড সম্পন্ন: মোট {len(doc)} পৃষ্ঠা")

# We want to inspect pages 12 to 35 (Surah Fatihah and Surah Baqarah)
# On each page, let's extract all text spans: font, text, bbox, point
# Let's see how PyMuPDF sees the page text
sample_pages = [12, 13, 20, 25, 31] # Page 31 is Para 1 Page 21!

symbol_contexts = defaultdict(list)
font_letter_map = Counter()

for pno in sample_pages:
    page = doc[pno - 1]
    text_page = page.get_text("dict")
    
    # Collect all spans with baseline y
    spans = []
    for b in text_page["blocks"]:
        if b.get("type") == 0: # text
            for line in b["lines"]:
                for s in line["spans"]:
                    spans.append({
                        "font": s["font"],
                        "text": s["text"],
                        "bbox": s["bbox"],
                        "origin": s["origin"],
                        "size": s["size"]
                    })
    
    print(f"\n--- পৃষ্ঠা {pno} (মোট স্প্যান: {len(spans)}) ---")
    # Group by Arabic lines (using origin Y rounded to 2 decimals)
    arabic_spans = [s for s in spans if "AnicaKariSAKQ" in s["font"]]
    print(f"  আরবি ক্বারীয়ানা স্প্যান সংখ্যা: {len(arabic_spans)}")
    
    # Show first 5 spans
    for s in arabic_spans[:8]:
        clean_f = s["font"].split("+")[-1]
        print(f"    Font: {clean_f:25s} | Text (hex): {s['text'].encode('latin1', 'replace').hex():20s} | Origin: ({s['origin'][0]:.1f}, {s['origin'][1]:.1f})")

print("\nস্প্যান এক্সট্রাকশন সম্পন্ন।")
