# Astra H1 Phase 11D — exact historical prepared-frame recovery and feasibility revision

**Date:** 2026-10-09. **Branch:** `astra-work`. **Feasibility disposition: `NO_GO_INSUFFICIENT_EVIDENCE`** pending actual measured runner capacity, resource peaks, complete time bound and independent technical/safety review. **Real H1 training launch remains BLOCKED** pending written OpenAI Support case **#16795041** outcome and all other gates. This phase did NOT launch new Actions, train/infer with models, use paid compute, access original media, alter the frozen H1 workflow, or generate its blocked training-launch JSON.

## Major discovery: existing scalar-only artifact closes full frame-count gap

A previously authorized **zero-optimizer fixed-output admission audit** had already evaluated **every one of the frozen 256 accepted P1/P2 development captures**. Its published scalar result is `docs/astra/GUITARTECHS_POST_V9_FIXED_OUTPUT_ADMISSION_RESULT_V1.json` (Git blob **`bb6e2d6c21fb545145af4925b81c3697dddd2f29`**) with run **37836761676**, job **113515647380**, manifest SHA256 **`2b6851a5c0f1639f84df987372985e4d26ca34ad9e281d84f8c686531fdccf4c`**. The GitHub historical artifact **11580776876** was verified by its workflow upload declaration to contain **only** `post-v9-admission-audit-v1.json` (no media, weights or raw logits); ZIP size **175,276 B**, uncompressed JSON **1,185,612 B**. The two exact SHA256 identities were independently checked after a **read-only download of this scalar-only artifact**:
- ZIP **`3e7d59b40d6311c800a0a5ee85f4ef90a38a0f8d6a17351578108f292604079b`**.
- JSON **`5dbc876c3b77be3dff1f42b52e33f1955a8b96356aff08452e2fa9116aab6f94`**.

The frozen audit source `astra_backend/guitartechs_training_v9/post_v9_output_admission_audit_v1.py` (Git blob **`8e4cf8a6aa052d0703fc69128a387de8eb2bf6d5`**) verifies the exact 256-key manifest and each feature/label hash; `infer_raw()` allocates its state buffer for **`feature.shape[1]`** positions, and `summarize_capture()` reports `frames=state.shape[0]`. The preparer `astra_backend/guitartechs_real_training/real_training.py` (blob **`d4a3dd99c4a2c3cda16c10bde1a5dc63f6380254`**) writes `(192,F)` float32 CQT and `(6,F)` int16 labels with the same `F`, and writes the original full accepted source key in the manifest. The artifact records a SHA-256 hash of each key rather than raw media.

**Checks actually completed, without reexecuting the model:** For **all 256 captures**, recomputed SHA256 of the **256 frozen accepted scalar keys** in `docs/astra/GUITARTECHS_PRIMARY_ALIGNMENT_CORRECTIONS_V1.json` (Git blob **`9090d465422ebf5d4fdf170693fe0936934f3073`**), matched **256/256** artifact key hashes (no missing or duplicate), enforced fold identity and counts (**P2 120, P1 136**), verified every capture's `validPositions+maskedPositions=6×frames`, and verified **V8 and V9 recorded the same frame count** for every key. Independently reconciled fold sums (**901,390 + 1,023,415 = 1,924,805**) against the published result's `stringPositions` (**11,548,830 = 6×1,924,805**) and verified the stored manifest SHA256 and zero-optimizer guard.

**This resolves exact historical prepared-array frames across the entire accepted population**, even though the original MP3 file durations were never recorded. No MP3 durations were estimated or media queried.

| Historical verified scalar | Value |
| --- | ---: |
| Accepted captures, all views | **256** |
| P2 validation frames, 120 captures | **901,390** |
| P1 validation frames, 136 captures | **1,023,415** |
| **All accepted prepared frames** | **1,924,805** |
| Largest single accepted CQT capture | **23,773 frames** |
| Smallest accepted capture | **2,066 frames** |
| Median accepted capture | **6,889 frames** |
| **Float32 features + int16 labels payload (780×F)** | **1,501,347,900 B = 1.398 GiB** |
| Missing original MP3 file durations | **Still unknown**, but **no longer needed** to calculate the exact prepared-array payload |

### Exact source-key-matched by-archive prepared frames

| Archive | Captures | Exact prepared frames | Exact feature+label array payload |
| --- | ---: | ---: | ---: |
| P1_chords.zip | 84 | 580,707 | 452,951,460 B |
| P1_scales.zip | 47 | 323,845 | 252,599,100 B |
| P1_singlenotes.zip | 3 | 71,317 | 55,627,260 B |
| P1_techniques.zip | 2 | 47,546 | 37,085,880 B |
| P2_chords.zip | 72 | 488,811 | 381,272,580 B |
| P2_scales.zip | 43 | 295,095 | 230,174,100 B |
| P2_singlenotes.zip | 3 | 71,316 | 55,626,480 B |
| P2_techniques.zip | 2 | 46,168 | 36,011,040 B |
| **ALL** | **256** | **1,924,805** | **1,501,347,900 B** |

Views: directinput **80 captures/623,554 frames**, micamp **78/604,432**, ego **52/370,409**, exo **46/326,410**. This resolves the **98 accepted ego/exo frame counts** specifically, without reconstructing their original MP3 lengths.

## Updated deterministic overlap ledger — previous duration scenarios superseded for array payload

Combining the new **per-archive exact prepared frame counts** with existing independently reconciled historical archive ZIP/extraction logical sizes (`astra-work/H1_HISTORICAL_INVENTORY_RECOVERY_2026-10-09.json`, Git blob **`5706ac4ed1a9590fa74f7644e6be7e642ffb9db2`**) and **the exact archive sequence in the dormant H1 workflow** (`.github/workflows/guitar-techs-h1-20epoch-paired-pilot.yml`, Git blob **`90e8168fc1ca40738ba07291ca1001a36718f4e3`**) gives:

- ZIP+extraction phase = **retained prior prepared-array payload + current compressed ZIP bytes + current historical extracted visible-file logical bytes**.
- End-of-preparation phase = **retained prior prepared-array payload + current historical extracted bytes + current archive's exact prepared-array payload**; current ZIP is already deleted.
- After archive cleanup = **retained prior prepared-array payload + current archive's exact prepared-array payload**, with extracted files removed.

The largest modeled identifiable stage remains **P2_chords.zip ZIP+extraction**, now **`798,263,700 + 1,150,819,056 + 2,442,840,341 = 4,391,923,097 bytes ≈4.090 GiB`**, with no hypothetical MP3 duration assumptions. This is **source-backed historical logical overlap**, NOT a measured physical disk high-water mark or a proven upper bound: it excludes 512 NPY headers, filesystem blocks, package/runtime caches, repository, incidental temp copies, download partials, output artifacts, reserve and **actual free disk**. Other historical extraction sizes are still prior inventory logical-file sizes, not an H1 runner free-space measurement. The earlier Phase 11C hypothetical 1–15 minute MP3 duration scenarios are now **superseded only for predicting the prepared-array payload**; their warnings about unmeasured disk overhead remain valid.

Machine receipt: **`astra-work/H1_PHASE11D_EXACT_STAGE_CAPACITY_2026-10-09.json`** (Git blob **`e8375ec0cd132eadda93456a023df77a88153eda`**). Original per-capture hashed records were **not re-committed**; only group aggregates were saved.

## RAM array sizes from actual longest capture, not peak resident memory

For verified maximum **F=23,773** frames, the identifiable individual arrays in the historical CPU evaluation source occupy:

| Identifiable array | Computed bytes |
| --- | ---: |
| Padded CQT `(192,F+8)` float32 | **18,263,808** |
| State `(F,6,21)` float32 | **11,981,592** |
| Event `(F,6)` float32 | **570,552** |
| One `state.astype(float64)` copy | **23,963,184** |

These are **individual allocations, not a jointly verified peak**; some may overlap, and other simultaneous temporary arrays exist. The H1 V4 full-fold evaluations, torch/Adadelta/activation buffers, FFmpeg decoded PCM, librosa VQT temporaries, worker/OS memory and resident page cache lack measured maxima. A **nominal 16 GB RAM** specification cannot close the RAM gate.

## Additional historic runtime risk evidence, reconciled without training

Reviewed all **ten** original V9 segment-job logs in run **37573544151**, spanning **80 archived preparation completion receipts**; produced `astra-work/H1_PHASE11D_V9_HISTORICAL_PREP_TIMINGS_2026-10-09.json` recording each job ID, UTC start and completion, capture-count reconciliation and archive gaps. Historical preparation interval measured from shell `mkdir -p /tmp/prepared /tmp/extract` to the eighth prepared-archive receipt: **minimum 1,551.280 seconds (25.855 min)**, **maximum 3,416.914 seconds (56.949 min)**, median **2,036.9135 seconds (33.9486 min)**, **2.203× max/min variation**. These observational V9 intervals reflect archive download/verify/extract/prepare and are **not** end-to-end H1 measurements or hard upper bounds. The prior **3,429.715-second maximum** used a different V9 job-step log interval boundary; the two numbers should not be conflated or treated as conflicting exact stage definitions. Ten checked V9 job logs contained **no explicit `df` free-disk high-water, `du` usage or `VmHWM`/peak-RSS memory telemetry**; repeated apt message **“202 MB additional disk space”** is a *package-install estimate*, not actual runner free space or peak allocation.

## Reproducible offline-only verification

- Checker `astra-work/h1_offline_recover_prepared_frames_v1.py` — exact locally tested Git blob **`bf4309a92736c4e8c27a0ef4e2bf1a54be8e4029`**; accepts an **already-downloaded exact SHA-verified** scalar-only historical ZIP and locally available frozen accepted-key and published-summary JSON; neither downloads data nor imports model code.
- Test `astra-work/test_h1_offline_recover_prepared_frames_v1.py` — exact locally tested blob **`768eefaee6eca9b876fd52724542219ba9e19574`**.
- Group-only exact frame receipt `astra-work/H1_PHASE11D_EXACT_PREPARED_FRAME_RECOVERY_2026-10-09.json` — exact locally generated Git blob **`701d4626de0e04200534ed17827db00c896a3d6b`**. Local accepted-key list was reconstituted from the frozen GitHub JSON's **81 accepted performance/view groups**; this was independently validated by **all 256 SHA256 capture-key matches** to the archived scalar JSON. A future run with the untouched original repo accepted-key JSON is preferable for independent reproducibility; not falsely claimed in this session.
- Historical exact stage ledger `astra-work/H1_PHASE11D_EXACT_STAGE_CAPACITY_2026-10-09.json` — blob **`e8375ec0cd132eadda93456a023df77a88153eda`**.
- Actually ran local Python **3.13.5** pure-scalar verification **9/9 tests PASS, 0 failures/errors**, with `py_compile` PASS. Final test log SHA256 **`1f367c1a3aa96aef7ef857a8f57dd1d83d969b06852bc945e7b036d025ff4fea`**. Deliberate initial negative synthetic test uncovered and fixed an empty-bucket aggregation problem before the final pass; the exact tested corrected bytes were committed.

### Next exact independent gates

1. Obtain independently reviewed *effective* public GitHub runner **free SSD** (not nominal capacity), preinstall/package/source/FFmpeg/VQT disk footprint, NPY header+allocation size, prepared-array/temporary overlap and failure reserve. Use measured historical log evidence or **permitted scalar-only independent runner instrumentation**, not a real-data H1 preflight; do not self-authorize any Actions.
2. Produce a justified **peak CPU RAM** upper bound, accounting for decoded waveform, VQT intermediate materialization, per-capture V4 decoder and float64 buffers, Torch full model/Adadelta and Python/system overhead. Exact Fmax enables shape arithmetic but is insufficient without transient/activation evidence.
3. Complete all **12 provenance-bearing wall-time stages** and a real safe reserve under **≤18,000 sec**, not just historical V9 183.719-minute proxy or the 56.949-minute observed V9 preparation. H1 evaluation and setup remain unverified.
4. In a genuinely permitted **complete checkout** and frozen Python **3.10.15 / Torch 1.11.0+cpu / NumPy 1.21.6** environment, execute the authentic H1 no-media unit tests, source closure and **synthetic-only full-model parity**; still NOT RUN. Obtain independent source identity and globally durable atomic single-use approval. No H1 job/launch JSON or media to collect evidence.
5. Await explicit **written OpenAI Support case #16795041** decision; retain **NO-GO** until both platform/safety and independently evidenced technical gates are satisfied. Keep the blocked launch JSON absent and do not retry the separately prohibited `docs/checkpoints/CURRENT_STATE.md` write.

**STOP:** No actual H1 Actions/preflight/training, media acquisition/decoding, alternative-tool bypass, real optimizer or inference, paid compute, P3/protected/Stage-B, weights export, `main`/Production/frozen V8/V9 science changes. This phase is read-only prior scalar artifact recovery and offline calculations **only**.
