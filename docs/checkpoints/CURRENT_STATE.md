# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V160 is terminal/consumed forever after one generation + one professional-reference score. V161 preregistration and numeric implementation contract are sealed. V161 implementation is now substantially built, but NO V161 song audio, Demucs, Basic Pitch, pYIN, candidate generation, reference read, or score has run. Implemented so far: pure event logic + song-blind fixture, V161 global timebase builder, independent timebase QC, event-refined transcriber, and independent structural QC. Next: add the V161 JSON-native regression fixture and negative leakage/runtime guard, then perform song-blind static review/validation only. No same-song processing may occur until exact implementation identities, one static preflight, and a pre-run identity seal are complete. GPU/Modal/CUDA remain 0; main/Production untouched.**

## Standing safety — MUST PRESERVE
- CPU-only work and CPU scoring are authorized at assistant discretion.
- Fresh explicit user authorization is required immediately before Modal, NVIDIA L4, CUDA, or any GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional reference and frozen scorer are scoring-only; direct content must not guide V161 implementation.
- V161 may use only aggregate frozen score evidence copied into its sealed preregistration.
- V159 closed forever.
- V160 closed forever: no regeneration, re-QC, repair, retune, threshold sweep, variant selection, or rescore.
- V161 may not read/reuse/mine V160 candidate events for tuning.
- No same-song score loop during V161 implementation.
- Do not commit professional-tab screenshot bytes.
- Target remains automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## V160 frozen terminal result
- V160 score terminal commit `1274dc20dbbe535cb8ff91ebf2e9d02078e3d9a9`.
- Sole score run `33206424361`, run #1 attempt #1, job `98968523271`.
- Score report blob `d280a19052228f71e4520db077686dfe9ae8f9bb`; SHA256 `32476d8d6036c72cb3b29bc4e67ec7c3fd5e7dc11b9334bd04730b4fd25e5e04`.
- Score terminal blob `bc73cefe6653b9c398e65381256caa843182661d`; outcome `SCORE_GATE_FAIL`; scoreExecutionCount=1; V160 candidate/score opportunity consumed forever.
- Guitar primary F1 `0.09975470155355683`; gross ±2-step F1 `0.2131370945761788`; measure+pitch F1 `0.3881166530389752`; generated 2276 vs aggregate reference count 1393.
- Bass primary F1 `0.18073485600794442`; gross ±2-step F1 `0.31777557100297915`; measure+pitch F1 `0.5124131082423039`; generated 460 vs aggregate reference count 547.
- Gates remain Guitar/Bass >= `0.80` each.

## V161 sealed design boundaries
### Preregistration
- `debug/v161-cpu-autonomous/preregistration.json`.
- Seal commit `8b8a8810af2bb693ba13d5a82e85493c720e526f`.
- Git blob `3d6b0412caaafbad39781f72a95fe29c72a38729`.
- Schema `dadrock.tabs.v161.reference-blind-cpu-preregistration.v1`; status `PREREGISTERED_BEFORE_IMPLEMENTATION_CODE`; PASS.
- Direct professional-reference/scorer reads for V161 design forbidden; V160 candidate event mining/reuse forbidden.

### Numeric implementation contract
- `debug/v161-cpu-autonomous/implementation-contract.json`.
- Seal commit `70e59185f8e9c853e0c8723f42cf97a061a8fa63`.
- Git blob `51fe81400347119c95a2e6a1a63731070269a090`.
- Schema `dadrock.tabs.v161.numeric-implementation-contract.v1`; status `SEALED_BEFORE_IMPLEMENTATION_CODE`; PASS.
- All windows, thresholds, weights, admission formulas, tie-breaks and static fixtures were frozen before code.

### Frozen architecture summary
- Retain V160 global timebase numerics/reference-blind CPU separation.
- Guitar Basic Pitch thresholds unchanged: onset `0.50`, frame `0.30`, minimum note `90ms`.
- Disable standalone Guitar harmonic-track recovery entirely; harmonic evidence becomes ranking/validation only.
- Merge same-MIDI Guitar fragments at <=`0.080s` gap.
- Guitar onset refinement radius ±6 frames; Bass ±8; movement requires positive-onset q60 and >=1.10× current strength.
- Guitar admission = `.45 confidence + .25 templateRank + .15 onset + .10 persistence + .05 activity`, minimum `.50`, activity >=`.05`; cap 6 notes/grid step.
- Bass adds stable pYIN pitch-transition proposals: >=`1.50` semitone change, both-sided voiced probability >=`.55`, min transition IOI `.060s`; onset/transition proposal merge radius `.045s`.
- Bass admission = `.40 voiced + .35 templateRank + .15 onset + .10 activity`, minimum `.42`, activity >=`.04`, plus fundamental present OR voiced>=`.60`; same-pitch refractory `.060s`; cap 1 note/grid step.
- Same frozen CPU dependencies as V160.

## V161 implementation identities — CURRENT
### Pure event logic
- `validation/v161_cpu_autonomous/event_logic_v161.py`
- Commit `d4c323c084e1448b3a147611774999fb9116c636`
- Git blob `85419429a2dae4baeb60232b756af4b127f87ce2`
- Implements sealed onset refinement, support/rank calculations, Guitar same-pitch consolidation, Bass median-smoothed pitch transitions, onset/transition proposal merging, Bass refractory handling, Guitar/Bass grid caps, and frozen admission formulas.

### Song-blind event-logic fixture
- `validation/v161_cpu_autonomous/test_event_logic_v161.py`
- Commit `8767ecd8661470424ba146a707afcfc5605c5cb6`
- Git blob `11e1c8b56375fe9675804778e7154b89ac6f24e7`
- Synthetic only; no song/reference data. Covers merge boundary, onset strong/weak/tie behavior, support/rank, Bass transition + voiced boundary, proposal merge, refractory, polyphony caps, admission bounds.

### V161 timebase builder
- `validation/v161_cpu_autonomous/build_timebase_v161.py`
- Commit `c1d7635c7441b236ceca5cc339a2cf0cdabac33c`
- Git blob `7ac9f91b807430ee2edb3631393c9261b6db980b`
- Version-isolates the validated V160 global timebase semantics; safety adds `V160CandidateRead=false`.

### V161 independent timebase QC
- `validation/v161_cpu_autonomous/timebase_qc_v161.py`
- Commit `6fbf5357cd60028573e0b854a4d550c24061cb77`
- Git blob `7743c8f2ca2d09546d4eeb09f1fef3d14d7a1970`
- Hard pre-pitch boundary; validates V161 timebase/input identities and reference-blind safety; records `pitchInferenceInvoked=false`.

### V161 event-refined transcriber
- `validation/v161_cpu_autonomous/transcribe_v161.py`
- Commit `4965267397047536081d0d72e902c7d881589aea`
- Git blob `0137f211a79ef2b1a63d1485497eb00686b3afd1`
- Pitch inference is below the frozen independent timebase-QC PASS runtime boundary.
- Guitar: Basic Pitch → same-pitch consolidation → local onset refinement → harmonic register/rank evidence → activity/admission → only `basic_pitch_consolidated`; no standalone harmonic recovery.
- Bass: detected onsets + smoothed pYIN pitch-transition proposals → deterministic proposal merge → local onset refinement → harmonic+pYIN pitch selection → activity/admission → same-pitch refractory → monophonic grid cap.
- Candidate safety explicitly forbids reference/V160-candidate/prior-score reads, sweeps, variants, human correction, GPU/Modal, Production change.

### V161 independent structural QC
- `validation/v161_cpu_autonomous/structural_qc_v161.py`
- Commit `4d25287b0c7f68ce4f74ed81aa49af87ca9280c1`
- Git blob `35fd631fe9a6fad37aac66526aa56e9ef8d5a26a`
- Independently recomputes frozen-grid event mapping, validates schemas/hash chains/code pins/write-once boundary, checks only `basic_pitch_consolidated` Guitar source, no harmonic recovery, Guitar cap6, Bass cap1, admission scores/refinement fields, and reference-blind safety.
- Uses V160-style recursive JSON-native receipt normalization with `allow_nan=false`.

## Validation status
- **No V161 song audio processing has run.**
- V161 Demucs executions=0; Basic Pitch executions=0; pYIN executions=0; candidate count=0; structural-QC runtime executions=0; professional-reference reads=0; score calls=0.
- GPU/CUDA/Modal=0. main/Production untouched.
- Implementation files above have not yet been consumed by a static preflight; exact identities may still change only for implementation correctness, never in response to same-song/reference output.

## Current hard boundary
- Do not run same-song audio/Demucs/pitch yet.
- Do not create/arm V161 generation workflow yet.
- Finish song-blind safety implementation first: JSON-native regression fixture + negative leakage/runtime guard.
- Then compile/run song-blind fixtures and reviewer-audit a single static preflight.
- Static preflight must not access song audio, professional reference, scorer, V160 candidate, or run Demucs/pitch.
- Only after static PASS: seal final implementation identities, create V161 pre-run identity receipt while runtime artifacts + generation workflow remain absent, reviewer-audit generation workflow, then arm exactly once.
- No GPU/Modal/CUDA without fresh explicit user authorization.
- Never touch `main`/Production without explicit user direction.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint before every write.
2. Add `validation/v161_cpu_autonomous/test_json_native_v161.py` matching the sealed V160 JSON-native regression contract.
3. Add `debug/v161-cpu-autonomous/negative-runtime-guard.py` proving generation/static code cannot open professional reference, frozen scorer, V160 candidate/prior score, and proving no pitch inference before independent timebase-QC PASS.
4. Reviewer-inspect all V161 Python modules for syntax/static contract drift; only song-blind corrections are allowed.
5. Checkpoint final implementation identities.
6. Create/audit exactly one `.github/workflows/v161-static-preflight.yml`, song-blind only; consume it once and never rerun.
7. Only after static preflight PASS, proceed to pre-run identity seal and one-shot CPU generation workflow review/arm.
