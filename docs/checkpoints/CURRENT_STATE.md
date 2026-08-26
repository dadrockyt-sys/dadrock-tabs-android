# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Current accepted calibration baseline is `pitch-position-shift-54a6e8d3aa91c422` (1144 events / 113 measures / SHA `5b36270a...`). Its family is consumed and archived. Fresh fit-only diagnostics are complete and sealed. A materially distinct three-way pitch + within-measure step + adjacent-string family is pre-registered; its corrected policy CPU gate `32972795739` passed. Search implementation commit `b409d796...` now exists, but search-level invariant tests and CPU-gate integration are not yet complete. No candidate evaluation has occurred. Production remains untouched.**

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
- Structured reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; 113 measures / 603 playable onsets / 946 notes / 104 populated measures.
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
- Transform chain: historical triple prune → same-string pitch shift → joint pitch+adjacent-string revoice `pitchClass::11 && stepParity::0 => pitch -2, string +1`.
- 1144 events; SHA/PDF `5b36270aaeafa73b2e25722e2576a40424ce5951dcfd2b5d769746bd9eb07e0d`; 113/113 measures; PDF `1.0`.
- Full gold: critical `1754`; pitch `0.32822966507177037`; pitch/timing `0.06411483253588517`; string/fret/timing `0.045933014354066985`; chord/voicing `0.038700760193503804`; coverage `1.0`; PDF `1.0`.
- Improvement vs prior accepted baseline: critical `-48`; pitch `+0.02392344497607657`; pitch/timing `+0.011483253588516741`; string/fret/timing `+0.006698564593301433`; chord/voicing `+0.0027643400138217047`.
- Promotion scope remains calibration-only: Production false; Rhythm complete false; near-100 false; unseen generalization false.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1. Single-signature prune — failed validation.
2. Two-signature prune — failed final measure-set invariant.
3. Triple prune — historical accepted baseline.
4. Additive four-signature prune — none fit-qualified; sealed `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Same-string contextual pitch shift — prior accepted baseline; sealed `21ca074f3917fb72614686ca5b46a3894ea53374`.
6. Joint contextual pitch+step — failed canary; sealed `215fc49106ef3501b71452b1f6c9f6d638cafd77`.
7. Joint contextual pitch+adjacent-string position — current accepted baseline; run `32971373324`; report blob `04a462983bf4c50364d0e4f39bcd08a5652c6b5e`; sealed `61422dea64ed4758999b3cd3c978d0db344e3ef6` / blob `6e18eaebf2f0a40e0d238fa1298b30c5be45915b`.

## Fresh current-baseline fit-only diagnostic — COMPLETE / SEALED
- Diagnostic implementation blob `7b6b0e51e1f0b8cfb69f7c0019845b7dbea74755`; reconstruction test blob `e32a76b050d34761fdee3dd29f7115076ac90cf9`.
- CPU gate `32971927840` SUCCESS.
- Diagnostic run `32972033516` SUCCESS; report bot commit `3bed803a666d105cd95c96c94ab7beb192c2241e`; report `debug/v144-rhythm-calibration/diagnostics/current-pitch-position-baseline-fit-mechanisms.json`; blob `dbc0c1ab0cfff943f95eab48720c7c2a5eb9d175`.
- Diagnostic workflow sealed `a6d5ddf373de8a71facf8474d48550aa990d7d54`; archived blob `ee09beb98852127f184d469c48614a9975869b56`.
- Isolation: candidate construction/ranking/selection all false; validation/canary labels false; runtime reference false; Modal/GPU false.
- Fit: generated `643`, reference `594`, critical `1075`; pitch matched `161` / F1 `0.26030719482619236`; tight pitch/timing `41` / F1 `0.06628940986257073`; gross ±2-step pitch/timing `81`; exact string/fret/timing `29` / F1 `0.04688763136620856`; chord/voicing `0.03976608187134503`.
- Fit mechanisms: exact-onset exact-pitch `41`; same-onset wrong-pitch slots `171`; displaced same-measure pitch matches `120`; gross-only timing recoveries `40`; pitch matches beyond gross tolerance/competing `80`; tight pitch matches with wrong string/fret `12`.
- Fit-only shape signals: timing opportunity `120`; same-onset pitch substitution `171`; position opportunity `12`.
- **Validation/canary outcomes from consumed families may not inform successor construction/ranking.**

## Joint pitch + step + adjacent-string family — PRE-REGISTERED / SEARCH IMPLEMENTED / NOT EVALUATED
- Fit-only rationale: fresh current-baseline diagnostic independently exposes pitch (`171` same-onset substitutions), timing (`120` displaced existing pitch matches), and position (`12` tight pitch/string-fret mismatches) opportunity.
- Policy `modal/v144_rhythm_pitch_step_position_shift_policy.py`; pre-registration commit `c5c78b0e23c275f997ce0c501b23a6797cd0d90d`; blob `6701084d4d9f7f4630cce147f57e5d746342f8d4`.
- Original policy-test commit `c410b2f903fb3d62dba26b922546891eb685f8c3`.
- Initial CPU gate `32972419227` failed only because a step-4 test fixture requested the wrong structural signature. Policy compilation, immutable V5 checks and provenance checks passed.
- Test-only correction commit `8cde106f359db42e1e83ea8aeae689630ad78d4b`; corrected test blob `e209141581724259f3bb0ed2a54792dd48c2894a`; retry CPU gate `32972795739` **SUCCESS**.
- Search implementation `validation/v144_rhythm_calibration/search_contextual_pitch_step_position_shifts.py`; commit `b409d7965110444309aa3e5118fdb609cb404eaa`; blob `cc4343a8b55d4703a8524dff39a7c0d01ca5900f`.
- Rule identity: source `pitchClass::<n>` + one reference-free structural context signature + fixed semitone shift + fixed step shift + fixed adjacent-string shift.
- **All three shifts are required non-zero**, so this family cannot collapse into consumed pitch-only, pitch+step, or pitch+position families.
- Pre-registered bounds: pitch within ±12; step within ±2; string exactly adjacent ±1.
- Construction uses deterministic same-measure pitch+step pairing, retaining only fit pairs whose target additionally requires a non-zero adjacent-string move and exactly matches a tuning-derived fret.
- Runtime receives generated event + locked signatures/shifts only; no reference. It preserves event count/order, measure, duration and other metadata while changing step/string/fret/MIDI together; fret is recomputed from E-standard tuning.
- Search implementation reconstructs the locked current baseline reference-free from V5 via historical triple → pitch shift → pitch+position transform and requires exact accepted SHA `5b36270a...` before any construction.
- Search `changed_event_count` requires pitch/step/string changes to occur together, fixed locked deltas, step bounds 0..15, adjacent-string-only movement, tuning-derived fret identity, protected metadata preservation, 1144-event preservation and 113-measure preservation.
- Fit-only ranking uses fixed support `3`, max candidates `256`, pitch bound `12`, step bound `2`, string bound `1`; validation/canary are not read during fit lock.
- **Search-level invariant tests and CPU-gate wiring are the next prerequisite. No workflow, one-shot, candidate evaluation, validation/canary result, or promotion exists yet.**

## Immediate next actions
1. Add deterministic search-level invariant tests for candidate naming, event count/order, protected metadata, joint three-way change, tuning identity, bounds, fixed deltas and expected-shift arity.
2. Wire the new search + tests into `.github/workflows/v144-rhythm-cpu-gate.yml`, compile/test on CPU, and save checkpoint.
3. Only after that search gate succeeds allow one exact-message/path-gated CPU one-shot with fixed support `3`, max candidates `256`, pitch `12`, step `2`, string `1`; archive immediately after one run.
4. Maintain fit-only construction/ranking → one locked winner → validation → canary → full-gold → independent PDF invariant; later failure means current-baseline fallback and no alternate selection.
5. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit user authorization.
