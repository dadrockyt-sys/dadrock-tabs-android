# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 20:46 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or live Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. Runtime/shadows may never read/train/tune/select from it.
- Retired scored render identities must never be rerun/rescored:
  - `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
  - `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- Any future professional score requires a genuinely new corrected candidate → immutable freeze/PDF → fidelity 1.0 → lock → exactly one score.
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 unless the user explicitly authorizes paid usage.**

## Immutable historical score state
- Score 1 retired: 725 attacks → 985 notes, 113 measures, PDF fidelity 1.0. Run `32731885778`; pitch F1 `0.23718280683583634`; pitch+timing F1 `0.033143448990160536`; critical mismatches `1723`.
- Score 2 retired after harmonic contradiction guard: 889 events, PDF fidelity 1.0. Run `32752374788`; pitch F1 `0.24305177111716622`; pitch+timing F1 `0.03051771117166212`; string/fret+timing F1 `0.01852861035422343`; chord F1 `0.012048192771084336`; critical mismatches `1635`.
- Harmonic contradiction was real but not dominant.

## Dominant pitch diagnosis
- Same 725 retained attacks entered legacy precision with **7,535 observed pitch hypotheses**.
- Legacy precision retained only `987`; **6,548 observed pitches were suppressed**.
- Genuine optional-secondary universe = 6,666; only 118 survived = `1.7702%`; suppression = `98.2298%`.
- Legacy non-harmonic secondary gate = score AND attack AND body at `0.80`.
- Exact upper-harmonic intervals `{12,19,24,28,31,36}` remain strict 3-of-3 at `0.92`.
- Historical suppressed carrier rows were not persisted, so exact replay requires one new carrier capture.

# Precision v2
Module: `analyzer/v143_contextual_prune_precision_shadow_v2.py`
Policy: `envelope-balanced-secondary-v2`

- Attack selection, fail-safe, primary/fundamental promotion, no-invention invariants and harmonic protections remain unchanged.
- Non-harmonic observed secondaries use **2-of-3 physical consensus** across score/attack/body at the existing `0.80` floor.
- Harmonics remain strict legacy 3-of-3 at `0.92`.
- No new numeric threshold, pitch, key/chord/song rule, runtime label, or professional information.

# One-shot capture path — prepared, NOT RUN
Producer: `analyzer/v143_repaired_timing_precision_candidate_product_modal.py`
Paid workflow: `.github/workflows/v143-repaired-timing-precision-candidate-product.yml`
CPU guard workflow: `.github/workflows/v143-precision-shadow-v2-cpu-guard.yml`
Lock: `debug/v143-contextual-prune/precision-v2-capture-lock.json`

## Paid-budget protections
- Paid workflow is manual only; `paid_capture_authorized=YES` required, default NO.
- Branch/ref/HEAD/remote target SHA must agree before reservation.
- Approved audio SHA and protected pipeline blob are hard-gated.
- Exactly one workflow `python -m modal run ...::approved_audio` and one producer `.remote(` call are permitted.
- Reservation lock is committed/pushed **before Modal** with `captureState=reserved_before_modal`, `singlePaidCaptureConsumed=false`, `automaticRetryAllowed=false`.
- A reserved/completed lock blocks automatic repeat.
- Failure artifacts are salvaged with `if: always()`.
- A failed/interrupted reserved attempt is intentionally not automatically retryable.

# Replay schema 2 — source-complete for the fixed best-row precision stage
`analyzer/v143_contextual_prune_precision_shadow_v2.py` now persists:
- retained `attacks` and full `eligibleAttacks` for every corrected-input attack that has a selected physical carrier row,
- input/eligible/retained attack keys and counts,
- carrier-missing input keys,
- retained and eligible pitch-hypothesis counts,
- grid time, onset time and grid error,
- row-level `precisionStrength`, `candidateStrength`, stem/sweep/detection supports,
- every observed candidate MIDI,
- aggregate attack/early/sustain/body/continuity/score evidence,
- per-view A/B attack/early/sustain evidence,
- retained/fail-safe/selected/primary flags.

Readiness flags:
- `fixedRetainedAttackPitchReplayReady=true`
- `attackPolicyReplayReady=true`
- `sourceViewEvidenceReady=true`
- `precisionStrengthRecomputeReady=true`
- `zeroValuePreservationReady=true`

Relevant commits:
- eligible attack universe: `b8e511e873ab6857e939b34381542300e219f7b9`
- per-view evidence: `fb953ef80bd2e7fb5ea652bd4fd67d804794f67b`
- zero-value preservation: `9714f48496334b6560aa4625987b00303b7d93da`

Important scope: this replay makes future experiments CPU-only **after the current `_best_rows_by_slot` carrier-row selection**. It does not yet claim replayability for changing the upstream carrier-row selection itself.

# Exact replay artifact validator
File: `analyzer/v143_precision_replay_artifact_validator.py`
Latest commit: `7e93ce15ad8255425d6628807f2a9a1df075c34f`

Validator now independently checks/recomputes:
- schema/policy/reference-free flags,
- input = eligible ∪ carrier-missing universe,
- canonical unique attack identities,
- retained source records equal their eligible records,
- candidate MIDI identity/order/uniqueness,
- per-view and aggregate evidence,
- aggregate attack/early/sustain = exact minima of A/B,
- body/continuity derivation and score formula,
- grid error from onset/grid time,
- precision strength from strongest score + support terms − grid error,
- replay↔precision counts,
- render attack/pitch subset binding,
- voicing-drop accounting,
- exact measure coverage,
- exact baseline attack-pruning/fail-safe identity.

Zero semantics:
- Replay serialization now preserves legitimate raw `0.0` values instead of rewriting via `x or fallback`.
- Validator reproduces the legacy decision-time behavior `float(row.get('_precisionStrength') or -99.0)` via `_legacy_strength`, so raw zero is preserved in evidence but maps to `-99.0` only where the legacy policy actually did so.
- Synthetic local-prominence and fail-safe edge tests cover this behavior.

# Negative corruption rejection
File: `analyzer/check_v143_precision_replay_corruption_rejection.py`
Commit: `392f5bc2dc35ded195f6adf92fb4f0c9304e6b7f`

- Forces a two-view minimum mismatch by decreasing one view by 0.20.
- Separately corrupts `precisionStrength`.
- Separately corrupts grid/onset consistency.
- Validator must reject all three.
- `check_v143_precision_capture_readiness.py` directly runs this guard before any paid reservation.

# Primary/fundamental replay recomputation
File: `analyzer/v143_precision_replay_policy_compare.py`
Latest commit: `e7f143ce4b3bad0c14549facde2dd68affc8cd22`

- Stored primary is no longer merely trusted.
- `_recomputed_primary_midi` independently reconstructs the legacy/v2 common primary from persisted candidate evidence using the actual positive floors, harmonic-family weights, strongest-raw tie-break and `FUNDAMENTAL_MIN_RAW_RATIO=0.55`.
- `_verified_primary_midi` rejects stored/recomputed disagreement.
- Self-tests import actual legacy constants to detect drift.
- Report binds `primaryRecomputeMatches=true` and `primaryRecomputeMismatchAttackCount=0`.
- Comparator remains explicitly scoped to pitch-policy comparison on the fixed retained-attack universe.

# Capture readiness guard
File: `analyzer/check_v143_precision_capture_readiness.py`
Latest commit: `fa994701649bee621623681f09ead352c641124c`

It now requires/runs:
- negative corruption rejection,
- per-view/source-strength/zero-value replay flags,
- exact attack-policy replay,
- primary recomputation,
- branch/head binding,
- pre-Modal reservation,
- one paid command / one `.remote(`,
- no automatic retry,
- failure artifact salvage,
- no Modal in CPU replay/validator paths.

# CPU-only executable preflight — NEW
Historical green guard run `32777140959` identified workflow:
`.github/workflows/v143-precision-shadow-v2-cpu-guard.yml`

That workflow is push-triggered on precision files and contains **no Modal call**. It was upgraded in commit:
`74d54037d7d22db27e0be8b155d0f4e5e45dbfdd`

The upgraded CPU guard now compiles/runs:
- precision v2 policy self-test,
- replay policy comparator self-test,
- replay artifact validator self-test,
- negative corruption rejection,
- full capture-readiness checker,
- historical optional-candidate accounting,
- protected pipeline blob guard,
- anti-reference token checks,
- one-shot paid-workflow static checks.

If green it writes schema-3 `debug/v143-contextual-prune/precision-v2-cpu-guard-result.json` with explicit flags for source-view binding, strength recomputation, zero preservation, primary recomputation, full attack replay, no inference, no Modal, no professional reference and no Production mutation.

Updating this CPU workflow itself is a push-path trigger, so commit `74d540...` should launch a real CPU-only guard run automatically. At this checkpoint the bot result had not yet appeared on branch head; branch head was still `74d54037d7d22db27e0be8b155d0f4e5e45dbfdd`.

# Timing remains frozen
- Relative sixteenth spacing remains exceptionally well supported; at residual <=0.20 step, 697/697 consecutive pairs exactly match labeled grid gaps.
- Tempo remains exactly `129.19921875`.
- Beat repair removes interval outliers without a leading phase-index error.
- Absolute 4/4 phase remains weak/section-dependent; no global phase correction is justified.
- Do not mutate timing/grid from current source-only evidence.

# Current mutation / cost state
- No new candidate generated.
- **No Modal/L4 invoked.**
- No professional scorer/reference invoked.
- No render events mutated.
- `main` and Production untouched.
- Protected runtime was previously reverified at blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`; reverify before any capture/mutation.

## Checkpoint save — 2026-08-24 20:46 America/Montreal
- Replay evidence now preserves per-view source evidence, exact raw zeros, strength inputs, and enough information to independently reconstruct the baseline attack policy and the common primary/fundamental choice on CPU.
- The weak negative test was replaced by a guaranteed corruption test.
- A real push-triggered CPU-only guard workflow has now been upgraded to execute all new schema-2 preflight tests without authorizing or invoking Modal.
- Paid budget remains untouched.
- No completion claim is made.

# Next exact actions
1. Confirm the new CPU guard run triggered by commit `74d540...` and inspect any failure logs; fix CPU-only until green.
2. Reverify branch head and protected runtime blob after the guard/bot commit settles.
3. If green, bind the candidate workflow final lock explicitly to source-view, strength, zero-value and primary-recompute validation outputs for audit clarity.
4. Keep timing frozen and professional reference closed.
5. **Do not dispatch Modal/L4 unless the user explicitly authorizes paid usage.**
6. If explicit authorization is later given: dispatch exactly once with `paid_capture_authorized=YES`; reservation must land before Modal.
7. Require candidate product + schema-2 replay + exact artifact validation + replay-policy comparison to reconcile before any later mutation.
8. Use persisted replay evidence for subsequent precision experiments CPU-only; avoid repeated separator/Basic Pitch inference.
9. Only when source-only evidence supports a genuinely corrected candidate: immutable freeze/PDF → fidelity `1.0` → lock → exactly one professional score.
10. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, fidelity=1.0.
