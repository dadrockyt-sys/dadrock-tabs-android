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
Committed-product CPU audit established:
- 725 attacks → 985 notes = 260 secondary notes.
- 236 multi-note attacks; chord histogram: 489×1, 215×2, 20×3, 1×6.
- 106/260 secondaries are harmonic-family intervals: +12=86, +19=13, +24=6, +28=1.
- precision metadata reports 144 fundamental promotions; serialized evidence reconstructs all 144.
- all 144/144 promoted attacks still rendered the strongest raw pitch.
- 96/144 promoted attacks rendered that strongest raw pitch at a harmonic-family interval above the promoted primary; +12=78, +19=11, +24=6, +28=1.
- synthetic proof reproduces observed `[40,52]`: 52 strongest raw, 40 promoted as fundamental, yet 52 remains selected/rendered.
- `harmonicPromotionDoubleCountPathProven=true`.
- protected pipeline unchanged; no professional reference/runtime labels/Production/Modal GPU.

Why structural: the upper pitch is used as overtone evidence to justify promoting the lower fundamental, then the same strongest upper pitch automatically passes the secondary-retention ratios and is rendered as an independent chord note.

## Minimal promoted-harmonic guard — PROVEN GREEN
Added `analyzer/v143_precision_promoted_harmonic_guard.py`, commit `588b314c3103ffbea8a0a933351562551750f670`.

Guard behavior:
- recompute strongest positive raw MIDI from the same physical row/evidence ordering used by precision;
- only when primary differs from strongest raw, strongest raw is an upper `HARMONIC_INTERVAL_WEIGHTS` interval, and it survived the selected pitch set, remove that exact strongest harmonic pitch;
- do not change attacks, grid positions, primary MIDI, non-harmonic secondaries, weaker harmonic secondaries, or add pitches.

Synthetic checker `analyzer/check_v143_precision_promoted_harmonic_guard.py` initial commit `938f7512e3ffc2f6f7f06adee71ccc3919ba9508`, diagnostic update `34998ba2a84662f2d2b8e72e319c3ee6e8150ed`.

Observed Actions proof `debug/v143-contextual-prune/precision-promoted-harmonic-guard-proof.json` PASSED:
- `passed=true`.
- old-candidate opportunity count = 96, including 78 octave opportunities.
- attack identity unchanged; primary MIDI unchanged; scoring pitch identity changes.
- no pitch/attack added, no relocation.
- protected pipeline exact expected blob.
- anti-leakage passed; professional reference false; runtime labels false; Production false; Modal GPU false.

Product path updated commit `534be3fec36cf5ec4a87089b1298becb4933693d`:
- bundles/applies guard after reference-free precision and before candidate assembly;
- emits `promotedHarmonicGuardDiagnostics`;
- output schemaVersion 4 / assembly version 6 / liveV143 version 7 / candidate schemaVersion 4.

CPU audit workflow updated commit `f8022a7a90baf8ce2a902217b2ceb499fa58e84a` and observed guard proof green.
Product-proof workflow extended commit `30d7da578667f7d128824d7d343be782bf064533` to compile/run the guard checker, include guard files/artifacts in path triggers, and enforce anti-leakage/protected-runtime tokens.

## Brand-new one-shot candidate path — CREATED, NOT YET TRIGGERED
Created `.github/workflows/v143-harmonic-guard-candidate-once.yml` in commit `346d0f38381906e9c821b7f6020c932f3e2b4c1c`.

Safety design:
- workflow triggers only when dedicated marker `debug/v143-contextual-prune/RUN_HARMONIC_GUARD_CANDIDATE_ONCE` is pushed; the marker has **not** been created yet at this checkpoint.
- bot pushes are excluded, so the workflow's marker deletion cannot launch a second inference.
- before Modal it requires: marker exists, old retired candidate blob remains exact `20e7a583...`, protected runtime exact, approved audio SHA exact, green guard proof with opportunity count 96, guard synthetic checker pass, anti-leakage pass.
- exactly one Modal L4 call writes only new path `debug/v143-contextual-prune/repaired-timing-precision-harmonic-guard-candidate-product.json`; old candidate path is never overwritten.
- after inference it runs repaired-timing freeze-payload preparation without opening scorer/reference, canonicalizes projected render events, and fails closed unless projected render SHA differs from retired `a81190...`.
- requires schema v4, guard suppression >0, 113 audio-derived measures, no invented attack/pitch/relocation, reference-free/runtime-label-free/Production-safe/protected-runtime-safe invariants.
- writes `repaired-timing-precision-harmonic-guard-candidate-proof.json` and `preFreezeTrace`, then commits both candidate/proof and deletes the marker in the same bot commit.

## Cost control
- No Modal/GPU inference has been run for the new guard yet.
- No professional scorer/reference opened.
- Old candidate/freeze/scorer remain untouched.
- One new approved-audio inference is now justified and the one-shot path is prepared to prevent accidental repeats.

## Next exact actions
1. Create the dedicated one-shot marker to trigger exactly one approved-audio harmonic-guard inference.
2. Re-check the branch for the new candidate + proof; require proof `passed=true`, guard suppression >0, 113 measures, protected hash exact, and projected render-event SHA != retired `a81190...`.
3. Save the new candidate SHA/event identity in this checkpoint immediately.
4. Create/use a new preholdout path bound to the new candidate and fail closed on all retired scored render identities, including `a81190...`; do not dispatch stale preholdout.
5. Only after deterministic new identity + freeze/PDF fidelity 1.0: immutable lock, then exactly one professional score.
