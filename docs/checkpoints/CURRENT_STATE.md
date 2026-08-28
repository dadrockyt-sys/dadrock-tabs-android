# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V161 is terminal/consumed forever. V162 successor preregistration and its complete numeric implementation contract are now sealed BEFORE implementation. V162 prereg: `debug/v162-cpu-autonomous/preregistration.json`, commit `5a3eecd2e4004ad254196bf926ecf8f1a97280e2`, blob `5c886fec4ac323b361d9128a51a25c6ccb03952b`. V162 numeric contract: `debug/v162-cpu-autonomous/implementation-contract.json`, commit `a11240eeef4ebf25a8bd9913dd0333892b6557f4`, blob `f3d8aa7cbfa1a65a6bc09e12d377f05e0ace3c87`, validation PASS. No V162 implementation/runtime files exist yet. Next: implement pure song-blind event/subdivision helpers + fixtures exactly to the sealed contract before audio-facing code.**

## Standing safety
- CPU-only work/scoring authorized at assistant discretion.
- Fresh explicit authorization required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159/V160/V161 closed forever; V161 never rerun/rescored/repaired/re-QC'd/retuned.
- V162 may use only frozen aggregate score/runtime evidence in its preregistration plus reference-blind V161 source/QC structure.
- No V161 candidate event mining/reuse; no professional-reference event/measure mining; no same-song score loop; no human correction.

## V161 terminal score — FROZEN
- Terminal commit `d1dd2f07bc5e07130a858981821d3b67bc2de78b`; run `33209465651`, #1 attempt #1, job `98978832375`; score workflow deleted.
- Guitar primary/gross/measure F1 `0.06993006993006994 / 0.1861888111888112 / 0.40297202797202797`; generated 895; matched 80/213/461.
- Bass primary/gross/measure F1 `0.20883534136546184 / 0.34136546184738953 / 0.5261044176706828`; generated 449; matched 104/170/262.
- Score report blob `08ebbd9f7ef38eeeb3defcce9aa445b21f120f57`; score-terminal blob `5b0550497432a6c5cb9b1b947694327b616f6241`; candidate consumed and score opportunity consumed forever.

## V162 preregistration — SEALED BEFORE CODE
- Commit `5a3eecd2e4004ad254196bf926ecf8f1a97280e2`; blob `5c886fec4ac323b361d9128a51a25c6ccb03952b`; PASS.
- Architecture: onset-aware Guitar rearticulation segmentation, active-Basic-Pitch-state-only reattack recovery, continuity-aware register inference, song-blind shared 16th subdivision lattice, instrument-specific step evidence, stable Bass pitch-state/rearticulation segmentation, no density targeting, no micro-tune.

## V162 numeric contract — SEALED BEFORE CODE
- `debug/v162-cpu-autonomous/implementation-contract.json`.
- Seal commit `a11240eeef4ebf25a8bd9913dd0333892b6557f4`; blob `f3d8aa7cbfa1a65a6bc09e12d377f05e0ace3c87`; schema `dadrock.tabs.v162.numeric-implementation-contract.v1`; PASS.
- Retains source/normalized audio identities, CPU deterministic `htdemucs_6s`, V161 beat/measure backbone, Basic Pitch thresholds 0.50/0.30/min90ms, harmonic CQT foundation, dependencies.

### Shared subdivision lattice — FROZEN
- 4 steps/beat; beat boundary fixed.
- shared onset = `0.65*unitDrums + 0.35*unitMix`.
- interior j=1,2,3 nominal quarter-beat subdivisions; search ±3 frames.
- move requires positive q55 + peak >=1.05× nominal; closest-to-nominal/lower-frame tie; Voronoi cell constraint; strictly increasing.
- event candidate steps nearest ±1; score `.70 temporal + .20 instrument onset + .10 shared onset`; non-nearest needs >=.05 margin; max correction one step.

### Guitar — FROZEN
- overlap fragments always consolidate; unsupported gaps <=120ms consolidate; supported q60/onset-support>=.30 reattack stays separate.
- independent active-state recovery: onset IOI 40ms; onset support>=.35; must intersect raw active Basic Pitch interval; parent confidence>=.35; harmonic rank>=.80 + fundamental above median; recovery score `.50 parentConfidence + .30 rank + .20 onset`; minimum .58; max 3 pitches/onset; no free harmonic pitch discovery.
- sequence register: same pitch-class context ±0.75s; no context => no repair; alternative needs fundamental, >=.15 rank gain, >=3 semitone context-distance improvement; sequence `.65 rank + .35 continuity`.
- segmented admission stays V161 `.45/.25/.15/.10/.05`, minimum .50, activity .05; cap6.

### Bass — FROZEN
- pYIN stable state voiced>=.50; median window7; nearest integer state MIDI; min stable run4 frames; bridge same MIDI gap<=2 frames; state change>=1 semitone; state median voiced>=.55.
- onset lookup radius4; detected onset support>=.20; same-pitch reattack support>=.30 q60 and IOI>=80ms; state-change proposal can exist without onset; merge45ms with fixed priority.
- harmonic/pYIN pitch window120ms and V161 admission retained; cap1.

### Mandatory static fixtures
- Guitar sustain/reattack/weak attack/active-state recovery/recovery cap.
- register no-context/context.
- nominal/shift/no-cross subdivision and event-step margin.
- Bass stable sustain/same-pitch reattack/state change/gap bridge.
- grid caps + JSON native + negative leakage/no-pitch-before-QC/absence proofs.

## Current hard boundary
- Numeric contract is immutable; no implementation-driven threshold retune.
- Implement pure `event_logic_v162.py` and `test_event_logic_v162.py` first; static/song-blind only.
- Then version-isolated timebase/QC/transcriber/structural QC/JSON test/negative guard.
- No song audio until one static preflight PASS + pre-run identity seal.
- V162 generation max one; separate one-score prereg required after structural PASS.
- No GPU/Modal/CUDA without fresh explicit authorization; never touch main/Production.

## Exact next steps — RESUME HERE
1. Re-fetch branch/checkpoint before each write.
2. Implement V162 pure event/subdivision helpers exactly to contract.
3. Add/run song-blind synthetic fixture source via one static workflow later; no song audio.
4. Implement audio-facing modules only after helpers/tests are frozen.
