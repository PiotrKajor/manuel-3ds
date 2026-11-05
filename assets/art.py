"""Menuel - the cast: enemies, people, bosses, items and effects, drawn with the inking engine."""
import math
from PIL import Image, ImageDraw
from ink import *
from art_menuel import player_frames, head as menuel_head, body as menuel_body


class Pen:
    """Plain drawing surface, used only for small door and crack tiles."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new('RGBA', (w * 4, h * 4), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def flat(self, pts, fill):
        self.d.polygon([(x * 4, y * 4) for x, y in pts], fill=fill)

    def line(self, pts, col, w=1.0):
        self.d.line([(x * 4, y * 4) for x, y in pts], fill=col, width=max(1, int(w * 4)))

    def done(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def C(r, g, b, a=255):
    return (r, g, b, a)


INK4 = (*INK, 255)


def leg(a, x0, y0, x1, y1, x2, y2, w=1.6, col=INK):
    p = a.part(ink=0)
    p.line([(x0, y0), (x1, y1), (x2, y2)], col, w, smooth=False)
    p.mask.paste(255, (0, 0, p.size[0], p.size[1]), None) if False else None
    q = [(x0 * SS, y0 * SS), (x1 * SS, y1 * SS), (x2 * SS, y2 * SS)]
    p.md.line(q, fill=255, width=int(w * SS), joint='curve')
    a.add(p)


# ------------------------------------------------------------------ enemies, 64x56, anchor bottom centre (y=56)
def e_salt_mite(t):
    a = Art(64, 56)
    for i, (x, sgn) in enumerate(((14, -1), (24, -1), (32, 1), (42, 1), (50, 1), (20, -1))):
        k = tau(t + i / 3) * 3
        lift = max(0, tau(t + i / 3 + .25)) * 3
        leg(a, x, 42, x + sgn * 4, 47 - lift, x + sgn * 6 + k, 55 - lift, 2.0)
    bob = tau(t * 2) * .8
    p = a.part(1.5)
    p.fill([S(7, 45 + bob), (9, 30 + bob), (20, 22 + bob), (40, 21 + bob), (53, 30 + bob), S(57, 45 + bob), (32, 49 + bob)], (108, 132, 170))
    p.cel((70, 88, 126), 3, 3.5).rim((158, 182, 214), -1.2, -1.3)
    a.add(p)
    for x, h, w, ph in ((18, 18, 6, .1), (30, 25, 7, .3), (42, 16, 5.5, .6)):
        y = 25 + bob
        c = a.part(1.2)
        c.fill([S(x - w, y), S(x - w * .5, y - h * .6), S(x, y - h), S(x + w * .6, y - h * .55), S(x + w, y)], (224, 243, 252), smooth=False)
        c.shade([S(x, y), S(x, y - h), S(x + w * .6, y - h * .55), S(x + w, y)], (160, 202, 228), smooth=False)
        c.line([(x - w * .4, y - 2), (x - w * .2, y - h * .6)], (255, 255, 255), .7, smooth=False)
        a.add(c)
    for x in (47, 53):
        e = a.part(1.0)
        e.circle(x, 35 + bob, 3.2, col=(250, 240, 186))
        e.dot(x + .8, 35.3 + bob, 1.5)
        a.add(e)
    return a.done()


def e_dust_moth(t):
    a = Art(64, 56)
    f = tau(t)
    up = f * 15
    y0 = 24 + tau(t + .25) * 2
    for s in (-1, 1):
        w = a.part(1.3)
        w.fill([S(32 + s * 2, y0 + 2), (32 + s * 16, y0 - 9 - up * .5), S(32 + s * 29, y0 - 15 - up), (32 + s * 28, y0 - 1 - up * .55), S(32 + s * 21, y0 + 8 - up * .2), S(32 + s * 3, y0 + 7)], (176, 148, 106))
        w.cel((128, 102, 74), 2 * s if s > 0 else -1, 2.5).rim((222, 198, 150), -1, -1)
        w.dot(32 + s * 18, y0 - 5 - up * .6, 3.4, 3.4, (84, 58, 48))
        w.dot(32 + s * 18, y0 - 5 - up * .6, 1.7, 1.7, (236, 208, 140))
        a.add(w)
        w2 = a.part(1.2)
        w2.fill([S(32 + s * 2, y0 + 5), (32 + s * 13, y0 + 11 - up * .2), S(32 + s * 18, y0 + 18 - up * .1), S(32 + s * 3, y0 + 13)], (154, 124, 86))
        w2.cel((112, 88, 64))
        a.add(w2)
    b = a.part(1.4)
    b.fill([(32, y0 - 7), (37, y0 + 1), (35, y0 + 13), S(32, y0 + 21), (29, y0 + 13), (27, y0 + 1)], (92, 72, 58))
    b.cel((60, 46, 40)).rim((142, 118, 96))
    for k in range(3):
        b.line([(28, y0 + 5 + k * 4), (36, y0 + 5 + k * 4)], (60, 46, 40), .8, smooth=False)
    b.dot(29.2, y0 - 3, 2, 2, (252, 232, 150))
    b.dot(34.8, y0 - 3, 2, 2, (252, 232, 150))
    a.add(b)
    for s in (-1, 1):
        an = a.part(ink=0)
        q = [(32 + s * 2, y0 - 6), (32 + s * 6, y0 - 13), (32 + s * 12, y0 - 15)]
        an.md.line([(x * SS, y * SS) for x, y in q], fill=255, width=int(1.1 * SS))
        a.add(an)
    return a.done()


def e_bog_frog(i):
    """i: 0,1 idle  2 crouch  3 leap  4 fall  5 land"""
    a = Art(64, 56)
    green, dk, lt = (66, 128, 98), (40, 88, 74), (110, 172, 128)
    if i in (3, 4):
        lean = -8 if i == 3 else 6
        leg(a, 18, 30, 8, 38 - lean * .3, 3, 47 + lean * .4, 4)
        leg(a, 47, 32, 55, 40, 60, 48, 3)
        p = a.part(1.5)
        p.fill([(8, 34 + lean * .5), (15, 16 + lean * .4), (34, 10), (53, 18 - lean * .4), (56, 28), (38, 37), (18, 40)], green)
        p.cel(dk, 3, 3.5).rim(lt)
        p.shade([(20, 36), (38, 32), (53, 26), (43, 36), (22, 40)], (180, 212, 160))
        a.add(p)
        ey = a.part(1.2)
        ey.circle(44, 12 - lean * .3, 6.5, col=(230, 240, 170))
        ey.dot(45.5, 12 - lean * .3, 3)
        a.add(ey)
        return a.done()
    sq = {0: 0, 1: 1, 2: 5, 5: 7}[i]
    th = {0: 0, 1: 2.2}.get(i, 0)
    p = a.part(1.5)
    y = 21 + sq
    p.fill([S(6, 55), (7, 41 + sq * .4), (15, y + 4), (32, y), (49, y + 4), (57, 41 + sq * .4), S(58, 55), (32, 55)], green)
    p.cel(dk, 3, 3.5).rim(lt)
    p.shade([S(14, 54), (19, 42 + sq * .4 - th), (32, 39 + sq * .4 - th), (45, 42 + sq * .4 - th), S(50, 54)], (184, 214, 164))
    p.line([(12, 36 + sq * .5), (24, 41 + sq * .5), (40, 41 + sq * .5), (52, 36 + sq * .5)], INK, 1.2)
    a.add(p)
    for x in (20, 44):
        e = a.part(1.2)
        e.circle(x, y + 1, 7, 7 - sq * .3, (230, 240, 170))
        e.dot(x + 1, y + 1, 3.3, 3.3 - sq * .1)
        a.add(e)
    return a.done()


def e_bell_fish(i):
    """i: 0-3 hang and swing  4 about to spit  5 spit"""
    a = Art(64, 56)
    rot = tau(i / 4) * 7 if i < 4 else (-4 if i == 4 else 3)
    R = lambda pts: poly_rot(pts, 32, 0, rot)
    r = a.part(.8)
    r.fill(R([S(30.8, 0), S(33.2, 0), S(33.2, 10), S(30.8, 10)]), (120, 106, 84), smooth=False)
    a.add(r)
    p = a.part(1.6)
    open_ = {4: 0, 5: 2}.get(i, 0)
    p.fill(R([S(26, 9), S(38, 9), (45, 20), (50, 37 - open_), S(57, 43 - open_), S(7, 43 - open_), (14, 37 - open_), (19, 20)]), (186, 148, 66))
    p.cel((128, 96, 40), 3.4, 4).rim((238, 212, 126))
    p.shade(R([S(15, 39), S(49, 39), (56, 43), S(8, 43)]), (116, 88, 44))
    a.add(p)
    for s in (-1, 1):
        e = a.part(1.0)
        c = R([(32 + s * 8, 26)])[0]
        e.circle(c[0], c[1], 4.6, col=(234, 240, 216))
        e.dot(c[0] + s * .3, c[1] + .6, 2.2)
        a.add(e)
    cl = a.part(1.2)
    c = R([(32, 45 + open_ * 3 + (i == 4) * -2)])[0]
    cl.circle(c[0], c[1], 5, col=(96, 72, 44))
    cl.cel((60, 44, 30), 1.6, 1.8)
    a.add(cl)
    return a.done()


def e_cinder_beetle(t):
    a = Art(64, 56)
    glow = (tau(t) + 1) / 2
    for i, x in enumerate((13, 21, 31, 41, 49, 55)):
        k = tau(t + i / 3) * 4
        lift = max(0, tau(t + i / 3 + .25)) * 3.5
        leg(a, x, 42, x + (k * .5), 48 - lift, x + k, 55 - lift, 2.3)
    p = a.part(1.7)
    p.fill([S(3, 45), (6, 28), (22, 15), (43, 17), (55, 28), S(59, 45), (32, 49)], (64, 40, 42))
    p.cel((38, 24, 28), 3.5, 4).rim((112, 82, 80))
    hot = (255, int(130 + glow * 90), 40)
    p.line([(31, 15), (28, 26), (33, 34), (30, 48)], INK, 1.4)
    for pts in ([(10, 34), (17, 27), (24, 31)], [(39, 22), (46, 30), (40, 38)], [(14, 42), (22, 39)], [(37, 44), (48, 40)]):
        p.line(pts, hot, 1.9)
    a.add(p)
    h = a.part(1.2)
    h.fill([S(50, 28), (60, 25), S(63, 37), (54, 42), (48, 36)], (52, 30, 32))
    h.dot(55, 32, 2.4, 2.4, (255, 228, 120))
    a.add(h)
    return a.done()


def e_furnace_mouth(i):
    """i: 0-3 breathing  4 about to spit  5 spit"""
    a = Art(64, 56)
    k = (tau(i / 4) + 1) / 2 if i < 4 else (0 if i == 4 else 1)
    gape = 3 + k * 3 + (i == 5) * 6
    p = a.part(1.8)
    p.fill([S(9, 55), (8, 21), S(17, 8), S(47, 8), (56, 21), S(55, 55)], (90, 80, 88))
    p.cel((56, 48, 58), 4, 4).rim((142, 132, 138))
    for x in (17, 32, 47):
        p.dot(x, 13, 1.9, 1.9, (44, 38, 46))
    a.add(p)
    m = a.part(1.5)
    my = 25 - gape * .3
    m.fill([S(15, my), S(49, my), (50, 44), S(46, 50), S(18, 50), (14, 44)], (255, int(120 + k * 70), 30))
    m.shade([S(20, my + 9), S(44, my + 9), (45, 44), S(42, 50), S(22, 50), (19, 44)], (255, 232, 140))
    a.add(m)
    for x in (20, 28, 36, 44):
        t = a.part(.9)
        t.fill([S(x - 4, my), S(x + 4, my), S(x, my + 7 - gape * .2)], (228, 226, 218), smooth=False)
        a.add(t)
    return a.done()


def e_hush_wraith(t):
    a = Art(64, 56)
    w1, w2 = tau(t) * 4, tau(t + .33) * 4
    y = tau(t + .1) * 1.5
    p = a.part(1.6)
    p.fill([S(32, 1 + y), (45, 11 + y), (50, 30 + y), S(46 + w1, 55), (40, 42 + y), S(32 + w2, 55), (26, 42 + y), S(18 + w1, 55), (14, 30 + y), (19, 11 + y)], (94, 80, 158))
    p.cel((60, 50, 118), 3.5, 3.8).rim((142, 128, 202))
    a.add(p)
    m = a.part(1.3)
    m.fill([S(32, 8 + y), (42, 19 + y), S(32, 33 + y), (22, 19 + y)], (236, 230, 252))
    m.cel((192, 182, 226), 2, 2.2)
    for s in (-1, 1):
        m.shade([S(32 + s * 8, 17 + y), S(32 + s * 2, 21 + y), S(32 + s * 5, 23 + y)], INK, smooth=False)
    a.add(m)
    return a.done()


def e_snow_hare(i):
    """i: 0,1 idle  2 crouch  3 leap  4 fall  5 land"""
    a = Art(64, 56)
    white, sh, inner = (236, 240, 252), (190, 196, 226), (226, 176, 200)
    if i in (3, 4):
        l = -5 if i == 3 else 4
        leg(a, 17, 34, 8, 38, 3, 46 + l, 3)
        leg(a, 44, 34, 52, 40, 57, 50 - l, 2.6, (60, 52, 80))
        for dx, ang in ((-2, -8), (5, -2)):
            e = a.part(1.2)
            base = (38 + dx, 16)
            e.fill(poly_rot([S(base[0] - 3, base[1]), (base[0] - 16, base[1] - 7 + l), S(base[0] - 25, base[1] - 7 + l), (base[0] - 15, base[1] - 11 + l), S(base[0] + 3, base[1] - 3)], base[0], base[1], ang), white)
            e.cel(sh, 1.4, 1.6)
            a.add(e)
        p = a.part(1.5)
        p.fill([(5, 28), (15, 15), (38, 12), (54, 19), (57, 29), (44, 38), (17, 38)], white)
        p.cel(sh, 3, 3.5)
        p.dot(47, 23, 2.3, 2.3, (70, 30, 70))
        a.add(p)
        return a.done()
    sq = {0: 0, 1: 1, 2: 6, 5: 8}[i]
    for x, d in ((23, -3), (37, 3)):
        h = 22 - sq * 1.2
        e = a.part(1.2)
        e.fill([S(x - 4, 27 + sq), (x - 4 + d * .5, 27 + sq - h * .6), S(x + d, 26 + sq - h), (x + 4 + d * .5, 27 + sq - h * .6), S(x + 4, 27 + sq)], white)
        e.shade([S(x - 1.5, 26 + sq), (x - 1.5 + d * .5, 27 + sq - h * .6), S(x + d, 28 + sq - h), (x + 1.5 + d * .5, 27 + sq - h * .6), S(x + 1.5, 26 + sq)], inner)
        a.add(e)
    p = a.part(1.5)
    p.fill([S(9, 55), (9, 39 + sq * .4), (20, 24 + sq), (42, 24 + sq), (54, 39 + sq * .4), S(55, 55), (32, 55)], white)
    p.cel(sh, 3, 3.5)
    p.dot(24, 36 + sq * .5, 2.3, 2.3, (70, 30, 70))
    p.dot(41, 36 + sq * .5, 2.3, 2.3, (70, 30, 70))
    p.line([(30, 41 + sq * .5), (32.5, 43 + sq * .5), (35, 41 + sq * .5)], (150, 90, 120), .9)
    a.add(p)
    return a.done()


def _cycle(fn):
    return [fn(i / 6) for i in range(6)]


def enemy_frames():
    return [_cycle(e_salt_mite), _cycle(e_dust_moth), [e_bog_frog(i) for i in range(6)], [e_bell_fish(i) for i in range(6)],
            _cycle(e_cinder_beetle), [e_furnace_mouth(i) for i in range(6)], _cycle(e_hush_wraith), [e_snow_hare(i) for i in range(6)]]


# ------------------------------------------------------------------ people, 72x72, anchor bottom centre (y=72)
def eyes(p, xl, xr, y, r=2.3, blink=False):
    for x in (xl, xr):
        if blink:
            p.line([(x - r, y), (x + r, y)], INK, 1.0, smooth=False)
        else:
            p.dot(x, y, r, r * 1.1)
            p.dot(x - r * .3, y - r * .4, r * .32, r * .32, (255, 255, 255))


def npc_ringer(t, blink=False, a=None):
    own = a is None
    a = a or Art(72, 72)
    k = tau(t) * 1.1
    st = a.part(1.1)
    st.fill([S(52, 12), S(55, 12), S(56, 72), S(52, 72)], (86, 62, 44), smooth=False)
    st.rim((132, 100, 72))
    a.add(st)
    b = a.part(1.3)
    b.fill([S(47, 3), S(60, 3), (63, 12), S(67, 20), S(41, 20), (44, 12)], (216, 178, 88))
    b.cel((162, 124, 56), 2, 2.4).rim((246, 222, 150))
    a.add(b)
    p = a.part(1.7)
    p.fill([S(15, 72), (19, 44), (28, 27 + k), (46, 27 + k), (53, 42), S(58, 72), (46, 68), (36, 72), (26, 68)], (116, 98, 88))
    p.cel((78, 66, 62), 4, 4).rim((160, 142, 124))
    p.line([(36, 37 + k), (35, 70)], (78, 66, 62), 1.0)
    a.add(p)
    h = a.part(1.7)
    h.fill([S(37, 11 + k), (47, 25 + k), (50, 34 + k), (37, 41 + k), (24, 34 + k), (27, 25 + k)], (232, 220, 196))
    h.cel((186, 170, 148), 2.2, 2.6)
    eyes(h, 31, 43, 29 + k, 2.0, blink)
    h.line([(27, 25 + k), (33, 26 + k)], (120, 104, 92), 1.2, smooth=False)
    h.line([(47, 25 + k), (41, 26 + k)], (120, 104, 92), 1.2, smooth=False)
    a.add(h)
    return a.done() if own else a


def npc_miner(t, blink=False, a=None):
    own = a is None
    a = a or Art(72, 72)
    k = tau(t) * 1.0
    pk = a.part(1.1)
    pk.fill([S(56, 28), S(59, 27), S(66, 68), S(63, 69)], (84, 60, 46), smooth=False)
    a.add(pk)
    hd = a.part(1.2)
    hd.fill([S(50, 28), (58, 21), S(72, 21), (63, 27), S(56, 33)], (158, 168, 186))
    hd.cel((104, 112, 134), 1.4, 1.8)
    a.add(hd)
    p = a.part(1.7)
    p.fill([S(14, 72), (14, 42), (24, 33 + k), (47, 33 + k), (56, 42), S(56, 72)], (98, 84, 72))
    p.cel((66, 56, 52), 4, 4).rim((144, 126, 104))
    p.shade([S(25, 50), S(46, 50), S(46, 72), S(25, 72)], (150, 134, 106), smooth=False)
    a.add(p)
    h = a.part(1.6)
    h.fill([S(20, 16 + k), (35, 12 + k), S(50, 16 + k), (51, 34 + k), (35, 39 + k), (19, 34 + k)], (230, 214, 188))
    h.cel((186, 168, 144), 2.4, 2.6)
    eyes(h, 28, 42, 25 + k, 2.2, blink)
    h.line([(31, 32 + k), (35, 33.5 + k), (39, 32 + k)], (120, 96, 80), 1.0)
    a.add(h)
    c = a.part(1.5)
    c.fill([S(13, 18 + k), (20, 8 + k), (35, 3 + k), (50, 8 + k), S(57, 18 + k), (35, 15 + k)], (216, 160, 58))
    c.cel((162, 112, 40), 2, 2.4).rim((246, 208, 120))
    a.add(c)
    l = a.part(1.0)
    l.circle(35, 8 + k, 3.8, col=(255, 248, 180))
    a.add(l)
    return a.done() if own else a


def npc_clerk(t, blink=False, a=None):
    own = a is None
    a = a or Art(72, 72)
    k = tau(t) * 1.1
    p = a.part(1.7)
    p.fill([S(10, 72), (15, 47), (36, 41 + k), (57, 47), S(62, 72)], (50, 92, 102))
    p.cel((30, 62, 74), 4, 4).rim((88, 138, 146))
    a.add(p)
    h = a.part(1.7)
    h.circle(36, 25 + k, 21, 20, (184, 226, 200))
    h.cel((130, 182, 160), 3, 3.4).rim((222, 244, 226))
    h.dot(28, 38 + k, 3, 1.8, (150, 202, 176))
    h.dot(44, 38 + k, 3, 1.8, (150, 202, 176))
    h.line([(31, 36 + k), (36, 38 + k), (41, 36 + k)], (70, 110, 96), 1.1)
    a.add(h)
    for x in (27, 45):
        g = a.part(1.1)
        g.circle(x, 25 + k, 6.2, col=(244, 248, 226))
        if blink:
            g.line([(x - 3, 25 + k), (x + 3, 25 + k)], INK, 1.0, smooth=False)
        else:
            g.dot(x + .4, 25 + k, 1.9)
        a.add(g)
    br = a.part(0)
    br.md.line([(33 * SS, (25 + k) * SS), (39 * SS, (25 + k) * SS)], fill=255, width=SS)
    a.add(br)
    sc = a.part(1.2)
    sc.fill([S(44, 51), S(64, 48), S(67, 68), S(47, 71)], (230, 220, 182))
    sc.cel((186, 172, 136), 1.6, 2)
    for y in (54, 58, 62):
        sc.line([(48, y + 1), (62, y - 1)], (120, 112, 96), .8, smooth=False)
    a.add(sc)
    return a.done() if own else a


def npc_smith(t, blink=False, a=None):
    own = a is None
    a = a or Art(72, 72)
    k = tau(t) * .9
    hm = a.part(1.1)
    hm.fill([S(60, 20 + k), S(63, 20 + k), S(64, 50), S(61, 50)], (74, 56, 46), smooth=False)
    a.add(hm)
    hh = a.part(1.2)
    hh.fill([S(53, 11 + k), S(70, 10 + k), S(71, 22 + k), S(54, 23 + k)], (150, 152, 168))
    hh.cel((96, 98, 118), 1.8, 2.2).rim((206, 208, 222))
    a.add(hh)
    p = a.part(1.8)
    p.fill([S(7, 72), (8, 42), (20, 32), (48, 32), (61, 42), S(62, 72)], (124, 72, 50))
    p.cel((84, 46, 36), 4, 4).rim((176, 114, 80))
    p.shade([S(21, 42), S(48, 42), S(50, 72), S(19, 72)], (70, 56, 54), smooth=False)
    p.shade([S(21, 42), S(26, 42), S(24, 72), S(19, 72)], (94, 78, 74), smooth=False)
    a.add(p)
    h = a.part(1.6)
    h.circle(34, 20 + k, 15, 15, (214, 160, 120))
    h.cel((170, 118, 86), 2.4, 2.6)
    eyes(h, 28, 40, 18 + k, 2.0, blink)
    h.line([(24, 13 + k), (31, 15 + k)], INK, 1.7, smooth=False)
    h.line([(44, 13 + k), (37, 15 + k)], INK, 1.7, smooth=False)
    a.add(h)
    b = a.part(1.3)
    b.fill([S(21, 23 + k), S(47, 23 + k), (45, 34 + k), S(34, 42 + k), (23, 34 + k)], (232, 110, 40))
    b.cel((178, 72, 28), 2, 2.4).rim((255, 170, 90))
    a.add(b)
    return a.done() if own else a


def npc_hermit(t, blink=False, a=None):
    own = a is None
    a = a or Art(72, 72)
    k = tau(t) * 1.4
    p = a.part(1.7)
    p.fill([S(12, 72), (17, 38), S(36, 7 + k), (55, 38), S(60, 72), (48, 66), (36, 72), (24, 66)], (204, 212, 236))
    p.cel((150, 158, 196), 4, 4).rim((240, 244, 255))
    a.add(p)
    f = a.part(1.2)
    f.fill([(25, 33 + k), (47, 33 + k), (43, 47 + k), (29, 47 + k)], (30, 26, 54))
    if blink:
        f.line([(30, 39 + k), (34, 39 + k)], (190, 220, 255), .9, smooth=False)
        f.line([(38, 39 + k), (42, 39 + k)], (190, 220, 255), .9, smooth=False)
    else:
        f.dot(32, 39 + k, 1.6, 1.6, (190, 220, 255))
        f.dot(40, 39 + k, 1.6, 1.6, (190, 220, 255))
    a.add(f)
    return a.done() if own else a


NPC_ART = [npc_ringer, npc_miner, npc_clerk, npc_smith, npc_hermit]


def npc_frames():
    return [[fn(i / 5, blink=(i == 5)) if i < 5 else fn(.6, blink=True) for i in range(6)] for fn in NPC_ART]


# ------------------------------------------------------------------ bosses, 128x128, anchor bottom centre
# phases: 0-3 idle  4,5 windup  6,7 attack  8,9 airborne  10,11 stunned
def _phase(f):
    i = {0: 0, 1: 1, 2: 2, 3: 3}.get(f)
    idle = tau(f / 4) if f < 4 else 0
    return dict(idle=idle, wind=f in (4, 5), wind2=f == 5, atk=f in (6, 7), atk2=f == 7, air=f in (8, 9), air2=f == 9, stun=f in (10, 11), stun2=f == 11,
                dy=idle * 1.6 + (6 if f == 4 else 9 if f == 5 else -4 if f == 6 else -2 if f == 7 else -4 if f in (8, 9) else 11 if f in (10, 11) else 0))


def bfoot(a, x, y, w, col):
    p = a.part(1.7)
    p.fill([S(x - w, y), (x - w * .9, 120), S(x - w - 3, 127), S(x + w + 3, 127), (x + w * .9, 120), S(x + w, y)], col)
    p.cel(tuple(int(c * .65) for c in col), 2.6, 3)
    a.add(p)


def boss_foreman(f):
    """Salt Foreman: a huge miner under a crust of salt, still swinging his pick."""
    a = Art(128, 128)
    v = _phase(f)
    dy = v['dy']
    ang = -55 if v['wind2'] else -40 if v['wind'] else 75 if v['atk2'] else 45 if v['atk'] else -15 if v['air'] else 90 if v['stun'] else 4 + v['idle'] * 3
    bfoot(a, 46, 97 + dy * .5, 11, (58, 50, 66))
    bfoot(a, 84, 97 + dy * .5, 11, (58, 50, 66))
    px, py = 106, 74 + dy
    hd = a.part(1.3)
    hd.fill(poly_rot([S(px - 2, py), S(px + 2, py), S(px + 3, py - 60), S(px - 2, py - 60)], px, py, ang), (84, 62, 48), smooth=False)
    hd.rim((130, 100, 74))
    a.add(hd)
    pk = a.part(1.5)
    pk.fill(poly_rot([S(px - 26, py - 53), (px, py - 67), S(px + 30, py - 52), (px, py - 59)], px, py, ang), (172, 186, 206))
    pk.cel((112, 124, 150), 2, 2.5).rim((224, 234, 244))
    a.add(pk)
    b = a.part(2.0)
    b.fill([S(17, 106 + dy), (12, 72 + dy), (20, 46 + dy), (38, 31 + dy), (90, 31 + dy), (108, 46 + dy), (116, 72 + dy), S(111, 106 + dy), (64, 111 + dy)], (84, 104, 142))
    b.cel((52, 68, 104), 6, 6).rim((132, 156, 194), -1.4, -1.6)
    a.add(b)
    for x, h, w, ph in ((29, 25, 10, 0), (49, 40, 12, 1), (72, 34, 11, 2), (94, 25, 9.5, 3)):
        h2 = h + (2 if v['idle'] > .5 and ph % 2 else 0)
        c = a.part(1.5)
        y = 36 + dy
        c.fill([S(x - w, y), S(x - w * .55, y - h2 * .62), S(x, y - h2), S(x + w * .6, y - h2 * .58), S(x + w, y)], (226, 244, 252), smooth=False)
        c.shade([S(x, y), S(x, y - h2), S(x + w * .6, y - h2 * .58), S(x + w, y)], (156, 200, 228), smooth=False)
        c.line([(x - w * .5, y - 3), (x - w * .2, y - h2 * .62)], (255, 255, 255), 1, smooth=False)
        a.add(c)
    m = a.part(1.8)
    m.fill([S(37, 54 + dy), (64, 50 + dy), S(91, 54 + dy), (87, 84 + dy), (64, 90 + dy), (41, 84 + dy)], (228, 214, 186))
    m.cel((180, 162, 136), 3, 3.5)
    if v['stun']:
        m.line([(47, 69 + dy), (58, 69 + dy)], INK, 2.2, smooth=False)
        m.line([(70, 69 + dy), (81, 69 + dy)], INK, 2.2, smooth=False)
    else:
        ey = 7 if v['wind'] or v['atk'] else 5
        m.shade([S(46, 63 + dy), S(60, 68 + dy), S(58, 68 + dy + ey), S(46, 68 + dy + ey * .7)], INK, smooth=False)
        m.shade([S(82, 63 + dy), S(68, 68 + dy), S(70, 68 + dy + ey), S(82, 68 + dy + ey * .7)], INK, smooth=False)
        if v['wind'] or v['atk']:
            m.dot(53, 70 + dy, 1.8, 1.8, (255, 120, 80))
            m.dot(75, 70 + dy, 1.8, 1.8, (255, 120, 80))
    m.line([(54, 82 + dy), (64, 80 + dy), (74, 82 + dy)], INK, 1.8)
    a.add(m)
    arm = a.part(1.8)
    hx, hy = 104, 72 + dy
    arm.fill([S(92, 55 + dy), (104, 53 + dy), (116, 63 + dy), (114, 78 + dy), (100, 82 + dy), (92, 72 + dy)], (84, 104, 142))
    arm.cel((52, 68, 104), 3, 3.5).rim((132, 156, 194))
    a.add(arm)
    return a.done()


def boss_rope(f):
    """Rope Drowned: a pale, bloated figure bound tight in the bell rope that drowned it."""
    a = Art(128, 128)
    v = _phase(f)
    dy = v['dy'] * .7
    wob = v['idle'] * 2
    rp = a.part(1.3)
    rp.fill([S(61, 0), S(67, 0), S(67, 26 + dy), S(61, 26 + dy)], (186, 162, 102), smooth=False)
    rp.rim((226, 204, 150))
    for y in range(4, 26, 6):
        rp.line([(61, y), (67, y + 3)], (120, 100, 62), 1, smooth=False)
    a.add(rp)
    s = 22 if v['atk'] else (-12 if v['wind'] else 10 if v['air'] else 0)
    for sgn, x in ((-1, 16), (1, 112)):
        ar = a.part(1.7)
        tip = (x + sgn * (5 + s * .4) + wob * sgn * .5, 118 if not v['wind'] else 104)
        ar.fill([S(x - 7, 70 + dy), (x + sgn * 3, 96), S(tip[0], tip[1]), (x + sgn * 3 - 10 * sgn, 98), S(x + 7, 70 + dy)], (66, 128, 124))
        ar.cel((40, 88, 92), 2.4, 2.8).rim((112, 174, 158))
        a.add(ar)
    p = a.part(2.1)
    p.circle(64, 66 + dy, 50 + wob * .3, 46 - wob * .3, (68, 132, 128))
    p.cel((40, 88, 96), 7, 7).rim((122, 188, 170), -1.6, -1.8)
    for i in range(5):
        y = 34 + i * 16 + dy
        p.line([(10, y - 3), (64, y + 3), (118, y + 7)], (58, 42, 30), 7.5)
        p.line([(10, y - 4), (64, y + 2), (118, y + 6)], (206, 182, 118), 4.2)
        for x in range(18, 114, 12):
            yy = y - 3 + (x - 10) * 10 / 108
            p.line([(x, yy - 1.5), (x + 4, yy + 1.5)], (136, 112, 70), 1.1, smooth=False)
    a.add(p)
    h = a.part(2.0)
    h.circle(64, 47 + dy, 26, 22, (218, 232, 208))
    h.cel((166, 190, 170), 3.5, 4)
    if v['stun']:
        for s_ in (-1, 1):
            h.line([(64 + s_ * 7, 44 + dy), (64 + s_ * 15, 44 + dy)], (20, 40, 44), 2, smooth=False)
    else:
        rr = 5.6 if v['wind'] or v['atk'] else 4.6
        h.dot(54, 45 + dy, rr, rr, (20, 40, 44))
        h.dot(74, 45 + dy, rr, rr, (20, 40, 44))
        h.dot(52.5, 43.5 + dy, 1.2, 1.2, (220, 236, 220))
        h.dot(72.5, 43.5 + dy, 1.2, 1.2, (220, 236, 220))
    mo = 7 if v['atk'] or v['wind'] else 3.5 + (f % 4 == 1) * 1
    h.dot(64, 59 + dy, 7, mo, (20, 40, 44))
    a.add(h)
    for x in (42, 64, 86):
        t = a.part(1.2)
        t.fill([S(x - 2.2, 106 + dy), S(x + 2.2, 106 + dy), S(x + v['idle'] * 3, 127)], (206, 182, 118), smooth=False)
        a.add(t)
    return a.done()


def boss_founder(f):
    """Two-Headed Founder: two bickering heads on one apron, with a ladle of molten metal."""
    a = Art(128, 128)
    v = _phase(f)
    dy = v['dy']
    bfoot(a, 44, 100 + dy * .5, 11, (52, 38, 38))
    bfoot(a, 84, 100 + dy * .5, 11, (52, 38, 38))
    p = a.part(2.0)
    p.fill([S(17, 108 + dy), (20, 62 + dy), (40, 49 + dy), (88, 49 + dy), (108, 62 + dy), S(112, 108 + dy), (64, 112 + dy)], (172, 94, 56))
    p.cel((120, 60, 40), 6, 6).rim((216, 146, 96), -1.4, -1.6)
    a.add(p)
    ap = a.part(1.8)
    ap.fill([S(39, 60 + dy), (64, 57 + dy), S(89, 60 + dy), (93, 113 + dy), S(35, 113 + dy)], (84, 58, 46))
    ap.cel((54, 36, 30), 4, 4).rim((124, 90, 70))
    ap.line([(50, 66 + dy), (48, 110 + dy)], (54, 36, 30), 1, smooth=False)
    ap.line([(79, 66 + dy), (81, 110 + dy)], (54, 36, 30), 1, smooth=False)
    ap.dot(64, 80 + dy, 7, 7, (54, 36, 30))
    a.add(ap)
    for hx, sgn, c in ((39, -1, (234, 178, 130)), (89, 1, (224, 160, 112))):
        off = v['idle'] * sgn * 1.2 + (f % 2) * .3
        tilt = 3 + off
        h = a.part(1.9)
        hy = 32 + dy + off
        h.circle(hx, hy, 22, 23, c)
        h.cel((176, 118, 82), 3.5, 3.8).rim((250, 214, 170))
        h.line([(hx - 13, hy - 8 + tilt * .5), (hx - 3, hy - 4)], INK, 2.3, smooth=False)
        h.line([(hx + 13, hy - 8 + tilt * .5), (hx + 3, hy - 4)], INK, 2.3, smooth=False)
        if v['stun']:
            h.line([(hx - 10, hy + 1), (hx - 4, hy + 1)], INK, 1.8, smooth=False)
            h.line([(hx + 4, hy + 1), (hx + 10, hy + 1)], INK, 1.8, smooth=False)
        else:
            eyes(h, hx - 7, hx + 7, hy + 1, 2.7)
        my = 6 if v['atk'] or v['wind'] else 2.6 + (f == (0 if sgn < 0 else 2)) * 2.5
        h.dot(hx + sgn * 1, hy + 12, 6.5, my)
        if my > 3:
            h.dot(hx + sgn * 1, hy + 10.5 + my * .5, 4, 1.4, (200, 70, 70))
        a.add(h)
    ang = -90 if v['wind2'] else -65 if v['wind'] else 45 if v['atk'] else -30 if v['air'] else 30 if v['stun'] else 8 + v['idle'] * 4
    ax, ay = 112, 72 + dy
    l = a.part(1.3)
    l.fill(poly_rot([S(ax - 2.4, ay), S(ax + 2.4, ay), S(ax + 2.4, ay + 34), S(ax - 2.4, ay + 34)], ax, ay, ang), (66, 54, 54), smooth=False)
    a.add(l)
    cx, cy = poly_rot([(ax, ay + 42)], ax, ay, ang)[0]
    b = a.part(1.6)
    b.circle(cx, cy, 11, 10, (88, 82, 92))
    b.dot(cx, cy - 2.5, 7.5, 5, (255, 170, 44))
    b.dot(cx - 2, cy - 3.5, 3, 1.8, (255, 240, 160))
    a.add(b)
    return a.done()


def boss_anvil(f):
    """The Anvil: a walking anvil of black iron with forge fire behind its visor."""
    a = Art(128, 128)
    v = _phase(f)
    dy = v['dy'] * (1.2 if v['wind'] or v['stun'] else 1)
    if not v['air']:
        bfoot(a, 42, 102 + dy * .5, 13, (42, 38, 48))
        bfoot(a, 88, 102 + dy * .5, 13, (42, 38, 48))
    else:
        tuck = 8 if v['air2'] else 3
        bfoot(a, 42, 94 + tuck, 12, (42, 38, 48))
        bfoot(a, 88, 94 + tuck, 12, (42, 38, 48))
    p = a.part(2.2)
    p.fill([S(2, 24 + dy), (42, 22 + dy), S(90, 22 + dy), (118, 26 + dy), S(127, 36 + dy), (100, 46 + dy), S(90, 56 + dy), (84, 72 + dy), S(101, 110 + dy), S(27, 110 + dy), (44, 72 + dy), S(36, 56 + dy), (24, 46 + dy)],
           (82, 78, 92))
    p.cel((46, 44, 56), 6, 6).rim((156, 152, 168), -1.6, -1.8)
    p.shade([S(5, 25 + dy), (42, 23.5 + dy), S(90, 23.5 + dy), (116, 27 + dy), S(122, 34 + dy), (90, 33 + dy), S(32, 34 + dy)], (170, 166, 182))
    p.line([(36, 94 + dy), (64, 92 + dy), (92, 94 + dy)], (46, 44, 56), 1.4)
    a.add(p)
    e = 11 if v['wind'] or v['atk'] else (3 if v['stun'] else 7 + v['idle'])
    m = a.part(1.8)
    m.fill([S(43, 53 + dy), S(85, 53 + dy), S(81, 53 + dy + e + 4), S(47, 53 + dy + e + 4)], (255, 140, 36), smooth=False)
    m.shade([S(49, 56 + dy), S(79, 56 + dy), S(77, 53 + dy + e + 1), S(51, 53 + dy + e + 1)], (255, 234, 150), smooth=False)
    a.add(m)
    return a.done()


def boss_ringer(f):
    """Silent Ringer: a tall robed figure whose head is a bell with no clapper."""
    a = Art(128, 128)
    v = _phase(f)
    dy = v['dy'] * .6
    hem = v['idle'] * 3
    ar = 60 if v['stun'] else -50 if v['wind'] else 40 if v['atk'] else -20 if v['air'] else 0
    for sgn, x in ((-1, 34), (1, 94)):
        s0 = a.part(1.5)
        tip = poly_rot([(x + sgn * 26, 62 + dy + 44)], x, 62 + dy, -sgn * ar)[0]
        mid = ((x + tip[0]) / 2 + sgn * 3, (62 + dy + 8 + tip[1]) / 2)
        s0.fill([S(x - 7, 60 + dy), mid, S(tip[0] - 3, tip[1]), S(tip[0] + 3, tip[1]), (mid[0] + 7, mid[1]), S(x + 7, 60 + dy)], (70, 58, 124))
        s0.cel((44, 36, 88), 2.6, 3).rim((112, 98, 170))
        a.add(s0)
        h = a.part(1.4)
        h.circle(tip[0], tip[1] + 2, 6, col=(234, 228, 250))
        h.cel((186, 178, 216), 1.4, 1.6)
        a.add(h)
    p = a.part(2.1)
    p.fill([S(24, 127), (33, 90), (39, 56 + dy), (89, 56 + dy), (95, 90), S(106, 127), (90 + hem, 113), S(79 - hem, 127), (64 + hem, 115), S(50 + hem, 127), (38 - hem, 113)], (72, 58, 128))
    p.cel((44, 36, 90), 6, 6).rim((120, 104, 176), -1.5, -1.7)
    p.line([(64, 64 + dy), (61 + hem * .3, 113)], (44, 36, 90), 1.2)
    a.add(p)
    t = 3 + dy
    b = a.part(2.2)
    b.fill([S(55, t), S(73, t), (82, t + 16), (90, t + 32), (98, t + 52), S(30, t + 52), (38, t + 32), (46, t + 16)], (228, 224, 246))
    b.cel((168, 160, 206), 5, 5).rim((252, 250, 255))
    a.add(b)
    lp = a.part(1.8)
    lp.fill([S(22, t + 50), S(106, t + 50), (108, t + 58), S(20, t + 58)], (156, 146, 196))
    lp.cel((110, 102, 150), 2, 2.2).rim((202, 196, 232))
    a.add(lp)
    fc = a.part(1.5)
    fc.circle(64, t + 37, 16, 12, (16, 12, 32))
    gl = (255, 90, 90) if v['wind'] or v['atk'] else (214, 204, 255)
    if v['stun']:
        fc.line([(55, t + 37), (61, t + 37)], gl, 1.2, smooth=False)
        fc.line([(67, t + 37), (73, t + 37)], gl, 1.2, smooth=False)
    else:
        fc.dot(57, t + 37, 2.3, 2.3, gl)
        fc.dot(71, t + 37, 2.3, 2.3, gl)
    a.add(fc)
    return a.done()


BOSS_ART = [boss_foreman, boss_rope, boss_founder, boss_anvil, boss_ringer]


def boss_frames():
    return [[fn(f) for f in range(12)] for fn in BOSS_ART]


# ------------------------------------------------------------------ portraits for dialogue, 64x64
def portrait_npc(fn, crop):
    im = fn(.2, blink=False).crop(crop)
    return im.resize((64, 64), Image.LANCZOS)


def portraits():
    out = []
    crops = [(8, 2, 64, 58), (8, 0, 64, 56), (8, 0, 64, 56), (6, 0, 62, 56), (8, 6, 64, 62)]
    for fn, c in zip(NPC_ART, crops):
        out.append(portrait_npc(fn, c))
    for fn, c in zip(BOSS_ART, ((14, 0, 114, 100), (12, 0, 116, 104), (6, 0, 122, 116), (0, 8, 128, 136), (14, 0, 114, 100))):
        out.append(fn(0).crop(c).resize((64, 64), Image.LANCZOS))
    a = Art(64, 64)
    menuel_body(a, 32, 76, 0, 1, 1, .2, (1.1, 1.1))
    menuel_head(a, 32, 8, 0, 1, (1.15, 1.15))
    out.append(a.done())
    return out


# ------------------------------------------------------------------ items, 40x40
GOLD, GOLD_L, GOLD_S = (236, 186, 76), (255, 236, 160), (170, 118, 44)


def item_rush():
    a = Art(40, 40)
    for i, o in enumerate((1, 11, 21)):
        p = a.part(1.3)
        p.fill([S(5 + o, 8), S(14 + o, 8), S(24 + o - (i == 2) * 3, 20), S(14 + o, 32), S(5 + o, 32), S(14 + o - 1, 20)], GOLD if i < 2 else GOLD_L, smooth=False)
        p.cel(GOLD_S, 1.6, 1.8)
        a.add(p)
    return a.done()


def item_hook():
    a = Art(40, 40)
    pts = []
    for i in range(18):
        ang = math.radians(195 + i * 16)
        pts.append((20 + math.cos(ang) * 14, 18 + math.sin(ang) * 14))
    inner = []
    for i in range(18):
        ang = math.radians(195 + i * 16)
        rr = 14 - 8 * (1 - i / 18) ** .3 * (i / 18) ** .8
        inner.append((20 + math.cos(ang) * (14 - 5.5 * math.sin(i / 17 * math.pi) - .1), 18 + math.sin(ang) * (14 - 5.5 * math.sin(i / 17 * math.pi) - .1)))
    p = a.part(1.5)
    p.fill(pts + inner[::-1], (156, 176, 190), smooth=False)
    p.cel((100, 118, 138), 1.5, 1.7).rim((226, 238, 244))
    a.add(p)
    h = a.part(1.2)
    h.fill([S(4, 18), S(9, 18), S(9, 38), S(4, 38)], (92, 70, 52), smooth=False)
    h.rim((144, 112, 84))
    a.add(h)
    return a.done()


def item_cleave():
    a = Art(40, 40)
    h = a.part(1.1)
    h.fill([S(18.5, 0), S(21.5, 0), S(21.5, 18), S(18.5, 18)], (66, 50, 72), smooth=False)
    a.add(h)
    p = a.part(1.7)
    p.fill([S(5, 15), S(35, 15), (32, 26), S(31, 39), (20, 36), S(9, 39), (8, 26)], (152, 118, 158))
    p.cel((104, 78, 118), 2.5, 2.8).rim((204, 176, 208))
    a.add(p)
    return a.done()


def item_cloak():
    a = Art(40, 40)
    p = a.part(1.6)
    p.fill([S(13, 4), S(27, 4), (32, 16), S(37, 26), S(30, 25), S(29, 36), S(21, 30), S(14, 37), S(12, 27), S(3, 28), (8, 16)], (190, 200, 240))
    p.cel((130, 140, 190), 3, 3.2).rim((240, 244, 255))
    p.line([(14, 8), (20, 10), (26, 8)], (130, 140, 190), 1)
    a.add(p)
    return a.done()


def item_shard(t):
    a = Art(40, 40)
    p = a.part(1.6)
    p.fill([S(20, 2), S(32, 16), S(25, 37), S(15, 37), S(8, 16)], GOLD_L, smooth=False)
    p.shade([S(20, 3), S(31, 16), S(20, 20)], (255, 250, 220), smooth=False)
    p.shade([S(9, 16), S(20, 20), S(15, 36)], GOLD, smooth=False)
    p.shade([S(25, 36), S(20, 20), S(31, 16)], GOLD_S, smooth=False)
    a.add(p)
    if t:
        for x, y, r in ((33, 7, 3.5), (7, 30, 2.5)):
            s = a.part(0)
            s.fill([S(x, y - r), S(x + r * .3, y - r * .3), S(x + r, y), S(x + r * .3, y + r * .3), S(x, y + r), S(x - r * .3, y + r * .3), S(x - r, y), S(x - r * .3, y - r * .3)], (255, 255, 235), smooth=False)
            a.add(s)
    return a.done()


def item_whet():
    a = Art(40, 40)
    p = a.part(1.6)
    p.fill([S(3, 26), (15, 14), S(27, 8), S(37, 16), (25, 28), S(14, 35)], (126, 138, 162))
    p.cel((84, 94, 122), 2.4, 2.8).rim((194, 204, 224))
    a.add(p)
    return a.done()


def item_bell(t):
    """The last bell: 72x84."""
    a = Art(72, 84)
    r = -3.5 + t * 7
    R = lambda pts: poly_rot(pts, 36, 8, r)
    h = a.part(1.3)
    h.fill(R([S(34, 0), S(38, 0), S(38, 12), S(34, 12)]), (90, 78, 66), smooth=False)
    a.add(h)
    p = a.part(2.0)
    p.fill(R([S(29, 9), S(43, 9), (53, 26), (59, 48), S(68, 64), S(4, 64), (13, 48), (19, 26)]), GOLD)
    p.cel(GOLD_S, 4, 4.4).rim(GOLD_L, -1.4, -1.6)
    p.shade(R([S(9, 58), S(63, 58), S(68, 64), S(4, 64)]), (158, 112, 44))
    a.add(p)
    return a.done()


def small_bell(on):
    a = Art(30, 32)
    col = GOLD if on else (46, 40, 66)
    p = a.part(1.2)
    p.fill([S(12, 3), S(18, 3), (22, 13), S(27, 25), S(3, 25), (8, 13)], col)
    p.cel(GOLD_S if on else (34, 30, 52), 1.6, 1.8)
    if on:
        p.rim(GOLD_L)
    a.add(p)
    return a.done()


def heart(full):
    a = Art(22, 20)
    pts = [S(11, 18), (3, 10), (2, 5.5), (6, 2.5), S(11, 6), (16, 2.5), (20, 5.5), (19, 10)]
    p = a.part(1.2)
    if full:
        p.fill(pts, (196, 164, 244))
        p.cel((132, 104, 190), 1.3, 1.5)
        p.dot(6.5, 6, 1.8, 1.5, (246, 236, 255))
    else:
        p.fill(pts, (40, 32, 62))
    a.add(p)
    return a.done()


# ------------------------------------------------------------------ projectiles and effects
def proj_drop(t):
    a = Art(22, 30)
    p = a.part(1.2)
    p.fill([S(11, 1), (17, 15), (15, 23), (11, 27), (7, 23), (5, 15)], (120, 196, 224))
    p.cel((70, 140, 180), 1.6, 1.8)
    p.dot(9, 17, 1.5, 2.6, (226, 248, 255))
    a.add(p)
    return a.done()


def proj_wave(t):
    a = Art(34, 38)
    k = t * 3.5
    p = a.part(1.4)
    p.fill([S(1, 37), S(5 + k, 20), S(9, 3 + k), S(15, 17), S(21 - k, 8 + k), S(26, 22), S(33, 37)], (236, 244, 255), smooth=False)
    p.cel((150, 196, 236), 2, 2.4)
    a.add(p)
    return a.done()


def proj_orb(t):
    a = Art(26, 26)
    for r_, al in ((12, .18), (10, .22)):
        a.glow([(13 + math.cos(i / 14 * math.tau) * (r_ + t), 13 + math.sin(i / 14 * math.tau) * (r_ + t)) for i in range(14)], (255, 130, 50), al, smooth=False)
    p = a.part(1.1)
    p.circle(13, 13, 7, col=(255, 150, 44))
    p.cel((214, 84, 24), 1.2, 1.5)
    p.dot(11, 11, 3, 3, (255, 244, 176))
    a.add(p)
    return a.done()


def spark(n):
    a = Art(48, 48)
    r = (9, 18, 22, 24)[n]
    w = (5, 3.4, 2, 1)[n]
    p = a.part(0)
    c = (255, 250, 226)
    for ang in range(0, 360, 45):
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        rr = r * (1 if ang % 90 == 0 else .65)
        r0 = r * .45 * (n > 0)
        p.fill([S(24 + ca * r0 - sa * w * .4, 24 + sa * r0 + ca * w * .4), S(24 + ca * rr, 24 + sa * rr), S(24 + ca * r0 + sa * w * .4, 24 + sa * r0 - ca * w * .4)], c, smooth=False)
    a.add(p)
    return a.done()


def dust(n):
    a = Art(28, 24)
    r = (4, 7, 9, 10)[n]
    al = (.9, .75, .45, .2)[n]
    for dx, dy, k in ((-5, 0, 1), (5, 1, .85), (0, -3, 1.1)):
        a.glow([(14 + dx * (1 + n * .3) + math.cos(i / 12 * math.tau) * r * k, 15 + dy - n + math.sin(i / 12 * math.tau) * r * k * .8) for i in range(12)], (206, 198, 214), al * .6, smooth=False)
    return a.done()


def mote(n):
    a = Art(12, 12)
    a.glow([(6 + math.cos(i / 10 * math.tau) * 5, 6 + math.sin(i / 10 * math.tau) * 5) for i in range(10)], (220, 204, 255), .35, smooth=False)
    p = a.part(0)
    p.circle(6, 6, 1.6 + n * .8, col=(246, 238, 255))
    a.add(p)
    return a.done()


def ring(n):
    """Shockwave when a Cleave lands."""
    a = Art(64, 26)
    rx = (10, 18, 25, 30)[n]
    ry = rx * .32
    t = (2.6, 2, 1.3, .8)[n]
    outer = [(32 + math.cos(i / 24 * math.tau) * rx, 13 + math.sin(i / 24 * math.tau) * ry) for i in range(24)]
    inner = [(32 + math.cos(i / 24 * math.tau) * (rx - t), 13 + math.sin(i / 24 * math.tau) * (ry - t * .4)) for i in range(24)]
    p = a.part(0)
    p.fill(outer + outer[:1] + inner[:1] + inner[::-1], (240, 232, 255), smooth=False)
    a.add(p)
    return a.done()


def shadow(w):
    a = Art(w, 12)
    a.glow([(w / 2 + math.cos(i / 24 * math.tau) * (w / 2 - 1), 6 + math.sin(i / 24 * math.tau) * 4.5) for i in range(24)], (8, 6, 16), .28, smooth=False)
    a.glow([(w / 2 + math.cos(i / 24 * math.tau) * (w / 2 - 6), 6 + math.sin(i / 24 * math.tau) * 3) for i in range(24)], (8, 6, 16), .3, smooth=False)
    return a.done()


def hook_link():
    a = Art(12, 12)
    p = a.part(1.0)
    p.circle(6, 6, 3.6, col=(190, 202, 218))
    p.cel((130, 142, 164), 1, 1.2)
    a.add(p)
    return a.done()


def anchor_ring(lit):
    a = Art(32, 32)
    if lit:
        for r_, al in ((15, .16), (11, .2)):
            a.glow([(16 + math.cos(i / 20 * math.tau) * r_, 16 + math.sin(i / 20 * math.tau) * r_) for i in range(20)], (255, 226, 130), al, smooth=False)
    outer = [(16 + math.cos(i / 24 * math.tau) * 10.5, 16 + math.sin(i / 24 * math.tau) * 10.5) for i in range(25)]
    inner = [(16 + math.cos(i / 24 * math.tau) * 6.5, 16 + math.sin(i / 24 * math.tau) * 6.5) for i in range(25)]
    p = a.part(1.4)
    p.fill(outer + inner[::-1], GOLD_L if lit else (176, 150, 96), smooth=False)
    p.cel(GOLD_S if lit else (116, 96, 62), 1.2, 1.4)
    a.add(p)
    return a.done()


def up_mark():
    a = Art(18, 20)
    p = a.part(1.2)
    p.fill([S(9, 1), S(16, 10), S(12, 10), S(12, 18), S(6, 18), S(6, 10), S(2, 10)], (255, 240, 180), smooth=False)
    p.cel((214, 176, 96), 1, 1.2)
    a.add(p)
    return a.done()
