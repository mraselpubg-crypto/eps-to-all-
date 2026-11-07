import os
import sys
import json
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

ayahs = [
    ("2:85", "Surah Baqarah Ayah 85"),
    ("2:86", "Surah Baqarah Ayah 86"),
    ("2:87", "Surah Baqarah Ayah 87")
]

fetched_data = []

for ayah_id, title in ayahs:
    url = f"http://api.alquran.cloud/v1/ayah/{ayah_id}/quran-uthmani"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            res_json = json.loads(res.read().decode("utf-8"))
            ayah_text = res_json.get("data", {}).get("text", "")
            fetched_data.append({
                "ayah_id": ayah_id,
                "title": title,
                "text": ayah_text
            })
            print(f"ডাউনলোড সম্পন্ন: {title} ({len(ayah_text)} অক্ষর)")
    except Exception as e:
        print(f"ত্রুটি: {title} - {e}")

out_path = r"extracted_data\international_quran_sample.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(fetched_data, f, ensure_ascii=False, indent=2)

print(f"\nআন্তর্জাতিক প্রোভাইডার টেক্সট সংরক্ষিত হয়েছে:\n-> {out_path}")
