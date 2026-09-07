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

Schema-2 validation also records:
- input/eligible attacks **984**
- original candidate hypotheses **7535**
- retained attacks **725**
- stored selected pitches **970**
- rendered pitches **967**
- `referenceFree=true`
- `newInferenceUsed=false`
- `failSafeAttackCount=0`

Older history stated **6525** retained-only hypotheses; the persisted artifact payload currently sums to **7535** across the 725 retained attacks. Treat this only as an evidence-lineage discrepancy; it is not permission to rerun inference.

## DETERMINISTIC REPLAY — BROAD FEASIBILITY RECOVERY REJECTED

Historical CPU-only/read-only replay of the already-consumed artifact showed broad feasibility recovery was unsafe:
- baseline selected pitches: **970**
- baseline rendered: **967**
- broad feasibility-boundary rendered: **3485**
- recovered beyond precision-v2: **2518**
- affected attacks: **703 / 725**
- primary preservation failures: **0**
- unobserved pitches/attacks: **0 / 0**

Decision: **guitar feasibility/physical positivity alone must never re-admit precision-v2-pruned pitches.**

## SCORE-STRUCTURE SLICE — ADAPTER HARDENED

Current exact blobs:
- helper `analyzer/v143_precision_polyphony_boundary.py`: `83a1d993ff654c45bb965a7794f2d155aab18a25`
- adapter `analyzer/v143_contextual_prune_precision_candidate_events.py`: `509032e3969ea057c05743c148ade2d2d4da4bf0`
- validator `analyzer/validate_v143_precision_polyphony_preservation.py`: `8f4c420482674f484541a4c6d5bf90df0d7f6465`

Code commits:
- adapter hardening: `255616674eb4d113804d5a4296b771318717745f`
- deterministic validator: `838d900732abeb19740bea0ca8a23131a8701fe3`

Correction retained from the prior checkpoint: the adapter matches the helper function signature; there is no signature `TypeError`.

Current helper behavior:
- precision-v2 retained pitch set is authoritative
- observed-but-pruned pitches remain provenance/diagnostic evidence only
- selected pitches are always a subset of the precision-v2 retained set
- primary is immutable
- `recovered_midis` is empty and guarded by a runtime invariant
- legal joint-guitar-voicing may drop precision-selected secondaries only

Adapter hardening now enforces the same policy independently:
- helper `candidate_midis` must exactly equal the persisted precision-v2 retained pitch set
- helper selected MIDIs must be a subset of that retained set
- any non-empty `recovered_midis` raises
- helper dropped MIDIs must exactly equal retained minus selected
- final emitted event MIDI must belong to `precision.pitch_sets[key]` unconditionally
- legacy recovery-shaped metadata fields remain for compatibility but are hard `False`
- `polyphonyBoundary.recoveredPitchCount = 0` and `recoveryPermitted = False`
- a recovery marker on an emitted event is itself a runtime error

## DETERMINISTIC VALIDATION COMPLETED

Local, CPU-only, dependency-free validation performed with no workflow/manual analysis trigger and no model/reference access:
- `py_compile` passed for the hardened adapter
- preservation assertion accepted a valid drop-only decision
- hostile synthetic widening from retained `(60,64)` to pruned MIDI `67` was rejected
- validator executes the actual helper functions from source AST with MIDI `67` deliberately made extremely strong, positive, and playable; helper still excludes `67`
- validator executes the actual adapter preservation assertion and rejects widened candidate set, widened selected set, and non-empty recovery set
- validator asserts legacy recovery-shaped output literals are hard-false and the old permissive `midi not in precision_set and not recovered` escape hatch is absent
- result: **`V143 precision polyphony preservation validation: PASS`**

This validation is reference-free and uses no inference, GPU, Modal, paid service, scorer, optimizer, threshold sweep, deployment, or Production mutation.

## ACCEPTANCE INVARIANTS

Persisted-evidence target remains:
- **725** retained attacks
- **970** precision-v2 selected pitches input
- **967** rendered after legal voicing
- exactly **3** legal-voicing drops
- **0** recovered/pruned hypotheses re-admitted
- **0** primary preservation failures
- **0** unobserved pitches
- **0** unobserved attacks

The source-level preservation invariant is now closed. A final optional safe check is a CPU-only/read-only replay of the already-persisted artifact against the current helper to reconfirm the 970 -> 967 / 3-drop counts without any new inference. Do not trigger a workflow to do this.

## WORKFLOW-SAFETY CHECK

Checkpoint push `36fc6bda1247bedbd9642a50b07ca4d52fbadb25` produced exactly one GitHub Actions run: `.github/workflows/cleanup-tab-preview.yml` run `34080214025`; no model/scoring workflow ran. No workflow was manually triggered.

## AFTER THIS SLICE

After the persisted replay check (or if it cannot be performed read-only), move to the separate async-result lifetime defect: locate the real ~900-second control/result ownership TTL and patch only that actual boundary so it safely exceeds the 1200-second worker budget. Do not patch a guessed symbol. Do not deploy without explicit authorization.

## FRESH-CHAT SUCCESS CONDITION

**The helper/adapter must never change attack identity, the persisted primary, or admit any pruned/non-precision pitch. Persisted evidence should remain 725 attacks / 970 retained pitches / 967 rendered / 3 legal-voicing drops with zero recovered hypotheses and zero primary/unobserved violations.**
