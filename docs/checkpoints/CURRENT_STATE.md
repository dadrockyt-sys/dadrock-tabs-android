# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163 generation and its single professional-reference scoring opportunity are both terminal/consumed forever. V163 produced an authoritative exact-V162-algorithm candidate and passed independent structural QC, but its sole frozen professional-reference CPU score terminally returned `SCORE_GATE_FAIL`. Combined Guitar primary timing-aware pitch F1 = `0.059983566146261304`; Bass = `0.21661409043112514`, both below the preregistered `0.80` gates. The candidate remained byte-identical and no correction/tuning/rescore occurred. Never rerun, rearm, repair, retune, regenerate, re-QC, or rescore V163. Do not advance V163 to role/string/fret/technique/PDF.**

## Standing safety
- CPU-only reference-free work is authorized at assistant discretion.
- Fresh explicit authorization is required immediately before Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159/V160/V161/V162/V163 generation versions are closed forever; V163 scoring is also closed forever.
- No professional-reference event/measure mining, candidate modification, score-informed retune, threshold sweep, variant selection, human correction, or second score of V163.
- Do not use V163's score or professional-reference contents to tune/select a successor same-song candidate.
- No GPU/Modal/CUDA without fresh explicit authorization.

## V163 authoritative generation — FROZEN
- V163 prereg blob `33c0eb36423bd5b014035e3a475b4232b0decf9a`; pre-run blob `ac47d48b3df3842725ab9a3c1995831d487f1b78`.
- Generation arm `4fb855b300c6d0331400b9aa642254be46752def`; workflow blob `a36facd5f6b0a67a6965de0a27d9491d589bc83a`.
- Generation run `33213512389`, #1 attempt #1, job `98991933938`; guard PASS; CPU pipeline PASS; terminal self-seal PASS.
- Generation terminal commit `3b6f98750291a2f7b229c5e50cbf802752cf84d4`; terminal blob `b5b9b7b043bca3fd4db7b72334d99731da293ed7`; outcome `STRUCTURAL_QC_PASS`; `candidateAuthoritative=true`; `eligibleForProfessionalReferenceScoring=true`; `neverRearmV163=true`.
- Generation workflow self-deleted.

## Frozen V163 candidate
- `debug/v163-cpu-autonomous/generated.json`.
- Git blob `f4eafb1488f139198cb7860a76f294c0e1775df8`.
- SHA256 `cc55d596a05bd8e9c0a149f6ba8263375c26fbb7334139a75697b58ca23c8c19`.
- Combined Guitar events `1041`; Bass events `404`.
- Evidence-step corrections Guitar/Bass `19 / 6`; pre-grid excluded `0 / 0`.
- Candidate is exact frozen V162 algorithm output under V163 execution identity.

## Structural QC — PASS / FROZEN
- `debug/v163-cpu-autonomous/structural-qc.json`.
- Git blob `35624b8bfbb3580573bb49bd12049726ee364977`; SHA256 `ae899558f436c872e3a3ee306463fe62163652497f96d36cea2558be27aa2337`.
- Validation PASS; errors `[]`; all structural/hash/code-pin/grid/recompute/source/cap/reference-blind checks true.

## V163 one-score preregistration — FROZEN
- `debug/v163-cpu-autonomous/score-preregistration.json`.
- Seal commit `f889b9917d7134164ea77e611eb2867795418fa2`; Git blob `03f03f4005ab2ab84e93d06a107bc8f680a54775`.
- Schema `dadrock.tabs.v163.professional-reference-score-preregistration.v1`; validation PASS.
- Frozen scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference: `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`, blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Frozen gates: Combined Guitar primary timing-aware pitch F1 `>=0.80`; Bass `>=0.80`; both required.
- Maximum professional-reference score executions `1`; candidate consumed regardless PASS/FAIL.

## V163 sole professional-reference score — TERMINAL / FROZEN
- Score arm commit `8809cb701d71c7bee73b1aad36c082fc5ea12ca0`.
- Exact score-arm parent/final pre-arm checkpoint head `edf9dc3ee8a225114cf1f458d936748c2eadeb0a`.
- Score workflow Git blob `18e6fd8017693a183672edfb945c343dc3b1274e`.
- GitHub Actions run `33214223643`, run #1 attempt #1, job `98994146394`.
- Sealed one-score guard PASS.
- Frozen scorer executed exactly once and completed successfully.
- Terminal self-seal PASS.
- Terminal score commit `7bd8c813cac506811e3c144e5efe9edcd3abc561` with message `research: freeze sole V163 professional-reference score FAIL [skip ci]`.
- `.github/workflows/v163-score.yml` self-deleted and is absent after terminal seal.
- Never rerun or rearm V163 scoring.

## V163 score terminal — SCORE_GATE_FAIL
- `debug/v163-cpu-autonomous/score-terminal-freeze.json` Git blob `b7e6634d67b89632389f2be3edfdbe0162ff98dd`.
- Schema `dadrock.tabs.v163.professional-reference-score-terminal.v1`; status `TERMINAL`; outcome `SCORE_GATE_FAIL`.
- `scoreExecutionCount=1`; `scoreOpportunityConsumed=true`; `candidateConsumed=true`; `neverRerunOrRescoreV163=true`.
- `eligibleForRoleStringFretTechniquePdfPhase=false`.
- Combined Guitar primary timing-aware pitch F1 `0.059983566146261304` vs gate `0.80`.
- Bass primary timing-aware pitch F1 `0.21661409043112514` vs gate `0.80`.
- Candidate blob/SHA remained exactly `f4eafb1488f139198cb7860a76f294c0e1775df8` / `cc55d596a05bd8e9c0a149f6ba8263375c26fbb7334139a75697b58ca23c8c19`.
- Safety: candidateModified=false; candidateRegenerated=false; candidateReQc=false; thresholdSweep=false; variantSelection=false; humanCorrection=false; postScoreRetune=false; referenceFacingScoreCalls=1; professionalReferenceUsedForScoringOnly=true; GPU/CUDA/Modal=false; main/Production=false.

## Frozen score report
- `debug/v163-cpu-autonomous/reference-score.json`.
- Git blob `d10ae33aba35afd2547f94a3ec3dcd8443972fcf`.
- SHA256 `b87e745d1b3dafea2e99b841e8af028c55f8749341e5736fa5ec488ebf66cfd9`.
- Combined Guitar: primary F1 `0.059983566146261304`; gross F1 `0.2004930156121611`; measure/pitch diagnostic F1 `0.4864420706655711`.
- Bass: primary F1 `0.21661409043112514`; gross F1 `0.35962145110410093`; measure/pitch diagnostic F1 `0.5215562565720294`.
- These values are terminal evaluation evidence only. They MUST NOT be used for same-song candidate repair, threshold selection, event/measure mining, or another V163 score.

## Current execution state
- V163 generation execution count `1`, terminal.
- V163 professional-reference score execution count `1`, terminal.
- V163 score opportunity consumed.
- No V163 generation workflow exists.
- No V163 score workflow exists.
- V163 candidate remains immutable.
- V163 is NOT eligible for role/string/fret/technique/PDF phase.
- GPU/CUDA/Modal executions `0`; main/Production changes `0`.

## Hard boundary — NEXT
1. Never rerun, rearm, repair, regenerate, re-QC, retune, or rescore V163.
2. Do not inspect/mine professional-reference notes, measures, failures, or score diagnostics to design a same-song fix.
3. Do not advance V163 to role/string/fret/technique/PDF because both preregistered score gates failed.
4. Preserve all V163 terminal artifacts exactly as frozen.
5. Any successor scientific generation version must be a genuinely new, independently preregistered reference-blind hypothesis justified without professional-reference feedback or V163 score-informed tuning; its candidate must be generated before any future reference-facing evaluation is considered.
6. Before any successor execution, checkpoint its hypothesis, algorithm/numerics, frozen code identities, negative controls, one-shot semantics, and explicit no-loop policy.
7. CPU-only reference-free work is allowed. Any GPU/Modal/CUDA execution still requires fresh explicit user authorization immediately before execution.
