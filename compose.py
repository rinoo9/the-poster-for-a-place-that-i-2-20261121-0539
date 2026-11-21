#!/usr/bin/env python3
"""Draw the travel poster for VELMORA, the Floating Isles of the Amber Sea.

A place that does not exist: islands that drift above a golden sea at dusk,
waterfalls pouring off their edges into the clouds. Deterministic: no
randomness anywhere, fixed coordinates only. Output: entry.png 1024x1024.
"""
import hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1024, 1024
OUT = "entry.png"

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

CREAM = (253, 243, 216)
GOLD = (242, 193, 78)
DARK = (14, 42, 51)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, top, bottom, c_top, c_bot):
    """Vertical gradient from y=top to y=bottom."""
    for y in range(top, bottom):
        t = (y - top) / max(1, bottom - top - 1)
        draw.line([(0, y), (W, y)], fill=lerp(c_top, c_bot, t))


def ellipse_glow(base, center, radius, color, steps=12):
    """Soft glow: concentric circles fading out, composited on base."""
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(steps, 0, -1):
        r = radius * i / steps
        alpha = int(26 * (1 - i / steps) + 8)
        gd.ellipse(
            [center[0] - r, center[1] - r, center[0] + r, center[1] + r],
            fill=color + (alpha,),
        )
    base.alpha_composite(glow)


def island(draw, top_y, left, right, point, fill, rim):
    """A floating island: flat top, sloping sides meeting at a point below."""
    cx = (left + right) // 2
    draw.polygon(
        [(left, top_y), (right, top_y), (cx + (right - cx) // 3, point),
         (cx, point + 26), (cx - (cx - left) // 3, point)],
        fill=fill,
    )
    # sunlit rim along the flat top
    draw.line([(left, top_y), (right, top_y)], fill=rim, width=4)
    # tiny pine silhouettes on the top edge
    for tx in range(left + 28, right - 20, 34):
        th = 16 + ((tx * 7) % 13)
        draw.polygon(
            [(tx, top_y), (tx + 9, top_y), (tx + 4, top_y - th)],
            fill=(18, 16, 34),
        )
    # a small white cottage with a warm window on the big island
    return cx


def waterfall(draw, x, y0, y1, width=5):
    """A thin pale waterfall falling from an island edge."""
    for i in range(y1 - y0):
        t = i / max(1, y1 - y0 - 1)
        alpha = int(235 * (1 - t * 0.55))
        w = width - int(t * 2)
        draw.line([(x, y0 + i), (x + w, y0 + i)],
                  fill=(207, 232, 239, alpha), width=1)
    # mist puff at the bottom
    draw.ellipse([x - 8, y1 - 4, x + width + 8, y1 + 10],
                 fill=(220, 235, 240, 170))


def cloud(draw, cx, cy, scale, color):
    """A soft cloud made of overlapping ellipses."""
    blobs = [(-52, 6, 62, 30), (-28, -12, 66, 30), (8, -18, 70, 32),
             (34, 0, 60, 28), (-6, 8, 90, 26)]
    for dx, dy, w, h in blobs:
        draw.ellipse(
            [cx + dx * scale, cy + dy * scale,
             cx + (dx + w) * scale, cy + (dy + h) * scale],
            fill=color,
        )


def bird(draw, x, y, s):
    draw.line([(x - s, y), (x, y - s // 2)], fill=(30, 24, 44), width=3)
    draw.line([(x, y - s // 2), (x + s, y)], fill=(30, 24, 44), width=3)


def centered(draw, y, text, font, fill, shadow=True):
    w = draw.textlength(text, font=font)
    x = (W - w) / 2
    if shadow:
        draw.text((x + 3, y + 3), text, font=font, fill=(20, 16, 38))
    draw.text((x, y), text, font=font, fill=fill)
    return w


def main():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # --- sky: indigo dusk down to amber horizon ---
    vgrad(draw, 0, 640, (27, 42, 74), (232, 160, 76))
    # --- sea: amber horizon down to deep teal ---
    vgrad(draw, 640, H, (216, 138, 66), (16, 58, 66))

    # --- stars in the upper sky (fixed positions) ---
    for (sx, sy, sr) in [
        (90, 70, 2), (180, 130, 2), (300, 60, 3), (420, 110, 2),
        (640, 70, 2), (760, 120, 3), (880, 80, 2), (940, 170, 2),
        (520, 50, 2), (60, 210, 2), (960, 260, 2), (230, 190, 2),
    ]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(253, 243, 216, 200))

    # --- sun glow + disc low on the horizon ---
    ellipse_glow(img, (512, 640), 190, (255, 214, 130))
    draw = ImageDraw.Draw(img)
    draw.ellipse([512 - 78, 640 - 78, 512 + 78, 640 + 78],
                 fill=(255, 233, 176))
    draw.ellipse([512 - 66, 640 - 66, 512 + 66, 640 + 66],
                 fill=(255, 240, 196))

    # --- sea light streaks (fixed pattern; kept above the tagline rules) ---
    for i, (sy, sx0, sx1) in enumerate([
        (668, 380, 644), (692, 300, 724), (716, 430, 594),
        (744, 250, 774), (772, 360, 664), (806, 300, 724),
        (844, 420, 604),
    ]):
        alpha = 150 - i * 9
        draw.line([(sx0, sy), (sx1, sy)], fill=(255, 214, 130, alpha),
                  width=3)

    # --- clouds drifting between the isles and the sea ---
    cloud(draw, 150, 700, 1.0, (244, 196, 150, 235))
    cloud(draw, 690, 730, 1.15, (240, 186, 140, 225))
    cloud(draw, 880, 660, 0.8, (246, 204, 158, 215))

    # --- the floating isles (far to near) ---
    island(draw, 380, 430, 580, 470, (44, 38, 72), (217, 160, 91))
    island(draw, 420, 620, 900, 560, (36, 31, 61), (217, 160, 91))
    island(draw, 470, 120, 420, 640, (30, 26, 52), (217, 160, 91))

    # --- waterfalls pouring off the isles into the clouds ---
    waterfall(draw, 200, 560, 690, 5)
    waterfall(draw, 330, 580, 700, 4)
    waterfall(draw, 700, 520, 640, 5)
    waterfall(draw, 820, 500, 630, 4)
    waterfall(draw, 470, 460, 500, 4)

    # --- birds ---
    for (bx, by, bs) in [(240, 300, 12), (300, 260, 10), (700, 300, 12),
                         (760, 250, 9), (820, 320, 11), (180, 350, 9),
                         (620, 340, 10)]:
        bird(draw, bx, by, bs)

    # --- frame: cream rule + thin gold rule ---
    draw.rectangle([26, 26, W - 27, H - 27], outline=CREAM + (255,), width=5)
    draw.rectangle([40, 40, W - 41, H - 41], outline=GOLD + (255,), width=2)

    # --- title block ---
    title_font = ImageFont.truetype(SERIF_BOLD, 118)
    sub_font = ImageFont.truetype(SANS_BOLD, 34)
    tag_font = ImageFont.truetype(SANS_BOLD, 30)
    small_font = ImageFont.truetype(SANS, 20)
    centered(draw, 78, "VELMORA", title_font, CREAM)
    centered(draw, 208, "T H E   F L O A T I N G   I S L E S", sub_font, GOLD,
             shadow=False)

    # --- tagline + small print at the bottom ---
    draw.line([(312, 878), (712, 878)], fill=GOLD + (255,), width=2)
    centered(draw, 896, "WHERE THE SKY MEETS THE SEA", tag_font, CREAM)
    draw.line([(312, 940), (712, 940)], fill=GOLD + (255,), width=2)
    centered(draw, 952, "VISIT THE AMBER SEA  •  EST. 1897", small_font,
             (253, 243, 216, 220), shadow=False)

    img.convert("RGB").save(OUT, format="PNG")
    with open(OUT, "rb") as f:
        data = f.read()
    print(f"wrote {OUT}: {len(data)} bytes, "
          f"sha256 {hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
