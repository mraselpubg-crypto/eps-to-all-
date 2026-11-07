import os
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

with open("font_462.html", "r", encoding="utf-8") as f:
    h462 = f.read()

# Find buttons and forms
buttons = re.findall(r'<button[^>]*>(.*?)</button>', h462, re.DOTALL)
print("462 Buttons:", [re.sub(r'<[^>]+>', '', b).strip() for b in buttons if b.strip()])

# Find all links with /downloads or /cms
downloads = re.findall(r'href=["\'](/[^"\']+)["\']', h462)
for d in set(downloads):
    if any(k in d for k in ["download", "file", "resource", "font", "attachment"]):
        print("  Download link:", d)

# Find any text paragraphs
paras = re.findall(r'<p[^>]*>(.*?)</p>', h462, re.DOTALL)
for p in paras[:8]:
    clean = re.sub(r'<[^>]+>', ' ', p).strip()
    if clean:
        print("  P:", clean)
