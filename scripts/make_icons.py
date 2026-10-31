"""拡張のアイコン（icons/icon16〜128.png）を作り直す。

紫の角丸の上に、白いキラキラ（AI を表す）を置いた絵。
Chrome の決まりに合わせ、128px でも絵は中の 96px に収め、まわりは透明にする。

使い方: python scripts/make_icons.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "icons"
SIZES = [16, 32, 48, 128]
BIG = 1024  # 大きく描いてから縮める（ふちをなめらかにするため）

TOP = (138, 92, 255)  # 上の色
BOTTOM = (91, 47, 214)  # 下の色


def sparkle(draw, cx, cy, r, fill):
    """4 本の角が伸びたキラキラ。r は角の先までの長さ。"""
    w = r * 0.28  # くびれの太さ
    pts = [
        (cx, cy - r), (cx + w, cy - w), (cx + r, cy), (cx + w, cy + w),
        (cx, cy + r), (cx - w, cy + w), (cx - r, cy), (cx - w, cy - w),
    ]
    draw.polygon(pts, fill=fill)


def make_base(pad_ratio):
    img = Image.new("RGBA", (BIG, BIG), (0, 0, 0, 0))
    pad = int(BIG * pad_ratio)
    box = (pad, pad, BIG - pad, BIG - pad)
    side = box[2] - box[0]

    # 上から下へ色が変わる角丸の四角
    grad = Image.new("RGBA", (BIG, BIG))
    gd = ImageDraw.Draw(grad)
    for y in range(BIG):
        t = min(max((y - pad) / side, 0), 1)
        c = tuple(round(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3))
        gd.line([(0, y), (BIG, y)], fill=c + (255,))
    mask = Image.new("L", (BIG, BIG), 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius=int(side * 0.24), fill=255)
    img.paste(grad, (0, 0), mask)

    d = ImageDraw.Draw(img)
    cx = box[0] + side * 0.46
    cy = box[1] + side * 0.54
    sparkle(d, cx, cy, side * 0.34, (255, 255, 255, 255))
    sparkle(d, box[0] + side * 0.76, box[1] + side * 0.26, side * 0.13, (255, 255, 255, 235))
    return img


def main():
    OUT.mkdir(exist_ok=True)
    for size in SIZES:
        # 小さいアイコンは余白を少なくして絵を大きく見せる
        pad_ratio = 0.125 if size == 128 else 0.04
        img = make_base(pad_ratio).resize((size, size), Image.LANCZOS)
        img.save(OUT / f"icon{size}.png")
        print("作成:", OUT / f"icon{size}.png")


if __name__ == "__main__":
    main()
