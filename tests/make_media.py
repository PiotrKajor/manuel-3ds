"""Plays the game again and records the screenshots and GIFs used by the README."""
import sys, os, ctypes
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from t_boss import duel
from PIL import Image
sys.path.insert(0, os.path.join(ROOT, 'assets'))
import world as W

OUT = os.path.join(ROOT, 'docs', 'media')
os.makedirs(OUT, exist_ok=True)
ROOM = W.ROOM_KEYS
g = Game()
s = Search(g)


def top():
    g.L.host_render()
    buf = ctypes.string_at(g.L.host_fb_top(), 400 * 240 * 2)
    raw = bytearray(400 * 240 * 3)
    for i in range(400 * 240):
        c = buf[i * 2] | (buf[i * 2 + 1] << 8)
        raw[i * 3] = (c >> 11) << 3; raw[i * 3 + 1] = ((c >> 5) & 63) << 2; raw[i * 3 + 2] = (c & 31) << 3
    return Image.frombytes('RGB', (400, 240), bytes(raw))


def both(name):
    g.shot(name)
    os.replace(os.path.join(ROOT, 'preview', name + '.png'), os.path.join(OUT, name + '.png'))


class Rec:
    def __init__(self, start=0, frames=240, every=3):
        self.f = []; self.n = 0; self.start = start; self.limit = frames; self.every = every

    def __call__(self):
        self.n += 1
        if self.n > self.start and self.n <= self.start + self.limit and self.n % self.every == 0:
            self.f.append(top().convert('P', palette=Image.ADAPTIVE, colors=64))

    def save(self, name):
        self.f[0].save(os.path.join(OUT, name + '.gif'), save_all=True, append_images=self.f[1:], duration=50, loop=0, optimize=True)
        print(name, len(self.f), 'frames', os.path.getsize(os.path.join(OUT, name + '.gif')) // 1024, 'KB', flush=True)


def walk(goal, key):
    g.set_god(1)
    th = {W.ROOMS[g.room()].theme, W.ROOMS[ROOM[key]].theme}
    assert s.search(goal, allowed={i for i, r in enumerate(W.ROOMS) if r.theme in th}) is not None, key
    g.set_god(0)


def walk_recorded(goal, key, rec):
    start = g.snap()
    g.set_god(1)
    th = {W.ROOMS[g.room()].theme, W.ROOMS[ROOM[key]].theme}
    path = s.search(goal, allowed={i for i, r in enumerate(W.ROOMS) if r.theme in th})
    assert path is not None, key
    g.restore(start)
    for m in path:
        for keys, n in m:
            for _ in range(n):
                if keys == WAIT:
                    if not g.hooking():
                        break
                    g.step(0)
                else:
                    g.step(keys)
                rec()
                if g.mode() != M_PLAY:
                    break
            if g.mode() != M_PLAY:
                break
        for _ in range(180):
            if g.mode() in (M_FADEOUT, M_FADEIN) or (g.mode() == M_PLAY and not g.ground()):
                g.step(0); rec()
            else:
                break
    g.set_god(0)


def item(key):
    r = ROOM[key]
    return lambda: g.room() == r and g.mode() == M_DIALOG


def room(key):
    r = ROOM[key]
    return lambda: g.room() == r


def boss(key, name, rec=None, shot_hp=None):
    walk(room(key), key)
    g.settle()
    for _ in range(400):
        g.step(RIGHT)
        if g.mode() == M_DIALOG:
            break
    g.step(0, 60)
    both(name + '_intro')
    g.settle()
    shots = {}
    def frame():
        if rec:
            rec()
        hp = g.boss_hp()
        if hp and hp * 2 <= G_MAX[key] and 'mid' not in shots and any(g.pr(i, 0) for i in range(10)):
            shots['mid'] = 1
            both(name + '_walka')
    won, hp, fr = duel(g, frame)
    assert won
    g.settle()


G_MAX = dict(pit=20, rope=26, founder=30, anvil=26, summit=44)
g.step(0, 30)
g.L.host_set_headless(0)
g.step(0, 1)
both('01_tytul')
g.L.host_set_headless(1)
g.tap(A)
g.step(0, 120)
both('02_intro')
g.settle()
g.step(0, 30)
both('03_start')
rec = Rec(0, 300)
walk_recorded(item('shrine'), 'shrine', rec)
rec.save('walk_salt_mines')
g.settle()
both('04_rush_shrine')
rec = Rec(240, 240)
boss('pit', 'boss1', rec)
rec.save('boss_foreman')
walk(item('hookroom'), 'hookroom'); g.settle()
g.step(0, 20)
both('05_drowned_belfry')
rec = Rec(0, 360)
walk_recorded(room('choir'), 'choir', rec)
rec.save('hook_hanging_bells')
g.settle()
boss('rope', 'boss2')
walk(item('forge'), 'forge'); g.settle()
g.step(0, 20)
both('06_rust_foundry')
boss('founder', 'boss3')
boss('anvil', 'boss4')
walk(item('cairn'), 'cairn'); g.settle()
g.step(0, 20)
both('07_summit')
rec = Rec(600, 240)
boss('summit', 'boss5', rec)
rec.save('boss_ringer')
g.step(0, 40)
both('08_last_bell')
g.set_god(1)
assert s.search(lambda: g.mode() == M_DIALOG) is not None
g.finish_dialog()
g.step(0, 70)
both('09_napisy')
print('ALL OK')
