# PRE — Songsterr Fresh V7 Reattack Temporal/Support Diagnostic V1

Status: **PROSPECTIVE / SYNTHETIC-ONLY / DIAGNOSTIC-ONLY / FROZEN ON THIS COMMIT**
Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Authority: user instruction `Please continue 💚`, continuing `Let's wire this better please 🙏`

## 1. Frozen motivation

The frozen semantic-delta result is:

`COMPLETE_SYNTHETIC_V6_V3_SEMANTIC_DELTA_NO_DECISION`

Checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V7_V6_SEMANTIC_DELTA_DIAGNOSTIC_RESULT.md`
Commit: `7c43f842c7e4c8833d9c7e25722fd28b52a38ab7`

It separated two remaining wiring problems.

The candidate-competition problem is already localized by the simultaneous-dyad comparison. This PRE addresses only the other problem: frozen V6 strongly corroborates `reattack_m64`, while the frozen bridge-V2/V3 support route returns `NO_ELIGIBLE_DETUNING_ANCHOR` with zero valid support candidates before any NNLS fit can occur.

Frozen `reattack_m64` measurements:

- frozen V6 selected raw template valid: `true`;
- frozen V6 valid candidate count: `34`;
- frozen V6 necessity fraction: `0.14453142873815786`;
- frozen V6 selected raw harmonic innovation: `[50.902462979354425,18.39929669286834,16.311418147811047,5.608287303513769,5.461352299669706,4.151041656270273]`;
- frozen bridge-V2/V3 selected support template: `NO_ELIGIBLE_DETUNING_ANCHOR`;
- support valid candidate count: `0`;
- dual-view fit unavailable.

This diagnostic asks where that coherent reattack evidence is lost between the frozen per-frame complex-deviation sequence and the final leakage-cleaned support representation.

## 2. Diagnostic question — no classifier

For all 23 frozen V6 synthetic audio fixtures, trace the selected MIDI through the existing frozen analysis stages without defining a new final decision:

1. frozen V6 frame geometry and complex prediction-deviation sequence;
2. pre/post deviation maxima and raw onset innovation;
3. frozen bridge-V2 deterministic local-max centers and retained ±1 support bands;
4. frozen V3 detune-anchor harmonic peak/background/support diagnostics.

The diagnostic must identify mechanically whether selected-pitch harmonic evidence is lost because:

- the expected harmonic bin is not a bridge local-max center;
- another center within the frozen ±8 Hann suppression neighborhood wins;
- the selected harmonic survives only partially in the retained ±1 band;
- V3 local background/relative support then exceeds the retained harmonic peak;
- or the failure occurs earlier/later than those mechanisms.

These are descriptive categories only. They are not new acceptance rules.

## 3. Frozen population

Use all 23 fixtures from frozen:

`scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`

in manifest order, unchanged, for three in-process repetitions.

The fixture expected classification is reference-only metadata and may not affect diagnostic computation, branching, output availability, process exit status or any new rule.

No fixture-ID branch is allowed. Named rows may be highlighted only when summarizing the frozen result after execution.

## 4. Frozen dependencies / semantics

Read-only throughout this diagnostic:

- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`;
- frozen fixture manifest, blob `a6c3d99d47c529db3c3c5e4af544d13f21b179aa`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3.py`, blob `45b8f3b66df7500824071489205a732dfe05d759`;
- frozen V3 iteration-2/iteration-3 modules and tests;
- `scripts/songsterr-fresh/v6_innovation_peak_band_bridge_v2.py`, blob `402aa23f3f1821c4e5c45ccf7f170b542d76a453`;
- frozen dual-view and semantic-delta diagnostic files/results;
- frozen V7 successor files;
- all earlier PRE/result checkpoints/workflows;
- `songsterr_pipeline/**`;
- `main`, Production, closed lines and archived V143/Gomyway.

No frozen constant may be changed. In particular:

- V6 frame samples `2048`;
- V6 hop samples `256`;
- V6 FFT size `8192`;
- V6 frame-end offsets `-1536..+1536` in 256-sample increments;
- V6 post end max `1024`;
- bridge suppression radius `8` bins;
- bridge retained peak-band radius `1` bin;
- V3 detune anchors `-40..+40` cents in 5-cent steps;
- V3 peak radius `1`;
- V3 local-background radius `6`;
- V3 local-SNR multiplier `3.0`;
- V3 relative harmonic support floor `0.10`;
- V3 minimum supported harmonics `3`;
- V3 minimum weighted harmonic coverage `0.35`.

The historical V6 `0.20` fundamental-ratio rule remains historical/read-only and is not adopted as a successor rule.

## 5. Required per-fixture temporal measurements

For every fixture with valid frozen V6 context, record:

- frozen frame-end offsets;
- per-frame RMS;
- per-frame total complex-prediction-deviation norm;
- frozen pre-frame indices and post-frame indices used by `_onset_innovation_spectrum()`;
- raw innovation norm;
- bridge-V2 center count and exact center bins;
- bridge retained positive-bin count and exact retained bins.

For insufficient/context rows, record the frozen insufficiency/context reason and stop without fabricating temporal/support evidence.

## 6. Required selected-MIDI detune-anchor trace

For every frozen V3 detune anchor of the selected MIDI and for every available harmonic order up to six, record mechanically from the frozen arrays:

- target frequency and nearest FFT bin;
- frozen V3 peak window bounds (`nearest ±1`);
- raw innovation peak bin/value within that window;
- bridged innovation peak bin/value within that window;
- V3 local-background bin set/range and bridged median background;
- V3 support threshold as already defined by frozen V3 semantics;
- resulting frozen support boolean;
- pre-frame maximum deviation at the chosen/raw harmonic neighborhood;
- post-frame maximum deviation at the chosen/raw harmonic neighborhood;
- raw innovation at that harmonic neighborhood;
- nearest retained bridge center and signed/absolute bin distance where any center exists;
- whether the raw harmonic peak bin lies inside any retained ±1 support band;
- if it does not survive, the strongest bridge center within the frozen ±8 suppression neighborhood and its original raw innovation value, when such a center exists.

The diagnostic may compute distances, ratios and differences only as descriptive finite diagnostics. It may not introduce a cutoff from them.

## 7. Required anchor summaries

For each selected-MIDI detune anchor, record:

- frozen V3 anchor status;
- supported harmonic count;
- weighted harmonic coverage;
- weighted normalized strength;
- fundamental-to-max harmonic ratio diagnostic;
- count of available harmonic peaks whose raw peak bin survives a retained ±1 bridge band;
- count of supported harmonics after bridging;
- per-harmonic trace rows from section 6.

Also record the exact frozen `evaluate_candidate_template()` result for the selected MIDI so the detailed trace can be reconciled with the actual V3 selected-anchor outcome.

## 8. Key comparison classes to identify after execution

The result checkpoint must summarize, without special-case computation:

- ordinary clean onset (`clean_mid_m64`);
- noisy true onset (`attack_noise_true_m64`);
- already-sounding note (`already_sounding_m64`);
- entering note over existing lower note (`selected64_enters_over_existing60`);
- genuine reattack (`reattack_m64`);
- unrelated transient (`unrelated_transient_only_sel64`);
- weak selected note under stronger owner (`weak_selected64_under60`);
- both context-edge insufficiency controls.

These names are result-readability anchors only. The implementation must iterate all fixtures generically.

## 9. Mechanical invariants

The first execution must establish all of the following or fail:

- exact frozen dependency blobs/contracts;
- exactly 23 fixture rows in manifest order;
- exactly 3 in-process repetitions;
- canonical-JSON deterministic output across repetitions;
- `finalDecisionDefined:false` for every row and globally;
- reference expected classification not used for computation;
- finite numeric diagnostics where available;
- no bridge amplitude boost or invented positive bin;
- insufficient/context rows contain no fabricated anchor trace;
- diagnostic code contains no network/model/GPU/subprocess/repository mutation path;
- untouched V3 iteration-3 regression remains 34 fixtures ×3, deterministic, zero mismatches, PASS.

The diagnostic process status depends only on these mechanical invariants, not on whether reattack or any other fixture resembles its frozen reference class.

## 10. Prospective write boundary

May create/change only:

- `scripts/songsterr-fresh/v7_reattack_temporal_support_diagnostics_v1.py`;
- `scripts/songsterr-fresh/test_v7_reattack_temporal_support_diagnostics_v1.py`;
- `.github/workflows/songsterr-v7-reattack-temporal-support-diagnostic-one-shot.yml` if a runner is needed;
- `docs/checkpoints/SONGSTERR_FRESH_V7_REATTACK_TEMPORAL_SUPPORT_DIAGNOSTIC_RESULT.md`;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` for state-only updates.

Any other path requires another prospective PRE.

## 11. First-run policy

- Commit the diagnostic module/test pair before observing any diagnostic output.
- Verify the PRE-to-pair diff contains only the two allowed new Python files.
- Verify exact Git blobs and perform a static import/I/O scan before execution.
- If a runner is needed, use a self-scoped workflow triggered only by its own YAML path and pin/verify every frozen dependency blob before the diagnostic command.
- Execute the prospectively defined diagnostic exactly once, with the untouched V3 regression in the same attempt.
- Freeze the first result exactly as observed.
- No rescue rerun, threshold search, radius search, metric selection or post-result fixture addition.

## 12. Explicit prohibitions

No EGFxSet or other real media; no prior Basic Pitch artifact; no Basic Pitch/Demucs/model inference; no V6/V7 real correctness; no historical V6-threshold adoption/change; no V3 threshold/radius change; no suppression-width or peak-width search; no fixture-ID branch; no per-MIDI exception; no learned parameter; no AG-PT/rejected holdout; no protected song; no physical capture/calibration; no `songsterr_pipeline/**`; no `main`/Production; no GOAT/reference; no reserved GFN; no archived V143/Gomyway.

## 13. Authority after result

Measurement only. The result will not itself authorize a reattack fallback, successor classifier, candidate-population rule, real/model evaluation or delivery advancement.

Any composition/fallback rule after this diagnostic requires another prospective PRE.
