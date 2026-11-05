#!/bin/sh
# Runs inside the devkitARM container, from the project root.
set -e
export PATH=/opt/devkitpro/devkitARM/bin:/opt/devkitpro/tools/bin:$PATH
DKP=/opt/devkitpro
ARCH="-march=armv6k -mtune=mpcore -mfloat-abi=hard -mtp=soft"
CFLAGS="-O2 -g -Wall -Wno-unused-function -mword-relocations -ffunction-sections $ARCH -D__3DS__ -I$DKP/libctru/include -Isrc -include stddef.h"
mkdir -p build/obj build/romfs
cp build/assets.bin build/romfs/assets.bin
OBJS=""
for f in game player enemy boss render audio gen_world plat_3ds; do
    arm-none-eabi-gcc $CFLAGS -c src/$f.c -o build/obj/$f.o
    OBJS="$OBJS build/obj/$f.o"
done
arm-none-eabi-gcc -specs=3dsx.specs -g $ARCH -Wl,--gc-sections -o build/Manuel.elf $OBJS -L$DKP/libctru/lib -lctru -lm
smdhtool --create "$1" "A small warden wakes the bells." "$2" build/icon.png build/Manuel.smdh
3dsxtool build/Manuel.elf build/Manuel.3dsx --smdh=build/Manuel.smdh --romfs=build/romfs
# benchmark build, for tests only
arm-none-eabi-gcc $CFLAGS -DBENCH -c src/plat_3ds.c -o build/obj/plat_bench.o
arm-none-eabi-gcc -specs=3dsx.specs -g $ARCH -Wl,--gc-sections -o build/ManuelBench.elf $(echo $OBJS | sed 's#build/obj/plat_3ds.o#build/obj/plat_bench.o#') -L$DKP/libctru/lib -lctru -lm
3dsxtool build/ManuelBench.elf build/ManuelBench.3dsx --smdh=build/Manuel.smdh --romfs=build/romfs
arm-none-eabi-size build/Manuel.elf
ls -la build/Manuel.3dsx build/Manuel.elf
