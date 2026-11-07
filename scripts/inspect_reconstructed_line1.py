import os
import sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

PNG_PATH = r"extracted_data\eps_page21\eps_page21_reconstructed_color_layers.png"
img = Image.open(PNG_PATH)
print(f"রিকনস্ট্রাক্টেড ইমেজ সাইজ: {img.size}")

# Page size was 595.28 x 841.89 pt.
# If image is e.g. 1190 x 1684 (2x scale):
# Let's crop line 1 (y ~ 140 to 195 pt)
scale = img.width / 595.28
print(f"স্কেল ফ্যাক্টর: {scale}")

crop_box = (int(80 * scale), int(135 * scale), int(515 * scale), int(195 * scale))
line1_crop = img.crop(crop_box)
out_crop = r"dist\reconstructed_line1_crop.png"
line1_crop.save(out_crop)
print(f"লাইন ১ রিকনস্ট্রাক্টেড ক্রপ সেভ হয়েছে:\n-> {out_crop}")
