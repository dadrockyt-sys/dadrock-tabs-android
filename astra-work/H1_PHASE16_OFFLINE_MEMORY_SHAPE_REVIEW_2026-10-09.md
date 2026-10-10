# Astra H1 Phase 16 — source-backed, model-free memory shape review

**Date:** 2026-10-09. **Branch:** `astra-work`. **Disposition: `NO_GO_INSUFFICIENT_EVIDENCE`.** Offline-only source inspection, deterministic integer shape arithmetic and pure-synthetic tests. The dormant H1 launch and media-based preflight are **NOT AUTHORIZED** pending explicit written OpenAI Support case **#16795041** and independently verified feasibility/source/one-use controls. No GitHub Actions dispatched, media acquired, Torch/model imported, inference or optimizer performed, paid compute or blocked launch JSON created.

## Starting point: Phase 15 paper integration is already complete

Prior branch HEAD before this work **`06e4ede7f54e3f830331189ff4b49aedb347a98b`** had closed the entire original three-JSON local paper integration gap: Phase 12/13/15 **22 PASS / zero skips** using all three exact original Git blobs, with `BLOCKED_MISSING_EVIDENCE` and **19 missing** items. See `astra-work/H1_PHASE15_ORIGINAL_TRIPLE_INTEGRATION_2026-10-09.md`. In this phase that combined 22-test suite was **rerun on the same exact pinned scalar files** before adding 10 new shape tests. The inability to perform a **complete repository checkout** (GitHub DNS from this sandbox), genuine full H1 no-media ten-module suite or real runner measurement remains unchanged.

## New source-backed static shapes at historical Fmax = 23,773

Existing Phase11D authorized scalar-only historical audit established **1,924,805 prepared frames in 256 accepted captures**, largest accepted capture **Fmax=23,773**, and combined float32 feature + int16 label payload **1,501,347,900 bytes (1.398 GiB)**. This is true historical prepared-array payload; **not** a runtime RAM high-water.

Read-only original source evidence, checked through GitHub on branch `astra-work`:

| Read-only source | Exact Git blob | Relevant code |
| --- | --- | --- |
| `astra_backend/guitartechs_training_v9/post_v9_output_admission_audit_v1.py` | `8e4cf8a6aa052d0703fc69128a387de8eb2bf6d5` | `infer_raw`: padded CQT, (F,6,21) float32 state, (F,6) float32 event, chunked 512-frame contiguous windows; `summarize_capture`: float64 state clipping and entropy temporaries |
| `astra_backend/guitartechs_training_v10/h1_pilot_core_v1.py` | `2bf8085b6cd69214d5e2ec198d80c40b35d13875` | H1 `evaluate` uses `infer_raw` and V4 admission; paired 200-frame training view and one retained-gradient probe per arm |
| `astra_backend/guitartechs_training_v2/train_v2.py` | `4db5add96c58a8e54868ea06dacb1da724675163` | 200×192×9 contiguous float32 per-window input and `np.pad` full prepared CQT |
| `astra_backend/guitartechs_training_v9/paired_view.py` | `9b704ea9c5bf153197dfde260c1b995142d062b5` | Two tensor training views, with `.clone()`, gain/tilt/noise workspaces and separate forward/backprop graphs |
| `astra_backend/guitartechs_real_training/real_training.py` | `d4a3dd99c4a2c3cda16c10bde1a5dc63f6380254` | `ffmpeg` decoded PCM stdout is captured, `np.frombuffer(...).copy()` makes another waveform allocation, VQT preparation operates on decoded entire capture |
| `astra_backend/tabcnn_runtime/preprocessing.py` | `e1d251a341b811b1b8e2df97d78b754d3379046b` | 22,050 Hz/512 samples hop, 192 VQT bins, nine-frame convolutional context |

At **Fmax=23,773** the **individually identifiable** allocation shapes have exact byte payloads:

| Independent source-shape array or buffer | Bytes | MiB |
| --- | ---: | ---: |
| Original float32 `(192,F)` feature payload | 18,257,664 | 17.412 |
| Original int16 `(6,F)` label payload | 285,276 | 0.272 |
| Evaluation padded float32 `(192,F+8)` CQT | **18,263,808** | **17.418** |
| Full float32 `(F,6,21)` state probabilities | **11,981,592** | **11.427** |
| Full float32 `(F,6)` event scores | **570,552** | **0.544** |
| **One** float64 copy of full state `(F,6,21)` | **23,963,184** | **22.853** |
| Maximum 512-frame contiguous eval model input `(512,192,9)` float32 | **3,538,944** | **3.375** |
| One 200-frame `(200,192,9)` float32 training input | **1,382,400** | **1.318** |
| Two training input view payloads, before augmentation temporaries | **2,764,800** | **2.637** |

**Important:** These are individual payload sizes (some coexist, some do not); simply summing them is **NOT** a measured or defensible upper bound on process peak RSS or total RAM. `np.clip(state.astype(float64))`, `np.log`, multiplication, class reduction, thresholding/decoding, Torch convolutional activations, autograd, Adadelta optimizer states, CPU allocator overhead and page cache can introduce additional simultaneous resident storage. The upstream TabCNN convolutional parameter/activation footprint was **not independently fully evaluated** in this local environment, and pinned Python3.10/Torch1.11 model parity was **not** run.

### FFmpeg/VQT preparation: critical unknown

The source runs ffmpeg `-f f32le -ac 1 -ar 22050 ... pipe:1`; it retains captured decoded PCM bytes during `np.frombuffer(stdout,dtype='<f4').copy()`. This implies **overlapping bytes+NumPy copy**, but a precise waveform length cannot be established from Fmax solely because resampling, VQT padding, and original audio duration differ. The offline checker separately reports a **nominal** `F×512×4` PCM scenario and `2×F×512×4` pipe+copy scenario, explicitly marked *not actual decoded audio lengths or upper bounds*. VQT temporary stack and runtime worker memory remain **UNMEASURED**.

## Actual code and tests added

- `astra-work/h1_offline_memory_shape_review_v1.py`, Git blob **`3487ac157337c52d607630722e2317c4efe39825`**. Standard-library `argparse/json` and exact integer arithmetic only. Source identity annotations from GitHub read-only inspection; sets `localPinnedSourceFilesVerifiedByThisModel=false`, `completePeakRamBoundEstablished=false`, `runnerEffectiveAvailableRamMeasured=false`, `twelveStageH1TimeBoundEstablished=false` and `launchPermission=false`. Imports **no** NumPy, Torch, librosa, audio, network or model code.
- `astra-work/test_h1_offline_memory_shape_review_v1.py`, Git blob **`dd166a32cfe64608879ba198bb06ec5e8d10bed6`**. **10 PASS / 0 failures** synthetic regression methods covering exact array shapes, 512-frame evaluation chunk, paired training input, PCM caveat, source-identity fields, invalid scalar inputs and non-authorization.
- `astra-work/H1_PHASE16_MEMORY_SHAPES_2026-10-09.json`, Git blob **`c8f1321671d4e2d7624f181771e2079786994063`**, exact locally generated program output.
- Local commands (no complete checkout required): `cd /mnt/data/astra_phase16 && python -m unittest -v test_h1_feasibility_review_offline_v1 test_h1_phase13_original_receipts_integration_v1 test_h1_phase15_relative_cli_v1 test_h1_offline_memory_shape_review_v1`; **32 PASS / zero skipped / zero failures**, local **Python 3.13.5**, `py_compile` PASS. Exact combined log SHA256 **`a4921701e0b9343f4a10e3a49913f8746b378ad490aed8907b94f9b96dbf6703`**. Exact tested source and new JSON Git object identities matched uploaded remote files. All 4 Phase15 paper integration source files used in local combined suite still have their original expected pinned Git hashes.

## Independent remaining measurement contract

1. **Actual comparable CPU runner evidence** (only in an expressly permitted non-media synthetic-only environment): GitHub hosted `ubuntu-22.04` image identity, effective free disk bytes after pinned Python/torch/librosa/AMT-Tools staging, peak additional physical disk (including all eight sequential archives and preparation/working files), headroom and disk reserve. Existing historical 4.090 GiB **identifiable logical overlap** excludes package/cache/artifacts, filesystem blocks and transients, so is **not a peak**.
2. **Actual memory high-water and upper-bound review**: measure or conservatively bound waveform bytes+copy and VQT workspaces for **Fmax=23,773**, per-capture evaluation (up to 512-frame chunk) plus full state/V4 float64 admission, Conv/GRU activations, double-paired training backprop/gradient probe, Adadelta state and system page cache. Record actual `VmHWM`/RSS plus runner total/available memory, reserve and an evidence run SHA256. The 16 GB nominal hosted RAM specification is not a measured resident margin.
3. **Twelve attributable stage-time upper bounds**, not averages or historical analogues: environment/deps, source, archive+preparation, four 20-epoch training arms, four full V4 fold evals, artifact/cleanup+failure reserve, **≤18,000 seconds** on CPU; actual H1 bounds still unavailable. Historic V9 183.719-min illustration and 25.86–56.95-min prep observations are **not valid H1 upper bounds**.
4. **Technical and safety approvals separately remain STOP**: actual complete-checkout H1 no-media suite not run, frozen Python3.10.15/Torch1.11.0+cpu/NumPy1.21.6 synthetic-only parity not run, source/dependency import closure and immutable lock not independently approved, durable global atomic single-use not established, written OpenAI Support #16795041 clearance not received. All **19 Phase15 paper worksheet evidence entries still MISSING**.

**No new real H1 feasibility test, preflight, training, GPU, paid compute, protected real P1/P2/P3/Stage B media, optimizer/inference, weights or source/protocol changes were made.** Keep the blocked `docs/astra/GUITARTECHS_H1_20EPOCH_PAIRED_PILOT_TRAINING_LAUNCH_V1.json` absent, do not route around this via Codespaces/Codex/Actions, and do not retry separately blocked `docs/checkpoints/CURRENT_STATE.md` write. **Current decision remains `NO_GO_INSUFFICIENT_EVIDENCE`; this additional shape ledger is useful preparation only.**
