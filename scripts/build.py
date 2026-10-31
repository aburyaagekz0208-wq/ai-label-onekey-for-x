"""配布用の zip（Chrome ウェブストアにそのまま上げられる形）を dist/ に作る。

拡張に必要なファイルだけを入れる（store/・scripts/・README などは入れない）。
zip の中のパスは / 区切りにする（PowerShell 5.1 の Compress-Archive は \ になり、ストアで弾かれることがある）。

使い方: python scripts/build.py
"""

import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [
    "manifest.json",
    "background.js",
    "hotkey.js",
    "content.js",
    "options.html",
    "options.css",
    "options.js",
    "icons/icon16.png",
    "icons/icon32.png",
    "icons/icon48.png",
    "icons/icon128.png",
]


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    missing = [f for f in FILES if not (ROOT / f).is_file()]
    if missing:
        raise SystemExit("見つからないファイル: " + ", ".join(missing))

    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    out = dist / f"ai-label-onekey-{version}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in FILES:
            z.write(ROOT / f, f)
    print(f"作成: {out}（{out.stat().st_size:,} バイト・{len(FILES)} ファイル）")


if __name__ == "__main__":
    main()
