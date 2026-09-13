# Songsterr Fresh V6 — Final Method Preregistration

Status: **FROZEN BEFORE ANY V6 REAL-CORPUS CORRECTNESS RESULT**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Purpose

This document freezes the final V6 admission-filter method from synthetic-only development before any V6 correctness result on Guitar-TECHS or any other untouched real corpus.

The currently running Guitar-TECHS work is reference-blind alignment/inventory only. No Guitar-TECHS Basic Pitch/V6 correctness has been computed or may influence this method freeze.

## Scientific question

V6 asks:

> Does the already-selected Basic Pitch MIDI exhibit a candidate-specific **onset-synchronous acoustic birth signature** relative to immediately preceding audio?

This is deliberately different from V1/V2/V4/V5 post-onset steady-state evidence and is not a threshold retune of a rejected line.

## Frozen implementation identity

Implementation:
`scripts/songsterr-fresh/onset_birth_corroboration_v6.py`

Implementation commit:
`3a6cbb144fec5613ab6350deb6539297d713df28`

Implementation blob SHA:
`2b18ef0ee710a6ad5ecb27253b977495db7d6534`

Contract:
`songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6`

Version: `6`.

Synthetic fixture manifest:
`scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`

Fixture freeze commit:
`ca71eb218ce701686e4a4806813ac84580defa78`

Controlled synthetic result:
`docs/checkpoints/SONGSTERR_FRESH_V6_SYNTHETIC_RESULT.md`

Synthetic-result commit:
`ed0b597d7e86f1756395445952db1f40b62e9b13`

Official synthetic run `34754079541` passed all 23 pre-frozen fixtures. Synthetic success is not external admission evidence.

## Frozen input contract

V6 may consume only:
- finite mono audio at exactly `44,100 Hz`;
- one existing event onset as integer sample index;
- that event's existing selected integer MIDI;
- selected MIDI range `40..88`.

V6 MUST NOT consume:
- reference/annotation truth;
- filename, dataset, player, song, style, category, guitar type, string/fret identity or corpus identity as classification features;
- Basic Pitch confidence or activation/decision surfaces;
- event duration/end;
- next onset, future events or reattack heuristics from the decoded event sequence;
- protected-song history or previous holdout correctness;
- downstream tablature/string/fret decisions.

It must preserve the event identity and selected MIDI exactly.

## Frozen signal design

Constants:
- sample rate: `44100`
- complex STFT frame length: `2048` samples
- hop: `256` samples
- FFT size: `8192`
- frame-end offsets relative to the event onset: `-1536,-1280,-1024,-768,-512,-256,0,256,512,768,1024,1280,1536` samples
- early-post novelty horizon: through `+1024` samples
- playable candidate MIDI set: every integer `40..88`
- maximum harmonic count: `6`
- minimum analysis RMS: `1e-5`
- minimum onset-innovation energy: `1e-6`
- candidate-template fundamental/max-harmonic onset-innovation ratio: `0.20`
- selected-template necessity fraction: `0.01`.

### Complex prediction deviation

For each required frame:
1. demean;
2. apply a Hann window;
3. compute an `8192`-point real FFT;
4. for frame `t >= 2`, predict the current complex spectrum from previous-frame magnitude and linearly extrapolated phase `2*phase[t-1] - phase[t-2]`;
5. complex prediction deviation is the magnitude of actual minus predicted complex spectrum.

If required context extends outside the audio, evidence is insufficient.

### Onset innovation

- pre-onset baseline is the bin-wise maximum complex prediction deviation across eligible frames ending at or before onset;
- early-post evidence is the bin-wise maximum complex prediction deviation across frames ending after onset and no later than `+1024` samples;
- onset innovation is the positive difference `max(0, post_max - pre_max)` per FFT bin.

If maximum analysis-frame RMS is below `1e-5`, classify insufficient.
If onset-innovation L2 energy is below `1e-6`, classify insufficient.

### Candidate harmonic templates

For each integer MIDI `40..88`:
1. find the strongest onset-innovation bin inside that MIDI's equal-tempered semitone cell `[m-0.5,m+0.5)`;
2. use that bin frequency as the candidate fundamental estimate;
3. sample harmonics 1..6 at nearest FFT bins, searching each nearest-bin neighborhood by +/-1 bin;
4. template harmonic weights are exactly `1/h`, then L2-normalized;
5. require at least three in-band harmonics;
6. require selected fundamental onset innovation / maximum selected-harmonic onset innovation >= `0.20` for the template to enter the polyphonic explanation dictionary.

This last rule prevents a nonexistent fundamental candidate from explaining another note primarily through coincident upper harmonics.

### Polyphonic onset explanation

Form one nonnegative onset-innovation feature vector over the union of bins touched by every valid candidate template.

Fit all valid candidate templates simultaneously with deterministic `scipy.optimize.nnls`.

Let:
- `R_full` be the full-dictionary residual norm;
- `R_without` be the residual after removing only the selected-MIDI template and refitting;
- `E` be the feature-vector L2 norm.

Selected-MIDI onset necessity is:
`(R_without - R_full) / E`.

## Frozen classification

Classes:
- `onset-birth-corroborated-candidate`
- `not-onset-birth-corroborated`
- `insufficient-evidence`.

The selected event is V6-positive **only** when:
- its template is physically valid under the frozen fundamental guard;
- its NNLS coefficient is strictly greater than zero;
- selected-template necessity fraction is >= `0.01`.

Valid finite evidence that fails any positive condition is `not-onset-birth-corroborated`.
Missing/truncated/low-support/nonfinite/solver-invalid evidence is `insufficient-evidence`.

No majority vote, fallback, alternate threshold, confidence rescue or post-hoc override is allowed.

## Frozen runtime

Future controlled V6 correctness execution must use:
- Python 3.10.x
- NumPy `1.26.4`
- SciPy `1.15.3`
- CPU execution for the V6 corroborator itself.

A later scoring preregistration may additionally pin audio-decoding/resampling and Basic Pitch packages required to create V6 inputs, but it may not change the V6 implementation or constants above.

## Real-audio preparation boundary

V6 itself requires 44.1-kHz mono audio. Any future external-scoring preregistration must freeze one deterministic canonical decode/downmix/resampling path **before correctness** and must pass the exact same canonical waveform to any event decoder and V6 where scientifically appropriate.

No resampling choice may be selected from correctness results.

## Precision-first synthetic decision retained

The frozen synthetic fixture contract intentionally rejects one ambiguous simultaneous-dyad lower-note case rather than loosening the admission rule to recover it. This is retained. V6 is an admission filter aimed at very high precision, not a recall-maximizing transcription rewrite.

## Holdout contamination boundary

Do not use correctness from:
- FLGD/V5;
- IDMT/V4;
- GuitarSet/V3;
- protected-song outcomes;
- any future Guitar-TECHS scoring result

to change this V6 method, thresholds, candidate set, feature family or positive-class definition.

After this method freeze, any amendment to V6 would constitute a new successor method and would require a new untouched external holdout; it cannot be evaluated as a revised V6 on a holdout whose correctness has already been exposed.

## Promotion boundary

This method freeze does not authorize a real correctness run by itself.

Before one official external correctness run, all of the following must exist:
1. immutable untouched-holdout inventory/alignment result;
2. exact scoring population and alignment identities;
3. frozen canonical audio/model runtime;
4. frozen reference matching/tolerances;
5. frozen uncertainty statistic and admission gates;
6. a single-run/deferred-reveal execution boundary.

Even a passing external run still requires an immutable result record followed by a separate policy review.

Until such a review explicitly approves admission:
- `modelValidationComplete:false`;
- customer-eligible events `0`;
- `mayAdvanceDelivery:false`;
- duration authority unchanged/paused;
- protected song remains embargoed;
- Production remains unchanged.

No Modal, Vercel heavy-GPU or L4 run is authorized by this document; those require explicit user approval under the standing compute rule.
