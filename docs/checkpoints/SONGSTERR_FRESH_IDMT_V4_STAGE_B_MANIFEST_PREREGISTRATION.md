# Songsterr Fresh — IDMT V4 Stage B Manifest Preparation Preregistration

Status: **PREREGISTERED NON-SCORING MANIFEST PREPARATION / NO MODEL INFERENCE / NO CORRECTNESS METRIC**

Recorded: 2026-09-11 America/Toronto

Branch: `songsterr-fresh-pipeline-v1`

## Purpose

This preregistration freezes the deterministic rules used to derive the exact IDMT V4 evaluation population from the completed Stage A inventory before any Basic Pitch/V4 correctness result is produced.

This stage is still non-scoring. It may inspect the archive, WAV headers and XML annotation values, but it MUST NOT run Basic Pitch, V4, Demucs, estimate/reference matching, precision/recall/F-score/Wilson calculations, or any protected-song logic.

## Bound Stage A evidence

- archive `IDMT-SMT-GUITAR_V2.zip`
- archive MD5 `06796e08731bccffaed6ae59361486e4`
- archive SHA-256 `02816258252538603c051054219cb4bba1c0ae8c9d0a3ca5418dfc951eae997a`
- Stage A inventory report SHA-256 `fd9086891a9a699619810f4bccd6f0f2533c194afc6cc1b09cf80484626d704f`
- Stage A exact one-to-one pair count 569 across `dataset1`/`dataset2`/`dataset3`.

The manifest-preparation tool MUST verify both archive and inventory-report hashes before proceeding.

## Frozen inclusion rules

A WAV/XML pair is eligible for the Stage B evaluation manifest only if all of the following are true:

1. it appears in the Stage A report `pairs` array as an exact one-to-one leaf-stem pair;
2. its WAV path second component is exactly one of `dataset1`, `dataset2`, `dataset3`;
3. the WAV member exists in the bound archive and its member SHA-256 equals the Stage A manifest SHA-256 for that path;
4. the XML member exists in the bound archive and its member SHA-256 equals the Stage A manifest SHA-256 for that path;
5. WAV header is exactly:
   - channels = 1;
   - sampleRate = 44100;
   - compressionType = `NONE`;
   - sampleWidthBytes in `{2,3}`;
6. XML root tag is exactly `instrumentRecording`;
7. XML contains `instrumentRecording/transcription/event` note-event elements;
8. every note event contains text values for `onsetSec`, `offsetSec`, and `pitch`;
9. all three values parse as finite decimal numbers;
10. `onsetSec >= 0`;
11. `offsetSec >= onsetSec`;
12. the XML contains at least one valid note event.

No pair may be excluded because of Basic Pitch output, V4 output, model confidence, musical style, performer/instrument identity, note density, pitch content, or any future correctness result.

## Frozen exclusion reasons

The manifest-preparation output must preserve every rejected exact Stage A pair with exactly one or more mechanical reason codes from:

- `DATASET_NOT_IN_1_2_3`
- `WAV_MEMBER_IDENTITY_MISMATCH`
- `XML_MEMBER_IDENTITY_MISMATCH`
- `WAV_NOT_MONO`
- `WAV_SAMPLE_RATE_NOT_44100`
- `WAV_COMPRESSION_NOT_NONE`
- `WAV_SAMPLE_WIDTH_NOT_16_OR_24_BIT`
- `XML_ROOT_NOT_INSTRUMENT_RECORDING`
- `XML_NO_TRANSCRIPTION_EVENTS`
- `XML_EVENT_REQUIRED_FIELD_MISSING`
- `XML_EVENT_REQUIRED_FIELD_NONFINITE`
- `XML_EVENT_NEGATIVE_ONSET`
- `XML_EVENT_OFFSET_BEFORE_ONSET`
- `XML_NO_VALID_EVENTS`.

No other exclusion reason is permitted without a new preregistration version before scoring.

## Annotation-value inspection

The manifest-preparation tool MUST record, across included files only:

- total reference note-event count;
- minimum/maximum `onsetSec`;
- minimum/maximum `offsetSec`;
- minimum/maximum `pitch`;
- count of pitch values that are mathematically integer-valued within `1e-9`;
- count of non-integer pitch values;
- count by dataset directory;
- WAV counts by sample width.

It MUST NOT compare any annotation value to model output.

The final Stage B scoring preregistration will interpret `onsetSec`/`offsetSec` as seconds and `pitch` as a MIDI-note coordinate only if the non-scoring manifest output is consistent with that interpretation and the public IDMT transcription documentation. If not, scoring remains blocked pending a new preregistration.

## Output contract

The manifest-preparation result must be canonical JSON and include:

- exact input identities;
- deterministic included-file rows with WAV/XML paths and member hashes;
- deterministic excluded-pair rows with frozen mechanical reason codes;
- per-file reference-event counts and WAV header identity;
- aggregate annotation-value statistics;
- policy boundary object proving no inference/scoring occurred.

The result SHA-256 and included-manifest SHA-256 must be frozen into the final Stage B scoring preregistration before any model execution.

## Policy boundary

This stage MUST report and preserve:
- `basicPitchInvoked:false`
- `v4ClassifierInvoked:false`
- `demucsInvoked:false`
- `estimateReferenceMatchingPerformed:false`
- `correctnessMetricComputed:false`
- `protectedSongUsed:false`
- `durationAuthorityChanged:false`
- `admissionDecisionMade:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`.

## Next gate

After this manifest-preparation result is generated and reviewed, a separate final Stage B scoring preregistration must freeze, before any correctness result:

1. exact included manifest hash/population;
2. exact annotation interpretation;
3. Basic Pitch runtime/settings;
4. exact V4 implementation/source identities;
5. one-to-one estimate/reference matching tolerances/tie rules;
6. minimum V4-positive count;
7. uncertainty method;
8. overall and any stratum pass gates;
9. execution provenance/fail-closed rules;
10. protected-song embargo until a separate post-result policy review.

No real correctness scoring is authorized by this manifest-preparation preregistration alone.
