import os
import sys
from PIL import Image
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

eps_f = "dist/eps_verified_lines/eps_line_1.png"
pdf_f = "dist/pdf_verified_lines/pdf_line_1.png"

eps_img = Image.open(eps_f).convert("L")
pdf_img = Image.open(pdf_f).convert("L")

# Resize pdf_img to match eps_img exactly
pdf_resized = pdf_img.resize(eps_img.size, Image.Resampling.LANCZOS)

# Binarize both images (text is black, background is white)
eps_arr = np.array(eps_img) < 180
pdf_arr = np.array(pdf_resized) < 180

intersection = np.logical_and(eps_arr, pdf_arr).sum()
union = np.logical_or(eps_arr, pdf_arr).sum()
iou = intersection / union if union > 0 else 0

print(f"লাইন ১ ইন্টারসেকশন ও ইউনিয়ন অ্যানালিসিস:")
print(f"  ইন্টারসেকশন পিক্সেল: {intersection:,}")
print(f"  ইউনিয়ন পিক্সেল:       {union:,}")
print(f"  ভিজ্যুয়াল ওভারল্যাপ (IoU): {iou * 100:.2f}%")
