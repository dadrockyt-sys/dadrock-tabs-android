# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Current accepted calibration baseline remains `pitch-position-shift-54a6e8d3aa91c422` (1144 events / 113 measures / SHA `5b36270a...`). Nine candidate families are consumed and sealed. The current-baseline FIT onset-topology analyzer passed its required pre-label CPU gate. The PR-delivery wrapper manifest-key bug has been corrected and a trigger-only retry was armed, but its exact-SHA run `32991337100` executed the CPU prerequisite successfully and SKIPPED the one-shot job. Therefore the topology analyzer still has NOT read gold FIT labels and no topology report exists. PR #21 is closed, draft, unmerged, and targets only inert `noop`. No successor family is pre-registered. Production remains untouched.**

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

## Current-baseline fit-only mechanism diagnostic — COMPLETE / SEALED
- CPU gate `32971927840` SUCCESS; diagnostic run `32972033516` SUCCESS.
- Report `debug/v144-rhythm-calibration/diagnostics/current-pitch-position-baseline-fit-mechanisms.json`; commit `3bed803a666d105cd95c96c94ab7beb192c2241e`; blob `dbc0c1ab0cfff943f95eab48720c7c2a5eb9d175`; workflow sealed `a6d5ddf373de8a71facf8474d48550aa990d7d54`.
- Candidate construction/ranking/selection false; validation/canary labels false; runtime reference false; GPU false.
- Fit: generated `643`, reference `594`, critical `1075`; pitch `161` / F1 `0.26030719482619236`; tight pitch/timing `41` / F1 `0.06628940986257073`; gross ±2-step matches `81`; exact string/fret/timing `29` / F1 `0.04688763136620856`; chord/voicing `0.03976608187134503`.
- Shape signals: same-onset wrong-pitch substitutions `171`; displaced existing pitch matches `120`; tight pitch/string-fret mismatches `12`.
- This sealed fit-only diagnostic remains permissible while baseline is unchanged. Never use validation/canary/full outcomes from consumed searches to construct/rank a successor.

## Current-baseline FIT onset-topology diagnostic — PRE-RUN / CPU GATED / DELIVERY EVENT ISSUE
- Analyzer `validation/v144_rhythm_calibration/analyze_current_baseline_fit_onset_topology.py`; commit `2fd4fffc17111be8acb1741985ff9ece32a630d5`; blob `b4ddb289e2e0e54177e51e1b4ff1140dd304ed46`.
- Synthetic tests `modal/tests/test_v144_rhythm_current_baseline_fit_onset_topology.py`; five deterministic tests. User manual comment commit `c58917b950cf5c5c3f173f49a9899c4b97eaeff8` changed only one comment; analyzer executable unchanged.
- **Required pre-label CPU gate `32988449841` SUCCESS**, job `98240070427`: compiled analyzer, ran all five topology tests, immutable V5/provenance/config guards all passed.
- Standalone push one-shot `.github/workflows/v144-current-fit-onset-topology-diagnostic-one-shot.yml`; pre-registration commit `d16388a0bdd2996b594184ff519eea02b53de403`; blob `c66b4c782967c1b00b783cf43e4fefafd2fcfaa4`. Push→Actions scheduling remains unreliable, so it has not executed.
- Temporary PR-delivery one-shot job lives in `.github/workflows/v144-rhythm-cpu-gate.yml`; corrected current workflow blob `77f68a57ba55f0e2e0116c79b3b8e0e8d08b4b86`. Original topology-only broad workflow to restore after success is blob `0102223c67e4a489dda2e5c88808c0a1dad7c240` at commit `073d276bcae5873bfed104eda34aebe7c19a0b49`.
- First PR-delivery attempt run `32990041415`: CPU job SUCCESS; one-shot wrapper FAILED before analyzer because it used nonexistent `manifest['canonicalEvents']`; diagnostic step skipped, so no FIT labels read.
- Wrapper was corrected to `selected = manifest.get('selectedCandidate') or {}` and checks `eventCount=1144`, `generatedMeasureCount=113`, event SHA `5b36270a...`; analyzer/reference/baseline/selector unchanged.
- Corrected trigger-only arming commit `f61b75a92392e7e6382787921c323c1a2fc94685`; parent `a41fa13255158bf13b140ddb6d14525b6db5ef9f`; exact message `v144 execute current fit onset topology diagnostic one-shot`; only trigger file changed. Trigger blob `4e5e8fa90535d9f901bd89dddf0e09b456b153c6`, locking workflow blob `77f68a57...` and analyzer blob `b4ddb289...`.
- Exact-SHA run `32991337100`: CPU prerequisite job `98249351510` **SUCCESS** on head `f61b75a9...`; one-shot job `98249470077` was **SKIPPED** at job condition, with no steps executed. Therefore this run also read no FIT labels and created no report.
- A separate earlier delayed CPU-only run `32990742872` corresponded to an older PR event/workflow head and did not execute the one-shot.
- PR #21 is now **closed**, draft, unmerged, base `noop`, head branch `v143-contextual-prune-lobo`; it never targeted `main`.
- Report path `debug/v144-rhythm-calibration/diagnostics/current-pitch-position-baseline-fit-onset-topology.json` does not exist at this checkpoint.
- Analyzer isolation remains: candidate construction/ranking/selection false; no rule/shift histogram; validation/canary false; consumed-family outcomes excluded; runtime reference false; GPU false.

## Immediate next actions
1. Let already-queued PR events drain while PR #21 remains closed; do not emit duplicate events that could race a delayed one-shot.
2. Determine why exact-SHA run `32991337100` skipped the one-shot condition. Fix delivery condition only; do not alter analyzer/tests/reference/baseline/selector/thresholds/topology semantics.
3. Re-arm at most one safe event after the queue is drained. Ensure the CPU prerequisite succeeds before the one-shot and exact trigger-only identity is verified before labels are opened.
4. If the topology diagnostic succeeds, verify the persisted report identity/isolation, immediately close PR #21, restore broad CPU workflow to topology-only form, archive/delete standalone executable one-shot and trigger surface, and refuse replay.
5. Interpret only aggregate FIT topology to decide whether a materially distinct transformation unit is justified. Never use consumed-family outcomes, validation, or canary to choose the shape.
6. If justified, pre-register the successor before candidate evaluation and follow policy/tests → CPU gate → search/invariants → CPU gate → at most one one-shot → archive.
7. Keep `pitch-position-shift-54a6e8d3aa91c422` / SHA `5b36270a...` as baseline unless a future fully gated family passes every invariant.
8. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit authorization.
