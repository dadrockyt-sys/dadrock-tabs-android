# Songsterr Fresh V6 — Synthetic Onset-Birth Result

Status: **CONTROLLED SYNTHETIC CONTRACT GREEN / NO REAL-CORPUS EVIDENCE**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Authority

This record is synthetic-development evidence only under `SONGSTERR_FRESH_SUCCESSOR_RESEARCH_CHARTER_V6.md`.

It does not authorize model/customer admission, Production, protected-song execution, duration work, or any reopening of archived V143/Gomyway.

Authority remains:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`.

## Frozen synthetic inputs

Research charter commit:
`2b96fba0e3df955e62386691023cb31eeb2d11f6`

Fixture manifest:
`scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`

Fixture-manifest freeze commit:
`ca71eb218ce701686e4a4806813ac84580defa78`

Implementation:
`scripts/songsterr-fresh/onset_birth_corroboration_v6.py`

Implementation commit:
`3a6cbb144fec5613ab6350deb6539297d713df28`

CPU CI workflow:
`.github/workflows/songsterr-fresh-v6-synthetic-ci.yml`

Workflow creation/source commit:
`45328f1d07644eef62f8fa7ab5b22f798f65fa20`

## Method under synthetic test

Contract:
`songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6`

The method is reference-blind and asks whether the selected Basic Pitch MIDI has a candidate-specific onset innovation relative to immediately preceding audio.

Controlled constants in this synthetic execution:
- sample rate: 44,100 Hz
- complex STFT frame: 2,048 samples
- hop: 256 samples
- FFT: 8,192
- frame-end offsets: -1536 through +1536 samples in 256-sample increments
- post-onset innovation horizon: +1024 samples
- maximum harmonics: 6
- minimum analysis RMS: `1e-5`
- minimum onset-innovation energy: `1e-6`
- valid-template fundamental/max-harmonic onset-innovation ratio: `0.20`
- selected-template necessity fraction: `0.01`
- polyphonic explanation: deterministic SciPy NNLS on the positive complex-domain onset-innovation spectrum.

A candidate template that lacks meaningful fundamental onset innovation is excluded from the explanation dictionary rather than being allowed to explain another pitch only through its harmonics.

## Frozen fixture behavior

23 deterministic fixtures were frozen before the implementation commit.

They cover:
- clean low/mid/high notes;
- +/-25-cent detuning;
- true note with attack noise;
- already-sounding selected pitch;
- octave/harmonic alias traps;
- selected pitch entering over an already-sounding lower pitch;
- simultaneous dyads and triads;
- neighboring-semitone false selection;
- reattack;
- unrelated transient only;
- deliberately weak/ambiguous selected note under a stronger simultaneous note;
- silence / low noise;
- truncated pre/post context;
- exact selected-MIDI identity preservation.

The fixture contract intentionally rejects an ambiguous lower note in one simultaneous dyad rather than weakening the precision-oriented gate to recover it. Synthetic recall is not an admission objective.

## Official controlled CPU run

Workflow: `Songsterr Fresh V6 Synthetic CI`

- run ID: `34754079541`
- run number: `1`
- job ID: `103715385229`
- trigger: `push`
- source/head SHA: `45328f1d07644eef62f8fa7ab5b22f798f65fa20`
- runner: GitHub-hosted `ubuntu-24.04`
- Python: 3.10
- NumPy: `1.26.4`
- SciPy: `1.15.3`
- GPU disabled (`CUDA_VISIBLE_DEVICES=''`)
- result: `success`.

All scientific/test steps completed successfully:
- checkout
- Python setup
- pinned CPU runtime installation/verification
- frozen V6 synthetic contract
- fail-closed boundary verification
- artifact upload.

No Modal, Vercel heavy-GPU or L4 execution occurred.

## Result artifact

Artifact name:
`songsterr-fresh-v6-synthetic-result`

Artifact ID:
`10316469276`

Artifact ZIP SHA-256:
`23e3951dc8796206167642bd980aefb4ad030902f8e4b13fc012a458187cb465`

Result JSON filename:
`v6-synthetic-result.json`

Result JSON SHA-256:
`4991aaec34f71fbb603865e2fcef47c59a551bf1f675b19d9db8318affa0e01a`

## Synthetic outcome

Fixture count: `23`

Classification counts:
- `onset-birth-corroborated-candidate`: `12`
- `not-onset-birth-corroborated`: `7`
- `insufficient-evidence`: `4`

Every fixture matched its pre-frozen expected classification and every selected MIDI was preserved.

Policy boundary in the artifact:
- `realCorpusEvaluated:false`
- `protectedSongUsed:false`
- `modelInferenceInvoked:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- `durationAuthorityChanged:false`.

## Interpretation boundary

This result establishes only that the new onset-birth representation is internally coherent on its deterministic synthetic contract in the pinned CPU runtime.

It does **not** establish real-audio precision, recall, calibration, robustness, external validity or customer eligibility.

Do not use FLGD, IDMT, GuitarSet or protected-song correctness to tune these constants.

## Next allowed step

Proceed to metadata/reference-blind holdout preparation. Guitar-TECHS is the leading current candidate, but no correctness scoring is allowed yet. First freeze a separate alignment/inventory audit capable of determining, without scoring Basic Pitch/V6 correctness:
- exact dataset/version/file identities;
- authoritative usable audio path;
- MIDI structure and note-event semantics;
- deterministic audio/MIDI alignment semantics, including how the published <=100 ms path offsets are handled;
- population/strata definitions;
- licensing/attribution requirements.

Only after that audit and a final V6 method/scoring preregistration may a real external correctness execution be considered.
