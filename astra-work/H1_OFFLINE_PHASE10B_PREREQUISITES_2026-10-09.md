# Astra H1 Phase 10B — local frozen-runtime prerequisites (2026-10-09)

**Branch:** `astra-work`. **Status:** NO-MEDIA OFFLINE ENGINEERING / **REAL H1 LAUNCH BLOCKED** pending OpenAI Support case **#16795041** and independent technical review.

## Purpose and new files

Added an entirely separate, read-only, non-launching prerequisite checker:

- `astra-work/h1_offline_runtime_prerequisites_v1.py` — Git blob **`c14b39c6faa729f04516e22904b3682ab7989adc`**.
- `astra-work/test_h1_offline_runtime_prerequisites_v1.py` — Git blob **`ebf5c6d93a1f637c16909f6040e1063346b16b8b`**.

These are **not** added to the dormant training workflow or safety-blocked launch source manifest. No other workflow or model code is changed. Both GitHub blob IDs equal the exact locally tested file hashes.

The checker imports local Torch and NumPy **only to read `__version__` and whether CUDA is available**, compares their actual values and Python micro-version to the original frozen environment (**Python 3.10.15, Torch 1.11.0+cpu, NumPy 1.21.6**), and can inspect **already staged** upstream AMT-Tools sources and three generated `__init__.py` files via exact bytes/Git blob IDs. It performs **no download, inference, optimization, training, workflow dispatch or media access**. It never emits a launch JSON or launches parity. Its only positive disposition is `LOCAL_IDENTITIES_ONLY_REVIEW_REQUIRED`, with `independentApproval=PENDING`, `fullModelParityExecuted=false`, `trainingExecuted=false`, and `launchPermission=false`. Failure or missing data produces `BLOCKED_OR_UNVERIFIED` and CLI exit code **2**.

## Actual local test execution

Environment: **Python 3.13.5**, **Git 2.47.3**, CPU-only local session (NOT pinned and NOT a full GitHub repository checkout).

Command in local scratch directory:

```bash
cd /mnt/data/astra_phase10_followup
python -m unittest -v test_h1_offline_runtime_prerequisites_v1
python -m py_compile h1_offline_runtime_prerequisites_v1.py test_h1_offline_runtime_prerequisites_v1.py
```

**Final result: 15 tests passed / 0 failures / 0 errors**, plus Python byte-compilation PASS. Test log SHA256: `6bc43a878300d3c30bb2dc1c9b084d61cf5cc7181e8a48f2b7f95d8bedb8a41c`. The fixtures cover missing/incorrect Python/Torch/NumPy pins, CUDA availability, missing upstream source, modified content/initializers, symlink sources and directories, traversal rejection, and positive dummy-only upstream fixtures which the **real production pins reject**.

**New regression finding corrected:** PyTorch's `torch.__version__` may be a **subclass of Python `str`** (TorchVersion), not `type(raw) is str`. The initial synthetic checker incorrectly classified that case as unavailable. It was fixed to use `isinstance(raw, str)` both when reading an installed version and when comparing exact versions; two additional regression checks were added. Only the **final corrected checker** and its 15-test output are submitted as a passing result.

## Executed read-only local prerequisite check

Command:

```bash
python h1_offline_runtime_prerequisites_v1.py > actual_environment_review.json
# Actual result: exit code 2 (blocked)
```

Results from the actual imports:

| Check | Frozen expectation | Local observation | Outcome |
| --- | --- | --- | --- |
| Python | 3.10.15 | **3.13.5** | Mismatch |
| PyTorch | 1.11.0+cpu | **2.10.0+cpu** | Mismatch |
| NumPy | 1.21.6 | **2.3.5** | Mismatch |
| CUDA available | False | **False** | CPU-only observation |
| Four pinned upstream sources plus 3 generated inits | Exact local copies verified | **No local source root staged** | Not checked |

**Verdict:** `BLOCKED_OR_UNVERIFIED`, `prerequisitesLocallyMatched=false`, `fullModelParityExecuted=false`, `launchPermission=false`; the full actual JSON result had SHA256 `bdb5052e53242c588c7a17c322a6d1ceb3a5947430b54`. This is a proper **fail-closed** observation, **not** an authorization or a frozen model-parity run.

## Unresolved next steps

1. **Full repository checkout still unavailable here** (local network DNS cannot resolve GitHub); the ten-module actual H1 no-media regression suite and Phase-9 complete import AST audit on all project files remain **NOT RUN**.
2. The existing full-model synthetic parity script **still lacks its own frozen-version enforcement**; it was not modified. Before relying on its future results, an independent reviewer must approve exact prerequisites/recording in a permitted pinned environment. This separate checker is **review evidence only**, not an authoritative wrapper or launch gate.
3. Exact local staging of the four upstream AMT-Tools sources, their three generated initializer files, and complete package/namespace behavior remain unverified in this environment. Remote Git blob identities were checked earlier, but do not replace local runtime verification.
4. Durable, shared atomic single-use control and a defensible **≤300-minute** end-to-end budget remain **UNPROVEN**; prior Phase-8/9 evidence stays valid with its limitations.
5. Wait for **written OpenAI Support case #16795041** disposition. The already-blocked `docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_TRAINING_LAUNCH_V1.json` must **not** be created/edited via any alternate tool. The daily Support-email reply watch remains separate.

**Hard STOP:** No Actions/preflight/training, real P1/P2/P3/protected/Stage B data use, Codex/Codespaces rerouting, spending, inference/optimizer, trained-weight export, `main`/Production or frozen V8/V9 changes, and no retry of the separately blocked `docs/checkpoints/CURRENT_STATE.md` write. This increment only adds review artifacts and documents an honestly blocked runtime prerequisite check.
