#!/usr/bin/env python3
"""店招和左上角的蒸笼：把 Mark 给的大图（tools/src/steamer.png，1254×1254）缩成真正的像素图。
用法：在网站根目录跑 python3 tools/steamer.py（需要 pip install pillow numpy）
写出 assets/ui/steamer.png（75×75，店招上放大 2 倍用）和 assets/ui/steamer_nav.png（30×30，左上角回主页的小图标）。
做法：先把颜色乘上透明度再缩（透明像素的黑色不会混进边上），缩完透明度一刀切（像素图的边要干净），再把颜色归成几十种（没有渐变才像像素图）。
"""
import os
from PIL import Image
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "src", "steamer.png")
OUT = os.path.join(ROOT, "assets", "ui")

def convert(src, size, method, colors, threshold=0.5):
    a = np.asarray(src.convert("RGBA")).astype(np.float32) / 255.0
    alpha = a[:, :, 3:4]
    premultiplied = np.concatenate([a[:, :, :3] * alpha, alpha], axis=2)
    small = np.stack([np.asarray(Image.fromarray(premultiplied[:, :, i], mode="F").resize((size, size), method)) for i in range(4)], axis=2)
    alpha2 = small[:, :, 3:4]
    rgb = np.where(alpha2 > 1e-4, small[:, :, :3] / np.maximum(alpha2, 1e-4), 0)
    im = Image.fromarray(np.clip(rgb * 255 + 0.5, 0, 255).astype(np.uint8), "RGB")
    im = im.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    mask = (alpha2[:, :, 0] >= threshold) * 255
    return Image.fromarray(np.dstack([np.asarray(im), mask.astype(np.uint8)]), "RGBA")

def main():
    src = Image.open(SRC)
    convert(src, 75, Image.Resampling.LANCZOS, 32).save(os.path.join(OUT, "steamer.png"))
    convert(src, 30, Image.Resampling.BOX, 24).save(os.path.join(OUT, "steamer_nav.png"))
    print("ok: steamer.png 75x75, steamer_nav.png 30x30")

if __name__ == "__main__":
    main()
