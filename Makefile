# make            assets and the host test library
# make 3ds        build/Menuel.3dsx and build/Menuel.cia (devkitARM runs in a podman container)
PY = .venv/bin/python
CORE = src/game.c src/player.c src/enemy.c src/boss.c src/render.c src/audio.c src/gen_world.c
HDRS = src/core.h src/gen.h
IMG = docker.io/devkitpro/devkitarm:latest
TITLE = Menuel and the Last Bell
AUTHOR = Menuel project

all: build/libmenuel.so

build/assets.bin src/gen.h src/gen_world.c: assets/art.py assets/world.py assets/music.py assets/build.py docs/menuel-reference.png
	$(PY) assets/build.py

build/libmenuel.so: $(CORE) src/host.c $(HDRS) build/assets.bin
	gcc -O2 -Wall -Wno-unused-function -fPIC -shared -include stddef.h -o $@ $(CORE) src/host.c

3ds: build/assets.bin src/gen.h src/gen_world.c
	podman run --rm -v $(CURDIR):/w:Z -w /w $(IMG) sh tools/build3ds.sh "$(TITLE)" "$(AUTHOR)"
	tools/makecia.sh

clean:
	rm -f build/*.so build/*.3dsx build/*.cia build/*.elf build/*.smdh build/*.o src/gen.h src/gen_world.c build/assets.bin

.PHONY: all 3ds clean
