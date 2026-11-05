"""Menuel himself, redrawn after the user's drawing, and his full animation set."""
import math
from ink import *

MASK = (240, 234, 253)
MASK_S = (198, 184, 228)
GEM = (190, 168, 226)
CLOAK = (104, 84, 150)
CLOAK_L = (146, 124, 186)
CLOAK_S = (70, 58, 112)
BAND = (54, 54, 98)
BAND_S = (38, 38, 74)
LEG = (20, 14, 30)
LEG_R = (70, 60, 104)
BLADE = (152, 118, 158)
BLADE_L = (204, 176, 208)
BLADE_S = (104, 78, 118)
POLE = (66, 50, 72)
POLE_L = (112, 90, 112)
STEEL = (150, 160, 186)

W_, H_ = 170, 150
AX, AY = 85, 112        # anchor: between the feet


def tapered_leg(a, hx, hy, fx, fy, bend=0.0):
    """A long black spike from the hip to the foot, slightly bowed like a knee."""
    p = a.part(ink=0)
    mx, my = (hx + fx) / 2 + bend, (hy + fy) / 2
    p.fill([S(hx - 5.6, hy), (mx - 3.1, my), (fx - 1.0, fy - 5), S(fx, fy), (fx + 1.0, fy - 5), (mx + 3.1, my), S(hx + 5.6, hy)], LEG)
    a.add(p)
    p2 = a.part(ink=0)
    p2.fill([S(hx - 4.0, hy), (mx - 2.3, my), S(mx - 1.5, my + 8), (mx - 1.2, my), S(hx - 1.8, hy)], LEG_R)
    a.add(p2)


def draw_axe(a, hx, hy, deg, reach=1.0, bladescale=1.0):
    """Long pole, big flag blade at the far end, a steel butt at the near end."""
    R = lambda pts: poly_rot(pts, hx, hy, deg)
    L0, L1 = -17 * reach, 30 * reach
    p = a.part(ink=1.0)
    p.fill(R([S(hx + L0, hy - 1.5), S(hx + L1, hy - 1.5), S(hx + L1, hy + 1.5), S(hx + L0, hy + 1.5)]), POLE, smooth=False)
    p.shade(R([S(hx + L0, hy - 1.5), S(hx + L1, hy - 1.5), S(hx + L1, hy - .4), S(hx + L0, hy - .4)]), POLE_L, smooth=False)
    a.add(p)
    b = a.part(ink=1.0)
    b.fill(R([S(hx + L0 - 5, hy), (hx + L0 - 1, hy - 2.8), S(hx + L0 + 2, hy - 2.2), S(hx + L0 + 2, hy + 2.2), (hx + L0 - 1, hy + 2.8)]), STEEL)
    b.cel((96, 104, 132))
    a.add(b)
    k = bladescale
    x0 = hx + L1 - 3
    blade = a.part(ink=1.7)
    blade.fill(R([S(x0, hy + 1), (x0 + 1.5 * k, hy - 9 * k), S(x0 + 3 * k, hy - 19 * k), (x0 + 13 * k, hy - 20 * k), S(x0 + 24 * k, hy - 24 * k),
                  (x0 + 25 * k, hy - 11 * k), S(x0 + 28 * k, hy + 1 * k), (x0 + 14 * k, hy + 2.5 * k), S(x0 + 2 * k, hy + 6 * k)]), BLADE)
    blade.cel(BLADE_S, 3, 3.4)
    blade.rim(BLADE_L, -1.2, -1.2)
    blade.line(R([(x0 + 5 * k, hy - 13 * k), (x0 + 14 * k, hy - 14.5 * k), (x0 + 22 * k, hy - 17.5 * k)]), BLADE_L, .7)
    a.add(blade)


def smear(a, cx, cy, r0, r1, ang0, ang1, col=(244, 238, 255), alpha=.5):
    """A thin crescent along the blade's path: fades towards the tail, three soft layers instead of a flat wedge."""
    span = ang1 - ang0
    for thick, al, start in ((13, .16, 0.0), (8, .2, .25), (3.5, .34, .5)):
        n = 14
        outer, inner = [], []
        for i in range(n + 1):
            t = start + (1 - start) * i / n
            ang = math.radians(ang0 + span * t)
            th = thick * math.sin((i / n) * math.pi) ** .8
            ro = r1 + 3
            outer.append((cx + math.cos(ang) * ro, cy + math.sin(ang) * ro))
            inner.append((cx + math.cos(ang) * (ro - th), cy + math.sin(ang) * (ro - th)))
        a.glow(outer + inner[::-1], col, al * alpha * 2, smooth=False)


def body(a, cx, hip, lean, sway, ripple, tip_phase, sq=(1.0, 1.0)):
    """Spiky cloak. Each tip trails the motion on its own, so the hem ripples instead of moving as one piece."""
    sx, sy = sq
    ccx, ccy = cx + lean, hip - 10 * sy
    tips = [(196, 30), (168, 31), (140, 28), (113, 25), (88, 23), (62, 25), (35, 28), (8, 31), (-16, 28)]
    pts = [S(ccx - 11 * sx, ccy - 13 * sy)]
    for i, (angd, ln) in enumerate(tips):
        ang = math.radians(angd)
        ph = tip_phase + i * .13
        wob = math.sin(ph * math.tau) * ripple
        drag = sway * (.5 + .5 * (1 - abs(math.cos(ang))))
        tx = ccx + math.cos(ang) * (ln + wob) * sx - sway * (.5 + i * .02) + (drag * -.3)
        ty = ccy + math.sin(ang) * (ln + wob * .6) * sy + abs(sway) * .1 - abs(math.cos(ang)) * abs(sway) * .18
        if i:
            pa = math.radians((tips[i - 1][0] + angd) / 2)
            pts.append((ccx + math.cos(pa) * 18.5 * sx, ccy + math.sin(pa) * 16.5 * sy))
        pts.append(S(tx, ty))
    pts.append(S(ccx + 11 * sx, ccy - 13 * sy))
    p = a.part(ink=1.7)
    p.fill(pts, CLOAK)
    p.cel(CLOAK_S, 3.2, 3.8)
    p.rim(CLOAK_L, -1.6, -1.8)
    # the dark sweep across the chest, as in the drawing
    p.shade([S(ccx - 30 * sx - sway * .4, ccy + 3 * sy), S(ccx + 13 * sx, ccy - 12 * sy), S(ccx + 18 * sx, ccy - 5 * sy), S(ccx - 19 * sx, ccy + 11 * sy)], BAND)
    p.shade([S(ccx - 24 * sx, ccy + 7 * sy), S(ccx + 16 * sx, ccy - 7 * sy), S(ccx + 18 * sx, ccy - 5 * sy), S(ccx - 19 * sx, ccy + 11 * sy)], BAND_S)
    p.line([(ccx - 14 * sx, ccy - 2 * sy), (ccx - 10 * sx, ccy + 2 * sy)], INK, .9)
    p.line([(ccx - 10 * sx, ccy - 2 * sy), (ccx - 14 * sx, ccy + 2 * sy)], INK, .9)
    p.line([(ccx + 1 * sx, ccy + 7 * sy), (ccx + 4 * sx, ccy + 9.5 * sy), (ccx + 7.5 * sx, ccy + 6 * sy)], INK, 1.0)
    a.add(p)


def head(a, hx, top, rot=0.0, eye=1.0, sq=(1.0, 1.0), mood=0.0):
    """The kite mask: sharp crown and chin, soft shoulders, big inward-slanted slit eyes."""
    sx, sy = sq
    cx, cy = hx, top + 21 * sy
    R = lambda pts: poly_rot(pts, cx, cy, rot)
    p = a.part(ink=1.9)
    p.fill(R([S(hx, top), (hx + 11 * sx, top + 14 * sy), (hx + 19.5 * sx, top + 27 * sy), (hx + 11 * sx, top + 35 * sy), S(hx + .8, top + 42 * sy),
              S(hx - .8, top + 42 * sy), (hx - 11 * sx, top + 35 * sy), (hx - 19.5 * sx, top + 27 * sy), (hx - 11 * sx, top + 14 * sy)]), MASK)
    p.cel(MASK_S, 2.6, 3.2)
    ey = top + 25 * sy
    for s in (-1, 1):
        ex = hx + s * 9.2 * sx
        h = (3.2 * eye + .35) * sy
        slant = (1.8 + mood * 1.4) * sy
        if eye <= .08:
            p.line(R([(ex + s * 5.6 * sx, ey - slant * .5), (ex, ey + .3), (ex - s * 5.2 * sx, ey + slant)]), INK, 1.1)
        else:
            p.shade(R([S(ex + s * 6 * sx, ey - slant - h * .5), (ex + s * 1.5 * sx, ey - h * .55), S(ex - s * 5.4 * sx, ey + slant), (ex - s * 2 * sx, ey + h + 1.1),
                       S(ex + s * 4.6 * sx, ey + h * .6 - slant * .4)]), INK)
            p.dot(*R([(ex + s * 2.1 * sx, ey - h * .1)])[0], .75, .75, (240, 234, 253))
    # the small forehead mark
    p.shade(R([S(hx + 5.6 * sx, top + 9.5 * sy), S(hx + 9.2 * sx, top + 14.5 * sy), S(hx + 6 * sx, top + 19.5 * sy), S(hx + 2.4 * sx, top + 14.5 * sy)]), GEM)
    a.add(p)


def pose(leg_l=(-6, 0), leg_r=(6, 0), bob=0.0, lean=0.0, sway=0.0, ripple=1.0, phase=0.0, axe=None, axe_front=False,
         head_dx=0.0, head_dy=0.0, rot=0.0, eye=1.0, sq=(1.0, 1.0), mood=0.0, hand=(9, -9), glow=None, smear_args=None, reach=1.0):
    """Draws one frame. leg_l, leg_r: foot offsets from the anchor (y up is negative). hip is above the anchor."""
    a = Art(W_, H_)
    sx, sy = sq
    hip = AY - 24 * sy + bob
    cx = AX
    if glow:
        for r_, al in ((38, .05), (33, .06), (28, .07), (23, .08), (18, .09)):
            pts = [(cx + math.cos(i / 24 * math.tau) * r_, hip - 18 + math.sin(i / 24 * math.tau) * r_ * 1.2) for i in range(24)]
            a.glow(pts, glow, al, smooth=False)
    if smear_args:
        smear(a, cx + hand[0] + lean, hip + hand[1], *smear_args)
    if axe is not None and not axe_front:
        draw_axe(a, cx + hand[0] + lean, hip + hand[1], axe, reach)
    for (off, f, b) in ((-5, leg_l, -1.2), (5, leg_r, 1.2)):
        tapered_leg(a, cx + off * sx + lean * .6, hip - 5, cx + f[0], AY + f[1], b)
    body(a, cx, hip, lean, sway, ripple, phase, sq)
    top = hip - 57 * sy + head_dy
    head(a, cx + lean * 1.25 + head_dx, top, rot, eye, sq, mood)
    if axe is not None and axe_front:
        draw_axe(a, cx + hand[0] + lean, hip + hand[1], axe, reach)
    return a.done()


def player_frames():
    F = {}
    # idle: slow breath, the cloak breathing a beat later, one blink
    for i in range(8):
        t = i / 8
        br = tau(t)
        F['IDLE%d' % i] = pose(bob=br * .9, sway=tau(t + .2) * 1.4, ripple=.7, phase=t, axe=-54 + tau(t + .1) * 1.8, head_dy=tau(t - .12) * .7,
                               rot=tau(t) * .6, eye=.06 if i == 6 else 1.0, sq=(1 - br * .008, 1 + br * .01))
    # run: ten frames with real foot contacts; the head lags, the hem streams behind
    n = 10
    for i in range(n):
        t = i / n
        a_ = t * math.tau
        fl = (math.cos(a_) * 13, min(0, -math.sin(a_)) * 7)
        fr = (math.cos(a_ + math.pi) * 13, min(0, -math.sin(a_ + math.pi)) * 7)
        step = abs(math.sin(a_))
        F['RUN%d' % i] = pose(leg_l=fl, leg_r=fr, bob=-step * 2.4 + .8, lean=3.5 + math.sin(a_ * 2) * .6, sway=7 + step * 2.5, ripple=2.0, phase=t * 2, axe=-34 + math.sin(a_) * 8,
                              head_dy=-step * 1.1, rot=2.2 + math.sin(a_ * 2 - .6) * 1.2, sq=(1 + step * .012, 1 - step * .012 + .012))
    # jump
    F['RISE0'] = pose(leg_l=(-3, -3), leg_r=(7, -9), bob=-1.5, sway=-3, ripple=1, phase=.1, axe=-74, lean=1.5, rot=-2, sq=(.93, 1.09))
    F['RISE1'] = pose(leg_l=(-5, -6), leg_r=(8, -11), bob=-1, sway=-1, ripple=1.2, phase=.3, axe=-68, lean=1, rot=-1, sq=(.97, 1.04))
    F['APEX'] = pose(leg_l=(-7, -9), leg_r=(7, -12), bob=0, sway=2, ripple=2, phase=.6, axe=-56, sq=(1.02, .99))
    F['FALL0'] = pose(leg_l=(-5, -7), leg_r=(7, -6), sway=5, ripple=2.3, phase=.8, axe=-42, rot=1.5, sq=(1.0, 1.02), eye=.9)
    F['FALL1'] = pose(leg_l=(-6, -5), leg_r=(6, -4), sway=7, ripple=2.6, phase=1.1, axe=-36, rot=2, sq=(.97, 1.05), eye=.85)
    # landing: squash and recover
    F['LAND0'] = pose(leg_l=(-10, 0), leg_r=(10, 0), bob=7, sway=-5, ripple=2.5, phase=.2, axe=-30, sq=(1.13, .84), eye=.5)
    F['LAND1'] = pose(leg_l=(-9, 0), leg_r=(9, 0), bob=4, sway=-3, ripple=1.8, phase=.4, axe=-40, sq=(1.07, .92), eye=.8)
    F['LAND2'] = pose(leg_l=(-7, 0), leg_r=(7, 0), bob=1.5, sway=-1, ripple=1, phase=.6, axe=-50, sq=(1.02, .98))
    # first swing: anticipation, overhead arc, follow through, settle
    A = [(-150, 2, -2, False, None, .9, .4), (-142, 3, -3, False, None, 1, .9), (-85, 5, 1, True, (18, 62, -142, -86), 1, 1),
         (-20, 8, 4, True, (16, 66, -92, -20), 1, 1), (32, 9, 5, True, (18, 62, -28, 32), 1, 1), (46, 8, 3, True, (24, 58, 28, 46), .9, 1), (30, 5, 1, True, None, .9, .4)]
    for i, (ang, lean, bob, front, sm, sqk, mood) in enumerate(A):
        F['ATKA%d' % i] = pose(leg_l=(-11, 0), leg_r=(11, 0), bob=bob, lean=lean, sway=4 + i, ripple=1.8, phase=i * .15, axe=ang, axe_front=front,
                               smear_args=sm, mood=mood, rot=lean * .6, sq=(1 + (.02 if i >= 2 else -.03), 1 - (.02 if i >= 2 else -.04)), head_dy=-1 if i < 2 else 0)
    # second swing: a low backhand rising, so repeated attacks do not look the same
    B = [(70, 2, 2, True, None, .9, .4), (80, 4, 3, True, None, 1, .9), (40, 7, 3, True, (18, 62, 82, 40), 1, 1),
         (-30, 9, 1, False, (16, 66, 44, -30), 1, 1), (-92, 7, -2, False, (18, 62, -28, -92), 1, 1), (-120, 5, -2, False, (24, 58, -88, -120), .9, 1), (-90, 3, 0, False, None, .9, .4)]
    for i, (ang, lean, bob, front, sm, sqk, mood) in enumerate(B):
        F['ATKB%d' % i] = pose(leg_l=(-10, 0), leg_r=(12, 0), bob=bob, lean=lean, sway=5 - i * .4, ripple=1.8, phase=.5 + i * .15, axe=ang, axe_front=front,
                               smear_args=sm, mood=mood, rot=lean * .6, sq=(1 - (.02 if i < 3 else -.02), 1 + (.03 if i >= 3 else -.03)))
    # rush: stretched, flat, hem pulled out behind
    for i, (k, sw) in enumerate(((1.12, 11), (1.2, 15), (1.2, 16), (1.1, 12))):
        F['DASH%d' % i] = pose(leg_l=(-20, -7), leg_r=(-9, -4), bob=3, lean=11, sway=sw, ripple=2.6, phase=i * .3, axe=-6, hand=(-4, -8), rot=9, sq=(k, 2 - k * .98), mood=.8,
                               head_dy=2)
    F['HURT0'] = pose(leg_l=(-13, -3), leg_r=(3, -6), bob=1, lean=-7, sway=-8, ripple=3, phase=.1, axe=-125, rot=-12, eye=.08, sq=(.92, 1.06))
    F['HURT1'] = pose(leg_l=(-10, -2), leg_r=(5, -3), bob=2, lean=-5, sway=-6, ripple=3, phase=.4, axe=-115, rot=-8, eye=.3, sq=(.97, 1.0))
    for i in range(4):
        t = i / 4
        F['HEAL%d' % i] = pose(leg_l=(-9, 0), leg_r=(9, 0), bob=5 + tau(t) * .8, sway=tau(t) * 2, ripple=1.3, phase=t, axe=-92, hand=(0, -13), eye=.08, sq=(1.05, .93),
                               glow=(214, 196, 255), head_dy=1 + tau(t) * .6, rot=tau(t) * .8)
    F['HOOK0'] = pose(leg_l=(-9, -7), leg_r=(1, -3), lean=4, sway=6, ripple=2, phase=.2, axe=-72, rot=-3, sq=(.96, 1.05), mood=.6)
    F['HOOK1'] = pose(leg_l=(-11, -9), leg_r=(-1, -5), lean=6, sway=9, ripple=2.4, phase=.6, axe=-70, rot=-4, sq=(.93, 1.09), mood=.6)
    F['CLEAVE0'] = pose(leg_l=(-6, -8), leg_r=(6, -10), bob=-5, sway=-2, ripple=2, phase=.1, axe=-100, sq=(.92, 1.1), mood=1, axe_front=True, hand=(0, -22))
    F['CLEAVE1'] = pose(leg_l=(-4, -8), leg_r=(4, -8), bob=-2, sway=-5, ripple=2.8, phase=.4, axe=90, axe_front=True, hand=(0, -6), sq=(.88, 1.15), mood=1,
                        smear_args=(22, 56, 20, 90))
    F['CLEAVE2'] = pose(leg_l=(-3, -8), leg_r=(3, -8), bob=-2, sway=-7, ripple=3, phase=.7, axe=90, axe_front=True, hand=(0, -6), sq=(.85, 1.18), mood=1)
    F['CLEAVE3'] = pose(leg_l=(-3, -8), leg_r=(3, -8), bob=-2, sway=-8, ripple=3, phase=1.0, axe=90, axe_front=True, hand=(0, -6), sq=(.85, 1.18), mood=1)
    # death: knocked back, cracks to the ground, fades in code
    for i, (lean, bob, rot, sw, sqy) in enumerate(((-6, 2, -14, -8, .96), (-9, 6, -24, -10, .92), (-11, 12, -38, -8, .86), (-12, 17, -56, -5, .80), (-12, 21, -72, -3, .76), (-12, 22, -78, -2, .75))):
        F['DIE%d' % i] = pose(leg_l=(-18, -2), leg_r=(0, -1), bob=bob, lean=lean, sway=sw, ripple=2 - i * .2, phase=i * .2, axe=-160 + i * 8, rot=rot, eye=.08, sq=(1.06, sqy))
    return F


if __name__ == '__main__':
    import sys
    from PIL import Image
    F = player_frames()
    bg = (46, 44, 70, 255)
    cols = 10
    rows = (len(F) + cols - 1) // cols
    cw, ch = 110, 110
    sheet = Image.new('RGBA', (cols * cw, rows * ch), bg)
    for i, im in enumerate(F.values()):
        tile = im.crop((30, 10, 140, 120))
        sheet.alpha_composite(tile, ((i % cols) * cw, (i // cols) * ch))
    sheet.save(sys.argv[1])
    F['IDLE0'].resize((W_ * 4, H_ * 4), Image.LANCZOS).save(sys.argv[1].replace('.png', '_big.png'))
    print(len(F))
