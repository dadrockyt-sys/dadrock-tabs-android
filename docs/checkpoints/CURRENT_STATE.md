# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families 1–10 are consumed/sealed. Family #10 winner `singleton-onset-replace-be9e9aa7a734e3cd` is the ACCEPTED V144 RHYTHM CALIBRATION BASELINE. A new accepted-baseline FIT aggregate residual diagnostic is PRE-REGISTERED, its required pre-label CPU gate is GREEN, and its one-shot workflow is PRE-REGISTERED but NOT ARMED. The diagnostic has NOT read FIT labels yet. No family #11 is pre-registered/evaluated. Production/main/Bass/Lead remain untouched.**

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

## ACCEPTED V144 Rhythm calibration baseline — LOCKED / CALIBRATION ONLY
- Name `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`; creation commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- Transform chain: frozen V5 → historical triple prune → same-string pitch shift → joint pitch+adjacent-string position revoice → exact-singleton replacement `stepParity::0`, source string `0`, source pitch class `4`, explicit target string `3`, semitone shift `-12`.
- 1144 events / 113 measures; exact event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity `1.0`; 110 changed singleton events/onsets.
- Full gold: critical `1712`; pitch `0.35406698564593303`; pitch/timing `0.06698564593301436`; string/fret/timing `0.05454545454545454`; chord pitch-set `0.0580511402902557`; exact voicing `0.0580511402902557`; coverage `1.0`; no regressions.
- Calibration baseline `true`; Production `false`; Rhythm complete `false`; near-100 `false`; unseen-generalization `false`.

## Accepted-baseline reconstruction proof — COMPLETE / CPU GREEN
- Test `modal/tests/test_v144_rhythm_singleton_selected_baseline_reconstruction.py`; commit `7f815493a1bd055bad79cfd76f2cf875e3abd2e3`; blob `e6acdd8b49dc6d87f04f7cf89367c97a3ca49041`.
- CPU run `32996069426`, job `98265545933`: SUCCESS. Reference-free V5 → accepted chain exactly reproduces `4e6f9f...`, 1144 events, 113 measures, 110 changes before gold labels.

## Consumed families — NEVER REPLAY / RESELECT / RETUNE
1. Single-signature prune — failed validation.
2. Two-signature prune — failed measure-set invariant.
3. Triple prune — historical accepted baseline.
4. Additive four-signature prune — no fit-qualified; sealed `69db5acad3e313610f22617f06fbb325e5b8941d`.
5. Same-string contextual pitch shift — prior accepted; sealed `21ca074f3917fb72614686ca5b46a3894ea53374`.
6. Joint contextual pitch+step — failed canary; sealed `215fc49106ef3501b71452b1f6c9f6d638cafd77`.
7. Joint contextual pitch+adjacent-string position — prior accepted; run `32971373324`; sealed `61422dea64ed4758999b3cd3c978d0db344e3ef6`.
8. Joint contextual pitch+step+position — no fit-qualified; run `32974497513`; sealed `55a948fa97ab100bdca0b1338b36c9a43a4f5ce9`.
9. Atomic exact-two-note onset dyad pitch rewrite — zero supported rules / zero candidates; run `32975912923`; report blob `9b1099e42f57127a9cf3168471fdb49415067f5f`; sealed `6e0e23254a4e6c845c681368a96e1623f04364bd`.
10. Atomic singleton-onset pitch+explicit-string replacement — successful locked winner; one-shot `32995503662`; report commit `ff6165982e8e3036404489c954a7d06ab8a1b015`; report blob `92de07b1cac11cba87e923c18eebf9cce7b0cea7`; workflow deleted `bb7e96c849a21441547eff0cb2ac7da37eb6e223`; trigger deleted `deeef71043fecb34520e0c0b048eddc1497b1ef5`; consumed/sealed — never replay/reselect/retune or select another of its 25 candidates.

## Prior FIT-only diagnostics — SEALED / HISTORICAL TO PRIOR `5b36270a...` BASELINE
- Mechanism diagnostic run `32972033516`; report blob `dbc0c1ab0cfff943f95eab48720c7c2a5eb9d175`; sealed `a6d5ddf373de8a71facf8474d48550aa990d7d54`.
- Onset topology diagnostic run `32992367811`; report blob `26e1265adf5c1c11838c207b4c5af0927f26b95b`; execution surfaces sealed/deleted.
- They must NOT be treated as current residual-shape evidence after promotion to `4e6f9f...`.

## Accepted-singleton-baseline FIT residual diagnostic — PRE-REGISTERED / PRE-LABEL CPU GREEN / ONE-SHOT UNARMED
- Diagnostic `validation/v144_rhythm_calibration/analyze_singleton_baseline_fit_residuals.py`; commit `dbc2ff96252a7069b928a31d0cf38771d45e9a1f`; blob `27ac8699279db8fc0208d067479ad3751da1a630`.
- Synthetic tests `modal/tests/test_v144_rhythm_singleton_baseline_fit_residual_diagnostic.py`; commit `9dae8b40170d20d31a618bc2ea5bd5d61564fc79`; blob `6d45faeb70d1ed99de0d57161fa061e12b7f0a2f`; six synthetic tests.
- Broad CPU wiring commit `4fafa26008ef6a9de9bb8a64a5660d8214c22f09`; workflow blob `ef39cad011796bcd0cb5f39a6f03e06fc7cde7b7`.
- **Required pre-label CPU run `32996550172`, job `98267233982`: SUCCESS.** Logs explicitly confirm diagnostic compile, all six residual-diagnostic tests PASS, accepted-baseline reconstruction tests PASS, immutable V5/provenance/config guards PASS. The diagnostic was NOT executed against gold labels in this gate.
- Output contract: aggregate note-match/mechanism/onset/cardinality counts only; candidate construction/ranking/selection false; rule/shift histogram false; validation/canary false; runtime reference false; GPU false.
- One-shot `.github/workflows/v144-singleton-baseline-fit-residual-diagnostic.yml`; preregistration commit `f931f39b62ccbb6b8245f615e47ebf233480660e`; workflow blob `b3d00151d6082b8f8c5e182e3469b5d10b22bb3e`.
- One-shot locks V5 analyzer/result/render/PDF, gold ref SHA, accepted manifest blob, diagnostic/test/reconstruction blobs, current counting helpers, canonical/scorer/split helpers, family #10 reconstruction dependencies, context split policy/config, and exact trigger identity before labels.
- Target report `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json` does not exist yet.
- **One-shot is NOT ARMED at this checkpoint; no FIT labels have been read by this diagnostic; no family #11 exists.**

## Immediate next actions
1. Create exactly one trigger-only commit at `debug/v144-rhythm-calibration/diagnostics/.singleton-baseline-fit-residual-trigger` with exact message `v144 execute singleton baseline fit residual diagnostic one-shot`, locking workflow blob `b3d00151...` and pre-label run/job `32996550172` / `98267233982`.
2. Poll that exact trigger SHA until the one-shot completes. Do not create duplicate trigger events.
3. On SUCCESS, verify bot persistence commit added only `singleton-baseline-fit-residuals.json`; inspect aggregate report; immediately delete workflow + trigger and refuse replay while baseline unchanged.
4. Use only the new accepted-baseline FIT aggregate report to decide whether a materially distinct family #11 shape exists. Never use validation/canary/consumed-family outcomes to choose it. If unclear, stop at diagnostic boundary.
5. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit authorization.
