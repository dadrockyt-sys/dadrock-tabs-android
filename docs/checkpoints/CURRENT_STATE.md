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
- Repaired timing + precision: 449 repaired beats, 0 interval outliers, 113 measures / 1796 slots, all measures populated, explicit primary complete.
- Exact 2-pass proof run `32697939613` passed. Old candidate/freeze must not be rerun/rescored.
- One-shot professional run `32731885778`: coverage recall `1.0`, pitch-content F1 `0.23718280683583634`, pitch+timing F1 `0.033143448990160536`, critical mismatches `1723`.
- Scorer/reference is closed again. Allowed diagnosis only: coverage solved; timing/grid identity and pitch identity fundamentally wrong.
- Retired scored render identity `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`: 725 selected/unique attacks → 985 rendered notes, 236 multi-note onsets, max chord size 6, 113 measures, PDF fidelity 1.0.

## Closed timing hypotheses
- Do not mutate global bar phase or derive musical phase from raw beat-list offset; audio-only evidence did not support it.
- Earlier claim that precision/assembly choose different physical rows was retracted; `_best_rows_by_slot` behavior is semantically identical.
- Old product cannot recover physical onset because sustain promotion had already overwritten it.

## Physical onset provenance — corrected and proven
Old defect: candidate assembly preserved `timeSeconds=grid_time` and `onsetTime=physical_onset`, then sustain promotion overwrote `onsetTime` with grid time while claiming `attackTimingChanged=False`.

Correction/proof commits:
- initial checker `45b260a60afa82ec8c5f6c02a7104df9a2ffd28c`
- initial static workflow `885e1154af9e08f9e38dfcb6da14132383e654e0`
- pure helper `analyzer/v143_precision_sustain_promotion.py` commit `89143dc7382b200af449b607d1fbd294ba6916fd`
- product correction commit `c72ed6ff569e402f8761dbe1be5ea802c8e68059`
- corrected checker `2e488187fd53414090efdf0c47d39fa1cca72229`
- corrected workflow `38c4cc9b56bf3cd9356b2456837555c1cbd3d0cf`

Observed schema-v2 Actions diagnostic PASSED:
- physical onset preserved exactly; grid `timeSeconds/start` unchanged;
- event count, `(measure,step)`, MIDI/string/fret unchanged;
- duration/residual contracts truthful; no invented attack/pitch;
- protected pipeline exact; no Modal/GPU/reference/Production.

Important scoring boundary: `projectV143RenderEvents()`/freeze/PDF omit physical timing seconds and score grid/pitch identity. Therefore physical-onset preservation alone cannot create a new scored identity and must **not** trigger a GPU candidate or holdout.

Cheap dual-timing projection proof: `validation/rhythm_holdout/check_v143_precision_dual_timing_projection.mjs` commit `37164fcabaf03fe3a900eb0e29a81143ac623722`; product-proof workflow extended commit `e3264e90a79c3f5412df6894f20973a6ae723613`.

## Holdout workflow safety drift
- `.github/workflows/v143-repaired-timing-precision-final-preholdout.yml` is stale/pinned to the old candidate and generic freeze prep.
- Its retired set does not yet include scored `a81190...`.
- **Do not dispatch it as-is.** Future preholdout must fail closed on `a81190...` and bind a genuinely new scoring-relevant candidate.

## Precision polyphonic expansion — audio-only defect PROVEN
Source audit first established that secondaries are not arbitrary:
- carrier groups per-pitch Basic Pitch clusters within a ≤30 ms onset group;
- precision requires positive two-view CQT attack/body evidence;
- non-harmonic secondary floor `0.80`, harmonic-above-primary floor `0.92`;
- assembly only renders selected observed pitches that can be jointly voiced.

However the committed-product CPU audit found a specific internal contradiction, not a reference-tuned hypothesis.

Audit files:
- `analyzer/check_v143_precision_polyphonic_expansion.py` initial commit `3f5874ce3ce2b569eed1f0dd958afc4e2c91bf32`, expanded proof commit `16bf59f87f71ee057938009728bc80baf4b1cf9e`.
- workflow `.github/workflows/v143-precision-polyphonic-expansion-audit.yml` initial commit `241234a7a25de06df12b6c98e649b84884a10732`.
- observed diagnostic `debug/v143-contextual-prune/precision-polyphonic-expansion-audit.json` schemaVersion 2.

Observed old-candidate counts, no scorer/GPU:
- 725 attacks → 985 notes = 260 secondary notes.
- 236 multi-note attacks; chord histogram: 489×1, 215×2, 20×3, 1×6.
- 106/260 secondaries are harmonic-family intervals (`40.77%`): +12 = 86, +19 = 13, +24 = 6, +28 = 1.
- precision metadata reports **144 fundamental promotions**.
- serialized evidence independently reconstructs **144 promoted primaries**.
- **all 144/144 still render the strongest raw pitch**.
- **96/144 promoted primaries also render that strongest raw pitch at a harmonic-family interval above the promoted primary**; interval distribution includes +12 = 78, +19 = 11, +24 = 6, +28 = 1.
- synthetic proof reproduces the logic: observed 40/52, 52 strongest raw, 40 promoted as fundamental, yet selected set remains `[40,52]`.
- `harmonicPromotionDoubleCountPathProven=true`.
- protected pipeline unchanged; no professional reference/runtime labels/Production/Modal GPU.

Why this is a real structural defect:
- precision’s own rationale says a lower physically observed candidate may replace a stronger **overtone** when harmonic-family evidence makes the lower pitch the likely fundamental.
- immediately afterward, the strongest raw pitch has ratio `1.0` to itself, so it automatically passes secondary retention and is rendered as an independent note.
- the same upper pitch is therefore treated simultaneously as the overtone evidence that justified lower-fundamental promotion and as a separate chord note.
- This directly changes scored MIDI identity and does not depend on professional-reference labels.

Secondary provenance note:
- all 238 multi-hypothesis attacks serialize identical group-level Basic Pitch `stemSupport/sweepSupport/detectionCount` across their per-pitch hypotheses; true per-pitch Basic Pitch support is not recoverable from the committed serialized hypotheses.
- Do not invent per-pitch support from those group maxima.

## Minimal scoring-relevant correction — committed, CPU proof pending Actions artifact
Added `analyzer/v143_precision_promoted_harmonic_guard.py`, commit `588b314c3103ffbea8a0a933351562551750f670`.

Guard is deliberately minimal:
- recompute strongest positive raw MIDI from the same physical row/evidence ordering used by precision;
- if primary differs from strongest raw **and** strongest raw is an upper interval in `HARMONIC_INTERVAL_WEIGHTS` **and** it survived selected pitches, remove only that exact strongest harmonic pitch;
- do not change attacks, grid positions, primary MIDI, non-harmonic secondaries, weaker harmonic secondaries, or add any pitch.
- result remains a `PrecisionShadowResult`; suppressed pitch count increases only by actual removals.

Synthetic checker `analyzer/check_v143_precision_promoted_harmonic_guard.py`:
- initial commit `938f7512e3ffc2f6f7f06adee71ccc3919ba9508`;
- diagnostic-producing update commit `34998ba2a84662f2d2b8e72e319c3ee6e8150edb`.
- proves promoted +12 strongest is suppressed, non-harmonic +7 strongest is preserved, unpromoted pitch set is preserved, attack/primary identity unchanged, no invented pitch/attack/relocation.
- binds the observed old-candidate audit: 144 promotions / 96 scoring-relevant harmonic-strongest opportunities / 78 octave opportunities.

Product path updated commit `534be3fec36cf5ec4a87089b1298becb4933693d`:
- bundles `v143_precision_promoted_harmonic_guard` in candidate image;
- applies guard immediately after reference-free precision and before candidate assembly;
- output schemaVersion 4 / assembly version 6 / liveV143 version 7 / candidate schemaVersion 4;
- emits `promotedHarmonicGuardDiagnostics`;
- candidate mode explicitly names promoted-harmonic guard.

CPU audit workflow updated commit `f8022a7a90baf8ce2a902217b2ceb499fa58e84a` to run both expansion audit and guard proof and commit `precision-promoted-harmonic-guard-proof.json`/log. It enforces expected old-candidate opportunity count 96, scoring-relevant pitch change, unchanged attack identity, protected runtime, anti-leakage, no GPU/reference/Production.

At this checkpoint, **do not yet claim the guard proof Actions artifact passed** until `debug/v143-contextual-prune/precision-promoted-harmonic-guard-proof.json` is observed with `passed=true`.

## Cost control
- No Modal/GPU inference in this continuation so far.
- No professional scorer/reference opened.
- Old candidate/freeze/scorer remain untouched.
- The new harmonic guard is the first correction in this continuation proven by source + committed-audio evidence to be capable of changing scored pitch identity.

## Next exact actions
1. Observe `debug/v143-contextual-prune/precision-promoted-harmonic-guard-proof.json`; require `passed=true`, protected pipeline unchanged, opportunity count 96, no reference/GPU/Production.
2. Extend cheap product proof/anti-leakage gates to include `v143_precision_promoted_harmonic_guard.py` and its checker if not already transitively covered.
3. Fail-close future preholdout path on retired scored SHA `a81190...`; do not dispatch stale preholdout.
4. If all CPU/static gates remain clean, **one new approved-audio candidate inference is now justified** because this correction changes scored MIDI identity. It must write a new candidate identity/path; do not overwrite or rescore retired freeze.
5. Before any professional score: prove new candidate determinism, freeze/PDF fidelity, brand-new render-event SHA != `a81190...`, then lock and score exactly once.
