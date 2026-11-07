import os
import sys
import json
import subprocess
from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding="utf-8")

font = TTFont("dist/KarianaQuranRecoverFont.ttf")
cmap = font.getBestCmap()
rev_cmap = {v: k for k, v in cmap.items()}

prefix_map = {
    "AnicaKariSAKQPlain": "ar",
    "AnicaKariSAKQPlainExtra": "ar_ex",
    "AnicaKariSAKQPlainSpare": "ar_sp",
    "AnicaKariSAKQHarkat": "hrk",
    "AnicaKariSAKQHarkatExtra": "hrk_ex",
    "AnicaKariSAKQHarkatSpare": "hrk_sp",
    "AnicaKariSAKQS1": "taj_s1",
    "AnicaKariSAKQS2": "taj_s2",
    "AnicaKariSAKQS3": "taj_s3",
    "AnicaKariSAKQS4": "taj_s4",
    "AnicaKariSAKQA4": "taj_a4",
    "AnicaKariSAKQAW": "wqf_aw",
    "AnicaKariSAKQLW": "wqf_lw"
}

with open("extracted_data/eps_page21/eps_page21_stream.json", "r", encoding="utf-8") as f:
    events = json.load(f)

l1 = [e for e in events if abs(e["y"] - 169.73) < 3.0 and e["base_font"].startswith("AnicaKariSAKQ")]

# Test 1: Order by x desc (RTL natural)
l1_desc = sorted(l1, key=lambda x: -x["x"])
chars_desc = []
for e in l1_desc:
    canon = f"{prefix_map.get(e['base_font'])}_{e['glyph']}"
    if canon in rev_cmap:
        chars_desc.append(chr(rev_cmap[canon]))

# Test 2: Order by x asc (LTR)
l1_asc = sorted(l1, key=lambda x: x["x"])
chars_asc = []
for e in l1_asc:
    canon = f"{prefix_map.get(e['base_font'])}_{e['glyph']}"
    if canon in rev_cmap:
        chars_asc.append(chr(rev_cmap[canon]))

str_desc = "".join(chars_desc)
str_asc = "".join(chars_asc)

html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @font-face {{
    font-family: 'KarianaRecover';
    src: url('KarianaQuranRecoverFont.ttf') format('truetype');
  }}
  body {{ background: #fff; padding: 20px; font-family: sans-serif; }}
  .box {{ border: 1px solid #ccc; margin-bottom: 20px; padding: 10px; }}
  .font-test {{
    font-family: 'KarianaRecover';
    font-size: 32px;
    line-height: 2.0;
    white-space: nowrap;
  }}
  .rtl-bidi {{
    direction: rtl;
    unicode-bidi: bidi-override;
  }}
  .rtl-normal {{
    direction: rtl;
  }}
  .ltr-normal {{
    direction: ltr;
  }}
</style>
</head>
<body>
  <h2>১. RTL + bidi-override (x descending: Right to Left)</h2>
  <div class="box font-test rtl-bidi">{str_desc}</div>

  <h2>২. RTL normal (x descending: Right to Left)</h2>
  <div class="box font-test rtl-normal">{str_desc}</div>

  <h2>৩. LTR normal (x ascending: Left to Right)</h2>
  <div class="box font-test ltr-normal">{str_asc}</div>
</body>
</html>
"""

os.makedirs("dist", exist_ok=True)
test_html_path = os.path.abspath("dist/test_font_render.html")
with open(test_html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

shot_path = os.path.abspath("dist/test_font_render.png")
res = subprocess.run([
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    '--headless=new',
    '--disable-gpu',
    f'--screenshot={shot_path}',
    '--window-size=1400,900',
    'http://localhost:8088/dist/test_font_render.html'
], capture_output=True, text=True)

print("Screenshot captured:", os.path.exists(shot_path), "Size:", os.path.getsize(shot_path) if os.path.exists(shot_path) else 0)
