import os
import sys
import json
import math
import pymupdf

sys.stdout.reconfigure(encoding="utf-8")

MASTER_JSON = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs\master_973_all_glyphs.json"
CHARTS_DIR = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\master_973_glyphs\charts"
os.makedirs(CHARTS_DIR, exist_ok=True)


def render_font_group_chart(master, font_names, out_png_name, cols=10):
    cells = []
    for fname in font_names:
        if fname not in master:
            continue
        glyphs = master[fname]["glyphs"]
        # Sort: standard ASCII first, then alphabetical
        for gname in sorted(glyphs.keys(), key=lambda g: (0 if len(g) == 1 else 1, g)):
            if gname == ".notdef":
                continue
            vdict = glyphs[gname]
            gv = next(iter(vdict.values()))
            cells.append((fname, gname, gv))

    if not cells:
        return

    rows = math.ceil(len(cells) / cols)
    cell_w = 135
    cell_h = 155
    svg_w = cols * cell_w + 20
    svg_h = rows * cell_h + 50

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}" style="background:#ffffff;font-family:Arial,sans-serif">',
        f'<text x="15" y="28" font-size="16" font-weight="bold" fill="#111">Kariana 973-Page Master Glyph Chart: {", ".join(font_names)} ({len(cells)} glyphs)</text>',
    ]

    for idx, (fname, gname, gv) in enumerate(cells):
        r = idx // cols
        c = idx % cols
        x0 = 10 + c * cell_w
        y0 = 40 + r * cell_h

        short_f = fname.replace("AnicaKariSAKQ", "").replace("Anica", "An.")
        w = gv["width"]
        bounds = gv["bounds"]
        path = gv["svg_path"]
        pages_cnt = gv["subset_count"]

        svg.append(f'<rect x="{x0+2}" y="{y0+2}" width="{cell_w-4}" height="{cell_h-4}" fill="#fcfcfc" stroke="#cccccc" stroke-width="1" rx="4"/>')

        # Determine optimal scale & anchor inside cell box (height ~95px for glyph)
        # Standard view window in font units: X in [-350..1050], Y in [-560..1460] (height 2020 -> scale 0.045 => 91px)
        scale = 0.046
        base_y = y0 + 88  # baseline Y=0 in cell
        # Top Tajweed band Y=1061..1422 -> base_y - 1422*0.046 .. base_y - 1061*0.046 = y0+22.6 .. y0+39.2
        top_b1 = base_y - 1422 * scale
        top_b2 = base_y - 1061 * scale
        svg.append(f'<rect x="{x0+6}" y="{top_b1:.1f}" width="{cell_w-12}" height="{top_b2-top_b1:.1f}" fill="#eef8ee" />')
        # Baseline Y=0
        svg.append(f'<line x1="{x0+6}" y1="{base_y:.1f}" x2="{x0+cell_w-6}" y2="{base_y:.1f}" stroke="#e0b0b0" stroke-width="0.8" />')

        if path and bounds:
            cx_font = (bounds[0] + bounds[2]) / 2.0
            # If bounds fit well at 0.055 scale, zoom slightly more for S1-S4/Harkat clarity!
            bw = max(bounds[2] - bounds[0], 1.0)
            bh = max(bounds[3] - bounds[1], 1.0)
            if fname.endswith(("S1", "S2", "S3", "S4")):
                # Center S1..S4 nicely in the middle of the box AND show a mini true-height indicator
                s_zoom = min(0.11, 80.0 / max(bw, bh, 250.0))
                cy_font = (bounds[1] + bounds[3]) / 2.0
                tx = x0 + cell_w / 2.0 - cx_font * s_zoom
                ty = y0 + 62 + cy_font * s_zoom
                svg.append(f'<path d="{path}" transform="translate({tx:.2f},{ty:.2f}) scale({s_zoom:.4f},{-s_zoom:.4f})" fill="#b42000" />')
            else:
                tx = x0 + cell_w / 2.0 - cx_font * scale
                ty = base_y
                svg.append(f'<path d="{path}" transform="translate({tx:.2f},{ty:.2f}) scale({scale:.4f},{-scale:.4f})" fill="#111111" />')
                # Draw advance width tick if width > 0
                if w > 0:
                    wx0 = tx
                    wx1 = tx + w * scale
                    svg.append(f'<line x1="{wx0:.1f}" y1="{base_y-3:.1f}" x2="{wx0:.1f}" y2="{base_y+3:.1f}" stroke="#0066cc" stroke-width="1"/>')
                    svg.append(f'<line x1="{wx1:.1f}" y1="{base_y-3:.1f}" x2="{wx1:.1f}" y2="{base_y+3:.1f}" stroke="#0066cc" stroke-width="1"/>')

        # Labels
        esc_g = gname.replace("&", "&amp;").replace("<", "&lt;")
        svg.append(f'<text x="{x0+6}" y="{y0+14}" font-size="9.5" fill="#0b5394" font-weight="bold">{short_f}</text>')
        svg.append(f'<text x="{x0+cell_w-6}" y="{y0+14}" font-size="8.5" fill="#666" text-anchor="end">p:{pages_cnt}</text>')
        svg.append(f'<text x="{x0+cell_w/2:.1f}" y="{y0+cell_h-20}" font-size="10.5" font-weight="bold" fill="#000" text-anchor="middle">{esc_g}</text>')
        b_str = f"w={int(round(w))}" + (f" y:[{int(bounds[1])}..{int(bounds[3])}]" if bounds else " [space]")
        svg.append(f'<text x="{x0+cell_w/2:.1f}" y="{y0+cell_h-7}" font-size="8.5" fill="#555" text-anchor="middle">{b_str}</text>')

    svg.append("</svg>")
    svg_str = "\n".join(svg)
    svg_path = os.path.join(CHARTS_DIR, out_png_name.replace(".png", ".svg"))
    png_path = os.path.join(CHARTS_DIR, out_png_name)
    with open(svg_path, "w", encoding="utf-8") as fp:
        fp.write(svg_str)

    sdoc = pymupdf.open(svg_path)
    pix = sdoc[0].get_pixmap(dpi=130)
    pix.save(png_path)
    sdoc.close()
    print(f"Generated chart: {out_png_name} ({len(cells)} glyphs)")


def main():
    with open(MASTER_JSON, "r", encoding="utf-8") as fp:
        master = json.load(fp)

    render_font_group_chart(
        master,
        ["AnicaKariSAKQS1", "AnicaKariSAKQS2", "AnicaKariSAKQS3", "AnicaKariSAKQS4", "AnicaKariSAKQA4"],
        "chart_01_top_symbols_S1_S4_A4.png",
        cols=10,
    )
    render_font_group_chart(
        master,
        ["AnicaKariSAKQHarkat", "AnicaKariSAKQHarkatExtra", "AnicaKariSAKQHarkatSpare"],
        "chart_02_harkat_all.png",
        cols=12,
    )
    render_font_group_chart(
        master,
        ["AnicaKariSAKQAW", "AnicaKariSAKQLW"],
        "chart_03_ayah_waqf_AW_LW.png",
        cols=12,
    )
    render_font_group_chart(
        master,
        ["AnicaKariSAKQPlain"],
        "chart_04_arabic_Plain.png",
        cols=12,
    )
    render_font_group_chart(
        master,
        ["AnicaKariSAKQPlainExtra", "AnicaKariSAKQPlainSpare"],
        "chart_05_arabic_PlainExtra_Spare.png",
        cols=10,
    )
    render_font_group_chart(
        master,
        ["AnicaKariSAKQA1", "AnicaKariSAKQA2", "AnicaKariSAKQA3"],
        "chart_06_bottom_symbols_A1_A3.png",
        cols=14,
    )
    render_font_group_chart(
        master,
        ["AnicaBangali", "AnicaBangali-Bold", "KarianaBangali", "KarianaBangali-Bold"],
        "chart_07_bangali_all.png",
        cols=15,
    )


if __name__ == "__main__":
    main()
