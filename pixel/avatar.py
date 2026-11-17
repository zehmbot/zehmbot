"""Turn a profile picture into an 80x80 pixel-art portrait.

The picture is box-averaged down to 80x80, contrast-stretched, then mapped
onto a 5-tone palette with a 4x4 Bayer dither, the Game Boy Camera look.
"color" keeps the original colours instead, reduced to 16.
"""

import io
import pathlib
import urllib.request

from PIL import Image, ImageEnhance, ImageOps

SIZE = 80
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
RAMPS = {
    "ink": [(13, 17, 23), (40, 46, 70), (84, 92, 128), (150, 156, 186), (226, 224, 214)],
    "majorelle": [(14, 16, 40), (36, 48, 140), (76, 96, 200), (160, 176, 236), (240, 236, 222)],
    "tea": [(20, 16, 22), (70, 46, 40), (140, 96, 64), (210, 168, 112), (246, 232, 200)],
}


def load(source, here, avatar_url):
    """source is "github", "robot", or an image path relative to the pixel/ folder.
    Returns a PIL image, or None to fall back to the robot."""
    if source == "robot":
        return None
    if source and source != "github":
        return Image.open(pathlib.Path(here) / source)
    if not avatar_url:
        return None
    req = urllib.request.Request(avatar_url, headers={"User-Agent": "pixel-profile"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return Image.open(io.BytesIO(r.read()))


def square(img):
    img = ImageOps.exif_transpose(img).convert("RGB")
    side = min(img.size)
    left, top = (img.width - side) // 2, (img.height - side) // 2
    return img.crop((left, top, left + side, top + side))


def pixelate(img, style="ink"):
    img = square(img).resize((SIZE, SIZE), Image.BOX)
    if style == "color":
        img = ImageEnhance.Color(img).enhance(1.2)
        return img.quantize(colors=16, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")

    ramp = RAMPS.get(style, RAMPS["ink"])
    g = ImageOps.autocontrast(img.convert("L"), cutoff=2)
    g = ImageEnhance.Contrast(g).enhance(1.15)
    out = Image.new("RGB", (SIZE, SIZE))
    src, dst = g.load(), out.load()
    k = len(ramp) - 1
    for y in range(SIZE):
        for x in range(SIZE):
            v = src[x, y] / 255 * k + (BAYER[y % 4][x % 4] / 16 - 0.5) * 0.9
            dst[x, y] = ramp[max(0, min(k, round(v)))]
    return out
