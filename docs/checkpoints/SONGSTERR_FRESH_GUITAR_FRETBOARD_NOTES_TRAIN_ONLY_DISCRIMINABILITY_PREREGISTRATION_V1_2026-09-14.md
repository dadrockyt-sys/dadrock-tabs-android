# Songsterr Fresh — Guitar Fretboard Notes Train-Only Physical-Position Discriminability Preregistration V1

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN BEFORE AUDIO RETRIEVAL / ANALYSIS

## Purpose

This is a zero-additional-cost, NON_HOLDOUT external-corpus feasibility study. It asks one narrow question:

> For two recordings with the same labeled MIDI pitch but different labeled physical string/fret positions, does deterministic audio timbre contain reproducible information that can distinguish the physical position across recording sessions?

This study does **not** establish Songsterr Fresh correctness, holdout validity, production eligibility, physical-reference authority, or any Basic Pitch/V6 authorization.

## External corpus identity

Dataset: `collegefishiesd/guitar-fretboard-notes`
Dataset card: `https://huggingface.co/datasets/collegefishiesd/guitar-fretboard-notes`
Pinned repository revision: `a33a26243e88e7ccd4893bee30eac3219ec8bef8`
Declared license on dataset card: `CC-BY-SA-4.0`
Declared format: raw/unprocessed mono WAV, 44,100 Hz, 32-bit float.
Declared total population: 390 recordings, all six standard-tuned guitar strings, frets 0–12.

Frozen split policy:
- `train`: 234 rows; allowed for this NON_HOLDOUT study; allowed sources exactly `ele`, `eqm`, `eqm2`.
- `test`: 78 rows; source `deb`; **RESERVED / MUST NOT BE RETRIEVED OR DECODED BY THIS STUDY**.
- `validation`: 78 rows; source `ele_natural`; **RESERVED / MUST NOT BE RETRIEVED OR DECODED BY THIS STUDY**.

The source-based split is preserved exactly. No random reshuffling across the dataset is allowed.

## Hard prohibitions

The study must not:
- load, stream, download, decode, inspect, feature-extract, score, or otherwise consume `test` or `validation` audio;
- use Basic Pitch;
- use V6;
- use archived V143/Gomyway;
- use any evaluated Songsterr customer audio;
- use model outputs as reference truth;
- alter the frozen Songsterr Fresh correctness gates;
- claim that isolated-note feasibility establishes performance on chords, bends, slides, hammer-ons, pull-offs, rearticulation, overlapping sustain, noisy recordings, or full songs;
- authorize customer delivery or correctness execution.

Required downstream state remains:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

## Acquisition / integrity gate

The implementation must request only `split="train"` at the pinned dataset revision.

Before feature extraction it must fail closed unless all are true:
- row count is exactly 234;
- observed source set is exactly `{ele, eqm, eqm2}`;
- every row has `string_number` in 1..6;
- every row has `fret` in 0..12;
- every row has `midi_number` in 40..76;
- every row reports/decodes at 44,100 Hz mono;
- every `(source,string_number,fret)` identity is unique;
- every allowed source contains exactly 78 rows and all 78 `(string,fret)` positions;
- no reserved source identifier (`deb`, `ele_natural`) occurs.

The result JSON must record the pinned revision, observed source identities, row count, and deterministic feature-contract identifier.

## Frozen study population

Only same-pitch ambiguous-position groups are evaluated: a MIDI pitch is eligible when, within the standard-tuned six-string fret-0..12 grid, it has at least two distinct `(string_number,fret)` positions represented in both compared sources.

Primary comparison is the two acoustic sessions from the same declared player:
- prototype source: `eqm`; query source: `eqm2`;
- reverse prototype source: `eqm2`; query source: `eqm`.

`ele` remains an allowed train-only diagnostic source, but its electric-vs-acoustic domain difference must not be used to tune the primary metric or to redefine the primary population after results are seen.

## Frozen deterministic feature contract

Feature contract ID: `gfn-train-position-features-v1`.

For each decoded waveform:
1. require finite mono samples and sample rate exactly 44,100 Hz;
2. remove the waveform mean (DC);
3. compute non-overlapping 1,024-sample RMS frames over the full file;
4. define onset frame as the first frame whose RMS is at least 15% of the maximum frame RMS; fail the row if no positive finite maximum exists;
5. take exactly 65,536 samples starting at that frame boundary, zero-padding at the end if needed;
6. RMS-normalize that fixed segment to unit RMS when RMS is positive;
7. apply a Hann window and compute the real FFT power spectrum;
8. using the corpus-provided labeled fundamental frequency, compute log-power features for harmonics 1..12 by summing FFT-bin power inside ±25 cents of each harmonic center that remains below Nyquist; unavailable harmonic slots are filled with the minimum finite harmonic log-power for that row;
9. subtract the first-harmonic log-power from all 12 harmonic log-power features, making harmonic 1 exactly zero;
10. append four temporal RMS fractions over fixed post-onset regions: 0–100 ms, 100–300 ms, 300–700 ms, and 700–1,400 ms, each divided by the sum of those four RMS values plus a fixed epsilon `1e-12`.

Final feature vector length is exactly 16.

No learned embedding, neural network, pitch detector, source separator, or adaptive feature selection is permitted in V1.

## Frozen cross-session matching procedure

For each direction (`eqm` -> `eqm2`, then `eqm2` -> `eqm`):
1. fit per-feature mean and population standard deviation using **all 78 prototype-source rows only**;
2. replace any prototype standard deviation below `1e-12` with 1.0;
3. standardize both prototype and query vectors using only those prototype statistics;
4. for each eligible query row, restrict candidate prototypes to rows with the exact same corpus-labeled MIDI number;
5. choose the candidate with minimum ordinary Euclidean distance in the 16-dimensional standardized feature space;
6. ties are resolved deterministically by ascending `(string_number,fret)`;
7. count exact physical-position success only when predicted `(string_number,fret)` equals the query label.

Because candidates are restricted to the same MIDI pitch, this is deliberately **not** a pitch-recognition test. It is a physical-position timbre-discriminability probe conditional on known pitch.

## Frozen metrics

For each direction and pooled across both directions, report:
- eligible query count;
- exact `(string,fret)` correct count;
- exact-position accuracy;
- mean per-query chance baseline `mean(1 / candidate_count_for_that_MIDI)`;
- absolute accuracy lift over that chance baseline;
- confusion counts by true string -> predicted string;
- result per MIDI pitch and candidate count.

Also report dataset-integrity counters and feature-extraction failures.

There is **no production PASS threshold** in V1. The output is descriptive feasibility evidence only. No observed accuracy may retroactively change this preregistration or authorize downstream correctness.

## Determinism

Given identical decoded train audio bytes, metadata, and implementation bytes, canonical JSON output must be byte-identical. JSON serialization must use sorted keys and fixed compact separators.

## Interpretation boundary

A positive result would show only that some repeatable physical-position information exists in these isolated-note train recordings under this narrow cross-session comparison. A negative result would show only that this frozen feature/matching method did not recover enough signal in this corpus.

Neither outcome replaces the purpose-built independent physical-reference route, and neither outcome permits touching reserved `deb` / `ele_natural` audio without a later separate frozen authorization.
