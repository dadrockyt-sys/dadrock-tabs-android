# Songsterr Fresh — FLGD V5 Scoring Numerical Amendment

Status: **FROZEN BEFORE ANY FLGD BASIC PITCH / V5 CORRECTNESS RESULT**

Date: 2026-09-12 America/Toronto

The final scoring preregistration defines inclusive thresholds:
- onset delta <= 0.050 seconds;
- pitch delta <= 50 cents.

To preserve those inclusive mathematical boundaries under IEEE-754 binary64 arithmetic, the implementation must evaluate each as:

`delta < limit OR math.isclose(delta, limit, rel_tol=0.0, abs_tol=1e-12)`

The `1e-12` value is numerical representation tolerance only. It is not a tunable scoring margin and may not be changed after correctness results.

No FLGD Basic Pitch/V5 correctness result existed when this amendment was frozen.
