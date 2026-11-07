import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

with open('user_uploaded_package/page21_reference_lines.json', 'r', encoding='utf-8') as f:
    lines_ref = json.load(f)

with open('extracted_data/eps_page21/eps_page21_stream.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

# Arabic events for Line 1
l1_events = [e for e in events if abs(e['y'] - 169.73) < 3.0 and e['base_font'].startswith('AnicaKariSAKQ')]
# Sort Right-to-Left (highest X to lowest X)
l1_events.sort(key=lambda e: -e['x'])

# Split Line 1 reference text into words
words = lines_ref[0].split()
print("লাইন ১-এর মোট রেফারেন্স শব্দ:", len(words))
for i, w in enumerate(words):
    print(f"  শব্দ {i+1}: {w}")

# Group EPS events into words using spaces
word_clusters = []
current_cluster = []

for e in l1_events:
    if e['glyph'] == 'space':
        if current_cluster:
            word_clusters.append(current_cluster)
            current_cluster = []
    else:
        current_cluster.append(e)
if current_cluster:
    word_clusters.append(current_cluster)

print(f"\nEPS-এ স্পেস দ্বারা চিহ্নিত ক্লাস্টার সংখ্যা: {len(word_clusters)}")

for idx, cluster in enumerate(word_clusters):
    ref_w = words[idx] if idx < len(words) else "---"
    glyphs_str = ", ".join([f"{e['base_font'].replace('AnicaKariSAKQ', '')}.{e['glyph']}" for e in cluster])
    print(f"\n[শব্দ {idx+1}] ইউনিকোড: {ref_w} (x={cluster[0]['x']:.1f} .. {cluster[-1]['x']:.1f})")
    print(f"  ক্বারীয়ানা গ্লিফ সিকোয়েন্স: {glyphs_str}")
