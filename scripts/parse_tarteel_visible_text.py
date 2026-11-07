import os
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

with open("tarteel_page.html", "r", encoding="utf-8") as f:
    html = f.read()

# Strip tags and print text blocks
# Also find all <a> and <button> and <select> tags
links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
print("=== Links found ===")
for href, text in links[:20]:
    clean_t = re.sub(r'<[^>]+>', '', text).strip()
    if clean_t or 'mushaf' in href or 'download' in href:
        print(f"  {clean_t} -> {href}")

# Find any JSON embedded in <script> tags
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"\nTotal scripts: {len(scripts)}")
for i, s in enumerate(scripts):
    s_clean = s.strip()
    if len(s_clean) > 50:
        print(f"  Script {i} snippet: {s_clean[:150]}...")

# Find forms or download targets
downloads = re.findall(r'(?:download|href|action|src)=["\']([^"\']+)["\']', html)
print("\nDownload-like targets:")
for d in set(downloads):
    if any(k in d.lower() for k in ["mushaf", "download", "json", "layout", "kfgqpc", "tarteel"]):
        print(" ", d)
