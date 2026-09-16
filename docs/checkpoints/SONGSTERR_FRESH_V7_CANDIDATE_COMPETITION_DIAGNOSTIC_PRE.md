# PRE — Songsterr Fresh V7 Candidate-Population / Competition Diagnostic V1

Status: **PROSPECTIVE / SYNTHETIC-ONLY / DIAGNOSTIC-ONLY / NO CLASSIFIER**
Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## 1. Frozen motivation

This PRE advances only the candidate-population/competition dimension already isolated by the frozen semantic-delta result:

- result: `docs/checkpoints/SONGSTERR_FRESH_V7_V6_SEMANTIC_DELTA_DIAGNOSTIC_RESULT.md`
- result commit: `7c43f842c7e4c8833d9c7e25722fd28b52a38ab7`
- frozen result label: `COMPLETE_SYNTHETIC_V6_V3_SEMANTIC_DELTA_NO_DECISION`

That result established, without defining a successor rule, that:

- `simultaneous_dyad_sel60` is rejected by frozen V6 with a 49-candidate raw-template population and necessity `0.0041216775902363015`;
- the same selected MIDI60 remains strongly necessary when the candidate dictionary is narrowed to the seven support-derived candidates, including when the observed vector is changed back to raw innovation;
- same-audio selected MIDI64 remains necessary in frozen V6 and in the narrow dual-view fit;
- `reattack_m64` is a separate upstream support/temporal problem and does not reach the candidate-competition comparison.

The subsequent temporal/support diagnostic attempt completed mechanically but its exact attempt-1 console payload is not currently accessible. Its frozen evidence-access result is:

`COMPLETE_MECHANICAL_EXECUTION / BLOCKED_STORED_LOG_ACCESS / NO_MEASUREMENT_DECISION`

This PRE does **not** infer anything from that missing payload and does not attempt to repair reattack behavior.

## 2. Diagnostic question

For each frozen V6 synthetic fixture with valid onset innovation, quantify how the selected-MIDI NNLS necessity changes when candidate **population breadth** changes while raw V6 observation and raw V6 template semantics are held fixed.

The primary controlled comparison is:

1. **raw/full** — frozen V6 raw innovation, frozen V6 raw candidate templates, every raw-valid MIDI candidate;
2. **raw/support-MIDI-restricted** — the same raw innovation and the same raw V6 candidate templates, but candidate MIDIs restricted to the intersection of raw-V6-valid and V3-support-valid MIDIs;
3. **support-template/raw-observed reference** — the already-frozen dual-view fit, carried only as a namespaced reference so template-basis differences are not confused with population breadth.

No final decision, threshold, promotion rule, fallback, or successor classifier is defined.

## 3. Frozen population

Use all 23 fixtures from:

`scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`

in manifest order, unchanged, for exactly three in-process repetitions.

Reference expected classifications may be copied into output metadata but may not affect computation, branching, process status, candidate construction, fitting, or availability.

No fixture-ID computation branch is allowed. Named fixtures may be highlighted only in the frozen result summary after execution.

## 4. Frozen dependencies

Read-only throughout this diagnostic:

- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`;
- `scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`, blob `a6c3d99d47c529db3c3c5e4af544d13f21b179aa`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3.py`, blob `45b8f3b66df7500824071489205a732dfe05d759`;
- frozen V3 iteration-2 and iteration-3 modules/tests;
- `scripts/songsterr-fresh/v6_innovation_peak_band_bridge_v2.py`, blob `402aa23f3f1821c4e5c45ccf7f170b542d76a453`;
- `scripts/songsterr-fresh/v7_dual_view_diagnostics_v1.py` and its frozen dependencies;
- `scripts/songsterr-fresh/v7_v6_semantic_delta_diagnostics_v1.py`, blob `f3e63be1dba7c862c5ec654750cc5ec2e27e19b8`;
- all earlier frozen PRE/result checkpoints and one-shot runs;
- `songsterr_pipeline/**`, `main`, Production, closed research lines, and archived V143/Gomyway.

No frozen constant may be changed. Historical V6 thresholds remain historical/reference-only.

## 5. Candidate-set construction

For each onset-available fixture, construct mechanically for all playable MIDIs `40..88`:

- `rawValidMidis`: MIDIs whose frozen V6 `_candidate_template()` is valid on the untouched raw V6 innovation;
- `supportValidMidis`: MIDIs whose frozen V3 `evaluate_candidate_template()` is valid after the frozen bridge-V2 support transform;
- `intersectionMidis = rawValidMidis ∩ supportValidMidis`;
- `rawOnlyMidis = rawValidMidis - supportValidMidis`;
- `supportOnlyMidis = supportValidMidis - rawValidMidis`.

Sort every MIDI set ascending. Do not filter, widen, or add candidates based on reference labels or post-result observations.

If the selected MIDI is not raw-valid, raw-population fits are unavailable for that row. If the selected MIDI is raw-valid but not support-valid, record the set relation but do not treat restricted-fit unavailability as candidate-competition evidence; that is the separate upstream support problem.

## 6. Controlled raw-template NNLS fit

Define one diagnostic helper that accepts an explicit ascending MIDI candidate list and performs the same structural fit as frozen V6 while keeping these semantics fixed:

- observed spectrum: untouched raw V6 onset innovation;
- candidate template basis: frozen V6 `_candidate_template()` rows only;
- feature bins: union of the included raw-template harmonic bins;
- NNLS implementation: `scipy.optimize.nnls`;
- selected necessity definition: `(withoutSelectedResidual - fullResidual) / max(featureEnergy, 1e-15)`;
- no pass/fail comparison to a threshold.

For every available row, record:

- candidate count and exact MIDI list;
- feature-bin count and exact feature-bin list;
- feature energy;
- selected coefficient;
- full residual;
- residual without selected candidate;
- selected necessity fraction.

Required fits:

1. `rawFullFit` using `rawValidMidis`;
2. `rawSupportMidiRestrictedFit` using `intersectionMidis`, only when the selected MIDI is in the intersection.

`rawFullFit` must mechanically reproduce the corresponding frozen V6 fit fields when those fields are available. Any reproduction mismatch beyond prospectively fixed numeric tolerance `1e-12` absolute and relative is a mechanical failure, not a measurement result.

## 7. Prospectively frozen excluded-candidate attribution

When `rawSupportMidiRestrictedFit` is available, quantify every candidate omitted by support eligibility without choosing candidates after observing output.

For each MIDI in `rawOnlyMidis`, ascending:

### Add-one attribution

Fit the candidate set `intersectionMidis ∪ {midi}` and record:

- resulting selected necessity fraction;
- `necessityDeltaFromRestricted = addOneNecessity - restrictedNecessity`.

### Full leave-one-out attribution

Fit `rawValidMidis - {midi}` when the selected MIDI remains present and at least one other candidate remains; record:

- resulting selected necessity fraction;
- `necessityDeltaFromFull = leaveOneOutNecessity - fullNecessity`.

These deltas are descriptive only. No cutoff, winner, causal threshold, or automatic candidate-admission rule is defined.

For readability, the result may report all attribution rows in ascending MIDI order and may additionally identify the numerically largest absolute delta with deterministic tie-break to lower MIDI, but that label is descriptive and cannot itself become a rule.

## 8. Existing dual-view reference

Carry the frozen `v7_dual_view_diagnostics_v1` payload as a namespaced reference for each onset-available row.

Do not recompute a new support-template classifier. The dual-view reference exists only to distinguish:

- population breadth effects under a fixed raw-template basis; from
- template-basis/support-representation differences.

## 9. Key result-summary classes

The frozen result checkpoint must summarize, without special-case computation:

- `simultaneous_dyad_sel60`;
- `simultaneous_dyad_sel64` if present as the same-audio selected-MIDI64 control in the frozen fixture manifest;
- `selected64_enters_over_existing60`;
- `octave_alias_sel72_actual60`;
- `octave_alias_sel79_actual67`;
- `neighbor_sel60_actual61`;
- `unrelated_transient_only_sel64`;
- `weak_selected64_under60`;
- `already_sounding_m64`;
- `reattack_m64` only to state whether candidate-competition comparison is unavailable because selected support eligibility fails.

The implementation must remain generic across all 23 fixtures.

## 10. Mechanical invariants

The first execution must establish all of the following or fail:

- exact frozen dependency blobs/contracts;
- exactly 23 fixture rows in manifest order;
- exactly 3 in-process repetitions;
- canonical-JSON deterministic output across repetitions;
- `finalDecisionDefined:false` globally and for every row;
- reference expected classification not used for computation;
- finite numeric diagnostics where available;
- sorted/unique candidate MIDI lists within playable range;
- raw/full fit reproduces frozen V6 fit fields to `1e-12` when comparable;
- no candidate outside frozen raw-valid/support-valid set algebra enters a fit;
- excluded-candidate attribution enumerates every and only `rawOnlyMidis`;
- diagnostic code contains no network/model/GPU/subprocess/repository mutation path;
- untouched V3 iteration-3 regression remains 34 fixtures ×3, deterministic, zero mismatches, PASS.

Process status depends only on these prospective mechanical invariants, not on whether any fixture resembles its frozen reference class.

## 11. First-run evidence preservation

The one-shot runner must persist the authoritative attempt-1 output as a GitHub Actions artifact in addition to console output.

Required artifact name:

`songsterr-fresh-v7-candidate-competition-diagnostic`

Required files:

- `candidate-competition-diagnostic.json` — exact stdout JSON from the diagnostic test;
- `v3-regression.txt` — untouched V3 regression stdout.

Use `actions/upload-artifact@v4` with `if: always()` so the first attempt's preserved files remain available even if a mechanical invariant fails after producing partial output. The artifact does not authorize a rerun.

## 12. Prospective write boundary

May create/change only:

- `docs/checkpoints/SONGSTERR_FRESH_V7_CANDIDATE_COMPETITION_DIAGNOSTIC_PRE.md`;
- `scripts/songsterr-fresh/v7_candidate_competition_diagnostics_v1.py`;
- `scripts/songsterr-fresh/test_v7_candidate_competition_diagnostics_v1.py`;
- `.github/workflows/songsterr-v7-candidate-competition-diagnostic-one-shot.yml`;
- `docs/checkpoints/SONGSTERR_FRESH_V7_CANDIDATE_COMPETITION_DIAGNOSTIC_RESULT.md`;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` for state-only updates.

Any other path requires another prospective PRE.

## 13. First-run policy

- Commit this PRE before creating executable diagnostic code.
- Commit the diagnostic module/test pair before observing any diagnostic output.
- Verify the PRE-to-pair diff contains only the two prospectively allowed new Python files plus state-only checkpoint updates.
- Perform static import/I/O review before execution.
- Add the self-scoped workflow only after the module/test pair is frozen; the workflow push is the sole first execution trigger.
- Pin/verify every frozen dependency blob before the diagnostic command.
- Execute the diagnostic exactly once with the untouched V3 regression in the same attempt.
- Freeze attempt 1 exactly as observed from the persisted artifact.
- No rescue rerun, threshold search, candidate-range search, candidate-subset search, metric selection, or post-result fixture addition.

## 14. Explicit prohibitions

No reattack repair; no EGFxSet or other real media; no prior Basic Pitch artifact; no Basic Pitch/Demucs/model inference; no V6/V7 real correctness; no historical V6 threshold adoption/change; no V3 threshold/radius change; no suppression-width or peak-width search; no playable-MIDI range search; no fixture-ID computation branch; no per-MIDI exception; no learned parameter; no AG-PT/rejected holdout; no protected song; no physical capture/calibration; no `songsterr_pipeline/**`; no `main`/Production; no GOAT/reference; no reserved GFN; no archived V143/Gomyway.

## 15. Authority after result

Measurement only. The result will not itself authorize a successor classifier, candidate-admission rule, reattack fallback, real/model evaluation, or delivery advancement.

Any composition rule after this diagnostic requires another prospective PRE.
