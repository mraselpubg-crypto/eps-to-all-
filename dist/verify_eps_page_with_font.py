#!/usr/bin/env python3
"""
Verify any decoded EPS page against the Kariana Quran Recover Font.

Usage:
  python scripts/verify_eps_page_with_font.py \
      --stream extracted_data/eps_page21/eps_page21_stream.json \
      --tag page21 \
      [--eps-png dist/authentic_eps_render.png] [--lines lines.json]

--stream  is the glyph-event stream written by scripts/phase1_eps_decoder.py for a
          given .eps file (list of {x,y,sx,sy,base_font,glyph,...}).
Renders three full-page rasters with headless Chromium (2480x3509):
  R1  every event drawn from the original decrypted vector paths  (ground truth)
  R2  core Kariana events drawn as TEXT with KarianaQuranRecoverFont.ttf
  R3  same with KarianaQuranRecoverFont.otf
then diffs R2/R3 against R1 (and R1 against the real EPS render, if given) and
writes dist/verify/<tag>/ images + report.json + dist/kuran_<tag>_recover_font_verification.html
"""
import argparse
import base64
import json
import os
import sys

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
MASTER = os.path.join(ROOT, "extracted_data", "master_973_glyphs", "master_973_all_glyphs.json")
PUA_MAP = os.path.join(DIST, "kariana_recover_pua_map.json")
PAGE_W, PAGE_H = 595.28, 841.89
PX_W, PX_H = 2480, 3509
FONT_FAMILY = "Kariana Quran Recover Font"


def load(args):
    stream = json.load(open(args.stream, encoding="utf-8"))
    master = json.load(open(MASTER, encoding="utf-8"))
    pua = json.load(open(PUA_MAP, encoding="utf-8"))
    return stream, master, pua


def path_of(master, ev):
    fam = master.get(ev["base_font"], {}).get("glyphs", {})
    v = fam.get(ev["glyph"])
    if not v:
        return None
    gv = next(iter(v.values()))
    return gv["svg_path"] or None


def build_events(stream, master, pua):
    """Split events into core (font text) and other (vector path) drawables."""
    core, other, skipped = [], [], 0
    for ev in stream:
        if ev["sx"] == 0 or ev["sy"] == 0:
            skipped += 1
            continue
        d = path_of(master, ev)
        if not d:
            skipped += 1
            continue
        key = f"{ev['base_font']}/{ev['glyph']}"
        if key in pua:
            ch = int(pua[key]["unicode"][2:], 16)
            core.append((ev, ch, d))
        else:
            other.append((ev, d))
    return core, other, skipped


def path_el(ev, d):
    return (f'<path transform="translate({ev["x"]:.4f},{ev["y"]:.4f}) '
            f'scale({ev["sx"]/1000:.6f},{ev["sy"]/1000:.6f})" d="{d}"/>')


def text_el(ev, ch):
    return (f'<text transform="translate({ev["x"]:.4f},{ev["y"]:.4f}) '
            f'scale({ev["sx"]/1000:.6f},{-ev["sy"]/1000:.6f})">&#x{ch:X};</text>')


def page_group(core, other, use_font):
    parts = [path_el(ev, d) for ev, d in other]
    if use_font:
        parts += [text_el(ev, ch) for ev, ch, d in core]
    else:
        parts += [path_el(ev, d) for ev, ch, d in core]
    return "\n".join(parts)


def raster_html(group, font_file):
    face = ""
    if font_file:
        face = (f"@font-face{{font-family:'{FONT_FAMILY}';src:url('{font_file}');}}")
    return f"""<!doctype html><meta charset="utf-8"><style>
{face}
html,body{{margin:0;background:#fff}}
svg{{display:block}}
text{{font-family:'{FONT_FAMILY}';font-size:1000px;font-kerning:none;
 font-feature-settings:normal;text-rendering:geometricPrecision;white-space:pre}}
</style>
<svg xmlns="http://www.w3.org/2000/svg" width="{PX_W}" height="{PX_H}" viewBox="0 0 {PAGE_W} {PAGE_H}">
<rect width="100%" height="100%" fill="#fff"/><g fill="#000">{group}</g></svg>"""


def shoot(pw_page, html_path, png_path, wait_font):
    pw_page.goto("file://" + html_path)
    if wait_font:
        ok = pw_page.evaluate(
            f"document.fonts.load(\"1000px '{FONT_FAMILY}'\").then(()=>document.fonts.check(\"1000px '{FONT_FAMILY}'\"))")
        if not ok:
            raise RuntimeError("font failed to load in Chromium")
    pw_page.evaluate("document.fonts.ready")
    pw_page.screenshot(path=png_path, clip={"x": 0, "y": 0, "width": PX_W, "height": PX_H})


def gray(path):
    return np.asarray(Image.open(path).convert("L"), dtype=np.int16)


def _dilate(m, r=1):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def compare(a, b, diff_png=None):
    d = np.abs(a - b)
    A, B = a < 128, b < 128
    tol1 = int((A & ~_dilate(B)).sum() + (B & ~_dilate(A)).sum())
    ink = (a < 128) | (b < 128)
    bin_mismatch = int(((a < 128) != (b < 128)).sum())
    res = {
        "ink_pixels": int(ink.sum()),
        "pixels_diff_gt0": int((d > 0).sum()),
        "pixels_diff_gt32": int((d > 32).sum()),
        "pixels_diff_gt128": int((d > 128).sum()),
        "binary_mismatch_pixels": bin_mismatch,
        "binary_mismatch_pct_of_ink": round(100 * bin_mismatch / max(1, int(ink.sum())), 4),
        "max_diff": int(d.max()),
        "structural_mismatch_px_tol1": tol1,
        "structural_mismatch_pct_tol1": round(100 * tol1 / max(1, int((A | B).sum())), 4),
    }
    if diff_png:
        img = np.full(a.shape + (3,), 255, dtype=np.uint8)
        img[(a < 128) & (b < 128)] = (190, 190, 190)       # agree
        img[(a < 128) & (b >= 128)] = (220, 40, 40)         # only reference
        img[(a >= 128) & (b < 128)] = (30, 90, 220)         # only font
        Image.fromarray(img).save(diff_png)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stream", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--eps-png")
    ap.add_argument("--orig-png", help="render of the ORIGINAL 973-page PDF page (same A4 aspect) used for side-by-side")
    ap.add_argument("--lines", help="(unused) kept for compatibility")
    args = ap.parse_args()

    stream, master, pua = load(args)
    core, other, skipped = build_events(stream, master, pua)
    out = os.path.join(DIST, "verify", args.tag)
    os.makedirs(out, exist_ok=True)

    h1 = os.path.join(out, "r1_paths.html")
    h2 = os.path.join(out, "r2_ttf.html")
    h3 = os.path.join(out, "r3_otf.html")
    open(h1, "w", encoding="utf-8").write(raster_html(page_group(core, other, False), None))
    open(h2, "w", encoding="utf-8").write(raster_html(page_group(core, other, True), "../../KarianaQuranRecoverFont.ttf"))
    open(h3, "w", encoding="utf-8").write(raster_html(page_group(core, other, True), "../../KarianaQuranRecoverFont.otf"))

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": PX_W, "height": PX_H}, device_scale_factor=1)
        shoot(pg, h1, os.path.join(out, "r1_paths.png"), False)
        shoot(pg, h2, os.path.join(out, "r2_ttf.png"), True)
        shoot(pg, h3, os.path.join(out, "r3_otf.png"), True)
        b.close()

    r1, r2, r3 = (gray(os.path.join(out, n)) for n in ("r1_paths.png", "r2_ttf.png", "r3_otf.png"))
    report = {
        "stream": os.path.relpath(args.stream, ROOT),
        "events_total": len(stream),
        "events_core_font_text": len(core),
        "events_other_vector": len(other),
        "events_skipped_empty_or_zero_scale": skipped,
        "ttf_vs_vectors": compare(r1, r2, os.path.join(out, "diff_ttf.png")),
        "otf_vs_vectors": compare(r1, r3, os.path.join(out, "diff_otf.png")),
    }
    if args.eps_png:
        ref = gray(args.eps_png)
        if ref.shape == r1.shape:
            report["vectors_vs_real_eps_render"] = compare(ref, r1, os.path.join(out, "diff_vectors_vs_eps.png"))
            report["ttf_vs_real_eps_render"] = compare(ref, r2, os.path.join(out, "diff_ttf_vs_eps.png"))
        else:
            report["note"] = f"eps-png size {ref.shape} differs from {r1.shape}; skipped"
    json.dump(report, open(os.path.join(out, "report.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(report, indent=1))

    lines = json.load(open(args.lines, encoding="utf-8")) if args.lines else None
    write_html(args, core, other, report, lines)


def baselines(core):
    ys = sorted({round(ev["y"], 2) for ev, ch, d in core if ev["base_font"] == "AnicaKariSAKQPlain"})
    return ys


def write_html(args, core, other, report, lines):
    ttf_b64 = base64.b64encode(open(os.path.join(DIST, "KarianaQuranRecoverFont.ttf"), "rb").read()).decode()
    group = page_group(core, other, True)
    ys = baselines(core)
    import io
    eps_png = os.path.relpath(args.eps_png, DIST) if args.eps_png else None
    t, o = report["ttf_vs_vectors"], report["otf_vs_vectors"]
    ev_eps = report.get("ttf_vs_real_eps_render")
    orig = Image.open(args.orig_png).convert("RGB") if args.orig_png else None

    def data_uri(img, fmt="PNG"):
        buf = io.BytesIO()
        img.save(buf, fmt, **({"quality": 92} if fmt == "JPEG" else {}))
        return f"data:image/{fmt.lower()};base64," + base64.b64encode(buf.getvalue()).decode()

    arabic_only = "\n".join(text_el(ev, ch) for ev, ch, d in core)   # font glyphs only: letters, harakat, tajweed, waqf
    rows = []
    for i, y in enumerate(ys, 1):
        y0, h = y - 47, 70
        crop = ""
        if orig:
            k = orig.width / PAGE_W
            c = orig.crop((0, int(y0 * k), orig.width, int((y0 + h) * k)))
            crop = f'<div class="lbl">মূল ৯৭৩ পৃষ্ঠার PDF থেকে (ক্রপ)</div><img class="crop" src="{data_uri(c)}" alt="original line {i}">'
        rows.append(f'''<section class="line"><h3>লাইন {i} <small>baseline Y = {y:.2f}</small></h3>
<div class="lbl">নতুন ফন্ট — শুধু ফন্টের গ্লিফ (হরফ + হরকত + উপরের তাজবীদ চিহ্ন + ওয়াকফ)</div>
<svg viewBox="0 {y0:.2f} {PAGE_W} {h}"><g fill="#000">{arabic_only}</g></svg>
{crop}</section>''')
    metrics = f"""
<table><tr><th></th><th>ইঙ্ক পিক্সেল</th><th>পার্থক্য &gt;32</th><th>পার্থক্য &gt;128</th><th>বাইনারি মিসম্যাচ (০ px সহনশীলতা)</th><th>কাঠামোগত মিসম্যাচ (১ px সহনশীলতা)</th></tr>
<tr><td>TTF বনাম মূল ভেক্টর</td><td>{t['ink_pixels']:,}</td><td>{t['pixels_diff_gt32']:,}</td><td>{t['pixels_diff_gt128']:,}</td><td>{t['binary_mismatch_pixels']:,} ({t['binary_mismatch_pct_of_ink']}%)</td><td>{t['structural_mismatch_px_tol1']:,} ({t['structural_mismatch_pct_tol1']}%)</td></tr>
<tr><td>OTF বনাম মূল ভেক্টর</td><td>{o['ink_pixels']:,}</td><td>{o['pixels_diff_gt32']:,}</td><td>{o['pixels_diff_gt128']:,}</td><td>{o['binary_mismatch_pixels']:,} ({o['binary_mismatch_pct_of_ink']}%)</td><td>{o['structural_mismatch_px_tol1']:,} ({o['structural_mismatch_pct_tol1']}%)</td></tr>"""
    if ev_eps:
        metrics += (f"<tr><td>TTF বনাম আসল EPS রেন্ডার (PNG)</td><td>{ev_eps['ink_pixels']:,}</td>"
                    f"<td>{ev_eps['pixels_diff_gt32']:,}</td><td>{ev_eps['pixels_diff_gt128']:,}</td>"
                    f"<td>{ev_eps['binary_mismatch_pixels']:,} ({ev_eps['binary_mismatch_pct_of_ink']}%)</td>"
                    f"<td>{ev_eps['structural_mismatch_px_tol1']:,} ({ev_eps['structural_mismatch_pct_tol1']}%)</td></tr>")
    metrics += "</table>"
    slider = ""
    if orig:
        small = orig.resize((1241, int(1241 * PAGE_H / PAGE_W)))
        slider = (f'<div class="cmp" id="cmp"><svg viewBox="0 0 {PAGE_W} {PAGE_H}"><use href="#page"/></svg>'
                  f'<div class="clip" id="clip"><img src="{data_uri(small, "JPEG")}" alt="original"></div>'
                  '<input id="rng" type="range" min="0" max="100" value="50"></div>')
    html = f"""<!doctype html><html lang="bn"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ক্বারীয়ানা কুরআন রিকভার ফন্ট — {args.tag} যাচাই</title>
<style>
@font-face{{font-family:'{FONT_FAMILY}';src:url(data:font/ttf;base64,{ttf_b64}) format('truetype');}}
:root{{--bg:#fafaf7;--fg:#1d1d1b;--mut:#6b6b66;--card:#fff;--bd:#dcdcd4}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--fg:#ecece6;--mut:#9c9c94;--card:#1f1f1c;--bd:#3a3a35}}}}
body{{margin:0;padding:24px;background:var(--bg);color:var(--fg);font:16px/1.6 'Kalpurush','Noto Sans Bengali',system-ui,sans-serif}}
main{{max-width:980px;margin:auto}} h1{{font-size:24px;margin:0 0 4px}} .sub{{color:var(--mut);margin:0 0 20px}}
section,.box{{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:14px 16px;margin:14px 0}}
table{{border-collapse:collapse;width:100%;font-size:14px;display:block;overflow-x:auto}}
th,td{{border-bottom:1px solid var(--bd);padding:6px 10px;text-align:left;white-space:nowrap}}
svg{{width:100%;height:auto;display:block;background:#fff;border-radius:6px}}
text{{font-family:'{FONT_FAMILY}';font-size:1000px;font-kerning:none;text-rendering:geometricPrecision;white-space:pre}}
.lbl{{font-size:12px;color:var(--mut);margin:8px 0 3px}} h3{{margin:0;font-size:16px}} h3 small{{color:var(--mut);font-weight:400}}
.crop{{width:100%;height:auto;display:block;border-radius:6px}}
.ref{{font:26px/1.6 'Scheherazade New','Noto Naskh Arabic','Traditional Arabic',serif;margin-top:6px;color:var(--mut)}}
.cmp{{position:relative;max-width:620px;margin:auto}} .cmp img{{display:block;width:100%}}
.clip{{position:absolute;inset:0;overflow:hidden;width:50%}} .clip img{{width:620px;max-width:none}}
.cmp input{{position:absolute;left:0;right:0;bottom:-28px;width:100%}} .note{{color:var(--mut);font-size:14px}}
</style>
<main>
<h1>ক্বারীয়ানা কুরআন রিকভার ফন্ট — {args.tag} যাচাই</h1>
<p class="sub">ফন্ট: {FONT_FAMILY} · PS: KarianaQuranRecover-Regular · কোর গ্লিফ ইভেন্ট {len(core)}টি ফন্ট-টেক্সট হিসেবে, অন্য {len(other)}টি (বাংলা অনুবাদ ইত্যাদি) মূল ভেক্টর হিসেবে আঁকা</p>
<div class="box"><b>পিক্সেল ডিফ রিপোর্ট</b> (২৪৮০×৩৫০৯ px, ৩০০ dpi)
{metrics}
<p class="note">‘মূল ভেক্টর’ = ডিক্রিপ্ট করা আসল আউটলাইন সরাসরি আঁকা। ‘ফন্ট’ = একই ইভেন্ট নতুন ফন্টের টেক্সট হিসেবে আঁকা। ০ px সহনশীলতায় মিসম্যাচ আসে শুধু অ্যান্টি-অ্যালিয়াসিংয়ের কিনারা থেকে; ১ px সহনশীলতায় যা থাকে সেটাই প্রকৃত আকৃতির পার্থক্য। আসল EPS PNG-তে ডিকোডারের আঁকা গাইড-ব্যান্ডও আছে।</p></div>
{('<div class="box"><b>ওভারলে স্লাইডার</b> — বামে মূল PDF পৃষ্ঠা, ডানে নতুন ফন্ট (স্লাইডার টানুন)<br><br>' + slider + '<br><br></div>') if slider else ''}
{''.join(rows)}
<svg width="0" height="0" style="position:absolute"><defs><g id="page" fill="#000">{group}</g></defs></svg>
</main>
<script>
const r=document.getElementById('rng');
if(r)r.addEventListener('input',()=>{{document.getElementById('clip').style.width=r.value+'%';}});
</script></html>"""
    out_html = os.path.join(DIST, f"kuran_{args.tag}_recover_font_verification.html")
    open(out_html, "w", encoding="utf-8").write(html)
    print("wrote", out_html)


if __name__ == "__main__":
    sys.exit(main())
