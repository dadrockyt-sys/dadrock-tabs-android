# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; do not modify/merge `main` or change live Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional human reference is scorer-only. Runtime/shadows may never read/train/tune/select from it.
- Retired scored freeze event SHA `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb` must never be rescored.
- Any accepted correction requires a completely new approved-audio candidate → immutable freeze/PDF → lock → one professional score.
- Completion remains score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is not complete.**

## Last proven candidate/freeze + failed holdout
- Combined repaired timing + precision: 449 repaired beats, 0 interval outliers, 113 measures / 1796 slots, all measures populated, explicit primary complete.
- Exact 2-pass proof run `32697939613` passed. Old candidate/freeze must not be rerun/rescored.
- One-shot professional run `32731885778` failed broadly: coverage recall `1.0`, pitch-content F1 `0.23718280683583634`, pitch+timing F1 `0.033143448990160536`, critical mismatches `1723`.
- Allowed diagnosis only: coverage solved; timing/grid identity and pitch identity fundamentally wrong. Scorer/reference closed again.

## Bar-phase / raw-index timing investigation — CLOSED FOR NOW
- Beat repair can invalidate inherited raw modulo-4 phase in principle, proven synthetically.
- Approved global/local audio-only phase diagnostics do not support a safe global or raw-index-derived phase correction.
- Local phase evidence changes through the audio while repaired intervals are clean; raw↔repaired index offsets do not track those local musical phase changes one-for-one.
- Decision: **do not mutate global bar phase or derive musical phase from raw beat-list offset**.

## Subdivision / event-timing audit — CORRECTED FINDING
The previous hypothesis that precision and assembly choose different physical rows has been **retracted** after source comparison:
- `v143_contextual_prune_precision_shadow.py::_best_rows_by_slot` and `v143_contextual_prune_candidate_events.py::_best_rows_by_slot` are semantically identical: same per-measure nearest-slot selection, same pitch evidence, same strength formula, same strict `>` replacement/tie behavior. Different private diagnostic field names do not change selection.
- Therefore do **not** claim assembly reattaches retained keys because of helper-formula divergence.

The first physical-grid diagnostic also had the wrong product-schema assumption:
- old product contains no top-level `sourceRows`, so its `sourceRows.rowCount=0` result is not a physical-provenance measurement.
- all 985 serialized top-level events have `onsetTime == timeSeconds`, so the diagnostic trivially reports zero residual there. This does **not** prove the detected physical onset was on the grid.

### New direct source-level timing handoff defect
`build_precision_candidate_assembly()` explicitly preserves two separate timing facts before downstream semantics:
- `grid_time = grid[key]`
- `physical_onset = row.get("onsetTime") or grid_time`
- source/event row gets `timeSeconds=grid_time` and `onsetTime=physical_onset`.

But `analyzer/v143_repaired_timing_precision_candidate_product_modal.py::_promote_candidate_sustain()` later does:
- `start = event["timeSeconds"]`
- writes `rhythmSustain.attackTimingChanged = False`
- then overwrites `event["onsetTime"] = start`
- and `event["offsetTime"] = start + duration_seconds`.
Thus any distinct physical onset provenance is erased and replaced by the quantized grid time while the same promoted sustain metadata asserts attack timing was not changed.

This also explains why the committed old product cannot be used to recover physical onset residuals after the fact: the physical `onsetTime` exists in the immediate candidate assembly but is not serialized separately, and the promoted product overwrites it before output.

`v143_rhythm_sustain_consensus_shadow.py` additionally uses `timeSeconds` (not physical `onsetTime`) as its sustain-analysis onset, so the sustain stage itself is grid-anchored. That may be intentional for quantized sustain, but it makes preserving the separate physical onset provenance even more important.

## Cheap static proof added — 2026-08-24 continuation
- Added `analyzer/check_v143_precision_sustain_onset_handoff.py` in commit `45b260a60afa82ec8c5f6c02a7104df9a2ffd28c`.
- Added `.github/workflows/v143-precision-sustain-onset-handoff-static-proof.yml` in commit `885e1154af9e08f9e38dfcb6da14132383e654e0`.
- Checker is stdlib/AST-only plus `git hash-object`; it does **not** import/run Modal or inference code.
- It proves from source structure that assembly keeps quantized `timeSeconds` and distinct physical `onsetTime`, then current sustain promotion replaces `onsetTime` with grid-derived `start` while claiming `attackTimingChanged=False`.
- It includes a synthetic nonzero physical-vs-grid residual to make the destructive handoff explicit and enforces the protected pipeline blob.
- Workflow is CPU-only and writes a diagnostic JSON/log. No Modal/GPU inference and no professional reference/scorer access.
- At this checkpoint the workflow result has not yet been inspected; do not claim the static proof has passed CI until its run is verified.

## Existing diagnostic files from earlier audit
- `analyzer/check_v143_candidate_physical_grid_fidelity.py` commit `013053025984172752af46ef2d10112dd22aec1f` and workflow commit `13ba13453424ce861c96d02d0c4c483817a74c6c` exist, but their first result is schema-limited as described above. Do not use its zero top-level residual as evidence of physical timing accuracy.

## Cost control
- No Modal/GPU inference in this continuation yet.
- Do not rerun old candidate/freeze/scorer.
- Prove the onset-provenance overwrite statically/synthetically before changing candidate runtime behavior.

## Next exact actions
1. Verify the new cheap static-proof workflow run and inspect its diagnostic; protected pipeline must remain unchanged.
2. If proof passes, correct `_promote_candidate_sustain()` so quantized `timeSeconds/start` remains the tab-grid identity while physical `onsetTime` survives promotion and serialization.
3. Decide offset/duration semantics carefully so `durationSeconds` stays internally consistent and no attack/pitch/event identity changes occur.
4. Add synthetic post-fix invariants: same `(measure,step)`, same MIDI/string/fret, same `timeSeconds`, same event count, physical `onsetTime` preserved, no invented timing, and promoted sustain truthfully reports whether attack timing changed.
5. Only after static post-fix proof consider one new low-cost approved-audio candidate inference with a brand-new identity; never modify/rescore the retired freeze.
