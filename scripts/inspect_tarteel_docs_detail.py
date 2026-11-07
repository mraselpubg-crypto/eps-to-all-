import os
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

with open("tarteel_docs.html", "r", encoding="utf-8") as f:
    html = f.read()

# Look for font references
fonts = re.findall(r'https?://[^\s"\'<>]+\.(?:ttf|otf|woff2|woff)', html)
print(f"সরাসরি ফন্ট লিংক: {set(fonts)}")

# Look for CSS @font-face rules
font_faces = re.findall(r'@font-face\s*\{[^}]+\}', html)
print(f"Font face রুলস সংখ্যা: {len(font_faces)}")
for ff in font_faces:
    print(" ", ff.replace("\n", " "))

# Let's see what resources are listed on https://qul.tarteel.ai/resources
# Let's inspect all mushaf layouts available
