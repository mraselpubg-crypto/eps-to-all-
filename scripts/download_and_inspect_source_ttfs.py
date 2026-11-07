import os
import sys
import json
import urllib.request
from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\source_fonts"
os.makedirs(OUT_DIR, exist_ok=True)

FILES = [
    ("1ix5ycJe8ABNa29IcMiOQ9XNgo0OVzpCh", "AnicaKariSAKQA1.ttf"),
    ("1gsTl74_nS3DPMB3-GGIkrZg4AmNj_RvV", "AnicaKariSAKQA2.ttf"),
    ("1YiRnvfY4ZXiIPm8dA_Trw4PsczlbdfHO", "AnicaKariSAKQA3.ttf"),
    ("1R6Lh0PH2eiZVTgbDROJThkQZroKjaQYz", "AnicaKariSAKQA4.ttf"),
    ("1SOO4npMEdnbtoFBBp5UXISshPBzIsSkP", "AnicaKariSAKQAW.ttf"),
    ("1YQ_NlTq2zjc4nGUbkxVxkJBKs6hnXHQ6", "AnicaKariSAKQHarkat.ttf"),
    ("1AJsIno_d-SXaSUrViZ166-r6cImm7pxG", "AnicaKariSAKQHarkatExtra.ttf"),
    ("1plk2bAO0g_P2ljPd9agUGLhzaCdq8MRQ", "AnicaKariSAKQHarkatSpare.ttf"),
    ("1eFZ6JalaMSoMJxuTVBv4Ih5NKKSZxk_4", "AnicaKariSAKQLW.ttf"),
    ("1kK5RyMRnws4ahtQOY9bhsIh7qMy_Ip8m", "AnicaKariSAKQPlain.ttf"),
    ("1v2Kr-zf9p5uKQZhipxQA_aGoD6lmV-YI", "AnicaKariSAKQPlainExtra.ttf"),
    ("1vzj-QI_UIQdr5Cgb0R6EZhg5ZjF4rt6Z", "AnicaKariSAKQPlainSpare.ttf"),
]

master_json_path = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs\master_973_all_glyphs.json"
with open(master_json_path, "r", encoding="utf-8") as fp:
    master_973 = json.load(fp)

summary = {}
for fid, fname in FILES:
    dst = os.path.join(OUT_DIR, fname)
    if not os.path.exists(dst) or os.path.getsize(dst) < 1000:
        url = f"https://drive.google.com/uc?export=download&id={fid}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=30).read()
        with open(dst, "wb") as f:
            f.write(data)
    tt = TTFont(dst)
    upm = tt["head"].unitsPerEm
    gorder = tt.getGlyphOrder()
    fam_key = fname.replace(".ttf", "")
    pdf_glyphs = set(master_973.get(fam_key, {}).get("glyphs", {}).keys())
    ttf_set = set(gorder)
    missing_in_ttf = sorted(pdf_glyphs - ttf_set - {".notdef"})
    mac_cmap = {}
    win_cmap = {}
    for t in tt["cmap"].tables:
        if t.platformID == 1 and t.platEncID == 0:
            mac_cmap = dict(t.cmap)
        elif t.platformID == 3 and t.platEncID in (1, 0):
            win_cmap = dict(t.cmap)

    print(
        f"  {fname:30s} | size={os.path.getsize(dst):6d} B | UPM={upm} | "
        f"TTF glyphs={len(gorder):3d} | Used in 973-PDF={len(pdf_glyphs):3d} | "
        f"In PDF but not TTF={missing_in_ttf}"
    )
    summary[fam_key] = {
        "upm": upm,
        "glyph_count": len(gorder),
        "used_in_973_pdf": len(pdf_glyphs),
        "missing_in_ttf": missing_in_ttf,
        "mac_cmap_len": len(mac_cmap),
        "win_cmap_len": len(win_cmap),
    }

with open(os.path.join(OUT_DIR, "source_ttfs_comparison.json"), "w", encoding="utf-8") as fp:
    json.dump(summary, fp, indent=2, ensure_ascii=False)
