# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Families 1–10 are consumed/sealed. Family #10 winner `singleton-onset-replace-be9e9aa7a734e3cd` is the ACCEPTED V144 RHYTHM CALIBRATION BASELINE after reference-free reconstruction CPU proof. A new accepted-baseline FIT aggregate residual diagnostic is PRE-REGISTERED and broad-CPU-gate wired, but it has NOT read FIT labels yet. No family #11 is pre-registered/evaluated. Production/main/Bass/Lead remain untouched.**

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
- Manifest `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`.
- Manifest creation commit `3f38f6cbd6adce77eccece281b33ae6d315ec000`; manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- Prior baseline preserved historically at `debug/v144-rhythm-calibration/selected/v144-pitch-position-selected-baseline.json`; blob `45287a40fbbe88f411d2eca7db3cce072174eda8`; prior event SHA `5b36270aaeafa73b2e25722e2576a40424ce5951dcfd2b5d769746bd9eb07e0d`.
- Transform chain: frozen V5 → historical triple prune → same-string pitch shift → joint pitch+adjacent-string position revoice → exact-singleton replacement `stepParity::0`, source string `0`, source pitch class `4`, explicit target string `3`, semitone shift `-12`.
- Selected event count `1144`; generated measures `113`; exact event/PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; PDF fidelity `1.0`.
- Family #10 changes `110` events / `110` singleton onsets; event count/order/timing/measure/non-position metadata preserved; target fret tuning-derived; runtime reference forbidden.
- Full gold calibration: critical mismatch `1712`; pitch F1 `0.35406698564593303`; pitch/timing `0.06698564593301436`; string/fret/timing `0.05454545454545454`; chord pitch-set `0.0580511402902557`; exact voicing `0.0580511402902557`; coverage `1.0`.
- Versus prior baseline: critical `-42`; pitch `+0.02583732057416266`; pitch/timing `+0.0028708133971291905`; string/fret/timing `+0.008612440191387558`; chord/voicing `+0.0193503800967519`; no regressions.
- Promotion scope: calibration baseline `true`; Production promotion `false`; Rhythm complete `false`; near-100 `false`; unseen-generalization claim `false`.

## Accepted-baseline reconstruction proof — COMPLETE / CPU GREEN
- Reconstruction test `modal/tests/test_v144_rhythm_singleton_selected_baseline_reconstruction.py`; creation commit `7f815493a1bd055bad79cfd76f2cf875e3abd2e3`; blob `e6acdd8b49dc6d87f04f7cf89367c97a3ca49041`.
- Broad CPU workflow pre-residual blob `a88ead7c7af65c2621e8f62a595b1d2896d22e4b`; reconstruction gate/head commit `ab40c78ce0f274c24127ca45ee1663a79580620a`.
- CPU run `32996069426`, job `98265545933`: **SUCCESS**.
- Reference-free chain test reproduces exact `4e6f9f...`, 1144 events, 113 measures, and 110 changed events without opening gold labels.
- Manifest-scope test locks calibration-only provenance/replay refusal. Immutable V5/provenance/config guards passed.

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
10. Atomic singleton-onset pitch+explicit-string replacement — successful locked winner; one-shot `32995503662`; report commit `ff6165982e8e3036404489c954a7d06ab8a1b015`; report blob `92de07b1cac11cba87e923c18eebf9cce7b0cea7`; workflow deleted `bb7e96c849a21441547eff0cb2ac7da37eb6e223`; trigger deleted `deeef71043fecb34520e0c0b048eddc1497b1ef5`; **consumed/sealed — never replay/reselect/retune or select another of its 25 candidates**.

## Family #10 fixed provenance
- Policy commit `9f1d4d609f62a6f75f0b708d9eb6efff2118a8d3`; blob `1e05e66a3523f98944370837a59e5d6e7293f9ac`; tests commit `4f6c22ac2c01227beebb75517aa50d48ac267696`; blob `a4e1c52e5f63187e8bad5f853300e644f056e726`; policy CPU `32994157957` SUCCESS.
- Search `validation/v144_rhythm_calibration/search_atomic_singleton_onset_replacements.py`; commit `33bc68a24057e141a5e426439ec588f99b5fe79e`; blob `70880d26418d907cc702233af37bcc4b643e3a57`.
- Search tests commit `142364f38839c5823f91e1131387f77adec833dd`; blob `3a2adbecbe810e6738718fc72e2cf231555e8c3e`; search CPU `32995017936` SUCCESS.
- One-shot workflow blob `a9bef022032f2d5195dc54ba2a5bd9d7629686da`; trigger commit `ded6bf5d064a5daa02e69e1df4140e9289530960`; trigger blob `bb98a9de3c0ffbaad4dd32aa457d07f703a2bf5b`.

## Prior FIT-only diagnostics — SEALED / HISTORICAL TO PRIOR `5b36270a...` BASELINE
- Mechanism diagnostic: CPU `32971927840`; diagnostic `32972033516`; report blob `dbc0c1ab0cfff943f95eab48720c7c2a5eb9d175`; sealed `a6d5ddf373de8a71facf8474d48550aa990d7d54`.
- Onset topology diagnostic: pre-label CPU `32988449841`; one-shot `32992367811`; report blob `26e1265adf5c1c11838c207b4c5af0927f26b95b`; execution surfaces sealed/deleted.
- These may explain why family #10 was proposed, but must NOT be treated as current residual-shape evidence after promotion to `4e6f9f...`.
- Consumed-family validation/canary/full outcomes must never construct/rank a successor.

## Accepted-singleton-baseline FIT residual diagnostic — PRE-REGISTERED / PRE-LABEL / CPU PENDING
- Diagnostic `validation/v144_rhythm_calibration/analyze_singleton_baseline_fit_residuals.py`.
- Implementation commit `dbc2ff96252a7069b928a31d0cf38771d45e9a1f`; blob `27ac8699279db8fc0208d067479ad3751da1a630`.
- Synthetic tests `modal/tests/test_v144_rhythm_singleton_baseline_fit_residual_diagnostic.py`; commit `9dae8b40170d20d31a618bc2ea5bd5d61564fc79`; blob `6d45faeb70d1ed99de0d57161fa061e12b7f0a2f`; six synthetic tests.
- Broad CPU-gate wiring commit `4fafa26008ef6a9de9bb8a64a5660d8214c22f09`; workflow blob `ef39cad011796bcd0cb5f39a6f03e06fc7cde7b7`.
- Wiring only adds diagnostic/test path filters, diagnostic `py_compile`, and synthetic test execution. **It does not execute the diagnostic or open FIT labels.**
- Diagnostic reconstructs `4e6f9f...` reference-free before loading gold reference, using the same locked chain already proven by the promotion reconstruction test.
- Output is aggregate only: note match counts, onset topology/cardinality counts, same-onset substitution/extra/missing counts, displacement/tolerance counts, and position mismatch counts.
- Hard flags: candidate construction/ranking/selection `false`; rule/shift histogram `false`; validation/canary labels `false`; runtime reference `false`; GPU `false`.
- Interpretation boundary: aggregate FIT residuals may inform only a materially distinct future family unit; they may not rank a rule/shift, change fixed thresholds, use validation/canary/consumed-family outcomes, or claim unseen generalization.
- **No FIT labels have been read by this diagnostic yet. No report exists. No family #11 exists.**

## Immediate next actions
1. Wait for broad CPU gate on wiring commit `4fafa26008ef6a9de9bb8a64a5660d8214c22f09`.
2. If it fails, fix diagnostic/tests only; do not execute against FIT labels.
3. After CPU SUCCESS, create one tightly locked CPU-only one-shot that verifies immutable V5/result/render/PDF, gold ref SHA, accepted singleton manifest blob `acd12ab6...`, diagnostic blob `27ac8699...`, test blob `6d45faeb...`, search/reconstruction dependencies, and exact trigger identity.
4. Execute diagnostic at most once to `debug/v144-rhythm-calibration/diagnostics/singleton-baseline-fit-residuals.json`; verify aggregate-only contract; persist only report; immediately delete/archive executable one-shot + trigger and refuse replay while baseline unchanged.
5. Interpret only that new accepted-baseline FIT aggregate report to decide whether a materially distinct family #11 exists. If unclear, stop at diagnostic boundary.
6. Never start Bass/Lead, modify main/Production, claim near-100%, or use Modal/L4/GPU without fresh explicit authorization.
