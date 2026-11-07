"""店招：挂在铁皮墙上的铁牌（九宫格）、吊牌的链条、小笼包蒸笼图标。全部 1 倍像素，网页按 --s 放大。"""
# 用法：python3 tools/sign.py（在网站根目录跑，需要 pip install pillow）
import random
from PIL import Image, ImageDraw
OUT = __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "..", "assets", "ui") + "/"
IRON = (58, 61, 66); IRON_L = (112, 118, 126); IRON_D = (34, 36, 40); IRON_DD = (20, 22, 25)
RUST = (139, 78, 40); RUST_D = (96, 52, 26); RIVET = (120, 126, 132); RIVET_D = (44, 46, 50)

def plate():
    # 48×48 九宫格，边 12 像素；中间一块可以平铺
    r = random.Random(7)
    im = Image.new("RGBA", (48, 48), IRON); d = ImageDraw.Draw(im)
    for x in range(48):
        for y in range(48):
            if r.random() < .10: im.putpixel((x, y), IRON_D if r.random() < .5 else IRON_L)
    d.rectangle([0, 0, 47, 47], outline=IRON_DD)             # 最外一圈
    d.line([1, 1, 46, 1], fill=IRON_L); d.line([1, 1, 1, 46], fill=IRON_L)   # 左上亮边
    d.line([1, 46, 46, 46], fill=IRON_D); d.line([46, 1, 46, 46], fill=IRON_D)  # 右下暗边
    for (x, y) in [(4, 4), (40, 4), (4, 40), (40, 40)]:      # 四角铆钉
        d.rectangle([x, y, x + 3, y + 3], fill=RIVET); d.point((x, y), fill=(160, 166, 172))
        d.point((x + 3, y + 3), fill=RIVET_D); d.point((x + 3, y), fill=RIVET_D); d.point((x, y + 3), fill=RIVET_D)
    for (x, y, w, h) in [(2, 20, 3, 9), (43, 30, 3, 10), (18, 44, 9, 2)]:     # 边上几块锈
        d.rectangle([x, y, x + w, y + h], fill=RUST)
        for i in range(w * h // 3): im.putpixel((x + r.randint(0, w), y + r.randint(0, h)), RUST_D)
    im.save(OUT + "sign9.png")

def chain():
    # 6×12 一节，竖着平铺：粗环和细环交替
    im = Image.new("RGBA", (6, 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([1, 0, 4, 6], outline=IRON_L); d.point((1, 0), fill=IRON_D); d.point((4, 6), fill=IRON_D)
    d.line([2, 6, 3, 6], fill=IRON_DD)
    d.line([2, 7, 2, 11], fill=IRON_D); d.line([3, 7, 3, 11], fill=IRON_L)
    im.save(OUT + "chain.png")

# 蒸笼（steamer.png、steamer_nav.png）不在这里画了：是 Mark 给的图，由 tools/steamer.py 缩成像素图。

plate(); chain(); print("ok")
