# Songsterr Fresh — IDMT V4 External Validation Stage A Result

Status: **STAGE A INVENTORY COMPLETE / NO CORRECTNESS RESULT / STAGE B SCORING NOT YET AUTHORIZED BY THIS RECORD**

Recorded: 2026-09-11 America/Toronto

Branch: `songsterr-fresh-pipeline-v1`

## Purpose

This record freezes the completed IDMT-SMT-Guitar Stage A archive inventory. Stage A was explicitly inventory-only and did not invoke Basic Pitch, V4, Demucs, estimate/reference matching, or any correctness metric.

## Dataset identity

- dataset: IDMT-SMT-Guitar Dataset
- Zenodo version: `1.0.0`
- DOI: `10.5281/zenodo.7544110`
- archive: `IDMT-SMT-GUITAR_V2.zip`
- archive MD5: `06796e08731bccffaed6ae59361486e4`
- archive SHA-256: `02816258252538603c051054219cb4bba1c0ae8c9d0a3ca5418dfc951eae997a`

Stage A inventory report SHA-256:

`fd9086891a9a699619810f4bccd6f0f2533c194afc6cc1b09cf80484626d704f`

The report was written outside the repository and binds the complete member-level inventory, hashes, WAV-header signatures, XML structural signatures, exact one-to-one pair rows, unpaired rows, ambiguous stem groups, and the Stage A policy boundary.

## Archive inventory summary

ZIP members: **4,292**.

File-extension counts:
- `.csv`: 745
- `.pdf`: 1
- `.sv`: 244
- `.svl`: 244
- `.txt`: 810
- `.ur4972`: 1
- `.wav`: 1,173
- `.xml`: 667

Exact one-to-one WAV/XML leaf-stem pairs: **569**.

Exact-pair counts by documented dataset directory:
- `dataset1`: **312**
- `dataset2`: **252**
- `dataset3`: **5**

Integrity populations outside the exact-pair set:
- unpaired WAV: **512**
- unpaired XML: **9**
- ambiguous leaf-stem groups: **45**

These populations are inventory facts only. No correctness-based exclusion was performed.

## WAV container observations

All 1,173 WAV headers reported sample rate `44100 Hz`.

Observed channel/sample-width population:
- mono, 16-bit (`channels=1`, `sampleWidthBytes=2`): **911**
- mono, 24-bit (`channels=1`, `sampleWidthBytes=3`): **261**
- stereo, 16-bit (`channels=2`, `sampleWidthBytes=2`): **1**

Compression type reported `NONE` for the observed RIFF WAVE headers.

This does not yet identify whether the single stereo WAV belongs to the future exact evaluation population; Stage B manifest preparation must resolve that deterministically before scoring.

## XML structural observations

The inventory found multiple XML structural signatures. The dominant root is `instrumentRecording`; at least one non-note-oriented XML signature uses another root (`sv`).

Across inventoried XML structures, text-bearing field names include:
- `audioFileName`
- `composer`
- `excitationStyle`
- `expressionStyle`
- `fretNumber`
- `instrument`
- `instrumentBodyMaterial`
- `instrumentModel`
- `instrumentStringMaterial`
- `instrumentTuning`
- `modulationFrequency`
- `modulationFrequencyRange`
- `offsetSec`
- `onsetSec`
- `pickupSetting`
- `pitch`
- `recordingArtist`
- `recordingDate`
- `stringNumber`

The note-event structural path observed in the inventory is:

`instrumentRecording/transcription/event/...`

with note-level text fields including `onsetSec`, `pitch`, and `offsetSec`.

Stage A intentionally did not interpret these values as correctness ground truth. Stage B manifest preparation must validate exact numeric semantics and units before the final scoring preregistration is frozen.

## Stage A policy boundary

The completed report recorded:
- `basicPitchInvoked:false`
- `v4ClassifierInvoked:false`
- `demucsInvoked:false`
- `audioSamplesUsedForSignalAnalysis:false`
- `estimateReferenceMatchingPerformed:false`
- `correctnessMetricComputed:false`
- `guitarSetUsed:false`
- `protectedSongUsed:false`
- `durationAuthorityChanged:false`
- `admissionDecisionMade:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`.

Therefore Stage A created **no real-world V4 correctness result**.

## Required next boundary

Before any Basic Pitch/V4 execution on IDMT, Stage B preparation must deterministically derive and freeze an exact evaluation manifest from the bound Stage A report/archive, including:
1. exact eligible WAV/XML pairs;
2. dataset membership;
3. WAV input-contract eligibility (mono, 44100 Hz, uncompressed);
4. XML note-event parser validity;
5. numeric semantics/statistics for `onsetSec`, `offsetSec`, and `pitch` without comparing them to model output;
6. exact manifest hash and population counts.

Only after that non-scoring manifest is frozen may the separate final Stage B scoring preregistration lock matching rules, uncertainty method, pass gates, runtime/provenance, and authorize one official external evaluation.

No protected-song V4 execution or duration work is authorized by this result record.
