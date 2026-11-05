"""Menuel - rooms, entities and all in-game text."""
W, H = 25, 15
NONE = 0xFF

# tile ids stored in room data
T = dict(empty=0, rock=1, oneway=2, spike=3, door=4, crack=5, anchor=6, lantern=7, lanternR=8, tablet=9, entry=10,
         deco_a=11, deco_b=12, deco_c=13, deco_d=14, deco_e=15, deco_f=16)
CH = {'.': 'empty', '#': 'rock', '-': 'oneway', '^': 'spike', 'D': 'door', 'x': 'crack', 'o': 'anchor', 'E': 'entry',
      'a': 'deco_a', 'b': 'deco_b', 'c': 'deco_c', 'd': 'deco_d', 'e': 'deco_e', 'f': 'deco_f'}

ENT = dict(START=1, LANTERN=2, TABLET=3, NPC=4, ENEMY=5, ABILITY=6, SHARD=7, WHET=8, BOSS=9, CRACK=10, ANCHOR=11, BELL=12)

# enemies: crawl, fly, hop, spit variants
MITE, MOTH, FROG, BELLFISH, BEETLE, FURNACE, WRAITH, HARE = range(8)

# flags (bits of the save file)
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


text('INTRO', "THE BELLS OF THE UNDERTOWN HAVE GONE QUIET.",
     "WITHOUT THEM THE CITY FORGETS ITSELF, ONE STREET AT A TIME.",
     "IN A DUSTY LOFT, A SMALL WARDEN IN A KITE-SHAPED MASK OPENS ITS EYES. ITS NAME IS MENUEL.")
text('RINGER1', "OH! YOU ARE AWAKE, MENUEL. GOOD. I AM TOO OLD TO CLIMB.",
     "FOUR BELLS KEEP THIS PLACE ALIVE. SOMETHING HAS STOLEN THEIR VOICES.",
     "TAKE YOUR AXE. WAKE THE BELLS. START IN THE SALT MINES, DOWN THE STAIR.")
text('RINGER2', "THE LANTERNS STILL BURN. REST BY ONE AND IT WILL REMEMBER YOU.",
     "PRESS UP TO USE IT. THE LOWER SCREEN SHOWS WHERE YOU HAVE BEEN.")
text('RINGER3', "I HEARD IT! A BELL! FAINT, BUT TRUE. KEEP GOING, LITTLE WARDEN.")
text('MINER1', "MIND YOUR HEAD. THE FOREMAN STILL WORKS HIS SHIFT, AND HE DOES NOT KNOW HE IS DEAD.",
     "HIS PIT LIES ACROSS THE BROKEN SPAN. NO ONE JUMPS THAT FAR.",
     "BUT THERE IS A SHRINE LEFT OF HERE. THE OLD ONES LEFT A GIFT FOR FAST FEET.")
text('MINER2', "THE SPAN IS UP THE SHAFT AND TO THE RIGHT. PRESS R IN THE AIR TO RUSH.")
text('CLERK1', "NAME? DATE OF DROWNING? NO? THEN I CANNOT HELP YOU. SORRY. HABIT.",
     "THE BELFRY FLOODED YEARS AGO. THE ROPE MEN NEVER LET GO OF THEIR ROPES.",
     "BELOW THE ROPE WALK THERE IS A HOOK FOR THOSE WHO MUST CROSS THE BELLS.")
text('CLERK2', "ANCHOR RINGS HOLD A HOOK. PRESS L NEAR ONE. FILE THAT UNDER USEFUL.")
text('SMITH1', "HAH. THAT AXE IS DULL AND YOU SWING IT LIKE A BROOM.",
     "TAKE WHAT LIES ON MY ANVIL. HOLD DOWN AND STRIKE WHILE FALLING.",
     "CRACKED FLOORS WILL GIVE WAY. MY TWO BROTHERS ARE BELOW. WE SHARE ONE APRON.")
text('SMITH2', "THERE IS A CRACKED FLOOR PAST THE SCRAP TOWER. FALL HARD AND STRIKE.")
text('HERMIT1', "SHH. UP HERE WE KEEP THE QUIET. IT IS ALL THAT IS LEFT.",
     "THE RINGER TOOK THE VOICES SO THAT NOTHING WOULD HURT ANY MORE.",
     "IT MEANT WELL. THAT IS THE WORST OF IT. TAKE THE CLOAK. THE WIND WILL LIFT YOU TWICE.")
text('HERMIT2', "JUMP AGAIN IN THE AIR. THE LAST BELL HANGS ABOVE THE HIGH SHELF.")
text('TAB_CTRL', "A: JUMP. B: AXE. HOLD A TO JUMP HIGHER.",
     "EACH HIT FILLS YOUR ECHO. HOLD X ON SOLID GROUND TO TURN ECHO INTO HEALTH.",
     "DOWN: DROP THROUGH A LEDGE. START: PAUSE.")
text('TAB_MINES', "SHIFT LOG: DAY 9,114. THE BELL HAS STOPPED. WORK CONTINUES.")
text('TAB_BELFRY', "THE WATER ROSE WITHOUT A SOUND. NOTHING HERE MAKES A SOUND NOW.")
text('TAB_FOUNDRY', "WE CAST THE LAST BELL HERE. WE GAVE IT NO TONGUE. IT WAS TOLD TO WAIT.")
text('TAB_SUMMIT', "WHEN ALL IS RINGING, WHO WILL LISTEN? WHEN ALL IS QUIET, WHO WILL HURT?")
text('GOT_RUSH', "YOU FOUND THE RUSH. PRESS R TO DART FORWARD, ON THE GROUND OR IN THE AIR.")
text('GOT_HOOK', "YOU FOUND THE HOOK. PRESS L NEAR AN ANCHOR RING TO PULL YOURSELF TO IT.")
text('GOT_CLEAVE', "YOU FOUND THE CLEAVE. HOLD DOWN AND PRESS B IN THE AIR TO CRASH DOWN AND BREAK CRACKED FLOORS.")
text('GOT_CLOAK', "YOU FOUND THE CLOAK OF WIND. PRESS A IN THE AIR TO JUMP AGAIN.")
text('GOT_SHARD', "A BELL SHARD. IT HUMS IN YOUR HANDS. MAXIMUM HEALTH UP.")
text('GOT_WHET', "A WHETSTONE. THE AXE BITES TWICE AS DEEP.")
text('BOSS0_IN', "SHIFT... NOT... OVER.")
text('BOSS1_IN', "THE ROPE... MUST NOT... SLACKEN.")
text('BOSS2_IN', "WHO COMES? A CUSTOMER! NO, BROTHER. A THIEF! THEN WE MELT IT.")
text('BOSS3_IN', "THE ANVIL STANDS ALONE. IT HAS WAITED A LONG TIME TO BE STRUCK.")
text('BOSS4_IN', "LITTLE ONE. PUT IT DOWN. LISTEN. ISN'T THE QUIET KIND?")
text('BOSS0_OUT', "SOMEWHERE FAR ABOVE, THE FIRST BELL BEGINS TO RING.")
text('BOSS1_OUT', "THE ROPE GOES SLACK. THE SECOND BELL ANSWERS THE FIRST.")
text('BOSS2_OUT', "THE BROTHERS FALL QUIET, AND FOR ONCE THEY AGREE. THE WAY ON IS OPEN.")
text('BOSS3_OUT', "THE ANVIL SPLITS. THE THIRD BELL SOUNDS THROUGH THE IRON. THE WAY UP IS OPEN.")
text('BOSS4_OUT', "THE RINGER LAYS DOWN ITS HANDS. THE LAST BELL HANGS IN FRONT OF YOU, SILENT.")
text('ENDING', "MENUEL TAKES THE AXE AND STRIKES THE BELL ITSELF.",
     "THE NOTE ROLLS DOWN THE MOUNTAIN, THROUGH IRON AND WATER AND SALT.",
     "ALL ACROSS THE UNDERTOWN, PEOPLE REMEMBER THEIR NAMES.",
     "THE LITTLE WARDEN SITS DOWN AND LISTENS FOR A WHILE.")

# ------------------------------------------------------------------ rooms
ROOMS = []
BYPOS = {}


class Room:
    def __init__(s, key, name, theme, x, y):
        assert len(name) <= 17, name
        s.key, s.name, s.theme, s.x, s.y = key, name, theme, x, y
        s.g = [['.'] * W for _ in range(H)]
        s.ents = []
        s.doors = set()
        s.fill(0, 0, W - 1, 0, '#')
        s.fill(0, 0, 0, H - 1, '#')
        s.fill(W - 1, 0, W - 1, H - 1, '#')
        s.fill(0, 13, W - 1, 14, '#')
        assert (x, y) not in BYPOS, name
        BYPOS[(x, y)] = s
        ROOMS.append(s)

    def fill(s, x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                s.g[y][x] = ch
        return s

    def l(s, ch='.'):
        s.fill(0, 10, 0, 12, ch); s.doors.add('l'); return s

    def r(s, ch='.'):
        s.fill(W - 1, 10, W - 1, 12, ch); s.doors.add('r'); return s

    def u(s, x0=11, x1=13, ladder=(10, 7, 4)):
        """Opening in the ceiling with a ladder of ledges up to it."""
        s.fill(x0, 0, x1, 0, '.'); s.doors.add('u')
        for y in ladder:
            s.fill(x0, y, x1, y, '-')
        return s

    def d(s, x0=11, x1=13):
        """Opening in the floor, bridged by a ledge you can drop through."""
        s.fill(x0, 13, x1, 13, '-'); s.fill(x0, 14, x1, 14, '.'); s.doors.add('d'); return s

    def pit(s, x0, x1):
        s.fill(x0, 13, x1, 13, '.'); s.fill(x0, 14, x1, 14, '^'); return s

    def block(s, x0, y0, x1, y1):
        return s.fill(x0, y0, x1, y1, '#')

    def plat(s, x0, x1, y):
        return s.fill(x0, y, x1, y, '-')

    def ent(s, kind, x, y, arg=0, arg2=0):
        s.ents.append((ENT[kind], x, y, arg, arg2)); return s

    def lantern(s, x):
        s.g[12][x] = 'L'; s.g[12][x + 1] = 'M'
        return s.ent('LANTERN', x, 12)

    def tablet(s, x, name, y=12):
        s.g[y][x] = 't'
        return s.ent('TABLET', x, y, TEXT_ORDER.index(name))

    def npc(s, x, who, y=12):
        return s.ent('NPC', x, y, who)

    def enemy(s, kind, x, y=12):
        return s.ent('ENEMY', x, y, kind)

    def ability(s, name, x, y=12):
        return s.ent('ABILITY', x, y, FLAGS[name])

    def shard(s, x, y=12):
        return s.ent('SHARD', x, y, flag('SHARD_' + s.key))

    def whet(s, x, y=12):
        return s.ent('WHET', x, y, FLAGS['WHET'])

    def anchor(s, x, y):
        s.g[y][x] = 'o'
        return s.ent('ANCHOR', x, y)

    def crack(s, x0, x1, y=13, rows=2):
        """Cracked floor: solid until a Cleave lands on it. Stays broken."""
        f = flag('CRACK_' + s.key)
        s.fill(x0, y, x1, y + rows - 1, 'x')
        s.doors.add('d')
        return s.ent('CRACK', x0, y, f, x1 - x0 + 1)

    def boss(s, bid, x=18, entry='l', exit_='r'):
        """Boss arena. The entry door shuts when the fight begins, the exit opens when it ends."""
        if entry == 'l':
            s.fill(0, 10, 0, 12, 'E'); s.doors.add('l')
        if exit_ == 'r':
            s.fill(W - 1, 10, W - 1, 12, 'D'); s.doors.add('r')
        elif exit_ == 'u':
            s.fill(11, 0, 13, 0, 'D'); s.doors.add('u')
        return s.ent('BOSS', x, 9, bid)


R = Room
TEXT = lambda n: TEXT_ORDER.index(n)
RINGER, MINER, CLERK, SMITH, HERMIT = range(5)
# NPC art: 0 ringer, 1 miner, 2 clerk; smith reuses miner, hermit reuses ringer

# ===== SALT MINES (theme 0)
r = R('loft', "RINGER'S LOFT", 0, 1, 1).r()
r.ent('START', 6, 12).lantern(3).npc(13, RINGER)
r.plat(9, 13, 9).plat(16, 20, 7)

r = R('stair', "BELL STAIR", 0, 2, 1).l().d(17, 19)
r.tablet(4, 'TAB_CTRL').plat(8, 12, 10).plat(13, 16, 8).enemy(MITE, 10)

r = R('shaft', "UPPER SHAFT", 0, 2, 2).u(17, 19).l().r()
r.plat(10, 13, 10).enemy(MITE, 8)

r = R('cache', "OLD CACHE", 0, 1, 2).r()
r.pit(6, 16).plat(5, 8, 5).shard(6, 4).anchor(14, 4).anchor(10, 3).enemy(MOTH, 12, 8)

r = R('gallery', "SALT GALLERY", 0, 3, 2).l().r()
r.pit(9, 12).plat(8, 13, 9).enemy(MITE, 5).enemy(MITE, 17).tablet(21, 'TAB_MINES')

r = R('lift', "BROKEN LIFT", 0, 4, 2).l().r().d(6, 8)
r.pit(12, 20).enemy(MITE, 3).enemy(MOTH, 9, 7)

r = R('rest', "MINER'S REST", 0, 4, 3).u(6, 8).l()
r.lantern(13).npc(18, MINER)

r = R('shrine', "RUSH SHRINE", 0, 3, 3).r()
r.pit(10, 14).plat(11, 13, 9).ability('RUSH', 4).enemy(MOTH, 12, 6).enemy(MITE, 18).block(2, 11, 6, 12).ents[0]
r.ents[0] = (ENT['ABILITY'], 4, 10, FLAGS['RUSH'], 0)

r = R('span', "CRYSTAL SPAN", 0, 5, 2).l().r()
r.pit(7, 12).plat(9, 10, 9).enemy(MOTH, 10, 6).enemy(MITE, 16).enemy(MITE, 3)

r = R('pit', "FOREMAN'S PIT", 0, 6, 2).boss(0)
r.plat(4, 7, 9).plat(17, 20, 9)

# ===== DROWNED BELFRY (theme 1)
r = R('gate', "WATER GATE", 1, 7, 2).l().r()
r.lantern(3).npc(9, CLERK).tablet(13, 'TAB_BELFRY').enemy(FROG, 19)

r = R('nave', "FLOODED NAVE", 1, 8, 2).l().r()
r.pit(5, 19).plat(7, 9, 10).plat(12, 14, 8).plat(17, 19, 10).enemy(FROG, 13, 7).enemy(BELLFISH, 8, 3)

r = R('walk', "ROPE WALK", 1, 9, 2).l().r().d(5, 7)
r.pit(13, 21).enemy(FROG, 10).enemy(BELLFISH, 17, 3)

r = R('under', "UNDERCROFT", 1, 9, 3).u(5, 7).l().r()
r.enemy(FROG, 14).plat(11, 13, 10)

r = R('hookroom', "HOOK SHRINE", 1, 8, 3).r()
r.block(3, 8, 6, 12).ability('HOOK', 4, 7).plat(8, 10, 10).enemy(BELLFISH, 12, 3).enemy(FROG, 15)

r = R('archive', "DROWNED ARCHIVE", 1, 10, 3).l()
r.crack(13, 16).enemy(FROG, 8).enemy(BELLFISH, 19, 3).plat(4, 7, 9).plat(18, 21, 9)

r = R('vault', "SUNK VAULT", 1, 10, 4).u(13, 15, ladder=(10, 7, 4))
r.shard(4).pit(7, 10).enemy(FROG, 19).plat(7, 10, 10)

r = R('bells', "HANGING BELLS", 1, 10, 2).l().r()
r.pit(3, 21).anchor(7, 5).anchor(12, 4).anchor(17, 5).plat(12, 13, 10).enemy(BELLFISH, 10, 2).enemy(BELLFISH, 15, 2)

r = R('choir', "CHOIR LOFT", 1, 11, 2).l().u(16, 18)
r.lantern(5).enemy(FROG, 11)

r = R('spire', "SPIRE WALK", 1, 11, 1).d(16, 18).r()
r.pit(4, 13).plat(5, 7, 10).plat(10, 12, 8).enemy(BELLFISH, 8, 3).enemy(FROG, 21)
r.anchor(4, 6).block(1, 9, 3, 12)

r = R('rope', "ROPE CHAMBER", 1, 12, 1).boss(1, 11)
r.plat(5, 8, 9).plat(16, 19, 9)

# ===== RUST FOUNDRY (theme 2)
r = R('slag', "SLAG DOOR", 2, 13, 1).l().r()
r.lantern(3).enemy(BEETLE, 12).enemy(FURNACE, 20)

r = R('blast', "BLAST HALL", 2, 14, 1).l().r()
r.pit(6, 10).pit(14, 18).plat(7, 9, 9).plat(15, 17, 9).enemy(BEETLE, 12).enemy(FURNACE, 21).tablet(2, 'TAB_FOUNDRY')

r = R('crane', "CRANE BAY", 2, 15, 1).l().d(19, 21)
r.pit(4, 15).anchor(7, 5).anchor(13, 5).plat(9, 11, 9).enemy(BEETLE, 10, 8)
r.plat(2, 4, 4).shard(2, 3).block(22, 4, 23, 12)

r = R('cast', "CASTING FLOOR", 2, 15, 2).u(19, 21).l().r()
r.enemy(BEETLE, 8).enemy(FURNACE, 14).lantern(3)

r = R('forge', "CLEAVE FORGE", 2, 14, 2).r().l()
r.npc(16, SMITH).ability('CLEAVE', 10).enemy(FURNACE, 4).plat(9, 12, 9)

r = R('kiln', "OLD KILN", 2, 13, 2).r()
r.fill(9, 8, 9, 12, '#').fill(14, 8, 14, 12, '#').crack(10, 13, y=7, rows=1).plat(4, 7, 10).plat(12, 13, 10).whet(11)
r.doors.discard('d')

r = R('scrap', "SCRAP TOWER", 2, 16, 2).l()
r.crack(11, 14).plat(4, 8, 9).plat(16, 20, 8).enemy(BEETLE, 6, 8).enemy(FURNACE, 18, 7)

r = R('cinder', "CINDER RUN", 2, 16, 3).u(11, 14).r()
r.pit(16, 21).plat(17, 20, 9).enemy(BEETLE, 5).enemy(FURNACE, 22)

r = R('founder', "FOUNDER'S HALL", 2, 17, 3).boss(2)
r.plat(4, 7, 9).plat(17, 20, 9)

r = R('quench', "QUENCH ROOM", 2, 18, 3).l().r()
r.lantern(7).enemy(FURNACE, 18)

r = R('anvil', "ANVIL ROOM", 2, 19, 3).boss(3, exit_='u')
r.plat(11, 13, 4).plat(11, 13, 7)
r.plat(4, 7, 10).plat(17, 20, 10)

# ===== SUMMIT OF SILENCE (theme 3)
r = R('cold', "COLD STAIR", 3, 19, 2).d(11, 13).l()
r.enemy(WRAITH, 6, 6).enemy(HARE, 18).lantern(21)

r = R('ledge', "WIND LEDGE", 3, 18, 2).r().u(17, 19).l()
r.pit(6, 12).plat(8, 10, 9).enemy(HARE, 3).enemy(WRAITH, 11, 5).tablet(15, 'TAB_SUMMIT')

r = R('chapel', "FROZEN CHAPEL", 3, 17, 2).r()
r.block(2, 6, 7, 12).shard(4, 5).pit(9, 15).anchor(11, 4).enemy(WRAITH, 12, 7).enemy(HARE, 20)

r = R('pass', "HUSH PASS", 3, 18, 1).d(17, 19).l()
r.pit(6, 13).plat(8, 11, 9).enemy(WRAITH, 12, 5).enemy(HARE, 3)

r = R('cairn', "CLOAK CAIRN", 3, 17, 1).r().u(4, 6, ladder=())
r.npc(14, HERMIT).ability('CLOAK', 9).enemy(HARE, 19)
r.block(1, 8, 3, 12).block(7, 8, 8, 12).fill(4, 8, 6, 8, '-')

r = R('shelf', "HIGH SHELF", 3, 17, 0).d(4, 6).r()
r.pit(10, 17).plat(13, 14, 8).enemy(WRAITH, 14, 4).enemy(HARE, 21)

r = R('last', "LAST LANTERN", 3, 18, 0).l().r()
r.lantern(11).enemy(HARE, 4)

r = R('summit', "SILENT BELFRY", 3, 19, 0)
r.boss(4, 18, exit_=None)
r.fill(W - 1, 10, W - 1, 12, '#')
r.plat(4, 7, 9).plat(17, 20, 9)
r.ent('BELL', 12, 11, FLAGS['BOSS4'])

ROOM_KEYS = {r.key: i for i, r in enumerate(ROOMS)}


def exits(r):
    out = []
    for side, (dx, dy) in zip('lrud', ((-1, 0), (1, 0), (0, -1), (0, 1))):
        if side in r.doors:
            other = BYPOS.get((r.x + dx, r.y + dy))
            assert other is not None, (r.key, side)
            back = {'l': 'r', 'r': 'l', 'u': 'd', 'd': 'u'}[side]
            assert back in other.doors, (r.key, side, other.key)
            out.append(ROOMS.index(other))
        else:
            out.append(NONE)
    return out


def tile_rows(r):
    """Room grid as tile ids. Lantern and tablet cells are mapped here."""
    out = []
    for row in r.g:
        for ch in row:
            if ch == 'L':
                out.append(T['lantern'])
            elif ch == 'M':
                out.append(T['lanternR'])
            elif ch == 't':
                out.append(T['tablet'])
            else:
                out.append(T[CH[ch]])
    return out


def decorate(r):
    """Scatter decoration on empty cells, deterministically."""
    i = ROOMS.index(r)
    occupied = {(e[1], e[2]) for e in r.ents}
    for x in range(1, W - 1):
        h = (x * 7 + i * 13) % 11
        if r.g[1][x] == '.' and r.g[0][x] == '#' and h in (1, 5):
            r.g[1][x] = 'a' if h == 1 else 'f'
        h = (x * 5 + i * 3) % 9
        if r.g[12][x] == '.' and r.g[13][x] == '#' and (x, 12) not in occupied and h == 2:
            r.g[12][x] = 'b'
        h = (x * 11 + i * 17) % 13
        if h == 3 and r.g[2][x] == '.' and r.g[1][x] in '.af':
            r.g[2][x] = 'c' if r.g[1][x] == '.' and r.g[3][x] == '.' else r.g[2][x]
        h = (x * 3 + i * 23) % 17
        if h == 6 and r.g[5][x] == '.':
            r.g[5][x] = 'd'


for _r in ROOMS:
    decorate(_r)
