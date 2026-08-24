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
- Retired scored render-event identity is confirmed from committed preholdout proof as `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`, with `725` selected/unique onsets expanded to `985` rendered notes across `113` measures and PDF fidelity `1.0`.

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

## Direct source-level timing handoff defect — PROVEN
`build_precision_candidate_assembly()` explicitly preserves two separate timing facts before downstream semantics:
- `grid_time = grid[key]`
- `physical_onset = row.get("onsetTime") or grid_time`
- source/event row gets `timeSeconds=grid_time` and `onsetTime=physical_onset`.

The old `_promote_candidate_sustain()` then overwrote `onsetTime` with `timeSeconds` while claiming `rhythmSustain.attackTimingChanged=False`.

Cheap proof:
- checker `analyzer/check_v143_precision_sustain_onset_handoff.py` initially added in commit `45b260a60afa82ec8c5f6c02a7104df9a2ffd28c`.
- workflow `.github/workflows/v143-precision-sustain-onset-handoff-static-proof.yml` initially added in commit `885e1154af9e08f9e38dfcb6da14132383e654e0`.
- committed schema-v1 diagnostic proved `assemblySeparatesPhysicalFromGrid=true`, `promotionOverwritesPhysicalOnset=true`, `promotionClaimsAttackTimingChangedFalse=true`, with a synthetic `10.083s` physical attack overwritten to grid `10.000s` (`-0.083s` loss).
- protected pipeline remained exact blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- no Modal/GPU or professional reference/scorer used.

## Candidate-only correction — STATIC/SYNTHETIC PROOF PASSED
- Added pure CPU helper `analyzer/v143_precision_sustain_promotion.py` in commit `89143dc7382b200af449b607d1fbd294ba6916fd`.
- Updated `analyzer/v143_repaired_timing_precision_candidate_product_modal.py` in commit `c72ed6ff569e402f8761dbe1be5ea802c8e68059` to bundle the helper and delegate `_promote_candidate_sustain()` to it.
- Updated static/synthetic checker in commit `2e488187fd53414090efdf0c47d39fa1cca72229`.
- Updated workflow enforcement in commit `38c4cc9b56bf3cd9356b2456837555c1cbd3d0cf`.

Corrected timing contract:
- `timeSeconds` remains the quantized tab-grid identity.
- `start = timeSeconds` remains the quantized presentation start.
- `onsetTime` now preserves the physical detected attack from candidate assembly; it is no longer overwritten by sustain promotion.
- `end`, `duration`, and `offsetTime` remain grid-start-plus-sustain-duration because the current sustain consensus itself is grid-anchored.
- `rhythmSustain` now explicitly serializes `physicalOnsetPreserved=true`, `analysisTimingBasis=quantized-timeSeconds`, `presentationStartBasis=quantized-timeSeconds`, and `offsetTimingBasis=quantized-timeSeconds-plus-durationSeconds`.
- `physicalOnsetDeltaFromGridSeconds` is serialized directly from the two preserved timing facts; no timing is invented.
- `attackTimingChanged=false` is now truthful: promotion preserves the incoming physical attack while retaining the separate grid start.

The Actions-generated schema-v2 diagnostic has been observed and passes:
- `schemaVersion=2`, `passed=true`, `defectPresent=false`, `correctionProven=true`.
- assembly separation true; product delegates to pure promotion helper; helper is bundled into candidate image.
- synthetic event count `2 → 2` unchanged.
- `(measure,step)`, MIDI, string, fret, and `timeSeconds` identity unchanged.
- physical `onsetTime` preserved exactly; quantized grid start preserved.
- duration contract consistent; residual metadata truthful; sustain timing metadata truthful; no invented attack/pitch.
- positive residual example `+0.08300000000000018s`; negative residual example `-0.02800000000000047s`.
- protected pipeline exact blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`, unchanged.
- `professionalReferenceUsed=false`, `runtimeLabelsRequired=false`, `productionModified=false`, `modalGpuUsed=false`.

## Sustain semantics note
`v143_rhythm_sustain_consensus_shadow.py` still intentionally analyzes sustain from `timeSeconds` through `_event_time()`, so the promoted absolute sustain endpoint remains grid-derived. This correction does not silently change sustain inference; it only preserves the independent physical attack provenance and makes timing bases explicit.

## Downstream render/freeze audit — IMPORTANT SCORING BOUNDARY
Inspected:
- `.github/workflows/v143-repaired-timing-precision-candidate-product.yml`
- `.github/workflows/v143-repaired-timing-precision-product-proof.yml`
- `.github/workflows/v143-repaired-timing-precision-final-preholdout.yml`
- `validation/rhythm_holdout/prepare_repaired_timing_precision_candidate_freeze_payload.mjs`
- `validation/rhythm_holdout/prepare_precision_candidate_freeze_payload.mjs`
- `lib/jimmyPaigeAnalysisPayload.js`
- `lib/v143RenderContract.js`
- `validation/rhythm_holdout/freeze_rhythm_analysis.py`
- `validation/rhythm_holdout/canonical.py`
- `analyzer/v143_rhythm_output_adapter.py`

Findings:
- `render_rhythm_tab()` uses authenticated grid placement/pitch-position fields and technique markers; it does not use physical onset seconds.
- `buildJimmyPaigeAnalysisPayload()` creates structured `renderEvents` through `projectV143RenderEvents(rawEvents)`.
- `projectV143RenderEvents()` intentionally projects `eventIndex`, `measure`, `step`, `stringIndex`, `fret`, `midi`, sustain duration/tier, and techniques. It does **not** serialize `timeSeconds`, `start`, `onsetTime`, `end`, `offsetTime`, or physical-onset residual.
- freeze preparation writes only `structured.renderEvents`; `freeze_rhythm_analysis.py` freezes exactly those events; `canonical.py` likewise has no physical-onset-seconds field.
- Therefore preserving physical `onsetTime` is a valid provenance/correctness fix in the raw candidate JSON, but **by itself it cannot change the frozen/PDF/scored event stream**.
- Because the correction deliberately leaves `(measure,step)`, pitch-position, sustain, and event count unchanged, a new inference based only on this fix would be expected to reproduce retired frozen render-event SHA `a81190…`, not create a legitimate new scoring identity. **Do not spend Modal/GPU or open the holdout for this correction alone.**

Cheap projection proof:
- Added `validation/rhythm_holdout/check_v143_precision_dual_timing_projection.mjs` in commit `37164fcabaf03fe3a900eb0e29a81143ac623722`.
- It proves raw JSON preserves distinct physical onset/residual while mutations to physical onset alone leave `projectV143RenderEvents()` byte-structurally unchanged, and confirms physical timing fields are absent from the scored/render projection.
- Extended `.github/workflows/v143-repaired-timing-precision-product-proof.yml` in commit `e3264e90a79c3f5412df6894f20973a6ae723613` to run both the corrected onset-handoff checker and render-projection checker before any expensive candidate path, with protected-runtime and anti-leakage gates.
- Product-proof workflow is CPU-only/read-only; no Modal/GPU or professional reference use.

## Workflow safety drift to resolve before future holdout
- `v143-repaired-timing-precision-final-preholdout.yml` is still pinned to old candidate blob `20e7a583...` / result commit `289a04e...` and uses the generic `prepare_precision_candidate_freeze_payload.mjs` instead of the repaired-timing-specific preparation script.
- Its local `retired` set currently lists older identities `c621...` and `e693...` but not the now-scored retired `a81190...` identity.
- Do not dispatch this old final-preholdout workflow as-is. Before any future freeze path, make the retired `a81190...` identity fail closed and bind a genuinely new candidate only after a correction changes scored grid/pitch identity.

## Existing diagnostic files from earlier audit
- `analyzer/check_v143_candidate_physical_grid_fidelity.py` commit `013053025984172752af46ef2d10112dd22aec1f` and workflow commit `13ba13453424ce861c96d02d0c4c483817a74c6c` exist, but their first result is schema-limited as described above. Do not use its zero top-level residual as evidence of physical timing accuracy.

## Cost control
- No Modal/GPU inference in this continuation yet.
- Do not rerun old candidate/freeze/scorer.
- Do **not** run a new GPU candidate for physical-onset preservation alone because it cannot change the scored render-event identity.
- Current work is source/static/synthetic/CPU-only.

## Next exact actions
1. Verify the updated CPU-only product-proof workflow is green after commit `e3264e90...`.
2. Fail-close future preholdout/holdout paths against retired scored event SHA `a81190...`; do not dispatch any old workflow while doing this.
3. Continue audio-only source audit for a correction that can actually change scored `measure/step` and/or MIDI/string/fret identity without using professional reference.
4. Prioritize a cheap structural audit of precision polyphonic expansion: old candidate has `725` selected attacks but `985` rendered notes (`236` multi-note onsets, max chord size `6`) while pitch-content F1 was only `0.237`; determine whether secondary-tone expansion has an audio-only over-expansion defect before any GPU run.
5. Only after a proven scoring-relevant correction exists, create a brand-new approved-audio candidate identity/path; freeze/PDF/lock it immutably and only then permit one professional score.
