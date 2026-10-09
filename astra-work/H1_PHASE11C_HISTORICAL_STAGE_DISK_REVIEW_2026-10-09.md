# Astra H1 Phase 11C — historical stage-overlap disk feasibility

**Date:** 2026-10-09. **Branch:** `astra-work`. **Disposition: `NO_GO_INSUFFICIENT_EVIDENCE`.** This phase uses only previously published **scalar inventory-log metadata** and synthetic duration scenarios. OpenAI Support case **#16795041** still requires a written decision. No real media was retrieved or decoded, no model, training, inference, Actions/preflight, Codespaces, paid compute, launch artifact, or production workflow was used.

## New evidence: alignment receipts do not recover the 98 missing durations

The frozen accepted-key list contains **256** captures. Prior Phase 11B matched **158 WAV headers** and found **98 accepted ego/exo MP3 video-view captures** lacking duration observations (52 ego; 46 exo). Review of the recorded `astra_backend/guitartechs_alignment/align_development.py` (Git blob **`982de241925edcfbe2043196c6900460cd88870b`**) confirms its `evaluate_alignment()` JSON records lag/residual/onset diagnostics and audio-envelope **sample rate/window/hop parameters**, **not decoded sample count or capture duration**. The historical alignment summary `docs/astra/GUITARTECHS_DEVELOPMENT_ALIGNMENT_EVIDENCE_V1.json` (Git blob **`47ec1567003e87181fbbeb55dfdabe1a1f3244ee`**) likewise records aggregate capture outcomes, not a verified full 256-source duration/frame table. No new H1 frame-count result or 98 MP3 durations have been claimed. We did **not** retrieve the original MP3/video data.

## Exact historical archive sizes and frozen workflow ordering

Machine provenance is retained in `astra-work/H1_HISTORICAL_INVENTORY_RECOVERY_2026-10-09.json`, blob **`5706ac4ed1a9590fa74f7644e6be7e642ffb9db2`**: eight historical original inventory-only jobs, all eight frozen archive identities, **7,288,969,715 total visible extracted logical bytes** and **4,004,045,267 total compressed bytes**. Per-archive accepted-source counts are **84, 47, 3, 2, 72, 43, 3, 2**, in the precise dormant `ubuntu-22.04` workflow order: P1 chords, scales, singlenotes, techniques, then P2 chords, scales, singlenotes, techniques. These counts total **256** and sum **158 WAV and 98 MP3** matches.

The dormant workflow (Git blob **`90e8168fc1ca40738ba07291ca1001a36718f4e3`**) downloads **one ZIP at a time**, extracts it, deletes the ZIP, prepares accepted capture arrays into a persistent `/tmp/prepared` directory, and then deletes the extracted archive. Its **ZIP + extraction** stage can overlap **all previously accumulated prepared arrays**, but it does **not** simultaneously hold the prior archives' extracted data. Historical `stat().st_size` logical extracted bytes are **not physical disk allocation**, current-run high-water measurements, or hard upper bounds.

## New conditional overlap calculation — no measured video durations

Only the source-backed prepared-array payload (**780 × F bytes**) is modeled. Historic accepted WAV-header durations give a **nominal**, not actual, CQT frame proxy of **1,227,986 frames** for 158 WAV captures. Each missing one of 98 MP3 durations is assigned an **explicitly hypothetical** 1, 2, 5, 10 or 15 minutes. Frame proxy per MP3 uses `ceil(minutes×60×22,050/512)`. The model uses `780×(historical WAV nominal frames + 98×hypothetical MP3 nominal frames)` as a conditional retained prepared payload. This **cannot** supply actual `SUM(F_i)` or `MAX(F_i)`: FFmpeg/librosa decoding/resampling/padding and the missing MP3 durations are unknown.

For archive `i` and retained prepared payload from prior archives `R_before`, the modeled identifiable logical bytes are:

- **ZIP + extraction** = `R_before + frozen compressed ZIP bytes_i + historical extracted visible logical bytes_i`.
- **End of preparation (ZIP deleted)** = `R_before + extracted visible logical bytes_i + hypothetical current prepared payload_i`.
- **After extraction cleanup** = `R_before + hypothetical current prepared payload_i`.

Take the largest among those stage values across the eight archives; the model does **not** add all eight historical extraction sizes as if concurrent.

| Hypothetical average duration *per one of 98 MP3 captures* | Conditional complete prepared-array payload only | Largest identifiable stage overlap only | Modeled stage |
| --- | ---: | ---: | --- |
| **1 minute** | **1.076 GiB** | **3.904 GiB** | P2_chords ZIP + extraction |
| **2 minutes** | **1.260 GiB** | **4.005 GiB** | P2_chords ZIP + extraction |
| **5 minutes** | **1.812 GiB** | **4.309 GiB** | P2_chords ZIP + extraction |
| **10 minutes** | **2.732 GiB** | **4.816 GiB** | P2_chords ZIP + extraction |
| **15 minutes** | **3.651 GiB** | **5.323 GiB** | P2_chords ZIP + extraction |

**All five rows are counterfactual sensitivity scenarios, not observed data or measured/verified maximum disk use.** They exclude 512 `.npy` headers, filesystem blocks, Git repository, Python/Torch/librosa/FFmpeg and dependency caches, download partials, model weights and optimizer state, artifacts, logs, OS reserve, failure margin and free-disk variance. The historic largest single archive ZIP + extraction was **3,593,659,397 bytes ≈3.347 GiB**, before earlier prepared arrays. Even the nominal published **14 GB SSD / 16 GB RAM** runner specification cannot establish effective available capacity; **disk/RAM feasibility remains UNPROVEN**.

## New tested offline review files

- `astra-work/h1_historical_stage_disk_model_v1.py`, verified Git blob **`04b1eb377740ca0fca9be87fd6fbc4214d50b013`**.
- `astra-work/test_h1_historical_stage_disk_model_v1.py`, verified Git blob **`1d16dcc802e623699e9cc9d563b4ef58770d8c85`**.
- `astra-work/H1_PHASE11C_STAGE_DISK_SENSITIVITY_2026-10-09.json`, verified Git blob **`cb15f120a7bc6c9686ff53f92b23b9ffa33506d4`**, generated directly from the tested model with `sort_keys=True`.

Actual local CPU-only Python **3.13.5** commands, no external dependencies or media:

```bash
cd /mnt/data/astra_phase11c
python -m unittest -v test_h1_historical_stage_disk_model_v1.py
python -m py_compile h1_historical_stage_disk_model_v1.py test_h1_historical_stage_disk_model_v1.py
python h1_historical_stage_disk_model_v1.py > H1_PHASE11C_STAGE_DISK_SENSITIVITY_2026-10-09.json
```

**12/12 tests PASS, 0 failures/errors**, syntax compilation PASS. Test log SHA-256 **`1c03e97b07bb86a85b0d1151c5136f7f30fbdabe7c6fc690b4e21c0b1d4f0492`**. Tests exercise all-eight inventory sums/capture counts, exact workflow-stage arithmetic, absence of previous extraction double counting, the known largest ZIP/extraction identity, scenarios monotonicity, failure on altered scalar receipts, and non-authorization. Exact tested Python bytes, and the generated JSON bytes, were independently confirmed as GitHub file blob hashes. This is **not** a run of the full H1 repo suite or pinned full-model parity.

## Next independent no-media work and hard-stop gates

1. **Seek a historical 98-MP3 scalar duration source** (for exactly 52 ego and 46 exo accepted captures), or previously saved exact 256-capture `SUM(F_i)` and `MAX(F_i)` with matching provenance. The checked alignment source/report does **not** contain lengths. Do not treat companion WAV durations as actual MP3 lengths or query protected media.
2. Obtain **independently measured effective free runner disk** and overhead from permitted *existing* logs (installed Python/Torch/libraries, caches/repo, manifests/artifacts, NPY headers and system reserve); present a reliable **stage maximum** not a sum of unrelated archive peaks. Still require an independently justified RAM peak for largest accepted capture, VQT extraction, model activations, Adadelta, V4 state and float64 evaluation intermediates.
3. Preserve the existing **12-stage ≤18,000s H1 wall-time/CPU budget** as **NOT PROVEN**. Original V9 historical **183.719-minute proxy** is a sensitivity input only, not an H1 upper bound. Complete checkout ten-module no-media H1 tests, pinned Python **3.10.15 / Torch 1.11.0+cpu / NumPy 1.21.6** synthetic model parity, independent immutable source/import closure and globally atomic one-use approval all remain outstanding.
4. Wait for **explicit written OpenAI Support case #16795041 clearance** and all independent technical gates before any real study. Maintain `NO_GO_INSUFFICIENT_EVIDENCE`, not a claim that it is impossible. Only record new verified outcomes to `astra-work/CURRENT_STATE.md`, preserving earlier handoff.

**HARD STOP:** Do not create/edit blocked `docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_TRAINING_LAUNCH_V1.json`, dispatch Actions/preflight/training, bypass via Codespaces/Codex/UI, access/download original P1/P2/P3/protected/Stage-B media, execute real inference/optimization, pay for compute, export trained weights, change `main`/Production or frozen V8/V9 science, or retry the separately blocked `docs/checkpoints/CURRENT_STATE.md` write. This increment adds only independent offline review scripts/tests/receipts/documentation outside the live trigger.
