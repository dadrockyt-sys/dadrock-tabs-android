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

## Post-repair phase shadow work
- `analyzer/v143_post_repair_bar_phase_shadow.py`: diagnostic-only multi-window audio phase assessment; no runtime mutation.
- `analyzer/check_v143_post_repair_bar_phase_shadow.py`: hardened at commit `5b99cf111845ba99f9269a1cf00d261821f8e871`. Synthetic proof now demonstrates raw modulo-index corruption arithmetically after one inserted false sub-beat, sets the stale inherited phase explicitly, then requires the post-repair **audio-only** assessment to recover physical phase. This removes a brittle dependency on raw multi-signal consensus from the unit proof.
- `.github/workflows/v143-post-repair-bar-phase-shadow.yml`: updated at commit `16ce36d5a5330062a7f95ebf91cff20518099fd2` to self-report failures. CPU-only/no Modal. Synthetic and approved-audio steps capture logs with `continue-on-error`; an `if: always()` step writes and commits `debug/v143-contextual-prune/post-repair-bar-phase-shadow-status.json` even if a diagnostic stage fails. If approved analysis succeeds it also commits `post-repair-bar-phase-approved-audio-shadow.json`.
- This workflow update triggers one new CPU-only run. `runtimePhaseChanged=false`, protected/live/Production untouched.

## Cost control
- No Modal/GPU inference in this continuation.
- Do not rerun old candidate/freeze/scorer.
- Wait only for the single self-reporting CPU run result; do not blind-loop compute.

## Next exact actions
1. Read `debug/v143-contextual-prune/post-repair-bar-phase-shadow-status.json` once committed; inspect exact synthetic/approved outcomes and log tails.
2. If successful, inspect `post-repair-bar-phase-approved-audio-shadow.json` for robustness/window agreement.
3. If robust, create a NEW repaired timing shadow that explicitly applies audio-derived post-repair rephasing; update shadow invariants to permit and prove that change. Do not touch old frozen identity.
4. Run static/determinism gates before any Modal inference, then at most one targeted low-cost combined inference.
5. After timing coherence, resume independent pitch-carrier audit. Current static concern only: pitch evidence uses the minimum across two guitar views and may be over-conservative; no pitch change accepted yet.
