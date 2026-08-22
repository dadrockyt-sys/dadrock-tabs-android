# CURRENT STATE — V143 contextual-prune / measures 1–16 producer recovery

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`
Historical source commit: `4d735846fbd834cc4c722f2cb48727e4629647f1`
Prior recovery checkpoint: `412208c946737e9902ab78a19db5fa48c439fdd7`
Static-equivalence verifier correction commit: `0da83faf420730cc16bc1af8a89941d3a5d73fd3`

## Objective

Recover and source-prove the deterministic historical V143 measures 1–16 reference-free pipeline, including the preserved raw-attack/onset carrier caches and frozen grid/sequence/contextual-prune model handoff, without retraining, changing historical thresholds, modifying production, or introducing professional/reference labels at runtime.

## Current status

The source/artifact/feature/model chain is now statically source-proven and the repository-side equivalence verifier is PASSING.

The source-audio cross-ref gate is also closed: `public/gomywayfullaitest.m4a` at historical baseline `4d735846fbd834cc4c722f2cb48727e4629647f1` and on `v143-contextual-prune-lobo` resolves to the same Git blob SHA, `5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`. Because Git blob identities are content-addressed, this proves the historical and current research refs contain byte-for-byte identical input audio. Changed source audio is therefore ruled out as the cause of any historical/current separator replay difference.

A fresh raw-audio GPU replay is **not yet authorized as a bit-exact historical reproduction**. The remaining blocker is external runtime closure: the historical first-party Python graph is archived and checksum-manifested, but the exact resolved third-party environment and pretrained separator model payload bytes used by the historical Modal run were not preserved strongly enough to authenticate bit-identical regeneration.

No production files were edited. No analyzer retraining, threshold tuning, model replacement, deployment, or reference-label runtime dependency was introduced.

## Preserved evidence

Historical source archive:

`analyzer/v143-intro-1-16-evidence/historical-source-4d735846/`

Preserved Codespace snapshot:

`analyzer/v143-intro-1-16-evidence/codespace-snapshot/`

Important preserved artifacts include:

- `intro-raw-attack-cache.json`
- `intro-onset-feature-cache.json`
- `v143_intro_learned_grid_event_selector_model.json`
- `v143_intro_sequence_event_model.json`
- `v143_contextual_prune_model.json`
- historical source manifest / `SHA256SUMS.txt`

The preserved raw/onset artifact identities are checksum-pinned. Earlier source reads also established the raw-attack/onset producer chain, deterministic two-view guitar stem contract, timing adapter, onset grouping, CQT settings/windows, and exact 36-feature base-grid assembler.

## Static source/artifact equivalence — PASS

Verifier:

`analyzer/v143-intro-1-16-evidence/verify_source_artifact_equivalence.py`

Runner:

`analyzer/v143-intro-1-16-evidence/run_source_artifact_equivalence_verifier.py`

Workflow:

`.github/workflows/v143-contextual-prune-equivalence.yml`

Recorded result:

`docs/checkpoints/V143_STATIC_EQUIVALENCE_RESULT.txt`

Current PASS invariants:

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

### Verifier-only correction already committed

Commit:

`0da83faf420730cc16bc1af8a89941d3a5d73fd3`

Message:

`Verify historical partial intro grid exactly`

The historical source/artifacts/models were not changed. The runner patches two verifier assumptions in memory:

1. valid subdivision `step == 0` must not be converted to `-1` by an `or -1` fallback;
2. the historical intro grid is not a synthetic 16 x 16 = 256-row rectangle.

The historical timing has `firstBeatInMeasure=3`, so measure 1 begins partway through the bar and contains only steps 12–15. The exact source-faithful measures 1–16 grid therefore contains **244 rows**.

The runner reconstructs the expected grid directly from cached `timing.beatTimes` plus `firstBeatInMeasure` and compares ordered `globalStep`, `measure`, `step`, and `timeSeconds` values with absolute tolerance `1e-12`.

## Historical raw-attack producer chain

Historical writer:

`analyzer/v143_intro_capture_raw_attack_cache.py`

Historical output:

`public/training/v143-musical-reconstruction-calibration/intro-raw-attack-cache.json`

Source-proven chain:

1. original audio bytes;
2. inspect/validate audio;
3. normalize to WAV;
4. estimate reference-free timing;
5. build subdivision grid preserving detected bar phase;
6. build deterministic two-view guitar stem bundle;
7. run historical Basic Pitch wide-recall sweeps;
8. parse note events;
9. guitar-range filtering;
10. wide-grid filtering;
11. measures 1–16 filtering;
12. production-grid tolerance annotation;
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

Basic Pitch call contract recovered from historical source:

- caller-supplied onset threshold;
- caller-supplied frame threshold;
- minimum note length: 20 ms;
- minimum frequency: 80 Hz;
- maximum frequency: 1400 Hz;
- guitar MIDI range: 40..88.

## Deterministic historical guitar-view contract

The historical graph produces exactly two guitar views:

1. direct Demucs6s Guitar;
2. BS-RoFormer Instrumental -> Demucs6s Guitar.

Historical deterministic controls include:

- seed 143;
- Demucs shifts 1;
- overlap 0.10;
- segment size 6;
- RoFormer batch size 1;
- direct output `direct-demucs6s-guitar.wav`;
- cascade output `bsroformer-demucs6s-guitar.wav`.

Historical separator model names observed in source:

- `model_bs_roformer_ep_317_sdr_12.9755.ckpt`
- `htdemucs_6s.yaml`

These names are source-proven; the exact historical external model payload bytes are not independently archived/authenticated.

The grading/benchmark archaeology also identifies the historical best GPU path as the two-stage `bsroformer-then-demucs6s` stem. This identifies the intended algorithmic path but does not authenticate the downloaded model payload bytes.

## Historical onset-spectrum producer chain

Historical writer:

`analyzer/v143_intro_capture_onset_spectrum_cache.py`

The source consumes the original audio, reference-free raw-attack clusters and the same deterministic two-view stem bundle.

Recovered historical settings include:

- sample rate 22050 Hz;
- hop length 128;
- 36 bins/octave;
- CQT MIDI range 28..112;
- guitar MIDI range 40..88;
- 30 ms attack clustering;
- 30 ms physical-onset grouping;
- exactly two deterministic views;
- CQT `filter_scale=0.75`;
- stored substrate `log(abs(CQT) + 1e-9)`.

Per-onset spectral windows:

- `attackMax`: -0.020 s to +0.045 s, max reducer;
- `earlyMean`: +0.020 s to +0.095 s, mean reducer;
- `sustainMean`: +0.070 s to +0.180 s, mean reducer.

The historical onset-cache chain uses the median-onset clustering behavior preserved in the archived source. Do **not** replace it with the later amplitude-weighted carrier onset behavior during historical replay.

## Base-grid feature mapping

Authoritative historical assembler:

`analyzer/v143_intro_learned_grid_event_selector.py`

The base grid feature vector is exactly **36 values**.

The mapping includes nearby-onset support/evidence fields, three seven-value two-view spectral summaries (`attackMax`, `earlyMean`, `sustainMean`), and final 16-step phase terms:

- `sin(2π * step / 16)`
- `cos(2π * step / 16)`

Each seven-value spectral summary emits:

1. mean;
2. standard deviation;
3. top1;
4. top1 - top2;
5. view-A L2;
6. view-B L2;
7. two-view cosine correlation.

The three base view-correlation feature columns are 19, 26 and 33 and are neutralized in the preserved correlation-safe base model.

## Sequence model mapping

The frozen sequence vector width is exactly **260**:

```text
6 * 36 base-grid windows = 216
+ 3 current score fields
+ 14 local-delta fields
+ 6 local aggregate fields
+ 5 same-step peer aggregate fields
+ 8 modulus-group fields
+ 8 adjacent-measure aggregate fields
= 260
```

This mapping was re-read from archived `v143_intro_sequence_event_model.py` and is covered by the static equivalence PASS.

## Contextual-prune carrier mapping

The contextual-prune runtime consumes exactly **15 carrier features** derived from base/sequence scores, reference-free evidence, step phase, and neighboring/recurrent base events.

Historical runtime source:

`v143_contextual_prune_runtime.py`

No professional/reference label is required by the runtime carrier path.

The frozen contextual model construction also preserves neutralization of the six correlation-diagnostic base fields used for safety/diagnostic separation. Do not re-enable them during replay or tuning.

## Dependency closure audit

### Closed: first-party source graph

The historical source archive includes checksum-manifested local copies of the relevant V143 Python modules, including the seeded/deterministic separator path, Modal endpoint/worker path, timing adapter, reference-free timing, onset diagnostic and frozen-model consumers.

Examples explicitly present in the source manifest include:

- `v143_seeded_separator.py`
- `v143_production_separator.py`
- `v143_modal_live_endpoint.py`
- `v143_ai_tab_gpu_worker.py`

Therefore the local Python source side is sufficiently preserved for archaeology.

### Partially closed: top-level separator package and historical Modal image recipe

Historical Modal source directly pins:

`audio-separator[gpu]==0.44.5`

The archived GPU worker/image source establishes the following historical execution contract:

- Modal `debian_slim` base;
- Python 3.11;
- `audio-separator[gpu]==0.44.5`;
- `ffmpeg` installed in the image;
- NVIDIA L4 GPU target;
- 8 GB memory allocation.

The historical smoke function was explicitly designed to capture device/package details including CUDA/Torch/ONNX/runtime information, but the preserved smoke record reports that the smoke was not actually executed (`smokeAttempted=false`). Therefore those intended diagnostics cannot be treated as a captured runtime fingerprint.

A historical GitHub-side replay log reports Python `3.11.16`, but that run verified preserved artifacts rather than regenerating the separator stem from raw audio. It therefore does not establish that `3.11.16` was the exact Python patch version inside the original Modal separator execution.

The runtime image does not preserve a complete resolved lock/freeze. Important packages required underneath the worker/separator stack could resolve through transitive/floating dependencies on a fresh build.

No preserved `pip freeze`, complete package lock, exact Torch/CUDA/ONNX inventory or immutable Modal image digest has been recovered.

### Open blocker: external pretrained model bytes

The historical source names the BS-RoFormer and Demucs model/config identifiers, but the corresponding pretrained payload bytes were not copied into the historical source archive and no historical SHA-256 for those model files has been recovered.

Repository archaeology found no tracked copy of the relevant pretrained model payloads and no preserved model-download hash record sufficient to authenticate them.

Do not substitute a current public mirror hash and call it historical provenance. A modern mirror may be useful for comparison later, but it is not evidence that the historical `audio-separator==0.44.5` download produced identical bytes.

The separator can dynamically obtain models/metadata, so model filename alone is not a bit-exact replay guarantee.

### Historical logs and generated benchmark artifacts checked

Historical runtime-replay and Modal smoke records were inspected along with the preserved evidence bundle and checkpoint lineage.

Important findings:

- the historical runtime replay represented artifact-level replay/verification rather than a newly captured raw-audio separator regeneration;
- the Modal smoke path was skipped because required credentials were unavailable;
- therefore those logs do **not** provide the missing separator-model download hashes or a resolved GPU environment fingerprint;
- the generated GPU benchmark report expected by the grader is not preserved on the current branch;
- the current branch retains grading/consumer logic identifying the `bsroformer-then-demucs6s` winner, but does not retain enough generated benchmark output to infer immutable external dependency bytes;
- the preserved Codespace snapshot contains analyzer caches/models/reports plus provenance/checksums, but no complete environment freeze or separator download log has been found.

## Source audio provenance — PASS

Historical producer source references:

`public/gomywayfullaitest.m4a`

Historical baseline:

`4d735846fbd834cc4c722f2cb48727e4629647f1`

Current research branch:

`v143-contextual-prune-lobo`

Git blob at both refs:

`5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`

The same Git blob SHA is returned at both refs. Git blob IDs are content-addressed over the blob contents, so matching blob IDs prove byte-for-byte identity of the source audio even though the byte size was not separately surfaced by the connector during this audit.

This closes the input-audio identity gate and rules out changed source bytes as the cause of any historical/current replay divergence.

## Replay readiness matrix

| Component | Status | Evidence / blocker |
|---|---|---|
| Historical first-party Python source | PASS | archived + SHA manifest |
| Raw/onset preserved artifacts | PASS | preserved/checksum-pinned |
| Frozen grid/sequence/contextual models | PASS | preserved research artifacts |
| Static source/artifact dimensions | PASS | verifier result above |
| Runtime professional/reference dependency | PASS | none in replay carrier |
| Historical source audio path | PASS | Git-tracked historical path |
| Cross-ref source-audio blob identity | PASS | same Git blob `5e34fb55fbd011c55b56bc40cc5d062735b3fcd0` at historical/current refs |
| Top-level `audio-separator` version | PASS | pinned to `0.44.5` in historical Modal source |
| Historical Modal execution recipe | PARTIAL | Python 3.11 / Debian slim / ffmpeg / L4 / 8 GB recovered; immutable image + resolved transitive packages missing |
| Fully resolved Python/CUDA runtime | BLOCKED | no complete historical freeze/image digest; historical GPU smoke was not executed |
| BS-RoFormer historical payload hash | BLOCKED | filename known; historical bytes/hash not proven |
| Demucs historical payload hash/config closure | BLOCKED | identifier known; historical bytes/hash not proven |
| Fresh raw-audio GPU replay as bit-exact historical reproduction | DEFERRED | fail closed while runtime/model byte provenance remains incomplete |
| Controlled compatibility comparator | ALLOWED TO PLAN | may be designed as new evidence only, with complete fresh provenance capture and isolated outputs; must not be labelled historical equivalence |

## Hard constraints

- Work only on `v143-contextual-prune-lobo`.
- Do not modify `main` or production.
- Do not retrain.
- Do not retune historical thresholds to force expected output.
- Do not inject professional/reference labels into runtime features.
- Do not overwrite preserved historical caches during any future replay.
- Preserve median-onset historical behavior; do not silently substitute the later weighted carrier behavior.
- Treat current/mirrored third-party model files as unproven until historical provenance is established.
- Do not claim bit-exact raw-audio replay while external runtime/model closure is incomplete.
- Do not disturb the statically proven measures 1–16 producer/feature chain merely to manufacture replay agreement.
- Codespace is not required for the current archaeology path and should remain unnecessary unless a specific unrecoverable evidence gap demands it.

## Next safe steps

1. Continue historical repository/action/artifact archaeology only if a new plausible source of model hashes, `audio-separator` download metadata, resolved package versions, CUDA/Torch/ONNX versions or immutable Modal image identity is identified; do not repeatedly search already exhausted evidence without a new lead.
2. Treat exact historical separator recreation as **unproven** unless the missing external payload/runtime evidence is recovered.
3. If runtime comparison is still useful, write a controlled compatibility-comparator plan first. It must capture fresh model payload checksums, full environment/package inventory, CUDA/Torch/ONNX details, input blob SHA, separator command/config, seed/deterministic controls and output hashes.
4. Any such comparator must write only isolated research artifacts and be explicitly labelled **new compatibility evidence**, not a bit-exact historical reproduction.
5. Compare newly generated outputs against the preserved historical caches using frozen boundaries, thresholds, tolerances and model inputs. Never retrain, retune or modify production to improve agreement.
6. Keep promotion disabled unless the evidence gates required by the research checkpoint are genuinely closed.

## Runtime provenance continuation — 2026-08-22

The latest provenance pass established the following concrete points:

1. **Source input identity is closed.** Historical and current refs resolve `public/gomywayfullaitest.m4a` to Git blob `5e34fb55fbd011c55b56bc40cc5d062735b3fcd0`.
2. **Historical algorithmic separator path is identified.** The benchmark/grading code identifies `bsroformer-then-demucs6s` as the historical best GPU stem path.
3. **Historical first-party separator code is archived and checksum-anchored.** The evidence manifest includes the relevant seeded separator, production separator, Modal endpoint and GPU worker sources.
4. **The top-level separator dependency is pinned.** Historical Modal source specifies `audio-separator[gpu]==0.44.5`.
5. **The historical execution class is recovered.** The archived Modal worker used a Debian slim / Python 3.11 image recipe with FFmpeg, NVIDIA L4 and 8 GB RAM.
6. **The intended runtime fingerprint hook did not execute.** The preserved smoke evidence shows `smokeAttempted=false`; therefore exact Torch/CUDA/ONNX/transitive package versions were not captured by that mechanism.
7. **The pretrained model payload bytes are not preserved.** Model/config names are known, but no historical payload SHA-256 or immutable downloaded-file copy has been recovered.
8. **Historical GitHub replay evidence is not separator regeneration evidence.** Python `3.11.16` appears in an artifact-level replay context and must not be promoted to an exact historical Modal GPU fingerprint.
9. **No GPU replay was launched during this provenance pass.** The statically proven measures 1–16 producer chain and preserved historical artifacts remain untouched.

Conclusion: changed source audio is ruled out, while exact third-party model/runtime provenance remains genuinely unresolved. A future GPU execution may be useful only as a fully fingerprinted compatibility comparator unless stronger historical external-dependency evidence is recovered.

## Resume directive

Continue GitHub-only on `v143-contextual-prune-lobo`.

The source/artifact/feature/model structural chain is PASSING and the source-audio Git-blob identity gate is now PASSING. No further reconstruction of the 36/260/15 feature widths or input-audio identity is needed unless contradictory evidence appears.

The active task is now **external separator/runtime provenance closure or, if that remains unrecoverable, design of a strictly labelled controlled compatibility comparator**. Fail closed: do not execute or describe a fresh separator run as bit-identical historical replay until the missing third-party environment/model payload evidence is authenticated.