#!/usr/bin/env python3
"""把游戏里的章节背景同步到网站。游戏里换了背景，跑一遍就行。

用法：在网站根目录跑  python3 tools/backdrops.py <游戏仓库的路径>      （需要 pip install pillow）
例子：python3 tools/backdrops.py "/Users/cake5031/Game Dev/Ferazoic"

游戏里的章节背景是 720×880 的竖图（给手机竖屏用的）：上面 340 行是远景，中间是动物走的地面，下面是近景。
网站上只用得着其中一段，整张放上来一张要 1 MB 多，所以截出来：
  1. assets/games/ferazoic/backdrop.png：首页展示窗、详情页顶图后面的背景。
     第一章背景的第 80～419 行，原样截，一个像素都不改。
     放多大、动物的脚踩在第几行，写在 css/site.css 的「.t-ferazoic .window, .t-ferazoic .gh」那一段；
     这里截的行改了（BACKDROP），那一段里的 420 要跟着改（这个脚本会检查）。
  2. assets/games/ferazoic/scene1.jpg、scene2.jpg、scene3.jpg：详情页「三个章节的场景」的三张小图。
     前三章背景的第 0～359 行（景色那一段）。网页上是缩小了看的，所以存成 JPEG，一张 100 KB 左右。
"""
import os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "games", "ferazoic")
BACKGROUNDS = os.path.join("client", "Assets", "Resources", "Ferazoic", "Art", "Backgrounds")
SIZE = (720, 880)                                # 游戏里章节背景的大小
BACKDROP = ("chapter1", 80, 420)                 # 展示窗、顶图：用哪一张，从第几行截到第几行（不含）
SCENES = ["chapter1", "chapter2", "chapter3"]    # 三张小图，按顺序存成 scene1、scene2、scene3
SCENE_ROWS = (0, 360)                            # 小图截哪几行（不含后一个数）


def die(msg):
    sys.exit("不行：" + msg)


def read(game, name):
    """读一张章节背景，检查大小、有没有透明的地方，转成不带透明度的图。"""
    path = os.path.join(game, BACKGROUNDS, name + ".png")
    if not os.path.isfile(path):
        die("找不到 " + path)
    im = Image.open(path)
    if im.size != SIZE:
        die("%s 是 %d×%d，这个脚本是按 %d×%d 写的" % (path, im.width, im.height, SIZE[0], SIZE[1]))
    rgba = im.convert("RGBA")
    if rgba.getchannel("A").getextrema()[0] != 255:
        die(path + " 里有透明的地方，背景应该是铺满的")
    return rgba.convert("RGB")


def main():
    if len(sys.argv) != 2:
        die("用法：python3 tools/backdrops.py <游戏仓库的路径>")
    game = sys.argv[1]
    if not os.path.isdir(os.path.join(game, BACKGROUNDS)):
        die("%s 里没有 %s，路径是不是游戏仓库的根目录？" % (game, BACKGROUNDS))

    name, top, bottom = BACKDROP
    css = os.path.join(ROOT, "css", "site.css")
    with open(css, encoding="utf-8") as f:
        if ("(%d - var(--row))" % bottom) not in f.read():
            die("css/site.css 里背景那一段写的不是 (%d - var(--row))：截的行改了，那里要一起改" % bottom)

    written = []
    out = os.path.join(OUT, "backdrop.png")
    read(game, name).crop((0, top, SIZE[0], bottom)).save(out, optimize=True)
    written.append(out)
    for i, scene in enumerate(SCENES, 1):
        out = os.path.join(OUT, "scene%d.jpg" % i)
        read(game, scene).crop((0, SCENE_ROWS[0], SIZE[0], SCENE_ROWS[1])).save(
            out, quality=90, subsampling=0, optimize=True, progressive=True)   # subsampling=0：颜色不减半，红锈、黄草的边不糊
        written.append(out)
    for path in written:
        with Image.open(path) as im:
            print("%s  %d×%d  %d KB" % (os.path.relpath(path, ROOT), im.width, im.height, os.path.getsize(path) // 1024))


if __name__ == "__main__":
    main()
