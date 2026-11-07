import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

STREAM_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\eps_page21\eps_page21_stream.json"

with open(STREAM_PATH, "r", encoding="utf-8") as f:
    events = json.load(f)

bangla_events = [e for e in events if "Bangali" in e["base_font"]]
print(f"পৃষ্ঠা ২১-এ বাংলা ইভেন্ট সংখ্যা: {len(bangla_events)}")

# Sort by Y ascending (top to bottom), then X ascending (left to right)
lines = {}
for e in bangla_events:
    y = round(e["y"], 1)
    if y not in lines: lines[y] = []
    lines[y].append(e)

print(f"মোট বাংলা লাইন সংখ্যা: {len(lines)}")
for y, line_evs in sorted(lines.items()):
    line_evs.sort(key=lambda x: x["x"])
    text_chars = "".join([e["glyph"] if len(e["glyph"]) == 1 else f"[{e['glyph']}]" for e in line_evs])
    print(f"  Y={y:5.1f} | Glyphs: {text_chars[:60]}...")
