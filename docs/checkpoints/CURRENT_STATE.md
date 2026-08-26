# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families 1–9 are consumed/sealed. Family #10 — atomic singleton-onset pitch+explicit-string replacement — is now COMPLETE, SUCCESSFUL, and SEALED. Its one locked winner passed FIT, validation, canary, full-gold, and independent PDF-event invariants. The currently committed selected-baseline manifest still points to the prior `pitch-position-shift-54a6e8d3aa91c422` baseline; no manifest promotion has been performed yet. Production/main/Bass/Lead remain untouched.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Frozen V5 result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Original V5 professional one-shot holdout permanently consumed; never rerun/retry/retune V5 from V144 evidence.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false` untouched.
- **No Modal/L4/GPU without fresh explicit user authorization. None used in V144.**

## Gold calibration / fixed selector
- Professional target is a **gold calibration benchmark, not unseen holdout**.
- Structured reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; 113 measures / 603 playable onsets / 946 notes / 104 populated measures.
- Split measure+step seed 144: 60% fit / 20% validation / 20% canary.
- FIT may construct/rank; validation/canary gate only ONE locked winner.
- Fixed FIT gate: pitch-content gain >= `0.005`; no musical metric regression; no critical mismatch increase; PDF-event fidelity 1.0.
- Preserve all 113 generated measures; count-preserving families preserve 1144 events.
- Gate order fixed: fit → validation → canary → full-gold → independent PDF-event invariant.
- Any later failure => deterministic accepted-baseline fallback; never select an alternate.
- Never change thresholds/support from observed outcomes; never claim unseen generalization.

## Prior accepted V144 Rhythm calibration baseline — STILL THE COMMITTED MANIFEST UNTIL PROMOTION
- Name `pitch-position-shift-54a6e8d3aa91c422`.
- Manifest `debug/v144-rhythm-calibration/selected/v144-pitch-position-selected-baseline.json`; blob `45287a40fbbe88f411d2eca7db3cce072174eda8`.
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
7. Joint contextual pitch+adjacent-string position — prior accepted baseline; run `32971373324`; sealed `61422dea64ed4758999b3cd3c978d0db344e3ef6`.
8. Joint contextual pitch+step+position — no fit-qualified; run `32974497513`; sealed `55a948fa97ab100bdca0b1338b36c9a43a4f5ce9`.
9. Atomic exact-two-note onset dyad pitch rewrite — zero supported rules / zero candidates; run `32975912923`; report blob `9b1099e42f57127a9cf3168471fdb49415067f5f`; sealed `6e0e23254a4e6c845c681368a96e1623f04364bd`.
10. **Atomic singleton-onset pitch+explicit-string replacement — successful winner; completed and sealed in run `32995503662`; do not replay/reselect/retune.**

## Sealed current-baseline FIT-only diagnostics
- Mechanism diagnostic: CPU `32971927840` SUCCESS; diagnostic `32972033516` SUCCESS; report blob `dbc0c1ab0cfff943f95eab48720c7c2a5eb9d175`; workflow sealed `a6d5ddf373de8a71facf8474d48550aa990d7d54`.
- Onset topology diagnostic: pre-label CPU `32988449841` SUCCESS; one-shot `32992367811` SUCCESS; report blob `26e1265adf5c1c11838c207b4c5af0927f26b95b`; execution surfaces sealed/deleted.
- Topology signal that justified family #10: singleton→singleton `100`, of which wrong-pitch different-string `78`, wrong-pitch same-string `5`.

## Family #10 — COMPLETE / SUCCESSFUL / SEALED
### Fixed pre-registered family
- Policy `modal/v144_rhythm_singleton_onset_replacement_policy.py`; commit `9f1d4d609f62a6f75f0b708d9eb6efff2118a8d3`; blob `1e05e66a3523f98944370837a59e5d6e7293f9ac`.
- Policy tests commit `4f6c22ac2c01227beebb75517aa50d48ac267696`; blob `a4e1c52e5f63187e8bad5f853300e644f056e726`.
- Fixed support `3`; max candidates `256`; max absolute pitch shift `12` semitones.
- Exactly one generated + one reference note at a shared FIT onset; both pitch and string change; explicit source→target string; non-adjacent target allowed; cardinality edits excluded; linked pitch techniques excluded.
- Runtime reference forbidden. Only `stringIndex`, `fret`, `midi` may change; all other event metadata/count/order/timing preserved.
- Policy CPU run `32994157957`, job `98258911576`: SUCCESS; all 7 policy tests passed.

### Search preregistration / CPU proof
- Search `validation/v144_rhythm_calibration/search_atomic_singleton_onset_replacements.py`; commit `33bc68a24057e141a5e426439ec588f99b5fe79e`; blob `70880d26418d907cc702233af37bcc4b643e3a57`.
- Search tests `modal/tests/test_v144_rhythm_singleton_onset_replacement_search.py`; commit `142364f38839c5823f91e1131387f77adec833dd`; blob `3a2adbecbe810e6738718fc72e2cf231555e8c3e`.
- Broad CPU workflow blob `961f65cc31e64527fb0510d98211b2a7f2b990cc` at wiring commit `b1ce9f263139ae1bf23f30d2264cce97d9e2af64`.
- Search CPU run `32995017936`, job `98261834131`: SUCCESS; search compiled, all 7 search invariant tests passed, immutable V5/provenance/config guards passed.

### One-shot identity
- One-shot workflow `.github/workflows/v144-atomic-singleton-onset-replacement-search.yml`; preregistration commit `f2eb9e8bbb32f6be5bf34a822ae8b0539e9c162f`; workflow blob `a9bef022032f2d5195dc54ba2a5bd9d7629686da`.
- Trigger commit `ded6bf5d064a5daa02e69e1df4140e9289530960`; trigger blob `bb98a9de3c0ffbaad4dd32aa457d07f703a2bf5b`; changed only trigger path; exact message `v144 execute atomic singleton onset replacement one-shot`.
- One-shot run `32995503662`, job `98263489845`: **SUCCESS end-to-end**.
- All steps SUCCESS: exact immutable trigger verification; fixed search; staged semantics; independent PDF-event proof; final full-gold invariant; post-search immutable recheck; report-only persistence.

### Persisted family #10 report
- Report `debug/v144-rhythm-calibration/candidates/atomic-singleton-onset-replacement-search.json`.
- Persistence commit `ff6165982e8e3036404489c954a7d06ab8a1b015`; report blob `92de07b1cac11cba87e923c18eebf9cce7b0cea7`.
- Bot commit added **only** the 1535-line report.
- `rankedRuleCount=25`; `evaluatedCandidateCount=25`; construction FIT-only; validation/canary did not construct/rank; consumed-family outcomes excluded.

### Locked winner
- Name `singleton-onset-replace-be9e9aa7a734e3cd`.
- Rule: `stepParity::0`; `sourceStringIndex=0`; `sourcePitchClass=4`; `targetStringIndex=3`; `semitoneShift=-12`.
- Candidate event SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`.
- 110 changed events = 110 changed singleton onsets; 1144 total events; 113 generated measures; measure set exact.
- FIT locked winner: pitch-content gain `0.02425222312045272`; chord/voicing gains `0.018713450292397654`; pitch/timing delta `0.0`; string/fret/timing gain `0.008084074373484247`; critical mismatch delta `-18`; no regressions.
- Validation **PASSED**: pitch gain `0.00865800865800867`; chord/voicing `+0.018292682926829278`; pitch/timing `0.0`; string/fret/timing `+0.004329004329004328`; critical `-2`; no regressions.
- Canary **PASSED**: pitch gain `0.005115089514066501`; chord/voicing `+0.022727272727272728`; pitch/timing/string-fret timing each `+0.015345268542199489`; critical `-6`; no regressions.
- Full-gold **PASSED**:
  - critical mismatch `1712` (`-42` vs prior baseline)
  - pitch F1 `0.35406698564593303` (`+0.02583732057416266`)
  - pitch/timing `0.06698564593301436` (`+0.0028708133971291905`)
  - string/fret/timing `0.05454545454545454` (`+0.008612440191387558`)
  - chord pitch-set `0.0580511402902557` (`+0.0193503800967519`)
  - exact voicing `0.0580511402902557` (`+0.0193503800967519`)
  - coverage `1.0`
- Independent PDF-event proof **PASSED**: fidelity `1.0`; event count `1144`; PDF/frozen event SHA exactly `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; professional reference not opened during PDF proof.
- Final full invariant `true`; `calibrationPromotionAllowed=true`; `selected=singleton-onset-replace-be9e9aa7a734e3cd`; `stoppedAt=complete`.
- Safety: V5 false, main false, Production false, runtime reference false, Modal/GPU false; deterministic true.

### Sealing / replay refusal
- Executable one-shot workflow deleted immediately at commit `bb7e96c849a21441547eff0cb2ac7da37eb6e223`.
- Trigger deleted immediately at commit `deeef71043fecb34520e0c0b048eddc1497b1ef5`.
- Family #10 is consumed. **Never rerun, replay, retune, or select an alternate family #10 rule from the 25 candidates.**

## Immediate next actions
1. Inspect the historical selected-baseline manifest promotion pattern and create a **new calibration-only selected baseline manifest** for the family #10 winner; do not overwrite historical evidence blindly.
2. The promotion manifest must lock family #10 report blob/commit, exact winner rule, 1144/113/event SHA `4e6f9f...`, full-gold metrics, PDF proof, safety scope, and provenance that this is a gold-calibration baseline — not unseen generalization and not Production.
3. Add a reference-free deterministic reconstruction test for the promoted chain (V5 → triple → pitch → position → singleton winner) that proves the exact `4e6f9f...` SHA/1144/113 without opening gold labels.
4. CPU-gate that promotion/reconstruction proof before treating family #10 as the new accepted calibration baseline for any successor diagnostic/family.
5. Do not start a new candidate family until the new baseline manifest + reconstruction proof are sealed and checkpointed.
6. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit authorization.
