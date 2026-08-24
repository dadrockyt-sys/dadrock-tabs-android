# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 America/Thunder_Bay
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; do not modify/merge `main` or change live Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional human reference is scorer-only. Runtime/shadows may never read/train/tune/select from it.
- Retired scored freeze event SHA `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb` must never be rerun/rescored.
- Any accepted correction requires a completely new approved-audio candidate → immutable freeze/PDF → lock → one professional score.
- Completion remains score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is not complete.**

## Last scored candidate / holdout result
- Combined repaired timing + precision: 449 repaired beats, 0 interval outliers, 113 measures / 1796 slots, all measures populated, explicit primary complete.
- Exact 2-pass proof run `32697939613` passed. Old candidate/freeze must not be rerun/rescored.
- One-shot professional run `32731885778` failed broadly: coverage recall `1.0`, pitch-content F1 `0.23718280683583634`, pitch+timing F1 `0.033143448990160536`, critical mismatches `1723`.
- Allowed diagnosis only: coverage solved; timing/grid identity and pitch identity fundamentally wrong. Scorer/reference closed again.
- Retired scored render-event identity `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`: 725 selected/unique attacks → 985 rendered notes, 236 multi-note onsets, max chord size 6, 113 measures, PDF-event fidelity 1.0.

## Closed timing hypotheses
- Do not mutate global bar phase or derive musical phase from raw beat-list offset. Audio-only global/local phase diagnostics did not support that correction.
- Earlier claim that precision and assembly choose different physical rows was retracted: their `_best_rows_by_slot` behavior is semantically identical.
- Old physical-grid diagnostic cannot recover physical onset from the old serialized product because sustain promotion had already overwritten it.

## Physical-onset handoff defect — proven and corrected candidate-only
Source-level defect was proven:
- candidate assembly stores `timeSeconds=grid_time` and `onsetTime=physical_onset`;
- old sustain promotion then replaced `onsetTime` with quantized `timeSeconds/start` while claiming `attackTimingChanged=False`.

Cheap initial proof:
- `analyzer/check_v143_precision_sustain_onset_handoff.py` initial commit `45b260a60afa82ec8c5f6c02a7104df9a2ffd28c`.
- `.github/workflows/v143-precision-sustain-onset-handoff-static-proof.yml` initial commit `885e1154af9e08f9e38dfcb6da14132383e654e0`.
- schema-v1 diagnostic proved a synthetic `10.083s` physical attack became grid `10.000s` (`-0.083s` provenance loss), protected pipeline unchanged, no Modal/GPU/reference.

Correction:
- pure helper `analyzer/v143_precision_sustain_promotion.py`, commit `89143dc7382b200af449b607d1fbd294ba6916fd`.
- product update `analyzer/v143_repaired_timing_precision_candidate_product_modal.py`, commit `c72ed6ff569e402f8761dbe1be5ea802c8e68059`.
- corrected checker commit `2e488187fd53414090efdf0c47d39fa1cca72229`.
- corrected workflow commit `38c4cc9b56bf3cd9356b2456837555c1cbd3d0cf`.

Corrected contract:
- `timeSeconds` and `start` remain quantized grid identity/presentation.
- physical `onsetTime` survives unchanged.
- `end`, `duration`, `offsetTime` remain grid-start + sustain duration because sustain consensus itself is still grid-anchored.
- `physicalOnsetDeltaFromGridSeconds = onsetTime - timeSeconds` is serialized.
- `rhythmSustain` explicitly records physical onset preservation and timing bases.

Actions-generated schema-v2 proof PASSED:
- `passed=true`, `defectPresent=false`, `correctionProven=true`.
- synthetic event count 2→2; `(measure,step)`, MIDI, string, fret, `timeSeconds` unchanged; physical onset preserved; duration/residual contracts truthful; no invented attack/pitch.
- example residuals `+0.08300000000000018s` and `-0.02800000000000047s`.
- protected pipeline exact expected blob; no Modal/GPU/reference/Production.

## Downstream scoring boundary — important
Audited render/freeze/PDF path:
- `analyzer/v143_rhythm_output_adapter.py`
- `lib/jimmyPaigeAnalysisPayload.js`
- `lib/v143RenderContract.js`
- repaired/generic freeze payload scripts
- `freeze_rhythm_analysis.py`, `canonical.py`
- repaired candidate/product-proof/final-preholdout workflows.

Finding:
- scored/render `renderEvents` project grid/pitch identity (`measure`, `step`, string/fret/MIDI, sustain/tier, techniques) but do **not** carry physical `onsetTime`, `timeSeconds`, `start/end/offsetTime`, or physical residual.
- Therefore physical-onset preservation is a valid provenance fix but cannot by itself change the frozen/PDF/scored identity.
- Do **not** spend Modal/GPU or reopen holdout for that fix alone; it would be expected to recreate retired event SHA `a81190...`.

Cheap projection proof:
- `validation/rhythm_holdout/check_v143_precision_dual_timing_projection.mjs`, commit `37164fcabaf03fe3a900eb0e29a81143ac623722`.
- proves raw JSON preserves physical onset while physical-only mutations leave `projectV143RenderEvents()` unchanged.
- product-proof workflow extended in commit `e3264e90a79c3f5412df6894f20973a6ae723613` to run onset + projection CPU-only gates.
- GitHub combined status on `e326...` exposed no individual checks (`statuses=[]`), so do **not** claim this updated product-proof workflow itself is observed green. The dedicated onset workflow schema-v2 result is observed green.

## Holdout workflow safety drift
- `.github/workflows/v143-repaired-timing-precision-final-preholdout.yml` is stale: pinned to old candidate blob/result commit and uses generic precision freeze prep.
- its local retired set contains older identities but not now-scored retired `a81190...`.
- **Do not dispatch it as-is.** Future freeze/holdout path must fail closed on `a81190...` and bind a genuinely new scoring-relevant candidate.

## Precision polyphonic-expansion audit — current work
Source audit findings so far:
- `v143_contextual_prune_reference_free_carrier.py` forms per-pitch Basic Pitch clusters, then groups pitches whose cluster onsets are within `30 ms` into one physical onset group.
- `v143_contextual_prune_precision_shadow.py::_precision_pitch_set()` only keeps candidate MIDIs physically observed in that same onset group and requires positive two-view CQT attack/body evidence. Secondary tones require strong relative evidence (`0.80` non-harmonic; `0.92` harmonic-above-primary).
- `v143_contextual_prune_precision_candidate_events.py` does not invent a new pitch; it renders selected supported MIDIs only when the set has a legal joint guitar voicing.
- Therefore it is **not justified** to assume all 260 secondary rendered notes are erroneous merely from the failed holdout.

Narrowed structural risk:
- onset-group carrier stores only group-level `stemSupportMax`, `sweepSupportMax`, and `detectionCountSum`.
- candidate assembly copies those same group-level support values into every per-MIDI `pitchHypotheses` item. Thus serialized Basic Pitch support provenance is not truly per-pitch and may be indistinguishable among pitches even when original cluster support differed.
- Precision secondary selection itself currently uses per-MIDI two-view CQT evidence, so this provenance issue is not yet proven to cause wrong scored notes. It must be measured before changing runtime behavior.

Cheap committed-product audit added, with **no inference/scorer**:
- `analyzer/check_v143_precision_polyphonic_expansion.py`, commit `3f5874ce3ce2b569eed1f0dd958afc4e2c91bf32`.
- `.github/workflows/v143-precision-polyphonic-expansion-audit.yml`, commit `241234a7a25de06df12b6c98e649b84884a10732`.
- checker reads the already committed repaired-timing precision candidate product only; computes exact attack/chord expansion counts, harmonic-vs-nonharmonic secondary intervals, secondary CQT score/attack/body ratio distributions, and how often serialized per-pitch Basic Pitch support is indistinguishable.
- workflow is CPU-only, writes diagnostic JSON/log, enforces protected pipeline hash, no reference, no Modal/GPU, no Production.
- At this checkpoint the new diagnostic file has not appeared yet (`404` on first check). **Do not claim audit results until Actions commits the JSON.**

## Cost control
- No Modal/GPU inference in this continuation.
- No professional scorer/reference opened.
- Do not rerun old candidate/freeze/scorer.
- Do not run new GPU candidate until a source/audio-only correction is proven capable of changing scored grid/pitch identity.

## Next exact actions
1. Wait only by re-checking current branch (no background promise) for `debug/v143-contextual-prune/precision-polyphonic-expansion-audit.json`; inspect it when Actions commits it.
2. Use that audio-only diagnostic to decide whether secondary expansion has a defensible structural correction. Do not threshold-tune against professional reference.
3. In parallel, locate the actual future holdout/scorer workflow(s) and add fail-closed retired identity `a81190...` before any future dispatch.
4. If per-pitch support provenance is needed for a correction, preserve per-pitch cluster `stemSupport/sweepSupport/detectionCount` in carrier onset groups rather than reusing group maxima; prove with synthetic/static tests before inference.
5. Only after a scoring-relevant correction is proven, create a brand-new approved-audio candidate identity/path → immutable freeze/PDF → lock → exactly one professional score.
