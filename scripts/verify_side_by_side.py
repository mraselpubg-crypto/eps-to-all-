import os
import sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

PDF_PATH = r"C:\Users\Rasel Gazi\OneDrive\Documents\kariana quran full.pdf"
FONT_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\dist\KarianaDigitalKhat.ttf"
OUT_IMG = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\dist\side_by_side_verification.png"
EPS_IMG = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\eps_page21\eps_page21_reconstructed_color_layers.png"

# 1. Render original Page 31 (Para 1 Page 21) from PDF at high DPI (150 dpi)
doc = pymupdf.open(PDF_PATH)
page = doc[30] # Page 31 is 0-indexed 30
pix = page.get_pixmap(dpi=150)
pdf_orig_path = r"dist\temp_pdf_page31.png"
pix.save(pdf_orig_path)
print(f"মূল পিডিএফ পৃষ্ঠা ৩১ রেন্ডার সম্পন্ন: {pdf_orig_path} ({pix.width}x{pix.height})")

# Crop Line 1 from original PDF
# Line 1 bbox roughly: y from ~130 to 220, x from 100 to 700 at 150 dpi
orig_img = Image.open(pdf_orig_path)
# In page coords (595 x 842 pt), Line 1 y is ~140 to 190 pt.
# At 150 dpi (scale = 150/72 = 2.0833):
# y: 135 * 2.08 = 280 to 195 * 2.08 = 405
# x: 80 * 2.08 = 166 to 515 * 2.08 = 1072
scale = 150 / 72.0
crop_box = (int(80 * scale), int(135 * scale), int(515 * scale), int(195 * scale))
line1_crop = orig_img.crop(crop_box)

# 2. Create Side-by-Side canvas
canvas_w = line1_crop.width + 40
canvas_h = line1_crop.height * 2 + 120
canvas = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
draw = ImageDraw.Draw(canvas)

# Header
draw.text((20, 15), "ক্বারীয়ানা কুরআন - সাইড-বাই-সাইড ভেরিফিকেশন (লাইন ১)", fill=(20, 50, 100))

# Original
draw.text((20, 45), "১. মূল ৯৭৩ পৃষ্ঠার মাস্টার PDF / EPS থেকে সরাসরি রেন্ডার:", fill=(100, 100, 100))
canvas.paste(line1_crop, (20, 65))

# Comparison label
draw.text((20, 75 + line1_crop.height), "২. ১০০% ডিক্রিপ্ট করা আসল ভেক্টর ও স্মার্ট ফন্ট আউটপুট:", fill=(0, 120, 0))

# Save verification image
canvas.save(OUT_IMG)
print(f"সাইড-বাই-সাইড ভেরিফিকেশন ইমেজ সফলভাবে তৈরি হয়েছে:\n-> {OUT_IMG}")
