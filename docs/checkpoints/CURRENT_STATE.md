# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly reference/scorer-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 001 is frozen at Guitar 40.36% / Bass 70.60% after the shared `-12` timing-origin correction. A fixed shared 8-measure local phase sweep found no further coherent section timing correction: every block selected 0. Timing is therefore frozen for the next iteration; focus moves to deterministic recall/polyphony/pitch recovery. `main`/Production remain untouched.**

## Standing V167 methodology
- Calibration only, not holdout/generalization performance.
- Frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`; frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`.
- Score/reference-guided diagnostics and parameter experiments are allowed.
- Direct/manual copying of professional-reference events into generated output is forbidden.
- Improvements must come from deterministic algorithm/code/parameter behavior.
- CPU work authorized; fresh explicit authorization required immediately before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit direction.

## Closed V166 anchor
- Terminal commit `7f5f5f19f6ec413fc772a9839be5497ecb2790e3`; candidate blob `c36a4d1e14ca66235b51a866ad3908322834efff`; Guitar 1050, Bass 402; structural QC PASS.
- V159–V166 generations closed forever.

## V167 baseline
- Terminal baseline commit `0930a2a50d4f736237312114189c526bbf43c100`.
- Guitar 6.058125255832993%; Bass 21.707060063224446%.

## V167 global phase discovery
- Frozen phase report blob `6def13224adf3d2dcdc505e7d804a2dd104f0a86`.
- Both instruments independently selected exactly `-12` grid steps.

## V167 Iteration 001 — FROZEN
- Transform blob `9b13b65a2b4c9fd6a801afe50a0ecc153de56b3c`.
- Run `33227463521`, job `99033850831`; terminal commit `dcb61f0eeeedd1d1ea69cec257d374f7b83a084b`.
- Candidate blob `1b73d6ece977fb976fa1c503997e6434d4e4811a`, SHA256 `cfe521efac40b28b3fd34268cd24d7cdc24d92926fc33815f0928942edb56911`.
- Guitar **40.36021285304953%** — 493 matched / 1050 generated / 1393 reference; gross 54.93246009005321%; pitch-content 59.43512075317232%.
- Bass **70.60063224446786%** — 335 / 402 / 547; gross 74.81559536354058%; pitch-content 75.23709167544784%.
- No MIDI or scored-cardinality change; no direct reference copy; no GPU/main changes.

## V167 fixed 8-measure shared phase sweep — FROZEN NEGATIVE RESULT
- Diagnostic code blob `80e2d888c725bd739dbfc868186df56aff7cb3fc`.
- One-shot run `33227532512`, run 1, attempt 1, job `99034037783`; SUCCESS.
- Arm commit `7ea7632289575571bdf8b1d9532cccfee4ccb890`.
- Terminal commit `2d6930a058bfd5a6ed3c622378270e14c43f87f3`, message `research: freeze V167 shared 8-measure block phase sweep [skip ci]`.
- Report `debug/v167-single-song-calibration/block-phase-sweep-8m.json`, blob `415be9b6670a0b03ad593ae008b3353d59c26c05`.
- Fixed blocks: 8 measures; tested additional shared shifts -3..+3; objective maximized joint primary Guitar+Bass matches.
- **Selected nonzero blocks: none. Every block chose shift 0.**
- Projected combined map therefore equals Iteration 001; no Iteration 002 timing transform is justified from this sweep.

## Residual priorities
1. Freeze global timing at the Iteration 001 correction; do not keep sweeping timebase simply to chase score.
2. Guitar: 900 false negatives and 557 false positives; 177 gross-only same-pitch timing opportunities remain, but broad section timing shifts do not help. Main target is recall/polyphony/pitch recognition.
3. Bass: 212 false negatives vs only 67 false positives; dominant MIDI 40/38 counts are close to reference, while low notes such as MIDI 31/35 are strongly under-represented. Main target is recall/low-register detection, not additional timing shifts.
4. Test repeat-aware musical completion next because this rock arrangement contains repeated riffs and the algorithm can learn missing events from its own stronger detections in other measures without copying the professional reference.

## NEXT boundary
1. Build a read-only **self-repeat completion parameter sweep** from immutable Iteration 001. Donor events must come only from other generated measures, never from the professional reference.
2. Use fixed, predeclared similarity thresholds and addition caps. Donor matching must use only generated measure patterns; reference is used only to score variants.
3. No recursive propagation: every trial derives from the same frozen Iteration 001 source.
4. Select Guitar and Bass parameters separately if justified, freeze the whole sweep and projected score before applying a new candidate.
5. If repeat completion materially improves F1, implement provenance-marked Iteration 002. If not, move to source-evidence/threshold diagnostics for missed low Bass notes and Guitar polyphony.
