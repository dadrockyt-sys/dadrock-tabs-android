# PRE — Songsterr Fresh V7 Fixed-Feature Competition Diagnostic V1

Status: **PROSPECTIVE / SYNTHETIC-ONLY / DIAGNOSTIC-ONLY / NO CLASSIFIER**
Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## 1. Frozen motivation

Two prospectively frozen results now establish:

1. candidate-population breadth materially changes selected-MIDI NNLS necessity;
2. a threshold-free all-playable competition dictionary can be built for all 19 onset-available frozen fixtures without using historical V6 `0.20` as a competition-admission gate.

Authorities:

- candidate breadth result: `docs/checkpoints/SONGSTERR_FRESH_V7_CANDIDATE_COMPETITION_DIAGNOSTIC_RESULT.md`, commit `4750332a347b03795d089690e8f7c4249319cd71`, run `35057264267`, artifact `10430643432`;
- gate-free result: `docs/checkpoints/SONGSTERR_FRESH_V7_GATE_FREE_COMPETITION_DIAGNOSTIC_RESULT.md`, commit `2b115a380cc49a34fc9d42fe0590073e1d1c6d46`, run `35057812575`, artifact `10431411768`.

The gate-free result also froze a remaining semantic confound: under frozen V6 NNLS construction, candidate admission determines the union of feature bins used for the raw observed vector. Changing the candidate population therefore changes both dictionary columns and observation support.

This PRE isolates those roles by fixing one feature universe before comparing candidate populations.

The blocked temporal/support line remains separate and untouched.

## 2. Diagnostic question — no classifier

For every onset-available frozen fixture, construct the already-frozen threshold-free competition template for every playable MIDI `40..88`.

Define one **fixed feature universe** as the sorted union of harmonic bins from all structurally constructible gate-free templates.

Sample the untouched raw V6 onset innovation on that feature universe exactly once.

Then fit different prospectively defined candidate-column populations against the **same fixed observed vector and same feature bins** to measure column-breadth effects independently from population-induced feature-union changes.

No threshold comparison, selected-note verdict or successor classifier is defined.

## 3. Frozen population

Use all 23 fixtures from:

`scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`

in manifest order, unchanged, for exactly three in-process repetitions.

Reference expected classifications are metadata only and may not affect computation, branching, fit availability, candidate sets, process status or result interpretation.

No fixture-ID computation branch is allowed.

## 4. Frozen dependencies

Read-only:

- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`;
- `scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`, blob `a6c3d99d47c529db3c3c5e4af544d13f21b179aa`;
- `scripts/songsterr-fresh/v7_gate_free_competition_diagnostics_v1.py`, blob `08eb9e945bf2cdf33e640cf7b3349ae075002846`;
- `scripts/songsterr-fresh/v6_innovation_peak_band_bridge_v2.py`, blob `402aa23f3f1821c4e5c45ccf7f170b542d76a453`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3.py`, blob `45b8f3b66df7500824071489205a732dfe05d759`;
- frozen V3 iteration-2 / iteration-3 modules and untouched iteration-3 regression test;
- all prior fresh-pipeline checkpoints/results/runs;
- `songsterr_pipeline/**`, `main`, Production, closed lines and archived V143/Gomyway.

No frozen constant may change.

Historical V6 `0.20` and `0.01` thresholds remain reference-only and are not decision boundaries here.

## 5. Frozen fixed feature universe

For each onset-available fixture:

1. obtain untouched raw V6 onset innovation;
2. use the frozen gate-free template builder to construct competition templates for MIDI `40..88`;
3. define `gateFreeMidis` as every structurally constructible / admitted gate-free competition MIDI;
4. define `fixedFeatureBins` as the sorted unique union of template harmonic bins across **all `gateFreeMidis`**;
5. define `fixedObserved` as raw V6 innovation sampled at `fixedFeatureBins`;
6. define `fixedFeatureEnergy = ||fixedObserved||_2`.

This fixed universe is created before any compared candidate subset is fitted.

No compared subset may add, remove or redefine feature bins. Candidate columns absent from a population are simply absent from the dictionary; observation rows remain fixed.

For the frozen playable range, prior gate-free attempt 1 found all 49 structurally constructible on all 19 onset-available fixtures. This is historical evidence only; the new attempt must verify the same mechanical condition from frozen code rather than assume it.

## 6. Prospectively frozen candidate populations

Construct generically for each onset-available fixture:

### A. `gateFree49Midis`

All structurally constructible gate-free competition MIDIs.

### B. `historicalRawValidMidis`

MIDIs whose untouched frozen V6 `_candidate_template()` is valid.

### C. `supportValidMidis`

MIDIs whose untouched frozen V3 `evaluate_candidate_template()` is valid after the frozen bridge-V2 support transform of the raw V6 innovation.

### D. `rawSupportIntersectionMidis`

`historicalRawValidMidis ∩ supportValidMidis`.

Sort every set ascending. No reference label or post-result output may change membership.

## 7. Fixed-feature NNLS fit

Define one diagnostic fit helper that accepts:

- selected MIDI;
- untouched raw innovation;
- frozen gate-free templates;
- the fixed all-49 feature-bin universe;
- one explicit candidate-MIDI list.

For every fit:

- observed vector is identical `fixedObserved`;
- feature energy is identical `fixedFeatureEnergy`;
- dictionary columns use frozen gate-free template weights placed on the fixed feature rows;
- solver is `scipy.optimize.nnls`;
- selected necessity is `(withoutSelectedResidual - fullResidual) / max(fixedFeatureEnergy, 1e-15)`;
- no threshold comparison is performed.

Record exact candidate list/count, fixed feature list/count/energy, selected coefficient, full residual, residual without selected, necessity fraction and all candidate coefficients.

## 8. Required fixed-feature comparisons

When the selected MIDI belongs to the required set, compute:

1. `gateFree49FixedFit` — population A;
2. `historicalRawValidFixedFit` — population B;
3. `rawSupportIntersectionFixedFit` — population D.

The same fixed feature bins/energy must appear in all available fits for that fixture.

### Column-breadth measurements

Where available record:

- `gateFreeVsHistoricalColumnDelta = gateFree49FixedNecessity - historicalRawValidFixedNecessity`;
- `historicalVsIntersectionColumnDelta = historicalRawValidFixedNecessity - rawSupportIntersectionFixedNecessity`.

These are descriptive scalar differences only.

## 9. Variable-feature references — namespaced only

Carry/recompute prospectively fixed reference values without changing their semantics:

- frozen V6 historical gated fit payload;
- frozen gate-free diagnostic variable-feature all-49 fit from the frozen gate-free module;
- a variable-feature raw/support-intersection fit using the same frozen gate-free/V6-equivalent template geometry and subset-specific union, solely to reproduce the earlier population diagnostic semantics.

Record reference values under a distinct `variableFeatureReferences` namespace.

Do not use reference values to construct the fixed feature universe or candidate sets.

### Feature-universe deltas

Where both values exist record descriptively:

- `historicalFeatureUniverseDelta = historicalRawValidFixedNecessity - frozenV6VariableFeatureNecessity`;
- `intersectionFeatureUniverseDelta = rawSupportIntersectionFixedNecessity - intersectionVariableFeatureNecessity`;
- `gateFreeFeatureUniverseDelta = gateFree49FixedNecessity - gateFree49VariableFeatureNecessity`.

Because the fixed universe is defined from the all-gate-free population, `gateFreeFeatureUniverseDelta` is expected to be mechanically zero within `1e-12`; mismatch is a mechanical failure.

## 10. Geometry / reference invariants

The new diagnostic must not redefine template geometry.

- For historically V6-valid candidates, gate-free templates must continue to reproduce frozen V6 template geometry to `1e-12`.
- The gate-free all-49 fixed fit must reproduce the frozen gate-free variable-feature fit to `1e-12`, because both use the same all-gate-free union.
- The variable-feature raw/support-intersection reference must reproduce the frozen candidate-population diagnostic's raw-template restricted semantics mechanically; it may be recomputed from frozen primitives rather than reading the old artifact.

## 11. Key result-summary classes

The result must summarize generically computed rows for:

- `clean_low_m40`, `clean_mid_m64`, `clean_high_m88`;
- both detune controls;
- `attack_noise_true_m64`;
- `already_sounding_m64`;
- both octave aliases;
- `selected64_enters_over_existing60`;
- both simultaneous-dyad selected notes;
- all simultaneous-triad selected notes;
- `neighbor_sel60_actual61`;
- `reattack_m64` only as a competition/feature measurement, not a temporal/support conclusion;
- `unrelated_transient_only_sel64`;
- `weak_selected64_under60`;
- all insufficient/context rows.

No special-case computation is allowed.

## 12. Mechanical invariants

Attempt 1 must establish or fail:

- exact frozen dependency blobs/contracts;
- exactly 23 fixtures in manifest order;
- exactly 3 in-process repetitions;
- canonical deterministic output across repetitions;
- `finalDecisionDefined:false` globally/per row;
- reference expected labels unused for computation;
- finite diagnostics where available;
- sorted/unique candidate sets within playable range;
- fixed feature bins sorted/unique/in range;
- identical fixed feature bins/energy across every available fixed-feature population fit for a fixture;
- no compared population can redefine observation rows;
- gate-free 49 fixed fit reproduces frozen gate-free variable-feature fit to `1e-12`;
- gate-free/V6 valid template geometry remains equivalent to `1e-12`;
- no support/V3 field is used as a final verdict; support only defines prospectively frozen comparison population D;
- no classifier, threshold decision, candidate search or successor verdict;
- no network/model/GPU/subprocess/repository mutation path;
- untouched V3 iteration-3 regression remains 34 fixtures ×3, deterministic, zero mismatches, PASS.

Process success depends only on these mechanics, never on whether the measurements favor a design.

## 13. First-run evidence preservation

Required artifact:

`songsterr-fresh-v7-fixed-feature-competition-diagnostic`

Required files:

- `fixed-feature-competition-diagnostic.json`;
- `v3-regression.txt`.

Use `actions/upload-artifact@v4` with `if: always()`.

## 14. Prospective write boundary

May create/change only:

- `docs/checkpoints/SONGSTERR_FRESH_V7_FIXED_FEATURE_COMPETITION_DIAGNOSTIC_PRE.md`;
- `scripts/songsterr-fresh/v7_fixed_feature_competition_diagnostics_v1.py`;
- `scripts/songsterr-fresh/test_v7_fixed_feature_competition_diagnostics_v1.py`;
- `.github/workflows/songsterr-v7-fixed-feature-competition-diagnostic-one-shot.yml`;
- `docs/checkpoints/SONGSTERR_FRESH_V7_FIXED_FEATURE_COMPETITION_DIAGNOSTIC_RESULT.md`;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` for state-only updates.

Any other path requires another prospective PRE.

## 15. First-run policy

- Commit PRE before executable code.
- Commit module/test pair before observing output.
- Verify PRE-to-pair diff contains only the two allowed Python files plus state-only checkpoint updates.
- Compile/static guard before execution.
- Add self-scoped workflow only after pair freeze; workflow-file push is sole first execution trigger.
- Pin/verify all frozen dependencies and new PRE/module/test blobs.
- Run diagnostic exactly once with untouched V3 regression.
- Freeze attempt 1 from persisted artifact.
- No rescue rerun, threshold search, MIDI-range search, candidate-subset search, metric selection or post-result fixture addition.

## 16. Explicit prohibitions

No final classifier; no threshold adoption/change/search; no V6 `0.20` transplant; no historical `0.01` decision reuse; no selected-note eligibility change; no reattack repair; no per-MIDI exception; no fixture branch; no candidate-subset search; no learned parameter; no EGFxSet/real media; no Basic Pitch/Demucs/model inference; no real correctness; no AG-PT/rejected holdout; no protected song; no physical capture/calibration; no `songsterr_pipeline/**`; no `main`/Production; no GOAT/reference; no reserved GFN; no archived V143/Gomyway.

## 17. Authority after result

Measurement only. The result will not itself authorize a final successor composition, real/model evaluation or delivery advancement.

Any executable composition after this diagnostic requires another prospective PRE.
