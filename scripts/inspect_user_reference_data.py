import os
import sys
import json
from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding="utf-8")

JSON_PATH = r"user_reference\digital-khatt-indopak-ayah-by-ayah-script.json"
OTF_PATH = r"user_reference\DigitalKhattIndoPak.otf"

print("=================== JSON ফাইল বিশ্লেষণ ===================")
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"JSON ডেটা টাইপ: {type(data)}")
if isinstance(data, list):
    print(f"মোট এন্ট্রি সংখ্যা: {len(data)}")
    print(f"প্রথম ৩টি এন্ট্রির স্যাম্পল:")
    for item in data[:3]:
        print(f"  {item}")
elif isinstance(data, dict):
    print(f"মোট কি (Keys): {len(data)}")
    print(f"কি সমূহের তালিকা (প্রথম ১০টি): {list(data.keys())[:10]}")
    for k in list(data.keys())[:2]:
        val = data[k]
        print(f"\nকি: {k}")
        if isinstance(val, dict):
            print(f"  মান (dict keys): {list(val.keys())}")
            for vk in list(val.keys())[:5]:
                print(f"    {vk}: {val[vk]}")
        else:
            print(f"  মান: {str(val)[:150]}")

print("\n=================== OTF ফন্ট বিশ্লেষণ ===================")
font = TTFont(OTF_PATH)
print("টেবিল তালিকা:", list(font.keys()))
print("মোট গ্লিফ সংখ্যা:", len(font.getGlyphOrder()))

# Check cmap
cmap = font.getBestCmap()
if cmap:
    print(f"ম্যাপ করা ইউনিকোড অক্ষর সংখ্যা: {len(cmap)}")
    # Sample mapped code points
    for cp in sorted(cmap.keys())[:15]:
        print(f"  U+{cp:04X} ({chr(cp) if cp > 32 else 'ctrl'}) -> {cmap[cp]}")

# Check GSUB
if "GSUB" in font:
    gsub = font["GSUB"].table
    scripts = [s.ScriptTag for s in gsub.ScriptList.ScriptRecord]
    features = [f.FeatureTag for f in gsub.FeatureList.FeatureRecord]
    print(f"GSUB স্ক্রিপ্ট: {scripts}")
    print(f"GSUB ফিচারসমূহ: {set(features)}")
    print(f"GSUB লুকআপ সংখ্যা: {len(gsub.LookupList.Lookup)}")
