# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Accepted baseline remains `pitch-position-shift-54a6e8d3aa91c422` (1144 events / 113 measures / SHA `5b36270a...`). Families 1–9 are consumed/sealed. Both current-baseline FIT-only diagnostics are complete/sealed. Family #10 — atomic singleton-onset pitch+explicit-string replacement — has a pre-registered policy AND pre-registered deterministic search; both policy and search CPU gates are SUCCESS. No family #10 calibration search has been executed yet, so no FIT candidate rule has been constructed/ranked/evaluated and validation/canary remain closed. Production remains untouched.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Frozen V5 result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Original V5 professional one-shot holdout permanently consumed; never rerun/retry/retune V5 from V144 evidence.
- `main`, Production, `/ai-tab` frontend, Bass/Lead, `freezeReady=false` untouched.
- **No Modal/L4/GPU without fresh explicit user authorization. None has been used in V144.**

## Gold calibration / fixed selector
- Professional target is a **gold calibration benchmark, not unseen holdout**.
- Structured reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; 113 measures / 603 playable onsets / 946 notes / 104 populated measures.
- Split measure+step seed 144: 60% fit / 20% validation / 20% canary.
- Fit may construct/rank. Validation/canary only gate ONE locked winner.
- Fixed fit gate: pitch-content gain >= `0.005`; no musical metric regression; no critical mismatch increase; PDF-event fidelity `1.0`.
- Preserve all 113 generated measures; count-preserving families preserve 1144 events.
- Gate order fixed: fit → validation → canary → full-gold → independent PDF-event invariant.
- Any later failure => deterministic accepted-baseline fallback; never select an alternate.
- Never change thresholds/support from observed outcomes; never claim unseen generalization.

## Accepted V144 Rhythm baseline — LOCKED / UNCHANGED
- `pitch-position-shift-54a6e8d3aa91c422`.
- Manifest `debug/v144-rhythm-calibration/selected/v144-pitch-position-selected-baseline.json`; blob `45287a40fbbe88f411d2eca7db3cce072174eda8`.
- Transform chain: historical triple prune → same-string pitch shift → adjacent-string pitch-position revoice.
- 1144 events / 113 measures / event+PDF SHA `5b36270aaeafa73b2e25722e2576a40424ce5951dcfd2b5d769746bd9eb07e0d`; PDF fidelity 1.0.
- Full gold: critical `1754`; pitch `0.32822966507177037`; pitch/timing `0.06411483253588517`; string/fret/timing `0.045933014354066985`; chord/voicing `0.038700760193503804`; coverage 1.0.
- Calibration baseline true; Production false; Rhythm complete false; near-100 false; unseen-generalization false.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1. Single-signature prune — failed validation.
2. Two-signature prune — failed measure-set invariant.
3. Triple prune — historical accepted baseline.
4. Additive four-signature prune — no fit-qualified; sealed `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Same-string contextual pitch shift — prior accepted baseline; sealed `21ca074f3917fb72614686ca5b46a3894ea53374`.
6. Joint contextual pitch+step — failed canary; sealed `215fc49106ef3501b71452b1f6c9f6d638cafd77`.
7. Joint contextual pitch+adjacent-string position — current accepted baseline; run `32971373324`; sealed `61422dea64ed4758999b3cd3c978d0db344e3ef6`.
8. Joint contextual pitch+step+position — no fit-qualified; run `32974497513`; sealed `55a948fa97ab100bdca0b1338b36c9a43a4f5ce9`.
9. Atomic exact-two-note onset dyad pitch rewrite — zero supported rules / zero candidates; run `32975912923`; report blob `9b1099e42f57127a9cf3168471fdb49415067f5f`; sealed `6e0e23254a4e6c845c681368a96e1623f04364bd`.

## Sealed current-baseline FIT-only diagnostics
### Mechanism diagnostic
- CPU `32971927840` SUCCESS; diagnostic `32972033516` SUCCESS; report blob `dbc0c1ab0cfff943f95eab48720c7c2a5eb9d175`; workflow sealed `a6d5ddf373de8a71facf8474d48550aa990d7d54`.
- Shape signals: same-onset wrong-pitch substitutions `171`; displaced existing pitch matches `120`; tight pitch/string-fret mismatches `12`.
### Onset-topology diagnostic
- Analyzer blob `b4ddb289e2e0e54177e51e1b4ff1140dd304ed46`; pre-label CPU `32988449841` SUCCESS.
- Successful one-shot `32992367811`; report persistence commit `cbe6bcf73862ef8f15bf1bad306f746f6f022301`; report blob `26e1265adf5c1c11838c207b4c5af0927f26b95b`.
- FIT topology: generated onsets `485`; reference `370`; shared `190`; generated-only `295`; reference-only `180`; singleton→singleton `100`; exact-pitch same-string `17`; wrong-pitch same-string `5`; wrong-pitch different-string `78`; shared cardinality mismatch `84`; dyad→dyad only `5`.
- Diagnostic execution surfaces deleted/sealed; no replay.

## Family #10 — atomic singleton-onset pitch+explicit-string replacement — SEARCH CPU PASSED / PRE-EXECUTION
### Fixed family/policy
- Shape source: sealed FIT-only aggregate diagnostics only; baseline unchanged.
- Generated + reference each exactly one note at same FIT onset; both pitch and string must change.
- Explicit `sourceStringIndex` → `targetStringIndex`; non-adjacent target allowed. Distinct from consumed adjacent-string family #7 and dyad family #9.
- Cardinality-changing edits excluded; linked pitch techniques excluded; runtime reference forbidden.
- Only `stringIndex`, `fret`, `midi` mutable; count/order/measure/step/timing/duration/techniques/all other metadata preserved.
- Policy `modal/v144_rhythm_singleton_onset_replacement_policy.py`; commit `9f1d4d609f62a6f75f0b708d9eb6efff2118a8d3`; blob `1e05e66a3523f98944370837a59e5d6e7293f9ac`.
- Fixed support `3`; max candidates `256`; max abs pitch shift `12` semitones.
- Policy tests commit `4f6c22ac2c01227beebb75517aa50d48ac267696`; blob `a4e1c52e5f63187e8bad5f853300e644f056e726`.
- Policy CPU run `32994157957`, job `98258911576`: SUCCESS; all 7 policy tests passed.

### Pre-registered search
- Search `validation/v144_rhythm_calibration/search_atomic_singleton_onset_replacements.py`.
- Search pre-registration commit `33bc68a24057e141a5e426439ec588f99b5fe79e`; blob `70880d26418d907cc702233af37bcc4b643e3a57`.
- Search code enforces fixed parameters exactly: support `3`, max candidates `256`, semitone bound `12`; execution-time variation is rejected.
- Search reconstructs current accepted baseline reference-free from immutable V5 and the frozen triple/pitch/position policies.
- Candidate name/rule identity: structural onset context + source string + source pitch class + explicit target string + semitone shift.
- FIT-only ranking; at most one fit-locked winner; later stages exact validation → canary → full calibration; no alternate after failure.
- Strict `changed_event_count` invariant: event count/order exact; all fields except `midi/fret/stringIndex` exact; changed onset must be singleton; pitch AND string both change; tuning-derived target position; max delta 12; locked source/context/target/shift enforced.
- Search emits a locked event stream for later independent PDF-event proof but does not itself claim PDF/full invariant completion.
- Search tests `modal/tests/test_v144_rhythm_singleton_onset_replacement_search.py`; commit `142364f38839c5823f91e1131387f77adec833dd`; blob `3a2adbecbe810e6738718fc72e2cf231555e8c3e`.
- Seven synthetic search invariant tests cover deterministic rule naming, valid non-adjacent singleton changes, singleton-only onset requirement, event count/order/metadata protection, pitch-only/string-only/tuning rejection, locked source/context/target/shift enforcement, and immutable fixed search parameters.
- CPU workflow wiring commit `b1ce9f263139ae1bf23f30d2264cce97d9e2af64`; workflow blob `961f65cc31e64527fb0510d98211b2a7f2b990cc`.
- **Search CPU gate run `32995017936`, job `98261834131`: SUCCESS.** Logs explicitly show search `py_compile` SUCCESS and all 7 singleton search invariant tests SUCCESS; immutable V5/provenance/config guards passed.
- **No family #10 search has executed against calibration labels yet. No ranked rule/candidate outcome exists. Validation/canary remain closed.**

## Immediate next actions
1. Pre-register exactly one CPU-only family #10 one-shot workflow. It must lock V5/reference/manifest/policy/search/test/config/selector blobs; exact commit message/path gate; no Modal/GPU.
2. One-shot runs search exactly once with fixed `3 / 256 / 12`, verifies construction isolation and staged-stop semantics, then independently re-freezes the locked stream and proves PDF-event fidelity 1.0 without opening reference during PDF proof.
3. Full invariant (only if split gates passed): 1144 events, 113 measures, singleton/pitch+string/tuning/metadata invariants, measure coverage 1.0, no gated metric regressions, critical mismatch delta <=0, PDF fidelity 1.0. Failure => accepted-baseline fallback.
4. Persist ONLY the family #10 report. Immediately archive/delete one-shot workflow and refuse replay regardless outcome.
5. If no supported rules or no FIT-qualified winner, seal family #10 at FIT without changing support/thresholds/family shape.
6. Keep current accepted baseline unless the one locked family #10 winner passes every fixed gate/invariant. Never start Bass/Lead/main/Production/near-100/GPU work.
