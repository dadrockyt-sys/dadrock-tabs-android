# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V160 is terminal/consumed forever after one generation and one score. V161 successor design is preregistered and its full numeric implementation contract is now sealed BEFORE implementation at `debug/v161-cpu-autonomous/implementation-contract.json`, seal commit `70e59185f8e9c853e0c8723f42cf97a061a8fa63`, Git blob `51fe81400347119c95a2e6a1a63731070269a090`. No V161 implementation code exists yet. All successor thresholds/windows/weights/tie-breaks are frozen reference-blind. Next: implement V161 modules exactly to the sealed contract, then run only song-blind/static validation before any same-song audio processing. GPU/Modal/CUDA remain 0; main/Production untouched.**

## Standing safety — MUST PRESERVE
- CPU-only work and CPU scoring are authorized at assistant discretion.
- Fresh explicit user authorization is required immediately before Modal, NVIDIA L4, CUDA, or any GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; direct reference/scorer content must not guide V161 implementation.
- V161 may use only the aggregate frozen score evidence copied into its preregistration.
- V159 closed forever. V160 closed forever: no regeneration, re-QC, repair, rescore, retune, threshold sweep, or variant selection.
- V161 may not read/reuse/mine V160 candidate events for tuning.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Target remains automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## V160 terminal evidence — FROZEN
- V160 terminal score commit `1274dc20dbbe535cb8ff91ebf2e9d02078e3d9a9`; sole score run `33206424361`, #1 attempt #1, job `98968523271`.
- Score report blob `d280a19052228f71e4520db077686dfe9ae8f9bb`; SHA256 `32476d8d6036c72cb3b29bc4e67ec7c3fd5e7dc11b9334bd04730b4fd25e5e04`.
- Score terminal blob `bc73cefe6653b9c398e65381256caa843182661d`; `SCORE_GATE_FAIL`; V160 consumed forever.
- Guitar primary F1 `0.09975470155355683`; gross F1 `0.2131370945761788`; measure+pitch F1 `0.3881166530389752`; generated 2276 vs aggregate reference count 1393.
- Bass primary F1 `0.18073485600794442`; gross F1 `0.31777557100297915`; measure+pitch F1 `0.5124131082423039`; generated 460 vs aggregate reference count 547.
- Gates remain 0.80/0.80.

## V161 preregistration — SEALED
- `debug/v161-cpu-autonomous/preregistration.json`; seal commit `8b8a8810af2bb693ba13d5a82e85493c720e526f`; blob `3d6b0412caaafbad39781f72a95fe29c72a38729`.
- Status `PREREGISTERED_BEFORE_IMPLEMENTATION_CODE`; validation PASS.
- Direct professional-reference/scorer reads for design forbidden; V160 candidate event mining/reuse forbidden.
- Frozen architecture hypotheses: Guitar consolidation, local instrument onset refinement, Bass pitch-transition segmentation, activity/confidence gating, retain validated global timebase, no micro-tune.

## V161 numeric implementation contract — SEALED BEFORE CODE
- `debug/v161-cpu-autonomous/implementation-contract.json`.
- Seal commit `70e59185f8e9c853e0c8723f42cf97a061a8fa63`; Git blob `51fe81400347119c95a2e6a1a63731070269a090`.
- Schema `dadrock.tabs.v161.numeric-implementation-contract.v1`; status `SEALED_BEFORE_IMPLEMENTATION_CODE`; validation PASS.
- Created from branch head `b2596d36d4accd2a2aa67972266dfabfda6b8a23` after V161 preregistration was checkpointed.

### Retained V161 foundations
- Same frozen source audio identity and normalized-WAV identity.
- CPU deterministic fresh `htdemucs_6s`: shifts=1, jobs=1, repeat=1, seed=0, Torch/math threads=1.
- Same V160 global timebase numerics: SR 22050, hop 256, `0.5*unitMix+0.5*unitDrums`, beat start120/tightness100, four-phase evidence, sequential absolute grid, Python round to 16-step measures.
- Same harmonic CQT foundation: 36 bins/octave, harmonics 1..5, weights `[1,.5,.3333333333,.25,.2]`, radius 1.
- Same dependencies: Python 3.10.x, Torch 2.8.0+cpu, NumPy 1.26.4, SciPy 1.13.1, SoundFile 0.12.1, Basic Pitch 0.4.0, Demucs 4.1.0, imageio-ffmpeg 0.6.0, librosa 0.11.0.

### V161 onset refinement — FROZEN
- Guitar local onset search radius ±6 frames; Bass ±8 frames.
- Move requires local peak >= global positive-onset q60 and >=1.10× current-frame onset strength.
- Peak tie-break: closest frame to original, then lower frame.
- Refine instrument timestamp before global-grid interpolation/rounding.

### V161 Guitar architecture — FROZEN
- Basic Pitch thresholds remain exactly V160: onset 0.50, frame 0.30, minimum note 90ms; no threshold micro-tune.
- **Standalone harmonic-track recovery disabled.** Harmonic evidence is validation/ranking only; no up-to-six extra notes per onset.
- Same-MIDI raw Basic Pitch fragments merge when gap <=0.080s.
- Register repair remains raw/±12 semitones with fundamental-above-median + strict template-score improvement.
- Admission score: 0.45 confidence + 0.25 template rank + 0.15 onset support + 0.10 persistence + 0.05 activity support.
- Admission minimum 0.50; activity support minimum 0.05.
- Grid dedupe `(absoluteStep,midi)`; maximum 6 Guitar notes per absolute step; deterministic ranking.
- Event source `basic_pitch_consolidated` only.

### V161 Bass architecture — FROZEN
- Bass MIDI 28..67; onset detector backtrack true; onset min IOI 35ms.
- pYIN frame 2048/hop256; 5-frame median smoothing; sigma 0.75; fusion 0.75 retained.
- Add pitch-transition proposals for finite smoothed MIDI changes >=1.50 semitones with both-side voiced probability >=0.55; transition min IOI 60ms.
- Union onset + transition proposals within 45ms; detected onset takes priority, then strongest onset/lower frame tie-break.
- Refined Bass pitch window 0.120s.
- Admission score: 0.40 voiced probability + 0.35 template rank + 0.15 onset support + 0.10 activity support; minimum 0.42; activity minimum 0.04; additionally require fundamental-present OR voiced probability>=0.60.
- Same-MIDI raw refractory 60ms; maximum 1 Bass note per absolute grid step; deterministic winner.

### Required song-blind fixtures — FROZEN
- Same-pitch Guitar merge boundary 80ms.
- Weak/strong onset refinement + tie handling.
- Bass 1.50-semitone transition / voiced-probability boundary.
- Guitar polyphony cap 6; Bass grid monophony cap 1.
- No standalone Guitar harmonic recovery.
- JSON-native serialization regression fixture retained.
- No same-song audio, professional reference, scorer, or V160 candidate in static validation.

## Current hard boundary
- V161 preregistration + numeric implementation contract are sealed; do not change numerics based on implementation output.
- No V161 song audio has run.
- Implement V161 code exactly to the sealed contract.
- Before any same-song processing: compile/static fixtures + negative leakage guard + static preflight + pre-run identity seal are mandatory.
- V161 generation maximum remains one; no rerun/repair after candidate creation.
- No GPU/Modal/CUDA without fresh explicit user authorization.
- Never touch `main`/Production without explicit user direction.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint before every write.
2. Implement `validation/v161_cpu_autonomous/event_logic_v161.py` first as pure deterministic song-blind helpers matching the contract.
3. Add `test_event_logic_v161.py` and run song-blind fixtures before integrating audio code.
4. Version-isolate V160 timebase builder/QC to V161 with unchanged global-timebase semantics.
5. Implement `transcribe_v161.py` using sealed Guitar consolidation/admission + Bass transition/onset architecture.
6. Implement V161 structural QC, JSON-native fixture, and negative runtime guard.
7. Compile/run static fixtures only; no song audio/Demucs/pitch execution.
8. Checkpoint frequently.
