# Songsterr Fresh — FLGD V5 Stage B Manifest / Annotation-Semantics Preregistration

Status: **FROZEN BEFORE ANY FLGD CORRECTNESS RESULT**

Date: 2026-09-12 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Purpose

Stage B converts the completed FLGD Stage A inventory into one exact, hash-bound 79-performance canonical population and records reference-MIDI timing/annotation semantics needed for a later scoring preregistration.

Stage B is still non-scoring. It MUST NOT invoke Basic Pitch, V5, Demucs, source separation, audio-sample pitch analysis, estimate/reference matching, precision/recall, or any correctness metric.

## Frozen dataset identity

Only this release is allowed:
- repository: `xavriley/FrancoisLeducGuitarDataset`
- canonical origin: `https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset`
- exact Git revision: `a38306c244b3ea81496ad58b4514622185e58211`
- selected release license declaration: MIT

Stage A result binding:
- Stage A report SHA-256 `f03d6e3b9549a13dbcc9557ec6f13516fb52ac9d4fbf64138a0bb008b7a891b3`
- `metadata.csv` SHA-256 `05047b224d65dcf37b6f2e85e3c1457e9a3f26a50d4a9a87526b7ea4bde8048b`
- Stage A observed exactly 79 canonical `audio/` files, 79 canonical `midi/` files, 79 exact one-to-one leaf-stem pairs, zero canonical ambiguities and zero canonical unpaired files.

## Frozen population rule

All and only the 79 rows in the selected release's root `metadata.csv` are the Stage B canonical population.

Required columns, in exact observed order:
`split,midi_filename,audio_filename,guitar_type,slice_id,artist,name`

For every row:
1. `audio_filename` must resolve mechanically to exactly one regular file under canonical root `audio/`;
2. `midi_filename` must resolve mechanically to exactly one regular file under canonical root `midi/`;
3. audio and MIDI must share the canonical performance stem expected by Stage A pairing;
4. each resolved file SHA-256 must be recorded;
5. every canonical audio/MIDI file must be used by exactly one metadata row;
6. no row may be silently dropped.

`split` and `guitar_type` are recorded as metadata strata only. Stage B does not select or exclude rows based on these labels.

Anything under `test_set/`, including duplicate ground-truth files and model-output MIDI, is **forbidden as reference truth** and must not enter the canonical population.

Any file outside metadata-named canonical `audio/` and `midi/` paths is non-population material.

## Syncpoint inventory rule

The release contains syncpoint JSON material. Stage B may inspect it only to establish timing/alignment structure.

For each canonical performance stem, Stage B must mechanically look for the corresponding syncpoint JSON under `syncpoints/` and record:
- exact path and SHA-256;
- JSON top-level type;
- point count;
- per-point arity counts;
- whether each point is a numeric sequence;
- monotonicity/range of the second coordinate, treated only as an observed numeric coordinate until semantics are separately justified;
- ranges/domains for the other coordinates when present.

Stage B MUST NOT use syncpoint values to score an estimate, alter V5, choose favorable files, or create a correctness result.

If exact syncpoint membership is not one-to-one for all 79 canonical stems, Stage B must report the discrepancy and fail closed rather than invent mappings.

## Reference MIDI parser contract

Stage B may parse canonical metadata-named `midi/` files only. It must not parse `test_set/` or model-output MIDI as truth.

Parser is deterministic Standard MIDI File (SMF) structure/timing logic implemented without model libraries.

Required structural handling:
- accept PPQ/ticks-per-quarter division only; SMPTE division fails closed;
- parse variable-length delta times exactly;
- support running status;
- `note_on` velocity 0 is `note_off`;
- collect tempo meta events `FF 51 03` across tracks by absolute tick;
- if no tempo exists at tick 0, standard default tempo is 500,000 microseconds/quarter until first explicit tempo;
- convert absolute ticks to seconds piecewise through the globally merged tempo map;
- collect note-on/note-off events by `(channel, MIDI note)`;
- pair overlapping same-key events FIFO in onset order;
- unmatched note-offs or note-ons fail closed;
- nonfinite/negative converted times fail closed;
- note offsets earlier than onsets fail closed.

Stage B records only annotation/timing statistics and exact identities:
- note-event count per file and total;
- MIDI note min/max;
- onset and offset min/max seconds;
- duration min/max seconds as annotation diagnostics only (duration authority remains unchanged);
- tempo-event count/domain;
- PPQ division and track-count domains;
- channel domains;
- any same-key overlap count before FIFO pairing;
- canonical reference-event identity hash using exact `(file stem, event ordinal, channel, MIDI, onset tick, offset tick, onset seconds, offset seconds)` records.

Reference note durations are not an admission-duration authority and are not input to V5 classification.

## Stage B manifest output

The deterministic Stage B JSON must include:
- dataset provenance and Stage A bindings;
- all 79 rows in deterministic `metadata.csv` row order;
- canonical audio/MIDI/syncpoint path + SHA-256 for every row;
- split/guitar-type counts;
- exact canonical MIDI parser statistics;
- exact reference event counts/ranges;
- exact included-population canonical SHA-256 over the 79 identity rows;
- exact reference-event-identity SHA-256;
- policy boundary.

No post-hoc exclusions are authorized. Any integrity/parser failure stops Stage B and requires a new preregistration version before proceeding.

## Policy boundary required in output

Exactly:
- `basicPitchInvoked:false`
- `v5ClassifierInvoked:false`
- `demucsInvoked:false`
- `audioSamplesUsedForPitchAnalysis:false`
- `estimateReferenceMatchingPerformed:false`
- `correctnessMetricComputed:false`
- `protectedSongUsed:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- `durationAuthorityChanged:false`

## Controlled CI before real Stage B

Before this parser/manifest tool touches real FLGD, controlled CI must prove on a synthetic local Git dataset:
- exact origin/revision binding;
- metadata row/path bijection;
- `test_set/` exclusion from population;
- syncpoint structure validation;
- MIDI running status / tempo map / note pairing / tick-to-second conversion;
- deterministic population/reference hashes;
- fail-closed malformed-MIDI cases;
- all policy flags false/zero;
- real FLGD absent from CI.

## After Stage B

Only after the one real Stage B manifest is generated and immutably bound may a **separate scoring preregistration** freeze:
- Basic Pitch runtime/version/settings;
- V5 implementation/runtime hashes;
- exact matching protocol;
- uncertainty method;
- minimum positive-event requirement;
- pooled and metadata-stratum pass gates;
- output/provenance contract;
- single official FLGD correctness-run rule.

No correctness scoring is authorized by this document.
