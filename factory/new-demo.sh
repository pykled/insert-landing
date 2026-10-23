#!/bin/zsh
# Insert demo pipeline: venue URL -> verified content file + photos -> unique site -> strict QA -> private preview.
#
#   factory/new-demo.sh <venue-url> <slug>                    run from the start; pauses for the human review
#   factory/new-demo.sh <venue-url> <slug> --from <stage>     resume at intake|review|validate|build|qa|preview
#   ... [--to <stage>]                                         stop after that stage
#
# Stages (each timed; one line per stage appended to factory/data/timings.log):
#   1 intake    factory/intake/intake.py -> content/<slug>.draft.json, <slug>.intake-report.md, content/photos/<slug>/
#   2 review    PAUSE. A human (or a reviewing agent) turns the draft into content/<slug>.json against the live pages:
#               every fact cited, nothing unverifiable, short paraphrases only, 8-14 photos named with curate.py, alt +
#               captions written from what the photo shows, no people photo as lead, vibe words confirmed (INTAKE.md).
#   3 validate  lib/schema.py content/<slug>.json (must be 0 errors) + intake/score.py (dialect table)
#   4 build     build.py --dialect auto (the scorer picks the dialect; the registry guard keeps it unlike other sites)
#   5 qa        qa.py --strict against a local http.server on :4821, then preview.py --mark-qa-strict
#   6 preview   preview.py stages index.html + images under private-previews/<token>/demos/<slug>/ (local only)
#
# Env: LEAD=<photo name> (default: hero), VARIANT (default: demo), REGISTER=1 to add the build to data/registry.json,
#      BUILD_ARGS="..." extra build.py flags, NONINTERACTIVE=1 to stop at the review pause instead of waiting.
# Deploying the staged preview is a separate, approved step (never done here).
set -e
FACTORY="$(cd "$(dirname "$0")" && pwd)"
REPO="$(dirname "$FACTORY")"
URL="$1"; SLUG="$2"; shift 2 || { echo "usage: factory/new-demo.sh <venue-url> <slug> [--from stage]"; exit 2; }
FROM=intake; TO=preview
while (( $# )); do
  case "$1" in --from) FROM="$2"; shift 2;; --to) TO="$2"; shift 2;; *) echo "unknown option $1"; exit 2;; esac
done
[[ "$SLUG" =~ '^[a-z0-9][a-z0-9-]*$' ]] || { echo "slug must be lowercase letters, digits, hyphens"; exit 2; }
CONTENT="$FACTORY/content/$SLUG.json"
OUT="$REPO/.factory-check/demos/$SLUG"
LOG="$FACTORY/data/timings.log"
STAGES=(intake review validate build qa preview)
start_idx=${STAGES[(i)$FROM]}
end_idx=${STAGES[(i)$TO]}
(( start_idx <= ${#STAGES} && end_idx <= ${#STAGES} )) || { echo "unknown stage (one of: $STAGES)"; exit 2; }

t0=0
begin() { echo "\n== $1 =="; t0=$(date +%s); }
finish() { local s=$(( $(date +%s) - t0 )); printf '%s\t%s\t%s\t%ss\t%s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$SLUG" "$1" "$s" "${2:-}" >> "$LOG"; echo "-- $1: ${s}s"; }
run() { local i=${STAGES[(i)$1]}; (( i >= start_idx && i <= end_idx )); }

if run intake; then
  begin intake
  python3 "$FACTORY/intake/intake.py" "$URL" --slug "$SLUG"
  finish intake automated
fi

if run review; then
  begin review
  echo "Review now: factory/content/$SLUG.intake-report.md and $SLUG.draft.json -> write factory/content/$SLUG.json"
  echo "  contact sheets: python3 factory/intake/curate.py $SLUG --sheet"
  echo "  name photos:    python3 factory/intake/curate.py $SLUG hero=p03 barn=p07 ..."
  if [[ -n "$NONINTERACTIVE" ]]; then
    echo "Paused. Resume with: factory/new-demo.sh $URL $SLUG --from validate"; exit 0
  fi
  read "?Press Enter when factory/content/$SLUG.json is written (Ctrl-C to stop) "
  finish review judgement
fi

if run validate; then
  begin validate
  [[ -f "$CONTENT" ]] || { echo "missing $CONTENT (the reviewed file, not the draft)"; exit 3; }
  python3 "$FACTORY/lib/schema.py" "$CONTENT"
  python3 "$FACTORY/intake/score.py" "$CONTENT" ${LEAD:+--lead $LEAD}
  finish validate automated
fi

if run build; then
  begin build
  cd "$FACTORY"
  set +e
  python3 build.py "content/$SLUG.json" --variant "${VARIANT:-demo}" --out "$OUT" --lead "${LEAD:-hero}" ${REGISTER:+--register} ${=BUILD_ARGS}
  rc=$?
  set -e
  cd "$REPO"
  (( rc == 0 )) || { finish build "automated FAIL rc=$rc"; echo "Build stopped (a guard REFUSE means too close to a registered site: change --force/--lead via BUILD_ARGS/LEAD)"; exit 5; }
  finish build automated
fi

if run qa; then
  begin qa
  started=""
  if ! curl -s -o /dev/null "http://localhost:4821/"; then
    (cd "$REPO" && python3 -m http.server 4821 >/dev/null 2>&1) &
    started=$!; sleep 1
  fi
  set +e
  python3 "$FACTORY/qa.py" "$OUT" --strict
  rc=$?
  set -e
  [[ -n "$started" ]] && kill $started 2>/dev/null
  (( rc == 0 )) || { finish qa "automated FAIL"; echo "QA failed: fix and resume with --from build or --from qa"; exit 4; }
  python3 "$FACTORY/preview.py" "$OUT" --mark-qa-strict
  finish qa automated
fi

if run preview; then
  begin preview
  python3 "$FACTORY/preview.py" "$OUT" --name "$SLUG" --group demos
  finish preview automated
fi
echo "\nTimings appended to factory/data/timings.log"
