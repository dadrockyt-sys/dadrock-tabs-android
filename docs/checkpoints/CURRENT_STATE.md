# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is the explicitly reference/scorer-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Iteration 001 remains the best frozen candidate at Guitar 40.36% / Bass 70.60% after the shared `-12` timing-origin correction. Broad local timing and generated-only repeat completion have now both been tested and rejected as next-step promotions. Focus moves to probing stored audio-derived evidence for deterministic recall/polyphony/low-register recovery. `main`/Production remain untouched.**

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

## V167 Iteration 001 — CURRENT BEST / FROZEN
- Transform blob `9b13b65a2b4c9fd6a801afe50a0ecc153de56b3c`.
- Run `33227463521`, job `99033850831`; terminal commit `dcb61f0eeeedd1d1ea69cec257d374f7b83a084b`.
- Candidate blob `1b73d6ece977fb976fa1c503997e6434d4e4811a`, SHA256 `cfe521efac40b28b3fd34268cd24d7cdc24d92926fc33815f0928942edb56911`.
- Guitar **40.36021285304953%** — 493 matched / 1050 generated / 1393 reference; gross 54.93246009005321%; pitch-content 59.43512075317232%.
- Bass **70.60063224446786%** — 335 / 402 / 547; gross 74.81559536354058%; pitch-content 75.23709167544784%.
- No MIDI or scored-cardinality change; no direct reference copy; no GPU/main changes.

## V167 fixed 8-measure shared phase sweep — FROZEN NEGATIVE RESULT
- Code blob `80e2d888c725bd739dbfc868186df56aff7cb3fc`.
- Run `33227532512`, job `99034037783`; terminal commit `2d6930a058bfd5a6ed3c622378270e14c43f87f3`.
- Report blob `415be9b6670a0b03ad593ae008b3353d59c26c05`.
- All fixed 8-measure blocks selected additional shift `0`; no broad section timing transform justified.

## V167 self-repeat completion sweep — FROZEN WEAK/NEGATIVE RESULT
- Code `validation/v167_single_song_calibration/repeat_completion_sweep_v167.py`, blob `cbd3e5535de78ddd07675ae279a85386bdf29174`.
- One-shot run `33227633093`, run 1, attempt 1, job `99034323903`; SUCCESS.
- Arm commit `d39fb487a2098b415b9f5e77996868c880ea7ed0`.
- Terminal commit `a379a3a1c329326f2311a7db3812dcc7f048a2e6`, message `research: freeze V167 self-repeat completion sweep [skip ci]`.
- Report `debug/v167-single-song-calibration/repeat-completion-sweep.json`, blob `3a71ad10fd74805d86803f5e86c5332c54acf0ef`.
- Fixed generated-only donor grid: thresholds `[0.50,0.67,0.75,0.80,0.90,1.00]`; max additions `[1,2,4,8]`; minimum target events `[1,2,3]`; no recursive propagation.
- Bass: **no variant beat the Iteration 001 baseline**. Best selection is baseline unchanged at **70.60063224446786%**.
- Guitar: best variant reached only **40.98240469208211%**, a gain of **+0.622191839032582 percentage points**, but required 285 added notes across 60 measures; matched increased 493→559 while generated increased 1050→1335 and precision fell 46.95%→41.87%.
- This tradeoff is not strong enough to promote as Iteration 002. No repeat-completion candidate was created.
- All repeat additions came only from generated donor measures; reference supplied no events.

## Residual priorities
1. Keep Iteration 001 as best candidate. Do not promote weak repeat completion merely because it moves F1 slightly.
2. Timing is globally corrected and broad section timing is exhausted for now.
3. Bass remains mainly recall/low-register limited: 212 false negatives vs 67 false positives; low MIDI 31/35 strongly under-represented.
4. Guitar remains recall/polyphony/pitch limited: 900 false negatives and 557 false positives.
5. The next high-value route is to inspect what rejected/candidate/source-evidence fields are already stored in Iteration 001/V166 artifacts so we can recover events from real audio-derived evidence rather than synthetic repetition.

## NEXT boundary
1. Run a **candidate evidence-schema probe** against immutable Iteration 001, with no professional-reference read required. Report top-level paths, list sizes, event/object field frequencies, and numeric evidence/rank/confidence fields that could support deterministic recovery.
2. Identify whether the payload preserves rejected candidates, pre-grid candidates, Basic Pitch confidence, CQT/template ranks, onset evidence, stream-local source events, or other audio-derived near-miss pools.
3. If useful evidence exists, build a reference-facing but candidate-read-only threshold/ranking sweep over those existing source candidates. Reference may grade variants but must not supply events.
4. Target Bass low-register recall first if the evidence pool supports it; target Guitar polyphony/near-miss recovery in parallel or immediately after.
5. Do not create Iteration 002 until a frozen sweep shows a material improvement with a defensible precision/recall tradeoff.
