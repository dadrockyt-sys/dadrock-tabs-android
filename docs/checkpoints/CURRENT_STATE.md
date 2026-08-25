# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 America/Montreal
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
The future one-shot capture persists enough source evidence to continue precision-stage experiments CPU-only after the existing `_best_rows_by_slot` selection:
- retained `attacks` plus full corrected-input `eligibleAttacks` that have a selected physical carrier row,
- input/eligible/retained keys and counts plus carrier-missing input keys,
- grid/onset/error, precision/candidate strength, stem/sweep/detection supports,
- every observed candidate MIDI,
- aggregate attack/early/sustain/body/continuity/score,
- per-view A/B attack/early/sustain,
- retained/fail-safe/selected/primary flags,
- legitimate raw zero values preserved exactly.

Readiness flags:
- `fixedRetainedAttackPitchReplayReady=true`
- `attackPolicyReplayReady=true`
- `sourceViewEvidenceReady=true`
- `precisionStrengthRecomputeReady=true`
- `zeroValuePreservationReady=true`

Scope is intentionally **post existing best-row selection**. It is exact for precision attack/pitch policy experiments; it does not claim the alternate raw carrier-row universe is replayable.

Relevant commits:
- eligible universe `b8e511e873ab6857e939b34381542300e219f7b9`
- per-view evidence `fb953ef80bd2e7fb5ea652bd4fd67d804794f67b`
- zero preservation `9714f48496334b6560aa4625987b00303b7d93da`

# Exact CPU reconstruction
## Source/replay artifact validator
`analyzer/v143_precision_replay_artifact_validator.py`

Independently checks/reconstructs:
- source-view minima and aggregate evidence,
- body/continuity/score formula,
- grid error and precision strength,
- exact input/eligible/retained identities/counts,
- baseline attack pruning and exact fail-safe identity,
- legacy zero-strength decision semantics while preserving raw `0.0`,
- render subset and voicing-drop accounting,
- exact audio-derived measure coverage.

## Negative corruption guard
`analyzer/check_v143_precision_replay_corruption_rejection.py`, commit `392f5bc2dc35ded195f6adf92fb4f0c9304e6b7f`.
- Forces true A/B aggregate corruption, precision-strength corruption and grid/onset corruption; validator must reject all.

## Primary + strict stored-v2 replay
`analyzer/v143_precision_replay_policy_compare.py`.
- Primary/fundamental is independently recomputed from persisted physical evidence and must equal stored primary.
- Legacy vs v2 secondary selection is independently recomputed on the fixed retained-attack universe.
- Stored v2 selected pitch sets must equal independent CPU v2 replay exactly; mismatch is fatal.
- Comparator now also runs deterministic voicing/timing validation on the actual product and stores it under `voicingValidation`.
- Latest integration commit: `4f98150d253666ee0e8ee63d427ab3758abab43f`.

## Deterministic voicing + timing replay
`analyzer/v143_precision_replay_voicing_validator.py`.
- Created at `17a650b86e461e7ecf21bb41c60219a7c8c06f7c`.
- Exact voicing/string/fret replay added using the same deterministic `resolve_joint_chord_voicing` path.
- Exact final event timing replay added in commit `681b8bcf4cb03ca188839aa6c1b383f3bb1f6bd7`.

For every retained attack it independently verifies:
- exact supported → playable rendered MIDI set,
- exact `stringIndex`, `stringName`, and `fret`,
- exact preserved primary/dominant MIDI and note-mapping markers,
- exact `timeSeconds == replay.gridTime`,
- exact `onsetTime == replay.onsetTime`,
- rendered/voicing-dropped pitch accounting.

Reports:
- `stringFretReplayMatches=true`
- `primaryPreservationMatches=true`
- `gridTimingReplayMatches=true`
- `physicalOnsetReplayMatches=true`

Self-tests explicitly reject a corrupted fret, corrupted grid time, and corrupted physical onset.

## Capture-order guard
`analyzer/check_v143_precision_replay_capture_order.py`, commit `1e1d8f27f4720585ba73bb07a3eb1cb4c732be4f`.
- Requires order: v2 precision → promoted-harmonic guard → replay capture → candidate voicing → semantic/sustain rendering.
- Confirms replay source is `carrier.rows`, `carrier.grid`, and post-guard precision identity.

# Paid one-shot workflow safety
Workflow: `.github/workflows/v143-repaired-timing-precision-candidate-product.yml`
- Manual dispatch only; `paid_capture_authorized=YES`, default NO.
- Exact branch/head/remote SHA binding before reservation.
- Approved-audio SHA and protected pipeline blob gates.
- Exactly one `python -m modal run ...::approved_audio` command and one producer `.remote(`.
- Reservation lock committed/pushed **before Modal**; `automaticRetryAllowed=false`.
- Any reserved/completed lock blocks automatic repeat.
- Failure outputs salvaged with `if: always()`.
- Artifact validator runs after capture; strict replay comparator + deterministic voicing/timing replay run before final lock.
- Final lock hashes candidate product, replay comparison and replay validation artifacts, so successful finalization binds those green postconditions.

# CPU-only preflight — GREEN through timing/string/fret replay
Workflow: `.github/workflows/v143-precision-shadow-v2-cpu-guard.yml`

Key recent commits:
- strict stored-v2 + capture-order guard `7b61b0778a2aa1eb8c9f031c2fb798828bda8054`
- deterministic voicing workflow guard `4cb35e7211d907dc97e0a688b805042d5612c106`
- deterministic timing workflow guard `69b24d6a978f27f5e40326d54145c7b4580e198e`
- readiness guard requiring voicing + timing evidence `57d482a9f3a04829656176a8895b3dd7b2400a50`

**Latest actual CPU-only guard run: `32799566642` — GREEN.**
Persisted schema-6 result source SHA: `57d482a9f3a04829656176a8895b3dd7b2400a50`.
Bot result commit / observed branch head: `3c64d1f95a7871c28fee9590b7ad7ca4c7c8889e`.

Green result explicitly reports:
- `passed=true`
- `captureReadinessPassed=true`
- `deterministicVoicingReplayPassed=true`
- `deterministicTimingReplayPassed=true`
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

# Downstream technique/sustain replay scope
Audit found that bend, legato and sustain evidence currently derives from temporary separated carrier stems / pitch-energy views after candidate voicing.
- Current one-shot product persists the resulting technique/sustain annotations for the captured v2 render.
- Schema-2 precision replay does **not** persist the full CQT/onset-view universe needed to recompute every downstream technique for hypothetical newly selected pitches later.
- Persisting full stems/CQT would add substantial artifact size/cost and is not justified yet by the known dominant pitch/timing/string/fret failure metrics.
- Therefore do not bloat the one-shot payload now. Treat future CPU replay guarantees as exact for precision attack/pitch + deterministic voicing/string/fret/grid timing/physical onset. Downstream technique re-analysis is a separate scope if source-only evidence later proves it necessary.

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
- Protected runtime reverified after latest guard work at exact blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.

## Checkpoint save — 2026-08-24 America/Montreal
The one-shot capture path is now CPU-preflight green through source evidence, attack selection, primary selection, strict v2 pitch selection, deterministic playable voicing, exact string/fret assignment, grid timing, and physical onset. The paid budget remains untouched.

# Next exact actions
1. Reverify branch/protected blob immediately before any future paid dispatch.
2. Keep timing frozen and professional reference closed.
3. Avoid further low-value hardening/bloat unless a concrete pre-capture risk is found.
4. **Do not dispatch Modal/L4 until the user explicitly authorizes paid usage.**
5. If authorization is given: dispatch exactly once with `paid_capture_authorized=YES`; reservation must land before Modal.
6. Require candidate product + schema-2 replay + exact artifact validator + strict replay/voicing/timing comparison to reconcile before any mutation/freeze.
7. Use persisted replay evidence for subsequent precision experiments CPU-only.
8. Only when source-only evidence supports a genuinely corrected candidate: immutable freeze/PDF → fidelity 1.0 → lock → exactly one professional score.
9. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, fidelity=1.0.

## Revalidation — 2026-08-24 21:11 America/Montreal
- Branch head before this checkpoint save: `38386637acb17a3437696cc3bee8839a67bd1ee4`.
- Protected runtime reverified at exact required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Latest persisted CPU guard remains schema 6 / `passed=true`, run `32799566642`, with `modalInvoked=false`, `newInferenceUsed=false`, `professionalReferenceUsed=false`, `productionModified=false`.
- `debug/v143-contextual-prune/precision-v2-capture-lock.json` is absent: no paid capture has been reserved or consumed.
- No new concrete pre-capture defect was established during this revalidation; per the cost boundary, no speculative payload/runtime expansion was made.
- Current legitimate progress boundary is the explicitly authorized one-shot capture. Until authorization is explicit, remain CPU-only and do not dispatch Modal/L4.

## Strict paid-boundary checkpoint — 2026-08-24 21:22 America/Montreal
- User explicitly authorized steps 1–5, including **exactly one** Modal/L4 carrier capture after CPU preflight is green.
- Added CPU-only strict finalizer `analyzer/v143_precision_paid_capture_finalizer.py`; it refuses finalization unless source-view evidence, precision-strength recomputation, zero preservation, baseline attack replay, independently recomputed primary, strict stored-v2 pitch replay, deterministic playable voicing/string/fret, grid timing, and physical onset all reconcile exactly.
- Paid workflow now records the new readiness flags in `preFreezeTrace` and invokes the strict finalizer only after artifact validation + replay comparison.
- Final lock now binds the green postconditions and artifact SHA256 values; missing replay mismatch counters are rejected rather than treated as zero.
- CPU guard run `32801119456` on source SHA `7d366e90019006bb0a98b83b1ba2039342eab8c9` is **GREEN**.
- Persisted schema-7 CPU result reports `paidFinalLockBindingPassed=true`, `passed=true`, `modalInvoked=false`, `newInferenceUsed=false`, `professionalReferenceUsed=false`, `productionModified=false`.
- CPU result commit / branch head immediately before this checkpoint save: `251933c9d1e592b9c875ea94c0227ea436e5cac9`.
- The earlier run `32800965126` had all tests green but its result-persist step lost a concurrent JSON rebase race; run `32801119456` subsequently completed cleanly and is the authoritative preflight.
- Paid capture has **not yet** been dispatched at this checkpoint. Next action is immediate protected-blob/head/lock reverification, then one manual dispatch with `paid_capture_authorized=YES` under the user's explicit authorization.

## Paid-capture timeout recovery checkpoint — 2026-08-24 America/Montreal
- The previously authorized one-shot paid workflow ran as GitHub Actions run `32801442757`. Reservation landed before Modal and exactly one Modal invocation occurred.
- The Modal function timed out at exactly `1800s` while the second deterministic CPU Demucs pass was at `39/40`; the first direct Demucs pass had taken about 14m33s. This was a timeout-boundary failure, not a model crash.
- No completed new candidate/replay product was accepted. Post-capture artifact validation, replay comparison, final lock, mutation/freeze and professional scoring were skipped.
- Failure-path artifact salvage succeeded, but salvaged files are not a validated new capture product.
- The paid attempt is now explicitly recorded as consumed in `debug/v143-contextual-prune/precision-v2-capture-lock.json`: schema 3, `captureState=failed_timeout`, `modalRunAttemptConsumed=true`, `singlePaidCaptureConsumed=true`, `automaticRetryAllowed=false`, `retryAuthorizationRequired=true`.
- The temporary one-shot dispatch relay workflow and its authorization marker were deleted after use, preventing accidental reuse.
- CPU-only timeout correction changed exactly one producer line: Modal function timeout `1800 -> 3000` seconds. Deterministic Demucs remains CPU-only/single-thread with its proven execution controls; no musical model/settings/path logic changed.
- CPU guard run `32804303926` on source SHA `7bf45837aa6c784a24823d4dd4902a7744539444` is **GREEN**. Persisted schema-7 result reports `passed=true`, `paidFinalLockBindingPassed=true`, `modalInvoked=false`, `newInferenceUsed=false`, `professionalReferenceUsed=false`, `productionModified=false`.
- A separate Product Proof run initially exposed a static anti-leakage false positive: its grep scanned checker code that intentionally contains a forbidden-token test string. Only that checker was removed from the grep target list; it remains compiled and executed as a safety checker.
- Product Proof rerun `32804488611` is **GREEN** after the one-line workflow correction. The exact workflow diff was one deletion only.
- Branch head immediately before this checkpoint save: `d568daaff3173a52d055467269677305f7a9b5f6`.
- Protected runtime reverified at exact required blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- `main`/Production remain untouched. Professional reference/scorer remains closed.
- **Do not run another Modal/L4 capture from a generic “continue”. A second paid attempt requires fresh explicit user authorization.** If authorized later, preserve attempt-1 history, establish a new one-shot authorization/reservation, and dispatch exactly once with the corrected `3000s` timeout.

## CPU-only continuation revalidation — 2026-08-24 22:18 America/Montreal
- Generic `Please continue` was treated as CPU-only continuation, not fresh paid authorization.
- Branch head at revalidation: `85fc7bb9f71d3cb485dfa1009b430fa163e8cdcd`.
- Protected runtime remains exact blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Persisted CPU guard run `32804303926` remains schema 7 / `passed=true`, with all replay/final-lock checks green and `modalInvoked=false`, `newInferenceUsed=false`, `professionalReferenceUsed=false`, `productionModified=false`.
- Product Proof run `32804488611` remains completed / `success`.
- Attempt-1 lock remains schema 3 / `captureState=failed_timeout`, `singlePaidCaptureConsumed=true`, `automaticRetryAllowed=false`, `retryAuthorizationRequired=true`.
- No second Modal/L4 invocation occurred. No scorer/reference, render mutation, freeze, Production, or `main` change occurred.
- No further free algorithmic change is justified before the carrier/replay capture; avoid speculative hardening or payload growth.
- Next paid boundary is a **new explicitly authorized one-shot retry** using the already-corrected `3000s` timeout, while preserving attempt-1 history.
