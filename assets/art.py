"""Menuel - character art. Everything is drawn large with ink outlines, then reduced to smooth game-size frames."""
import math
from PIL import Image, ImageDraw

SS = 4  # supersampling factor
INK = (16, 11, 26, 255)


class Pen:
    """Drawing surface in final-pixel coordinates; the image is reduced by SS at the end."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def _pts(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def poly(self, pts, fill, ink=1.2):
        p = self._pts(pts)
        self.d.polygon(p, fill=fill)
        if ink:
            self.d.line(p + p[:2], fill=INK, width=max(1, int(ink * SS)), joint='curve')

    def flat(self, pts, fill):
        self.d.polygon(self._pts(pts), fill=fill)

    def line(self, pts, col=INK, w=1.2):
        self.d.line(self._pts(pts), fill=col, width=max(1, int(w * SS)), joint='curve')

    def disc(self, x, y, rx, ry=None, fill=INK, ink=0):
        ry = rx if ry is None else ry
        box = ((x - rx) * SS, (y - ry) * SS, (x + rx) * SS, (y + ry) * SS)
        self.d.ellipse(box, fill=fill, outline=INK if ink else None, width=max(1, int(ink * SS)) if ink else 0)

    def arc(self, x, y, r, a0, a1, col, w):
        box = ((x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS)
        self.d.arc(box, a0, a1, fill=col, width=max(1, int(w * SS)))

    def done(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def rot(pts, cx, cy, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def C(r, g, b, a=255):
    return (r, g, b, a)


# ------------------------------------------------------------------ Menuel, after the user's drawing
MASK = C(238, 230, 252)
MASK_S = C(205, 190, 232)
GEM = C(196, 176, 232)
CLOAK = C(104, 82, 146)
CLOAK_L = C(132, 108, 172)
CLOAK_D = C(62, 50, 104)
BLADE = C(150, 116, 156)
BLADE_L = C(186, 152, 190)
BLADE_D = C(112, 84, 122)
HANDLE = C(52, 38, 62)
POMMEL = C(120, 130, 160)


def draw_axe(p, hx, hy, deg, reach=1.0):
    """Long pole with a big flag-like blade at the far end and a small steel butt, pivoting at the hand."""
    def R(pts):
        return rot(pts, hx, hy, deg)
    L0, L1 = -15 * reach, 25 * reach
    p.poly(R([(hx + L0, hy - 1.2), (hx + L1, hy - 1.2), (hx + L1, hy + 1.2), (hx + L0, hy + 1.2)]), HANDLE, 0.8)
    p.poly(R([(hx + L0 - 4, hy), (hx + L0, hy - 2.4), (hx + L0 + 1, hy + 2.4)]), POMMEL, 0.9)
    b = hx + L1 - 3
    blade = [(b, hy - 1), (b + 3, hy - 17), (b + 20, hy - 20), (b + 23, hy - 1), (b + 20, hy + 2), (b + 2, hy + 4)]
    p.poly(R(blade), BLADE, 1.4)
    p.flat(R([(b + 4, hy - 16), (b + 20, hy - 18.5), (b + 21.5, hy - 12), (b + 5, hy - 10)]), BLADE_L)
    p.flat(R([(b + 3, hy + 2.6), (b + 20, hy + 0.8), (b + 21.5, hy - 3), (b + 3, hy - 1)]), BLADE_D)
    p.line(R([(b + 3, hy - 17), (b + 20, hy - 20)]), C(226, 206, 226), 0.7)


def menuel(leg_a=0.0, leg_b=0.0, bob=0.0, sway=0.0, lean=0.0, axe=None, axe_front=False, squash=0.0, eye=1.0, tuck=0.0):
    """128x128 canvas, feet at y=92, body centred on x=64, facing right. Proportions follow the drawing:
    a huge kite mask, a short jagged cloak and two long black spikes for legs."""
    p = Pen(128, 128)
    cx, feet = 64.0, 92.0
    hip = feet - 19 - tuck + bob + squash
    if axe is not None and not axe_front:
        draw_axe(p, cx + 6 + lean, hip - 8, axe)
    # legs: long black spikes, clearly visible under the hem
    for off, a in ((-6, leg_a), (6, leg_b)):
        lift = abs(a) * 0.3
        p.flat([(cx + off - 3.4, hip - 8), (cx + off + 3.4, hip - 8), (cx + off + a, feet - lift)], INK)
    # cloak with jagged hem and collar
    y = hip - 22
    t = sway
    pts = [(cx - 8 + lean, y), (cx - 19 + lean - t, y + 1), (cx - 13 + lean, y + 5), (cx - 22 + lean - t * 1.4, y + 10),
           (cx - 14 + lean, y + 11), (cx - 19 + lean - t, y + 17), (cx - 9 + lean, y + 15), (cx - 7 + lean - t * .4, y + 21),
           (cx - 2 + lean, y + 16), (cx + 2 + lean - t * .3, y + 21), (cx + 6 + lean, y + 15), (cx + 12 + lean - t * .6, y + 19),
           (cx + 13 + lean, y + 13), (cx + 22 + lean + t * .4, y + 13), (cx + 15 + lean, y + 7), (cx + 21 + lean + t * .4, y + 2),
           (cx + 8 + lean, y)]
    p.poly(pts, CLOAK, 1.5)
    # dark sweep across the cloak, as in the drawing
    p.flat([(cx - 20 + lean - t, y + 10), (cx + 10 + lean, y + 1), (cx + 15 + lean, y + 6), (cx - 14 + lean, y + 15)], CLOAK_D)
    p.flat([(cx - 12 + lean, y + 3), (cx - 3 + lean, y + 1), (cx - 9 + lean, y + 6)], CLOAK_L)
    # stitch and small mark
    p.line([(cx - 11 + lean, y + 5), (cx - 7 + lean, y + 9)], INK, .8)
    p.line([(cx - 7 + lean, y + 5), (cx - 11 + lean, y + 9)], INK, .8)
    p.line([(cx + 1 + lean, y + 11), (cx + 4 + lean, y + 13), (cx + 7 + lean, y + 10)], INK, .9)
    # kite mask, big as in the drawing
    top = hip - 55 + squash * .6
    hx = cx + lean * 1.3
    head = [(hx, top), (hx + 18, top + 25 - squash * .4), (hx + 2, top + 38), (hx - 2, top + 38), (hx - 18, top + 25 - squash * .4)]
    p.poly(head, MASK, 1.7)
    p.flat([(hx + 16, top + 26), (hx + 2, top + 36.5), (hx - 4, top + 36), (hx + 4, top + 27)], MASK_S)
    # slit eyes tilting inward
    ey = top + 22
    for s in (-1, 1):
        ex = hx + s * 8.5
        h = 2.6 * eye + .3
        p.flat([(ex + s * 5, ey - h), (ex - s * 4.2, ey + h * .5), (ex - s * 3, ey + h + 1.7), (ex + s * 4.2, ey + h * .2)], INK)
    # forehead gem
    p.flat([(hx + 5, top + 9), (hx + 8.5, top + 13), (hx + 5.5, top + 18), (hx + 2, top + 13)], GEM)
    if axe is not None and axe_front:
        draw_axe(p, cx + 6 + lean, hip - 8, axe)
    return p.done()


def player_frames():
    F = {}
    for i in range(4):                      # idle: slow breathing, cloak drifting
        s = math.sin(i * math.pi / 2)
        F['IDLE%d' % i] = menuel(0, 0, s * .8, s * 1.0, axe=-52 + s * 2)
    for i in range(8):                      # run: long stride, cloak trailing
        a = math.sin(i * math.pi / 4)
        b = abs(math.cos(i * math.pi / 4))
        F['RUN%d' % i] = menuel(a * 7, -a * 7, -b * 1.5, 3 + b * 2, lean=2.5, axe=-40 + a * 7)
    F['RISE'] = menuel(-3, 4, -1, -2, lean=1, axe=-68, tuck=3)
    F['FALL'] = menuel(4, -4, 0, 5, lean=0, axe=-30, tuck=1)
    # swing: windup, then a big arc over the head and through
    for i, ang in enumerate((-125, -85, -30, 15, 40)):
        F['ATK%d' % i] = menuel(5, -4, 0, 2 + i * .4, lean=2 + min(i, 2) * 1.2, axe=ang, axe_front=i >= 2)
    F['DASH0'] = menuel(9, -9, 1, 9, lean=7, axe=-8, tuck=4)
    F['DASH1'] = menuel(10, -10, 2, 11, lean=9, axe=-4, tuck=5)
    F['HURT'] = menuel(-6, 5, 0, -5, lean=-4, axe=-110, eye=.2)
    F['HEAL0'] = menuel(0, 0, 3, 2, axe=-90, squash=2, eye=.3)
    F['HEAL1'] = menuel(0, 0, 3.8, -2, axe=-90, squash=2.6, eye=.3)
    F['HOOK'] = menuel(-5, 5, -2, 6, lean=3, axe=-70, tuck=2)
    F['CLEAVE0'] = menuel(-3, 3, -2, -5, lean=1, axe=70, axe_front=True, tuck=4)
    F['CLEAVE1'] = menuel(-2, 2, -2, -7, lean=0, axe=92, axe_front=True, tuck=5)
    return F


# ------------------------------------------------------------------ enemies, 56x48, feet at the bottom
def e_salt_mite(t):
    p = Pen(56, 48)
    k = math.sin(t * math.tau)
    for i, x in enumerate((14, 24, 34, 42)):
        o = k * 3 * (1 if i % 2 else -1)
        p.line([(x, 34), (x + o - 3, 46)], INK, 2)
    p.poly([(6, 38), (9, 22), (20, 12 + k), (37, 12 + k), (49, 24), (50, 38), (28, 42)], C(112, 136, 170), 1.5)
    for x, h, w in ((16, 22, 5), (27, 27, 6), (38, 19, 5)):
        p.poly([(x - w, 20), (x - 1, 20 - h + k), (x + w, 20)], C(226, 244, 252), 1.2)
        p.flat([(x, 19), (x - 1, 20 - h + 3 + k), (x + w - 1, 19)], C(170, 206, 228))
    p.disc(44, 28, 3.4, fill=C(250, 240, 180), ink=1)
    p.disc(45, 28, 1.3, fill=INK)
    return p.done()


def e_dust_moth(t):
    p = Pen(56, 48)
    a = math.sin(t * math.tau) * 12
    wing = C(176, 150, 106)
    for s in (-1, 1):
        p.poly([(28, 22), (28 + s * 24, 6 - a), (28 + s * 26, 22 - a * .6), (28 + s * 14, 32)], wing, 1.4)
        p.flat([(28 + s * 6, 21), (28 + s * 20, 11 - a), (28 + s * 21, 20 - a * .6), (28 + s * 11, 27)], C(218, 194, 146))
        p.disc(28 + s * 16, 18 - a * .7, 3, fill=C(90, 62, 50))
    p.poly([(23, 15), (33, 15), (32, 36), (28, 42), (24, 36)], C(92, 72, 58), 1.3)
    p.disc(25, 18, 2, fill=C(250, 230, 150)); p.disc(31, 18, 2, fill=C(250, 230, 150))
    p.line([(25, 15), (20, 7)], INK, 1); p.line([(31, 15), (36, 7)], INK, 1)
    return p.done()


def e_bog_frog(t):
    p = Pen(56, 48)
    if t < .5:
        k = math.sin(t * 2 * math.tau) * 1.5
        p.poly([(5, 47), (7, 30), (16, 18 + k), (40, 18 + k), (50, 30), (52, 47)], C(62, 124, 96), 1.5)
        p.flat([(12, 44), (16, 34), (40, 34), (46, 44)], C(170, 206, 152))
        p.line([(10, 31), (28, 36), (47, 30)], INK, 1.3)
        for x in (18, 38):
            p.disc(x, 17 + k, 6.5, fill=C(226, 238, 164), ink=1.2); p.disc(x + 1, 17 + k, 3, fill=INK)
    else:
        p.poly([(2, 34), (12, 12), (34, 6), (52, 16), (42, 32), (18, 38)], C(62, 124, 96), 1.5)
        p.line([(12, 34), (2, 46)], INK, 3); p.line([(40, 30), (52, 44)], INK, 3)
        p.disc(40, 9, 6, fill=C(226, 238, 164), ink=1.2); p.disc(42, 9, 2.8, fill=INK)
    return p.done()


def e_bell_fish(t):
    p = Pen(56, 48)
    k = math.sin(t * math.tau) * 2.5
    p.line([(28, 0), (28, 8)], C(90, 80, 66), 2)
    p.poly([(23, 7), (33, 7), (41, 19), (46, 34), (10, 34), (15, 19)], C(182, 146, 66), 1.5)
    p.flat([(18, 18), (24, 9), (27, 9), (22, 32), (13, 32)], C(232, 204, 116))
    p.poly([(7, 33), (49, 33), (49, 37), (7, 37)], C(112, 88, 44), 1.2)
    p.disc(22, 22, 3, fill=C(20, 40, 44)); p.disc(34, 22, 3, fill=C(20, 40, 44))
    p.disc(28 + k, 41, 4.5, fill=C(92, 70, 40), ink=1.1)
    return p.done()


def e_cinder_beetle(t):
    p = Pen(56, 48)
    k = math.sin(t * math.tau)
    for i, x in enumerate((13, 27, 41)):
        p.line([(x, 34), (x + (k * 4 if i % 2 else -k * 4), 47)], INK, 2.2)
    p.poly([(3, 36), (6, 21), (24, 8), (42, 12), (53, 26), (54, 36), (30, 40)], C(70, 44, 42), 1.6)
    p.line([(26, 8), (30, 40)], INK, 1.6)
    for x, y in ((14, 25), (20, 16), (38, 22), (44, 30), (35, 32), (13, 33)):
        p.disc(x, y, 2.6, fill=C(255, 150 + int(k * 40), 40))
    p.poly([(46, 20), (56, 15), (53, 27)], C(52, 32, 32), 1.1)
    p.disc(46, 28, 2.5, fill=C(255, 226, 120))
    return p.done()


def e_furnace_mouth(t):
    p = Pen(56, 48)
    k = (math.sin(t * math.tau) + 1) / 2
    p.poly([(8, 47), (8, 13), (16, 4), (40, 4), (48, 13), (48, 47)], C(88, 78, 84), 1.6)
    p.flat([(11, 44), (11, 15), (17, 8), (22, 8), (17, 44)], C(124, 114, 118))
    p.poly([(14, 20 - k * 3), (42, 20 - k * 3), (42, 40), (14, 40)], C(255, int(130 + k * 80), 36), 1.4)
    p.flat([(18, 28), (38, 28), (38, 40), (18, 40)], C(255, 236, 150))
    for x in (18, 26, 34):
        p.poly([(x - 3, 20 - k * 3), (x + 4, 20 - k * 3), (x + .5, 27 - k * 3)], C(226, 226, 220), .9)
    for x in (16, 28, 40):
        p.disc(x, 9, 1.8, fill=C(40, 34, 40))
    return p.done()


def e_hush_wraith(t):
    p = Pen(56, 48)
    k = math.sin(t * math.tau) * 3
    p.poly([(28, 1), (43, 12), (46, 30), (41 + k, 47), (35, 37), (28 - k, 47), (22, 37), (15 + k, 47), (10, 30), (13, 12)], C(96, 82, 156), 1.5)
    p.flat([(16, 14), (26, 5), (24, 40), (17, 42), (13, 30)], C(132, 118, 190))
    p.poly([(28, 8), (39, 20), (28, 32), (17, 20)], C(234, 228, 250), 1.3)
    p.line([(22, 19), (26, 22)], INK, 1.8); p.line([(34, 19), (30, 22)], INK, 1.8)
    return p.done()


def e_snow_hare(t):
    p = Pen(56, 48)
    if t < .5:
        k = math.sin(t * 2 * math.tau)
        p.poly([(8, 47), (10, 28), (24, 20), (42, 26), (48, 47)], C(232, 236, 250), 1.5)
        p.poly([(26, 22), (22, 1 + k), (30, 1 + k), (34, 22)], C(232, 236, 250), 1.3)
        p.poly([(36, 24), (37, 4 - k), (44, 6 - k), (42, 26)], C(232, 236, 250), 1.3)
        p.flat([(27, 19), (25, 6), (28, 6), (31, 19)], C(214, 170, 196))
        p.disc(39, 32, 2.4, fill=C(70, 30, 70))
    else:
        p.poly([(2, 30), (16, 14), (38, 12), (54, 24), (40, 34), (14, 38)], C(232, 236, 250), 1.5)
        p.poly([(24, 16), (10, 2), (18, 0), (34, 14)], C(232, 236, 250), 1.2)
        p.line([(14, 36), (3, 46)], INK, 2.8); p.line([(40, 33), (52, 46)], INK, 2.8)
        p.disc(44, 22, 2.2, fill=C(70, 30, 70))
    return p.done()


ENEMY_ART = [e_salt_mite, e_dust_moth, e_bog_frog, e_bell_fish, e_cinder_beetle, e_furnace_mouth, e_hush_wraith, e_snow_hare]


# ------------------------------------------------------------------ NPCs, 64x64, feet at the bottom
def npc_ringer(t):
    p = Pen(64, 64)
    k = math.sin(t * math.tau) * 1.2
    p.line([(47, 8), (47, 64)], C(70, 50, 36), 2.4)
    p.poly([(42, 7), (47, 2), (52, 7), (54, 14), (40, 14)], C(214, 178, 88), 1.2)
    p.poly([(16, 64), (19, 32), (28, 22), (38, 22), (46, 34), (49, 64)], C(112, 96, 86), 1.5)
    p.flat([(20, 62), (22, 34), (29, 26), (28, 62)], C(146, 128, 112))
    p.poly([(22, 28 + k), (33, 10 + k), (44, 28 + k), (33, 34 + k)], C(232, 220, 196), 1.4)
    p.flat([(27, 22 + k), (31, 22 + k), (31, 24 + k), (27, 24 + k)], INK)
    p.flat([(36, 22 + k), (40, 22 + k), (40, 24 + k), (36, 24 + k)], INK)
    return p.done()


def npc_miner(t):
    p = Pen(64, 64)
    k = math.sin(t * math.tau)
    p.poly([(14, 64), (15, 34), (24, 28), (42, 28), (51, 36), (50, 64)], C(96, 82, 70), 1.5)
    p.flat([(25, 42), (40, 42), (40, 64), (25, 64)], C(148, 132, 104))
    p.poly([(20, 12 + k), (46, 12 + k), (48, 32 + k), (18, 32 + k)], C(230, 214, 188), 1.4)
    p.disc(27, 22 + k, 2.3, fill=INK); p.disc(39, 22 + k, 2.3, fill=INK)
    p.poly([(15, 13 + k), (22, 3 + k), (44, 3 + k), (51, 13 + k)], C(214, 160, 60), 1.4)
    p.disc(33, 7 + k, 4, fill=C(255, 244, 170), ink=1)
    p.line([(52, 30), (60, 60)], C(66, 50, 40), 2.4)
    p.poly([(46, 30), (60, 24), (61, 28), (51, 34)], C(150, 160, 176), 1)
    return p.done()


def npc_clerk(t):
    p = Pen(64, 64)
    k = math.sin(t * math.tau) * 1.2
    p.poly([(10, 64), (15, 36), (49, 36), (54, 64)], C(52, 92, 100), 1.5)
    p.disc(32, 22 + k, 18, fill=C(186, 226, 200), ink=1.4)
    p.disc(25, 21 + k, 5, fill=C(240, 246, 220), ink=1); p.disc(39, 21 + k, 5, fill=C(240, 246, 220), ink=1)
    p.disc(25, 21 + k, 1.6, fill=INK); p.disc(39, 21 + k, 1.6, fill=INK)
    p.line([(30, 21 + k), (34, 21 + k)], INK, 1)
    p.poly([(38, 44), (56, 42), (58, 60), (40, 62)], C(226, 216, 180), 1.2)
    p.line([(42, 49), (53, 48)], C(90, 90, 90), .8); p.line([(43, 54), (54, 53)], C(90, 90, 90), .8)
    return p.done()


def npc_smith(t):
    p = Pen(64, 64)
    k = math.sin(t * math.tau)
    p.poly([(8, 64), (10, 32), (22, 24), (44, 24), (56, 32), (56, 64)], C(112, 68, 48), 1.6)
    p.poly([(20, 34), (46, 34), (46, 64), (20, 64)], C(66, 54, 54), 1.2)
    p.disc(32, 16 + k, 13, fill=C(214, 160, 120), ink=1.4)
    p.flat([(22, 19 + k), (43, 19 + k), (39, 30 + k), (26, 30 + k)], C(230, 110, 40))
    p.line([(25, 14 + k), (29, 16 + k)], INK, 1.5); p.line([(39, 14 + k), (35, 16 + k)], INK, 1.5)
    p.line([(55, 34), (58, 10 + k)], C(60, 44, 36), 3)
    p.poly([(50, 8 + k), (63, 7 + k), (63, 15 + k), (50, 16 + k)], C(150, 150, 164), 1.1)
    return p.done()


def npc_hermit(t):
    p = Pen(64, 64)
    k = math.sin(t * math.tau) * 1.5
    p.poly([(12, 64), (16, 28), (32, 8 + k), (48, 28), (52, 64), (42, 60), (32, 64), (22, 60)], C(204, 212, 236), 1.6)
    p.flat([(18, 58), (20, 30), (32, 14 + k), (28, 60)], C(236, 240, 252))
    p.poly([(23, 30 + k), (41, 30 + k), (37, 40 + k), (27, 40 + k)], C(30, 26, 54), 1.2)
    p.disc(29, 34 + k, 1.3, fill=C(190, 220, 255)); p.disc(35, 34 + k, 1.3, fill=C(190, 220, 255))
    return p.done()


NPC_ART = [npc_ringer, npc_miner, npc_clerk, npc_smith, npc_hermit]


# ------------------------------------------------------------------ bosses, 128x128, feet at the bottom
# f: 0,1 idle  2 windup  3 attack  4 airborne  5 stunned
def _f(f):
    return dict(dy=(0, 2, 6, -2, -6, 10)[f], arm=(0, 8, -45, 40, -20, 60)[f], eye=(1, 1, 1.3, 1.4, 1, .25)[f])


def boss_foreman(f):
    """Salt Foreman: a huge miner under a crust of salt crystals, still swinging his pick."""
    p = Pen(128, 128)
    v = _f(f)
    dy = v['dy']
    for x in (42, 72):
        p.poly([(x, 96 + dy), (x + 16, 96 + dy), (x + 18, 127), (x - 3, 127)], C(46, 40, 54), 1.6)
    # pick behind
    ax, ay = 104, 66 + dy
    a = v['arm']
    p.line(rot([(ax, ay), (ax + 8, ay - 54)], ax, ay, a), C(64, 48, 40), 5)
    p.poly(rot([(ax - 18, ay - 50), (ax + 8, ay - 62), (ax + 34, ay - 46), (ax + 8, ay - 52)], ax, ay, a), C(170, 184, 204), 1.6)
    p.poly([(16, 104 + dy), (12, 56 + dy), (30, 28 + dy), (96, 28 + dy), (116, 58 + dy), (112, 104 + dy)], C(86, 104, 140), 2)
    p.flat([(22, 98 + dy), (20, 58 + dy), (36, 36 + dy), (54, 36 + dy), (42, 98 + dy)], C(116, 136, 172))
    for x, h, w in ((30, 28, 9), (50, 40, 11), (72, 34, 10), (93, 26, 9)):
        p.poly([(x - w, 34 + dy), (x, 34 + dy - h), (x + w, 34 + dy)], C(226, 244, 252), 1.6)
        p.flat([(x, 33 + dy), (x, 34 + dy - h + 5), (x + w - 2, 33 + dy)], C(164, 204, 228))
    p.poly([(38, 54 + dy), (90, 54 + dy), (86, 84 + dy), (42, 84 + dy)], C(226, 212, 184), 1.8)
    e = 3.2 * v['eye']
    p.flat([(48, 66 + dy - e), (60, 66 + dy), (60, 66 + dy + e), (48, 66 + dy + e)], INK)
    p.flat([(80, 66 + dy - e), (68, 66 + dy), (68, 66 + dy + e), (80, 66 + dy + e)], INK)
    p.line([(54, 78 + dy), (74, 78 + dy)], INK, 2)
    p.poly([(96, 56 + dy), (116, 62 + dy), (108, 78 + dy), (92, 74 + dy)], C(86, 104, 140), 1.7)
    return p.done()


def boss_rope(f):
    """Rope Drowned: a bloated, pale figure bound in the bell rope that drowned it."""
    p = Pen(128, 128)
    v = _f(f)
    dy = v['dy']
    p.line([(64, 0), (64, 22 + dy)], C(170, 150, 96), 5)
    p.disc(64, 66 + dy, 50, 46, fill=C(70, 132, 128), ink=2)
    p.disc(50, 56 + dy, 28, 26, fill=C(106, 170, 156))
    for i in range(5):
        y = 34 + i * 16 + dy
        p.line([(22, y), (106, y + 9)], C(60, 44, 30), 7)
        p.line([(22, y - 1), (106, y + 8)], C(210, 186, 120), 4)
    p.disc(64, 48 + dy, 25, 21, fill=C(216, 232, 208), ink=2)
    e = 4.2 * v['eye']
    p.disc(54, 46 + dy, 5, e + 1, fill=C(20, 40, 44)); p.disc(74, 46 + dy, 5, e + 1, fill=C(20, 40, 44))
    p.disc(64, 60 + dy, 6, 3 + v['eye'] * 2, fill=C(20, 40, 44))
    s = {3: 18, 4: -8}.get(f, 0)
    for x, o in ((20, -6), (108, 6)):
        p.line([(x, 76 + dy), (x + o - s * (1 if x < 64 else -1), 118)], C(70, 132, 128), 11)
        p.line([(x, 76 + dy), (x + o - s * (1 if x < 64 else -1), 118)], C(106, 170, 156), 5)
    for x in (42, 64, 86):
        p.line([(x, 108 + dy), (x + (f % 2) * 4 - 2, 127)], C(210, 186, 120), 3.5)
    return p.done()


def boss_founder(f):
    """Two-Headed Founder: two bickering heads on one leather apron, with a ladle of molten metal."""
    p = Pen(128, 128)
    v = _f(f)
    dy = v['dy']
    for x in (36, 74):
        p.poly([(x, 100 + dy), (x + 18, 100 + dy), (x + 20, 127), (x - 3, 127)], C(40, 30, 30), 1.6)
    p.poly([(20, 106 + dy), (22, 52 + dy), (106, 52 + dy), (110, 106 + dy)], C(170, 92, 54), 2)
    p.poly([(40, 60 + dy), (88, 60 + dy), (94, 112 + dy), (34, 112 + dy)], C(82, 56, 44), 1.8)
    p.flat([(44, 66 + dy), (56, 66 + dy), (50, 108 + dy), (40, 108 + dy)], C(112, 80, 60))
    for hx, tilt, c in ((40, -6, C(232, 176, 128)), (88, 6, C(222, 158, 110))):
        o = (f % 2) * 2
        p.disc(hx, 34 + dy + o, 21, 22, fill=c, ink=2)
        e = 2.8 * v['eye']
        p.line([(hx - 12, 27 + dy + o + tilt / 3), (hx - 3, 30 + dy + o)], INK, 2)
        p.line([(hx + 12, 27 + dy + o - tilt / 3), (hx + 3, 30 + dy + o)], INK, 2)
        p.disc(hx - 7, 35 + dy + o, 2.8, e, fill=INK); p.disc(hx + 7, 35 + dy + o, 2.8, e, fill=INK)
        p.disc(hx, 46 + dy + o, 7, 3 + (f == 3) * 3, fill=INK)
    ax, ay = 110, 72 + dy
    a = v['arm']
    p.line(rot([(ax, ay), (ax + 10, ay + 38)], ax, ay, -a), C(56, 44, 44), 5)
    cx, cy = rot([(ax + 12, ay + 44)], ax, ay, -a)[0]
    p.disc(cx, cy, 11, fill=C(84, 78, 88), ink=1.6)
    p.disc(cx, cy - 2, 7, 5, fill=C(255, 170, 40))
    p.disc(cx - 2, cy - 3, 3, 2, fill=C(255, 240, 150))
    return p.done()


def boss_anvil(f):
    """The Anvil: a walking anvil of black iron with forge fire behind its visor."""
    p = Pen(128, 128)
    v = _f(f)
    dy = v['dy']
    if f != 4:
        for x in (32, 78):
            p.poly([(x, 100 + dy / 2), (x + 20, 100 + dy / 2), (x + 24, 127), (x - 4, 127)], C(38, 34, 42), 1.8)
    p.poly([(2, 26 + dy), (88, 26 + dy), (125, 36 + dy), (92, 50 + dy), (84, 70 + dy), (98, 106 + dy), (28, 106 + dy), (44, 70 + dy), (30, 50 + dy)],
           C(80, 76, 90), 2.2)
    p.flat([(6, 28 + dy), (88, 28 + dy), (112, 35 + dy), (86, 38 + dy), (22, 38 + dy)], C(150, 146, 162))
    p.flat([(36, 94 + dy), (50, 72 + dy), (60, 72 + dy), (44, 104 + dy)], C(106, 102, 116))
    e = 7 * v['eye']
    p.poly([(44, 54 + dy), (84, 54 + dy), (80, 54 + dy + e + 6), (48, 54 + dy + e + 6)], C(255, 150, 40), 1.6)
    p.flat([(50, 57 + dy), (78, 57 + dy), (76, 54 + dy + e + 3), (52, 54 + dy + e + 3)], C(255, 236, 150))
    return p.done()


def boss_ringer(f):
    """Silent Ringer: a tall robed figure whose head is a bell with no clapper."""
    p = Pen(128, 128)
    v = _f(f)
    dy = v['dy'] * .6
    p.poly([(26, 127), (36, 56 + dy), (92, 56 + dy), (104, 127), (86, 114), (64, 127), (42, 114)], C(70, 56, 124), 2.2)
    p.flat([(32, 120), (40, 60 + dy), (58, 60 + dy), (48, 112)], C(102, 86, 158))
    a = v['arm']
    for s, x in ((-1, 36), (1, 92)):
        h = 60 + dy
        tip = rot([(x + s * 30, h + 44)], x, h, -s * a)[0]
        p.line([(x, h + 6), tip], C(52, 42, 98), 13)
        p.line([(x, h + 6), tip], C(92, 76, 148), 8)
        p.disc(tip[0], tip[1], 6, fill=C(232, 226, 250), ink=1.5)
    t = 2 + dy
    p.poly([(56, t), (72, t), (90, 30 + dy), (98, 60 + dy), (30, 60 + dy), (38, 30 + dy)], C(226, 222, 244), 2.2)
    p.flat([(42, 56 + dy), (50, 28 + dy), (60, 6 + dy), (58, 56 + dy)], C(250, 248, 255))
    p.poly([(24, 58 + dy), (104, 58 + dy), (104, 66 + dy), (24, 66 + dy)], C(150, 140, 190), 1.8)
    p.disc(64, 44 + dy, 15, 11, fill=C(16, 12, 32))
    e = 2 * v['eye']
    p.disc(58, 44 + dy, 2, e, fill=C(210, 200, 255)); p.disc(70, 44 + dy, 2, e, fill=C(210, 200, 255))
    return p.done()


BOSS_ART = [boss_foreman, boss_rope, boss_founder, boss_anvil, boss_ringer]


# ------------------------------------------------------------------ items, 36x36
GOLD, GOLD_L = C(236, 186, 76), C(255, 234, 150)


def item_rush():
    p = Pen(36, 36)
    for i, o in enumerate((0, 8, 16)):
        p.poly([(6 + o, 8), (14 + o, 8), (24 + o, 18), (14 + o, 28), (6 + o, 28), (16 + o, 18)], (GOLD_L if i == 2 else GOLD), 1.2)
    return p.done()


def item_hook():
    p = Pen(36, 36)
    p.arc(18, 17, 12, 190, 60, INK, 6.5)
    p.arc(18, 17, 12, 190, 60, C(150, 170, 184), 3.5)
    p.line([(6, 18), (6, 34)], INK, 3.6); p.line([(6, 18), (6, 34)], GOLD, 1.6)
    return p.done()


def item_cleave():
    p = Pen(36, 36)
    p.line([(18, 0), (18, 16)], HANDLE, 3)
    p.poly([(5, 14), (31, 14), (27, 34), (9, 34)], BLADE, 1.5)
    p.flat([(9, 16), (27, 16), (26, 22), (10, 22)], BLADE_L)
    return p.done()


def item_cloak():
    p = Pen(36, 36)
    p.poly([(11, 4), (25, 4), (33, 20), (28, 32), (23, 25), (18, 34), (13, 25), (8, 32), (3, 20)], C(190, 200, 240), 1.5)
    p.flat([(8, 20), (13, 7), (18, 7), (15, 28)], C(236, 240, 255))
    return p.done()


def item_shard(t):
    p = Pen(36, 36)
    p.poly([(18, 2), (29, 15), (22, 33), (13, 33), (7, 15)], GOLD_L, 1.5)
    p.flat([(18, 4), (27, 15), (18, 18)], C(255, 250, 214))
    p.flat([(9, 15), (18, 18), (14, 32)], GOLD)
    if t:
        p.line([(31, 5), (31, 11)], C(255, 255, 230), 1); p.line([(28, 8), (34, 8)], C(255, 255, 230), 1)
    return p.done()


def item_whet():
    p = Pen(36, 36)
    p.poly([(3, 23), (24, 7), (33, 14), (12, 31)], C(124, 136, 160), 1.5)
    p.flat([(7, 22), (24, 9), (28, 12), (11, 26)], C(180, 192, 214))
    return p.done()


def item_bell(t):
    """The last bell, large: 64x72."""
    p = Pen(64, 72)
    p.line([(32, 0), (32, 10)], C(70, 60, 54), 3)
    a = (-3, 3)[t]
    pts = rot([(26, 8), (38, 8), (48, 28), (56, 56), (8, 56), (16, 28)], 32, 8, a)
    p.poly(pts, GOLD, 2)
    p.flat(rot([(16, 52), (21, 26), (28, 11), (29, 52)], 32, 8, a), GOLD_L)
    p.poly(rot([(4, 55), (60, 55), (60, 61), (4, 61)], 32, 8, a), C(158, 112, 44), 1.6)
    return p.done()


def small_bell(on):
    p = Pen(28, 30)
    col = GOLD if on else C(44, 38, 62)
    p.poly([(11, 3), (17, 3), (21, 12), (25, 23), (3, 23), (7, 12)], col, 1.3)
    p.poly([(2, 23), (26, 23), (26, 26), (2, 26)], C(158, 112, 44) if on else C(30, 26, 44), 1)
    if on:
        p.flat([(8, 21), (10, 10), (13, 5), (13, 21)], GOLD_L)
    return p.done()


def heart(full):
    p = Pen(20, 18)
    pts = [(10, 17), (2, 9), (1, 5), (4, 2), (7, 2), (10, 5), (13, 2), (16, 2), (19, 5), (18, 9)]
    if full:
        p.poly(pts, C(190, 160, 240), 1.3)
        p.flat([(4, 8), (3, 5), (5, 3.5), (8, 4), (8, 7)], C(240, 230, 255))
    else:
        p.poly(pts, C(30, 24, 48, 200), 1.1)
    return p.done()


# ------------------------------------------------------------------ projectiles and effects
def proj_drop(t):
    p = Pen(20, 28)
    p.poly([(10, 1), (16, 14), (15, 22), (10, 26), (5, 22), (4, 14)], C(120, 196, 224), 1.2)
    p.flat([(7, 15), (10, 7), (10, 21)], C(216, 244, 252))
    return p.done()


def proj_wave(t):
    p = Pen(28, 34)
    k = t * 3
    p.poly([(1, 33), (5 + k, 15), (10, 4 + k), (15, 13), (22 - k, 8 + k), (27, 33)], C(236, 244, 255), 1.3)
    p.flat([(7, 32), (10, 14), (14, 32)], C(150, 196, 236))
    return p.done()


def proj_orb(t):
    p = Pen(24, 24)
    p.disc(12, 12, 10 + t, fill=C(255, 120, 40, 90))
    p.disc(12, 12, 7, fill=C(255, 150, 40), ink=1)
    p.disc(10, 10, 3.2, fill=C(255, 244, 170))
    return p.done()


def spark(n):
    p = Pen(40, 40)
    r = (6, 13, 18)[n]
    w = (3, 2.4, 1.2)[n]
    for a in range(0, 360, 45):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        r0 = r * .45 * (n > 0)
        p.line([(20 + ca * r0, 20 + sa * r0), (20 + ca * r, 20 + sa * r)], C(255, 250, 225), w)
    return p.done()


def mote(n):
    p = Pen(10, 10)
    p.disc(5, 5, 2 + n, fill=C(235, 225, 255, 230))
    return p.done()


def hook_link():
    p = Pen(12, 12)
    p.disc(6, 6, 3.6, fill=C(186, 198, 214), ink=1.1)
    return p.done()


def anchor_ring(lit):
    p = Pen(28, 28)
    if lit:
        p.disc(14, 14, 13, fill=C(255, 226, 130, 80))
    p.arc(14, 14, 9, 0, 360, INK, 5)
    p.arc(14, 14, 9, 0, 360, GOLD_L if lit else C(176, 150, 96), 2.6)
    return p.done()


def up_mark():
    p = Pen(16, 18)
    p.poly([(8, 1), (15, 9), (11, 9), (11, 17), (5, 17), (5, 9), (1, 9)], C(255, 240, 180), 1.2)
    return p.done()


if __name__ == '__main__':
    import sys
    bg = (46, 44, 70, 255)
    F = player_frames()
    cols = 8
    sheet = Image.new('RGBA', (cols * 128, ((len(F) + cols - 1) // cols) * 128), bg)
    for i, im in enumerate(F.values()):
        sheet.alpha_composite(im, ((i % cols) * 128, (i // cols) * 128))
    sheet.save(sys.argv[1] + '/menuel.png')
    items = []
    for fn in ENEMY_ART + NPC_ART:
        for t in (0.0, 0.6):
            items.append(fn(t))
    s2 = Image.new('RGBA', (8 * 68, 3 * 68), bg)
    for i, im in enumerate(items):
        s2.alpha_composite(im, ((i % 8) * 68 + 2, (i // 8) * 68 + 2))
    s2.resize((s2.width * 2, s2.height * 2), Image.NEAREST).save(sys.argv[1] + '/mobs.png')
    s3 = Image.new('RGBA', (6 * 130, 5 * 130), bg)
    for b, fn in enumerate(BOSS_ART):
        for f in range(6):
            s3.alpha_composite(fn(f), (f * 130 + 1, b * 130 + 1))
    s3.save(sys.argv[1] + '/bosses.png')
