# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V160 is terminal/consumed forever after one generation and one score. V161 successor design is now preregistered BEFORE implementation at `debug/v161-cpu-autonomous/preregistration.json`, seal commit `8b8a8810af2bb693ba13d5a82e85493c720e526f`, Git blob `3d6b0412caaafbad39781f72a95fe29c72a38729`. The V161 evidence boundary allows only frozen aggregate score summaries plus reference-blind implementation/runtime evidence; direct professional-reference reads, frozen-scorer reads for design, and event-level mining/reuse of the V160 candidate are forbidden. No V161 implementation code exists yet. Next: inspect only allowed V160 reference-blind source code and seal a numeric V161 implementation contract before writing any V161 code. GPU/Modal/CUDA remain 0; main/Production untouched.**

## Standing safety — MUST PRESERVE
- CPU-only work and CPU scoring are authorized at assistant discretion.
- Fresh explicit user authorization is required immediately before Modal, NVIDIA L4, CUDA, or any GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; direct reference/scorer content must not guide V161 implementation.
- Frozen aggregate score evidence may guide V161 only inside the sealed V161 preregistration boundary.
- V159 closed forever.
- V160 closed forever: no regeneration, re-QC, repair, threshold sweep, variant selection, rescore, or retune.
- V161 may not read/reuse/mine V160 candidate events for tuning.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Target remains automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## V160 terminal score evidence — FROZEN
- V160 score terminal commit `1274dc20dbbe535cb8ff91ebf2e9d02078e3d9a9`; score run `33206424361`, run #1 attempt #1, job `98968523271`.
- Score report Git blob `d280a19052228f71e4520db077686dfe9ae8f9bb`; SHA256 `32476d8d6036c72cb3b29bc4e67ec7c3fd5e7dc11b9334bd04730b4fd25e5e04`.
- Score-terminal Git blob `bc73cefe6653b9c398e65381256caa843182661d`; outcome `SCORE_GATE_FAIL`; scoreExecutionCount=1; candidateConsumed=true; scoreOpportunityConsumed=true; neverRerunOrRescoreV160=true.
- Combined Guitar primary F1 `0.09975470155355683`; gross ±2-step F1 `0.2131370945761788`; measure+pitch F1 `0.3881166530389752`; generated 2276 vs aggregate reference count 1393.
- Bass primary F1 `0.18073485600794442`; gross ±2-step F1 `0.31777557100297915`; measure+pitch F1 `0.5124131082423039`; generated 460 vs aggregate reference count 547.
- Required gates remain Guitar >=0.80 and Bass >=0.80.
- V160 score workflow self-deleted. Candidate/scorer/reference identities remained frozen; score used professional reference for scoring only; GPU/CUDA/Modal=false; main/Production=false.

## V161 preregistration — SEALED BEFORE IMPLEMENTATION
- File `debug/v161-cpu-autonomous/preregistration.json`.
- Seal commit `8b8a8810af2bb693ba13d5a82e85493c720e526f`; Git blob `3d6b0412caaafbad39781f72a95fe29c72a38729`.
- Schema `dadrock.tabs.v161.reference-blind-cpu-preregistration.v1`; status `PREREGISTERED_BEFORE_IMPLEMENTATION_CODE`; validation PASS.
- Created from branch head `55eabcfb9600b138c9920a8e7e33972365c5ccab` after V160 terminal score was fully checkpointed.

### V161 allowed evidence
- Frozen aggregate score summaries for V154, V157, V158, V160.
- Frozen V159 structural/runtime diagnosis identities.
- V160 structural-QC and timebase-QC identities.
- Reference-blind V160 implementation source may be read: timebase builder/QC, transcriber, structural QC, JSON-native fixture, negative runtime guard.
- Only aggregate V160 metrics copied into the preregistration may drive successor design.

### V161 forbidden leakage
- No direct professional-reference read for V161 design.
- No professional-reference event/measure mining.
- No frozen-scorer content read for V161 design.
- No V160 candidate event-level read, reuse, repair, regeneration, re-QC, or rescore.
- No reference-guided threshold sweep or variant selection.
- No same-song scoring loop during V161 implementation.
- No human correction; no main/Production modification.

### Frozen V161 failure interpretation
- Global V160 timebase/QC passed strongly; V161 will not treat the global beat grid as the primary failure.
- Guitar: severe over-generation/precision collapse plus timing disagreement. Generated 2276 vs aggregate reference count 1393; measure+pitch recall materially above primary recall.
- Bass: measure+pitch signal materially stronger than timing-aware score, generated count somewhat low; missing-note recovery plus onset/timing localization are primary successor targets.
- Gross ±2-step score materially exceeds ±0.5-step score for both instruments; V161 preregisters instrument-specific onset localization before final grid quantization.

### Frozen V161 architecture hypotheses
- H1 Guitar event consolidation: onset-gated pitch tracks, persistence merging, deterministic same-pitch refractory behavior, song-blind polyphony/event-density policy.
- H2 Instrument onset localization: local stem onset-strength refinement before 16-step grid mapping.
- H3 Bass transition segmentation: pitch transitions + onset evidence create discrete notes rather than sustained-frame event opportunities.
- H4 Activity gating: stem activity/confidence suppresses low-evidence events.
- H5 Confidence calibration: deterministic composite of model probability/harmonic support/spectral prominence/persistence/onset support.
- H6 Retain validated global grid while refining instrument timestamps locally.
- H7 V161 must be architectural, not a V160 micro-threshold tune.

### V161 song-blind validation boundary
Before any same-song processing V161 requires compile checks, negative reference/candidate leakage guard, synthetic repeated-note/sustained-note/polyphonic/onset-offset/bass-transition fixtures, JSON-native receipt fixture, static no-pitch-before-timebase-QC proof, and runtime-artifact/workflow absence proof.
- Same-song audio forbidden during static validation.
- Professional reference forbidden during static validation.
- Same-song score forbidden during implementation validation.

## Current hard boundary
- No V161 implementation code yet.
- A numeric `debug/v161-cpu-autonomous/implementation-contract.json` must be sealed before any V161 code change.
- All algorithm thresholds/windows/weights/tie-breaks must be fixed from reference-blind reasoning + song-blind fixtures, never selected by rescoring V160.
- V161 generation remains one-shot after static preflight + pre-run identity seal.
- No GPU/Modal/CUDA without fresh explicit user authorization.
- Never touch `main`/Production without explicit user direction.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint before every write.
2. Inspect only V161-allowed V160 reference-blind source to map existing Guitar/Bass event construction and quantization numerics.
3. Create/seal `debug/v161-cpu-autonomous/implementation-contract.json` with fixed CPU dependencies, retained global timebase rules, and exact V161 numerics for onset refinement, event consolidation, activity gating, confidence admission, Bass transition segmentation, Guitar polyphony/refractory behavior, grid mapping, receipt schemas, and song-blind fixtures.
4. Only after numeric contract seal, implement V161 modules under `validation/v161_cpu_autonomous/` plus a V161 negative runtime guard.
5. Run only song-blind/static validation before any audio processing; then seal exact implementation identities + one static preflight.
6. Preserve `CURRENT_STATE.md` frequently.
