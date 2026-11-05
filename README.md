<div align="center">

<img src="docs/media/01_tytul.png" width="400" alt="Manuel and the Last Bell">

# Manuel and the Last Bell

**Natywna metroidvania na New 2DS XL / 3DS, napisana w C od zera**

![platforma](https://img.shields.io/badge/platforma-2DS%20XL%20%2F%203DS-7a5ca0)
![język](https://img.shields.io/badge/C-libctru-blue)
![klatki](https://img.shields.io/badge/60%20FPS-emulator-success)
![testy](https://img.shields.io/badge/przej%C5%9Bcie%20gry-bot-informational)

</div>

Dzwony Podziemnego Miasta umilkły, a wraz z nimi jego mieszkańcy zapominają, kim są.
W zakurzonym lofcie budzi się Manuel, mały strażnik w masce w kształcie latawca.
Bierze topór, schodzi w dół i po kolei budzi cztery dzwony, aż dociera do tego, kto je uciszył.

**40 pokoi na dwa ekrany · 4 krainy · 5 bossów · 4 zdolności · 4 odłamki zdrowia · osełka · 9 utworów · zapis przy latarniach.**
Każdy pokój obejmuje oba ekrany: Manuel skacze i spada z górnego na dolny, a bossowie atakują przez oba. Tekst w grze jest po angielsku. To nie jest ROM do emulatora: gra działa bezpośrednio na konsoli.

| Eksploracja na dwóch ekranach | Hak nad Hanging Bells |
|:-:|:-:|
| ![](docs/media/walk_salt_mines.gif) | ![](docs/media/hook_hanging_bells.gif) |

| Rope Drowned spada z góry | Silent Ringer |
|:-:|:-:|
| ![](docs/media/boss_rope.gif) | ![](docs/media/boss_ringer.gif) |

## Pobierz i zainstaluj

Konsola musi mieć custom firmware (np. Luma3DS). Pliki są w [`release/`](release/) oraz w [Releases](../../releases).

| Plik | Jak użyć |
|---|---|
| [`Manuel.cia`](release/Manuel.cia) | Skopiuj na kartę SD i zainstaluj w FBI. Gra pojawi się na ekranie HOME. |
| [`Manuel.3dsx`](release/Manuel.3dsx) | Skopiuj do `/3ds/Manuel/` i uruchom z Homebrew Launchera. |

- **Zapis:** `sdmc:/3ds/Manuel/save.bin`. Obie wersje korzystają z tego samego pliku.
- **Dźwięk:** wymaga `/3ds/dspfirm.cdc`. Bez tego pliku gra działa, tylko bez dźwięku.

## Sterowanie

| Przycisk | Akcja |
|---|---|
| ←/→ lub Circle Pad | ruch |
| **A** | skok (przytrzymaj = wyżej), drugi skok z Cloak |
| **B** | topór |
| **R** | Rush, czyli zryw |
| **L** lub dotknięcie pierścienia na dolnym ekranie | Hook, z wciśniętym kierunkiem wybiera pierścień po tej stronie |
| **↓ + B** w powietrzu | Cleave, czyli cios w dół, który kruszy spękane podłogi |
| **X** (przytrzymaj na ziemi) | zamienia echo na zdrowie |
| **↓** | zeskok z cienkiej platformy |
| **↑** | rozmowa, tablica, latarnia (zapis i leczenie) |
| **START** | pauza, mapa i ekwipunek na dolnym ekranie |
| **SELECT** | licznik wydajności na dolnym ekranie |

## Świat

| Kraina | Pokoje | Zdolność | Boss |
|---|---|---|---|
| Salt Mines | 10 | Rush | Salt Foreman |
| Drowned Belfry | 11 | Hook | Rope Drowned |
| Rust Foundry | 11 | Cleave | Two-Headed Founder, The Anvil |
| Summit of Silence | 8 | Cloak | Silent Ringer |

Górny ekran pokazuje pełną szerokość pokoju, a dolny jego niższą część. Serca podążają za Manuelem na ekran, na którym jest, a dialogi pojawiają się na tym drugim, żeby niczego nie zasłaniać. Przycisk START wyświetla na dolnym ekranie mapę odwiedzonych pokoi, latarnie, bossów, zdolności i dzwony.

## Zrzuty ekranu

| | | |
|:-:|:-:|:-:|
| ![](docs/media/03_start.png) | ![](docs/media/05_drowned_belfry.png) | ![](docs/media/06_rust_foundry.png) |
| Ringer's Loft | Drowned Belfry | Rust Foundry |
| ![](docs/media/07_summit.png) | ![](docs/media/10_pauza_mapa.png) | ![](docs/media/02_intro.png) |
| Summit of Silence | Pauza i mapa | Dialog na wolnym ekranie |
| ![](docs/media/boss1_walka.png) | ![](docs/media/boss2_walka.png) | ![](docs/media/boss3_walka.png) |
| Salt Foreman | Rope Drowned | Two-Headed Founder |
| ![](docs/media/boss4_walka.png) | ![](docs/media/boss5_walka.png) | ![](docs/media/08_last_bell.png) |
| The Anvil | Silent Ringer | Ostatni dzwon |

## Budowanie

Wymagane: Python 3 w `.venv`, czcionki Noto Serif, gcc, podman (kompilator devkitARM działa w kontenerze) oraz `gh` do pobrania `makerom` i `bannertool`.

```sh
python3 -m venv .venv && .venv/bin/python -m pip install pillow numpy scipy lz4
make                            # assety i biblioteka testowa
make 3ds                        # build/Manuel.3dsx i build/Manuel.cia
.venv/bin/python tests/t_full.py   # pełne przejście gry
```

## Jak to działa

Cała gra to zwykły C bez zależności od sprzętu. Rysuje programowo do buforów RGB565 z półprzezroczystością, a warstwa konsoli tylko je wyświetla, czyta przyciski i ekran dotykowy i gra dźwięk przez NDSP. Dzięki temu te same piksele powstają na konsoli i w testach.

```
assets/  ink.py (silnik rysunku), art_manuel.py, art.py (postacie), bake.py (malowane tła), world.py (pokoje i teksty), music.py, build.py
src/     game.c, player.c, enemy.c, boss.c, render.c, audio.c
         plat_3ds.c (konsola), host.c (biblioteka do testów)
tests/   t_world, t_boss, t_full, t_misc, make_media
tools/   budowanie .3dsx i .cia
docs/    spec.md, rysunek Manuela, zrzuty i gify
```

Postacie powstają w małym silniku do tuszowania (`assets/ink.py`): gładkie krzywe, gruba kreska na obrysie, cienka w środku i cieniowanie z jednego kierunku światła. Manuel ma 62 klatki, m.in. 8 klatek spoczynku z mrugnięciem, 10 klatek biegu, dwa różne zamachy ze smugą, przygotowanie i lądowanie ze ściskaniem, a także śmierć. Każdy szpic peleryny porusza się z własnym opóźnieniem. Wrogowie mają po 6 klatek, bossowie po 12, postacie mówiące mają portrety w dialogach, a w grze dochodzą duchy zrywu, kurz, fale uderzeniowe i cienie. Każdy pokój jest malowany przy budowaniu (tekstury, światło, cienie, dekoracje) i przechowywany w postaci skompresowanej LZ4. Muzyka też powstaje ze skryptu. Wygląd Manuela opiera się na rysunku `docs/manuel-reference.png`. Okładka (`assets/cover.py`) to malowana scena na oba ekrany, w której Manuel i dzwon są animowani.

## Testy

Bot steruje grą tymi samymi przyciskami co gracz i korzysta z prawdziwej fizyki.

- **`t_world`** przeszukuje stany gry i sprawdza, że każdy cel i każdy przedmiot jest osiągalny w zaplanowanej kolejności, a bez danej zdolności nie da się ominąć jej blokady.
- **`t_boss`** walczy z każdym bossem przy zwykłych obrażeniach. Bot przewiduje ruchy dzięki migawkom stanu gry, więc jest sprawniejszy od człowieka.
- **`t_full`** przechodzi grę od ekranu tytułowego do napisów. Wrogowie są nieszkodliwi tylko na trasie między celami, bossowie zadają normalne obrażenia.
- **`t_misc`** sprawdza śmierć, zapis po restarcie, pauzę, dźwięk i renderowanie wszystkich pokoi.

- **`tests/fuzz.c`** gra losowymi przyciskami we wszystkich pokojach pod ASan i UBSan, sprawdza utknięcia w ścianach, wyjście poza ekran i uszkodzone pliki zapisu.

`.3dsx` oraz `.cia`, zainstalowany i uruchomiony jako tytuł, zostały sprawdzone w emulatorze Azahar. `tools/check_cia.py` przy każdym budowaniu sprawdza nagłówek `.cia`. Gra nie była jeszcze uruchamiana na fizycznej konsoli, więc wydajność i dźwięk na sprzęcie są niepotwierdzone.

## Wydajność

Pomiar kodu ARM w emulatorze Azahar, 240 klatek w każdym z 40 pokoi, budżet klatki to 16,67 ms. Pełny wynik: [`docs/perf-azahar.txt`](docs/perf-azahar.txt).

| Co | Średnio | Najwięcej |
|---|---:|---:|
| Logika i rysowanie | 3,5 ms | ok. 21 ms (rozpakowanie pokoju, w czasie wygaszenia ekranu) |
| Kopiowanie na oba ekrany | 3,4 ms | 3,4 ms |
| Dźwięk | 0,4 ms | 1,5 ms |
| Zapis na kartę (tylko latarnia i przedmioty) | | ok. 90 ms |

Emulator nie odwzorowuje dokładnie czasów pamięci i karty SD, więc to szacunek, a nie wynik ze sprzętu. Na konsoli **SELECT** pokazuje na dolnym ekranie `logika/cała klatka max najgorsza late liczba spóźnionych klatek` w milisekundach. Wynik nad 16,6 ms oznacza spóźnioną klatkę.

Fuzz (600 tys. klatek): 0 błędów pamięci, 0 klatek w ścianie, 0 wyjść poza ekran i 0 z 28 uszkodzonych zapisów przyjętych przez grę.
