# Astra H1 — offline feasibility-test readiness package

**2026-10-09 | Branch `astra-work` | Phase 12 paper-only preparation**

**Decision:** `BLOCKED_MISSING_EVIDENCE` for a feasible 300-minute H1 pilot. **This package is ready for an independent, authorized evidence review, not ready to dispatch the H1 training workflow or a preflight.** OpenAI Support case **#16795041** has not supplied written launch clearance. The safety-blocked launch JSON stays absent.

## What is prepared and verified

- `astra-work/h1_feasibility_review_offline_v1.py` — standalone, **read-only** Python standard-library reviewer; imports no model, media, Torch or network code; cannot dispatch, spend, optimize, launch, produce a training configuration or approve safety clearance.
- `astra-work/test_h1_feasibility_review_offline_v1.py` — **13 real local synthetic tests PASS**, zero failures/errors, plus `py_compile` PASS (Python 3.13.5). Tests cover missing evidence, fake complete evidence **still non-authorizing**, >300-minute total, disk/RAM reserve overruns, missing stage/source identity, negative/NaN/bool inputs, unsupported external-clearance self-assertions, source-blob tampering and symlink rejection.
- `astra-work/H1_FEASIBILITY_MEASUREMENT_WORKSHEET_BLANK_2026-10-09.json` — blank evidence worksheet (all absent measurements are `null`; no operational H1 authorization fields, no source code or launch trigger). It identifies **12 independent timing upper bounds**, **6 runner resource-byte measurements**, and **1 runner evidence reference** = **19 unresolved entries**. The local fixture check returned `BLOCKED_MISSING_EVIDENCE`. The demonstration uses synthetic source consistency values derived from prior reported aggregates, **not an actual CLI read of the three pinned remote JSON receipts**.
- Existing immutable-source inputs, checked through GitHub this phase:
  - `astra-work/H1_PHASE11D_EXACT_PREPARED_FRAME_RECOVERY_2026-10-09.json`, Git blob **`701d4626de0e04200534ed17827db00c896a3d6b`**.
  - `astra-work/H1_PHASE11D_EXACT_STAGE_CAPACITY_2026-10-09.json`, Git blob **`e8375ec0cd132eadda93456a023df77a88153eda`**.
  - `astra-work/H1_PHASE11D_V9_HISTORICAL_PREP_TIMINGS_2026-10-09.json`, Git blob **`309bbe19d6e52083237bd8f10d0998623bea6e80`**.
  - Dormant H1 workflow, Git blob **`90e8168fc1ca40738ba07291ca1001a36718f4e3`**, left unchanged.

## Test contract — human-review evidence only

The reviewer **cryptographically checks the exact Git blob SHA-1 content** of each of the three scalar receipts *before* reading their JSON. It reconciles **256 prepared captures**, **1,924,805 exact prior CQT frames**, maximum **23,773** frames, **1,501,347,900 bytes** in float32-feature/int16-label payload, and the prior **4,391,923,097-byte** maximum identifiable historical logical disk overlap. It also verifies ten V9 prior preparation job observations ranged **1,551.280–3,416.914 seconds**. **These are historic identities and sample observations, not H1 upper bounds or measured runner free capacity.**

For the 12 stage names already required by `astra_backend/guitartechs_training_v10/h1_offline_budget_v1.py`, a future independent reviewer must supply an evidence-backed *upper* duration, original run ID, and source SHA-256. The 12 stages are: dependencies/environment; pinned source acquisition; archives/preparation; two original-fold training runs; two normalized-treatment-fold training runs; four full-fold V4 evaluations; upload+cleanup reserve. The **complete documented upper envelope must not exceed 18,000 seconds**, inclusive of cleanup and reserve; simply adding the historically observed V9 intervals is inadequate. A proposed upper-bound field is **not independently validated by the Python code**.

For the runner, the worksheet requests **actual available disk at start**, **worst-case additional peak disk**, **disk reserve**, **actual available RAM**, **peak resident RAM**, **RAM reserve**, and a separately identifiable runner evidence run/image/hash. All bytes are integers and measured values must be attributable to an authorized, comparable runner. The model requires

```
availableDiskBytesAtJobStart − peakAdditionalDiskBytes − diskReserveBytes >= 0
availableRamBytes − peakResidentRamBytes − ramReserveBytes >= 0
SUM(twelve validated upperBoundSeconds) <= 18_000
```

It flags a proposed disk peak below the **4.090 GiB** historical *model* for review, **not** as a logically proven contradiction or a real lower bound. The 14-GB nominal GitHub SSD, 16-GB nominal RAM and old apt package-install estimates do not substitute for physical free-space/peak-RSS measurements, VQT/transient buffers or reserve.

**No script input can produce `launchPermission=true`.** Missing fields are `BLOCKED_MISSING_EVIDENCE`; demonstrated overruns are `BLOCKED_BOUND_EXCEEDS_LIMIT`; even a synthetic fully filled, within-budget worksheet yields `PAPER_PACKAGE_AWAITS_EXTERNAL_VERIFICATION`, `independentLaunchReview=PENDING` and `writtenSupportApproval=PENDING`. There is **no "GO" or runtime launch command** in this package.

## How to reproduce offline, only when the three exact committed receipts are available

From an already available, permitted repository checkout at the reviewed `astra-work` commit, run **only the standalone reviewer** and its pure-scalar fixture tests:

```bash
python astra-work/test_h1_feasibility_review_offline_v1.py
python astra-work/h1_feasibility_review_offline_v1.py \
  --frames astra-work/H1_PHASE11D_EXACT_PREPARED_FRAME_RECOVERY_2026-10-09.json \
  --capacity astra-work/H1_PHASE11D_EXACT_STAGE_CAPACITY_2026-10-09.json \
  --timings astra-work/H1_PHASE11D_V9_HISTORICAL_PREP_TIMINGS_2026-10-09.json \
  --worksheet astra-work/H1_FEASIBILITY_MEASUREMENT_WORKSHEET_BLANK_2026-10-09.json
```

The second command **reads scalar files and prints JSON to stdout only**. It downloads nothing and changes no files. This session **did not run it on the complete remote checkout**, because github.com DNS resolution prevents cloning into the local sandbox. It has tested the reviewer functions and blank status with isolated synthetic scalar fixtures. Do not interpret any output as an H1 pilot feasibility execution or approval.

## What remains before an actual feasibility measurement/test

1. **Independent reviewer**: identify an expressly permitted, frozen-version, non-media measurement context on a comparable public Ubuntu 22.04 CPU runner, using only pre-existing allowed telemetry or a **separately authorized synthetic-only** experiment. Do **not** start Actions, an H1 preflight, or actual training to fill the worksheet while the case is blocked; no Codespaces/Codex workaround, no paid compute.
2. **Collect and sign genuinely attributable evidence**: exact runner image and free disk, staged source/environment/package/cache footprint, synthetic-only decoded-waveform/VQT-equivalent peak, model/Adadelta/activation and V4 evaluation RSS high-water, plus OS/cache/reserve. The prior verified **23,773-frame** maximum helps calculate tensor shapes but does not establish transient memory peaks.
3. **Complete the twelve time-stage ceiling**: pinned environment, source acquisition, eight sequential archive/prep costs without HTTP double-counting, four 20-epoch arms, four H1 full-fold evals, and artifacts/cleanup/failure reserve. The earlier V9 **183.719-minute** illustration is a *proxy*, not a guaranteed H1 bound.
4. **Independent source/dependency and trust review**: exact Python 3.10.15 / Torch 1.11.0+cpu / NumPy 1.21.6 CPU environment, four upstream AMT-Tools source blobs and 3 generated init files, dynamic import closure, actual repo ten-module no-media tests, synthetic-only frozen-model parity (both still **NOT RUN**), and durable global atomic one-use proof.
5. **Written OpenAI Support decision**: case **#16795041** remains open. The blocked `docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_TRAINING_LAUNCH_V1.json` **MUST NOT** be created, edited, reconstructed, or tested through alternate tools. The separately blocked `docs/checkpoints/CURRENT_STATE.md` write must not be retried. Keep `main`, Production, P3/protected material and frozen V8/V9 science unchanged.

**Deliverable state:** Paper feasibility reviewer **PREPARED AND SYNTHETICALLY TESTED**; real runner feasibility measurement **NOT EXECUTED**, disk/RAM resource ceiling **UNPROVEN**, complete 12-stage wall-time bound **UNPROVEN**, technical and Support launch gates **PENDING**.
