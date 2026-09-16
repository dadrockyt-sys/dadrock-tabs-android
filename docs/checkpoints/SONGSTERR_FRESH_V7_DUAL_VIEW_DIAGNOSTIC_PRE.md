# PRE — Songsterr Fresh V7 Dual-View Representation Diagnostic V1

Status: **PROSPECTIVE / DIAGNOSTIC-ONLY / FROZEN ON THIS COMMIT**
Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Authority: user instruction `Let's wire this better please 🙏`

## 1. Frozen motivation

This diagnostic follows two permanently frozen representation-bridge failures:

- iteration 1 result `FAIL_SYNTHETIC_REPRESENTATION_BRIDGE_SINGLE_BIN_SPARSIFICATION`, result commit `d2eb412bec5bcf920a397b2d7e69642464497320`, 18/23 frozen V6 audio expectations matched;
- iteration 2 result `FAIL_SYNTHETIC_REPRESENTATION_BRIDGE_THREE_MISMATCHES`, result commit `dfa51a1a6da521a36feb3733d199dfbbeea99de8`, 20/23 frozen V6 audio expectations matched.

Iteration 2 repaired `clean_low_m40` and `simultaneous_triad_sel60`, but three mismatches remained:

- `selected64_enters_over_existing60`: support-view V3 `FAIL_NECESSITY`;
- `simultaneous_dyad_sel60`: support-view V3 unexpected PASS with no lower-owner veto;
- `reattack_m64`: support-view `SELECTED_TEMPLATE_INELIGIBLE`.

The untouched frozen V3 direct-spectrum suite remained 34/34 PASS in both bridge attempts.

No bridge iteration may be edited or rerun.

## 2. Diagnostic question — no decision rule

Frozen V3 currently uses one innovation array for multiple semantic roles:

1. candidate harmonic support and local-background eligibility;
2. the valid-candidate population and template dictionary;
3. NNLS observed evidence and leave-one-out necessity;
4. lower-owner support geometry;
5. iteration-3 candidate-evidence significance denominator.

The bridge results suggest the first role benefits from deterministic Hann-leakage suppression, while candidate competition/necessity may need richer raw V6 innovation.

This iteration asks only:

**What diagnostics are obtained when support eligibility/templates/owners are constructed from the frozen iteration-2 peak-band support view, while the support-derived dictionary is fit against the untouched raw V6 innovation at those exact support-derived feature bins?**

This PRE does **not** define a new classifier, promotion rule, combined PASS condition, threshold, score or delivery decision.

## 3. Frozen evidence views

For every fully contextualized frozen V6 audio fixture:

### Raw view

Use the exact nonnegative frozen V6 onset innovation returned by `_onset_innovation_spectrum()` with no transformation.

### Support view

Use the frozen iteration-2 bridge unchanged:

`v6_innovation_peak_band_bridge_v2.collapse_hann_lobes_to_peak_bands(raw_innovation)`

Frozen bridge constants remain:

- V6 frame `2048`;
- FFT `8192`;
- zero-padding factor `4`;
- local-max separation radius `8` bins;
- retained peak-band radius `1` bin, inherited from frozen V3 `PEAK_BIN_RADIUS=1`;
- no energy invention, boosting, shifting, interpolation or renormalization.

## 4. Prospectively frozen dual-view diagnostic construction

For each selected MIDI and fully analyzable fixture:

1. Validate raw/support arrays on the frozen V3 FFT grid.
2. Construct **all MIDI 40..88 candidate templates from the support view only** by calling frozen `physical_template_plausibility_v3.evaluate_candidate_template()`.
3. Record support-view selected-template status and diagnostics, including chosen detune cents, bins, supported flags/count, weighted harmonic coverage, normalized strength, local backgrounds and thresholds where available.
4. Define the dual-view valid-candidate population as exactly the MIDIs whose support-view templates are frozen-V3 valid.
5. Define feature bins as the sorted union of support-view template bins from that valid-candidate population.
6. Construct the template dictionary exactly as frozen V3 does from those support-derived bins/weights.
7. For the **dual-view fit only**, define the observed vector as the untouched raw V6 innovation sampled at those exact support-derived feature bins.
8. Run the same SciPy NNLS full fit and selected-column leave-one-out reduced fit mechanically, without changing template weights or fitting thresholds.
9. Record selected coefficient, full residual, without-selected residual, raw feature energy and raw-view necessity fraction `(without - full) / max(rawFeatureEnergy, 1e-15)`.
10. Independently compute support-view lower-owner structural diagnostics using the frozen iteration-2 overlap/exclusive-bin semantics (`OVERLAP_BIN_RADIUS=1`, minimum owner exclusive supported count `2`, minimum selected exclusive supported count `2`), **without using those diagnostics to accept/reject anything**.
11. Independently compute the frozen iteration-3 candidate-evidence fraction from the support-view selected-template peaks/thresholds/supported flags and the support-view norm whenever a valid selected template exists, even when a frozen support-view NNLS stage would fail before iteration 3 normally reports it.
12. Also record the ordinary frozen support-view V3 iteration-3 composite output strictly as a comparison diagnostic.

No raw-view candidate template is used for eligibility, because the already-frozen representation failure showed raw Hann-lobe local background is not compatible with the frozen narrow-line support assumption.

No dual-view fit result is converted into a classification in this diagnostic iteration.

## 5. Frozen population

Use all 23 fixtures from frozen `scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`, unchanged.

The fixture's frozen `expectedClassification` may be copied into output only as reference metadata. It must never alter template construction, fit, owner diagnostics, evidence diagnostics, branching or process exit status.

Insufficient-context/audio fixtures remain diagnostic rows with the frozen V6 onset status/reason; no context or spectral evidence may be fabricated.

## 6. Diagnostic output required for every fixture

At minimum record:

- fixture ID;
- selected MIDI;
- frozen expected classification as reference-only metadata;
- V6 onset status/reason, analysis RMS and raw innovation energy where available;
- raw norm / raw positive-bin count;
- support norm / support retained-center count / support positive-bin count;
- frozen support-view V3 composite status/passed flag;
- support selected-template valid/status and diagnostics;
- support valid-candidate count and candidate MIDI list;
- support-derived feature-bin count;
- dual-view fit availability/status;
- dual-view selected coefficient;
- dual-view full residual;
- dual-view without-selected residual;
- dual-view raw feature energy;
- dual-view raw necessity fraction;
- support-view candidate-evidence fraction where defined;
- support-view credible/veto owner rows calculated structurally and independently of a final decision;
- explicit `finalDecisionDefined:false`.

## 7. Mechanical diagnostic invariants

The first diagnostic implementation/test pair must fail closed unless:

- frozen V6/V3/bridge contracts and key constants match exactly;
- raw/support arrays are finite, nonnegative, same length and on the frozen frequency grid;
- support output never exceeds raw input at any bin;
- support nonzero bins are a subset of raw nonzero bins;
- all support-derived template bins are valid indices;
- dictionary/observed dimensions agree;
- all reported numeric diagnostics are finite when their stage is available;
- necessity uses raw feature energy exactly as prospectively defined;
- support candidate-evidence fraction uses support-view norm exactly as frozen iteration-3 semantics define;
- no `finalDecision`, `classification`, `passed` or equivalent new dual-view verdict is emitted by the diagnostic module; the only passed/status fields allowed are copied/namespaced frozen component outputs or mechanical availability statuses;
- all 23 fixture rows are produced in manifest order;
- three in-process repetitions are byte-for-byte deterministic after canonical JSON serialization.

The untouched frozen V3 iteration-3 test must again remain 34 fixtures ×3, deterministic, zero mismatches, PASS.

## 8. Frozen/read-only files

Read-only throughout this diagnostic line:

- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`;
- `scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`;
- all frozen V3 modules/tests;
- `scripts/songsterr-fresh/onset_birth_corroboration_v7.py`;
- all V2/clip-start files;
- iteration-1 bridge files;
- iteration-2 bridge module/test, especially `v6_innovation_peak_band_bridge_v2.py` blob `402aa23f3f1821c4e5c45ccf7f170b542d76a453`;
- all prior PRE/result checkpoints;
- all prior one-shot workflows;
- `songsterr_pipeline/**`;
- all closed lines, `main`, Production and archived V143/Gomyway.

No V3/V6 threshold or bridge parameter may change.

## 9. Prospective write boundary

This diagnostic may create/change only:

- `scripts/songsterr-fresh/v7_dual_view_diagnostics_v1.py`;
- `scripts/songsterr-fresh/test_v7_dual_view_diagnostics_v1.py`;
- `.github/workflows/songsterr-v7-dual-view-diagnostic-one-shot.yml` if repository execution requires a runner;
- `docs/checkpoints/SONGSTERR_FRESH_V7_DUAL_VIEW_DIAGNOSTIC_RESULT.md`;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` for state-only updates.

Any other path requires a new prospective PRE.

## 10. Workflow / execution isolation

Prior workflow isolation established no catch-all automatic `scripts/songsterr-fresh/**` trigger. The subsequently added V7 real and bridge workflows are each self-scoped to their own exact YAML path. The proposed diagnostic Python paths therefore do not match those triggers.

If a runner is required, the only new workflow allowed is `.github/workflows/songsterr-v7-dual-view-diagnostic-one-shot.yml`, and it must:

- trigger only on push changes to its own exact YAML path;
- verify exact frozen/new blobs before execution;
- run only the diagnostic synthetic test plus untouched V3 iteration-3 regression;
- contain no curl/wget/artifact download/dataset URL/model/Basic Pitch/Demucs/GPU/real-media/protected-song/dispatch/repository-mutation step.

## 11. First-run policy

1. Commit diagnostic module/test pair before observing output.
2. Verify PRE-to-pair diff contains exactly the two allowed Python files.
3. Record exact Git blobs and static I/O/import review.
4. If needed, commit the self-scoped synthetic workflow only after the pair is frozen.
5. Execute the diagnostic exactly once, with three deterministic in-process repetitions, plus the untouched V3 regression in the same workflow attempt.
6. Freeze the first diagnostic result exactly as observed.
7. Do not revise this diagnostic implementation and rerun it to search for favorable values.
8. Any later decision/composition rule must be designed in a **new prospective PRE after this diagnostic result is frozen**.

## 12. Explicit prohibitions

This PRE does not authorize any real media, EGFxSet, prior Basic Pitch artifact, Basic Pitch/Demucs/model inference, real correctness run, threshold/radius/support-width search, per-MIDI or dataset-specific rule, AG-PT/rejected-holdout reopening, physical capture/calibration, protected-song access, `songsterr_pipeline/**`, `main`, Production, GOAT/reference, reserved GFN or archived V143/Gomyway work.

## 13. Authority after result

This is measurement only. A completed diagnostic does not authorize a dual-view classifier, integration, production change, or real/model evaluation. Any successor composition rule requires a new prospective synthetic PRE. Any future real evaluation requires a separate real-evaluation PRE plus fresh explicit user authorization.