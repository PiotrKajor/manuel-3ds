"""Plays the game again and records the screenshots and GIFs used by the README. GIFs show both screens."""
import sys, os, ctypes
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from t_boss import duel
from PIL import Image
sys.path.insert(0, os.path.join(ROOT, 'assets'))
import world as W

OUT = os.path.join(ROOT, 'docs', 'media')
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))
ROOM = W.ROOM_KEYS
g = Game()
s = Search(g)


def screens():
    def conv(buf, w, h):
        a = np.frombuffer(buf, dtype='<u2').reshape(h, w)
        return np.dstack([((a >> 11) & 31) * 255 // 31, ((a >> 5) & 63) * 255 // 63, (a & 31) * 255 // 31]).astype('uint8')
    g.L.host_render()
    im = Image.new('RGB', (400, 480))
    im.paste(Image.fromarray(conv(ctypes.string_at(g.L.host_fb_top(), 400 * 240 * 2), 400, 240)), (0, 0))
    im.paste(Image.fromarray(conv(ctypes.string_at(g.L.host_fb_bot(), 320 * 240 * 2), 320, 240)), (40, 240))
    return im


import numpy as np


def both(name):
    screens().save(os.path.join(OUT, name + '.png'))


class Rec:
    def __init__(self, start=0, frames=240, every=3):
        self.f = []; self.n = 0; self.start = start; self.limit = frames; self.every = every

    def __call__(self):
        self.n += 1
        if self.n > self.start and self.n <= self.start + self.limit and self.n % self.every == 0:
            self.f.append(screens().resize((300, 360), Image.LANCZOS).convert('P', palette=Image.ADAPTIVE, colors=96))

    def save(self, name):
        self.f[0].save(os.path.join(OUT, name + '.gif'), save_all=True, append_images=self.f[1:], duration=50, loop=0, optimize=True)
        print(name, len(self.f), 'frames', os.path.getsize(os.path.join(OUT, name + '.gif')) // 1024, 'KB', flush=True)


def allowed(key):
    th = {W.ROOMS[g.room()].theme, W.ROOMS[ROOM[key]].theme}
    return {i for i, r in enumerate(W.ROOMS) if r.theme in th}


def walk(goal, key):
    g.set_god(1)
    assert s.search(goal, allowed=allowed(key)) is not None, key
    g.set_god(0)


def walk_recorded(goal, key, rec):
    start = g.snap()
    g.set_god(1)
    path = s.search(goal, allowed=allowed(key))
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


def boss(key, name, maxhp, rec=None):
    walk(room(key), key)
    g.settle()
    for _ in range(400):
        g.step(RIGHT)
        if g.mode() == M_DIALOG:
            break
    assert g.mode() == M_DIALOG, name
    g.step(0, 60)
    both(name + '_intro')
    g.settle()
    shots = {}
    def frame():
        if rec:
            rec()
        hp = g.boss_hp()
        st = g.boss_state()
        if hp and hp * 2 <= maxhp and 'mid' not in shots and any(g.pr(i, 0) for i in range(10)):
            shots['mid'] = 1
            both(name + '_walka')
    won, hp, fr = duel(g, frame)
    assert won
    g.settle()


g.step(0, 30)
both('01_tytul')
g.tap(A)
g.step(0, 120)
both('02_intro')
g.settle()
g.step(0, 30)
both('03_start')
rec = Rec(0, 330)
walk_recorded(item('shrine'), 'shrine', rec)
rec.save('walk_salt_mines')
g.settle()
both('04_rush_shrine')
rec = Rec(300, 240)
boss('pit', 'boss1', 20, rec)
rec.save('boss_foreman')
walk(item('hookroom'), 'hookroom'); g.settle()
g.step(0, 20)
both('05_drowned_belfry')
rec = Rec(0, 360)
walk_recorded(room('choir'), 'choir', rec)
rec.save('hook_hanging_bells')
g.settle()
rec = Rec(300, 300)
boss('rope', 'boss2', 26, rec)
rec.save('boss_rope')
walk(item('forge'), 'forge'); g.settle()
g.step(0, 20)
both('06_rust_foundry')
boss('founder', 'boss3', 30)
boss('anvil', 'boss4', 26)
walk(item('cairn'), 'cairn'); g.settle()
g.step(0, 20)
both('07_summit')
g.tap(START)
g.step(0, 2)
both('10_pauza_mapa')
g.tap(START)
rec = Rec(600, 240)
boss('summit', 'boss5', 44, rec)
rec.save('boss_ringer')
g.step(0, 40)
both('08_last_bell')
g.set_god(1)
assert s.search(lambda: g.mode() == M_DIALOG) is not None
g.finish_dialog()
g.step(0, 70)
both('09_napisy')
print('ALL OK')
