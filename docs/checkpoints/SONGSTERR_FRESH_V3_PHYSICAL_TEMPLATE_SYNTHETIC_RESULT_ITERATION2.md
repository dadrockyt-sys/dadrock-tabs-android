# SONGSTERR FRESH V3 PHYSICAL-TEMPLATE SYNTHETIC RESULT — ITERATION 2

Status: **FROZEN FAIL**
Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## 1. PROSPECTIVE PRE / IMPLEMENTATION IDENTITY

Iteration-2 PRE:

- path: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE_ITERATION2.md`
- frozen commit: `b2821f8690bea49783071ead87e69424fd63c787`
- PRE parent head: `8593676ae85b8fa692ffe8a03f9906591b5bce02`

First committed iteration-2 implementation/test pair:

- wrapper commit: `0587daa4cd1055255fb394939af2162e20b80be4`
- complete pair head: `4d69b7bc20637507c3a9167a5fb9c5ad498773ca`
- wrapper path: `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration2.py`
- wrapper Git blob: `7090e17baff60f91700a760f617e905ff53484ab`
- test path: `scripts/songsterr-fresh/test_physical_template_plausibility_v3_iteration2.py`
- test Git blob: `eefe00346a94e8f0ed433ac916352a4b2e9331c5`
- frozen iteration-1 base module remained Git blob `45b8f3b66df7500824071489205a732dfe05d759`

The pre-execution compare `b2821f8690bea49783071ead87e69424fd63c787..4d69b7bc20637507c3a9167a5fb9c5ad498773ca` contained exactly the two new iteration-2 Python files and no other changes.

## 2. EXECUTION INTEGRITY

Before execution, the isolated local files were hashed using Git blob semantics and exactly matched the committed blobs:

- base iteration-1 module -> `45b8f3b66df7500824071489205a732dfe05d759`
- iteration-2 wrapper -> `7090e17baff60f91700a760f617e905ff53484ab`
- iteration-2 test -> `eefe00346a94e8f0ed433ac916352a4b2e9331c5`

The only synthetic command executed for iteration 2 was:

`python3 test_physical_template_plausibility_v3_iteration2.py`

The test evaluated the complete fixture inventory three times in the same process before deciding overall PASS/FAIL. No GitHub workflow, Basic Pitch inference, V6 classifier/correctness job, real media, candidate payload, network fetch, subprocess from the research code, protected song, heavy-compute workflow, physical capture/calibration, V143/Gomyway, GOAT/reference, GuitarSet/V3, IDMT/V4, V5/FLGD, Guitar-TECHS, Production, or `main` execution occurred.

## 3. FIRST-RUN RESULT

**Overall: FAIL.**

Frozen summary emitted by the first committed test execution:

- fixture count: `31`
- repetitions: `3`
- deterministic: `true`
- mismatch count: `5`
- overall result: `FAIL`

The five complete mismatches were all unexpected PASS results:

1. `two_harmonics_only` — expected FAIL, observed `PASS`;
2. `single_peak_only` — expected FAIL, observed `PASS`;
3. `broadband_noise` — expected FAIL, observed `PASS`;
4. `nonharmonic_impulses` — expected FAIL, observed `PASS`;
5. `clip_start_insufficient_support` — expected FAIL, observed `PASS`.

All other 26 prospective cases matched their frozen expectations in the same first execution.

## 4. WHAT ITERATION 2 DID FIX SYNTHETICALLY

The original iteration-1 alias failure was not among the mismatches:

- `octave_alias_lower_a3_selected_a4` matched the frozen iteration-2 FAIL expectation and the PRE-required owner-aware status/owner check;
- `third_harmonic_owner_a3_selected_e5` did not PASS;
- `true_octave_polyphony_a3_plus_a4` matched its PASS expectation;
- `weak_lower_a3_plus_a4` matched its PASS expectation;
- inherited `true_polyphony_a3_plus_e5` and both selected notes in `true_polyphony_a4_plus_b4` matched PASS expectations.

Therefore the prospective lower-owner guard repaired the iteration-1 synthetic alias-protection defect without failing the new owner/polyphony controls. That does **not** make iteration 2 a PASS because the five inherited rejection gates above failed.

## 5. FROZEN INTERPRETATION

Iteration 2 exposed a separate weakness that iteration 1 had not reached because its fail-fast run stopped earlier: the inherited iteration-1 multi-harmonic eligibility + NNLS composite can produce PASS on sparse/non-harmonic/noise-only synthetic controls.

The owner-aware guard is downstream-only and cannot repair those cases because they already arrive as iteration-1 composite PASS and do not necessarily contain a credible lower owner. The result therefore indicates that any successor must address **candidate evidence significance / spurious detuning-anchor support** separately from lower-owner alias protection.

This is a synthetic research finding only. It is not a V6 real-world correctness result, not an EGFxSet result, not evidence about any closed dataset, and not authorization for real/model evaluation.

## 6. NO POST-RESULT TUNING OR RERUN

After observing the first-run result:

- the iteration-2 PRE was not edited;
- the iteration-2 wrapper was not edited;
- the iteration-2 test or fixtures were not edited;
- the frozen iteration-1 base module/test/PRE/result were not edited;
- no threshold, support rule, owner count, detuning grid, fixture, or expected decision was changed;
- no second iteration-2 synthetic run was used to search for a rescuing parameter or mechanism;
- no real/closed evidence was accessed.

Iteration 2 is permanently frozen as `FAIL_SYNTHETIC_SPURIOUS_SUPPORT` at pair head `4d69b7bc20637507c3a9167a5fb9c5ad498773ca` plus this result record.

## 7. NEXT PERMITTED RESEARCH STEP

Any continuation requires a **new prospective iteration-3 PRE before any code revision or synthetic execution**.

A successor may preserve the successful iteration-2 lower-owner guard while prospectively investigating a separate evidence-significance control against sparse/noise-only detuning-anchor support. Such a control must preserve all 31 iteration-2 fixture expectations, must be defined before implementation, and must not be tuned from or evaluated on closed real evidence.

No real-media/model evaluation is authorized by this result or by any future synthetic successor without a separately frozen real-evaluation PRE and explicit authorization consistent with the main current-state checkpoint.
