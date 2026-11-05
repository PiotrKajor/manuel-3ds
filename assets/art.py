"""Menuel - procedural art. Pixel values are indices 0..3, assets/build.py applies the palettes and scales by two."""
from PIL import Image, ImageDraw


def c555(rgb):
    r, g, b = rgb
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)


class Cv:
    def __init__(self, w, h, fill=0):
        self.w, self.h = w, h
        self.im = Image.new('P', (w, h), fill)
        self.d = ImageDraw.Draw(self.im)

    def get(self, x, y):
        return self.im.getpixel((x, y)) if 0 <= x < self.w and 0 <= y < self.h else 0

    def set(self, x, y, v):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.im.putpixel((x, y), v)

    def rect(self, x0, y0, x1, y1, v):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, v)

    def line(self, *pts, v=1):
        self.d.line(pts, fill=v)

    def poly(self, pts, fill, outline=None):
        self.d.polygon(pts, fill=fill, outline=outline)

    def blit(self, src, x, y, key=True):
        for yy in range(src.h):
            for xx in range(src.w):
                v = src.get(xx, yy)
                if v or not key:
                    self.set(x + xx, y + yy, v)

    def flipx(self):
        c = Cv(self.w, self.h)
        c.im = self.im.transpose(Image.FLIP_LEFT_RIGHT)
        c.d = ImageDraw.Draw(c.im)
        return c

    def flipy(self):
        c = Cv(self.w, self.h)
        c.im = self.im.transpose(Image.FLIP_TOP_BOTTOM)
        c.d = ImageDraw.Draw(c.im)
        return c


def art(*lines):
    c = Cv(max(len(l) for l in lines), len(lines))
    for y, l in enumerate(lines):
        for x, ch in enumerate(l):
            if ch not in '. ':
                c.set(x, y, int(ch))
    return c


def tile_bytes(c, x0=0, y0=0):
    out = []
    for y in range(8):
        lo = hi = 0
        for x in range(8):
            v = c.get(x0 + x, y0 + y)
            lo |= (v & 1) << (7 - x)
            hi |= ((v >> 1) & 1) << (7 - x)
        out += [lo, hi]
    return out


def spr_bytes(c):
    """8x16 sprite order: column major, top tile then bottom tile."""
    out = []
    for cx in range(c.w // 8):
        for cy in range(c.h // 16):
            out += tile_bytes(c, cx * 8, cy * 16)
            out += tile_bytes(c, cx * 8, cy * 16 + 8)
    return out


# ------------------------------------------------------------------ font (5x7)
GLYPHS = {}


def _g(ch, *rows):
    GLYPHS[ch] = rows


_g('A', ".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
_g('B', "####.", "#...#", "#...#", "####.", "#...#", "#...#", "####.")
_g('C', ".###.", "#...#", "#....", "#....", "#....", "#...#", ".###.")
_g('D', "####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####.")
_g('E', "#####", "#....", "#....", "####.", "#....", "#....", "#####")
_g('F', "#####", "#....", "#....", "####.", "#....", "#....", "#....")
_g('G', ".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###.")
_g('H', "#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
_g('I', ".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###.")
_g('J', "..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##..")
_g('K', "#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#")
_g('L', "#....", "#....", "#....", "#....", "#....", "#....", "#####")
_g('M', "#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#")
_g('N', "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#")
_g('O', ".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.")
_g('P', "####.", "#...#", "#...#", "####.", "#....", "#....", "#....")
_g('Q', ".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#")
_g('R', "####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#")
_g('S', ".####", "#....", "#....", ".###.", "....#", "....#", "####.")
_g('T', "#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..")
_g('U', "#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.")
_g('V', "#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#..")
_g('W', "#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#")
_g('X', "#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#")
_g('Y', "#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..")
_g('Z', "#####", "....#", "...#.", "..#..", ".#...", "#....", "#####")
_g('0', ".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###.")
_g('1', "..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###.")
_g('2', ".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####")
_g('3', "####.", "....#", "....#", ".###.", "....#", "....#", "####.")
_g('4', "...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#.")
_g('5', "#####", "#....", "####.", "....#", "....#", "#...#", ".###.")
_g('6', ".###.", "#....", "#....", "####.", "#...#", "#...#", ".###.")
_g('7', "#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#...")
_g('8', ".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###.")
_g('9', ".###.", "#...#", "#...#", ".####", "....#", "....#", ".###.")
_g(' ', *["....."] * 7)
_g('.', ".....", ".....", ".....", ".....", ".....", ".....", "..#..")
_g(',', ".....", ".....", ".....", ".....", "..#..", "..#..", ".#...")
_g('!', "..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#..")
_g('?', ".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#..")
_g('-', ".....", ".....", ".....", ".###.", ".....", ".....", ".....")
_g(':', ".....", "..#..", ".....", ".....", ".....", "..#..", ".....")
_g("'", "..#..", "..#..", ".#...", ".....", ".....", ".....", ".....")
_g('>', "#....", "##...", "###..", "####.", "###..", "##...", "#....")
_g('/', "....#", "....#", "...#.", "..#..", ".#...", "#....", "#....")
_g('+', ".....", "..#..", "..#..", "#####", "..#..", "..#..", ".....")


def glyph(ch, color=3):
    c = Cv(8, 8)
    for y, row in enumerate(GLYPHS.get(ch, GLYPHS[' '])):
        for x, p in enumerate(row):
            if p == '#':
                c.set(x + 1, y, color)
    return c


# ------------------------------------------------------------------ Menuel
def menuel(leg=0, bob=0, tip=0, lean=0, squash=0):
    """16x16, facing right. 1 black, 2 purple, 3 pale lilac."""
    c = Cv(16, 16)
    cx = 7 + lean
    top = bob
    # legs: two thin black spikes, as in the drawing
    fy = 15
    lx, rx = 6 + leg, 9 - leg
    c.line(lx, 12 + bob, lx, fy, v=1)
    c.line(rx, 12 + bob, rx, fy, v=1)
    c.set(lx + 1, 12 + bob, 1)
    c.set(rx - 1, 12 + bob, 1)
    # jagged cloak
    cy = 8 + bob + squash
    pts = [(cx - 3, cy), (cx - 6, cy + 1 - tip), (cx - 4, cy + 2), (cx - 7, cy + 4 - tip), (cx - 3, cy + 4),
           (cx - 2, cy + 6), (cx, cy + 4), (cx + 2, cy + 6), (cx + 3, cy + 4), (cx + 6, cy + 4 + tip),
           (cx + 4, cy + 2), (cx + 6, cy + 1 + tip), (cx + 3, cy)]
    c.poly(pts, 2, 1)
    # darker fold across the chest
    c.line(cx - 3, cy + 3, cx + 1, cy + 1, v=1)
    # kite shaped mask, widest below the middle, sharp at both ends
    head = [(cx, top), (cx + 4, top + 5 + squash), (cx + 1, top + 9), (cx, top + 9), (cx - 4, top + 5 + squash)]
    c.poly(head, 3, 1)
    # slit eyes
    ey = top + 5 + squash
    c.set(cx - 2, ey, 1); c.set(cx - 1, ey + 1, 1); c.set(cx - 2, ey + 1, 1)
    c.set(cx + 2, ey, 1); c.set(cx + 1, ey + 1, 1); c.set(cx + 2, ey + 1, 1)
    # small mark on the forehead
    c.set(cx + 1, top + 3, 2)
    return c


def player_frames():
    return [
        menuel(0, 0, 0),            # 0 idle
        menuel(0, 1, 1),            # 1 idle
        menuel(1, 0, 1),            # 2 run
        menuel(0, 1, 0),            # 3 run
        menuel(-1, 0, 1),           # 4 run
        menuel(0, 1, 0),            # 5 run
        menuel(1, 0, -1),           # 6 rise
        menuel(-1, 0, 2),           # 7 fall
        menuel(1, 0, 0, 1),         # 8 strike
        menuel(1, 1, 2, 2),         # 9 rush
        menuel(-1, 0, 2, -1),       # 10 hurt
        menuel(0, 2, 2, 0, 1),      # 11 heal
    ]


def axe_idle():
    """8x16: the axe held out beside Menuel."""
    return art(
        "........",
        "..1111..",
        ".122221.",
        "12222221",
        "12222221",
        "12222221",
        "12222221",
        ".122221.",
        "..1221..",
        "...11...",
        "...11...",
        "...11...",
        "...11...",
        "...11...",
        "........",
        "........")


def axe_swing(kind):
    """16x16 swing frames. 0 raised, 1 forward, 2 low, 3 straight down (Cleave)."""
    c = Cv(16, 16)
    if kind == 0:
        c.line(1, 14, 8, 6, v=1)
        c.poly([(5, 1), (13, 1), (15, 6), (9, 9)], 2, 1)
    elif kind == 1:
        c.line(0, 10, 7, 9, v=1)
        c.line(0, 11, 7, 10, v=1)
        c.poly([(7, 3), (15, 2), (15, 14), (7, 12)], 2, 1)
        c.line(14, 4, 14, 12, v=3)
    elif kind == 2:
        c.line(0, 4, 7, 10, v=1)
        c.poly([(6, 8), (14, 7), (13, 15), (4, 14)], 2, 1)
    else:
        c.line(7, 0, 7, 7, v=1)
        c.line(8, 0, 8, 7, v=1)
        c.poly([(2, 7), (13, 7), (11, 15), (4, 15)], 2, 1)
        c.line(5, 14, 10, 14, v=3)
    return c


# ------------------------------------------------------------------ enemies (16x16, two frames each)
def e_mite(f):
    c = Cv(16, 16)
    c.poly([(2, 15), (3, 9), (7, 5), (12, 6), (14, 11), (14, 15)], 2, 1)
    c.poly([(5, 9), (7, 6), (9, 9)], 3, 1)
    c.poly([(10, 10), (12, 7), (13, 11)], 3, 1)
    c.set(4, 12, 1); c.set(6, 12, 1)
    for x in (3, 7, 11):
        c.set(x + f, 15, 1)
    return c


def e_moth(f):
    c = Cv(16, 16)
    a = -2 if f else 2
    c.poly([(7, 8), (1, 4 + a), (2, 11 + a), (6, 11)], 2, 1)
    c.poly([(8, 8), (14, 4 + a), (13, 11 + a), (9, 11)], 2, 1)
    c.poly([(6, 6), (9, 6), (9, 13), (7, 15), (6, 13)], 3, 1)
    c.set(6, 8, 1); c.set(9, 8, 1)
    return c


def e_frog(f):
    c = Cv(16, 16)
    if f:
        c.poly([(1, 13), (6, 3), (12, 3), (15, 9), (9, 11)], 2, 1)
        c.line(2, 15, 5, 11, v=1)
        c.line(13, 10, 15, 14, v=1)
        c.rect(9, 5, 10, 6, 3)
    else:
        c.poly([(1, 15), (2, 8), (6, 5), (11, 5), (14, 9), (15, 15)], 2, 1)
        c.line(3, 11, 12, 13, v=1)
        c.rect(9, 7, 10, 8, 3)
        c.rect(4, 7, 5, 8, 3)
    return c


def e_bell(f):
    """A small bell that spits drops from its mouth."""
    c = Cv(16, 16)
    c.poly([(7, 2), (9, 2), (12, 7), (13, 12), (3, 12), (4, 7)], 2, 1)
    c.line(2, 13, 14, 13, v=1)
    c.rect(6, 5, 7, 8, 3)
    c.rect(7 + (1 if f else -1), 14, 8 + (1 if f else -1), 15, 3)
    return c


def e_beetle(f):
    c = Cv(16, 16)
    c.poly([(1, 13), (3, 7), (8, 4), (13, 7), (15, 13)], 2, 1)
    c.line(8, 4, 8, 13, v=1)
    c.rect(11, 8, 12, 9, 3)
    c.rect(3, 10, 5, 11, 3)
    for x in (3, 8, 12):
        c.line(x, 14, x + (1 if f else -1), 15, v=1)
    return c


def e_furnace(f):
    c = Cv(16, 16)
    c.rect(2, 3, 13, 15, 2)
    c.d.rectangle((2, 3, 13, 15), outline=1)
    c.rect(4, 1, 11, 3, 1)
    c.rect(4, 7 + f, 11, 12, 3)
    c.rect(4, 7 + f, 11, 7 + f, 1)
    c.set(5, 12, 1); c.set(8, 12, 1); c.set(10, 12, 1)
    return c


def e_wraith(f):
    c = Cv(16, 16)
    w = 1 if f else 0
    c.poly([(8, 1), (13, 6), (13, 12), (11 + w, 15), (9, 12), (7 - w, 15), (5, 12), (3 + w, 15), (3, 6)], 2, 1)
    c.poly([(8, 3), (11, 7), (8, 10), (5, 7)], 3, 1)
    c.set(7, 7, 1); c.set(9, 7, 1)
    return c


def e_hare(f):
    c = Cv(16, 16)
    if f:
        c.poly([(2, 12), (6, 7), (12, 6), (15, 9), (9, 12)], 3, 1)
        c.poly([(9, 7), (5, 2), (8, 2), (11, 6)], 2, 1)
        c.line(3, 13, 1, 15, v=1)
        c.line(11, 12, 14, 15, v=1)
    else:
        c.poly([(2, 15), (3, 9), (8, 7), (13, 9), (14, 15)], 3, 1)
        c.poly([(8, 8), (6, 1), (9, 1), (11, 8)], 2, 1)
    c.rect(11, 10 if not f else 8, 11, 10 if not f else 8, 1)
    return c


ENEMY_ART = [e_mite, e_moth, e_frog, e_bell, e_beetle, e_furnace, e_wraith, e_hare]


# ------------------------------------------------------------------ NPCs (16x16, two frames)
def npc_ringer(f):
    c = Cv(16, 16)
    c.poly([(4, 15), (5, 7), (11, 7), (12, 15)], 2, 1)
    c.poly([(5, 8), (8, 1 + f), (11, 8)], 3, 1)
    c.set(7, 6, 1); c.set(9, 6, 1)
    c.line(12, 3, 12, 15, v=1)
    c.rect(11, 2, 13, 4, 3)
    return c


def npc_miner(f):
    c = Cv(16, 16)
    c.poly([(3, 15), (4, 8), (12, 8), (13, 15)], 2, 1)
    c.rect(5, 3 + f, 11, 8, 3)
    c.d.rectangle((5, 3 + f, 11, 8), outline=1)
    c.rect(4, 1 + f, 12, 3 + f, 2)
    c.d.rectangle((4, 1 + f, 12, 3 + f), outline=1)
    c.set(7, 6, 1); c.set(9, 6, 1)
    c.set(8, 2 + f, 3)
    return c


def npc_clerk(f):
    c = Cv(16, 16)
    c.d.ellipse((3, 2 + f, 12, 11 + f), fill=3, outline=1)
    c.poly([(4, 10), (12, 10), (14, 15), (2, 15)], 2, 1)
    c.rect(5, 5 + f, 6, 7 + f, 1)
    c.rect(9, 5 + f, 10, 7 + f, 1)
    return c


NPC_ART = [npc_ringer, npc_miner, npc_clerk]


# ------------------------------------------------------------------ pickups, particles
def item_rush():
    return art("................", "................", ".....111........", "....12221.......", "...1222211...1..", "..122222211.11..", "..1222222211....", ".1222222222111..", ".12222222222211.", ".1222222222111..", "..1222222211....", "..122222211.11..", "...1222211...1..", "....12221.......", ".....111........", "................")


def item_hook():
    c = Cv(16, 16)
    c.d.arc((2, 2, 14, 14), 180, 60, fill=3)
    c.d.arc((3, 3, 13, 13), 180, 60, fill=2)
    c.line(2, 8, 2, 15, v=1)
    c.line(3, 8, 3, 15, v=1)
    return c


def item_cleave():
    return axe_swing(3)


def item_cloak():
    c = Cv(16, 16)
    c.poly([(5, 2), (10, 2), (14, 9), (12, 13), (10, 11), (8, 14), (6, 11), (4, 13), (2, 9)], 2, 1)
    c.line(5, 5, 10, 5, v=3)
    return c


def item_shard(f):
    c = Cv(16, 16)
    c.poly([(8, 2), (12, 7), (9, 13), (6, 13), (4, 7)], 3, 1)
    c.line(8, 4, 8, 10, v=2)
    if f:
        c.set(13, 3, 3); c.set(2, 11, 3)
    return c


def item_whet():
    c = Cv(16, 16)
    c.poly([(2, 10), (10, 4), (14, 7), (6, 13)], 2, 1)
    c.line(4, 10, 10, 6, v=3)
    return c


def item_bell(f):
    c = Cv(16, 16)
    c.poly([(7, 1), (9, 1), (12, 6), (14, 12), (2, 12), (4, 6)], 3, 1)
    c.line(1, 13, 15, 13, v=1)
    c.rect(7 + f, 14, 8 + f, 15, 2)
    c.rect(6, 4, 6, 8, 2)
    return c


def fx16(rows):
    return art(*rows)


def spark(n):
    c = Cv(8, 16)
    r = [1, 3, 4][n]
    for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
        c.line(4, 8, 4 + dx, 8 + dy, v=3 if n < 2 else 2)
    return c


def mote(n):
    c = Cv(8, 16)
    c.rect(3, 7, 3 + n, 7 + n, 3)
    return c


def proj_drop(n):
    c = Cv(8, 16)
    c.poly([(4, 3), (6, 7), (5, 9), (3, 9), (2, 7)], 3, 1)
    c.set(4 + n, 12, 2)
    return c


def proj_wave(n):
    c = Cv(8, 16)
    c.poly([(1, 15), (2 + n, 5 + n), (4, 2 + n), (6 - n, 6 + n), (7, 15)], 3, 2)
    c.line(3, 15, 4, 8, v=1)
    return c


def proj_orb(n):
    c = Cv(8, 16)
    c.d.ellipse((1, 4, 6, 9 + n), fill=2, outline=1)
    c.rect(3, 5, 4, 6, 3)
    return c


def hook_link():
    c = Cv(8, 16)
    c.rect(3, 6, 4, 9, 3)
    c.d.rectangle((2, 5, 5, 10), outline=1)
    return c


def up_mark():
    c = Cv(8, 16)
    c.poly([(4, 2), (7, 6), (5, 6), (5, 10), (3, 10), (3, 6), (1, 6)], 3, 1)
    return c


# ------------------------------------------------------------------ bosses (32x32, five frames)
def _legs(c, x0, x1, y0, f):
    c.rect(x0, y0, x0 + 3, 31 - (2 if f == 2 else 0), 1)
    c.rect(x1, y0, x1 + 3, 31 - (2 if f == 3 else 0), 1)


def boss_foreman(f):
    """Salt Foreman: a squat miner in a crystal crust, swinging a pick."""
    c = Cv(32, 32)
    dy = {0: 0, 1: 1, 2: 3, 3: -1, 4: -2}[f]
    _legs(c, 9, 19, 24, 0 if f < 2 else f)
    c.poly([(4, 26), (3, 12 + dy), (9, 5 + dy), (22, 5 + dy), (28, 12 + dy), (27, 26)], 2, 1)
    c.poly([(9, 7 + dy), (12, 0 + dy), (15, 7 + dy)], 3, 1)
    c.poly([(16, 7 + dy), (20, 1 + dy), (23, 8 + dy)], 3, 1)
    c.rect(11, 13 + dy, 21, 19 + dy, 3)
    c.d.rectangle((11, 13 + dy, 21, 19 + dy), outline=1)
    c.rect(13, 15 + dy, 14, 17 + dy, 1)
    c.rect(18, 15 + dy, 19, 17 + dy, 1)
    if f in (2, 4):
        c.line(26, 15 + dy, 30, 1, v=1)
        c.line(25, 3, 31, 1, v=3)
    elif f == 3:
        c.line(26, 18, 31, 18, v=1)
        c.line(31, 12, 31, 24, v=3)
    else:
        c.line(27, 20, 31, 28, v=1)
    return c


def boss_rope(f):
    """Rope Drowned: a bloated figure wound in old bell rope."""
    c = Cv(32, 32)
    dy = {0: 0, 1: 2, 2: 4, 3: 0, 4: -2}[f]
    c.d.ellipse((5, 4 + dy, 26, 26 + dy), fill=2, outline=1)
    for k in range(3):
        c.line(6, 10 + k * 5 + dy, 25, 13 + k * 5 + dy, v=1)
        c.line(6, 11 + k * 5 + dy, 25, 14 + k * 5 + dy, v=3)
    c.d.ellipse((10, 6 + dy, 21, 15 + dy), fill=3, outline=1)
    c.rect(12, 9 + dy, 14, 11 + dy, 1)
    c.rect(17, 9 + dy, 19, 11 + dy, 1)
    c.line(15, 0, 15, 5 + dy, v=3)
    c.line(16, 0, 16, 5 + dy, v=1)
    if f == 3:
        c.line(6, 22, 0, 31, v=3)
        c.line(25, 22, 31, 31, v=3)
    else:
        for x in (8, 15, 22):
            c.line(x, 26 + dy, x + (f % 2) * 2 - 1, 31, v=3)
    return c


def boss_founder(f):
    """Two-Headed Founder: two heads on one apron, ladle in hand."""
    c = Cv(32, 32)
    dy = {0: 0, 1: 1, 2: 2, 3: -1, 4: -2}[f]
    _legs(c, 8, 20, 25, 0 if f < 2 else f)
    c.poly([(5, 26), (6, 13 + dy), (26, 13 + dy), (27, 26)], 2, 1)
    c.rect(11, 16 + dy, 21, 26, 3)
    c.d.rectangle((11, 16 + dy, 21, 26), outline=1)
    for hx in (9, 22):
        tilt = (f % 2) if hx == 9 else -(f % 2)
        c.d.ellipse((hx - 5, 3 + dy + tilt, hx + 4, 13 + dy + tilt), fill=3, outline=1)
        c.rect(hx - 3, 7 + dy + tilt, hx - 2, 9 + dy + tilt, 1)
        c.rect(hx + 1, 7 + dy + tilt, hx + 2, 9 + dy + tilt, 1)
    if f == 2:
        c.line(26, 17, 31, 6, v=1)
        c.rect(28, 1, 31, 6, 3)
    else:
        c.line(27, 20, 31, 28, v=1)
        c.rect(28, 27, 31, 30, 3)
    return c


def boss_anvil(f):
    """The Anvil: a walking anvil with a furnace glow in its waist."""
    c = Cv(32, 32)
    dy = {0: 0, 1: 1, 2: 4, 3: 0, 4: -3}[f]
    c.poly([(1, 6 + dy), (24, 6 + dy), (31, 10 + dy), (24, 13 + dy), (22, 19 + dy), (26, 27), (5, 27), (9, 19 + dy), (6, 13 + dy)], 2, 1)
    c.line(3, 7 + dy, 24, 7 + dy, v=3)
    c.rect(11, 15 + dy, 19, 18 + dy, 3)
    c.rect(13, 16 + dy, 14, 17 + dy, 1)
    c.rect(17, 16 + dy, 18, 17 + dy, 1)
    if f != 4:
        c.rect(7, 28, 12, 31, 1)
        c.rect(19, 28, 24, 31, 1)
    return c


def boss_ringer(f):
    """Silent Ringer: a tall hooded figure with a bell for a head and no clapper."""
    c = Cv(32, 32)
    dy = {0: 0, 1: 1, 2: 2, 3: 0, 4: -2}[f]
    c.poly([(7, 31), (9, 14 + dy), (22, 14 + dy), (25, 31), (20, 28), (16, 31), (12, 28)], 2, 1)
    c.poly([(14, 0 + dy), (18, 0 + dy), (23, 8 + dy), (25, 16 + dy), (7, 16 + dy), (9, 8 + dy)], 3, 1)
    c.line(5, 17 + dy, 27, 17 + dy, v=1)
    c.rect(12, 9 + dy, 19, 13 + dy, 1)
    if f == 2:
        c.line(9, 18, 0, 6, v=1)
        c.line(22, 18, 31, 6, v=1)
    elif f == 3:
        c.line(9, 20, 0, 22, v=1)
        c.line(22, 20, 31, 22, v=1)
    else:
        c.line(9, 20, 4, 30, v=1)
        c.line(22, 20, 27, 30, v=1)
    return c


BOSS_ART = [boss_foreman, boss_rope, boss_founder, boss_anvil, boss_ringer]


# ------------------------------------------------------------------ palettes
BLK = (8, 6, 16)
THEMES = {
    0: dict(name='salt', rock=[(14, 18, 34), (46, 58, 88), (96, 118, 150), (206, 228, 240)],
            back=[(14, 18, 34), (20, 26, 46), (28, 36, 60), (44, 54, 82)],
            deco=[(14, 18, 34), (40, 60, 90), (120, 170, 200), (230, 250, 255)],
            hazard=[(14, 18, 34), (70, 80, 110), (170, 190, 210), (250, 255, 255)],
            en1=[(0, 0, 0), BLK, (90, 120, 160), (220, 240, 250)], en2=[(0, 0, 0), BLK, (150, 130, 90), (240, 230, 180)]),
    1: dict(name='belfry', rock=[(6, 22, 28), (20, 54, 58), (44, 104, 96), (140, 200, 150)],
            back=[(6, 22, 28), (8, 32, 40), (12, 44, 54), (20, 64, 72)],
            deco=[(6, 22, 28), (60, 80, 60), (170, 150, 80), (240, 220, 140)],
            hazard=[(6, 22, 28), (20, 80, 110), (60, 150, 190), (190, 240, 250)],
            en1=[(0, 0, 0), BLK, (50, 120, 90), (180, 240, 170)], en2=[(0, 0, 0), BLK, (170, 140, 60), (250, 230, 130)]),
    2: dict(name='foundry', rock=[(26, 12, 10), (66, 32, 22), (122, 62, 34), (214, 134, 70)],
            back=[(26, 12, 10), (36, 18, 14), (50, 26, 18), (72, 38, 24)],
            deco=[(26, 12, 10), (80, 60, 56), (170, 120, 80), (250, 210, 120)],
            hazard=[(26, 12, 10), (150, 40, 10), (240, 120, 20), (255, 230, 120)],
            en1=[(0, 0, 0), BLK, (150, 70, 30), (250, 190, 90)], en2=[(0, 0, 0), BLK, (110, 90, 90), (255, 160, 60)]),
    3: dict(name='summit', rock=[(20, 16, 40), (58, 50, 92), (112, 104, 150), (236, 236, 250)],
            back=[(20, 16, 40), (28, 24, 56), (38, 34, 72), (54, 50, 96)],
            deco=[(20, 16, 40), (80, 70, 130), (170, 150, 210), (250, 240, 255)],
            hazard=[(20, 16, 40), (90, 110, 170), (170, 200, 240), (250, 255, 255)],
            en1=[(0, 0, 0), BLK, (110, 90, 170), (235, 225, 255)], en2=[(0, 0, 0), BLK, (160, 170, 210), (250, 250, 255)]),
}
HUD_PAL = [(10, 8, 20), (70, 50, 100), (168, 120, 200), (244, 236, 250)]
LANTERN_PAL = [(0, 0, 0), (70, 40, 20), (230, 150, 50), (255, 240, 160)]
# OBJ palettes: 0 Menuel, 1 fx, 2 enemy A, 3 enemy B, 4 boss, 5 NPC, 6 items, 7 hit flash
MENUEL_PAL = [(0, 0, 0), BLK, (120, 92, 160), (232, 222, 250)]
FX_PAL = [(0, 0, 0), (60, 50, 90), (190, 170, 230), (255, 255, 255)]
NPC_PAL = [(0, 0, 0), BLK, (110, 104, 120), (225, 215, 195)]
ITEM_PAL = [(0, 0, 0), BLK, (190, 130, 60), (255, 235, 150)]
FLASH_PAL = [(0, 0, 0), (255, 255, 255), (255, 255, 255), (255, 255, 255)]
BOSS_PALS = [
    [(0, 0, 0), BLK, (86, 110, 150), (226, 244, 255)],
    [(0, 0, 0), BLK, (40, 110, 110), (200, 230, 170)],
    [(0, 0, 0), BLK, (150, 60, 30), (250, 200, 110)],
    [(0, 0, 0), BLK, (90, 86, 100), (255, 170, 60)],
    [(0, 0, 0), BLK, (74, 60, 120), (240, 236, 255)],
]
MAP_PALS = [
    [(12, 10, 24), (46, 58, 88), (120, 170, 200), (230, 250, 255)],
    [(12, 10, 24), (20, 54, 58), (70, 170, 140), (190, 250, 200)],
    [(12, 10, 24), (70, 32, 20), (220, 120, 60), (255, 210, 120)],
    [(12, 10, 24), (58, 50, 92), (170, 150, 220), (250, 240, 255)],
]


def bg_palettes(theme):
    t = THEMES[theme]
    bg = t['rock'][0]
    def fix(p):
        return [bg] + p[1:]
    return [t['rock'], t['back'], t['deco'], t['hazard'], fix(LANTERN_PAL), fix(FX_PAL), fix(ITEM_PAL), HUD_PAL]


def obj_palettes(theme):
    t = THEMES[theme]
    return [MENUEL_PAL, FX_PAL, t['en1'], t['en2'], BOSS_PALS[0], NPC_PAL, ITEM_PAL, FLASH_PAL]


# ------------------------------------------------------------------ BG tiles
U, D, L, R = 1, 2, 4, 8
F_SOLID, F_ONEWAY, F_HAZARD = 1, 2, 4


def rock_tile(theme, mask):
    c = Cv(8, 8, 1)
    if theme == 0:      # salt: crossing facets
        c.line(0, 7, 7, 0, v=2)
        c.set(2, 2, 2); c.set(5, 6, 2)
    elif theme == 1:    # wet bricks
        c.line(0, 3, 7, 3, v=2); c.line(0, 7, 7, 7, v=2)
        c.line(3, 0, 3, 3, v=2); c.line(6, 4, 6, 7, v=2)
    elif theme == 2:    # riveted plate
        c.d.rectangle((0, 0, 7, 7), outline=2)
        c.set(2, 2, 3); c.set(5, 5, 3)
    else:               # frozen stone
        c.set(1, 2, 2); c.set(2, 2, 2); c.set(5, 5, 2); c.set(6, 5, 2); c.set(4, 1, 2)
    if mask & L:
        c.line(0, 0, 0, 7, v=2)
    if mask & R:
        c.line(7, 0, 7, 7, v=2)
    if mask & D:
        c.line(0, 7, 7, 7, v=0)
    if mask & U:
        c.line(0, 0, 7, 0, v=3)
        if theme == 0:
            c.set(1, 1, 3); c.set(4, 1, 3); c.set(6, 1, 3)
        elif theme == 1:
            c.line(0, 1, 7, 1, v=2); c.set(2, 2, 3); c.set(6, 3, 3)
        elif theme == 2:
            c.line(0, 1, 7, 1, v=2)
        else:
            c.line(0, 1, 7, 1, v=3); c.set(1, 2, 3); c.set(4, 2, 3); c.set(7, 3, 3)
    return c


def back_tile(theme, n):
    c = Cv(8, 8)
    if n == 1:
        if theme == 0:
            c.line(1, 5, 4, 2, v=1)
        elif theme == 1:
            c.line(0, 4, 7, 4, v=1); c.line(4, 0, 4, 4, v=1)
        elif theme == 2:
            c.rect(2, 2, 3, 3, 1)
        else:
            c.set(4, 3, 3)
    elif n == 2:
        if theme == 0:
            c.set(5, 5, 2)
        elif theme == 1:
            c.set(3, 2, 2); c.set(3, 3, 1)
        elif theme == 2:
            c.line(0, 6, 7, 6, v=1)
        else:
            c.set(2, 6, 2)
    return c


def deco_tiles(theme):
    """Six decorative non-solid tiles: a b c d e f."""
    out = []
    if theme == 0:
        a = art("........", "...3....", "..33....", "..32.3..", ".332.33.", ".322.32.", "3322332.", "32223223")
        b = art("........", "........", "........", "......3.", ".3...33.", ".33..32.", "3323.322", "32233222")
        c = art("..1221..", "..1221..", "..1221..", "..1221..", "..1221..", "..1221..", "..1221..", "..1221..")
        d = art("11111111", "22222222", "1..11..1", "........", "........", "........", "........", "........")
        e = art("........", "........", "...11...", "..1221..", ".112211.", ".122221.", ".122221.", "11111111")
        f = art("...1....", "...1....", "...1....", "..111...", "..121...", "..131...", "..111...", "........")
    elif theme == 1:
        a = art("...33...", "..2222..", "..2222..", ".222222.", ".222222.", "33333333", "...22...", "........")
        b = art("...12...", "...21...", "...12...", "...21...", "...12...", "...21...", "...12...", "...21...")
        c = art("........", "1.......", "1.....1.", "11....1.", ".1..1.11", ".1..1..1", ".11.11.1", "..1..1.1")
        d = art("11111111", "12222221", "12333221", "12222221", "11111111", "........", "........", "........")
        e = art("..2222..", ".211112.", "21111112", "21122112", "21122112", "21111112", "21111112", "22222222")
        f = art("........", "...3....", "...3....", "........", "...3....", "...3....", "........", "...3....")
    elif theme == 2:
        a = art("..1221..", ".122221.", "12211221", "21133112", "21133112", "12211221", ".122221.", "..1221..")
        b = art("11211211", "11211211", "11211211", "11211211", "11211211", "11211211", "11211211", "11211211")
        c = art("........", "...3....", "........", ".3......", "......3.", "..3.....", ".....3..", "........")
        d = art("11111111", "22222222", "33333333", "22222222", "11111111", "........", "........", "........")
        e = art("..2112..", "..1221..", "..2112..", "..1221..", "..2112..", "..1221..", "..2112..", "..1221..")
        f = art("........", "........", "........", "...1....", "..111...", ".12321..", "1233321.", "12333321")
    else:
        a = art("33333333", ".3322333", ".323.232", ".32..22.", "..2..2..", "..2.....", "........", "........")
        b = art("........", "........", "........", "...3....", "..333...", ".33333.3", "33233333", "32323333")
        c = art("11111111", "12222221", "12222221", "12232221", "12222221", "12222221", ".122221.", "..1221..")
        d = art("........", ".3......", "......3.", "..3.....", ".....3..", "3.......", "....3...", "........")
        e = art("...11...", "...11...", "...11...", "...11...", "...11...", "...11...", "...11...", "...11...")
        f = art("........", "...2....", "..222...", ".12221..", "..222...", "...2....", "........", "........")
    for t in (a, b, c, d, e, f):
        out.append(t)
    return out


# Fixed BG tile layout. The common block never changes, the area block is swapped per theme.
SOUL_STEPS = 9


def _heart(full):
    if full:
        return art("........", ".11..11.", "1331223.", "13322221", ".122221.", "..1221..", "...11...", "........")
    return art("........", ".11..11.", "1..11..1", "1......1", ".1....1.", "..1..1..", "...11...", "........")


def _meter(part, n):
    """Three tile bar pieces, n of 8 columns filled."""
    c = Cv(8, 8)
    for x in range(8):
        c.set(x, 1, 2); c.set(x, 6, 2)
    if part == 0:
        c.rect(0, 1, 0, 6, 2)
    if part == 2:
        c.rect(7, 1, 7, 6, 2)
    for x in range(n):
        for y in range(2, 6):
            c.set(x, y, 3)
    return c


def common_tiles():
    names = {}
    tiles = []

    def add(name, cv):
        names[name] = len(tiles)
        tiles.append(cv)
    add('hudbg', Cv(8, 8))
    add('heart_full', _heart(True))
    add('heart_empty', _heart(False))
    add('whet', art("........", "........", ".....11.", "...1123.", ".1123311", "1233111.", ".111....", "........"))
    for part in range(3):
        for n in range(SOUL_STEPS):
            add('soul%d_%d' % (part, n), _meter(part, n))
    border = {
        'b_tl': art("........", ".2222222", ".2111111", ".21.....", ".21.....", ".21.....", ".21.....", ".21....."),
        'b_t': art("........", "22222222", "11111111", "........", "........", "........", "........", "........"),
        'b_tr': art("........", "2222222.", "1111112.", ".....12.", ".....12.", ".....12.", ".....12.", ".....12."),
        'b_l': art(".21.....", ".21.....", ".21.....", ".21.....", ".21.....", ".21.....", ".21.....", ".21....."),
        'b_r': art(".....12.", ".....12.", ".....12.", ".....12.", ".....12.", ".....12.", ".....12.", ".....12."),
        'b_bl': art(".21.....", ".21.....", ".21.....", ".21.....", ".21.....", ".2111111", ".2222222", "........"),
        'b_b': art("........", "........", "........", "........", "........", "11111111", "22222222", "........"),
        'b_br': art(".....12.", ".....12.", ".....12.", ".....12.", ".....12.", "1111112.", "2222222.", "........"),
    }
    for k, v in border.items():
        add(k, v)
    add('m_room', art("........", ".222222.", ".211112.", ".211112.", ".211112.", ".211112.", ".222222.", "........"))
    add('m_seen', art("........", ".333333.", ".322223.", ".322223.", ".322223.", ".322223.", ".333333.", "........"))
    add('m_lantern', art("........", ".333333.", ".322223.", ".323323.", ".323323.", ".322223.", ".333333.", "........"))
    add('m_boss', art("........", ".333333.", ".313313.", ".331133.", ".331133.", ".313313.", ".333333.", "........"))
    for i in range(32, 96):
        add('font%d' % i, glyph(chr(i)))
    return tiles, names


AREA_NAMES = ['rock%d' % m for m in range(16)] + [
    'empty', 'empty1', 'empty2', 'oneway', 'spike', 'lanternL', 'lanternR', 'tablet', 'crack', 'anchor', 'door',
    'deco_a', 'deco_b', 'deco_c', 'deco_d', 'deco_e', 'deco_f']
AREA_FLAG = {'oneway': F_ONEWAY, 'spike': F_HAZARD, 'crack': F_SOLID, 'door': F_SOLID}
AREA_PAL = {'empty': 1, 'empty1': 1, 'empty2': 1, 'oneway': 0, 'spike': 3, 'lanternL': 4, 'lanternR': 4, 'tablet': 2,
            'crack': 0, 'anchor': 6, 'door': 2}


def area_tiles(theme):
    out = {}
    for m in range(16):
        out['rock%d' % m] = rock_tile(theme, m)
    for n, nm in enumerate(('empty', 'empty1', 'empty2')):
        out[nm] = back_tile(theme, n)
    out['oneway'] = art("33333333", "22222222", "1.1..1.1", "........", "........", "........", "........", "........")
    if theme == 1:  # deep water instead of spikes
        out['spike'] = art("........", "..2...2.", ".232.232", "23222322", "22222222", "12222122", "22122221", "11111111")
    elif theme == 2:  # molten slag
        out['spike'] = art("........", ".3...3..", "323.323.", "22222222", "23222322", "22212222", "12222122", "11111111")
    else:
        out['spike'] = art("...3...3", "...3...3", "..32..32", "..32..32", ".3322332", ".3223222", "33222222", "22222222")
    out['lanternL'] = art("......11", ".....122", "....1233", "....1233", "....1232", "....1233", ".....122", ".....111")
    out['lanternR'] = art("11......", "221.....", "3321....", "3321....", "2321....", "3321....", "221.....", "111.....")
    out['tablet'] = art(".111111.", "12222221", "12333321", "12222221", "12333221", "12222221", "12222221", "11111111")
    out['crack'] = art("31131133", "21121122", "12211212", "11222112", "12112211", "21121122", "21222112", "11111111")
    out['anchor'] = art("..1111..", ".133331.", "13.11.31", "13.1..31", "13.1.131", ".133331.", "..1111..", "........")
    out['door'] = art("12222221", "13333331", "12222221", "12222221", "12222221", "13333331", "12222221", "12222221")
    for k, t in zip(('deco_a', 'deco_b', 'deco_c', 'deco_d', 'deco_e', 'deco_f'), deco_tiles(theme)):
        out[k] = t
    return [out[n] for n in AREA_NAMES]


# ------------------------------------------------------------------ sprite sheet
class Sheet:
    def __init__(self):
        self.tiles = []     # 16-byte tiles
        self.names = {}

    def add(self, name, cv):
        self.names[name] = len(self.tiles)
        b = spr_bytes(cv)
        for i in range(0, len(b), 16):
            self.tiles.append(b[i:i + 16])
        assert len(self.tiles) % 2 == 0


def build_sprites():
    s = Sheet()
    for i, f in enumerate(player_frames()):
        s.add('MENUEL%d' % i if i else 'MENUEL', f)
    s.add('AXE_IDLE', axe_idle())
    for i in range(4):
        s.add('AXE%d' % i, axe_swing(i))
    for ei, fn in enumerate(ENEMY_ART):
        for f in range(2):
            s.add('EN%d_%d' % (ei, f), fn(f))
    for ni, fn in enumerate(NPC_ART):
        for f in range(2):
            s.add('NPC%d_%d' % (ni, f), fn(f))
    s.add('IT_RUSH', item_rush()); s.add('IT_HOOK', item_hook()); s.add('IT_CLEAVE', item_cleave()); s.add('IT_CLOAK', item_cloak())
    s.add('IT_SHARD', item_shard(0)); s.add('IT_SHARD1', item_shard(1)); s.add('IT_WHET', item_whet())
    s.add('IT_BELL', item_bell(0)); s.add('IT_BELL1', item_bell(1))
    for i in range(3):
        s.add('SPARK%d' % i, spark(i))
    s.add('MOTE0', mote(0)); s.add('MOTE1', mote(1))
    s.add('DROP0', proj_drop(0)); s.add('DROP1', proj_drop(1))
    s.add('WAVE0', proj_wave(0)); s.add('WAVE1', proj_wave(1))
    s.add('ORB0', proj_orb(0)); s.add('ORB1', proj_orb(1))
    s.add('LINK', hook_link()); s.add('UPMARK', up_mark())
    return s


SPR_BOSS_FIRST = 176


def boss_bytes(i):
    out = []
    for f in range(5):
        out += spr_bytes(BOSS_ART[i](f))
    return out


# ------------------------------------------------------------------ title
def title_canvas():
    """160x144 title: Menuel with axe. Palette 0: art, palette 1: letters."""
    c = Cv(160, 144)
    # Distant bells
    for bx, by in ((18, 18), (136, 26)):
        c.poly([(bx, by), (bx + 4, by), (bx + 10, by + 14), (bx - 6, by + 14)], 1)
    # Axe behind Menuel
    c.poly([(112, 40), (146, 28), (154, 62), (120, 74)], 2, 1)
    c.line(113, 44, 146, 32, v=3)
    c.line(116, 62, 84, 74, v=1)
    c.line(116, 63, 84, 75, v=1)
    c.line(116, 64, 84, 76, v=1)
    # Cloak
    c.poly([(58, 62), (32, 60), (42, 72), (22, 72), (36, 84), (28, 96), (50, 92), (58, 106), (68, 94), (76, 106), (86, 92),
            (106, 96), (96, 84), (114, 72), (92, 72), (102, 60), (78, 62)], 2, 1)
    c.line(44, 84, 84, 66, v=1)
    c.line(44, 85, 84, 67, v=1)
    # Legs
    for x in (56, 76):
        c.poly([(x - 3, 100), (x + 5, 100), (x + 1, 122)], 1)
    # Mask
    c.poly([(68, 6), (94, 44), (70, 72), (66, 72), (42, 44)], 3, 1)
    c.line(68, 6, 94, 44, v=1)
    c.poly([(50, 42), (62, 50), (60, 56), (52, 50)], 1)
    c.poly([(86, 42), (74, 50), (76, 56), (84, 50)], 1)
    c.poly([(76, 24), (80, 28), (76, 32), (72, 28)], 2)
    return c


def build_title():
    """Returns tiles, map, attrs and four palettes."""
    c = title_canvas()
    tiles, m, attrs = [], [], []
    seen = {}
    for ty in range(18):
        for tx in range(20):
            b = tuple(tile_bytes(c, tx * 8, ty * 8))
            if b not in seen:
                seen[b] = len(tiles)
                tiles.append(list(b))
            m.append(seen[b])
            attrs.append(0)
    assert len(tiles) <= 165, len(tiles)
    return tiles, m, attrs
