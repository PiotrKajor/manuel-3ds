"""Refuses a CIA whose kernel capabilities would stop it from launching. Installing alone does not reveal this."""
import struct, sys


def align(x):
    return (x + 63) & ~63


d = open(sys.argv[1], 'rb').read(0x4000 + 0x10000)
hs, _, _, cs, ts, tm = struct.unpack('<IHHIII', d[:20])
off = align(hs) + align(cs) + align(ts) + align(tm)
assert d[off + 0x100:off + 0x104] == b'NCCH', 'no NCCH at the expected offset'
ex = d[off + 0x200:off + 0x600]
caps = struct.unpack('<28I', ex[0x370:0x370 + 28 * 4])
flags = [c for c in caps if (c >> 23) == 0x1FE]
assert flags, 'no kernel flags descriptor'
mem = (flags[0] >> 8) & 0xF
assert mem == 1, 'memory type is %d, must be 1 (APPLICATION)' % mem
sys_mask = [c for c in caps if (c >> 27) == 0x1E]
assert len(sys_mask) >= 6, 'system call list looks truncated'
print('CIA check ok: memory type APPLICATION, %d system call masks' % len(sys_mask))
