#!/bin/zsh
# Rebuild the three Stonehurst proof variants. Personalities are the only per-variant input besides lead/palette photos.
# They predate the dialect layer (stage 2A) and build with --dialect none so their choices stay exactly as published.
# FACTORY_OUT redirects the output (default ../previews/stonehurst-variants), e.g. for a regression check:
#   FACTORY_OUT=../.factory-check/stonehurst-variants ./build-all.sh
set -e
cd "$(dirname "$0")"
OUT=${FACTORY_OUT:-../previews/stonehurst-variants}
python3 build.py content/stonehurst.json --variant a --out $OUT/a --dialect none --personality formality=85,scale=70,era=55,density=70,temperature=65,voice=80 --lead greenhouse --palette-photos greenhouse,reception,bamboo,stonepath "$@"
python3 build.py content/stonehurst.json --variant b --out $OUT/b --dialect none --personality formality=30,scale=45,era=35,density=25,temperature=15,voice=25 --lead barn --palette-photos barn,flower,terrace,bungalow "$@"
python3 build.py content/stonehurst.json --variant c --out $OUT/c --dialect none --personality formality=70,scale=55,era=95,density=92,temperature=55,voice=92 --lead hero --palette-photos hero,bamboo,greenhouse,stonepath "$@"
