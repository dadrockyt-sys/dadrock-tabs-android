#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
PRIVATE_ROOT="${V168_SPLITMYSONG_PRIVATE_ROOT:-$HOME/v168-splitmysong-private}"
SOURCE="${1:-$PRIVATE_ROOT/input/isolated-guitar.m4a}"
OUTPUT_DIR="${2:-$PRIVATE_ROOT/generation}"

git config --global --add safe.directory "$REPO_ROOT"

printf 'SplitMySong one-shot reference-blind candidate generation\n'
printf 'Repository: %s\n' "$REPO_ROOT"
printf 'Private source: %s\n' "$SOURCE"
printf 'Private output: %s\n\n' "$OUTPUT_DIR"

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

if [ -e "$OUTPUT_DIR/splitmysong-generation-attempt.marker" ] || \
   [ -e "$OUTPUT_DIR/splitmysong-i005-candidate.json" ] || \
   [ -e "$OUTPUT_DIR/splitmysong-generation-receipt.json" ] || \
   [ -e "$OUTPUT_DIR/splitmysong-candidate-freeze.json" ]; then
  printf 'ERROR: one-shot generation output/attempt already exists in %s; rerun forbidden.\n' "$OUTPUT_DIR" >&2
  exit 1
fi

python "$REPO_ROOT/validation/v168_splitmysong_diagnostic/generate_splitmysong_candidate_v168.py" \
  --repo-root "$REPO_ROOT" \
  --source "$SOURCE" \
  --normalized-guitar "$PRIVATE_ROOT/input-normalized.wav" \
  --arm-receipt "$PRIVATE_ROOT/arm-preflight-receipt.json" \
  --environment-receipt "$PRIVATE_ROOT/environment-receipt.json" \
  --ffmpeg-receipt "$PRIVATE_ROOT/ffmpeg-normalizer-receipt.json" \
  --output-dir "$OUTPUT_DIR"

printf '\nPRIVATE CANDIDATE FREEZE FILES\n'
sha256sum \
  "$OUTPUT_DIR/splitmysong-i005-candidate.json" \
  "$OUTPUT_DIR/splitmysong-generation-receipt.json" \
  "$OUTPUT_DIR/splitmysong-candidate-freeze.json"
printf '\nSTOP: do not run a scorer until these hashes are checkpointed.\n'
