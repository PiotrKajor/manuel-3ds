"""Each boss fought with button input only and normal damage. The bot reads the game state and looks ahead with
snapshots, about what a good player can see. It starts with the health a player has without any optional shard."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
sys.path.insert(0, os.path.join(ROOT, 'assets'))
import world as W

F = W.FLAGS
FIGHTS = [('Salt Foreman', 'pit', 'rest', ['RUSH']), ('Rope Drowned', 'rope', 'choir', ['RUSH', 'BOSS0', 'HOOK']),
          ('Two-Headed Founder', 'founder', 'cast', ['RUSH', 'BOSS0', 'HOOK', 'BOSS1', 'CLEAVE']),
          ('The Anvil', 'anvil', 'quench', ['RUSH', 'BOSS0', 'HOOK', 'BOSS1', 'CLEAVE', 'BOSS2']),
          ('Silent Ringer', 'summit', 'last', ['RUSH', 'BOSS0', 'HOOK', 'BOSS1', 'CLEAVE', 'BOSS2', 'BOSS3', 'CLOAK'])]
PLANS = []
for d in (0, LEFT, RIGHT):
    PLANS.append([(d, 16)])
    PLANS.append([(d | A, 16)])
    PLANS.append([(d | B, 2), (d, 14)])
    PLANS.append([(d | A, 6), (d | A | B, 2), (d, 8)])
for d in (LEFT, RIGHT):
    PLANS.append([(d | R, 2), (d, 14)])
    PLANS.append([(d | A, 8), (d | R, 2), (d, 6)])


def fight(g, room_key, start_key, flags, maxhp, verbose=True):
    b = bytearray(8)
    for n in flags:
        b[F[n] >> 3] |= 1 << (F[n] & 7)
    r = W.ROOM_KEYS[room_key]
    g.setup(r, 6, 27, maxhp, bytes(b))
    while g.mode() != M_PLAY:
        g.step(0)
    # walk in until the fight starts
    for _ in range(300):
        g.step(RIGHT)
        if g.mode() == M_DIALOG:
            break
    g.settle()
    g.step(0, 2)
    return duel(g)


def duel(g, on_frame=None):
    frames = 0
    while g.boss_active() and g.dead() == 0 and frames < 60 * 300:
        if g.mode() != M_PLAY:
            if g.mode() == M_DIALOG:
                g.finish_dialog()
            else:
                g.step(0)
            continue
        s = g.snap()
        best, bestv = None, -1e18
        hp0, bhp0 = g.hp(), g.boss_hp()
        for pl in PLANS:
            g.restore(s)
            for k, n in pl:
                g.step(k, n)
            g.step(0, 18)
            v = (g.hp() - hp0) * 1000 + (bhp0 - g.boss_hp()) * 120
            if g.dead():
                v -= 5000
            if g.boss_active():
                dx = abs(g.px() + 16 - (g.boss_x() + 48))
                v -= abs(dx - 62) * 0.6
                if not g.ground():
                    v -= 3
                v -= 0 if 60 < g.px() < 320 else 25
            if v > bestv:
                best, bestv = pl, v
        g.restore(s)
        for k, n in best:
            if on_frame:
                for _ in range(min(n, 8)):
                    g.step(k)
                    on_frame()
            else:
                g.step(k, min(n, 8))
            frames += min(n, 8)
            if g.mode() != M_PLAY:
                break
    won = not g.boss_active() and g.dead() == 0
    return won, g.hp(), frames


if __name__ == '__main__':
    g = Game()
    g.shot('title') if False else None
    fails = 0
    for name, room, lant, fl in FIGHTS:
        won, hp, fr = fight(g, room, lant, fl, 5)
        print('%-20s %s  health left %d/5  %ds' % (name, 'WON ' if won else 'LOST', hp, fr // 60), flush=True)
        fails += not won
    print('ALL OK' if not fails else 'FAILED %d' % fails)
    sys.exit(1 if fails else 0)
