import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

folder_ids = ["1grAqlzXclmbzUySdWV4Mz7jzASJ26bpb", "1w4jq4jB3oRsRLps3b8PjKI378FhdFQ9M"]

if os.path.exists(r"G:\.shortcut-targets-by-id"):
    print("All G:\\.shortcut-targets-by-id:", os.listdir(r"G:\.shortcut-targets-by-id"))
    for sub in os.listdir(r"G:\.shortcut-targets-by-id"):
        sp = os.path.join(r"G:\.shortcut-targets-by-id", sub)
        try:
            top = os.listdir(sp)
            print(f"  G shortcut {sub} -> {top[:10]} (total {len(top)})")
            for t in top[:5]:
                tp = os.path.join(sp, t)
                if os.path.isdir(tp):
                    sub_items = os.listdir(tp)
                    print(f"    subdir {t} -> total {len(sub_items)}: {sub_items[:15]} ... {sub_items[-5:]}")
        except Exception as e:
            print(f"  G shortcut {sub} err: {e}")

for fid in folder_ids[1:]:
    print(f"\n=== Checking Web Embedded Folder {fid} ===")
    url = f"https://drive.google.com/embeddedfolderview?id={fid}#list"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="replace")
    title_m = re.findall(r"<title>(.*?)</title>", html, re.S)
    print("Title:", [t.strip() for t in title_m])
    entries = re.findall(
        r'id="entry-([A-Za-z0-9_-]+)".*?class="flip-entry-title">([^<]+)</div>(.*?)(?=id="entry-|$)',
        html,
        re.S,
    )
    print(f"Found {len(entries)} entries:")
    for eid, ename, rest in entries[:80]:
        kind = "FOLDER" if "folder" in rest.lower() else "FILE  "
        print(f"  [{kind}] {eid} | {ename}")
