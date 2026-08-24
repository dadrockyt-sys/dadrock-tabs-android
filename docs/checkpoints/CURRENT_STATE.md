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

## Timing audit finding — GENERAL / REFERENCE-FREE
Adapter sign convention is coherent. General defect is earlier: beat-grid repair rebuilds a clean pulse sequence after malformed raw beat intervals but blindly copies raw `first_beat_in_measure` / `downbeat_index_mod4`. Raw phase is defined by raw sequence index modulo 4, so inserted/sub-beat/duplicate pulse removal can invalidate inherited phase.

## Approved post-repair phase shadow — GREEN DIAGNOSTIC, NOT YET ACCEPTED RUNTIME CHANGE
CPU-only run `32736686527`, trigger `acc3d0d89ff8973186e093b4e2f155cdcc87aa60`:
- synthetic outcome `success`
- approved outcome `success`
- approved diagnostic exists
- protected pipeline exact; reference-free; runtime labels false; runtime phase unchanged; live/Production unchanged
- raw timing: 447 beats, phase 1 / first beat 3, bar confidence `0.0879734`, 38 interval outliers
- repaired timing: 449 beats, 0 interval outliers
- approved repaired-grid multi-window preferred phase: `downbeatIndexMod4=2`, `firstBeatInMeasure=2`
- preferred vote count `5/7`, vote fraction `0.7142857`, weighted vote fraction `0.6784292`
- full-file winner matches preferred, full consensus signal count `2`, full confidence `0.197795`
- `robustPreference=true`, `phaseChangeRecommended=true`

Important caution discovered from the same audio-only diagnostic: phase evidence is not uniform through the song. The first half strongly prefers inherited phase 1 (`confidence=0.48126`, two signal winners, stable across halves), while the second half strongly prefers phase 2 (`confidence=0.44882`, two signal winners, stable across halves). The first three quarters also prefer phase 1, while full/trim/middle/last-three-quarters prefer phase 2. Therefore a simple global phase-2 replacement may hide a real local phase transition / pulse-index slip / structural bar shift. **Do not wire global rephase yet.**

## Cost control
- No Modal/GPU inference in this continuation.
- Do not rerun old candidate/freeze/scorer.
- Stay CPU/reference-free until local phase path is understood.

## Next exact actions
1. Build a cheap CPU-only repaired-grid phase-path diagnostic using bar-aligned local windows (no runtime mutation) to locate whether/where the preferred modulo-4 phase changes.
2. Require generic evidence only: local window winner, independent signal winners, confidence, stability across halves, and contiguous-run consistency. No song/reference labels.
3. If a stable local transition exists, determine whether it is caused by beat-grid index drift/repair or by genuine musical bar structure before any runtime-affecting timing change.
4. Only after timing phase path is coherent should a NEW timing shadow be allowed to alter phase.
5. Then static/determinism gates before at most one targeted low-cost combined inference.
6. After timing coherence, resume the independent pitch-carrier audit.
7. Any accepted correction eventually requires a brand-new candidate/freeze/PDF/lock identity before another single professional score.
