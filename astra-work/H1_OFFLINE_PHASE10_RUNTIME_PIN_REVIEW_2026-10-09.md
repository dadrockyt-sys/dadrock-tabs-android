# H1 Phase 10 — offline frozen-runtime parity prerequisite audit (2026-10-09)

**Scope:** NON-EXECUTING REVIEW ONLY. Branch `astra-work`. **No real H1 training**, launch receipt, GitHub Actions dispatch, new data access, new paid compute, or full frozen TemporalTabCNNV9 synthetic parity. OpenAI Support case #16795041 remains a hard launch blocker until an explicit written decision.

## New verified issue: the parity probe can label a non-pinned environment "PASS"

Read-only GitHub inspection of the **existing** frozen synthetic parity source, `astra_backend/guitartechs_training_v10/h1_full_model_synthetic_parity_v1.py` (blob `3eb3638c94a2cdfd835c3d600e4b614b2f2401ca`), alongside the dormant workflow (blob `90e8168fc1ca40738ba07291ca1001a36718f4e3`) and dependency file (blob `174a5016cfe9e6c00816d2171210aa84c66081a8`), verified these frozen constraints:

| Runtime | Frozen constraint | Evidence |
| --- | --- | --- |
| Python | `3.10.15` | Dormant workflow's `python-version` |
| PyTorch | `1.11.0+cpu` | `requirements.lock.txt` |
| NumPy | `1.21.6` | `requirements.lock.txt` |

The parity script **does not contain direct comparisons enforcing any of these three version values** before printing JSON with `status: PASS_SYNTHETIC_ONLY`. It reports `torch.__version__` but does not validate it against the frozen target. It likewise lacks a Python-version import/check and a NumPy-version check. The check is a narrow read-only source-pattern observation, **not** a model execution or complete control-flow proof.

**Risk:** A developer could execute the script in a nonfrozen environment, observe a synthetic-only "PASS" result, and mistakenly describe that as frozen V9/H1 parity. Consequently an output showing `PASS_SYNTHETIC_ONLY` must not be accepted as evidence of frozen reproducibility until environment identity and the actual pinned workload are independently verified. **Do not change the existing parity script, the dormant workflow, or the DRAFT lock solely to bypass or expedite the platform block.**

## New non-executing review materials

- `astra-work/h1_frozen_runtime_review_v1.py` — exact committed Git blob **`8cc35183831aca5065723e8b68226568234011b5`**.
- `astra-work/test_h1_frozen_runtime_review_v1.py` — exact committed Git blob **`b5e5fcd1d8f506613e1ea5e398484b9934272705`**.

The helper reads **only** three already-local source files in a permitted checkout, extracts exact literal frozen dependency pins, scans the parity source with Python AST for literal version comparisons, and returns a **non-authorizing** JSON finding. It does **not** execute the model script or prove runtime guards are on reachable paths. Even if version comparisons were found, the result still sets `runtimeEnforcementProven=false`, `fullModelParityExecuted=false`, `safeToClaimFrozenParityPass=false`, and `launchPermission=false`. It rejects malformed/drifted/duplicated frozen pins, malformed Python AST and symlinked inputs.

## Actual offline synthetic test receipt

Environment: Python **3.13.5**, Git **2.47.3**; PyTorch **2.10.0+cpu**, NumPy **2.3.5** installed but **not imported by these tests**. No repository clone was available: direct git HTTPS resolution of github.com failed. This is a local fixture suite, NOT a full-repository H1 run.

```text
PYTHONPATH=/mnt/data/astra_phase8:/mnt/data/astra_phase9:/mnt/data/astra_phase10 \
python -m unittest -v \
  h1_one_use_synthetic_review_v1 \
  test_h1_source_review_no_media_v1 \
  test_h1_frozen_runtime_review_v1

Ran 17 tests in 0.115s
OK
```

All **17 tests PASS, 0 errors/failures**: prior Phase-8 **5**, Phase-9 **6**, and new Phase-10 **6**. New tests cover missing literal runtime checks, comparisons present without assuming they enforce anything, comments/strings not matching AST checks, dependency-pin drift/ambiguity, malformed source, and fixed-file-path/symlink rejection. New source and test both passed `python -m py_compile`. Terminal output SHA-256 (for the recorded combined execution) **`3b263d5ffc6cf553266e6d0365528fc217af1fc63c70ef205f26e0b1ef2bd587`**. `git hash-object` of both exact local tested Python files equals the committed remote blob IDs above, independently fetched and verified. No test executes any real model, optimizer step, P1/P2 media or workflow.

## Next tasks, blocked gates and disposition

1. **Before accepting any later full-model synthetic parity receipt**, ensure the run **actually uses** Python 3.10.15, Torch 1.11.0+cpu, and NumPy 1.21.6, and independently checks the exact staged pinned AMT-Tools blobs/init bytes. Have an independent reviewer approve a safe, fail-closed environment-verification change or wrapper; simply finding version comparisons in source is insufficient.
2. In a **permitted complete checkout**, run the full ten-module H1 no-media regression suite, including the already committed pre-journal prepared-array AST driver test. Then run both Phase-9 and Phase-10 read-only helpers against exact checked-out bytes and record their actual JSON outputs. This phase does **not** claim those full-checkout tests or source scripts executed successfully.
3. Full-model frozen two-step synthetic parity remains **NOT RUN**. Complete import/runtime closure, independent immutable trust anchoring of the draft source lock, durable globally atomic single-use and a defensible end-to-end **≤300-minute** CPU/RAM/disk/evaluation/resource bound remain **UNPROVEN**.
4. Await OpenAI Support case **#16795041**'s written decision. If Support requests the currently absent blocked launch JSON, ask for an explicitly permitted non-executing review format instead of creating it.

**Hard STOP:** Do not create/edit the safety-blocked `docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_TRAINING_LAUNCH_V1.json`, launch Actions/preflight/training, use Codespaces/Codex/UI as alternate routing, access real P1/P2/P3/protected-song/Stage-B media, spend compute or perform real optimization/inference, export trained weights, modify `main`/Production/frozen V8/V9 science, or retry writing the separately blocked `docs/checkpoints/CURRENT_STATE.md`. This increment modifies only review files outside the live workflow.
