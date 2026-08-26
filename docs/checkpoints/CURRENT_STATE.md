# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Current accepted calibration baseline remains `pitch-position-shift-54a6e8d3aa91c422` (1144 events / 113 measures / SHA `5b36270a...`). Its family is consumed and archived. A fresh fit-only diagnostic for this new baseline is complete and sealed; it constructed/ranked/selected no candidates and read no validation/canary labels. Fresh fit signals now permit pre-registration of a materially distinct successor family. Production remains untouched.**

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
- Improvement vs previous accepted baseline: critical `-48`; pitch `+0.02392344497607657`; pitch/timing `+0.011483253588516741`; string/fret/timing `+0.006698564593301433`; chord/voicing `+0.0027643400138217047`.
- Promotion scope remains calibration-only: Production false; Rhythm complete false; near-100 false; unseen generalization false.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1. Single-signature prune — failed validation.
2. Two-signature prune — failed final measure-set invariant.
3. Triple prune — historical accepted baseline.
4. Additive four-signature prune — none fit-qualified; sealed `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Same-string contextual pitch shift — previous accepted baseline; sealed `21ca074f3917fb72614686ca5b46a3894ea53374`.
6. Joint contextual pitch+step — failed canary; sealed `215fc49106ef3501b71452b1f6c9f6d638cafd77`.
7. Joint contextual pitch+adjacent-string position — current accepted baseline; run `32971373324`; report blob `04a462983bf4c50364d0e4f39bcd08a5652c6b5e`; sealed `61422dea64ed4758999b3cd3c978d0db344e3ef6` / blob `6e18eaebf2f0a40e0d238fa1298b30c5be45915b`.

## Fresh current-baseline fit-only diagnostic — COMPLETE / SEALED
- Diagnostic implementation retarget commit `faaa1102f5311a8068b25e2feea2d566c5e75a4b`; blob `7b6b0e51e1f0b8cfb69f7c0019845b7dbea74755`.
- Reconstruction/helper test commit `9cbeab9b75d0695784c9cecf7e9a64bc1ced53c6`; blob `e32a76b050d34761fdee3dd29f7115076ac90cf9`.
- CPU gate `32971927840` SUCCESS.
- One-shot diagnostic arming commit `c6c808901ac84d0defbabceb543b59a328fc2d7c`; run `32972033516` SUCCESS.
- Persisted report `debug/v144-rhythm-calibration/diagnostics/current-pitch-position-baseline-fit-mechanisms.json`; bot commit `3bed803a666d105cd95c96c94ab7beb192c2241e`; report blob `dbc0c1ab0cfff943f95eab48720c7c2a5eb9d175`.
- Diagnostic workflow sealed `a6d5ddf373de8a71facf8474d48550aa990d7d54`; archived blob `ee09beb98852127f184d469c48614a9975869b56`.
- Isolation: candidate construction false; ranking false; selection false; validation labels false; canary labels false; runtime reference false; Modal/GPU false.
- Fit counts: generated `643`, reference `594`, critical `1075`; pitch matched `161` / F1 `0.26030719482619236`; tight pitch/timing matched `41` / F1 `0.06628940986257073`; gross ±2-step pitch/timing matched `81`; exact string/fret/timing matched `29` / F1 `0.04688763136620856`; chord/voicing `0.03976608187134503`.
- Fit mechanisms: exact-onset exact-pitch `41`; same-onset wrong-pitch substitution slots `171`; same-measure pitch matches displaced from exact onset `120`; recovered only by gross ±2-step tolerance `40`; pitch matches outside gross tolerance/competing `80`; tight pitch matches with wrong string/fret `12`.
- Fit-only ceilings remain diagnostic only: count-preserving pitch ceiling `0.9603880355699272`; timing-alignment ceiling for existing pitch matches `0.2603071948261924`; string/fret-remap ceiling for tight pitch matches `0.06628940986257073`.
- Shape signals: timing opportunity `120`; same-onset pitch substitution opportunity `171`; position opportunity inside tight pitch matches `12`.
- **No validation/canary outcomes from consumed families may inform successor construction/ranking.**

## Next materially distinct family — NOT YET IMPLEMENTED
- Permissible fit-only evidence supports exploring a joint **pitch + within-measure timing + adjacent-string position** correction family.
- To remain materially distinct from all consumed correction families, every transformed event must require all three non-zero changes together: pitch shift, step shift, and adjacent-string shift.
- Proposed fixed semantic bounds before evaluation: pitch within ±12 semitones; step within ±2; string exactly adjacent ±1; event count/order/measure/duration/other metadata preserved; fret recomputed from E-standard tuning; linked pitch-technique events excluded; invalid targets skipped, never clamped.
- This family is only a pre-registration direction at this checkpoint. No policy, tests, search, workflow, candidate, or outcome exists yet.

## Immediate next actions
1. Pre-register the joint pitch+step+adjacent-string policy from the fresh fit-only diagnostic, requiring all three non-zero deltas so it cannot collapse into consumed families.
2. Add deterministic policy tests and pass the CPU gate before search implementation.
3. Add search-level invariants and pass another CPU gate before any candidate evaluation.
4. Only then allow one exact-message/path-gated CPU one-shot with fixed support `3`, max candidates `256`, pitch bound `12`, step bound `2`, string bound `1`; archive immediately after one run.
5. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit user authorization.
