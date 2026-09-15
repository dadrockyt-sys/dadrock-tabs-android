# SONGSTERR FRESH V3 PHYSICAL-TEMPLATE SYNTHETIC PRE — ITERATION 2

Status: **PROSPECTIVE / FROZEN ON FIRST COMMIT**
Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
PRE parent head: `8593676ae85b8fa692ffe8a03f9906591b5bce02`

This PRE is frozen before any iteration-2 implementation exists and before any iteration-2 synthetic result is observed. Iteration 1 remains immutable history and is not patched or rerun.

## 1. MOTIVATION FROM FROZEN ITERATION 1

Iteration-1 PRE: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE.md`, frozen commit `0292869c1e1e1bc138f2fdff4e839326c0e5d082`.

Iteration-1 result: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT.md`, frozen FAIL commit `6a6965730250f2000cc480ede2ed3d2638b0df44`.

The first committed iteration-1 implementation/test pair at head `f34f256ec9747d65eee6381b00b1324336e433c4` failed the prospective octave-alias gate: a pure MIDI-57 / A3 harmonic series produced a composite PASS when MIDI 69 / A4 was selected. No iteration-1 code, fixture, constant, expectation, or PRE was changed after that result.

Iteration 2 addresses only that newly established synthetic weakness: a selected higher pitch may be explainable as a harmonic subset of a credible lower owner. The repair must preserve genuine polyphony, weak-fundamental acceptance, the iteration-1 multi-harmonic eligibility rule, and the unchanged NNLS necessity concept.

This is synthetic research only. It does not authorize real-media/model evaluation, frozen V6 modification, Basic Pitch inference, EGFxSet, AG-PT-set payload access, rejected holdouts, protected songs, physical capture/calibration, V143/Gomyway, GOAT/reference, GuitarSet/V3, IDMT/V4, V5/FLGD, Guitar-TECHS, Production, or `main`.

## 2. WORKFLOW ISOLATION RECHECK

The authoritative automatic-trigger audit was recorded at commit `cc924c96abf70b23e79bda60010d6c8466a1d301`.

Before this PRE was written, compare `cc924c96abf70b23e79bda60010d6c8466a1d301..8593676ae85b8fa692ffe8a03f9906591b5bce02` showed changes only under `docs/checkpoints/` and the two iteration-1 `scripts/songsterr-fresh/` files. No `.github/workflows` file changed. The audited automatic set still contains no catch-all `scripts/songsterr-fresh/**` push path.

No workflow file may be created or edited by iteration 2.

## 3. EXACT ITERATION-2 WRITE BOUNDARY

After this PRE is frozen, only these files may be created or changed for iteration 2:

- `scripts/songsterr-fresh/physical_template_plausibility_v3_iteration2.py` — new owner-aware wrapper research module;
- `scripts/songsterr-fresh/test_physical_template_plausibility_v3_iteration2.py` — new deterministic synthetic harness;
- `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT_ITERATION2.md` — result record after first committed test execution;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` — state-transition record only.

This PRE is immutable after its creation commit.

Iteration-1 files are frozen/read-only inputs and may not be edited:

- `scripts/songsterr-fresh/physical_template_plausibility_v3.py`, Git blob `45b8f3b66df7500824071489205a732dfe05d759`;
- `scripts/songsterr-fresh/test_physical_template_plausibility_v3.py`, Git blob `71289b9ed6654199e40936a1e9ccbde5dbf0054c`;
- iteration-1 PRE and result checkpoint.

Frozen V6/V2, all workflow files, `songsterr_pipeline/**`, and all closed research lines remain read-only.

## 4. INHERITED ITERATION-1 MECHANISM — UNCHANGED

Iteration 2 must import the frozen iteration-1 research module as a read-only dependency and must not duplicate or alter its constants or candidate-eligibility algorithm.

Inherited unchanged behavior includes:

- 44.1 kHz / FFT 8192 frequency grid;
- MIDI 40–88;
- six harmonics;
- ±1-bin harmonic peak search;
- -40..+40 cent detuning anchors at 5-cent spacing;
- ±6-bin local background with ±1-bin peak exclusion;
- local SNR multiplier 3.0;
- relative strongest-harmonic support floor 0.10;
- minimum 3 supported harmonics;
- minimum weighted harmonic coverage 0.35;
- minimum innovation L2 norm `1e-6`;
- L2-normalized `1/h` template weights;
- shared NNLS full/reduced necessity calculation;
- positive selected coefficient plus `necessityFraction >= 0.01`.

Iteration 2 may not change the frozen historical V6 `0.20` threshold because V3 does not use that ratio as an eligibility threshold at all. The ratio may remain diagnostic only.

## 5. PROSPECTIVE ITERATION-2 HYPOTHESIS

The iteration-1 alias failure is not necessarily evidence that the selected higher candidate lacks harmonic coherence; it is evidence that harmonic coherence plus global leave-one-out necessity can confuse a harmonic subset of a real lower owner with an independent higher note.

A lower pitch should be allowed to veto that interpretation only when it has **owner-exclusive supported harmonics** that establish it independently of the selected higher pitch. Conversely, a genuine simultaneous higher note should survive when it has **selected-exclusive supported harmonics** that the credible lower owner cannot explain.

Therefore iteration 2 adds a deterministic lower-owner explanation guard **after** the unchanged iteration-1 composite PASS. It does not replace, lower, or bypass iteration-1 eligibility or necessity.

## 6. FROZEN OWNER-AWARE GUARD

### 6.1 Preconditions

For selected MIDI `S`:

1. Call frozen iteration-1 `evaluate_composite_necessity(S, innovation, frequencies)`.
2. If its result is not PASS, iteration 2 returns that failure unchanged in substance and cannot promote it.
3. If it passes, build frozen iteration-1 candidate templates for every lower playable MIDI `O` in `40..S-1`.
4. Only lower candidates whose frozen iteration-1 template is `valid:true` are considered potential owners.

### 6.2 Harmonic-bin overlap

For two template harmonic bins `a` and `b`, define overlap prospectively as:

`abs(a - b) <= 1` FFT bin.

The ±1-bin overlap is fixed to the same local peak tolerance already frozen in iteration 1. It is not fitted from the failed fixture.

### 6.3 Supported exclusive evidence

Use the frozen iteration-1 template `supported` boolean associated with each harmonic bin.

For potential lower owner `O` relative to selected `S`:

- `ownerExclusiveSupportedCount`: number of **supported** owner harmonic bins that do not overlap any selected template harmonic bin;
- `selectedExclusiveSupportedCount`: number of **supported** selected harmonic bins that do not overlap any owner template harmonic bin.

Overlap comparison uses all template harmonic bins on the opposite side, not only its supported subset, so an exclusive count means the harmonic location itself is not geometrically explainable by the other pitch's six-harmonic template.

### 6.4 Credible lower owner and veto

Freeze these structural counts for iteration 2:

- minimum owner-exclusive supported harmonics for a **credible lower owner**: `2`;
- minimum selected-exclusive supported harmonics required to survive each credible owner: `2`.

For every valid lower owner candidate:

1. if `ownerExclusiveSupportedCount < 2`, it is not a credible owner and cannot veto the selected pitch;
2. if `ownerExclusiveSupportedCount >= 2` and `selectedExclusiveSupportedCount < 2`, return deterministic FAIL status `LOWER_OWNER_EXPLAINS_SELECTED` and identify that lower owner;
3. if `ownerExclusiveSupportedCount >= 2` and `selectedExclusiveSupportedCount >= 2`, that owner does not veto because both pitches have independently supported harmonic locations;
4. selected PASS requires surviving **all** credible lower owners.

No amplitude ratio, confidence score, selected MIDI special case, or real-data-derived threshold is added by this guard.

### 6.5 Composite decision order

Iteration-2 decision order is frozen as:

`iteration-1 template eligibility -> iteration-1 NNLS necessity -> iteration-2 lower-owner guard`.

Iteration 2 may turn an iteration-1 PASS into FAIL. It may never turn an iteration-1 FAIL into PASS.

## 7. SYNTHETIC FIXTURES — INHERITED GATES

Iteration 2 must recreate all iteration-1 prospective fixtures in memory with the exact same seed, spectra, amplitudes, selected MIDI values, context labels and expected PASS/FAIL decisions recorded in the iteration-1 PRE. No real audio or repository fixture file may be opened.

The inherited PASS set includes:

- strong fundamental in-clip;
- weak-fundamental bright in-clip;
- zero-fundamental upper-support in-clip;
- weak-fundamental clip-start-post-only with `syntheticPreContextUsed=false`;
- true polyphony A3 + E5, selected E5;
- true polyphony A4 + B4, each selected independently;
- the exact nine-case bright/dark/fundamental-notch × -30/0/+30-cent matrix.

The inherited FAIL set includes:

- pure A3 selected A4 octave alias;
- pure A3 selected E5 third-harmonic-owner trap;
- two-harmonics-only;
- single-peak-only;
- broadband noise;
- near silence;
- nonharmonic impulses;
- clip-start insufficient support;
- all iteration-1 fail-closed invalid-input gates.

Unlike iteration 1, the test harness must evaluate the full fixture inventory and collect every mismatch before asserting overall PASS/FAIL, so a future failure record can be complete without changing or rerunning the frozen implementation.

## 8. NEW PROSPECTIVE OWNER/POLYPHONY CONTROLS

Use deterministic background scale `0.002` and the inherited seed `730915` unless stated otherwise.

### 8.1 PASS — true octave polyphony

`true_octave_polyphony_a3_plus_a4`:

- lower MIDI 57 amplitudes `[1.00, 0.60, 0.40, 0.30, 0.20, 0.15]`;
- simultaneous selected MIDI 69 amplitudes `[0.35, 0.90, 0.65, 0.48, 0.33, 0.22]`;
- cents `0` for both;
- selected MIDI 69 must PASS iteration-2 composite.

Rationale frozen prospectively: the lower owner has independent odd/low harmonic support, but the genuine selected octave also supplies several supported harmonics above the lower owner's six-harmonic geometry.

### 8.2 PASS — weak lower owner must not veto strong selected pitch

`weak_lower_a3_plus_a4`:

- lower MIDI 57 amplitudes `[0.04, 0.04, 0.04, 0.04, 0.04, 0.04]`;
- simultaneous selected MIDI 69 amplitudes `[1.00, 0.50, 0.32, 0.22, 0.15, 0.10]`;
- cents `0` for both;
- selected MIDI 69 must PASS.

The lower candidate may acquire overlapping harmonic support from A4, but it must not veto unless at least two of its own non-overlapping harmonic locations are supported under the already-frozen iteration-1 support rule.

### 8.3 FAIL — octave alias with lower-owner evidence

The inherited `octave_alias_lower_a3_selected_a4` remains exactly the iteration-1 pure A3 fixture. Iteration-2 expected status must be `LOWER_OWNER_EXPLAINS_SELECTED`, with a credible lower owner that includes MIDI 57. Composite result must FAIL.

### 8.4 FAIL — third-harmonic alias with lower-owner evidence

The inherited `third_harmonic_owner_a3_selected_e5` remains exactly the iteration-1 pure A3 fixture selected at MIDI 76. Iteration-2 must FAIL through lower-owner explanation or an earlier inherited failure; it may not PASS.

## 9. IMMUTABLE ITERATION-2 ACCEPTANCE GATES

Iteration 2 is PASS only if all are true on the first committed implementation/test pair:

1. every inherited iteration-1 PASS fixture remains PASS;
2. every inherited iteration-1 FAIL fixture remains FAIL;
3. all inherited invalid-input cases remain deterministic fail-closed cases;
4. pure A3 selected A4 is rejected specifically by `LOWER_OWNER_EXPLAINS_SELECTED` and reports MIDI 57 among the credible vetoing owners;
5. pure A3 selected E5 does not PASS;
6. `true_octave_polyphony_a3_plus_a4` selected A4 passes;
7. `weak_lower_a3_plus_a4` selected A4 passes;
8. the existing A3 + E5 true-polyphony selected E5 fixture still passes, proving the guard is not a blanket subharmonic veto;
9. the existing A4 + B4 true-polyphony fixture passes for both selected notes;
10. iteration 2 never promotes any case for which frozen iteration-1 `evaluate_composite_necessity` returns `passed:false`;
11. the iteration-1 module/test/PRE/result blobs remain unchanged;
12. no Basic Pitch, V6 classifier, real-media loader, network client, subprocess, workflow API, dataset access, protected-song access, or closed-line code is imported or executed;
13. the full fixture suite is evaluated three times in one process and canonical decision/diagnostic output is byte-identical across all three repetitions;
14. no workflow file, frozen V6/V2 file, `songsterr_pipeline/**` file, iteration-1 file, or closed-line file changes.

There is no xfail, partial PASS, post-result fixture exception, threshold tuning, or rerun-to-rescue rule. Any mismatch freezes iteration 2 as FAIL.

## 10. IMPLEMENTATION / EXECUTION ORDER

After this PRE commit exists:

1. create only the two new iteration-2 Python files;
2. the iteration-2 module may import `physical_template_plausibility_v3.py` read-only and add only the owner-aware guard above;
3. commit both first versions before observing a synthetic fixture result;
4. compare the PRE/checkpoint head to the complete pair and verify only the two iteration-2 research files changed;
5. verify forbidden imports/I/O are absent;
6. copy or otherwise materialize the exact committed blobs into an isolated local execution directory and verify Git blob identity before result recording;
7. run only `test_physical_template_plausibility_v3_iteration2.py`;
8. record the complete first-run fixture inventory and frozen PASS/FAIL in `SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT_ITERATION2.md`;
9. update the main current-state checkpoint;
10. if any gate fails, stop iteration 2. Any revision requires iteration 3 PRE before new code or execution.

## 11. AUTHORIZATION AFTER ITERATION 2

Even a complete synthetic PASS does not authorize editing frozen V6, running Basic Pitch, opening real candidate media, or performing any real correctness evaluation. A successor integration/evaluation stage requires its own prospectively frozen PRE and whatever explicit authorization the main checkpoint requires.
