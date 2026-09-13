# Songsterr Fresh V6 — Multitrack Benchmark Replacement Sweep

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: metadata/license/reference-semantics screening only; **no candidate media downloaded, no Basic Pitch/V6 execution, no correctness exposure**

## Scope

This checkpoint continues only the allowed V6 replacement untouched-holdout search after the completed Guitar-TECHS reference-blind audit returned frozen decision `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`.

The frozen replacement gate remains: explicit usable dataset-audio rights, real performed guitar, immutable independent performed note-level onset+pitch truth, plausible >=1,000-positive evidence volume without duplicate inflation, and defensible untouched status before any media access.

Archived V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, duration research, protected-song execution, `main`, and Production remain closed.

## Sources reviewed

Primary/authoritative pages checked in this metadata-only pass:

- MedleyDB downloads / terms: https://medleydb.weebly.com/downloads.html
- MedleyDB description / annotations: https://medleydb.weebly.com/description.html
- MUSDB18 official SigSep dataset page: https://sigsep.github.io/datasets/musdb.html
- MUSDB18 Zenodo record: https://zenodo.org/records/1117372
- MoisesDB official repository: https://github.com/moises-ai/moises-db
- Slakh official dataset site: https://www.slakh.com/

## MedleyDB — REJECTED ON RIGHTS; ALSO NO V6 NOTE TRUTH

MedleyDB contains real multitrack music and many guitar stems, but the official terms state that the dataset is offered for **non-commercial research use only** and is licensed CC BY-NC-SA 4.0. That independently fails the product-validation rights gate.

Its authoritative annotation inventory is also oriented to melody f0, instrument activation, stem intervals/rankings and related MIR tasks. It does not establish immutable independent discrete performed guitar note events with both onset timestamps and pitch/MIDI identity for a qualifying guitar population. Melody f0 contours are not silently converted into the frozen V6 note-event reference.

**Disposition:** reject before media access for V6 admission. Do not derive note truth from f0 contours, stems, score reconstruction, source separation, transcription, or audio-derived onset detection.

## MUSDB18 / MUSDB18-HQ — REJECTED ON RIGHTS + REFERENCE STRUCTURE

Official MUSDB18 materials state that access is for academic/educational purposes and that constituent tracks include MedleyDB CC BY-NC-SA material and other copyright-holder-specific sources. The Zenodo release explicitly says the material should not be used commercially without express permission.

MUSDB18 provides only mixture plus drums, bass, vocals and `other` accompaniment stems. Guitar is not a dedicated canonical note-event reference stream, and no immutable performed guitar onset+pitch/MIDI truth is part of the official corpus structure.

**Disposition:** reject before media access. Do not isolate guitar from `other`, infer guitar notes, or treat source-separation stems as note truth.

## MoisesDB — REJECTED ON RIGHTS + NO NOTE-EVENT TRUTH

The official MoisesDB repository states that the corpus is distributed under **CC BY-NC-SA 4.0**, independently failing the usable-rights gate for this product-validation path.

The public schema is source-separation oriented: mixtures, hierarchical source/stem labels, activity/bleed metadata and audio stems. It does not establish an immutable independent performed guitar note stream containing both onset and pitch/MIDI identity.

**Disposition:** reject before media access for V6 admission.

## Slakh2100 — REJECTED AS SYNTHETIC, NOT REAL PERFORMED GUITAR

Slakh is permissively licensed CC BY 4.0 and provides aligned MIDI, including guitar-class material. However, the official construction is explicit: MIDI from Lakh is rendered through sample-based virtual instruments/VST patches to generate the audio. The aligned MIDI is therefore synthesis control, not a contemporaneously captured reference for real human guitar performance.

This clean alignment cannot satisfy the frozen requirement for an untouched **real performed-guitar** external holdout.

**Disposition:** reject for V6 external admission. Do not substitute synthetic/rendered guitar audio for the required real-performance holdout.

## Search-frontier result

This benchmark-family sweep does **not** produce an audit-ready replacement. It closes a tempting but invalid route: broad MIR/multitrack corpora may contain guitar stems or aligned MIDI, but current candidates fail either product-use rights, independent note-reference semantics, or the real-performed-guitar requirement.

The scientifically strongest blocked lead remains AG-PT-set because it has manually labeled onset events plus pitch metadata, but its dataset-audio rights remain unresolved. Multimodal Electric Guitar Data still has cleaner rights but no established immutable performed note-level onset+pitch reference. EGFxSet remains only a narrow backup and cannot inflate evidence using effect duplicates.

## Authority unchanged

No candidate was selected. No candidate media was downloaded or inspected. No structural/alignment audit, Basic Pitch run, V6 run, correctness computation, optimizer/threshold sweep, method change, protected-song execution, or production action occurred.

Fail-closed authority remains exactly:
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected song embargoed

No Modal, Vercel heavy-GPU, or L4 compute was used.