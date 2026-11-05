<div align="center">

<img src="docs/media/01_tytul.png" width="400" alt="Menuel and the Last Bell">

# Menuel and the Last Bell

**Natywna metroidvania na New 2DS XL / 3DS, napisana w C od zera**

![platforma](https://img.shields.io/badge/platforma-2DS%20XL%20%2F%203DS-7a5ca0)
![język](https://img.shields.io/badge/C-libctru-blue)
![klatki](https://img.shields.io/badge/60%20FPS-emulator-success)
![testy](https://img.shields.io/badge/przej%C5%9Bcie%20gry-bot-informational)

</div>

Dzwony Podziemnego Miasta umilkły, a wraz z nimi jego mieszkańcy zapominają, kim są.
W zakurzonym lofcie budzi się Menuel, mały strażnik w masce w kształcie latawca.
Bierze topór, schodzi w dół i po kolei budzi cztery dzwony, aż dociera do tego, kto je uciszył.

**40 pokoi · 4 krainy · 5 bossów · 4 zdolności · 4 odłamki zdrowia · osełka · mapa na dolnym ekranie · 9 utworów · zapis przy latarniach.**
Tekst w grze jest po angielsku. To nie jest ROM do emulatora: gra działa bezpośrednio na konsoli.

| Eksploracja | Hak nad Hanging Bells |
|:-:|:-:|
| ![](docs/media/walk_salt_mines.gif) | ![](docs/media/hook_hanging_bells.gif) |

| Salt Foreman | Silent Ringer |
|:-:|:-:|
| ![](docs/media/boss_foreman.gif) | ![](docs/media/boss_ringer.gif) |

## Pobierz i zainstaluj

Konsola musi mieć custom firmware (np. Luma3DS). Pliki są w [`release/`](release/) oraz w [Releases](../../releases).

| Plik | Jak użyć |
|---|---|
| [`Menuel.cia`](release/Menuel.cia) | Skopiuj na kartę SD i zainstaluj w FBI. Gra pojawi się na ekranie HOME. |
| [`Menuel.3dsx`](release/Menuel.3dsx) | Skopiuj do `/3ds/Menuel/` i uruchom z Homebrew Launchera. |

- **Zapis:** `sdmc:/3ds/Menuel/save.bin`. Obie wersje korzystają z tego samego pliku.
- **Dźwięk:** wymaga `/3ds/dspfirm.cdc`. Bez tego pliku gra działa, tylko bez dźwięku.

## Sterowanie

| Przycisk | Akcja |
|---|---|
| ←/→ lub Circle Pad | ruch |
| **A** | skok (przytrzymaj = wyżej), drugi skok z Cloak |
| **B** | topór |
| **R** | Rush, czyli zryw |
| **L** | Hook do pierścienia w zasięgu, z wciśniętym kierunkiem wybiera pierścień po tej stronie |
| **↓ + B** w powietrzu | Cleave, czyli cios w dół, który kruszy spękane podłogi |
| **X** (przytrzymaj na ziemi) | zamienia echo na zdrowie |
| **↓** | zeskok z cienkiej platformy |
| **↑** | rozmowa, tablica, latarnia (zapis i leczenie) |
| **START** | pauza |

## Świat

| Kraina | Pokoje | Zdolność | Boss |
|---|---|---|---|
| Salt Mines | 10 | Rush | Salt Foreman |
| Drowned Belfry | 11 | Hook | Rope Drowned |
| Rust Foundry | 11 | Cleave | Two-Headed Founder, The Anvil |
| Summit of Silence | 8 | Cloak | Silent Ringer |

Dolny ekran to stale widoczna mapa odwiedzonych pokoi, latarnie, bossowie, zdobyte zdolności i obudzone dzwony.

## Zrzuty ekranu

| | | |
|:-:|:-:|:-:|
| ![](docs/media/02_intro.png) | ![](docs/media/03_start.png) | ![](docs/media/04_rush_shrine.png) |
| Początek historii | Ringer's Loft | Rush Shrine |
| ![](docs/media/05_drowned_belfry.png) | ![](docs/media/06_rust_foundry.png) | ![](docs/media/07_summit.png) |
| Drowned Belfry | Rust Foundry | Summit of Silence |
| ![](docs/media/boss1_walka.png) | ![](docs/media/boss2_walka.png) | ![](docs/media/boss3_walka.png) |
| Salt Foreman | Rope Drowned | Two-Headed Founder |
| ![](docs/media/boss4_walka.png) | ![](docs/media/boss5_walka.png) | ![](docs/media/08_last_bell.png) |
| The Anvil | Silent Ringer | Ostatni dzwon |

## Budowanie

Wymagane: Python 3 z Pillow w `.venv`, gcc, podman (kompilator devkitARM działa w kontenerze) oraz `gh` do pobrania `makerom` i `bannertool`.

```sh
python3 -m venv .venv && .venv/bin/pip install pillow
make                            # assety i biblioteka testowa
make 3ds                        # build/Menuel.3dsx i build/Menuel.cia
.venv/bin/python tests/t_full.py   # pełne przejście gry
```

## Jak to działa

Cała gra to zwykły C bez zależności od sprzętu. Rysuje programowo do buforów RGB565, a warstwa konsoli tylko je wyświetla, czyta przyciski i gra dźwięk przez NDSP. Dzięki temu te same piksele powstają na konsoli i w testach.

```
assets/  art.py (grafika), world.py (pokoje i teksty), music.py, build.py (generator)
src/     game.c, player.c, enemy.c, boss.c, render.c, audio.c
         plat_3ds.c (konsola), host.c (biblioteka do testów)
tests/   t_world, t_boss, t_full, t_misc, make_media
tools/   budowanie .3dsx i .cia
docs/    spec.md, rysunek Menuela, zrzuty i gify
```

Grafika świata, wrogowie i muzyka są generowane skryptami w Pythonie. Ilustracja na ekranie tytułowym i ikona powstały z rysunku Menuela (`docs/menuel-reference.png`).

## Testy

Bot steruje grą tymi samymi przyciskami co gracz i korzysta z prawdziwej fizyki.

- **`t_world`** przeszukuje stany gry i sprawdza, że każdy cel i każdy przedmiot jest osiągalny w zaplanowanej kolejności, a bez danej zdolności nie da się ominąć jej blokady.
- **`t_boss`** walczy z każdym bossem przy zwykłych obrażeniach. Bot przewiduje ruchy dzięki migawkom stanu gry, więc jest sprawniejszy od człowieka.
- **`t_full`** przechodzi grę od ekranu tytułowego do napisów. Wrogowie są nieszkodliwi tylko na trasie między celami, bossowie zadają normalne obrażenia.
- **`t_misc`** sprawdza śmierć, zapis po restarcie, pauzę, dźwięk i renderowanie wszystkich pokoi.

`.3dsx` i instalacja `.cia` zostały sprawdzone w emulatorze Azahar. Gra nie była jeszcze uruchamiana na fizycznej konsoli, więc wydajność i dźwięk na sprzęcie są niepotwierdzone.
