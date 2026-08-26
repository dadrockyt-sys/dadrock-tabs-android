# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Accepted calibration baseline remains `pitch-position-shift-54a6e8d3aa91c422` (1144 events / 113 measures / SHA `5b36270a...`). Nine earlier candidate families are consumed/sealed. Both current-baseline FIT-only diagnostics are complete/sealed. Family #10 — atomic singleton-onset pitch+explicit-string replacement — is PRE-REGISTERED and its policy CPU gate is now SUCCESS. No family #10 search exists yet; no FIT candidate rules have been constructed/ranked/evaluated. Production remains untouched.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Frozen V5 result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Original V5 professional one-shot holdout permanently consumed; never rerun/retry/retune V5 from V144 evidence.
- `main`, Production, `/ai-tab` frontend, Bass/Lead, and `freezeReady=false` remain untouched.
- **No Modal/L4/GPU without fresh explicit user authorization. None has been used in V144.**

## Gold calibration semantics / fixed selector
- Professional target is a **gold calibration benchmark, not unseen holdout**.
- Structured reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; 113 measures / 603 playable onsets / 946 notes / 104 populated measures.
- Deterministic split: measure+step, seed 144, 60% fit / 20% validation / 20% canary.
- Fit labels may construct/rank; validation/canary only gate one locked winner.
- Fixed fit gate: pitch-content gain >= `0.005`; no musical metric regression; no critical mismatch increase; PDF-event fidelity `1.0`.
- Preserve all 113 generated measures; count-preserving families preserve 1144 events.
- Fixed gate order: fit → validation → canary → full-gold → independent PDF-event invariant.
- Any later failure means deterministic accepted-baseline fallback; never select an alternate.
- Never change thresholds/support from observed outcomes. Never claim unseen generalization.

## Accepted V144 Rhythm calibration baseline — LOCKED / UNCHANGED
- Name `pitch-position-shift-54a6e8d3aa91c422`.
- Manifest `debug/v144-rhythm-calibration/selected/v144-pitch-position-selected-baseline.json`; commit `0b55bc1f3e2fdefe179f3eb17bd81be2a0574d31`; blob `45287a40fbbe88f411d2eca7db3cce072174eda8`.
- Transform chain: historical triple prune → same-string pitch shift → joint pitch+adjacent-string revoice `pitchClass::11 && stepParity::0 => pitch -2, string +1`.
- 1144 events; event/PDF SHA `5b36270aaeafa73b2e25722e2576a40424ce5951dcfd2b5d769746bd9eb07e0d`; 113/113 measures; PDF fidelity `1.0`.
- Full gold: critical `1754`; pitch `0.32822966507177037`; pitch/timing `0.06411483253588517`; string/fret/timing `0.045933014354066985`; chord/voicing `0.038700760193503804`; coverage `1.0`.
- Calibration-only: Production false; Rhythm complete false; near-100 false; unseen generalization false.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1. Single-signature prune — failed validation.
2. Two-signature prune — failed final measure-set invariant.
3. Triple prune — historical accepted baseline.
4. Additive four-signature prune — none fit-qualified; sealed `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Same-string contextual pitch shift — prior accepted baseline; sealed `21ca074f3917fb72614686ca5b46a3894ea53374`.
6. Joint contextual pitch+step — failed canary; sealed `215fc49106ef3501b71452b1f6c9f6d638cafd77`.
7. Joint contextual pitch+adjacent-string position — current accepted baseline; run `32971373324`; sealed `61422dea64ed4758999b3cd3c978d0db344e3ef6`.
8. Joint contextual pitch+step+adjacent-string position — no fit-qualified winner; run `32974497513`; sealed `55a948fa97ab100bdca0b1338b36c9a43a4f5ce9`.
9. Atomic exact-two-note onset dyad pitch rewrite — zero supported rules / zero candidates; run `32975912923`; report blob `9b1099e42f57127a9cf3168471fdb49415067f5f`; sealed `6e0e23254a4e6c845c681368a96e1623f04364bd`.

## Current-baseline FIT-only diagnostics — COMPLETE / SEALED
### Mechanism diagnostic
- CPU gate `32971927840` SUCCESS; diagnostic run `32972033516` SUCCESS.
- Report commit `3bed803a666d105cd95c96c94ab7beb192c2241e`; blob `dbc0c1ab0cfff943f95eab48720c7c2a5eb9d175`; workflow sealed `a6d5ddf373de8a71facf8474d48550aa990d7d54`.
- Candidate construction/ranking/selection false; validation/canary false; runtime reference false; GPU false.
- Shape signals: same-onset wrong-pitch substitutions `171`; displaced existing pitch matches `120`; tight pitch/string-fret mismatches `12`.

### Onset-topology diagnostic
- Analyzer commit `2fd4fffc17111be8acb1741985ff9ece32a630d5`; blob `b4ddb289e2e0e54177e51e1b4ff1140dd304ed46`; pre-label CPU gate `32988449841` SUCCESS.
- Successful one-shot run `32992367811`: CPU prerequisite `98252843458` SUCCESS; diagnostic job `98252964359` SUCCESS.
- Report persistence commit `cbe6bcf73862ef8f15bf1bad306f746f6f022301`; blob `26e1265adf5c1c11838c207b4c5af0927f26b95b`; bot commit added only the report.
- FIT topology: generated onsets `485`; reference `370`; shared `190`; generated-only `295`; reference-only `180`; singleton→singleton `100`; singleton exact-pitch same-string `17`; singleton wrong-pitch same-string `5`; singleton wrong-pitch different-string `78`; shared cardinality mismatch `84`; equal-cardinality multi-note only `6`; dyad→dyad only `5`.
- Diagnostic execution surfaces sealed/deleted; PR #21 closed/draft/unmerged against inert `noop`.

## Family #10 — atomic singleton-onset pitch+explicit-string replacement — POLICY CPU PASSED
### Fixed family shape
- Shape derived only from sealed FIT-only aggregate diagnostics while accepted baseline is unchanged.
- Exactly one generated note and one reference note at the same FIT onset.
- Both pitch and string must change.
- Explicit `sourceStringIndex` → `targetStringIndex` rule identity; non-adjacent targets allowed. This is not a replay of adjacent-string family #7.
- Atomic unit is one singleton onset, not dyad family #9.
- Cardinality-changing edits excluded.
- Runtime reference forbidden; linked pitch techniques excluded.
- Only `stringIndex`, `fret`, `midi` may change; count/order/measure/step/timing/duration/techniques/other metadata preserved.

### Policy identity
- Policy `modal/v144_rhythm_singleton_onset_replacement_policy.py`.
- Pre-registration commit `9f1d4d609f62a6f75f0b708d9eb6efff2118a8d3`; blob `1e05e66a3523f98944370837a59e5d6e7293f9ac`.
- Fixed support `3`; max candidates `256`; max absolute pitch shift `12` semitones.
- Rule identity: one structural onset context signature + `sourceStringIndex` + `sourcePitchClass` + explicit `targetStringIndex` + `semitoneShift`.
- Structural signatures: `measurePhase`, `section16`, `stepParity`, `stepQuarter`, or `measurePhaseStep` only.

### Synthetic tests / CPU proof
- Tests `modal/tests/test_v144_rhythm_singleton_onset_replacement_policy.py`; commit `4f6c22ac2c01227beebb75517aa50d48ac267696`; blob `a4e1c52e5f63187e8bad5f853300e644f056e726`.
- CPU wiring commit `ba14cf61443bc32d7cdad2ab64af7df100a0b09b`; workflow blob `c552c378f40a6a86527e6af18db15f34dd880daa`.
- **Policy CPU gate run `32994157957` SUCCESS; job `98258911576` SUCCESS.**
- Logs explicitly show policy `py_compile` SUCCESS and all 7 singleton policy tests SUCCESS:
  - deterministic construction under reversal.
  - shared-singleton + both pitch/string change requirement.
  - invalid rule/context/shift rejection.
  - linked/invalid target skip.
  - supported/capped ranking with explicit non-adjacent target.
  - exact singleton source/context runtime matching.
  - non-adjacent atomic rewrite with metadata preservation.
- Immutable V5/provenance/config guards all passed in the same job.
- PR #21 was reopened only as inert `noop` CPU-delivery fallback, then immediately closed again; never merged, never targeted `main`.
- **No family #10 search exists yet. No FIT candidate rule has been constructed/ranked/evaluated. Validation/canary remain closed.**

## Immediate next actions
1. Pre-register deterministic family #10 search implementation before opening FIT labels. Fixed parameters remain support `3`, max candidates `256`, pitch bound `12`; no changes permitted from observed outcomes.
2. Search must reconstruct the accepted baseline reference-free from frozen V5; rank rules using FIT only; lock at most one FIT winner; then gate exactly validation → canary → full gold → independent PDF-event fidelity; later failure => accepted-baseline fallback, never alternate selection.
3. Add strict event invariant proving only the locked singleton event's `midi`, `fret`, and `stringIndex` may change; count/order/timing/measure/step/duration/techniques/metadata must remain exact; target fret must satisfy tuning identity.
4. Add deterministic synthetic search/invariant tests and CPU-gate search + tests before any one-shot candidate evaluation.
5. If no rule meets fixed support/shape or no FIT candidate passes the fixed gate, seal family #10 at FIT without relaxing anything.
6. Keep `pitch-position-shift-54a6e8d3aa91c422` / SHA `5b36270a...` as baseline unless a future fully gated family passes every invariant.
7. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit authorization.
