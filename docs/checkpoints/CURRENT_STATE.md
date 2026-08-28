# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V161 generation is complete, terminal, authoritative, and eligible for exactly one professional-reference score. The sole CPU generation run self-sealed successfully and deleted `.github/workflows/v161-generate.yml`. Terminal bot commit: `1b58ffcb8c2ee8fc7dd6152bf02c071d75035ade`. Terminal outcome: `STRUCTURAL_QC_PASS`; `candidateAuthoritative=true`; `eligibleForProfessionalReferenceScoring=true`; `neverRearmV161=true`. Candidate SHA256 `75c4edd6560ee832bf7df4799c4e9389a7424e7056ac5f3cd5a9e07fc254996a`; counts: Combined Guitar 895, Bass 449. NO professional-reference read or score has occurred for V161 yet. Next: seal a separate one-shot V161 scoring preregistration/identity boundary, reviewer-audit the score workflow, then permit exactly one CPU score.**

## Standing safety — MUST PRESERVE
- CPU-only work and CPU scoring authorized at assistant discretion.
- Fresh explicit authorization required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional reference/frozen scorer are scoring-only and may not guide V161 generation/QC or post-generation retuning.
- V159 and V160 are closed forever.
- V161 generation is now consumed forever: no regeneration, repair, re-QC, threshold change, variant selection, rearm, or candidate replacement.
- V161 may receive at most one professional-reference score, under a separately sealed score boundary. No rescore or post-score retune.
- No human correction. Do not commit professional-tab screenshot bytes.
- Target remains automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF.

## V160 frozen terminal result
- Terminal score commit `1274dc20dbbe535cb8ff91ebf2e9d02078e3d9a9`.
- Guitar F1 primary `0.09975470155355683`, gross `0.2131370945761788`, measure+pitch `0.3881166530389752`.
- Bass F1 primary `0.18073485600794442`, gross `0.31777557100297915`, measure+pitch `0.5124131082423039`.
- Required gates 0.80/0.80. V160 consumed forever.

## V161 sealed design identities
- Preregistration blob `3d6b0412caaafbad39781f72a95fe29c72a38729`; commit `8b8a8810af2bb693ba13d5a82e85493c720e526f`.
- Numeric contract blob `51fe81400347119c95a2e6a1a63731070269a090`; commit `70e59185f8e9c853e0c8723f42cf97a061a8fa63`.

## V161 implementation identities
- event logic `85419429a2dae4baeb60232b756af4b127f87ce2`
- event fixture `11e1c8b56375fe9675804778e7154b89ac6f24e7`
- timebase builder `7ac9f91b807430ee2edb3631393c9261b6db980b`
- timebase QC `7743c8f2ca2d09546d4eeb09f1fef3d14d7a1970`
- transcriber `0137f211a79ef2b1a63d1485497eb00686b3afd1`
- structural QC `35fd631fe9a6fad37aac66526aa56e9ef8d5a26a`
- JSON-native fixture `c91e223d682b03faceb3d0704fa754a2d1c91af4`
- negative runtime guard `7dc6141cfc18d192d165f86d3eecbda3cf15851a`

## V161 static preflight — PASS / CONSUMED
- Workflow blob `2a774f4c03d9779ca764d4752254445569e7034b`; arm/head `3080d35519f07c1f058b1606f9fe5fb04057e57e`.
- Run `33207839556`, #1 attempt #1, job `98973355115`, conclusion success.
- Compile, negative runtime/leakage guard, synthetic event fixture, JSON-native regression, and final runtime absence proof all PASS.
- Never rerun static preflight.

## V161 pre-run identity receipt — PASS / SEALED
- `debug/v161-cpu-autonomous/pre-run-identity-receipt.json`.
- Seal commit `d5d6f844fca18e24d3199532eb52a4a7798e042a`; Git blob `bb1aed847c62b37e68f158a50614c48acf20781a`.
- Schema `dadrock.tabs.v161.pre-run-identity-receipt.v1`; validation PASS.
- At seal all runtime artifacts and generation workflow were absent; reference/scorer/candidate/score reads were zero; GPU/CUDA/Modal=0; main/Production=false.

## V161 sole CPU generation — PASS / CONSUMED
- Arm commit/head `418a25f82e4aa3742e995e4a3ce341bc48a24151`.
- Generation workflow Git blob `38cd491453c618f595d42bb6d42e87e478f35f0e`.
- Run `33208183041`, run #1 attempt #1, job `98974530460`, conclusion success.
- Pre-run guard PASS before pipeline.
- CPU pipeline PASS.
- Terminal freeze/self-seal PASS.
- Bot terminal commit `1b58ffcb8c2ee8fc7dd6152bf02c071d75035ade`, parent exactly the arm commit.
- `.github/workflows/v161-generate.yml` is absent after self-seal.
- **Never rearm, rerun, regenerate, repair, or re-QC V161.**

## V161 runtime artifacts — FROZEN
- Candidate `debug/v161-cpu-autonomous/generated.json`; Git blob `52178705ef3830f6849b71037cd283877aa7655f`; SHA256 `75c4edd6560ee832bf7df4799c4e9389a7424e7056ac5f3cd5a9e07fc254996a`.
- Generation receipt blob `6d691f060366e58988943fd627fe60b386029310`; SHA256 `d3f25db06d13ab3f9586a7cb26ad5724c4de76f5320a9ea2b1b7d77de423c8ac`.
- Environment receipt blob `bc327802943afe6affd31fc8d6d2eee28e264984`; SHA256 `83b7b7118e2ff02939e2304958d36fc1de2726fc8cce9e292aa173fa1a592ff7`.
- Timebase blob `3e6fd409d3cb04e24b6049fac9e2367ebba8b733`; SHA256 `079f50e4fc6ad622631a8f19ac1499076b26c0cf45d0f970689ee74ab0e03f57`.
- Timebase-QC blob `e7a0d1e9be2529ecc3175ccc631a30d134124268`; SHA256 `5bff3ef704b335cbb5681a4ae937fc7a49391aeb2982de37b313667ce9d5ff88`.
- Structural-QC blob `2146cf9f7b9e92ce704ef2118e711bd42ae2e093`; SHA256 `ba17ac241d438e15d13f0d45a93194e97151868805541dc252ea41caa1ae34ba`.
- Terminal-freeze blob `5ff59c993698b00df3503c6e22e036f181140aa4`.

## V161 candidate/result diagnostics — FROZEN, REFERENCE-BLIND
- Final stream counts: Combined Guitar `895`, Bass `449`; pre-grid excluded both `0`.
- Guitar: Basic Pitch raw 1404 → consolidated candidates 985 → admitted pre-grid-dedupe 978 → final 895. Onset refined 827; register repairs 382; admission rejects 7; standalone harmonic recovery added 0 and remains disabled.
- Bass: detected onsets 465 → retained/merged proposals 464 → admitted pre-grid-dedupe 449 → final 449. Onset refined 464; activity rejects 1; admission/additional-gate rejects 0; pitch-transition proposals 0 for this song.
- Compared with V160, Guitar final event count dropped from 2276 to 895; Bass is 449 vs V160 460. This is structural/reference-blind evidence only and is not a quality score.

## V161 structural QC — PASS / AUTHORITATIVE
- `debug/v161-cpu-autonomous/structural-qc.json`; validation `PASS`; errors `[]`.
- Candidate/hash/schema/code pins/single-run/write-once/hash chains/timebase/timebase-QC all PASS.
- Combined Guitar and Bass structures PASS.
- Guitar no-standalone-harmonic-recovery and cap-six checks PASS.
- Bass monophony cap-one PASS.
- Event admission values/refinement fields PASS.
- Candidate/generation/timebase reference-blind safety PASS.

## V161 terminal freeze — TERMINAL
- `debug/v161-cpu-autonomous/terminal-freeze.json`.
- `status=TERMINAL`, `outcome=STRUCTURAL_QC_PASS`, `lastCompletedStage=STRUCTURAL_QC_PASS`.
- `candidateAuthoritative=true`.
- `eligibleForProfessionalReferenceScoring=true`.
- `neverRearmV161=true`.
- `referenceRead=false`, professional reference paths `0`, score calls `0`, frozen scorer read `false`, V160 candidate read `false`, GPU/CUDA/Modal `false`, main/Production `false`.

## Current hard boundary
- V161 candidate and all generation/QC artifacts are immutable and consumed.
- Do not inspect professional-reference event details or scorer internals for tuning/design.
- Do not change V161 implementation/numerics/candidate based on any forthcoming score.
- Before scoring, seal a V161 score preregistration/identity receipt pinning: terminal commit, candidate hash/blob, structural-QC hash/blob, terminal-freeze blob, professional-reference identity, frozen scorer identity, score gate 0.80/0.80, one-score maximum, run #1 attempt #1, self-delete/self-seal behavior.
- Exactly one CPU professional-reference score may then run. No rerun/rescore regardless outcome.
- After score: freeze exact score report/terminal receipt, consume V161 forever, then design V162 only from permitted aggregate evidence.
- No GPU/Modal/CUDA without fresh explicit authorization; never touch main/Production.

## Exact next steps — RESUME HERE
1. Re-fetch branch/checkpoint before every write.
2. Locate the already-frozen professional-reference/scorer identities used by the V160 score without reading scorer/reference event content for design.
3. Create/seal `debug/v161-cpu-autonomous/score-preregistration.json` while no V161 score workflow/report/score-terminal exists.
4. Reviewer-audit `.github/workflows/v161-score.yml` without creating it: exact candidate/structural/terminal pins, one self-path push trigger, run #1 attempt #1, CPU-only, score once, write immutable report + score-terminal receipt, self-delete, never rerun.
5. After final absence proof, arm score workflow exactly once.
6. While score active: read-only observation only.
7. After score terminal self-seal: verify score report, gates, candidate unchanged, score workflow absent, checkpoint V161 consumed forever.
