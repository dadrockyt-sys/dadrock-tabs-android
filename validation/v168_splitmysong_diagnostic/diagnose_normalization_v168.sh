#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 /private/path/to/isolated-guitar.m4a" >&2
  exit 2
fi

SOURCE="$1"
EXPECTED_SOURCE_SHA="6601b8d01cbbbe6b6e70d9ec0ca3c15d17873c78e62ae4acdc258c96f168e3c9"
EXPECTED_FFMPEG715_WAV_SHA="fdb0578d71f77c150e7fe66766a03953be55e7028fef4c24dc777416f2e7ff4f"
EXPECTED_FFMPEG715_PCM_SHA="2c5dc122c2d37e562d90a13eac0c6dcac534ad7ee562fecd154b98e9124f63dd"
OUT_DIR="$HOME/v168-splitmysong-private/normalization-diagnostic"
OUT_WAV="$OUT_DIR/system-ffmpeg-normalized.wav"

mkdir -p "$OUT_DIR"
chmod 700 "$HOME/v168-splitmysong-private" "$OUT_DIR"

if [ ! -f "$SOURCE" ]; then
  echo "FAIL: source file missing: $SOURCE" >&2
  exit 1
fi

SOURCE_SHA="$(sha256sum "$SOURCE" | awk '{print $1}')"
printf 'Source SHA256: %s\n' "$SOURCE_SHA"
if [ "$SOURCE_SHA" != "$EXPECTED_SOURCE_SHA" ]; then
  echo "FAIL: source SHA256 mismatch" >&2
  exit 1
fi

printf 'System FFmpeg: '
ffmpeg -version | head -n 1

ffmpeg -hide_banner -loglevel error -y \
  -i "$SOURCE" -map 0:a:0 -vn -ar 22050 -ac 1 -c:a pcm_s16le "$OUT_WAV"

WAV_SHA="$(sha256sum "$OUT_WAV" | awk '{print $1}')"
WAV_BYTES="$(stat -c '%s' "$OUT_WAV")"
PCM_SHA_FROM_WAV="$(ffmpeg -hide_banner -loglevel error -i "$OUT_WAV" -f s16le -acodec pcm_s16le - | sha256sum | awk '{print $1}')"
PCM_SHA_DIRECT="$(ffmpeg -hide_banner -loglevel error -i "$SOURCE" -map 0:a:0 -vn -ar 22050 -ac 1 -f s16le -acodec pcm_s16le - | sha256sum | awk '{print $1}')"

printf 'Generated WAV SHA256: %s\n' "$WAV_SHA"
printf 'Generated WAV bytes: %s\n' "$WAV_BYTES"
printf 'PCM SHA256 from WAV: %s\n' "$PCM_SHA_FROM_WAV"
printf 'PCM SHA256 direct from source: %s\n' "$PCM_SHA_DIRECT"
printf 'Frozen FFmpeg-7.1.5 WAV SHA256: %s\n' "$EXPECTED_FFMPEG715_WAV_SHA"
printf 'Frozen FFmpeg-7.1.5 PCM SHA256: %s\n' "$EXPECTED_FFMPEG715_PCM_SHA"

if [ "$PCM_SHA_FROM_WAV" != "$PCM_SHA_DIRECT" ]; then
  echo 'DIAGNOSIS FAIL: generated WAV PCM differs from direct PCM decode.' >&2
  exit 1
fi

if [ "$PCM_SHA_DIRECT" = "$EXPECTED_FFMPEG715_PCM_SHA" ]; then
  if [ "$WAV_SHA" = "$EXPECTED_FFMPEG715_WAV_SHA" ]; then
    echo 'DIAGNOSIS: EXACT_MATCH — WAV bytes and PCM samples match the frozen FFmpeg 7.1.5 normalization.'
  else
    echo 'DIAGNOSIS: WRAPPER_ONLY_DIFFERENCE — PCM samples match; only WAV container/header bytes differ.'
  fi
else
  echo 'DIAGNOSIS: PCM_DIFFERENCE — this FFmpeg build produces different normalized PCM samples.'
fi

printf 'Private diagnostic WAV: %s\n' "$OUT_WAV"
printf 'No inference, scorer, or reference access occurred.\n'
