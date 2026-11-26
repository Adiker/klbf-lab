"""Draws the KLBF Lab Bench BM-v1 certificate template (the validated postcard sketch, every
variable text left out) to crates/victory-gpu/src/klbf_card.png, 1280 x 820 RGBA.
The runtime (klbf_bench.rs) decodes it and writes the figures, project, player, date, serial,
machine, share line and the CERTIFIED / PARTIAL / INVALID band over it.

Usage: python -I tools/klbf-card-template.py
Needs Pillow and the Windows fonts Impact, Arial, Georgia. Run once; commit the script and the PNG.
Coordinates are the sketch's (1000 x 640 units).
"""
import math
import re
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

OUT_W, OUT_H = 1280, 820
SS = 2  # drawn at twice the size, then reduced
U = OUT_W / 1000 * SS  # pixels per unit while drawing
W, H = OUT_W * SS, OUT_H * SS
FONTS = Path("C:/Windows/Fonts")


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), round(size * U))


def hexc(h, a=255):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), a)


def pt(x, y):
    return (x * U, y * U)


def subpaths(d):
    """Absolute M L Q C Z paths only, flattened; one point list per subpath."""
    toks = re.findall(r"[MLQCZ]|-?\d*\.?\d+", d)
    out, cur, x, y, i, cmd = [], [], 0.0, 0.0, 0, None
    def num():
        nonlocal i
        i += 1
        return float(toks[i - 1])
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            if cmd == "Z":
                if cur:
                    out.append(cur)
                cur = []
                continue
        if cmd == "M":
            if cur:
                out.append(cur)
            x, y = num(), num()
            cur = [(x, y)]
            cmd = "L"
        elif cmd == "L":
            x, y = num(), num()
            cur.append((x, y))
        elif cmd in "QC":
            n = 4 if cmd == "Q" else 6
            a = [num() for _ in range(n)]
            ctrl = [(x, y)] + [(a[j], a[j + 1]) for j in range(0, n, 2)]
            for s in range(1, 17):
                t = s / 16
                if cmd == "Q":
                    (x0, y0), (x1, y1), (x2, y2) = ctrl
                    u = 1 - t
                    cur.append((u * u * x0 + 2 * u * t * x1 + t * t * x2, u * u * y0 + 2 * u * t * y1 + t * t * y2))
                else:
                    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = ctrl
                    u = 1 - t
                    cur.append((u**3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t**3 * x3,
                                u**3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t**3 * y3))
            x, y = ctrl[-1]
    if cur:
        out.append(cur)
    return out


TRUNK = "M0 0 C 6 -60 10 -120 4 -190"
LEAVES = ("M4 -190 C -40 -200 -80 -185 -110 -160 C -70 -175 -35 -178 4 -186 Z "
          "M4 -190 C 45 -205 90 -195 120 -165 C 80 -180 45 -182 4 -186 Z "
          "M4 -190 C -20 -230 -55 -245 -90 -245 C -50 -230 -25 -215 4 -188 Z "
          "M4 -190 C 30 -232 70 -245 105 -240 C 65 -228 35 -214 4 -188 Z")


def palm(draw, tx, ty, k, ox=0.0, oy=0.0):
    """The sketch's palm (translate(tx ty) scale(k)) into an L-mode draw; (ox, oy) shifts units."""
    f = lambda p: pt(tx + p[0] * k - ox, ty + p[1] * k - oy)
    draw.line([f(p) for p in subpaths(TRUNK)[0]], fill=255, width=max(1, round(10 * k * U)), joint="curve")
    for leaf in subpaths(LEAVES):
        draw.polygon([f(p) for p in leaf], fill=255)


def gradient(w, h, stops, diagonal):
    """A w x h RGBA gradient (vertical, or corner to corner)."""
    sw, sh = max(2, w // 8), max(2, h // 8)
    img = Image.new("RGBA", (sw, sh))
    px = []
    for yy in range(sh):
        for xx in range(sw):
            t = (xx / (sw - 1) + yy / (sh - 1)) / 2 if diagonal else yy / (sh - 1)
            for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
                if t <= t1:
                    f = (t - t0) / (t1 - t0) if t1 > t0 else 0
                    a, b = hexc(c0), hexc(c1)
                    px.append(tuple(round(a[i] + (b[i] - a[i]) * f) for i in range(4)))
                    break
    img.putdata(px)
    return img.resize((w, h), Image.BILINEAR)


def layer_fill(img, mask, colour):
    """Lays `colour` (RGBA) over `img` through the L `mask`."""
    solid = Image.new("RGBA", img.size, colour)
    m = ImageChops.multiply(mask, Image.new("L", img.size, colour[3]))
    img.paste(solid, (0, 0), m)


def dashed(draw, x0, y0, x1, y1, dash, gap, width, colour):
    length = math.hypot(x1 - x0, y1 - y0)
    s = 0.0
    while s < length:
        e = min(s + dash, length)
        a = (x0 + (x1 - x0) * s / length, y0 + (y1 - y0) * s / length)
        b = (x0 + (x1 - x0) * e / length, y0 + (y1 - y0) * e / length)
        draw.line([pt(*a), pt(*b)], fill=colour, width=max(1, round(width * U)))
        s += dash + gap


def main():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # Card: gradient wash, rounded, 3-unit border.
    card = Image.new("L", (W, H), 0)
    ImageDraw.Draw(card).rounded_rectangle([*pt(10, 10), *pt(990, 630)], radius=18 * U, fill=255)
    wash = gradient(round(980 * U), round(620 * U), [(0, "#ffd1e8"), (0.55, "#ffc6b0"), (1, "#ffb37a")], True)
    img.paste(wash, (round(10 * U), round(10 * U)), card.crop((round(10 * U), round(10 * U), round(10 * U) + wash.width, round(10 * U) + wash.height)))
    d.rounded_rectangle([*pt(8.5, 8.5), *pt(991.5, 631.5)], radius=19.5 * U, outline=hexc("#e7a3b8"), width=round(3 * U))
    # Watermark palms, cut at the card's edge.
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    palm(md, 430, 640, 1.5)
    palm(md, 770, 640, 1.7)
    layer_fill(img, ImageChops.multiply(m, card), hexc("#b0507a", round(255 * 0.16)))
    # Sun with its stripes.
    sun = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sun).ellipse([*pt(234, 46), *pt(366, 178)], fill=round(255 * 0.85))
    sg = gradient(W, round(132 * U), [(0, "#ffe066"), (1, "#ff4f8b")], False)
    full = Image.new("RGBA", (W, H))
    full.paste(sg, (0, round(46 * U)))
    img.paste(full, (0, 0), sun)
    for y, h in ((120, 6), (138, 8), (158, 10)):
        d.rectangle([*pt(234, y), *pt(366, y + h)], fill=hexc("#ffd1e8"))
    # Title, letter-spaced, gradient fill, dark outline.
    impact = font("impact.ttf", 72)
    for word, base, spacing in (("KLBF LAB", 112, 2), ("BENCH", 186, 7)):
        fill_m = Image.new("L", (W, H), 0)
        edge_m = Image.new("L", (W, H), 0)
        fd, ed = ImageDraw.Draw(fill_m), ImageDraw.Draw(edge_m)
        x = 50 * U
        for ch in word:
            ed.text((x, base * U), ch, font=impact, anchor="ls", fill=255, stroke_width=round(1.5 * U), stroke_fill=255)
            fd.text((x, base * U), ch, font=impact, anchor="ls", fill=255)
            x += impact.getlength(ch) + spacing * U
        layer_fill(img, edge_m, hexc("#3b1a6b"))
        box = fill_m.getbbox()
        g = gradient(box[2] - box[0], box[3] - box[1], [(0, "#ffde59"), (0.45, "#ff6fa8"), (1, "#7a3cff")], False)
        full = Image.new("RGBA", (W, H))
        full.paste(g, box[:2])
        img.paste(full, (0, 0), fill_m)
    # Left lines (the date line is written at run time).
    ink = hexc("#3b2240")
    d.text(pt(255, 278), "Bayside Morning v1", font=font("georgiab.ttf", 24), anchor="ms", fill=ink)
    d.text(pt(255, 336), "5 minutes at the male lead's house", font=font("georgia.ttf", 18), anchor="ms", fill=ink)
    for y in (290, 348, 406):
        dashed(d, 70, y, 440, y, 3, 5, 2, hexc("#7a5a6a"))
    # The palm stamp at (50, 455), its picture cut to the vignette.
    d.rectangle([*pt(50, 455), *pt(160, 590)], fill=hexc("#fff6ee"))
    for a, b in (((50, 455), (160, 455)), ((160, 455), (160, 590)), ((160, 590), (50, 590)), ((50, 590), (50, 455))):
        dashed(d, *a, *b, 6, 4, 2, hexc("#cc99aa"))
    vw, vh = round(90 * U), round(100 * U)
    vig = Image.new("RGBA", (vw, vh), hexc("#ffb37a"))
    vd = ImageDraw.Draw(vig, "RGBA")
    vd.ellipse([(31 * U, 34 * U), (79 * U, 82 * U)], fill=hexc("#ffe066"))
    vd.rectangle([(0, 72 * U), (vw, vh)], fill=hexc("#6fc7d6"))
    pm = Image.new("L", (vw, vh), 0)
    palm(ImageDraw.Draw(pm), 34, 106, 0.3, 10, 10)
    palm(ImageDraw.Draw(pm), 76, 106, 0.24, 10, 10)
    layer_fill(vig, pm, hexc("#4a2a50"))
    img.paste(vig, (round(60 * U), round(465 * U)))
    d.text(pt(105, 582), "BM-v1", font=font("georgiab.ttf", 14), anchor="ms", fill=ink)
    # Divider.
    d.line([pt(500, 50), pt(500, 600)], fill=hexc("#7a5a6a"), width=round(2 * U))
    # The round postmark (serial, date and band are written at run time).
    red = hexc("#d6264f")
    cx, cy = 880, 120
    for r, w in ((72, 4), (54, 2)):
        d.ellipse([*pt(cx - r - w / 2, cy - r - w / 2), *pt(cx + r + w / 2, cy + r + w / 2)], outline=red, width=round(w * U))
    arial_b = font("arialbd.ttf", 19)
    text, track, rad = "KLBF LAB", 3 * U, 63 * U
    total = sum(arial_b.getlength(c) + track for c in text) - track
    acc = -total / 2
    for c in text:
        adv = arial_b.getlength(c)
        a = (acc + adv / 2) / rad
        size = round(40 * U)
        g = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((size / 2, size / 2), c, font=arial_b, anchor="mm", fill=red)
        g = g.rotate(-math.degrees(a), resample=Image.BICUBIC)
        px, py = cx * U + rad * math.sin(a), cy * U - rad * math.cos(a)
        img.alpha_composite(g, (round(px - size / 2), round(py - size / 2)))
        acc += adv + track
    flask = subpaths("M -9 -28 L 9 -28 L 9 -10 L 27 25 Q 29 36 18 36 L -18 36 Q -29 36 -27 25 L -9 -10 Z")[0]
    flask = [pt(cx + x, cy + y) for x, y in flask]
    d.line(flask + flask[:2], fill=red, width=round(4 * U), joint="curve")
    d.line([pt(cx - 20, cy + 16), pt(cx + 20, cy + 16)], fill=red, width=round(3 * U))
    for x, y, r in ((-5, 26, 4), (8, 22, 3)):
        d.ellipse([*pt(cx + x - r, cy + y - r), *pt(cx + x + r, cy + y + r)], fill=red)
    # The address side's fixed parts.
    d.text(pt(535, 275), "from:", font=font("arial.ttf", 20), anchor="ls", fill=ink)
    d.line([pt(535, 314), pt(960, 314)], fill=hexc("#7a5a6a"), width=round(2 * U))
    d.text(pt(680, 352), "FPS", font=font("arialbd.ttf", 20), anchor="ls", fill=ink)
    d.text(pt(680, 378), "average", font=font("arial.ttf", 16), anchor="ls", fill=ink)
    tiles = Image.new("L", (W, H), 0)
    for i, label in enumerate(("median", "1 % low", "max", "time \u2265 12 fps")):
        x = 535 + 108 * i
        ImageDraw.Draw(tiles).rounded_rectangle([*pt(x, 398), *pt(x + 100, 460)], radius=8 * U, fill=255)
    layer_fill(img, tiles, hexc("#fff6ee", round(255 * 0.85)))
    for i, label in enumerate(("median", "1 % low", "max", "time \u2265 12 fps")):
        d.text(pt(535 + 108 * i + 50, 452), label, font=font("arial.ttf", 12), anchor="ms", fill=hexc("#6b4a5a"))
    out = img.resize((OUT_W, OUT_H), Image.LANCZOS)
    dst = Path(__file__).resolve().parent.parent / "crates/victory-gpu/src/klbf_card.png"
    out.save(dst, optimize=True)
    print(f"{dst}: {dst.stat().st_size} bytes")


if __name__ == "__main__":
    main()
