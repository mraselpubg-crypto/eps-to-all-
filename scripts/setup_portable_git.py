import os
import sys
import urllib.request
import zipfile

sys.stdout.reconfigure(encoding="utf-8")

DEST_DIR = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\tools\git"
ZIP_PATH = r"c:\Users\Rasel Gazi\Downloads\Kariana Old Version Recover\tools\mingit.zip"
os.makedirs(os.path.dirname(ZIP_PATH), exist_ok=True)

# MinGit 64-bit release URL
URL = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/MinGit-2.44.0-64-bit.zip"

print(f"Downloading MinGit from {URL} ...")
headers = {"User-Agent": "Mozilla/5.0"}
req = urllib.request.Request(URL, headers=headers)

try:
    with urllib.request.urlopen(req, timeout=30) as res:
        data = res.read()
        with open(ZIP_PATH, "wb") as f:
            f.write(data)
    print(f"Downloaded MinGit zip ({len(data):,} bytes). Extracting...")
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
        zf.extractall(DEST_DIR)
        
    git_exe = os.path.join(DEST_DIR, "cmd", "git.exe")
    print(f"Extraction complete! Git executable: {git_exe} (Exists: {os.path.exists(git_exe)})")
except Exception as e:
    print(f"Failed to download/setup MinGit: {e}")
