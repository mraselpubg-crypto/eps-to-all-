import os
import sys
import zipfile
import shutil

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
ZIP_OUT = os.path.join(DIST, "Kariana_Full_AI_Agent_Handoff_Package.zip")

readme_content = """# ক্বারীয়ানা কুরআন ডিজিটাল রিকভারি ও ফন্ট ইঞ্জিনিয়ারিং হ্যান্ডঅফ প্যাকেজ
## (Kariana Quran Full AI Agent Handoff Package)

এই প্যাকেজে অন্য যেকোনো এআই এজেন্ট (যেমন Claude / ChatGPT) বা ডেভেলপারের কাজ করার জন্য প্রয়োজনীয় সমস্ত রিসোর্স, মূল ফন্ট, ডিক্রিপ্ট করা ভেক্টর আউটলাইন, ইউনিকোড টেক্সট এবং ওপেনটাইপ রুলস সুসংগঠিতভাবে দেওয়া হলো।

---

### ফোল্ডার ও ফাইলের বিবরণ:

#### ১. 01_Original_Source_Fonts/ (মূল ফন্ট ফাইলসমূহ)
- `AnicaKariSAKQPlain.ttf`, `AnicaKariSAKQPlainExtra.ttf`, `AnicaKariSAKQPlainSpare.ttf`
- `AnicaKariSAKQHarkat.ttf`, `AnicaKariSAKQHarkatExtra.ttf`, `AnicaKariSAKQHarkatSpare.ttf`
- `AnicaKariSAKQA1.ttf` .. `AnicaKariSAKQA4.ttf`
- `AnicaKariSAKQAW.ttf`, `AnicaKariSAKQLW.ttf`
- `KarianaQuranRecoverFont.otf` (১,০০২টি গ্লিফ, আসল ভেক্টর কিউবিক কার্ভ, ওপেনটাইপ GSUB/GPOS সহ)
- `KarianaQuranRecoverFont.ttf` (ট্রু-টাইপ ফরম্যাট)

#### ২. 02_Vector_Database_and_EPS_Stream/ (ভেক্টর ডেটা ও স্ট্রিম)
- `master_973_all_glyphs.json`: ৯৭৩ পৃষ্ঠার মাস্টার PDF থেকে ডিক্রিপ্ট করা ৬৫৮টি মূল ভেক্টর গ্লিফের SVG পাথ ও বাউন্ডিং বক্স ডেটাবেস।
- `eps_page21_stream.json`: পৃষ্ঠা ২১-এর মূল ম্যাক ইনডিজাইন EPS ফাইলের ১৮৪৪টি ইভেন্টের নির্ভুল X, Y কোঅর্ডিনেট।
- `KariSAKQ_Para-01_21.eps`: পৃষ্ঠা ২১-এর মূল ম্যাক Illustrator 8.0 / InDesign 1.5.2 ভেক্টর EPS ফাইল।

#### ৩. 03_Unicode_Quran_Texts/ (ইউনিকোড কুরআনিক টেক্সট)
- `digital-khatt-indopak-ayah-by-ayah-script.json`: ১১৪টি সূরা, ৬,২৩৬টি আয়াতের সম্পূর্ণ ইন্দো-পাক ইউনিকোড আরবি টেক্সট (হরকত ও তাজবীদ চিহ্নসহ)।
- `page21_reference_lines.json`: পৃষ্ঠা ২১-এর ৯টি লাইনের শব্দ-বাই-শব্দ রেফারেন্স টেক্সট।

#### ৪. 04_Code_to_Glyph_Mappings/ (কোড ও গ্লিফ ম্যাপিং)
- `kariana_recover_pua_map.json`: ক্বারীয়ানার ১,০০১টি গ্লিফের ফ্যামিলি/নাম থেকে PUA ইউনিকোড (U+E000..U+E3E8) ম্যাপিং ডিকশনারি।
- `kariana_features.fea`: Adobe InDesign World-Ready Composer-এর জন্য OpenType GSUB (init, medi, fina, rlig) ও GDEF ফিচার ফাইল।

#### ৫. 05_Blueprint_and_Verification_Reports/ (মাস্টার ব্লুপ্রিন্ট ও ভেরিফিকেশন রিপোর্ট)
- `KARIANA_QURAN_MASTER_BLUEPRINT.md`: সম্পূর্ণ প্রজেক্টের কারিগরি ব্লুপ্রিন্ট, টাইপ ১ ক্রিপ্টোগ্রাফি অ্যালগরিদম, গাণিতিক কোঅর্ডিনেট ও অন্য এআই এজেন্টের জন্য রেডিমেড প্রম্পট।
- `report.json`: মূল ভেক্টর বনাম নতুন ফন্টের এম্পিরিক্যাল পিক্সেল ডিফারেন্সিয়াল রিপোর্ট (Structural Mismatch: 0.0%)।
- `kuran_page21_recover_font_verification.html`: স্বয়ংসম্পূর্ণ সিঙ্গেল-ফাইল ভেরিফিকেশন ওয়েব পেজ (ইনলাইন বেস৬৪ ফন্ট ও রাস্টার কম্প্যারিজনসহ)।

#### ৬. 06_Core_Scripts/ (মূল এক্সিকিউটেবল পাইথন স্ক্রিপ্টসমূহ)
- `phase1_eps_decoder.py`: ম্যাক Type 1 ফন্ট ও eexec ডিক্রিপশন ইঞ্জিন।
- `phase1_pdf_973_unifier.py`: ৯৭৩ পৃষ্ঠার PDF থেকে CFF ফন্ট সাবসেট এক্সট্র্যাক্টর।
- `build_kariana_smart_opentype_font.py`: ওপেনটাইপ GSUB/GPOS স্মার্ট ফন্ট কম্পাইলার।
- `verify_eps_page_with_font.py`: হেডলেস ব্রাউজার দিয়ে ভেক্টর বনাম ফন্ট রাস্টার কম্প্যারিজন স্ক্রিপ্ট।
- `align_unicode_to_kariana_glyphs.py`: ইউনিকোড শব্দের সাথে ক্বারীয়ানা গ্লিফ সিকোয়েন্স অ্যালাইনার।

---
**প্রজেক্ট গিটহাব রিপোজিটরি:** https://github.com/mraselpubg-crypto/eps-to-all-
"""

files_to_zip = [
    # 01 Source Fonts
    ("source_fonts/AnicaKariSAKQPlain.ttf", "01_Original_Source_Fonts/AnicaKariSAKQPlain.ttf"),
    ("source_fonts/AnicaKariSAKQPlainExtra.ttf", "01_Original_Source_Fonts/AnicaKariSAKQPlainExtra.ttf"),
    ("source_fonts/AnicaKariSAKQPlainSpare.ttf", "01_Original_Source_Fonts/AnicaKariSAKQPlainSpare.ttf"),
    ("source_fonts/AnicaKariSAKQHarkat.ttf", "01_Original_Source_Fonts/AnicaKariSAKQHarkat.ttf"),
    ("source_fonts/AnicaKariSAKQHarkatExtra.ttf", "01_Original_Source_Fonts/AnicaKariSAKQHarkatExtra.ttf"),
    ("source_fonts/AnicaKariSAKQHarkatSpare.ttf", "01_Original_Source_Fonts/AnicaKariSAKQHarkatSpare.ttf"),
    ("source_fonts/AnicaKariSAKQA1.ttf", "01_Original_Source_Fonts/AnicaKariSAKQA1.ttf"),
    ("source_fonts/AnicaKariSAKQA2.ttf", "01_Original_Source_Fonts/AnicaKariSAKQA2.ttf"),
    ("source_fonts/AnicaKariSAKQA3.ttf", "01_Original_Source_Fonts/AnicaKariSAKQA3.ttf"),
    ("source_fonts/AnicaKariSAKQA4.ttf", "01_Original_Source_Fonts/AnicaKariSAKQA4.ttf"),
    ("source_fonts/AnicaKariSAKQAW.ttf", "01_Original_Source_Fonts/AnicaKariSAKQAW.ttf"),
    ("source_fonts/AnicaKariSAKQLW.ttf", "01_Original_Source_Fonts/AnicaKariSAKQLW.ttf"),
    ("dist/KarianaQuranRecoverFont.otf", "01_Original_Source_Fonts/KarianaQuranRecoverFont.otf"),
    ("dist/KarianaQuranRecoverFont.ttf", "01_Original_Source_Fonts/KarianaQuranRecoverFont.ttf"),

    # 02 Vector DB and EPS
    ("extracted_data/master_973_glyphs/master_973_all_glyphs.json", "02_Vector_Database_and_EPS_Stream/master_973_all_glyphs.json"),
    ("extracted_data/eps_page21/eps_page21_stream.json", "02_Vector_Database_and_EPS_Stream/eps_page21_stream.json"),
    ("extracted_data/eps_page21/eps_page21_fonts.json", "02_Vector_Database_and_EPS_Stream/eps_page21_fonts.json"),
    ("C:/xampp/htdocs/Bipul code craft Api/KariSAKQ_Para-01_21.eps", "02_Vector_Database_and_EPS_Stream/KariSAKQ_Para-01_21.eps"),

    # 03 Unicode Texts
    ("user_reference/digital-khatt-indopak-ayah-by-ayah-script.json", "03_Unicode_Quran_Texts/digital-khatt-indopak-ayah-by-ayah-script.json"),
    ("dist/page21_reference_lines.json", "03_Unicode_Quran_Texts/page21_reference_lines.json"),

    # 04 Mappings
    ("dist/kariana_recover_pua_map.json", "04_Code_to_Glyph_Mappings/kariana_recover_pua_map.json"),
    ("dist/kariana_features.fea", "04_Code_to_Glyph_Mappings/kariana_features.fea"),

    # 05 Blueprint & Reports
    ("KARIANA_QURAN_MASTER_BLUEPRINT.md", "05_Blueprint_and_Verification_Reports/KARIANA_QURAN_MASTER_BLUEPRINT.md"),
    ("dist/report.json", "05_Blueprint_and_Verification_Reports/report.json"),
    ("dist/kuran_page21_recover_font_verification.html", "05_Blueprint_and_Verification_Reports/kuran_page21_recover_font_verification.html"),

    # 06 Scripts
    ("scripts/phase1_eps_decoder.py", "06_Core_Scripts/phase1_eps_decoder.py"),
    ("scripts/phase1_pdf_973_unifier.py", "06_Core_Scripts/phase1_pdf_973_unifier.py"),
    ("scripts/build_kariana_smart_opentype_font.py", "06_Core_Scripts/build_kariana_smart_opentype_font.py"),
    ("scripts/build_kariana_quran_recover_font.py", "06_Core_Scripts/build_kariana_quran_recover_font.py"),
    ("scripts/verify_eps_page_with_font.py", "06_Core_Scripts/verify_eps_page_with_font.py"),
    ("scripts/align_unicode_to_kariana_glyphs.py", "06_Core_Scripts/align_unicode_to_kariana_glyphs.py")
]

print("=== জিপ আর্কাইভ প্যাকেজিং শুরু ===")
with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("README_FOR_AI_AGENT.md", readme_content)
    print("Added: README_FOR_AI_AGENT.md")
    for src, dst in files_to_zip:
        if os.path.exists(src):
            z.write(src, dst)
            print(f"Added: {dst} ({os.path.getsize(src):,} bytes)")
        else:
            print(f"Warning: File not found: {src}")

print(f"\nসফলভাবে জিপ ফাইল তৈরি হয়েছে: {ZIP_OUT} ({os.path.getsize(ZIP_OUT):,} bytes)")
