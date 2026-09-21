# Note Inference Candidate Inventory V1

Status: static no-download review
Date: 2026-09-21
Branch: `astra-work`

## Decision

Astra should stop tuning the exposed Gomyway development song and evaluate a stronger general note-inference component only after its identity, rights, preprocessing and runtime boundaries are frozen.

The next bounded **guitar** candidate is the official DAFx-24 GuitarProFX-augmented TabCNN checkpoint deposited with EGSet12. MR-MT3 is the secondary heavier multi-instrument candidate.

Neither candidate is authorized for execution or customer delivery by this inventory.

## Why GuitarProFX TabCNN is first

The observed Gomyway residual failures are dominated by missing/incorrect simultaneous guitar pitches after role evidence improved. A guitar-specific model whose output is six string/fret states directly targets that failure mode more closely than another generic pitch-list model.

Official source/code identity reviewed:

- repository: `robust-guitar-tabs/code`
- revision: `f50309ad06dc734ddae5e3a0eda756fca221e2e7`
- repository license: CC0-1.0
- LICENSE Git blob: `1625c1793607996fcfc46420e8aa2f3d2b7efd1e`
- README Git blob: `0ab556f527c038b589cf2c2b1a53750b052e97eb`

The source README identifies the `guitarProFx` training path and an EGSet12 inference script.

Official deposited weight metadata reviewed without downloading:

- record: `https://zenodo.org/records/11406378`
- deposited file: `best_TabCNN_tablature_trancription_model`
- size: 3,345,122 bytes
- published MD5: `ce168b2cd426f81a2a78499214e40605`
- record license metadata: CC-BY-4.0
- record description explicitly says the best-performing GuitarProFX TabCNN weights are included.

Astra has **not** downloaded the official checkpoint and therefore does not yet have its own SHA-256. A third-party ONNX conversion exists and publishes a SHA-256, but it is not accepted as Astra authority until numerical equivalence to the official checkpoint and exact preprocessing are independently verified.

### Blockers before a bounded development run

1. Download the exact official Zenodo checkpoint only after the development-rights review is accepted; verify published MD5 and compute/freeze Astra SHA-256.
2. Freeze the exact official inference/preprocessing path, especially CQT geometry and normalization. Do not silently substitute a third-party conversion.
3. Review the GuitarProFX training/data rights chain for the intended paid product. The deposited weight's CC-BY-4.0 metadata is evidence about the deposited artifact, not by itself a complete commercial training-lineage opinion.
4. Build a minimal CPU runtime lock and measure memory/wall time.
5. Keep lead/rhythm distinction external. TabCNN is generic-guitar inference; Astra's stereo/fallback role evidence remains responsible for requested role.
6. No adequate prospective second-song note benchmark currently exists. A Gomyway run could diagnose component behavior only; it cannot prove cross-song generalization.

## Secondary candidate: MR-MT3

Reviewed source identity:

- repository: `gudgud96/MR-MT3`
- revision: `826ea84a933f93cd707d11e91af711f1d19c8d79`
- code license: MIT
- LICENSE Git blob: `c9c472bdc3f68c27698aef2cde08418ae0d1ab7b`
- README Git blob: `b8d837a1bbbcb8a8ac72d5fc49926dd2c3c74b22`

The README points to pretrained models and describes a research stack containing PyTorch, TensorFlow/T5, librosa and related dependencies. It names Slakh, ComMU and NSynth in the data preparation/training workflow.

Selected published checkpoint identity for a possible later review:

- model repository: `gudgud1014/MR-MT3`
- file: `continual/exp_segmemV2_prev_context=0_MT3_1e-5_ep100_norandom.ckpt`
- LFS SHA-256: `74b2620009e9455a8f36da8a2b41950da4f12a229652a6cbd3ccb4333920c97f`
- size: 582,511,409 bytes
- model repository license metadata: MIT

### Why it is secondary

MR-MT3 is multi-instrument and may help with generic instrument event inference, but it is roughly two orders of magnitude larger than the official TabCNN checkpoint and has a substantially heavier runtime surface. CPU latency/memory are unverified. It also does not establish lead-versus-rhythm guitar identity.

Before any execution, Astra still needs training-data commercial-rights review, a frozen runtime/preprocessing contract, local checkpoint verification and a CPU budget measurement.

## Candidates not selected for first execution

- **FretNet**: guitar-specific and technically interesting, but its canonical repository primarily exposes training/evaluation code and does not provide an obvious ready-to-run canonical pretrained checkpoint. It is not the cheapest zero-new-spend next run.
- **SynthTab-derived checkpoints**: useful research, but the published SynthTab dataset lineage includes non-commercial restrictions; do not use for a paid product without separate clearance.
- **unverified third-party TabCNN conversions**: useful for understanding deployment shape, but cannot replace official checkpoint/provenance validation.
- **fixed MIDI-register role gates**: remain prohibited as lead/rhythm truth.

## Architecture fit

The preferred future graph for a stereo input is:

```text
stereo audio
  -> reference-blind spatial role evidence / abstention
  -> role-supported guitar channel
  -> GuitarProFX TabCNN candidate
  -> Astra evidence-state integration
  -> structure / rhythm / fretboard / product adapters
  -> existing acceptance and delivery gates
```

For mono or weakly separated stereo, the role layer must still abstain or use a separately validated general separator. The note model itself must never be promoted into role truth.

## Next action

Create and test the static candidate registry (same milestone), then perform a **no-model runtime/preprocessing review** of the official TabCNN source path. Do not download weights or execute inference until the artifact SHA/rights/runtime preflight is explicitly cleared.

No main/Production change.
