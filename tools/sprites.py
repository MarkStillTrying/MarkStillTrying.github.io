#!/usr/bin/env python3
"""把游戏里动物的待机图同步到网站。游戏里换了美术、加了动物，跑一遍就行。

用法：在网站根目录跑  python3 tools/sprites.py <游戏仓库的路径>      （需要 pip install pillow numpy）
例子：python3 tools/sprites.py "/Users/cake5031/Game Dev/Ferazoic"

做三件事：
  1. 按游戏的动物表（units.json）把每只动物的待机精灵图（<art>_idle.png，8 帧横着排）原样复制到
     assets/games/ferazoic/sprites/，游戏里已经没有的动物的图删掉；
  2. 重写 js/projects.js 里 window.SPRITES 那张表（两行记号中间）：帧的宽高、一圈多少毫秒、
     身子画在哪几列（x0～x1，排位置、居中用）、脚下面还空着几行（foot，让每只都踩在同一条线上）；
  3. 重写 ferazoic.html 里「登场动物」的名单（两行记号中间）：按稀有度从低到高排，名字用游戏里的。
首页展示窗、详情页顶图站哪几只不归它管：在 js/projects.js 的 showcase.sprites 和 ferazoic.html 顶图的 data-sprites 里写。
新名字里有生僻字的话，跑完再跑一遍 python3 tools/subset_font.py（它会说字体里没有哪几个字）。
"""
import json, os, re, shutil, sys
from PIL import Image
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "games", "ferazoic", "sprites")
URL = "assets/games/ferazoic/sprites/"
FRAMES = 8          # css/site.css 里的动画写死了 steps(8)
CONFIG = os.path.join("shared", "Ferazoic.Config", "Resources", "Ferazoic", "Config")
UNITS = os.path.join("client", "Assets", "Resources", "Ferazoic", "Art", "Units")


def die(msg):
    sys.exit("不行：" + msg)


def read_units(game):
    """每只动物：id、名字、稀有度、精灵图和量出来的数。顺序和游戏的动物表一样。"""
    with open(os.path.join(game, CONFIG, "rarities.json"), encoding="utf-8") as f:
        rarities = [r["id"] for r in json.load(f)]
    with open(os.path.join(game, CONFIG, "units.json"), encoding="utf-8") as f:
        units = json.load(f)
    out = []
    for u in units:
        art = u["art"]
        folder = os.path.join(game, UNITS, art)
        with open(os.path.join(folder, "anim.json"), encoding="utf-8") as f:
            anim = json.load(f)
        idle = anim["anims"]["idle"]
        fw, fh = anim["frameWidth"], anim["frameHeight"]
        ms = idle["durationsMs"]
        if len(ms) != FRAMES:
            die("%s 的待机动画是 %d 帧，网站的动画按 %d 帧写的" % (art, len(ms), FRAMES))
        if len(set(ms)) != 1:
            die("%s 的待机动画每帧时间不一样 %s，网站的动画只会每帧一样长" % (art, ms))
        sheet = os.path.join(folder, idle["sheet"] + ".png")
        px = np.asarray(Image.open(sheet).convert("RGBA"))
        if px.shape[1] != fw * FRAMES or px.shape[0] != fh:
            die("%s 是 %d×%d，按 anim.json 应该是 %d×%d" % (sheet, px.shape[1], px.shape[0], fw * FRAMES, fh))
        drawn = px[:, :, 3] > 0
        cols = np.nonzero(drawn.reshape(fh, FRAMES, fw).any(axis=(0, 1)))[0]   # 八帧叠在一起，哪几列画了东西
        if u["rarity"] not in rarities:
            die("%s 的稀有度 %s 不在 rarities.json 里" % (u["id"], u["rarity"]))
        out.append({
            "id": u["id"], "name": u["name"], "rarity": u["rarity"], "rank": rarities.index(u["rarity"]),
            "src": sheet, "file": u["id"] + "_idle.png",
            "fw": fw, "fh": fh, "dur": sum(ms), "x0": int(cols[0]), "x1": int(cols[-1]), "foot": fh - anim["pivotY"],
        })
    return out


def replace_block(path, start, end, body):
    """把文件里 start 那一行和 end 那一行中间的内容换成 body（两行记号留着）。"""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    pattern = re.compile(r"(^[^\n]*" + re.escape(start) + r"[^\n]*\n)(.*?)(^[^\n]*" + re.escape(end) + r")", re.S | re.M)
    if len(pattern.findall(text)) != 1:
        die("%s 里应该正好有一段「%s」……「%s」" % (os.path.relpath(path, ROOT), start, end))
    new = pattern.sub(lambda m: m.group(1) + body + m.group(3), text)
    if new != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
    return new != text


def sprites_js(units):
    pad = max(len(u["id"]) for u in units) + 1
    rows = []
    for u in units:
        rows.append('  %s{ fw: %d, fh: %d, dur: %d, x0: %d, x1: %d, foot: %d, sheet: "%s%s" }' % (
            (u["id"] + ":").ljust(pad + 1), u["fw"], u["fh"], u["dur"], u["x0"], u["x1"], u["foot"], URL, u["file"]))
    return "window.SPRITES = {\n" + ",\n".join(rows) + "\n};\n"


def roster_html(units, indent):
    """「登场动物」的格子。动物直接写在网页里（不靠 JavaScript），--wmax 是最宽的那只有多宽，格子窄时按它缩小。"""
    ordered = sorted(units, key=lambda u: u["rank"])      # sorted 是稳定的：同一档里还是动物表的顺序
    wmax = max(u["x1"] - u["x0"] + 1 for u in units)
    lines = ['%s<div class="roster" role="list" style="--wmax:%d">' % (indent, wmax)]
    for u in ordered:
        cx = (u["x0"] + u["x1"] + 1) // 2                 # 身子正中间在第几列（取整，图才落在整像素上）
        style = "--fw:%d;--fh:%d;--foot:%d;--cx:%d;--dur:%dms;background-image:url(%s%s)" % (
            u["fw"], u["fh"], u["foot"], cx, u["dur"], URL, u["file"])
        lines.append('%s  <div role="listitem"><div class="stage" aria-hidden="true"><i class="sprite" style="%s"></i></div>'
                     '<div class="name r-%s">%s</div></div>' % (indent, style, u["rarity"], u["name"]))
    lines.append("%s</div>" % indent)
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    game = os.path.expanduser(sys.argv[1])
    if not os.path.isdir(os.path.join(game, UNITS)):
        die("%s 里没有 %s，路径要写到游戏仓库的最外面一层" % (game, UNITS))
    units = read_units(game)

    os.makedirs(OUT, exist_ok=True)
    changed, same = [], 0
    for u in units:
        dst = os.path.join(OUT, u["file"])
        with open(u["src"], "rb") as f:
            data = f.read()
        old = open(dst, "rb").read() if os.path.exists(dst) else None
        if old == data:
            same += 1
            continue
        shutil.copyfile(u["src"], dst)
        changed.append(("新加 " if old is None else "换了 ") + u["name"])
    keep = {u["file"] for u in units}
    gone = sorted(f for f in os.listdir(OUT) if f.endswith(".png") and f not in keep)
    for f in gone:
        os.remove(os.path.join(OUT, f))

    js = replace_block(os.path.join(ROOT, "js", "projects.js"), ">>> sprites", "<<< sprites", sprites_js(units))
    html_path = os.path.join(ROOT, "ferazoic.html")
    with open(html_path, encoding="utf-8") as f:
        indent = re.search(r"^([ \t]*)<!-- >>> roster", f.read(), re.M)
    if not indent:
        die("ferazoic.html 里没找到 <!-- >>> roster 这一行")
    html = replace_block(html_path, ">>> roster", "<<< roster", roster_html(units, indent.group(1)))

    print("动物 %d 只：%s" % (len(units), "、".join(u["name"] for u in units)))
    print("精灵图：%d 张没变%s%s" % (same, "；" + "，".join(changed) if changed else "", "；删掉 " + "、".join(gone) if gone else ""))
    print("js/projects.js 的表%s，ferazoic.html 的名单%s" % ("改了" if js else "没变", "改了" if html else "没变"))
    missing = [r for r in sorted({u["rarity"] for u in units}) if (".roster .r-" + r) not in open(os.path.join(ROOT, "css", "site.css"), encoding="utf-8").read()]
    if missing:
        print("注意：css/site.css 里还没有这几种稀有度的名字颜色：" + "、".join(".r-" + r for r in missing))


if __name__ == "__main__":
    main()
