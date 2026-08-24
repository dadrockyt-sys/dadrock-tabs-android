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

## General timing defect
Beat-grid repair can rebuild a clean pulse train after malformed raw beat intervals but still blindly inherit raw modulo-4 phase. Raw phase is defined by raw sequence index, so inserted/sub-beat/duplicate pulse removal can make inherited phase stale.

## Approved post-repair global phase diagnostic
CPU run `32736686527`: synthetic + approved success, protected/live/Production unchanged. Repaired grid 449 beats / 0 interval outliers. Global multi-window preferred phase 2 with 5/7 votes and weighted fraction `0.6784292`, but first half strongly/stably prefers phase 1 while second half strongly/stably prefers phase 2. Global phase replacement remains unsafe.

## Approved local phase-path diagnostic — GREEN / IMPORTANT
CPU run `32737275715`, trigger `c680158f29b61ceaa721acc7f8fb99223795456a`:
- static `success`, approved `success`, protected exact, reference-free, single feature extraction pass, runtime/live/Production unchanged.
- 26 local windows (64 repaired beats / 16-beat stride).
- first strong run: phase 1, 12 strong windows, repaired beat indices 32→272, mean confidence `0.54835`, min `0.40707`.
- transition region 224→304 is ambiguous/unstable (winners 2/0/2 with insufficient stability).
- later strong run: phase 3, 2 strong windows, repaired indices 304→384, mean confidence `0.50006`.
- later strong phase 2: one strong window, repaired indices 368→432, confidence `0.48565`.
- overall strong windows: phase1=12, phase3=2, phase2=1; multiple strong phases observed.
This rules out treating the full-file phase-2 vote as a simple global correction. The repaired pulse train or musical phase evidence changes materially later in the track.

## Raw↔repaired index-alignment diagnostic staged
To distinguish repair-index drift from arrangement-only accent changes, added a purely reference-free raw/repaired index provenance test:
- `analyzer/v143_repair_index_alignment_shadow.py` commit `f11e47147e9840280e10f7aef2762ab2c1502603`.
  - nearest raw-beat match within 0.25 expected period (same generic scale as repair boundary search), traces `rawIndex - repairedIndex` and modulo-4 offset runs/change points.
  - a raw inserted pulse should objectively produce a later modulo offset change even when repaired intervals are clean.
- `analyzer/check_v143_repair_index_alignment_shadow.py` commit `2159d9172b37cf88fef4141115b70d10417b8a9f`.
  - synthetic false-sub-beat proof requires offset run 0 before insertion and offset run 1 afterward; no song/reference labels.
- Updated CPU-only phase-path workflow at commit `6ce76949057eaae6a10ed160de061e984db7f023` to run both static checkers and add `rawRepairedIndexAlignment` to the approved diagnostic.
- This triggers one new CPU-only pass; still no Modal/GPU, no runtime timing mutation.

## Cost control
- No Modal/GPU inference in this continuation.
- Do not rerun old candidate/freeze/scorer.
- Inspect only the single CPU index-alignment-enhanced local-phase-path run triggered by `6ce7694...`.

## Next exact actions
1. Read the new `post-repair-local-phase-path-status.json` and enhanced approved diagnostic.
2. Compare raw↔repaired modulo-offset change points with the local phase-path transition region around repaired indices ~224–304 and later phase changes.
3. If index-offset changes line up with phase changes, build a general post-repair phase provenance correction; if they do not, treat local phase changes as musical/arrangement evidence and do not mutate the global beat index.
4. Stay CPU/reference-free until this distinction is resolved.
5. Only after timing coherence, resume independent pitch-carrier audit; any accepted correction still requires a brand-new candidate/freeze/PDF/lock before one new professional score.
