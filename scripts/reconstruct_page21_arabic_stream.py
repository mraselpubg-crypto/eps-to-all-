import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open('extracted_data/eps_page21/eps_page21_stream.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

# Filter Arabic events
ar_events = [e for e in events if e['base_font'].startswith('AnicaKariSAKQ')]

# 9 Baselines
lines_y = [169.73, 234.18, 298.63, 363.07, 427.52, 491.97, 556.41, 620.86, 685.31]

def get_line_events(y_target):
    evs = [e for e in ar_events if abs(e['y'] - y_target) < 3.0]
    # Sort from Right to Left (highest X to lowest X)
    evs.sort(key=lambda x: -x['x'])
    return evs

print("=== পৃষ্ঠা ২১-এর ৯টি লাইনের গ্লিফ সংখ্যা ও সীমানা ===")
for i, y in enumerate(lines_y):
    evs = get_line_events(y)
    first_g = evs[0]['glyph'] if evs else ""
    first_f = evs[0]['base_font'] if evs else ""
    last_g = evs[-1]['glyph'] if evs else ""
    last_f = evs[-1]['base_font'] if evs else ""
    print(f"লাইন {i+1} (Y={y:.2f}): মোট গ্লিফ={len(evs)} | শুরু (Right, x={evs[0]['x']:.1f}): {first_f}:{first_g} | শেষ (Left, x={evs[-1]['x']:.1f}): {last_f}:{last_g}")
