import os
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

def get_links(fname):
    print(f"\n--- {fname} ---")
    html = open(fname, encoding="utf-8").read()
    # find all a tags with Download woff2 or Download ttf
    for m in re.finditer(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL):
        href = m.group(1)
        text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if "download" in text.lower() or "ttf" in text.lower() or "woff" in text.lower():
            print(f"  {text:25s} -> {href}")

get_links("font_462.html")
get_links("font_568.html")
