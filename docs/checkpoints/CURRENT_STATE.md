# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is an explicitly reference/scorer-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Baseline is now frozen. The dominant first engineering target is grid/timing placement, because measure-level pitch content is far stronger than exact-timing F1. `main`/Production remain untouched.**

## Closed V166 terminal
- Sole generation run `33226705813`, run 1, attempt 1, job `99031747626`; SUCCESS.
- Terminal commit `7f5f5f19f6ec413fc772a9839be5497ecb2790e3`; structural QC PASS.
- Immutable candidate `debug/v166-cpu-autonomous/generated.json` blob `c36a4d1e14ca66235b51a866ad3908322834efff`, SHA256 `fa2411598b401f745eff49a9cbda294ed767de093c905909531c7dd4dc6eb378`.
- Guitar 1050; Bass 402. `neverRearmV166=true`.
- V159–V166 generations are closed forever; do not rerun/rearm/mutate them.

## V167 calibration contract
- Manifest `debug/v167-single-song-calibration/calibration-manifest.json`, blob `8d6e9723e77e9ec2159e765436db2e9d91982fb2`.
- Label: `SINGLE_SONG_TRAINING_CALIBRATION` — not holdout/generalization performance.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`, blob `9644e65719fbd361a9b39778ae9950c5e983e855`; primary tolerance 0.5 grid step, gross tolerance 2.0.
- Frozen professional reference blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`, SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; Guitar 1393, Bass 547.
- Score/reference-guided diagnostics, parameter experiments, variant comparison, and deterministic algorithmic repair are allowed in V167.
- Direct/manual copying of reference events into generated output remains forbidden.
- Any 100% reached here means 100% on this calibration song under the frozen scorer only; later untouched multi-song holdout remains required.
- CPU work authorized. Fresh explicit authorization required immediately before GPU/CUDA/Modal. Never modify `main`/Production without explicit direction.

## V167 frozen baseline — SUCCESS
- One-shot baseline run `33227202895`, run 1, attempt 1, job `99033120458`; all steps SUCCESS and workflow self-sealed.
- Baseline terminal commit `0930a2a50d4f736237312114189c526bbf43c100`, message `research: freeze V167 calibration baseline diagnostic [skip ci]`.
- Baseline receipt status `BASELINE_FROZEN`.
- Recognition F1 × 100:
  - Combined Guitar: **6.058125255832993%** (74 matched / 1050 generated / 1393 reference).
  - Bass: **21.707060063224446%** (103 matched / 402 generated / 547 reference).
- Gross ±2-step same-pitch timing F1:
  - Guitar: **20.139173147769135%**, 246 matches; 172 are gross-only timing-drift matches.
  - Bass: **36.248682824025286%**, 172 matches; 69 are gross-only timing-drift matches.
- Same-measure pitch-content F1 ignoring exact step:
  - Guitar: **48.95620139173148%**, 598 matched pitches.
  - Bass: **52.05479452054794%**, 247 matched pitches.
- This gap is the first major signal: substantial correct pitch content is already landing in the correct measure but on incorrect grid positions.

## Baseline error buckets
Guitar unmatched reference events: 710 no generated event within ±0.5 step in same measure; 421 other pitch errors near correct time; 96 near-semitone; 85 octave/register; 7 local collision/duplicate. Guitar unmatched generated: 504 no nearby reference event; 318 other pitch error; 82 near-semitone; 72 octave/register.

Bass unmatched reference events: 255 no generated event within ±0.5 step same measure; 104 other pitch error near correct time; 82 near-semitone; 3 octave/register. Bass unmatched generated: 111 no nearby reference; 104 other pitch; 81 near-semitone; 3 octave/register.

## Interpretation / priority
1. **Timing/grid phase first.** Exact-timing F1 is dramatically below same-measure pitch-content F1 for both instruments.
2. Guitar also has a major recall/polyphony problem: 1393 reference vs 1050 generated and many no-nearby-event misses.
3. Bass pitch distribution shows likely under-detection of lower notes (notably reference MIDI 31 and 35 frequencies substantially exceed generated), but timing should be corrected/tested before altering pitch thresholds.
4. Octave/register errors exist but are not the dominant count, so do not spend the next iteration primarily on octave repair.

## NEXT boundary
- Run a read-only deterministic **absolute-grid phase sweep** on the frozen V166 candidate, separately for Guitar and Bass, using integer shifts around the current lattice (no candidate mutation). Recompute `absoluteGridStep -> measure/step` for each tested shift and score with the frozen scorer.
- Record the full score curve and best shift for each stream. This is a calibration diagnostic/parameter experiment, not a generalization claim.
- If a stable phase shift yields a material gain, implement it as the first V167 deterministic timing calibration rule and produce a new provenance-tracked calibration candidate; otherwise proceed to per-section/timebase-warp diagnostics rather than blindly changing pitch logic.
