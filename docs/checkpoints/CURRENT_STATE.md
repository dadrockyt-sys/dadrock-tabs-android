# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Current accepted calibration baseline remains `pitch-position-shift-54a6e8d3aa91c422` (1144 events / 113 measures / SHA `5b36270a...`). Nine candidate families are consumed and sealed. The second current-baseline FIT-only diagnostic — onset topology — is now COMPLETE, persisted, and SEALED. It used FIT labels only, emitted aggregate topology only, constructed/ranked/selected no candidates, and used no validation/canary labels. No successor family has yet been evaluated. Production remains untouched.**

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
- This sealed FIT-only diagnostic remains permissible while baseline is unchanged. Never use validation/canary/full outcomes from consumed searches to construct/rank a successor.

## Current-baseline FIT onset-topology diagnostic — COMPLETE / SEALED
- Analyzer `validation/v144_rhythm_calibration/analyze_current_baseline_fit_onset_topology.py`; implementation commit `2fd4fffc17111be8acb1741985ff9ece32a630d5`; blob `b4ddb289e2e0e54177e51e1b4ff1140dd304ed46`.
- Synthetic tests `modal/tests/test_v144_rhythm_current_baseline_fit_onset_topology.py`; five deterministic synthetic tests. Required pre-label CPU gate `32988449841` SUCCESS.
- Temporary PR #21 was draft, unmerged, and targeted only inert `noop`; it never targeted `main`.
- Early PR-delivery run `32990041415` failed in wrapper verification before analyzer execution due to a nonexistent `canonicalEvents` manifest key. No FIT labels were read by that failed attempt.
- Wrapper-only correction changed verification to `selectedCandidate`; analyzer/reference/baseline/selector/thresholds/topology semantics were unchanged.
- Final exact trigger-only arming commit `6f889ab5fcc31a3cdac459a19b0933e9209e3559`; only trigger path changed; exact message `v144 execute current fit onset topology diagnostic one-shot`.
- **Successful one-shot run `32992367811`**:
  - CPU prerequisite job `98252843458` SUCCESS.
  - One-shot job `98252964359` SUCCESS.
  - Exact trigger/immutable checks SUCCESS.
  - FIT-only aggregate topology analyzer SUCCESS.
  - Isolation verification SUCCESS.
  - Single-report persistence SUCCESS.
- Report `debug/v144-rhythm-calibration/diagnostics/current-pitch-position-baseline-fit-onset-topology.json`; bot persistence commit `cbe6bcf73862ef8f15bf1bad306f746f6f022301`; report blob `26e1265adf5c1c11838c207b4c5af0927f26b95b`.
- Persistence commit added **only** the 111-line report.
- Isolation/safety all held: candidate construction false; ranking false; selection false; rule/shift histogram false; validation labels false; canary labels false; consumed-family outcomes excluded; runtime reference false; V5/main/Production false; Modal/GPU false.
- FIT counts: generated notes `643`; reference notes `594`; generated onsets `485`; reference onsets `370`; union `665`; shared `190`; generated-only `295`; reference-only `180`.
- Topology signals:
  - same-onset wrong-pitch substitution slots `171`.
  - same-string wrong-pitch slots `43`.
  - singleton→singleton onsets `100`.
  - singleton exact-pitch same-string `17`.
  - singleton wrong-pitch same-string `5`.
  - singleton wrong-pitch different-string `78`.
  - shared cardinality mismatches `84` (`27` generated-heavier / `57` reference-heavier).
  - equal-cardinality multi-note onsets only `6`; dyad→dyad only `5`; 3+ equal-cardinality only `1`.
- Interpretation boundary remains topology-only: may inform a materially distinct family unit; may NOT rank a specific rule/shift; validation/canary/consumed-family outcomes may NOT inform family shape; selector thresholds may NOT change.
- Sealing:
  - obsolete standalone push one-shot deleted at commit `1f50ad5273aaba453dfdc81e9f6e815971747a82`.
  - broad CPU workflow restored exactly to topology-test-only blob `0102223c67e4a489dda2e5c88808c0a1dad7c240` at commit `f5403086ca4477a5bcd3a3b78a348e16004a031c`.
  - trigger file deleted at commit `addb76e396d462b5bb1c94b4a03d1ed705b09fe7`.
  - PR #21 closed, draft, unmerged; replay surface removed.

## Family-shape interpretation boundary after topology diagnostic
- The new topology evidence supports examining a **singleton-onset atomic replacement unit** because 78/100 singleton→singleton shared onsets are wrong-pitch + different-string, versus only 5 wrong-pitch + same-string.
- This would be materially distinct from the consumed dyad family because the atomic unit is exactly one generated note at one shared singleton onset, not a two-note chord/dyad.
- To remain distinct from consumed contextual adjacent-string family #7, any successor must be pre-registered as an onset-scoped singleton replacement with an explicit source-string → target-string mapping; it must not merely replay an adjacent-string `stringDelta` contextual shift family.
- Cardinality-changing onset edits are NOT yet pre-registered. Although 84 shared onsets have cardinality mismatch and 475 onsets are one-sided across the union, count-changing edits introduce a larger invariant surface and should not be mixed into the singleton replacement family.
- No concrete singleton rule, source pitch class, semitone shift, source/target string pair, or structural signature has been selected or ranked yet.

## Immediate next actions
1. Pre-register one materially distinct **atomic singleton-onset pitch+string replacement policy** before opening FIT labels for candidate construction. Fixed shape only: shared singleton topology; one generated note → one replacement note; both pitch and string must change; target string is explicit, not adjacent-delta-only; timing/count/order/duration/techniques/metadata preserved; linked pitch techniques excluded; runtime reference forbidden.
2. Add deterministic synthetic policy tests and wire policy/tests into `.github/workflows/v144-rhythm-cpu-gate.yml`.
3. Run CPU gate. If it fails, fix policy/tests only; do not create or execute a search.
4. Only after policy CPU SUCCESS, pre-register a deterministic FIT-only search with fixed support/max-candidate/pitch bounds before inspecting any candidate outcomes. Validation/canary remain closed until one FIT winner is locked.
5. If no singleton rule meets the fixed support/shape requirements, seal the family at fit without relaxing thresholds/support or switching to a fallback shape.
6. Keep `pitch-position-shift-54a6e8d3aa91c422` / SHA `5b36270a...` as baseline unless a future fully gated family passes every invariant.
7. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit authorization.
