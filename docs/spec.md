# Menuel and the Last Bell: spec

Native homebrew for the user's 2DS XL (`.cia` for the HOME Menu, `.3dsx` for the Homebrew
Launcher). No GBC emulator is involved. Menuel is the user's character
(`docs/menuel-reference.png`). World, story, enemies, art and music are original to this
project. In-game text is English.

## Technology
- C with libctru. Software renderer in RGB565 with alpha at 400x240 (top) and 320x240 (bottom).
- Rooms span both screens (400x480 world). The bottom screen shows x 40..359, y 240..479.
- Game code in `src/` is platform free. `plat_3ds.c` is the console layer, `host.c` builds the
  same game as a shared library for tests.
- Sound: own chiptune synth through NDSP (needs `/3ds/dspfirm.cdc`, present on the user's card).
  Without it the game runs silently.
- Save: `sdmc:/3ds/Menuel/save.bin`.

## Content
- 40 two-screen rooms (25x30 tiles of 16 px) in four areas: Salt Mines, Drowned Belfry,
  Rust Foundry, Summit of Silence.
- Five bosses: Salt Foreman, Rope Drowned, Two-Headed Founder, The Anvil, Silent Ringer.
- Four abilities: Rush (dash), Hook (anchor points), Cleave (down strike, breaks cracked
  floors), Cloak (second jump).
- Upgrades: four bell shards (+1 max health each), whetstone (double axe damage).
- Lanterns save the game and heal.
- Pause shows the map, abilities and bells on the bottom screen. Health follows Menuel, dialogue uses the other screen.

## Controls
| Input | Action |
|---|---|
| Left / Right or Circle Pad | move |
| A | jump, second jump with Cloak |
| B | axe |
| R | Rush |
| L, or tap a ring on the bottom screen | Hook to an anchor |
| Down + B in the air | Cleave |
| X (hold, on the ground) | spend echo to heal |
| Down | drop through a ledge |
| Up | talk, read, use a lantern |
| START | pause and map |
| SELECT | performance readout |

## Definition of done
- `tests/t_world.py`: the map is consistent, and with real game physics every room and item is
  reachable in the intended ability order, with no way to get stranded.
- `tests/t_full.py`: a button-driven run goes from the title screen to the credits.
- Separate tests: each boss fought with real inputs, death and continue, save after restart,
  audio output.
- The `.3dsx` starts and runs in a 3DS emulator.
- Not tested on the physical console. That check is the user's.

## Out of scope
Scrolling cameras, shops and currency, side quests, multiple endings.
