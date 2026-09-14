# Songsterr Fresh V6 — MUSMET Metadata / Rights / Reference Review

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata-only replacement-holdout screening; no corpus media access; no Basic Pitch/V6 correctness.

## Candidate

MUSMET — First version of multimodal dataset, Zenodo record `17379727`, published 2025-10-17 and modified 2026-02-14.

## Authoritative public evidence reviewed

- Zenodo record `17379727` describes five groups of four musicians (20 musicians total) performing piano, electric bass, electric guitar, and drums. Each group performs eight pieces; the release stores synchronized streams in XDF/LSL.
- The same Zenodo description states that the synchronized streams include **audio and EEG**. It does not identify a guitar MIDI, per-note event, hexaphonic note stream, fret sensor stream, or other independent performed onset+pitch reference for the electric-guitar part.
- MUSMET's official software-and-datasets page independently describes this release as a multimodal dataset of **EEG and audio** from five four-player bands. It separately lists an unrelated drum-pattern dataset as containing audio and MIDI, which reinforces that MIDI is not claimed for this guitar-band release.
- The Zenodo Rights section exposes `Copyright 2025 The MUSMET consortium` but no explicit permissive dataset/audio license suitable for product-validation use.

## Frozen V6 pre-media gate assessment

1. **Explicit usable/permissive performance-audio rights for product validation: FAIL / not established.** The authoritative record provides copyright ownership but no explicit permissive license.
2. **Real guitar: PASS at metadata level.** The release explicitly includes electric-guitar performances by real musicians.
3. **Immutable independent performed note-level onset + pitch truth: FAIL / not established.** Public release metadata describes audio+EEG synchronization only; no independent guitar note-event reference is exposed.
4. **Plausible >=1,000 V6-positive capacity without duplicate/effect inflation: NOT EVALUATED.** Gate 3 already fails and no media access is justified.
5. **Defensible untouched status: NOT EVALUATED.** No need to inspect history/content after prior hard-gate failures.

## Binding decision

`REJECTED_BEFORE_MEDIA_ACCESS__RIGHTS_AND_REFERENCE_INSUFFICIENT`

MUSMET must not advance to corpus acquisition, reference-blind structural audit, Basic Pitch, V6, or correctness under the current public release. A future authoritative release could only reopen this candidate if it materially changes a hard gate — specifically by providing both explicit usable performance-audio rights and an immutable independent performed guitar onset+pitch reference.

## Guardrails preserved

- No MUSMET media downloaded or inspected.
- No Basic Pitch, V6, or correctness run.
- No change to frozen V6 constants, matcher, tolerances, uncertainty, admission gates, strata, or deferred-reveal/single-run rule.
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration unchanged/paused
- Policy C `UNENROLLED`
- protected-song execution remains embargoed.
