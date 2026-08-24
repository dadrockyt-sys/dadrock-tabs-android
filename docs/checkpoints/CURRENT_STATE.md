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

## General timing defect remains real, but simple phase correction rejected
Beat-grid repair rebuilds a clean pulse train after malformed raw beat intervals but blindly inherits raw modulo-4 phase. Synthetic proof confirms that can become stale after inserted/sub-beat/duplicate pulses. However, approved-audio evidence does **not** support a simple global or raw-index-derived rephase.

## Global + local phase diagnostics
- Global post-repair CPU run `32736686527`: preferred phase 2 with 5/7 votes / weighted fraction `0.6784292`, but first half strongly/stably phase 1 and second half strongly/stably phase 2. Global replacement rejected.
- Local phase CPU run `32737275715`: 26 windows, strong phase counts phase1=12, phase3=2, phase2=1. Strong phase1 run repaired indices 32→272; ambiguous region ~224→304; strong phase3 run 304→384; one later strong phase2 window 368→432. Runtime untouched.

## Raw↔repaired index alignment — GREEN / INTERPRETATION COMPLETE
Enhanced CPU run `32737637171`, trigger `6ce76949057eaae6a10ed160de061e984db7f023`:
- static `success`, approved `success`, protected exact, reference-free, runtime/live/Production unchanged.
- 323/449 repaired beats matched raw beats within 0.25 period (`0.7193764`), median absolute residual `0.0s`, mean `0.007584s`.
- raw-minus-repaired index modulo changes at repaired indices approximately 111, 149, 227, 230, 271, 344, 368, 378, 392, 419, 435.
- early raw/repaired offset runs cycle 0→1→2→3→0→1 while the independent local audio phase remains strongly/stably **phase 1 continuously from repaired indices 32→272**.
- therefore raw/repaired modulo-offset changes do **not** map one-for-one to musical bar phase. Raw tracker index drift proves inherited raw phase lacks provenance, but it cannot itself be used to derive a corrected musical phase.
- the later strong phase1→phase3 change begins around local window start 304, while the next raw/repaired offset change is much later at 344; this does not support repair-index drift as the cause of that phase transition.
- the later phase3→phase2 evidence overlaps an index-offset change at 368, but this isolated coincidence is insufficient given the many earlier offset changes with no corresponding musical-phase change.

### Timing decision
**Do not mutate runtime bar phase globally or by raw-index offset.** The generic evidence says the audio contains changing/ambiguous local bar-accent structure, while the repaired pulse train itself has zero interval outliers. Any phase correction derived solely from raw beat-list index provenance would be unsafe.

Timing audit can now move from bar-phase hypothesis to **subdivision/attack-grid self-consistency**: verify that retained physical onsets are assigned to appropriate 16th slots and that grid residuals / quantization behavior remain coherent through repaired regions. This stays reference-free and can use existing candidate/carrier diagnostics before any new inference.

## Cost control
- No Modal/GPU inference in this continuation.
- Do not rerun old candidate/freeze/scorer.
- Prefer existing committed candidate/event diagnostics and static source inspection for subdivision/attack audit.

## Next exact actions
1. Inspect current candidate product/event payload for `onsetTime` vs `timeSeconds` / measure-step assignments and residual distributions, especially around repaired-index anomaly regions.
2. Trace `build_subdivision_grid` + `nearest_timing_slot` + candidate assembly to rule out a 16th-grid serialization/quantization defect independent of bar phase.
3. If subdivision timing is internally coherent, close timing changes for now and resume independent pitch-carrier audit.
4. Pitch audit should quantify the effect of taking the minimum across deterministic guitar views and harmonic/fundamental selection using only audio/carrier evidence; no correction accepted yet.
5. Any accepted runtime-affecting correction still requires a brand-new candidate/freeze/PDF/lock before one new professional score.
