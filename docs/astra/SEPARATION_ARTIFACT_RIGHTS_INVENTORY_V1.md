# Jimmy PAIge Astra — Separation Artifact Rights Inventory V1

Status: Milestone 7A evidence inventory; no candidate admitted for execution
Date: 2026-09-19 UTC

## Purpose

This inventory asks a narrower question than musical quality: is there a current source-separation artifact that (a) exposes both a bass stem and a guitar stem, (b) has a plausible CPU deployment path, and (c) has a complete artifact-rights chain for development evaluation and commercial paid-tab inference?

No model weight was downloaded or executed for this review. Runtime claims below are upstream claims only; Astra has not benchmarked them.

## Screening rules

1. A generic `other` stem is not a guitar stem.
2. A generic guitar stem is not independent evidence for lead versus rhythm.
3. A repository software license does not automatically establish terms for separately hosted weights.
4. A downstream conversion or fine-tune license cannot erase unresolved rights in the base weights it derives from.
5. "CPU supported" is not the same as meeting Astra's 1200-second analyzer budget; that remains unverified until an authorized runtime milestone.
6. Model-page quality claims are not Astra quality results.

## Candidates

### Spleeter 5-stem — capability near-miss

- Upstream: `deezer/spleeter`, release `v2.3.0` (GitHub shows release commit `e65ece8`).
- Artifact identity reviewed: embedded `spleeter:5stems` pretrained-model family. Astra did not download the release asset, so no local artifact SHA-256 is claimed.
- Stems: vocals, piano, drums, bass, other. There is no guitar stem.
- Rights: the Spleeter paper explicitly states that the source code and pretrained models are distributed under MIT.
- CPU: the paper states TensorFlow inference can run on CPU or GPU.
- Astra disposition: **rejected for this product path** because `other` cannot be promoted to guitar truth.

### Open-Unmix `umxhq` — capability near-miss

- Upstream: `sigsep/open-unmix-pytorch`, release `v1.0.0` (release commit shown as `3f6a421`).
- Artifact identity reviewed: `umxhq` pretrained family; no Astra download and no local artifact digest.
- Stems: vocals, drums, bass, other. There is no guitar stem.
- Repository software license: MIT.
- Exact pretrained-weight commercial terms were not separately frozen by Astra during this review, so the registry remains conservative.
- CPU: the public API supports a CPU device.
- Astra disposition: **rejected for this product path** because `other` is not guitar.

### StemSplit HTDemucs 6-stem ONNX — capability match, lineage blocked

- Upstream artifact repo: `StemSplitio/htdemucs-6s-onnx`.
- Exact artifact commit: `52c122c298c21fb0c74e7f04fe6e5d9c1f6dceef`.
- File: `htdemucs_6s.onnx`.
- Upstream LFS SHA-256: `48f8e84945579f8ab340e083339e9221e03785dbe733a52c388200b6d3ca779a`.
- Upstream size: 258,159,781 bytes.
- Stems: drums, bass, other, vocals, guitar, piano.
- Deployment claim: ONNX Runtime CPU provider is supported and PyTorch is not required for inference.
- The repository labels the conversion MIT and identifies the original model as `facebookresearch/demucs`.
- Astra disposition: **blocked**. This is a derivative conversion of the same `htdemucs_6s` lineage whose exact base-weight commercial rights remain unresolved in `DEMUCS_ARTIFACT_ADMISSION_V1.md`. The downstream MIT label does not independently cure that unresolved base-weight chain.
- Lead/rhythm: still unavailable; the output is one generic guitar stem.

### Guitar Domain Expert HTDemucs 6s — capability match, lineage/training chain blocked

- Upstream artifact repo: `adityalakhani/htdemucs-6s-guitar-ft`.
- Initial artifact revision: `3c3272339025ddb0ef899e939637b93c54186431`.
- File: `guitar_htdemucs_6s.pt`.
- Upstream LFS SHA-256: `4fde369e41582ba5c2759b6ab926a44af467c64d4566bf914374ab267b19260e`.
- Upstream size: 329,654,071 bytes.
- The model card/config say it is fine-tuned from `htdemucs_6s`, outputs the six-source layout including bass and guitar, and labels the downstream model Apache-2.0.
- The same card says MoisesDB v0.1 was used for fine-tuning under research licensing terms.
- Astra disposition: **blocked**. Base `htdemucs_6s` weight rights remain unresolved, and Astra has not established that the complete training/data/model rights chain permits commercial paid-tab inference.
- Lead/rhythm: the model card explicitly says overlapping lead/rhythm/acoustic guitars are extracted together into one guitar stem, so it cannot supply independent lead/rhythm role evidence.

## Result

**Zero reviewed candidates satisfy all 7A conditions.**

Spleeter has unusually clear pretrained-model MIT terms but no guitar stem. Open-Unmix has no guitar stem. The two reviewed bass+guitar alternatives are HTDemucs derivatives and therefore do not solve Astra's unresolved base-weight rights problem. None distinguishes lead from rhythm guitar.

No candidate is execution-ready, customer-ready or production-ready. No customer quality result exists.

## Exact next action

Continue Milestone 7B as a no-download search for an **independently trained** bass+guitar separator (not derived from the blocked `htdemucs_6s` artifact) whose model-artifact terms explicitly permit commercial inference. If none is found with a plausible CPU path, the decision point is either (1) obtain a documented rights clearance/license for the exact frozen Demucs weight, or (2) scope a separately licensed/trained replacement. Do not weaken the existing Demucs admission gate.
