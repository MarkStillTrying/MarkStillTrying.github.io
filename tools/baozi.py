#!/usr/bin/env python3
"""店里的包子吉祥物：从 Mark 画的包子国王（king.png）里把身子抠出来（右边被盾牌挡住的照左边镜像，
王冠盖住的顶按褶子补画），再换表情、加帽子、衣服和手里的东西。
用法：python3 tools/baozi.py（在网站根目录跑，需要 pip install pillow）
写到 assets/ui/mascots/：base.png 光身子，waiter.png 店小二，chef.png 厨师，artist.png 画家，coder.png 写代码的。
画风照 Mark 的包子：没有黑描边，Material 那套颜色，灰白的包子，细腿黑脚，眼睛是两条竖的小黑条，手是两像素宽的棕线。
坐标全用 king.png 的坐标（身子 x 25~72、顶 y 11、底 y 46，脚到 y 57），最后按内容裁掉空边。
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "ui", "mascots")
KING = os.path.join(OUT, "king.png")

def rgb(h, a=255): return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), a)
# Mark 的色板（从他的图里数出来的）
WHITE, WHITE2, EDGE_L, EDGE_R = rgb("#eeeeee"), rgb("#e9e9e9"), rgb("#cecece"), rgb("#bdbdbd")
PLEAT_L, PLEAT_D = rgb("#b1afaf"), rgb("#757575")      # 褶子：亮边 + 暗缝
INK, INK2, EYE_HI = rgb("#212121"), rgb("#424242"), rgb("#bdbdbd")
ARM, ARM2 = rgb("#3e2723"), rgb("#4e342e")
RED, RED2 = rgb("#e51c23"), rgb("#b6171c")
SLATE, SLATE2, SLATE3 = rgb("#546e7a"), rgb("#455a64"), rgb("#78909c")
DARK = rgb("#37474f")
AMBER, GREEN, BLUE = rgb("#ffc107"), rgb("#43a047"), rgb("#1e88e5")
BROWN, BROWN2, WOOD = rgb("#6d4c41"), rgb("#4e342e"), rgb("#8d6e63")
GRAY, GRAY2, GRAY3, STEEL = rgb("#9e9e9e"), rgb("#757575"), rgb("#616161"), rgb("#424242")
BAMBOO, BAMBOO2, BAMBOO3 = rgb("#c9a86a"), rgb("#a8864a"), rgb("#8a6e3a")
STEAM = rgb("#e8eef0", 140)
CX = 98  # 左右对称轴：x' = 98 - x

def is_gray(c): return c[3] > 0 and max(c[:3]) - min(c[:3]) <= 10

class Canvas:
    """按 king.png 的坐标画，margin 是四周留的边（帽子、手里的东西会超出身子）。"""
    def __init__(self, margin=(30, 30, 30, 10)):
        self.ml, self.mt = margin[0], margin[1]
        k = Image.open(KING).convert("RGBA")
        self.im = Image.new("RGBA", (k.width + margin[0] + margin[2], k.height + margin[1] + margin[3]), (0, 0, 0, 0))
        self.p = self.im.load()
    def put(self, x, y, c):
        X, Y = x + self.ml, y + self.mt
        if 0 <= X < self.im.width and 0 <= Y < self.im.height:
            if c[3] == 255: self.p[X, Y] = c
            else:
                b = self.p[X, Y]; a = c[3] / 255
                self.p[X, Y] = tuple(int(c[i] * a + b[i] * (1 - a)) for i in range(3)) + (max(b[3], c[3]),)
    def get(self, x, y):
        X, Y = x + self.ml, y + self.mt
        return self.p[X, Y] if 0 <= X < self.im.width and 0 <= Y < self.im.height else (0, 0, 0, 0)
    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): self.put(x, y, c)
    def hline(self, x0, x1, y, c):
        for x in range(min(x0, x1), max(x0, x1) + 1): self.put(x, y, c)
    def vline(self, x, y0, y1, c):
        for y in range(min(y0, y1), max(y0, y1) + 1): self.put(x, y, c)
    def line(self, x0, y0, x1, y1, c, w=1):
        """Bresenham，w=2 时往右（竖线）或往下（横线）多画一像素。"""
        dx, dy = abs(x1 - x0), abs(y1 - y0); sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1
        err = dx - dy; x, y = x0, y0
        while True:
            self.put(x, y, c)
            if w == 2: self.put(x + 1, y, c) if dy >= dx else self.put(x, y + 1, c)
            if x == x1 and y == y1: break
            e2 = 2 * err
            if e2 > -dy: err -= dy; x += sx
            if e2 < dx: err += dx; y += sy
    def ellipse(self, cx, cy, rx, ry, c, edge=None):
        """实心椭圆，一行一行扫，边上干净；edge 给了就把最外一圈换成 edge 色。"""
        rows = {}
        for y in range(int(cy - ry), int(cy + ry) + 1):
            dy = (y - cy) / ry
            if dy * dy >= 1: continue
            h = rx * (1 - dy * dy) ** 0.5
            rows[y] = (int(round(cx - h)), int(round(cx + h)))
        for y, (x0, x1) in rows.items():
            for x in range(x0, x1 + 1): self.put(x, y, c)
        if edge:
            for y, (x0, x1) in rows.items():
                for x in range(x0, x1 + 1):
                    if x in (x0, x1) or y - 1 not in rows or y + 1 not in rows or not (rows[y - 1][0] <= x <= rows[y - 1][1]) or not (rows[y + 1][0] <= x <= rows[y + 1][1]):
                        self.put(x, y, edge)
    def crop(self):
        return self.im.crop(self.im.getbbox())

def body(cv):
    """把包子身子从国王身上抠下来画到 cv 上。"""
    k = Image.open(KING).convert("RGBA"); kp = k.load()
    def body_px(x, y):
        if not (0 <= x < k.width and 0 <= y < k.height): return None
        c = kp[x, y]
        if not is_gray(c): return None
        if 18 <= y <= 42 and 25 <= x <= 73: return c
        if 43 <= y <= 45 and 30 <= x <= 68: return c          # 底边的阴影（左边是剑，不要）
        if 46 <= y <= 57 and 38 <= x <= 60: return c          # 腿和脚
        return None
    for y in range(18, 58):
        for x in range(25, 74):
            c = body_px(x, y)
            if c is None and x > 49:                           # 右边被盾牌挡住的：照左边镜像
                m = body_px(CX - x, y)
                if m is not None: c = EDGE_R if m == EDGE_L else m
            if c is not None: cv.put(x, y, c)
    # 左手臂盖住的那段边
    for (x, y, c) in [(25, 33, EDGE_L), (25, 34, EDGE_L), (25, 35, EDGE_L), (26, 35, WHITE2), (25, 36, EDGE_R), (26, 36, WHITE2), (25, 37, EDGE_R), (26, 37, WHITE2)]:
        cv.put(x, y, c)
    for (x, y, c) in [(CX - 25, 33, EDGE_R), (CX - 25, 34, EDGE_R), (CX - 25, 35, EDGE_R), (CX - 26, 35, WHITE2), (CX - 25, 36, EDGE_R), (CX - 26, 36, WHITE2), (CX - 25, 37, EDGE_R), (CX - 26, 37, WHITE2)]:
        cv.put(x, y, c)
    # 王冠盖住的顶：按每行的半宽补成圆顶
    half = {19: 15.5, 18: 13.5, 17: 12, 16: 10.5, 15: 9, 14: 7.5, 13: 5.5, 12: 3}
    for y, h in half.items():
        x0, x1 = int(round(48.5 - h)), int(round(48.5 + h))
        for x in range(x0, x1 + 1):
            if cv.get(x, y)[3] == 0 or y == 18 and 40 <= x <= 57:
                cv.put(x, y, EDGE_L if x == x0 else EDGE_R if x == x1 else WHITE)
    # 褶子：从顶上的小揪往下放射，接上他画的那三条（亮边在左、暗缝在右）
    def pleat(pts):
        for (x, y) in pts: cv.put(x - 1, y, PLEAT_L); cv.put(x, y, PLEAT_D)
    pleat([(44, 18), (45, 17), (46, 16), (47, 15), (47, 14), (48, 13)])                 # 左边那条往上接
    pleat([(50, 18), (49, 17), (49, 16), (49, 15), (49, 14)])                           # 中间那条
    pleat([(55, 18), (54, 17), (53, 16), (52, 15), (51, 14), (50, 13)])                 # 右边那条
    pleat([(46, 13), (45, 14), (44, 14), (43, 15), (42, 15), (41, 16), (40, 17), (39, 17), (38, 18), (37, 19)])   # 再加两条短的
    pleat([(51, 13), (52, 14), (53, 14), (54, 15), (55, 15), (56, 16), (57, 17), (58, 17), (59, 18), (60, 19)])
    for (x, y, c) in [(48, 11, PLEAT_L), (49, 11, PLEAT_L), (47, 12, PLEAT_L), (48, 12, WHITE), (49, 12, WHITE), (50, 12, PLEAT_D), (47, 13, PLEAT_L), (48, 13, PLEAT_D), (49, 13, PLEAT_D)]:
        cv.put(x, y, c)   # 小揪

def face(cv, kind):
    """表情。眼睛在 x 42~43 和 52~53、y 32~36，眉毛 y 28~29，嘴 y 40 x 46~49。"""
    for y in list(range(27, 31)) + list(range(32, 37)) + list(range(38, 43)):
        for x in range(39, 57): cv.put(x, y, WHITE)
    def eye(ex, top=32):
        for y in range(top, 37):
            cv.put(ex, y, EYE_HI if y <= 33 else INK if y == 34 else INK2); cv.put(ex + 1, y, INK)
    def brow(ex, y=28): cv.put(ex, y, INK); cv.put(ex + 1, y, INK); cv.put(ex - 1, y + 1, INK); cv.put(ex + 2, y + 1, INK)
    def smile(y=39):  # 弯嘴
        for (x, dy) in [(45, 0), (46, 1), (47, 2), (48, 2), (49, 1), (50, 0)]: cv.put(x, y + dy, INK)
    if kind == "normal":
        eye(42); eye(52); brow(42); brow(52); cv.hline(46, 49, 40, INK)
    elif kind == "happy":      # 笑眯眯 ^ ^，嘴弯着
        for ex in (42, 52):
            for (x, dy) in [(-2, 2), (-1, 1), (0, 0), (1, 0), (2, 1), (3, 2)]: cv.put(ex + x, 33 + dy, INK)
        brow(42); brow(52); smile(38)
    elif kind == "shout":      # 眼睛睁大、眉毛挑高，嘴张成 o
        eye(42, 31); eye(52, 31); brow(42, 27); brow(52, 27)
        for (x, y) in [(47, 38), (48, 38), (46, 39), (49, 39), (46, 40), (49, 40), (47, 41), (48, 41)]: cv.put(x, y, INK)
        cv.rect(47, 39, 48, 40, RED2)
    elif kind == "wink":       # 左眼眨着，右眼睁着，嘴歪着笑
        for (x, dy) in [(40, 0), (41, 1), (42, 1), (43, 1), (44, 1), (45, 0)]: cv.put(x, 34 + dy, INK)
        cv.hline(41, 44, 29, INK)
        eye(52); brow(52)
        for (x, dy) in [(46, 0), (47, 0), (48, 0), (49, 0), (50, -1), (51, -2)]: cv.put(x, 40 + dy, INK)
    elif kind == "focus":      # 眉毛压平压低，眼睛半睁，嘴一条线
        eye(42, 34); eye(52, 34); cv.hline(41, 44, 30, INK); cv.hline(51, 54, 30, INK); cv.hline(46, 49, 40, INK)

def arm(cv, side, x1, y1):
    """从身子边上（y 33）伸出来的棕色小手臂，两像素宽，伸到 (x1, y1)。"""
    x0 = 25 if side == "l" else 72
    cv.line(x0, 33, x1, y1, ARM, w=2)
    cv.line(x0 + (1 if side == "l" else -1), 33, x1 + (1 if side == "l" else -1), y1, ARM2)

def waiter():
    cv = Canvas((34, 6, 36, 10)); body(cv); face(cv, "happy")
    # 红头带，右边打结飘两根带子
    for y in (22, 23, 24):
        for x in range(25, 74):
            if cv.get(x, y)[3] and cv.get(x, y) not in (ARM, ARM2): cv.put(x, y, RED if y < 24 else RED2)
    cv.rect(69, 21, 71, 25, RED2); cv.rect(70, 22, 70, 24, RED)
    cv.line(72, 22, 78, 18, RED, w=2); cv.line(72, 24, 79, 26, RED2, w=2); cv.put(79, 17, RED); cv.put(80, 27, RED2)
    # 围裙：从嘴下面挂到腿上，中间一个口袋
    for y in range(42, 52):
        s = (y - 42) // 3
        cv.hline(33 + s, 64 - s, y, SLATE)
    cv.hline(33, 64, 42, SLATE3); cv.hline(36, 61, 51, DARK)
    cv.rect(44, 45, 53, 48, SLATE2); cv.hline(44, 53, 45, DARK)
    # 右手端着蒸笼
    arm(cv, "r", 75, 39)
    sx, sy = 74, 37     # 蒸笼左上角
    cv.rect(sx, sy + 1, sx + 19, sy + 7, BAMBOO); cv.hline(sx - 1, sx + 20, sy, BAMBOO3); cv.hline(sx - 1, sx + 20, sy + 1, BAMBOO2)
    cv.hline(sx, sx + 19, sy + 7, BAMBOO3); cv.hline(sx, sx + 19, sy + 6, BAMBOO2)
    for x in range(sx + 3, sx + 19, 4): cv.vline(x, sy + 2, sy + 5, BAMBOO2)
    for bx in (sx + 4, sx + 10, sx + 16):      # 笼里冒头的三个小包子
        cv.ellipse(bx, sy - 2, 3, 2.6, WHITE, edge=EDGE_R); cv.put(bx, sy - 4, PLEAT_D)
    for (x, y) in [(sx + 3, sy - 8), (sx + 4, sy - 9), (sx + 10, sy - 9), (sx + 11, sy - 11), (sx + 17, sy - 8), (sx + 16, sy - 10)]: cv.put(x, y, STEAM)
    return cv.crop()

def chef():
    cv = Canvas((30, 26, 34, 10)); body(cv); face(cv, "shout")
    # 高帽：帽箍压在包子顶上，上面直筒，顶上三团蓬起来
    cv.rect(36, 10, 61, 15, rgb("#f5f5f5")); cv.hline(36, 61, 15, EDGE_R); cv.hline(36, 61, 10, EDGE_R)
    for x in range(40, 60, 6): cv.vline(x, 11, 14, rgb("#dcdcdc"))
    cv.rect(37, -2, 60, 9, WHITE); cv.vline(60, -2, 9, EDGE_R); cv.vline(37, -2, 9, EDGE_L)
    for x in range(42, 58, 7): cv.vline(x, -1, 8, rgb("#e0e0e0"))
    cv.ellipse(42, -6, 7, 5.5, WHITE); cv.ellipse(56, -6, 7, 5.5, WHITE); cv.ellipse(49, -9, 8, 6, WHITE)
    cv.ellipse(49, -9, 8, 6, WHITE, edge=None)
    for (x, y) in [(63, -6), (63, -5), (62, -3), (62, -2), (61, -1)]: cv.put(x, y, EDGE_R)   # 右边的影子
    for (x, y) in [(55, -14), (56, -13), (57, -12), (50, -15), (51, -15), (52, -14)]: cv.put(x, y, EDGE_R)
    # 脖子上的红领巾
    for (y, x0, x1) in [(43, 43, 54), (44, 44, 53), (45, 45, 52), (46, 46, 51), (47, 47, 50), (48, 48, 49)]: cv.hline(x0, x1, y, RED if y < 46 else RED2)
    # 右手拄着擀面杖：斜着的木棍，两头细一点
    arm(cv, "r", 76, 40)
    cv.line(75, 46, 91, 19, WOOD, w=2); cv.line(76, 46, 92, 19, WOOD, w=2); cv.line(77, 46, 93, 19, BROWN)
    cv.line(75, 45, 91, 18, rgb("#a1887f"))
    cv.rect(73, 46, 75, 48, BROWN); cv.rect(92, 15, 94, 17, BROWN); cv.put(93, 16, WOOD); cv.put(74, 47, WOOD)
    return cv.crop()

def artist():
    cv = Canvas((40, 12, 36, 10)); body(cv); face(cv, "wink")
    # 贝雷帽，歪在右上
    cv.ellipse(52, 13, 16, 5.2, RED, edge=RED2); cv.ellipse(52, 11.6, 14, 4.2, RED)
    cv.hline(37, 67, 16, RED2); cv.hline(39, 66, 17, RED2); cv.vline(53, 5, 6, RED2)
    # 脸上蹭的一块蓝颜料
    for (x, y) in [(38, 37), (39, 37), (38, 38), (37, 38)]: cv.put(x, y, BLUE)
    # 左手的调色板
    arm(cv, "l", 21, 38)
    cv.ellipse(13, 42, 11, 6.5, BROWN, edge=BROWN2); cv.ellipse(12, 41, 10, 5.5, BROWN); cv.rect(19, 44, 20, 45, BROWN2)
    for (x, y, c) in [(6, 40, RED), (10, 38, AMBER), (14, 38, BLUE), (7, 44, GREEN), (12, 44, WHITE), (16, 42, rgb("#8e24aa"))]: cv.rect(x, y, x + 1, y + 1, c)
    # 右手的画笔，笔尖蘸着蓝色
    arm(cv, "r", 75, 41)
    cv.line(76, 44, 83, 28, WOOD, w=2); cv.line(77, 44, 84, 28, BROWN2)
    cv.line(84, 27, 86, 23, GRAY, w=2); cv.line(86, 22, 88, 18, BLUE, w=2); cv.put(88, 17, BLUE)
    return cv.crop()

def coder():
    cv = Canvas((30, 14, 30, 10))
    body(cv); face(cv, "focus")
    # 耳机的梁：贴着包子的边往外三像素，从左边罩绕过顶到右边罩
    for y in range(12, 30):
        xl = next(x for x in range(20, 60) if cv.get(x, y)[3])
        for d in (2, 3): cv.put(xl - d, y, DARK); cv.put(CX - xl + d, y, DARK)
    for (y, x0, x1) in [(11, 44, 53), (10, 45, 52), (9, 46, 51), (8, 47, 50)]: cv.hline(x0, x1, y, DARK)
    for (x, y) in [(43, 12), (54, 12), (44, 11), (53, 11)]: cv.put(x, y, DARK)
    # 耳机罩
    for x in (21, 72):
        cv.rect(x, 29, x + 5, 38, SLATE); cv.rect(x + 1, 30, x + 4, 37, DARK); cv.put(x, 29, (0, 0, 0, 0)); cv.put(x + 5, 29, (0, 0, 0, 0)); cv.put(x, 38, (0, 0, 0, 0)); cv.put(x + 5, 38, (0, 0, 0, 0))
    # 圆眼镜：镜片套着眼睛，镜腿搭到耳机上
    for ex in (42.5, 52.5):
        cv.ellipse(ex, 34, 4.5, 4.5, (0, 0, 0, 0), edge=DARK)
        for y in range(30, 39):
            for x in range(int(ex - 3), int(ex + 4)):
                c = cv.get(x, y)
                if c == (0, 0, 0, 0): cv.put(x, y, WHITE)
    face_eyes = None
    cv.hline(47, 48, 33, DARK); cv.hline(27, 38, 33, DARK); cv.hline(57, 71, 33, DARK)
    # 眼睛被镜片擦掉的补回来
    for ex in (42, 52):
        for y in range(34, 37): cv.put(ex, y, INK if y == 34 else INK2); cv.put(ex + 1, y, INK)
    cv.hline(41, 44, 30, INK); cv.hline(51, 54, 30, INK)
    # 抱着的笔记本，屏幕朝外
    arm(cv, "l", 31, 42); arm(cv, "r", 66, 42)
    cv.rect(33, 41, 64, 52, STEEL); cv.rect(35, 43, 62, 50, INK); cv.hline(33, 64, 52, GRAY3); cv.rect(31, 53, 66, 54, GRAY3); cv.hline(31, 66, 54, STEEL)
    for (x, y) in [(37, 45), (38, 46), (37, 47)]: cv.put(x, y, AMBER)
    cv.hline(41, 50, 46, GREEN); cv.hline(37, 47, 49, GRAY3); cv.rect(49, 48, 50, 49, AMBER)
    return cv.crop()

def base():
    cv = Canvas((2, 2, 2, 2)); body(cv); face(cv, "normal"); return cv.crop()

def main():
    outs = {"base": base(), "waiter": waiter(), "chef": chef(), "artist": artist(), "coder": coder()}
    for n, im in outs.items():
        im.save(os.path.join(OUT, n + ".png")); print(n, im.size)

if __name__ == "__main__":
    main()
