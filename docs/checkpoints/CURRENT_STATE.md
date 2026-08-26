# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Current accepted calibration baseline is now `pitch-position-shift-54a6e8d3aa91c422` (1144 events / 113 measures / SHA `5b36270a...`). It passed fit, validation, canary, full-gold, and independent PDF-event invariants. Its one-shot family is consumed and archived. Production remains untouched. The next safe step is a fresh fit-only diagnostic against this new baseline before any successor family is proposed.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Frozen V5 result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Original V5 professional one-shot holdout is permanently consumed; never rerun/retry or retune V5 from V144 evidence.
- `main`, Production, `/ai-tab` frontend, Bass/Lead, and `freezeReady=false` remain untouched.
- **No Modal/L4/GPU without fresh explicit user authorization. None has been used in V144.**

## Gold calibration semantics
- Professional target is a **gold calibration benchmark, not an unseen holdout**.
- Exact structured reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; completeness 113 measures / 603 playable onsets / 946 notes / 104 populated measures.
- Never claim unbiased generalization from this benchmark.

## Fixed selector / invariant safety
- Deterministic split: measure+step, seed 144, 60% fit / 20% validation / 20% canary.
- Fit labels may construct/rank; validation/canary only gate one locked winner.
- Fixed fit gate: pitch-content gain >= `0.005`; no musical metric regression; no critical mismatch increase; PDF-event fidelity `1.0`.
- Every candidate must preserve all 113 generated measures; count-preserving correction families must preserve 1144 events.
- Fixed order: fit → validation → canary → full-gold → independent PDF-event invariant.
- Later failure means deterministic accepted-baseline fallback; never select an alternate.
- Never change thresholds/support from observed outcomes.

## Accepted V144 Rhythm calibration baseline — LOCKED
- Name `pitch-position-shift-54a6e8d3aa91c422`.
- Manifest `debug/v144-rhythm-calibration/selected/v144-pitch-position-selected-baseline.json`; commit `0b55bc1f3e2fdefe179f3eb17bd81be2a0574d31`; blob `45287a40fbbe88f411d2eca7db3cce072174eda8`.
- Transform chain: historical triple prune → accepted same-string pitch shift → contextual joint pitch + adjacent-string revoice `pitchClass::11 && stepParity::0 => pitch -2, string +1`.
- 1144 events; canonical/PDF SHA `5b36270aaeafa73b2e25722e2576a40424ce5951dcfd2b5d769746bd9eb07e0d`; exact 113/113 generated measures; PDF fidelity `1.0`.
- Full gold: critical `1754`; pitch `0.32822966507177037`; pitch/timing `0.06411483253588517`; string/fret/timing `0.045933014354066985`; chord/voicing `0.038700760193503804`; measure coverage `1.0`; PDF fidelity `1.0`.
- Improvement vs previous accepted baseline: critical `-48`; pitch `+0.02392344497607657`; pitch/timing `+0.011483253588516741`; string/fret/timing `+0.006698564593301433`; chord/voicing `+0.0027643400138217047`; coverage unchanged.
- Promotion scope: calibration baseline true; Production false; Rhythm complete false; near-100 false; unseen generalization false.

## Previous accepted baseline
- `pitch-shift-41b7a7470fa3245a`; manifest blob `ee86c40d68e5c5b8e85bc4d008d9713c35e37a6c`; event SHA `b6e1f8a8be150943d7224c74f9193b1b4050454620063846f6f5f5c773d4cbf6`.
- Full gold was critical `1802`; pitch `0.3043062200956938`; pitch/timing `0.052631578947368425`; string/fret/timing `0.03923444976076555`; chord/voicing `0.0359364201796821`.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1. Single-signature prune — failed validation.
2. Two-signature prune — failed final measure-set invariant.
3. Triple prune — produced historical accepted baseline.
4. Additive four-signature prune — no fit-qualified candidate; sealed `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Same-string contextual pitch shift — produced previous accepted baseline; sealed `21ca074f3917fb72614686ca5b46a3894ea53374`.
6. Joint contextual pitch+step — winner failed canary; sealed `215fc49106ef3501b71452b1f6c9f6d638cafd77`.
7. Joint contextual pitch + adjacent-string position — **produced current accepted baseline**; run `32971373324`; report commit `3283d881304166cce9bb691e15557f3eb0e14d3e`; report blob `04a462983bf4c50364d0e4f39bcd08a5652c6b5e`; sealed `61422dea64ed4758999b3cd3c978d0db344e3ef6`; archived blob `6e18eaebf2f0a40e0d238fa1298b30c5be45915b`.

## Current accepted-family evidence — SEALED
- Policy `modal/v144_rhythm_pitch_position_shift_policy.py`; blob `f69755b61bdcdf3a669847ce7e425289b4b0927f`.
- Search `validation/v144_rhythm_calibration/search_contextual_pitch_position_shifts.py`; blob `30e9a5fc5dea3012efaad69872c80b09b5c892b3`.
- Policy CPU gate `32970902634` SUCCESS; search CPU gate `32971230708` SUCCESS; one-shot `32971373324` SUCCESS.
- 9 fit-only candidates evaluated; locked `pitch-position-shift-54a6e8d3aa91c422`, 93 changed events, event SHA `5b36270a...`.
- Fit passed: pitch `+0.029102667744543176`, pitch/timing `+0.012934518997574765`, string/fret/timing `+0.006467259498787382`, chord/voicing `+0.0023391812865497102`, critical `-26`, no regressions.
- Validation passed: pitch `+0.00865800865800867`, pitch/timing `+0.008658008658008656`, string/fret/timing `+0.004329004329004328`, chord/voicing `+0.006097560975609755`, critical `-8`, no regressions.
- Canary passed: pitch `0.0`, pitch/timing `+0.010230179028132988`, string/fret/timing `+0.010230179028132988`, chord/voicing `0.0`, critical `-2`, no regressions.
- Independent PDF-event proof passed at `1.0`; professional reference unopened during PDF proof.
- **Family consumed. Never replay, reselect runner-ups, retune support/bounds, or use its validation/canary outcomes to construct/rank future families.**

## Immediate next actions
1. Build a fresh current-baseline **fit-only mechanism diagnostic** that reconstructs and hard-checks the new `5b36270a...` baseline. It must not construct/rank/select candidates or read validation/canary labels.
2. Add deterministic reconstruction/helper tests and pass the CPU gate before running the diagnostic.
3. Run the diagnostic once on CPU, persist only its report, archive its workflow immediately, and record all identities here.
4. Only after that diagnostic may a materially distinct successor family be pre-registered from the new baseline's permissible fit-only evidence.
5. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit user authorization.
