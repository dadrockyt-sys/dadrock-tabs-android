# Astra H1 — Phase 11 offline disk and RAM capacity desk review

**Date:** 2026-10-09. **Branch:** `astra-work`. **Verdict:** `NO_GO_INSUFFICIENT_EVIDENCE` for a complete 300-minute CPU-only H1 launch. This is an offline resource assessment, not a training run, a platform safety decision or independent approval. Written OpenAI Support case **#16795041** remains an additional hard blocker. No media, workflow, launch JSON, optimizer or model forward pass was used.

## Exact static source inputs (read-only GitHub)

| Source | Observed Git blob | Fact supported |
| --- | --- | --- |
| `astra_backend/guitartechs_real_training/real_training.py` | `d4a3dd99c4a2c3cda16c10bde1a5dc63f6380254` | Per accepted capture: `extract_cqt_features(...).astype(float32)`, labels `(6,frames)` `int16`, two `.npy` output files; audio is fully decoded via ffmpeg to a float32 waveform in memory before CQT |
| `astra_backend/tabcnn_runtime/preprocessing.py` | `e1d251a341b811b1b8e2df97d78b754d3379046b` | 22,050 Hz, 512-sample hop, 192 CQT bins; frame rate nominally 22,050/512 ≈ 43.0664 Hz |
| `astra_backend/guitartechs_training_v10/h1_prepared_array_guard_v1.py` | `b589b7118e2d23ec3d1557195954c65a7727a928` | Exactly `(192,F)` float32 features and `(6,F)` int16 labels, minimum 200 frames; bounded 4096-frame scan; no maximum F |
| `astra_backend/guitartechs_training_v2/sampling.py` | `9eb62fde56f592646077afa1e0ff3013a5dc6560` | Frozen segment of 200 frames; 32 sequences per batch group |
| `astra_backend/guitartechs_training_v2/train_v2.py` | `4db5add96c58a8e54868ea06dacb1da724675163` | A single contiguous 200×192×9 float32 model-input window per selected microbatch |
| `astra_backend/guitartechs_training_v9/post_v9_output_admission_audit_v1.py` | `8e4cf8a6aa052d0703fc69128a387de8eb2bf6d5` | Per-capture evaluation stores float32 `(F,6,21)` state and `(F,6)` event buffers; admission trace uses additional arrays including `state.astype(float64)` |
| `astra_backend/guitartechs_training_v10/h1_pilot_core_v1.py` | `2bf8085b6cd69214d5e2ec198d80c40b35d13875` | Evaluates each validation capture and applies frozen V4 admission and full metrics, with additional unmeasured model runtime memory |
| `docs/astra/GUITARTECHS_DEVELOPMENT_INVENTORY_EVIDENCE_V1.json` | `98cc3c5ee39d8d939261af3c5ca6298451cd6fdc` | Historical total extraction **7,288,969,715 bytes across separate 8-archive inventory runs**; NOT a concurrent peak |
| `.github/workflows/guitar-techs-h1-20epoch-paired-pilot.yml` | `90e8168fc1ca40738ba07291ca1001a36718f4e3` | Eight compressed archives processed sequentially with `/tmp/extract` cleared between them; prepared arrays accumulate in `/tmp/prepared`; runner nominally 14 GB SSD / 16 GB RAM / 4 vCPU (public standard runner) |

### Prepared-data payload: exact formula, unknown real frame total

For each accepted capture with **F** CQT frames:

```
feature payload = 192 bins × F × 4 bytes = 768F bytes
label payload   =   6 strings × F × 2 bytes =  12F bytes
combined .npy array payload               = 780F bytes
```

With **256 accepted P1/P2 development captures**, total prepared-array data payload is **`780 × SUM(F_i)` bytes**, excluding `.npy` headers, a 256-line manifest, filesystem allocation and scratch copies. The frozen minimum is **200 frames per capture**, so a **mathematical minimum**, *not an expected size*, is **39,936,000 bytes**. The real aggregate and maximum individual `F_i` remain absent from the inspected committed metadata. No finite maximum follows from the source alone because there is **no maximum capture frame count** check.

The model's nominal CQT rate is **22,050/512 ≈ 43.066 frames per second**. The following scenarios round up nominal frames per capture and are **hypothetical average durations, not dataset metadata or observed time**:

| Assumed average audio duration per accepted capture | Nominal combined prepared payload only |
| --- | ---: |
| 1 minute | **0.481 GiB** |
| 2 minutes | **0.961 GiB** |
| 5 minutes | **2.403 GiB** |
| 10 minutes | **4.805 GiB** |
| 15 minutes | **7.208 GiB** |

These omit both `.npy` headers for each of 256 captures (512 total files). Audio duration is not guaranteed to map exactly to this nominal frame count under librosa padding, so these figures are sensitivity estimates, **not reliable upper bounds**.

### Archive staging: don't confuse aggregate records with simultaneous peaks

Eight frozen compressed archives total **4,004,045,267 bytes = 3.729 GiB**; largest single compressed archive **1,150,819,056 bytes = 1.072 GiB**. Earlier inventory extracted a **total of 7,288,969,715 bytes ≈ 6.79 GiB across eight separate inspections**. It did not record each archive's extracted size or an H1 job's measured disk high-water mark. In the dormant H1 job the following phases overlap:

- **During unzip:** retained prepared `.npy` files from previous archives + the current compressed ZIP + current extracted archive + repository/packages/caches.
- **During preparation:** growing retained prepared files + current extracted archive + transient ffmpeg decoded waveform, CQT/VQT intermediates and source/dependency footprint. The current ZIP has already been deleted, but extracted contents persist until processing finishes.
- **During training/evaluation:** all retained prepared `.npy` files + runtime libraries + model/optimizer + journals and outputs. Memory-mapped arrays limit eager dataset reads but do **not** establish a bound on OS page cache, evaluation arrays or model activations.

The historical **7.29 GB aggregate extracted** value cannot be added as an observed simultaneous peak; conversely, ignoring current extraction and software because the ZIPs are serial would be unsafe. The nominal **14 GB SSD** is not the runner's actual usable free space. Without trustworthy **largest individual archive extracted bytes, total accepted frames, installation/cache footprint, and effective free disk**, no robust inequality proves peak disk remains under capacity.

### CPU RAM: array size identities, not measured peak

The frozen sequence-window function produces a contiguous **200 × 192 × 9 float32** buffer = **1,382,400 bytes (~1.32 MiB)** for a single 200-frame microbatch sequence. Model activations, backpropagation, Adadelta state and resident library memory are **additional and unmeasured**.

For a hypothetical evaluation capture containing **100,000 frames** (NOT a real capture measurement), the identifiable array allocations include:

| Identifiable evaluator array | Byte size |
| --- | ---: |
| Padded CQT float32 copy `(192,F+8)` | 76,806,144 |
| State float32 `(F,6,21)` | 50,400,000 |
| Event float32 `(F,6)` | 2,400,000 |
| One `state.astype(float64)` copy `(F,6,21)` | 100,800,000 |

These are per-array sizes **not a jointly measured resident-memory total, exact lifetimes, or worst-case bound**. Additional softmax/entropy intermediates, hidden tensors, activations, decoded PCM, VQT arrays and Python/Torch overhead are not bounded. Current code loads the full decoded audio into memory and creates CQT arrays, so the largest capture length matters at preprocessing time as well as evaluation.

### Reproducible no-media model and genuine local checks

Added two self-contained review-only files, outside the dormant workflow's trigger and source set:

- **`astra-work/h1_offline_capacity_model_v1.py`**, Git blob **`f66e473777692f4c9dd42956d5b8dd48477e9b44`**.
- **`astra-work/test_h1_offline_capacity_model_v1.py`**, Git blob **`1bf772f67c255185bca56fea1750bddd6ad3798b`**.

Command: `cd /mnt/data/astra_phase11_capacity && python -m unittest -v test_h1_offline_capacity_model_v1 && python -m py_compile h1_offline_capacity_model_v1.py test_h1_offline_capacity_model_v1.py && python h1_offline_capacity_model_v1.py`. **9 actual synthetic scalar tests PASS; 0 failures/errors; byte compilation PASS**, local Python 3.13 (NOT frozen Torch/Python runtime). Test output SHA-256 **`275fa8075a86fc8adfa5c22677669843e7473a85552a490a47c74ac3dd2b0128`**. Neither the tool nor tests import Torch, NumPy, audio, network libraries or Astra model modules. It accepts only an optional aggregate frame **integer**, not media paths; any supplied scalar remains explicitly **unverified/non-authorizing**. Both exact tested Python source files and generated receipt match their committed Git blob IDs.

Machine-readable desk-review receipt: **`astra-work/H1_STATIC_CAPACITY_READ_ONLY_2026-10-09.json`**, Git blob **`782ce62d3e163ba58d73e6ed0740a60f8e8bd9ef`**. This is exactly the local offline CLI's output, with `readiness=NO_GO_INSUFFICIENT_EVIDENCE`, `verifiedDiskOrMemoryHeadroom=false`, `realMediaRead=false`, `trainingExecuted=false`, `launchPermission=false`.

## Precise next permitted tasks and stop conditions

1. **Evidence gap: verified scalar frames.** Look for an independently recorded, privacy-preserving historical **`SUM(F_i)`** and **`MAX(F_i)`**, with file/run/commit provenance for all 256 original accepted captures. The inspected committed inventory and alignment receipts do **not** contain those two values. Do not read original audio or generate new H1 prepared data to obtain them while blocked. A trusted scalar-only receipt would enable a real prepared-payload estimate; it cannot by itself establish total peak disk.
2. **Evidence gap: extracted footprint.** Obtain prior, permitted **per-archive extracted-byte totals**, preferably historical log or inventory receipts. The aggregate 7.29 GB across inventory runs is not a per-archive peak measurement. Model disk by **stage overlap** above, including packages/cache/source and failure reserve.
3. **Evidence gap: real hardware.** Obtain independently reviewed runner **effective free SSD/RAM**, model+Adadelta parameter memory, preprocessing/VQT peak and evaluation peak. Use an already-authorized, non-media, synthetic-only pinned CPU environment if available; **do not launch H1 Actions/preflight or incur paid compute** to fill the gap.
4. **Unchanged separate hard gates:** actual complete-checkout no-media ten-module tests **NOT RUN**, frozen full-model synthetic parity **NOT RUN**, independent source lock / dependency closure **PENDING**, trusted globally atomic single-use **NOT ESTABLISHED**, measured 12-stage ≤300-minute budget **NOT AVAILABLE**, and written OpenAI Support **#16795041** clearance **PENDING**. No source, scientific or authorization files should be self-approved.

**Assessment remains NO-GO due to insufficient evidence, not proven technical impossibility.** Do not create/edit the blocked launch JSON, dispatch workflows, bypass via Codex/Codespaces/UI, access real P1/P2/P3/protected/Stage-B media, perform real training/inference, spend money, export weights, alter `main`/Production/frozen V8/V9 science, or retry the separately safety-blocked `docs/checkpoints/CURRENT_STATE.md` write.
