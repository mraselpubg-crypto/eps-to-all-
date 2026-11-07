import os
import sys
import struct
import re

sys.stdout.reconfigure(encoding="utf-8")

EPS_PATH = r"c:\xampp\htdocs\Bipul code craft Api\KariSAKQ_Para-01_21.eps"

with open(EPS_PATH, "rb") as f:
    data = f.read()

ps_offset, ps_length = struct.unpack("<II", data[4:12])
ps_bytes = data[ps_offset:ps_offset+ps_length]
ps_text = ps_bytes.decode("latin1", "replace")

sh_commands = re.findall(r'([\d\.\-]+)\s+([\d\.\-]+)\s+mov\s*\((.*?)\)\s*sh', ps_text)
print(f"মোট sh কমান্ড: {len(sh_commands)}")

for i, (x, y, s) in enumerate(sh_commands[:15], 1):
    print(f"[{i:2d}] X={float(x):6.2f}, Y={float(y):6.2f} | String len: {len(s)} | Hex: {s.encode('latin1', 'replace').hex()} | Raw: {repr(s)}")
