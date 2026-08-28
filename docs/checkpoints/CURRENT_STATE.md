# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V160 is terminal/consumed forever. V161 preregistration + numeric implementation contract + implementation set are sealed in substance, and the sole song-blind static preflight is now PASS/consumed forever. Run `33207839556`, run #1 attempt #1, job `98973355115`, head `3080d35519f07c1f058b1606f9fe5fb04057e57e`, conclusion success. All eight V161 Python files compiled, the AST/runtime leakage guard PASSed, the synthetic event-logic fixture PASSed, the JSON-native regression fixture PASSed, and the final absence proof PASSed. NO V161 song audio, Demucs, Basic Pitch, pYIN, candidate generation, reference read, scorer read, or score has run. Next: create/seal the V161 pre-run identity receipt while all runtime artifacts + `.github/workflows/v161-generate.yml` remain absent, then reviewer-audit the one-shot CPU generation workflow before arming it. Never rerun the V161 static preflight.**

## Standing safety — MUST PRESERVE
- CPU-only work and CPU scoring are authorized at assistant discretion.
- Fresh explicit user authorization is required immediately before Modal, NVIDIA L4, CUDA, or any GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional reference/frozen scorer are scoring-only and may not guide V161 generation/QC.
- V161 may use only aggregate frozen score evidence copied into its preregistration.
- V159 closed forever.
- V160 closed forever: no regeneration, re-QC, repair, retune, sweep, variant selection, or rescore.
- V161 may not read/reuse/mine V160 candidate events or V160 score artifacts during generation/QC.
- No same-song score loop during V161 implementation.
- No human correction.
- Do not commit professional-tab screenshot bytes.
- Target remains automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## V160 frozen terminal result
- V160 score terminal commit `1274dc20dbbe535cb8ff91ebf2e9d02078e3d9a9`; one score forever.
- Guitar F1 primary `0.09975470155355683`, gross `0.2131370945761788`, measure+pitch `0.3881166530389752`.
- Bass F1 primary `0.18073485600794442`, gross `0.31777557100297915`, measure+pitch `0.5124131082423039`.
- Gates remain 0.80/0.80. V160 consumed forever.

## V161 sealed design identities
- Preregistration `debug/v161-cpu-autonomous/preregistration.json`; commit `8b8a8810af2bb693ba13d5a82e85493c720e526f`; blob `3d6b0412caaafbad39781f72a95fe29c72a38729`.
- Numeric contract `debug/v161-cpu-autonomous/implementation-contract.json`; commit `70e59185f8e9c853e0c8723f42cf97a061a8fa63`; blob `51fe81400347119c95a2e6a1a63731070269a090`.
- Both PASS and sealed before implementation.

## V161 final implementation identities consumed by static preflight
- `validation/v161_cpu_autonomous/event_logic_v161.py` — blob `85419429a2dae4baeb60232b756af4b127f87ce2`.
- `validation/v161_cpu_autonomous/test_event_logic_v161.py` — blob `11e1c8b56375fe9675804778e7154b89ac6f24e7`.
- `validation/v161_cpu_autonomous/build_timebase_v161.py` — blob `7ac9f91b807430ee2edb3631393c9261b6db980b`.
- `validation/v161_cpu_autonomous/timebase_qc_v161.py` — blob `7743c8f2ca2d09546d4eeb09f1fef3d14d7a1970`.
- `validation/v161_cpu_autonomous/transcribe_v161.py` — blob `0137f211a79ef2b1a63d1485497eb00686b3afd1`.
- `validation/v161_cpu_autonomous/structural_qc_v161.py` — blob `35fd631fe9a6fad37aac66526aa56e9ef8d5a26a`.
- `validation/v161_cpu_autonomous/test_json_native_v161.py` — blob `c91e223d682b03faceb3d0704fa754a2d1c91af4`.
- `debug/v161-cpu-autonomous/negative-runtime-guard.py` — blob `7dc6141cfc18d192d165f86d3eecbda3cf15851a`.

## V161 sole static preflight — PASS / CONSUMED
- Workflow `V161 static reference-blind preflight`.
- Path `.github/workflows/v161-static-preflight.yml`.
- Arm commit/head `3080d35519f07c1f058b1606f9fe5fb04057e57e`; parent `e2fd584adbe8000fff3caf6f4e4fcb9421354ebe`.
- Workflow Git blob `2a774f4c03d9779ca764d4752254445569e7034b`.
- Run ID `33207839556`; run number `1`; attempt `1`; job ID `98973355115`; conclusion `success`.
- Created `2026-08-28T20:20:54Z`; completed `2026-08-28T20:21:26Z`.
- Exact identity + runtime-absence guard PASS.
- All 8 Python files `py_compile` PASS.
- Negative runtime/leakage guard PASS: no professional-reference/scorer/V160-candidate runtime paths; timebase builder/QC contain no pitch calls; transcriber enforces independent timebase-QC PASS/hash before Bass/Guitar inference; sealed event/Guitar/Bass architecture tokens present; structural JSON-native ordering/rules present.
- Only explicit fixture dependency installed: `numpy==1.26.4`.
- Song-blind event fixture PASS.
- JSON-native regression fixture PASS, including historical NumPy `bool_` failure reproduction and NaN/Inf rejection.
- Final runtime absence proof PASS; branch remained exact static arm SHA; no V161 runtime files/generation workflow were created.
- **Never rerun V161 static preflight.**

## Frozen V161 architecture validated statically
### Guitar
- Basic Pitch thresholds unchanged: onset 0.50, frame 0.30, min 90ms.
- Standalone harmonic-track event recovery disabled; harmonic evidence ranking-only.
- Same-pitch fragments merge <=80ms.
- Onset refinement ±6 frames with q60 + 1.10× move requirement.
- Admission `.45 confidence + .25 template rank + .15 onset + .10 persistence + .05 activity`; min .50/activity .05.
- Grid dedupe and cap 6; source `basic_pitch_consolidated` only.

### Bass
- Adds median-smoothed pitch-transition proposals >=1.50 semitones, voiced>=.55 both sides, min transition IOI 60ms.
- Onset/transition merge 45ms; onset priority.
- Onset refinement ±8 frames; 120ms pitch window.
- Admission `.40 voiced + .35 template rank + .15 onset + .10 activity`; min .42/activity .04; fundamental present OR voiced>=.60.
- Same-pitch refractory 60ms; Bass cap 1/grid step.

## Validation status
- **V161 song processing count = 0.**
- Demucs=0; Basic Pitch=0; pYIN=0; candidate=0; runtime timebase=0; runtime QC=0; structural runtime QC=0.
- Professional-reference reads=0; frozen-scorer reads=0; score calls=0.
- GPU/CUDA/Modal=0. main/Production untouched.
- Static workflow is consumed/PASS and must not be edited/rerun for validation.

## Current hard boundary
- Do not alter V161 implementation numerics or architecture based on any later song output.
- Do not run song audio yet until pre-run identities and generation workflow review are sealed.
- Create V161 pre-run identity receipt while `environment-receipt.json`, `timebase.json`, `timebase-qc.json`, `generated.json`, `generation-receipt.json`, `structural-qc.json`, `terminal-freeze.json`, and `.github/workflows/v161-generate.yml` are absent.
- Pre-run receipt must pin prereg/contract/all eight implementation blobs + static workflow blob/run/job/head.
- Generation workflow must be CPU-only, one creation trigger, run #1 attempt #1, fresh source/normalization/Demucs/timebase/QC, no pitch before QC PASS, fresh transcriber + structural QC, self-delete/self-seal, no rerun.
- No manual/assistant branch writes while one-shot generation is active.
- No GPU/Modal/CUDA without fresh explicit user authorization.
- Never touch main/Production without explicit user direction.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint + V161 debug directory before each write.
2. Verify generation workflow and all V161 runtime artifacts remain absent.
3. Create/seal `debug/v161-cpu-autonomous/pre-run-identity-receipt.json` pinning exact identities and consumed static preflight.
4. Checkpoint the pre-run seal.
5. Reviewer-audit proposed `.github/workflows/v161-generate.yml` without creating it. Audit one-shot trigger, exact pins, CPU-only dependency set, source identity → normalization → fresh `htdemucs_6s` → environment receipt → V161 timebase → independent QC; QC PASS only then permits pitch/transcriber → independent structural QC.
6. Only structural-QC PASS may make candidate authoritative/scoring-eligible. Any QC/runtime failure terminal-freezes V161 and forbids rerun/score.
7. After audit PASS, prove workflow/runtime absence again and create generation workflow exactly once. While active: read-only observation only.
8. Fresh explicit authorization remains required before any Modal/NVIDIA L4/CUDA/GPU execution.
