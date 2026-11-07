import os
import sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

IMG_PATH = r"dist\authentic_eps_render.png"
OUT_DIR = r"dist\eps_verified_lines"
os.makedirs(OUT_DIR, exist_ok=True)

img = Image.open(IMG_PATH)
w, h = img.size
print(f"আসল EPS রেন্ডার সাইজ: {w} x {h}")

# In authentic_eps_render.png (viewBox 595.28 x 841.89, rendered at 150 dpi -> 2480 x 3509)
# scale = 2480 / 595.28 = 4.166
scale = w / 595.28

# Baselines for the 9 Arabic lines:
baselines = [169.73, 234.17, 298.61, 363.05, 427.49, 491.93, 556.37, 620.81, 685.25]

for idx, y_base in enumerate(baselines, 1):
    # Top symbol is at y_base - 26.5 * 1.422 ~ y_base - 38
    # Bottom of letter is at y_base + 10
    # Line band height: y_base - 42 to y_base + 12
    y1 = int((y_base - 42) * scale)
    y2 = int((y_base + 12) * scale)
    x1 = int(85 * scale)
    x2 = int(510 * scale)
    
    line_crop = img.crop((x1, y1, x2, y2))
    out_p = os.path.join(OUT_DIR, f"eps_line_{idx}.png")
    line_crop.save(out_p)
    print(f"লাইন {idx} ক্রপ সেভ হয়েছে: {out_p} ({line_crop.size})")
