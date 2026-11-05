"""Plays the whole game from the title screen to the credits with button input.
Walking between goals uses harmless enemies (the search would otherwise spend hours on them).
Boss fights use normal damage. If a fight is lost, the game's own respawn is used and the fight is retried."""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from t_boss import duel
sys.path.insert(0, os.path.join(ROOT, 'assets'))
import world as W

ROOM = W.ROOM_KEYS
g = Game()
s = Search(g)
t0 = time.time()
log = lambda m: print('[%4ds] %s' % (time.time() - t0, m), flush=True)


def walk(goal, label, key):
    g.set_god(1)
    th = {W.ROOMS[g.room()].theme, W.ROOMS[ROOM[key]].theme}
    p = s.search(goal, allowed={i for i, r in enumerate(W.ROOMS) if r.theme in th})
    assert p is not None, label + ': no path, reached ' + ' '.join(W.ROOMS[i].key for i in sorted(s.rooms))
    log('%-26s %d moves' % (label, len(p)))
    # the search leaves the game in the goal state
    g.set_god(0)


def item(key):
    r = ROOM[key]
    return lambda: g.room() == r and g.mode() == M_DIALOG


def room(key):
    r = ROOM[key]
    return lambda: g.room() == r


def boss(key, name):
    walk(room(key), 'walk to ' + name, key)
    g.settle()
    tries = 0
    while True:
        for _ in range(400):
            g.step(RIGHT)
            if g.mode() == M_DIALOG:
                break
        g.settle()
        won, hp, fr = duel(g)
        tries += 1
        log('%-26s %s, health %d/%d, %ds, attempt %d' % (name, 'won' if won else 'lost', hp, g.maxhp(), fr // 60, tries))
        if won:
            break
        assert tries < 12, name
        for _ in range(400):
            if g.mode() == M_PLAY and not g.dead():
                break
            g.step(0)
        walk(room(key), 'return to ' + name, key)
        g.settle()
    g.settle()


g.step(0, 30)
g.L.host_set_headless(0); g.shot('01_title'); g.L.host_set_headless(1)
g.start_new()
g.shot('02_start')
walk(item('shrine'), 'Rush', 'shrine'); g.settle()
boss('pit', 'Salt Foreman')
g.shot('03_after_foreman')
walk(item('hookroom'), 'Hook', 'hookroom'); g.settle()
boss('rope', 'Rope Drowned')
walk(item('forge'), 'Cleave', 'forge'); g.settle()
g.shot('04_foundry')
boss('founder', 'Two-Headed Founder')
boss('anvil', 'The Anvil')
walk(item('cairn'), 'Cloak', 'cairn'); g.settle()
g.shot('05_summit')
boss('summit', 'Silent Ringer')
g.shot('06_last_bell')
g.set_god(1)
p = s.search(lambda: g.mode() == M_DIALOG)
assert p is not None, 'no way to the bell'
g.finish_dialog()
assert g.mode() == M_CREDITS, g.mode()
log('credits reached')
g.step(0, 70)
g.shot('07_credits')
g.tap(START)
assert g.mode() == M_TITLE
log('back at the title screen')
print('ALL OK')
