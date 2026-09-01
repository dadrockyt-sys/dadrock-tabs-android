#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
PRIVATE_ROOT="${V168_SPLITMYSONG_PRIVATE_ROOT:-$HOME/v168-splitmysong-private}"
SOURCE="${1:-$PRIVATE_ROOT/input/isolated-guitar.m4a}"
OUTPUT_DIR="${2:-$PRIVATE_ROOT/historical-support-generation}"
GENERATOR="$REPO_ROOT/validation/v168_splitmysong_diagnostic/generate_splitmysong_historical_support_v168.py"
HELPER="$REPO_ROOT/validation/v168_splitmysong_diagnostic/historical_shared_support_v168.py"
PREREG="$REPO_ROOT/debug/v168-splitmysong-diagnostic/historical-shared-support-neighborhood-preregistration.json"

EXPECTED_GENERATOR_BLOB="5adfb45a69f922dc409f35350683935df518bf07"
EXPECTED_HELPER_BLOB="c9b5cc1bc4076be77780d64f73d53f2a7083f94f"
EXPECTED_PREREG_BLOB="f34661e2d67f9f1c541b80ac01af2c6ea82e2159"

git config --global --add safe.directory "$REPO_ROOT"

printf 'SplitMySong one-shot historical shared-support generation\n'
printf 'Repository: %s\n' "$REPO_ROOT"
printf 'Private source: %s\n' "$SOURCE"
printf 'Private output: %s\n\n' "$OUTPUT_DIR"

if [ "$(git -C "$REPO_ROOT" branch --show-current)" != "v143-contextual-prune-lobo" ]; then
  printf 'ERROR: wrong branch.\n' >&2
  exit 1
fi
if [ -n "$(git -C "$REPO_ROOT" status --porcelain --untracked-files=no)" ]; then
  printf 'ERROR: tracked repository changes present.\n' >&2
  exit 1
fi

for spec in \
  "$GENERATOR:$EXPECTED_GENERATOR_BLOB" \
  "$HELPER:$EXPECTED_HELPER_BLOB" \
  "$PREREG:$EXPECTED_PREREG_BLOB"; do
  path="${spec%%:*}"
  expected="${spec##*:}"
  observed="$(git -C "$REPO_ROOT" hash-object "$path")"
  if [ "$observed" != "$expected" ]; then
    printf 'ERROR: frozen Git blob mismatch: %s observed=%s expected=%s\n' "$path" "$observed" "$expected" >&2
    exit 1
  fi
done

for path in \
  "$SOURCE" \
  "$PRIVATE_ROOT/input-normalized.wav" \
  "$PRIVATE_ROOT/arm-preflight-receipt.json" \
  "$PRIVATE_ROOT/environment-receipt.json" \
  "$PRIVATE_ROOT/ffmpeg-normalizer-receipt.json"; do
  if [ ! -f "$path" ]; then
    printf 'ERROR: required frozen private input missing: %s\n' "$path" >&2
    exit 1
  fi
done

for name in \
  splitmysong-historical-support-attempt.marker \
  splitmysong-basic-pitch-observation.json \
  splitmysong-historical-support-neighborhood-gate.json \
  splitmysong-i005-candidate.json \
  splitmysong-generation-receipt.json \
  splitmysong-candidate-freeze.json; do
  if [ -e "$OUTPUT_DIR/$name" ]; then
    printf 'ERROR: one-shot output/attempt already exists: %s\n' "$OUTPUT_DIR/$name" >&2
    exit 1
  fi
done

set +e
python "$GENERATOR" \
  --repo-root "$REPO_ROOT" \
  --source "$SOURCE" \
  --normalized-guitar "$PRIVATE_ROOT/input-normalized.wav" \
  --arm-receipt "$PRIVATE_ROOT/arm-preflight-receipt.json" \
  --environment-receipt "$PRIVATE_ROOT/environment-receipt.json" \
  --ffmpeg-receipt "$PRIVATE_ROOT/ffmpeg-normalizer-receipt.json" \
  --output-dir "$OUTPUT_DIR"
rc=$?
set -e

if [ "$rc" -eq 2 ]; then
  printf '\nNEIGHBORHOOD GATE FAILED CLOSED — NO CANDIDATE GENERATED\n'
  sha256sum \
    "$OUTPUT_DIR/splitmysong-basic-pitch-observation.json" \
    "$OUTPUT_DIR/splitmysong-historical-support-neighborhood-gate.json"
  printf '\nSTOP: do not rerun the one-shot observation and do not run a scorer. Checkpoint these hashes.\n'
  exit 2
fi
if [ "$rc" -ne 0 ]; then
  printf '\nERROR: one-shot generator failed with exit %s. The attempt marker is persistent; do not rerun until the failure is diagnosed.\n' "$rc" >&2
  exit "$rc"
fi

printf '\nPRIVATE REFERENCE-BLIND FREEZE FILES\n'
sha256sum \
  "$OUTPUT_DIR/splitmysong-basic-pitch-observation.json" \
  "$OUTPUT_DIR/splitmysong-historical-support-neighborhood-gate.json" \
  "$OUTPUT_DIR/splitmysong-i005-candidate.json" \
  "$OUTPUT_DIR/splitmysong-generation-receipt.json" \
  "$OUTPUT_DIR/splitmysong-candidate-freeze.json"
printf '\nSTOP: do not run a scorer until all five hashes are checkpointed.\n'
