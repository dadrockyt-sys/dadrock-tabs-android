# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-06 America/Toronto
Branch: `v143-contextual-prune-lobo`

This is the compact fresh-chat source of truth. Full prior detail remains in Git history.

## NON-NEGOTIABLE AUTHORIZATION / BUDGET BOUNDARY

Authorized evaluation budget is consumed:
- replacement V143 Rhythm model-bearing start: **0 available / 1 consumed**
- professional full-1–113 score: **0 available / 1 consumed**
- replacement PDF E2E: **1 performed / passed**

**DO NOT** start another Rhythm/Lead/Bass model-bearing analysis.
**DO NOT** run the professional scorer again.
**DO NOT** invoke Modal/GPU/paid inference, optimizer/training/threshold sweeps, deploy/promote Production, weaken Deployment Protection, or mutate model/scheduler parameters without new explicit user authorization.

Safe continuation: deterministic/model-free source inspection, static/unit validation, and CPU-only/read-only replay of already-persisted evidence.

## FROZEN LIVE RESULT — DO NOT RERUN

Authorized Rhythm run:
- workflow `.github/workflows/v143-one-shot-final-rhythm-e2e.yml`
- run `34046854397`
- recovery run `34048291636`
- frozen result: **364 selected attacks / 925 rendered notes**
- PDF event fidelity: **1.0**

Consumed professional holdout run `34048719525`:
- `near100ProfessionalGatePassed = false`
- pitch-content F1 `0.30892570817744525`
- pitch-timing tolerant F1 `0.05879208979155532`
- chord pitch-set tolerant F1 `0.004136504653567736`
- unmatched generated notes `779`
- unmatched reference notes `800`

Interpretation remains unchanged: infrastructure/rendering succeeded; musical score construction did not. **Do not tune against the professional reference.**

## PERSISTED PAID PRECISION EVIDENCE — SOURCE OF TRUTH

Authorized paid precision capture:
- workflow run `32805316807`
- capture/replay commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`
- fixture SHA-256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- artifact `v143-precision-v2-one-shot-32805316807`, id `9548666053`
- artifact digest `sha256:5104522aab3e6193c6b06fe3abb807994065f858a945a81070c611fc63707d4f`
- no further paid capture is authorized

Persisted baseline invariants:
- measures: **113**
- retained attacks: **725**
- precision-v2 selected pitches: **970**
- rendered after deterministic guitar voicing: **967**
- legal-voicing drops: **3**
- all 113 measures populated
- no unobserved attack/pitch creation
- professional reference not used

Schema-2 validation records:
- input/eligible attacks **984**
- original candidate hypotheses **7535**
- retained attacks **725**
- stored selected pitches **970**
- rendered pitches **967**
- `referenceFree=true`
- `newInferenceUsed=false`
- `failSafeAttackCount=0`

Older history stated **6525** retained-only hypotheses; the persisted artifact payload currently sums to **7535** across the 725 retained attacks. Treat this only as an evidence-lineage discrepancy; it is not permission to rerun inference.

## HISTORICAL BROAD FEASIBILITY RECOVERY — REJECTED

Historical CPU-only/read-only replay showed broad feasibility recovery was unsafe:
- baseline selected pitches: **970**
- baseline rendered: **967**
- broad feasibility-boundary rendered: **3485**
- recovered beyond precision-v2: **2518**
- affected attacks: **703 / 725**

Decision: **guitar feasibility/physical positivity alone must never re-admit precision-v2-pruned pitches.**

## SCORE-STRUCTURE SLICE — CLOSED

Current exact blobs:
- helper `analyzer/v143_precision_polyphony_boundary.py`: `83a1d993ff654c45bb965a7794f2d155aab18a25`
- adapter `analyzer/v143_contextual_prune_precision_candidate_events.py`: `509032e3969ea057c05743c148ade2d2d4da4bf0`
- validator `analyzer/validate_v143_precision_polyphony_preservation.py`: `8f4c420482674f484541a4c6d5bf90df0d7f6465`

Code commits:
- adapter hardening: `255616674eb4d113804d5a4296b771318717745f`
- deterministic validator: `838d900732abeb19740bea0ca8a23131a8701fe3`

Correction retained from earlier checkpoint: the adapter matches the helper function signature; there is no signature `TypeError`.

Preservation policy now enforced independently at helper + adapter:
- precision-v2 retained pitch set is sole musical authority
- observed-but-pruned pitches are diagnostic/provenance only
- helper candidates must exactly equal persisted precision-v2 retained set
- helper selected MIDIs must be a subset of that set
- primary is immutable
- any non-empty `recovered_midis` raises
- helper drop set must equal retained minus selected
- final emitted event MIDI must belong to `precision.pitch_sets[key]` unconditionally
- legacy recovery-shaped metadata remains only for compatibility and is hard `False`
- `polyphonyBoundary.recoveredPitchCount = 0`
- `polyphonyBoundary.recoveryPermitted = False`
- a recovery marker on an emitted event is a runtime error

## DETERMINISTIC VALIDATION — PASS

Dependency-free local validator result:
- adapter `py_compile`: PASS
- actual helper source tested with MIDI `67` deliberately made extremely strong, positive, and playable while pruned; it remains excluded
- adapter rejects widened candidate set
- adapter rejects widened selected set
- adapter rejects non-empty recovery set
- legacy recovery-shaped output fields verified hard-false
- old permissive `midi not in precision_set and not recovered` escape hatch absent
- result: **`V143 precision polyphony preservation validation: PASS`**

## PERSISTED CURRENT-HELPER REPLAY — PASS

The already-consumed artifact `9548666053` was downloaded read-only. No workflow was triggered. The persisted `precisionReplayEvidence.attacks` payload was replayed through the **current** preservation-only helper using the current deterministic guitar-voicing constraints and stored attack/body/score evidence.

Replay result:
- retained attacks: **725**
- precision-v2 selected pitches input: **970**
- rendered after current legal voicing: **967**
- legal-voicing drops: **3**
- recovered/pruned hypotheses re-admitted: **0**
- primary preservation failures: **0**
- unobserved pitches: **0**
- candidate-set mismatches: **0**
- stored artifact render count: **967**

Exact deterministic drops:
- measure 40, step 14: MIDI **78**
- measure 63, step 14: MIDI **47**
- measure 113, step 13: MIDI **43**

All acceptance invariants match exactly. **The score-structure preservation slice is closed.**

This validation/replay used no new inference, model, Basic Pitch run, GPU, Modal, paid service, professional scorer/reference, optimizer, threshold sweep, deployment, or Production mutation.

## WORKFLOW-SAFETY CHECK

Checkpoint push `36fc6bda1247bedbd9642a50b07ca4d52fbadb25` produced exactly one GitHub Actions run: `.github/workflows/cleanup-tab-preview.yml` run `34080214025`; no model/scoring workflow ran. No workflow was manually triggered during this work.

## NEXT SAFE ACTION — ASYNC RESULT LIFETIME DEFECT

Now move to the separate async-result lifetime defect.

Known problem statement from prior work: a control/result ownership lifetime appears to be ~900 seconds while the worker budget can reach 1200 seconds. The goal is to locate the **actual** TTL/expiration boundary and patch only that real boundary so it safely exceeds the 1200-second worker budget.

Rules:
1. inspect source/history first; do not patch a guessed symbol
2. distinguish worker execution timeout from result/control ownership TTL
3. do not change model inference, scheduler/model parameters, score construction, or Production
4. prefer a minimal isolated constant/config change plus deterministic tests/static validation
5. do not deploy without explicit authorization
6. checkpoint this file again immediately after locating the actual TTL boundary and before/after any patch

## FRESH-CHAT SUCCESS CONDITION

Score-structure is closed at **725 / 970 / 967 / 3 drops / 0 recovery**. Next success condition is: **identify the real async control/result lifetime responsible for the ~900-second expiry, prove its relationship to the 1200-second worker budget, and patch only that boundary with deterministic validation—without deploying or triggering model-bearing work.**
