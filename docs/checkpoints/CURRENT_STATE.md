# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. The joint contextual pitch + adjacent-string position family completed its single CPU one-shot and produced a winner that passed fit, validation, canary, full-gold, and independent PDF-event invariants. Winner `pitch-position-shift-54a6e8d3aa91c422` (1144 events / 113 measures / SHA `5b36270a...`) is eligible to become the next calibration baseline. The one-shot is already consumed and archived; Production remains untouched. Selected-baseline manifest creation is the immediate next step.**

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

## Previous accepted V144 Rhythm calibration baseline
- Name `pitch-shift-41b7a7470fa3245a`.
- Manifest `debug/v144-rhythm-calibration/selected/v144-pitch-shift-selected-baseline.json`; blob `ee86c40d68e5c5b8e85bc4d008d9713c35e37a6c`.
- 1144 events; SHA/PDF `b6e1f8a8be150943d7224c74f9193b1b4050454620063846f6f5f5c773d4cbf6`; 113 measures.
- Full gold: critical `1802`; pitch `0.3043062200956938`; pitch/timing `0.052631578947368425`; string/fret/timing `0.03923444976076555`; chord/voicing `0.0359364201796821`; coverage `1.0`; PDF `1.0`.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1. Single-signature prune: run `32935621669`; fit winner failed validation.
2. Two-signature prune: passed split but lost a generated measure and failed final invariant.
3. Triple prune: consumed by historical triple baseline.
4. Additive four-signature prune: run `32938769540`; none cleared fit; sealed `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Same-string contextual pitch shift: run `32940695879`; winner became previous accepted baseline; sealed `21ca074f3917fb72614686ca5b46a3894ea53374`.
6. Same-string contextual joint pitch+step: run `32970149662`; winner failed canary; fallback retained previous baseline; sealed `215fc49106ef3501b71452b1f6c9f6d638cafd77`.
7. Joint contextual pitch + adjacent-string position: run `32971373324`; **winner passed all gates and full invariant**; workflow sealed `61422dea64ed4758999b3cd3c978d0db344e3ef6`, archived blob `6e18eaebf2f0a40e0d238fa1298b30c5be45915b`.

## Current-baseline fit-only diagnostic — SEALED
- Diagnostic report blob `9a187bba4159c0454089d40644a89d6859870fcc`; workflow sealed `c76f733a3ae91c7136ab7e81a68e5b20c264c923`.
- Fit generated `643`, reference `594`, critical `1101`; pitch matched `143`; tight pitch/timing `33`; gross ±2-step pitch/timing `68`; exact string/fret/timing `25`.
- Shape signals used before pre-registration: timing opportunity `110`; position-remap opportunity `8`; same-onset wrong-pitch substitutions `179`.
- No validation/canary labels were used to define the successor family.

## Joint pitch + adjacent-string position family — COMPLETE / CONSUMED / WINNER ELIGIBLE FOR CALIBRATION BASELINE
- Policy `modal/v144_rhythm_pitch_position_shift_policy.py`; pre-registration commit `28f14cfd5cc8bdd64160732cac8343a7553bbaa3`; blob `f69755b61bdcdf3a669847ce7e425289b4b0927f`.
- Policy tests commit `e72efebcb827abfa47eda01cc0be79f332cb72e0`.
- Policy CPU gate run `32970902634` SUCCESS.
- Search `validation/v144_rhythm_calibration/search_contextual_pitch_position_shifts.py`; commit `9c4ae70699a9706a5f76f6df5ddad0c4f8ef8d5b`; blob `30e9a5fc5dea3012efaad69872c80b09b5c892b3`.
- Search invariant tests commit `883958de29f9e4a55e2686ca108cd04a972d1495`.
- Search CPU gate commit `fd206f5beb216d218887e0300ed46699566fed57`; run `32971230708` SUCCESS.
- One-shot arming commit `96e5b050b999346d7a2a6a32fd5f6f6680862e9e`; exact trigger `v144 execute contextual pitch position one-shot`; run `32971373324` SUCCESS.
- Fixed values: support `3`, max candidates `256`, pitch bound `12`, adjacent-string bound `1`; CPU only.
- 9 fit-only candidates ranked/evaluated. Locked winner `pitch-position-shift-54a6e8d3aa91c422`: `pitchClass::11 && stepParity::0 => pitch -2, string +1`; 93 changed events; SHA `5b36270aaeafa73b2e25722e2576a40424ce5951dcfd2b5d769746bd9eb07e0d`.
- Fit gate passed: pitch-content `+0.029102667744543176`; pitch/timing `+0.012934518997574765`; string/fret/timing `+0.006467259498787382`; chord/voicing `+0.0023391812865497102`; critical delta `-26`; no regressions.
- Validation passed: pitch `+0.00865800865800867`; pitch/timing `+0.008658008658008656`; string/fret/timing `+0.004329004329004328`; chord/voicing `+0.006097560975609755`; critical delta `-8`; no regressions.
- Canary passed: pitch `0.0`; pitch/timing `+0.010230179028132988`; string/fret/timing `+0.010230179028132988`; chord/voicing `0.0`; critical delta `-2`; no regressions.
- Full-gold invariant passed: critical `1754` (`-48`); pitch `0.32822966507177037` (`+0.02392344497607657`); pitch/timing `0.06411483253588517` (`+0.011483253588516741`); string/fret/timing `0.045933014354066985` (`+0.006698564593301433`); chord/voicing `0.038700760193503804` (`+0.0027643400138217047`); coverage `1.0`; PDF fidelity `1.0`.
- Independent locked-candidate PDF proof passed at `1.0`, 1144 events, SHA `5b36270a...`, with professional reference unopened during fidelity proof.
- Persisted report `debug/v144-rhythm-calibration/candidates/contextual-pitch-position-search.json`; bot commit `3283d881304166cce9bb691e15557f3eb0e14d3e`; report blob `04a462983bf4c50364d0e4f39bcd08a5652c6b5e`.
- Workflow archived immediately in commit `61422dea64ed4758999b3cd3c978d0db344e3ef6`; archived blob `6e18eaebf2f0a40e0d238fa1298b30c5be45915b`. Replay is refused.
- **Family is consumed. Runner-up selection/replay/retuning is forbidden.**

## Immediate next actions
1. Create a selected calibration-baseline manifest for `pitch-position-shift-54a6e8d3aa91c422`, recording the exact report/run/archive identities and promotion scope: calibration baseline true, Production false, Rhythm complete false, near-100 false, unseen-generalization false.
2. After manifest creation, treat SHA `5b36270a...` / 1144 events / 113 measures as the locked current V144 Rhythm calibration baseline.
3. Before defining any further family, build a fresh **fit-only diagnostic for the new baseline**; do not reuse old-baseline shape counts as if they described the new baseline.
4. Validation/canary outcomes from this consumed family may not be used to construct or rank future candidates.
5. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit user authorization.
