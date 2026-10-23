#!/usr/bin/env bash
# Promote the staged /venues rehaul to the live page file. Run only after Dillon approves.
# Backs up the current venues.html to scripts/backups/venues.prev.html (scripts/ is excluded from deploys),
# then copies the private preview over venues.html. Deploy separately (insert-local-smoke skill, step 4).
set -euo pipefail
cd "$(dirname "$0")/.."
SRC=private-previews/2d32be7dda6d361dd89ffdfd/venues-rehaul/index.html
[ -f "$SRC" ] || { echo "missing $SRC" >&2; exit 1; }
mkdir -p scripts/backups
cp venues.html scripts/backups/venues.prev.html
cp "$SRC" venues.html
echo "venues.html replaced (backup: scripts/backups/venues.prev.html)."
echo "Rollback: cp scripts/backups/venues.prev.html venues.html"
