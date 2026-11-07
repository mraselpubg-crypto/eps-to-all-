import json

master = json.load(open('extracted_data/master_973_glyphs/master_973_all_glyphs.json', encoding='utf-8'))
data = json.load(open('extracted_data/eps_page21/eps_page21_stream.json', encoding='utf-8'))

l1 = [e for e in data if abs(e['y'] - 169.73) < 3.0 and e['base_font'].startswith('AnicaKariSAKQ')]
l1.sort(key=lambda x: -x['x'])

widths = {}
for fam, fd in master.items():
    for g, vd in fd.get('glyphs', {}).items():
        if g != '.notdef':
            v = next(iter(vd.values()))
            widths[f"{fam}_{g}"] = v['width']

print("First 20 glyphs of Line 1 with EPS positions and Font widths:")
for i in range(min(20, len(l1))):
    e = l1[i]
    k = f"{e['base_font']}_{e['glyph']}"
    w_font = widths.get(k, 0)
    w_pt = w_font * 26.5 / 1000.0
    dx = (e['x'] - l1[i+1]['x']) if i + 1 < len(l1) else 0.0
    print(f"[{i:2d}] x={e['x']:6.2f} pt | dx={dx:5.2f} pt | w_pt={w_pt:5.2f} pt | {e['base_font']:24} | {e['glyph']}")
