import os
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

with open("tarteel_fonts_page.html", "r", encoding="utf-8") as f:
    html = f.read()

# Look for font cards
cards = re.findall(r'<div\s+class=["\'][^"\']*card[^"\']*["\'][^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
print(f"কার্ড সংখ্যা: {len(cards)}")

# Look for titles
titles = re.findall(r'<h[2345][^>]*>(.*?)</h[2345]>', html, re.DOTALL)
print("\n=== Fonts / Titles found ===")
for t in set(titles):
    clean_t = re.sub(r'<[^>]+>', ' ', t).strip()
    if clean_t and len(clean_t) < 80:
        print("  -", clean_t)

# Look for download links
links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
print("\n=== Font Download Links ===")
for href, t in links:
    clean_t = re.sub(r'<[^>]+>', '', t).strip()
    if any(k in href.lower() for k in ["font", "zip", "ttf", "otf"]):
        print(f"  {clean_t:30s} -> {href}")
