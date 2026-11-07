import os
import sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

PDF_IMG = r"dist\page31_original_highres.png"
OUT_DIR = r"dist\pdf_verified_lines"
os.makedirs(OUT_DIR, exist_ok=True)

img = Image.open(PDF_IMG)
w, h = img.size
print(f"মূল PDF ইমেজ সাইজ: {w} x {h}")

scale = w / 595.28
baselines = [169.73, 234.17, 298.61, 363.05, 427.49, 491.93, 556.37, 620.81, 685.25]

for idx, y_base in enumerate(baselines, 1):
    y1 = int((y_base - 42) * scale)
    y2 = int((y_base + 12) * scale)
    x1 = int(85 * scale)
    x2 = int(510 * scale)
    
    line_crop = img.crop((x1, y1, x2, y2))
    out_p = os.path.join(OUT_DIR, f"pdf_line_{idx}.png")
    line_crop.save(out_p)
    print(f"PDF লাইন {idx} ক্রপ সেভ হয়েছে: {out_p} ({line_crop.size})")
