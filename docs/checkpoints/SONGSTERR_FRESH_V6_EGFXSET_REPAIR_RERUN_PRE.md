# Songsterr Fresh V6 — EGFxSet Repaired One-Shot Pre-Run Freeze

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: `AUTHORIZED_REPAIRED_ONE_SHOT_PRE_RUN`

## User authorization

After the first EGFxSet one-shot ended before decoded output because of a NumPy/TFLite runtime incompatibility, the user explicitly instructed: `Please fix and rerun`.

This authorizes exactly **one repaired, non-authorizing rerun** of the same frozen EGFxSet candidate. It does not authorize V6 correctness, model validation, customer eligibility, delivery, tuning, retries beyond this single repaired attempt, alternate candidates, or any closed/reserved dataset line.

Global authorization fields remain unchanged:

- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

## Frozen candidate — unchanged

- dataset: EGFxSet version 1.0
- Zenodo DOI: `10.5281/zenodo.7044411`
- archive: `Clean.zip`
- archive MD5: `cdb1b401960f56becc8640387910e78a`
- member: `Clean/Bridge/6-0.wav`
- frozen member bytes from first attempt: `722976`
- frozen member SHA-256 from first attempt: `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`
- independent physical label: string `6`, fret `0`
- expected MIDI: `40` (E2)

No candidate switch is allowed.

## Prior failure — fixed cause only

The first authorized attempt installed:

- `basic-pitch==0.4.0`
- `numpy==2.2.6`
- `tflite-runtime==2.14.0`

The TFLite extension was compiled against NumPy 1.x and failed during model initialization with:

`AttributeError: _ARRAY_API not found`

No decoded-note artifact was produced.

## Prospectively frozen environment correction

The repaired one-shot changes **only the dependency compatibility layer**:

- Python: `3.10.21`
- Basic Pitch: `0.4.0`
- TFLite Runtime: `2.14.0`
- NumPy: `1.26.4`
- CPU only

The successor workflow must install and verify these exact versions before media access. `numpy==1.26.4` satisfies Basic Pitch 0.4.0's declared `numpy>=1.18` requirement while remaining on the NumPy 1.x ABI expected by the observed TFLite runtime.

No Basic Pitch algorithm setting changes are permitted.

## Frozen Basic Pitch/settings — unchanged

- minimum MIDI: `40`
- maximum MIDI: `88`
- onset threshold: `0.5`
- frame threshold: `0.3`
- minimum note length: `127.7 ms`
- bends: false
- melodia: true
- input: exact clean isolated EGFxSet member above
- deterministic mapper: unchanged standard tuning MIDI `[40,45,50,55,59,64]`

## Frozen scoring — unchanged

1. Execute `scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py` exactly once on the candidate.
2. No listening, waveform inspection, trimming, denoising, EQ, gain tuning, threshold changes, output-driven adjustments, alternate candidates, or second repaired attempt.
3. `PASS_RUNTIME` requires successful one-shot inference and parseable decoded output.
4. `PASS_PITCH` requires a non-empty decoded artifact and the set of all emitted MIDI values exactly `{40}`.
5. `PASS_POSITION` requires every emitted event to map uniquely to string `6`, fret `0`, reconstructed MIDI `40`.
6. Overall PASS requires runtime + pitch + position PASS.
7. Report note count and MIDI histogram diagnostically.
8. PASS remains non-authorizing smoke evidence only; FAIL remains diagnostic only.

## Execution boundary

This checkpoint is committed **before** the repaired workflow is created/executed. The successor workflow may differ from the original only where needed to enforce the frozen environment correction and identify the repaired result artifact. The original workflow and original result remain immutable historical evidence.

Exactly one repaired inference attempt is authorized. Do not rerun if it fails for any reason without another explicit user instruction.
