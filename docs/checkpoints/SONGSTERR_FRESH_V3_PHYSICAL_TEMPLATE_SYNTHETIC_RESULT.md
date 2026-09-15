# SONGSTERR FRESH V3 PHYSICAL-TEMPLATE SYNTHETIC RESULT — ITERATION 1

Status: **FROZEN FAIL**
Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## 1. FROZEN PRE / IMPLEMENTATION IDENTITY

Prospective PRE:

- path: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE.md`
- frozen commit: `0292869c1e1e1bc138f2fdff4e839326c0e5d082`
- PRE parent head: `cc924c96abf70b23e79bda60010d6c8466a1d301`

First committed implementation/test pair:

- module commit: `3f679a0f701d23e6ad15dc567e2728e89a4abd87`
- complete pair head: `f34f256ec9747d65eee6381b00b1324336e433c4`
- module path: `scripts/songsterr-fresh/physical_template_plausibility_v3.py`
- module Git blob: `45b8f3b66df7500824071489205a732dfe05d759`
- test path: `scripts/songsterr-fresh/test_physical_template_plausibility_v3.py`
- test Git blob: `71289b9ed6654199e40936a1e9ccbde5dbf0054c`

The pre-execution compare from checkpoint head `f94053e3156db25497f58918f4fd520eac7b05e7` to pair head `f34f256ec9747d65eee6381b00b1324336e433c4` contained exactly those two added research files and no other changes.

## 2. EXECUTION IDENTITY

The committed files were copied into an isolated local execution directory. Their local Git blob hashes were computed before result recording and exactly matched the committed GitHub blobs above:

- local module blob -> `45b8f3b66df7500824071489205a732dfe05d759`
- local test blob -> `71289b9ed6654199e40936a1e9ccbde5dbf0054c`

Execution environment:

- Python `3.13.5`
- NumPy `2.3.5`
- SciPy `1.17.0`

A syntax-only `py_compile` of the frozen module succeeded after both first versions were committed and before the synthetic fixture execution. No fixture result was observed before the complete committed pair existed.

The first synthetic execution was only:

`python3 test_physical_template_plausibility_v3.py`

No GitHub workflow was triggered for this test. No Basic Pitch inference, V6 classifier/correctness execution, repository media access, real candidate payload, network fetch, protected-song execution, heavy-compute workflow, physical capture/calibration, V143/Gomyway, GOAT/reference, GuitarSet/V3, IDMT/V4, V5/FLGD, or Guitar-TECHS execution occurred.

## 3. FIRST-RUN RESULT

**Overall: FAIL.**

The test is fail-fast. All prospective PASS cases reached before the alias section had passed their assertions, including the strong-fundamental, weak-fundamental, zero-fundamental, clip-start-post-only support, true-polyphony cases, and the frozen nine-case timbre/detuning matrix.

The first failing immutable gate was:

- fixture: `octave_alias_lower_a3_selected_a4`
- frozen fixture source: only MIDI 57 / A3 harmonic series with amplitudes `[1.00, 0.60, 0.40, 0.30, 0.20, 0.15]`, selected MIDI 69 / A4
- frozen expectation: composite FAIL
- observed assertion outcome: composite returned PASS
- exact fail-fast assertion: `octave_alias_lower_a3_selected_a4: composite must FAIL`

The process terminated at that assertion. Later FAIL fixtures and fail-closed input gates were therefore not used to revise, rescue, or reinterpret iteration 1.

## 4. FROZEN INTERPRETATION

Iteration 1 demonstrated that the prospective multi-harmonic eligibility rule can admit the selected octave-alias candidate strongly enough that the copied unchanged `necessityFraction >= 0.01` concept did **not** by itself preserve the frozen octave/lower-owner protection on this prospective synthetic control.

That violates immutable PRE acceptance gates 1–3. Therefore iteration 1 is frozen as FAIL regardless of the earlier passing synthetic cases.

This is a synthetic research failure only. It is not a V6 real-world correctness result, not an EGFxSet result, not evidence about any closed dataset, and not authorization to modify frozen V6 or run real/model media.

## 5. NO POST-RESULT TUNING

After observing the failure:

- the iteration-1 PRE was not edited;
- the iteration-1 module was not edited;
- the iteration-1 test/fixtures were not edited;
- no threshold, detuning grid, support rule, template weight, necessity threshold, or expected result was changed;
- no second iteration-1 synthetic run was used to search for a rescuing parameter;
- no closed real evidence was accessed.

Iteration 1 remains immutable at pair head `f34f256ec9747d65eee6381b00b1324336e433c4` plus this result record.

## 6. NEXT PERMITTED RESEARCH STEP

Any revision must be a **new prospective iteration** frozen before its new implementation or execution. A successor may investigate an explicit owner-aware / subharmonic-explanation protection, but it must preserve true polyphony and the frozen necessity concept and must define its algorithm, fixtures and gates in a new PRE before code changes.

No real-media/model evaluation is authorized by this FAIL or by any future synthetic successor without a separate real-evaluation PRE and explicit authorization.
