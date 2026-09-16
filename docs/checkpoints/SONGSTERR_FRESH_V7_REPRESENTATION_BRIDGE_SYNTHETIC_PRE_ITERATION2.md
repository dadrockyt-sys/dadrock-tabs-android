# PRE — Songsterr Fresh V7 Representation Bridge Synthetic Iteration 2

Status: **PROSPECTIVE / FROZEN ON THIS COMMIT**
Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Authority: user instruction `Let's wire this better please 🙏`

## 1. Frozen input result

Iteration 1 is permanently frozen as:

`FAIL_SYNTHETIC_REPRESENTATION_BRIDGE_SINGLE_BIN_SPARSIFICATION`

Result checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_V7_REPRESENTATION_BRIDGE_SYNTHETIC_RESULT.md`

Frozen result commit:
`d2eb412bec5bcf920a397b2d7e69642464497320`

Iteration-1 facts used to motivate this PRE, and only these facts:

- geometry-derived ±8-bin leakage collapse repaired the original broad-Hann-lobe support mismatch for most frozen V6 audio fixtures;
- 18/23 frozen V6 audio expectations matched;
- all bridge structural invariants passed;
- untouched frozen V3 iteration-3 suite remained 34/34 PASS;
- five V6-audio seam mismatches remained:
  - `clean_low_m40` -> `REDUCED_DICTIONARY_EMPTY` after only 6 positive bins survived;
  - `selected64_enters_over_existing60` -> `FAIL_NECESSITY`;
  - `simultaneous_dyad_sel60` -> unexpected PASS;
  - `simultaneous_triad_sel60` -> `FAIL_NECESSITY`;
  - `reattack_m64` -> `SELECTED_TEMPLATE_INELIGIBLE`.

Iteration 1 may not be edited or rerun.

## 2. Iteration-2 hypothesis

The iteration-1 bridge removed deterministic Hann leakage but collapsed every retained physical spectral lobe to exactly one bin. Frozen V3 does not model a physical harmonic as an exact delta: its candidate support search already uses `PEAK_BIN_RADIUS = 1`, i.e. the center bin plus its immediate neighbor on each side.

**Iteration-2 hypothesis:** preserve the same prospectively justified Hann main-lobe separation radius (`8` zero-padded bins), but retain a narrow **original-amplitude peak band** of ±1 bin around every deterministic local maximum instead of retaining only the center bin.

The ±1 half-width is not tuned from iteration-1 outcomes. It is inherited directly from frozen V3's existing `PEAK_BIN_RADIUS = 1` representation assumption.

The bridge therefore maps:

- raw frozen V6 Hann-lobe innovation;
- to deterministic local-max centers using the same frozen ±8 geometry;
- then retains only the exact original input amplitudes at center-1, center, center+1;
- all other bins are zero.

No energy may be invented, boosted, shifted, interpolated or normalized.

## 3. Frozen constants / dependency contract

Iteration 2 must fail closed unless all of the following frozen dependencies remain exact:

- V6 contract/version unchanged;
- V6 `FRAME_SAMPLES == 2048`;
- V6 `FFT_SIZE == 8192`;
- zero-padding factor `4`;
- Hann first-null native half-width `2` bins;
- lobe suppression radius `2 * 4 = 8` bins;
- frozen V3 base `PEAK_BIN_RADIUS == 1`.

Iteration 2 may import these constants read-only; it may not redefine them to different values.

## 4. Bridge contract

The new bridge must:

1. accept only a one-dimensional finite nonnegative vector of length `4097`;
2. identify deterministic positive local maxima exactly as iteration 1: first maximum in clipped ±8-bin neighborhood wins ties;
3. for every retained center, copy the original input values at offsets `-1, 0, +1` when in bounds;
4. never write a value larger than or different from the corresponding input amplitude;
5. never move energy to another bin;
6. zero every bin not inside a retained center's ±1 peak band;
7. preserve exact FFT-grid length and indexing;
8. preserve zero input as zero;
9. preserve positive scale equivariance: multiplying input by finite positive scalar must preserve retained-bin identities and scale retained amplitudes by the same scalar;
10. fail closed on malformed rank, length, negative or nonfinite input;
11. perform no file/network/subprocess/model/GPU/repository/media I/O in the bridge module itself;
12. inspect no selected MIDI, confidence, expected class, dataset identity, reference truth or EGFxSet value.

## 5. Frozen/read-only files

Read-only throughout iteration 2:

- all iteration-1 bridge/PRE/result files;
- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`;
- `scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`;
- all frozen V3 base/iteration-2/iteration-3 modules and tests;
- frozen `scripts/songsterr-fresh/onset_birth_corroboration_v7.py`;
- all frozen V2/clip-start files;
- all prior V3/V7 PRE/result checkpoints;
- `songsterr_pipeline/**`;
- every closed line, `main`, Production and archived V143/Gomyway.

No frozen V3/V6 threshold changes are permitted.

## 6. Prospective write boundary

Iteration 2 may create/change only:

- `scripts/songsterr-fresh/v6_innovation_peak_band_bridge_v2.py`;
- `scripts/songsterr-fresh/test_v6_innovation_peak_band_bridge_v2.py`;
- `.github/workflows/songsterr-v7-representation-bridge-synthetic-iteration2-one-shot.yml` if repository execution requires a runner;
- `docs/checkpoints/SONGSTERR_FRESH_V7_REPRESENTATION_BRIDGE_SYNTHETIC_RESULT_ITERATION2.md`;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` for state-only updates.

Any other path requires a new prospective PRE.

## 7. Frozen synthetic gates

### 7.1 Complete frozen V6 audio population

All 23 expectations from frozen `v6_onset_birth_synthetic_fixtures.json` remain unchanged and must all match through:

`frozen V6 synthetic audio -> frozen V6 onset innovation -> iteration-2 peak-band bridge -> frozen V3 iteration-3 composite`.

No fixture may be removed, renamed, reweighted or reclassified.

Every bridge-path V3 PASS must retain finite:

- `necessityFraction >= 0.01`;
- `candidateEvidenceFraction >= 0.10`.

Insufficient V6 audio/context cases remain insufficient without fabricated context or energy.

### 7.2 Untouched frozen V3 suite

`python scripts/songsterr-fresh/test_physical_template_plausibility_v3_iteration3.py`

must remain exactly:

- 34 fixtures;
- 3 repetitions;
- deterministic;
- 0 mismatches;
- PASS.

The iteration-2 bridge is not inserted into those direct-spectrum fixtures.

### 7.3 Structural bridge gates

Before execution, freeze tests for:

- zero input -> zero output;
- isolated peak retains original amplitudes only in its available ±1 band;
- 4x-zero-padded Hann main lobe produces exactly one retained center and one ±1 peak band inside the frozen ±8 main-lobe neighborhood;
- two local maxima more than 8 bins apart retain two independent ±1 bands;
- weaker maximum inside stronger maximum's ±8 neighborhood is not a center and therefore does not create a band;
- equal local maxima within one neighborhood resolve to lower-bin center;
- no output bin exceeds or differs from input at the same index;
- output nonzero indices are a subset of input nonzero indices;
- positive scaling preserves retained indices and amplitudes proportionally;
- malformed rank/length/negative/nonfinite input fails closed.

### 7.4 Determinism

Run the complete 23-fixture bridge population three times in-process and require identical decisions and diagnostics.

## 8. First-run policy

Before first execution:

1. commit the bridge/test pair without observing output;
2. verify PRE-to-pair delta contains exactly the two allowed Python files;
3. record exact Git blobs;
4. perform static forbidden import/I/O review;
5. if a workflow is required, add only the prospectively allowed self-scoped synthetic workflow, triggered solely by its own YAML path;
6. run the bridge suite and untouched V3 suite exactly once in the same workflow attempt;
7. freeze the first result exactly as observed.

No same-iteration rescue rerun, code repair, support-width change, radius change, fixture change, expected-decision change or threshold change after first output. Failure requires a new prospective iteration PRE.

## 9. Explicit prohibitions

No EGFxSet or other real media; no prior Basic Pitch artifact; no Basic Pitch/Demucs/model inference; no real correctness run; no dataset or protected-song access; no AG-PT/rejected-holdout reopening; no learned/tuned parameters; no MIDI/dataset special case; no physical capture/calibration; no `songsterr_pipeline/**`, `main`, Production, GOAT/reference, reserved GFN or archived V143/Gomyway work.

## 10. Authority after result

A PASS would establish only a synthetic representation seam for the frozen V6/V3 evidence geometry. It would not switch any production route or authorize any real/model evaluation. A later successor integration requires a new prospective integration PRE. Any future real evaluation requires a separate real-evaluation PRE plus fresh explicit user authorization.