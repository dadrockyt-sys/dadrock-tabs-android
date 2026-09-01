#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
OUT_ROOT="${1:-$HOME/v168-splitmysong-private}"
CONTEXT_DIR="$OUT_ROOT/historical-context"
PREP="$REPO_ROOT/validation/v168_splitmysong_diagnostic/prepare_historical_context_v168.py"
EXPECTED_PREP_BLOB="b93d8e671858c8b433c6e6645dc9f0e826429ed3"

git config --global --add safe.directory "$REPO_ROOT"
cd "$REPO_ROOT"

test "$(git branch --show-current)" = "v143-contextual-prune-lobo"
test "$(git hash-object "$PREP")" = "$EXPECTED_PREP_BLOB"

if [ -e "$CONTEXT_DIR" ] || [ -e "$CONTEXT_DIR.building" ]; then
  echo "Historical context output/build directory already exists; refusing overwrite:" >&2
  echo "  $CONTEXT_DIR" >&2
  echo "  $CONTEXT_DIR.building" >&2
  exit 1
fi

bash "$REPO_ROOT/validation/v168_splitmysong_diagnostic/codespace_status.sh"

python "$PREP" \
  --repo-root "$REPO_ROOT" \
  --output-dir "$CONTEXT_DIR"

printf '\nHistorical context receipt: %s\n' "$CONTEXT_DIR/context-receipt.json"
printf 'Historical context receipt SHA256: '
sha256sum "$CONTEXT_DIR/context-receipt.json" | awk '{print $1}'
printf '\nDo not git-add or commit the private historical context directory.\n'
