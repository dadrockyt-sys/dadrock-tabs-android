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

## Current subdivision/attack-grid audit — NEW HIGH-PRIORITY FINDING TO QUANTIFY
Static source inspection found a potentially more direct timing handoff defect:
- carrier admission originally accepts Basic Pitch physical onsets only when `nearest_timing_slot(...)` is within `WIDE_GRID_TOLERANCE_SECONDS=0.30` of the global grid.
- precision selection has its own `_best_rows_by_slot` implementation.
- `build_precision_candidate_assembly()` later imports a different `_best_rows_by_slot` from `v143_contextual_prune_candidate_events.py` and recomputes the physical row for each retained `(measure, step)` key instead of preserving the exact row selected by precision.
- both helpers constrain row mapping to slots inside the row's current **measure**, and the assembly helper has no hard grid-error ceiling.
- therefore a retained key can potentially be reattached to a physically distant row during assembly.
- sample from committed old candidate product appears alarming: one source row has measure 1 / step 3 / `timeSeconds≈0.6966` but `onsetTime≈1.60088`, residual ≈`0.9043s`; another row is normal at ≈`0.038s`. This is not yet generalized until full residual distribution is measured.

## Physical-grid fidelity diagnostic staged — CPU/STATIC ONLY
- Added `analyzer/check_v143_candidate_physical_grid_fidelity.py` commit `013053025984172752af46ef2d10112dd22aec1f`.
  - reads the already-committed candidate product only; no audio inference.
  - computes source-row and event `onsetTime - timeSeconds` residual p50/p90/p95/p99/max, fractions within 30/60/100/150/300/500ms, counts >300ms and >500ms, worst rows, duplicate `(measure,step)` source keys, event/source key and onset/grid consistency.
  - diagnostic only; no arbitrary acceptance threshold, no runtime mutation.
- Added `.github/workflows/v143-candidate-physical-grid-fidelity.yml` commit `13ba13453424ce861c96d02d0c4c483817a74c6c`.
  - CPU/stdlib only, reads existing `debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json`.
  - protected-blob + anti-reference gates.
  - writes `debug/v143-contextual-prune/repaired-timing-precision-candidate-physical-grid-fidelity.json` and commits it.
  - no Modal/GPU, scorer, runtime, or Production change.

## Cost control
- No Modal/GPU inference in this continuation.
- Do not rerun old candidate/freeze/scorer.
- Inspect only the new CPU diagnostic result before code changes.

## Next exact actions
1. Read `repaired-timing-precision-candidate-physical-grid-fidelity.json` when committed.
2. If many source rows exceed the original 300ms physical-grid admission tolerance, treat this as a general reference-free candidate-assembly handoff defect.
3. Trace/compare the two `_best_rows_by_slot` implementations and design a correction that preserves the exact physical row identity selected by precision instead of recomputing it downstream.
4. Prove the correction with synthetic/static invariants first: no invented attack/pitch, retained key unchanged, explicit primary preserved, physical-grid residual remains tied to the selected carrier row.
5. Only then consider one new low-cost inference. Any accepted correction still needs a brand-new candidate/freeze/PDF/lock before one new professional score.
