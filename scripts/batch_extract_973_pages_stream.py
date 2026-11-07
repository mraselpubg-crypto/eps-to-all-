import os
import sys
import json
import time
import pymupdf

sys.stdout.reconfigure(encoding="utf-8")

PDF_PATH = r"C:\Users\Rasel Gazi\OneDrive\Documents\kariana quran full.pdf"
OUT_DIR = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\all_pages_streams"
os.makedirs(OUT_DIR, exist_ok=True)

doc = pymupdf.open(PDF_PATH)
total_pages = len(doc)
print(f"=== ৯৭৩ পৃষ্ঠার কুরআন গ্লিফ-স্ট্রিম অটো-এক্সট্রাকশন শুরু (মোট পৃষ্ঠা: {total_pages}) ===")

t0 = time.time()
pages_summary = []

# Process first 25 pages as rapid verification phase
sample_count = min(25, total_pages)

for pno in range(sample_count):
    page = doc[pno]
    text_data = page.get_text("rawjson")
    page_json = json.loads(text_data)
    
    arabic_spans = []
    bangla_spans = []
    
    for block in page_json.get("blocks", []):
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                font_name = span.get("font", "")
                if "AnicaKariSAKQ" in font_name or "KariSAKQ" in font_name:
                    arabic_spans.append({
                        "x": round(span["bbox"][0], 2),
                        "y": round(span["bbox"][3], 2),
                        "font": font_name,
                        "size": round(span["size"], 2),
                        "chars": len(span.get("chars", []))
                    })
                elif "Bangali" in font_name:
                    bangla_spans.append({
                        "y": round(span["bbox"][3], 2),
                        "font": font_name
                    })
                    
    # Detect Arabic baselines (typically 9 baselines)
    from collections import defaultdict
    y_bins = defaultdict(int)
    for s in arabic_spans:
        y_bins[round(s["y"], 1)] += 1
    baselines = sorted([y for y, count in y_bins.items() if count >= 3])
    
    summary_entry = {
        "page_number": pno + 1,
        "arabic_elements": len(arabic_spans),
        "bangla_elements": len(bangla_spans),
        "detected_arabic_lines": len(baselines),
        "baselines": baselines
    }
    pages_summary.append(summary_entry)
    
    # Save page stream
    out_file = os.path.join(OUT_DIR, f"page_{pno+1:03d}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(page_json, f, ensure_ascii=False)

elapsed = time.time() - t0
print(f"\nপ্রথম {sample_count}টি পৃষ্ঠা সফলভাবে এক্সট্র্যাক্ট সম্পন্ন হয়েছে ({elapsed:.2f} সেকেন্ডে)!")
print("নমুনা আউটপুট (প্রথম ৫টি পৃষ্ঠা):")
for s in pages_summary[:5]:
    print(f"  পৃষ্ঠা {s['page_number']:02d}: আরবি উপাদান {s['arabic_elements']}টি, লাইন সংখ্যা: {s['detected_arabic_lines']}টি (বেসলাইন: {s['baselines'][:3]}...)")

# Save summary index
with open(os.path.join(OUT_DIR, "pages_1_to_25_summary.json"), "w", encoding="utf-8") as f:
    json.dump(pages_summary, f, indent=2, ensure_ascii=False)
