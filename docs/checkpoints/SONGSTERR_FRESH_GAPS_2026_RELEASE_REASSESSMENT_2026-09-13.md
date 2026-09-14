# Songsterr Fresh V6 — GAPS 2026 Release Reassessment

Date: 2026-09-13 (America/Toronto)
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/license/reference-provenance only; no candidate media access; no Basic Pitch/V6 correctness.

## Reason for reassessment

The canonical state previously classified GAPS as rights-blocked. A later official Zenodo record now points to a 2026 Hugging Face release (`xavriley/GAPS`) that includes audio, and the Hugging Face dataset card advertises `license: mit`. This is materially newer distribution metadata and warranted a reference-blind metadata reassessment.

## Sources checked

- Official Zenodo updated record: https://zenodo.org/records/17152440
- Official Hugging Face dataset: https://huggingface.co/datasets/xavriley/GAPS
- Hugging Face README: https://huggingface.co/datasets/xavriley/GAPS/blob/main/README.md
- ISMIR 2024 GAPS paper/public full text metadata: https://www.researchgate.net/publication/383216845_GAPS_A_Large_and_Diverse_Classical_Guitar_Dataset_and_Benchmark_Transcription_Model
- Xavier Riley thesis evidence for the GAPS construction flow: https://qmro.qmul.ac.uk/xmlui/bitstream/handle/123456789/114779/Xavier%20Riley%20-%20Transcribing%20the%20Jazz%20Ensemble.pdf?sequence=2

## Updated distribution facts

- The official Zenodo record says a newer GAPS version is available on Hugging Face, includes audio, and is recommended for future research projects.
- The official Hugging Face card says version 1.1 contains 300 solo-guitar performances with accurately aligned MIDI/MusicXML and now includes audio.
- The Hugging Face metadata advertises `license: mit`.

These facts supersede the narrow statement that no permissive-looking official distribution exists. They do **not** establish admission for V6.

## Frozen independence gate fails

The GAPS paper describes the source audio as matching YouTube performances and the source score as GuitarPro/ClassClef material. The published construction method then:

1. converts score material to MIDI/MusicXML;
2. aligns score and recorded audio with DTW;
3. performs a fine alignment in which notes/chords are moved toward activations from an existing transcription model;
4. manually verifies the alignment;
5. re-aligns and filters the population before emitting performance MIDI.

The thesis flowchart independently describes `GuitarPro Scores` + `Audio (YouTube)` -> auto-alignment -> manual verification -> re-alignment -> `Performance MIDI` -> filtering -> dataset.

Therefore GAPS note-onset timing is materially reconstructed from the evaluated performance audio, including neural/model-derived activation evidence. It is not an immutable independent performed onset reference captured on a separate clock/sensor path.

That independently violates frozen replacement-holdout gate 3:

> immutable independent performed note-level onset + pitch truth, not reconstructed from evaluated audio.

No amount of later licensing clarification can cure that reference-provenance failure for this frozen V6 audit.

## Rights interpretation

The 2026 Hugging Face release is more permissive-looking than the earlier state because the official dataset card now declares MIT. However, the performances originate from third-party YouTube recordings. The surfaced release metadata does not provide per-performance rightsholder grants establishing that those underlying recordings are licensed for commercial/product validation independent of the repository-level MIT tag.

Because the reference-independence gate already fails, no further rights escalation is needed for admission. The rights question remains non-authoritative for product-validation use and must not be treated as cleared solely from a dataset-card tag.

## Decision

**REJECTED FOR V6 ADMISSION — AUDIO-DERIVED REFERENCE.**

- `realGuitar`: true
- `capacityPlausible`: true (>250,000 note events reported)
- `independentPerformedReference`: false
- `rightsForProductValidation`: not established to the frozen standard
- `auditReady`: false
- `mediaAccessAuthorizedByThisCheckpoint`: false
- `correctnessAuthorizedByThisCheckpoint`: false

Do not download/acquire GAPS for V6 admission, do not run Basic Pitch/V6 on it, and do not attempt to repair the reference by substituting or re-aligning annotations. The 2026 audio release changes the distribution metadata but **does not rehabilitate GAPS for frozen V6 external validation**.

## Global authority unchanged

`modelValidationComplete:false`; `customerEligibleEvents:0`; `mayAdvanceDelivery:false`; duration unchanged/paused; Policy C `UNENROLLED`; protected-song embargo unchanged. No Modal, Vercel heavy-GPU, or L4 execution was used.