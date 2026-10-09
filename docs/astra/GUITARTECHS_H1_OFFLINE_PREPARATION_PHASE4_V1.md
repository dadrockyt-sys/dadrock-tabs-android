# Guitar-TECHS H1 — Phase 4 offline objective and core guard preparation

**2026-10-08 · branch `astra-work` · status: OFFLINE ONLY / REAL-DATA LAUNCH BLOCKED.** This phase continues from Phase 3 evidence commit `8a8665fbbbca0e8b054e2f0a53c3cb43c933f6be`. The OpenAI Support escalation concerning the blocked launch JSON remains unresolved. **No Codespaces usage, new GitHub Actions run, real P1/P2 audio access, trained checkpoint or real H1 optimizer update** occurred here.

## Changes

1. **Actual frozen-function import parity fixture:** `astra_backend/guitartechs_training_v10/test_h1_real_v7_objective_parity_v1.py`. The committed test imports **the actual repository's frozen V7 `v7_sequence_loss`, V9 `paired_tensor_views` and `symmetric_kl_consistency`, and H1's `losses` and `probe`**. A small synthetic multi-head neural network produces the expected 200-frame / 6-string / 21-class states, activity, 44-pitch, and event heads, with a few synthetic active and masked note regions. It compares **two Adadelta steps** executed using the original V9 objective expression against H1's original-control expression/probe: exact parameter tensors, optimizer state and RNG after each step. It independently checks that the normalized arm's weighted KL is the original divided by 1,200, without changing the supervised loss.
2. **Actual core train/evaluate AST failure fixture:** `astra_backend/guitartechs_training_v10/test_h1_core_failclosed_v1.py`. The tests extract the committed `train_arm` / `evaluate` function bodies via AST; they stub dependencies to prevent actual data loading, full model inference or real training. Seven scenarios cover normal synthetic evaluation, nonfinite capture metrics, all required audit counters, impossible matched-event counts, fold/count and macro metric failures, stop-before-first optimizer update, reporting failure after one toy update, and plan-group drift. These extend the earlier four driver-level mocks; they are **not** a performance or model architecture benchmark.
3. **Fail-closed production-path fix (still dormant):** `h1_pilot_core_v1.evaluate` now validates **all 10 event/admission counters** are actual nonnegative Python integers **before** aggregation, including `stateArgmaxActivePositions`, `activeRunsBeforeGapMerge`, confirmed/strong-start candidates, and accepted start counts. Previously only four counters were checked, and an absent later counter could produce an unclassified `KeyError`. Boolean values do not count as valid integers.
4. Updated the explicitly nonlaunch `GUITARTECHS_H1_REVISED_SOURCE_LOCK_REVIEW_DRAFT_V1.json` with the changed core blob and the two new test blobs: currently **17 dormant workflow dependencies and 9 offline auxiliary sources**. It remains **`DRAFT_REQUIRES_INDEPENDENT_REVIEW_NOT_LAUNCH_AUTHORIZATION`**.

## Evidence and exact limits

Local mirror: `/mnt/data/h1prep_local`, Python environment with Torch `2.10.0+cpu`. The committed objective parity test file **exactly matched its local Git blob `8868ea56f1da130ff4a479056fe65fcaa388162c`**. Local imports used a **manual mirror of the relevant frozen V7 objective implementation and model constants, V9 paired-view helper, and H1 core objective/probe**; original full `TemporalTabCNNV9` and upstream TabCNN runtime were **not** instantiated. The remote test's imports, when run in the actual repository, instead load the real frozen modules. Exact `h1_pilot_core_v1.py` remote blob is `2bf8085b6cd69214d5e2ec198d80c40b35d13875`; the local AST test exercised manually mirrored copies of its train/evaluate functions, **not** an independent byte-for-byte full repository checkout.

Local commands:

```bash
cd /mnt/data/h1prep_local
PYTHONPATH=. python -m unittest -v \
  guitartechs_training_v10.test_h1_core_failclosed_v1 \
  guitartechs_training_v10.test_h1_real_v7_objective_parity_v1
```

**Observed: 9 tests PASS (7 core-function synthetic/fault checks + 2 V7-formula tiny-network parity checks).** The local core-fault test file was the earlier local version with functionally corresponding seven cases; the newly committed test is not claimed as independently run byte-identically. No new workflow/CI run was dispatched. The remote source/test Git blobs were inspected after commit via GitHub connector; source-lock snapshot updated accordingly.

**Scientific limitation:** Passing tiny-network objective parity does not prove original V9 model epoch-20 state SHA reproduction (exact original hashes remain `933c5fae...` / `56b275d...`), same seed/optimizer behavior across different runner hardware, or P1/P2 treatment efficacy. Torch version here differs from the frozen `1.11.0+cpu` runner. The first-microbatch gradient probe is not proof of a cause for the original V9 scientific failure. V8 baseline/F1 and V9 frozen FAIL remain unchanged.

## Next authorized offline work

- Execute the new test suite *on the unchanged frozen V9 dependencies and pinned Torch runtime* when a supported, separately permitted **no-media** environment is available, without invoking the launch mechanism. Also add complete full-model synthetic initialization/optimizer/RNG parity and more fixture variations (mask/no-active/event-heavy) without real media.
- Independently review the 17-source closure, 9 offline-file draft, upstream hashes and durable once-only launch-consumption design. The GitHub `run_attempt==1` guard does not prevent a fresh run from a new launch-file edit.
- Reconcile historical V9 timing evidence with **full H1** evaluation and instrumentation cost, bounded acquisition retry deadline, CPU/RAM/disk evidence, artifact reserves and the frozen 300-minute limit. Phase-3 183.72-minute illustration is **not** a full verified upper bound.
- **Await platform safety escalation response**; written platform clearance and independent technical approval are both required before considering even a revised preflight or any real-data operation. The prior green preflight was for an older source commit.

**Hard stop:** Do **not** create/change `docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_TRAINING_LAUNCH_V1.json`, reroute it through Codespaces/Codex/alternate APIs, dispatch GitHub Actions preflight or training, touch P3/protected songs/Stage-B, paid compute, `main`, Production, historical frozen checkpoints/metrics, or relax the protocol. 💚
