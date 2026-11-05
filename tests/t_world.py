"""With real physics: everything is reachable in order, and every reachable place can still reach the goal."""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from lib import *

g = Game()
g.set_god(1)
s = Search(g)
sys.path.insert(0, os.path.join(ROOT, 'assets'))
import world as W

F = W.FLAGS
ROOM = W.ROOM_KEYS


def area(*keys):
    """Rooms in the same areas as the given rooms, to keep the search focused."""
    themes = {W.ROOMS[ROOM[k]].theme for k in keys}
    return {i for i, r in enumerate(W.ROOMS) if r.theme in themes}


def flagbytes(names):
    b = bytearray(8)
    for n in names:
        i = F[n]
        b[i >> 3] |= 1 << (i & 7)
    return bytes(b)


def at(room_key):
    r = W.ROOMS[ROOM[room_key]]
    for e in r.ents:
        if e[0] in (W.ENT['LANTERN'], W.ENT['START']):
            return ROOM[room_key], e[1], e[2]
    raise SystemExit('no lantern in ' + room_key)


def goal_item(key):
    r = ROOM[key]
    n = g.nent(r)
    ents = [i for i in range(n) if g.ent(r, i, 0) in (ENT_ABILITY, ENT_SHARD, ENT_WHET)]
    def f():
        return g.room() == r and g.mode() == M_DIALOG
    return f


def goal_room(key):
    r = ROOM[key]
    return lambda: g.room() == r


# name, start lantern, flags held, goal
A0 = []
A1 = ['RUSH']
A1b = A1 + ['BOSS0']
A2 = A1b + ['HOOK']
A2b = A2 + ['BOSS1']
A3 = A2b + ['CLEAVE']
A3b = A3 + ['BOSS2', 'BOSS3']
A4 = A3b + ['CLOAK']
STAGES = [
    ('reach Rush', 'loft', A0, goal_item('shrine'), 'shrine'),
    ('reach Salt Foreman', 'rest', A1, goal_room('pit'), 'pit'),
    ('reach Hook', 'gate', A1b, goal_item('hookroom'), 'hookroom'),
    ('reach Rope Drowned', 'gate', A2, goal_room('rope'), 'rope'),
    ('reach Cleave', 'slag', A2b, goal_item('forge'), 'forge'),
    ('reach Founder', 'cast', A3, goal_room('founder'), 'founder'),
    ('reach Anvil', 'quench', A3 + ['BOSS2'], goal_room('anvil'), 'anvil'),
    ('reach Cloak', 'cold', A3b, goal_item('cairn'), 'cairn'),
    ('reach Silent Ringer', 'cold', A4, goal_room('summit'), 'summit'),
    ('shard: cache', 'gate', A2b, goal_item('cache'), 'cache'),
    ('shard: vault', 'choir', A4, goal_item('vault'), 'vault'),
    ('shard: crane', 'cast', A4, goal_item('crane'), 'crane'),
    ('shard: chapel', 'cold', A4, goal_item('chapel'), 'chapel'),
    ('whetstone', 'cast', A4, goal_item('kiln'), 'kiln'),
    ('home 1: foundry to belfry', 'quench', A4 + ['CRACK_scrap'], goal_room('rope'), 'rope'),
    ('home 2: belfry to mines', 'choir', A4 + ['CRACK_scrap'], goal_room('pit'), 'pit'),
    ('home 3: mines to loft', 'rest', A4 + ['CRACK_scrap'], goal_room('loft'), 'loft'),
]
# Things that must NOT work before their ability
BLOCKS = [
    ('Foreman needs Rush', 'rest', A0, goal_room('pit'), 'pit'),
    ('Hanging Bells need Hook', 'gate', A1b, goal_room('choir'), 'choir'),
    ('Scrap Tower needs Cleave', 'cast', A2b, goal_room('cinder'), 'cinder'),
    ('High Shelf needs Cloak', 'cold', A3b, goal_room('shelf'), 'shelf'),
]
bad = 0
t0 = time.time()
for name, lant, fl, goal, gkey in STAGES:
    g.host_clear_save if False else None
    room, tx, ty = at(lant)
    g.setup(room, tx, ty, 5, flagbytes(fl))
    g.settle() if False else None
    while g.mode() != M_PLAY:
        g.step(0)
    p = s.search(goal, allowed=area(lant, gkey))
    ok = p is not None
    bad += not ok
    print('%-26s %s  moves=%s tried=%d nodes=%d  %.0fs' % (name, 'OK  ' if ok else 'FAIL', len(p) if p else '-', s.tried, len(s.seen), time.time() - t0), flush=True)
    if not ok:
        print('    reached:', ' '.join(W.ROOMS[i].key for i in sorted(s.rooms)), flush=True)
for name, lant, fl, goal, gkey in BLOCKS:
    room, tx, ty = at(lant)
    g.setup(room, tx, ty, 5, flagbytes(fl))
    while g.mode() != M_PLAY:
        g.step(0)
    p = s.search(goal, limit=150000, allowed=area(lant, gkey))
    ok = p is None
    bad += not ok
    print('%-26s %s  tried=%d nodes=%d  %.0fs' % (name, 'OK  ' if ok else 'BROKEN (sequence break)', s.tried, len(s.seen), time.time() - t0), flush=True)
print('FAILED' if bad else 'ALL OK', bad)
sys.exit(1 if bad else 0)
