# Songsterr Fresh — FLGD V5 Final External-Validation Scoring Preregistration

Status: **FROZEN BEFORE ANY FLGD BASIC PITCH / V5 CORRECTNESS RESULT**

Date: 2026-09-12 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Purpose

This document freezes the one official FLGD V5 correctness protocol before Basic Pitch or V5 is run on FLGD audio.

Passing this external validation is necessary but not sufficient for admission; a separate post-result policy review remains mandatory.

## Frozen dataset / population identity

Dataset:
- François Leduc Guitar Dataset
- Hugging Face `xavriley/FrancoisLeducGuitarDataset`
- canonical origin `https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset`
- exact revision `a38306c244b3ea81496ad58b4514622185e58211`.

Stage A report SHA-256:
`f03d6e3b9549a13dbcc9557ec6f13516fb52ac9d4fbf64138a0bb008b7a891b3`.

Stage B frozen result:
- Stage B JSON SHA-256 `065335aac5a6cd46ef713bae9f19d6f7ca7d764233419f6d8eb9ec6bace9911e`
- included-population SHA-256 `def77a45baf1b453e3f8ec0feed82e1cd3964bd85d50fb30f4912c0564425b02`
- reference-event identity SHA-256 `e34b360515d35dc77a6f423eb8a36e860e46f9469c16a499243186aea1f6223a`
- ignored-duplicate-release identity SHA-256 `8751a5425e3348b4e7005b09121bd43425c23a9f296b8f2e58c8da1c245fcfd3`
- exactly 79 performances
- exactly 76,392 canonical reference note events
- exactly 24 audited duplicate-release edges ignored structurally; no row/file excluded.

Stage B immutable record:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_RESULT.md`.

Alignment semantics:
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_ALIGNMENT_SEMANTICS_RESULT.md`.
Canonical MIDI note times under standard SMF tempo semantics are the authoritative audio-aligned reference times. Syncpoints are not used to warp note times for correctness scoring.

No `test_set/` duplicate/model-output MIDI is reference truth.

## Frozen audio/model path

FLGD recordings are already solo-guitar audio. Demucs/source separation is not used.

For each metadata-named MP3:
1. verify its exact Stage B SHA-256;
2. decode mono at exactly 44,100 Hz using librosa `0.11.0` in the pinned Python runtime;
3. require finite nonempty samples;
4. write a temporary 44,100-Hz mono float WAV via SoundFile `0.13.1`, subtype `FLOAT`;
5. read that WAV back and use the re-read waveform for V5, so Basic Pitch and V5 are bound to the same canonical decoded WAV;
6. hash and record the canonical WAV bytes.

Basic Pitch invocation is exactly one call per performance using existing script:
`scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py`.

Frozen Basic Pitch settings:
- `basic-pitch==0.4.0`
- minimum MIDI `40`
- maximum MIDI `88`
- onset threshold `0.5`
- frame threshold `0.3`
- minimum note length `127.7 ms`
- `multiple_pitch_bends=False`
- `melodia_trick=True`
- CPU only; GPU flag false
- `audio-source` binds the canonical source MP3 identity
- `separation-source = flgd-direct-solo-guitar-no-demucs`.

Decoded Basic Pitch end/confidence are diagnostic only and are not inputs to V5 or correctness matching.

## Frozen V5 path

V5 implementation:
`scripts/songsterr-fresh/independent_pitch_corroboration_v5.py`
contract `songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5`.

Pinned runtime packages:
- Python 3.10.x
- NumPy `1.26.4`
- SciPy `1.15.3`
- librosa `0.11.0`
- SoundFile `0.13.1`
- Basic Pitch `0.4.0`.

For every decoded Basic Pitch event, preserve identity and compute:
`onsetSample = floor(startSeconds * 44100 + 0.5)`.
Call V5 exactly once for that event using canonical decoded mono audio, onsetSample and selected integer MIDI.

Every decoded event must receive exactly one of V5's frozen classes. No event deletion/rewrite is allowed.

Primary V5-positive class:
`independently-corroborated-candidate`.

`not-independently-corroborated` and `insufficient-evidence` are not positives.

No confidence, Basic Pitch activation/decision surface, diagnostic model end, split, guitar type, artist, bit depth, reference truth or future correctness information may affect V5 classification.

## Frozen reference matching

Matching is performed separately within each performance.

A V5-positive estimate may match a canonical reference event iff:
- absolute onset difference <= `0.050` seconds, inclusive;
- absolute pitch difference <= `50` cents, inclusive.

For current integer-MIDI estimates/references, the pitch rule is exact-semitone identity; adjacent semitones do not match.

Offsets/durations are ignored for correctness. This validation tests note-onset/pitch admission only and grants no duration authority.

One-to-one matching uses deterministic maximum-cardinality bipartite matching. No reference event or estimate may be used twice.

The primary metric is **V5-positive precision**:
`matched V5-positive estimates / all V5-positive estimates`.

Diagnostics only:
- baseline Basic Pitch precision using all decoded events under the same matcher;
- V5-positive recall against all canonical references;
- decoded/classification counts;
- per-file metrics and unmatched-positive pitch/onset-distance diagnostics.

No diagnostic can override a failed admission gate.

## Frozen uncertainty

Primary uncertainty statistic: one-sided 95% Wilson lower confidence bound on V5-positive precision with
`z = 1.6448536269514722`.

No bootstrap/model selection or alternate confidence interval may replace it after results.

## Frozen mandatory gates

All gates must pass:

1. **Population completeness**: all 79 frozen performances complete; no post-result exclusions.
2. **Event preservation**: V5 class counts sum exactly to all decoded Basic Pitch events.
3. **Minimum evidence volume**: at least `1,000` V5-positive events pooled.
4. **Primary admission bar**: pooled one-sided 95% Wilson lower bound >= `0.9900`.
5. **Split robustness**: each metadata `split` stratum with at least `100` V5-positive events must have point precision >= `0.9500`. Strata with fewer than 100 positives remain diagnostic and do not fail solely for size.
6. **Guitar-type robustness**: each `guitar_type` stratum with at least `100` V5-positive events must have point precision >= `0.9500`. Smaller strata remain diagnostic.
7. **Identity/runtime guards**: exact dataset revision, Stage B hashes, implementation hashes, package versions, decoded-WAV identities and clean source must remain valid.
8. **Policy boundary**: no protected song, no Demucs, no duration authority change, no admission/customer promotion from the run itself.

The 0.9900 pooled bar is the same product-policy standard used before V5 results and is not lowered because earlier V3/V4 methods failed.

## Single-run rule

After the scoring harness is implemented, it must pass synthetic/contract-only CI with no real FLGD audio/model scoring.

Then one official full 79-performance FLGD run is authorized on one exact clean source commit.

After any correctness result is observed:
- do not tune V5;
- do not change Basic Pitch settings;
- do not alter matching/tolerances/gates;
- do not exclude files/strata;
- do not rerun FLGD under this preregistration to seek a better result.

Write an immutable result record and a separate policy review.

## Policy boundary

Even a passing run must initially emit:
- `admissionDecisionMade:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- `durationAuthorityChanged:false`
- `protectedSongUsed:false`
- `demucsInvoked:false`
- `separatePolicyReviewRequired:true`.
