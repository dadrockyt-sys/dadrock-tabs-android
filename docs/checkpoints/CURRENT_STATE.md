# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V160 is terminal/consumed forever. V161 preregistration + numeric implementation contract are sealed, and the complete pre-static V161 implementation set is now present: event logic, song-blind event fixture, global timebase builder, independent timebase QC, event-refined transcriber, independent structural QC, JSON-native regression fixture, and negative runtime/leakage guard. NO V161 song audio, Demucs, Basic Pitch, pYIN, candidate generation, professional-reference read, or score has run. Next: reviewer-audit and create exactly one song-blind static preflight that compiles all V161 modules, runs both synthetic fixtures + negative guard, pins all exact Git blobs, and proves all V161 runtime artifacts/generation workflow are absent. The static preflight must never be rerun.**

## Standing safety — MUST PRESERVE
- CPU-only work and CPU scoring are authorized at assistant discretion.
- Fresh explicit user authorization is required immediately before Modal, NVIDIA L4, CUDA, or any GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional reference/frozen scorer are scoring-only and may not guide V161 implementation.
- V161 may use only aggregate frozen score evidence copied into its sealed preregistration.
- V159 closed forever.
- V160 closed forever: no regeneration, re-QC, repair, retune, threshold sweep, variant selection, or rescore.
- V161 may not read/reuse/mine V160 candidate events or score artifacts during generation/QC.
- No same-song score loop during V161 implementation.
- No human correction.
- Do not commit professional-tab screenshot bytes.
- Target remains automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## V160 terminal result — FROZEN
- Terminal score commit `1274dc20dbbe535cb8ff91ebf2e9d02078e3d9a9`; sole score run `33206424361`, #1 attempt #1, job `98968523271`.
- Guitar primary F1 `0.09975470155355683`; gross `0.2131370945761788`; measure+pitch `0.3881166530389752`; generated 2276 vs aggregate ref count 1393.
- Bass primary F1 `0.18073485600794442`; gross `0.31777557100297915`; measure+pitch `0.5124131082423039`; generated 460 vs aggregate ref count 547.
- Required gates remain 0.80/0.80. V160 consumed forever.

## V161 sealed design
- Preregistration `debug/v161-cpu-autonomous/preregistration.json`; commit `8b8a8810af2bb693ba13d5a82e85493c720e526f`; blob `3d6b0412caaafbad39781f72a95fe29c72a38729`; PASS.
- Numeric contract `debug/v161-cpu-autonomous/implementation-contract.json`; commit `70e59185f8e9c853e0c8723f42cf97a061a8fa63`; blob `51fe81400347119c95a2e6a1a63731070269a090`; PASS.
- Contract froze all CPU dependencies, global-grid numerics, onset-refinement windows/thresholds, Guitar consolidation/admission rules, Bass transition/admission rules, structural-QC rules, static fixtures, and one-shot boundaries before V161 code.

## V161 complete pre-static implementation identities
- `validation/v161_cpu_autonomous/event_logic_v161.py` — commit `d4c323c084e1448b3a147611774999fb9116c636`; blob `85419429a2dae4baeb60232b756af4b127f87ce2`.
- `validation/v161_cpu_autonomous/test_event_logic_v161.py` — commit `8767ecd8661470424ba146a707afcfc5605c5cb6`; blob `11e1c8b56375fe9675804778e7154b89ac6f24e7`.
- `validation/v161_cpu_autonomous/build_timebase_v161.py` — commit `c1d7635c7441b236ceca5cc339a2cf0cdabac33c`; blob `7ac9f91b807430ee2edb3631393c9261b6db980b`.
- `validation/v161_cpu_autonomous/timebase_qc_v161.py` — commit `6fbf5357cd60028573e0b854a4d550c24061cb77`; blob `7743c8f2ca2d09546d4eeb09f1fef3d14d7a1970`.
- `validation/v161_cpu_autonomous/transcribe_v161.py` — commit `4965267397047536081d0d72e902c7d881589aea`; blob `0137f211a79ef2b1a63d1485497eb00686b3afd1`.
- `validation/v161_cpu_autonomous/structural_qc_v161.py` — commit `4d25287b0c7f68ce4f74ed81aa49af87ca9280c1`; blob `35fd631fe9a6fad37aac66526aa56e9ef8d5a26a`.
- `validation/v161_cpu_autonomous/test_json_native_v161.py` — commit `1abb7ba70f63ce63b31d11241aecf99199ca03d2`; blob `c91e223d682b03faceb3d0704fa754a2d1c91af4`.
- `debug/v161-cpu-autonomous/negative-runtime-guard.py` — commit `585c618ab1dc29e8833fde6cf4f5b251e7c39dbf`; blob `7dc6141cfc18d192d165f86d3eecbda3cf15851a`.

## Frozen V161 architecture represented by implementation
### Guitar
- Basic Pitch thresholds unchanged from V160: onset 0.50, frame 0.30, min length 90ms.
- Standalone harmonic-track note recovery is disabled; harmonic data is evidence/ranking only.
- Same-MIDI raw fragments merge at <=80ms gap.
- Local onset refinement ±6 frames with q60/1.10 move criteria.
- Admission = `.45 confidence + .25 templateRank + .15 onset + .10 persistence + .05 activity`; minimum .50 and activity >=.05.
- Grid dedupe `(step,midi)` and deterministic polyphony cap 6.
- Only Guitar source `basic_pitch_consolidated`.

### Bass
- Retains onset detector/pYIN/harmonic fusion foundation.
- Adds median-smoothed pitch-transition proposals for >=1.50 semitones, both-side voiced probability >=.55, min transition IOI 60ms.
- Onset + transition merge radius 45ms; onset priority.
- Local onset refinement ±8 frames; pitch analysis window 120ms.
- Admission = `.40 voiced + .35 templateRank + .15 onset + .10 activity`; minimum .42; activity >=.04; fundamental-present OR voiced>=.60.
- Same-pitch raw refractory 60ms and Bass grid cap 1.

## Static safety implementation
### JSON-native regression fixture
- `test_json_native_v161.py` is synthetic only.
- Reproduces NumPy `bool_` raw JSON failure, verifies bool/int/float/array/nested normalization, exact JSON round trip, native bool checks, and NaN/Inf rejection.
- Declares songAudioRead=false, Demucs=false, pitchInference=false, professionalReferenceRead=false, frozenScorerRead=false, V160CandidateRead=false.

### Negative runtime/leakage guard
- `negative-runtime-guard.py` uses source text + AST only.
- Forbids runtime literals for professional reference, frozen scorer, V160 candidate, V160 score artifacts, and V160 generation/score workflow paths.
- Proves V161 timebase builder/QC contain no Basic Pitch import or pitch primitive calls.
- Proves transcriber calls `validate_runtime_boundary()` before `bass_events()`/`guitar_events()` and explicitly requires exact independent timebase-QC PASS/hash chain, CPU environment, referenceRead=false, and V160CandidateRead=false.
- Mechanically checks sealed Guitar/Bass architecture tokens, event-logic constants/functions, structural JSON-native ordering, and song-blind fixture coverage.

## Validation status
- **No V161 song processing has run.**
- Demucs=0; Basic Pitch=0; pYIN=0; candidate=0; runtime QC=0; reference reads=0; score calls=0; GPU/CUDA/Modal=0; main/Production changes=0.
- No V161 static-preflight workflow exists yet.
- No V161 runtime artifacts exist yet.
- Pre-static implementation identities above are the exact set to be reviewed by the static preflight. If static checks reveal implementation correctness defects, fixes may be made only from song-blind evidence and the numeric contract may not be changed.

## Current hard boundary
- Do not run same-song audio/Demucs/pitch.
- Do not create V161 generation workflow.
- Reviewer-audit a single song-blind static preflight before creating it.
- Static preflight may install NumPy only for synthetic fixtures; it must not install/run Demucs/Basic Pitch/librosa inference stack or access song audio/reference/scorer/V160 candidate/score artifacts.
- Static preflight creation must be its sole trigger, run #1 attempt #1, exact blob pins, compile all eight Python files, run event fixture, run JSON fixture, run negative guard against itself, and prove runtime/generation artifacts absent.
- Never rerun static preflight after consumption.
- Only after static PASS may final implementation identities be sealed into a pre-run identity receipt and one-shot generation be reviewed.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint before every write.
2. Reviewer-audit proposed `.github/workflows/v161-static-preflight.yml` without creating it.
3. Audit exact Git blobs listed above, single self-path push trigger, run #1 attempt #1, no song/reference/scorer/V160-candidate access, NumPy-only fixture dependency, py_compile all eight files, execute both fixtures + negative guard, and final absence proof.
4. After audit PASS, re-fetch branch/checkpoint and prove static workflow + V161 runtime/generation artifacts remain absent; then create static preflight exactly once.
5. Observe sole static run. Never rerun.
6. If PASS, checkpoint run/job/head identities and create V161 pre-run identity seal while runtime/generation artifacts remain absent.
7. No GPU/Modal/CUDA without fresh explicit user authorization. Never touch main/Production without explicit user direction.
