# Songsterr Fresh V6 — AG-PT-set Reference Provenance Review

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **REJECTED BEFORE MEDIA ACCESS FOR V6 ADMISSION — REFERENCE PROVENANCE FAILS INDEPENDENTLY OF RIGHTS**

## Purpose

Resolve whether AG-PT-set's scientifically attractive millisecond-level onset labels satisfy the frozen V6 requirement for an immutable **independent performed note-level onset + pitch reference**, i.e. a reference not constructed from the evaluated audio.

This review is metadata/paper-methodology only. No AG-PT-set archive was downloaded or inspected, no Basic Pitch/V6 run occurred, and no correctness was exposed.

## Sources reviewed

Primary dataset record:
- Zenodo `10.5281/zenodo.10159492`, AG-PT-set v1.

Primary methodology paper:
- Domenico Stefani, Gregorio Andrea Giudici, Luca Turchet, `On the Importance of Temporally Precise Onset Annotations for Real-Time Music Information Retrieval: Findings from the AG-PT-set Dataset`, Audio Mostly 2024, DOI `10.1145/3678299.3678325`.

Institutional record:
- University of Trento IRIS record `11572/443133`.

## Previously attractive facts

AG-PT-set remains scientifically substantial:
- 15 h 55 m total monophonic acoustic-guitar recordings;
- 10 h 04 m labeled portion;
- 32,592 labeled individual notes;
- multiple players / seven guitars reported across dataset materials;
- precise onset labels stored in seconds/samples;
- note metadata includes MIDI pitch/string information;
- file-integrity metadata includes SHA-256 values;
- pitch/technique/dynamics coverage could plausibly exceed the frozen evidence-volume floor.

These facts do **not** overcome reference-provenance requirements.

## Decisive onset-labeling method

Section 3.3 of the Audio Mostly paper describes the onset labeling process explicitly:

1. Five musician annotators labeled the recordings.
2. Annotation was performed in Audacity while viewing the **recorded audio signal** and a high-temporal-resolution Mel spectrogram.
3. Annotation projects were pre-populated with candidate onset labels produced by the `aubioonset` onset detector.
4. Annotators inspected each audio file, added missed onsets, removed false positives, then zoomed in and **visually aligned each label to the onset** using the audio/spectrogram display.
5. The known number/pitch/sequence of notes in each file were used to identify annotation mistakes, with the aid of a pitch detector, and those mistakes were corrected.

Therefore the released onset timestamps are not a contemporaneous independent hardware/reference stream. They are deliberately constructed and refined from the same family of recorded audio signals that would be evaluated.

## Frozen V6 reference gate

The replacement-holdout rule requires:
- immutable performed note onset + pitch truth;
- independent of the evaluated audio;
- no candidate-audio-derived onset detection, pitch estimation, transcription, visual/audio manual alignment, score alignment or reconstructed truth as a substitute.

This gate was frozen before selecting a replacement corpus and is intentionally stricter than common MIR `ground truth` usage.

## Reference-provenance decision

**AG-PT-set fails the V6 independent-reference gate before media access.**

The issue is not annotation quality. The paper's methodology is explicitly designed to produce very precise human-corrected onset labels, and those labels may be excellent MIR annotations. The issue is experimental independence: onset timing was obtained by inspecting/detecting the evaluated recording itself.

The pitch side does not rescue the experiment. The paper states that the number, pitch and sequence of notes were known and that a pitch detector aided identification/correction of annotation mistakes. A nominal intended sequence or audio-aided corrected pitch label is not a separately captured performed-note sensor stream capable of establishing the required independent performed reference.

## Rights result becomes secondary

The previous rights review found that the primary Zenodo dataset record did not surface an explicit permissive dataset-file license suitable for this product-validation use. That remains unresolved.

However, **even a future permissive license or direct rights-holder permission would not by itself make AG-PT-set eligible**, because the independent-reference gate now fails on the published labeling method.

Rights clearance would matter for other uses, but it cannot cure reference provenance for this frozen V6 admission experiment.

## Disposition

AG-PT-set is now **REJECTED / NOT AUDIT-READY BEFORE MEDIA ACCESS** for V6 external admission under the current frozen framework.

Do not:
- download/acquire the 6.7 GB archive for V6 admission;
- run contamination/history audit as a route toward V6 scoring;
- bind AG-PT-set into the frozen scoring framework;
- use its Audacity/aubioonset-derived onset labels as independent truth;
- substitute nominal score/fret/string sequence timing;
- rebuild onset truth with a different detector;
- manually re-annotate the audio to try to restore independence;
- score V6 on AG-PT-set.

Reconsider only if an authoritative release exists with a **separately captured contemporaneous performed note-level onset+pitch stream** independent of the evaluated recordings. A better manual/audio-derived annotation release would still not satisfy this gate.

## Authority unchanged

No V6 method/scoring rule changes. No correctness exposed. Fail-closed state remains:
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected song embargoed

The public replacement frontier is correspondingly narrower. The purpose-built independent-sensor holdout design becomes more scientifically relevant, but remains design-only and requires explicit user authorization before procurement/contact/recording/data acquisition.
