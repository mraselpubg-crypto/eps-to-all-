import os
import sys
import re
import json

sys.stdout.reconfigure(encoding="utf-8")

with open("tarteel_page.html", "r", encoding="utf-8") as f:
    html = f.read()

print("ফাইল সাইজ:", len(html))

# Look for Next.js __NEXT_DATA__ or embedded json
m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    print("Found __NEXT_DATA__ keys:", list(data.keys()))
    props = data.get("props", {}).get("pageProps", {})
    print("pageProps keys:", list(props.keys()))
    print("Props preview:")
    for k, v in props.items():
        if isinstance(v, dict):
            print(f"  {k}: dict with keys {list(v.keys())}")
        elif isinstance(v, list):
            print(f"  {k}: list of length {len(v)}")
        else:
            print(f"  {k}: {v}")
    
    # Save props to a json file
    with open("tarteel_page_props.json", "w", encoding="utf-8") as pf:
        json.dump(props, pf, ensure_ascii=False, indent=2)
    print("tarteel_page_props.json সেভ করা হয়েছে।")
else:
    print("No __NEXT_DATA__ script found. Searching for JSON / API endpoints...")
    matches = re.findall(r'https?://[^\s"\'<>]+(?:json|api|mushaf)[^\s"\'<>]*', html)
    print("Found URLs:", set(matches[:15]))
