# Controlled Duplicate-Class Stress Result V1

Date: 2026-10-02
Run ID: 37088717448
Status: **DETECTOR GENERALIZATION PASS / MERGE METRIC INVALID FOR THIS STRESS DESIGN**

Artifact:
- id: 11261451719
- digest: `sha256:c8b6864d90d43391e28a511e6edf2f84edc353d502b33e601394e7f7fb1a625f`

## Frozen detector result

The pair classifier was unchanged from the prior S0 run.

Test matrix:
- 3 bass sources
- 3 guitar sources
- 4 split ratios each
- 24 total cases

Expected duplicate positives:
- 50/50
- 40/60
- 35/65
- 18 cases total

Prospective hard negatives:
- 30/70, outside the frozen 6 dB pair-energy-gap gate
- 6 cases total

Observed:
- **18/18 intended duplicate positives classified correctly**
- **6/6 hard negatives classified correctly**
- positive accuracy: **100%**
- hard-negative accuracy: **100%**

The detector generalized in both directions:
- bass source split across guitar+bass -> duplicate_bass_candidate
- guitar source split across guitar+bass -> duplicate_guitar_candidate

and stopped at the intended 30/70 boundary.

## Important metric correction

The stress generator created each pseudo stem as an exact scalar multiple of the same isolated source waveform.

Therefore SI-SDR is not a valid way to judge merge quality in this particular stress design because SI-SDR is scale-invariant. A 35%, 50%, or 65% scaled copy of a source can already score nearly perfectly against that source.

This explains why the reported merge-improvement field ranges from negative to positive even though:
- the merged waveform exactly reconstructs the original split source;
- merge reconstruction max absolute error is **0.0 for all 24 cases**.

Therefore:
- detector accuracy is valid evidence;
- the stress-set `mergeImprovementDb` values must **not** be interpreted as action quality.

## What remains valid

The prior S0M10 action result remains meaningful because BS-Roformer produced two imperfect, differently distorted outputs; merging them raised bass SI-SDR from 0.0728 dB to 30.5695 dB while preserving reconstruction.

This controlled stress result independently strengthens the **detection** side:
- duplicate-class pair detection generalized across 6 source identities;
- it worked for both guitar and bass;
- it respected the prospectively frozen 6 dB stop boundary.

## Decision

Freeze PairClassifierConfig V1 unchanged.

Next experiment should test consolidation quality using **non-collinear split errors**, not exact scaled copies. Suitable synthetic perturbations include:
- complementary frequency-band partitioning;
- time-varying leakage;
- phase or filter differences;
- small independent contamination added to each split output.

The pair detector remains frozen during that experiment.

Do not move to production or real-audio automatic consolidation yet.
