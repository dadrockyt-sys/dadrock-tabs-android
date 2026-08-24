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

Approved-audio evidence already shows disagreement without professional reference:
- raw: 447 beats, 38 interval outliers, phase 1 / first beat 3, bar confidence `0.08797`
- repaired: 449 beats, 0 interval outliers
- independent repaired-grid consensus: phase 2 / first beat 2, confidence `0.1978`, two signal winners, unstable halves
This proves inheritance is unsafe; it does not yet prove phase 2 is correct.

## Post-repair phase shadow status
- `analyzer/v143_post_repair_bar_phase_shadow.py`: diagnostic-only multi-window audio phase assessment; no runtime mutation.
- Self-reporting CPU workflow run `32735869765` proved the previous synthetic test was over-constrained. It failed because the artificial click signal itself was ambiguous: preferred phase 2 had only 4/7 window votes, weighted fraction `0.44899`, full consensus signal count `0`, confidence `0.0223`; therefore `robustPreference=false` and `phaseChangeRecommended=false`. Approved-audio stage was correctly skipped. Protected/runtime/Production unchanged.
- This is a good safety behavior: ambiguous phase evidence must not trigger a rephase.
- `analyzer/check_v143_post_repair_bar_phase_shadow.py` fixed at commit `acc3d0d89ff8973186e093b4e2f155cdcc87aa60`.
  - still proves the defect class arithmetically: one inserted false sub-beat shifts later physical downbeats from raw residue 0 to raw residue 1 while repair restores the clean physical pulse train but retains stale phase 1.
  - no longer falsely requires this artificial audio to recover phase 0.
  - now requires the real safety invariant: `phase_change_recommended == robust_preference AND preferred != inherited`; ambiguous evidence must refuse change.
- The push from `acc3d0d...` triggers one new CPU-only self-reporting workflow. No Modal/GPU.

## Cost control
- No Modal/GPU inference in this continuation.
- Do not rerun old candidate/freeze/scorer.
- Inspect only the single CPU self-report result triggered by `acc3d0d...`.

## Next exact actions
1. Read the new `debug/v143-contextual-prune/post-repair-bar-phase-shadow-status.json` and confirm synthetic success.
2. If approved stage ran, inspect `post-repair-bar-phase-approved-audio-shadow.json` for robustness/window agreement.
3. If approved audio remains ambiguous, do **not** rephase. Improve generic audio-only phase evidence or switch focus to the independent pitch-carrier audit without spending Modal compute.
4. If approved phase is robust, create a NEW repaired timing shadow that explicitly applies audio-derived post-repair rephasing, then static/determinism gates before at most one targeted low-cost inference.
5. Any accepted correction eventually requires a brand-new candidate/freeze/PDF/lock identity before another single professional score.
