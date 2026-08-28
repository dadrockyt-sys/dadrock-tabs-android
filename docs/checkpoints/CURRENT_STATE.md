# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V161 is terminal/consumed forever. V162 preregistration + numeric implementation contract are sealed, and the complete pre-static V162 implementation set is now present: pure event/subdivision logic + fixtures, subdivision timebase builder, independent timebase QC, state-segmented transcriber, independent structural QC, JSON-native fixture, and negative runtime/leakage guard. NO V162 song audio, Demucs, Basic Pitch, pYIN, candidate generation, professional-reference read, or score has run. Next: reviewer-audit and arm exactly one song-blind static preflight.**

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
- V161 candidate and sole score opportunity consumed forever.

## V162 sealed design
- Preregistration `debug/v162-cpu-autonomous/preregistration.json`; commit `5a3eecd2e4004ad254196bf926ecf8f1a97280e2`; blob `5c886fec4ac323b361d9128a51a25c6ccb03952b`; PASS.
- Numeric contract `debug/v162-cpu-autonomous/implementation-contract.json`; seal commit `a11240eeef4ebf25a8bd9913dd0333892b6557f4`; **authoritative current Git blob `409da313ed03a6c232d6578d48b0da6aa35b000b`**; PASS. Earlier checkpoint blob string was stale metadata and is superseded by this repository-fetched identity. Contract content/numerics were not changed.
- Architecture/numerics immutable: onset-aware Guitar state segmentation; active-Basic-Pitch-state-only reattack recovery; sequence-aware register; shared evidence-refined 16th lattice; bounded evidence step selection; stable Bass pitch-state/rearticulation segmentation.

## V162 complete pre-static implementation identities
- `validation/v162_cpu_autonomous/event_logic_v162.py` — current blob `9f9b33fd8c210ad581025b454cf69b6999aa544b`; final-beat extrapolation contract conformance fix committed `c294a49e1c6eb67316a98c46c041427f8180d90f`.
- `validation/v162_cpu_autonomous/test_event_logic_v162.py` — current blob `1e8dc629412dda23ac8106a35894aa0d86cac786`; Bass proposal-spacing fixture corrected at `d251983b22c8d5e9edd66f9137a649b79c044323`.
- `validation/v162_cpu_autonomous/build_timebase_v162.py` — blob `f7e9483aea16af770bcffe01ad8cfaf689d693b9`; commit `baa0236a231e6f34ac99829b08e8e8fda8f0c6db`.
- `validation/v162_cpu_autonomous/timebase_qc_v162.py` — blob `78acc9fd626039801011d039cca12686b72369c0`; commit `4d218c0fa146f34ce18444e970aa8cf758e5246b`.
- `validation/v162_cpu_autonomous/transcribe_v162.py` — current blob `fa163cafe2131aa73cdbb50df10d4e4912cff53b`; local-peak recovery-evidence conformance fix commit `c445e4bc9d663fef9d2cdbec472e713759f9906d`.
- `validation/v162_cpu_autonomous/structural_qc_v162.py` — blob `b7d3fa92fc9f3bed00931d19097e08cd91eab62b`; commit `4d3a74100fbd69f26ed4038efe9d73d8753b754b`.
- `validation/v162_cpu_autonomous/test_json_native_v162.py` — blob `654557363745f580f425252395542e9fb91adaad`; commit `b662a46643af72c2b4d847c078ff8524b06b5def`.
- `debug/v162-cpu-autonomous/negative-runtime-guard.py` — blob `8d40bc7f3dce9c9717e41fa1060c553434ad9959`; commit `fcd41e91a24d2e15caed71f07031677948580479`.

## V162 implemented architecture
### Shared timebase/subdivision
- V161 beat tracker/phase backbone retained.
- Shared onset `0.65*unitDrums + 0.35*unitMix`.
- Every beat anchor remains fixed at absolute steps divisible by 4.
- Interior 16ths refined with sealed ±3-frame/q55/1.05/Voronoi rule.
- One final beat interval extrapolated from median of last up-to-8 positive IBIs; full `subdivisionTimesSeconds` + sequential absolute steps frozen in timebase.
- Independent timebase QC reloads only mix/drums, rebuilds shared envelope/lattice, requires exact lattice/anchor/final-extrapolation agreement before pitch.

### Guitar
- Basic Pitch thresholds unchanged 0.50/0.30/min90ms.
- <=120ms same-pitch gaps merge only when no supported reattack; overlaps always merge; >120ms stays separate.
- Existing segmented attacks use V161 local onset refinement.
- Sequence register uses same-pitch-class context ±0.75s; no context => no repair; alternatives require fundamental + rank/context gains.
- Independent attack recovery can only recover MIDI pitches active in raw Basic Pitch intervals at the local attack peak; rank/fundamental/parent confidence/recovery score gates fixed; cap3; no free harmonic pitch discovery.
- Segmented admission retained; evidence-based event step selection uses nearest±1 lattice candidates; final cap6.

### Bass
- pYIN median7 -> stable integer MIDI states, min4 frames, voiced gates, short same-MIDI gap bridge.
- Proposals from detected onset, supported same-pitch reattack, or stable state change; state-change can activate without detected onset.
- Fixed proposal priority/45ms merge; V161 harmonic+pYIN pitch evidence/admission retained; evidence step mapping; final cap1.

### Independent structural QC
- Recomputes the shared subdivision lattice from fresh mix/drums stems.
- Recomputes `select_event_step()` for every candidate note from candidate start + fresh instrument/shared onset envelopes.
- Enforces exact hash/schema/code pins, one-shot environment, allowed sources, no standalone harmonic recovery, sequence-context metadata for repairs, Bass state metadata, score ranges, dedupe/caps, and reference-blind safety.

## Static safety
- Event fixture is song-blind NumPy-only and covers sustain/reattack/recovery/register/subdivision/final extrapolation/Bass state/caps.
- JSON-native fixture reproduces raw NumPy JSON failure and proves normalization/round-trip/nonfinite rejection.
- Negative guard uses AST/text only; pre-pitch builder/QC cannot import Basic Pitch or call `pyin/yin/predict`; generation runtime cannot contain reference/scorer/V161 candidate/score/workflow paths; validates exact sealed architecture tokens and QC-before-pitch main-call ordering.

## Validation status
- No V162 static-preflight workflow exists yet.
- No V162 runtime artifacts exist yet beyond prereg/contract/negative guard.
- Song processing=0; Demucs=0; Basic Pitch=0; pYIN=0; candidate=0; runtime QC=0; professional-reference/scorer reads=0; score calls=0; GPU/CUDA/Modal=0; main/Production=0.

## Current hard boundary
- Reviewer-audit one static workflow before creation.
- Static workflow may install NumPy only; no song/source/reference/scorer/V161-candidate access, no librosa/Demucs/Basic Pitch execution.
- It must pin all exact blobs above, compile all seven V162 validation Python files + negative guard, run negative guard against itself, run event fixture and JSON fixture, and prove all runtime artifacts + generation workflow absent.
- Static creation is sole trigger; expected run #1 attempt #1; never rerun.
- Only after static PASS: seal final identities into pre-run receipt, then reviewer-audit one-shot CPU generation.
- No GPU/Modal/CUDA without fresh explicit authorization; never touch main/Production.

## Exact next steps — RESUME HERE
1. Re-fetch branch/checkpoint and prove `.github/workflows/v162-static-preflight.yml`, `.github/workflows/v162-generate.yml`, and all V162 runtime receipts/candidate are absent.
2. Reviewer-audit/create sole V162 static preflight with exact pins.
3. Observe read-only; never rerun.
4. If PASS, checkpoint run/job/head and seal V162 pre-run identities.
