#!/bin/zsh
# Rebuild the three Stonehurst proof variants. Personalities are the only per-variant input besides lead/palette photos.
set -e
cd "$(dirname "$0")"
python3 build.py content/stonehurst.json --variant a --out ../previews/stonehurst-variants/a --personality formality=85,scale=70,era=55,density=70,temperature=65,voice=80 --lead greenhouse --palette-photos greenhouse,reception,bamboo,stonepath "$@"
python3 build.py content/stonehurst.json --variant b --out ../previews/stonehurst-variants/b --personality formality=30,scale=45,era=35,density=25,temperature=15,voice=25 --lead barn --palette-photos barn,flower,terrace,bungalow "$@"
python3 build.py content/stonehurst.json --variant c --out ../previews/stonehurst-variants/c --personality formality=70,scale=55,era=95,density=92,temperature=55,voice=92 --lead hero --palette-photos hero,bamboo,greenhouse,stonepath "$@"
