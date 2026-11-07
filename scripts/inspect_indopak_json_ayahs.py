import os
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

JSON_PATH = r"user_reference\digital-khatt-indopak-ayah-by-ayah-script.json"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== সূরা ফাতিহা (১:১ থেকে ১:৭) ===")
for i in range(1, 8):
    key = f"1:{i}"
    item = data.get(key, {})
    print(f"[{key}] {item.get('text', '')}")

print("\n=== সূরা বাক্বারাহ (২:৮৫ থেকে ২:৮৭) ===")
for i in range(85, 88):
    key = f"2:{i}"
    item = data.get(key, {})
    print(f"[{key}] {item.get('text', '')}")
