"""Menuel - original chiptune songs. Notes C2..B6, R is a rest, name:ticks."""
NOTE = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def parse(seq):
    out = []
    for tok in seq.split():
        n, l = tok.split(':')
        if n == 'R':
            out.append((0, int(l)))
        else:
            out.append(((int(n[-1]) - 2) * 12 + NOTE[n[:-1]] + 1, int(l)))
    return out


SONGS = {}


def song(name, tick, duty, lead, bass, drums=0):
    a, b = parse(lead), parse(bass)
    assert sum(x[1] for x in a) == sum(x[1] for x in b), (name, sum(x[1] for x in a), sum(x[1] for x in b))
    SONGS[name] = dict(tick=tick, duty=duty, lead=a, bass=b, drums=drums)


song('TITLE', 10, 1,
     "D5:6 F5:2 A5:8 G5:4 F5:4 E5:8  C5:6 E5:2 G5:8 F5:4 E5:4 D5:8  "
     "D5:4 F5:4 A5:4 D6:4 C6:6 A5:2 G5:8  F5:4 E5:4 D5:4 C#5:4 D5:16",
     "D3:16 A2:16 C3:16 G2:16 A#2:16 F2:16 A2:16 D3:16")
song('MINES', 8, 2,
     "A4:2 R:2 C5:2 R:2 E5:2 R:2 C5:2 R:2  G4:2 R:2 B4:2 R:2 D5:2 R:2 B4:2 R:2  "
     "F4:2 R:2 A4:2 R:2 C5:2 R:2 A4:2 R:2  E4:2 R:2 G#4:2 R:2 B4:4 E5:4  "
     "A5:6 G5:2 E5:4 C5:4  G5:6 E5:2 D5:4 B4:4  F5:6 E5:2 C5:4 A4:4  B4:4 C5:4 B4:4 G#4:4",
     "A2:8 E3:8 G2:8 D3:8 F2:8 C3:8 E2:8 B2:8 A2:8 E3:8 G2:8 D3:8 F2:8 C3:8 E2:8 E3:8")
song('BELFRY', 12, 3,
     "E5:8 B4:4 G4:4  A4:8 C5:8  B4:4 G4:4 E4:8  F#4:8 R:8  "
     "G4:4 B4:4 E5:4 G5:4  F#5:8 D5:8  C5:4 B4:4 A4:4 G4:4  E4:16",
     "E2:16 A2:16 E2:16 B2:16 C3:16 D3:16 A2:16 E2:16")
song('FOUNDRY', 6, 0,
     "D4:2 D4:2 R:2 D4:2 F4:2 R:2 G4:2 R:2  G#4:2 G4:2 F4:2 D4:2 R:4 C4:4  "
     "D4:2 D4:2 R:2 D4:2 F4:2 R:2 A4:2 R:2  G#4:2 A4:2 G#4:2 G4:2 F4:4 D4:4  "
     "A4:4 G#4:4 G4:4 F4:4  G4:2 F4:2 D4:4 F4:4 D4:4  A4:4 C5:4 D5:4 C5:4  A4:2 G#4:2 G4:2 F4:2 D4:8",
     "D2:2 D3:2 D2:2 D3:2 D2:2 D3:2 D2:2 D3:2 D2:2 D3:2 D2:2 D3:2 C2:2 C3:2 C2:2 C3:2 "
     "D2:2 D3:2 D2:2 D3:2 D2:2 D3:2 D2:2 D3:2 D2:2 D3:2 D2:2 D3:2 C2:2 C3:2 C2:2 C3:2 "
     "G2:2 G3:2 G2:2 G3:2 G2:2 G3:2 G2:2 G3:2 D2:2 D3:2 D2:2 D3:2 D2:2 D3:2 D2:2 D3:2 "
     "F2:2 F3:2 F2:2 F3:2 F2:2 F3:2 F2:2 F3:2 G2:2 G3:2 G2:2 G3:2 D2:2 D3:2 D2:2 D3:2", 1)
song('SUMMIT', 14, 1,
     "B5:4 F#5:4 D5:4 B4:4  C#5:8 E5:8  A5:4 E5:4 C#5:4 A4:4  B4:16  "
     "G5:4 D5:4 B4:4 G4:4  A4:8 D5:8  F#5:4 E5:4 D5:4 C#5:4  B4:16",
     "B2:16 A2:16 F#2:16 B2:16 G2:16 D3:16 A2:16 B2:16")
song('BOSS', 5, 0,
     "E5:2 E5:2 R:2 E5:2 G5:2 R:2 F#5:2 E5:2  D5:2 D5:2 R:2 D5:2 F#5:2 R:2 E5:2 D5:2  "
     "C5:2 C5:2 R:2 C5:2 E5:2 R:2 D5:2 C5:2  B4:2 D#5:2 F#5:2 B5:2 A5:2 F#5:2 D#5:2 B4:2",
     "E2:2 E3:2 E2:2 E3:2 E2:2 E3:2 E2:2 E3:2 D2:2 D3:2 D2:2 D3:2 D2:2 D3:2 D2:2 D3:2 "
     "C2:2 C3:2 C2:2 C3:2 C2:2 C3:2 C2:2 C3:2 B2:2 B3:2 B2:2 B3:2 B2:2 B3:2 B2:2 B3:2", 1)
song('FINAL', 5, 2,
     "A5:4 R:2 A5:2 G#5:4 E5:4  F5:4 R:2 F5:2 E5:4 C5:4  D5:4 R:2 D5:2 C5:4 A4:4  B4:2 C5:2 D5:2 E5:2 G#5:8  "
     "A4:2 C5:2 E5:2 A5:2 C6:4 B5:4  A5:2 F5:2 D5:2 F5:2 A5:4 G#5:4  E5:2 G#5:2 B5:2 E6:2 D6:4 B5:4  A5:8 R:8",
     "A2:4 A3:4 A2:4 A3:4 F2:4 F3:4 F2:4 F3:4 D2:4 D3:4 D2:4 D3:4 E2:4 E3:4 E2:4 E3:4 "
     "A2:4 A3:4 A2:4 A3:4 D2:4 D3:4 D2:4 D3:4 E2:4 E3:4 E2:4 E3:4 A2:4 E3:4 A2:8", 1)
song('END', 11, 1,
     "G5:4 B5:4 D6:4 B5:4  A5:4 C6:4 E6:4 C6:4  B5:4 D6:4 G6:4 D6:4  C6:4 B5:4 A5:8  "
     "G5:4 B5:4 D6:4 G6:4  F#6:4 E6:4 D6:8  E6:4 C6:4 D6:4 B5:4  G5:16",
     "G2:16 A2:16 B2:16 D3:16 E3:16 D3:16 C3:8 D3:8 G2:16")
song('QUIET', 16, 1,
     "D5:8 A4:8 C5:8 G4:8 A#4:8 F4:8 A4:16",
     "D3:16 C3:16 A#2:16 A2:16")
SONG_ORDER = ['TITLE', 'MINES', 'BELFRY', 'FOUNDRY', 'SUMMIT', 'BOSS', 'FINAL', 'END', 'QUIET']
