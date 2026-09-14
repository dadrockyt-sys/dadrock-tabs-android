# Songsterr Fresh V6 — GAPS v1.1 Release Delta Review

Date: 2026-09-14 (America/Toronto)
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/reference-provenance review only; no candidate media acquisition and no model correctness.

## Frozen authority

This review does not reopen or modify the frozen V6 method or scoring framework.

- V6 method preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`, commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
- Frozen implementation: commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
- External scoring framework preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`, commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.
- Guitar-TECHS remains closed outcome `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; no Guitar-TECHS correctness is allowed.

## Why GAPS was rechecked

The prior canonical state rejected GAPS because its note timing is reconstructed from the evaluated recording and because third-party performance-audio rights were unresolved. A material public-release delta now exists: the authoritative GAPS Hugging Face release identifies itself as version 1.1, states that audio is now included, and labels the dataset `license: mit`.

Primary release evidence reviewed:

- GAPS Hugging Face dataset: https://huggingface.co/datasets/xavriley/GAPS
- GAPS Hugging Face README: https://huggingface.co/datasets/xavriley/GAPS/blob/main/README.md
- GAPS Zenodo record pointing to the newer Hugging Face release: https://zenodo.org/records/17152440
- GAPS paper: https://arxiv.org/abs/2408.08653

No audio files were downloaded or inspected.

## Release delta

The Hugging Face release currently reports:

- 300 solo-guitar performances;
- approximately 14 hours of real guitar audio;
- audio now included in version 1.1;
- total repository size about 16.4 GB;
- top-level dataset metadata `license: mit`.

The current Zenodo record explicitly says the newer Hugging Face version includes audio and is recommended for future research projects. This is new public-release evidence relative to the older no-audio Zenodo package.

## Frozen gate 3 remains failed: reference timing is not independent

The GAPS paper is explicit about how the note-level alignment is constructed from the evaluated recordings:

1. scores are converted to MusicXML/MIDI;
2. an initial score/audio alignment is produced with Dynamic Time Warping;
3. a fine-alignment stage moves notes of each chord to their closest activation from an existing guitar transcription model;
4. authors manually inspect/correct downbeat alignment;
5. the corrected material is re-aligned with the same method;
6. the final retained 300 performances are selected partly by agreement with outputs of the guitar transcription model.

Therefore the high-resolution performed onset locations are not an independent physical or simultaneously captured performed note-event reference. They are reconstructed from the same performance audio that V6 would evaluate, using audio alignment and transcription-model activations. Manual verification of downbeats does not convert those per-note timings into an independent performed reference stream.

This alone fails the frozen replacement-holdout requirement for immutable independent performed note-level onset + pitch truth. The new v1.1 packaging cannot cure this provenance failure.

## Rights delta does not create admission

The Hugging Face repository now declares `license: mit`, and the package includes audio. That is a material metadata change and is recorded here rather than ignored.

However, the paper states that the performances were sourced from YouTube and drawn from 205 different performers, including professionally produced recordings. A repository-level MIT label does not, by itself, establish that every underlying third-party performance recording carries a permissive product-validation license granted by the relevant recording/rightsholder. The public materials reviewed here do not provide a track-by-track performance-audio rights chain sufficient to override that concern.

Even if a later authoritative rights instrument fully cleared the audio, gate 3 would still fail because the note timing reference is audio-derived.

## Decision

**GAPS remains REJECTED for Songsterr Fresh V6 external correctness.**

Reason hierarchy:

1. **Decisive structural provenance failure:** performed note timing is reconstructed from evaluated audio via DTW + transcription-model activations, with manual downbeat intervention and model-agreement filtering.
2. **Rights remain insufficiently established for this product-validation use:** v1.1 carries an MIT dataset label but the underlying performances are third-party YouTube recordings and no per-performance rights chain was established by the reviewed primary materials.

The v1.1 audio-inclusion/MIT metadata delta is real, but it does not change the V6 admission result.

## Actions explicitly not taken

- no GAPS audio/media acquisition;
- no Basic Pitch execution;
- no V6 correctness exposure;
- no threshold/matcher/method changes;
- no scoring harness work triggered by GAPS;
- no Modal run;
- no Vercel heavy-GPU run;
- no L4 GPU run;
- no protected-song execution;
- no duration research;
- no Production/main work.

## Fail-closed state

Unchanged:

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration unchanged/paused
- Policy C `UNENROLLED`
- protected song embargoed

## Result

The replacement-holdout search remains open only for genuinely new primary evidence. GAPS v1.1 is now explicitly closed under the new release state unless a future authoritative source establishes a genuinely independent performed note-event reference; a packaging or licensing change alone cannot repair the frozen reference-provenance failure.
