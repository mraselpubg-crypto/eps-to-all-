import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

STREAM_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\eps_page21\eps_page21_stream.json"

with open(STREAM_PATH, "r", encoding="utf-8") as f:
    events = json.load(f)

line1 = [e for e in events if abs(e["y"] - 169.7) < 5.0 and "Bangali" not in e["base_font"]]
line1.sort(key=lambda e: -e["x"]) # Right to left (high X to low X)

# Group into words by space glyphs (space in Plain or AW)
words = []
curr_word = []
for e in line1:
    if e["glyph"] == "space":
        if curr_word:
            words.append(curr_word)
            curr_word = []
    else:
        curr_word.append(e)
if curr_word:
    words.append(curr_word)

print(f"লাইন ১-এ মোট শব্দ সংখ্যা: {len(words)}\n")

for w_idx, w in enumerate(words, 1):
    x_start = w[0]["x"]
    x_end = w[-1]["x"]
    bases = [f"{e['base_font'].replace('AnicaKariSAKQ', '')}:{e['glyph']}" for e in w if "Plain" in e["base_font"]]
    harkats = [f"{e['base_font'].replace('AnicaKariSAKQ', '')}:{e['glyph']}" for e in w if "Harkat" in e["base_font"]]
    tajweeds = [f"{e['base_font'].replace('AnicaKariSAKQ', '')}:{e['glyph']}" for e in w if any(s in e["base_font"] for s in ["S1", "S2", "S3", "S4", "A4"])]
    print(f"--- শব্দ {w_idx} (X: {x_start:5.1f} -> {x_end:5.1f}, মোট গ্লিফ: {len(w)}) ---")
    print(f"  হরফ (Plain):    {bases}")
    print(f"  হরকত (Harkat):  {harkats}")
    print(f"  ★ তাজবীদ প্রতীক: {tajweeds}")
