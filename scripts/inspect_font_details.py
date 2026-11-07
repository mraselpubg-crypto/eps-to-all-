import os
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

def analyze_page(fname, name):
    print(f"\n=================== {name} ({fname}) ===================")
    with open(fname, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Title & description
    m_title = re.search(r'<title>(.*?)</title>', html)
    if m_title: print("Title:", m_title.group(1))
    
    # Text overview
    m_desc = re.search(r'class=["\'][^"\']*description[^"\']*["\'][^>]*>(.*?)</div>', html, re.DOTALL)
    if m_desc:
        clean = re.sub(r'<[^>]+>', ' ', m_desc.group(1)).strip()
        print("Description:", clean[:300])
        
    # Download links
    links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
    print("Download Links:")
    for href, t in links:
        clean_t = re.sub(r'<[^>]+>', '', t).strip()
        if any(k in href.lower() for k in ["download", "zip", "ttf", "otf", "tarteel"]):
            print(f"  {clean_t:25s} -> {href}")

analyze_page("font_462.html", "KFGQPC Nastaleeq")
analyze_page("font_568.html", "Digital Khatt Indopak")
