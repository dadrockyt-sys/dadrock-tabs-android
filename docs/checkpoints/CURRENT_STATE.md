# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V161 is terminal/consumed forever. V162 preregistration + numeric implementation contract are sealed, and the first pure song-blind V162 implementation layer is now present: `event_logic_v162.py` plus `test_event_logic_v162.py`. No V162 song audio, Demucs, Basic Pitch, pYIN, runtime artifact, professional-reference read, or score has run. Next: integrate the sealed shared subdivision lattice into V162 timebase/QC, then implement the audio-facing transcriber/structural QC without changing any frozen numeric.**

## Standing safety
- CPU-only work/scoring authorized at assistant discretion.
- Fresh explicit authorization required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159/V160/V161 closed forever; never rerun/rescore/repair/re-QC/retune V161.
- V162 may use only frozen aggregate evidence copied into its preregistration plus reference-blind V161 source/QC structure.
- No V161 candidate event mining/reuse; no professional-reference event/measure mining; no same-song score loop; no human correction.

## V161 terminal score — FROZEN
- Terminal commit `d1dd2f07bc5e07130a858981821d3b67bc2de78b`; score run `33209465651`, #1 attempt #1, job `98978832375`; workflow deleted.
- Guitar primary/gross/measure F1 `0.06993006993006994 / 0.1861888111888112 / 0.40297202797202797`; generated 895; matched 80/213/461.
- Bass primary/gross/measure F1 `0.20883534136546184 / 0.34136546184738953 / 0.5261044176706828`; generated 449; matched 104/170/262.
- Score report blob `08ebbd9f7ef38eeeb3defcce9aa445b21f120f57`; score-terminal blob `5b0550497432a6c5cb9b1b947694327b616f6241`; candidate/score opportunity consumed forever.

## V162 sealed design
- Preregistration: `debug/v162-cpu-autonomous/preregistration.json`; commit `5a3eecd2e4004ad254196bf926ecf8f1a97280e2`; blob `5c886fec4ac323b361d9128a51a25c6ccb03952b`; PASS.
- Numeric contract: `debug/v162-cpu-autonomous/implementation-contract.json`; commit `a11240eeef4ebf25a8bd9913dd0333892b6557f4`; blob `f3d8aa7cbfa1a65a6bc09e12d377f05e0ace3c87`; PASS.
- Architecture/numerics are immutable: onset-aware Guitar segmentation, active-state-only reattack recovery, sequence-aware register, shared evidence-refined subdivision lattice, bounded event-step selection, stable Bass pitch-state segmentation/rearticulation.

## V162 pure implementation identities
- `validation/v162_cpu_autonomous/event_logic_v162.py` — commit `4474d48c78bc5d6f0de5d60fda30205404ed9db5`; Git blob `5d2441687d59cd09fdb7b7c282c292c34f0fe519`.
- `validation/v162_cpu_autonomous/test_event_logic_v162.py` — commit `355f9270a50ea95f63fdc30aad41fd40e4c9d4bf`; Git blob `d58de054b8e5114d6746effec3991340feefe075`.
- Both are song-blind/source-pure; event logic imports only Python stdlib + NumPy. The synthetic fixture imports only event logic + NumPy.

### Pure helper coverage implemented
- Guitar unsupported sustain-gap consolidation vs supported same-pitch reattack preservation.
- Active-state reattack recovery restricted to raw Basic Pitch intervals active at attack; deterministic top-3 cap; free harmonic pitch discovery impossible by API shape.
- Existing-attack exclusion.
- Sequence register: no context => raw; contextual repair only under sealed rank/fundamental/context gates.
- Shared beat subdivision refinement with ±3-frame/q55/1.05/Voronoi/strict-order constraints.
- Event step scoring and one-neighbor bounded choice with non-nearest margin.
- Bass median smoothing/stable states/short-gap bridge/state lookup/detected onset/same-pitch reattack/state-change proposals.
- deterministic Guitar cap6/Bass cap1.

### Synthetic fixture coverage implemented
- Guitar sustain merge, strong reattack separation, overlap merge, >120ms separation.
- active-state recovery-only + cap3 + existing-attack exclusion.
- no-context register protection, valid contextual octave repair, insufficient-rank rejection.
- fixed beat boundaries, qualifying subdivision shift, strict ordering, bounded event-step selection.
- Bass stable state + two-frame gap bridge, same-pitch reattack, onset-independent state change, no duplicate sustain, median7 outlier suppression.
- grid caps and explicit safety declarations (`songAudioRead=false`, `professionalReferenceRead=false`, `V161CandidateRead=false`, `gpuUsed=false`).

## Frozen V162 key numerics
- Shared onset `0.65*unitDrums + 0.35*unitMix`; interior 16ths search ±3 frames; q55; move ratio >=1.05; Voronoi constrained.
- Event step candidates nearest±1; `.70 temporal + .20 instrument onset + .10 shared onset`; non-nearest margin >=.05.
- Guitar: unsupported gap <=120ms merges; reattack support>=.30/q60; active recovery support>=.35, parent conf>=.35, rank>=.80 + fundamental, recovery>=.58, cap3; register context ±.75s, rank gain .15, distance gain3; admission min .50/activity .05; cap6.
- Bass: voiced state>=.50, median7, stable4 frames, bridge gap2, state median vp>=.55; reattack>=.30/q60/80ms; state change>=1 semitone; proposal merge45ms; admission min .42/activity .04; cap1.

## Validation status
- No V162 static workflow yet; pure fixtures have been authored but not executed in Actions yet.
- V162 song processing=0; Demucs=0; Basic Pitch=0; pYIN=0; candidate=0; runtime QC=0; reference/scorer reads=0; score calls=0; GPU/CUDA/Modal=0; main/Production=0.

## Current hard boundary
- Do not change sealed numerics based on fixture/runtime output.
- Implement V162 timebase/QC/transcriber/structural QC/JSON test/negative guard exactly to contract.
- One song-blind static preflight must compile all files and execute pure fixtures before any song audio.
- No song audio until static PASS + pre-run identity seal.
- V162 generation maximum one; separate one-score prereg required after structural PASS.
- No GPU/Modal/CUDA without fresh explicit authorization; never touch main/Production.

## Exact next steps — RESUME HERE
1. Re-fetch branch/checkpoint before each write.
2. Implement `build_timebase_v162.py`: retain V161 beat/phase backbone and add shared refined subdivision lattice to artifact.
3. Implement `timebase_qc_v162.py`: independently recompute/validate beat backbone and subdivision lattice invariants before pitch.
4. Implement V162 transcriber using pure helpers and subdivision step selection.
5. Implement independent structural QC, JSON-native test, negative guard.
6. Arm sole static preflight only after complete implementation set is frozen.
