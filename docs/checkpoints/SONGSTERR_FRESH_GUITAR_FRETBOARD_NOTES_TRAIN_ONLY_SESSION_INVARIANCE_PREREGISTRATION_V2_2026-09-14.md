# Songsterr Fresh — Guitar Fretboard Notes Train-Only Session-Invariance Preregistration V2

Date: 2026-09-14 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: FROZEN BEFORE V2 RESULT EXECUTION

## Purpose

This is a zero-additional-cost, NON_HOLDOUT feasibility experiment using only the already-exposed Guitar Fretboard Notes `train` sources. It asks one narrow follow-up to V1:

> Conditional on the exact corpus-labeled MIDI pitch, does deterministic per-session robust normalization make physical `(string,fret)` discrimination more session-invariant across the two acoustic train sessions `eqm` and `eqm2`?

The V1 result is already known and is the fixed comparison baseline. This V2 preregistration is frozen before any V2 real-audio result is executed or observed.

This study does **not** establish Songsterr Fresh correctness, holdout validity, production eligibility, physical-reference authority, or any Basic Pitch/V6 authorization.

## External corpus identity and access boundary

Dataset: `collegefishiesd/guitar-fretboard-notes`
Pinned repository revision: `a33a26243e88e7ccd4893bee30eac3219ec8bef8`
Declared license: `CC-BY-SA-4.0`
Pinned train parquet: `data/train-00000-of-00001.parquet`
Previously observed canonical train parquet SHA-256: `86ac522303251f2a5d77376261c23bf1af09b3c69183ad365b105cd230354add`

Allowed V2 sources, all from `train` only:
- `ele`: 78 rows;
- `eqm`: 78 rows;
- `eqm2`: 78 rows;
- total: 234 rows.

Reserved and still untouched:
- `test`, source `deb`: 78 rows;
- `validation`, source `ele_natural`: 78 rows.

V2 must not load, stream, download, decode, inspect, feature-extract, listen to, score, normalize from, tune on, or otherwise consume `deb` or `ele_natural`.

## Hard prohibitions

V2 must not:
- access any split other than `train`;
- access any source other than `ele`, `eqm`, `eqm2`;
- use Basic Pitch;
- use V6;
- use archived V143/Gomyway or GOAT/reference scoring;
- use any Songsterr customer/protected-song audio;
- use any evaluated-audio-derived reference truth;
- use a learned embedding, neural network, learned classifier, optimizer, hyperparameter sweep, threshold sweep, or adaptive feature selection;
- change feature/normalization/matching rules after V2 real results are observed;
- claim that this isolated-note feasibility result establishes correctness for chords, simultaneous same-pitch notes, bends, slides, hammer-ons, pull-offs, rearticulation, overlapping sustain, noisy deployment audio, or full songs;
- authorize customer delivery or correctness execution.

Required downstream state remains:
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

## Acquisition and integrity gate

The implementation may retrieve only the pinned `train` parquet at the pinned revision.

Before feature extraction it must fail closed unless all are true:
- train parquet SHA-256 equals `86ac522303251f2a5d77376261c23bf1af09b3c69183ad365b105cd230354add`;
- row count is exactly 234;
- observed source set is exactly `{ele, eqm, eqm2}`;
- each source contributes exactly 78 rows;
- every row has `string_number` in 1..6;
- every row has `fret` in 0..12;
- every row has `midi_number` in 40..76;
- every `(source,string_number,fret)` identity is unique;
- every source contains the complete 78-position six-string fret-0..12 grid;
- decoded audio is finite mono at exactly 44,100 Hz;
- no reserved source identifier (`deb`, `ele_natural`) occurs.

The result JSON must record the pinned revision, train parquet SHA-256, observed sources, row count, feature contract ID, normalization contract ID, and all downstream authorization fields.

## Frozen study population

The primary population is identical to V1: same-pitch ambiguous-position groups only. A query is eligible when its corpus-labeled MIDI number has at least two distinct prototype `(string_number,fret)` candidates in the compared source.

Primary directions are frozen as:
- `eqm` prototypes -> `eqm2` queries;
- `eqm2` prototypes -> `eqm` queries.

`ele` is diagnostic/domain-stress only. The frozen secondary directions are:
- `eqm` -> `ele`;
- `ele` -> `eqm`;
- `eqm2` -> `ele`;
- `ele` -> `eqm2`.

Secondary `ele` results may not redefine the primary metric, feature contract, normalization contract, or interpretation rule.

## Frozen V2 feature extraction

Feature contract ID: `gfn-train-position-features-v2`.

V2 intentionally keeps the V1 per-row 16-dimensional extraction unchanged so the experiment isolates the effect of session normalization.

For each decoded waveform:
1. require finite mono samples at exactly 44,100 Hz;
2. remove DC by subtracting the waveform mean;
3. compute non-overlapping 1,024-sample RMS frames over the whole file;
4. choose the first frame whose RMS is at least 15% of the maximum frame RMS; fail if there is no positive finite maximum;
5. take exactly 65,536 samples from that frame boundary, zero-padding at the end if required;
6. RMS-normalize that segment to unit RMS;
7. apply a Hann window and compute real-FFT power;
8. using the corpus-provided labeled fundamental frequency, compute harmonic log-power for harmonics 1..12 in fixed +/-25-cent bands below Nyquist; unavailable harmonic slots are filled with the minimum finite harmonic log-power from that row;
9. subtract harmonic-1 log-power from all 12 harmonic log-power values;
10. append four temporal RMS fractions for 0-100 ms, 100-300 ms, 300-700 ms, and 700-1,400 ms, each divided by the sum of the four RMS values plus `1e-12`.

Final raw feature vector length is exactly 16. No additional learned or selected feature may be added.

## Frozen V2 per-session robust normalization

Normalization contract ID: `gfn-train-session-robust-mad-v2`.

Normalization is performed separately for each source (`ele`, `eqm`, `eqm2`) using all 78 rows of that source and **without using string/fret labels to compute any statistic**.

For each of the 16 feature dimensions in a source:
1. compute the median across all 78 source rows;
2. compute MAD = median(abs(x - median));
3. set primary scale = `1.4826 * MAD`;
4. if primary scale is non-finite or `< 1e-9`, replace it with the population standard deviation (`ddof=0`) of that feature over the same 78 rows;
5. if the fallback standard deviation is non-finite or `< 1e-9`, use scale `1.0`;
6. transform every row from that source as `(x - median) / scale`.

The statistics for a source are computed from that source only. Thus `eqm` rows use only `eqm` medians/scales, `eqm2` rows use only `eqm2` medians/scales, and `ele` rows use only `ele` medians/scales.

This is explicitly a train-only, transductive session-alignment probe: query-source distribution statistics are permitted because V2 is NON_HOLDOUT feasibility work. This normalization must never be described as untouched external validation behavior.

## Frozen matching rule

For every frozen direction:
1. use the independently robust-normalized 16-D vectors for the prototype and query sources;
2. for each eligible query, restrict prototype candidates to the exact same corpus-labeled integer MIDI number;
3. compute ordinary Euclidean distance in the 16-D normalized feature space;
4. choose the minimum-distance candidate;
5. resolve exact distance ties by ascending `(string_number,fret)`;
6. count success only when predicted `(string_number,fret)` exactly equals the query label.

No candidate outside the exact same labeled MIDI may be considered. This remains a physical-position discriminability study conditional on known pitch, not pitch recognition.

## Frozen primary metrics

For each primary direction and pooled across the two primary directions, report:
- eligible query count;
- exact-position correct count;
- exact `(string,fret)` accuracy;
- mean per-query chance baseline `mean(1 / candidate_count_for_that_MIDI)`;
- accuracy lift over chance;
- confusion counts by true string -> predicted string;
- per-MIDI query/correct/candidate counts.

Also report:
- absolute directional accuracy gap `abs(accuracy(eqm->eqm2) - accuracy(eqm2->eqm))`;
- all four frozen `ele` diagnostic direction metrics;
- integrity counters;
- feature-extraction failure count;
- normalization finite-value checks;
- canonical result SHA-256 when produced by CI.

## Frozen V1 comparison baseline

The already-observed V1 primary baseline is fixed as:
- `eqm` -> `eqm2`: 41/68 = `0.6029411764705882`;
- `eqm2` -> `eqm`: 32/68 = `0.47058823529411764`;
- pooled: 73/136 = `0.5367647058823529`;
- pooled chance baseline: `0.39705882352941174`;
- pooled lift over chance: `0.13970588235294118`;
- absolute directional accuracy gap: `0.13235294117647056`.

These constants are comparison references only; they are not tunable targets.

## Frozen interpretation rule

There is no production PASS threshold.

For this V2 feasibility question only:
- `SESSION_INVARIANCE_IMPROVED` requires **both** pooled V2 exact-position accuracy `>` `0.5367647058823529` **and** V2 absolute directional gap `<` `0.13235294117647056`;
- `MIXED` applies when exactly one of those two conditions is true;
- `NO_IMPROVEMENT` applies when neither condition is true;
- equality to a V1 baseline value does not satisfy the corresponding strict-improvement condition.

This classification is descriptive NON_HOLDOUT evidence only. None of the three outcomes authorizes Basic Pitch, V6, correctness, reserved-source access, model validation, customer eligibility, or delivery.

## Determinism and synthetic contract tests

Before real V2 execution, synthetic tests must pass and enforce at minimum:
- exact pinned dataset revision and train-only URL/path constants;
- exact allowed and reserved source sets;
- fail-closed metadata/source/row-count/identity/grid gates;
- train parquet SHA-256 gate;
- 16-D deterministic feature extraction;
- deterministic independent source-wise median/MAD normalization with the exact fallbacks above;
- normalization statistics independent of row ordering;
- exact same-MIDI candidate restriction;
- deterministic `(string,fret)` tie-breaking;
- primary directions exactly `eqm<->eqm2`;
- `ele` diagnostics cannot enter the primary pooled result;
- canonical JSON byte determinism;
- all downstream authorization fields remain false/zero.

Given identical train parquet bytes, implementation bytes, and runtime dependencies, canonical JSON output must be byte-identical.

## Execution boundary

Only after this preregistration is committed may V2 implementation/tests/workflow be committed and ordinary GitHub CPU CI execute the real train-only V2 study. No V2 result may be used to modify this preregistration.

The reserved `deb` and `ele_natural` sources remain untouched unless a later, separate preregistration is frozen before any access.
