#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"

git config --global --add safe.directory "$REPO_ROOT"
cd "$REPO_ROOT"

BRANCH="$(git branch --show-current)"
printf 'Branch: %s\n' "$BRANCH"
if [ "$BRANCH" != "v143-contextual-prune-lobo" ]; then
  echo "FAIL: wrong branch" >&2
  exit 1
fi

printf 'HEAD: %s\n' "$(git rev-parse HEAD)"
printf 'Python: %s\n' "$(python --version 2>&1)"

if [ "$(python - <<'PY'
import platform
print(platform.python_version())
PY
)" != "3.10.21" ]; then
  echo "FAIL: this Codespace is not using the frozen V168 CPU devcontainer." >&2
  echo "Pull the branch and rebuild the Codespace container, then rerun this command." >&2
  exit 1
fi

OUT="$HOME/v168-splitmysong-private"
mkdir -p "$OUT"
chmod 700 "$OUT"

python validation/v168_splitmysong_diagnostic/verify_ffmpeg_normalizer_v168.py \
  --receipt "$OUT/ffmpeg-normalizer-receipt.json"

python validation/v168_splitmysong_diagnostic/verify_environment_v168.py \
  --repo-root . \
  --receipt "$OUT/environment-receipt.json"

printf '\nCODESPACE CPU ENVIRONMENT PASS\n'
printf 'Environment receipt: %s\n' "$OUT/environment-receipt.json"
printf 'Environment receipt SHA256: '
sha256sum "$OUT/environment-receipt.json" | awk '{print $1}'
printf 'FFmpeg receipt: %s\n' "$OUT/ffmpeg-normalizer-receipt.json"
printf 'FFmpeg receipt SHA256: '
sha256sum "$OUT/ffmpeg-normalizer-receipt.json" | awk '{print $1}'
printf '\nNext: place the frozen SplitMySong .m4a only in the Codespace private filesystem, then run run_private_arm_preflight.sh against that path.\n'
