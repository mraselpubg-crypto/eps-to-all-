import os
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

with open("tarteel_resources.html", "r", encoding="utf-8") as f:
    html = f.read()

# Look for resource titles and links
cards = re.findall(r'<a\s+[^>]*href=["\'](/resources/[^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
print(f"মোট রিসোর্স কার্ড সংখ্যা: {len(cards)}")
seen = set()
for href, inner in cards:
    clean_t = re.sub(r'<[^>]+>', ' ', inner).strip()
    clean_t = re.sub(r'\s+', ' ', clean_t)
    if href not in seen:
        seen.add(href)
        print(f"  {href:35s} : {clean_t[:70]}")
