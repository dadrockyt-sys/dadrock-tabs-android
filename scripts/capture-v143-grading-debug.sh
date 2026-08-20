#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
OUT="$ROOT/debug/v143-grading"
SRC="/tmp/last_grade_cmd.txt"

mkdir -p "$OUT/local-inputs"

if [[ ! -f "$SRC" ]]; then
  echo "Missing $SRC. Re-run the grading command first so the temporary grader exists." >&2
  exit 1
fi

cp "$SRC" "$OUT/last_grade_cmd.py"

{
  echo "branch=$(git branch --show-current)"
  echo "head=$(git rev-parse HEAD)"
  echo "captured_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "git status --short"
  git status --short
} > "$OUT/repo-state.txt"

python - "$ROOT" "$SRC" "$OUT" <<'PY'
from pathlib import Path
import re
import shutil
import sys

root = Path(sys.argv[1]).resolve()
src = Path(sys.argv[2]).resolve()
out = Path(sys.argv[3]).resolve()
text = src.read_text(encoding="utf-8", errors="replace")

# Collect quoted paths to source/structured files used by the temporary grader.
pattern = re.compile(r"(?P<q>['\"])(?P<p>[^'\"\n]+\.(?:py|json|txt|csv|tsv|md))(?P=q)", re.I)
raw = []
for m in pattern.finditer(text):
    p = m.group("p").strip()
    if p not in raw:
        raw.append(p)

rows = []
for value in raw:
    p = Path(value).expanduser()
    candidates = [p] if p.is_absolute() else [root / p, Path.cwd() / p]
    resolved = None
    for candidate in candidates:
        if candidate.exists():
            resolved = candidate.resolve()
            break

    if resolved is None:
        rows.append((value, "MISSING", ""))
        continue

    try:
        rel = resolved.relative_to(root)
        rows.append((value, "IN_REPO", str(rel)))
        continue
    except ValueError:
        pass

    lower = resolved.name.lower()
    blocked = any(x in lower for x in (".env", "secret", "token", "credential", "private_key", "id_rsa"))
    safe_suffix = resolved.suffix.lower() in {".py", ".json", ".txt", ".csv", ".tsv", ".md"}
    safe_location = str(resolved).startswith("/tmp/")

    if safe_location and safe_suffix and not blocked:
        dest = out / "local-inputs" / resolved.name
        if dest.resolve() != resolved:
            shutil.copy2(resolved, dest)
        rows.append((value, "COPIED_LOCAL", str(dest.relative_to(root))))
    else:
        rows.append((value, "EXTERNAL_NOT_COPIED", str(resolved)))

with (out / "referenced-files.tsv").open("w", encoding="utf-8") as f:
    f.write("grader_path\tstatus\trepo_or_resolved_path\n")
    for row in rows:
        f.write("\t".join(row) + "\n")

# Preserve the lines most useful for parser debugging in a compact view.
keywords = re.compile(r"ref|reference|parser|read_text|open\(|csv|tsv|measure|reserve", re.I)
with (out / "parser-lines.txt").open("w", encoding="utf-8") as f:
    for i, line in enumerate(text.splitlines(), 1):
        if keywords.search(line):
            f.write(f"{i}: {line}\n")
PY

cat > "$OUT/README.md" <<'EOF'
# v143 grading debug capture

This directory preserves the temporary grading code and parser diagnostics that previously existed only inside the Codespace `/tmp` directory.

Files:
- `last_grade_cmd.py` — exact temporary grading program copied from `/tmp/last_grade_cmd.txt`.
- `parser-lines.txt` — compact parser/reference-related lines from the grader.
- `referenced-files.tsv` — files referenced by the grader and whether they are already in the repo, copied from `/tmp`, missing, or intentionally not copied.
- `repo-state.txt` — branch, HEAD, timestamp, and working-tree state at capture time.
- `local-inputs/` — safe source/structured files referenced by the grader that lived in `/tmp`. Secrets and credential-like files are never copied.

The frozen candidate/model files are not modified by this capture.
EOF

echo
printf 'Captured v143 grading diagnostics in:\n  %s\n\n' "$OUT"
cat "$OUT/referenced-files.tsv"
echo
echo "Nothing has been committed yet. Review the files above, then commit/push them when ready."
