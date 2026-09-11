# Songsterr Fresh — IDMT V4 Policy Review

Status: **CLOSED / REJECTED AS ADMISSION AUTHORITY**

Recorded: 2026-09-11 America/Toronto

Branch: `songsterr-fresh-pipeline-v1`

## Inputs reviewed

This review considers only the frozen V4 method, preregistered Stage B scoring contract, numerical-boundary amendment, controlled CI, and the immutable official IDMT result recorded in:

- `docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_EXTERNAL_VALIDATION_RESULT.md`
- result artifact SHA-256 `d97ea2c7f004876fc43f6c3d2e28e4838df86a4a4c4a8bc8f8a2a98ab5e37d2c`
- execution source `ef92d873ed6cdb6b78fe06e42d0b8ffd24cce237`

No protected-song result, GuitarSet event-level error, reference tab/pro scorer, GOAT material, archived V143/Gomyway logic, duration signal, or post-result threshold sweep is part of this decision.

## Frozen acceptance criteria

Before the official IDMT run, V4 required all of the following relevant gates:
- all 568 files complete;
- at least 1000 V4-positive events;
- pooled one-sided 95% Wilson lower bound at least `0.9900`;
- dataset1 and dataset2 point precision at least `0.9500` with at least 100 positives;
- every sample-width stratum with at least 100 positives point precision at least `0.9500`;
- identity/policy guards intact.

These criteria may not be weakened after observing the result.

## Observed result

The official run completed all 568 files and produced sufficient positives, but failed multiple mandatory accuracy gates:
- V4-positive precision `0.7858880778588808`;
- one-sided 95% Wilson lower bound `0.7687844934184139` < required `0.9900`;
- dataset1 precision `0.9566563467492261` → PASS;
- dataset2 precision `0.7409126063418406` → FAIL;
- 16-bit precision `0.9515669515669516` → PASS;
- 24-bit precision `0.7409126063418406` → FAIL;
- `externalValidationPassed:false`.

Dataset1/16-bit success cannot override the pooled failure or the mandatory dataset2/24-bit failures. No voting, selective promotion, or post-hoc population split is authorized by the preregistration.

## Policy decision

**V4 is rejected as model-evidence admission authority.**

The official IDMT result is retained only as a frozen research diagnostic. V4 may not be promoted for customer-facing note admission, and the failed result may not be repaired under the same preregistration by changing thresholds, filtering datasets/events, selecting successful strata, rerunning IDMT, or retuning against observed errors.

No protected-song V4 execution is authorized because the independent external-validation gate failed first.

## Authority state after review

Remain unchanged and fail-closed:
- `modelValidationComplete:false`
- customer-eligible events: `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research paused
- persistent Policy C remains `UNENROLLED`

The following remain false:
- customer promotion from V4
- duration resumption
- protected-song V4 evaluation
- use of V4 as admission authority

## Successor boundary

No V5 or other successor is authorized by this review.

A future successor would require explicit user authorization and a fresh preregistration before implementation or any new external correctness result. It must not tune itself against IDMT V4 event-level outcomes, failed subsets, or protected-song historical outcomes unless a future preregistration explicitly establishes a valid development/validation split that preserves an untouched admission holdout.

Until then, V1–V4 remain closed/rejected research diagnostics and delivery remains blocked.
