# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is an explicitly reference/scorer-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Calibration Iteration 001 is frozen: a single shared `-12` absolute-grid-step timing-origin correction raised Guitar from 6.06% to 40.36% and Bass from 21.71% to 70.60% without changing MIDI or scored event cardinality. Next: diagnose shared section-level timing drift with fixed 8-measure blocks before touching pitch/recall logic. `main`/Production remain untouched.**

## Closed V166 terminal
- Sole generation run `33226705813`, run 1, attempt 1, job `99031747626`; SUCCESS.
- Terminal commit `7f5f5f19f6ec413fc772a9839be5497ecb2790e3`; structural QC PASS.
- Immutable V166 candidate blob `c36a4d1e14ca66235b51a866ad3908322834efff`, SHA256 `fa2411598b401f745eff49a9cbda294ed767de093c905909531c7dd4dc6eb378`; Guitar 1050, Bass 402.
- V159–V166 generations are closed forever; never rerun/rearm/mutate them.

## V167 calibration contract
- Manifest blob `8d6e9723e77e9ec2159e765436db2e9d91982fb2`.
- Label `SINGLE_SONG_TRAINING_CALIBRATION`; calibration score is not holdout/generalization performance.
- Frozen scorer blob `9644e65719fbd361a9b39778ae9950c5e983e855`; primary tolerance 0.5 grid step, gross tolerance 2.0.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; Guitar 1393, Bass 547.
- Reference/scorer-guided diagnostics, parameter experiments and deterministic algorithmic repair are allowed in V167.
- Direct/manual copying of professional-reference events into generated output remains forbidden.
- CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal. Never modify `main`/Production without explicit direction.

## Frozen V167 baseline
- Baseline run `33227202895`, job `99033120458`; terminal commit `0930a2a50d4f736237312114189c526bbf43c100`.
- Guitar 6.058125255832993%; Bass 21.707060063224446%.
- Same-measure pitch-content F1: Guitar 48.9562%; Bass 52.0548%, exposing major timing misalignment.

## Frozen global phase sweep
- Sweep report blob `6def13224adf3d2dcdc505e7d804a2dd104f0a86`; terminal commit `e0f59a92a82f95f9c1606305476118e1dd50c07b`.
- Both Guitar and Bass independently selected exactly `-12` absolute grid steps.
- Predicted at `-12`: Guitar 40.36021285304953%; Bass 70.60063224446786%.

## V167 Calibration Iteration 001 — FROZEN SUCCESS
- Transform `validation/v167_single_song_calibration/apply_global_phase_v167.py`, blob `9b13b65a2b4c9fd6a801afe50a0ecc153de56b3c`.
- One-shot iteration run `33227463521`, run 1, attempt 1, job `99033850831`; transform/score/diagnostic/self-seal all PASS.
- Arm commit `16831e9d389572d3c39ce6f45cc77e5906cc4c55`.
- Terminal commit `dcb61f0eeeedd1d1ea69cec257d374f7b83a084b`, message `research: freeze V167 calibration iteration 001 global phase [skip ci]`.
- Candidate `debug/v167-single-song-calibration/iteration-001-generated.json`: blob `1b73d6ece977fb976fa1c503997e6434d4e4811a`; SHA256 `cfe521efac40b28b3fd34268cd24d7cdc24d92926fc33815f0928942edb56911`.
- Score blob `6b8d4c09c167f976721c0f60913639cda35ada64`; diagnostic blob `68ee76d97aae5ebeb063ab67ce2e280b76c444c7`; receipt blob `28baca94c6853df80a72cde4a1b333a1518e9d92`.
- Exact recognition F1 ×100:
  - Guitar **40.36021285304953%** — 493 matched, precision 46.9524%, recall 35.3912%.
  - Bass **70.60063224446786%** — 335 matched, precision 83.3333%, recall 61.2431%.
- Gross ±2-step F1 after correction: Guitar **54.93246009005321%** (671 matched); Bass **74.81559536354058%** (355 matched).
- Same-measure pitch-content F1 after correction: Guitar **59.43512075317232%** (726 matched); Bass **75.23709167544784%** (357 matched).
- Transform changed no MIDI and no scored stream cardinality; direct reference copy=false; human correction=false; GPU/CUDA/Modal=false; main/Production=false.

## Residual error interpretation after Iteration 001
- Guitar has **177 gross-only same-pitch timing-drift matches** still within ±2 steps but outside the primary timing position. This is the next clean timing opportunity.
- Bass has only **19** gross-only timing-drift matches; Bass is now mainly recall-limited: 212 false negatives vs 67 false positives.
- Guitar remains strongly recall/pitch-limited too: 900 false negatives vs 557 false positives, with 478 misses having no generated event within ±0.5 step in the same measure.
- Octave/register is not the dominant residual: Guitar 79 FN / 53 FP bucket; Bass 2 / 2.
- Therefore do not lead Iteration 002 with octave repair.

## NEXT boundary
1. Run a reference-facing but candidate-read-only **shared 8-measure block phase sweep** starting from immutable Iteration 001. Fixed blocks; for each block test only small additional integer shifts (recommended -3..+3). Use one shared shift per block for both Guitar and Bass to preserve a common timebase.
2. Optimize a predeclared joint objective based on total primary matched events across both streams, tie-breaking toward smaller absolute shift and then zero/earlier deterministic order.
3. Freeze the complete block-by-block score map before applying any local correction.
4. If the map shows coherent non-zero section offsets and meaningful projected gain, create Iteration 002 by applying only that fixed piecewise timing map; otherwise leave timing frozen and move to recall/pitch detection.
5. Keep every transform deterministic and provenance-tracked; no event-by-event reference copying.
6. No GPU/CUDA/Modal without fresh explicit authorization. Never touch `main`/Production without explicit direction.
