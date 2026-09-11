# Songsterr Fresh — IDMT V4 External Validation Metadata Plan

Status: **METADATA-ONLY PLANNING / NOT AN EXTERNAL-VALIDATION PREREGISTRATION / NO HOLDOUT EXECUTION AUTHORIZED**

Recorded: 2026-09-11 America/Toronto

Branch: `songsterr-fresh-pipeline-v1`

## Purpose

This document preserves public metadata needed to design a future, versioned V4 external-validation preregistration without touching real correctness results.

It does **not** authorize:
- downloading the IDMT archive into a workbench for evaluation;
- running Basic Pitch or V4 on IDMT audio;
- parsing IDMT annotations for correctness scoring;
- computing precision/recall/matching outcomes;
- changing the frozen V4 method;
- protected-song execution;
- customer admission or duration work.

Holdout/external scoring remains closed until the user explicitly reopens it.

## Candidate corpus identity

Dataset: **IDMT-SMT-Guitar Dataset**.

Authoritative public metadata:
- publisher/source: Fraunhofer IDMT / Zenodo;
- Zenodo version: `1.0.0`;
- DOI: `10.5281/zenodo.7544110`;
- archive: `IDMT-SMT-GUITAR_V2.zip`;
- archive size displayed by Zenodo: approximately `1.3 GB`;
- archive MD5: `06796e08731bccffaed6ae59361486e4`;
- authors: Christian Kehling, Andreas Männchen, Arndt Eppler;
- Fraunhofer states the dataset is provided for evaluation under **CC BY-NC-ND 4.0**.

Zenodo itself currently labels the record as an open dataset but its displayed Rights/License field is not populated. For future execution documentation, use the Fraunhofer dataset page as the license authority and do not infer a different Zenodo license.

## Authoritative audio characteristics

Fraunhofer describes:
- seven guitars in standard tuning;
- varied pickup settings and string gauges;
- direct guitar output for the normal recording setup, with one condenser-microphone case;
- one-channel RIFF WAVE audio;
- sample rate `44100 Hz`.

These characteristics are compatible in principle with the frozen V4 sample-rate/mono input contract, but archive-level validation is still required before any future evaluation.

## Public subset descriptions

The dataset contains four documented subsets.

### Subset 1 — playing techniques / realistic licks

Fraunhofer describes:
- finger-style, muted and picked plucking styles;
- expression styles including normal, bending, slide, vibrato, harmonics and dead notes;
- 24-bit audio;
- three guitars;
- about 4,700 note events;
- monophonic and polyphonic material;
- realistic guitar licks;
- parameter annotations stored in XML.

This is a plausible future pitch/onset validation subset because it contains note-event-oriented XML annotations, but exact file membership and usable annotation semantics are **not frozen by this planning document**.

### Subset 2 — isolated note events

Fraunhofer describes:
- 400 monophonic and polyphonic note events;
- each played with two different guitars;
- no expression styles;
- each event stored in a separate 16-bit file;
- parameter annotations stored in XML.

This is also a plausible future pitch/onset validation subset. Exact archive membership remains unresolved until an explicitly authorized inventory step.

### Subset 3 — five short recordings

Fraunhofer describes:
- five short monophonic/polyphonic guitar recordings;
- one instrument;
- no special expression styles;
- 16-bit audio;
- each file accompanied by a parameter annotation in XML.

This may be usable for future validation, but exact XML semantics/file pairings must be established before preregistering it.

### Subset 4 — chord/rhythm evaluation material

Fraunhofer describes:
- 64 short musical pieces grouped by genre;
- two tempi;
- three guitars;
- 16-bit audio;
- annotations for onset positions, chords, rhythmic-pattern length and monophony/polyphony texture in various file formats;
- purpose: chord recognition and rhythm-style estimation.

Because the frozen V4 validation question requires independently annotated note-level pitch/onset correctness, subset 4 is **not presently assumed eligible**. A future preregistration should exclude it unless authoritative metadata demonstrates note-level pitch annotations suitable for the locked matching contract.

## Zenodo archive-preview observations

Zenodo exposes a browser preview of `IDMT-SMT-GUITAR_V2.zip`, but the preview explicitly warns that it is **not showing all files**.

Visible preview structure includes:
- archive root `IDMT-SMT-GUITAR_V2`;
- `dataset1`;
- guitar/setup directories such as `Fender Strat Clean Neck SC`;
- paired `annotation/` and `audio/` directories;
- XML and WAV files with matching stems, e.g. `G53-40100-1111-00001.xml` and `G53-40100-1111-00001.wav`;
- additional chord-labelled directories also containing paired annotation/audio files.

The preview is useful for confirming broad organization and filename pairing, but because it is incomplete it MUST NOT be used to assert the full archive file count, exact evaluation population, exclusions, or final manifest.

## Annotation-schema status

Authoritative Fraunhofer metadata establishes that parameter annotations for subsets 1 and 2 are XML and that subset 3 has XML parameter annotations.

Secondary documentation found during metadata research indicates note-event XML commonly exposes fields corresponding to pitch/MIDI and onset/offset timing, plus instrument/performance parameters. These secondary descriptions are **not sufficient to freeze parsing semantics**.

Before any future correctness result, the external-validation preregistration must freeze XML interpretation from either:
1. an authoritative schema/parser/public documentation, or
2. an explicitly authorized archive-inventory step that reads annotation structure **without running model inference or computing correctness metrics**.

No annotation field has been consumed by V4 scoring at this stage.

## Provisional future corpus strategy — not frozen

Based only on public task descriptions, the strongest candidate evaluation surface is:
- consider subsets 1, 2 and 3 for note-level pitch/onset validation;
- do not assume subset 4 is eligible for note-level pitch validation.

This is planning guidance only. It is intentionally **not** a frozen subset selection, file manifest, or exclusion rule.

## Requirements before external scoring can be reopened

If the user explicitly reopens holdout/external validation, the next phase must still occur **before any correctness result is viewed**:

1. create a versioned V4 external-validation preregistration;
2. bind exact dataset/version/archive MD5;
3. explicitly authorize and inventory archive structure without model scoring;
4. freeze exact included subset(s), file IDs and any exclusions based only on public integrity/documentation facts;
5. freeze XML parser/field semantics and units;
6. freeze Basic Pitch inference settings and runtime versions;
7. freeze V4 implementation/source identities;
8. freeze one-to-one estimate/reference matching tolerances and tie rules;
9. freeze minimum V4-positive count;
10. freeze uncertainty method and overall/stratum pass gates;
11. freeze execution provenance and fail-closed rules;
12. only then run one official external evaluation.

No GuitarSet result may be used to choose these gates or tune V4.

## Current boundary

No IDMT archive has been downloaded or scored by the V4 workstream.
No protected-song V4 run has occurred.
No real V4 correctness metric exists.

Authority remains:
- `modelValidationComplete:false`;
- customer-eligible events `0`;
- `mayAdvanceDelivery:false`;
- duration authority unchanged;
- duration research paused;
- persistent Policy C `UNENROLLED`.
