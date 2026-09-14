# Songsterr Fresh V6 — François Leduc Guitar Dataset Metadata / Reference Review

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/rights/reference-provenance review only; no candidate media access; no Basic Pitch/V6 correctness.

## Binding decision

**REJECTED BEFORE MEDIA ACCESS — AUDIO/MODEL-DERIVED PERFORMANCE TIMING.**

The François Leduc Guitar Dataset (FLGD) contains real solo-guitar audio paired with aligned MIDI, but the released MIDI is not an independent performed note-level onset reference. The associated ICASSP 2024 work explicitly constructs the high-resolution alignment from commercial GuitarPro transcriptions by aligning those scores to activations of an existing high-resolution transcription model on the evaluated audio. Its fine-alignment stage moves note timing to local activation peaks in order to recover performance microtiming. Therefore the performance-time note onsets are materially reconstructed from the evaluated audio/model activations and fail frozen V6 replacement-holdout gate 3.

This is a provenance failure, not a quality judgment. Manual/professional source transcription quality and later public distribution do not cure the lack of an independent performed onset stream.

## Primary/public evidence reviewed

1. Project page, *High-resolution guitar transcription via domain adaptation*:
   - https://xavriley.github.io/HighResolutionGuitarTranscription/
   - States that existing guitar transcriptions are aligned to activations of a piano transcription model.
   - Describes fine alignment recovering chord-note microtiming from model activations.

2. ICASSP 2024 paper / preprint:
   - https://arxiv.org/abs/2402.15258
   - https://www.eecs.qmul.ac.uk/~simond/pub/2024/RileyEdwardsDixon-ICASSP2024-preprint.pdf
   - Describes a dataset of commercially available score/audio pairs and the use of transcription-model activations for score alignment.

3. Original Zenodo release:
   - https://zenodo.org/records/10984521
   - Describes audio-MIDI pairs for 78 solo-guitar recordings; the original distribution was restricted/request-only for research and stated that separate permission from the original copyright holder was required for non-research use of the scores.

4. Newer Hugging Face release:
   - https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset
   - Dataset card now labels the release `mit` and exposes 79 audio/aligned-MIDI performances.
   - This later packaging/licensing signal does not cure the frozen reference-independence failure above, and is not treated here as proof that all underlying third-party recording/score rights are cleared for product validation.

## Frozen-gate evaluation

1. Explicit usable/permissive performance-audio rights for product validation: **NOT ESTABLISHED TO FROZEN STANDARD**. The newer HF card says MIT, while the original record describes restricted research use and third-party score permission. No conclusion is needed because gate 3 independently fails.
2. Real guitar: **YES**.
3. Immutable independent performed note-level onset + pitch truth, not reconstructed from evaluated audio: **FAIL**. Performance timing is obtained by audio/model-activation score alignment and fine alignment.
4. Plausible >=1,000 V6-positive capacity without duplicate/effect inflation: **NOT EVALUATED / MOOT AFTER GATE 3 FAILURE**.
5. Defensible untouched status: **NOT EVALUATED / MOOT AFTER GATE 3 FAILURE**.

## Consequences

- Do not download/acquire FLGD media for V6 admission.
- Do not run Basic Pitch, V6, alignment inventory, correctness, thresholds, tuning, or scoring on FLGD.
- Do not attempt to rescue the corpus by treating professionally transcribed source scores as independent performance timing; the evaluated performance timing is reconstructed from audio/model activations.
- A future packaging/license change cannot cure this provenance failure unless an authoritative release provides a genuinely independent performed note-event stream whose timing was captured independently of the evaluated audio.

## Global authority unchanged

- Guitar-TECHS remains frozen outcome `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION` before correctness.
- V6 method/scoring remain frozen.
- `modelValidationComplete:false`.
- `customerEligibleEvents:0`.
- `mayAdvanceDelivery:false`.
- duration remains unchanged/paused.
- Policy C remains `UNENROLLED`.
- protected song remains embargoed.
- No Modal, Vercel heavy-GPU, or L4 GPU work was used or authorized by this review.
