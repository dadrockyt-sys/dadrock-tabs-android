# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V161 generation is complete, terminal, authoritative, and immutable. A separate V161 one-score preregistration is now sealed before any V161 reference-facing score: `debug/v161-cpu-autonomous/score-preregistration.json`, seal commit `22fdd5df418f0d196f5472026c6c0ffd24f893e6`, Git blob `8f50b65d023bd5469935ed3ca70c115bf0b86dda`, validation PASS. Candidate SHA256 `75c4edd6560ee832bf7df4799c4e9389a7424e7056ac5f3cd5a9e07fc254996a`; Combined Guitar 895 events; Bass 449. Exactly one CPU professional-reference score is permitted, with unchanged 0.80/0.80 gates. NO V161 score has run yet. Next: mechanically adapt/reviewer-audit the proven V160 one-score workflow to V161 identities, prove score report/terminal/workflow absence, then arm once.**

## Standing safety — MUST PRESERVE
- CPU-only work and CPU scoring authorized at assistant discretion.
- Fresh explicit authorization required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V161 generation/QC is consumed forever: no regeneration, repair, re-QC, retune, threshold sweep, variant selection, or candidate replacement.
- Professional reference and frozen scorer are scoring-only; they cannot influence candidate/generation artifacts.
- V161 may receive at most one professional-reference score. No rerun/rescore regardless of pass/fail/runtime outcome.
- No post-score retune of V161; no human correction.
- V159 and V160 remain closed forever.
- Do not commit professional-tab screenshot bytes.

## V161 terminal generation — FROZEN
- Bot terminal commit `1b58ffcb8c2ee8fc7dd6152bf02c071d75035ade`; parent arm `418a25f82e4aa3742e995e4a3ce341bc48a24151`.
- Generation run `33208183041`, run #1 attempt #1, job `98974530460`, success.
- Generation workflow blob `38cd491453c618f595d42bb6d42e87e478f35f0e`; workflow self-deleted.
- Terminal freeze blob `5ff59c993698b00df3503c6e22e036f181140aa4`: `STRUCTURAL_QC_PASS`, `candidateAuthoritative=true`, `eligibleForProfessionalReferenceScoring=true`, `neverRearmV161=true`.
- Structural QC blob `2146cf9f7b9e92ce704ef2118e711bd42ae2e093`; SHA256 `ba17ac241d438e15d13f0d45a93194e97151868805541dc252ea41caa1ae34ba`; validation PASS; errors `[]`; every check true.
- Candidate blob `52178705ef3830f6849b71037cd283877aa7655f`; SHA256 `75c4edd6560ee832bf7df4799c4e9389a7424e7056ac5f3cd5a9e07fc254996a`.
- Final counts: Combined Guitar 895; Bass 449.
- Generation/runtime safety: referenceRead=false; professional paths=0; score calls=0; V160CandidateRead=false; prior score/candidate reads=false; GPU/CUDA/Modal=false; main/Production=false.

## V161 frozen design/implementation identities
- preregistration `3d6b0412caaafbad39781f72a95fe29c72a38729`
- numeric contract `51fe81400347119c95a2e6a1a63731070269a090`
- event logic `85419429a2dae4baeb60232b756af4b127f87ce2`
- event fixture `11e1c8b56375fe9675804778e7154b89ac6f24e7`
- timebase builder `7ac9f91b807430ee2edb3631393c9261b6db980b`
- timebase QC code `7743c8f2ca2d09546d4eeb09f1fef3d14d7a1970`
- transcriber `0137f211a79ef2b1a63d1485497eb00686b3afd1`
- structural QC code `35fd631fe9a6fad37aac66526aa56e9ef8d5a26a`
- JSON fixture `c91e223d682b03faceb3d0704fa754a2d1c91af4`
- negative guard `7dc6141cfc18d192d165f86d3eecbda3cf15851a`
- static workflow `2a774f4c03d9779ca764d4752254445569e7034b`; static run `33207839556`, #1 attempt #1, job `98973355115`, PASS/consumed.
- pre-run identity receipt blob `bb1aed847c62b37e68f158a50614c48acf20781a`.

## V161 reference-blind runtime diagnostics — FROZEN
- Guitar: Basic Pitch raw 1404 → consolidated 985 → admitted 978 → final 895; onset-refined 827; register repairs 382; admission rejects 7; standalone harmonic recovery 0/disabled.
- Bass: detected onsets 465 → retained/merged 464 → admitted/final 449; onset-refined 464; activity rejects 1; transition proposals 0.
- V160 comparison only as aggregate structural evidence: Guitar 2276→895; Bass 460→449. This is not a professional-reference quality score.

## V161 score preregistration — PASS / SEALED
- Path `debug/v161-cpu-autonomous/score-preregistration.json`.
- Seal commit `22fdd5df418f0d196f5472026c6c0ffd24f893e6`; Git blob `8f50b65d023bd5469935ed3ca70c115bf0b86dda`.
- Schema `dadrock.tabs.v161.professional-reference-score-preregistration.v1`; status `SEALED_BEFORE_REFERENCE_OR_SCORER_OPEN`; validation PASS.
- Frozen candidate blob/SHA/counts exactly match terminal V161 candidate.
- Pins generation terminal commit/run/job/workflow blob and terminal-freeze blob.
- Pins structural-QC blob/SHA and PASS state.
- Frozen scorer remains `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference remains `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`, blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Score gates frozen: Guitar timing-aware pitch F1 >=0.80 AND Bass timing-aware pitch F1 >=0.80.
- Maximum score executions=1; run #1 attempt #1; rerun/second-arm/duplicate forbidden; candidate mutation/replacement/re-QC/regeneration forbidden; threshold sweep/variant selection/human correction forbidden; post-score retune/rescore forbidden.
- Score workflow must self-delete and self-seal report/terminal receipt.
- At score seal: V161 score report absent; score terminal absent; score workflow absent; V161 score calls=0; GPU/CUDA/Modal=0; main/Production=false.

## Proven scoring control pattern available
- V160 used the same frozen scorer/reference and completed exactly one score safely.
- V160 score workflow blob `b05b43bdac131561da15209b0beed56b3c6ea982`; run `33206424361`, #1 attempt #1.
- V161 score workflow should be a mechanical version/identity adaptation only, not a scorer/reference or metric change.

## Current hard boundary
- Do not alter V161 candidate or any generation/QC artifact.
- Do not use professional-reference details to tune or repair V161.
- Reviewer-audit `.github/workflows/v161-score.yml` before creation.
- Score workflow creation must be the sole trigger; exact parent/head one-file proof; run #1 attempt #1.
- Guard must pin candidate blob/SHA, structural-QC blob/SHA, generation terminal blob/commit/run, score-prereg blob, scorer blob, reference blob/SHA, and prove score outputs absent.
- Frozen scorer command must appear exactly once.
- After score starts: assistant/manual branch writes forbidden until terminal self-seal.
- Score terminal must consume V161 regardless PASS/FAIL/runtime outcome and self-delete workflow.
- No GPU/Modal/CUDA without fresh explicit authorization; never touch main/Production.

## Exact next steps — RESUME HERE
1. Re-fetch branch/checkpoint before every write.
2. Mechanically adapt V160 score workflow to V161 exact identities and V161 terminal schema; no metric/scorer/reference change.
3. Reviewer-audit proposed workflow without creating it.
4. Re-prove `.github/workflows/v161-score.yml`, `debug/v161-cpu-autonomous/reference-score.json`, and `debug/v161-cpu-autonomous/score-terminal-freeze.json` are absent.
5. Use latest checkpoint head as EXPECTED_PARENT_HEAD and create `.github/workflows/v161-score.yml` exactly once.
6. While score active: read-only observation only; never rerun.
7. After self-seal: verify report/terminal/candidate immutability/workflow absence; checkpoint V161 consumed forever and then design V162 only from permitted aggregate evidence.
