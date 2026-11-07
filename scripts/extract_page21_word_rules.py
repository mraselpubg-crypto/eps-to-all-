import os
import sys
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

STREAM_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\eps_page21\eps_page21_stream.json"

with open(STREAM_PATH, "r", encoding="utf-8") as f:
    events = json.load(f)

# Group events by line (Arabic baselines: ~169.73, 234.17, 298.61, 363.05, 427.49, 491.93, 556.37, 620.81, 685.25)
lines = defaultdict(list)
for ev in events:
    # Filter Arabic and symbol fonts only
    if ev["base_font"].startswith("AnicaKariSAKQ"):
        # Match nearest baseline
        y = ev["y"]
        matched_line = round(y, 1)
        lines[matched_line].append(ev)

print(f"শনাক্তকৃত আরবি লাইন সংখ্যা: {len(lines)}\n")

for line_idx, (y_base, line_events) in enumerate(sorted(lines.items()), 1):
    # Sort events by X coordinate (Right to Left: high X to low X)
    rtl_events = sorted(line_events, key=lambda e: -e["x"])
    
    # Separate into Base letters, Harakats, Top Symbols, Ayah/Waqf
    print(f"=== লাইন {line_idx} (Y = {y_base}, মোট ইভেন্ট: {len(rtl_events)}) ===")
    
    # We can track cluster of glyphs sharing the same X range
    clusters = []
    current_cluster = []
    last_x = None
    
    for ev in rtl_events:
        x = ev["x"]
        if last_x is None or abs(x - last_x) < 8.0:
            current_cluster.append(ev)
        else:
            clusters.append(current_cluster)
            current_cluster = [ev]
        last_x = x
    if current_cluster:
        clusters.append(current_cluster)
        
    print(f"  শনাক্তকৃত অক্ষর/চিহ্ন ক্লাস্টার সংখ্যা: {len(clusters)}")
    for c_idx, cluster in enumerate(clusters[:10], 1): # show first 10 clusters of line
        bases = [e["glyph"] for e in cluster if "Plain" in e["base_font"]]
        harkats = [e["glyph"] for e in cluster if "Harkat" in e["base_font"]]
        symbols = [f"{e['base_font'][-2:]}:{e['glyph']}" for e in cluster if any(s in e["base_font"] for s in ["S1", "S2", "S3", "S4", "A4"])]
        waqf = [e["glyph"] for e in cluster if "AW" in e["base_font"] or "LW" in e["base_font"]]
        
        info = []
        if bases: info.append(f"হরফ: {bases}")
        if harkats: info.append(f"হরকত: {harkats}")
        if symbols: info.append(f"★ তাজবীদ চিহ্ন: {symbols}")
        if waqf: info.append(f"ওয়াকফ/আয়াত: {waqf}")
        
        avg_x = round(sum(e["x"] for e in cluster) / len(cluster), 1)
        print(f"    [{c_idx:2d}] X={avg_x:5.1f} | {' | '.join(info)}")
    print("    ...")
