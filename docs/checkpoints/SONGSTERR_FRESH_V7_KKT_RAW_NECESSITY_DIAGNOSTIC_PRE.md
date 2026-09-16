# SONGSTERR FRESH V7 KKT RAW-NECESSITY DIAGNOSTIC PRE

Status: **PROSPECTIVE / FROZEN BEFORE IMPLEMENTATION OR OUTPUT**
Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
PRE parent head: `35a6dfde10254c79219bb7af5e075b652c917c96`

## 1. PURPOSE AND NON-AUTHORITY

This PRE opens one synthetic-only, measurement-only line after the frozen composition-principle theory review.

The narrow question is:

> Can the broad all-49 fixed-feature raw NNLS problem assign the selected MIDI a mathematically defined **strict-necessity certificate** without transporting historical `0.01`, choosing a new magnitude cutoff, or using rank/top-K semantics?

This PRE does **not** define a final successor classifier. It does not resolve reattack temporal/support representation. It does not authorize real/media/model execution, Basic Pitch, V6/V7 real correctness, EGFxSet, AG-PT/rejected holdouts, protected-song access, physical capture/calibration, `songsterr_pipeline/**`, `main`, Production, GOAT/reference scoring, reserved GFN data, or archived V143/Gomyway.

Global authority remains false/0/false exactly as frozen in `SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`.

## 2. EX-ANTE MATHEMATICAL PRINCIPLE

For a fixed observation vector `y` and nonnegative template dictionary `A`, NNLS solves

`minimize 0.5 * ||A x - y||_2^2 subject to x >= 0`.

This is a convex problem. Classical Lawson-Hanson NNLS and SciPy `scipy.optimize.nnls` are active-set methods based on the Karush-Kuhn-Tucker (KKT) optimality conditions.

Let selected raw column `a_s` be omitted and let `A_-s` be the remaining 48 all-playable columns. Let `x_-s` be the reduced NNLS solution and

`r = y - A_-s x_-s`.

Using the residual-correlation sign convention

`c_j = a_j^T r`,

the exact reduced optimum satisfies:

- `c_j = 0` for a column with positive coefficient;
- `c_j <= 0` for a column at coefficient zero.

For the omitted selected column, if

`a_s^T r > 0`,

then the reduced solution violates the full problem's KKT condition in the selected positive direction. A sufficiently small positive selected coefficient decreases the squared residual. Therefore the selected column is a **strict descent direction**, and the full 49-column optimum must be strictly better than the reduced 48-column optimum.

This zero boundary follows from convex NNLS geometry. It is not a learned, fitted, or fixture-selected raw-necessity magnitude threshold.

References for the mathematical mechanism:

- C. Lawson and R. J. Hanson, *Solving Least Squares Problems*, SIAM, DOI `10.1137/1.9781611971217`.
- SciPy `optimize.nnls` documentation: NNLS is a convex constrained least-squares problem and the implementation uses an active-set method that solves KKT conditions.

## 3. FROZEN RAW REPRESENTATION

This diagnostic must use the already-frozen broad raw measurement representation without modification:

1. frozen V6 raw onset innovation;
2. every playable MIDI `40..88` as a structurally constructible gate-free competition column;
3. gate-free template geometry exactly from `v7_gate_free_competition_diagnostics_v1.py`;
4. one fixed feature universe equal to the sorted union of all 49 gate-free template bins;
5. one common observed vector sampled from raw onset innovation on that fixed universe;
6. one full 49-column NNLS fit and one selected-omitted 48-column NNLS fit.

No historical V6 `0.20` ratio is an all-49 competition admission gate. Historical raw necessity `0.01` is reference-only and MUST NOT be applied.

## 4. PROSPECTIVE NUMERICAL CERTIFICATE

Exact KKT uses a zero boundary, but finite-precision solver and arithmetic error must not turn roundoff into scientific evidence. This PRE therefore freezes a self-calibrating numerical certificate; it introduces no empirical tolerance constant.

### 4.1 Unit roundoff

Use IEEE-754 float64 unit roundoff

`u = np.finfo(np.float64).eps / 2`.

For integer `k` with `k*u < 1`, define the standard forward-error factor

`gamma(k) = (k*u) / (1 - k*u)`.

No multiplier fitted from fixture outcomes may be added.

### 4.2 Recomputed reduced residual and row error bound

After SciPy NNLS returns reduced coefficients `x`, recompute each fitted row with deterministic `math.fsum` over float64 products:

`p_i = fsum_j A_ij * x_j`

`r_i = y_i - p_i`.

Let

`s_i = fsum_j abs(A_ij * x_j)`.

Freeze the conservative row arithmetic bound

`b_pred_i = gamma(n) * s_i`

where `n = 48` reduced columns, and

`b_r_i = b_pred_i + u * (abs(y_i) + abs(p_i) + b_pred_i)`.

This is an arithmetic bound only. Solver stationarity error is handled separately below.

### 4.3 Per-column correlation interval

For every full-dictionary column `a_j`, calculate with deterministic `math.fsum`:

`c_j = fsum_i a_ij * r_i`

and

`t_j = fsum_i abs(a_ij * r_i)`.

Freeze the correlation arithmetic bound

`b_c_j = gamma(m) * t_j + fsum_i abs(a_ij) * b_r_i`

where `m` is the fixed feature-row count.

Let column scale be

`q_j = sqrt(fsum_i a_ij^2)`.

Every column scale must be finite and strictly positive.

### 4.4 Reduced-solver KKT stationarity floor

For each of the 48 included columns, use its reduced NNLS coefficient `x_j`.

Its conservative normalized KKT-defect upper bound is:

- if `x_j > 0`: `(abs(c_j) + b_c_j) / q_j`;
- if `x_j == 0`: `max(0, c_j + b_c_j) / q_j`.

Define

`reducedKktDefectFloor = max(defect_j over the 48 included columns)`.

This floor is not a scientific threshold. It is the reduced solver's own observed stationarity-defect ceiling under the same matrix, residual and arithmetic bounds.

### 4.5 Selected omitted-direction lower bound

For omitted selected column `s`, define

`selectedCorrelationLowerBound = (c_s - b_c_s) / q_s`.

The selected raw column is **KKT-certified strictly necessary** only when

`selectedCorrelationLowerBound > max(0, reducedKktDefectFloor)`.

Otherwise strict raw necessity is **not certified**.

No `0.01`, no new raw magnitude threshold, no rank, no top-K, no maximum-only rule and no per-MIDI exception is permitted.

### 4.6 Mechanical consistency checks

When strict raw necessity is certified, the same diagnostic must also observe:

- finite full and reduced NNLS solutions;
- selected full-fit coefficient `> 0`;
- selected-omitted residual strictly greater than full residual.

A contradiction is a mechanical diagnostic error/no-decision, not a rescue threshold opportunity.

The historical descriptive raw necessity fraction may be emitted only as

`(withoutResidual - fullResidual) / featureEnergy`

for cross-checking frozen measurement lineage. It has no acceptance cutoff in this PRE.

## 5. NEW MATRIX-LEVEL SYNTHETIC CONTROLS

Before any audio-fixture diagnostic output is observed, the test harness must freeze and execute these deterministic NNLS geometry controls. They test the KKT principle itself, not guitar correctness.

All columns are finite, nonnegative and normalized or explicitly normalized before evaluation.

1. `unique_selected_direction` — reduced columns explain orthogonal components while the selected column alone explains one remaining positive component. Expected: **certified true**.
2. `selected_absent` — the observation has no component in the selected direction. Expected: **certified false**.
3. `duplicate_selected_column` — an included column is exactly identical to the selected column and already explains that component. Expected: **certified false**.
4. `selected_in_cone_of_others` — the selected column is a nonnegative combination of included columns and the reduced cone explains the observation exactly. Expected: **certified false**.
5. `weak_unique_selected_direction` — selected contributes only `1e-8` on an otherwise orthogonal exact geometry. Expected: **certified true**, demonstrating that scientific magnitude is not being thresholded; only numerical certifiability matters.
6. `zero_observation` — no positive residual direction exists. Expected: **certified false**.

The matrix controls must run three times in-process and canonical diagnostics must be byte-identical.

No control may be changed after first output to rescue the attempt.

## 6. FROZEN 23-FIXTURE AUDIO DIAGNOSTIC

The exact existing V6 synthetic fixture manifest is read-only input:

`scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json`
blob `a6c3d99d47c529db3c3c5e4af544d13f21b179aa`.

The diagnostic must evaluate the exact 23 fixture waveforms using the already-frozen deterministic synthesis semantics used by the existing diagnostic lineage.

This PRE deliberately freezes **no new final PASS/FAIL expectations from those 23 fixture outcomes**. Their purpose in this attempt is measurement and lineage consistency only.

For each fixture, persist when onset evidence is available:

- selected MIDI;
- support-valid status and existing support/protection diagnostics where mechanically available;
- fixed feature-bin count/energy;
- full 49-column coefficient for the selected MIDI;
- full residual;
- selected-omitted residual;
- descriptive historical raw necessity fraction;
- selected raw correlation and arithmetic bound;
- selected normalized lower bound;
- reduced KKT defect floor;
- `kktCertifiedStrictRawNecessity` boolean;
- consistency-check status.

Unavailable onset/context cases remain unavailable; no measurement may be fabricated.

The attempt defines:

- `finalDecisionDefined:false`;
- `rawMagnitudeThresholdDefined:false`;
- `rankCutoffDefined:false`;
- `historicalNecessityThresholdApplied:false`;
- `reattackFallbackDefined:false`.

## 7. FROZEN DEPENDENCIES / READ-ONLY LINEAGE

At minimum the executable pair must pin and verify these frozen dependencies before execution:

- `scripts/songsterr-fresh/onset_birth_corroboration_v6.py` blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`;
- `scripts/songsterr-fresh/v6_onset_birth_synthetic_fixtures.json` blob `a6c3d99d47c529db3c3c5e4af544d13f21b179aa`;
- `scripts/songsterr-fresh/physical_template_plausibility_v3.py` blob `45b8f3b66df7500824071489205a732dfe05d759`;
- `scripts/songsterr-fresh/v6_innovation_peak_band_bridge_v2.py` blob `402aa23f3f1821c4e5c45ccf7f170b542d76a453`;
- `scripts/songsterr-fresh/v7_gate_free_competition_diagnostics_v1.py` blob `08eb9e945bf2cdf33e640cf7b3349ae075002846`;
- `scripts/songsterr-fresh/v7_support_conditioned_raw_necessity_landscape_v1.py` blob `25a8f2c943d97730acf8fdc521c5ad1c3e8f8ea1`.

Frozen V3 iteration-3 regression remains 34 fixtures ×3 and must still PASS unchanged in the one-shot workflow.

All existing V6/V3/V7 modules, tests, PREs/results and one-shot outputs remain read-only history.

## 8. PROSPECTIVE WRITE BOUNDARY

After this PRE commit exists, this attempt may create/change only:

- `scripts/songsterr-fresh/v7_kkt_raw_necessity_diagnostics_v1.py` — new measurement-only module;
- `scripts/songsterr-fresh/test_v7_kkt_raw_necessity_diagnostics_v1.py` — new deterministic matrix/audio diagnostic harness;
- `.github/workflows/songsterr-v7-kkt-raw-necessity-diagnostic-one-shot.yml` — self-scoped first-run workflow;
- `docs/checkpoints/SONGSTERR_FRESH_V7_KKT_RAW_NECESSITY_DIAGNOSTIC_RESULT.md` — immutable attempt-1 result record;
- `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` — state transitions only.

No other path is authorized by this PRE.

## 9. ONE-SHOT EXECUTION CONTRACT

Before first output:

1. create the module and test only;
2. commit both first versions;
3. compare this PRE commit to the pair head and require exactly those two Python files;
4. pin their exact Git blobs;
5. update CURRENT_STATE to record the frozen unexecuted pair;
6. create the self-scoped workflow;
7. the workflow must use Python `3.10.21`, NumPy `1.26.4`, SciPy `1.15.3`;
8. static guard must reject network/model/media/subprocess/repository-mutation code paths;
9. run the new diagnostic exactly once plus the untouched V3 iteration-3 regression exactly once;
10. upload artifact `songsterr-fresh-v7-kkt-raw-necessity-diagnostic` containing `kkt-raw-necessity-diagnostic.json` and `v3-regression.txt` even when a diagnostic gate fails;
11. attempt 1 is authoritative; no rescue rerun or post-output code/criterion adjustment.

If the first attempt reveals a mechanical implementation defect, freeze it as such. Any revised executable attempt requires a new prospective PRE before code changes.

## 10. INTERPRETATION BOUNDARY

A successful attempt can establish only that broad raw evidence has a cutoff-free, KKT-derived strict-necessity certificate under the frozen all-49 fixed-feature representation.

It cannot by itself:

- define the final successor classifier;
- determine whether support/protection/KKT measurements should be composed conjunctively for delivery;
- repair or bypass reattack support/temporal representation;
- authorize historical `0.01` on the new raw fit;
- authorize a rank rule;
- authorize any real/media/model evaluation;
- advance model validation or customer eligibility.

Any later final composition requires a new prospective PRE after this result is frozen.

Archived V143/Gomyway remains untouched.