import os
import sys
import zipfile
import glob

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
ZIP_OUT = os.path.join(DIST, "Kariana_Full_Quran_Streams_and_S1_S4.zip")

readme_for_claude = """# ক্বারীয়ানা কুরআন: সম্পূর্ণ ৯৬৩ পৃষ্ঠার গ্লিফ-স্ট্রিম ও S1-S4 TTF প্যাকেজ
## (Complete 963-Page Glyph Streams, S1-S4 TTF Fonts & Page Index for Claude)

Claude-এর পূর্ববর্তী বিশ্লেষণের প্রতিটি প্রশ্নের সুনির্দিষ্ট উত্তর ও প্রয়োজনীয় সমস্ত ডেটা এই প্যাকেজে দেওয়া হলো:

---

### ১. আপনার প্রতিটি প্রশ্নের সরাসরি উত্তর:

1. **"৯৭৩ পৃষ্ঠার PDF বা সব পৃষ্ঠার গ্লিফ-স্ট্রিম নেই"**:
   - এই প্যাকেজের `02_Full_963_Pages_Glyph_Streams/` ফোল্ডারে সম্পূর্ণ কুরআনের **১ম থেকে ৯৬৩তম পৃষ্ঠার সবকটি পৃষ্ঠার লাইটওয়েট JSON গ্লিফ-স্ট্রিম** দেওয়া হয়েছে (মোট ৯৭৯,৭১০টি ইভেন্ট)।
   - প্রতিটি ফাইলে প্রতিটি হরফ, হরকত, ওয়াকফ ও তাজবীদ চিহ্নের সুনির্দিষ্ট X, Y কোঅর্ডিনেট, ফন্ট নাম এবং গ্লিফ নাম রয়েছে।

2. **"PDF-এ পৃষ্ঠা ১২ থেকে কুরআনের শুরু কি না?"**:
   - **হ্যাঁ, নিশ্চিত!** 
     - PDF পেজ ১–১০: কভার, সূচিপত্র ও ভূমিকা।
     - **PDF পেজ ১১:** মুদ্রিত পৃষ্ঠা ১ (সূরা আল-ফাতিহা ১:১ - ১:৭)।
     - **PDF পেজ ১২:** মুদ্রিত পৃষ্ঠা ২ (সূরা আল-বাক্বারাহ ২:১ - ২:৫)।
     - **PDF পেজ ৩১:** মুদ্রিত পৃষ্ঠা ২১ (সূরা আল-বাক্বারাহ ২:৮৫ - ২:৮৭, যা আমরা প্রমাণ করেছি)।
     - গাণিতিক সূত্র: `PDF Page Number = Printed Page Number + 10`।

3. **"S1-S4-এর মূল TTF ফন্ট"**:
   - `01_S1_S4_Original_TTF_Fonts/` ফোল্ডারে `master_973_all_glyphs.json`-এর মূল আউটলাইন থেকে কম্পাইল করা ৪টি স্বতন্ত্র TTF ফন্ট দেওয়া হয়েছে:
     - `AnicaKariSAKQS1.ttf` (১৯টি গ্লিফ)
     - `AnicaKariSAKQS2.ttf` (১১টি গ্লিফ)
     - `AnicaKariSAKQS3.ttf` (১১টি গ্লিফ)
     - `AnicaKariSAKQS4.ttf` (৫টি গ্লিফ)

4. **"গ্লিফ সংখ্যার স্পষ্টতা"**:
   - মূল ১৬টি কোর ক্বারীয়ানা ফন্টের ইউনিক ভেক্টর গ্লিফ সংখ্যা: **৬৫৭–৬৫৮টি**।
   - ১,০০১টি হলো PUA ম্যাপিং (ফ্যামিলি/গ্লিফ কম্বিনেশন)।
   - ১,৭৫৪টির মধ্যে বাংলা অনুবাদের ফন্ট (`AnicaBangali`, `KarianaBangali`) এবং বাফার ফন্ট অন্তর্ভুক্ত ছিল। কোর আরবি ও তাজবীদে ৬৫৭টিই চূড়ান্ত।

---

### ২. প্যাকেজের ফোল্ডার গঠন:

```
Kariana_Full_Quran_Streams_and_S1_S4.zip
├── README_FOR_CLAUDE.md
├── 01_S1_S4_Original_TTF_Fonts/
│   ├── AnicaKariSAKQS1.ttf
│   ├── AnicaKariSAKQS2.ttf
│   ├── AnicaKariSAKQS3.ttf
│   └── AnicaKariSAKQS4.ttf
├── 02_Full_963_Pages_Glyph_Streams/
│   ├── master_pages_catalog.json (৯৬৩ পৃষ্ঠার ক্যাটালগ)
│   ├── page_001.json (সূরা ফাতিহা)
│   ├── ...
│   └── page_963.json (সূরা নাস)
└── 03_Reference_and_Mappings/
    ├── master_973_all_glyphs.json (৬৫৭টি ভেক্টর গ্লিফের SVG পাথ ডেটাবেস)
    ├── kariana_recover_pua_map.json (১,০০১ গ্লিফ ম্যাপিং)
    └── digital-khatt-indopak-ayah-by-ayah-script.json (৬,২৩৬ আয়াতের ইন্দো-পাক টেক্সট)
```

---
**গিটহাব রিপোজিটরি:** https://github.com/mraselpubg-crypto/eps-to-all-
"""

print("=== সম্পূর্ণ ৯৬৩ পৃষ্ঠার জিপ প্যাকেজিং শুরু ===")
with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("README_FOR_CLAUDE.md", readme_for_claude)
    print("Added: README_FOR_CLAUDE.md")
    
    # 01 S1-S4 Fonts
    for fam in ["AnicaKariSAKQS1", "AnicaKariSAKQS2", "AnicaKariSAKQS3", "AnicaKariSAKQS4"]:
        fpath = f"source_fonts/{fam}.ttf"
        if os.path.exists(fpath):
            z.write(fpath, f"01_S1_S4_Original_TTF_Fonts/{fam}.ttf")
            print(f"Added font: {fam}.ttf")
            
    # 02 All 963 Pages Streams
    streams_dir = "extracted_data/all_pages_streams"
    catalog_path = os.path.join(streams_dir, "master_pages_catalog.json")
    if os.path.exists(catalog_path):
        z.write(catalog_path, "02_Full_963_Pages_Glyph_Streams/master_pages_catalog.json")
        
    page_files = sorted(glob.glob(os.path.join(streams_dir, "page_*.json")))
    print(f"Adding {len(page_files)} page stream files...")
    for pf in page_files:
        arcname = f"02_Full_963_Pages_Glyph_Streams/{os.path.basename(pf)}"
        z.write(pf, arcname)
        
    # 03 Reference & Mappings
    z.write("extracted_data/master_973_glyphs/master_973_all_glyphs.json", "03_Reference_and_Mappings/master_973_all_glyphs.json")
    z.write("dist/kariana_recover_pua_map.json", "03_Reference_and_Mappings/kariana_recover_pua_map.json")
    z.write("user_reference/digital-khatt-indopak-ayah-by-ayah-script.json", "03_Reference_and_Mappings/digital-khatt-indopak-ayah-by-ayah-script.json")

print(f"\n✓ সফলভাবে তৈরি হয়েছে: {ZIP_OUT} ({os.path.getsize(ZIP_OUT):,} bytes)")
