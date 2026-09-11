# Songsterr Fresh — External GuitarSet Validation V3

Status: **FROZEN IMPLEMENTATION + EXECUTION PROVENANCE / CONTROLLED CONTRACT CI GREEN / REAL CORPUS NOT YET EVALUATED**

Recorded: 2026-09-11 America/Toronto

Preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V3.md`
- commit `2dfd8c5d52093c36c0924e5f0b57eb2b2284e7d0`

Core validation implementation:
- `scripts/songsterr-fresh/external_guitarset_validation_v3.py`
- implementation commit `a8a7b5f05950de6dfa061f7ee4995bafd778f17b`
- contract `songsterr-fresh-guitarset-external-validation-v3`

Execution-provenance wrapper:
- `scripts/songsterr-fresh/run_external_guitarset_validation_v3.py`
- wrapper commit `49e98254417c416f59575097ee6cdbf62636374a`
- contract `songsterr-fresh-guitarset-external-validation-execution-v3`

Focused controlled CI:
- `.github/workflows/songsterr-fresh-guitarset-v3-ci.yml`
- initial workflow commit `27b1916ef5c9fa287b0186bdf03fa9e05fcd225a`
- boundary-guard self-match fix `96ae75bcfb7ddc4d469b4f96d4126f276f4c9d15`
- execution-provenance verification update `e3e6f1fa1292d9ad82d55d64d1da9463829f064f`.

## Frozen purpose

V3 does not create a new pitch classifier and does not alter V2. It validates the already frozen V2-positive subset against an independently annotated guitar corpus under a protocol frozen before model results.

The frozen V2 evaluator remains:
- `scripts/songsterr-fresh/independent_pitch_corroboration_v2.py`
- contract `songsterr-fresh-independent-pitch-corroboration-research-v2`
- 44.1 kHz, fixed 16384-sample window
- MIDI 40..88
- competitors `[-12,-7,-2,-1,+1,+2,+7,+12]`
- RMS `<1e-4` insufficient
- strict `>` unique-best
- both spectral and YIN/CMND channels must choose the existing selected MIDI.

The V3 harness imports that file directly and asserts the frozen contract/constants before execution. It does not copy or reimplement the scorer.

## Locked corpus contract

Dataset: GuitarSet v1.1.0, DOI `10.5281/zenodo.3371780`.

Authorized archives only:
- `annotation.zip` MD5 `b39b78e63d3446f2e54ddb7a54df9b10`
- `audio_mono-mic.zip` MD5 `275966d6610ac34999b58426beb119c3`.

Source corpus must expose exactly 360 paired JAMS/microphone-WAV track identities. Exactly three tracks are preregistered exclusions because of public annotation defects:
- `02_Funk2-119-G_comp`
- `04_BN3-154-E_comp`
- `04_Jazz1-200-B_comp`.

The locked evaluation corpus is therefore exactly 357 tracks. The harness fails closed on any archive checksum, track-set, count, exclusion, or pairing drift. No later post-hoc track exclusion is permitted under V3.

No GuitarSet track is development data. Synthetic/unit fixtures are the only development surface.

## Frozen model execution

The GuitarSet microphone recording is already isolated guitar, so V3 does not invoke Demucs.

Each locked microphone WAV must already be mono 44100 Hz. No silent resampling is allowed.

Each track invokes the existing Basic Pitch wrapper exactly once with frozen settings:
- Basic Pitch `0.4.0`
- MIDI 40..88
- onset threshold `0.5`
- frame threshold `0.3`
- minimum note length `127.7 ms`
- multiple pitch bends disabled
- melodia trick enabled.

Only deterministic note identity, onset seconds, and integer MIDI are admitted to V3 scoring. Basic Pitch confidence and decoded note end are excluded from classification and matching policy.

Every decoded event is retained. The frozen V2 rule classifies each event on the exact microphone-audio window. V3-positive means exactly `independently-corroborated-candidate`.

## Frozen reference and matching

Reference notes are the union of all six GuitarSet per-string `note_midi` annotations in each locked JAMS file. Exactly one note-MIDI annotation per string ID `0..5` is required.

Correctness uses deterministic one-to-one maximum-cardinality bipartite matching:
- onset difference `<=0.050 s`
- pitch difference `<=50 cents`
- offsets ignored
- each estimate and reference used at most once
- confidence/scorer margin cannot influence correctness.

Polyphonic notes are matched independently through the same one-to-one graph.

## Frozen metrics and gates

Primary metric:
- V3-positive precision = matched V3-positive events / all V3-positive events.

Uncertainty:
- one-sided 95% Wilson score lower bound
- fixed `z=1.6448536269514722`.

All pass gates are frozen before corpus execution:
1. exact dataset/version/archive identities and exact exclusions;
2. all 357 locked tracks complete;
3. at least 1000 V3-positive events;
4. pooled V3-positive precision one-sided 95% Wilson lower bound >= `0.9900`;
5. every player `00..05`: at least 50 positives and point precision >= `0.9500`;
6. both `comp` and `solo`: at least 50 positives and point precision >= `0.9500`;
7. event identity preserved and all non-promotion guards remain false/zero.

Secondary diagnostics such as baseline decoded precision, recall, style/tempo observations, per-track counts, or error distances cannot alter these gates.

## Frozen execution provenance

Before the first real corpus run, the execution wrapper was added to satisfy the preregistered immutable-result provenance requirements without changing the scorer or any acceptance rule.

Official execution now fails closed unless:
- current branch is exactly `songsterr-fresh-pipeline-v1`;
- Git worktree is completely clean;
- an exact 40-hex source commit is available;
- Python major/minor is exactly `3.10`;
- `basic-pitch==0.4.0`;
- `numpy==1.26.4`;
- `soundfile==0.13.1`;
- work/output locations are outside the repository;
- the core result retains every non-promotion guard.

The wrapper records:
- exact source branch + commit + clean-worktree state;
- full Python/platform information;
- required package versions plus available SciPy/TensorFlow/librosa versions;
- SHA-256 identities for the wrapper, V3 core harness, frozen V2 scorer, Basic Pitch wrapper, V3 preregistration and this method record;
- the complete core V3 result and its SHA-256;
- the unchanged false/zero promotion boundary.

It rechecks source and runtime after the complete evaluation and fails if either changed during execution.

This provenance addition is an execution-integrity completion required by the preregistration. It does not alter audio scoring, event classification, reference matching, exclusions, thresholds, metrics, or pass gates.

## Controlled implementation verification

### Run 1 — integration guard failure only

Run `34642016377`, job `103403803350`, source `27b1916ef5c9fa287b0186bdf03fa9e05fcd225a`.

Compile, synthetic/contract self-test, frozen V2 import and all preregistered constants passed. The final controlled-only boundary check failed only because it searched its own source for a forbidden download literal which appeared in its own forbidden-string list. This was self-referential guard text only.

No GuitarSet archive was downloaded; no GuitarSet or protected-song inference/classification result was produced.

### Run 2 — GREEN

Run `34642084982`, job `103404026067`, source `96ae75bcfb7ddc4d469b4f96d4126f276f4c9d15`: **SUCCESS**.

Only the self-referential guard representation changed. No V3 method or policy constant changed.

Run 2 proved:
- V2/V3 compile;
- synthetic matching, ambiguity, polyphony, exact tolerance boundary, Wilson math, aggregate gates, event preservation and frozen-V2 import tests pass;
- exact preregistered constants/exclusions pass;
- controlled-only boundary passes;
- `GUITARSET_NOT_EVALUATED_BY_V3_CI`;
- `PROTECTED_SONG_NOT_EVALUATED_BY_V3_CI`.

### Run 3 — GREEN method-record freeze

Run `34642234908`, job `103404515324`, source `3d44108807a291d43f790679e11d6825a47bca9b`: **SUCCESS**.

This documentation-triggered run re-proved all controlled checks after the initial method record was committed. No corpus result was generated.

### Run 4 — GREEN provenance surface

Run `34642484069`, job `103405310705`, source `e3e6f1fa1292d9ad82d55d64d1da9463829f064f`: **SUCCESS**.

In addition to the existing controlled suite, Run 4 proved:
- execution wrapper compiles;
- execution-provenance self-test passes without running an official evaluation;
- exact source binding is required;
- the declared runtime pins are Python 3.10 / Basic Pitch 0.4.0 / NumPy 1.26.4 / SoundFile 0.13.1;
- provenance constants bind to the same core V3 contract;
- all controlled-only and protected-song embargo guards remain green.

Self-test policy output remains false/zero: no GuitarSet evaluation, no protected-song evaluation, no model validation, no customer eligibility.

## Execution boundary after green controlled CI

The V3 method, pass policy, and execution provenance are frozen for the first real GuitarSet execution. From this point until that execution completes:
- do not change scorer logic;
- do not change Basic Pitch settings;
- do not change matching tolerances/algorithm;
- do not change archive identities/exclusions;
- do not change Wilson/gate thresholds;
- do not change runtime pins or provenance binding;
- do not inspect a partial GuitarSet correctness result and then patch the method.

The first real evaluation must process the entire locked 357-track corpus in one official execution contract and write the final immutable provenance-bound result artifact. If dataset integrity or execution-contract failure prevents completion, fail closed; do not post-hoc exclude a track or relax policy.

The protected authorized song remains embargoed throughout V3 external validation.

## Promotion boundary

A real GuitarSet pass still does not automatically authorize customer admission. A separate explicit policy review is required.

Until then:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research paused.
