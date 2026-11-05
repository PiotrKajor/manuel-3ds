#!/usr/bin/env python3
"""Builds build/assets.bin, src/gen.h and src/gen_world.c from art.py, world.py and music.py."""
import os, struct, sys, random, math
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw
import art as A
import world as W
import music as M

ROOT = os.path.join(os.path.dirname(__file__), '..')
KEY = 0xF81F


def rgb565(c):
    v = ((c[0] >> 3) << 11) | ((c[1] >> 2) << 5) | (c[2] >> 3)
    return 0xF81E if v == KEY else v


blob = bytearray()
sprites = []


def add_pixels(name, w, h, px):
    off = len(blob) // 2
    blob.extend(struct.pack('<%dH' % len(px), *px))
    sprites.append((name, w, h, off))


def cv_px(cv, pal, scale=2):
    px = []
    for y in range(cv.h):
        row = [KEY if cv.get(x, y) == 0 else rgb565(pal[cv.get(x, y)]) for x in range(cv.w) for _ in range(scale)]
        for _ in range(scale):
            px += row
    return px


def add_cv(name, cv, pal, scale=2):
    add_pixels(name, cv.w * scale, cv.h * scale, cv_px(cv, pal, scale))


def add_im(name, im):
    im = im.convert('RGBA')
    px = [KEY if a < 128 else rgb565((r, g, b)) for r, g, b, a in im.getdata()]
    add_pixels(name, im.width, im.height, px)


# ------------------------------------------------------------------ Menuel: native 32x32 drawn after the reference
INK, MASK, MSHADE, CLOAK, CDARK, BLADE = (14, 10, 24), (232, 224, 250), (196, 180, 226), (92, 72, 130), (58, 46, 92), (146, 112, 150)


def menuel(leg=0, bob=0, tip=0, lean=0, squash=0, heal=False):
    im = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = 15 + lean
    for lx, off in ((12 + leg, 0), (19 - leg, 0)):
        d.polygon([(lx - 2, 22 + bob), (lx + 2, 22 + bob), (lx, 31)], fill=INK)
    cy = 15 + bob + squash
    pts = [(cx - 6, cy), (cx - 12, cy + 2 - tip), (cx - 8, cy + 4), (cx - 13, cy + 8 - tip), (cx - 7, cy + 8), (cx - 4, cy + 12),
           (cx, cy + 9), (cx + 4, cy + 12), (cx + 7, cy + 8), (cx + 13, cy + 8 + tip), (cx + 8, cy + 4), (cx + 12, cy + 2 + tip), (cx + 6, cy)]
    d.polygon(pts, fill=CLOAK, outline=INK)
    d.polygon([(cx - 8, cy + 6), (cx + 3, cy + 1), (cx + 5, cy + 4), (cx - 5, cy + 9)], fill=CDARK)
    d.line([(cx + 1, cy + 7), (cx + 4, cy + 6)], fill=INK)
    t = bob
    head = [(cx, t), (cx + 9, t + 10 + squash), (cx + 1, t + 18), (cx - 1, t + 18), (cx - 9, t + 10 + squash)]
    d.polygon(head, fill=MASK, outline=INK)
    d.polygon([(cx + 8, t + 11 + squash), (cx + 1, t + 17), (cx, t + 13)], fill=MSHADE)
    e = t + 10 + squash
    d.polygon([(cx - 6, e - 1), (cx - 2, e + 2), (cx - 3, e + 3), (cx - 6, e + 1)], fill=INK)
    d.polygon([(cx + 6, e - 1), (cx + 2, e + 2), (cx + 3, e + 3), (cx + 6, e + 1)], fill=INK)
    d.polygon([(cx + 2, t + 4), (cx + 4, t + 6), (cx + 2, t + 8), (cx, t + 6)], fill=MSHADE)
    if heal:
        d.point([(cx - 11, t + 4), (cx + 11, t + 8), (cx - 8, t + 13)], fill=(255, 255, 255))
    return im


def axe(kind):
    im = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def blade(pts):
        d.polygon(pts, fill=BLADE, outline=INK)
        d.line([pts[0], pts[1]], fill=MASK)
    if kind == 0:   # raised
        d.line([(4, 36), (17, 16)], fill=INK, width=3)
        blade([(12, 2), (34, 3), (36, 16), (15, 22)])
    elif kind == 1: # level
        d.line([(0, 22), (20, 20)], fill=INK, width=3)
        blade([(18, 6), (38, 3), (39, 33), (18, 30)])
    elif kind == 2: # low
        d.line([(0, 8), (17, 24)], fill=INK, width=3)
        blade([(15, 18), (36, 16), (34, 38), (9, 37)])
    elif kind == 3: # straight down
        d.line([(19, 0), (19, 18)], fill=INK, width=3)
        blade([(7, 17), (32, 17), (28, 38), (11, 38)])
    else:           # carried
        d.line([(3, 38), (11, 20)], fill=INK, width=3)
        blade([(4, 4), (24, 1), (27, 17), (9, 22)])
    return im


for i, a in enumerate([(0, 0, 0), (0, 1, 1), (2, 0, 1), (0, 1, 0), (-2, 0, 1), (0, 1, 0), (2, 0, -1), (-2, 0, 2), (2, 0, 0, 2), (2, 1, 2, 4), (-2, 0, 2, -2)]):
    add_im('MENUEL%d' % i, menuel(*a))
add_im('MENUEL11', menuel(0, 2, 2, 0, 1, heal=True))
for k in range(5):
    add_im('AXE%d' % k, axe(k))
# ------------------------------------------------------------------ everything else at 2x
for ei, fn in enumerate(A.ENEMY_ART):
    t = A.THEMES[ei // 2]
    pal = t['en1' if ei % 2 == 0 else 'en2']
    for f in range(2):
        add_cv('EN%d_%d' % (ei, f), fn(f), pal)
for ni, fn in enumerate(A.NPC_ART):
    for f in range(2):
        add_cv('NPC%d_%d' % (ni, f), fn(f), A.NPC_PAL)
for nm, cv in (('IT_RUSH', A.item_rush()), ('IT_HOOK', A.item_hook()), ('IT_CLEAVE', A.item_cleave()), ('IT_CLOAK', A.item_cloak()),
               ('IT_SHARD', A.item_shard(0)), ('IT_SHARD1', A.item_shard(1)), ('IT_WHET', A.item_whet()), ('IT_BELL', A.item_bell(0)), ('IT_BELL1', A.item_bell(1))):
    add_cv(nm, cv, A.ITEM_PAL)
for i in range(3):
    add_cv('SPARK%d' % i, A.spark(i), A.FX_PAL)
add_cv('MOTE0', A.mote(0), A.FX_PAL); add_cv('MOTE1', A.mote(1), A.FX_PAL)
for nm, fn in (('DROP', A.proj_drop), ('WAVE', A.proj_wave), ('ORB', A.proj_orb)):
    for i in range(2):
        add_cv('%s%d' % (nm, i), fn(i), [(0, 0, 0), (40, 20, 40), (240, 130, 70) if nm == 'ORB' else (120, 170, 220), (255, 240, 200)])
add_cv('LINK', A.hook_link(), A.FX_PAL)
add_cv('UPMARK', A.up_mark(), A.FX_PAL)
for b, fn in enumerate(A.BOSS_ART):
    for f in range(5):
        add_cv('BOSS%d_%d' % (b, f), fn(f), A.BOSS_PALS[b])
add_cv('HEART_FULL', A.common_tiles()[0][A.common_tiles()[1]['heart_full']], [(0, 0, 0), (40, 10, 30), (150, 110, 200), (240, 230, 255)])
add_cv('HEART_EMPTY', A.common_tiles()[0][A.common_tiles()[1]['heart_empty']], [(0, 0, 0), (110, 100, 130), (0, 0, 0), (0, 0, 0)])


# ------------------------------------------------------------------ title art from the user's drawing
def clean_reference():
    im = Image.open(os.path.join(ROOT, 'docs', 'menuel-reference.png')).convert('RGB')
    w, h = im.size
    px = im.load()
    mask = Image.new('L', im.size, 255)
    mp = mask.load()
    stack = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    while stack:
        x, y = stack.pop()
        if not (0 <= x < w and 0 <= y < h) or mp[x, y] == 0:
            continue
        r, g, b = px[x, y]
        if min(r, g, b) < 235:
            continue
        mp[x, y] = 0
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    # remove the neighbouring figures cropped by the edge of the drawing
    d = ImageDraw.Draw(mask)
    d.rectangle((0, 170, 24, h), fill=0)
    d.rectangle((340, 280, w, h), fill=0)
    out = im.convert('RGBA')
    out.putalpha(mask)
    return out.crop(out.getbbox())


ref = clean_reference()
ts = 196 / ref.height
title_art = ref.resize((int(ref.width * ts), 196), Image.LANCZOS)
add_im('TITLE', title_art)
os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
icon = Image.new('RGBA', (48, 48), (28, 22, 48, 255))
small = ref.resize((int(ref.width * 46 / ref.height), 46), Image.LANCZOS)
small = small.crop((0, 0, 48, 46)) if small.width > 48 else small
icon.alpha_composite(small, ((48 - small.width) // 2, 1))
icon.save(os.path.join(ROOT, 'build', 'icon.png'))
banner = Image.new('RGBA', (256, 128), (28, 22, 48, 255))
bs = ref.resize((int(ref.width * 120 / ref.height), 120), Image.LANCZOS)
banner.alpha_composite(bs, ((256 - bs.width) // 2, 4))
banner.save(os.path.join(ROOT, 'build', 'banner.png'))


# ------------------------------------------------------------------ backdrops
def backdrop(theme):
    rnd = random.Random(theme * 7 + 3)
    im = Image.new('RGB', (200, 120))
    d = ImageDraw.Draw(im)
    tops = [(16, 20, 44), (6, 26, 36), (40, 14, 10), (18, 14, 48)]
    bots = [(26, 34, 62), (10, 46, 56), (84, 30, 14), (56, 46, 92)]
    a, b = tops[theme], bots[theme]
    for y in range(120):
        t = y / 119
        band = int(t * 12) / 12
        d.line([(0, y), (199, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * band) for i in range(3)))
    if theme == 0:  # salt veins and props
        c = (40, 50, 80)
        for _ in range(16):
            x, y = rnd.randrange(200), rnd.randrange(120)
            for _ in range(4):
                nx, ny = x + rnd.randint(-14, 14), y + rnd.randint(-10, 10)
                d.line([(x, y), (nx, ny)], fill=c)
                x, y = nx, ny
        for x in (30, 95, 160):
            d.rectangle((x, 0, x + 5, 119), fill=(30, 36, 62))
            d.rectangle((x - 12, 18, x + 17, 22), fill=(30, 36, 62))
    elif theme == 1:  # drowned arches
        c = (10, 40, 50)
        for x in (-10, 50, 110, 170):
            d.arc((x, 16, x + 50, 110), 180, 360, fill=c, width=4)
            d.rectangle((x - 2, 62, x + 3, 119), fill=c)
        for y in range(88, 120, 5):
            for _ in range(7):
                x = rnd.randrange(200)
                d.line([(x, y), (x + rnd.randint(4, 14), y)], fill=(16, 66, 76))
    elif theme == 2:  # furnace mouths and gears
        for x in (24, 92, 164):
            d.rectangle((x - 13, 30, x + 13, 119), fill=(36, 16, 12))
            d.ellipse((x - 7, 46, x + 7, 60), fill=(160, 60, 16))
            d.ellipse((x - 4, 49, x + 4, 57), fill=(245, 170, 60))
        for _ in range(26):
            x, y = rnd.randrange(200), rnd.randrange(120)
            d.point((x, y), fill=(190, 90, 30))
    else:  # night sky over peaks
        for _ in range(60):
            d.point((rnd.randrange(200), rnd.randrange(70)), fill=(170, 170, 220))
        d.ellipse((150, 12, 170, 32), fill=(214, 214, 240))
        d.ellipse((145, 10, 165, 30), fill=a)
        for pk, base, col in (((40, 40), 120, (34, 30, 72)), ((110, 26), 120, (34, 30, 72)), ((175, 46), 120, (34, 30, 72))):
            d.polygon([(pk[0] - 60, base), pk, (pk[0] + 60, base)], fill=col)
            d.polygon([(pk[0] - 9, pk[1] + 14), pk, (pk[0] + 9, pk[1] + 14)], fill=(150, 150, 190))
    return im.resize((400, 240), Image.NEAREST)


backdrop_off = []
for th in range(4):
    backdrop_off.append(len(blob) // 2)
    blob.extend(struct.pack('<96000H', *[rgb565(p) for p in backdrop(th).getdata()]))

# ------------------------------------------------------------------ tiles per theme: 16 rock masks then the T ids from 2 up
TILE_NAMES = {2: 'oneway', 3: 'spike', 4: 'door', 5: 'crack', 6: 'anchor', 7: 'lanternL', 8: 'lanternR', 9: 'tablet',
              11: 'deco_a', 12: 'deco_b', 13: 'deco_c', 14: 'deco_d', 15: 'deco_e', 16: 'deco_f'}
tile_off = len(blob) // 2
for th in range(4):
    pal = A.bg_palettes(th)
    ts_ = dict(zip(A.AREA_NAMES, A.area_tiles(th)))
    for m in range(16):
        blob.extend(struct.pack('<256H', *[v if v != KEY else rgb565(pal[0][0]) for v in cv_px(ts_['rock%d' % m], pal[0])]))
    for tid in range(17):
        nm = TILE_NAMES.get(tid)
        if not nm:
            blob.extend(struct.pack('<256H', *([KEY] * 256)))
            continue
        p = pal[2] if nm.startswith('deco') else pal[A.AREA_PAL.get(nm, 0)]
        blob.extend(struct.pack('<256H', *cv_px(ts_[nm], p)))

open(os.path.join(ROOT, 'build', 'assets.bin'), 'wb').write(blob)

# ------------------------------------------------------------------ gen.h
h = ['/* generated by assets/build.py */\n#ifndef GEN_H\n#define GEN_H\n#include <stdint.h>\n']
h.append('#define KEYCOL 0x%04X\n#define NUM_ROOMS %d\n#define NONE 255\n' % (KEY, len(W.ROOMS)))
for k, v in W.T.items():
    h.append('#define T_%s %d\n' % (k.upper(), v))
for k, v in W.ENT.items():
    h.append('#define ENT_%s %d\n' % (k, v))
for k, v in W.FLAGS.items():
    h.append('#define F_%s %d\n' % (k.upper(), v))
h.append('#define NUM_FLAGS %d\n' % len(W.FLAGS))
for i, n in enumerate(W.TEXT_ORDER):
    h.append('#define TXT_%s %d\n' % (n, i))
for i, n in enumerate(M.SONG_ORDER):
    h.append('#define SONG_%s %d\n' % (n, i))
h.append('#define NUM_SONGS %d\n' % len(M.SONG_ORDER))
for i, s in enumerate(sprites):
    h.append('#define S_%s %d\n' % (s[0], i))
h.append('#define TILE_OFF %d\n' % tile_off)
h.append('#define MAX_ENTS 12\n')
h.append('''typedef struct { uint16_t w, h; uint32_t off; } SprDef;
typedef struct { uint8_t type, tx, ty, arg, arg2; } Ent;
typedef struct { const char *name; uint8_t theme, mx, my, exits[4], nent; Ent ent[MAX_ENTS]; uint8_t t[375]; } RoomDef;
typedef struct { const uint8_t *lead, *bass; uint8_t tick, duty, drums; } SongDef;
extern const SprDef spr_defs[];
extern const uint32_t backdrop_off[4];
extern const RoomDef rooms[NUM_ROOMS];
extern const char *const text_pages[];
extern const uint8_t text_first[], text_count[];
extern const uint8_t font5x7[64][8];
extern const SongDef songs[];
#endif
''')
open(os.path.join(ROOT, 'src', 'gen.h'), 'w').write(''.join(h))

# ------------------------------------------------------------------ gen_world.c
c = ['/* generated by assets/build.py */\n#include "gen.h"\n']
c.append('const SprDef spr_defs[] = {\n' + ''.join('{%d,%d,%d},' % s[1:] for s in sprites) + '};\n')
c.append('const uint32_t backdrop_off[4] = {%s};\n' % ','.join(map(str, backdrop_off)))
c.append('const RoomDef rooms[NUM_ROOMS] = {\n')
for r in W.ROOMS:
    assert len(r.ents) <= 12, (r.key, len(r.ents))
    ents = ','.join('{%d,%d,%d,%d,%d}' % e for e in r.ents) or '{0,0,0,0,0}'
    e = W.exits(r)
    c.append('{"%s",%d,%d,%d,{%s},%d,{%s},{%s}},\n' % (r.name, r.theme, r.x, r.y, ','.join(map(str, e)), len(r.ents), ents, ','.join(map(str, W.tile_rows(r)))))
c.append('};\n')


def wrap(pg, width=30, lines=3):
    out, cur = [], ''
    ls = []
    for w_ in pg.split():
        if len(cur) + (1 if cur else 0) + len(w_) <= width:
            cur = (cur + ' ' + w_) if cur else w_
        else:
            ls.append(cur); cur = w_
    if cur:
        ls.append(cur)
    for i in range(0, len(ls), lines):
        out.append('\\n'.join(ls[i:i + lines]))
    return out


pages, first, count = [], [], []
for n in W.TEXT_ORDER:
    first.append(len(pages))
    k = 0
    for p in W.TEXTS[n]:
        for line in wrap(p):
            for ch in line.replace('\\n', ''):
                assert ch in A.GLYPHS, (n, ch)
            pages.append(line); k += 1
    count.append(k)
c.append('const char *const text_pages[] = {\n' + ''.join('"%s",\n' % p for p in pages) + '};\n')
c.append('const uint8_t text_first[] = {%s};\nconst uint8_t text_count[] = {%s};\n' % (','.join(map(str, first)), ','.join(map(str, count))))
c.append('const uint8_t font5x7[64][8] = {\n')
for i in range(32, 96):
    rows = A.GLYPHS.get(chr(i), A.GLYPHS[' '])
    vals = [sum(1 << (4 - x) for x, ch in enumerate(r) if ch == '#') for r in rows] + [0]
    c.append('{%s},' % ','.join(map(str, vals)))
c.append('};\n')
for i, n in enumerate(M.SONG_ORDER):
    s = M.SONGS[n]
    c.append('static const uint8_t s%d_l[] = {%s,255,0};\n' % (i, ','.join(str(v) for p in s['lead'] for v in p)))
    c.append('static const uint8_t s%d_b[] = {%s,255,0};\n' % (i, ','.join(str(v) for p in s['bass'] for v in p)))
c.append('const SongDef songs[] = {' + ''.join('{s%d_l,s%d_b,%d,%d,%d},' % (i, i, M.SONGS[n]['tick'], M.SONGS[n]['duty'], M.SONGS[n]['drums']) for i, n in enumerate(M.SONG_ORDER)) + '};\n')
open(os.path.join(ROOT, 'src', 'gen_world.c'), 'w').write(''.join(c))
print('rooms %d, sprites %d, blob %.1f MB, pages %d, flags %d' % (len(W.ROOMS), len(sprites), len(blob) / 1e6, len(pages), len(W.FLAGS)))
