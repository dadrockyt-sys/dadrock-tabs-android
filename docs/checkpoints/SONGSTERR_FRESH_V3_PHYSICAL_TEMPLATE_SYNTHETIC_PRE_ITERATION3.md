# SONGSTERR FRESH V3 PHYSICAL-TEMPLATE SYNTHETIC PRE — ITERATION 3

Status: **PROSPECTIVE / FROZEN ON FIRST COMMIT**
Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
PRE parent head: `eca05f1c46208f0df4273a2948e98de7db611563`

This PRE is frozen before any iteration-3 implementation exists and before any iteration-3 synthetic result is observed. Iterations 1 and 2 remain immutable frozen FAIL history and are not patched or rerun.

## 1. MOTIVATION FROM FROZEN ITERATION 2

Iteration-2 PRE: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE_ITERATION2.md`, frozen commit `b2821f8690bea49783071ead87e69424fd63c787`.

Iteration-2 result: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT_ITERATION2.md`, frozen FAIL commit `7153a02ede14b0a43af58609bdc12cd4b792e9b9`.

The first committed iteration-2 implementation/test pair at head `4d69b7bc20637507c3a9167a5fb9c5ad498773ca` evaluated 31 fixtures three times deterministically. Five inherited rejection fixtures unexpectedly passed: `two_harmonics_only`, `single_peak_only`, `broadband_noise`, `nonharmonic_impulses`, and `clip_start_insufficient_support`.

The owner-aware guard itself repaired the frozen iteration-1 alias defect while preserving the prospective owner/polyphony controls. Iteration 3 therefore preserves iteration 2 unchanged and addresses only the newly established synthetic weakness: an eligible detuning anchor can be selected from locally plausible but globally insignificant candidate evidence.

This is synthetic research only. It does not authorize real-media/model evaluation, frozen V6/V2 modification, Basic Pitch inference, EGFxSet, AG-PT-set payload access, rejected holdouts, protected songs, physical capture/calibration, V143/Gomyway, GOAT/reference, GuitarSet/V3 validation, IDMT/V4, V5/FLGD, Guitar-TECHS, Production, or `main`.

## 2. WORKFLOW ISOLATION RECHECK

The authoritative automatic-trigger audit was recorded at commit `cc924c96abf70b23e79bda60010d6c8466a1d301`.

Before this PRE was written, compare `cc924c96abf70b23e79bda60010d6c8466a1d301..eca05f1c46208f0df4273a2948e98de7db611563` showed changes only under `docs/checkpoints/` and the isolated V3 synthetic research files. No `.github/workflows` file changed. The audited automatic workflow set contained no catch-all `scripts/songsterr-fresh/**` push path; the only broad research wildcard recorded by that audit was `songsterr_pipeline/**`, outside this V3 boundary.

Iteration 3 uses only the same isolated `scripts/songsterr-fresh/physical_template_plausibility_v3*` research namespace with new iteration-specific filenames. No workflow file may be created, edited, dispatched, or executed by iteration 3.

## 3. EXACT ITERATION-3 WRITE BOUNDARY

After this PRE is frozen, only these files may be created or changed for iteration 3:

- `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration3.py` — new evidence-significance wrapper research module;
- `scripts/songsterr-fresh/test_physical_template_plausibility_v3_iteration3.py` — new deterministic synthetic harness;
- `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT_ITERATION3.md` — result record after the first committed test execution;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` — state-transition record only.

This PRE is immutable after its creation commit.

Frozen/read-only dependencies:

- `scripts/songsterr-fresh/physical_template_plausibility_v3.py`, Git blob `45b8f3b66df7500824071489205a732dfe05d759`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration2.py`, Git blob `7090e17baff60f91700a760f617e905ff53484ab`;
- `scripts/songsterr-fresh/test_physical_template_plausibility_v3_iteration2.py`, Git blob `eefe00346a94e8f0ed433ac916352a4b2e9331c5`;
- all iteration-1/iteration-2 PRE/result records;
- frozen V6/V2 implementations, all workflow files, `songsterr_pipeline/**`, and all closed research lines.

## 4. INHERITED ITERATION-2 MECHANISM — UNCHANGED

Iteration 3 must import the frozen iteration-2 wrapper read-only and may only reject an iteration-2 PASS. It may never promote an iteration-2 failure.

The following remain unchanged and outside iteration-3 tuning:

- iteration-1 candidate-template construction and detuning-anchor search;
- 44.1 kHz / FFT 8192 grid, MIDI 40–88, six harmonics and ±1-bin peak search;
- -40..+40 cent anchors at 5-cent spacing;
- local background/SNR and relative support rules;
- minimum three supported harmonics and weighted coverage 0.35;
- shared NNLS and `necessityFraction >= 0.01`;
- iteration-2 lower-owner overlap radius 1 bin;
- iteration-2 minimum two owner-exclusive supported harmonics and two selected-exclusive supported harmonics;
- all boundary/fail-closed semantics represented by the frozen fixture set.

The historical frozen V6 `0.20` ratio remains untouched and is not an iteration-3 threshold.

## 5. PROSPECTIVE ITERATION-3 HYPOTHESIS

A locally eligible detuning anchor should not be accepted when the supported harmonic evidence unique to that selected template is only a tiny fraction of the complete innovation spectrum. This specifically guards against anchors assembled from incidental local maxima while preserving strong coherent harmonic series, weak/zero fundamentals with strong upper harmonics, and genuine polyphony.

The new guard is deliberately global-and-scale-free: it measures supported candidate evidence relative to the L2 norm of the same already-validated in-memory innovation spectrum. It does not use confidence, selected MIDI identity, real-data observations, dataset metadata, or any learned/fitted parameter.

## 6. FROZEN EVIDENCE-SIGNIFICANCE GUARD

### 6.1 Preconditions and decision order

For selected MIDI `S`:

1. Call frozen iteration-2 `evaluate_owner_aware_composite(S, innovation, frequencies)`.
2. If iteration 2 does not PASS, return that failure unchanged in substance. Iteration 3 cannot promote it.
3. From the iteration-2 result, use the frozen iteration-1 selected template at `baseComposite.selectedTemplate`.
4. Apply the evidence-significance calculation below.
5. Only a case that passes both iteration 2 and the significance guard may return iteration-3 PASS.

Frozen order:

`iteration-1 eligibility -> iteration-1 NNLS necessity -> iteration-2 lower-owner guard -> iteration-3 evidence-significance guard`.

### 6.2 Supported excess evidence

For each selected-template harmonic `i`, use the already-frozen diagnostics:

- observed peak `p_i = observedHarmonicInnovation[i]`;
- frozen support threshold `t_i = supportThresholds[i]`;
- frozen support flag `supported[i]`.

Define prospectively:

`e_i = max(0, p_i - t_i)` when `supported[i] == true`, otherwise `e_i = 0`.

Then:

`supportedExcessNorm = sqrt(sum(e_i^2))`

`innovationNorm = L2(innovation)`

`candidateEvidenceFraction = supportedExcessNorm / innovationNorm`

All values must be finite. The already-frozen base validation guarantees a nonnegative one-dimensional spectrum and `innovationNorm >= 1e-6`; iteration 3 nevertheless fails closed on missing/malformed selected-template diagnostics or any nonfinite/invalid calculated value.

### 6.3 Frozen threshold and status

Freeze:

`MIN_CANDIDATE_EVIDENCE_FRACTION = 0.10`

Iteration-3 PASS requires:

`candidateEvidenceFraction >= 0.10`.

Otherwise return deterministic FAIL status:

`INSUFFICIENT_CANDIDATE_EVIDENCE_SIGNIFICANCE`.

The value `0.10` is fixed prospectively from the geometry of the synthetic measurement rather than from any closed real observation: six candidate harmonic slots occupy only a tiny fraction of the 4097-bin innovation vector; an unstructured-noise reference scale is approximately `sqrt(6 / 4097) ~= 0.038` before peak-selection inflation. A 0.10 minimum requires candidate-aligned supported excess to be materially more concentrated than that diffuse baseline while remaining dimensionless and amplitude-scale invariant. This rationale does not use EGFxSet, AG-PT-set, or any real candidate result.

No per-MIDI exception, no confidence term, no V6 `0.20` reuse, no owner-rule change, and no post-result threshold adjustment are permitted within iteration 3.

## 7. FROZEN 31 ITERATION-2 REGRESSION FIXTURES

Iteration 3 must recreate all 31 iteration-2 fixtures exactly with seed `730915`, spectra, amplitudes, cents, selected MIDI, context fields, and expected outcomes unchanged.

Expected PASS (16):

- `strong_fundamental_inclip`;
- `weak_fundamental_bright_inclip`;
- `zero_fundamental_upper_support_inclip`;
- `weak_fundamental_clip_start_post_only`;
- `true_polyphony_a3_plus_e5`;
- `true_polyphony_a4_plus_b4_selected_69`;
- `true_polyphony_a4_plus_b4_selected_71`;
- `timbre_bright_-30c`, `timbre_bright_+0c`, `timbre_bright_+30c`;
- `timbre_dark_-30c`, `timbre_dark_+0c`, `timbre_dark_+30c`;
- `timbre_fundamental_notch_-30c`, `timbre_fundamental_notch_+0c`, `timbre_fundamental_notch_+30c`.

Expected FAIL / fail-closed (13):

- `octave_alias_lower_a3_selected_a4` — must still reject specifically through `LOWER_OWNER_EXPLAINS_SELECTED` with MIDI 57 among vetoing owners;
- `third_harmonic_owner_a3_selected_e5`;
- `two_harmonics_only`;
- `single_peak_only`;
- `broadband_noise`;
- `near_silence`;
- `nonharmonic_impulses`;
- `clip_start_insufficient_support`;
- `input_nonfinite`;
- `input_shape_mismatch`;
- `input_negative`;
- `input_missing_frequency_bin`;
- `input_fewer_than_three_available_harmonics`.

Expected PASS owner controls (2):

- `true_octave_polyphony_a3_plus_a4`;
- `weak_lower_a3_plus_a4`.

Total inherited fixtures: `16 + 13 + 2 = 31`.

For all inherited cases, iteration 3 must preserve the frozen expected PASS/FAIL semantics. Earlier deterministic failure statuses may pass through unchanged. The iteration-3 significance status is permitted only as an additional rejection of a case whose frozen iteration-2 result was PASS.

## 8. NEW PROSPECTIVE SCALE CONTROLS

These are frozen before implementation and before the first iteration-3 execution.

### 8.1 PASS — low-scale coherent harmonic series

`low_scale_valid_harmonic_a4`:

- background scale `0.0002`;
- MIDI 69 amplitudes `[0.100, 0.055, 0.036, 0.024, 0.017, 0.012]`;
- cents `0`;
- selected MIDI 69 must PASS.

This is exactly a 0.1 amplitude scaling of the inherited strong-fundamental profile and background, prospectively checking scale invariance.

### 8.2 FAIL — low-scale broadband noise

`low_scale_broadband_noise`:

- spectrum is only `fresh_spectrum(0.002)` with seed `730915`;
- selected MIDI 69;
- must FAIL through iteration 2 or the new significance guard.

### 8.3 FAIL — high-scale broadband noise

`high_scale_broadband_noise`:

- spectrum is only `fresh_spectrum(0.20)` with seed `730915`;
- selected MIDI 69;
- must FAIL through iteration 2 or the new significance guard.

These two noise controls surround the inherited `broadband_noise` scale `0.02` by one and ten times, checking that the new ratio is not merely an absolute-amplitude filter.

Total iteration-3 fixture inventory: `34`.

## 9. IMMUTABLE ITERATION-3 ACCEPTANCE GATES

Iteration 3 is PASS only if all are true on the first committed implementation/test pair:

1. all 18 inherited PASS cases remain PASS (the 16 inherited PASS cases plus both iteration-2 owner/polyphony PASS controls);
2. all 13 inherited FAIL/fail-closed cases remain FAIL;
3. `octave_alias_lower_a3_selected_a4` still reports `LOWER_OWNER_EXPLAINS_SELECTED` and includes MIDI 57 among vetoing owners;
4. the five frozen iteration-2 unexpected PASS cases all become FAIL without changing their spectra or expectations;
5. `low_scale_valid_harmonic_a4` passes;
6. both new broadband-noise scale controls fail;
7. iteration 3 never promotes any case for which iteration 2 returns `passed:false`;
8. every iteration-3 PASS has finite `candidateEvidenceFraction >= 0.10`;
9. every rejection produced by the new guard has finite `candidateEvidenceFraction < 0.10` and exact status `INSUFFICIENT_CANDIDATE_EVIDENCE_SIGNIFICANCE`;
10. the frozen iteration-1/iteration-2 modules, tests, PREs and results remain byte-identical;
11. frozen V6/V2, all workflows, `songsterr_pipeline/**`, and all closed-line files remain unchanged;
12. no Basic Pitch, model/Demucs inference, V6 correctness, real-media loader, network client, subprocess, workflow API, dataset access, candidate payload, protected-song access, physical capture/calibration, or heavy-compute path is imported or executed;
13. the complete 34-fixture suite is evaluated three times in one process and canonical decision/diagnostic output is byte-identical across all three repetitions;
14. the PRE-to-complete-pair compare contains exactly the two new iteration-3 Python files before execution.

There is no xfail, partial PASS, rescue rerun, post-result fixture exception, threshold search, or expectation change. Any mismatch freezes iteration 3 as FAIL.

## 10. IMPLEMENTATION / EXECUTION ORDER

After this PRE commit exists:

1. create only `physical_template_plausibility_v3_iteration3.py` and `test_physical_template_plausibility_v3_iteration3.py`;
2. the new module imports iteration 2 read-only and adds only the evidence-significance guard defined above;
3. commit both first versions before observing any iteration-3 synthetic result;
4. compare the PRE commit to the complete pair and verify exactly those two files changed;
5. verify forbidden imports/I/O are absent;
6. materialize the exact committed frozen dependencies and iteration-3 pair into an isolated local execution directory and verify Git blob identity;
7. execute only `python3 test_physical_template_plausibility_v3_iteration3.py`;
8. record the complete first-run fixture inventory and frozen PASS/FAIL in `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT_ITERATION3.md`;
9. update `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` at each meaningful state transition;
10. if any gate fails, stop iteration 3. Any revision requires a new prospective iteration PRE before new code or execution.

## 11. AUTHORIZATION AFTER ITERATION 3

Even a complete synthetic PASS does not authorize editing frozen V6/V2, running Basic Pitch, opening real candidate media, dispatching workflows, or performing any real correctness evaluation. Any integration or real-evaluation successor requires its own prospectively frozen PRE and explicit authorization consistent with the main current-state checkpoint.
