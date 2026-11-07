import os
import sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

IMG_PATH = r"dist\page31_original_highres.png"
OUT_DIR = r"dist\line1_words"
os.makedirs(OUT_DIR, exist_ok=True)

img = Image.open(IMG_PATH)
w_img, h_img = img.size

# Line 1 bbox in 150 DPI image
# Page size: 1241 x 1754
# Arabic text box: x ~ 180 to 1050, y ~ 290 to 420
scale = 150 / 72.0

# Crop full line 1
line1_crop = img.crop((int(90 * scale), int(135 * scale), int(505 * scale), int(195 * scale)))
line1_crop.save(os.path.join(OUT_DIR, "line1_full.png"))
print(f"লাইন ১ সম্পূর্ণ ক্রপ সেভ হয়েছে: {os.path.join(OUT_DIR, 'line1_full.png')} ({line1_crop.size})")

# Let's crop 5 slices from Right to Left across Line 1
# Width of line1_crop is ~864 px
total_w = line1_crop.width
slice_w = total_w // 5
for i in range(5):
    # i=0 is rightmost slice (Arabic start)
    x1 = total_w - (i + 1) * slice_w
    x2 = total_w - i * slice_w
    slice_img = line1_crop.crop((x1, 0, x2, line1_crop.height))
    out_f = os.path.join(OUT_DIR, f"slice_{i+1}_rtl.png")
    slice_img.save(out_f)
    print(f"  স্লাইস {i+1} (RTL): {out_f}")
