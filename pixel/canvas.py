"""A tiny pixel-art canvas on top of Pillow, plus a GIF writer.

Everything is drawn at native resolution and upscaled with nearest-neighbour
at save time, so every "pixel" stays a crisp square on GitHub.
"""

from PIL import Image, ImageDraw

from fonts import FONT


def mix(a, b, t):
    """Blend colour a toward b by t (0..1)."""
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def scale(c, k):
    return tuple(max(0, min(255, round(v * k))) for v in c)


def hex_rgb(h, default=(139, 148, 158)):
    try:
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except (AttributeError, ValueError, IndexError):
        return default


def luminance(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


class Canvas:
    def __init__(self, w, h, bg=(0, 0, 0)):
        self.w, self.h = w, h
        self.img = Image.new("RGB", (w, h), bg)
        self.emit = Image.new("L", (w, h), 0)  # pixels that ignore room lighting
        self._bind()

    def _bind(self):
        self.d = ImageDraw.Draw(self.img)
        self.e = ImageDraw.Draw(self.emit)

    def copy(self):
        c = Canvas.__new__(Canvas)
        c.w, c.h = self.w, self.h
        c.img = self.img.copy()
        c.emit = self.emit.copy()
        c._bind()
        return c

    # -- primitives -------------------------------------------------------
    def rect(self, x, y, w, h, c, emit=False):
        if w <= 0 or h <= 0:
            return
        box = [x, y, x + w - 1, y + h - 1]
        self.d.rectangle(box, fill=c)
        if emit:
            self.e.rectangle(box, fill=255)

    def frame(self, x, y, w, h, c, emit=False):
        self.rect(x, y, w, 1, c, emit)
        self.rect(x, y + h - 1, w, 1, c, emit)
        self.rect(x, y, 1, h, c, emit)
        self.rect(x + w - 1, y, 1, h, c, emit)

    def px(self, x, y, c, emit=False):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img.putpixel((x, y), c)
            if emit:
                self.emit.putpixel((x, y), 255)

    def line(self, x0, y0, x1, y1, c, emit=False):
        self.d.line([x0, y0, x1, y1], fill=c)
        if emit:
            self.e.line([x0, y0, x1, y1], fill=255)

    def ellipse(self, x, y, w, h, c, emit=False):
        box = [x, y, x + w - 1, y + h - 1]
        self.d.ellipse(box, fill=c)
        if emit:
            self.e.ellipse(box, fill=255)

    def polygon(self, pts, c, emit=False):
        self.d.polygon(pts, fill=c)
        if emit:
            self.e.polygon(pts, fill=255)

    def sprite(self, x, y, rows, pal, emit=False, flip=False):
        """Draw ASCII-art rows. pal maps chars to colours; unknown chars are clear.
        emit may be a bool or a set of chars that glow."""
        for j, row in enumerate(rows):
            if flip:
                row = row[::-1]
            for i, ch in enumerate(row):
                col = pal.get(ch)
                if col is not None:
                    glow = emit if isinstance(emit, bool) else ch in emit
                    self.px(x + i, y + j, col, glow)

    def text(self, x, y, s, c, font=FONT, scale=1, spacing=1, emit=False, shadow=None):
        """Draw text with its cap-top at y. Returns the drawn width."""
        s = font.normalize(s)
        cx = x
        for ch in s:
            g = font.glyph(ch)
            for j, row in enumerate(g):
                for i, bit in enumerate(row):
                    if bit == "#":
                        if shadow:
                            self.rect(cx + i * scale + scale, y + j * scale + scale, scale, scale, shadow, emit)
                        self.rect(cx + i * scale, y + j * scale, scale, scale, c, emit)
            cx += (len(g[0]) + spacing) * scale
        return cx - x - spacing * scale if s else 0

    def paste(self, other, x, y, mask=None, emit=False):
        img = other.img if isinstance(other, Canvas) else other
        self.img.paste(img, (x, y), mask)
        if emit:
            self.emit.paste(255, (x, y, x + img.width, y + img.height), mask)


def rounded_mask(w, h, steps=(3, 1, 1)):
    """Alpha mask with pixel-stepped corners. steps[i] = pixels cut on row i."""
    m = Image.new("L", (w, h), 255)
    for j, cut in enumerate(steps):
        for i in range(cut):
            for x, y in ((i, j), (w - 1 - i, j), (i, h - 1 - j), (w - 1 - i, h - 1 - j)):
                m.putpixel((x, y), 0)
    return m


def save_gif(path, frames, durations, k=2, mask=None, loop=True):
    """Write native-resolution RGB frames as an upscaled, delta-compressed GIF.

    One shared palette is used for every frame so nothing shimmers, and
    pixels that do not change between frames are written as transparent.

    mask is one alpha mask for every frame (opaque art with cut corners), or a
    list with one mask per frame for art floating on a transparent page. The
    latter needs "restore to background" disposal so pixels can disappear.
    """
    per_frame = isinstance(mask, (list, tuple))
    masks = list(mask) if per_frame else [mask] * len(frames)

    # Palette work happens at native resolution: k*k times fewer pixels.
    colors = set()
    for f in frames:
        colors.update(col for _, col in f.getcolors(1 << 24))
        if len(colors) > 255:
            break

    if len(colors) <= 255:
        palette = sorted(colors)
    else:
        # Too many colours (night lighting, lightning): median-cut every frame
        # together, refined with k-means, into one shared 255-colour palette.
        strip = Image.new("RGB", (frames[0].width, frames[0].height * len(frames)))
        for i, f in enumerate(frames):
            strip.paste(f, (0, i * f.height))
        q = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT, kmeans=2, dither=Image.Dither.NONE)
        flat = q.getpalette()[: 255 * 3]
        palette = [tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)]

    # One free slot for transparency. Its key colour is whichever cube corner
    # sits furthest from every real colour, so no pixel snaps to it by accident.
    tidx = len(palette)
    corners = [(r, g, b) for r in (0, 255) for g in (0, 255) for b in (0, 255)]
    key = max(corners, key=lambda c0: min(sum((c0[i] - c[i]) ** 2 for i in range(3)) for c in palette))
    flat = [v for col in palette for v in col]
    flat += list(key)
    flat += list(palette[0]) * (256 - len(palette) - 1)
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette(flat)

    out = []
    for f, m in zip(frames, masks):
        p = f.quantize(palette=pal_img, dither=Image.Dither.NONE)
        if m is not None:
            p.paste(tidx, (0, 0, p.width, p.height), Image.eval(m, lambda v: 255 - v))
        p = p.resize((p.width * k, p.height * k), Image.NEAREST)
        p.info["transparency"] = tidx
        out.append(p)

    kwargs = dict(
        save_all=True,
        append_images=out[1:],
        duration=durations,
        disposal=2 if per_frame else 1,
        transparency=tidx,
        optimize=not per_frame,
    )
    if loop:
        kwargs["loop"] = 0
    out[0].save(path, **kwargs)
