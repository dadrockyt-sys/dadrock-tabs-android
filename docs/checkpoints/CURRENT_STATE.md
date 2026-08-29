# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly reference/scorer-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Calibration Iteration 002 is frozen and is the current best candidate: Guitar 41.92%, Bass 71.87%. Timing calibration is now largely exhausted. The exact V166/V164/V162 CPU discard gates have been mapped, and the sealed source audio can be reproduced CPU-only from historical Git commit `74b0f815ff3f66f325220975c410621503de440f`. Next action is an output-neutral, reference-blind instrumentation layer that records the real near-miss/rejected pools while reproducing the frozen V166 musical output. `main`/Production remain untouched.**

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

## V167 recall/pitch source audit — DISCARD GATES MAPPED
### Exact frozen implementation chain
- V166 event wrapper `validation/v166_cpu_autonomous/event_logic_v166.py`, blob `6561194742093d76bab452ef0bbb0b889724dc4e`, mechanically inherits V165/V164 event behavior.
- V166 transcriber `validation/v166_cpu_autonomous/transcribe_v166.py`, blob `f04ca86525b2ce71680a90b84ed476943e9e6426`; sole V166 musical change is the paired six-frame Guitar template offsets `[-1,0,1,2,3,4]`.
- Actual admission/grid implementation descends from V162 transcriber blob `fa163cafe2131aa73cdbb50df10d4e4912cff53b`, with V164 local-evidence adapter blob `df1302216df404bc3368ff820f005d6b63ae100d` and V164 event logic blob `62303877a1971f75cacda002c5ad921680161674`.

### Reproducible CPU source boundary
- Historical V166 workflow materializes `public/gomywayfullaitest.m4a` from Git commit `74b0f815ff3f66f325220975c410621503de440f`.
- Exact source identity: 3,478,611 bytes; SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Original run normalized with bundled ffmpeg and used deterministic `demucs==4.1.0`, model `htdemucs_6s`, device `cpu`, shifts=1, jobs=1; Python 3.10.21 / torch 2.8.0+cpu.
- Therefore the instrumentation run can reproduce source/stems CPU-only without external upload and without GPU/CUDA/Modal.

### Guitar discard points to instrument
1. **Raw Basic Pitch → segmentation**: Basic Pitch uses onset threshold 0.50, frame threshold 0.30, minimum note length 90ms, MIDI 40–88. Same-MIDI rows with gap <=0.120s are merged when local reattack evidence is unsupported; child rows are not retained as standalone candidates.
2. **Segmented admission**: each segmented row computes paired-window template/register evidence, onset/activity/persistence/confidence, then rejects activity `<0.05` and admission score `<0.50`. Admission score = `0.45*confidence + 0.25*rank + 0.15*onset + 0.10*persistence + 0.05*activity`.
3. **Active-state reattack recovery**: candidate onset must have support >=0.35, not be within 0.050s of an existing attack, parent confidence >=0.35, pitch evidence present, template rank >=0.80, fundamental present, recovery score >=0.58; per-onset candidates are capped at 3. Failed candidates are currently discarded by `continue` branches.
4. **Grid mapping/dedupe**: events before the first-grid half-window are dropped; identical `(absoluteGridStep,midi)` collisions retain only the stronger evidence/confidence event.
5. **Guitar polyphony cap**: after mapping, each grid step is capped at 6 by admission/recovery score then confidence, discarding lower-ranked simultaneous pitches.

### Bass discard points to instrument
1. **Stable pitch-state construction**: pYIN states require frame voiced probability >=0.50, minimum run 4 frames, median voiced probability >=0.55; only gaps <=2 frames between identical states are bridged. Short/weak states disappear before proposals.
2. **Onset/state proposal construction**: detected onsets with no nearby state are discarded; onset support `<0.20` is discarded. Same-pitch reattacks require IOI >=0.080s and local peak/threshold plus support >=0.30.
3. **Proposal merge**: proposals within 0.045s are grouped; only one winner survives, ordered by proposal priority, onset support, state voiced probability, then frame. Nonwinning proposal dictionaries are discarded.
4. **Bass admission**: for each merged proposal, pitch is chosen from harmonic template + pYIN proximity. Reject activity `<0.04`; reject unless fundamental is present or median pYIN voiced probability >=0.60; reject admission score `<0.42`. Bass admission score = `0.40*voiced + 0.35*rank + 0.15*onset + 0.10*activity`.
5. **Grid mapping/dedupe**: pre-grid events are dropped; same `(absoluteGridStep,midi)` collisions retain only stronger evidence.
6. **Bass grid cap**: final grid is capped at one Bass note per step by admission score, voiced probability, then MIDI; lower-ranked simultaneous candidates are discarded.

## NEXT boundary — output-neutral near-miss instrumentation
1. Implement a V167 calibration-only instrumentation layer over the exact pinned V166 behavior. The first run must not alter any admission/recovery/grid decisions.
2. Emit machine-readable pools with explicit decision/reason codes for: Guitar raw/segmentation merges, segmented rejects, recovery rejects/cap losers, grid dedupe/polyphony losers; Bass weak/short state candidates if practical, onset/reattack rejects, proposal merge losers, admission rejects, grid dedupe/cap losers.
3. Preserve enough existing audio evidence per rejected object to support later deterministic threshold/ranking sweeps; do not read the professional reference while constructing the pool.
4. Re-run the exact sealed source/stem pipeline CPU-only and assert the instrumented final V166 musical streams reproduce the frozen V166 candidate before freezing the evidence pool.
5. After the evidence pool is frozen, apply the already-frozen V167 `-12` and Iteration 002 timing transforms for apples-to-apples calibration scoring of any recovery variants.
6. Reference may then grade whole fixed threshold/ranking variants only. Prioritize Bass MIDI 31/35 low-register recovery and Guitar missing polyphony/chord tones.
7. Do not create Iteration 003 until a frozen recovery sweep demonstrates a material improvement with a defensible precision/recall tradeoff.
