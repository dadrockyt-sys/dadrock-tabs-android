# Songsterr Fresh — IDMT V4 Stage B Numerical Comparison Amendment

Status: **PRE-RESULT IMPLEMENTATION AMENDMENT / SCORING THRESHOLDS UNCHANGED**

Recorded: 2026-09-11 America/Toronto

Branch: `songsterr-fresh-pipeline-v1`

## Trigger

The first controlled-only CI self-test of the IDMT V4 external-validation harness failed before any real IDMT inference or correctness result.

The failing synthetic assertion represented an onset exactly 50 ms from a reference (`1.05 - 1.0`). IEEE-754 binary64 represents that subtraction as slightly greater than decimal `0.050`, causing direct `delta <= 0.050` code to reject a boundary case even though the preregistered rule explicitly says the 50-ms boundary is inclusive.

No IDMT Basic Pitch output, V4 classification, estimate/reference correctness result, precision, recall, Wilson bound or protected-song result was viewed before this amendment.

## Frozen correction

The formal matching thresholds remain exactly:
- onset tolerance: absolute difference **<= 0.050 seconds**;
- pitch tolerance: absolute difference **<= 50 cents**.

Implementation of those inclusive comparisons must use:

`delta < limit OR math.isclose(delta, limit, rel_tol=0.0, abs_tol=1e-12)`

for both onset and pitch-difference boundary checks.

The `1e-12` value is a numerical representation guard only. It MUST NOT be described or used as a substantive widening/tuning of the 50-ms or 50-cent matching rule.

## Official entrypoint

The official scoring entrypoint is:

`scripts/songsterr-fresh/run_external_idmt_v4_validation.py`

It loads the frozen core harness `external_idmt_v4_validation.py`, replaces only its `valid_match` function with the inclusive numerical comparator above, adds its own SHA-256 to implementation provenance, then invokes the otherwise unchanged frozen core harness.

No other core function, threshold, gate, V4 constant, Basic Pitch setting, manifest identity or corpus rule may be changed by the adapter.

## Policy boundary

This amendment does not authorize or change product authority:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- protected song remains embargoed
- real IDMT correctness execution remains blocked until controlled CI on the amended official entrypoint is green.
