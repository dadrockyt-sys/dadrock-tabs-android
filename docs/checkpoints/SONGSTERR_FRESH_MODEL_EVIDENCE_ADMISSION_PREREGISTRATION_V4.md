# Songsterr Fresh — Model-Evidence Admission Preregistration V4

Status: **PREREGISTERED SUCCESSOR / SYNTHETIC DEVELOPMENT ONLY / NOT ADMISSION AUTHORITY**

Recorded: 2026-09-11 America/Toronto

Branch: `songsterr-fresh-pipeline-v1`

## Purpose

V1, V2, and V3 are closed as admission-authority candidates. V3 completed a frozen external validation and failed its preregistered precision gates. V4 is a new successor, not a patch to V3.

V4 asks a narrower question:

> Can a deliberately conservative, duration-free, model-independent temporal-consensus signal test identify a subset of existing Basic Pitch note events whose selected MIDI remains supported across multiple post-onset time views and two distinct signal representations?

V4 does **not** change Basic Pitch, does not alter event onset/MIDI identity, and does not authorize delivery.

## Preregistration amendment before implementation

The initial V4 draft proposed a real-cepstrum second view. Before implementation and before any real-corpus/protected-song execution, a synthetic-only E2 fixture exposed octave/harmonic aliasing: the plain cepstral maximum preferred a high harmonic rather than the synthetic fundamental.

Because this occurred entirely on generated synthetic audio, before implementation freeze and before any external correctness result, View 2 is replaced here with standard YIN fundamental estimation. No GuitarSet event, IDMT event, protected-song event, reference tab, or historical V3 false-positive example was inspected to make this change.

This amended document is the operative V4 preregistration for implementation.

## Anti-retuning boundary

V4 may use only the qualitative historical fact that V1–V3 failed admission. It MUST NOT use:
- V3 event-level GuitarSet errors;
- V3 per-track errors;
- V3 false-positive examples;
- V3 player/mode differences;
- the protected-song V1/V2 event outcomes;
- any threshold sweep against GuitarSet or the protected song;
- any reference tab/pro scorer/GOAT/archive signal.

The historical V3 aggregate result (89.04% precision; failed frozen gates) is a closeout fact only and may not select V4 constants.

GuitarSet is now **historical only** for successor design. It MUST NOT be reused as V4's pass/fail validation corpus.

## Fixed input contract

V4 receives only:
- isolated-guitar mono WAV audio;
- sample rate;
- existing event `sourceStart` seconds;
- existing integer `selectedMidi`.

Permitted provenance identifiers may be recorded but MUST NOT affect classification.

Forbidden classification inputs:
- Basic Pitch confidence;
- Basic Pitch note end;
- any duration/release estimate;
- next onset;
- activation sidecars;
- decision-surface diagnostics;
- reference notes/tabs;
- performer/style/track identity;
- V1/V2/V3 historical outcome labels.

## Frozen playable range / sample rate

- sample rate: exactly `44100` Hz;
- playable MIDI range: exactly `40..88` inclusive;
- every MIDI in `40..88` competes in the spectral view;
- no local spectral competitor subset.

## Frozen temporal windows

Three post-onset analysis windows are required. Each is exactly `8192` samples.

Relative start offsets from the rounded onset sample `floor(sourceStart*44100 + 0.5)`:
- window A: `1024` samples;
- window B: `7168` samples;
- window C: `13312` samples.

Thus the final required sample is onset + `21504` samples.

Rationale frozen before real results: a plucked guitar note should exhibit pitch evidence beyond the immediate attack transient. Requiring the same selected MIDI to survive separated early/mid/late views is intentionally conservative and trades recall for precision.

If any required window is outside the audio, classification is `insufficient-evidence`.

## View 1 — coherent harmonic spectrum

For each temporal window:
1. convert to float64 and reject non-finite samples;
2. subtract the window mean;
3. if the demeaned window is exactly zero-energy, the event is `insufficient-evidence`;
4. multiply by `numpy.hanning(8192)`;
5. compute `rfft` with exact FFT size `32768`;
6. for each MIDI candidate `40..88`, define its non-overlapping equal-tempered semitone cell `[m-0.5,m+0.5)`;
7. choose the maximum-magnitude FFT bin whose frequency lies in that cell; ties use the lower-frequency bin because `argmax` returns the first maximum;
8. use that winning fundamental frequency coherently for harmonics `1..6` that remain below Nyquist;
9. for each harmonic, sample the maximum magnitude across the nearest FFT bin and its immediate neighbors;
10. floor each sampled magnitude at exactly `1e-15` only to keep the logarithm finite;
11. spectral score = arithmetic mean of natural-log harmonic magnitudes.

The spectral winner is the unique MIDI with strictly greatest score across all `40..88`. Any exact tie means no unique winner.

## View 2 — standard YIN fundamental estimate

For each same raw 8192-sample temporal window, use `librosa.yin` version `0.11.0` with exactly:
- `sr=44100`;
- `frame_length=8192`;
- `hop_length=8192`;
- `center=False`;
- `fmin = midi_to_hz(39.5)`;
- `fmax = midi_to_hz(88.5)`;
- `trough_threshold=0.1` (the standard YIN/librosa default threshold; frozen before real data).

Exactly one frame/fundamental estimate is expected.

Convert finite positive YIN frequency to floating MIDI using `69 + 12*log2(f0/440)`. The YIN winner is the integer MIDI whose equal-tempered semitone cell `[m-0.5,m+0.5)` contains that estimate. If no playable cell contains the estimate, the YIN view does not select the input MIDI.

No confidence score, probability, score margin, or learned calibration is used.

## Frozen V4 classification

For each of the three windows there are exactly two required decisions: spectral unique winner and YIN semitone-cell winner.

- `independently-corroborated-candidate` only if `selectedMidi` is the spectral strict unique winner **and** the YIN winner in **all three** windows.
- `not-independently-corroborated` if every required window is valid but any of the six decisions disagrees or the spectral view has no unique winner.
- `insufficient-evidence` if input is invalid/non-finite, MIDI/sample-rate contract fails, any required window is truncated, any window has exactly zero demeaned energy, or YIN cannot return one finite positive estimate.

There is no voting, fallback, confidence average, learned calibration, reference-informed threshold, or event deletion.

## Identity / policy guards

V4 MUST preserve every input event's original identity, onset and MIDI. Classification is an attached research label only.

V4 MUST NOT:
- set `modelValidationComplete:true`;
- create customer-eligible events;
- set `mayAdvanceDelivery:true`;
- alter duration authority;
- invoke protected-song audio;
- invoke GuitarSet during development/CI;
- invoke IDMT during development/CI;
- import archived V143/Gomyway logic, GOAT, or professional/reference scorers.

## Synthetic-only development protocol

Before any external corpus execution, implementation must pass deterministic synthetic/contract tests covering at minimum:
- low/mid/high playable MIDI;
- modest in-cell detuning;
- attack-transient contamination followed by stable pitch;
- wrong octave selection;
- stronger adjacent semitone;
- stronger fifth/competing pitch;
- temporal pitch change after onset;
- polyphonic competing tone;
- exact-zero audio;
- truncated late window;
- strict spectral tie behavior;
- full-range `40..88` spectral competition;
- event identity preservation;
- all non-promotion guards false/zero.

No real annotated guitar corpus may be used to choose or change these constants.

## Future external validation candidate — execution NOT authorized here

Candidate untouched corpus: **IDMT-SMT-Guitar Dataset**, Zenodo version `1.0.0`, DOI `10.5281/zenodo.7544110`.

Candidate archive identity:
- `IDMT-SMT-GUITAR_V2.zip`
- MD5 `06796e08731bccffaed6ae59361486e4`.

Public dataset documentation describes mono RIFF WAVE audio at 44100 Hz and guitar-transcription subsets with XML parameter annotations, including pitch and onset information.

This preregistration does **not** authorize downloading, model inference, scoring, holdout evaluation, or pass/fail use of IDMT-SMT-Guitar. Existing checkpoint scope keeps holdout scoring closed unless explicitly reopened by the user.

Before any future IDMT execution, a separate versioned external-validation preregistration must freeze:
- exact allowed subsets/files;
- exact archive/file manifest;
- any exclusions from public documentation only;
- exact XML field interpretation;
- one-to-one matching rule;
- minimum positive count;
- uncertainty metric;
- overall/stratum pass gates;
- execution provenance contract.

All of that must be committed before any V4 correctness result is viewed.

## Current acceptance state

V4 preregistration itself changes no authority:
- `modelValidationComplete:false`;
- customer-eligible events `0`;
- `mayAdvanceDelivery:false`;
- duration authority unchanged;
- duration research paused;
- persistent Policy C `UNENROLLED`.

## Next allowed steps

1. implement the amended V4 temporal-consensus evaluator exactly as preregistered;
2. add deterministic synthetic fixtures/self-tests;
3. add focused controlled CI that cannot access GuitarSet, IDMT, or the protected song;
4. freeze method/implementation after green CI;
5. stop before any real external-corpus scoring unless holdout evaluation is explicitly reopened.
