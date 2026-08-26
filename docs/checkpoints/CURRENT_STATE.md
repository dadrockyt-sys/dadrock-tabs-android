# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Current accepted calibration baseline remains `pitch-position-shift-54a6e8d3aa91c422` (1144 events / 113 measures / SHA `5b36270a...`). Eight candidate families are consumed and sealed. The materially distinct atomic exact-two-note onset dyad pitch-rewrite family is pre-registered; policy gate `32975186364` passed. Search + search-level invariant tests now exist and CPU search gate `32975651407` is queued/running. No candidate evaluation or one-shot workflow exists yet. Production remains untouched.**

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

## Atomic exact-two-note onset dyad pitch rewrite — PRE-REGISTERED / SEARCH IMPLEMENTED / NOT EVALUATED
- Materially distinct unit: exactly two events at one onset are transformed atomically; both pitch/fret changes happen together or neither happens.
- Rationale uses only sealed current-baseline fit diagnostic: same-onset wrong-pitch substitutions `171` and fit chord/voicing F1 `0.03976608187134503`.
- Policy `modal/v144_rhythm_onset_dyad_pitch_policy.py`; pre-registration commit `5ff7c68f1772150ce92d0bf9911c5145d6dda4b3`.
- Policy tests `modal/tests/test_v144_rhythm_onset_dyad_pitch_policy.py`; commit `48818926a12505cc40f0dc534c15a71d09c72719`.
- Policy CPU gate wiring `657f677af8321f1f7312f9e3280f7efae6f31fd9`; run `32975186364` SUCCESS.
- Search `validation/v144_rhythm_calibration/search_atomic_onset_dyad_pitch_rewrites.py`; commit `002e79d561e4404ea00d7a58ec591d006802bf00`.
- Search invariants `modal/tests/test_v144_rhythm_onset_dyad_pitch_search.py`; commit `41f49951cb8b7325e608402f5cda69407c21ce22`.
- Search CPU-gate wiring commit `2fd8e1c5752dc34968bf4ad51718ea194cfe4fa0`; run `32975651407` queued/running.
- Construction requires generated/reference fit onsets each have exactly two notes on the same two distinct strings; both shifts non-zero; same-string target fret tuning-derived; linked pitch techniques excluded.
- Rule identity: one shared reference-free structural onset signature plus two `{stringIndex, sourcePitchClass, semitoneShift}` note rules sorted by string.
- Fixed values: support `3`; max candidates `256`; max abs semitone shift `12`.
- Runtime receives generated onset + locked rule only; no professional reference. Exact two-note source dyad required. Invalid/linked either note => atomic skip.
- Search reconstructs exact accepted baseline `5b36270a...` from immutable V5 via historical triple → accepted pitch shift → accepted pitch+position transform before construction.
- Search-level invariants: 1144-event count/order; 113-measure set; measure/step/string/duration/techniques/all non-pitch metadata unchanged; MIDI/fret move together; changed onsets must contain exactly two baseline events and exactly two changed events; both changed strings distinct; locked context/source pitch classes/shifts enforced; tuning identity and ±12 bound enforced.
- Search is fit-only for construction/ranking; validation/canary only gate one locked winner; full-gold is only reached after both split gates.
- **No candidate evaluation workflow, one-shot result, validation/canary outcome, or promotion exists yet.**

## Immediate next actions
1. Resolve search CPU gate `32975651407`; if it fails, fix search/tests only and do not create a one-shot.
2. After search gate SUCCESS, lock exact policy/search/test/config/accepted-manifest blobs and allow at most one exact-message/path-gated CPU one-shot with support `3`, max candidates `256`, pitch bound `12`.
3. Persist only the dyad search report, independently reprove PDF-event identity without opening the reference, then archive the workflow immediately after the single run.
4. Maintain deterministic fallback to current accepted baseline on any fit/validation/canary/full/PDF failure; never select an alternate.
5. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit user authorization.
