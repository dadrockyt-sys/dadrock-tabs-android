# Astra V2 Stage-B descriptor implementation supplement V1

Date: 2026-09-28
Status: **PRE-EXECUTION INTERPRETATION FROZEN**

This supplement resolves only implementation details left implicit by the already-frozen Stage-B design.

## Negative-only rows

For descriptors defined as a median over attacked events:
- `firstDifferenceEnergy`
- `preparedCqtPositiveFlux`

a row with zero attacked events receives the value **0.0**.

Rationale:
- the row contains no labeled acoustic attack;
- zero is the natural event-energy/positive-onset-flux value for absence of attacked events;
- this keeps all six challenge rows and all 30 training rows in each family in the predeclared family-level median/quantile calculation;
- no row is dropped based on outcome.

Rise time remains report-only and may be null for no-attack rows.

## Quantile implementation

For each family and gated descriptor:
- training p05 = `numpy.quantile(values, 0.05, method="linear")`;
- training p95 = `numpy.quantile(values, 0.95, method="linear")`;
- challenge statistic = `numpy.median` across all six challenge rows.

Pass iff:
`p05 <= challengeMedian <= p95`.

The frozen requirement remains **35/35** family/descriptor checks.

## Deterministic repeat

Stage B must construct the full V2 preparation twice in the same pinned runtime and require identical array-content hashes and descriptor values across repeats.

Only the first preparation is persisted.

Total V2 source-domain renders for the two repeats:
- (210 train + 42 challenge) × 2 = **504 renders**
- **1,008 synthetic audio seconds**

This remains inside the already-frozen <=900 render / <=1,800-second Stage-B ceiling.

No model, P1/P2/P3, threshold or production access.
