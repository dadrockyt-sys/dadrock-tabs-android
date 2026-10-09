# Astra H1 Phase 10C — strict upstream staging-tree review (2026-10-09)

**Branch:** `astra-work`. **Scope:** Additional offline, no-media, fail-closed source identity review. **Real H1 training remains BLOCKED** pending OpenAI Support case #16795041 and independent readiness gates. No training launch JSON, workflows, real media, model weights, Actions run, Codespaces, paid compute, or frozen scientific source was created or modified by this phase.

## Problem verified and corrected

Prior Phase 10B prerequisite checker verified the four pinned AMT-Tools source blobs and the three expected generated Python `__init__.py` bytes **but accepted other files/directories in the same `amt_tools` tree**. A matching fixed subset is insufficient evidence that Python could not encounter extra importable code, compiled modules, startup path files or executable initializers. It also previously followed a symlink at the supplied `--source-root` before checking component symlinks.

This phase **does not** change the dormant training workflow or the actual model parity experiment. It tightens only the standalone, non-authorizing, read-only checker `astra-work/h1_offline_runtime_prerequisites_v1.py`. It now requires the staged `amt_tools` subtree to contain **exactly seven expected regular files and the two expected directories** (`models/`, `tools/`) and no extras; any symlink at the source-root, `amt_tools` root, or within the staged subtree fails closed. The seven files are the four pinned source files plus three exact-byte generated package initializers. Unexpected `.py`, `.pyc`, `.pth`, arbitrary directories or other paths produce `UPSTREAM_UNEXPECTED_PATH` or `UPSTREAM_PATH_SYMLINK`. **The strict review assumes a fresh pristine staging tree and may correctly reject `__pycache__` from a previously imported source tree**; run it before importing pinned modules.

**Exact remotely verified committed blobs:**

- `astra-work/h1_offline_runtime_prerequisites_v1.py`: **`330956a29e646803f59ceb4bae9e4cf06cc2986a`**.
- `astra-work/test_h1_offline_runtime_prerequisites_v1.py`: **`e53f30478c6629ab26d38725e5892af59b364cd5`**.

Both blob IDs exactly equal `git hash-object` for the actual locally tested files. This does **not** demonstrate independent source approval, local staged upstream parity, runtime integrity or full H1 model parity.

## Tests actually executed (synthetic-only)

Local Python **3.13.5**, Git **2.47.3**, offline disposable test directories, no downloaded upstream material or production runner.

Before the code correction, the six new test methods identified the gap (six failures and one error under subtests; the original 15 tests passed). After correction:

```bash
cd /mnt/data/astra_phase10c
python -m unittest -v test_h1_offline_runtime_prerequisites_v1 > green_tests.txt 2>&1
python -m py_compile *.py
git hash-object h1_offline_runtime_prerequisites_v1.py test_h1_offline_runtime_prerequisites_v1.py
```

**Final actual result: 21 tests run; 21 PASS; 0 failures/errors; py_compile PASS.** The six new tests cover unexpected extra `.py` source, extra `.pyc` and `.pth` artifacts (including a nested `__pycache__` file), unexpected directory, symlinked source root, symlinked `amt_tools` root, and a pristine synthetic positive source tree. Existing Phase 10B tests still cover version mismatch, CPU-only restriction, pinned source tampering, initializer mismatch, path traversal, and symlink components.

- Final test log SHA-256: **`574b6b22c879d277429a532875089831862f3de73301f527c34bb1dbd0d9734c`**.
- Live local prerequisite CLI rerun: **exit code 2** and `status=BLOCKED_OR_UNVERIFIED`, Python **3.13.5**, Torch **2.10.0+cpu**, NumPy **2.3.5**, CUDA unavailable (false). Actual JSON SHA-256: **`bdb5052e53242c588c7a17c322a6d1ceb3c56bb50fdef75a3eeb3a5947430b54`**. No local pinned upstream `--source-root` was provided.
- Direct `git ls-remote` from this sandbox failed DNS resolution for github.com; therefore the complete actual H1 ten-module no-media suite and full-checkout Phase-9 audit are still **NOT RUN**.

## Interpretation, remaining risks and exact next steps

1. This is a **pre-import staged-tree identity check**, not dynamic dependency closure or a defense against concurrent mutations after checking. It cannot prove installed distributions, imports resolved by `sys.path`, package execution, TOCTOU resistance or complete runtime immutability. A positive `LOCAL_IDENTITIES_ONLY_REVIEW_REQUIRED` remains non-authorizing, never `PASS` for frozen model parity or training clearance.
2. Acquire a **permitted complete local checkout** (without starting Actions/media/training) and run the authentic 10-module H1 no-media suite, including the pre-journal prepared-array driver guard. Then run Phase 9 static/dynamic import-source review against exact committed source. Record actual test outputs and Git object identities. This is still blocked by the local GitHub network resolution failure.
3. Independently review trusted source identity, the exact pinned **Python 3.10.15 / Torch 1.11.0+cpu / NumPy 1.21.6** CPU environment, four pinned upstream source blobs, generated init bytes and dynamic import closure before any **synthetic-only** full TemporalTabCNNV9 model parity. **Actual full model parity has NOT RUN**; do not run in an unpinned environment and overclaim equivalence.
4. Resolve the independent **globally durable atomic one-use authorization** design, defensible complete **≤300-minute** wall-time/CPU/RAM/disk/evaluation/upload/cleanup budget, and written **OpenAI Support case #16795041** disposition. The previous Git-history first-add guard remains insufficient and historical ~183.72 minutes is not a worst-case budget.
5. Keep the blocked `docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_TRAINING_LAUNCH_V1.json` absent, do not attempt to reroute its creation, and do not write the separately safety-blocked `docs/checkpoints/CURRENT_STATE.md`. Only this primary `astra-work/CURRENT_STATE.md` is the active handoff.

**HARD STOP:** no GitHub Actions/preflight/training, blocked launch JSON, Codespaces/Codex/UI alternate-surface bypass, real P1/P2/P3/protected/Stage-B media, paid compute, real inference or optimization, trained-weight exports, `main`/Production or frozen V8/V9 protocol/result changes. This phase changed only separate review scripts and documentation.
