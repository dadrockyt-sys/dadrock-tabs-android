# PRE — Songsterr Fresh V7 Protection / Raw-Fit Seam Diagnostic V1

Status: **PROSPECTIVE / SYNTHETIC-ONLY / MEASUREMENT-ONLY / NO CLASSIFIER**
Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Pre-code branch head: `e01969f6fbf6abc464079eae951c279d80c82974`

## 1. Motivation and frozen authorities

The fixed-feature competition result separated candidate-column breadth from feature-universe effects, but it did not define a successor acceptance rule. The frozen V7 wiring review then established that historical V7 feeds raw V6 innovation directly into frozen V3 iteration 3, thereby coupling support/template eligibility, support-space NNLS necessity, lower-owner protection and candidate-evidence significance on one representation.

The newer frozen diagnostics require those roles to remain separated. This PRE therefore asks a narrower measurement question: **what do the already-frozen support protections look like beside the already-frozen broad fixed-feature raw fit, without defining a final decision or transporting a raw-fit threshold?**

Frozen authorities include:

- V3 iteration-3 synthetic result `e97ab67c9c2794f4a50c5170102d1380484f5fb1`;
- V7 mechanical integration result `9f6345e971f36a0def367a70564ba9b86c948e23`;
- dual-view diagnostic result / semantics, including independent owner and candidate-evidence diagnostics;
- semantic-delta result `7c43f842c7e4c8833d9c7e25722fd28b52a38ab7`;
- candidate-breadth result `4750332a347b03795d089690e8f7c4249319cd71`;
- gate-free result `2b115a380cc49a34fc9d42fe0590073e1d1c6d46`;
- fixed-feature result `7230d915cb1e07a0c97b09cdd767f98ba4755c6f`;
- current-state wiring review commit `e01969f6fbf6abc464079eae951c279d80c82974`.

The temporal/support attempt remains blocked at result commit `86549fcf3f15898aa551064b522ce42ca32b1b86`. This PRE does not reconstruct, rerun or repair that diagnostic.

## 2. Diagnostic question — no final verdict

For each of the 23 frozen V6 synthetic audio fixtures, measure side-by-side:

1. untouched raw V6 onset innovation;
2. leakage-cleaned bridge-V2 support representation;
3. frozen V3 selected-template eligibility on the support representation;
4. frozen lower-owner geometry/veto diagnostics computed independently of support-space NNLS acceptance;
5. frozen candidate-evidence significance diagnostics computed independently of support-space NNLS acceptance;
6. the already-frozen all-gate-free, fixed-feature raw NNLS competition fit;
7. the historical frozen V7 raw-to-V3 composite only as a namespaced reference.

The diagnostic must not combine those measurements into a successor PASS/FAIL. In particular it must not define a raw-necessity threshold, transport historical `0.01` onto the fixed-feature raw fit, or promote an ineligible support template.

## 3. Frozen population

Use all 23 fixtures from:

`scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`

in manifest order, unchanged, for exactly three in-process repetitions.

Reference expected classifications are metadata only. They may not affect computation, branching, support eligibility, owner/evidence diagnostics, fit construction, availability, process status or any rule.

No fixture-ID or MIDI-specific computation branch is allowed.

## 4. Frozen read-only dependencies

The diagnostic may import these existing modules read-only:

- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`;
- fixture manifest, blob `a6c3d99d47c529db3c3c5e4af544d13f21b179aa`;
- `scripts/songsterr-fresh/v6_innovation_peak_band_bridge_v2.py`, blob `402aa23f3f1821c4e5c45ccf7f170b542d76a453`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3.py`, blob `45b8f3b66df7500824071489205a732dfe05d759`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration2.py`, blob `7090e17baff60f91700a760f617e905ff53484ab`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration3.py`, blob `39629250c6d141d5cda9e9d7f570580ec725ae42`;
- `scripts/songsterr-fresh/v7_dual_view_diagnostics_v1.py`, blob `e9e84ed663aab732408d1d618bd9486ffb660628`;
- `scripts/songsterr-fresh/v7_gate_free_competition_diagnostics_v1.py`, blob `08eb9e945bf2cdf33e640cf7b3349ae075002846`;
- `scripts/songsterr-fresh/v7_fixed_feature_competition_diagnostics_v1.py`, blob `d69382ae14b1fb8f7f570919240dce372db1e424`;
- historical `scripts/songsterr-fresh/onset_birth_corroboration_v7.py`, blob `6dfadda70db6b902f1dcc4d804f2d66da547314d`, reference-only;
- untouched V3 iteration-3 regression test, blob `76455337bd17a952dd36c1dabd03ce741e806b07`.

No frozen dependency or constant may change.

## 5. Support-side measurements

For every onset-available row:

1. obtain raw innovation only through frozen V6 `_onset_innovation_spectrum()`;
2. produce support only through frozen bridge-V2 `collapse_hann_lobes_to_peak_bands()`;
3. evaluate V3 candidate templates for all playable MIDIs `40..88` on that support representation;
4. record the selected support template exactly as returned by frozen V3;
5. record sorted support-valid candidate MIDIs;
6. use the already-frozen independent dual-view helper semantics for lower-owner diagnostics;
7. use the already-frozen independent dual-view helper semantics for candidate-evidence diagnostics.

These support-side diagnostics must remain independent of the V3 base composite necessity verdict. A selected template may be eligible even when the historical support-space composite fails necessity; owner/evidence measurements must remain observable in that case exactly as in the frozen dual-view diagnostic.

### Existing protection constants

The diagnostic may report whether the already-frozen candidate-evidence fraction is below or at/above V3 iteration-3 minimum `0.10`, because that threshold is an existing frozen support protection. It may report whether frozen owner diagnostics contain vetoing owners. These are support-protection measurements only and must not be aggregated into a new final classifier field.

No new support threshold, coverage threshold, owner threshold or evidence threshold may be introduced.

## 6. Raw fixed-feature fit measurement

For the same onset-available event, call the frozen fixed-feature diagnostic and carry only its existing all-gate-free fixed-fit measurement as the primary raw-fit view:

`fixedFeatureFits.gateFree49FixedFit`

The diagnostic must preserve its exact:

- candidate MIDI list/count;
- fixed feature-bin list/count;
- fixed feature energy;
- selected coefficient;
- full residual;
- residual without selected;
- necessity fraction;
- coefficient rows.

No raw-necessity comparison or decision boundary is allowed. Historical `0.01` may appear only inside namespaced frozen reference payloads already returned by dependencies; this diagnostic must not compute `rawNecessityPassed`, `passed`, or an equivalent field.

## 7. Historical references — namespaced only

Carry the following as references without using them to define new measurements:

- frozen dual-view support composite and its narrow-dictionary raw fit;
- frozen fixed-feature historical/intersection comparisons;
- historical frozen V7 `evaluate_in_memory_innovation()` result on the untouched raw V6 innovation.

Historical V7 may contain `passed` because it is a frozen historical result. It must live under an explicit `historicalReferences` namespace and must not become this diagnostic's decision.

## 8. Required per-row schema

Each row must include at minimum:

- `fixtureId` in frozen manifest order;
- `selectedMidi`;
- reference expected classification plus `referenceExpectedUsedForComputation:false`;
- onset availability/status;
- `finalDecisionDefined:false`;
- raw/support norms and bridge diagnostics where available;
- selected support template;
- support-valid candidate MIDI list/count;
- owner diagnostics;
- candidate-evidence diagnostics;
- all-gate-free fixed-feature raw fit;
- namespaced historical references.

Insufficient/context rows must not fabricate support or fit measurements.

## 9. Prospectively named result-summary classes

After attempt 1, summarize generic rows for:

- `clean_low_m40`, `clean_mid_m64`, `clean_high_m88`;
- `detune_plus25_m64`, `detune_minus25_m64`;
- `attack_noise_true_m64`;
- `already_sounding_m64`;
- both octave aliases;
- `selected64_enters_over_existing60`;
- `simultaneous_dyad_sel60` and `simultaneous_dyad_sel64`;
- all simultaneous-triad selected-note rows;
- `neighbor_sel60_actual61`;
- `reattack_m64` only as a support-availability/raw-fit juxtaposition, with no temporal mechanism inference;
- `unrelated_transient_only_sel64`;
- `weak_selected64_under60`;
- all insufficient/context controls.

These names are readability anchors only. Computation must iterate all fixtures identically.

## 10. Mechanical invariants

Attempt 1 must establish or fail:

- exact pinned dependency blobs/contracts;
- exactly 23 frozen fixtures in manifest order;
- exactly three in-process repetitions;
- canonical deterministic output across repetitions;
- `finalDecisionDefined:false` globally/per row;
- reference expected classifications unused for computation;
- finite diagnostics where available;
- support representation never boosts amplitude or invents a positive bin;
- selected support template, support candidate list, owner diagnostics and evidence diagnostics exactly reproduce frozen dual-view semantics;
- all-gate-free fixed-feature raw fit exactly reproduces frozen fixed-feature diagnostic semantics to `1e-12` where available;
- historical V7 reference exactly reproduces the frozen historical module for the same raw innovation;
- no support-space necessity result is used to suppress independent owner/evidence diagnostics;
- no raw-fit threshold comparison, final decision, candidate subset search or metric selection;
- no network/model/GPU/subprocess/repository-mutation path;
- untouched V3 iteration-3 regression remains 34 fixtures ×3, deterministic, zero mismatches, PASS.

Process success depends only on those mechanical invariants, never on whether a row resembles its reference expected classification.

## 11. First-run evidence preservation

Required artifact:

`songsterr-fresh-v7-protection-fit-seam-diagnostic`

Required files:

- `protection-fit-seam-diagnostic.json`;
- `v3-regression.txt`.

Use `actions/upload-artifact@v4` with `if: always()`.

## 12. Prospective write boundary

After this PRE is committed, only these paths may be created/changed for this line:

- `scripts/songsterr-fresh/v7_protection_fit_seam_diagnostics_v1.py`;
- `scripts/songsterr-fresh/test_v7_protection_fit_seam_diagnostics_v1.py`;
- `.github/workflows/songsterr-v7-protection-fit-seam-diagnostic-one-shot.yml`;
- `docs/checkpoints/SONGSTERR_FRESH_V7_PROTECTION_FIT_SEAM_DIAGNOSTIC_RESULT.md`;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` for state-only updates.

No existing V6/V3/V7 implementation or frozen result file may be edited.

## 13. First-run policy

- Commit this PRE before executable code.
- Commit the module/test pair before observing output.
- Verify PRE-to-pair diff contains only the two allowed new Python files plus state-only checkpoint updates.
- Compile/static-guard the committed pair before execution.
- Add the self-scoped one-shot workflow only after pair freeze; its own workflow-file push is the sole execution trigger.
- Pin/verify every frozen dependency and new PRE/module/test blob.
- Execute exactly once with untouched V3 regression in the same attempt.
- Persist attempt-1 evidence as the required artifact.
- Freeze the result before any further executable composition work.
- No rescue rerun, threshold search, candidate search, metric selection or post-result fixture addition.

## 14. Explicit prohibitions

No final classifier; no successor PASS/FAIL; no raw-necessity threshold; no transfer of historical V6/V3 `0.01` onto the fixed-feature raw fit; no V6 `0.20` transplant; no selected-note eligibility change; no temporal/reattack repair or reconstruction; no per-MIDI exception; no fixture branch; no candidate subset search; no learned parameter; no EGFxSet or other real media; no Basic Pitch/Demucs/model inference; no real correctness; no AG-PT/rejected holdout; no protected song; no physical capture/calibration; no `songsterr_pipeline/**`; no `main`/Production; no GOAT/reference; no reserved GFN; no archived V143/Gomyway.

## 15. Authority after result

Measurement only. The result may establish whether the frozen support protections and broad fixed-feature raw fit can be observed side-by-side without the old support-space necessity coupling. It will not authorize a raw-fit threshold, complete successor composition, temporal repair, real/model evaluation or delivery advancement.
