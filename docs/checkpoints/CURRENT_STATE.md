# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 20:51 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. No runtime/shadow tuning or selection from it.
- Retired render identities must never be rerun/rescored:
  - `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
  - `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 without explicit user authorization.**

## Historical score state
- Score 1 retired: 725 attacks → 985 notes, 113 measures, PDF fidelity 1.0; pitch F1 `0.23718280683583634`; pitch+timing F1 `0.033143448990160536`; critical mismatches `1723`.
- Score 2 retired after harmonic contradiction guard: 889 events, PDF fidelity 1.0; pitch F1 `0.24305177111716622`; pitch+timing F1 `0.03051771117166212`; critical mismatches `1635`.

## Dominant source-only diagnosis
- 725 retained attacks entered legacy precision with **7,535 observed pitch hypotheses**.
- Legacy precision retained only `987`; **6,548 observed pitches were suppressed**.
- Genuine optional-secondary universe = 6,666; only 118 survived (`1.7702%`).
- Legacy non-harmonic secondaries require score AND attack AND body at `0.80`; exact upper-harmonic intervals `{12,19,24,28,31,36}` stay strict 3-of-3 at `0.92`.
- Historical suppressed rows were not persisted; one new carrier capture is required for exact current-source replay.

# Precision v2
Module: `analyzer/v143_contextual_prune_precision_shadow_v2.py`
Policy: `envelope-balanced-secondary-v2`

- Non-harmonic observed secondaries use 2-of-3 score/attack/body at the existing `0.80` floor.
- Harmonic upper secondaries remain legacy 3-of-3 at `0.92`.
- Attack selection, measure fail-safe, primary/fundamental promotion, no-invention invariants and harmonic protections remain unchanged.
- No new numeric threshold, song/key/chord rule, runtime label, or professional information.

# Replay schema 2 — fixed-best-row precision-stage replay
The future one-shot capture now persists enough source evidence to continue precision-stage experiments CPU-only after the existing `_best_rows_by_slot` selection:
- retained `attacks` plus full corrected-input `eligibleAttacks` that have a selected physical carrier row,
- input/eligible/retained keys and counts plus carrier-missing input keys,
- grid/onset/error, precision/candidate strength, stem/sweep/detection supports,
- every observed candidate MIDI,
- aggregate attack/early/sustain/body/continuity/score,
- per-view A/B attack/early/sustain,
- retained/fail-safe/selected/primary flags,
- zero values preserved exactly.

Readiness flags:
- `fixedRetainedAttackPitchReplayReady=true`
- `attackPolicyReplayReady=true`
- `sourceViewEvidenceReady=true`
- `precisionStrengthRecomputeReady=true`
- `zeroValuePreservationReady=true`

Scope is intentionally **post existing best-row selection**. It is exact for precision attack/pitch policy experiments; it does not claim the raw alternate carrier-row universe is replayable.

Relevant commits:
- eligible universe `b8e511e873ab6857e939b34381542300e219f7b9`
- per-view evidence `fb953ef80bd2e7fb5ea652bd4fd67d804794f67b`
- zero preservation `9714f48496334b6560aa4625987b00303b7d93da`

# Replay validation / strict CPU reconstruction
## Artifact validator
`analyzer/v143_precision_replay_artifact_validator.py`, commit `7e93ce15ad8255425d6628807f2a9a1df075c34f`.

It independently reconstructs/checks:
- source-view minima and aggregate evidence,
- body/continuity/score formula,
- grid error and precision strength,
- exact input/eligible/retained identities and counts,
- render subset and voicing-drop accounting,
- baseline attack pruning and exact fail-safe identity,
- legacy zero-strength decision semantics while preserving raw `0.0` in the artifact.

## Negative corruption guard
`analyzer/check_v143_precision_replay_corruption_rejection.py`, commit `392f5bc2dc35ded195f6adf92fb4f0c9304e6b7f`.
- Forces true A/B aggregate corruption, strength corruption and grid/onset corruption; validator must reject all.

## Primary + strict stored-v2 replay
`analyzer/v143_precision_replay_policy_compare.py`.
- Primary/fundamental is independently recomputed from persisted physical evidence and must match stored primary.
- Legacy vs v2 secondary selection is recomputed on the fixed retained-attack universe.
- **Stored v2 selected pitch sets must now match independent v2 CPU replay exactly; any mismatch is fatal.**
- Latest strict commit: `bcf240a2327983e7602e2d7b553f00a93addc31d`.

## Capture-order guard
`analyzer/check_v143_precision_replay_capture_order.py`, commit `1e1d8f27f4720585ba73bb07a3eb1cb4c732be4f`.
- Requires order: v2 precision → promoted-harmonic guard → replay capture → candidate voicing → semantic/sustain rendering.
- Confirms replay is sourced from `carrier.rows`, `carrier.grid`, and post-guard precision identity.
- This prevents downstream voicing drops from being confused with source-pitch suppression.

# Paid one-shot workflow safety
Workflow: `.github/workflows/v143-repaired-timing-precision-candidate-product.yml`
- Manual dispatch only; `paid_capture_authorized=YES`, default NO.
- Exact branch/head/remote SHA binding before reservation.
- Approved-audio SHA and protected pipeline blob gates.
- Exactly one `python -m modal run ...::approved_audio` command and one producer `.remote(`.
- Reservation lock committed/pushed **before Modal**; `automaticRetryAllowed=false`.
- Any reserved/completed lock blocks automatic repeat.
- Failure outputs salvaged with `if: always()`.
- Validator runs after capture; strict replay comparator runs before final lock.
- Final lock hashes candidate product, replay comparison and replay validation artifacts. Because validator/comparator fail on source/replay mismatch, those hashes bind the green postconditions.

# CPU-only preflight — GREEN
Workflow: `.github/workflows/v143-precision-shadow-v2-cpu-guard.yml`

Latest guard enhancement:
- commit `7b61b0778a2aa1eb8c9f031c2fb798828bda8054` adds strict stored-v2 replay and capture-order testing.
- readiness commit `4c31788e5cd377d588cd40a559edbbfa7f10af9b` makes capture-order + strict replay part of the paid workflow pre-Modal readiness command too.

**Latest actual CPU run: `32799057905` — SUCCESS.**
Persisted result source SHA: `4c31788e5cd377d588cd40a559edbbfa7f10af9b`.
Bot result commit / current observed branch head before this checkpoint: `fd42a41f68c5279920feac80017fa6c82886a62c`.

Green schema-4 result explicitly reports:
- `passed=true`
- `captureReadinessPassed=true`
- `storedV2ReplayStrictPassed=true`
- `replayCaptureOrderPassed=true`
- `replayArtifactValidatorSelfTestPassed=true`
- `replayCorruptionRejectionPassed=true`
- `sourceViewEvidenceBindingPassed=true`
- `precisionStrengthRecomputePassed=true`
- `zeroValuePreservationPassed=true`
- `primaryRecomputePassed=true`
- `fixedBestRowAttackReplayPassed=true`
- `singlePaidCaptureStaticGuardPassed=true`
- `modalInvoked=false`
- `newInferenceUsed=false`
- `professionalReferenceUsed=false`
- `productionModified=false`
- protected blob exact `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.

# Timing remains frozen
- Relative sixteenth spacing remains strongly source-supported; at residual <=0.20 step, 697/697 pairs exactly match labeled grid gaps.
- Tempo remains exactly `129.19921875`.
- Beat repair has no leading phase-index error.
- Absolute bar phase remains weak/section-dependent; no global timing mutation is justified.

# Current cost/mutation state
- No new candidate generated.
- **No Modal/L4 invoked.**
- No professional scorer/reference invoked.
- No render events mutated.
- `main` and Production untouched.
- Protected runtime reverified during this work at exact blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.

## Checkpoint save — 2026-08-24 20:51 America/Montreal
We now have a real green CPU-only preflight proving the schema-2 replay source binding, negative corruption rejection, baseline attack replay, primary recomputation, strict stored-v2 replay agreement, capture ordering, paid-budget guards and protected-runtime identity. No paid inference was used.

# Next exact actions
1. Reverify branch/protected blob after this checkpoint commit.
2. Audit the remaining one-shot artifact for anything else worth persisting before paid inference; avoid unnecessary raw-carrier bloat unless technically justified.
3. Keep timing frozen and professional reference closed.
4. **Do not dispatch Modal/L4 until the user explicitly authorizes paid usage.**
5. If authorization is later given, dispatch exactly once with `paid_capture_authorized=YES`; reservation must land before Modal.
6. Require candidate product + schema-2 replay + exact validator + strict replay comparison to reconcile before any mutation/freeze.
7. Use persisted replay evidence for subsequent precision experiments CPU-only.
8. Only when source-only evidence supports a genuinely corrected candidate: immutable freeze/PDF → fidelity 1.0 → lock → exactly one professional score.
9. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, fidelity=1.0.
