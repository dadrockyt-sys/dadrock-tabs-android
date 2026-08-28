# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163 is fully terminal/consumed and failed its sole preregistered professional-reference score gate. Never rerun/rearm/repair/retune/regenerate/re-QC/rescore V163 and do not advance it to role/string/fret/technique/PDF. V164 is now preregistered, its numeric local-evidence contract is sealed, and the first version-isolated pure local-normalization helper module plus synthetic invariance fixture have been implemented and locally CPU-validated. No V164 song processing, scorer/reference read, model inference, workflow arm, or candidate exists.**

## Standing safety
- CPU-only reference-free work authorized at assistant discretion.
- Fresh explicit authorization required immediately before Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159/V160/V161/V162/V163 generation versions closed forever; V163 score opportunity closed forever.
- No professional-reference event/measure mining, candidate repair, score-informed retune, threshold sweep, variant selection, human correction, or second V163 score.
- V163 aggregate score was observed before V164 preregistration. V164 does **not** claim reviewer score-blindness; V164 design/numerics are explicitly quarantined from V163 score/reference evidence.
- No GPU/Modal/CUDA without fresh explicit authorization.

## V163 frozen terminal facts
- Generation arm `4fb855b300c6d0331400b9aa642254be46752def`; run `33213512389`, #1 attempt #1, job `98991933938`; generation terminal `3b6f98750291a2f7b229c5e50cbf802752cf84d4`; outcome `STRUCTURAL_QC_PASS`.
- Candidate `debug/v163-cpu-autonomous/generated.json`: blob `f4eafb1488f139198cb7860a76f294c0e1775df8`; SHA256 `cc55d596a05bd8e9c0a149f6ba8263375c26fbb7334139a75697b58ca23c8c19`; Guitar `1041`, Bass `404`.
- Structural QC blob `35624b8bfbb3580573bb49bd12049726ee364977`; SHA256 `ae899558f436c872e3a3ee306463fe62163652497f96d36cea2558be27aa2337`; PASS.
- Score prereg blob `03f03f4005ab2ab84e93d06a107bc8f680a54775`; score arm `8809cb701d71c7bee73b1aad36c082fc5ea12ca0`; run `33214223643`, #1 attempt #1, job `98994146394`; exactly one frozen scorer call; terminal score commit `7bd8c813cac506811e3c144e5efe9edcd3abc561`; score workflow self-deleted.
- Score terminal blob `b7e6634d67b89632389f2be3edfdbe0162ff98dd`; `SCORE_GATE_FAIL`; score opportunity consumed; Guitar primary F1 `0.059983566146261304`, Bass primary F1 `0.21661409043112514`, gates `0.80/0.80`; downstream PDF phase ineligible.
- Score report blob `d10ae33aba35afd2547f94a3ec3dcd8443972fcf`; SHA256 `b87e745d1b3dafea2e99b841e8af028c55f8749341e5736fa5ec488ebf66cfd9`.

## V164 preregistration — FROZEN
- `debug/v164-cpu-autonomous/preregistration.json`.
- Commit `1f0b4a904227491cbd5c62039d1ecbd500453966`; blob `05d255d75a6c1947891fba38d96d9399e3f75f9c`.
- Schema `dadrock.tabs.v164.local-evidence-invariance-preregistration.v1`; PASS; sealed before numerics/code.
- Hypothesis is derived only from static V162 semantics: global positive-quantile/q95 onset normalization creates nonlocal coupling, so remote amplitude can alter an unchanged local evidence decision.
- Allowed design evidence: V162 contract blob `409da313ed03a6c232d6578d48b0da6aa35b000b`; event logic blob `9f9b33fd8c210ad581025b454cf69b6999aa544b`; song-blind fixture blob `e301f38db66f44193d799a9c1a02c99169823d45`.
- V163 score/reference/candidate rows and same-song audio behavior are forbidden V164 design evidence.

## V164 numeric implementation contract — FROZEN
- `debug/v164-cpu-autonomous/implementation-contract.json`.
- Commit `174a1c3850b4eb30335c9afd0e0ada776de37a3b`; blob `098f24282b59abba0f7cffa0793b344b76701724`.
- Schema `dadrock.tabs.v164.local-evidence-numeric-contract.v1`; PASS; sealed before implementation code.
- Event-local evidence window: half-window `32` frames, inclusive/clipped, up to `65` frames; positive samples only; minimum positive samples `1`; q95 support scale; no-positive support `0.0`, threshold `null`.
- Beat-local subdivision evidence: population restricted to enclosing beat; q55 unchanged; search radius `3`, move ratio `1.05`, Voronoi/tie-break unchanged.
- Beat-local event-step support: q95 populations from candidate step's enclosing beat; endpoint uses preceding beat; score weights `0.70/0.20/0.10`, non-nearest margin `0.05`, max correction one step unchanged.
- All unrelated V162 Basic Pitch, Guitar segmentation/recovery/register/admission/caps, Bass pYIN/state/proposal/admission/cap, beat-backbone and safety numerics remain frozen.
- Invariance fixture constants: remote scale `1,000,000`; local scales `0.1` and `10.0`; abs/rel tolerance `1e-12`.

## V164 pure helper implementation — CURRENT
### `validation/v164_cpu_autonomous/event_logic_v164.py`
- Creation commit `5ac25c12116290d33967894405f965914aabc9af`.
- Git blob `1357139d634f0b463a3dceee05f9ef64946aea9e`.
- Contains **only** pure/local deterministic helpers; no song I/O/model/scorer/reference access.
- Implements sealed 32-frame local populations, local q95 support, local positive thresholds, beat frame/population helpers, beat-local subdivision refinement/lattice construction, and beat-local event-step support/selection.
- Nonfinite onset envelopes rejected.

### `validation/v164_cpu_autonomous/test_event_logic_v164.py`
- Creation commit `308d1b696c06558a8c6306ca120696a7a312d26e`.
- Git blob `641a05dd7fd71cfc702b1b5b42f5c54102b2321a`.
- Synthetic-only tests cover:
  - local window clipping at start/end;
  - zero-positive fallback;
  - nonfinite rejection;
  - Guitar-style supported-attack remote invariance;
  - Bass-style onset-evidence remote invariance;
  - beat subdivision remote + local-scale invariance;
  - event-step remote + local-scale invariance;
  - q95 beat support zero fallback.
- Local CPU compile/test performed before commit against the exact committed text; result schema `dadrock.tabs.v164.local-evidence-static-test.v1`, `validation=PASS`.
- Reported flags PASS: eventRemoteInvariant, bassOnsetRemoteInvariant, subdivisionRemoteInvariant, eventStepRemoteInvariant, localScaleInvariant, zeroFallbackDeterministic, boundaryClippingDeterministic, nonfiniteRejected; song/reference/scorer/V163 candidate/V163 score/GPU reads all false.

## Current V164 execution state
- Preregistration: sealed.
- Numeric contract: sealed.
- Pure helper code: implemented.
- Pure synthetic invariance fixture: implemented and locally CPU PASS.
- Full V164 integrated event/transcriber/timebase/QC modules: not yet implemented.
- GitHub static preflight workflow: not armed/not created.
- Song audio reads `0`; Demucs/pitch inference `0`; V164 candidate `0`; professional-reference/scorer reads for V164 `0`; GPU/CUDA/Modal `0`; main/Production unchanged.
- V164 prereg/contract do not authorize professional-reference scoring.

## Hard boundary — NEXT
1. Never reopen V163 for tuning/scoring.
2. Continue V164 implementation only from contract blob `098f24282b59abba0f7cffa0793b344b76701724`.
3. Integrate the pure V164 locality helpers into version-isolated V164 copies of the V162 event/timebase/transcriber/QC path while preserving every unrelated V162 numeric/behavioral rule.
4. Add/retain song-blind regression fixtures for all unchanged V162 segmentation/register/Bass-state/grid-cap behavior and JSON-native/nonfinite protections.
5. Do not read song audio, V163 candidate/score, scorer, or professional reference during implementation/static validation.
6. After all V164 code is complete, create a one-shot CPU-only static preflight that may compile/run synthetic fixtures only; checkpoint before arm and make zero branch writes while any sealed workflow is active.
7. No V164 song processing until static preflight and pre-run identity are separately sealed.
8. No GPU/Modal/CUDA without fresh explicit authorization.
