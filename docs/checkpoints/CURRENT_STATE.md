# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-06 America/Toronto
Branch: `v143-contextual-prune-lobo`

This file is intentionally compact for fresh-chat continuation. Full prior detail remains in Git history, including the immediately previous checkpoint and the earlier lineage it references.

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

Consumed professional holdout:
- run `34048719525`
- `near100ProfessionalGatePassed = false`
- pitch-content F1 `0.30892570817744525`
- pitch-timing tolerant F1 `0.05879208979155532`
- chord pitch-set tolerant F1 `0.004136504653567736`
- unmatched generated notes `779`
- unmatched reference notes `800`

Interpretation remains unchanged: infrastructure/rendering succeeded; musical score construction did not. Do not tune against the professional reference.

## CURRENT SCORE-STRUCTURE SLICE

The exact live/frozen path is separate from the isolated precision candidate. Do **not** wire the precision candidate into the live endpoint by assumption.

Recent deterministic precision-path repair exists:
- `analyzer/v143_precision_polyphony_boundary.py`
  - blob `720a068d71ad72719053cdc89bdab81db541c884`
- `analyzer/v143_contextual_prune_precision_candidate_events.py`
  - blob `68732a07701a30a455ba9bcbf7c2adddd3930622`
- fail-closed pre-export validator and sustain integration are already committed.

The new polyphony boundary preserves the precision primary, prioritizes already-retained secondaries, and may recover only same-attack observed MIDI values with positive two-view physical evidence when the full set remains a legal joint guitar voicing. It blocks the protected promoted-harmonic contradiction and cannot add/relocate attacks or invent unobserved pitches.

**Open risk:** this helper may recover too many hypotheses that precision-v2 intentionally pruned. Guitar feasibility alone is not musical evidence. The next step is therefore a CPU-only replay against persisted paid precision evidence before keeping/changing the helper.

## PERSISTED PAID PRECISION EVIDENCE — SOURCE OF TRUTH

Successful authorized paid precision capture:
- workflow run `32805316807`
- capture/replay commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`
- approved fixture SHA-256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`
- no further paid capture is authorized.

Persisted baseline facts:
- full audio-derived range: measures 1–113
- precision-v2 retained attacks: **725**
- precision-v2 selected pitches: **970**
- rendered before later guard convenience layer: **967**
- historical event-layer replay after guard: **965**
- all 113 measures populated
- exact deterministic replay mismatch counts were zero
- no unobserved attack/pitch creation
- professional reference not used

Historical checkpoint also recorded retained-attack replay evidence with **6525 original pitch hypotheses** across the 725 retained attacks and exact live/replay selected-pitch SHA match.

Commit `c1451df...` additionally contains schema-2 replay-validation material. During this chat, inspecting the commit showed `debug/v143-contextual-prune/precision-v2-replay-artifact-validation.json` with retainedAttackCount 725, storedSelectedPitchCount 970, renderedPitchCount 967, voicingDroppedPitchCount 3, referenceFree true, and newInferenceUsed false. It also showed `precision-v2-replay-policy-compare.json`.

## CONNECTOR / FILE-LOOKUP QUIRKS OBSERVED

Do not infer evidence is absent from a failed convenience fetch.

Observed in this chat:
- direct branch fetch of `debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json` returned empty decoded content but the known blob SHA `7e6002cd4d42f355685241e0576c78940056f093`.
- direct branch/historical fetch attempts for the older convenience names `replay-validation-a.json` / `replay-validation-b.json` returned 404.
- direct branch fetch of `.github/workflows/v143-replay-precision-candidate.yml` also returned 404.
- the historical commit itself is valid and exposed newer exact replay filenames such as `precision-v2-replay-artifact-validation.json` and `precision-v2-replay-policy-compare.json`.

Therefore, in the fresh chat, inspect the historical commit/tree/file list for the exact persisted replay filenames rather than relying on stale convenience names. Prefer Git-persisted evidence. Read-only inspection of already-consumed Actions evidence is acceptable only if needed to recover the exact persisted payload; do not trigger a workflow.

## IN-PROGRESS CPU-ONLY PRECISION REPLAY RECOVERY

Checkpointed 2026-09-06 during deterministic continuation.

Recovered from historical capture commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527` without rerunning anything:
- exact committed evidence files are `precision-v2-capture-lock.json`, `precision-v2-replay-artifact-validation.json`, `precision-v2-replay-policy-compare.json`, and `repaired-timing-precision-candidate-product.json` under `debug/v143-contextual-prune/`
- schema-2 binding confirms **725 retained attacks**, **970 stored selected pitches**, **967 rendered pitches**, **3 voicing drops**, `referenceFree=true`, `newInferenceUsed=false`, and `failSafeAttackCount=0`
- all-input replay had **984** input/eligible attacks and **7535** original pitch hypotheses; the retained-only historical checkpoint separately records **6525** original pitch hypotheses across the retained 725
- historical candidate Git blob is `7e6002cd4d42f355685241e0576c78940056f093`; connector convenience decoding is empty because the payload is oversized, so that empty convenience response must not be treated as absent evidence

No model, GPU, Modal, professional scorer, workflow rerun, optimizer, production mutation, or deployment action was used for this recovery.

Next deterministic recovery:
1. read the current helper sources by path and verify the expected blobs
2. inspect/download the already-consumed run `32805316807` artifact read-only for the exact per-attack payload if needed
3. replay only `resolve_precision_polyphony(...)` against the persisted 725 retained attacks
4. checkpoint immediately after the result, before changing the helper or candidate assembly

## EXACT NEXT STEPS FOR FRESH CHAT

1. Stay on branch `v143-contextual-prune-lobo` and preserve all budget restrictions above.
2. Open commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527` and enumerate the exact precision replay/evidence files committed there, especially the schema-2 replay artifact/evidence and CPU-only replay/validation script or workflow equivalents.
3. Recover the persisted per-retained-attack data needed for replay: `(measure, step)`, original observed pitch set, precision-v2 retained pitch set, explicit primary MIDI, and the two-view physical evidence/carrier information required by `_pitch_evidence`.
4. Reproduce **only** the new `resolve_precision_polyphony(...)` feasibility-recovery behavior against those 725 retained attacks. No Basic Pitch inference, no Modal, no model, no GPU, no scorer, no optimizer, no professional reference.
5. Compare against the baseline 725 attacks / 970 selected pitches (967 rendered; 965 historical post-guard event layer).
6. Record structural deltas only:
   - retained attack identity changed? (must be no)
   - original observed hypothesis count
   - baseline selected pitch count
   - recovered pitch count
   - attacks affected by recovery
   - total selected/rendered note count
   - legal-voicing drops/rejections
   - max chord size
   - primary preservation failures (must be zero)
   - unobserved pitch count (must be zero)
   - unobserved attack count (must be zero)
   - protected promoted-harmonic violations (must be zero)
7. **Checkpoint `docs/checkpoints/CURRENT_STATE.md` immediately after obtaining that CPU-only replay result, before changing the helper or candidate assembly.**
8. Decision rule: if feasibility recovery materially inflates the precision product, do not keep it merely because it is legal/playable. Restrict or remove the recovery behavior using deterministic source-evidence invariants only. Do not tune to the consumed professional score.
9. If the replay is structurally conservative, keep the helper isolated and continue deterministic validation. Still do not integrate it into the live endpoint/Production without a separate explicit product/integration authorization.
10. Only after this score-structure slice is closed, return to the separate async-result lifetime defect: locate the real ~900-second control/result ownership TTL and patch only that boundary so it safely exceeds the 1200-second worker budget. Do not patch a guessed symbol.

## FRESH-CHAT SUCCESS CONDITION

Answer, deterministically and reference-free:

**Does the new feasibility-recovery boundary safely preserve the persisted precision candidate, or does it over-recover precision-v2-pruned hypotheses?**

No new paid/model/professional evaluation budget may be consumed to answer it.
