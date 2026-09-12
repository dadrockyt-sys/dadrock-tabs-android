# Songsterr Fresh Model-Evidence Admission Preregistration V5

Status: **AUTHORIZED SUCCESSOR / SYNTHETIC DEVELOPMENT ONLY**

Branch: `songsterr-fresh-pipeline-v1`

This document is frozen before V5 implementation and before any V5 correctness result on a real annotated corpus.

## Purpose

V5 is a new successor after the closed/rejected V4 line. It is not a V4 threshold retune. V5 addresses a general signal-processing limitation of single-winner pitch tests: real guitar audio is frequently polyphonic and strong harmonics from one note can make another physically present note fail a winner-take-all test.

V5 therefore asks a different question:

> Is the selected Basic Pitch MIDI independently necessary to explain the observed polyphonic harmonic spectrum across multiple post-onset views?

The method is reference-blind and admission-filter-only. It does not change Basic Pitch event identity or MIDI.

## Non-contamination boundary

V5 constants and implementation MUST NOT be chosen from:
- protected-song historical outcomes;
- GuitarSet V3 correctness results;
- IDMT V4 correctness results, including dataset/bit-depth strata;
- post-hoc threshold sweeps on any previously observed holdout.

Previously observed corpora may remain historical diagnostics only. They are not untouched V5 admission holdouts.

Before any future real V5 external correctness scoring, a separate untouched holdout and exact scoring preregistration must be frozen.

## Input contract

V5 may consume only:
- mono isolated-guitar audio;
- sample rate exactly `44100` Hz;
- existing event onset as integer sample index;
- existing selected MIDI as integer;
- selected MIDI playable range `40..88`.

V5 MUST NOT consume:
- reference/annotation truth;
- performer, song, dataset, style, bit depth, filename or corpus identity as classification features;
- Basic Pitch confidence, activation surface, duration/end, next onset, reattack logic or future events;
- historical pass/fail labels;
- Demucs/model confidence;
- downstream tablature/string/fret decisions.

It must preserve event identity and selected MIDI exactly.

## Frozen V5 signal design

Contract name:
`songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5`

### Temporal views

Use exactly three post-onset analysis windows:
- sample offsets from event onset: `2048`, `8192`, `14336`;
- each window length: `8192` samples;
- FFT size: `32768`;
- Hann window after demeaning.

If any required window extends outside the audio, classify `insufficient-evidence`.

If demeaned RMS of any required window is below `1e-4`, classify `insufficient-evidence`.

### Candidate space

Candidate MIDI set is exactly all integers `40..88`.

For each MIDI candidate and temporal view:
1. Search the candidate's equal-tempered semitone cell `[m-0.5, m+0.5)` for the strongest FFT magnitude bin.
2. The frequency of that bin is the candidate's coherent `f_hat` for that view.
3. Build a nonnegative harmonic template at integer multiples `1..8` of `f_hat`, stopping before Nyquist.
4. Each harmonic contributes at the nearest FFT bin and its immediate neighbors using the maximum magnitude location; harmonic template amplitude weight is exactly `1/h` before L2 normalization.
5. Candidate templates are L2-normalized. Templates with fewer than three in-band harmonics are invalid for that view.

### Polyphonic explanation

For each temporal view, form one nonnegative spectral feature vector from the union of all bins touched by any valid candidate template.

Fit all valid candidate templates simultaneously using deterministic nonnegative least squares (NNLS). The implementation must use `scipy.optimize.nnls` with pinned SciPy `1.15.3`.

Define:
- `R_full`: L2 residual norm from the full candidate dictionary;
- `R_without`: L2 residual norm after removing only the selected MIDI template and refitting all remaining candidates;
- `E`: L2 norm of the observed feature vector.

The selected MIDI is **necessary in a view** only when all are true:
- selected template is valid;
- selected NNLS coefficient is strictly greater than zero;
- `E > 0`;
- `(R_without - R_full) / E >= 0.01`.

The `0.01` necessity fraction is frozen before implementation and may not be tuned from real-corpus results. Synthetic-only amendment is permitted before any real corpus access if the method is mathematically ill-posed or cannot satisfy the preregistered synthetic contract; any amendment must be separately documented before implementation/result use.

### Fundamental-presence guard

To reject octave/harmonic aliases, the selected MIDI must also have a resolved local maximum inside its own fundamental semitone cell in every temporal view, and that fundamental-bin magnitude must be at least `0.05` times the maximum magnitude among its own harmonics 1..8 in the same view.

This guard is intentionally conservative and frozen before implementation.

### Temporal consensus

Classification:
- `independently-corroborated-candidate` only if the selected MIDI is necessary **and** passes the fundamental-presence guard in all three views;
- `not-independently-corroborated` if evidence is finite/valid but any view fails necessity or the fundamental guard;
- `insufficient-evidence` for truncated windows, low support, invalid/nonfinite transforms, invalid templates or solver failure.

No voting, fallback, average confidence or majority rule is allowed.

## Frozen runtime

Controlled V5 workbench/CI runtime:
- Python 3.10.x;
- NumPy `1.26.4`;
- SciPy `1.15.3`.

No model inference is required by the V5 corroborator itself.

## Synthetic development contract

Before any real-corpus V5 evaluation, controlled CI must include deterministic synthetic fixtures covering at least:
- clean monophonic MIDI 40, 64 and 88;
- +25 cent and -25 cent detuning;
- attack-noise contamination;
- octave-up and octave-down selected-MIDI traps;
- dominant second harmonic;
- stronger neighboring semitone;
- perfect-fifth dyad;
- major/minor triads where the selected note is root, third and fifth in separate fixtures;
- dense six-note playable mixture;
- equal-energy close dyad;
- temporal pitch change after onset;
- silence;
- low-level noise below support threshold;
- truncated audio;
- exact event/MIDI identity preservation.

Expected behavior must be frozen in the synthetic fixture manifest before CI results are used to claim readiness.

## Promotion boundary

Synthetic success does not authorize customer admission.

V5 remains research-only until all of the following occur in order:
1. implementation + synthetic manifest frozen;
2. controlled synthetic/contract CI green;
3. untouched external corpus selected using metadata/inventory only;
4. exact corpus manifest/annotation semantics/matching/uncertainty/pass gates frozen before results;
5. one official external correctness run;
6. immutable result record;
7. separate policy review.

Until a later policy review explicitly approves V5:
- `modelValidationComplete:false`;
- customer-eligible events `0`;
- `mayAdvanceDelivery:false`;
- duration authority unchanged;
- duration research remains paused;
- protected song remains embargoed.

## Forbidden shortcuts

Do not:
- retune V4 or rerun IDMT/GuitarSet as a V5 admission holdout;
- tune V5 constants against previously observed real-corpus correctness;
- use dataset/bit-depth identity as a classifier feature;
- delete or rewrite events/MIDI;
- use duration/next onset/Basic Pitch confidence to rescue V5;
- open protected-song V5 evaluation before future external validation and separate policy approval.
