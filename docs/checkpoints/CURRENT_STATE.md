# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly reference/scorer-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 001 is frozen at Guitar 40.36% / Bass 70.60%. A new fixed whole-stream audio-evidence timing-rule sweep is frozen and materially improves both instruments without changing MIDI or event cardinality: projected Guitar 41.92%, Bass 71.87%. Next boundary is deterministic Iteration 002 using the selected whole-stream rules, followed by score/diagnostic freeze. `main`/Production remain untouched.**

## Standing V167 methodology
- Calibration only, not holdout/generalization performance.
- Frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`; frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`.
- Reference/scorer may grade complete predeclared variants and select a whole deterministic rule; it may not choose an individual event answer.
- Direct/manual copying of professional-reference events into generated output is forbidden.
- CPU work authorized; fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit direction.

## Closed V166 anchor
- Terminal commit `7f5f5f19f6ec413fc772a9839be5497ecb2790e3`; candidate blob `c36a4d1e14ca66235b51a866ad3908322834efff`; Guitar 1050, Bass 402; structural QC PASS.
- V159–V166 generations closed forever.

## V167 Iteration 001 — FROZEN
- Terminal commit `dcb61f0eeeedd1d1ea69cec257d374f7b83a084b`.
- Candidate blob `1b73d6ece977fb976fa1c503997e6434d4e4811a`, SHA256 `cfe521efac40b28b3fd34268cd24d7cdc24d92926fc33815f0928942edb56911`.
- Guitar **40.36021285304953%** — 493 matched / 1050 generated / 1393 reference; gross 54.93246009005321%.
- Bass **70.60063224446786%** — 335 / 402 / 547; gross 74.81559536354058%.
- Shared global phase correction is `-12` grid steps.

## Previous frozen diagnostics
- Fixed 8-measure shared phase sweep: report blob `415be9b6670a0b03ad593ae008b3353d59c26c05`; all blocks chose 0 additional shift.
- Generated-only repeat completion: report blob `3a71ad10fd74805d86803f5e86c5332c54acf0ef`; no Bass gain and weak Guitar gain with excessive added notes; not promoted.
- Candidate evidence probe: run `33227694682`, terminal commit `0944ca72009e087c46cb02ab3d544a211d442b90`, report blob `b15fcdf72f39ce5342c7306f0fb78c1588c80f75`; every admitted event stores three audio-derived `stepSelection.candidates`.

## V167 fixed whole-stream step-rule sweep — FROZEN POSITIVE RESULT
- Code `validation/v167_single_song_calibration/step_rule_sweep_v167.py`, blob `14cac9e217f65f72933c72ee349523ca9681fc21`.
- One-shot run `33227803023`, run 1, attempt 1, job `99034806131`; SUCCESS.
- Arm commit `0f652c0be51750c7ba66314373c50ffb56c14aba`.
- Terminal commit `81593418a2f4e429e7eb5a8423de9f92037b0e3d`, message `research: freeze V167 fixed audio-evidence step-rule sweep [skip ci]`.
- Report `debug/v167-single-song-calibration/step-rule-sweep.json`, blob `2096d3caa58b6ce7d6ab57aeaa7512989e2e4acd`.
- All alternatives come from each event's existing 3 stored audio-derived lattice candidates. MIDI and event cardinality remain unchanged. Stored candidate absolute step receives the already-frozen `-12` global correction before measure/step conversion.
- Reference selected only complete whole-stream rules, never individual event alternatives.

### Guitar selected rule
- Rule: `max_score_x_shared`.
- Baseline primary F1 40.36021285304953% → projected **41.9156774457634%**; **+1.5554645927138677 pp**.
- Matches 493 → 512; precision 46.9524% → 48.7619%; recall 35.3912% → 36.7552%.
- Gross F1 54.93246009005321% → **55.09619320507573%**; gross matches 671 → 673.
- 266 / 1050 events move: 160 by -1, 105 by +1, 1 by -2; 784 unchanged. Mean absolute movement 0.2543 step.

### Bass selected rule
- Rule: `max_score_x_mean_support` where mean support = `(instrumentSupport + sharedSupport)/2`.
- Baseline primary F1 70.60063224446786% → projected **71.86512118018967%**; **+1.264488935721808 pp**.
- Matches 335 → 341; precision 83.3333% → 84.8259%; recall 61.2431% → 62.3400%.
- Gross F1 74.81559536354058% → 74.39409905163331%; gross matches 355 → 353. Primary scorer improves materially while gross changes slightly downward.
- Only 15 / 402 events move: 8 by -1, 7 by +1; 387 unchanged. Mean absolute movement 0.0373 step.

## Promotion decision
- Promote the two selected deterministic rules as V167 Calibration Iteration 002 because both improve the frozen primary scorer with no pitch/cardinality changes and use only stored audio evidence.
- Iteration 002 transform itself must not read the professional reference. It may read the frozen sweep report as the sealed calibration parameter source.
- Preserve Iteration 001 as immutable parent and record exact per-stream rules, movement counts, sweep/code blobs, and zero direct-reference copying.

## NEXT boundary
1. Implement deterministic Iteration 002 transform from immutable Iteration 001: Guitar `max_score_x_shared`, Bass `max_score_x_mean_support`.
2. For each selected stored lattice candidate, apply `storedStep - 12`; update final `absoluteGridStep`, `measure`, and `step`. Preserve MIDI and scored event count exactly.
3. Preserve original nested audio evidence; add explicit calibration provenance rather than rewriting source evidence silently.
4. Score and run the standard detailed V167 diagnostic; freeze candidate, score, diagnostic, receipt, and workflow self-seal.
5. After Iteration 002, move to recall/pitch recovery. Because the frozen candidate lacks rejected-event dictionaries, the likely next high-value step is a new CPU-only instrumented front-end calibration run that captures near-miss/rejected pools for Bass low-register and Guitar polyphony.
