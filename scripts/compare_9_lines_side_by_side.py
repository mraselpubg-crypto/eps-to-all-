import os
import sys
from PIL import Image, ImageDraw, ImageOps

sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = r"dist\comparison_9_lines"
os.makedirs(OUT_DIR, exist_ok=True)

for i in range(1, 10):
    eps_f = f"dist/eps_verified_lines/eps_line_{i}.png"
    pdf_f = f"dist/pdf_verified_lines/pdf_line_{i}.png"
    
    eps_img = Image.open(eps_f)
    pdf_img = Image.open(pdf_f)
    
    # Scale pdf_img to match eps_img width
    target_w = eps_img.width
    scale_factor = target_w / pdf_img.width
    target_h = int(pdf_img.height * scale_factor)
    pdf_scaled = pdf_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Canvas for side-by-side comparison
    canvas_h = eps_img.height + target_h + 80
    canvas = Image.new("RGB", (target_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    
    # Titles
    draw.text((20, 10), f"লাইন {i}: ১. আমাদের এক্সট্রাক্ট করা ভেক্টর আউটলাইন (Kariana Recover Font Data)", fill=(0, 100, 0))
    canvas.paste(eps_img, (0, 35))
    
    draw.text((20, 45 + eps_img.height), f"লাইন {i}: ২. মূল ৯৭৩ পৃষ্ঠার মাস্টার PDF স্ক্যান (আসল পৃষ্ঠা ২১)", fill=(180, 0, 0))
    canvas.paste(pdf_scaled, (0, 70 + eps_img.height))
    
    out_p = os.path.join(OUT_DIR, f"compare_line_{i}.png")
    canvas.save(out_p)
    print(f"লাইন {i} সাইড-বাই-সাইড কম্প্যারিজন সেভ হয়েছে: {out_p}")
