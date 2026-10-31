#!/usr/bin/env python3
"""把像素字体裁成常用字，网页就不用下载 3.4 MB 的整套字体。

用法：python3 tools/subset_font.py        （在网站根目录跑，需要 pip install fonttools brotli）

裁出来的字包括：
  - 网页里实际写了的每一个字（扫 *.html 和 js/*.js）；
  - GB2312 一级常用汉字 3755 个；
  - ASCII、常用中英文标点、箭头、方块、星星等符号。
加了生僻字、字体里有但不在以上范围的字，重新跑一遍就行；没跑的话那个字会退回系统字体。
整套字体在 tools/font/FusionPixel.ttf，裁好的写到 assets/fonts/FusionPixel-sub.woff2 和 .ttf。
"""
import glob, os, sys
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "font", "FusionPixel.ttf")
OUT = os.path.join(ROOT, "assets", "fonts", "FusionPixel-sub")

def chars():
    keep = set()
    for pat in ("*.html", "js/*.js"):
        for f in glob.glob(os.path.join(ROOT, pat)):
            with open(f, encoding="utf-8") as fh:
                keep.update(fh.read())
    keep.update(chr(c) for c in range(0x20, 0x7F))                 # ASCII
    for lo, hi in ((0x00A0, 0x00FF), (0x2000, 0x206F), (0x2190, 0x21FF), (0x2500, 0x25FF),
                   (0x2600, 0x2606), (0x2660, 0x2667), (0x3000, 0x303F), (0xFF00, 0xFFEF)):
        keep.update(chr(c) for c in range(lo, hi + 1))             # 标点、箭头、方块、星星、全角
    for row in range(0xB0, 0xD8):                                  # GB2312 一级汉字（16~55 区）
        for col in range(0xA1, 0xFF):
            try: keep.add(bytes((row, col)).decode("gb2312"))
            except UnicodeDecodeError: pass
    return {c for c in keep if ord(c) >= 0x20 and c not in "\x7f"}

def main():
    text = "".join(sorted(chars()))
    cmap = TTFont(SRC).getBestCmap()
    missing = sorted(c for c in text if ord(c) not in cmap)
    for flavor in ("woff2", None):
        out = OUT + ("." + flavor if flavor else ".ttf")
        args = [SRC, "--text=" + text, "--output-file=" + out, "--layout-features=*", "--no-hinting",
                "--desubroutinize", "--name-IDs=*", "--notdef-outline", "--drop-tables+=DSIG"]
        if flavor: args.append("--flavor=" + flavor)
        subset.main(args)
        print("%s  %.0f KB  %d 字形" % (os.path.relpath(out, ROOT), os.path.getsize(out) / 1024, TTFont(out)["maxp"].numGlyphs))
    print("整套 %.0f KB，%d 字形；要的字 %d 个，字体里没有的 %d 个%s" % (
        os.path.getsize(SRC) / 1024, TTFont(SRC)["maxp"].numGlyphs, len(text), len(missing),
        ("：" + "".join(missing[:40])) if missing else ""))

if __name__ == "__main__":
    main()
