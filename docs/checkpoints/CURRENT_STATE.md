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

## Last proven candidate/freeze
- Combined repaired timing + precision: 449 repaired beats, 0 interval outliers, 113 measures / 1796 slots, all measures populated, explicit primary complete.
- Exact 2-pass proof run `32697939613` passed.
- Candidate product blob `20e7a583fcb96249636cc63b01cf9ae0044f2c62`; pre-freeze run `32699399835`. Do not rerun it.
- Fresh scored lock came from preholdout run `32702772593`; PDF-event fidelity `1.0`; protected/Production unchanged.

## One-shot professional score — FAILED
Run `32731885778` used immutable scorer-only V2 after lock validation. Broad results only:
- measure coverage recall `1.0`
- pitch-content F1 `0.23718280683583634`
- pitch+timing tolerant F1 `0.033143448990160536`
- string/fret+timing tolerant F1 `0.018643190056965304`
- chord pitch-set tolerant F1 `0.006024096385542168`
- exact voicing tolerant F1 `0.006024096385542168`
- critical mismatches `1723`
Allowed diagnosis: coverage is solved; timing/grid identity and pitch identity remain fundamentally wrong. Scorer/reference is closed again.

## Timing audit finding — GENERAL / REFERENCE-FREE
The adapter sign convention itself is coherent: `first_beat_in_measure = (-downbeat_index_mod4) % 4` and serialization uses that phase consistently.

A general defect was found one stage earlier: `v143_reference_free_beat_grid_repair.py` reconstructs a new clean beat sequence but copies the raw tracker's `first_beat_in_measure` and `downbeat_index_mod4` unchanged and declares `barPhaseChanged=false`. Raw phase is defined by raw `sequence_index % 4`; once inserted/sub-beat/duplicate pulse indices are repaired, that phase is not a safe invariant.

Existing audio-only diagnostics already expose this disagreement without professional-reference data:
- raw timing: 447 beats, 38 interval outliers, `downbeatIndexMod4=1`, `firstBeatInMeasure=3`, bar confidence `0.08797`
- repaired timing: 449 beats, 0 interval outliers
- independent post-repair bar consensus: phase `2`, `firstBeatInMeasure=2`, confidence `0.1978`, two signal winners, not stable across halves
This proves inherited phase is logically unsafe; it does **not** yet prove phase 2 should be accepted.

## New diagnostic-only work staged
1. `analyzer/v143_post_repair_bar_phase_shadow.py`
   - created commit `1880c8da7f0e31f0cdfdb36a7b204bd00a904a7b`
   - current trigger commit `26a95a3cdb37110b8663ea895b39f94f6f74b4da`
   - evaluates seven long bar-residue-aligned windows of the repaired pulse train and aggregates independent audio-only phase votes/scores.
   - recommendation only; does not mutate runtime timing.
2. `analyzer/check_v143_post_repair_bar_phase_shadow.py`
   - commit `f7675600ceaa31378528b7db8851d081f0c70f75`
   - synthetic proof inserts one false sub-beat early, demonstrating how raw index phase becomes wrong while repair restores physical beat continuity; post-repair audio-only phase must recover the physical phase.
3. `.github/workflows/v143-post-repair-bar-phase-shadow.yml`
   - commit `473b0bc9b8abb2d1fcd89022f5c1da00579486c0`
   - CPU-only; no Modal/GPU. Runs syntax/synthetic/anti-leakage/protected gates, then one approved-audio post-repair phase shadow and writes `debug/v143-contextual-prune/post-repair-bar-phase-approved-audio-shadow.json`.
   - `runtimePhaseChanged=false`, live output unchanged, Production unchanged.

The workflow was explicitly triggered by commit `26a95a3cdb37110b8663ea895b39f94f6f74b4da`. At this checkpoint the diagnostic file had not yet appeared, so do not infer pass/fail yet.

## Cost control
- No Modal/GPU inference has been used in this continuation.
- Do not rerun old candidate/freeze or old scorer.
- Inspect the single CPU phase-shadow result first.
- If ambiguous, improve generic audio-only phase evidence only; no song-specific offset and no professional-event diagnosis.

## Next exact actions
1. Read `debug/v143-contextual-prune/post-repair-bar-phase-approved-audio-shadow.json` once it exists.
2. If the shadow is robust and internally consistent, create a NEW repaired timing shadow that applies rephasing after repair; update its invariants so phase change is explicit and audio-derived rather than forbidden.
3. Re-establish deterministic/static gates before any Modal inference.
4. Only then run at most one targeted low-cost combined inference to validate the new timing carrier.
5. After timing is coherent, continue the independent pitch-carrier audit; current static note is that pitch selection is extremely conservative across the two guitar views and needs separate audio-only evidence before change.
6. If a timing/pitch correction is accepted, create a brand-new candidate/freeze/PDF/lock identity before one new professional score.
