# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-06 America/Toronto
Branch: `v143-contextual-prune-lobo`

This file is the compact fresh-chat source of truth. Full prior detail remains in Git history.

## NON-NEGOTIABLE AUTHORIZATION / BUDGET BOUNDARY

The authorized evaluation budget is already consumed:
- replacement V143 Rhythm model-bearing start: **0 available / 1 consumed**
- professional full-1–113 score: **0 available / 1 consumed**
- replacement PDF E2E: **1 performed / passed**

**DO NOT** start another Rhythm/Lead/Bass model-bearing analysis.
**DO NOT** run the professional scorer again.
**DO NOT** invoke Modal/GPU/paid inference, optimizer/training/threshold sweeps, deploy/promote Production, weaken Deployment Protection, or mutate model/scheduler parameters without new explicit user authorization.

Safe continuation is deterministic/model-free source inspection, static validation, and CPU-only/read-only replay of already-persisted evidence.

## FROZEN LIVE RESULT — DO NOT RERUN

Authorized Rhythm run:
- workflow `.github/workflows/v143-one-shot-final-rhythm-e2e.yml`
- run `34046854397`
- recovery run `34048291636`
- frozen result: 364 selected attacks / 925 rendered notes
- PDF event fidelity: 1.0

Consumed professional holdout run `34048719525`:
- `near100ProfessionalGatePassed = false`
- pitch-content F1 `0.30892570817744525`
- pitch-timing tolerant F1 `0.05879208979155532`
- chord pitch-set tolerant F1 `0.004136504653567736`
- unmatched generated notes `779`
- unmatched reference notes `800`

Interpretation remains unchanged: infrastructure/rendering succeeded; musical score construction did not. **Do not tune against the professional reference.**

## PERSISTED PAID PRECISION EVIDENCE — SOURCE OF TRUTH

Successful authorized paid precision capture:
- workflow run `32805316807`
- capture/replay commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`
- approved fixture SHA-256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- artifact `v143-precision-v2-one-shot-32805316807`, id `9548666053`
- historical candidate Git blob `7e6002cd4d42f355685241e0576c78940056f093`
- no further paid capture is authorized.

Persisted baseline facts:
- measures 1–113
- precision-v2 retained attacks: **725**
- precision-v2 selected pitches: **970**
- rendered after deterministic guitar voicing: **967**
- voicing drops: **3**
- historical later event-layer convenience replay: **965**
- all 113 measures populated
- exact deterministic replay mismatch counts were zero
- no unobserved attack/pitch creation
- professional reference not used

Schema-2 replay artifact validation also records:
- input/eligible attacks **984**
- all-input original pitch hypotheses **7535**
- retained attacks **725**
- stored selected pitches **970**
- rendered pitches **967**
- `referenceFree=true`
- `newInferenceUsed=false`
- `failSafeAttackCount=0`

An older checkpoint stated **6525** retained-only original hypotheses. The downloaded persisted artifact's `precisionReplayEvidence.attacks` currently sums to **7535 candidate hypotheses across the 725 retained attacks**. Treat this as an evidence-lineage discrepancy to document, not as permission to rerun inference; the current replay below uses the exact persisted per-attack artifact payload.

Historical commit `c1451df...` contains:
- `debug/v143-contextual-prune/precision-v2-capture-lock.json`
- `debug/v143-contextual-prune/precision-v2-replay-artifact-validation.json`
- `debug/v143-contextual-prune/precision-v2-replay-policy-compare.json`
- `debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json`

## CPU-ONLY REPLAY RESULT — FEASIBILITY RECOVERY FAILS

**Checkpointed immediately after replay and before any helper/candidate change.**

Current isolated helper before repair:
- `analyzer/v143_precision_polyphony_boundary.py`
- blob `720a068d71ad72719053cdc89bdab81db541c884`
- adapter `analyzer/v143_contextual_prune_precision_candidate_events.py`
- blob `68732a07701a30a455ba9bcbf7c2adddd3930622`

The exact persisted artifact from already-consumed run `32805316807` was downloaded read-only. No workflow was triggered. `resolve_precision_polyphony(...)` was replayed deterministically against all **725 persisted retained attacks**, using the artifact's per-pitch `attack`, `body`, and `score` evidence, the current floors (`attack > 0.0`, `body > -0.25`), current harmonic interval set `{12,19,24,28,31,36}`, and the current deterministic joint-guitar-voicing constraints.

Replay result:
- retained attack identity changed: **NO**
- replay attacks: **725**
- original observed candidate hypotheses in persisted retained-attack payload: **7535**
- baseline precision-v2 selected pitches: **970**
- baseline precision-only deterministic voicing render: **967**
- baseline precision-only voicing drops: **3**
- feasibility-boundary rendered pitches: **3485**
- recovered pitches beyond precision-v2: **2518**
- attacks affected by recovery: **703 / 725**
- inflation versus 970 selected pitches: **+2515 / +259.28%**
- inflation versus 967 rendered baseline: **+2518 / +260.39%**
- recovery candidate legal-voicing drops/rejections: **1168**
- max rendered chord size: **6**
- primary preservation failures: **0**
- unobserved pitch count: **0**
- unobserved attack count: **0**
- protected promoted-harmonic violations: **0**
- median recovered pitches on affected attacks: **4**
- maximum recovered pitches on an affected attack: **5**

**Deterministic decision: the feasibility-recovery boundary materially over-recovers precision-v2-pruned hypotheses and is NOT safe to keep in its current form.** Guitar playability is not sufficient musical evidence. The helper must not re-admit all merely-positive observed hypotheses.

This result is reference-free. No model, Basic Pitch inference, GPU, Modal, paid inference, professional scorer, optimizer, threshold sweep, production mutation, deployment, or live endpoint integration was used.

## NEXT SAFE SCORE-STRUCTURE ACTION

Per the preregistered decision rule, remove or restrict the feasibility-recovery behavior using deterministic source-evidence invariants only. The safest minimal repair is **preservation-only polyphony**:
- keep the precision-v2 retained pitch set authoritative
- preserve the explicit precision primary
- perform only deterministic legal joint-guitar voicing over those already-retained precision pitches
- allow the same historical legal-voicing drops (expected baseline 970 -> 967)
- recover **zero** precision-v2-pruned hypotheses
- do not add/relocate attacks or invent pitches
- keep the helper isolated from the frozen live endpoint/Production

After changing the isolated helper/adapter:
1. rerun the same CPU-only persisted-artifact replay only
2. require 725 attacks, 970 baseline selected, 967 rendered, 3 voicing drops, 0 recovered, 0 primary failures, 0 unobserved attacks/pitches
3. add/update deterministic unit/static validation for the preservation-only invariant
4. checkpoint `docs/checkpoints/CURRENT_STATE.md` again
5. do **not** integrate into live/Production without separate explicit product/integration authorization

Only after this score-structure slice is closed, return to the separate async-result lifetime defect: locate the real ~900-second control/result ownership TTL and patch only that boundary so it safely exceeds the 1200-second worker budget. Do not patch a guessed symbol.

## FRESH-CHAT SUCCESS CONDITION

The central question is now answered:

**The new feasibility-recovery boundary over-recovers precision-v2-pruned hypotheses. Replace it with preservation-only legal voicing, validate deterministically against persisted evidence, and keep it isolated.**
