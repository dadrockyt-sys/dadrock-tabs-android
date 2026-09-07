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

A CPU-only/read-only replay of the already-consumed persisted artifact showed the historical feasibility-recovery boundary was unsafe:
- baseline selected pitches: **970**
- baseline rendered: **967**
- broad feasibility-boundary rendered: **3485**
- recovered beyond precision-v2: **2518**
- affected attacks: **703 / 725**
- primary preservation failures: **0**
- unobserved pitches/attacks: **0 / 0**

Decision: **guitar feasibility/physical positivity alone must never re-admit precision-v2-pruned pitches.**

## CURRENT SCORE-STRUCTURE SLICE — EXACT REFRESHED STATE

Fresh branch refresh established these exact current blobs before the adapter patch:
- `analyzer/v143_precision_polyphony_boundary.py`: `83a1d993ff654c45bb965a7794f2d155aab18a25`
- `analyzer/v143_contextual_prune_precision_candidate_events.py`: `68732a07701a30a455ba9bcbf7c2adddd3930622`

Correction to the previous checkpoint: the current adapter **does match** the current helper function signature; there is no current signature `TypeError`.

Current helper behavior:
- precision-v2 retained pitch set is authoritative
- observed-but-pruned pitches remain provenance/diagnostic evidence only
- selected pitches are always a subset of the precision-v2 retained set
- primary is immutable
- helper `recovered_midis` is always empty and guarded by a runtime invariant
- legal joint-guitar-voicing may drop precision-selected secondaries only

Current adapter issue:
- behavior is currently safe because the helper returns no recovered pitches, but the adapter still carries recovery-era vocabulary and an invariant that would permit a non-precision MIDI if marked `feasibilityRecoveredSecondary`
- this is an unnecessary future escape hatch and must be removed
- retain legacy recovery-shaped output fields only for schema compatibility, with hard-false values; they must never authorize selection

Next safe patch:
1. change only `analyzer/v143_contextual_prune_precision_candidate_events.py`
2. require helper candidate MIDI set and selected MIDI set to remain subsets/equivalent to the persisted precision-v2 authority as appropriate
3. reject any non-empty helper `recovered_midis`
4. ensure every emitted event MIDI belongs to `precision.pitch_sets[key]` regardless of any marker
5. keep legacy feasibility-recovery fields false for compatibility
6. add deterministic validation that deliberately simulates a helper recovery attempt and proves the adapter rejects/ignores it
7. checkpoint again immediately after patch/validation
8. keep this isolated from the frozen live endpoint and Production

Acceptance invariants remain:
- **725** retained attacks
- **970** precision-v2 selected pitches input
- **967** rendered after legal voicing
- exactly **3** legal-voicing drops
- **0** recovered/pruned hypotheses re-admitted
- **0** primary preservation failures
- **0** unobserved pitches
- **0** unobserved attacks

## WORKFLOW-SAFETY CHECK

The prior checkpoint push (`36fc6bda1247bedbd9642a50b07ca4d52fbadb25`) produced exactly one GitHub Actions run: `.github/workflows/cleanup-tab-preview.yml` run `34080214025`; no model/scoring workflow ran. No workflow was manually triggered.

## AFTER THIS SLICE

Only after the score-structure adapter slice is closed, return to the separate async-result lifetime defect: locate the real ~900-second control/result ownership TTL and patch only that actual boundary so it safely exceeds the 1200-second worker budget. Do not patch a guessed symbol. Do not deploy without explicit authorization.

## FRESH-CHAT SUCCESS CONDITION

**The helper/adapter must never change attack identity, the persisted primary, or admit any pruned/non-precision pitch. Deterministic validation must preserve 725 attacks / 970 retained pitches / 967 rendered / 3 legal-voicing drops with zero recovered hypotheses and zero primary/unobserved violations.**
