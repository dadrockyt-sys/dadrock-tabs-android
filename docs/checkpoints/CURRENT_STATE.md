# CURRENT STATE — V143 contextual-prune / measures 1–16 producer recovery

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`
Historical source commit: `4d735846fbd834cc4c722f2cb48727e4629647f1`
Static-equivalence verifier correction commit: `0da83faf420730cc16bc1af8a89941d3a5d73fd3`
Prior provenance checkpoint commit: `6c74f52c9bb8db64a95907112d1b255fa61e43be`

## Objective

Recover and source-prove the historical V143 measures 1–16 reference-free producer chain, including the raw-attack/onset carrier artifacts and frozen grid/sequence/contextual-prune handoff, without retraining, changing historical thresholds, modifying production, or introducing professional/reference labels at runtime.

The active forensic question is narrower than before: recover enough surviving historical evidence to authenticate the separator/runtime lineage that produced the preserved measures 1–16 raw-attack cache. Do not manufacture equivalence when evidence is missing.

## Current status

### Closed / proven

- Historical first-party measures 1–16 source graph is archived and checksum-manifested.
- Preserved raw/onset artifacts and frozen models are checksum-pinned.
- Repository-side static source/artifact equivalence is PASSING.
- Source audio identity is closed: historical and current refs contain the same Git blob for `public/gomywayfullaitest.m4a`.
- The historical deterministic two-view separator algorithm and thresholds are source-proven.
- A real Aug-16 Codespace-driven Modal GPU dependency smoke **did execute and pass**; an older statement that “the historical GPU smoke was not executed” was too broad and is corrected below.
- The historical direct benchmark WAV SHA-256 has been recovered from the Aug-16 checkpoint.
- The preserved intro raw-attack cache now has a recovered exact file checksum plus exact per-stem and per-sweep event fingerprints.
- Current research evidence independently proves an exact historical Section3 separator **Family B** exists and can be reproduced by one L4 worker while other equivalent workers can produce **Family A**.
- Measures 33–113 research closure remains green and is not being reworked.

### Still open

- Exact original historical BS-RoFormer and Demucs downloaded payload hashes are not authenticated.
- No immutable historical Modal image digest or complete lock of every resolved transitive dependency has been recovered.
- The old seeded repeatability diagnostic source survives, but its historical printed pass-1/pass-2 stem hashes have not been recovered.
- No surviving static artifact found so far directly ties the measures 1–16 raw-attack cache to a known whole-song separator PCM family (A vs B).

Therefore a fresh GPU separator run is **not authorized to be described as a bit-exact historical reproduction**. Any future run must remain separate compatibility evidence unless the missing historical external-dependency/payload provenance is recovered.

No production files were edited. No retraining, threshold tuning, model replacement, deployment, or reference-label runtime dependency was introduced.

## Non-negotiable constraints

- Work only on `v143-contextual-prune-lobo`.
- Do not modify `main` or production.
- Do not deploy or modify live endpoints.
- Do not retrain or retune historical thresholds/tolerances.
- Do not modify frozen models or frozen predictions.
- Do not inject professional/reference labels into runtime/provenance features.
- Do not overwrite preserved historical caches.
- Preserve historical median-onset behavior; do not silently substitute later amplitude-weighted behavior.
- Preserve original historical band boundaries.
- Treat current/mirrored third-party model files as unproven until historical provenance is authenticated.
- Do not call current/fresh separator output “historical bit-exact replay” while external payload/runtime closure remains incomplete.
- Avoid Codespaces unless a specific unrecoverable evidence gap requires it; the current path is GitHub/archaeology only.

## Historical measures 1–16 source/artifact equivalence — PASS

Historical source archive:

`analyzer/v143-intro-1-16-evidence/historical-source-4d735846/`

Preserved Codespace snapshot:

`analyzer/v143-intro-1-16-evidence/codespace-snapshot/`

Verifier:

`analyzer/v143-intro-1-16-evidence/verify_source_artifact_equivalence.py`

Runner:

`analyzer/v143-intro-1-16-evidence/run_source_artifact_equivalence_verifier.py`

Workflow:

`.github/workflows/v143-contextual-prune-equivalence.yml`

Recorded result:

`docs/checkpoints/V143_STATIC_EQUIVALENCE_RESULT.txt`

Current invariants:

```text
status=PASS
raw_attack_count=22270
raw_grid_count=244
onset_count=787
onset_vector_count=4722
grid_feature_count=36
sequence_feature_count=260
contextual_carrier_count=15
runtime_reference_dependency=none
replay_performed=no
production_edits=no
retraining=no
```

The historical timing has `firstBeatInMeasure=3`, so measure 1 starts with only steps 12–15. The exact measures 1–16 grid contains **244 rows**, not a synthetic 256-row rectangle.

## Historical source audio identity — PASS

Historical/current source path:

`public/gomywayfullaitest.m4a`

Historical baseline:

`4d735846fbd834cc4c722f2cb48727e4629647f1`

Git blob at both historical and current research refs:

`5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`

Matching Git blob identity proves byte-for-byte source-audio identity. Changed input audio is ruled out as the explanation for historical/current separator differences.

## Historical raw-attack producer chain

Historical writer:

`analyzer/v143_intro_capture_raw_attack_cache.py`

Historical output path at the source commit:

`public/training/v143-musical-reconstruction-calibration/intro-raw-attack-cache.json`

Source-proven chain:

1. original audio bytes;
2. inspect/validate audio;
3. normalize to WAV;
4. reference-free timing estimate;
5. subdivision grid preserving detected bar phase;
6. deterministic two-view guitar stem bundle;
7. Basic Pitch historical wide-recall sweeps;
8. parse note events;
9. guitar MIDI 40..88 filtering;
10. 0.30-second wide-grid filter;
11. **measures 1–16 filter**;
12. 0.10-second production-grid annotation;
13. direct JSON serialization.

Historical Basic Pitch sweeps:

```python
HISTORICAL_WIDE_RECALL_SWEEPS = (
    ("o030_f020", 0.30, 0.20),
    ("o025_f015", 0.25, 0.15),
    ("o020_f012", 0.20, 0.12),
    ("o015_f010", 0.15, 0.10),
)
```

Call contract also preserves 20 ms minimum note length, 80–1400 Hz frequency range and guitar MIDI 40..88.

### Recovered exact intro raw-attack fingerprint

Preserved cache:

`analyzer/v143-intro-1-16-evidence/codespace-snapshot/intro-raw-attack-cache.json`

SHA-256 from the preserved `SHA256SUMS.txt`:

`698a57b57b47944b61516a6807a0eeb4b13e8096741d0fd6b2c44386e7ac72a9`

Exact filtered raw-event count:

`22270`

Per-stem counts **after measures 1–16 filtering**:

```text
stem0:direct-demucs6s-guitar.wav      11164
stem1:bsroformer-demucs6s-guitar.wav  11106
```

Historical sweep counts:

```text
o015_f010  12776
o020_f012   4979
o025_f015   2830
o030_f020   1685
```

These values are now the strongest surviving intro-specific separator/Basic-Pitch fingerprint. They must not be confused with whole-song Basic Pitch totals.

## Historical deterministic separator contract

The source graph produces exactly two guitar views:

1. direct Demucs6s Guitar;
2. BS-RoFormer Instrumental -> Demucs6s Guitar.

Historical controls:

- deterministic seed 143;
- Demucs shifts 1;
- overlap 0.10;
- segment size 6;
- RoFormer batch size 1;
- direct output `direct-demucs6s-guitar.wav`;
- cascade output `bsroformer-demucs6s-guitar.wav`.

Historical model identifiers:

- `model_bs_roformer_ep_317_sdr_12.9755.ckpt`
- `htdemucs_6s.yaml`

These identifiers are source-proven. Their original downloaded payload bytes remain unauthenticated.

## Aug-16 Codespace / Modal runtime provenance — recovered correction

The Aug-16 separator checkpoint preserves a successful invocation of the historical-era `analyzer/v143_ai_tab_gpu_worker.py` smoke function.

Historical worker/image recipe:

- Modal `debian_slim`;
- Python 3.11;
- FFmpeg;
- `audio-separator[gpu]==0.44.5`;
- NVIDIA L4.

The **Modal smoke test PASSED** and recorded:

```text
cudaAvailable: true
torchVersion: 2.13.0+cu130
torchCudaVersion: 13.0
deviceCount: 1
deviceName: NVIDIA L4
onnxProviders:
  TensorRTExecutionProvider
  CUDAExecutionProvider
  CPUExecutionProvider
audioSeparatorExitCode: 0
```

The checkpoint also records that the local return path was fixed by converting `torch.__version__` and `torch.version.cuda` to plain strings.

### Important correction to earlier checkpoint wording

A separate later GitHub-side smoke wrapper did record `smokeAttempted=false` because credentials were unavailable in that context. That **does not mean no historical-era Modal smoke ever ran**. The Aug-16 Codespace checkpoint is direct surviving evidence that `gpu_smoke()` ran and passed.

This closes an important part of the runtime fingerprint, but it still does **not** provide an immutable Modal image digest, complete resolved transitive lock, or historical pretrained model payload hashes.

## Historical tracked package inventory — partial runtime closure

`analyzer/audio-separation-requirements-20260814.txt` is present at historical source commit `4d735846...`.

It pins a substantial separator environment including:

```text
torch==2.13.0
numpy==2.5.1
scipy==1.18.0
soundfile==0.14.0
demucs==4.1.0
cuda-toolkit==13.0.3.0
nvidia-cuda-runtime==13.0.96
nvidia-cudnn-cu13==9.20.0.48
triton==3.7.1
setuptools==83.0.0
```

This is real historical package evidence and strongly corroborates the smoke fingerprint. It is **not** a complete Modal lock: for example, it does not itself enumerate every package used by the full runtime and cannot authenticate external downloaded model bytes.

## Historical direct benchmark WAV — file SHA recovered

Historical local benchmark path:

`public/separator-benchmark-v2/gomyway-demucs6s-direct-guitar.wav`

Recovered historical **WAV-file SHA-256**:

`5b77a0a5a074256a6538d15fc37487441c574a252c1d759c12e5231c56fdb4b5`

The best Aug-16 frozen-parameter PCM16 Modal comparison had the same 9,324,544 decoded samples and approximately:

```text
RMSE: ~0.003767
peak absolute error: ~0.09409
correlation: ~0.9986526
separator time: ~34.9 s
total remote time: ~35.9 s
GPU: NVIDIA L4
```

It was extremely close but not byte/sample exact under the initial strict gate.

Do not confuse this historical **WAV-file hash** with later canonical **decoded-PCM hashes**.

The companion historical cascade path is known:

`public/separator-benchmark-v2/gomyway-bsroformer-demucs6s-guitar.wav`

but its historical WAV-file SHA has not yet been recovered from surviving Aug-16 evidence.

## Surviving Codespace state — stronger than a hypothesis

The Aug-20 troubleshoot bundle explicitly recorded untracked Codespace state including:

```text
.venv-jimmy311/
analyzer/v143_ai_tab_cpu_provenance.py
analyzer/v143_ai_tab_gpu_worker_historical_defaults.py
analyzer/v143_modal_deterministic_dependency_smoke.py
analyzer/v143_modal_repeatability_diagnostic.py
analyzer/v143_modal_seeded_repeatability_diagnostic.py
analyzer/v143_seeded_audio_separator.py
public/separator-benchmark-gpu-v1/
public/separator-benchmark-v2-forensic-replay/
public/separator-benchmark-v2/
public/v143-modal-replay/
```

Therefore the benchmark/replay directories and diagnostic scripts were genuinely present as local Codespace state; they were not merely inferred from filenames in tracked source.

The old seeded repeatability diagnostic source survives, but targeted Library/repository searches have **not** recovered the actual historical pass-1/pass-2 `carrierA`/`carrierB` hashes that it printed. Do not invent them.

## Later exact-family research evidence — historical Family B

The research artifact:

`debug/v143-contextual-prune/section3-exact-family-provenance-capture.json`

proves exact historical Section3 separator Family B with canonical decoded-PCM SHA-256 values:

```text
direct PCM:
1542856aca8275c727e6c77edd941588aa359b65b8b897c1b3ada2926f2d579e

cascade PCM:
e26f7a430b835adcd7a284db8a18c3aa93632b81e1c1a653eeffa16c02a62bc3
```

Worker 1 of 4 produced Family B in direct/cascade lockstep and then reproduced the exact historical Section3 carrier and frozen scoring outputs:

```text
rowCount: 802
rawEventCount: 20830
candidateClusterCount: 9048
direct stem events: 10625
cascade stem events: 10205
sweep counts: 12211 / 4539 / 2540 / 1540
exact frozen decisions: true
exact base scores: true
exact sequence scores: true
exact keep probabilities: true
```

Workers 2–4 instead produced Family A:

```text
direct PCM:
30cffcc2e472abe6d613b3853295c47b71ae8c4318f8709c8c9d45d69d9351f8

cascade PCM:
68a1c75e59bf45fbae340938e580575c043e7a94a70e7be2361e4c2d4621cb56
```

All workers observed Demucs shift value `6026` for the traced shift call.

This is strong evidence that the same current research recipe can yield two separator output families across nominally equivalent L4 workers. It makes GPU/runtime nondeterminism a credible explanation for the historical/current family split and weakens any assumption that Family A vs B necessarily implies different model payload bytes. It does **not** authenticate the original historical external model payloads by itself.

## Current cross-container runtime fingerprint

`debug/v143-contextual-prune/section3-cross-container-repeatability.json` captured three independent L4 workers with:

```text
torch: 2.13.0+cu130
audioSeparator: 0.44.5
basicPitch: 0.4.0
torch CUDA: 13.0
cuDNN: 92000
GPU: NVIDIA L4
compute capability: 8.9
NVIDIA driver: 580.95.05
```

Important deterministic flags observed after inference:

```text
torch deterministic algorithms: false
cuDNN deterministic: false
cuDNN benchmark: false
CUDA matmul TF32: false
cuDNN TF32: true
```

Those three workers all produced Family A. This is current/research runtime evidence, not proof of the original immutable historical image. It does, however, independently corroborate the Aug-16 smoke generation (`torch 2.13 + CUDA 13 + audio-separator 0.44.5 + L4`).

## Why the intro family link remains open

The historical raw-attack cache provides exact measures 1–16 per-stem Basic Pitch counts, but it does not store whole-song stem WAV/PCM hashes.

The producer source increments `stemEventCounts` only after:

- Basic Pitch event parsing;
- guitar-range filtering;
- wide-grid acceptance;
- measures 1–16 filtering.

Therefore `11164 / 11106` is a strong intro-specific fingerprint, but it cannot be equated directly to the whole-song Section3 Family A/B stem hashes without additional evidence.

Targeted searches for surviving evidence containing the exact intro counts plus a stem hash/family identity did not recover such a link. Likewise, the old seeded repeatability diagnostic’s printed pass hashes were not recovered.

Fail closed: **do not declare the intro cache Family B solely because Section3 later proved Family B.**

## Onset-spectrum and frozen feature mapping

The historical onset cache uses:

- sample rate 22050 Hz;
- hop length 128;
- 36 bins/octave;
- CQT MIDI 28..112;
- guitar MIDI 40..88;
- 30 ms attack clustering;
- 30 ms physical-onset grouping;
- two deterministic views;
- `filter_scale=0.75`;
- `log(abs(CQT) + 1e-9)` substrate;
- historical median-onset clustering.

Spectral windows:

- `attackMax`: -0.020 to +0.045 s, max;
- `earlyMean`: +0.020 to +0.095 s, mean;
- `sustainMean`: +0.070 to +0.180 s, mean.

Frozen dimensional mapping remains source-proven:

```text
base grid: 36
sequence: 260
contextual-prune carrier: 15
```

No professional/reference label is required by the runtime carrier path.

## Replay readiness matrix

| Component | Status | Evidence / blocker |
|---|---|---|
| Historical first-party Python source | PASS | archived + SHA manifest |
| Raw/onset preserved artifacts | PASS | preserved/checksum-pinned |
| Intro raw-attack exact fingerprint | PASS | SHA + 22,270 events + exact stem/sweep counts |
| Frozen grid/sequence/contextual models | PASS | preserved research artifacts |
| Static source/artifact dimensions | PASS | 36 / 260 / 15 verifier |
| Runtime professional/reference dependency | PASS | none in replay carrier |
| Source-audio identity | PASS | same Git blob at historical/current refs |
| Top-level `audio-separator` version | PASS | historical source pins `0.44.5` |
| Aug-16 Torch/CUDA/L4 smoke fingerprint | PASS | `2.13.0+cu130`, CUDA 13.0, L4, ONNX providers, separator CLI exit 0 |
| Historical tracked package inventory | PARTIAL/PASS | substantial Aug-14 package freeze exists; not complete Modal lock |
| Historical direct benchmark WAV file hash | PASS | `5b77a0a5...6fdb4b5` |
| Historical cascade benchmark WAV file hash | OPEN | path known; hash not recovered |
| Complete immutable Modal image identity | BLOCKED | no image digest recovered |
| Original BS-RoFormer payload hash | BLOCKED | filename known; historical bytes/hash not authenticated |
| Original Demucs payload/config payload hash | BLOCKED | identifier known; historical downloaded bytes/hash not authenticated |
| Old seeded repeatability printed stem hashes | OPEN | diagnostic source survives; output not recovered |
| Intro raw-cache -> whole-song separator Family A/B link | OPEN | no surviving direct hash/family link recovered |
| Fresh raw-audio GPU run as bit-exact historical reproduction | DEFERRED | fail closed while remaining lineage is incomplete |
| New fully fingerprinted compatibility comparator | ALLOWED TO PLAN | must be labelled new evidence only |

## Exhausted / do not repeat broadly

Do not restart broad repository archaeology for:

- the 36/260/15 feature widths;
- source audio identity;
- top-level `audio-separator` version;
- whether any Aug-16 Modal smoke ever ran;
- whether local Codespace separator benchmark/replay directories existed;
- Section3 Family B exact proof;
- 33–113 surviving-band closure.

Those questions now have surviving evidence.

## Immediate next safe operation

Continue **without Modal** and search only for a surviving intro-specific separator-family bridge, for example:

1. a historical `direct-demucs6s-guitar.wav` or cascade hash recorded near the intro capture;
2. a Basic Pitch prediction-cache fingerprint tied to a known stem hash;
3. an Actions artifact/log from the Aug-18 seeded repeatability run containing its printed `carrierA` / `carrierB` SHA values;
4. a surviving file in the Library/checkpoints that records the intro `11164 / 11106` counts together with a whole-song stem identity.

If no such evidence survives after these targeted searches, stop archaeology rather than broad-searching again. Record the gap explicitly: the intro producer chain and output cache are statically proven, but the final raw-audio-to-separator-family bit lineage cannot be independently authenticated from surviving static evidence.

Only after that evidence status is written should a controlled compatibility comparator be considered. Such a comparator must capture fresh model payload hashes, full package/runtime inventory, CUDA/cuDNN/Torch/ONNX details, input Git/blob SHA, separator command/config, seed/shift trace, output WAV and decoded-PCM hashes, intro Basic Pitch event fingerprints, and frozen downstream outputs. It must remain isolated research evidence and must not overwrite historical artifacts.

## Resume directive

Continue GitHub-only on `v143-contextual-prune-lobo`.

The exact place to resume is the **targeted intro separator-family bridge search** described above. The Aug-16 runtime smoke, direct benchmark WAV SHA and intro raw-attack fingerprint are now recovered and should not be rediscovered. Do not run Modal. Do not modify production. If the surviving intro bridge cannot be found, create a formal evidence-gap checkpoint and move to a separately labelled compatibility-comparator design rather than weakening the historical claim.
