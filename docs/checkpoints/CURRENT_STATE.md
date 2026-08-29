# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal/immutable. V167 is an explicitly reference/scorer-guided SINGLE-SONG TRAINING CALIBRATION lane for Lenny Kravitz — Are You Gonna Go My Way. Baseline and the first global timing-phase sweep are frozen. Both Guitar and Bass independently select the exact same global shift: `-12` absolute grid steps, producing a very large score increase without changing any pitch. Next boundary: create the first provenance-tracked V167 calibrated candidate by applying this deterministic shared timing-origin correction, score/diagnose it, then attack residual local timing and recall/pitch errors. `main`/Production remain untouched.**

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
- One-shot baseline run `33227202895`, run 1, attempt 1, job `99033120458`; SUCCESS.
- Terminal baseline commit `0930a2a50d4f736237312114189c526bbf43c100`.
- Recognition F1 × 100: Guitar **6.058125255832993%** (74/1050/1393), Bass **21.707060063224446%** (103/402/547).
- Gross ±2-step F1: Guitar **20.139173147769135%** (246 matches), Bass **36.248682824025286%** (172 matches).
- Same-measure pitch-content F1 ignoring exact step: Guitar **48.95620139173148%** (598 matches), Bass **52.05479452054794%** (247 matches).

## V167 absolute-grid phase sweep — BREAKTHROUGH / FROZEN
- Sweep code `validation/v167_single_song_calibration/grid_phase_sweep_v167.py`, blob `68e247ea780c46a8e5bf9f1a7a86e8c3b3eccce9`.
- One-shot sweep run `33227314958`, run 1, attempt 1, job `99033433099`; SUCCESS.
- Arm commit `bd9146e0926bda6ab82ecd1eafb67ff55b9b7f6b`.
- Terminal sweep commit `e0f59a92a82f95f9c1606305476118e1dd50c07b`, message `research: freeze V167 absolute-grid phase sweep [skip ci]`.
- Frozen report `debug/v167-single-song-calibration/grid-phase-sweep.json`, blob `6def13224adf3d2dcdc505e7d804a2dd104f0a86`.
- Sweep covered integer absolute-grid shifts `[-16,+16]`, read-only, preserving MIDI and event cardinality.

### Shared optimum: `-12` grid steps
**Guitar**
- Baseline primary F1: `0.060581252558329926` = **6.0581%**, 74 matches.
- Best at `-12`: primary F1 `0.4036021285304953` = **40.3602%**, 493 matches.
- Gain: **+34.3021 percentage points**, +419 primary matches.
- At `-12`, precision `0.4695238095238095`, recall `0.3539124192390524`.
- Gross F1 at `-12`: `0.5493246009005321`, 671 matches.

**Bass**
- Baseline primary F1: `0.21707060063224448` = **21.7071%**, 103 matches.
- Best at `-12`: primary F1 `0.7060063224446786` = **70.6006%**, 335 matches.
- Gain: **+48.8936 percentage points**, +232 primary matches.
- At `-12`, precision `0.8333333333333334`, recall `0.6124314442413162`.
- Gross F1 at `-12`: `0.7481559536354058`, 355 matches.

## Interpretation / priority
1. **Confirmed shared global timebase-origin/phase error.** Guitar and Bass independently choose exactly `-12`, which strongly supports a common timing-origin correction rather than instrument-specific overfitting.
2. The first V167 calibrated candidate should apply one shared deterministic `-12` absolute-grid-step correction to generated musical coordinates, with MIDI/event identity otherwise unchanged.
3. After the corrected candidate is frozen and rescored, residual Guitar error is expected to be dominated by recall/polyphony/pitch content plus local timing; Bass is already entering useful-draft territory from timing correction alone.
4. Do not mistake calibration score for generalization.

## NEXT boundary
1. Build a versioned deterministic V167 transform from immutable V166: subtract exactly 12 from each event `absoluteGridStep`, recompute `measure/step` from the 16-step-per-measure lattice, preserve MIDI/source evidence/event ordering, and reject any invalid negative-grid event rather than silently corrupting it.
2. Emit provenance recording V166 candidate blob, phase-sweep report blob, transform code blob, exact shift `-12`, before/after counts, and zero direct reference-event copying.
3. Score and run the same detailed V167 diagnostic on the transformed candidate using the frozen scorer/reference.
4. Freeze the candidate/score/diagnostic as calibration iteration 1.
5. Then use residual errors to decide between local/section timing warp and recall/pitch improvements.
6. No GPU/CUDA/Modal without fresh explicit authorization. Never touch `main`/Production without explicit direction.
