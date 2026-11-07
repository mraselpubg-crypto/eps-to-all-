import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

os.makedirs("reference_fonts", exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://qul.tarteel.ai/"
}

fonts = [
    ("https://static-cdn.tarteel.ai/qul/fonts/nastaleeq/KFGQPCNastaleeq-Regular.ttf", "reference_fonts/KFGQPCNastaleeq-Regular.ttf"),
    ("https://static-cdn.tarteel.ai/qul/fonts/dk/DigitalKhattIndoPak.otf", "reference_fonts/DigitalKhattIndoPak.otf")
]

for url, dest in fonts:
    print(f"Downloading {url} ...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as res:
            data = res.read()
            with open(dest, "wb") as f:
                f.write(data)
            print(f"  -> Saved {dest} ({len(data):,} bytes)")
    except Exception as e:
        print(f"  Failed: {e}")
