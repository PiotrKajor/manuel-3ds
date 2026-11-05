#!/usr/bin/env python3
"""Builds build/assets.bin, src/gen.h and src/gen_world.c."""
import hashlib, os, struct, sys, pickle
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import lz4.block
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import art as A
import world as W
import music as M
import bake as B

ROOT = os.path.join(os.path.dirname(__file__), '..')
BUILD = os.path.join(ROOT, 'build')
os.makedirs(BUILD, exist_ok=True)
FONT_R = '/usr/share/fonts/google-noto/NotoSerif-Regular.ttf'
FONT_B = '/usr/share/fonts/google-noto/NotoSerif-Bold.ttf'

blob = bytearray()
sprites = []


def align():
    while len(blob) % 2:
        blob.append(0)


def add_sprite(name, im, ax=None, ay=None):
    """Stores colours and alpha cropped to the visible part. The anchor defaults to bottom centre."""
    im = im.convert('RGBA')
    ax = im.width // 2 if ax is None else ax
    ay = im.height if ay is None else ay
    box = im.getbbox() or (0, 0, 1, 1)
    c = np.array(im.crop(box))
    h, w, _ = c.shape
    rgb = B.to565(c[:, :, :3].astype(float))
    alpha = c[:, :, 3].astype('uint8')
    align()
    off = len(blob) // 2
    blob.extend(rgb.tobytes())
    aoff = len(blob)
    blob.extend(alpha.tobytes())
    sprites.append((name, w, h, box[0] - ax, box[1] - ay, off, aoff))


for nm, im in A.player_frames().items():
    add_sprite('M_' + nm, im, 64, 92)
for ei, fn in enumerate(A.ENEMY_ART):
    for f in range(4):
        add_sprite('EN%d_%d' % (ei, f), fn(f / 4))
for ni, fn in enumerate(A.NPC_ART):
    for f in range(2):
        add_sprite('NPC%d_%d' % (ni, f), fn(f / 2 + .25))
for b, fn in enumerate(A.BOSS_ART):
    for f in range(6):
        add_sprite('BOSS%d_%d' % (b, f), fn(f).resize((96, 96), Image.LANCZOS))
for nm, im in (('IT_RUSH', A.item_rush()), ('IT_HOOK', A.item_hook()), ('IT_CLEAVE', A.item_cleave()), ('IT_CLOAK', A.item_cloak()),
               ('IT_SHARD0', A.item_shard(0)), ('IT_SHARD1', A.item_shard(1)), ('IT_WHET', A.item_whet()), ('BELL0', A.item_bell(0)), ('BELL1', A.item_bell(1)),
               ('SBELL_OFF', A.small_bell(0)), ('SBELL_ON', A.small_bell(1)), ('HEART_FULL', A.heart(1)), ('HEART_EMPTY', A.heart(0)),
               ('DROP0', A.proj_drop(0)), ('DROP1', A.proj_drop(1)), ('WAVE0', A.proj_wave(0)), ('WAVE1', A.proj_wave(1)), ('ORB0', A.proj_orb(0)), ('ORB1', A.proj_orb(1)),
               ('SPARK0', A.spark(0)), ('SPARK1', A.spark(1)), ('SPARK2', A.spark(2)), ('MOTE0', A.mote(0)), ('MOTE1', A.mote(1)),
               ('LINK', A.hook_link()), ('RING0', A.anchor_ring(0)), ('RING1', A.anchor_ring(1)), ('UPMARK', A.up_mark())):
    add_sprite(nm, im)


# dynamic tiles: doors and cracked floors, one per theme
def dyn_tile(theme, crack):
    th = B.THEME[theme]
    p = A.Pen(16, 16)
    if crack:
        p.flat([(0, 0), (16, 0), (16, 16), (0, 16)], A.C(*th['dark']))
        p.flat([(0, 0), (16, 0), (16, 4), (0, 4)], A.C(*th['rim2']))
        for pts in ([(1, 2), (6, 8), (3, 15)], [(9, 0), (7, 7), (13, 12), (11, 16)], [(15, 4), (12, 7)]):
            p.line(pts, A.INK, 1.1)
    else:
        p.flat([(0, 0), (16, 0), (16, 16), (0, 16)], A.C(*th['plank_d']))
        p.flat([(2, 0), (14, 0), (14, 16), (2, 16)], A.C(*th['plank']))
        p.line([(0, 0), (0, 16)], A.INK, 1.2); p.line([(15.6, 0), (15.6, 16)], A.INK, 1.2)
        p.line([(0, 7.5), (16, 7.5)], A.INK, 1)
    return p.done()


for th in range(4):
    add_sprite('DOOR%d' % th, dyn_tile(th, 0), 0, 0)
    add_sprite('CRACK%d' % th, dyn_tile(th, 1), 0, 0)


# ------------------------------------------------------------------ the user's drawing, cleaned
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
    d = ImageDraw.Draw(mask)
    d.rectangle((0, 170, 24, h), fill=0)
    d.rectangle((340, 280, w, h), fill=0)
    # keep only the largest connected shape: Menuel with the axe, not bits of neighbouring figures
    from scipy import ndimage as nd
    arr = np.array(mask) > 0
    lab, n = nd.label(arr)
    sizes = nd.sum(arr, lab, range(1, n + 1))
    keep = lab == (int(np.argmax(sizes)) + 1)
    mask = Image.fromarray((keep * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(.5))
    out = im.convert('RGBA')
    out.putalpha(mask)
    return out.crop(mask.point(lambda v: 255 if v > 8 else 0).getbbox())


ref = clean_reference()
scale = 196 / ref.height
add_sprite('TITLE', ref.resize((int(ref.width * scale), 196), Image.LANCZOS), 0, 0)
icon = Image.new('RGBA', (48, 48), (28, 22, 48, 255))
small = ref.resize((int(ref.width * 46 / ref.height), 46), Image.LANCZOS)
small = small.crop((0, 0, 48, 46)) if small.width > 48 else small
icon.alpha_composite(small, ((48 - small.width) // 2, 1))
icon.save(os.path.join(BUILD, 'icon.png'))
banner = Image.new('RGBA', (256, 128), (28, 22, 48, 255))
bs = ref.resize((int(ref.width * 120 / ref.height), 120), Image.LANCZOS)
banner.alpha_composite(bs, ((256 - bs.width) // 2, 4))
banner.save(os.path.join(BUILD, 'banner.png'))


# ------------------------------------------------------------------ fonts: alpha glyphs, variable width
def make_font(path, size):
    f = ImageFont.truetype(path, size)
    asc, desc = f.getmetrics()
    h = asc + desc
    glyphs = []
    for i in range(32, 127):
        adv = int(round(f.getlength(chr(i))))
        adv = max(adv, 1)
        im = Image.new('L', (adv + 2, h), 0)
        ImageDraw.Draw(im).text((1, 0), chr(i), font=f, fill=255)
        off = len(blob)
        blob.extend(np.array(im).astype('uint8').tobytes())
        glyphs.append((adv + 2, adv, off))
    return f, h, glyphs


small_font, small_h, small_g = make_font(FONT_R, 12)
big_font, big_h, big_g = make_font(FONT_B, 34)
mid_font, mid_h, mid_g = make_font(FONT_B, 16)
align()


# ------------------------------------------------------------------ painted rooms, cached by content
CACHE = os.path.join(BUILD, 'room_cache')
os.makedirs(CACHE, exist_ok=True)
bake_src = open(os.path.join(os.path.dirname(__file__), 'bake.py'), 'rb').read()
room_blobs = []
for i, r in enumerate(W.ROOMS):
    key = hashlib.sha1(bake_src + pickle.dumps((i, r.theme, r.g, r.ents, r.props))).hexdigest()
    path = os.path.join(CACHE, key)
    if os.path.exists(path):
        data = open(path, 'rb').read()
    else:
        data = lz4.block.compress(B.to565(B.paint_room(r, i)).tobytes(), store_size=False, mode='high_compression', compression=9)
        open(path, 'wb').write(data)
    align()
    while len(blob) % 4:
        blob.append(0)
    room_blobs.append((len(blob), len(data)))
    blob.extend(data)

open(os.path.join(BUILD, 'assets.bin'), 'wb').write(blob)


# ------------------------------------------------------------------ text: pixel-accurate wrapping to the 288 px box
def wrap(pg, width=288, lines=3):
    out, ls, cur = [], [], ''
    for w_ in pg.split():
        t = (cur + ' ' + w_) if cur else w_
        if small_font.getlength(t) <= width:
            cur = t
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
            pages.append(line.replace('"', '\\"')); k += 1
    count.append(k)

# ------------------------------------------------------------------ gen.h
h = ['/* generated by assets/build.py */\n#ifndef GEN_H\n#define GEN_H\n#include <stdint.h>\n']
h.append('#define NUM_ROOMS %d\n#define NONE 255\n#define RW %d\n#define RH %d\n' % (len(W.ROOMS), W.W, W.H))
for k, v in W.T.items():
    h.append('#define T_%s %d\n' % (k.upper(), v))
for k, v in W.ENT.items():
    h.append('#define ENT_%s %d\n' % (k, v))
for k, v in W.FLAGS.items():
    h.append('#define F_%s %d\n' % (k.upper(), v))
for i, n in enumerate(W.TEXT_ORDER):
    h.append('#define TXT_%s %d\n' % (n, i))
for i, n in enumerate(M.SONG_ORDER):
    h.append('#define SONG_%s %d\n' % (n, i))
for i, s in enumerate(sprites):
    h.append('#define S_%s %d\n' % (s[0], i))
h.append('#define MAX_ENTS 14\n')
h.append('''typedef struct { uint16_t w, h; int16_t ox, oy; uint32_t off, aoff; } SprDef;
typedef struct { uint8_t type, tx, ty, arg, arg2; } Ent;
typedef struct { const char *name; uint8_t theme, mx, my, exits[4], nent; Ent ent[MAX_ENTS]; uint8_t t[750]; uint32_t bg_off, bg_len; } RoomDef;
typedef struct { const uint8_t *lead, *bass; uint8_t tick, duty, drums; } SongDef;
typedef struct { uint8_t w, adv; uint32_t off; } Glyph;
typedef struct { uint8_t h; const Glyph *g; } Font;
extern const SprDef spr_defs[];
extern const RoomDef rooms[NUM_ROOMS];
extern const char *const text_pages[];
extern const uint8_t text_first[], text_count[];
extern const Font font_small, font_mid, font_big;
extern const SongDef songs[];
#endif
''')
open(os.path.join(ROOT, 'src', 'gen.h'), 'w').write(''.join(h))

# ------------------------------------------------------------------ gen_world.c
c = ['/* generated by assets/build.py */\n#include "gen.h"\n']
c.append('const SprDef spr_defs[] = {\n' + ''.join('{%d,%d,%d,%d,%d,%d},\n' % s[1:] for s in sprites) + '};\n')
c.append('const RoomDef rooms[NUM_ROOMS] = {\n')
for i, r in enumerate(W.ROOMS):
    assert len(r.ents) <= 14, (r.key, len(r.ents))
    ents = ','.join('{%d,%d,%d,%d,%d}' % e for e in r.ents) or '{0,0,0,0,0}'
    e = W.exits(r)
    c.append('{"%s",%d,%d,%d,{%s},%d,{%s},{%s},%d,%d},\n' % (r.name, r.theme, r.x, r.y, ','.join(map(str, e)), len(r.ents), ents,
                                                             ','.join(map(str, W.tile_rows(r))), room_blobs[i][0], room_blobs[i][1]))
c.append('};\n')
c.append('const char *const text_pages[] = {\n' + ''.join('"%s",\n' % p for p in pages) + '};\n')
c.append('const uint8_t text_first[] = {%s};\nconst uint8_t text_count[] = {%s};\n' % (','.join(map(str, first)), ','.join(map(str, count))))
for nm, hh, gl in (('small', small_h, small_g), ('mid', mid_h, mid_g), ('big', big_h, big_g)):
    c.append('static const Glyph g_%s[] = {%s};\nconst Font font_%s = {%d, g_%s};\n' % (nm, ','.join('{%d,%d,%d}' % g for g in gl), nm, hh, nm))
for i, n in enumerate(M.SONG_ORDER):
    s = M.SONGS[n]
    c.append('static const uint8_t s%d_l[] = {%s,255,0};\n' % (i, ','.join(str(v) for p in s['lead'] for v in p)))
    c.append('static const uint8_t s%d_b[] = {%s,255,0};\n' % (i, ','.join(str(v) for p in s['bass'] for v in p)))
c.append('const SongDef songs[] = {' + ''.join('{s%d_l,s%d_b,%d,%d,%d},' % (i, i, M.SONGS[n]['tick'], M.SONGS[n]['duty'], M.SONGS[n]['drums']) for i, n in enumerate(M.SONG_ORDER)) + '};\n')
open(os.path.join(ROOT, 'src', 'gen_world.c'), 'w').write(''.join(c))
print('rooms %d, sprites %d, blob %.1f MB, pages %d, flags %d' % (len(W.ROOMS), len(sprites), len(blob) / 1e6, len(pages), len(W.FLAGS)))
