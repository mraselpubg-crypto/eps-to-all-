import os
import sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

img = Image.open("dist/eps_verified_lines/eps_line_1.png")
w, h = img.size

# Rightmost 20%
right_crop = img.crop((int(w * 0.8), 0, w, h))
right_crop.save("dist/check_right_word.png")

# Leftmost 20%
left_crop = img.crop((0, 0, int(w * 0.2), h))
left_crop.save("dist/check_left_word.png")

print(f"ডান ও বাম প্রান্তের ছবি সেভ সম্পন্ন:\n-> dist/check_right_word.png\n-> dist/check_left_word.png")
