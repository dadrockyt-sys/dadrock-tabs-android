# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-29 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V166 is terminal and permanently closed with an authoritative CPU candidate and structural-QC PASS. The next phase is V167 SINGLE-SONG CALIBRATION: explicitly scorer/reference-guided work on this one fixed song, with the goal of driving the calibration score as close to 100% as practical. V167 calibration results must never be represented as holdout/generalization performance. `main`/Production remain untouched.**

## V166 terminal anchors
- Sole generation run `33226705813`, run `1`, attempt `1`, job `99031747626`; SUCCESS.
- Arm/head `1e06d775ee03ebf92fe8f68fc02cf034812ea43f`.
- Terminal commit `7f5f5f19f6ec413fc772a9839be5497ecb2790e3`, message `research: freeze sole V166 paired-window CPU candidate [skip ci]`.
- Outcome `STRUCTURAL_QC_PASS`; `candidateAuthoritative=true`; `neverRearmV166=true`.
- Candidate path `debug/v166-cpu-autonomous/generated.json`.
- Candidate blob `c36a4d1e14ca66235b51a866ad3908322834efff`.
- Candidate SHA256 `fa2411598b401f745eff49a9cbda294ed767de093c905909531c7dd4dc6eb378`.
- Counts: Guitar `1050`; Bass `402`.
- Evidence-step corrections: Guitar `18`; Bass `6`; pre-grid excluded `0` both.
- Timebase blob `abebae25801b7ddeb5b933977c4f4a918f7bf9ef`; SHA256 `899746d3048d239bc0032375d412a109ea04b055df19df1b7b08dc3e73aa5ca0`.
- Timebase-QC blob `7c371d3ef3e6aa0b786671cffa023aed675a02b7`; SHA256 `3d239c073f5d11ee4b89e08eddf50d5fa082ec1cf3e16fb617f865dc9c0433a5`.
- Generation receipt blob `14206b972bf9fbe2979a1bc19419ceca2822ebf2`; SHA256 `be330b09f67689646fe071090c59b5695fd8de7afe18ac4aa275f4877e1695c5`.
- Structural-QC blob `97b8072a24321a435356694b9d1d3e6bbad998e5`; SHA256 `52e2382cabf6a0e1bdb3e81fb00074b4da566b5670d320215071c2b4fa30d80d`.
- Generation workflow blob `6198db63c574cf922a56fd30fb829404dffc7173`; workflow self-deleted during terminalization.
- V166 generation safety: no professional reference/scorer read, no V165 candidate/score read, no threshold sweep/variant selection/human correction, no GPU/CUDA/Modal, no main/Production modification.

## V166 paired-window implementation
- Contract blob `9ab505ee8c7de732b6e9a8928854ae99d3ebb0c7`.
- Guitar template offsets exactly `[-1,0,1,2,3,4]`; six frames.
- V166 finalized implementation identities remain frozen as recorded in the previous checkpoint and pre-run receipt.

## Closed generations
- V159–V166 are closed forever. Never rerun/rearm/repair/retune/regenerate/re-QC a closed version.
- V163 and V165 score opportunities remain closed forever.
- V166 generation is closed forever. Do not mutate its candidate.

## V167 SINGLE-SONG CALIBRATION — authorization and scientific label
The user explicitly authorized taking this one song as far toward `100%` as possible. V167 therefore changes methodology on purpose:
- This is a **training/calibration lane**, not a blind experiment and not a holdout score.
- The frozen professional reference and frozen scorer may be read and used diagnostically.
- Event-level, timing-level, pitch/register, false-positive, false-negative, chord/polyphony, duration, and structural error analysis is allowed for this one song.
- Score-informed iteration, threshold/parameter experiments, variant comparison, and algorithmic repair are allowed inside V167 calibration.
- Every iteration must preserve provenance: exact parent candidate/code/config, exact scorer/reference identity, exact score, and the change tested.
- No manual copying of the professional reference into the generated output. Improvements must come through deterministic algorithm/code/parameter behavior so the exercise remains useful engineering rather than answer-key substitution.
- Any `100%` reached here means **100% on the calibration song under the chosen scorer**, not 100% general transcription accuracy.
- A later untouched multi-song holdout benchmark will be required to measure generalization.

## Calibration score presentation
Use scorer F1 × 100 as the immediate pitch/timing recognition percentage for Guitar and Bass. Also build a broader `Professional Tab Score /100` separately so PDF/tab quality is not confused with front-end note F1.

## V167 next boundary
1. Freeze a V167 calibration manifest before the first score-guided mutation. Pin V166 candidate, frozen scorer, frozen professional reference, song source, branch, and calibration-only label.
2. Run a read-only baseline diagnostic of the frozen V166 candidate against the frozen scorer/reference. This is the starting calibration score, not a V166 score claim.
3. Produce machine-readable error buckets for Guitar and Bass: matched, missed, extra, pitch-class/octave/register error, onset/timing displacement, duration mismatch, duplicate/fragmented events, chord/polyphony under/over detection where inferable.
4. Rank the largest error classes by achievable score impact.
5. Implement one deterministic calibration change at a time, rerun CPU-only as needed, score, log delta, retain the best calibration candidate, and continue toward 100%.
6. Do not use GPU/Modal/CUDA without fresh explicit authorization immediately before execution.
7. Never modify/merge/promote `main` or Production without explicit user direction.
