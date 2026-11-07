import os
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

for fn in ["font_462.html", "font_568.html"]:
    html = open(fn, encoding="utf-8").read()
    print(f"\n--- {fn} ---")
    urls = re.findall(r'(https?://[^\s"\'<>]+\.(?:ttf|otf|woff2?)[^\s"\'<>]*)', html)
    print("Direct font URLs:", urls)
    
    # check for stimulus controller or data-url
    targets = re.findall(r'data-[^=]+=["\']([^"\']+)["\']', html)
    for t in targets:
        if any(ext in t for ext in [".ttf", ".otf", ".woff", "download", "cdn"]):
            print("Target data attr:", t)
