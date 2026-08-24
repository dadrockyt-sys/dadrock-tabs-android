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
- synthetic `success`; approved `success`
- protected exact; reference-free; runtime/live/Production unchanged
- raw 447 beats / 38 interval outliers / inherited phase 1
- repaired 449 beats / 0 interval outliers
- global multi-window preferred phase 2, 5/7 votes, weighted fraction `0.6784292`, full signal count 2, `robustPreference=true`, `phaseChangeRecommended=true`
- BUT first half strongly/stably prefers phase 1 (`0.48126`) while second half strongly/stably prefers phase 2 (`0.44882`). Do not apply a global rephase until local phase path is understood.

## Local phase-path diagnostic staged
- Added `analyzer/v143_post_repair_phase_path_shadow.py`.
  - generic local windows: 64 repaired beats (16 bars), stride 16 beats (4 bars), starts aligned to modulo-4 residue.
  - computes the same four audio-only signals (accent, low accent, harmonic change, bass change) **once** for the whole repaired grid, then slices local windows; no repeated STFT per window.
  - a local window is `strong` only when at least two independent signals choose its winner **and** the winner is stable across the window halves; no fixture-tuned confidence threshold.
  - records local winners/scores/confidence plus contiguous strong runs and strong phase transitions; diagnostic only, no runtime phase mutation.
  - efficient version commit `a0adbfc346871ee921b13cc579c10e2c47771b65`.
- Added `analyzer/check_v143_post_repair_phase_path_shadow.py` commit `4434b13bfddf886e56a5e54f571c853139a19748`.
  - validates aligned local-window coverage and pure strong-run/transition summarization without song/reference data.
- Added CPU-only self-reporting workflow `.github/workflows/v143-post-repair-phase-path-shadow.yml` commit `c680158f29b61ceaa721acc7f8fb99223795456a`.
  - no Modal/GPU.
  - runs static checker + anti-leakage + protected blob gate, then one approved-audio timing/repair/local-phase-path pass.
  - writes `debug/v143-contextual-prune/post-repair-local-phase-path-status.json` always and approved diagnostic on success.
  - runtimePhaseChanged/liveRhythmOutputChanged/productionModified remain false.

## Cost control
- No Modal/GPU inference in this continuation.
- Do not rerun old candidate/freeze/scorer.
- Inspect only the single CPU local-phase-path run triggered by the new workflow.

## Next exact actions
1. Read `debug/v143-contextual-prune/post-repair-local-phase-path-status.json` once committed.
2. If successful, inspect `post-repair-local-phase-path-approved-audio-shadow.json` for strong local runs/transitions.
3. Determine whether the first-half phase-1 / second-half phase-2 disagreement is a stable local transition, ambiguous arrangement evidence, or pulse-grid drift.
4. Do not alter runtime timing until that is resolved generically/reference-free.
5. After timing coherence, resume independent pitch-carrier audit; any accepted correction still requires a brand-new candidate/freeze/PDF/lock before one new professional score.
