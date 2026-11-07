import os
import sys
import json
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

sys.stdout.reconfigure(encoding="utf-8")

SRC_TTF_DIR = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\source_fonts"
MASTER_JSON = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs\master_973_all_glyphs.json"

RENAME_MAP = {
    "apple": ["apple", "uniF8FF", " glyph240"],
    "Delta": ["Delta", "uni2206", "increment"],
    "Omega": ["Omega", "uni2126", "ohm"],
    "mu": ["mu", "uni00B5", "micro"],
    "nbspace": ["nbspace", "uni00A0", "nonbreakingspace", "space"],
    "DEL": ["DEL", "uni007F", "controlDEL"],
}

MAC_ROMAN_CODE = {
    "NUL": 0, "HT": 9, "CR": 13, "DLE": 16, "DC1": 17, "DC2": 18, "DC3": 19, "DC4": 20,
    "RS": 30, "US": 31, "DEL": 127, "nbspace": 202, "apple": 240, "Delta": 198, "Omega": 189, "mu": 181,
}

with open(MASTER_JSON, "r", encoding="utf-8") as fp:
    master = json.load(fp)

print("=== EXACT GEOMETRY & WIDTH CROSS-MATCH: 973-PAGE PDF vs GOOGLE DRIVE 12 TTFs ===")
total_pdf_glyphs = 0
total_matched = 0
unmatched_details = []

for fn in sorted(os.listdir(SRC_TTF_DIR)):
    if not fn.endswith(".ttf"):
        continue
    fam = fn[:-4]
    if fam not in master:
        continue
    tt = TTFont(os.path.join(SRC_TTF_DIR, fn))
    gset = tt.getGlyphSet()
    hmtx = tt["hmtx"].metrics
    mac_cmap = {}
    for t in tt["cmap"].tables:
        if t.platformID == 1 and t.platEncID == 0:
            mac_cmap = t.cmap
            break

    # Precompute bounds & widths of all TTF glyphs for fallback geometric matching
    ttf_geom = {}
    for tg in tt.getGlyphOrder():
        bp = BoundsPen(gset)
        gset[tg].draw(bp)
        ttf_geom[tg] = (hmtx[tg][0], bp.bounds)

    pdf_gdict = master[fam]["glyphs"]
    fam_total = 0
    fam_matched = 0
    fam_unmatched = []

    for pgname, vdict in pdf_gdict.items():
        if pgname == ".notdef":
            continue
        fam_total += 1
        total_pdf_glyphs += 1
        gv = next(iter(vdict.values()))
        pw = gv["width"]
        pb = gv["bounds"]

        # 1. Direct name match or known FontLab rename or MacRoman code match
        candidates = [pgname] + RENAME_MAP.get(pgname, [])
        if pgname in MAC_ROMAN_CODE and MAC_ROMAN_CODE[pgname] in mac_cmap:
            candidates.append(mac_cmap[MAC_ROMAN_CODE[pgname]])

        matched_tg = None
        for cand in candidates:
            if cand in ttf_geom:
                tw, tb = ttf_geom[cand]
                if abs(tw - pw) <= 1.5:
                    if (pb is None and tb is None) or (
                        pb is not None and tb is not None and max(abs(pb[i] - tb[i]) for i in range(4)) <= 2.5
                    ):
                        matched_tg = cand
                        break

        # 2. Pure geometric match across all 258 slots in TTF if renamed differently
        if matched_tg is None:
            for tg, (tw, tb) in ttf_geom.items():
                if abs(tw - pw) <= 1.5:
                    if (pb is None and tb is None) or (
                        pb is not None and tb is not None and max(abs(pb[i] - tb[i]) for i in range(4)) <= 2.5
                    ):
                        matched_tg = tg
                        break

        if matched_tg is not None:
            fam_matched += 1
            total_matched += 1
        else:
            fam_unmatched.append((pgname, pw, pb))
            unmatched_details.append((fam, pgname, pw, pb))

    print(
        f"  {fam:28s} | PDF Used: {fam_total:3d} | Matched in TTF: {fam_matched:3d}/{fam_total:3d} "
        f"({100*fam_matched/max(1,fam_total):5.1f}%) | Extra Unused Slots in TTF: {len(ttf_geom) - fam_matched}"
    )
    if fam_unmatched:
        print(f"      Unmatched in {fam}: {fam_unmatched[:5]}")

print(f"\nOVERALL 12-FONT CROSS-MATCH: {total_matched} / {total_pdf_glyphs} ({100*total_matched/max(1,total_pdf_glyphs):.2f}%)")

print("\n=== FONTS EXTRACTED 100% FROM 973-PAGE PDF + EPS (NOT IN THE 12-TTF GDRIVE FOLDER) ===")
for fam in ["AnicaKariSAKQS1", "AnicaKariSAKQS2", "AnicaKariSAKQS3", "AnicaKariSAKQS4", "AnicaBangali", "AnicaBangali-Bold", "KarianaBangali", "KarianaBangali-Bold", "TaheraFIKR-Plain", "TaheraFIKR-Harkat", "TaheraFIKR-Extra", "TaheraFIKR-Spare", "TaheraFIKR-Ornament", "TaheraFIKR-LW"]:
    if fam in master:
        gcnt = len([g for g in master[fam]["glyphs"] if g != ".notdef"])
        vis_cnt = len([g for g, vd in master[fam]["glyphs"].items() if g != ".notdef" and next(iter(vd.values()))["bounds"] is not None])
        print(f"  {fam:28s} | Total non-.notdef glyphs in 973-PDF: {gcnt:3d} (Visible drawn shapes: {vis_cnt:3d})")

print("\n=== DETAILED COMPARISON OF MODIFIED GLYPHS IN GDRIVE TTFs ===")
for fam, samples in [
    ("AnicaKariSAKQPlainExtra", ["B", "C", "D", "E", "I"]),
    ("AnicaKariSAKQPlainSpare", ["D", "E", "I", "M", "d"]),
    ("AnicaKariSAKQPlain", ["Edieresis", "Ydieresis", "F", "G", "P"]),
    ("AnicaKariSAKQHarkat", ["B", "P", "W", "greater", "quoteleft"]),
    ("AnicaKariSAKQA4", ["Idieresis", "Igrave", "Oacute", "Ograve", "Uacute"]),
]:
    tt = TTFont(os.path.join(SRC_TTF_DIR, f"{fam}.ttf"))
    gs = tt.getGlyphSet()
    hm = tt["hmtx"].metrics
    print(f"--- {fam} ---")
    for g in samples:
        pv = next(iter(master[fam]["glyphs"][g].values()))
        if g in gs:
            bp = BoundsPen(gs)
            gs[g].draw(bp)
            print(f"  {g:12s} | 973-PDF/EPS: w={pv['width']} bbox={pv['bounds']}  <-->  GDrive TTF: w={hm[g][0]} bbox={bp.bounds}")
        else:
            print(f"  {g:12s} | 973-PDF/EPS: w={pv['width']} bbox={pv['bounds']}  <-->  GDrive TTF: MISSING")
