"""The hero banner: a little Moroccan dev room in Rabat, rendered as pixel art.

The window shows the live weather (day or night), the monitor scrolls the
latest commits, the shelf holds one book per language, and the lantern casts
star-shaped light on the walls after dark.
"""

import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from canvas import Canvas, luminance, mix, scale
from fonts import FONT, TINY

W, H = 320, 180
FRAMES = 96
DELAY = 90

# --- palette ---------------------------------------------------------------
INK = (24, 22, 34)
WALL = (46, 50, 108)
WALL_D = (40, 44, 96)
WALL_L = (53, 58, 120)
SAND = (214, 186, 140)
SAND_D = (168, 138, 98)
SAND_L = (238, 216, 176)
WOOD = (128, 80, 46)
WOOD_D = (92, 56, 32)
WOOD_L = (166, 108, 62)
WOOD_H = (190, 132, 78)
TERRA = (152, 72, 46)
TERRA_L = (166, 82, 52)
TERRA_D = (138, 64, 42)
GROUT = (96, 44, 30)
BRASS = (190, 138, 58)
BRASS_D = (110, 72, 30)
BRASS_H = (238, 196, 108)
STEEL = (34, 36, 46)
STEEL_L = (62, 66, 80)
SCREEN = (11, 15, 22)
GREEN = (126, 231, 135)
YELLOW = (232, 194, 92)

ZELLIGE = {
    "y": (214, 160, 52),
    ".": (232, 226, 206),
    "t": (28, 128, 124),
    "b": (40, 76, 158),
}
ZELLIGE_TILE = [
    "y..tt..y",
    "..tbbt..",
    ".tb..bt.",
    "tb.yy.bt",
    "tb.yy.bt",
    ".tb..bt.",
    "..tbbt..",
    "y..tt..y",
]

LANTERN = [
    "......h......",
    ".....obo.....",
    "......o......",
    ".....obo.....",
    "....obhbo....",
    "...obahabo...",
    "..obabhbabo..",
    ".ooooooooooo.",
    ".obhbhbhbhbo.",
    ".ooooooooooo.",
    "..obbbbbbbo..",
    "..oabrrrbao..",
    "..oabrfrbao..",
    "..oabffFbao..",
    "..oabfFFbao..",
    "..oabrffbao..",
    "..oabrrrbao..",
    "..obbbbbbbo..",
    ".ooooooooooo.",
    ".obhbhbhbhbo.",
    ".ooooooooooo.",
    "...obbbbbo...",
    "....obabo....",
    ".....obo.....",
    "......h......",
]

TEAPOT = [
    "........o........",
    ".......oHo.......",
    "........o........",
    "......oSHSo......",
    ".....oSHSSDo....o",
    "....oggggggo...oo",
    ".ooooSHSSSSDo.oSo",
    "o...oSHSSSSSDoSDo",
    "o..oSHSSSSSSSDSo.",
    ".o.oSHSSSSSSSDo..",
    "..ooSSSSSSSSSDo..",
    "....oSSSSSSSDo...",
    ".....oDDDDDDo....",
    "....oSSSSSSSSo...",
    "....ooooooooo....",
]

TEA_GLASS = [
    "..mm..",
    ".mmmm.",
    "otTTto",
    "ogtgto",
    "otgtgo",
    "otTtto",
    ".otto.",
    ".oooo.",
]

TROPHY = [
    "..ooooooo..",
    "oohhggggdoo",
    "o.ohgggdo.o",
    "o.ohgggdo.o",
    ".oohgggdoo.",
    "...ohgdo...",
    "....odo....",
    "....ogo....",
    "...ohgdo...",
    "..ooooooo..",
    "..obbbbbo..",
    "..ooooooo..",
]

DUCK = [
    "..oooo.....",
    ".oyYYyo....",
    ".oykyyo....",
    "qqoyyyo..o.",
    ".qoyyyyooyo",
    ".oyyYYyyyyo",
    ".oyyyyyyyyo",
    "..oddddddo.",
    "...oooooo..",
]

CAT_EAR = [
    "..o..",
    ".ogo.",
    "ogpgo",
    "ggggg",
]

CAT_TAIL = [
    [
        "......oo",
        ".....olo",
        ".....ogo",
        "....ogo.",
        "..oogo..",
        "ogggo...",
        "oooo....",
    ],
    [
        "........",
        "........",
        ".....ooo",
        "....oglo",
        "..oogoo.",
        "ogggo...",
        "oooo....",
    ],
    [
        "........",
        "........",
        "........",
        "......oo",
        "...ooolo",
        "ogggggo.",
        "oooooo..",
    ],
]

CLOUDS = [
    [
        "......WWW.......",
        "...WWWWWWWW.WW..",
        ".WWWWWWWWWWWWWW.",
        "WWWWWWWWWWWWWWWW",
        "SSSSSSSSSSSSSSSS",
        ".SSSSSSSSSSSSSS.",
    ],
    [
        "...WWW.....",
        ".WWWWWWW.W.",
        "WWWWWWWWWWW",
        "SSSSSSSSSSS",
        ".SSSSSSSSS.",
    ],
    [
        ".......WWWW...........",
        "....WWWWWWWWW..WWW....",
        "..WWWWWWWWWWWWWWWWWW..",
        ".WWWWWWWWWWWWWWWWWWWW.",
        "WWWWWWWWWWWWWWWWWWWWWW",
        "SSSSSSSSSSSSSSSSSSSSSS",
        "..SSSSSSSSSSSSSSSSSS..",
    ],
]

# Window opening (horseshoe arch) -------------------------------------------
WIN_CX, WIN_CY, WIN_R = 54, 48, 32
WIN_X, WIN_Y, WIN_W, WIN_H = 22, 16, 65, 81
WIN_SPRING = 56  # where the arch meets the straight jambs


def in_arch(x, y, grow=0):
    if y > WIN_Y + WIN_H - 1 + grow:
        return False
    if y <= WIN_SPRING:
        return (x - WIN_CX) ** 2 + (y - WIN_CY) ** 2 <= (WIN_R + grow + 0.4) ** 2
    return WIN_CX - WIN_R + 3 - grow <= x <= WIN_CX + WIN_R - 3 + grow


def arch_mask(grow):
    m = Image.new("L", (W, H), 0)
    px = m.load()
    for y in range(H):
        for x in range(W):
            if in_arch(x, y, grow):
                px[x, y] = 255
    return m


# Light sources (used for night lighting) ------------------------------------
LANTERN_X, LANTERN_Y = 102, 18
LANTERN_C = (108, 32)
MONITOR = (124, 46, 109, 55)  # bezel x, y, w, h
SCREEN_BOX = (127, 49, 103, 49)
BEAM = [(25, 101), (84, 101), (150, 179), (64, 179)]
MOON_POOL = [(46, 142), (99, 142), (150, 179), (64, 179)]


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * (t / period + phase))


class Room:
    def __init__(self, ctx):
        self.ctx = ctx
        w = ctx["weather"]
        self.kind = w.get("kind", "clear")
        self.day = bool(w.get("day", True))
        self.rng = random.Random(7)
        self.opening = arch_mask(0)
        self.static = self._draw_static()
        self.lightmaps = {}
        self.beam_mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(self.beam_mask).polygon(BEAM, fill=255)
        self.sunny = self.day and self.kind in ("clear", "clouds")
        self._init_weather()

    # =====================================================================
    # static scenery
    # =====================================================================
    def _draw_static(self):
        c = Canvas(W, H, WALL)
        rng = random.Random(3)

        # wall texture: soft vertical stripes + tadelakt speckles
        for x in range(0, W, 9):
            c.rect(x, 0, 1, 114, WALL_D)
        for _ in range(260):
            c.px(rng.randrange(W), rng.randrange(8, 112), rng.choice((WALL_L, WALL_D)))

        # carved plaster cornice
        c.rect(0, 0, W, 1, INK)
        c.rect(0, 1, W, 5, SAND)
        for x0 in range(0, W, 6):
            c.rect(x0 + 1, 4, 4, 2, SAND_D)
            c.rect(x0 + 2, 3, 2, 1, SAND_D)
            c.px(x0 + 3, 2, SAND_L)
        c.rect(0, 6, W, 1, SAND_D)
        c.rect(0, 7, W, 1, scale(WALL, 0.75))

        # zellige wainscot
        c.rect(0, 113, W, 1, scale(WALL, 0.75))
        c.rect(0, 114, W, 1, SAND_L)
        c.rect(0, 115, W, 1, SAND_D)
        for y in range(116, 140):
            row = ZELLIGE_TILE[(y - 116) % 8]
            for x in range(W):
                c.px(x, y, ZELLIGE[row[x % 8]])
        c.rect(0, 140, W, 1, SAND_D)
        c.rect(0, 141, W, 1, INK)

        # terracotta floor
        for y in range(142, H):
            row = (y - 142) // 6
            fy = (y - 142) % 6
            off = 7 if row % 2 else 0
            for x in range(W):
                tile = (x + off) // 14
                if fy == 5 or (x + off) % 14 == 0:
                    col = GROUT
                else:
                    col = (TERRA, TERRA_L, TERRA_D)[(tile * 7 + row * 3) % 3]
                    if fy == 0:
                        col = mix(col, (200, 120, 80), 0.25)
                c.px(x, y, scale(col, 0.82 + 0.18 * min(1, (y - 142) / 30)))

        self._window_frame(c)
        self._plaque(c)
        self._server(c)
        self._shelves(c)
        self._clock(c)
        self._rug(c)
        self._desk(c)
        self._plant(c)
        self._pouf(c)
        return c

    def _window_frame(self, c):
        for grow, col in ((6, SAND_D), (5, SAND), (2, SAND_L), (1, WOOD_D)):
            m = arch_mask(grow)
            c.img.paste(col, (0, 0, W, H), m)
        # carved dots along the arch surround
        for a in range(0, 181, 15):
            r = WIN_R + 4
            x = round(WIN_CX + r * math.cos(math.radians(180 + a)))
            y = round(WIN_CY + r * math.sin(math.radians(180 + a)))
            c.px(x, y, SAND_D)
        for y in range(WIN_SPRING + 6, 97, 6):
            c.px(WIN_CX - WIN_R - 1, y, SAND_D)
            c.px(WIN_CX + WIN_R + 1, y, SAND_D)
        # sill
        c.rect(13, 97, 83, 1, SAND_L)
        c.rect(13, 98, 83, 2, SAND)
        c.rect(14, 100, 81, 1, SAND_D)
        c.rect(15, 101, 79, 1, scale(WALL, 0.7))

    def _plaque(self, c):
        w = self.ctx["weather"]
        label = self.ctx.get("city", "RABAT").upper()
        if w.get("temp") is not None:
            label += f" {round(w['temp'])}°C"
        tw = TINY.width(label)
        bw = max(tw + 8, 30)
        x0 = 54 - bw // 2
        c.line(x0 + 4, 101, x0 + 4, 103, BRASS_D)
        c.line(x0 + bw - 5, 101, x0 + bw - 5, 103, BRASS_D)
        c.rect(x0, 104, bw, 9, INK)
        c.rect(x0 + 1, 105, bw - 2, 7, (52, 64, 58))
        c.text(54 - tw // 2, 106, label, (226, 222, 196), font=TINY)

    def _server(self, c):
        x, y, w, h = 34, 117, 30, 39
        c.rect(x - 1, y - 1, w + 2, h + 2, INK)
        c.rect(x, y, w, h, (48, 52, 64))
        c.rect(x, y, w, 1, (86, 92, 110))
        c.rect(x, y, 1, h, (70, 76, 92))
        for i in range(4):
            by = y + 3 + i * 8
            c.rect(x + 3, by, w - 6, 6, (30, 32, 42))
            c.rect(x + 4, by + 1, w - 8, 1, (60, 64, 78))
            c.rect(x + 4, by + 3, 12, 1, (60, 64, 78))
        c.rect(x + 3, y + h - 4, w - 6, 2, (30, 32, 42))
        c.rect(x - 1, y + h + 1, w + 2, 1, scale(TERRA_D, 0.6))
        # cable to the desk
        pts = [(64, 149), (70, 151), (82, 152), (94, 151), (102, 148), (107, 144)]
        for (a, b), (c2, d2) in zip(pts, pts[1:]):
            c.line(a, b, c2, d2, (30, 30, 36))

    def _shelves(self, c):
        for y in (54, 86):
            c.rect(247, y, 68, 1, WOOD_H)
            c.rect(247, y + 1, 68, 1, WOOD_L)
            c.rect(247, y + 2, 68, 1, WOOD_D)
            c.rect(247, y + 3, 68, 1, scale(WALL, 0.7))
            for bx in (252, 306):
                for i in range(4):
                    c.rect(bx + i // 2, y + 3 + i, 4 - i, 1, BRASS_D)

        # books: one per language, then thinner framework books
        x = 251
        heights = (24, 21, 23, 20, 22, 25)
        for i, (label, col) in enumerate(self.ctx["books"]):
            h = max(heights[i % len(heights)], 6 * len(label) + 5)
            x = self._book(c, x, 53, 8, h, col, label) + 1
            if x > 300:
                break
        for i, col in enumerate(self.ctx.get("extra_books", [])):
            if x > 302:
                break
            h = (19, 17, 20)[i % 3]
            x = self._book(c, x, 53, 5, h, col, "") + 1
        if x < 304:
            # a leaning book and a bookend
            c.polygon([(x, 53), (x + 4, 53), (x + 12, 37), (x + 8, 35)], INK)
            c.polygon([(x + 1, 53), (x + 4, 53), (x + 11, 38), (x + 8, 36)], (154, 64, 74))
            c.line(x + 3, 51, x + 9, 39, (196, 120, 110))

        # shelf two: snake plant, trophy, rubber duck, flag
        self._snake_plant(c, 252, 85)
        c.sprite(266, 74, TROPHY, {"o": (90, 60, 20), "h": (255, 228, 136), "g": (232, 184, 64),
                                   "d": (172, 122, 38), "b": WOOD})
        c.sprite(281, 77, DUCK, {"o": (110, 76, 20), "y": (250, 212, 60), "Y": (255, 238, 150),
                                 "d": (210, 158, 40), "k": INK, "q": (240, 128, 40)})
        self._flag(c, 297, 85)

    def _book(self, c, x, base, w, h, col, label):
        top = base - h + 1
        dark = scale(col, 0.7)
        c.rect(x, top, w, h, INK)
        c.rect(x + 1, top + 1, w - 2, h - 1, col)
        c.rect(x + w - 2, top + 1, 1, h - 1, dark)
        c.rect(x + 1, top + 2, w - 3, 1, mix(col, (255, 255, 255), 0.35))
        c.rect(x + 1, base - 2, w - 3, 1, mix(col, (255, 255, 255), 0.35))
        if label:
            ink = (250, 250, 250) if luminance(col) < 150 else INK
            letters = [ch for ch in TINY.normalize(label) if ch.strip()][: max(0, (h - 5) // 6)]
            for j, ch in enumerate(letters):
                gw = TINY.width(ch)
                c.text(x + (w - 1 - gw) // 2, top + 4 + j * 6, ch, ink, font=TINY)
        return x + w

    def _snake_plant(self, c, x, base):
        g, gd, edge = (58, 128, 70), (40, 92, 52), (196, 196, 90)
        leaves = [(x + 2, 16, -1), (x + 4, 20, 0), (x + 6, 14, 1), (x + 5, 11, 2)]
        for lx, lh, lean in leaves:
            for i in range(lh):
                yy = base - 6 - i
                xx = lx + round(lean * i / lh)
                c.px(xx, yy, g if i % 3 else gd)
                if i > 2 and i < lh - 1:
                    c.px(xx + 1, yy, gd)
                if i == lh - 1:
                    c.px(xx, yy, edge)
        c.rect(x, base - 5, 10, 6, INK)
        c.rect(x + 1, base - 5, 8, 5, (178, 94, 58))
        c.rect(x + 1, base - 5, 8, 1, (206, 120, 76))
        c.rect(x + 2, base - 3, 6, 1, (40, 80, 160))

    def _flag(self, c, x, base):
        c.rect(x, base - 15, 1, 15, WOOD_D)
        c.px(x, base - 16, BRASS_H)
        c.rect(x - 2, base - 1, 5, 1, WOOD)
        fx, fy = x + 1, base - 15
        c.rect(fx, fy, 12, 8, (193, 39, 45))
        c.rect(fx, fy + 7, 12, 1, (150, 28, 34))
        # tiny green pentagram
        star = ["..#..", "#####", ".#.#.", "#...#"]
        for j, row in enumerate(star):
            for i, ch in enumerate(row):
                if ch == "#":
                    c.px(fx + 4 + i, fy + 2 + j, (0, 122, 51))

    def _clock(self, c):
        cx, cy = 296, 18
        hh, mm = self.ctx.get("clock", (10, 10))
        c.ellipse(cx - 10, cy - 10, 21, 21, INK)
        c.ellipse(cx - 9, cy - 9, 19, 19, BRASS)
        c.ellipse(cx - 8, cy - 8, 17, 17, BRASS_D)
        c.ellipse(cx - 7, cy - 7, 15, 15, (240, 230, 204))
        for a in range(0, 360, 30):
            r = 6 if a % 90 else 5
            x = round(cx + 6 * math.sin(math.radians(a)))
            y = round(cy - 6 * math.cos(math.radians(a)))
            c.px(x, y, (120, 100, 80) if a % 90 else INK)
        ma = math.radians(mm * 6)
        ha = math.radians((hh % 12) * 30 + mm * 0.5)
        c.line(cx, cy, round(cx + 5 * math.sin(ma)), round(cy - 5 * math.cos(ma)), INK)
        c.line(cx, cy, round(cx + 3.4 * math.sin(ha)), round(cy - 3.4 * math.cos(ha)), (176, 40, 40))
        c.px(cx, cy, BRASS_H)
        c.px(cx - 4, cy - 7, (255, 255, 255))

    def _rug(self, c):
        x0, y0, w, h = 96, 154, 194, 21
        cream, cream_d, line, red = (226, 212, 182), (206, 190, 158), (62, 50, 46), (170, 54, 50)
        c.rect(x0, y0 + h, w, 1, scale(GROUT, 0.8))
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                lx, ly = x - x0, y - y0
                col = cream if (lx * 3 + ly * 7) % 11 else cream_d
                if lx < 2 or lx >= w - 2 or ly < 1 or ly >= h - 1:
                    col = red
                elif (lx + ly * 2) % 18 == 0 or (lx - ly * 2) % 18 == 0:
                    col = line
                elif (lx + ly * 2) % 18 == 9 and (lx - ly * 2) % 18 == 9:
                    col = red
                c.px(x, y, col)
        for y in range(y0 + 1, y0 + h - 1, 2):
            c.rect(x0 - 2, y, 2, 1, cream_d)
            c.rect(x0 + w, y, 2, 1, cream_d)

    def _desk(self, c):
        x0, x1 = 104, 242
        # shadow on the zellige under the desk
        region = c.img.crop((112, 119, 235, 141))
        c.img.paste(ImageChops.multiply(region, Image.new("RGB", region.size, (150, 150, 170))), (112, 119))
        for lx in (108, 235):
            c.rect(lx - 1, 118, 6, 38, INK)
            c.rect(lx, 118, 4, 37, WOOD_D)
            c.rect(lx, 118, 1, 37, WOOD)
        c.rect(x0 - 1, 107, x1 - x0 + 3, 13, INK)
        c.rect(x0, 108, x1 - x0 + 1, 4, WOOD_L)
        c.rect(x0, 108, x1 - x0 + 1, 1, WOOD_H)
        c.rect(x0, 112, x1 - x0 + 1, 7, WOOD)
        c.rect(x0, 118, x1 - x0 + 1, 1, WOOD_D)
        for ax in range(x0 + 6, x1 - 4, 10):  # carved arches on the apron
            c.rect(ax, 114, 4, 3, WOOD_D)
            c.rect(ax + 1, 113, 2, 1, WOOD_D)
        c.rect(174, 114, 4, 2, BRASS_H)

        # monitor
        bx, by, bw, bh = MONITOR
        c.rect(166, 105, 24, 3, INK)
        c.rect(167, 105, 22, 2, STEEL_L)
        c.rect(173, 99, 10, 7, INK)
        c.rect(174, 99, 8, 6, STEEL)
        c.rect(bx - 1, by - 1, bw + 2, bh + 2, INK)
        c.rect(bx, by, bw, bh, STEEL)
        c.rect(bx, by, bw, 1, STEEL_L)
        c.rect(bx, by, 1, bh, STEEL_L)
        c.px(bx + bw // 2, by + bh - 2, (90, 200, 120))

        # keyboard + mouse
        c.rect(145, 108, 46, 4, INK)
        c.rect(146, 109, 44, 2, (58, 60, 72))
        for kx in range(147, 189, 2):
            c.px(kx, 109, (104, 108, 124))
        c.rect(196, 109, 5, 3, INK)
        c.rect(197, 109, 3, 2, (92, 96, 110))

        # mint tea: silver teapot + glass
        c.sprite(105, 93, TEAPOT, {"o": (58, 60, 78), "S": (196, 202, 216), "H": (244, 246, 252),
                                   "D": (128, 134, 154), "g": (214, 170, 70)})
        c.sprite(235, 100, TEA_GLASS, {"o": (196, 226, 218), "t": (190, 124, 40), "T": (226, 164, 66),
                                       "g": (230, 186, 74), "m": (70, 170, 84)})

    def _plant(self, c):
        # prickly-pear cactus in a painted pot, right corner
        green, dark, light = (78, 152, 84), (36, 84, 50), (124, 190, 112)
        for (x, y, w, h) in ((298, 112, 12, 22), (292, 102, 10, 16), (305, 100, 10, 16), (300, 92, 8, 12)):
            c.ellipse(x - 1, y - 1, w + 2, h + 2, dark)
            c.ellipse(x, y, w, h, green)
            c.ellipse(x + 2, y + 2, max(2, w // 3), max(2, h // 2), light)
            for sx, sy in ((x + 3, y + 4), (x + w - 3, y + h // 2), (x + w // 2, y + h - 4)):
                c.px(sx, sy, (226, 236, 200))
        for fx, fy in ((294, 101), (300, 91), (306, 91), (311, 99)):
            c.rect(fx, fy, 3, 2, (212, 62, 96))
            c.px(fx + 1, fy - 1, (240, 120, 140))
        c.rect(293, 131, 22, 25, INK)
        c.rect(294, 131, 20, 3, (206, 120, 76))
        c.rect(295, 134, 18, 21, (178, 94, 58))
        c.rect(295, 140, 18, 5, (232, 226, 206))
        for i in range(0, 18, 4):
            c.px(295 + i, 141, (40, 80, 160))
            c.px(296 + i, 142, (40, 80, 160))
            c.px(297 + i, 143, (40, 80, 160))
            c.px(298 + i, 142, (40, 80, 160))
        c.rect(296, 155, 16, 1, INK)

    def _pouf(self, c):
        x, y, w = 158, 144, 38
        leather, leather_d, leather_l = (180, 98, 48), (132, 66, 30), (208, 128, 66)
        c.ellipse(x - 1, y + 10, w + 2, 11, INK)
        c.rect(x - 1, y + 4, w + 2, 12, INK)
        c.ellipse(x - 1, y - 1, w + 2, 11, INK)
        c.ellipse(x, y + 11, w, 9, leather_d)
        c.rect(x, y + 4, w, 12, leather)
        c.rect(x + w - 6, y + 4, 6, 12, leather_d)
        c.ellipse(x, y, w, 9, leather_l)
        c.ellipse(x + 13, y + 2, 12, 5, leather)
        for i in range(0, w - 2, 4):
            c.px(x + 1 + i, y + 10 + (i // 4) % 2, (240, 200, 104))
        c.px(x + 19, y + 4, (240, 200, 104))

    # =====================================================================
    # weather setup
    # =====================================================================
    def _init_weather(self):
        rng = random.Random(11)
        self.stars = [(rng.randrange(2, WIN_W - 2), rng.randrange(2, 46), rng.randrange(24), rng.random() < 0.2)
                      for _ in range(22)]
        self.drops = [(rng.randrange(0, 80), rng.randrange(0, 96)) for _ in range(46)]
        self.glass_drops = [(rng.randrange(3, WIN_W - 3), rng.randrange(0, 96)) for _ in range(5)]
        self.flakes = [(rng.randrange(0, WIN_W), rng.randrange(0, 96), rng.random()) for _ in range(34)]
        self.motes = [(rng.random(), rng.random(), rng.random()) for _ in range(9)]
        self.windows_lit = [rng.random() < 0.6 for _ in range(16)]

    # =====================================================================
    # per-frame drawing
    # =====================================================================
    def frame(self, t):
        c = self.static.copy()
        self._window(c, t)
        self._monitor(c, t)
        self._server_leds(c, t)
        self._lantern(c, t)
        self._neon(c, t)
        self._steam(c, t)
        self._cat(c, t)
        return self._light(c, t)

    # --- window ------------------------------------------------------------
    def _sky_colors(self):
        k, d = self.kind, self.day
        if d:
            return {
                "clear": [(66, 136, 222), (96, 162, 234), (140, 192, 240), (178, 214, 242)],
                "clouds": [(70, 138, 220), (100, 164, 232), (142, 192, 238), (176, 210, 238)],
                "overcast": [(116, 128, 148), (132, 142, 160), (150, 158, 174), (168, 174, 186)],
                "rain": [(84, 94, 114), (98, 108, 126), (112, 122, 140), (128, 136, 152)],
                "storm": [(52, 56, 76), (64, 68, 88), (78, 82, 102), (92, 96, 114)],
                "fog": [(160, 166, 176), (174, 180, 188), (188, 192, 198), (200, 204, 208)],
                "snow": [(146, 156, 176), (162, 172, 190), (180, 188, 202), (198, 204, 214)],
            }[k]
        return {
            "clear": [(8, 12, 34), (14, 20, 50), (24, 32, 72), (40, 48, 96)],
            "clouds": [(10, 14, 36), (16, 22, 52), (26, 34, 72), (40, 48, 92)],
            "overcast": [(26, 28, 40), (32, 34, 48), (40, 42, 58), (48, 50, 66)],
            "rain": [(18, 20, 30), (24, 26, 38), (32, 34, 48), (40, 42, 56)],
            "storm": [(14, 14, 24), (20, 20, 32), (28, 28, 42), (36, 36, 52)],
            "fog": [(40, 44, 56), (48, 52, 64), (56, 60, 72), (64, 68, 80)],
            "snow": [(32, 36, 54), (40, 44, 64), (50, 54, 74), (60, 66, 86)],
        }[k]

    def _tone(self, col):
        """Recolour a daylight colour for the current weather and time of day."""
        if self.day:
            if self.kind in ("overcast", "rain", "fog", "snow"):
                return mix(col, (138, 144, 158), 0.35)
            if self.kind == "storm":
                return mix(scale(col, 0.7), (70, 74, 92), 0.4)
            return col
        return mix(scale(col, 0.3), (16, 20, 46), 0.3)

    def _window(self, c, t):
        s = Canvas(WIN_W, WIN_H)
        bands = self._sky_colors()
        flash = self.kind == "storm" and t in (40, 41, 44)
        for y in range(WIN_H):
            f = min(1.0, y / 58) * (len(bands) - 1)
            i = int(f)
            frac = f - i
            for x in range(WIN_W):
                j = i + (1 if frac > 0.5 + (0.2 if (x + y) % 2 else -0.2) and i + 1 < len(bands) else 0)
                s.img.putpixel((x, y), bands[j])
        if flash:
            s.rect(0, 0, WIN_W, WIN_H, (196, 204, 230) if t != 44 else (150, 158, 190))

        # celestial bodies
        if not self.day and self.kind in ("clear", "clouds"):
            for (sx, sy, ph, big) in self.stars:
                tw = (t + ph * 4) % 24
                bright = tw < 18
                col = (255, 250, 220) if bright else (120, 124, 160)
                s.px(sx, sy, col)
                if big and bright:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        s.px(sx + dx, sy + dy, (120, 124, 170))
            if 58 <= t < 66:  # shooting star
                k = t - 58
                hx, hy = 58 - k * 4, 4 + k * 2
                for i in range(5):
                    s.px(hx + i * 2, hy - i, mix((255, 255, 230), (40, 48, 96), i / 5))
                    s.px(hx + i * 2 + 1, hy - i, mix((255, 255, 230), (40, 48, 96), i / 5))
            # crescent moon
            mx, my = 46, 10
            s.ellipse(mx - 6, my - 6, 13, 13, (38, 44, 86))
            s.ellipse(mx - 5, my - 5, 11, 11, (238, 232, 196))
            s.ellipse(mx - 2, my - 7, 11, 11, bands[0])
        elif self.day and self.kind in ("clear", "clouds"):
            sx, sy = 16, 14
            s.ellipse(sx - 8, sy - 8, 17, 17, mix(bands[0], (255, 236, 160), 0.35))
            s.ellipse(sx - 6, sy - 6, 13, 13, (255, 222, 110))
            s.ellipse(sx - 4, sy - 4, 9, 9, (255, 242, 186))
            for a in range(0, 360, 45):
                r = 9 + (1 if (t // 12 + a // 45) % 2 else 0)
                s.px(round(sx + r * math.cos(math.radians(a))), round(sy + r * math.sin(math.radians(a))),
                     (255, 226, 130))

        # clouds
        self._clouds(s, t)

        # skyline -----------------------------------------------------------
        sea_y = 54
        sea = self._tone((40, 112, 176))
        s.rect(0, sea_y, WIN_W, 10, sea)
        for i in range(12):
            hx = (i * 23 + t * (1 if i % 2 else -1) // 2) % (WIN_W + 6) - 3
            hy = sea_y + 1 + (i * 5) % 8
            s.rect(hx, hy, 3, 1, self._tone((150, 202, 236)))
        if not self.day and self.kind in ("clear", "clouds"):
            for yy in range(sea_y, sea_y + 9):
                w = 2 + (yy + t // 3) % 3
                s.rect(46 - w // 2 + ((yy + t // 4) % 3) - 1, yy, w, 1, (190, 196, 220))

        # Mohammed VI tower, far across the river
        tw_col = self._tone((150, 168, 192))
        s.rect(10, 20, 1, 6, tw_col)
        s.rect(9, 26, 3, 6, tw_col)
        s.rect(8, 32, 5, 23, tw_col)
        s.rect(12, 32, 1, 23, self._tone((120, 136, 160)))
        if not self.day:
            for yy in range(28, 54, 3):
                s.px(10, yy, (255, 222, 150))
            if t % 24 < 12:
                s.px(10, 19, (255, 80, 80))

        # Hassan Tower
        body, shade, dark = self._tone((192, 128, 84)), self._tone((160, 102, 66)), self._tone((112, 70, 46))
        if not self.day:
            body, shade, dark = (178, 124, 82), (140, 94, 62), (82, 52, 36)  # floodlit
        tx, ty = 44, 26
        s.rect(tx, ty + 6, 11, 34, body)
        s.rect(tx + 8, ty + 6, 3, 34, shade)
        s.rect(tx + 1, ty + 3, 9, 3, body)
        for i in range(0, 9, 2):
            s.px(tx + 1 + i, ty + 2, body)
        s.rect(tx + 2, ty + 3, 7, 1, shade)
        for ay in (ty + 10, ty + 20):
            s.rect(tx + 2, ay + 1, 2, 4, dark)
            s.px(tx + 2, ay, dark)
            s.rect(tx + 6, ay + 1, 2, 4, dark)
            s.px(tx + 7, ay, dark)
        s.rect(tx + 3, ty + 30, 4, 2, dark)

        # palm
        trunk = self._tone((112, 82, 54))
        for i in range(22):
            s.px(34 + round(math.sin(i / 7) * 1.5), 48 + i, trunk)
            if i % 3 == 0:
                s.px(35 + round(math.sin(i / 7) * 1.5), 48 + i, self._tone((86, 62, 40)))
        frond = self._tone((62, 142, 74))
        frond_d = self._tone((40, 104, 54))
        sway = round(wave(t, 48) * 1)
        for dx, dy, ln in ((-1, 0, 8), (1, 0, 8), (-1, 1, 6), (1, 1, 6), (0, -1, 4)):
            for i in range(ln):
                fx = 35 + dx * i + (sway if i > ln // 2 else 0)
                fy = 47 + dy * i + (i * i) // 12
                s.px(fx, fy, frond if i % 2 else frond_d)
                s.px(fx, fy + 1, frond_d)

        # Kasbah wall + Oudaya houses
        wall_c, wall_s = self._tone((182, 118, 72)), self._tone((150, 94, 58))
        s.rect(0, 62, WIN_W, 19, wall_c)
        s.rect(0, 62, WIN_W, 1, wall_s)
        for x in range(0, WIN_W, 4):
            s.rect(x, 60, 2, 2, wall_c)
        for x in range(0, WIN_W, 7):
            s.rect(x, 66 + (x % 3), 2, 1, wall_s)
        white, blue = self._tone((232, 230, 222)), self._tone((48, 96, 184))
        win_dark = self._tone((40, 48, 70))
        houses = [(0, 66, 12), (11, 69, 10), (20, 64, 11), (30, 70, 9), (52, 68, 13)]
        wi = 0
        for hx, hy, hw in houses:
            s.rect(hx, hy, hw, WIN_H - hy, white)
            s.rect(hx, hy + (WIN_H - hy) // 2, hw, WIN_H, blue)
            s.rect(hx, hy, hw, 1, self._tone((200, 196, 186)))
            for wx in range(hx + 2, hx + hw - 2, 4):
                lit = not self.day and self.windows_lit[wi % len(self.windows_lit)]
                if lit and (t + wi * 13) % 96 < 4 and wi % 5 == 0:
                    lit = False  # someone switching a light
                s.rect(wx, hy + 3, 2, 3, (255, 206, 112) if lit else win_dark)
                wi += 1
            s.rect(hx + hw // 2 - 1, WIN_H - 5, 3, 5, self._tone((64, 100, 170)))

        # gulls over the sea
        if self.day and self.kind in ("clear", "clouds", "overcast"):
            for i, (ph, gy) in enumerate(((0, 30), (40, 38))):
                gx = (t + ph) % 96 - 14
                up = (t // 4 + i) % 2
                gc = (52, 56, 72)
                if up:
                    s.px(gx, gy, gc); s.px(gx + 1, gy + 1, gc); s.px(gx + 2, gy + 1, gc)
                    s.px(gx + 3, gy + 1, gc); s.px(gx + 4, gy, gc)
                else:
                    s.rect(gx, gy + 1, 5, 1, gc); s.px(gx + 2, gy, gc)

        # precipitation
        if self.kind in ("rain", "storm"):
            rc = (176, 190, 214) if self.day else (96, 110, 146)
            for x0, y0 in self.drops:
                yy = (y0 + t * 4) % 96 - 6
                xx = (x0 - yy // 4) % 72 - 2
                s.px(xx, yy, rc)
                s.px(xx, yy + 1, rc)
                s.px(xx - 1, yy + 2, mix(rc, bands[2], 0.5))
            if self.kind == "storm" and t in (40, 41):
                pts = [(30, 0), (26, 10), (32, 16), (24, 30), (30, 34), (22, 50)]
                for (a, b), (c2, d2) in zip(pts, pts[1:]):
                    s.line(a, b, c2, d2, (255, 255, 230))
                    s.line(a + 1, b, c2 + 1, d2, (210, 220, 255))
        elif self.kind == "snow":
            for x0, y0, ph in self.flakes:
                yy = (y0 + t) % 96 - 8
                xx = x0 + round(wave(t, 48, ph) * 1.5)
                s.px(xx, yy, (250, 252, 255))
                if ph > 0.7:
                    s.px(xx + 1, yy, (210, 220, 236))
        elif self.kind == "fog":
            fog = (214, 218, 222) if self.day else (92, 98, 112)
            for y in range(16, WIN_H):
                for x in range(WIN_W):
                    n = ((x + t // 2) % 48 * 7 + y * 13) % 17
                    band = math.sin((y + ((x + t // 2) % 48) / 6) / 5)
                    if band > 0.2 and (x + y) % 2 == 0 and n > 3:
                        s.px(x, y, fog)

        if self.kind in ("rain", "storm"):
            for gx, gy0 in self.glass_drops:
                gy = (gy0 + t) % 96 - 8
                dc = (210, 222, 240) if self.day else (120, 134, 170)
                s.px(gx, gy, dc)
                s.px(gx, gy + 1, dc)
                s.px(gx + 1, gy + 1, mix(dc, (255, 255, 255), 0.3))
                s.px(gx, gy - 2, mix(dc, bands[1], 0.6))

        # glass glare
        for i in range(10):
            s.px(10 + i, 44 - i, mix(s.img.getpixel((10 + i, 44 - i)), (255, 255, 255), 0.2))
            s.px(13 + i, 44 - i, mix(s.img.getpixel((13 + i, 44 - i)), (255, 255, 255), 0.12))

        local = self.opening.crop((WIN_X, WIN_Y, WIN_X + WIN_W, WIN_Y + WIN_H))
        c.img.paste(s.img, (WIN_X, WIN_Y), local)
        c.emit.paste(255, (WIN_X, WIN_Y, WIN_X + WIN_W, WIN_Y + WIN_H), local)

        # muntins (lit by the room, not emissive)
        mc, mh = (88, 56, 34), (124, 84, 52)
        for y in range(WIN_Y, WIN_Y + WIN_H):
            for x in (WIN_CX - 1, WIN_CX):
                if in_arch(x, y):
                    c.img.putpixel((x, y), mh if x == WIN_CX - 1 else mc)
                    c.emit.putpixel((x, y), 0)
        for x in range(WIN_X, WIN_X + WIN_W):
            for y in (WIN_SPRING, WIN_SPRING + 1):
                if in_arch(x, y):
                    c.img.putpixel((x, y), mh if y == WIN_SPRING else mc)
                    c.emit.putpixel((x, y), 0)

    def _clouds(self, s, t):
        k = self.kind
        if k == "clear" and not self.day:
            return
        if self.day:
            cols = {"clear": ((250, 252, 255), (206, 218, 238)), "clouds": ((250, 252, 255), (200, 212, 232)),
                    "overcast": ((188, 194, 206), (152, 160, 174)), "rain": ((132, 140, 156), (106, 114, 130)),
                    "storm": ((98, 102, 120), (74, 78, 96)), "fog": ((214, 218, 222), (190, 194, 200)),
                    "snow": ((214, 220, 230), (184, 192, 206))}[k]
        else:
            cols = {"clouds": ((64, 72, 104), (44, 50, 78)), "overcast": ((56, 58, 74), (44, 46, 60)),
                    "rain": ((44, 46, 60), (34, 36, 48)), "storm": ((36, 36, 50), (26, 26, 38)),
                    "fog": ((80, 86, 100), (66, 70, 84)), "snow": ((72, 78, 98), (58, 62, 80))}.get(k)
            if cols is None:
                return
        layout = {
            "clear": [(0, 8, 1, 0), (50, 24, 0, 1)],
            "clouds": [(0, 6, 2, 0), (40, 18, 1, 1), (70, 30, 0, 0), (20, 36, 1, 1)],
        }.get(k, [(0, 2, 2, 0), (30, 8, 0, 1), (60, 0, 2, 0), (10, 16, 2, 1), (50, 22, 0, 0), (80, 12, 1, 1),
                  (20, 28, 2, 0), (70, 34, 1, 1)])
        pal = {"W": cols[0], "S": cols[1]}
        far = {"W": mix(cols[0], cols[1], 0.5), "S": cols[1]}
        for x0, y0, shape, speed in layout:
            if speed:
                # near layer: 1px/frame over a 96px track, so it loops exactly
                s.sprite((x0 + t) % 96 - 22, y0, CLOUDS[shape], pal)
            else:
                # far layer: small wisps, 1px every 2 frames on a 48px track
                x = (x0 + t // 2) % 48 - 11
                s.sprite(x, y0, CLOUDS[1], far)
                s.sprite(x + 48, y0, CLOUDS[1], far)

    # --- monitor -----------------------------------------------------------
    def _monitor(self, c, t):
        sx, sy, sw, sh = SCREEN_BOX
        c.rect(sx, sy, sw, sh, SCREEN, emit=True)
        c.rect(sx, sy, sw, 7, (30, 34, 46), emit=True)
        for i, col in enumerate(((255, 95, 87), (255, 189, 46), (40, 201, 64))):
            c.rect(sx + 3 + i * 4, sy + 2, 2, 2, col, emit=True)
        title = self.ctx.get("repo_title", "~/DEV")
        c.text(sx + sw - 3 - TINY.width(title), sy + 1, title, (112, 122, 146), font=TINY, emit=True)

        py = sy + 9
        c.text(sx + 2, py, ">", GREEN, font=TINY, emit=True)
        w = c.text(sx + 7, py, "git log --oneline", (206, 214, 228), font=TINY, emit=True)
        if t % 12 < 6:
            c.rect(sx + 9 + w, py, 3, 5, (206, 214, 228), emit=True)

        commits = self.ctx["commits"] or [("0000000", "hello world")]
        lines = [commits[i % len(commits)] for i in range(8)]
        region_y, region_h = sy + 16, 30
        sub = Canvas(sw - 2, region_h, SCREEN)
        step, phase = t // 12, t % 12
        offset = step * 6 + max(0, phase - 6)
        for i in range(step, step + 8):
            y = i * 6 - offset
            if y > region_h:
                break
            sha, msg = lines[i % 8]
            hw = sub.text(1, y, sha[:5], YELLOW, font=TINY)
            avail = sw - 2 - (hw + 6) - 3
            sub.text(hw + 6, y, TINY.truncate(msg, avail), GREEN if i % 3 else (150, 220, 236), font=TINY)
        c.paste(sub, sx + 1, region_y, emit=True)
        # scanline sheen
        for x in range(sx, sx + sw, 2):
            c.px(x, sy + sh - 1, (20, 26, 36), emit=True)

    def _server_leds(self, c, t):
        x, y = 34, 117
        for i in range(4):
            by = y + 3 + i * 8
            for j in range(3):
                on = ((t // (3 + i + j)) * (7 + i * 3 + j * 5)) % 5 < 3
                col = ((90, 230, 120) if j < 2 else (255, 176, 64)) if on else (30, 50, 40)
                c.px(x + 20 + j * 2, by + 2, col, emit=on)
        c.px(x + 26, y + 35, (90, 200, 255) if t % 24 < 20 else (40, 60, 90), emit=True)

    # --- lantern -------------------------------------------------------------
    def _flicker(self, t):
        return (0, 1, 0, 2, 1, 0, 0, 1, 2, 0, 1, 0)[(t * 7 + t // 5) % 12]

    def _lantern(self, c, t):
        for y in range(7, LANTERN_Y):
            c.px(LANTERN_C[0], y, BRASS_D if y % 2 else BRASS)
        f = self._flicker(t)
        amber = ((255, 184, 84), (255, 200, 110), (240, 166, 70))[f]
        red = ((226, 86, 60), (240, 104, 70), (206, 74, 52))[f]
        flame = ((255, 236, 170), (255, 246, 204), (255, 222, 140))[f]
        pal = {"o": BRASS_D, "b": BRASS, "h": BRASS_H, "a": amber, "r": red, "f": flame,
               "F": (255, 255, 236)}
        c.sprite(LANTERN_X, LANTERN_Y, LANTERN, pal, emit={"a", "r", "f", "F"})

    # --- neon ----------------------------------------------------------------
    def _neon(self, c, t):
        text = self.ctx.get("neon", "HELLO")
        sc = 2 if FONT.width(text) * 2 <= 120 else 1
        tw = FONT.width(text) * sc
        x0, y0 = 178 - tw // 2, 15
        tube = Image.new("L", (W, H), 0)
        dead = Image.new("L", (W, H), 0)
        tmp = Canvas(W, H)
        tmp_dead = Canvas(W, H)
        off = {30, 31, 33, 34, 70}
        flick_letter = min(3, len(text) - 1)
        cx = x0
        for i, ch in enumerate(FONT.normalize(text)):
            target = tmp_dead if (i == flick_letter and t in off) or t == 71 else tmp
            target.text(cx, y0, ch, (255, 255, 255), scale=sc)
            cx += (len(FONT.glyph(ch)[0]) + 1) * sc
        tube = tmp.img.convert("L").point(lambda v: 255 if v else 0)
        dead = tmp_dead.img.convert("L").point(lambda v: 255 if v else 0)
        g1 = tube.filter(ImageFilter.MaxFilter(3))
        g2 = tube.filter(ImageFilter.MaxFilter(5))
        checker = Image.new("L", (W, H), 0)
        cd = checker.load()
        for y in range(y0 - 3, y0 + 7 * sc + 4):
            for x in range(x0 - 3, x0 + tw + 4):
                if (x + y) % 2 == 0 and 0 <= x < W and 0 <= y < H:
                    cd[x, y] = 255
        g2 = ImageChops.multiply(ImageChops.subtract(g2, g1), checker)
        g1 = ImageChops.subtract(g1, tube)
        c.img.paste((100, 36, 96), (0, 0, W, H), g2)
        c.img.paste((156, 48, 124), (0, 0, W, H), g1)
        c.img.paste((92, 58, 96), (0, 0, W, H), dead)
        c.img.paste((255, 122, 198), (0, 0, W, H), tube)
        for m in (g1, g2, tube):
            c.emit.paste(255, (0, 0, W, H), m)
        # mounting brackets
        c.rect(x0 - 5, y0 + 3, 2, 3, STEEL_L)
        c.rect(x0 + tw + 3, y0 + 3, 2, 3, STEEL_L)

    # --- steam, cat ------------------------------------------------------------
    def _steam(self, c, t):
        for k, (bx, ph) in enumerate(((237, 0), (239, 8), (238, 16))):
            age = (t + ph) % 24
            for i in range(3):
                a = age + i * 2
                if a >= 24:
                    continue
                y = 98 - a // 2 - i
                x = bx + round(wave(a, 16, k * 0.3) * 1.5)
                col = mix((236, 240, 248), WALL, a / 26)
                c.px(x, y, col)

    def _cat(self, c, t):
        x, y = 246, 152
        grey, light, dark, out = (132, 134, 150), (178, 180, 196), (96, 98, 116), (34, 32, 44)
        breathe = 1 if (t // 12) % 2 else 0
        pal = {"o": out, "g": grey, "l": light, "p": (226, 146, 160)}
        # tail curls out behind the body and lazily swishes
        c.sprite(281, 153, CAT_TAIL[(0, 1, 2, 1)[(t // 8) % 4]], pal)
        # body
        c.ellipse(x + 9, y - 1 + breathe, 30, 14 - breathe, out)
        c.ellipse(x + 10, y + breathe, 28, 12 - breathe, grey)
        c.ellipse(x + 14, y + 6, 20, 5, light)
        for sx in (x + 18, x + 24, x + 30):
            c.rect(sx, y + 1 + breathe, 2, 3, dark)
        # head
        hx, hy = x, y + 2
        for ex in (hx, hx + 8):
            c.sprite(ex, hy - 3, CAT_EAR, pal)
        c.ellipse(hx - 1, hy - 1, 15, 13, out)
        c.ellipse(hx, hy, 13, 11, grey)
        for ex in (hx, hx + 8):
            c.sprite(ex, hy - 3, CAT_EAR[:3], pal)
        c.rect(hx + 2, hy + 7, 9, 3, light)
        c.px(hx + 3, hy + 5, out); c.px(hx + 4, hy + 6, out); c.px(hx + 5, hy + 5, out)
        c.px(hx + 7, hy + 5, out); c.px(hx + 8, hy + 6, out); c.px(hx + 9, hy + 5, out)
        c.px(hx + 6, hy + 7, (226, 146, 160))
        c.rect(hx + 3, hy + 11, 4, 2, out)
        c.rect(hx + 4, hy + 11, 2, 1, light)
        # z z z
        for k, off in enumerate((0, 11, 22)):
            age = (t + off) % 32
            zx = hx + 12 + age // 4
            zy = hy - 4 - age // 2
            col = mix((236, 240, 255), WALL, age / 34)
            if age < 30:
                c.text(zx, zy - 2, "z", col, font=TINY)

    # =====================================================================
    # lighting
    # =====================================================================
    def _lightmap(self, f):
        key = (self.day, self.kind, f)
        if key in self.lightmaps:
            return self.lightmaps[key]
        if self.day:
            ambient = {"overcast": (226, 226, 236), "rain": (204, 206, 222), "storm": (176, 178, 202),
                       "fog": (220, 222, 230), "snow": (226, 228, 238)}.get(self.kind)
            if ambient is None:
                self.lightmaps[key] = None
                return None
            lights = [(LANTERN_C, 1.0 + f * 0.04, [(14, (255, 236, 200)), (26, (240, 226, 214))])]
        else:
            ambient = (74, 82, 136)
            k = (1.0, 1.06, 0.95)[f]
            lights = [
                (LANTERN_C, k, [(14, (255, 228, 186)), (26, (220, 194, 172)), (42, (170, 156, 172)),
                                (62, (124, 120, 162))]),
                ((178, 76), 1.0, [(34, (168, 196, 222)), (56, (124, 142, 186))]),
                ((178, 20), 1.0, [(18, (176, 120, 176)), (30, (130, 104, 160))]),
            ]
        lm = Image.new("RGB", (W, H), ambient)
        if not self.day and self.kind in ("clear", "clouds"):
            ImageDraw.Draw(lm).polygon(MOON_POOL, fill=(118, 132, 190))
        px = lm.load()
        for y in range(H):
            for x in range(W):
                best = px[x, y]
                jitter = 0.9 if (x + y) % 2 else -0.9
                for (cx, cy), k2, bands in lights:
                    d = math.hypot((x - cx) / 1.25, y - cy) / k2 + jitter
                    for r, col in bands:
                        if d < r:
                            best = (max(best[0], col[0]), max(best[1], col[1]), max(best[2], col[2]))
                            break
                px[x, y] = best
        self.lightmaps[key] = lm
        return lm

    def _light(self, c, t):
        f = self._flicker(t)
        lm = self._lightmap(f)
        img = c.img
        if lm is not None:
            lit = ImageChops.multiply(img, lm)
            img = Image.composite(img, lit, c.emit)

        if not self.day:
            # star-shaped light thrown by the pierced lantern
            cx, cy = LANTERN_C
            px = img.load()
            em = c.emit.load()
            warm = ((255, 196, 120), (255, 210, 140), (240, 180, 100))[f]
            for ring, (r, n, amt) in enumerate(((19, 12, 0.42), (31, 16, 0.34), (44, 20, 0.26))):
                for i in range(n):
                    a = 2 * math.pi * (i + 0.5 * (ring % 2)) / n
                    x = round(cx + r * 1.25 * math.cos(a))
                    y = round(cy + r * math.sin(a))
                    pts = [(x, y)] + ([(x + 1, y), (x, y + 1)] if ring < 2 else [])
                    for (qx, qy) in pts:
                        if 8 <= qy < 113 and 0 <= qx < W and not em[qx, qy]:
                            px[qx, qy] = mix(px[qx, qy], warm, amt + (0.06 if f == 1 else 0))

        if self.sunny:
            bright = Image.blend(img, Image.new("RGB", (W, H), (255, 240, 200)), 0.16)
            beam = ImageChops.multiply(self.beam_mask, ImageChops.invert(c.emit))
            img = Image.composite(bright, img, beam)
            px = img.load()
            for (u0, v0, ph) in self.motes:
                v = (v0 + t / FRAMES) % 1.0
                u = min(0.95, max(0.05, u0 + 0.04 * wave(t, 48, ph)))
                lx = BEAM[0][0] + (BEAM[1][0] - BEAM[0][0]) * u
                rx = BEAM[3][0] + (BEAM[2][0] - BEAM[3][0]) * u
                x = round(lx + (rx - lx) * v)
                y = round(BEAM[0][1] + (BEAM[3][1] - BEAM[0][1]) * v)
                if 0 <= x < W and 0 <= y < H:
                    px[x, y] = mix(px[x, y], (255, 250, 230), 0.55)

        if self.kind == "storm" and t in (40, 41, 44):
            img = Image.blend(img, Image.new("RGB", (W, H), (226, 232, 255)), 0.35 if t != 44 else 0.18)
        return img


def render(ctx):
    room = Room(ctx)
    return [room.frame(t) for t in range(FRAMES)], [DELAY] * FRAMES
