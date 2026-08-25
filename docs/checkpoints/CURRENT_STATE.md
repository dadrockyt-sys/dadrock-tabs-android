# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 America/Montreal
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
- Any future professional score requires a genuinely new approved-audio corrected candidate → immutable freeze/PDF → lock → exactly one score.
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 unless the user explicitly reopens paid usage.** Current work remains CPU-only/reference-free.

## Immutable historical score state
- Score 1 retired: 725 attacks → 985 rendered notes, 113 measures, PDF fidelity `1.0`; run `32731885778`; pitch F1 `0.23718280683583634`; pitch+timing F1 `0.033143448990160536`; critical mismatches `1723`.
- Score 2 retired after harmonic contradiction fix: 889 events, PDF fidelity `1.0`; run `32752374788`; pitch F1 `0.24305177111716622`; pitch+timing F1 `0.03051771117166212`; string/fret+timing F1 `0.01852861035422343`; chord F1 `0.012048192771084336`; critical mismatches `1635`.
- Harmonic contradiction was real but not the dominant failure.

## Frozen / historical source identity
- Frozen pre-scorer evidence: `debug/v143-contextual-prune/frozen-approved-audio-preholdout-evidence.json`.
- 725 retained attacks; 113 measures; `tempoBpm=129.19921875`; reference-free provenance exact.
- Historical candidate run `32699399835`, preholdout run `32702772593`.
- Historical carrier blob `99866aa8af14dc243d226c6fb28d68af14d003ac`; legacy precision blob `feeaafea511bf727099d1532a323f9106af75b7a`.

# Dominant pitch diagnosis
- Same 725 retained attacks entered legacy precision with **7,535 observed pitch hypotheses**.
- Legacy precision retained only `987`; **6,548 observed pitches were suppressed**.
- Genuine optional secondary universe = 6,666; only 118 survived = `1.7702%`; 6,548/6,666 = `98.2298%` suppressed.
- Legacy non-harmonic secondary gate requires score AND attack AND body at `0.80`; exact upper-harmonic intervals `{12,19,24,28,31,36}` require all three at `0.92`.
- MIDI64 remains a symptom of strong-primary/gate interaction, not an E4 hard-code.
- Historical suppressed rows cannot be recovered from old artifacts/logs; one new carrier capture is required for exact replay.

# Precision v2
Module: `analyzer/v143_contextual_prune_precision_shadow_v2.py`
Policy: `envelope-balanced-secondary-v2`

- Attack selection, fail-safe, primary/fundamental promotion, no-invention invariants and harmonic protections remain unchanged.
- Non-harmonic observed secondaries use **2-of-3 physical consensus** across score/attack/body at the existing `0.80` floor.
- Exact upper-harmonic intervals remain strict legacy 3-of-3 at `0.92`.
- No new numeric threshold, pitch, key/chord/song rule, runtime label, or professional information.
- Existing CPU guard: `debug/v143-contextual-prune/precision-v2-cpu-guard-result.json`; run `32777140959`, job `97590681839`, success; no Modal/reference/Production.

# One-shot capture path — prepared, NOT RUN
Producer: `analyzer/v143_repaired_timing_precision_candidate_product_modal.py`
Workflow: `.github/workflows/v143-repaired-timing-precision-candidate-product.yml`
Lock: `debug/v143-contextual-prune/precision-v2-capture-lock.json`

## Paid-budget/failure-path hardening
- Manual dispatch only; `paid_capture_authorized=YES` required; default `NO`.
- Dispatch must be on `refs/heads/v143-contextual-prune-lobo` and checkout `HEAD`, `GITHUB_SHA`, and fetched remote target head must agree before reservation.
- Approved fixture SHA and protected pipeline blob are hard-gated before capture.
- Exactly one workflow `python -m modal run ...::approved_audio` command and one producer `.remote(` call are permitted.
- A reservation lock is committed/pushed **before Modal** with `captureState=reserved_before_modal`, `singlePaidCaptureConsumed=false`, `automaticRetryAllowed=false`.
- Any reserved/completed lock blocks automatic repeat.
- Capture outputs are preserved via `actions/upload-artifact@v4` with `if: always()`.
- A failed/interrupted reserved attempt is intentionally not automatically retryable.

## Replay completeness hole found and fixed — NEW
Earlier replay persistence covered only retained attacks. That was sufficient for pitch-secondary policy experiments but **not** sufficient for future attack-pruning experiments without another separator/Basic Pitch run.

`analyzer/v143_contextual_prune_precision_shadow_v2.py` now writes replay schema **2** and preserves both:
1. `attacks`: retained-attack pitch replay contract, and
2. `eligibleAttacks`: the full corrected-input attack universe that has a physical carrier row.

Each eligible attack now persists:
- measure/step and onset time,
- `_precisionStrength` as `precisionStrength`,
- grid error,
- retained/fail-safe flags,
- every observed candidate MIDI,
- physical attack/early/sustain/body/continuity/score evidence,
- selected/primary flags.

Schema-2 replay also persists:
- `inputAttackKeys`,
- `carrierMissingInputAttackKeys`,
- `inputAttackCount`, `eligibleAttackCount`, `retainedAttackCount`, `prunedAttackCount`,
- retained and eligible pitch-hypothesis counts,
- `fixedRetainedAttackPitchReplayReady=true`,
- `attackPolicyReplayReady=true`,
- `replayCompleteness=retained-pitch-plus-eligible-attack-source-universe`.

Latest replay-universe module commit returned by connector: `b8e511e873ab6857e939b34381542300e219f7b9`.

## Exact replay artifact validator — schema 2
`analyzer/v143_precision_replay_artifact_validator.py` now validates:
- schema/policy/reference-free flags,
- exact input = eligible ∪ carrier-missing attack universe,
- unique/canonical attack identities,
- retained attacks exactly equal their eligible source records,
- observed candidate identity/order/uniqueness,
- finite attack/early/sustain/body/continuity/score values,
- body/continuity derivation and score formula,
- selected/primary invariants,
- replay↔precision counts,
- render attack/pitch subset binding,
- voicing-drop accounting,
- exact audio-derived measure coverage.

It also reconstructs the baseline precision **attack policy** from persisted eligible evidence using the exact current floors/radius/local-prominence/fail-safe rules and requires the recomputed retained and fail-safe identities to match the stored result exactly.
- Independent CPU logic check for the synthetic strong/pruned/fail-safe case reproduced retained `{(1,0),(2,0)}` and fail-safe `{(2,0)}` as intended.
- Latest validator commit returned by connector: `67b2da8968f1c000f4a8cb4384e87b2de97c5263`.

## Workflow binding updated for schema 2
- Inline candidate checks now require replay schema 2, completeness mode, fixed-retained pitch replay readiness and attack-policy replay readiness.
- Pre-freeze trace binds input/eligible/retained attack counts plus eligible/retained pitch counts.
- Final lock cannot complete unless validator reports `baselineAttackReplayMatches=true` and `attackPolicyReplayReady=true`.
- Final lock binds input/eligible/retained attack counts, eligible/retained pitch counts, replay hash, event hash, candidate product hash, replay-policy compare hash and validation artifact hash.
- Latest workflow commit returned by connector: `9cbeaf5f0b977f51adc9d8a5d030f983f59abbf5`.

## Replay policy comparison strengthened — NEW
`analyzer/v143_precision_replay_policy_compare.py` now:
- requires schema 2 and exact `envelope-balanced-secondary-v2` identity,
- requires both retained-pitch and full attack replay readiness,
- rejects duplicate retained attack keys and bad source flags,
- remains explicitly scoped to pitch-policy comparison on the **fixed retained-attack universe**,
- reports eligible attack/pitch universe sizes for provenance,
- includes edge-case self-tests for all three non-harmonic 2-of-3 combinations, one-dimension rejection, strict harmonic 3-of-3 behavior, promoted-strongest-harmonic common guard, and no-positive fallback,
- imports actual v143 thresholds during its self-test so constant drift is detected.
- Latest replay-compare commit returned by connector: `59cbe8cd1309ec47f3a2a9d1c7de5838ed3225c5`.

## Static capture readiness checker strengthened
`analyzer/check_v143_precision_capture_readiness.py` now requires:
- full schema-2 serializer tokens (`eligibleAttacks`, input keys, strength, readiness flags),
- validator attack-policy reconstruction/reporting,
- eligible-universe counts in the final lock,
- baseline attack replay before lock finalization,
- exact producer replay function name `build_precision_replay_evidence(` (fixing a stale static-string check),
- all prior branch/head/lock/single-paid-call/failure-salvage invariants.
- Latest checker commit returned by connector: `c295107556da7fa5c3ef3a82818e967e34a2e23b`.

# Timing remains frozen
- Relative integer sixteenth spacing remains exceptionally well supported: at residual <=0.20 step, 697/697 consecutive pairs exactly match labeled grid gaps; all 8-measure windows have exact high-confidence gap-match rate `1.0`.
- Tempo reproduces exactly at `129.19921875`.
- Beat repair removes interval outliers without a leading phase-index error.
- Full-mix absolute 4/4 phase is weak/section-dependent; no stable global phase correction is justified.
- Therefore do **not** mutate timing/grid from current source-only evidence.

# Current mutation / cost state
- No new candidate generated.
- **No Modal/L4 invoked.**
- No professional scorer/reference invoked.
- No render events mutated.
- `main` and Production untouched.
- Protected runtime must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1` and will be reverified before further mutation/capture work.

## Checkpoint save — 2026-08-24 America/Montreal
- The one future paid carrier capture is now being made substantially more valuable: schema-2 replay is intended to preserve enough derived physical evidence for both pitch-policy and attack-policy experiments to continue CPU-only afterward.
- Paid budget protections remain in place; nothing paid was dispatched.
- No completion claim is made.

# Next exact actions
1. Reverify branch head and protected runtime blob.
2. Finish CPU-only schema-2 consistency audit across serializer, validator, workflow and replay comparator; fix any static/self-test mismatch.
3. Add/verify drift checks tying attack replay constants to actual legacy precision constants.
4. Keep timing frozen and professional reference closed.
5. **Do not dispatch Modal/L4 unless the user explicitly authorizes paid usage.**
6. If explicit authorization is later given: dispatch exactly once with `paid_capture_authorized=YES`; reservation must land before Modal.
7. Require candidate product + schema-2 replay + exact artifact validation + replay-policy comparison to reconcile before any later mutation.
8. Use persisted replay evidence for subsequent precision experiments CPU-only; avoid repeated separator/Basic Pitch inference.
9. Only when source-only evidence supports a genuinely corrected candidate: immutable freeze/PDF → fidelity `1.0` → lock → exactly one professional score.
10. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, fidelity=1.0.
