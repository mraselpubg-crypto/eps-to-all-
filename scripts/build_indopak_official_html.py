import os
import sys
import json
import shutil

sys.stdout.reconfigure(encoding="utf-8")

JSON_PATH = r"user_reference\digital-khatt-indopak-ayah-by-ayah-script.json"
OTF_SRC = r"user_reference\DigitalKhattIndoPak.otf"
DIST_DIR = r"dist"
OUT_HTML = os.path.join(DIST_DIR, "test_indopak_official_render.html")

# Copy the official font to dist directory
shutil.copy2(OTF_SRC, os.path.join(DIST_DIR, "DigitalKhattIndoPak.otf"))

with open(JSON_PATH, "r", encoding="utf-8") as f:
    quran_json = json.load(f)

# Page 1: Surah Al-Fatihah (1:1 to 1:7)
fatihah_ayahs = [quran_json[f"1:{i}"]["text"] for i in range(1, 8)]

# Page 21: Surah Al-Baqarah (2:85, 2:86, 2:87)
baqarah_ayahs = [
    (85, quran_json["2:85"]["text"]),
    (86, quran_json["2:86"]["text"]),
    (87, quran_json["2:87"]["text"])
]

html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Digital Khatt IndoPak - অফিসিয়াল রেন্ডারিং ও ভেরিফিকেশন</title>
<style>
  @font-face {{
    font-family: 'DigitalKhattIndoPak';
    src: url('DigitalKhattIndoPak.otf') format('opentype');
    font-display: block;
  }}

  body {{
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    margin: 0;
    padding: 25px;
    direction: ltr;
  }}

  .header {{
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px 25px;
    max-width: 1400px;
    margin: 0 auto 25px auto;
  }}

  h1 {{
    color: #38bdf8;
    margin: 0 0 10px 0;
    font-size: 24px;
  }}
  p {{
    color: #94a3b8;
    margin: 4px 0;
    font-size: 14px;
  }}

  .grid-container {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 25px;
    max-width: 1400px;
    margin: 0 auto;
  }}

  .panel {{
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  }}

  .panel-title {{
    font-size: 17px;
    font-weight: bold;
    padding-bottom: 12px;
    border-bottom: 2px solid #334155;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
  }}
  .panel-title.new {{ color: #4ade80; }}
  .panel-title.orig {{ color: #fbbf24; }}

  /* Quran Paper Box */
  .mushaf-box {{
    background: #fffdf5;
    border: 3px double #b78a38;
    border-radius: 8px;
    padding: 30px 25px;
    direction: rtl;
    box-shadow: inset 0 0 40px rgba(183, 138, 56, 0.08);
  }}

  .ayah-block {{
    font-family: 'DigitalKhattIndoPak', serif;
    font-size: 32px;
    line-height: 2.2;
    color: #111827;
    text-align: justify;
    text-align-last: center;
    word-spacing: 4px;
    margin-bottom: 20px;
  }}

  .ayah-num {{
    font-family: 'DigitalKhattIndoPak', serif;
    color: #0369a1;
  }}

  .orig-viewer {{
    max-height: 1200px;
    overflow-y: auto;
    background: #000;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
  }}
  .orig-viewer img {{
    max-width: 100%;
    height: auto;
    border-radius: 4px;
  }}
</style>
</head>
<body>

<div class="header">
  <h1>Digital Khatt IndoPak - অফিসিয়াল ফন্ট ও JSON ভেরিফিকেশন টেস্টবেড</h1>
  <p><strong>ফন্ট:</strong> <code>DigitalKhattIndoPak.otf</code> (অফিসিয়াল ওপেনটাইপ ফন্ট)</p>
  <p><strong>টেক্সট সোর্স:</strong> <code>digital-khatt-indopak-ayah-by-ayah-script.json</code> (ইউজারের দেওয়া অফিসিয়াল ইন্দো-পাক স্ক্রিপ্ট)</p>
</div>

<div class="grid-container">
  <!-- Left Column: Rendered Mushaf using Official DigitalKhattIndoPak -->
  <div class="panel">
    <div class="panel-title new">
      <span>১. Digital Khatt IndoPak ফন্টে সরাসরি রেন্ডার</span>
      <span style="font-size: 13px; color: #94a3b8;">সূরা বাক্বারাহ (আয়াত ৮৫–৮৭)</span>
    </div>
    <div class="mushaf-box">
      <div class="ayah-block">
"""

for ayah_num, a_text in baqarah_ayahs:
    html += f"""        <span style="color: #64748b; font-size: 14px; font-family: sans-serif;">[আয়াত {ayah_num}]</span> {a_text}<br><br>\n"""

html += f"""      </div>
    </div>
  </div>

  <!-- Right Column: Original 973 Page Scan -->
  <div class="panel">
    <div class="panel-title orig">
      <span>২. মূল ৯৭৩ পৃষ্ঠার মাস্টার PDF-এর পৃষ্ঠা ২১ স্ক্যান</span>
      <span style="font-size: 13px; color: #94a3b8;">High-Res (150 DPI)</span>
    </div>
    <div class="orig-viewer">
      <img src="page31_original_highres.png" alt="মূল ক্বারীয়ানা কুরআন পৃষ্ঠা ২১">
    </div>
  </div>
</div>

</body>
</html>
"""

with open(OUT_HTML, "w", encoding="utf-8") as hf:
    hf.write(html)

print(f"\nসফলভাবে অফিসিয়াল টেস্টবেড HTML তৈরি সম্পন্ন:\n-> {OUT_HTML}")
