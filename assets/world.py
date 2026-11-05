"""Menuel - rooms and text. A room spans both screens: 25x30 tiles of 16 px, 400x480 in all.
The top screen shows rows 0-14 at full width. The bottom screen shows rows 15-29, columns 2.5 to 22.5,
so the lower half has thick side walls and "shoulders" at y=240 on both sides of the top screen."""
W, H = 25, 30
NONE = 0xFF
FLOOR = 27        # entity row standing on the floor
SHOULDER = 14     # entity row standing on a shoulder

T = dict(empty=0, rock=1, oneway=2, spike=3, door=4, crack=5, entry=6)
CH = {'.': 'empty', '#': 'rock', '-': 'oneway', '^': 'spike', 'D': 'door', 'x': 'crack', 'E': 'entry'}
ENT = dict(START=1, LANTERN=2, TABLET=3, NPC=4, ENEMY=5, ABILITY=6, SHARD=7, WHET=8, BOSS=9, CRACK=10, ANCHOR=11, BELL=12)
MITE, MOTH, FROG, BELLFISH, BEETLE, FURNACE, WRAITH, HARE = range(8)

FLAGS = {}


def flag(name):
    if name not in FLAGS:
        FLAGS[name] = len(FLAGS)
    return FLAGS[name]


for n in ('RUSH', 'HOOK', 'CLEAVE', 'CLOAK', 'BOSS0', 'BOSS1', 'BOSS2', 'BOSS3', 'BOSS4', 'WHET', 'MET_RINGER', 'MET_MINER',
          'MET_CLERK', 'MET_SMITH', 'MET_HERMIT', 'ENDED'):
    flag(n)

TEXTS, TEXT_ORDER = {}, []


def text(name, *pages):
    TEXT_ORDER.append(name)
    TEXTS[name] = pages


text('INTRO', "The bells of the Undertown have gone quiet.",
     "Without them the city forgets itself, one street at a time.",
     "In a dusty loft, a small warden in a kite-shaped mask opens its eyes. Its name is Menuel.")
text('RINGER1', "Oh! You are awake, Menuel. Good. I am too old to climb.",
     "Four bells keep this place alive. Something has stolen their voices.",
     "Take your axe. Wake the bells. Start in the Salt Mines, up the ledges and to the right.")
text('RINGER2', "The lanterns still burn. Rest by one and it will remember you.",
     "Press Up to use it. Pause with Start to see your map on the lower screen.")
text('RINGER3', "I heard it! A bell! Faint, but true. Keep going, little warden.")
text('MINER1', "Mind your head. The Foreman still works his shift, and he does not know he is dead.",
     "His pit lies across the broken span. No one jumps that far.",
     "But there is a shrine left of here. The old ones left a gift for fast feet.")
text('MINER2', "The span is up the shaft and to the right. Press R in the air to rush.")
text('CLERK1', "Name? Date of drowning? No? Then I cannot help you. Sorry. Habit.",
     "The belfry flooded years ago. The rope men never let go of their ropes.",
     "Below the rope walk there is a hook, for those who must cross the bells.")
text('CLERK2', "Anchor rings hold a hook. Press L near one. File that under useful.")
text('SMITH1', "Hah. That axe is dull and you swing it like a broom.",
     "Take what lies on my anvil. Hold Down and strike while falling.",
     "Cracked floors will give way. My two brothers are below. They share one apron.")
text('SMITH2', "There is a cracked floor in the scrap tower. Fall hard and strike.")
text('HERMIT1', "Shh. Up here we keep the quiet. It is all that is left.",
     "The Ringer took the voices so that nothing would hurt any more.",
     "It meant well. That is the worst of it. Take the cloak. The wind will lift you twice.")
text('HERMIT2', "Jump again in the air. The last bell hangs above the high shelf.")
text('TAB_CTRL', "A: jump. B: axe. Hold A to jump higher.",
     "Each hit fills your echo. Hold X on solid ground to turn echo into health.",
     "Down: drop through a ledge. Start: pause and map.")
text('TAB_MINES', "Shift log, day 9,114. The bell has stopped. Work continues.")
text('TAB_BELFRY', "The water rose without a sound. Nothing here makes a sound now.")
text('TAB_FOUNDRY', "We cast the last bell here. We gave it no tongue. It was told to wait.")
text('TAB_SUMMIT', "When all is ringing, who will listen? When all is quiet, who will hurt?")
text('GOT_RUSH', "You found the Rush. Press R to dart forward, on the ground or in the air.")
text('GOT_HOOK', "You found the Hook. Press L near an anchor ring, or tap a ring on the lower screen.")
text('GOT_CLEAVE', "You found the Cleave. Hold Down and press B in the air to crash down and break cracked floors.")
text('GOT_CLOAK', "You found the Cloak of Wind. Press A in the air to jump again.")
text('GOT_SHARD', "A bell shard. It hums in your hands. Maximum health up.")
text('GOT_WHET', "A whetstone. The axe bites twice as deep.")
text('BOSS0_IN', "Shift... not... over.")
text('BOSS1_IN', "The rope... must not... slacken.")
text('BOSS2_IN', "Who comes? A customer! No, brother. A thief! Then we melt it.")
text('BOSS3_IN', "The Anvil stands alone. It has waited a long time to be struck.")
text('BOSS4_IN', "Little one. Put it down. Listen. Isn't the quiet kind?")
text('BOSS0_OUT', "Somewhere far above, the first bell begins to ring.")
text('BOSS1_OUT', "The rope goes slack. The second bell answers the first.")
text('BOSS2_OUT', "The brothers fall quiet, and for once they agree. The way on is open.")
text('BOSS3_OUT', "The Anvil splits. The third bell sounds through the iron. The way up is open.")
text('BOSS4_OUT', "The Ringer lays down its hands. The last bell hangs in front of you, silent.")
text('ENDING', "Menuel takes the axe and strikes the bell itself.",
     "The note rolls down the mountain, through iron and water and salt.",
     "All across the Undertown, people remember their names.",
     "The little warden sits down and listens for a while.")

ROOMS = []
BYPOS = {}
RINGER, MINER, CLERK, SMITH, HERMIT = range(5)


class R:
    def __init__(s, key, name, theme, x, y):
        s.key, s.name, s.theme, s.x, s.y = key, name, theme, x, y
        s.g = [['.'] * W for _ in range(H)]
        s.ents = []
        s.doors = {}
        s.props = []
        s.fill(0, 0, W - 1, 0, '#')
        s.fill(0, 0, 0, 14, '#')
        s.fill(W - 1, 0, W - 1, 14, '#')
        s.fill(0, 15, 2, H - 1, '#')          # thick lower walls, the bottom screen is narrower
        s.fill(W - 3, 15, W - 1, H - 1, '#')
        s.fill(0, 28, W - 1, 29, '#')
        assert (x, y) not in BYPOS, name
        BYPOS[(x, y)] = s
        ROOMS.append(s)

    def fill(s, x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                s.g[y][x] = ch
        return s

    def l(s, lv='L', ch='.'):
        """Door on the left: L at the floor (bottom screen), H at the shoulder (top screen)."""
        if lv == 'H':
            s.fill(0, 11, 0, 14, ch)
        else:
            s.fill(0, 24, 2, 27, ch)
        s.doors['l'] = lv
        return s

    def r(s, lv='L', ch='.'):
        if lv == 'H':
            s.fill(W - 1, 11, W - 1, 14, ch)
        else:
            s.fill(W - 3, 24, W - 1, 27, ch)
        s.doors['r'] = lv
        return s

    def u(s, x0=11, x1=13, ladder=(24, 20, 16, 12, 8, 4)):
        s.fill(x0, 0, x1, 0, '.'); s.doors['u'] = 1
        for y in ladder:
            s.fill(x0, y, x1, y, '-')
        return s

    def d(s, x0=11, x1=13):
        s.fill(x0, 28, x1, 28, '-'); s.fill(x0, 29, x1, 29, '.'); s.doors['d'] = 1
        return s

    def pit(s, x0, x1):
        s.fill(x0, 28, x1, 28, '.'); s.fill(x0, 29, x1, 29, '^')
        return s

    def block(s, x0, y0, x1, y1):
        return s.fill(x0, y0, x1, y1, '#')

    def plat(s, x0, x1, y):
        return s.fill(x0, y, x1, y, '-')

    def steps(s, *spans):
        """A staircase of ledges: (x0, x1, row) triples."""
        for x0, x1, y in spans:
            s.plat(x0, x1, y)
        return s

    def ent(s, kind, x, y, arg=0, arg2=0):
        s.ents.append((ENT[kind], x, y, arg, arg2))
        return s

    def lantern(s, x, y=FLOOR):
        return s.ent('LANTERN', x, y)

    def tablet(s, x, name, y=FLOOR):
        s.props.append(('tablet', x, y))
        return s.ent('TABLET', x, y, TEXT_ORDER.index(name))

    def npc(s, x, who, y=FLOOR):
        return s.ent('NPC', x, y, who)

    def enemy(s, kind, x, y=FLOOR):
        return s.ent('ENEMY', x, y, kind)

    def ability(s, name, x, y=FLOOR):
        return s.ent('ABILITY', x, y, FLAGS[name])

    def shard(s, x, y=FLOOR):
        return s.ent('SHARD', x, y, flag('SHARD_' + s.key))

    def whet(s, x, y=FLOOR):
        return s.ent('WHET', x, y, FLAGS['WHET'])

    def anchor(s, x, y):
        return s.ent('ANCHOR', x, y)

    def crack(s, x0, x1, y=28, rows=2):
        f = flag('CRACK_' + s.key)
        s.fill(x0, y, x1, y + rows - 1, 'x')
        if y == 28:
            s.doors['d'] = 1
        return s.ent('CRACK', x0, y, f, x1 - x0 + 1)

    def boss(s, bid, x=13, entry='H', exit_=('r', 'H')):
        """Boss arena: the entry shuts when the fight starts, the exit opens when the boss falls."""
        s.l(entry, 'E')
        if exit_:
            if exit_[0] == 'r':
                s.r(exit_[1], 'D')
            else:
                s.fill(11, 0, 13, 0, 'D'); s.doors['u'] = 1
        return s.ent('BOSS', x, FLOOR, bid)


# ===== SALT MINES
r = R('loft', "Ringer's Loft", 0, 1, 1).r('H')
r.ent('START', 8, FLOOR).lantern(5).npc(14, RINGER)
r.steps((7, 11, 24), (12, 16, 20), (17, 21, 17))

r = R('stair', "Bell Stair", 0, 2, 1).l('H').d(17, 19)
r.steps((3, 6, 18), (5, 8, 22), (3, 6, 25)).tablet(10, 'TAB_CTRL').enemy(MITE, 13)
r.steps((9, 13, 12), (15, 19, 10)).enemy(MOTH, 16, 6)

r = R('shaft', "Upper Shaft", 0, 2, 2).u(17, 19, ladder=(24, 20, 16, 12, 8, 4)).l('L').r('L')
r.steps((7, 11, 22)).enemy(MITE, 9).enemy(MOTH, 8, 12)

r = R('cache', "Old Cache", 0, 1, 2).r('L')
r.pit(3, 16).block(1, 15, 8, 15).shard(3, SHOULDER).anchor(15, 19).anchor(9, 12).enemy(MOTH, 10, 20)

r = R('gallery', "Salt Gallery", 0, 3, 2).l('L').r('H')
r.pit(8, 11).enemy(MITE, 5).enemy(MITE, 15).tablet(19, 'TAB_MINES')
r.steps((14, 18, 24), (9, 13, 20), (14, 19, 17)).enemy(MOTH, 8, 9)

r = R('lift', "Broken Lift", 0, 4, 2).l('H').r('H').d(13, 15)
r.block(3, 15, 8, 15).block(20, 15, 21, 15).steps((3, 6, 24), (7, 10, 20), (3, 6, 17))
r.enemy(MITE, 18).enemy(MOTH, 14, 8)

r = R('rest', "Miner's Rest", 0, 4, 3).u(13, 15).l('L')
r.lantern(6).npc(9, MINER).enemy(MOTH, 18, 8)

r = R('shrine', "Rush Shrine", 0, 3, 3).r('L')
r.pit(8, 13).plat(9, 12, 24).block(3, 22, 6, 27).ability('RUSH', 4, 21).enemy(MOTH, 10, 18).enemy(MITE, 17)

r = R('span', "Crystal Span", 0, 5, 2).l('H').r('H')
r.pit(3, 21).block(7, 15, 9, 15).block(15, 15, 17, 15).enemy(MITE, 8, SHOULDER).enemy(MITE, 16, SHOULDER).enemy(MOTH, 12, 7)

r = R('pit', "Foreman's Pit", 0, 6, 2).boss(0)
r.steps((3, 6, 24), (18, 21, 24), (3, 5, 20), (19, 21, 20), (3, 5, 16), (19, 21, 16))

# ===== DROWNED BELFRY
r = R('gate', "Water Gate", 1, 7, 2).l('H').r('H')
r.lantern(5).npc(10, CLERK).tablet(15, 'TAB_BELFRY').enemy(FROG, 19)
r.steps((3, 6, 24), (7, 10, 20), (3, 6, 17), (14, 17, 22), (18, 21, 18))

r = R('nave', "Flooded Nave", 1, 8, 2).l('H').r('L')
r.pit(6, 18).steps((3, 7, 17), (8, 11, 21), (13, 16, 24), (9, 12, 12)).enemy(FROG, 14, 23).enemy(BELLFISH, 10, 15)

r = R('walk', "Rope Walk", 1, 9, 2).l('L').r('H').d(5, 7)
r.pit(13, 17).enemy(FROG, 10).enemy(BELLFISH, 15, 17)
r.steps((18, 21, 24), (13, 17, 20), (18, 21, 17))

r = R('under', "Undercroft", 1, 9, 3).u(5, 7).l('L').r('L')
r.enemy(FROG, 14).plat(11, 14, 23)

r = R('hookroom', "Hook Shrine", 1, 8, 3).r('L')
r.block(3, 21, 8, 27).ability('HOOK', 5, 20).plat(9, 12, 24).enemy(BELLFISH, 13, 16).enemy(FROG, 17)

r = R('archive', "Drowned Archive", 1, 10, 3).l('L')
r.crack(13, 16).enemy(FROG, 8).enemy(BELLFISH, 18, 18).plat(4, 8, 23).plat(17, 21, 23)

r = R('vault', "Sunk Vault", 1, 10, 4).u(13, 16)
r.shard(4).pit(7, 10).plat(7, 10, 24).enemy(FROG, 19)

r = R('bells', "Hanging Bells", 1, 10, 2).l('H').r('H')
r.pit(3, 21).anchor(6, 9).anchor(12, 6).anchor(18, 9).enemy(BELLFISH, 10, 4).enemy(BELLFISH, 16, 4)
r.props.append(('bigbell', 12, 2))

r = R('choir', "Choir Loft", 1, 11, 2).l('H').u(16, 18)
r.lantern(5).enemy(FROG, 11).steps((3, 7, 24), (8, 11, 20), (3, 7, 17))

r = R('spire', "Spire Walk", 1, 11, 1).d(16, 18).r('H')
r.pit(4, 13).steps((5, 8, 24), (10, 13, 21), (16, 19, 24), (20, 21, 20), (17, 19, 16)).enemy(BELLFISH, 8, 16).enemy(FROG, 11, 20).anchor(9, 10)

r = R('rope', "Rope Chamber", 1, 12, 1).boss(1, 10)
r.steps((3, 6, 24), (18, 21, 24), (3, 5, 20), (19, 21, 20), (3, 5, 16), (19, 21, 16))

# ===== RUST FOUNDRY
r = R('slag', "Slag Door", 2, 13, 1).l('H').r('H')
r.lantern(5).enemy(BEETLE, 12).enemy(FURNACE, 18)
r.steps((3, 6, 24), (7, 10, 20), (3, 6, 17), (13, 17, 22), (18, 21, 18))

r = R('blast', "Blast Hall", 2, 14, 1).l('H').r('L')
r.pit(6, 9).pit(13, 16).tablet(4, 'TAB_FOUNDRY').enemy(BEETLE, 11).enemy(FURNACE, 19)
r.steps((3, 6, 17), (7, 10, 21), (11, 14, 24))

r = R('crane', "Crane Bay", 2, 15, 1).l('L').d(18, 20)
r.pit(5, 15).anchor(8, 19).anchor(13, 18).steps((9, 12, 24)).enemy(BEETLE, 10, 23)
r.plat(3, 6, 9).shard(4, 8).enemy(FURNACE, 17)

r = R('cast', "Casting Floor", 2, 15, 2).u(18, 20).l('L').r('L')
r.enemy(BEETLE, 9).enemy(FURNACE, 14).lantern(5)

r = R('forge', "Cleave Forge", 2, 14, 2).r('L').l('L')
r.npc(16, SMITH).ability('CLEAVE', 11).enemy(FURNACE, 5).plat(9, 13, 23)
r.props.append(('anvil', 11, FLOOR))

r = R('kiln', "Old Kiln", 2, 13, 2).r('L')
r.block(9, 22, 9, 27).block(14, 22, 14, 27).crack(10, 13, y=21, rows=1).steps((4, 7, 24)).plat(12, 13, 25).whet(11).enemy(BEETLE, 18)

r = R('scrap', "Scrap Tower", 2, 16, 2).l('L')
r.crack(11, 14).steps((4, 8, 24), (16, 20, 23)).enemy(BEETLE, 6, 23).enemy(FURNACE, 18, 22)

r = R('cinder', "Cinder Run", 2, 16, 3).u(11, 14).r('L')
r.pit(15, 19).plat(16, 18, 24).enemy(BEETLE, 5).enemy(FURNACE, 20)

r = R('founder', "Founder's Hall", 2, 17, 3).boss(2, entry='L', exit_=('r', 'L'))
r.steps((3, 6, 23), (18, 21, 23), (8, 16, 19), (3, 6, 15), (18, 21, 15))

r = R('quench', "Quench Room", 2, 18, 3).l('L').r('L')
r.lantern(10).enemy(FURNACE, 18)

r = R('anvil', "Anvil Room", 2, 19, 3).boss(3, entry='L', exit_=('u', 0))
r.steps((3, 6, 23), (18, 21, 23), (11, 13, 24), (11, 13, 20), (11, 13, 16), (11, 13, 12), (11, 13, 8), (11, 13, 4))

# ===== SUMMIT OF SILENCE
r = R('cold', "Cold Stair", 3, 19, 2).d(11, 13).l('H')
r.lantern(5).enemy(WRAITH, 15, 18).enemy(HARE, 18)
r.steps((3, 6, 24), (7, 10, 20), (3, 6, 17))

r = R('ledge', "Wind Ledge", 3, 18, 2).r('H').u(17, 19, ladder=(12, 8, 4)).l('L')
r.pit(7, 13).plat(8, 12, 24).enemy(HARE, 4).enemy(WRAITH, 11, 16).tablet(16, 'TAB_SUMMIT')
r.steps((15, 19, 24), (18, 21, 20), (17, 21, 16))

r = R('chapel', "Frozen Chapel", 3, 17, 2).r('L')
r.block(3, 20, 7, 27).shard(5, 19).pit(9, 15).anchor(11, 18).enemy(WRAITH, 12, 19).enemy(HARE, 19)

r = R('pass', "Hush Pass", 3, 18, 1).d(17, 19).l('H')
r.pit(6, 13).steps((7, 12, 24), (3, 6, 20), (3, 6, 17), (15, 19, 24)).enemy(WRAITH, 12, 16).enemy(HARE, 16, 23)
r.steps((13, 16, 20), (8, 12, 17))

r = R('cairn', "Cloak Cairn", 3, 17, 1).r('H').u(4, 6, ladder=())
r.npc(14, HERMIT).ability('CLOAK', 9).enemy(HARE, 19)
r.steps((15, 19, 24), (18, 21, 20), (17, 21, 16), (15, 18, 12), (4, 12, 8))
r.block(13, 8, 14, 8)

r = R('shelf', "High Shelf", 3, 17, 0).d(4, 6).r('H')
r.pit(9, 15).steps((10, 14, 24)).enemy(WRAITH, 12, 16).enemy(HARE, 19)
r.steps((16, 20, 24), (18, 21, 20), (17, 21, 16))

r = R('last', "Last Lantern", 3, 18, 0).l('H').r('H')
r.lantern(11).enemy(HARE, 5)
r.steps((3, 6, 24), (3, 5, 20), (3, 5, 17), (18, 21, 24), (19, 21, 20), (19, 21, 17))

r = R('summit', "Silent Belfry", 3, 19, 0)
r.boss(4, 13, exit_=None)
r.steps((3, 6, 24), (18, 21, 24), (3, 5, 20), (19, 21, 20), (3, 5, 16), (19, 21, 16))
r.ent('BELL', 12, FLOOR, FLAGS['BOSS4'])

ROOM_KEYS = {r.key: i for i, r in enumerate(ROOMS)}


def exits(r):
    out = []
    for side, (dx, dy) in zip('lrud', ((-1, 0), (1, 0), (0, -1), (0, 1))):
        if side in r.doors:
            other = BYPOS.get((r.x + dx, r.y + dy))
            assert other is not None, (r.key, side)
            back = {'l': 'r', 'r': 'l', 'u': 'd', 'd': 'u'}[side]
            assert back in other.doors, (r.key, side, other.key)
            if side in 'lr':
                assert r.doors[side] == other.doors[back], ('door levels differ', r.key, side, other.key)
            out.append(ROOMS.index(other))
        else:
            out.append(NONE)
    return out


def tile_rows(r):
    return [T[CH[ch]] for row in r.g for ch in row]


def check_vertical(r):
    """An opening in a floor must line up exactly with the opening in the ceiling below it."""
    if 'd' not in r.doors:
        return
    below = BYPOS[(r.x, r.y + 1)]
    fall = {x for x in range(W) if r.g[28][x] in '-x' and r.g[29][x] in '.x'}
    rise = {x for x in range(W) if below.g[0][x] in '.D'}
    assert fall == rise, ('vertical openings differ', r.key, sorted(fall), below.key, sorted(rise))


for _r in ROOMS:
    check_vertical(_r)
