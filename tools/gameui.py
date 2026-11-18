#!/usr/bin/env python3
"""把游戏里的界面零件同步到网站。游戏里换了这些图，跑一遍就行。

用法：在网站根目录跑  python3 tools/gameui.py <游戏仓库的路径>      （需要 pip install pillow）
例子：python3 tools/gameui.py "/Users/cake5031/Game Dev/Ferazoic"

《兽变纪元》那一段和详情页用的是游戏里的界面零件，都放在 assets/games/ferazoic/ui/：
  concrete.png          水泥墙（避难所以外的页面铺的底），原样复制
  panel.png             铁框面板。游戏里是两张叠起来的：底（panel_base，灰度图，游戏里乘上面板的颜色）、
                        上面盖铁框（panel_trim）。网页的九宫格只能用一张图，所以在这里照游戏的做法叠成一张
  chip.png              数量条的铁皮条（网站上当标签的底），原样复制
  back.png              返回木牌，原样复制
  button_<颜色>.png      四种铁板按钮，原样复制

这些图多大、九宫格的边多宽，css/site.css 的「兽变纪元」那一节里写着同样的数。
游戏里改了（图的大小、.meta 里九宫格的边），这个脚本会停下来说哪里对不上，那一节要跟着改。
"""
import os, re, shutil, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "games", "ferazoic", "ui")
ART = os.path.join("client", "Assets", "Resources", "Ferazoic", "Art")
PARTS = os.path.join(ART, "UI", "Parts")
COLORS = os.path.join("client", "Assets", "Scripts", "Game", "GameText.cs")   # GameColors.Panel 写在这个文件里

# 原样复制的：网站上的名字 -> (游戏里的文件, 宽, 高, 九宫格的边 左 下 右 上)
COPIES = {
    "concrete.png": (os.path.join(ART, "Backgrounds", "concrete.png"), 288, 288, (0, 0, 0, 0)),
    "chip.png": (os.path.join(PARTS, "chip.png"), 48, 32, (14, 0, 18, 0)),
    "back.png": (os.path.join(PARTS, "back.png"), 88, 52, (0, 0, 0, 0)),
    "button_orange.png": (os.path.join(PARTS, "button_orange.png"), 40, 40, (12, 12, 12, 12)),
    "button_green.png": (os.path.join(PARTS, "button_green.png"), 40, 40, (12, 12, 12, 12)),
    "button_blue.png": (os.path.join(PARTS, "button_blue.png"), 40, 40, (12, 12, 12, 12)),
    "button_steel.png": (os.path.join(PARTS, "button_steel.png"), 40, 40, (12, 12, 12, 12)),
}
PANEL = (os.path.join(PARTS, "panel_base.png"), os.path.join(PARTS, "panel_trim.png"), 44, 44, (14, 14, 14, 14))

# css/site.css 里要有这几段（图的大小、九宫格的边写在里面），对不上就是那一节没跟着改
CSS_MUST_HAVE = [
    "calc(288px * var(--gu))",                # 水泥墙一块 288
    "ui/panel.png) 14 fill",                  # 面板九宫格四边各 14
    "ui/chip.png) 0 18 0 14 fill",            # 数量条：右 18、左 14，上下不切
    "width: 88px; height: 52px",              # 返回木牌 88×52
    "ui/button_orange.png) 12 fill",          # 按钮九宫格四边各 12
]


def die(msg):
    sys.exit("不行：" + msg)


def border(path):
    """读 Unity 的 .meta 里九宫格的边：左、下、右、上。"""
    meta = path + ".meta"
    if not os.path.isfile(meta):
        die("找不到 " + meta)
    with open(meta, encoding="utf-8") as f:
        m = re.search(r"spriteBorder:\s*\{x:\s*(\d+),\s*y:\s*(\d+),\s*z:\s*(\d+),\s*w:\s*(\d+)\}", f.read())
    if not m:
        die(meta + " 里没有 spriteBorder")
    return tuple(int(v) for v in m.groups())


def check(path, width, height, edges):
    if not os.path.isfile(path):
        die("找不到 " + path)
    with Image.open(path) as im:
        if im.size != (width, height):
            die("%s 是 %d×%d，网站是按 %d×%d 写的（css/site.css 的「兽变纪元」那一节要跟着改）" % (path, im.width, im.height, width, height))
    if border(path) != edges:
        die("%s 的九宫格的边是 %s，网站是按 %s 写的（左、下、右、上）" % (path, border(path), edges))


def to_linear(v):
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def to_srgb(v):
    v = v * 12.92 if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
    return max(0, min(255, int(round(v * 255))))


def panel_color(game):
    """游戏里面板的颜色：GameColors.Panel。"""
    path = os.path.join(game, COLORS)
    if not os.path.isfile(path):
        die("找不到 " + path)
    with open(path, encoding="utf-8") as f:
        m = re.search(r"Color\s+Panel\s*=>\s*new\s+Color32\(\s*0x([0-9a-fA-F]{2}),\s*0x([0-9a-fA-F]{2}),\s*0x([0-9a-fA-F]{2}),\s*0xff\s*\)", f.read())
    if not m:
        die(path + " 里找不到 GameColors.Panel（面板的颜色），是不是换地方写了？")
    return tuple(int(v, 16) for v in m.groups())


def tinted(base, color):
    """Unity 的界面给图上色：图的颜色 × 上的颜色，在线性空间里乘（工程的 Color Space 是 Linear）。"""
    lin = [to_linear(c) for c in color]
    out = Image.new("RGBA", base.size)
    src, dst = base.load(), out.load()
    for y in range(base.height):
        for x in range(base.width):
            r, g, b, a = src[x, y]
            dst[x, y] = (to_srgb(to_linear(r) * lin[0]), to_srgb(to_linear(g) * lin[1]), to_srgb(to_linear(b) * lin[2]), a)
    return out


def main():
    if len(sys.argv) != 2:
        die("用法：python3 tools/gameui.py <游戏仓库的路径>")
    game = sys.argv[1]
    if not os.path.isdir(os.path.join(game, PARTS)):
        die("%s 里没有 %s，路径是不是游戏仓库的根目录？" % (game, PARTS))

    with open(os.path.join(ROOT, "css", "site.css"), encoding="utf-8") as f:
        css = f.read()
    for piece in CSS_MUST_HAVE:
        if piece not in css:
            die("css/site.css 里没有「%s」：这个脚本和那一节写的数要一样，哪边改了另一边要跟着改" % piece)

    base_path, trim_path, width, height, edges = PANEL
    for name, (path, w, h, e) in COPIES.items():
        check(os.path.join(game, path), w, h, e)
    check(os.path.join(game, base_path), width, height, edges)
    check(os.path.join(game, trim_path), width, height, edges)

    written = []
    for name, (path, w, h, e) in COPIES.items():
        shutil.copyfile(os.path.join(game, path), os.path.join(OUT, name))
        written.append(name)

    base = Image.open(os.path.join(game, base_path)).convert("RGBA")
    trim = Image.open(os.path.join(game, trim_path)).convert("RGBA")
    for im, path in ((base, base_path), (trim, trim_path)):
        if any(im.getchannel("A").histogram()[1:255]):
            die(path + " 里有半透明的像素，这个脚本是按只有全透明、全不透明写的")
    color = panel_color(game)
    panel = tinted(base, color)
    panel.alpha_composite(trim)
    panel.save(os.path.join(OUT, "panel.png"), optimize=True)
    written.append("panel.png")

    print("面板的颜色（GameColors.Panel）：#%02x%02x%02x" % color)
    for name in written:
        path = os.path.join(OUT, name)
        with Image.open(path) as im:
            print("%s  %d×%d  %d B" % (os.path.relpath(path, ROOT), im.width, im.height, os.path.getsize(path)))


if __name__ == "__main__":
    main()
