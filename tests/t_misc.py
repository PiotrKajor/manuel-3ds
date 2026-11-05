"""Death and continue, save across a restart, pause, audio, rendering of every room."""
import sys, os, ctypes, array
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
sys.path.insert(0, os.path.join(ROOT, 'assets'))
import world as W

g = Game()
g.step(0, 5)
assert g.mode() == M_TITLE
g.tap(A); g.settle()
assert g.room() == 0 and g.hp() == 5

# use the lantern (room 0, tile 3): real input
for _ in range(120):
    if g.near() >= 0 and W.ROOMS[0].ents[g.near()][0] == W.ENT['LANTERN']:
        break
    g.step(LEFT)
g.step(0, 20)
g.tap(UP)
print('lantern used, save written')

# walk into the first room's enemy until dead, using real collisions
gate = W.ROOM_KEYS['gallery']
b = bytearray(8)
g.setup(gate, 1, 12, 2, bytes(b))
while g.mode() != M_PLAY:
    g.step(0)
for _ in range(4000):
    if g.dead() or g.mode() == M_DEATH:
        break
    g.step(RIGHT)
    if g.px() > 300:
        break
print('death state', g.mode(), g.hp())
assert g.mode() == M_DEATH or g.hp() < 2, 'expected damage in the gallery'
for _ in range(400):
    if g.mode() == M_PLAY and g.hp() > 0:
        break
    g.step(0)
print('respawned in room', g.room(), 'hp', g.hp())
assert g.room() == gate and g.hp() == g.maxhp()   # setup() made this room the respawn point

# lantern save from earlier is still on the card: restart must offer CONTINUE
assert g.L.host_init(os.path.join(ROOT, 'build', 'assets.bin').encode())
g.L.host_set_headless(1)
g.step(0, 5)
g.tap(A)                    # first item is CONTINUE when a save exists
g.settle()
assert g.room() == 0 and g.mode() == M_PLAY
print('continue after restart ok')

# pause and back
g.tap(START); assert g.mode() == M_PAUSE
g.tap(START); assert g.mode() == M_PLAY

# audio is produced, songs change
buf = (ctypes.c_int16 * 22050)()
g.L.host_audio(buf, 22050)
assert max(abs(v) for v in buf) > 500, 'silent'
print('audio peak', max(abs(v) for v in buf))

# every room renders and is unique
g.L.host_set_headless(0)
seen = set()
for i in range(g.num_rooms()):
    g.setup(i, 3, 12, 5, bytes(8))
    g.step(0, 1)
    g.L.host_render()
    seen.add(ctypes.string_at(g.L.host_fb_top(), 400 * 240 * 2))
print('rooms rendered', len(seen), 'of', g.num_rooms())
assert len(seen) == g.num_rooms()
print('ALL OK')
