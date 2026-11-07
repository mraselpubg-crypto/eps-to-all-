import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

for u in ['https://github.com/mraselpubg-crypto/eps-to-all', 'https://github.com/mraselpubg-crypto/eps-to-all-']:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=5)
        print(f"URL: {u} -> Status: {res.status}")
    except Exception as e:
        print(f"URL: {u} -> Error: {e}")

# Check user public repos
try:
    req = urllib.request.Request('https://api.github.com/users/mraselpubg-crypto/repos', headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req, timeout=5)
    repos = json.loads(res.read().decode('utf-8'))
    print("User public repos:", [r['name'] for r in repos])
except Exception as e:
    print("User repos check error:", e)
