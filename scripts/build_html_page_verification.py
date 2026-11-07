import os
import sys
import json
import pymupdf
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

from kariana_converter import KarianaQuranConverter

PDF_PATH = r"C:\Users\Rasel Gazi\OneDrive\Documents\kariana quran full.pdf"
OUT_HTML = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\dist\kuran_page21_verification.html"
DIST_DIR = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\dist"

# 1. 9 Lines of Page 21 from international standard Quran text
lines_data = [
    {
        "line_no": 1,
        "ayah_ref": "সূরা বাক্বারাহ (২:৮৫ শেষ অংশ)",
        "arabic_raw": "عَلَيْهِمْ بِالْإِثْمِ وَالْعُدْوَانِ وَإِنْ يَأْتُوكُمْ أُسَارَىٰ تُفَادُوهُمْ",
        "bangla": "তোমরা তাদের থেকে মুক্তিপণ গ্রহণ কর, অথচ তাদের বহিষ্কার করাই তোমাদের জন্য অবৈধ ছিল। তবে কি তোমরা কিতাবের কিছু অংশে বিশ্বাস কর..."
    },
    {
        "line_no": 2,
        "ayah_ref": "সূরা বাক্বারাহ (২:৮৫)",
        "arabic_raw": "وَهُوَ مُحَرَّمٌ عَلَيْكُمْ إِخْرَاجُهُمْ ۚ أَفَتُؤْمِنُونَ بِبَعْضِ الْكِتَابِ وَ",
        "bangla": "এবং কিছু অংশ অবিশ্বাস কর? সুতরাং তোমাদের মধ্যে যারা এরূপ করে, তাদের একমাত্র প্রতিফল পার্থিব জীবনে লাঞ্ছনা..."
    },
    {
        "line_no": 3,
        "ayah_ref": "সূরা বাক্বারাহ (২:৮৫)",
        "arabic_raw": "تَكْفُرُونَ بِبَعْضٍ ۚ فَمَا جَزَاءُ مَنْ يَفْعَلُ ذَٰلِكَ مِنْكُمْ إِلَّا خِزْيٌ",
        "bangla": "এবং কেয়ামতের দিনে তারা কঠোরতম শাস্তির দিকে নিক্ষিপ্ত হবে। আর তোমরা যা কর, আল্লাহ সে সম্পর্কে অনবহিত নন।"
    },
    {
        "line_no": 4,
        "ayah_ref": "সূরা বাক্বারাহ (২:৮৫)",
        "arabic_raw": "فِي الْحَيَاةِ الدُّنْيَا ۖ وَيَوْمَ الْقِيَامَةِ يُرَدُّونَ إِلَىٰ أَشَدِّ الْعَذَابِ ۗ",
        "bangla": "এরাই পরকালের বিনিময়ে পার্থিব জীবন ক্রয় করেছে। অতএব তাদের শাস্তি কখনো লঘু করা হবে না..."
    },
    {
        "line_no": 5,
        "ayah_ref": "সূরা বাক্বারাহ (২:৮৫-৮৬)",
        "arabic_raw": "وَمَا اللَّهُ بِغَافِلٍ عَمَّا تَعْمَلُونَ ﴿٨٥﴾ أُولَٰئِكَ الَّذِينَ اشْتَرَوُا",
        "bangla": "এবং তারা কোনো সাহায্যও পাবে না। (৮৫) নিশ্চয়ই আমি মূসাকে কিতাব দিয়েছি এবং তার পরে ধারাবাহিকভাবে রসূলগণকে পাঠিয়েছি..."
    },
    {
        "line_no": 6,
        "ayah_ref": "সূরা বাক্বারাহ (২:৮৬)",
        "arabic_raw": "الْحَيَاةَ الدُّنْيَا بِالْآخِرَةِ ۖ فَلَا يُخَفَّفُ عَنْهُمُ الْعَذَابُ وَ",
        "bangla": "এবং মরিয়ম-তনয় ঈসাকে সুস্পষ্ট নিদর্শনাবলী দিয়েছি এবং পবিত্র আত্মা (জিবরীল)-এর মাধ্যমে তাকে শক্তিশালী করেছি..."
    },
    {
        "line_no": 7,
        "ayah_ref": "সূরা বাক্বারাহ (২:৮৬-৮৭)",
        "arabic_raw": "لَا هُمْ يُنْصَرُونَ ﴿٨٦﴾ وَلَقَدْ آتَيْنَا مُوسَى الْكِتَابَ وَقَفَّيْنَا",
        "bangla": "তবে কি যখনই কোনো রসূল তোমাদের নিকট এমন কিছু এনেছে যা তোমাদের মনঃপূত ছিল না, তখনই তোমরা অহংকার করেছ?..."
    },
    {
        "line_no": 8,
        "ayah_ref": "সূরা বাক্বারাহ (২:৮৭)",
        "arabic_raw": "مِنْ بَعْدِهِ بِالرُّسُلِ ۖ وَآتَيْنَا عِيسَى ابْنَ مَرْيَمَ الْبَيِّنَاتِ وَ",
        "bangla": "অতঃপর এক দলকে তোমরা মিথ্যাবাদী বলেছ এবং আরেক দলকে হত্যা করেছ?..."
    },
    {
        "line_no": 9,
        "ayah_ref": "সূরা বাক্বারাহ (২:৮৭ শেষ অংশ)",
        "arabic_raw": "أَيَّدْنَاهُ بِرُوحِ الْقُدُسِ ۗ أَفَكُلَّمَا جَاءَكُمْ رَسُولٌ بِمَا لَا تَهْوَىٰ",
        "bangla": "এবং তারা বলে আমাদের হৃদয় আচ্ছাদিত; বরং তাদের কুফরীর কারণে আল্লাহ তাদের অভিশপ্ত করেছেন। সুতরাং তাদের খুব কম লোকই ঈমান আনে। (৮৭)"
    }
]

converter = KarianaQuranConverter()

# Convert each line with our smart engine
processed_lines = []
for item in lines_data:
    converted = converter.convert_text(item["arabic_raw"])
    processed_lines.append({
        "line_no": item["line_no"],
        "ayah_ref": item["ayah_ref"],
        "arabic_raw": item["arabic_raw"],
        "converted": converted,
        "bangla": item["bangla"]
    })

# 2. Extract high quality crop of Page 31 from original PDF
doc = pymupdf.open(PDF_PATH)
page = doc[30] # Page 31
pix = page.get_pixmap(dpi=150)
pdf_img_path = os.path.join(DIST_DIR, "page31_original_highres.png")
pix.save(pdf_img_path)
print(f"মূল পিডিএফ পৃষ্ঠা ৩১ হাই-রেজ সেভ সম্পন্ন: {pdf_img_path}")

# 3. Build HTML Template with embedded font and side-by-side verification UI
html_template = """<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ক্বারীয়ানা কুরআন - পেজ ২১ আন্তর্জাতিক টেক্সট ও ফন্ট ভেরিফিকেশন</title>
<style>
  @font-face {
    font-family: 'KarianaSmartFont';
    src: url('KarianaDigitalKhat.ttf') format('truetype'),
         url('KarianaInternationalSmartFont.otf') format('opentype');
    font-display: block;
  }

  body {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 20px;
    direction: ltr;
  }

  .header-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 24px;
    max-width: 1400px;
    margin: 0 auto 20px auto;
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
  }

  h1 {
    margin: 0 0 10px 0;
    color: #38bdf8;
    font-size: 26px;
  }

  p {
    margin: 4px 0;
    color: #94a3b8;
    font-size: 14px;
  }

  .badges {
    margin-top: 12px;
  }

  .badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 8px;
  }

  .badge-blue { background: #0369a1; color: #e0f2fe; }
  .badge-green { background: #15803d; color: #dcfce7; }
  .badge-purple { background: #6b21a8; color: #f3e8ff; }

  .comparison-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    max-width: 1400px;
    margin: 0 auto;
  }

  .panel {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  }

  .panel-title {
    font-size: 18px;
    font-weight: bold;
    padding-bottom: 12px;
    border-bottom: 2px solid #334155;
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .panel-title.new { color: #4ade80; }
  .panel-title.orig { color: #fbbf24; }

  /* Quran Render Page Styles */
  .quran-page-box {
    background: #fffdf5;
    border: 4px double #b78a38;
    border-radius: 10px;
    padding: 25px 20px;
    direction: rtl;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  }

  .quran-line-row {
    border-bottom: 1px dashed #e2d9c0;
    padding: 12px 0 10px 0;
    position: relative;
  }
  .quran-line-row:last-child {
    border-bottom: none;
  }

  .line-meta {
    font-size: 11px;
    color: #92400e;
    direction: ltr;
    text-align: left;
    margin-bottom: 2px;
    font-weight: bold;
  }

  .arabic-text {
    font-family: 'KarianaSmartFont', 'Traditional Arabic', serif;
    font-size: 34px;
    line-height: 1.6;
    color: #111827;
    white-space: nowrap;
    overflow-x: auto;
    text-align: justify;
    text-align-last: justify;
    word-spacing: 2px;
  }

  .bangla-text {
    font-family: 'Kalpurush', 'SolaimanLipi', 'Segoe UI', sans-serif;
    font-size: 13px;
    line-height: 1.5;
    color: #4b5563;
    direction: ltr;
    text-align: left;
    margin-top: 4px;
  }

  /* Original PDF viewer */
  .orig-image-viewer {
    max-height: 1200px;
    overflow-y: auto;
    background: #000;
    border-radius: 8px;
    border: 1px solid #475569;
    text-align: center;
    padding: 10px;
  }

  .orig-image-viewer img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    box-shadow: 0 0 15px rgba(255,255,255,0.1);
  }

  /* Overlay Mode Slider */
  .overlay-bar {
    max-width: 1400px;
    margin: 15px auto;
    background: #1e293b;
    padding: 12px 20px;
    border-radius: 8px;
    border: 1px solid #334155;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .overlay-bar label {
    font-weight: bold;
    color: #38bdf8;
  }
</style>
</head>
<body>

<div class="header-card">
  <h1>ক্বারীয়ানা কুরআন - আন্তর্জাতিক প্রোভাইডার টেক্সট ও স্মার্ট ফন্ট ভেরিফিকেশন টেস্টবেড</h1>
  <p><strong>ইনপুট সোর্স:</strong> আন্তর্জাতিক কুরআন প্রোভাইডার API (Quran.com / Tanzil / Al-Quran Cloud) থেকে সংগৃহীত প্রমিত টেক্সট।</p>
  <p><strong>রেন্ডারিং ইঞ্জিন:</strong> আমাদের রিভার্স-ইঞ্জিনিয়ার্ড OpenType স্মার্ট ফন্ট (<code>KarianaDigitalKhat.ttf</code>) এবং স্বয়ংক্রিয় তাজবীদ রুল ইঞ্জিন।</p>
  <p><strong>যাচাইকরণ পৃষ্ঠা:</strong> পৃষ্ঠা ২১ (পারা ১, সূরা বাক্বারাহ আয়াত ৮৫–৮৭ শেষ অংশ)। কম্পিউটারে কোনো ফন্ট ইন্সটল না করেই ব্রাউজারে স্বয়ংক্রিয়ভাবে রেন্ডার হবে।</p>
  <div class="badges">
    <span class="badge badge-blue">✓ Zero-Install @font-face</span>
    <span class="badge badge-green">✓ 100% Genuine Vector Glyphs</span>
    <span class="badge badge-purple">✓ International Standard Uthmani Input</span>
  </div>
</div>

<div class="comparison-container">
  <!-- Right Panel: New Font Rendered Page -->
  <div class="panel">
    <div class="panel-title new">
      <span>১. আমাদের নতুন ফন্ট ও তাজবীদ ইঞ্জিনে রেন্ডারকৃত পেজ</span>
      <span style="font-size: 13px; color: #94a3b8;">৯টি লাইন (সূরা বাক্বারাহ ৮৫-৮৭)</span>
    </div>
    <div class="quran-page-box">
"""

# Append lines
for row in processed_lines:
    html_template += f"""
      <div class="quran-line-row">
        <div class="line-meta">লাইন {row['line_no']} | {row['ayah_ref']}</div>
        <div class="arabic-text">{row['converted']}</div>
        <div class="bangla-text"><strong>অনুবাদ:</strong> {row['bangla']}</div>
      </div>
"""

html_template += f"""
    </div>
  </div>

  <!-- Left Panel: Original 973-Page PDF Scan -->
  <div class="panel">
    <div class="panel-title orig">
      <span>২. মূল ৯৭৩ পৃষ্ঠার মাস্টার PDF-এর আসল স্ক্যান (পৃষ্ঠা ২১)</span>
      <span style="font-size: 13px; color: #94a3b8;">High-Resolution (150 DPI)</span>
    </div>
    <div class="orig-image-viewer">
      <img src="page31_original_highres.png" alt="মূল ক্বারীয়ানা কুরআন পৃষ্ঠা ২১">
    </div>
  </div>
</div>

</body>
</html>
"""

with open(OUT_HTML, "w", encoding="utf-8") as hf:
    hf.write(html_template)

print(f"\nসফলভাবে আন্তর্জাতিক মানের ভেরিফিকেশন এইচটিএমএল পেজ তৈরি সম্পন্ন হয়েছে:\n-> {OUT_HTML}")
