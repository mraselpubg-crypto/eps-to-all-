import os
import io
import sys
import json
import time
import hashlib
from collections import defaultdict
import pymupdf
from fontTools.cffLib import CFFFontSet
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

sys.stdout.reconfigure(encoding="utf-8")

PDF_PATH = r"C:\Users\Rasel Gazi\OneDrive\Documents\kariana quran full.pdf"
INV_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\pdf_973_font_inventory.json"
EPS_FONTS_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\eps_page21\eps_page21_fonts.json"
OUT_DIR = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs"
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    t0 = time.time()
    with open(INV_PATH, "r", encoding="utf-8") as fp:
        inv = json.load(fp)

    doc = pymupdf.open(PDF_PATH)
    xrefs_dict = inv["xrefs"]
    total_xrefs = len(xrefs_dict)
    print(f"Fast-decompiling all {total_xrefs} embedded CFF font subsets across 973 pages...")

    master_fonts = defaultdict(lambda: {"bboxes": set(), "glyphs": defaultdict(dict)})
    # Cache (clean_base, gname, bytecode_key) -> vkey so SVGPathPen only runs on new bytecodes!
    bytecode_cache = {}
    errors = []

    for idx, (xref_str, xinfo) in enumerate(xrefs_dict.items(), 1):
        xref = int(xref_str)
        clean_base = xinfo["clean_base"]
        first_page = xinfo["first_page"]
        try:
            basename, ext, subtype, content = doc.extract_font(xref)
            if not content:
                continue
            cff = CFFFontSet()
            cff.decompile(io.BytesIO(content), None)
            top = cff[0]
            if hasattr(top, "FontBBox") and top.FontBBox:
                master_fonts[clean_base]["bboxes"].add(tuple(top.FontBBox))

            priv = top.Private if hasattr(top, "Private") else None
            def_w = getattr(priv, "defaultWidthX", 0)
            nom_w = getattr(priv, "nominalWidthX", 0)
            local_subrs = getattr(priv, "Subrs", None)
            subr_sig = b""
            if local_subrs is not None:
                subr_sig = b"|".join(bytes(local_subrs[i].bytecode) for i in range(len(local_subrs)))
            global_subrs = getattr(cff, "GlobalSubrs", None)
            gsubr_sig = b""
            if global_subrs is not None:
                gsubr_sig = b"|".join(bytes(global_subrs[i].bytecode) for i in range(len(global_subrs)))
            font_subr_hash = hashlib.md5(subr_sig + b"||" + gsubr_sig + f"|{def_w}|{nom_w}".encode()).digest()

            gs = top.CharStrings
            cs_idx = gs.charStringsIndex

            for gname, gid in gs.charStrings.items():
                cs_lazy = cs_idx[gid]
                raw_b = bytes(cs_lazy.bytecode)
                bkey = (clean_base, gname, raw_b, font_subr_hash)
                vkey = bytecode_cache.get(bkey)
                gvariants = master_fonts[clean_base]["glyphs"][gname]
                if vkey is not None and vkey in gvariants:
                    gv = gvariants[vkey]
                    gv["subset_count"] += 1
                    if len(gv["sample_pages"]) < 5 and first_page not in gv["sample_pages"]:
                        gv["sample_pages"].append(first_page)
                    continue

                # New bytecode! Decompile & draw via SVGPathPen + BoundsPen to get canonical geometry hash
                cs = gs[gname]
                pen = SVGPathPen(gs)
                cs.draw(pen)
                svg_cmd = pen.getCommands()
                w = cs.width
                vkey = hashlib.sha256(f"{w:.2f}|{svg_cmd}".encode("utf-8")).hexdigest()[:16]
                bytecode_cache[bkey] = vkey

                if vkey not in gvariants:
                    bpen = BoundsPen(gs)
                    cs.draw(bpen)
                    gvariants[vkey] = {
                        "width": w,
                        "bounds": [round(x, 3) for x in bpen.bounds] if bpen.bounds else None,
                        "svg_path": svg_cmd,
                        "subset_count": 1,
                        "first_page": first_page,
                        "sample_pages": [first_page],
                    }
                else:
                    gv = gvariants[vkey]
                    gv["subset_count"] += 1
                    if len(gv["sample_pages"]) < 5 and first_page not in gv["sample_pages"]:
                        gv["sample_pages"].append(first_page)

        except Exception as e:
            errors.append((xref, clean_base, str(e)))

        if idx % 4000 == 0 or idx == total_xrefs:
            print(f"  Processed {idx}/{total_xrefs} font xrefs ({time.time() - t0:.1f}s) | cache={len(bytecode_cache)}...")

    doc.close()
    print(f"\nCompleted 973-page CFF extraction in {time.time() - t0:.1f}s! Errors: {len(errors)}")
    if errors:
        print("Sample errors:", errors[:5])

    summary_report = {}
    serializable_master = {}

    print("\n=== COMPLETE 973-PAGE GLYPH INVENTORY BY FONT FAMILY ===")
    for fam in sorted(master_fonts.keys()):
        finfo = master_fonts[fam]
        glyphs_map = finfo["glyphs"]
        unique_names = len(glyphs_map)
        total_variants = sum(len(v) for v in glyphs_map.values())
        multi_variant_glyphs = {g: len(v) for g, v in glyphs_map.items() if len(v) > 1 and g != ".notdef"}

        all_bounds = [
            gv["bounds"]
            for vdict in glyphs_map.values()
            for gv in vdict.values()
            if gv["bounds"] is not None
        ]
        union_bbox = None
        if all_bounds:
            union_bbox = [
                round(min(b[0] for b in all_bounds), 2),
                round(min(b[1] for b in all_bounds), 2),
                round(max(b[2] for b in all_bounds), 2),
                round(max(b[3] for b in all_bounds), 2),
            ]

        print(
            f"  {fam:30s} | Glyphs: {unique_names:4d} | Variants: {total_variants:4d} | "
            f"MultiVar(excl .notdef): {len(multi_variant_glyphs):2d} | UnionBBox: {union_bbox}"
        )
        if multi_variant_glyphs:
            print(f"      -> Multi-variant glyphs in {fam}: {multi_variant_glyphs}")

        summary_report[fam] = {
            "declared_bboxes": [list(b) for b in sorted(finfo["bboxes"])],
            "union_glyph_bbox": union_bbox,
            "unique_glyph_names": unique_names,
            "total_variants": total_variants,
            "multi_variant_glyphs": multi_variant_glyphs,
        }
        serializable_master[fam] = {
            "declared_bboxes": [list(b) for b in sorted(finfo["bboxes"])],
            "union_glyph_bbox": union_bbox,
            "glyphs": dict(glyphs_map),
        }

    # Cross-check EPS Page 21 decrypted Type 1 glyphs vs 973-page PDF CFF glyphs!
    if os.path.exists(EPS_FONTS_PATH):
        with open(EPS_FONTS_PATH, "r", encoding="utf-8") as fp:
            eps_fonts = json.load(fp)
        eps_checked = 0
        eps_exact = 0
        eps_width_match = 0
        mismatches = []
        for fname, finfo in eps_fonts.items():
            if fname not in serializable_master:
                continue
            for gname, gdata in finfo["glyphs"].items():
                if gname == ".notdef":
                    continue
                eps_checked += 1
                pdf_vars = serializable_master[fname]["glyphs"].get(gname, {})
                if any(abs(v["width"] - gdata["width"]) < 0.01 for v in pdf_vars.values()):
                    eps_width_match += 1
                if any(v["svg_path"] == gdata["svg_path"] and abs(v["width"] - gdata["width"]) < 0.01 for v in pdf_vars.values()):
                    eps_exact += 1
                else:
                    mismatches.append((fname, gname))
        print(
            f"\n=== EPS Type 1 vs 973-Page PDF CFF Cross-Verification ===\n"
            f"  Checked non-.notdef glyphs: {eps_checked} | Width Match: {eps_width_match}/{eps_checked} | "
            f"Byte-Identical SVG Path Match: {eps_exact}/{eps_checked}"
        )
        if mismatches:
            print("  Sample SVG formatting diffs:", mismatches[:10])

    with open(os.path.join(OUT_DIR, "master_973_summary.json"), "w", encoding="utf-8") as fp:
        json.dump(summary_report, fp, indent=2, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, "master_973_all_glyphs.json"), "w", encoding="utf-8") as fp:
        json.dump(serializable_master, fp, indent=2, ensure_ascii=False)

    print(f"\nSaved complete 973-page master glyph database to {OUT_DIR}!")


if __name__ == "__main__":
    main()
