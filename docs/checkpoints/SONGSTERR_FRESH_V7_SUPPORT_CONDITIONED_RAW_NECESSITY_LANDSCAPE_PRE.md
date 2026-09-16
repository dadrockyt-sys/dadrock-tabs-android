# PRE — Songsterr Fresh V7 Support-Conditioned Raw Necessity Landscape V1

Status: **PROSPECTIVE / SYNTHETIC-ONLY / MEASUREMENT-ONLY / THRESHOLD-FREE / NO CLASSIFIER**
Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Pre-code branch head: `fd7389d3f3aa8293d07218eefd49e18aaa8e9463`

## 1. Frozen motivation

The frozen protection/raw-fit seam result establishes that:

- leakage-cleaned support eligibility is a distinct role;
- frozen lower-owner and candidate-evidence protections can be measured independently of the historical support-space NNLS necessity gate;
- broad all-gate-free fixed-feature raw fit is a distinct continuous measurement;
- selecting a numeric raw-necessity cutoff after observing the frozen fixture values would be post-result tuning;
- reattack remains support-ineligible and temporally unresolved.

Authority:

- protection/raw-fit seam result: `docs/checkpoints/SONGSTERR_FRESH_V7_PROTECTION_FIT_SEAM_DIAGNOSTIC_RESULT.md`, commit `e5b43f9a956310e55186600fc87931fab1b0eb20`, run `35059307767`, artifact `10431851835`;
- fixed-feature result: commit `7230d915cb1e07a0c97b09cdd767f98ba4755c6f`;
- dual-view result and frozen independent support-protection semantics;
- current state commit `fd7389d3f3aa8293d07218eefd49e18aaa8e9463`.

This PRE therefore opens a threshold-free measurement: for **every support-eligible candidate MIDI**, measure that candidate's leave-one-out raw necessity under the same all-49 fixed-feature competition problem. The selected MIDI is only one row in that generic candidate landscape.

No pass/fail cutoff, selected-candidate promotion, rank cutoff or final successor composition is defined.

The blocked temporal/reattack diagnostic remains separate and is not reconstructed.

## 2. Diagnostic question

For every onset-available frozen fixture:

1. construct the frozen leakage-cleaned support representation;
2. enumerate all support-valid candidate MIDIs using frozen V3 template eligibility;
3. construct the already-frozen all-gate-free 49-column raw competition dictionary and its all-49 fixed feature universe;
4. fit the full all-49 dictionary once;
5. for every support-valid MIDI, remove exactly that candidate column, re-fit NNLS against the **same fixed raw observation vector**, and record its leave-one-out necessity fraction;
6. attach the already-frozen candidate-evidence and lower-owner diagnostics for that support-valid candidate;
7. record threshold-free relative-order descriptors such as the number of support-valid candidates with strictly greater raw necessity.

The diagnostic asks whether support-eligible candidates occupy distinguishable positions in the broad raw competition landscape. It does not decide which position should pass.

## 3. Frozen fixture population

Use all 23 fixtures from:

`scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`

in manifest order, unchanged, for exactly three in-process repetitions.

Frozen expected classifications are reference metadata only and may not affect:

- support candidate eligibility;
- candidate landscape membership;
- raw fit construction;
- raw necessity computation;
- owner/evidence diagnostics;
- ordering descriptors;
- availability;
- process status.

No fixture-ID or selected-MIDI special-case computation branch is allowed.

## 4. Frozen read-only dependencies

- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`;
- fixture manifest, blob `a6c3d99d47c529db3c3c5e4af544d13f21b179aa`;
- `scripts/songsterr-fresh/v6_innovation_peak_band_bridge_v2.py`, blob `402aa23f3f1821c4e5c45ccf7f170b542d76a453`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3.py`, blob `45b8f3b66df7500824071489205a732dfe05d759`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration2.py`, blob `7090e17baff60f91700a760f617e905ff53484ab`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration3.py`, blob `39629250c6d141d5cda9e9d7f570580ec725ae42`;
- `scripts/songsterr-fresh/v7_dual_view_diagnostics_v1.py`, blob `e9e84ed663aab732408d1d618bd9486ffb660628`;
- `scripts/songsterr-fresh/v7_gate_free_competition_diagnostics_v1.py`, blob `08eb9e945bf2cdf33e640cf7b3349ae075002846`;
- `scripts/songsterr-fresh/v7_fixed_feature_competition_diagnostics_v1.py`, blob `d69382ae14b1fb8f7f570919240dce372db1e424`;
- untouched V3 iteration-3 regression test, blob `76455337bd17a952dd36c1dabd03ce741e806b07`;
- all earlier frozen fresh-pipeline results/checkpoints.

No frozen dependency or constant may change.

Historical V6 `0.20`, V3/V6 necessity `0.01`, and V3 evidence `0.10` remain historical/frozen reference semantics only. **No numeric threshold is applied to the new raw-necessity landscape.**

## 5. Frozen support candidate population

For every onset-available event:

1. obtain raw V6 onset innovation through frozen V6;
2. compute bridge-V2 support through the frozen bridge only;
3. evaluate frozen V3 candidate templates for every playable MIDI `40..88` on that support view;
4. define `supportValidMidis` as every MIDI whose frozen V3 candidate template is valid;
5. sort ascending.

Landscape membership is exactly `supportValidMidis`. The selected MIDI has no influence on membership.

For every support-valid candidate, record:

- frozen support template;
- independent candidate-evidence diagnostic using frozen dual-view helper semantics;
- independent lower-owner diagnostic using frozen dual-view helper semantics.

No support-space composite necessity gate may remove a support-valid candidate from the landscape.

## 6. Frozen all-49 fixed raw competition problem

Use the same mechanics already frozen by the gate-free and fixed-feature diagnostics:

1. construct a gate-free competition template for every playable MIDI `40..88`;
2. require all 49 to be structurally constructible/admitted for each onset-available frozen fixture, matching prior first-run mechanics;
3. define one fixed feature universe as the sorted union of all 49 gate-free template bins;
4. sample untouched raw V6 innovation on that universe once;
5. define one 49-column dictionary from the frozen gate-free template weights;
6. run full `scipy.optimize.nnls` once.

The full fit must reproduce the frozen fixed-feature all-49 fit to `1e-12`.

## 7. Per-candidate raw necessity landscape

For every MIDI in `supportValidMidis`:

- identify its all-49 column;
- record its full-fit coefficient;
- delete exactly that one column from the 49-column dictionary;
- run reduced NNLS against the same fixed observed vector;
- define raw necessity as:

`(withoutCandidateResidual - fullResidual) / max(fixedFeatureEnergy, 1e-15)`

Record:

- MIDI;
- selected-for-fixture boolean for readability only;
- full-fit coefficient;
- full residual;
- residual without candidate;
- raw necessity fraction;
- candidate-evidence diagnostic;
- lower-owner diagnostic;
- frozen support template.

No raw necessity threshold or boolean pass field may be defined.

## 8. Threshold-free relative-order descriptors

After every support-valid candidate row is computed, record for each candidate:

- `strictlyGreaterRawNecessityCount`: count of support-valid landscape rows whose raw necessity is strictly greater;
- `strictlyGreaterPositiveCoefficientCount`: count of support-valid rows whose full-fit coefficient is strictly greater;
- deterministic display ordering by descending raw necessity, then ascending MIDI only for serialized readability.

For the selected MIDI, when support eligible, record a selected-row reference and its two strictly-greater counts.

These are descriptive order measurements. **No maximum-only rule, top-K rule, rank cutoff or tie rule is a classifier.**

## 9. Required mechanical cross-checks

Attempt 1 must mechanically establish:

- exactly 23 frozen fixtures in manifest order;
- exactly three in-process repetitions;
- deterministic canonical output;
- reference expected classifications unused for computation;
- onset-unavailable rows contain no fabricated landscape;
- support view does not boost amplitude or invent a positive bin;
- `supportValidMidis` exactly reproduce frozen dual-view support-valid MIDIs;
- all 49 gate-free competition templates are mechanically available on each onset-available row;
- fixed feature bins/energy/full residual/all-49 coefficients reproduce frozen fixed-feature all-49 fit to `1e-12`;
- one landscape row exists for every and only every support-valid MIDI;
- every landscape raw necessity uses the identical all-49 fixed observed vector and full residual;
- for a support-eligible selected MIDI, its landscape raw necessity and coefficient reproduce the frozen selected all-49 fixed raw fit to `1e-12`;
- per-candidate owner/evidence diagnostics reproduce frozen dual-view helper semantics;
- no raw threshold, rank threshold, candidate subset search, final decision or successor classification;
- no network/model/GPU/subprocess/repository-mutation path;
- untouched V3 iteration-3 regression remains 34 fixtures ×3, deterministic, mismatch `0`, PASS.

Process success depends only on these mechanics, not on whether any candidate rank resembles reference expected metadata.

## 10. Prospectively named result summaries

The result checkpoint must summarize generically computed landscapes for:

- `clean_low_m40`, `clean_mid_m64`, `clean_high_m88`;
- both detune controls;
- `attack_noise_true_m64`;
- `already_sounding_m64`;
- both octave aliases;
- `selected64_enters_over_existing60`;
- both simultaneous-dyad selected-note rows;
- all three simultaneous-triad selected-note rows;
- `neighbor_sel60_actual61`;
- `reattack_m64` only as a support-availability fact — no temporal inference;
- `unrelated_transient_only_sel64`;
- `weak_selected64_under60`;
- all insufficient/context controls.

These names are result-readability anchors only and may not alter computation.

## 11. First-run evidence preservation

Required artifact:

`songsterr-fresh-v7-support-conditioned-raw-necessity-landscape`

Required files:

- `support-conditioned-raw-necessity-landscape.json`;
- `v3-regression.txt`.

Use `actions/upload-artifact@v4` with `if: always()`.

## 12. Prospective write boundary

After this PRE is committed, only these paths may be created/changed for this line:

- `scripts/songsterr-fresh/v7_support_conditioned_raw_necessity_landscape_v1.py`;
- `scripts/songsterr-fresh/test_v7_support_conditioned_raw_necessity_landscape_v1.py`;
- `.github/workflows/songsterr-v7-support-conditioned-raw-necessity-landscape-one-shot.yml`;
- `docs/checkpoints/SONGSTERR_FRESH_V7_SUPPORT_CONDITIONED_RAW_NECESSITY_LANDSCAPE_RESULT.md`;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` for state-only updates.

No existing V6/V3/V7 implementation or frozen result may be edited.

## 13. First-run policy

- Commit this PRE before executable code.
- Commit module/test pair before observing output.
- Verify PRE-to-pair diff contains only the two allowed Python files plus state-only checkpoint updates.
- Compile/static-guard committed pair before execution.
- Add the self-scoped one-shot workflow only after pair freeze; its own workflow-file push is the sole first execution trigger.
- Pin/verify every frozen dependency and new PRE/module/test blob.
- Execute exactly once with untouched V3 regression.
- Persist attempt-1 evidence as the required artifact.
- Freeze attempt 1 before any later executable composition work.
- No rescue rerun, threshold search, rank-cutoff search, candidate-subset search, MIDI search, metric selection or post-result fixture addition.

## 14. Explicit prohibitions

No classifier; no raw-necessity threshold; no top-K/rank cutoff; no maximum-only acceptance rule; no historical `0.01` transport; no V6 `0.20` transplant; no selected-note eligibility change; no candidate-subset search; no fixture/MIDI branch; no learned parameter; no reattack repair/reconstruction/fallback; no EGFxSet or real media; no Basic Pitch/Demucs/model inference; no real correctness; no AG-PT/rejected holdout; no protected song; no physical calibration; no `songsterr_pipeline/**`; no `main`/Production; no GOAT/reference; no reserved GFN; no archived V143/Gomyway.

## 15. Authority after result

Measurement only. The result may show how support-eligible candidates are ordered by broad fixed-feature raw contribution without choosing a cutoff. It does not authorize a final successor composition, raw/rank threshold, temporal repair, real/model evaluation or delivery advancement.
