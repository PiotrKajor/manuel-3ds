"""Test driver: the real game core in a shared library. Input goes through the same key mask as on the console."""
import ctypes, os
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..')
A, B, SELECT, START, RIGHT, LEFT, UP, DOWN, R, L, X = 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024
M_TITLE, M_PLAY, M_DIALOG, M_PAUSE, M_FADEOUT, M_FADEIN, M_DEATH, M_ENDING, M_CREDITS = range(9)
WAIT = -1  # macro token: wait until the Hook has finished pulling
ENT_LANTERN, ENT_ABILITY, ENT_SHARD, ENT_WHET, ENT_BOSS, ENT_CRACK, ENT_BELL = 2, 6, 7, 8, 9, 10, 12


class Game:
    def __init__(self):
        self.L = ctypes.CDLL(os.path.join(ROOT, 'build', 'libmenuel.so'))
        self.L.host_fb_top.restype = ctypes.c_void_p
        self.L.host_fb_bot.restype = ctypes.c_void_p
        self.L.host_clear_save()
        assert self.L.host_init(os.path.join(ROOT, 'build', 'assets.bin').encode())
        self.size = self.L.host_state_size()
        self.L.host_set_headless(1)
        self.flags = {}
        for l in open(os.path.join(ROOT, 'src', 'gen.h')):
            p = l.split()
            if len(p) == 3 and p[0] == '#define':
                self.flags[p[1]] = p[2]

    def define(self, n):
        return int(self.flags[n])

    def __getattr__(self, n):
        fn = getattr(self.__dict__['L'], 'host_' + n)
        return fn

    def snap(self):
        b = ctypes.create_string_buffer(self.size)
        self.L.host_snapshot(b)
        return b

    def restore(self, b):
        self.L.host_restore(b)

    def step(self, keys=0, n=1):
        self.L.host_run(keys, n)

    def tap(self, k, n=3, after=3):
        self.step(k, n); self.step(0, after)

    def pos(self):
        return self.L.host_room(), self.L.host_px(), self.L.host_py()

    def finish_dialog(self):
        """Read every page with real button presses."""
        pages = 0
        while self.L.host_mode() == M_DIALOG:
            self.step(A, 2); self.step(0, 2)
            pages += 1
            assert pages < 2000
        return pages

    def settle(self):
        for _ in range(400):
            m = self.L.host_mode()
            if m == M_PLAY:
                return
            if m == M_DIALOG:
                self.finish_dialog()
            else:
                self.step(0)

    def start_new(self):
        self.step(0, 5)
        self.tap(A)
        self.settle()

    def shot(self, name):
        def conv(buf, w, h):
            raw = bytearray(w * h * 3)
            for i in range(w * h):
                c = buf[i * 2] | (buf[i * 2 + 1] << 8)
                raw[i * 3] = (c >> 11) << 3; raw[i * 3 + 1] = ((c >> 5) & 63) << 2; raw[i * 3 + 2] = (c & 31) << 3
            return Image.frombytes('RGB', (w, h), bytes(raw))
        self.L.host_render()
        im = Image.new('RGB', (400, 480))
        im.paste(conv(ctypes.string_at(self.L.host_fb_top(), 400 * 240 * 2), 400, 240), (0, 0))
        im.paste(conv(ctypes.string_at(self.L.host_fb_bot(), 320 * 240 * 2), 320, 240), (40, 240))
        os.makedirs(os.path.join(ROOT, 'preview'), exist_ok=True)
        im.save(os.path.join(ROOT, 'preview', name + '.png'))


# ------------------------------------------------------------------ movement macros
def macros(has):
    """Each macro is a list of (keys, frames). They end once the player lands or changes room."""
    out = []
    for d in (LEFT, RIGHT):
        for n in (8, 16, 32):
            out.append([(d, n)])
        for hold in (6, 12, 24):
            out.append([(A | d, hold), (d, 90)])
        for hold in (10, 24):
            out.append([(A, hold), (d, 90)])
            out.append([(A | d, hold), (0, 90)])
        if has('RUSH'):
            out.append([(R | d, 2), (d, 14)])
            for t in (6, 14, 22, 30):
                out.append([(A | d, t), (R | d, 2), (d, 90)])
        if has('CLOAK'):
            for t in (10, 20, 30):
                out.append([(A | d, t), (d, 3), (A | d, 26), (d, 90)])
            if has('RUSH'):
                out.append([(A | d, 20), (d, 2), (A | d, 20), (R | d, 2), (d, 90)])
    out.append([(A, 26), (0, 60)])
    out.append([(DOWN, 4), (0, 40)])
    if has('CLEAVE'):
        out.append([(A, 20), (DOWN, 2), (DOWN | B, 2), (DOWN, 60)])
        out.append([(A, 28), (DOWN, 2), (DOWN | B, 2), (DOWN, 60)])
        for d in (LEFT, RIGHT):
            out.append([(A | d, 14), (DOWN, 2), (DOWN | B, 2), (DOWN, 60)])
    if has('HOOK'):
        for lead in ([], [(A, 10)], [(A, 24)]):
            for d in (0, LEFT, RIGHT):
                one = [(L | d, 2), (WAIT, 60)]
                out.append(lead + one + [(d, 90)])
                out.append(lead + one + [(A | d, 20), (d, 90)])
                out.append(lead + one + [(d, 3)] + one + [(d, 90)])
                out.append(lead + one + [(d, 3)] + one + [(d, 3)] + one + [(d, 90)])
                out.append(lead + one + [(d, 3)] + one + [(d, 3)] + one + [(d, 3)] + one + [(d, 90)])
    return out


class Search:
    """Breadth-first search over real game states with button macros. Enemies are harmless here (traversal only)."""

    def __init__(self, g):
        self.g = g

    def has_fn(self):
        g = self.g
        return lambda n: g.has(g.define('F_' + n))

    def run_macro(self, m):
        """Plays one macro. Returns False if the player died or a dialog/room change cut it short at a useful point."""
        g = self.g
        room = g.room()
        for keys, n in m:
            for _ in range(n):
                if keys == WAIT:
                    if not g.hooking():
                        break
                    g.step(0)
                else:
                    g.step(keys)
                mode = g.mode()
                if mode != M_PLAY or g.room() != room:
                    return True
        return True

    def after(self):
        """Let transitions finish so nodes are always stable play states."""
        g = self.g
        for _ in range(60):
            if g.mode() in (M_FADEOUT, M_FADEIN):
                g.step(0)
            else:
                break

    def key(self):
        g = self.g
        return (g.room(), g.px() // 10, g.py() // 8, g.ground())

    def search(self, goal, limit=400000, allowed=None):
        """Finds a path to goal(). Returns the input list or None. Leaves the game in the goal state."""
        g = self.g
        start = g.snap()
        seen = {self.key()}
        self.rooms = {g.room()}
        from collections import deque
        q = deque([(start, None, None)])
        ms = macros(self.has_fn())
        tried = 0
        while q and tried < limit:
            snap, parent, _ = node = q.popleft()
            for m in ms:
                g.restore(snap)
                tried += 1
                self.run_macro(m)
                reached = goal()
                if g.mode() in (M_FADEOUT, M_FADEIN):
                    self.after()
                    reached = reached or goal()
                    for _ in range(120):          # fall or rise into the new room
                        if g.mode() != M_PLAY or g.ground():
                            break
                        g.step(0)
                if reached:
                    path = [m]
                    n = node
                    while n[1] is not None:
                        path.append(n[2]); n = n[1]
                    path.reverse()
                    self.tried = tried
                    self.seen = seen
                    return path
                if g.mode() != M_PLAY or not g.ground():
                    continue
                if allowed is not None and g.room() not in allowed:
                    continue
                k = self.key()
                if k not in seen:
                    seen.add(k)
                    self.rooms.add(g.room())
                    q.append((g.snap(), node, m))
        self.tried = tried
        self.seen = seen
        return None
