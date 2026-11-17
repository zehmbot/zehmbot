"""The info cards under the hero: about, stats, projects, activity, footer.

Each function returns (frames, durations, mask) at native resolution.
"""

import datetime as dt
import hashlib
import math

from canvas import Canvas, hex_rgb, luminance, mix, rounded_mask, scale
from fonts import FONT, TINY

BG = (22, 27, 34)
INSET = (13, 17, 23)
BORDER = (48, 54, 61)
HILITE = (33, 39, 48)
TEXT = (230, 237, 243)
SOFT = (201, 209, 217)
MUTED = (139, 148, 158)
DIM = (96, 104, 114)
ACCENT = (126, 231, 135)
GOLD = (240, 196, 96)
INK = (24, 22, 34)
MAJORELLE = (44, 62, 178)

STEPS = (2, 1)
HEAT = [(36, 42, 51), (14, 68, 41), (0, 109, 50), (38, 166, 65), (57, 211, 83)]


def card(w, h):
    c = Canvas(w, h, BG)
    c.rect(2, 0, w - 4, 1, BORDER)
    c.rect(2, h - 1, w - 4, 1, BORDER)
    c.rect(0, 2, 1, h - 4, BORDER)
    c.rect(w - 1, 2, 1, h - 4, BORDER)
    for x, y in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
        c.px(x, y, BORDER)
    c.rect(2, 1, w - 4, 1, HILITE)
    return c


def label(c, x, y, text, t=None, color=ACCENT):
    w = c.text(x, y, "> " + text, color, font=TINY)
    if t is not None and t:
        c.rect(x + w + 2, y, 3, 5, color)
    return w


def compact(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 10_000:
        return f"{round(n / 1000)}K"
    if n >= 1000:
        return f"{n / 1000:.1f}K".replace(".0K", "K")
    return str(n)


# =============================================================================
# robot avatar
# =============================================================================
def robot(c, bx, by, t):
    """An 80x80 portrait of zehmbot: a tiny robot in a red fez."""
    size = 80
    c.rect(bx - 2, by - 2, size + 4, size + 4, BORDER)
    c.rect(bx - 1, by - 1, size + 2, size + 2, INK)
    c.rect(bx, by, size, size, MAJORELLE)
    # faint 8-point stars, like the zellige downstairs
    star = ["..#..", ".###.", "#####", ".###.", "..#.."]
    for sy in range(-2, size, 16):
        for sx in range(-2 + (8 if (sy // 16) % 2 else 0), size, 16):
            for j, row in enumerate(star):
                for i, ch in enumerate(row):
                    x, y = bx + sx + i, by + sy + j
                    if ch == "#" and bx <= x < bx + size and by <= y < by + size:
                        c.px(x, y, (52, 72, 196) if (i + j) % 2 else (38, 54, 160))
    c.rect(bx, by + size - 10, size, 10, (36, 50, 150))

    silver, shade, light, dark = (190, 198, 214), (146, 154, 174), (232, 238, 246), (92, 98, 118)
    hx, hy, hw, hh = bx + 18, by + 25, 44, 32
    bob = 1 if (t // 6) % 2 else 0
    hy += bob

    # body
    c.rect(bx + 12, by + 62 + bob, 56, 20, INK)
    c.rect(bx + 13, by + 63 + bob, 54, 17, (52, 128, 120))
    c.rect(bx + 13, by + 63 + bob, 54, 2, (76, 160, 150))
    c.rect(bx + 30, by + 65 + bob, 20, 15, (36, 96, 90))
    led = (90, 240, 120) if t % 12 < 8 else (40, 90, 60)
    c.rect(bx + 33, by + 68 + bob, 3, 3, led)
    c.text(bx + 40, by + 67 + bob, "Z", (170, 236, 228), font=TINY)
    c.rect(bx + 34, by + 57 + bob, 12, 6, INK)
    c.rect(bx + 35, by + 57 + bob, 10, 5, dark)

    # ear bolts
    for ex in (hx - 4, hx + hw):
        c.rect(ex, hy + 9, 4, 12, INK)
        c.rect(ex + 1, hy + 10, 2, 10, shade)
    # head
    c.rect(hx + 2, hy, hw - 4, hh, INK)
    c.rect(hx, hy + 2, hw, hh - 4, INK)
    c.rect(hx + 1, hy + 1, hw - 2, hh - 2, INK)
    c.rect(hx + 2, hy + 1, hw - 4, hh - 2, silver)
    c.rect(hx + 1, hy + 2, hw - 2, hh - 4, silver)
    c.rect(hx + 2, hy + 1, hw - 4, 1, light)
    c.rect(hx + hw - 3, hy + 2, 2, hh - 4, shade)
    c.rect(hx + 2, hy + hh - 2, hw - 4, 1, shade)
    # face screen
    fx, fy, fw, fh = hx + 5, hy + 5, hw - 10, 21
    c.rect(fx, fy, fw, fh, dark)
    c.rect(fx + 1, fy + 1, fw - 2, fh - 2, (14, 18, 28))
    c.px(fx + 2, fy + 2, (60, 70, 92))
    c.px(fx + 3, fy + 2, (40, 48, 66))
    look = (0, 0, 1, 1, 0, 0, -1, -1, 0, 0, 0, 0)[(t // 2) % 12]
    blink = t % 24 in (20, 21)
    eye = (96, 234, 240)
    for ex in (fx + 7, fx + 21):
        if blink:
            c.rect(ex + look, fy + 9, 6, 1, eye)
        else:
            c.rect(ex + look, fy + 5, 6, 8, eye)
            c.rect(ex + look + 1, fy + 6, 2, 2, (220, 255, 255))
    c.rect(fx + 15, fy + 16, 4, 1, eye)
    c.px(fx + 14, fy + 15, eye)
    c.px(fx + 19, fy + 15, eye)
    c.rect(fx + 3, fy + 15, 3, 1, (255, 120, 160))
    c.rect(fx + fw - 6, fy + 15, 3, 1, (255, 120, 160))

    # fez
    red, red_d, red_l, band = (204, 40, 50), (160, 26, 38), (236, 92, 92), (140, 20, 30)
    for i in range(13):
        y = hy - 13 + i
        half = 8 + i // 3
        cx = hx + hw // 2
        c.rect(cx - half - 1, y, 2 * half + 2, 1, INK)
        c.rect(cx - half, y, 2 * half, 1, red)
        c.px(cx - half + 1, y, red_l)
        c.rect(cx + half - 3, y, 3, 1, red_d)
    c.rect(hx + hw // 2 - 9, hy - 14, 18, 1, INK)
    c.rect(hx + hw // 2 - 8, hy - 13, 16, 1, (182, 32, 44))
    c.rect(hx + hw // 2 - 12, hy - 4, 24, 2, band)
    # tassel on a cord, swinging
    sway = (0, 1, 2, 2, 1, 0, -1, -1)[(t // 3) % 8]
    cx = hx + hw // 2
    cord = (34, 30, 40)
    c.rect(cx - 1, hy - 16, 3, 2, cord)
    for i in range(10):
        c.px(cx + 1 + i, hy - 15 + i // 4, cord)
    for j in range(7):
        c.px(cx + 11 + round(sway * j / 7), hy - 12 + j, cord)
    tx, ty = cx + 10 + sway, hy - 6
    c.rect(tx, ty, 4, 7, INK)
    c.rect(tx + 1, ty, 2, 6, (52, 46, 60))
    c.px(tx + 1, ty + 1, (110, 104, 124))
    for i in range(4):
        c.px(tx + i, ty + 7, INK if i % 2 else (52, 46, 60))


def portrait(c, bx, by, t, img):
    """The pixelated profile picture, with a holo-card glint and an online dot."""
    size = img.width
    c.rect(bx - 2, by - 2, size + 4, size + 4, BORDER)
    c.rect(bx - 1, by - 1, size + 2, size + 2, INK)
    c.paste(img, bx, by)
    # a shine sweeps diagonally across during the first half of the loop
    g = t * 14 - 20
    px = c.img.load()
    for d, amt in enumerate((0.14, 0.32, 0.32, 0.14)):
        s = g + d
        for x in range(max(0, s - size + 1), min(size - 1, s) + 1):
            p = (bx + x, by + s - x)
            px[p] = mix(px[p], (255, 255, 255), amt)
    # status dot on the corner of the frame
    dx, dy = bx + size - 6, by + size - 6
    c.ellipse(dx - 1, dy - 1, 10, 10, BG)
    c.ellipse(dx, dy, 8, 8, BORDER)
    c.ellipse(dx + 1, dy + 1, 6, 6, (63, 185, 80) if t % 12 < 6 else ACCENT)


# =============================================================================
# about
# =============================================================================
def about(profile, gh, avatar=None):
    W, H = 480, 124
    frames = []
    langs = profile["languages"]
    meta = " · ".join(x for x in [
        profile.get("location", ""),
        f"{gh['followers']} followers",
        f"{gh['repo_count']} repos",
        f"since {gh['since']}",
    ] if x)
    tagline = FONT.wrap(profile.get("tagline", ""), 350, max_lines=2)
    for t in range(24):
        c = card(W, H)
        label(c, 14, 12, "ABOUT", t=(t % 12) < 6)
        c.text(14, 26, profile["name"], TEXT, scale=2)
        role = profile.get("role", "")
        c.text(14, 48, role, GOLD)
        for i, line in enumerate(tagline):
            c.text(14, 62 + i * 11, line, SOFT)
        c.text(14, 90, meta, MUTED, font=TINY)
        x = 14
        for name in langs + profile.get("frameworks", []):
            col = hex_rgb(profile["colors"].get(name, "#8b949e"))
            w = TINY.width(name) + 12
            if x + w > 370:
                break
            c.rect(x, 101, w, 11, INSET)
            c.frame(x, 101, w, 11, BORDER)
            c.rect(x + 3, 104, 3, 5, col)
            c.text(x + 8, 104, name, SOFT, font=TINY)
            x += w + 4
        if avatar is not None:
            portrait(c, 386, 22, t, avatar)
        else:
            robot(c, 386, 22, t)
        frames.append(c.img)
    return frames, [110] * len(frames), rounded_mask(W, H, STEPS)


# =============================================================================
# studio
# =============================================================================
EMBER = [(255, 247, 226), (255, 224, 168), (245, 186, 110), (224, 136, 62), (186, 92, 40), (140, 60, 30)]
EMBER_BG = (11, 6, 9)


def ember_text(c, x, y, s, scale=2):
    """Text lit from above like the Lowlight wordmark: hot on top, sinking into
    the dark toward the bottom."""
    tmp = Canvas(FONT.width(s) * scale + 2, 9 * scale, (0, 0, 0))
    tmp.text(0, 0, s, (255, 255, 255), scale=scale)
    src = tmp.img.load()
    rows = 7 * scale
    for j in range(tmp.h):
        col = EMBER[min(len(EMBER) - 1, j * len(EMBER) // rows)]
        for i in range(tmp.w):
            if src[i, j] != (0, 0, 0):
                c.px(x + i, y + j, col)


def studio(info, logo):
    """A card for the studio: the animated ember mark plus who/what/where."""
    W, H = 480, 100
    years = info.get("founded")
    meta = [f"FOUNDED {years}" if years else "", info.get("url", "").replace("https://", "")]
    if info.get("public_repos"):
        meta.append(f"{info['public_repos']} PUBLIC REPOS")
    meta = " · ".join(m for m in meta if m)
    desc = FONT.wrap(info.get("tagline", ""), 360, max_lines=2)
    n = len(logo) * 2
    frames = []
    for t in range(n):
        c = card(W, H)
        # logo box: the mark keeps its own near-black background and flicker
        c.rect(12, 12, 76, 76, BORDER)
        c.rect(13, 13, 74, 74, EMBER_BG)
        c.paste(logo[t % len(logo)], 18, 18)
        x = 102
        label(c, x, 13, "STUDIO", t=(t // 5) % 2 == 0, color=(245, 186, 110))
        ember_text(c, x, 25, info.get("name", ""))
        c.text(x, 46, info.get("role", ""), GOLD)
        for i, line in enumerate(desc):
            c.text(x, 59 + i * 11, line, SOFT)
        c.text(x, 59 + len(desc) * 11 + 4, meta, MUTED, font=TINY)
        # a few embers drift up the right edge of the card
        for k in range(4):
            age = (t * 2 + k * 5) % n
            ex = 459 + (k * 5) % 13 + round(math.sin((age + k * 3) / 3))
            ey = 84 - age * 3
            if 14 < ey < 86:
                c.px(ex, ey, EMBER[min(5, 1 + age * 5 // n)])
        frames.append(c.img)
    return frames, [95] * n, rounded_mask(W, H, STEPS)


# =============================================================================
# stats strip (counts up once, then holds)
# =============================================================================
ICONS = {
    "commit": ["..#..", "..#..", ".###.", "##.##", ".###.", "..#..", "..#.."],
    "pr": ["##...##", "##...##", ".#...#.", ".#..#..", ".#.#...", "##.....", "##....."],
    "star": ["...#...", "..###..", "#######", ".#####.", "..###..", ".##.##.", "##...##"],
    "flame": ["..#....", "..##...", ".####..", ".#####.", "###.##.", "##..###", ".#####."],
}


def stats(gh):
    W, H = 480, 56
    items = [
        (gh["commits"], "COMMITS", "commit", (126, 231, 135)),
        (gh["prs"], "PULL REQS", "pr", (163, 113, 247)),
        (gh["stars"], "STARS", "star", GOLD),
        (gh["best_streak"], "BEST STREAK", "flame", (255, 140, 80)),
    ]
    n = 18
    frames = []
    for f in range(n + 1):
        k = 1 - (1 - min(1.0, f / n)) ** 3
        c = card(W, H)
        for i, (val, name, icon, col) in enumerate(items):
            x = 8 + i * 118
            if i:
                for y in range(10, H - 10, 3):
                    c.px(x - 4, y, BORDER)
            v = round(val * k)
            txt = f"{v}D" if icon == "flame" else compact(v)
            c.text(x + 12, 11, txt, TEXT, scale=3)
            c.sprite(x + 12, 38, ICONS[icon], {"#": col})
            c.text(x + 22, 39, name, MUTED, font=TINY)
        frames.append(c.img)
    durations = [55] * n + [60000]
    return frames, durations, rounded_mask(W, H, STEPS)


# =============================================================================
# section header
# =============================================================================
def header(text):
    W, H = 480, 24
    frames = []
    for t in range(2):
        c = Canvas(W, H, (0, 0, 0))
        w = c.text(2, 5, ">", ACCENT, scale=2)
        w2 = c.text(16, 5, text, ACCENT, scale=2)
        end = 16 + w2
        if t == 0:
            c.rect(end + 4, 5, 6, 14, ACCENT)
        for x in range(end + 16, W - 2, 6):
            c.rect(x, 11, 3, 2, (46, 90, 56))
        frames.append(c.img)
    return frames, [600, 600], ink_masks(frames)


def ink_masks(frames):
    """Per-frame alpha: opaque where something is drawn, clear elsewhere, so
    the art floats on GitHub's page in both light and dark themes."""
    return [f.convert("L").point(lambda v: 255 if v else 0) for f in frames]


# =============================================================================
# project cards
# =============================================================================
CREATURE_COLORS = [(96, 210, 255), (255, 120, 190), (250, 200, 80), (126, 231, 135),
                   (180, 140, 255), (255, 150, 90)]


LEGS = [
    ([[0, 1, 0, 0], [1, 0, 0, 0]], [[0, 0, 1, 0], [0, 1, 0, 0]]),
    ([[1, 0, 1, 0], [1, 0, 0, 0]], [[0, 1, 0, 0], [0, 1, 0, 0]]),
    ([[0, 1, 1, 0], [1, 0, 0, 0]], [[0, 1, 1, 0], [0, 0, 1, 0]]),
    ([[1, 0, 0, 0], [0, 1, 0, 0]], [[0, 1, 0, 0], [1, 0, 0, 0]]),
]
ANTENNAE = [[0, 0, 0, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [1, 0, 1, 0]]


def creature(name, slot=None):
    """A unique, symmetric pixel critter for a repo: (frame_a, frame_b, colour)."""
    h = hashlib.sha256(name.encode()).digest()
    bits = int.from_bytes(h, "big")

    def take(n):
        nonlocal bits
        v = bits % n
        bits //= n
        return v

    # left half (4 columns incl. the spine), mirrored to 7 columns
    grid = [[0] * 4 for _ in range(7)]
    grid[0] = ANTENNAE[take(len(ANTENNAE))][:]
    for y in range(1, 5):
        grid[y][3] = 1
        grid[y][2] = 1 if take(10) < 8 else 0
        grid[y][1] = 1 if take(10) < 6 else 0
        grid[y][0] = 1 if take(10) < 4 else 0
    eye_row, eye_col = 1 + take(2), 1 + take(2)
    grid[eye_row][eye_col] = 0
    for dx in (-1, 1):
        if 0 <= eye_col + dx <= 3:
            grid[eye_row][eye_col + dx] = 1
    grid[eye_row + 1][eye_col] = 1
    legs = LEGS[take(len(LEGS))]
    frames = []
    for leg in legs:
        g = [row[:] for row in grid]
        g[5], g[6] = leg[0][:], leg[1][:]
        frames.append([row + row[:3][::-1] for row in g])
    idx = h[-1] if slot is None else slot
    col = CREATURE_COLORS[idx % len(CREATURE_COLORS)]
    return frames[0], frames[1], col


def project(repo, slot=None):
    W, H = 236, 92
    name = repo["name"]
    desc = repo.get("description") or "No description yet."
    lang = (repo.get("primaryLanguage") or {}).get("name") or ""
    lcol = hex_rgb((repo.get("primaryLanguage") or {}).get("color") or "#8b949e")
    stars = compact(repo.get("stargazerCount", 0))
    fa, fb, ccol = creature(name, slot)
    lines = FONT.wrap(desc, 166, max_lines=3)
    title = FONT.truncate(name, 166)
    frames = []
    for t in range(16):
        c = card(W, H)
        # creature box
        c.rect(10, 12, 42, 42, BORDER)
        c.rect(11, 13, 40, 40, INSET)
        for sy in range(15, 52, 4):
            for sx in range(13, 50, 4):
                c.px(sx, sy, (24, 30, 40))
        grid = fa if (t // 4) % 2 == 0 else fb
        bob = 0 if (t // 4) % 2 == 0 else 1
        dark, light = scale(ccol, 0.55), mix(ccol, (255, 255, 255), 0.45)
        for gy, row in enumerate(grid):
            for gx, v in enumerate(row):
                if v:
                    x, y = 17 + gx * 4, 16 + gy * 4 + bob
                    c.rect(x, y, 4, 4, ccol)
                    if gy + 1 >= len(grid) or not grid[gy + 1][gx]:
                        c.rect(x, y + 3, 4, 1, dark)  # shade only exposed undersides
                    if gy == 0 or not grid[gy - 1][gx]:
                        c.rect(x, y, 4, 1, light)  # and catch light on top edges
        if t in (10, 11, 12):
            sp = {10: [(45, 18)], 11: [(44, 18), (46, 18), (45, 17), (45, 19)], 12: [(45, 18)]}[t]
            for x, y in sp:
                c.px(x, y, (255, 255, 255))
        # text
        c.text(60, 12, title, TEXT)
        for i, line in enumerate(lines):
            c.text(60, 26 + i * 11, line, MUTED)
        # stars + language
        star_col = GOLD if t not in (6, 7) else (255, 236, 170)
        c.sprite(60, 72, ICONS["star"], {"#": star_col})
        c.text(70, 72, stars, GOLD)
        if lang:
            lw = TINY.width(lang)
            c.rect(W - 14 - lw - 9, 73, 5, 5, lcol)
            c.text(W - 12 - lw, 73, lang, SOFT, font=TINY)
        frames.append(c.img)
    return frames, [140] * len(frames), rounded_mask(W, H, STEPS)


# =============================================================================
# activity heatmap
# =============================================================================
def activity(gh, today):
    W, H = 480, 120
    days = gh["days"]
    # 52 full weeks ending with the current (partial) week, Sunday first like GitHub
    end = today
    start = end - dt.timedelta(days=(end.weekday() + 1) % 7) - dt.timedelta(weeks=51)
    counts = sorted(v for v in days.values() if v > 0)

    def level(v):
        if v <= 0 or not counts:
            return 0
        q = [counts[int(len(counts) * p)] for p in (0.25, 0.5, 0.75)]
        return 1 + sum(v > x for x in q)

    cells = []
    d = start
    while d <= end:
        col = (d - start).days // 7
        row = (d.weekday() + 1) % 7
        cells.append((col, row, level(days.get(d, 0)), d))
        d += dt.timedelta(days=1)

    year_total = sum(v for k, v in days.items() if k.year == today.year and k <= today)
    year_365 = sum(v for k, v in days.items() if 0 <= (today - k).days < 365)
    cur, best = gh["current_streak"], gh["best_streak"]
    frames = []
    for t in range(32):
        c = card(W, H)
        label(c, 14, 12, "ACTIVITY", t=(t % 16) < 8)
        ox, oy = 14, 26
        glint = t * 3 - 10
        for col, row, lv, d in cells:
            color = HEAT[lv]
            g = col + row * 0.6
            if lv and abs(g - glint) < 1.5:
                color = mix(color, (220, 255, 220), 0.45)
            elif not lv and abs(g - glint) < 1.0:
                color = mix(color, (70, 80, 92), 0.6)
            c.rect(ox + col * 6, oy + row * 6, 5, 5, color)
            if d == today and (t // 4) % 2 == 0:
                c.frame(ox + col * 6 - 1, oy + row * 6 - 1, 7, 7, (220, 255, 220))
        # month labels
        seen = set()
        for col, row, lv, d in cells:
            if row == 0 and d.day <= 7 and (d.month not in seen) and col < 50:
                seen.add(d.month)
                c.text(ox + col * 6, oy + 46, d.strftime("%b"), DIM, font=TINY)
        # legend
        lx = ox + 52 * 6 - 5 * 6 - TINY.width("MORE") - 2
        c.text(lx - TINY.width("LESS") - 4, 84, "LESS", DIM, font=TINY)
        for i, colr in enumerate(HEAT):
            c.rect(lx + i * 6, 84, 5, 5, colr)
        c.text(lx + 5 * 6 + 2, 84, "MORE", DIM, font=TINY)
        c.text(ox, 84, f"{year_365:,} contributions in the last year", DIM, font=TINY)

        # numbers
        sx = 352
        for j, (lab, val) in enumerate((("CURRENT STREAK", f"{cur} day" + ("" if cur == 1 else "s")),
                                         ("BEST STREAK", f"{best} day" + ("" if best == 1 else "s")),
                                         ("THIS YEAR", f"{year_total:,}"))):
            y = 22 + j * 31
            c.text(sx, y, lab, MUTED, font=TINY)
            w = c.text(sx, y + 8, val, TEXT, scale=2)
            if j == 0 and cur > 0:
                fl = (ICONS["flame"], [r[::-1] for r in ICONS["flame"]])[(t // 3) % 2]
                c.sprite(sx + w + 6, y + 11, fl, {"#": (255, 140, 80) if t % 6 < 3 else (255, 190, 90)})
            if j == 2:
                c.text(sx + w + 4, y + 15, "contributions", MUTED, font=TINY)
        frames.append(c.img)
    return frames, [90] * len(frames), rounded_mask(W, H, STEPS)


# =============================================================================
# footer
# =============================================================================
MINI_BOT = [
    [
        ".....rrrr.k...",
        "....rrrrrrk...",
        "....rrrrrr.k..",
        "...oooooooo...",
        "...osssssso...",
        "...oseesseo...",
        "...osssssso...",
        "....oooooo....",
        "..ttttttttt...",
        ".t.ttttttt.t..",
        "...ttttttt....",
        "....o...o.....",
    ],
    [
        ".....rrrr..k..",
        "....rrrrrr.k..",
        "....rrrrrr..k.",
        "...oooooooo...",
        "...osssssso..t",
        "...oseesseo.t.",
        "...osssssso.t.",
        "....oooooo.t..",
        "..ttttttttt...",
        ".t.ttttttt....",
        "...ttttttt....",
        "....o...o.....",
    ],
]


def footer(profile):
    W, H = 480, 40
    frames = []
    msg = profile.get("footer", "Thanks for stopping by!")
    tw = FONT.width(msg)
    for t in range(24):
        c = Canvas(W, H, (0, 0, 0))
        x0 = (W - tw) // 2
        c.text(x0, 12, msg, MUTED)
        bot = MINI_BOT[(t // 3) % 2] if t < 12 else MINI_BOT[0]
        c.sprite(x0 - 24, 9, bot, {"r": (204, 40, 50), "k": (30, 30, 36), "o": (60, 64, 80),
                                   "s": (190, 198, 214), "e": (96, 234, 240), "t": (52, 128, 120)})
        # mint tea on the right with rising steam
        gx = x0 + tw + 10
        c.sprite(gx, 14, ["..mm..", ".mmmm.", "otTTto", "ogtgto", "otgtgo", "otTtto", ".otto.", ".oooo."],
                 {"o": (196, 226, 218), "t": (190, 124, 40), "T": (226, 164, 66), "g": (230, 186, 74),
                  "m": (70, 170, 84)})
        for k in range(2):
            age = (t + k * 12) % 24
            if age < 18:
                c.px(gx + 2 + k + round(math.sin((age + k * 5) / 3)), 12 - age // 3, (170, 178, 188))
        frames.append(c.img)
    return frames, [120] * len(frames), ink_masks(frames)
