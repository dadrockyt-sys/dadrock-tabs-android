# Songsterr Fresh — FLGD V5 Scoring Harness

Status: **FROZEN CONTROLLED-GREEN / BEFORE ANY FLGD CORRECTNESS RESULT**

Date: 2026-09-12 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Frozen prerequisites

- final scoring preregistration: `SONGSTERR_FRESH_FLGD_V5_FINAL_SCORING_PREREGISTRATION.md`, commit `846cdedad46c10553569011a28ae01c72a9f6504`;
- inclusive numerical amendment: `SONGSTERR_FRESH_FLGD_V5_SCORING_NUMERICAL_AMENDMENT.md`, commit `2d547c6d034defebf8369db7f48fafcf15a02cec`;
- immutable Stage B report SHA-256 `065335aac5a6cd46ef713bae9f19d6f7ca7d764233419f6d8eb9ec6bace9911e`;
- frozen population SHA-256 `def77a45baf1b453e3f8ec0feed82e1cd3964bd85d50fb30f4912c0564425b02`;
- frozen reference identity SHA-256 `e34b360515d35dc77a6f423eb8a36e860e46f9469c16a499243186aea1f6223a`;
- frozen ignored-release identity SHA-256 `8751a5425e3348b4e7005b09121bd43425c23a9f296b8f2e58c8da1c245fcfd3`.

## Harness

Official harness:
`scripts/songsterr-fresh/external_flgd_v5_validation.py`

Initial implementation commit:
`b7561defee0ec39d3be8ba877592b13d39d8e8d2`.

Controlled contract test:
`scripts/songsterr-fresh/test_external_flgd_v5_validation.py`.

The harness:
- requires the exact clean Songsterr branch and exact FLGD Git revision;
- binds exact frozen transcriber/V5/Stage-B-adapter Git blob identities;
- requires the exact immutable Stage B JSON SHA-256 and frozen population/reference identities;
- reconstructs each canonical MIDI reference population using the same amended Stage B parser and verifies each per-file identity before scoring;
- verifies every source MP3 SHA from Stage B;
- decodes each MP3 with librosa 0.11.0 to mono 44.1 kHz, writes SoundFile 0.13.1 `FLOAT` WAV, reads it back, and feeds that same canonical waveform to Basic Pitch/V5;
- invokes Basic Pitch exactly once per performance with the frozen 0.4.0 settings and CPU-only provenance;
- preserves every decoded `(noteId,startSeconds,midi)` through exactly one V5 classification;
- matches only V5-positive events to references using frozen onset/pitch-only maximum-cardinality matching;
- ignores all duration/end/confidence fields for V5 correctness;
- implements the frozen `1e-12` binary64 representation tolerance only at the inclusive 50-ms / 50-cent boundaries;
- computes the preregistered Wilson and pooled/split/guitar-type gates;
- always leaves admission/customer/duration/protected-song authority unchanged pending separate policy review.

## Controlled validation

Workflow:
`.github/workflows/songsterr-fresh-flgd-v5-scoring-contract-ci.yml`.

Final controlled source commit:
`2ae9b6b797449b5b11de370b2e5836c4707fd5c9`.

Run `34720390259`, job `103625060255`: **SUCCESS**.

Green checks include:
- Python compilation;
- self-test policy boundary false/zero;
- exact Stage B/dataset/runtime/scoring constants;
- exact inclusive onset/pitch numerical semantics;
- adjacent-semitone rejection;
- deterministic maximum-cardinality matching;
- duration/end irrelevance to matching;
- fake-classifier event preservation and three-class bookkeeping;
- one-sided Wilson calculation and pooled/stratum gate behavior;
- runtime-version drift fail-closed behavior;
- Basic Pitch payload/provenance validation without installing Basic Pitch;
- malformed/fake Stage B identity rejection;
- synthetic MP3 → librosa 44.1-kHz mono → SoundFile FLOAT WAV → reread canonicalization;
- no real FLGD checkout and no Basic Pitch model invocation in CI.

An earlier synthetic-audio run failed only because the current GitHub runner image lacked `ffmpeg`; the final workflow explicitly installs `ffmpeg`. This was CI-fixture infrastructure only and did not change the frozen scoring method.

## Consequence

The preregistered prerequisites for one official full 79-performance FLGD V5 correctness run are now satisfied.

The next permitted action is exactly one official run on one exact clean source commit. Once any correctness result is observed, V5/settings/matcher/tolerances/gates/files/strata may not be tuned or rerun under this preregistration to seek a better result. The result must be recorded immutably and reviewed separately before any authority change.

Current authority remains:
- `modelValidationComplete:false`;
- customer-eligible events `0`;
- `mayAdvanceDelivery:false`;
- duration paused/unchanged;
- protected song unused.
