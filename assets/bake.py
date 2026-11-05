"""Menuel - paints each room's 400x480 background: backdrop, textured terrain, ledges, hazards, props and light."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ni
import world as W

WW, WH = 400, 480
TS = 16

THEME = [
    dict(sky_top=(20, 26, 50), sky_bot=(38, 50, 84), far=(44, 58, 94), base=(84, 104, 140), dark=(36, 46, 72), rim=(226, 242, 250), rim2=(170, 200, 224),
         plank=(120, 110, 96), plank_d=(66, 58, 54), light=(190, 220, 255), hazard='crystal'),
    dict(sky_top=(6, 28, 36), sky_bot=(14, 62, 72), far=(16, 58, 66), base=(70, 102, 98), dark=(24, 46, 50), rim=(150, 208, 150), rim2=(84, 150, 110),
         plank=(112, 92, 64), plank_d=(58, 46, 34), light=(150, 240, 210), hazard='water'),
    dict(sky_top=(30, 14, 12), sky_bot=(92, 36, 18), far=(66, 28, 18), base=(112, 74, 56), dark=(46, 28, 24), rim=(244, 164, 84), rim2=(190, 104, 54),
         plank=(120, 106, 104), plank_d=(58, 50, 52), light=(255, 170, 90), hazard='slag'),
    dict(sky_top=(14, 12, 40), sky_bot=(64, 56, 112), far=(46, 42, 92), base=(96, 90, 136), dark=(40, 36, 70), rim=(246, 248, 255), rim2=(200, 206, 236),
         plank=(146, 136, 150), plank_d=(74, 68, 92), light=(210, 210, 255), hazard='ice'),
]


def noise(rng, h, w, scale):
    """Smooth value noise in 0..1."""
    n = rng.random((h // scale + 3, w // scale + 3))
    n = ni.zoom(n, scale, order=3)[:h, :w]
    return (n - n.min()) / (n.max() - n.min() + 1e-6)


def fbm(rng, h, w, scales=(64, 32, 16, 8)):
    out, amp, tot = np.zeros((h, w)), 1.0, 0.0
    for s in scales:
        out += noise(rng, h, w, s) * amp
        tot += amp
        amp *= .55
    return out / tot


def lerp(a, b, t):
    return a + (b - a) * t


def backdrop(theme, rng):
    th = THEME[theme]
    y = np.linspace(0, 1, WH)[:, None]
    top, bot = np.array(th['sky_top'], float), np.array(th['sky_bot'], float)
    img = np.zeros((WH, WW, 3))
    for c in range(3):
        img[:, :, c] = top[c] + (bot[c] - top[c]) * y
    im = Image.fromarray(img.astype('uint8'))
    d = ImageDraw.Draw(im, 'RGBA')
    far = th['far']
    if theme == 0:      # timber props and far crystal veins
        for x in (rng.integers(20, 90), rng.integers(170, 230), rng.integers(300, 370)):
            d.rectangle((x, 0, x + 11, WH), fill=(*far, 180))
            d.rectangle((x - 26, 110, x + 37, 118), fill=(*far, 180))
            d.rectangle((x - 26, 330, x + 37, 338), fill=(*far, 180))
        for _ in range(26):
            x, yy = rng.integers(0, WW), rng.integers(0, WH)
            h = rng.integers(8, 26)
            d.polygon([(x - h // 3, yy + h), (x, yy), (x + h // 3, yy + h)], fill=(120, 160, 200, 60))
    elif theme == 1:    # drowned arches, ropes, light from above
        for k, x in enumerate(range(-30, WW, 120)):
            d.arc((x, 50, x + 120, 330), 180, 360, fill=(*far, 220), width=10)
            d.rectangle((x - 5, 190, x + 5, WH), fill=(*far, 220))
            d.line((x + 60, 0, x + 60 + int(rng.integers(-6, 7)), rng.integers(120, 260)), fill=(120, 110, 80, 130), width=2)
        for _ in range(5):
            x = rng.integers(0, WW)
            d.polygon([(x, 0), (x + 30, 0), (x + 90, WH), (x + 20, WH)], fill=(150, 230, 220, 14))
    elif theme == 2:    # furnace walls and gears
        for x in (rng.integers(10, 80), rng.integers(150, 230), rng.integers(300, 360)):
            d.rectangle((x, 60, x + 58, WH), fill=(*far, 240))
            d.ellipse((x + 12, 180, x + 46, 214), fill=(255, 150, 50, 200))
            d.ellipse((x + 20, 188, x + 38, 206), fill=(255, 238, 150, 240))
        for _ in range(4):
            x, yy, r_ = rng.integers(0, WW), rng.integers(0, 200), rng.integers(22, 46)
            d.ellipse((x - r_, yy - r_, x + r_, yy + r_), outline=(*far, 230), width=8)
            for a in range(0, 360, 45):
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                d.line((x + ca * r_, yy + sa * r_, x + ca * (r_ + 8), yy + sa * (r_ + 8)), fill=(*far, 230), width=6)
    else:               # stars, moon and peaks
        for _ in range(170):
            x, yy = rng.integers(0, WW), rng.integers(0, 260)
            v = int(rng.integers(100, 255))
            d.point((x, yy), fill=(v, v, 255, 255))
        mx, my = rng.integers(60, 340), rng.integers(30, 90)
        d.ellipse((mx - 26, my - 26, mx + 26, my + 26), fill=(226, 226, 248, 255))
        d.ellipse((mx - 36, my - 30, mx + 14, my + 22), fill=(*THEME[3]['sky_top'], 245))
        for layer, col in ((0, (54, 50, 104)), (1, (40, 36, 80))):
            xs = 0
            while xs < WW + 80:
                pk = 170 + layer * 70 + int(rng.integers(-30, 30))
                w_ = int(rng.integers(70, 130))
                d.polygon([(xs - w_, WH), (xs, pk), (xs + w_, WH)], fill=col)
                d.polygon([(xs - 14, pk + 26), (xs, pk), (xs + 14, pk + 26), (xs + 4, pk + 20), (xs - 5, pk + 22)], fill=(170, 170, 210))
                xs += w_ + int(rng.integers(0, 50))
    return np.array(im.filter(ImageFilter.GaussianBlur(.8)).convert('RGB'), float)


def rock_texture(theme, rng):
    th = THEME[theme]
    h, w = WH, WW
    base, dark = np.array(th['base'], float), np.array(th['dark'], float)
    n = fbm(rng, h, w)
    t = np.clip((n - .3) / .45, 0, 1)
    tex = np.dstack([dark[c] + (base[c] - dark[c]) * t for c in range(3)])
    yy, xx = np.mgrid[0:h, 0:w]
    if theme == 0:       # crystal facets: sharp diagonal bands
        f = ((xx * .9 + yy * 1.2 + n * 60).astype(int) // 18 % 2) * .12 + ((xx * .9 - yy * 1.0 + n * 40).astype(int) // 26 % 2) * .1
        tex *= (.86 + f)[..., None]
    elif theme == 1:     # wet bricks
        row = yy // 14
        off = (row % 2) * 13
        mort = ((yy % 14) < 2) | (((xx + off) % 26) < 2)
        tex[mort] *= .55
        tex *= (.92 + .18 * ((row * 7 + (xx + off) // 26 * 13) % 5 / 5))[..., None]
    elif theme == 2:     # riveted iron plates, rust stains
        plate = ((yy % 32) < 2) | ((xx % 48) < 2)
        tex[plate] *= .55
        rv = ((yy % 32 - 6) ** 2 + (xx % 48 - 7) ** 2) < 5
        tex[rv] = tex[rv] * .5 + np.array((230, 170, 120)) * .5
        rust = noise(rng, h, w, 12) > .62
        tex[rust] = tex[rust] * .78 + np.array((150, 70, 30)) * .22
    else:                # frozen stone with cold cracks
        cr = np.abs(fbm(rng, h, w, (40, 20)) - .5) < .012
        tex[cr] = tex[cr] * .5 + np.array((200, 220, 255)) * .5
    return tex


def terrain_mask(room, rng):
    g = room.g
    m = np.zeros((WH, WW), bool)
    for y in range(W.H):
        for x in range(W.W):
            if g[y][x] == '#':
                m[y * TS:(y + 1) * TS, x * TS:(x + 1) * TS] = True
    # organic outline: a light wobble that never moves an edge more than about two pixels
    b = ni.gaussian_filter(m.astype(float), 2.2)
    wob = (fbm(rng, WH, WW, (24, 10)) - .5) * .32
    return (b + wob) > .5, m


def draw_planks(img, room, theme, rng):
    th = THEME[theme]
    p, pd = np.array(th['plank'], float), np.array(th['plank_d'], float)
    g = room.g
    for y in range(W.H):
        x = 0
        while x < W.W:
            if g[y][x] == '-':
                x0 = x
                while x < W.W and g[y][x] == '-':
                    x += 1
                px0, px1, py = x0 * TS, x * TS, y * TS
                for yy in range(py, py + 7):
                    t = (yy - py) / 6
                    img[yy, px0:px1] = p * (1.12 - t * .55)
                img[py, px0:px1] = np.minimum(p * 1.5, 255)
                img[py + 7:py + 9, px0:px1] = pd * .55
                for bx in range(px0, px1, 24):      # boards and supports
                    img[py:py + 7, bx:bx + 1] = pd
                for sx in (px0 + 3, px1 - 6):
                    img[py + 7:py + 15, sx:sx + 3] = pd
                    img[py + 7:py + 15, sx:sx + 1] = pd * 1.3
            else:
                x += 1


def draw_hazards(img, room, theme, rng):
    kind = THEME[theme]['hazard']
    g = room.g
    t = ni.gaussian_filter
    glow = np.zeros((WH, WW))
    for x in range(W.W):
        for y in range(W.H):
            if g[y][x] != '^':
                continue
            px, py = x * TS, y * TS
            if kind == 'water':
                for yy in range(py - 6, py + 16):
                    k = (yy - py + 6) / 22
                    img[yy, px:px + TS] = lerp(np.array((70, 170, 200.)), np.array((14, 60, 96.)), k)
                wave = (np.sin(np.arange(px, px + TS) * .5) * 1.5).astype(int)
                for i, xx in enumerate(range(px, px + TS)):
                    img[py - 6 + wave[i], xx] = (210, 245, 250)
            elif kind == 'slag':
                for yy in range(py - 4, py + 16):
                    k = (yy - py + 4) / 20
                    img[yy, px:px + TS] = lerp(np.array((255, 230, 120.)), np.array((200, 50, 10.)), k)
                glow[py - 4:py + 16, px:px + TS] = 1
                for _ in range(2):
                    bx = int(rng.integers(px, px + TS - 2))
                    img[py - 6:py - 4, bx:bx + 3] = (255, 240, 170)
            else:
                ice = kind == 'ice'
                col = np.array((225, 240, 255.)) if ice else np.array((210, 235, 250.))
                for sx, hh in ((2, 16), (8, 22), (13, 14)):
                    base = py + 16
                    for yy in range(base - hh, base):
                        k = (yy - base + hh) / hh
                        half = max(1, int(k * 4))
                        xa, xb = px + sx - half, px + sx + half
                        xa = max(xa, 0)
                        img[yy, xa:px + sx] = col * (.92 - k * .25)
                        img[yy, px + sx:xb] = col * (.62 - k * .25)
    return glow


def add_glow(img, cx, cy, r, col, strength):
    y0, y1 = max(0, cy - r), min(WH, cy + r)
    x0, x1 = max(0, cx - r), min(WW, cx + r)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    a = np.clip(1 - d, 0, 1) ** 2 * strength
    img[y0:y1, x0:x1] += a[..., None] * np.array(col, float)


def draw_lantern(im, x, y):
    """Standing lantern, feet on the given pixel row."""
    d = ImageDraw.Draw(im, 'RGBA')
    ink = (16, 11, 26, 255)
    d.rectangle((x - 2, y - 26, x + 1, y), fill=(50, 42, 44, 255))
    d.rectangle((x - 6, y - 2, x + 5, y), fill=ink)
    d.polygon([(x - 7, y - 26), (x + 6, y - 26), (x + 4, y - 42), (x - 5, y - 42)], fill=(255, 196, 80, 255), outline=ink)
    d.polygon([(x - 3, y - 28), (x + 2, y - 28), (x + 1, y - 38), (x - 2, y - 38)], fill=(255, 248, 200, 255))
    d.polygon([(x - 8, y - 42), (x + 7, y - 42), (x, y - 50)], fill=(60, 50, 54, 255), outline=ink)


def draw_tablet(im, x, y):
    d = ImageDraw.Draw(im, 'RGBA')
    ink = (16, 11, 26, 255)
    d.polygon([(x - 11, y), (x - 11, y - 26), (x - 6, y - 32), (x + 6, y - 32), (x + 11, y - 26), (x + 11, y)], fill=(118, 116, 132, 255), outline=ink)
    d.polygon([(x - 9, y - 1), (x - 9, y - 25), (x - 5, y - 30), (x - 1, y - 30), (x - 3, y - 1)], fill=(150, 148, 166, 255))
    for k in range(4):
        d.line((x - 6, y - 24 + k * 5, x + 6, y - 24 + k * 5), fill=(50, 46, 66, 255))


def decorate(im, room, theme, rng, mask):
    """Scenery that sits on surfaces: stalactites, crystals, moss, chains, pipes, snow."""
    d = ImageDraw.Draw(im, 'RGBA')
    ink = (16, 11, 26, 255)
    occupied = {(e[1], e[2]) for e in room.ents}
    # hanging from ceilings
    for x in range(1, W.W - 1):
        px = x * TS + 8
        if room.g[0][x] == '#' and room.g[1][x] == '.' and rng.random() < .34:
            h = int(rng.integers(10, 34))
            if theme == 0:
                d.polygon([(px - 6, 16), (px, 16 + h), (px + 6, 16)], fill=(150, 190, 220, 255), outline=ink)
                d.polygon([(px - 3, 17), (px - 1, 16 + h - 6), (px + 1, 17)], fill=(230, 245, 255, 255))
            elif theme == 1:
                d.line((px, 16, px + int(rng.integers(-3, 4)), 16 + h * 2), fill=(70, 130, 96, 255), width=2)
                d.line((px + 3, 16, px + 3, 16 + h), fill=(100, 170, 120, 255), width=1)
            elif theme == 2:
                for k in range(0, h * 2, 6):
                    d.ellipse((px - 2, 16 + k, px + 2, 22 + k), outline=(70, 62, 66, 255))
            else:
                d.polygon([(px - 4, 16), (px, 16 + h), (px + 4, 16)], fill=(220, 236, 255, 255), outline=(120, 130, 180, 255))
    # standing on the ground
    for y in range(2, W.H - 1):
        for x in range(1, W.W - 1):
            if room.g[y][x] == '.' and room.g[y + 1][x] == '#' and (x, y) not in occupied and rng.random() < .16:
                px, py = x * TS + 8, (y + 1) * TS
                k = rng.random()
                if theme == 0:
                    for o, h in ((-4, 12), (1, 19), (6, 10)):
                        d.polygon([(px + o - 3, py), (px + o, py - h), (px + o + 3, py)], fill=(190, 226, 244, 255), outline=ink)
                elif theme == 1:
                    for o in (-5, -1, 3, 6):
                        d.line((px + o, py, px + o + int(rng.integers(-3, 4)), py - rng.integers(6, 15)), fill=(84, 158, 110, 255), width=1)
                elif theme == 2:
                    if k < .5:
                        d.rectangle((px - 7, py - 14, px + 7, py), fill=(84, 70, 66, 255), outline=ink)
                        d.line((px - 7, py - 9, px + 7, py - 9), fill=ink)
                    else:
                        d.polygon([(px - 8, py), (px - 4, py - 9), (px + 3, py - 7), (px + 8, py)], fill=(70, 60, 62, 255), outline=ink)
                else:
                    d.ellipse((px - 9, py - 7, px + 9, py + 3), fill=(236, 240, 252, 255), outline=(150, 156, 196, 255))
    for kind, tx, ty in room.props:
        px, py = tx * TS + 8, (ty + 1) * TS
        if kind == 'tablet':
            draw_tablet(im, px, py)
        elif kind == 'anvil':
            d.polygon([(px - 24, py - 22), (px + 20, py - 22), (px + 30, py - 16), (px + 12, py - 12), (px + 10, py - 4), (px + 16, py), (px - 16, py), (px - 10, py - 4), (px - 12, py - 12)],
                      fill=(70, 66, 80, 255), outline=ink)
        elif kind == 'bigbell':
            d.line((px, 16, px, 34), fill=(70, 60, 54, 255), width=3)
            d.polygon([(px - 8, 34), (px + 8, 34), (px + 20, 58), (px + 30, 84), (px - 30, 84), (px - 20, 58)], fill=(150, 120, 54, 255), outline=ink)
    for e in room.ents:
        if e[0] == W.ENT['LANTERN']:
            draw_lantern(im, e[1] * TS + 8, (e[2] + 1) * TS)


def paint_room(room, index):
    rng = np.random.default_rng(1000 + index * 37)
    theme = room.theme
    th = THEME[theme]
    img = backdrop(theme, rng)
    solid, exact = terrain_mask(room, rng)
    # contact shadow on the backdrop
    ao = ni.gaussian_filter(solid.astype(float), 10)
    img *= (1 - ao * .62)[..., None]
    # textured terrain with lit top edges and a dark interior
    tex = rock_texture(theme, rng)
    inner = ni.distance_transform_edt(solid)
    depth = np.clip(inner / 22, 0, 1)
    shade = (1.05 - depth * .62)[..., None]
    shaded = tex * shade
    # light comes from above: top edges catch it, undersides fall dark
    above = np.roll(solid, 1, axis=0)
    above[0] = True
    below = np.roll(solid, -1, axis=0)
    below[-1] = True
    top_edge = solid & ~above
    top_dist = ni.distance_transform_edt(~top_edge)
    rim = np.array(th['rim'], float)
    rim2 = np.array(th['rim2'], float)
    capw = 5 if theme in (1, 3) else 3
    cap = solid & (top_dist < capw + (noise(rng, WH, WW, 6) * 3))
    bott = solid & (ni.distance_transform_edt(~(solid & ~below)) < 3)
    shaded[bott] *= .55
    mid = solid & (top_dist < capw + 5) & ~cap
    shaded[mid] = shaded[mid] * .55 + rim2 * .45
    shaded[cap] = rim * (.82 + noise(rng, WH, WW, 4)[cap][..., None] * .18)
    # dark outline, in keeping with the inked characters
    outline = solid & (inner < 1.6)
    shaded[outline] = np.array((16, 11, 26), float)
    img[solid] = shaded[solid]

    draw_planks(img, room, theme, rng)
    hz = draw_hazards(img, room, theme, rng)

    im = Image.fromarray(np.clip(img, 0, 255).astype('uint8'))
    decorate(im, room, theme, rng, solid)
    img = np.array(im, float)

    # lights
    if hz.any():
        gl = ni.gaussian_filter(hz, 16)
        img += gl[..., None] * np.array((255, 110, 40), float) * 1.5
    for e in room.ents:
        if e[0] == W.ENT['LANTERN']:
            add_glow(img, e[1] * TS + 8, (e[2] + 1) * TS - 34, 90, (255, 170, 80), .55)
    if theme == 2:
        add_glow(img, WW // 2, WH, 280, (120, 40, 10), .5)
    elif theme == 1:
        add_glow(img, WW // 2, 0, 240, (40, 130, 120), .45)
    elif theme == 3:
        add_glow(img, 60, 40, 220, (90, 90, 170), .4)
    else:
        add_glow(img, WW // 2, 60, 260, (60, 90, 130), .35)
    # soft vignette on each screen
    yy, xx = np.mgrid[0:WH, 0:WW]
    v1 = 1 - .22 * (((xx - 200) / 200) ** 2 + ((np.minimum(yy, 240) - 120) / 120) ** 2) * (yy < 240)
    v2 = 1 - .22 * (((xx - 200) / 160) ** 2 + ((yy - 360) / 120) ** 2) * (yy >= 240)
    img *= (v1 * v2)[..., None]
    return np.clip(img, 0, 255)


BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], float) / 16 - .47


def to565(img):
    """RGB float array to little endian RGB565 with ordered dithering, so gradients do not band."""
    h, w, _ = img.shape
    d = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    r = np.clip(img[:, :, 0] / 8 + d, 0, 31).astype(np.uint16)
    g = np.clip(img[:, :, 1] / 4 + d, 0, 63).astype(np.uint16)
    b = np.clip(img[:, :, 2] / 8 + d, 0, 31).astype(np.uint16)
    return ((r << 11) | (g << 5) | b).astype('<u2')
