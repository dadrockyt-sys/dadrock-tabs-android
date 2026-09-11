# Songsterr Fresh — External GuitarSet Validation V3

Status: **FROZEN IMPLEMENTATION / CONTROLLED CONTRACT CI GREEN / REAL CORPUS NOT YET EVALUATED**

Recorded: 2026-09-11 America/Toronto

Preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V3.md`
- commit `2dfd8c5d52093c36c0924e5f0b57eb2b2284e7d0`

Implementation:
- `scripts/songsterr-fresh/external_guitarset_validation_v3.py`
- implementation commit `a8a7b5f05950de6dfa061f7ee4995bafd778f17b`
- contract `songsterr-fresh-guitarset-external-validation-v3`

Focused controlled CI:
- `.github/workflows/songsterr-fresh-guitarset-v3-ci.yml`
- initial workflow commit `27b1916ef5c9fa287b0186bdf03fa9e05fcd225a`
- boundary-guard self-match fix `96ae75bcfb7ddc4d469b4f96d4126f276f4c9d15`

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

## Controlled implementation verification

### Run 1 — integration guard failure only

Run `34642016377`, job `103403803350`, source `27b1916ef5c9fa287b0186bdf03fa9e05fcd225a`.

Passed:
- checkout/setup/dependency install;
- V2/V3 Python compile;
- V3 synthetic/contract self-test;
- frozen V2 import and constant checks;
- preregistered dataset/checksum/exclusion/tolerance/gate assertions.

The final controlled-only boundary check failed only because the workflow searched its own source for the literal forbidden download token while that same literal appeared inside the guard's forbidden-string list. The failure was self-referential guard text, not a scorer, matcher, policy, dataset, or model failure.

No GuitarSet audio/annotation archive was downloaded. No GuitarSet inference/classification result and no protected-song result was produced.

### Run 2 — GREEN

Run `34642084982`, job `103404026067`, source `96ae75bcfb7ddc4d469b4f96d4126f276f4c9d15`: **SUCCESS**.

The only change from Run 1 was constructing forbidden guard strings from concatenated fragments so the guard no longer self-matched its own source. No V3 method, threshold, exclusion, model setting, matching rule, or pass gate changed.

Run 2 proved:
- Python 3.10 environment established;
- NumPy `1.26.4` and SoundFile `0.13.1` installed;
- frozen V2 and V3 harness compile;
- synthetic matching, ambiguity, polyphony, exact tolerance boundary, Wilson math, aggregate gate, event-preservation and V2-import contract tests pass;
- exact preregistered V3 constants and three exclusions match;
- controlled-only CI boundary passes;
- emitted markers:
  - `V3_CONTROLLED_ONLY_BOUNDARY_VALID`
  - `GUITARSET_NOT_EVALUATED_BY_V3_CI`
  - `PROTECTED_SONG_NOT_EVALUATED_BY_V3_CI`.

Self-test policy output remained:
- `guitarsetEvaluated:false`
- `protectedSongEvaluated:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`.

## Execution boundary after green controlled CI

The V3 implementation and pass policy are now frozen for the first real GuitarSet execution. From this point until that execution completes:
- do not change scorer logic;
- do not change Basic Pitch settings;
- do not change matching tolerances/algorithm;
- do not change archive identities/exclusions;
- do not change Wilson/gate thresholds;
- do not inspect a partial GuitarSet correctness result and then patch the method.

The first real evaluation must process the entire locked 357-track corpus in one preregistered execution contract and write an immutable result artifact. If dataset integrity or execution-contract failure prevents completion, fail closed; do not post-hoc exclude a track or relax policy.

The protected authorized song remains embargoed throughout V3 external validation.

## Promotion boundary

A real GuitarSet pass still does not automatically authorize customer admission. A separate explicit policy review is required.

Until then:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research paused.
