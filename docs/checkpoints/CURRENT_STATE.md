# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly reference/scorer-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Calibration Iteration 002 is now frozen and is the current best candidate: Guitar 41.92%, Bass 71.87%. It uses only the already-stored audio-derived lattice alternatives, with no MIDI/cardinality changes. The next major target is recall/pitch: instrument the CPU front-end to preserve and analyze near-miss/rejected event pools, then use the scorer to tune deterministic admission/recovery behavior. `main`/Production remain untouched.**

## Standing V167 methodology
- Calibration only, not holdout/generalization performance.
- Frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`; frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`.
- Reference/scorer may grade complete predeclared variants and select whole deterministic rules/parameter settings; it may not directly supply or copy candidate events.
- Direct/manual copying of professional-reference events into generated output is forbidden.
- CPU work authorized; fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit direction.

## Closed V166 anchor
- Terminal commit `7f5f5f19f6ec413fc772a9839be5497ecb2790e3`; candidate blob `c36a4d1e14ca66235b51a866ad3908322834efff`; Guitar 1050, Bass 402; structural QC PASS.
- V159–V166 generations closed forever.

## V167 Iteration 001 — FROZEN
- Terminal commit `dcb61f0eeeedd1d1ea69cec257d374f7b83a084b`.
- Candidate blob `1b73d6ece977fb976fa1c503997e6434d4e4811a`.
- Guitar 40.36021285304953%; Bass 70.60063224446786%.
- Shared global phase correction `-12` grid steps.

## Frozen step-rule sweep
- Code blob `14cac9e217f65f72933c72ee349523ca9681fc21`.
- Run `33227803023`, job `99034806131`; terminal commit `81593418a2f4e429e7eb5a8423de9f92037b0e3d`.
- Report blob `2096d3caa58b6ce7d6ab57aeaa7512989e2e4acd`.
- Selected Guitar rule `max_score_x_shared`; selected Bass rule `max_score_x_mean_support`.

## V167 Calibration Iteration 002 — CURRENT BEST / FROZEN SUCCESS
- Transform `validation/v167_single_song_calibration/apply_step_rules_v167.py`, blob `00dc94081117664890d1dc5539bf5e69fedf76fa`.
- One-shot run `33227898407`, run 1, attempt 1, job `99035077043`; all identity/transform/score/diagnostic/self-seal steps PASS.
- Arm commit `db02cdac39bf24bbdc020f4c5e61b0cb86b75ad4`.
- Terminal commit `9883daaa9770123aeab2a122fa72fa2fc6c16c4c`, message `research: freeze V167 calibration iteration 002 audio-evidence timing rules [skip ci]`.
- Candidate `debug/v167-single-song-calibration/iteration-002-generated.json`, blob `7eba73700116ceeca580a8851abe399aed764834`, SHA256 `96fbc329d9ba46b06d430c7c3c7b7f5b0e9077f6e133da5c3165c1fde609b5cc`.
- Score blob `5e01636b8ebe4753ee78a5126bfa321697139932`, SHA256 `f4ac083d43d3f8ecf507fca1631b6a6bcafbf403045a4efa1708ce4e3e856772`.
- Diagnostic blob `763b7f6450e02ea66406c5baba1372cde366cd41`, SHA256 `792cedf9ef62caea30a89f1c520745876e15ef28f015aabe53975b95acef2fae`.
- Receipt blob `c80a4e2a78309e359eaee67f745111c80e70d270`.

### Iteration 002 exact score
**Guitar**
- Primary F1 **41.9156774457634%** — 512 matched / 1050 generated / 1393 reference.
- Precision 48.76190476190476%; recall 36.755204594400576%.
- Gross ±2-step F1 **55.09619320507573%**, 673 matches.
- Same-measure pitch-content F1 **59.35325419566108%**, 725 matches.
- 160 gross-only same-pitch timing matches remain, but recall/pitch is the dominant limitation.
- Residual primary FN 881, FP 538; 491 FN have no generated event within ±0.5 step same measure.

**Bass**
- Primary F1 **71.86512118018967%** — 341 / 402 / 547.
- Precision 84.82587064676617%; recall 62.3400365630713%.
- Gross ±2-step F1 **74.39409905163331%**, 353 matches.
- Same-measure pitch-content F1 **75.0263435194942%**, 356 matches.
- Only 10 gross-only same-pitch timing matches remain.
- Residual primary FN 206, FP 61; 165 FN have no generated event within ±0.5 step same measure.
- Low-register recall remains obvious: generated MIDI 31 count 10 vs reference 73; generated MIDI 35 count 26 vs reference 70.

### Iteration 002 safety/provenance
- Guitar rule moved 266 events; Bass rule moved 15.
- No MIDI changes; no scored event cardinality changes.
- Transform did not read professional reference.
- Reference selected only the frozen whole-stream rule, never an individual event alternative.
- Direct reference copy=false; human correction=false; GPU/CUDA/Modal=false; main/Production=false.

## Prior negative/weak diagnostics retained
- 8-measure shared timing sweep: no nonzero block shift.
- Generated-only repeat completion: no Bass improvement and only weak Guitar gain with excessive additions; not promoted.
- Candidate evidence probe: no large rejected-event pool preserved in frozen candidate, but rich admitted-event audio evidence exists.

## NEXT boundary — recall/pitch near-miss instrumentation
1. Inspect the frozen V166/V165/V162 CPU front-end source and stream metadata to locate exact Guitar and Bass admission/recovery gates and determine where rejected event objects are discarded.
2. Create a V167 calibration-only instrumented CPU front-end that preserves near-miss/rejected candidate objects and reason codes without changing the existing detection behavior on its first instrumentation run.
3. First instrumentation run should reproduce the underlying V166 front-end musical output before V167 timing transforms while emitting machine-readable near-miss pools; then apply the already-frozen V167 `-12` and Iteration 002 timing rules for apples-to-apples scoring.
4. Use the reference only after near-miss generation to grade fixed threshold/recovery variants. Never copy reference events into the pool or candidate.
5. Prioritize Bass low-register recovery and Guitar missing polyphony/chord tones. Promote a new iteration only when a frozen parameter sweep shows a material precision/recall/F1 gain.
