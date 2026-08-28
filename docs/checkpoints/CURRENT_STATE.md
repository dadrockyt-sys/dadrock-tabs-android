# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V161 is terminal/consumed forever after its sole score. V162 successor design is now preregistered BEFORE implementation at `debug/v162-cpu-autonomous/preregistration.json`, seal commit `5a3eecd2e4004ad254196bf926ecf8f1a97280e2`, Git blob `5c886fec4ac323b361d9128a51a25c6ccb03952b`, validation PASS. No V162 implementation code or runtime artifact exists. Next: seal exact V162 numeric implementation contract before any V162 code.**

## Standing safety — MUST PRESERVE
- CPU-only work and CPU scoring authorized at assistant discretion.
- Fresh explicit authorization required immediately before any Modal/NVIDIA L4/CUDA/GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- V159, V160, V161 closed forever. Never rerun/rescore/repair/re-QC/retune V161.
- V162 may use only frozen aggregate score/runtime evidence copied into its preregistration plus reference-blind V161 source/QC structure.
- No V161 candidate event mining/reuse; no professional-reference event/measure mining; no same-song score loop; no human correction.

## V161 terminal score — FROZEN
- Score terminal commit `d1dd2f07bc5e07130a858981821d3b67bc2de78b`; run `33209465651`, #1 attempt #1, job `98978832375`; score workflow deleted.
- Score report blob `08ebbd9f7ef38eeeb3defcce9aa445b21f120f57`; SHA256 `3bf1c7da8304f2507e764e16deae62f36f220881dfa1d5f1c808fdedd6c34867`.
- Score-terminal blob `5b0550497432a6c5cb9b1b947694327b616f6241`; `SCORE_GATE_FAIL`; scoreExecutionCount=1; candidateConsumed=true; scoreOpportunityConsumed=true; neverRerunOrRescoreV161=true.
- Guitar primary/gross/measure F1: `0.06993006993006994 / 0.1861888111888112 / 0.40297202797202797`; matched `80/213/461`; generated `895`; aggregate reference `1393`.
- Bass primary/gross/measure F1: `0.20883534136546184 / 0.34136546184738953 / 0.5261044176706828`; matched `104/170/262`; generated `449`; aggregate reference `547`.
- Gates remain `0.80/0.80`.

## V162 preregistration — SEALED BEFORE CODE
- Path `debug/v162-cpu-autonomous/preregistration.json`.
- Seal commit `5a3eecd2e4004ad254196bf926ecf8f1a97280e2`; Git blob `5c886fec4ac323b361d9128a51a25c6ccb03952b`.
- Schema `dadrock.tabs.v162.reference-blind-cpu-preregistration.v1`; status `PREREGISTERED_BEFORE_IMPLEMENTATION_CODE`; PASS.
- Created from clean V162-absence head `f0b746b2f16a2536c19b6aca372596ab79f86879`.

### Frozen V162 aggregate interpretation
- V161 Guitar reduced flooding and raised measure+pitch precision, but recall collapsed; fixed-gap same-pitch consolidation is treated as over-destructive.
- Guitar measure+pitch >> gross >> primary remains; local onset refinement alone did not solve event-to-grid/subdivision placement.
- V161 isolated register repairs were numerous (382); V162 makes octave/register inference sequence-aware rather than one-event-only.
- Bass improved across all score levels with similar count; keep useful onset/harmonic/pYIN foundation, but replace the zero-activation transition-recovery branch.

### Frozen V162 architecture hypotheses
- H1 onset-aware Guitar rearticulation segmentation: supported new attack stays separate; sustained fragments consolidate.
- H2 no standalone harmonic flooding; recovery only at independent attack intersecting persistent Basic Pitch state + harmonic support, deterministically capped.
- H3 continuity-aware octave/register inference using local same-pitch-class track context + spectral evidence.
- H4 song-blind subdivision lattice inside validated beat/measure backbone; no pure nearest-time global rounding.
- H5 instrument-specific onset evidence chooses among a shared canonical subdivision lattice.
- H6 Bass stable pitch-state segmentation: state changes + supported same-pitch reattacks; sustained states emit no duplicates.
- H7 activity/confidence are admission evidence, never a target reference density.
- H8 architectural successor only; no V161 threshold micro-tune.

### V162 mandatory song-blind fixtures
- Guitar sustain consolidation; supported same-pitch reattack; weak attack suppression.
- sequence-aware octave/register continuity.
- shifted subdivision lattice and ambiguity/tie behavior.
- Bass stable sustain; same-pitch reattack; stable pitch-state change.
- Guitar polyphony/Bass monophony caps; JSON-native fixture; no-pitch-before-QC; negative leakage guard; runtime/workflow absence proof.

## Current hard boundary
- No V162 implementation code yet.
- `debug/v162-cpu-autonomous/implementation-contract.json` must be sealed first with all numerics/tie-breaks/fixtures.
- Static validation must remain song/reference/V161-candidate blind.
- V162 generation remains one-shot CPU after static PASS + pre-run seal.
- No GPU/Modal/CUDA without fresh explicit authorization; never touch main/Production.

## Exact next steps — RESUME HERE
1. Re-fetch branch/checkpoint before every write.
2. Seal exact numeric V162 contract for: onset-aware consolidation/reattacks, attack-specific recovery cap, sequence-aware register rule, shared subdivision lattice + event step scoring, Bass stable-state segmentation/rearticulation, admission/caps, schemas, fixtures, one-shot boundaries.
3. Only after contract seal implement `validation/v162_cpu_autonomous/` and V162 negative guard.
4. Run song-blind static preflight only before any song audio.
