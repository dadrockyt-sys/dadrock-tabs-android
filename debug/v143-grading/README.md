# v143 grading debug capture

This directory preserves the temporary grading code and parser diagnostics that previously existed only inside the Codespace `/tmp` directory.

Files:
- `last_grade_cmd.py` — exact temporary grading program copied from `/tmp/last_grade_cmd.txt`.
- `parser-lines.txt` — compact parser/reference-related lines from the grader.
- `referenced-files.tsv` — files referenced by the grader and whether they are already in the repo, copied from `/tmp`, missing, or intentionally not copied.
- `repo-state.txt` — branch, HEAD, timestamp, and working-tree state at capture time.
- `local-inputs/` — safe source/structured files referenced by the grader that lived in `/tmp`. Secrets and credential-like files are never copied.

The frozen candidate/model files are not modified by this capture.
