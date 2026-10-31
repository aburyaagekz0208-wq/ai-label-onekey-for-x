"""説明書のイラスト（docs/images/*.png）を作り直す。

SVG を組み立てて docs/images/src/ に書き出し、Chrome（headless）で PNG にする。
画面はどれも実物の写しではなく、わかりやすくした絵。

使い方: python scripts/make_illustrations.py
"""

import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "images" / "src"
OUT = ROOT / "docs" / "images"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

W, H = 1200, 675
FONT = "'BIZ UDPGothic','Yu Gothic UI','Meiryo',sans-serif"
MONO = "'Cascadia Mono','Consolas',monospace"

INK = "#1f1440"
SUB = "#5d5480"
ACCENT = "#7c4dff"
ACCENT_DARK = "#5b2fd6"
HL = "#ff4f7b"
BG = "#f4f0ff"
CARD = "#ffffff"
LINE = "#e3dcf5"
GRAY = "#eceaf2"
X_BLUE = "#1d9bf0"


# ---------- 部品 ----------

def t(x, y, s, size=20, color=INK, weight=400, anchor="start", family=FONT):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{escape(s)}</text>')


def rect(x, y, w, h, fill=CARD, r=12, stroke=None, sw=2, extra=""):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"{st} {extra}/>'


def hl(x, y, w, h, r=12):
    """注目してほしい場所を囲む枠。"""
    return (f'<rect x="{x - 6}" y="{y - 6}" width="{w + 12}" height="{h + 12}" rx="{r + 4}" '
            f'fill="none" stroke="{HL}" stroke-width="4"/>')


def arrow(x1, y1, x2, y2, bend=0, color=HL, width=5):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - bend
    return (f'<path d="M{x1},{y1} Q{mx},{my} {x2},{y2}" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" marker-end="url(#ah)"/>')


def keycap(x, y, label, w=None, size=26):
    w = w or max(64, int(len(label) * size * 0.62) + 32)
    h = size + 30
    return (rect(x, y + 6, w, h, fill="#c9bdf0", r=12)
            + rect(x, y, w, h, fill=CARD, r=12, stroke="#b9aaf0", sw=2)
            + t(x + w / 2, y + h / 2 + size * 0.36, label, size, INK, 700, "middle", MONO)), w


def keys(x, y, labels, size=26, gap=14):
    """Ctrl + Shift + Y のようなキーの並び。終わりの x を返す。"""
    out = []
    for i, lab in enumerate(labels):
        if i:
            out.append(t(x + gap, y + size + 6, "+", size, SUB, 700))
            x += gap * 2 + size * 0.6
        svg, w = keycap(x, y, lab, size=size)
        out.append(svg)
        x += w
    return "".join(out), x


def cursor(x, y, scale=1.0):
    return (f'<g transform="translate({x},{y}) scale({scale})">'
            '<path d="M0,0 L0,30 L8,23 L13,35 L19,32 L14,21 L24,21 Z" fill="#111" stroke="#fff" '
            'stroke-width="2" stroke-linejoin="round"/></g>')


def toggle(x, y, on=True):
    bg = ACCENT if on else "#c4c0d0"
    cx = x + 38 if on else x + 14
    return rect(x, y, 52, 28, fill=bg, r=14) + f'<circle cx="{cx}" cy="{y + 14}" r="10" fill="#fff"/>'


def sparkle(cx, cy, r, fill="#fff"):
    w = r * 0.28
    pts = [(cx, cy - r), (cx + w, cy - w), (cx + r, cy), (cx + w, cy + w),
           (cx, cy + r), (cx - w, cy + w), (cx - r, cy), (cx - w, cy - w)]
    return f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{fill}"/>'


def app_icon(x, y, s=40):
    return (rect(x, y, s, s, fill=ACCENT, r=s * 0.24)
            + sparkle(x + s * 0.46, y + s * 0.54, s * 0.32)
            + sparkle(x + s * 0.76, y + s * 0.26, s * 0.12))


def bubble(x, y, w, lines, size=19, color=INK):
    h = len(lines) * (size + 10) + 22
    out = [rect(x, y, w, h, fill="#fff8e1", r=14, stroke="#f2c94c", sw=2)]
    for i, line in enumerate(lines):
        out.append(t(x + 18, y + 20 + size + i * (size + 10), line, size, color))
    return "".join(out)


def browser(x, y, w, h, url, inner=""):
    return (f'<g filter="url(#sh)">{rect(x, y, w, h, fill=CARD, r=14)}</g>'
            + f'<path d="M{x},{y + 14} a14,14 0 0 1 14,-14 h{w - 28} a14,14 0 0 1 14,14 v34 h-{w} Z" fill="{GRAY}"/>'
            + "".join(f'<circle cx="{x + 22 + i * 18}" cy="{y + 24}" r="6" fill="{c}"/>'
                      for i, c in enumerate(["#ff6b6b", "#ffc94d", "#4cd27d"]))
            + rect(x + 86, y + 10, w - 110, 28, fill="#fff", r=14)
            + t(x + 104, y + 30, url, 16, SUB, 400, family=MONO)
            + f'<g transform="translate({x},{y + 48})">{inner}</g>')


def frame(step, title, sub, body):
    head = ""
    tx = 60
    if step:
        head = (f'<circle cx="82" cy="70" r="30" fill="{ACCENT}"/>'
                + t(82, 82, str(step), 32, "#fff", 700, "middle"))
        tx = 128
    head += t(tx, 80, title, 34, INK, 700)
    if sub:
        head += t(tx, 118, sub, 20, SUB)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <filter id="sh" x="-10%" y="-10%" width="120%" height="130%">
    <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#3b2a80" flood-opacity="0.16"/>
  </filter>
  <marker id="ah" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 Z" fill="{HL}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
{head}
{body}
{app_icon(W - 290, H - 44, 24)}{t(W - 258, H - 25, "AIラベル ワンキー for X", 16, "#9a90c0", 700)}
</svg>'''


def composer(x, y, w, text, chip=True):
    """X の投稿欄（わかりやすくした絵）。"""
    out = [rect(x, y, w, 250, fill="#fff", r=16, stroke=LINE),
           f'<circle cx="{x + 40}" cy="{y + 44}" r="22" fill="#d9d2f5"/>',
           t(x + 76, y + 52, text, 24, INK)]
    if chip:
        out.append(rect(x + 76, y + 92, 150, 34, fill="#f2edff", r=17))
        out.append(sparkle(x + 98, y + 109, 9, ACCENT))
        out.append(t(x + 116, y + 116, "AIで生成", 18, ACCENT_DARK, 700))
    ty = y + 196
    out.append(f'<line x1="{x + 20}" y1="{ty - 22}" x2="{x + w - 20}" y2="{ty - 22}" stroke="{LINE}" stroke-width="2"/>')
    for i in range(6):
        out.append(rect(x + 24 + i * 40, ty - 8, 24, 24, fill="#d6ecfb", r=6))
    out.append(f'<path d="M{x + 268},{ty - 8} v24 M{x + 268},{ty - 8} h14 l-3,6 l3,6 h-14" stroke="{X_BLUE}" stroke-width="3" fill="none"/>')
    out.append(rect(x + w - 150, ty - 14, 128, 38, fill=INK, r=19))
    out.append(t(x + w - 86, ty + 11, "ポストする", 17, "#fff", 700, "middle"))
    return "".join(out), (x + 76, y + 92, 150, 34), (x + 262, ty - 12, 28, 32)


def toast(cx, y, s):
    w = len(s) * 17 + 50
    return rect(cx - w / 2, y, w, 44, fill=ACCENT, r=22) + t(cx, y + 29, s, 19, "#fff", 700, "middle")


# ---------- 1 枚ずつ ----------

def img_hero():
    # 左：いままで
    left = [rect(50, 150, 470, 440, r=22, extra='filter="url(#sh)"'),
            t(80, 200, "いままで", 26, SUB, 700),
            t(80, 236, "毎回マウスで3回クリック", 20, SUB)]
    steps = ["旗マークを押す", "「AIで生成」をオン", "「完了」を押す"]
    for i, s in enumerate(steps):
        yy = 278 + i * 96
        left.append(rect(80, yy, 410, 72, fill=BG, r=14))
        left.append(f'<circle cx="118" cy="{yy + 36}" r="20" fill="#c4b5fd"/>')
        left.append(t(118, yy + 44, str(i + 1), 22, "#fff", 700, "middle"))
        left.append(t(156, yy + 45, s, 24, INK, 700))
        left.append(cursor(440, yy + 22, 0.9))
    # まんなかの矢印
    mid = (f'<path d="M548,370 h80" stroke="{ACCENT}" stroke-width="14" stroke-linecap="round"/>'
           f'<path d="M620,342 L662,370 L620,398 Z" fill="{ACCENT}"/>')
    # 右：これから
    right = [rect(690, 150, 460, 440, r=22, stroke=ACCENT, sw=4, extra='filter="url(#sh)"'),
             t(720, 200, "これから", 26, ACCENT_DARK, 700),
             t(720, 236, "キーを1回押すだけ", 20, SUB)]
    ks, _ = keys(724, 280, ["Ctrl", "Shift", "Y"], size=30)
    right.append(ks)
    right.append(f'<path d="M920,360 v40" stroke="{ACCENT}" stroke-width="6" stroke-linecap="round" marker-end="url(#ah)"/>')
    right.append(rect(800, 420, 210, 52, fill="#f2edff", r=26))
    right.append(sparkle(834, 446, 14, ACCENT))
    right.append(t(860, 456, "AIで生成", 26, ACCENT_DARK, 700))
    right.append(toast(920, 506, "AIラベル ON ✓"))
    body = "".join(left) + mid + "".join(right)
    return frame(None, "「AIで生成」ラベルをキー1つで付ける", "Xの投稿・返信で使えるChrome拡張（無料・投稿や送信はしません）", body)


def img_download():
    inner = (t(30, 52, "Releases", 30, INK, 700)
             + rect(30, 78, 88, 32, fill="#e6f4ea", r=16) + t(74, 100, "v1.0.0", 17, "#1a7f37", 700, "middle")
             + t(134, 101, "Latest", 17, SUB)
             + t(30, 160, "▼ Assets", 20, INK, 700)
             + rect(30, 178, 520, 54, fill="#f6f8fa", r=10, stroke="#d0d7de")
             + rect(48, 192, 22, 26, fill="#b6a3ff", r=4)
             + t(84, 213, "ai-label-onekey-1.0.0.zip", 20, X_BLUE, 700, family=MONO)
             + rect(30, 244, 520, 46, fill="#f6f8fa", r=10, stroke="#d0d7de")
             + t(84, 274, "Source code (zip)", 18, SUB, family=MONO))
    b = browser(50, 150, 600, 360, "github.com/…/releases", inner)
    b += hl(80, 376, 520, 54) + cursor(470, 395)
    # 右：解凍
    r = [rect(700, 150, 450, 360, r=18, extra='filter="url(#sh)"'),
         t(730, 196, "ダウンロードしたzipを", 22, INK, 700),
         t(730, 228, "右クリック→「すべて展開」", 22, INK, 700),
         rect(740, 262, 64, 76, fill="#b6a3ff", r=8), t(772, 312, "zip", 20, "#fff", 700, "middle"),
         rect(830, 256, 280, 128, fill="#fff", r=10, stroke=LINE),
         t(850, 290, "開く", 19, SUB),
         rect(842, 304, 256, 36, fill="#efe9ff", r=8), t(850, 330, "すべて展開...", 19, INK, 700),
         t(850, 368, "送る", 19, SUB),
         hl(842, 304, 256, 36, 8), cursor(1040, 318),
         f'<path d="M772,352 v40" stroke="{ACCENT}" stroke-width="5" marker-end="url(#ah)"/>',
         f'<path d="M740,410 h30 l10,12 h46 v56 h-86 Z" fill="#ffd166"/>',
         t(842, 452, "ai-label-onekey-1.0.0", 20, INK, 700),
         t(842, 480, "このフォルダを次で使います", 17, SUB)]
    body = b + "".join(r) + bubble(50, 530, 1100, ["「Source code」ではなく ai-label-onekey-○○.zip を選びます",
                                                  "解凍したフォルダは消さずに置いておきます（消すと拡張も動かなくなります）"], 19)
    return frame(1, "GitHubからzipをダウンロードして解凍", "Releasesページのいちばん新しい版を使います", body)


def ext_page_top(w):
    return (t(30, 52, "拡張機能", 28, INK, 700)
            + t(w - 300, 52, "デベロッパーモード", 20, INK, 700) + toggle(w - 100, 32, True))


def img_devmode():
    w = 1100
    inner = (ext_page_top(w)
             + f'<line x1="0" y1="80" x2="{w}" y2="80" stroke="{LINE}" stroke-width="2"/>'
             + "".join(rect(30 + i * 350, 110, 330, 150, fill="#faf9fd", r=12, stroke=LINE) for i in range(3))
             + t(46 + 0, 150, "（入っている拡張機能）", 18, "#a8a2bd"))
    b = browser(50, 150, w, 330, "chrome://extensions", inner)
    # 中身は (50, 198) からずれて置かれる
    b += hl(50 + w - 312, 198 + 22, 292, 48) + cursor(50 + w - 34, 198 + 44)
    body = b + bubble(50, 510, 760, ["Chromeのアドレス欄に chrome://extensions と入力してEnter",
                                     "右上の「デベロッパーモード」をオンにします"], 20)
    return frame(2, "拡張機能のページで「デベロッパーモード」をオン", "Chromeのプロフィールごとに1回だけ", body)


def img_load():
    w = 1100
    inner = (ext_page_top(w)
             + rect(30, 96, 400, 46, fill="#fff", r=8, stroke="#c9c2e0")
             + t(48, 126, "パッケージ化されていない拡張機能を読み込む", 17, ACCENT_DARK, 700)
             + rect(446, 96, 170, 46, fill="#fff", r=8, stroke="#c9c2e0") + t(466, 126, "拡張機能をパック", 17, SUB)
             + rect(632, 96, 90, 46, fill="#fff", r=8, stroke="#c9c2e0") + t(654, 126, "更新", 17, SUB)
             # 入ったあとのカード
             + rect(30, 180, 420, 170, fill="#faf9fd", r=14, stroke=ACCENT, sw=3)
             + app_icon(52, 204, 48)
             + t(116, 228, "AIラベル ワンキー for X", 20, INK, 700) + t(116, 256, "1.0.0", 16, SUB)
             + t(52, 300, "詳細　　削除", 17, ACCENT_DARK) + toggle(380, 298, True))
    b = browser(50, 150, w, 420, "chrome://extensions", inner)
    b += hl(80, 294, 400, 46, 8) + cursor(420, 316)
    # フォルダを選ぶ画面
    dlg = [f'<g filter="url(#sh)">{rect(600, 300, 520, 300, r=12)}</g>',
           t(624, 338, "フォルダーの選択", 20, INK, 700),
           rect(624, 356, 472, 150, fill="#fafafa", r=8, stroke=LINE),
           f'<path d="M640,374 h22 l7,8 h30 v34 h-59 Z" fill="#ffd166"/>',
           t(714, 402, "ai-label-onekey-1.0.0", 19, INK, 700),
           f'<path d="M640,440 h22 l7,8 h30 v34 h-59 Z" fill="#ffe7a3"/>', t(714, 468, "ダウンロード", 18, SUB),
           rect(624, 368, 472, 56, fill="none", r=8, stroke=X_BLUE, sw=2),
           rect(930, 530, 166, 42, fill=X_BLUE, r=8), t(1013, 557, "フォルダーの選択", 17, "#fff", 700, "middle"),
           hl(930, 530, 166, 42, 8), cursor(1050, 546),
           arrow(485, 340, 600, 380, 30)]
    return frame(3, "「読み込む」を押して解凍したフォルダを選ぶ", "カードが出てオンになっていれば入りました", b + "".join(dlg))


def img_ready():
    inner = (t(30, 60, "Xのタブ", 24, INK, 700)
             + rect(30, 90, 520, 160, fill="#f7f9f9", r=12, stroke=LINE)
             + t(56, 180, "（ホーム画面）", 20, "#a8a2bd"))
    b = browser(50, 150, 580, 320, "x.com/home", inner)
    # 再読み込みボタン
    b += (f'<circle cx="122" cy="174" r="0"/>')
    re = [rect(660, 150, 490, 320, r=18, extra='filter="url(#sh)"'),
          t(690, 200, "どちらかで再読み込み", 22, INK, 700),
          f'<circle cx="740" cy="270" r="40" fill="{BG}"/>',
          f'<path d="M760,250 a28,28 0 1 0 8,22" fill="none" stroke="{ACCENT_DARK}" stroke-width="6" stroke-linecap="round"/>'
          f'<path d="M752,236 L770,252 L748,258 Z" fill="{ACCENT_DARK}"/>',
          t(800, 278, "ボタンを押す", 20, INK)]
    ks, _ = keys(690, 340, ["F5"], size=28)
    re.append(ks)
    re.append(t(790, 374, "キーを押す", 20, INK))
    body = b + "".join(re) + bubble(50, 500, 1100, [
        "拡張を入れる前から開いていたXのタブは再読み込みするまで動きません",
        "Chromeのプロフィールを分けている人はXを使うプロフィールで手順2〜3をやってください"], 19)
    return frame(4, "開いているXのタブを再読み込み", "これで準備完了です", body)


def img_use():
    comp, chip_box, _ = composer(70, 170, 640, "新作のイラストです")
    body = [comp, hl(*chip_box, 17)]
    ks, _ = keys(790, 190, ["Ctrl", "Shift", "Y"], size=28)
    body.append(t(790, 176, "書き終わったら押す", 20, SUB, 700))
    body.append(ks)
    body.append(arrow(840, 270, 330, 290, -60))
    body.append(toast(390, 452, "AIラベル ON ✓"))
    body.append(bubble(760, 330, 390, [
        "旗マーク → AIで生成 → 完了",
        "を自動で進めます",
        "すでにONなら何もしません"], 19))
    body.append(rect(70, 520, 1080, 80, fill="#fff", r=16, stroke=LINE))
    k2, _ = keys(96, 534, ["Ctrl", "Enter"], size=22)
    body.append(k2)
    body.append(t(350, 568, "カーソルは文の最後に戻るのでそのまま送信できます（この拡張は送信しません）", 19, INK))
    return frame(5, "書いてキーを押すだけ", "投稿画面・返信画面・投稿ページの返信欄で使えます", "".join(body))


def img_settings():
    left = [rect(50, 150, 400, 400, r=18, extra='filter="url(#sh)"'),
            t(80, 196, "拡張アイコンを右クリック", 21, INK, 700),
            rect(80, 220, 340, 50, fill=GRAY, r=10), app_icon(370, 226, 38),
            rect(150, 286, 270, 210, fill="#fff", r=10, stroke=LINE)]
    for i, s in enumerate(["AIラベル ワンキー for X", "オプション", "拡張機能を削除", "ツールバーから固定解除"]):
        yy = 324 + i * 44
        if s == "オプション":
            left.append(rect(158, yy - 28, 254, 40, fill="#efe9ff", r=8))
        left.append(t(172, yy, s, 18, INK if s == "オプション" else SUB, 700 if s == "オプション" else 400))
    left.append(hl(158, 340, 254, 40, 8))
    left.append(cursor(380, 352))
    right = [rect(490, 150, 660, 400, r=18, extra='filter="url(#sh)"'),
             app_icon(520, 178, 40), t(574, 207, "AIラベル ワンキー for X", 22, INK, 700),
             t(520, 264, "ショートカットキー", 19, SUB, 700),
             rect(520, 280, 270, 48, fill=GRAY, r=10), t(655, 312, "Ctrl + Shift + Y", 20, INK, 700, "middle", MONO),
             rect(808, 284, 120, 40, fill=ACCENT, r=20), t(868, 310, "変更する", 18, "#fff", 700, "middle"),
             hl(808, 284, 120, 40, 20),
             f'<rect x="520" y="352" width="600" height="160" rx="14" fill="#faf8ff" stroke="{ACCENT}" stroke-width="3" stroke-dasharray="10 8"/>',
             t(820, 390, "使いたいキーの組み合わせを押してください", 18, SUB, 400, "middle")]
    ks, _ = keys(650, 414, ["Ctrl", "Alt", "L"], size=28)
    right.append(ks)
    body = "".join(left) + "".join(right) + t(50, 600, "CtrlかAltと組み合わせます（F1〜F12は単独でもOK）。Chromeが先に使うキーは選べません", 19, SUB)
    return frame(6, "キーは好きなものに変えられる", "変えたキーは開いているXのタブにもすぐ反映されます", body)


def mouse(cx, cy):
    return (f'<path d="M{cx - 90},{cy - 60} C{cx - 100},{cy - 170} {cx + 100},{cy - 170} {cx + 90},{cy - 60} '
            f'L{cx + 80},{cy + 110} C{cx + 70},{cy + 170} {cx - 70},{cy + 170} {cx - 80},{cy + 110} Z" fill="#fff" stroke="#b9aaf0" stroke-width="4"/>'
            f'<path d="M{cx},{cy - 150} v80" stroke="#b9aaf0" stroke-width="4"/>'
            + rect(cx - 10, cy - 125, 20, 40, fill="#d9d2f5", r=10)
            + rect(cx - 110, cy - 14, 34, 52, fill=HL, r=9)
            + t(cx - 93, cy + 21, "A", 22, "#fff", 700, "middle")
            + rect(cx - 110, cy + 46, 34, 52, fill=ACCENT, r=9)
            + t(cx - 93, cy + 81, "B", 22, "#fff", 700, "middle"))


def img_mouse():
    body = [mouse(260, 360)]
    body.append(rect(450, 230, 700, 120, r=18, stroke=HL, sw=3, extra='filter="url(#sh)"'))
    body.append(t(480, 272, "ボタンA：ラベルを付ける", 22, INK, 700))
    ks, _ = keys(480, 290, ["Ctrl", "Shift", "Y"], size=22)
    body.append(ks)
    body.append(rect(450, 380, 700, 120, r=18, stroke=ACCENT, sw=3, extra='filter="url(#sh)"'))
    body.append(t(480, 422, "ボタンB：送信する（お好みで）", 22, INK, 700))
    k2, _ = keys(480, 440, ["Ctrl", "Enter"], size=22)
    body.append(k2)
    body.append(t(830, 478, "押した瞬間に送信", 17, HL, 700))
    body.append(bubble(50, 540, 1100, ["マウスの設定ソフト（Logi Options+ など）の「キーストロークの割り当て」でボタンにキーを入れます",
                                      "Chromeだけで効くよう「アプリ別設定」にすると安心です"], 19))
    return frame(7, "マウスのボタン1つで使う", "ラベル→送信を親指だけで", "".join(body))


def flow_box(x, y, w, h, lines, fill="#fff", stroke=LINE, size=19, bold=False):
    out = [rect(x, y, w, h, fill=fill, r=14, stroke=stroke, sw=2)]
    total = len(lines) * (size + 8)
    for i, line in enumerate(lines):
        out.append(t(x + w / 2, y + (h - total) / 2 + size + i * (size + 8) - 2, line, size, INK, 700 if bold else 400, "middle"))
    return "".join(out)


def img_trouble():
    b = [flow_box(420, 140, 360, 64, ["キーを押すと画面の下に何か出る？"], fill="#efe9ff", stroke=ACCENT, bold=True),
         arrow(520, 206, 270, 254, 0, ACCENT, 4), arrow(680, 206, 900, 254, 0, ACCENT, 4),
         t(150, 238, "赤い字が出る", 20, HL, 700), t(920, 238, "何も出ない", 20, SUB, 700),
         flow_box(50, 262, 460, 210, ["Xの画面の作りが変わった可能性", "", "・投稿欄が開いているか確かめる", "・GitHubのIssuesで知らせてください",
                                      "・新しい版が出たら入れ直す"], size=18),
         flow_box(620, 262, 530, 64, ["① Xのタブを再読み込みした？"]),
         flow_box(620, 342, 530, 64, ["② いま使っているChromeのプロフィールに入れた？"]),
         flow_box(620, 422, 530, 64, ["③ ツールバーの拡張アイコンを押すと動く？"]),
         arrow(760, 490, 700, 532, 0, ACCENT, 4), arrow(1010, 490, 1070, 532, 0, ACCENT, 4),
         flow_box(560, 540, 280, 76, ["動く→キーが届いていない", "（マウス設定・他のソフト）"], size=16, fill="#fff8e1", stroke="#f2c94c"),
         flow_box(870, 540, 280, 76, ["動かない→拡張を更新して", "Xを再読み込み"], size=16, fill="#fff8e1", stroke="#f2c94c")]
    return frame(None, "うまく動かないときは", None, "".join(b))


IMAGES = {
    "01-hero": img_hero,
    "02-download": img_download,
    "03-devmode": img_devmode,
    "04-load": img_load,
    "05-reload": img_ready,
    "06-use": img_use,
    "07-settings": img_settings,
    "08-mouse": img_mouse,
    "09-trouble": img_trouble,
}


def main():
    SRC.mkdir(parents=True, exist_ok=True)
    for name, fn in IMAGES.items():
        svg_path = SRC / f"{name}.svg"
        svg_path.write_text(fn(), encoding="utf-8")
        png_path = OUT / f"{name}.png"
        subprocess.run([
            str(CHROME), "--headless=new", "--disable-gpu", "--hide-scrollbars",
            f"--window-size={W},{H}", "--force-device-scale-factor=2",
            f"--screenshot={png_path}", svg_path.as_uri(),
        ], check=True, capture_output=True)
        print("作成:", png_path.name)


if __name__ == "__main__":
    main()
