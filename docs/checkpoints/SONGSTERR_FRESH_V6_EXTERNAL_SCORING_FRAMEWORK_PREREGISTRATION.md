# Songsterr Fresh V6 — External Scoring Framework Preregistration

Status: **FROZEN BEFORE ANY V6 REAL-CORPUS CORRECTNESS; POPULATION/ALIGNMENT IDENTITY PENDING REFERENCE-BLIND AUDIT**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Purpose and ordering

This document freezes V6's upstream decoder/runtime, canonical audio path, event-preservation rule, correctness matcher, uncertainty statistic, admission gates and deferred-reveal/single-run policy **before any V6 correctness result** and before the active Guitar-TECHS alignment audit reveals its A/B/C alignment outcome.

The later final execution contract may bind only immutable holdout identities produced by the already-preregistered reference-blind audit. It may not alter the method/runtime/settings/matching/gates in this document.

If the audit returns outcome C (dataset unsuitable), this scoring framework is not executed on Guitar-TECHS and does not authorize substituting post-hoc files or paths.

## Frozen V6 method

Final method record:
`docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`

Implementation:
`scripts/songsterr-fresh/onset_birth_corroboration_v6.py`

Implementation commit:
`3a6cbb144fec5613ab6350deb6539297d713df28`

Implementation blob SHA:
`2b18ef0ee710a6ad5ecb27253b977495db7d6534`

Only class `onset-birth-corroborated-candidate` is V6-positive.

`not-onset-birth-corroborated` and `insufficient-evidence` are not positives.

Every decoded Basic Pitch event must be preserved and classified exactly once. V6 may not delete, rewrite or repitch an event.

## Frozen holdout-audio path

If Guitar-TECHS audit outcome A or B is structurally suitable, use only the audit-frozen DI (`audio/directinput`) WAV for each immutable DI/MIDI pair.

Amp-mic, ego and exo recordings are excluded from scoring by pre-correctness design and cannot become rescue paths after results.

For every scoring DI WAV:
1. verify the exact DI SHA-256 from the immutable audit population;
2. read/decode deterministically;
3. convert to mono by arithmetic mean across channels when multichannel;
4. resample to exactly 44,100 Hz with librosa `0.11.0` default high-quality resampling path as invoked by `librosa.load(..., sr=44100, mono=True)`; no amplitude normalization;
5. require finite nonempty samples;
6. write a temporary mono 44,100-Hz SoundFile `0.13.1` WAV with subtype `FLOAT`;
7. read that WAV back and use the re-read float waveform as the canonical shared waveform for V6 and the exact WAV file as the Basic Pitch input;
8. hash and record the canonical WAV bytes.

No Demucs/source separation is used: Guitar-TECHS DI is already an isolated guitar signal.

## Frozen Basic Pitch decoder

V6 evaluates admission of an existing Basic Pitch event stream. The upstream decoder is therefore retained unchanged from the previously frozen V5 protocol rather than retuned from any successor holdout.

Runtime/settings:
- `basic-pitch==0.4.0`
- CPU only
- minimum MIDI `40`
- maximum MIDI `88`
- onset threshold `0.5`
- frame threshold `0.3`
- minimum note length `127.7 ms`
- `multiple_pitch_bends=False`
- `melodia_trick=True`.

Invocation must use the existing deterministic isolated-guitar Basic Pitch adapter unless a pre-correctness controlled engineering check identifies a purely infrastructural incompatibility. Any such incompatibility must be checkpointed before correctness; model settings cannot change.

Basic Pitch event confidence, activation surface and decoded end/duration are diagnostic only and cannot enter V6 classification or correctness matching.

## Frozen V6 event input conversion

For every decoded event:
- preserve decoded event order/identity and selected integer MIDI exactly;
- convert start seconds to V6 onset sample by `floor(startSeconds * 44100 + 0.5)`;
- call the exact frozen V6 implementation once on the canonical shared waveform and selected MIDI;
- require exactly one V6 class per decoded event.

No decoded event may be silently omitted because V6 context is insufficient; it receives `insufficient-evidence` and remains in the preserved event count.

## Frozen reference timing

The immutable Guitar-TECHS audit alone decides reference timing before correctness:
- outcome A: use standard-SMF MIDI onset seconds without offset correction;
- outcome B: add that pair's exact frozen `lagSecondsAddedToMidi` to every standard-SMF MIDI onset in that pair;
- outcome C: do not score Guitar-TECHS.

No future model estimate or correctness result may change a reference lag.

Reference selected pitch is the integer MIDI note from the immutable audit's valid paired note events.

Reference offsets/durations are ignored for V6 admission correctness and grant no duration authority.

## Frozen one-to-one matching

Matching is performed independently within each immutable performance/pair.

A V6-positive estimate may match one corrected canonical reference event iff both are true:
- absolute onset difference <= `0.050` seconds, inclusive;
- absolute pitch difference <= `50` cents, inclusive.

For integer-MIDI estimates and references, adjacent semitones do not match.

Numerical boundary handling is frozen as:
`delta < limit OR math.isclose(delta, limit, rel_tol=0, abs_tol=1e-12)`.

Use deterministic maximum-cardinality bipartite matching. No estimate/reference event may be matched more than once. Offsets/durations are ignored.

## Frozen metrics

Primary metric: **V6-positive precision**
`matched V6-positive estimates / all V6-positive estimates`.

Primary uncertainty statistic: one-sided 95% Wilson lower confidence bound with
`z = 1.6448536269514722`.

Diagnostics only, unable to override a failed mandatory gate:
- all-decoded Basic Pitch baseline precision under the same matcher;
- V6-positive recall;
- per-performance precision/recall/counts;
- V6 classification counts;
- unmatched-positive onset/pitch diagnostics;
- insufficient-evidence counts;
- audio/MIDI structural metadata already frozen by the audit.

## Frozen mandatory admission gates

All mandatory gates must pass:

1. **Population completeness**: every pair in the immutable audit-approved scoring population completes; no result-based file exclusion.
2. **Event preservation**: V6 class counts sum exactly to all decoded Basic Pitch events and event/MIDI identity is preserved.
3. **Minimum evidence volume**: at least `1,000` V6-positive events pooled.
4. **Primary admission bar**: pooled one-sided 95% Wilson lower bound >= `0.9900`.
5. **Player robustness**: each player stratum with >=100 V6-positive events must have point precision >= `0.9500`.
6. **Category robustness**: each category stratum (`chords`, `scales`, `singlenotes`, `techniques`, `music`) with >=100 V6-positive events must have point precision >= `0.9500`.
7. **Identity/runtime guards**: exact audit-approved package/population/alignment identities, V6 implementation identity, Basic Pitch settings, pinned package versions and canonical audio identities must all remain valid.
8. **Policy boundary**: no protected song, no Demucs, no duration authority change, no customer/model promotion from the execution itself.

The pooled `0.9900` bar is the existing product-policy standard and is not lowered because V3/V4/V5 failed.

No secondary metric or favorable stratum can override a failed mandatory gate.

## Frozen runtime

Official correctness runtime must pin:
- Python 3.10.x
- Basic Pitch `0.4.0`
- NumPy `1.26.4`
- SciPy `1.15.3`
- librosa `0.11.0`
- SoundFile `0.13.1`
- CPU-only Basic Pitch/V6 execution unless a later explicit user-approved GPU execution is separately justified before correctness.

The standing user compute rule requires explicit authorization before Modal, Vercel heavy-GPU or L4 runs. This preregistration does not grant such authorization.

## Deferred correctness reveal

The official execution must be two-phase:

### Phase 1 — reference-blind event generation/classification

For **every** immutable scoring performance:
- verify source identities;
- construct canonical audio;
- run Basic Pitch exactly once;
- preserve every decoded event;
- run V6 exactly once per event;
- persist the reference-blind event/classification records needed for later scoring.

Phase 1 must complete for the entire population before any correctness matching starts.
No partial correctness counts/metrics may be emitted or interpreted during Phase 1.

### Phase 2 — scoring

Only after all Phase-1 files complete:
- load immutable reference MIDI identities/times and audit-frozen A/B alignment;
- perform deterministic matching;
- compute aggregate/stratum metrics and frozen gates once;
- emit one final result artifact.

## Single-run rule

After the final scoring harness passes controlled synthetic/contract-only CI with no real holdout correctness, authorize one official full external correctness execution on one exact clean source.

After any correctness result is exposed:
- do not tune V6;
- do not change Basic Pitch settings;
- do not alter audio preparation, reference alignment, matching/tolerances, uncertainty or gates;
- do not exclude files/categories/players;
- do not rerun the same holdout to seek a better result.

If an execution fails before any correctness exposure, checkpoint the infrastructure failure and make an explicit technical retry decision without changing the experiment. Never retry automatically after correctness exposure.

## Policy boundary

Even a passing run must initially retain:
- `admissionDecisionMade:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- `durationAuthorityChanged:false`
- `protectedSongUsed:false`
- `demucsInvoked:false`
- `separatePolicyReviewRequired:true`.

Write an immutable official-result record **before** pass/fail interpretation, then conduct a separate policy review.

## What remains unfrozen pending the audit

Only immutable identities that cannot exist until the reference-blind audit completes:
- audit artifact/result SHA;
- A/B alignment decision (or C rejection);
- per-pair lag manifest identity if B;
- exact scoring-population manifest identity;
- exact pair count/reference-event count/source hashes.

A later binding checkpoint may fill these identities only. It may not modify any method/runtime/matching/gate above.
