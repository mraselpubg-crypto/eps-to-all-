import os
import re
import sys
import json
import struct
from collections import defaultdict
from fontTools.misc.psCharStrings import T1CharString
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

sys.stdout.reconfigure(encoding="utf-8")

EPS_PATH = r"C:\xampp\htdocs\Bipul code craft Api\KariSAKQ_Para-01_21.eps"
OUT_DIR = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\extracted_data\eps_page21"
os.makedirs(OUT_DIR, exist_ok=True)


def decrypt_t1_bytes(cipher: bytes, lenIV: int = 0, R: int = 4330) -> bytes:
    c1 = 52845
    c2 = 22719
    plain = bytearray()
    for b in cipher:
        p = b ^ (R >> 8)
        R = ((b + R) * c1 + c2) & 0xFFFF
        plain.append(p)
    return bytes(plain[lenIV:])


def decrypt_eexec(cipher: bytes, R: int = 55665) -> bytes:
    c1 = 52845
    c2 = 22719
    plain = bytearray()
    for b in cipher:
        p = b ^ (R >> 8)
        R = ((b + R) * c1 + c2) & 0xFFFF
        plain.append(p)
    return bytes(plain[4:])


class SubrFontWrapper:
    """Minimal Private/Subrs holder for fontTools T1CharString bytecode execution."""
    def __init__(self, subrs_raw, lenIV=0):
        self.Subrs = [T1CharString(decrypt_t1_bytes(s, lenIV=lenIV), subrs=None) if s is not None else T1CharString(b"\x0b") for s in subrs_raw]
        for cs in self.Subrs:
            cs.private = self


def parse_ps_encoding_array(arr_str: str) -> list:
    """Parse PostScript encoding array like: 32{/.notdef}repeat /N /Uacute 202{/.notdef}repeat"""
    enc = []
    tokens = re.findall(r"(\d+)\s*\{\s*/([^\s\}]+)\s*\}\s*repeat|/([^\s/\[\]\{\}]+)", arr_str)
    for count_s, rep_glyph, single_glyph in tokens:
        if count_s:
            enc.extend([rep_glyph] * int(count_s))
        elif single_glyph:
            enc.append(single_glyph)
    if len(enc) < 256:
        enc.extend([".notdef"] * (256 - len(enc)))
    return enc[:256]


def unescape_ps_string(ps_lit: bytes) -> bytes:
    """Decode PostScript (...) literal bytes with octal and backslash escapes."""
    out = bytearray()
    i = 0
    n = len(ps_lit)
    while i < n:
        b = ps_lit[i]
        if b == 0x5C:  # backslash
            i += 1
            if i >= n:
                break
            nxt = ps_lit[i]
            if 0x30 <= nxt <= 0x37:  # octal \ddd
                oct_digits = bytes([nxt])
                for _ in range(2):
                    if i + 1 < n and 0x30 <= ps_lit[i + 1] <= 0x37:
                        i += 1
                        oct_digits += bytes([ps_lit[i]])
                    else:
                        break
                out.append(int(oct_digits, 8) & 0xFF)
            elif nxt == ord("n"):
                out.append(10)
            elif nxt == ord("r"):
                out.append(13)
            elif nxt == ord("t"):
                out.append(9)
            elif nxt == ord("b"):
                out.append(8)
            elif nxt == ord("f"):
                out.append(12)
            elif nxt in (ord("("), ord(")"), ord("\\")):
                out.append(nxt)
            elif nxt == 13:  # line continuation \CR or \CRLF
                if i + 1 < n and ps_lit[i + 1] == 10:
                    i += 1
            elif nxt == 10:
                pass
            else:
                out.append(nxt)
        else:
            out.append(b)
        i += 1
    return bytes(out)


def main():
    with open(EPS_PATH, "rb") as f:
        data = f.read()

    magic = data[:4]
    assert magic == b"\xc5\xd0\xd3\xc6", f"Unexpected EPS magic: {magic}"
    ps_offset, ps_len, wmf_off, wmf_len, tiff_off, tiff_len = struct.unpack("<6I", data[4:28])
    print(f"EPS Binary Header -> PS: offset={ps_offset}, len={ps_len} | TIFF: offset={tiff_off}, len={tiff_len}")

    if tiff_len > 0:
        tiff_path = os.path.join(OUT_DIR, "KariSAKQ_Para-01_21_preview.tiff")
        with open(tiff_path, "wb") as tf:
            tf.write(data[tiff_off : tiff_off + tiff_len])
        print(f"Saved embedded TIFF preview: {tiff_path}")

    ps_bytes = data[ps_offset : ps_offset + ps_len]

    # 1. Extract all %ADOBeginSubsetFont ... %ADOEndSubsetFont blocks in byte space!
    fonts_raw = {}  # font_name -> {"bbox": [], "lenIV": 0, "subrs": {}, "charstrings": {}}
    subset_pat = re.compile(b"%ADOBeginSubsetFont:[ \\t]*([^\\r\\n]+)[\\r\\n]+(.*?)%ADOEndSubsetFont", re.S)

    for m in subset_pat.finditer(ps_bytes):
        header = m.group(1).decode("latin1").strip()
        blk = m.group(2)
        parts = header.split()
        fname = parts[0]
        mode = parts[1] if len(parts) > 1 else "Initial"

        if fname not in fonts_raw:
            fonts_raw[fname] = {"bbox": None, "lenIV": 0, "subrs": {}, "charstrings": {}}

        if mode == "Initial":
            m_bbox = re.search(b"/FontBBox\\s*\\{\\s*([^\\}]+)\\s*\\}", blk)
            if m_bbox:
                fonts_raw[fname]["bbox"] = [float(x) for x in m_bbox.group(1).split()]
            m_leniv = re.search(b"/lenIV\\s+(\\d+)\\s+def", blk)
            if m_leniv:
                fonts_raw[fname]["lenIV"] = int(m_leniv.group(1))

        # Extract any Subrs: dup <idx> <len> -| <bytes> | (or NP)
        pos = 0
        subr_hdr = re.compile(b"dup\\s+(\\d+)\\s+(\\d+)\\s+(?:-\\||RD)\\s")
        while True:
            ms = subr_hdr.search(blk, pos)
            if not ms:
                break
            s_idx = int(ms.group(1))
            s_len = int(ms.group(2))
            start_b = ms.end()
            fonts_raw[fname]["subrs"][s_idx] = blk[start_b : start_b + s_len]
            pos = start_b + s_len

        # Extract all CharStrings: /<gname> <len> -| <bytes> |- (or ND)
        pos = 0
        cs_hdr = re.compile(b"/([A-Za-z0-9_\\.\\-]+)\\s+(\\d+)\\s+(?:-\\||RD)\\s")
        while True:
            mc = cs_hdr.search(blk, pos)
            if not mc:
                break
            gname = mc.group(1).decode("latin1")
            c_len = int(mc.group(2))
            start_b = mc.end()
            fonts_raw[fname]["charstrings"][gname] = blk[start_b : start_b + c_len]
            pos = start_b + c_len

    # Decompile all extracted Type 1 fonts into SVG paths & widths
    decoded_fonts = {}
    total_glyphs = 0
    for fname, finfo in sorted(fonts_raw.items()):
        max_subr = max(finfo["subrs"].keys(), default=-1)
        subrs_list = [finfo["subrs"].get(i) for i in range(max_subr + 1)]
        priv = SubrFontWrapper(subrs_list, lenIV=finfo["lenIV"])

        glyph_dict = {}
        # Build charstring objects first so seac (if any) or bounds/svg pen can resolve
        cs_objs = {}
        for gname, raw_b in finfo["charstrings"].items():
            dec = decrypt_t1_bytes(raw_b, lenIV=finfo["lenIV"])
            cs = T1CharString(dec, subrs=priv.Subrs)
            cs.private = priv
            cs_objs[gname] = cs

        for gname, cs in cs_objs.items():
            pen = SVGPathPen(cs_objs)
            cs.draw(pen)
            bpen = BoundsPen(cs_objs)
            cs.draw(bpen)
            glyph_dict[gname] = {
                "width": cs.width,
                "bounds": list(bpen.bounds) if bpen.bounds else None,
                "svg_path": pen.getCommands(),
            }
            total_glyphs += 1

        decoded_fonts[fname] = {
            "bbox": finfo["bbox"],
            "lenIV": finfo["lenIV"],
            "subrs_count": len(subrs_list),
            "glyph_count": len(glyph_dict),
            "glyphs": glyph_dict,
        }
        print(
            f"  Decoded EPS Font: {fname:28s} | BBox={str(finfo['bbox']):26s} | "
            f"Subrs={len(subrs_list):2d} | Glyphs={len(glyph_dict):3d}"
        )

    print(f"\nTotal decrypted Type 1 glyphs from EPS: {total_glyphs}")

    # 2. Parse Page Stream (strip binary font subsets & embedded border doc first so byte offsets / lines are clean)
    clean_ps = subset_pat.sub(b"\n% [SUBSET_REMOVED]\n", ps_bytes)
    clean_ps = re.sub(b"%%BeginDocument:.*?%%EndDocument", b"\n% [EMBEDDED_DOC_REMOVED]\n", clean_ps, flags=re.S)
    ps_str = clean_ps.decode("latin1")

    # Parse all nfnt sub-encodings in order, plus stream commands!
    # Notice nfnt definitions appear inline right before they are used!
    # Let's parse sequentially through the stream after %%EndPageSetup
    start_idx = ps_str.find("%%EndPageSetup")
    stream_str = ps_str[start_idx:]

    sub_encodings = {}  # subfont_name -> {"base": base_name, "enc": [256 glyph names]}
    # Pre-scan all nfnt blocks (each subfont name like AnicaKariSAKQPlain*2 is unique!)
    nfnt_pat = re.compile(r"/([A-Za-z0-9_\-\*]+)\s*\[(.*?)\]\s*/([A-Za-z0-9_\-]+)\s+nfnt", re.S)
    for mn in nfnt_pat.finditer(stream_str):
        sub_name, arr_body, base_name = mn.group(1), mn.group(2), mn.group(3)
        sub_encodings[sub_name] = {
            "base": base_name,
            "enc": parse_ps_encoding_array(arr_body),
        }
    print(f"Parsed {len(sub_encodings)} nfnt sub-encoding tables.")

    # Now scan line-by-line for font changes, color changes, mov, and (...) sh!
    cur_subfont = None
    cur_matrix = [1, 0, 0, 1, 0, 0]
    cur_x, cur_y = 0.0, 0.0
    cur_cmyk = [0, 0, 0, 1]

    re_font = re.compile(r"/([A-Za-z0-9_\-\*]+)\s+findfont\s+\[\s*([^\]]+)\]\s+mfnt\s+sfnt")
    re_mov = re.compile(r"([\-0-9\.]+)\s+([\-0-9\.]+)\s+mov\b")
    re_cmyk = re.compile(r"([\-0-9\.]+)\s+([\-0-9\.]+)\s+([\-0-9\.]+)\s+([\-0-9\.]+)\s+cmyk\b")
    re_sh = re.compile(r"^\((.*)\)\s+sh$")

    events = []
    for raw_line in stream_str.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        mf = re_font.search(line)
        if mf:
            cur_subfont = mf.group(1)
            cur_matrix = [float(x) for x in mf.group(2).split()]
            continue
        mc = re_cmyk.search(line)
        if mc:
            cur_cmyk = [float(mc.group(i)) for i in range(1, 5)]
            continue
        mm = re_mov.match(line)
        if mm:
            cur_x = float(mm.group(1))
            cur_y = float(mm.group(2))
            continue
        ms = re_sh.match(line)
        if ms and cur_subfont in sub_encodings:
            lit_bytes = ms.group(1).encode("latin1")
            char_codes = unescape_ps_string(lit_bytes)
            sub_info = sub_encodings[cur_subfont]
            base_font = sub_info["base"]
            enc_table = sub_info["enc"]
            sx, b_m, c_m, sy, tx_m, ty_m = cur_matrix
            cx = cur_x
            for code in char_codes:
                gname = enc_table[code]
                gdata = decoded_fonts.get(base_font, {}).get("glyphs", {}).get(gname)
                adv = gdata["width"] if gdata else 0
                events.append({
                    "x": round(cx, 4),
                    "y": round(cur_y, 4),
                    "sx": round(sx, 4),
                    "sy": round(sy, 4),
                    "base_font": base_font,
                    "sub_font": cur_subfont,
                    "code": code,
                    "glyph": gname,
                    "width": adv,
                    "cmyk": cur_cmyk,
                })
                cx += (adv / 1000.0) * sx

    print(f"Extracted {len(events)} positioned glyph events from Page 21 stream!")

    # Group Arabic Y baselines to inspect the 9-line structure!
    arabic_ys = defaultdict(int)
    bangla_ys = defaultdict(int)
    for ev in events:
        if ev["base_font"].startswith("AnicaKariSAKQ"):
            arabic_ys[round(ev["y"], 2)] += 1
        elif "Bangali" in ev["base_font"]:
            bangla_ys[round(ev["y"], 2)] += 1

    print("\nArabic Baselines (Y -> glyph count):", dict(sorted(arabic_ys.items())))
    print("Bangla Baselines (Y -> glyph count):", dict(sorted(bangla_ys.items())))

    # Save JSON data
    with open(os.path.join(OUT_DIR, "eps_page21_fonts.json"), "w", encoding="utf-8") as fp:
        json.dump(decoded_fonts, fp, indent=2, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, "eps_page21_stream.json"), "w", encoding="utf-8") as fp:
        json.dump(events, fp, indent=2, ensure_ascii=False)

    # Render standalone verification SVG of Page 21 from extracted glyphs!
    svg_lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 595.28 841.89" width="1190" height="1684" style="background:#fffdf6">',
        '<defs>',
    ]
    for fname, finfo in decoded_fonts.items():
        for gname, gdata in finfo["glyphs"].items():
            if gdata["svg_path"]:
                gid = f"{fname}__{gname}".replace(".", "_")
                svg_lines.append(f'  <path id="{gid}" d="{gdata["svg_path"]}" />')
    svg_lines.append("</defs>")

    # Draw guide bands for the 9 Arabic baselines + top symbol box
    for y_val in sorted(arabic_ys.keys()):
        if arabic_ys[y_val] > 5:
            # Top symbol band (Y_font 1061..1422 at sy=-26.5 => y_page - 26.5*1.422 .. y_page - 26.5*1.061)
            top_y1 = y_val - 26.5 * 1.422
            top_y2 = y_val - 26.5 * 1.061
            svg_lines.append(
                f'<rect x="88" y="{top_y1:.2f}" width="420" height="{top_y2 - top_y1:.2f}" '
                f'fill="#eef7ee" stroke="#bddbbd" stroke-width="0.4" />'
            )
            svg_lines.append(
                f'<line x1="88" y1="{y_val:.2f}" x2="508" y2="{y_val:.2f}" stroke="#e5d5b5" stroke-width="0.4" />'
            )

    # Color-code layers slightly or render authentic black (let's make two SVGs: authentic black & color-coded layers!)
    layer_colors = {
        "AnicaKariSAKQPlain": "#111111",
        "AnicaKariSAKQPlainExtra": "#111111",
        "AnicaKariSAKQPlainSpare": "#111111",
        "AnicaKariSAKQHarkat": "#0b5394",
        "AnicaKariSAKQHarkatSpare": "#0b5394",
        "AnicaKariSAKQS1": "#b45f06",
        "AnicaKariSAKQS2": "#cc0000",
        "AnicaKariSAKQS3": "#674ea7",
        "AnicaKariSAKQA1": "#38761d",
        "AnicaKariSAKQA4": "#38761d",
        "AnicaKariSAKQAW": "#741b47",
        "AnicaKariSAKQLW": "#a61c00",
    }

    svg_auth = list(svg_lines)
    svg_layered = list(svg_lines)

    for ev in events:
        gid = f"{ev['base_font']}__{ev['glyph']}".replace(".", "_")
        gdata = decoded_fonts.get(ev["base_font"], {}).get("glyphs", {}).get(ev["glyph"])
        if not gdata or not gdata["svg_path"]:
            continue
        # Font units are 1000 UPM, so matrix scale is sx/1000 and sy/1000 (note sy is negative, e.g. -26.5, which flips font Y up!)
        msx = ev["sx"] / 1000.0
        msy = ev["sy"] / 1000.0
        transform = f"translate({ev['x']:.4f},{ev['y']:.4f}) scale({msx:.6f},{msy:.6f})"
        svg_auth.append(f'<use href="#{gid}" transform="{transform}" fill="#000000" />')
        col = layer_colors.get(ev["base_font"], "#333333")
        svg_layered.append(f'<use href="#{gid}" transform="{transform}" fill="{col}" />')

    svg_auth.append("</svg>")
    svg_layered.append("</svg>")

    with open(os.path.join(OUT_DIR, "eps_page21_reconstructed_authentic.svg"), "w", encoding="utf-8") as fp:
        fp.write("\n".join(svg_auth))
    with open(os.path.join(OUT_DIR, "eps_page21_reconstructed_color_layers.svg"), "w", encoding="utf-8") as fp:
        fp.write("\n".join(svg_layered))

    print("Saved reconstructed SVGs (authentic & color-coded layers)!")


if __name__ == "__main__":
    main()
