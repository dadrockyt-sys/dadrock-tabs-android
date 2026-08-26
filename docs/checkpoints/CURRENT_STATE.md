# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Current accepted calibration baseline remains `pitch-position-shift-54a6e8d3aa91c422` (1144 events / 113 measures / SHA `5b36270a...`). Nine candidate families are consumed and sealed. The diagnostic-only current-baseline FIT onset-topology analyzer passed its required pre-label CPU gate. A temporary inert-base PR delivery run reached the one-shot wrapper but failed BEFORE the analyzer executed because the wrapper referenced a nonexistent manifest key (`canonicalEvents`). Gold FIT labels were NOT read by that failed attempt. No candidate/rule/shift/ranking was emitted and no successor family is pre-registered. Production remains untouched.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Frozen V5 result blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical V5 event SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Original V5 professional one-shot holdout permanently consumed; never rerun/retry/retune V5 from V144 evidence.
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
- Preserve all 113 generated measures; count-preserving correction families preserve 1144 events.
- Fixed order: fit → validation → canary → full-gold → independent PDF-event invariant.
- Later failure means deterministic accepted-baseline fallback; never select an alternate.
- Never change thresholds/support from observed outcomes.

## Accepted V144 Rhythm calibration baseline — LOCKED / UNCHANGED
- Name `pitch-position-shift-54a6e8d3aa91c422`.
- Manifest `debug/v144-rhythm-calibration/selected/v144-pitch-position-selected-baseline.json`; commit `0b55bc1f3e2fdefe179f3eb17bd81be2a0574d31`; blob `45287a40fbbe88f411d2eca7db3cce072174eda8`.
- Transform chain: historical triple prune → same-string pitch shift → joint pitch+adjacent-string revoice `pitchClass::11 && stepParity::0 => pitch -2, string +1`.
- 1144 events; SHA/PDF `5b36270aaeafa73b2e25722e2576a40424ce5951dcfd2b5d769746bd9eb07e0d`; 113/113 measures; PDF fidelity `1.0`.
- Full gold: critical `1754`; pitch `0.32822966507177037`; pitch/timing `0.06411483253588517`; string/fret/timing `0.045933014354066985`; chord/voicing `0.038700760193503804`; coverage `1.0`.
- Calibration-only: Production false; Rhythm complete false; near-100 false; unseen generalization false.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1. Single-signature prune — failed validation.
2. Two-signature prune — failed final measure-set invariant.
3. Triple prune — historical accepted baseline.
4. Additive four-signature prune — none fit-qualified; sealed `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Same-string contextual pitch shift — prior accepted baseline; sealed `21ca074f3917fb72614686ca5b46a3894ea53374`.
6. Joint contextual pitch+step — failed canary; sealed `215fc49106ef3501b71452b1f6c9f6d638cafd77`.
7. Joint contextual pitch+adjacent-string position — current accepted baseline; run `32971373324`; report blob `04a462983bf4c50364d0e4f39bcd08a5652c6b5e`; sealed `61422dea64ed4758999b3cd3c978d0db344e3ef6`.
8. Joint contextual pitch+step+adjacent-string position — 14 fit candidates, none qualified; run `32974497513`; report blob `c67bad28dea2ee7458a4e8159d5b7ab64fdce245`; sealed `55a948fa97ab100bdca0b1338b36c9a43a4f5ce9`.
9. Atomic exact-two-note onset dyad pitch rewrite — zero rules met pre-registered support/shape requirements; zero candidates evaluated; run `32975912923`; report commit `8d4c65a3abd10a7c4cbd1e979c89457b9a557c1d`; report blob `9b1099e42f57127a9cf3168471fdb49415067f5f`; sealed `6e0e23254a4e6c845c681368a96e1623f04364bd`; archived workflow blob `869c625913625806555184beef8ff33943304ce4`.

## Current-baseline fit-only diagnostic — COMPLETE / SEALED
- CPU gate `32971927840` SUCCESS; diagnostic run `32972033516` SUCCESS.
- Report `debug/v144-rhythm-calibration/diagnostics/current-pitch-position-baseline-fit-mechanisms.json`; commit `3bed803a666d105cd95c96c94ab7beb192c2241e`; blob `dbc0c1ab0cfff943f95eab48720c7c2a5eb9d175`; workflow sealed `a6d5ddf373de8a71facf8474d48550aa990d7d54`.
- Candidate construction/ranking/selection false; validation/canary labels false; runtime reference false; GPU false.
- Fit: generated `643`, reference `594`, critical `1075`; pitch `161` / F1 `0.26030719482619236`; tight pitch/timing `41` / F1 `0.06628940986257073`; gross ±2-step matches `81`; exact string/fret/timing `29` / F1 `0.04688763136620856`; chord/voicing `0.03976608187134503`.
- Shape signals: same-onset wrong-pitch substitutions `171`; displaced existing pitch matches `120`; tight pitch/string-fret mismatches `12`.
- This sealed fit-only diagnostic remains a permissible source for family-shape analysis while the accepted baseline is unchanged. **Do not use fit/validation/canary/full outcomes from consumed searches to construct/rank a successor.**

## Atomic onset dyad family — COMPLETE / CONSUMED / SEALED
- Policy `modal/v144_rhythm_onset_dyad_pitch_policy.py`; pre-registration commit `5ff7c68f1772150ce92d0bf9911c5145d6dda4b3`; blob `09deedbb5f31c3a7f0573d9e68f78f956f692c1c`.
- Policy tests commit `48818926a12505cc40f0dc534c15a71d09c72719`; blob `0c4d7508267a4f06e71d518a50d6d67eafd44335`; policy CPU gate `32975186364` SUCCESS.
- Search `validation/v144_rhythm_calibration/search_atomic_onset_dyad_pitch_rewrites.py`; commit `002e79d561e4404ea00d7a58ec591d006802bf00`; blob `235f88fd4ed881231d23532e04cc148b756eebf4`.
- Search tests commit `41f49951cb8b7325e608402f5cda69407c21ce22`; blob `bc2583853b89b7422c7595b3218fc477177ed93a`; search CPU gate `32975651407` SUCCESS.
- One-shot arming commit `b84dedb8350a4568adc40d6e6b4787d409d6d30d`; run `32975912923` SUCCESS infrastructure; CPU only; fixed support `3`, max candidates `256`, pitch bound `12`.
- Report `debug/v144-rhythm-calibration/candidates/atomic-onset-dyad-pitch-search.json`; persisted commit `8d4c65a3abd10a7c4cbd1e979c89457b9a557c1d`; blob `9b1099e42f57127a9cf3168471fdb49415067f5f`.
- `rankedRuleCount=0`; `evaluatedCandidateCount=0`; validation/canary/full all `null`; deterministic accepted-baseline fallback retained.
- Workflow archived immediately: commit `6e0e23254a4e6c845c681368a96e1623f04364bd`; blob `869c625913625806555184beef8ff33943304ce4`; replay refused.

## Current-baseline FIT onset-topology diagnostic — PRE-RUN / CPU GATE PASSED / WRAPPER FIX REQUIRED
- Implementation `validation/v144_rhythm_calibration/analyze_current_baseline_fit_onset_topology.py`; commit `2fd4fffc17111be8acb1741985ff9ece32a630d5`; blob `b4ddb289e2e0e54177e51e1b4ff1140dd304ed46`.
- Synthetic tests `modal/tests/test_v144_rhythm_current_baseline_fit_onset_topology.py`; initial commit `03becc266d7fe32980a8425ead72c0ce8f1fc3f3`; gate-tested blob `8c47a13f459832bbe564a080ab0e984edd3a9c25`.
- Broad CPU-gate wiring commit `073d276bcae5873bfed104eda34aebe7c19a0b49`; original topology-wired workflow blob `0102223c67e4a489dda2e5c88808c0a1dad7c240`.
- Temporary draft PR #21 targets inert branch `noop`, never `main`, and has never been merged.
- **Pre-label CPU gate `32988449841` SUCCESS.** Job `98240070427` explicitly compiled the topology analyzer, ran all five topology synthetic tests successfully, verified immutable V5 identities/provenance, and kept config CPU-safe/fallback-first.
- User manual retrigger commit `c58917b950cf5c5c3f173f49a9899c4b97eaeff8` added only one comment after `unittest.main()`; executable analyzer remains exact blob `b4ddb289...`.
- Standalone push one-shot workflow `.github/workflows/v144-current-fit-onset-topology-diagnostic-one-shot.yml`; pre-registration commit `d16388a0bdd2996b594184ff519eea02b53de403`; blob `c66b4c782967c1b00b783cf43e4fefafd2fcfaa4`. Repository push→Actions scheduling did not create its run.
- Temporary PR-delivery one-shot job was added to `.github/workflows/v144-rhythm-cpu-gate.yml` at commit `bdc6840fb852525572079326acb48d767e51aa80`; workflow blob `53696e21d088dced1fb06d711b62f604e2c4fa6a`.
- PR-delivery arming head `8fbf82580995f3c35e3ede37a6fd7158f07a152b`; exact message `v144 execute current fit onset topology diagnostic one-shot`; only trigger file changed. PR #21 was reopened against inert `noop`, then reclosed without merge.
- Delayed PR run `32990041415` materialized. CPU prerequisite job `98245212543` **SUCCESS**: immutable guards, compilation, all topology tests, config guards passed.
- One-shot job `98245334632` **FAILED BEFORE diagnostic execution** in `Verify exact one-shot arming commit and immutable identities`: wrapper used `manifest['canonicalEvents']`, but the accepted manifest stores identity under `manifest['selectedCandidate']`. Error was `KeyError: 'canonicalEvents'`.
- Diagnostic step, isolation verification, and report persistence were all skipped. **No gold FIT labels were read by run `32990041415`; no topology report exists from that attempt.**
- Fix scope is wrapper-only: change those three manifest assertions from `canonicalEvents` to `selectedCandidate`. Do not alter analyzer, tests, baseline, reference, selector, thresholds, or topology semantics.
- Analyzer isolation remains: candidate construction/ranking/selection false; no rule/shift histogram; validation/canary false; runtime reference false; GPU false.

## Immediate next actions
1. Correct only the PR one-shot wrapper manifest assertions to use `selectedCandidate`; update the exact trigger workflow blob identity and checkpoint the fix.
2. Re-arm via inert `noop` PR event only after the broad CPU prerequisite remains green; exact trigger commit must change only the trigger path and use the exact message.
3. If the topology diagnostic succeeds, verify the persisted report identity/isolation, then immediately remove/archive both executable one-shot surfaces and refuse replay.
4. Interpret only aggregate FIT topology to decide whether a genuinely new transformation unit is justified. Never use consumed-family outcomes, validation, or canary to choose the shape.
5. If a successor unit is justified, pre-register it before candidate evaluation and follow policy/tests → CPU gate → search/invariants → CPU gate → at most one one-shot → immediate archive.
6. Keep `pitch-position-shift-54a6e8d3aa91c422` / SHA `5b36270a...` as baseline unless a future fully gated family passes every invariant.
7. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit user authorization.
