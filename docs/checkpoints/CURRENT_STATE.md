# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V163 is fully terminal/consumed: authoritative exact-V162-algorithm candidate, structural QC PASS, sole professional-reference CPU score executed exactly once and terminally returned `SCORE_GATE_FAIL`. V163 must never be rerun/rearmed/repaired/retuned/regenerated/re-QC'd/rescored and may not advance to role/string/fret/technique/PDF. V164 is preregistered and its exact local-evidence numeric implementation contract is now sealed before any V164 implementation code.**

## Standing safety
- CPU-only reference-free work authorized at assistant discretion.
- Fresh explicit authorization required immediately before Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159/V160/V161/V162/V163 generation versions closed forever; V163 score opportunity closed forever.
- No professional-reference event/measure mining, candidate repair, score-informed retune, threshold sweep, variant selection, human correction, or second V163 score.
- V163 aggregate score was observed before V164 preregistration. V164 does **not** claim reviewer score-blindness; V164 design/numerics are quarantined from V163 score/reference evidence and may use only the enumerated pre-existing V162 static contract/code/test semantics plus song-blind synthetic fixtures.
- No GPU/Modal/CUDA without fresh explicit authorization.

## V163 frozen terminal facts
- Generation arm `4fb855b300c6d0331400b9aa642254be46752def`; run `33213512389`, #1 attempt #1, job `98991933938`; generation terminal commit `3b6f98750291a2f7b229c5e50cbf802752cf84d4`; outcome `STRUCTURAL_QC_PASS`.
- Candidate `debug/v163-cpu-autonomous/generated.json`: blob `f4eafb1488f139198cb7860a76f294c0e1775df8`; SHA256 `cc55d596a05bd8e9c0a149f6ba8263375c26fbb7334139a75697b58ca23c8c19`; Combined Guitar `1041`; Bass `404`.
- Structural QC blob `35624b8bfbb3580573bb49bd12049726ee364977`; SHA256 `ae899558f436c872e3a3ee306463fe62163652497f96d36cea2558be27aa2337`; PASS/errors `[]`.
- Score prereg blob `03f03f4005ab2ab84e93d06a107bc8f680a54775`; score arm `8809cb701d71c7bee73b1aad36c082fc5ea12ca0`; run `33214223643`, #1 attempt #1, job `98994146394`; exactly one frozen score call; terminal score commit `7bd8c813cac506811e3c144e5efe9edcd3abc561`; score workflow self-deleted.
- Score terminal blob `b7e6634d67b89632389f2be3edfdbe0162ff98dd`; `SCORE_GATE_FAIL`; score opportunity consumed; Combined Guitar primary F1 `0.059983566146261304`, Bass primary F1 `0.21661409043112514`, gates `0.80/0.80`; role/string/fret/technique/PDF not eligible.
- Score report blob `d10ae33aba35afd2547f94a3ec3dcd8443972fcf`; SHA256 `b87e745d1b3dafea2e99b841e8af028c55f8749341e5736fa5ec488ebf66cfd9`.
- Safety: no candidate modification/regeneration/re-QC, no threshold sweep/variant selection/human correction/post-score retune, no GPU/CUDA/Modal, no main/Production change.

## V164 preregistration — FROZEN
- `debug/v164-cpu-autonomous/preregistration.json`.
- Commit `1f0b4a904227491cbd5c62039d1ecbd500453966`; blob `05d255d75a6c1947891fba38d96d9399e3f75f9c`.
- Schema `dadrock.tabs.v164.local-evidence-invariance-preregistration.v1`; PASS; sealed before V164 numerics/code.
- Hypothesis: V162 song-global positive-quantile/q95 onset normalization creates nonlocal coupling; a distant loud/dense region can alter a local attack/subdivision decision despite an unchanged local neighborhood.
- Allowed design evidence only: V162 numeric contract blob `409da313ed03a6c232d6578d48b0da6aa35b000b`; event logic blob `9f9b33fd8c210ad581025b454cf69b6999aa544b`; song-blind fixture blob `e301f38db66f44193d799a9c1a02c99169823d45`.
- V163 score/reference/candidate rows and same-song audio behavior are forbidden V164 design evidence.

## V164 numeric implementation contract — FROZEN BEFORE CODE
- `debug/v164-cpu-autonomous/implementation-contract.json`.
- Commit `174a1c3850b4eb30335c9afd0e0ada776de37a3b`.
- Git blob `098f24282b59abba0f7cffa0793b344b76701724`.
- Schema `dadrock.tabs.v164.local-evidence-numeric-contract.v1`; PASS.
- Contract created from checkpoint head `eeb25674721ddf0b462a21efe916c2dbc1807099`.
- Pins V164 prereg blob `05d255d75a6c1947891fba38d96d9399e3f75f9c` and all V162 carry-forward source identities.

## V164 exact local-normalization numerics
### Event-local onset evidence
- Half-window `32` frames; inclusive `[center-32, center+32]`, clipped; no padding/wrap.
- Full interior population `65` frames; half-window `0.3715192743764172s` at 22050/256 geometry.
- Population = finite values `>0` only; minimum positive samples `1`.
- Support scale quantile remains `q95`; no-positive support = `0.0`; no-positive threshold = `null`.
- Existing Guitar q60/reattack support `0.30`, recovery support `0.35`; Bass onset support `0.20`, same-pitch reattack q60/support `0.30` remain unchanged.
- Remote evidence outside the 32-frame half-window may not influence the local decision.

### Beat-local subdivision evidence
- Positive population limited to enclosing beat start/end frames, inclusive.
- Subdivision threshold remains positive `q55`; no positive values => no interior move.
- Existing search radius `3`, move peak/nominal ratio `1.05`, Voronoi constraint and tie-break unchanged.
- Remote evidence outside the beat may not influence subdivision movement.

### Beat-local event-step support
- Candidate step instrument/shared q95 populations come only from the candidate step's enclosing lattice beat; terminal endpoint uses preceding beat.
- Temporal/instrument/shared weights remain `0.70/0.20/0.10`.
- Non-nearest margin remains `0.05`; max correction remains one step.

## V164 unchanged V162 architecture
- Basic Pitch onset/frame/min length `0.50/0.30/90ms`.
- Guitar segmentation gap `0.120s`, reattack radius `3`, recovery parent confidence `0.35`, template rank `0.80`, recovery score `0.58`, cap `3`.
- Register window `0.75s`, rank gain `0.15`, context-distance gain `3 semitones`.
- Guitar admission minimum/activity `0.50/0.05`, polyphony cap `6`.
- Bass pYIN/state/proposal rules, admission minimum/activity `0.42/0.04`, monophony cap `1` unchanged.
- Beat tracker/backbone unchanged.
- No density target, pitch-threshold retune, scorer tolerance change, or reference-guided correction.

## V164 mandatory invariance fixtures
- Remote perturbation factor `1,000,000` strictly outside target local population must not alter target decision.
- Local scale factors `0.1` and `10.0` over full target population must preserve booleans/frame/step and normalized support within rel/abs `1e-12`.
- All-zero local population => threshold null/support 0/no NaN/Inf.
- Boundary windows clip, no padding/wrap/reflection.
- Existing non-normalization V162 song-blind fixture outcomes remain unchanged.
- Static validation may not read song audio, V163 candidate/score, scorer, or professional reference.

## V164 implementation paths
- `validation/v164_cpu_autonomous/event_logic_v164.py`
- `validation/v164_cpu_autonomous/build_timebase_v164.py`
- `validation/v164_cpu_autonomous/timebase_qc_v164.py`
- `validation/v164_cpu_autonomous/transcribe_v164.py`
- `validation/v164_cpu_autonomous/structural_qc_v164.py`
- `validation/v164_cpu_autonomous/test_event_logic_v164.py`
- `validation/v164_cpu_autonomous/test_json_native_v164.py`
- `debug/v164-cpu-autonomous/negative-runtime-guard.py`
- future static workflow `.github/workflows/v164-static-preflight.yml`; generation workflow `.github/workflows/v164-generate.yml` only after static/pre-run seals.

## Current execution state
- V163 generation: terminal/consumed.
- V163 scoring: terminal/consumed.
- V164: prereg + numeric contract only; **no V164 implementation code yet**, no workflow, song processing, candidate, reference access, or score.
- V164 prereg does not authorize professional-reference scoring.
- GPU/CUDA/Modal executions `0`; main/Production unchanged.

## Hard boundary — NEXT
1. Never reopen V163 for tuning/scoring.
2. Implement only version-isolated V164 pure local-normalization/event helpers and mandatory song-blind invariance fixtures first, exactly to blob `098f24282b59abba0f7cffa0793b344b76701724`.
3. Do not read song audio, V163 candidate/score, scorer, or professional reference during implementation/static validation.
4. Preserve all unrelated V162 numerics/behavior exactly.
5. Compile/run only synthetic CPU fixtures; checkpoint before any workflow arm.
6. No V164 song processing until static preflight and pre-run identity are separately sealed.
7. No GPU/Modal/CUDA without fresh explicit authorization.
