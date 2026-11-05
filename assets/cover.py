"""Manuel - the cover: a painted scene across both screens, with Manuel and the bell as animated layers."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage as ni
import ink
from ink import Art, S, poly_rot, tau
import art_manuel as AM
import bake as B

W, H = 400, 480
FONT_LOGO = '/usr/share/fonts/google-noto/NotoSerif-Bold.ttf'
FONT_SUB = '/usr/share/fonts/google-noto/NotoSerif-BoldItalic.ttf'
MOON = (118, 96)
HERO_FEET = (118, 228)   # where Manuel stands, on the belfry ridge


def _radial(cx, cy, r, power=2.0):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    return np.clip(1 - d, 0, 1) ** power


def _silhouette(fill):
    im = Image.new('L', (W, H), 0)
    fill(ImageDraw.Draw(im))
    return np.asarray(im, dtype=np.float32) / 255


def sky(rng):
    y = np.linspace(0, 1, 260)[:, None]
    top, mid, bot = np.array((12, 10, 36.)), np.array((44, 34, 92.)), np.array((130, 84, 128.))
    img = np.zeros((H, W, 3))
    for c in range(3):
        col = np.where(y < .55, top[c] + (mid[c] - top[c]) * (y / .55), mid[c] + (bot[c] - mid[c]) * ((y - .55) / .45))
        img[:260, :, c] = col
        img[260:, :, c] = bot[c]
    # stars, thinning out near the moon and the horizon
    for _ in range(240):
        x, yy = int(rng.integers(0, W)), int(rng.integers(0, 190))
        d = math.hypot(x - MOON[0], yy - MOON[1])
        if d < 90:
            continue
        v = float(rng.uniform(.35, 1)) * (1 - yy / 240)
        img[yy, x] += np.array((210, 210, 255.)) * v
        if v > .72:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= yy + dy < H and 0 <= x + dx < W:
                    img[yy + dy, x + dx] += np.array((150, 150, 220.)) * v * .45
    # moon: huge halo, then the disc with soft maria
    img += _radial(*MOON, 210, 2.2)[..., None] * np.array((110, 92, 150.))
    img += _radial(*MOON, 112, 2.0)[..., None] * np.array((120, 104, 150.))
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - MOON[0]) ** 2 + (yy - MOON[1]) ** 2)
    disc = np.clip(74 - d, 0, 1)
    maria = B.fbm(rng, H, W, (32, 16, 8))
    moonc = np.dstack([236 - maria * 46, 230 - maria * 50, 244 - maria * 38])
    shade = np.clip(1.02 - (d / 74) ** 3 * .22, 0, 1.02)[..., None]
    img = img * (1 - disc[..., None]) + moonc * shade * disc[..., None]
    # thin clouds lit from behind
    n = B.fbm(rng, H, W, (96, 48, 24))
    cl = np.clip((n - .56) * 5, 0, 1) * np.clip(1 - np.abs(np.arange(H)[:, None] - 150) / 95, 0, 1)
    img = img * (1 - cl[..., None] * .55) + (np.array((88, 66, 124.)) + _radial(*MOON, 240, 1.0)[..., None] * np.array((110, 100, 110.))) * cl[..., None] * .55
    return img


def city(img, rng):
    """Two layers of the sleeping Undertown: spires with a few lit windows."""
    for depth, (col, base, hmin, hmax) in enumerate((((72, 54, 110), 240, 34, 92), ((42, 32, 76), 248, 20, 62))):
        im = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(im)
        windows = []
        x = -10
        while x < W + 10:
            w = int(rng.integers(16, 34))
            h = int(rng.integers(hmin, hmax))
            top = base - h
            d.rectangle((x, top, x + w, base + 20), fill=255)
            if rng.random() < .55:
                d.polygon([(x - 2, top), (x + w // 2, top - int(rng.integers(12, 32))), (x + w + 2, top)], fill=255)
            for _ in range(int(rng.integers(0, 4))):
                windows.append((x + int(rng.integers(3, max(4, w - 3))), top + int(rng.integers(5, h))))
            x += w + int(rng.integers(0, 10))
        m = np.asarray(im, dtype=np.float32)[..., None] / 255
        img[:] = img * (1 - m) + np.array(col, float) * m
        for wx, wy in windows:
            if 0 <= wx < W - 1 and 0 <= wy < H - 2:
                img[wy:wy + 2, wx:wx + 2] = (255, 206, 120) if depth else (214, 170, 120)
    return img


def belfry(img, rng):
    """The tower Manuel stands on. Its ridge crosses the seam; the bell chamber fills the lower screen."""
    tex = B.rock_texture(3, rng) * .9
    tex = tex * np.array((.92, .88, 1.06))
    ridge = _silhouette(lambda d: d.polygon([(0, 246), (34, 232), (78, 226), (160, 226), (250, 230), (340, 226), (400, 232), (400, 480), (0, 480)], fill=255))
    # the arch that opens into the bell chamber
    arch = _silhouette(lambda d: (d.rectangle((88, 330, 312, 480), fill=255), d.ellipse((88, 244, 312, 420), fill=255)))
    wall = (ridge > .5) & ~(arch > .5)
    inner = ni.distance_transform_edt(wall)
    # stonework courses
    yy, xx = np.mgrid[0:H, 0:W]
    row = yy // 18
    off = (row % 2) * 20
    mort = ((yy % 18) < 2) | (((xx + off) % 40) < 2)
    t = tex.copy()
    t[mort] *= .5
    shade = (1.12 - np.clip(inner / 40, 0, 1) * .5)[..., None]
    # moonlight from the upper left falls on the top of the ridge
    top_edge = wall & ~np.roll(wall, 1, axis=0)
    td = ni.distance_transform_edt(~top_edge)
    t = t * shade
    cap = wall & (td < 6 + B.noise(rng, H, W, 5) * 5)
    t[cap] = np.array((238, 240, 254.)) * (.8 + B.noise(rng, H, W, 3)[cap][..., None] * .2)
    below = wall & (td >= 6) & (td < 14)
    t[below] *= .72
    img[wall] = t[wall]
    # chamber: warm darkness, a glow rising from below, side lanterns
    ch = arch > .5
    grad = np.clip((yy - 250) / 230, 0, 1)
    room = np.dstack([20 + grad * 26, 13 + grad * 12, 40 + grad * 2])
    back = (B.fbm(rng, H, W, (32, 16)) * .3 + .75)[..., None]
    img[ch] = (room * back)[ch]
    # back wall arches inside the chamber
    pil = Image.fromarray(np.clip(img, 0, 255).astype('uint8'))
    d = ImageDraw.Draw(pil, 'RGBA')
    for x in (128, 200, 272):
        d.arc((x - 34, 280, x + 34, 400), 180, 360, fill=(70, 46, 74, 170), width=5)
        d.rectangle((x - 3, 340, x + 3, 480), fill=(50, 34, 58, 150))
    # the beam the bell hangs from
    d.rectangle((96, 252, 304, 262), fill=(58, 40, 40, 255))
    d.line((96, 252, 304, 252), fill=(120, 88, 72, 255), width=1)
    d.line((96, 262, 304, 262), fill=(20, 14, 26, 255), width=1)
    img = np.array(pil, dtype=float)
    # inked arch edge
    ed = (ch & ~ni.binary_erosion(ch, iterations=2))
    img[ed] = (20, 14, 30)
    img += _radial(200, 520, 250, 2.0)[..., None] * np.array((170, 88, 34.)) * .75 * ch[..., None]
    for lx in (108, 292):
        img += _radial(lx, 380, 74, 2)[..., None] * np.array((255, 170, 80.)) * .7
        pil = Image.fromarray(np.clip(img, 0, 255).astype('uint8'))
        B.draw_lantern(pil, lx, 432)
        img = np.array(pil, dtype=float)
    # moonlight spilling on the ridge around Manuel, and the seam kept dark enough for the logo
    img += _radial(HERO_FEET[0], 214, 130, 2)[..., None] * np.array((60, 50, 80.)) * (wall[..., None])
    return img


def _text_layer(text, font, spacing=0):
    pad = 16
    x = pad
    widths = [font.getlength(c) for c in text]
    w = int(sum(widths) + spacing * (len(text) - 1) + pad * 2)
    asc, desc = font.getmetrics()
    im = Image.new('L', (w, asc + desc + pad * 2), 0)
    d = ImageDraw.Draw(im)
    for c, cw in zip(text, widths):
        d.text((x, pad), c, font=font, fill=255)
        x += cw + spacing
    return np.asarray(im, dtype=np.float32) / 255


def draw_logo(img, cx, y):
    """Gold title with an ink edge, drawn large and reduced; a small flourish under it."""
    k = 4
    m = _text_layer('Manuel', ImageFont.truetype(FONT_LOGO, 40 * k), 2 * k)
    h, w = m.shape
    # vertical metal gradient with a bright horizon line
    ys = np.linspace(0, 1, h)[:, None]
    top, mid, low = np.array((255, 246, 200.)), np.array((244, 196, 92.)), np.array((166, 104, 44.))
    grad = np.where(ys < .52, top + (mid - top) * (ys / .52), low + (mid - low) * (1 - (ys - .52) / .48))
    mb = m > .5
    d = ni.distance_transform_edt(~mb)
    outline = (d <= 3.0 * k)
    drop = np.roll(np.roll(outline, 3 * k, axis=0), 2 * k, axis=1)
    rgba = np.zeros((h, w, 4), dtype=np.float32)
    rgba[drop] = (8, 6, 18, 150)
    rgba[outline] = (22, 14, 32, 255)
    col = np.tile(grad[:, None, :].reshape(h, 1, 3), (1, w, 1))
    inner = ni.distance_transform_edt(mb)
    hi = mb & (inner < 1.0 * k) & np.roll(~mb, 2, axis=0)
    rgba[mb] = np.dstack([col, np.full((h, w), 255.)])[mb]
    rgba[hi] = (255, 252, 230, 255)
    im = Image.fromarray(rgba.astype('uint8'), 'RGBA').convert('RGBa').resize((w // k, h // k), Image.LANCZOS).convert('RGBA')
    x0, y0 = int(cx - im.width / 2), y
    a = np.asarray(im, dtype=float)
    al = a[:, :, 3:4] / 255
    # soft glow behind the letters
    gl = ni.gaussian_filter(a[:, :, 3] / 255, 7)
    yy0, xx0 = max(y0, 0), max(x0, 0)
    sub = img[yy0:yy0 + a.shape[0], xx0:xx0 + a.shape[1]]
    aa = a[:sub.shape[0], :sub.shape[1]]
    sub += gl[:sub.shape[0], :sub.shape[1], None] * np.array((150, 104, 60.)) * .55
    al = al[:sub.shape[0], :sub.shape[1]]
    sub[:] = sub * (1 - al) + aa[:, :, :3] * al
    # subtitle with a thin rule on each side
    m2 = _text_layer('and the Last Bell', ImageFont.truetype(FONT_SUB, 15 * k), 0)
    h2, w2 = m2.shape
    outl = ni.distance_transform_edt(m2 <= .5) <= 1.5 * k
    rg = np.zeros((h2, w2, 4), dtype=np.float32)
    rg[outl] = (18, 12, 30, 255)
    rg[m2 > .5] = (232, 220, 248, 255)
    s2 = Image.fromarray(rg.astype('uint8'), 'RGBA').convert('RGBa').resize((w2 // k, h2 // k), Image.LANCZOS).convert('RGBA')
    pil = Image.fromarray(np.clip(img, 0, 255).astype('uint8')).convert('RGBA')
    sy = y + im.height - 21
    pil.alpha_composite(s2, (int(cx - s2.width / 2), sy))
    d = ImageDraw.Draw(pil)
    ry = sy + s2.height - 3
    for sgn in (-1, 1):
        d.line((cx + sgn * 8, ry, cx + sgn * 62, ry), fill=(236, 190, 96, 255), width=1)
    d.polygon([(cx, ry - 4), (cx + 4, ry), (cx, ry + 4), (cx - 4, ry)], fill=(255, 226, 150, 255))
    return np.array(pil.convert('RGB'), dtype=float)


def paint(with_logo=True):
    rng = np.random.default_rng(4242)
    img = sky(rng)
    img = city(img, rng)
    hz = np.clip(1 - np.abs(np.arange(H)[:, None] - 214) / 34, 0, 1) ** 1.5
    img += (hz * _radial(HERO_FEET[0], 214, 190, 1.0))[..., None] * np.array((190, 150, 190.))
    img = belfry(img, rng)
    if with_logo:
        img = draw_logo(img, 300, 92)
    # a little atmosphere and a vignette per screen
    yy, xx = np.mgrid[0:H, 0:W]
    v1 = 1 - .26 * (((xx - 200) / 200) ** 2 + ((np.minimum(yy, 240) - 120) / 120) ** 2) * (yy < 240)
    v2 = 1 - .30 * (((xx - 200) / 160) ** 2 + ((yy - 360) / 120) ** 2) * (yy >= 240)
    return np.clip(img * (v1 * v2)[..., None], 0, 255)


def _big(fn, scale=2, ss=10):
    """Renders with the inking engine at a much finer grid, so a large sprite stays crisp."""
    old = ink.SS
    ink.SS = ss
    try:
        a = fn()
    finally:
        ink.SS = old
    return a


def _reduce(a, scale):
    h, w = a.h, a.w
    px = a.px
    al = px[:, :, 3:4] / 255
    rgb = np.where(al > 0, px[:, :, :3] / np.maximum(al, 1e-3), 0)
    arr = np.dstack([rgb, px[:, :, 3]]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA').convert('RGBa').resize((w * scale, h * scale), Image.LANCZOS).convert('RGBA')


def moon_rim(im):
    """Backlight: a pale line on edges that face the moon."""
    a = np.asarray(im, dtype=np.float32).copy()
    al = a[:, :, 3] > 120
    edge = al & ~np.roll(np.roll(al, 2, axis=0), 1, axis=1)
    a[edge, :3] = a[edge, :3] * .45 + np.array((236, 226, 255.)) * .55
    return Image.fromarray(a.astype('uint8'), 'RGBA')


def hero_frames():
    """Manuel on the ridge in the wind: six frames of cloak and breath, with one blink."""
    out = []
    for i in range(6):
        t = i / 6
        def draw():
            return _pose(t, eye=.07 if i == 4 else 1.0)
        out.append(moon_rim(_reduce(_big(draw), 2)))
    return out


def _pose(t, eye):
    AM_Art = AM.Art
    captured = {}

    class Keep(AM_Art):
        def done(self):
            captured['a'] = self
            return None
    AM.Art = Keep
    try:
        AM.pose(leg_l=(-12, 0), leg_r=(13, 0), bob=tau(t) * .7, lean=1.5, sway=6 + tau(t) * 2.4, ripple=2.0, phase=t, axe=-58 + tau(t + .1) * 1.2,
                axe_front=False, head_dx=.5, head_dy=tau(t - .12) * .5, rot=tau(t) * .5, eye=eye, mood=.5, reach=1.0)
    finally:
        AM.Art = AM_Art
    return captured['a']


def bell_frames():
    out = []
    for i in range(4):
        r = tau(i / 4) * 2.2
        def draw():
            a = Art(84, 74)
            R = lambda pts: poly_rot(pts, 42, 0, r)
            GOLD, GL, GS = (190, 146, 70), (246, 214, 136), (106, 74, 42)
            h = a.part(1.2)
            h.fill(R([S(39, 0), S(45, 0), S(45, 9), S(39, 9)]), (70, 56, 52), smooth=False)
            a.add(h)
            p = a.part(1.8)
            p.fill(R([S(34, 7), S(50, 7), (60, 22), (66, 44), S(77, 60), S(7, 60), (18, 44), (24, 22)]), GOLD)
            p.cel(GS, 5, 5).rim(GL, -1.6, -1.8)
            p.shade(R([S(12, 53), S(72, 53), S(77, 60), S(7, 60)]), (120, 84, 46))
            p.line(R([(19, 40), (42, 44), (65, 40)]), GS, 1.0)
            p.line(R([(23, 27), (42, 30), (61, 27)]), GS, .8)
            a.add(p)
            c = a.part(1.2)
            q = R([(42 + r * 1.2, 66)])[0]
            c.circle(q[0], q[1], 5.2, col=(92, 68, 44))
            c.cel((58, 42, 30), 1.4, 1.6)
            a.add(c)
            return a
        im = _reduce(_big(draw), 2)
        out.append(im.resize((int(im.width * .8), int(im.height * .8)), Image.LANCZOS))
    return out


def composite(bg, hero):
    im = Image.fromarray(bg.astype('uint8')).convert('RGBA')
    im.alpha_composite(hero, (HERO_FEET[0] - AM.AX * 2, HERO_FEET[1] - AM.AY * 2))
    return im


def icon(hero):
    """HOME Menu icon: Manuel's face and shoulders over the moon."""
    bg = Image.new('RGBA', (48, 48), (20, 16, 50, 255))
    px = bg.load()
    for y in range(48):
        for x in range(48):
            d = math.hypot(x - 24, y - 20) / 34
            k = max(0, 1 - d) ** 1.4
            px[x, y] = (int(22 + 150 * k), int(16 + 130 * k), int(52 + 150 * k), 255)
    box = hero.getbbox()
    size = 182
    crop = hero.crop((box[0] + 2, box[1] - 4, box[0] + 2 + size, box[1] - 4 + size))
    small = crop.resize((48, 48), Image.LANCZOS)
    bg.alpha_composite(small)
    return bg
