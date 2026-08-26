# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Current accepted calibration baseline remains `pitch-position-shift-54a6e8d3aa91c422` (1144 events / 113 measures / SHA `5b36270a...`). Eight candidate families are consumed and sealed. A materially distinct atomic exact-two-note onset dyad pitch-rewrite family has now been pre-registered from the sealed current-baseline fit-only diagnostic; policy + deterministic tests exist and CPU policy gate `32975186364` is running. No search implementation or candidate evaluation for this family exists yet. Production remains untouched.**

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

## Accepted V144 Rhythm calibration baseline — LOCKED / UNCHANGED
- Name `pitch-position-shift-54a6e8d3aa91c422`.
- Manifest `debug/v144-rhythm-calibration/selected/v144-pitch-position-selected-baseline.json`; commit `0b55bc1f3e2fdefe179f3eb17bd81be2a0574d31`; blob `45287a40fbbe88f411d2eca7db3cce072174eda8`.
- Transform chain: historical triple prune → same-string pitch shift → joint pitch+adjacent-string revoice `pitchClass::11 && stepParity::0 => pitch -2, string +1`.
- 1144 events; SHA/PDF `5b36270aaeafa73b2e25722e2576a40424ce5951dcfd2b5d769746bd9eb07e0d`; 113/113 measures; PDF `1.0`.
- Full gold: critical `1754`; pitch `0.32822966507177037`; pitch/timing `0.06411483253588517`; string/fret/timing `0.045933014354066985`; chord/voicing `0.038700760193503804`; coverage `1.0`; PDF `1.0`.
- Promotion scope remains calibration-only: Production false; Rhythm complete false; near-100 false; unseen generalization false.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1. Single-signature prune — failed validation.
2. Two-signature prune — failed final measure-set invariant.
3. Triple prune — historical accepted baseline.
4. Additive four-signature prune — none fit-qualified; sealed `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Same-string contextual pitch shift — prior accepted baseline; sealed `21ca074f3917fb72614686ca5b46a3894ea53374`.
6. Joint contextual pitch+step — failed canary; sealed `215fc49106ef3501b71452b1f6c9f6d638cafd77`.
7. Joint contextual pitch+adjacent-string position — current accepted baseline; run `32971373324`; report blob `04a462983bf4c50364d0e4f39bcd08a5652c6b5e`; sealed `61422dea64ed4758999b3cd3c978d0db344e3ef6`.
8. Joint contextual pitch+step+adjacent-string position — 14 fit candidates, none qualified; run `32974497513`; report commit `0cbf8c139d5123ecd27fe782c35f32cb33ff0f89`; report blob `c67bad28dea2ee7458a4e8159d5b7ab64fdce245`; sealed `55a948fa97ab100bdca0b1338b36c9a43a4f5ce9`; archived blob `b1123f14555192cf9a0b51217af2146df62f8472`.

## Fresh current-baseline fit-only diagnostic — COMPLETE / SEALED
- CPU gate `32971927840` SUCCESS; diagnostic run `32972033516` SUCCESS.
- Report `debug/v144-rhythm-calibration/diagnostics/current-pitch-position-baseline-fit-mechanisms.json`; commit `3bed803a666d105cd95c96c94ab7beb192c2241e`; blob `dbc0c1ab0cfff943f95eab48720c7c2a5eb9d175`; diagnostic workflow sealed `a6d5ddf373de8a71facf8474d48550aa990d7d54`.
- Candidate construction/ranking/selection false; validation/canary labels false; runtime reference false; GPU false.
- Fit: generated `643`, reference `594`, critical `1075`; pitch `161` / F1 `0.26030719482619236`; tight pitch/timing `41` / F1 `0.06628940986257073`; gross ±2-step matches `81`; exact string/fret/timing `29` / F1 `0.04688763136620856`; chord/voicing `0.03976608187134503`.
- Shape signals: same-onset wrong-pitch substitutions `171`; displaced existing pitch matches `120`; tight pitch/string-fret mismatches `12`.
- This diagnostic is the only permissible family-shape evidence while the accepted baseline stays unchanged. **Consumed-family candidate/gate outcomes may not be used to construct/rank a successor.**

## Joint pitch + step + adjacent-string family — COMPLETE / CONSUMED / SEALED
- Policy blob `6701084d4d9f7f4630cce147f57e5d746342f8d4`; search blob `cc4343a8b55d4703a8524dff39a7c0d01ca5900f`; final search-test blob `9b1b4b802c5de0fe59a306e7ab76313c36c94416`.
- Policy CPU gate `32972795739` SUCCESS; search CPU gate `32974163895` SUCCESS.
- One-shot run `32974497513` SUCCESS infrastructure. 14 rules ranked / 14 fit candidates evaluated; none passed fixed fit gate.
- Fit lock/selected `accepted-v144-baseline`; selected reason `fit-no-qualified-pitch-step-position-candidate`; stopped at fit; validation/canary/full null; calibration promotion false.
- Fallback SHA remained `5b36270a...`; independent PDF fidelity `1.0`; V5/main/Production/runtime-reference/GPU safety clean.
- Sealed commit `55a948fa97ab100bdca0b1338b36c9a43a4f5ce9`; replay refused. No selected manifest was created.

## Atomic exact-two-note onset dyad pitch rewrite — PRE-REGISTERED / NOT SEARCHED
- Materially distinct unit of transformation: **two events at one onset are an atomic unit**. This is not an individual-event pitch, pitch+step, pitch+position, or pitch+step+position retune.
- Fit-only rationale comes only from the sealed current-baseline diagnostic: `171` same-onset wrong-pitch substitution slots plus low fit chord/voicing F1 `0.03976608187134503`.
- Policy `modal/v144_rhythm_onset_dyad_pitch_policy.py`; pre-registration commit `5ff7c68f1772150ce92d0bf9911c5145d6dda4b3`.
- Deterministic synthetic tests `modal/tests/test_v144_rhythm_onset_dyad_pitch_policy.py`; commit `48818926a12505cc40f0dc534c15a71d09c72719`.
- CPU-gate wiring commit `657f677af8321f1f7312f9e3280f7efae6f31fd9`; run `32975186364` currently IN PROGRESS.
- Construction is deliberately narrow: generated and reference fit onsets must each contain exactly two notes, on the same two distinct strings; both notes must require non-zero pitch changes; target fret must equal the tuning-derived same-string fret; linked pitch-technique events are excluded.
- Rule identity: one shared reference-free structural onset signature (`measurePhase`, `section16`, `stepParity`, `stepQuarter`, or `measurePhaseStep`) plus exactly two locked note rules `{stringIndex, sourcePitchClass, semitoneShift}` sorted by string.
- Both note shifts are required non-zero; fixed pitch bound ±12; minimum support `3`; maximum candidates `256`.
- Runtime receives generated onset + locked structural signature/note rules only; no professional reference. It requires an exact two-note onset matching both source strings/pitch classes and applies both fret/MIDI shifts atomically. If either event is linked or either target fret is invalid, the entire dyad is skipped.
- Runtime preserves event count/order, measure, step/timing, strings, duration, techniques and all non-pitch metadata. MIDI/fret move together on each changed event.
- Candidate construction/ranking has **not** been run. No search file, search tests, one-shot workflow, validation/canary result, or promotion exists.

## Immediate next actions
1. Resolve policy CPU gate `32975186364`; if it fails, fix policy/tests only—do not implement search or evaluate candidates.
2. Only after policy gate SUCCESS implement search-level logic/invariants against accepted SHA `5b36270a...`, then pass another CPU gate.
3. Only after search gate SUCCESS allow at most one exact-message/path-gated CPU one-shot with fixed support `3`, max candidates `256`, pitch bound `12`; archive immediately after one run.
4. Maintain fit-only construction/ranking → one locked winner → validation → canary → full-gold → independent PDF invariant; later failure means current-baseline fallback and no alternate selection.
5. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit user authorization.
