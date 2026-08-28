# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V160 is terminal/consumed forever. V161 preregistration, numeric implementation contract, exact implementation set, consumed static preflight PASS, and pre-run identity receipt are now sealed. Pre-run receipt: `debug/v161-cpu-autonomous/pre-run-identity-receipt.json`, commit `d5d6f844fca18e24d3199532eb52a4a7798e042a`, Git blob `bb1aed847c62b37e68f158a50614c48acf20781a`, validation PASS. It was created while all V161 runtime artifacts and `.github/workflows/v161-generate.yml` were absent. NO V161 song audio, Demucs, Basic Pitch, pYIN, candidate, professional-reference read, scorer read, or score has run. Next: reviewer-audit the one-shot CPU generation workflow without creating it; only after audit PASS may one workflow-creation commit arm V161 generation.**

## Standing safety — MUST PRESERVE
- CPU-only work and CPU scoring authorized at assistant discretion.
- Fresh explicit authorization required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional reference/frozen scorer are scoring-only and may not guide V161 generation/QC.
- V159 and V160 are closed forever; V160 cannot be regenerated, repaired, re-QC'd, retuned, swept, variant-selected, or rescored.
- V161 generation/QC may not read/reuse/mine V160 candidate or V160 score artifacts.
- No same-song score loop; no human correction.
- Do not commit professional-tab screenshot bytes.
- Target remains automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF.

## V160 frozen terminal result
- Terminal score commit `1274dc20dbbe535cb8ff91ebf2e9d02078e3d9a9`.
- Guitar F1 primary `0.09975470155355683`, gross `0.2131370945761788`, measure+pitch `0.3881166530389752`.
- Bass F1 primary `0.18073485600794442`, gross `0.31777557100297915`, measure+pitch `0.5124131082423039`.
- Required gates 0.80/0.80. V160 consumed forever.

## V161 sealed design identities
- Preregistration blob `3d6b0412caaafbad39781f72a95fe29c72a38729`; commit `8b8a8810af2bb693ba13d5a82e85493c720e526f`.
- Numeric contract blob `51fe81400347119c95a2e6a1a63731070269a090`; commit `70e59185f8e9c853e0c8723f42cf97a061a8fa63`.

## V161 exact implementation identities
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
- All eight Python files compile PASS.
- Negative runtime/leakage guard PASS.
- Synthetic event-logic fixture PASS.
- JSON-native regression fixture PASS.
- Final runtime/generation-workflow absence proof PASS.
- NumPy 1.26.4 was the only explicit fixture dependency installed.
- No song audio, Demucs, pitch inference, reference/scorer read, candidate generation, or score occurred.
- **Never rerun or edit the static preflight for validation.**

## V161 pre-run identity receipt — PASS / SEALED
- `debug/v161-cpu-autonomous/pre-run-identity-receipt.json`.
- Seal commit `d5d6f844fca18e24d3199532eb52a4a7798e042a`; Git blob `bb1aed847c62b37e68f158a50614c48acf20781a`.
- Schema `dadrock.tabs.v161.pre-run-identity-receipt.v1`; status `SEALED_BEFORE_GENERATION_WORKFLOW`; validation PASS.
- Created from branch head `5583404d665feaa6987a3698f9be24716a1711c2`.
- Flat runtime-compatible `pinnedGitBlobs` pins prereg/contract/all implementation/static-test/guard files + static workflow.
- Pins static preflight run `33207839556`, run #1 attempt #1, job `98973355115`, head `3080d35519f07c1f058b1606f9fe5fb04057e57e`, success, neverRerun=true.
- At seal: timebase/timebase-QC/candidate/generation/environment/structural/terminal artifacts absent; generation workflow absent.
- At seal: referenceRead=false; professional paths=0; scorerRead=false; V160CandidateRead=false; prior candidate/score reads=false; score calls=0; song/Demucs/pitch executions=0; GPU/CUDA/Modal=0; main/Production=false.
- Trigger boundary: one workflow-creation trigger; expected generation run #1 attempt #1; rerun/duplicate/second arm forbidden; no branch writes while active.

## Frozen V161 architecture
- Retain validated V160 global timebase and CPU `htdemucs_6s` foundation.
- Guitar: unchanged Basic Pitch thresholds; disable standalone harmonic-track recovery; merge same-pitch <=80ms; local onset refinement ±6 frames; deterministic evidence/admission; cap6/grid step; source `basic_pitch_consolidated` only.
- Bass: add stable pYIN transition proposals; local onset refinement ±8 frames; onset+transition deterministic merge; harmonic+pYIN evidence/admission; same-pitch refractory; cap1/grid step.
- Structural QC independently validates frozen grid/hash chains/code pins/source rules/admission/refinement/reference-blind safety and JSON-native receipts.

## Validation status
- **V161 song processing count=0.**
- Demucs=0; Basic Pitch=0; pYIN=0; candidate=0; runtime QC=0; professional-reference reads=0; scorer reads=0; score calls=0; GPU/CUDA/Modal=0; main/Production changes=0.
- `.github/workflows/v161-generate.yml` does not exist.

## Current hard boundary
- Do not alter sealed V161 numerics/architecture based on later output.
- Reviewer-audit generation workflow before creation.
- Generation must verify pre-run blob `bb1aed847c62b37e68f158a50614c48acf20781a` and all exact implementation/static identities.
- CPU-only dependency pins; fresh source materialization → normalized WAV identity → fresh CPU htdemucs_6s → environment receipt → V161 timebase → independent timebase QC.
- No pitch inference before timebase-QC PASS.
- QC FAIL terminal-freezes without candidate. QC PASS alone permits transcriber/pitch.
- Independent structural-QC PASS alone may make candidate authoritative/scoring-eligible.
- Structural/runtime failure terminal-freezes V161, forbids rerun and score.
- Generation workflow must self-delete/self-seal. No assistant/manual branch writes while active.
- No GPU/Modal/CUDA without fresh explicit authorization; never touch main/Production.

## Exact next steps — RESUME HERE
1. Re-fetch branch/checkpoint before every write.
2. Reviewer-audit proposed `.github/workflows/v161-generate.yml` WITHOUT creating it against pre-run receipt + all pinned identities.
3. Audit one self-path push trigger, expected parent/one-file proof, run #1 attempt #1, CPU-only dependencies, exact source/normalization identities, fresh Demucs, environment receipt, timebase then independent QC, hard no-pitch-before-QC, transcriber, independent structural QC, terminal self-seal/self-delete.
4. After audit PASS, checkpoint audit result, re-prove workflow/runtime absence, substitute exact checkpoint head as expected parent, and create generation workflow exactly once.
5. While active: read-only observation only; never rerun.
6. After terminal self-seal, verify artifacts and checkpoint exact outcome.
