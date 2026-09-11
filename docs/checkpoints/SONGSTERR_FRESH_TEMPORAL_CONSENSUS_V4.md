# Songsterr Fresh — Temporal Consensus Pitch Corroboration V4

Status: **FROZEN IMPLEMENTATION / CONTROLLED SYNTHETIC CI GREEN / NO REAL CORPUS EVALUATED**

Recorded: 2026-09-11 America/Toronto

## Preregistration

Operative preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V4.md`
- initial prereg commit `a5cec402cf3bcd6c28ac3339d4d00de4d8cdf8b2`
- synthetic-only pre-implementation amendment commit `30b2769772d0a2a2edeaa8e92bff66ce3518fede`.

The amendment replaced the initially proposed plain real-cepstrum view with standard YIN after a generated E2 synthetic fixture exposed octave/harmonic aliasing. This happened before implementation freeze and before any GuitarSet, IDMT, protected-song, reference-tab, or other real correctness result was inspected.

## Frozen implementation

Evaluator:
- `scripts/songsterr-fresh/independent_pitch_corroboration_v4.py`
- implementation commit `6e9e11e60d0d6958c30edf6bb5d686d545936a19`
- contract `songsterr-fresh-temporal-consensus-pitch-corroboration-research-v4`
- version `4`.

Focused CI:
- `.github/workflows/songsterr-fresh-temporal-consensus-v4-ci.yml`
- workflow commit `736872e8fdf922c3975eda833ebd9616692bbd65`.

## Frozen V4 method

Input classification surface:
- isolated mono guitar audio only;
- exactly 44100 Hz;
- existing event onset `sourceStart` and integer `selectedMidi` only;
- playable MIDI range 40..88;
- duration/end/confidence/activation/reference/performer/style identity excluded.

Temporal rule:
- onset sample = `floor(sourceStart*44100 + 0.5)`;
- three exact 8192-sample windows;
- offsets from onset = `1024`, `7168`, `13312` samples;
- final required sample = onset + `21504`.

Spectral view in every window:
- demean float64 window;
- exact-zero demeaned energy => insufficient;
- `numpy.hanning(8192)`;
- rFFT size `32768`;
- complete MIDI 40..88 semitone-cell competition;
- candidate fundamental = strongest FFT bin in `[m-0.5,m+0.5)`;
- coherent harmonics 1..6 below Nyquist;
- each harmonic sampled from nearest FFT bin +/- one neighbor;
- magnitude floor `1e-15` only for finite log;
- score = mean natural-log harmonic magnitude;
- strict unique global winner; exact tie fails.

YIN view in every window:
- `librosa==0.11.0`;
- `librosa.yin` with `sr=44100`, `frame_length=8192`, `hop_length=8192`, `center=False`;
- `fmin=midi_to_hz(39.5)`;
- `fmax=midi_to_hz(88.5)`;
- `trough_threshold=0.1`;
- one finite positive f0 required;
- convert f0 to floating MIDI;
- winner = playable semitone cell `[m-0.5,m+0.5)` containing the estimate.

Classification:
- `independently-corroborated-candidate` only when selected MIDI is both spectral unique winner and YIN winner in all three windows;
- valid disagreement/nonunique spectral winner => `not-independently-corroborated`;
- invalid/nonfinite/truncated/zero-energy/YIN-invalid required view => `insufficient-evidence`;
- no voting, fallback, score margin threshold, confidence, duration, next onset, event deletion, or learned calibration.

## Controlled synthetic verification

GitHub Actions run:
- run `34653819306`
- job `103441756944`
- exact source `736872e8fdf922c3975eda833ebd9616692bbd65`
- conclusion: **SUCCESS**.

Green steps:
- Python 3.10 setup;
- NumPy `1.26.4`, librosa `0.11.0`, SoundFile `0.13.1` install;
- evaluator compile;
- synthetic-only V4 self-test;
- preregistered constant enforcement;
- evidence identity and duration guards;
- controlled-only source boundary.

Synthetic cases verified:
- stable low MIDI 40;
- stable mid MIDI 64;
- stable high MIDI 88;
- +25-cent in-cell detune;
- attack transient/noise followed by stable pitch;
- wrong octave;
- stronger adjacent semitone;
- stronger fifth;
- polyphonic stronger competitor;
- temporal pitch change;
- exact-zero audio;
- truncated late window;
- strict spectral tie rejection;
- complete 40..88 spectral competition.

Policy-boundary markers remained false/zero:
- GuitarSet evaluated: false;
- IDMT evaluated: false;
- protected song evaluated: false;
- reference/pro scorer/archived V143/GOAT used: false;
- duration authority changed: false;
- admission decision made: false;
- model validation complete: false;
- may advance delivery: false;
- customer eligible events: 0.

The CI source guard also confirms the evaluator has no dataset/protected-fixture download path and no subprocess/network execution surface.

## External validation boundary

GuitarSet is historical after V3 and MUST NOT be reused as V4 pass/fail validation.

Untouched candidate corpus metadata only:
- IDMT-SMT-Guitar Dataset, Zenodo v1.0.0;
- DOI `10.5281/zenodo.7544110`;
- archive `IDMT-SMT-GUITAR_V2.zip`;
- archive MD5 `06796e08731bccffaed6ae59361486e4`.

No IDMT archive has been downloaded or scored by V4 in this workstream.

**Holdout scoring remains closed.** V4 must stop here until the user explicitly reopens external/holdout validation. Before any IDMT correctness result, a separate versioned external-validation preregistration must freeze allowed subsets/files, manifest, XML interpretation, matching, gates, uncertainty and execution provenance.

## Promotion boundary

Synthetic success is not semantic correctness and creates no authority.

Current state remains:
- `modelValidationComplete:false`;
- customer eligible events `0`;
- `mayAdvanceDelivery:false`;
- duration authority unchanged;
- duration research paused;
- persistent Policy C `UNENROLLED`.

No protected-song V4 run is authorized. No GuitarSet rerun is authorized. No threshold tuning is authorized.
