#!/bin/sh
# Wraps build/Manuel.elf into an installable CIA. Downloads makerom and bannertool once.
set -e
cd "$(dirname "$0")/.."
T=tools/cia
mkdir -p "$T"
if [ ! -x "$T/makerom" ]; then
    gh release download makerom-v0.19.0 -R 3DSGuy/Project_CTR -D "$T" --clobber -p 'makerom-v0.19.0-ubuntu_x86_64.zip'
    python3 -I -m zipfile -e "$T/makerom-v0.19.0-ubuntu_x86_64.zip" "$T/"
    chmod +x "$T/makerom"
fi
if [ ! -x "$T/bannertool" ]; then
    gh release download 1.2.3 -R carstene1ns/3ds-bannertool -D "$T" --clobber -p 'bannertool-1.2.3-linux.tar.gz'
    tar -xzf "$T/bannertool-1.2.3-linux.tar.gz" -C "$T"
    B=$(find "$T" -type f -name bannertool | head -1)
    [ "$B" = "$T/bannertool" ] || cp "$B" "$T/bannertool"
    chmod +x "$T/bannertool"
fi
.venv/bin/python tools/make_wav.py build/banner.wav
"$T/bannertool" makebanner -i build/banner.png -a build/banner.wav -o build/banner.bnr
"$T/bannertool" makesmdh -s "Manuel and the Last Bell" -l "Manuel and the Last Bell" -p "Manuel project" -i build/icon.png -o build/icon.icn
"$T/makerom" -f cia -o build/Manuel.cia -rsf tools/manuel.rsf -target t -exefslogo -elf build/Manuel.elf -icon build/icon.icn -banner build/banner.bnr
python3 -I tools/check_cia.py build/Manuel.cia
ls -la build/Manuel.cia
