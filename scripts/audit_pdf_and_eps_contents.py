import os
import sys
import re
import pymupdf

sys.stdout.reconfigure(encoding="utf-8")

PDF_PATH = r"C:\Users\Rasel Gazi\OneDrive\Documents\kariana quran full.pdf"
EPS_DIR = r"G:\.shortcut-targets-by-id\1grAqlzXclmbzUySdWV4Mz7jzASJ26bpb\New folder (2)"

print("=== ১. গুগল ড্রাইভের ৮৯৬টি EPS ফাইলের পারা ও পৃষ্ঠা বিশ্লেষণ ===")
if os.path.exists(EPS_DIR):
    eps_files = sorted(os.listdir(EPS_DIR))
    print(f"মোট EPS ফোল্ডারে আইটেম সংখ্যা: {len(eps_files)}")
    
    # Parse filenames like KariSAKQ_Para-01_10.eps
    para_pages = {} # para_num -> list of page_nums
    non_conforming = []
    
    for fn in eps_files:
        m = re.match(r"KariSAKQ_Para-?(\d+)[_-](\d+)", fn, re.I)
        if m:
            p_num = int(m.group(1))
            pg_num = int(m.group(2))
            if p_num not in para_pages:
                para_pages[p_num] = []
            para_pages[p_num].append((pg_num, fn))
        else:
            non_conforming.append(fn)
            
    print(f"শনাক্তকৃত পারা সংখ্যা: {len(para_pages)} (পারা {min(para_pages.keys())} থেকে পারা {max(para_pages.keys())})")
    total_eps_pages = sum(len(v) for v in para_pages.values())
    print(f"পারাভিত্তিক মোট EPS পৃষ্ঠা: {total_eps_pages}")
    
    for p_num in sorted(para_pages.keys()):
        pgs = sorted(para_pages[p_num], key=lambda x: x[0])
        first_pg = pgs[0][0]
        last_pg = pgs[-1][0]
        count = len(pgs)
        # Check if missing any page in range
        expected_range = set(range(first_pg, last_pg + 1))
        actual_range = set(x[0] for x in pgs)
        missing = sorted(expected_range - actual_range)
        missing_str = f" [মিসিং পেজ: {missing}]" if missing else ""
        print(f"  পারা {p_num:02d}: {count:2d} টি পৃষ্ঠা (পৃষ্ঠা {first_pg:3d} থেকে {last_pg:3d}){missing_str}")
        
    if non_conforming:
        print(f"\nঅন্যান্য/বিশেষ ফাইলসমূহ ({len(non_conforming)}): {non_conforming[:20]}")

print("\n=== ২. ৯৭৩ পৃষ্ঠার পিডিএফ (kariana quran full.pdf) বিশ্লেষণ ===")
if os.path.exists(PDF_PATH):
    doc = pymupdf.open(PDF_PATH)
    total_pages = len(doc)
    print(f"পিডিএফ মোট পৃষ্ঠা: {total_pages}")
    
    # Let's sample headers/footers or footer page numbers across pages
    # Check beginning, middle, end, and boundaries
    page_records = []
    
    for idx in range(total_pages):
        page = doc[idx]
        txt = page.get_text()
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        
        # Check first 3 lines and last 3 lines for surah/para/page indicators
        header = " | ".join(lines[:2]) if lines else "EMPTY"
        footer = " | ".join(lines[-3:]) if len(lines) >= 3 else ""
        
        # Look for numbers or keywords
        page_records.append((idx + 1, header, footer))
        
    doc.close()
    
    print("\nপিডিএফের শুরুর পৃষ্ঠাগুলো (১-১৫):")
    for pno, h, f in page_records[:15]:
        print(f"  Page {pno:3d} | Header: {h[:60]} | Footer: {f[:60]}")
        
    print("\nপিডিএফের শেষের পৃষ্ঠাগুলো (৯৬০-৯৭৩):")
    for pno, h, f in page_records[-15:]:
        print(f"  Page {pno:3d} | Header: {h[:60]} | Footer: {f[:60]}")
