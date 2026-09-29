# V3 Upstream Transfer Diagnosis Result V1

Date: 2026-09-28  
Status: **V3A/V3C COMPLETED — SIMPLE AFFINE FRONTEND ALIGNMENT INSUFFICIENT**

## Exact historical synthetic export

A dedicated GitHub Actions export attempted to regenerate the historical S9 synthetic features under the original Python/package lock.

- run: **36518666947**
- job: **109246542435**
- Python 3.10.15
- torch 1.11.0+cpu
- librosa 0.9.1
- numpy 1.21.6

The export failed closed because the regenerated control feature-array SHA was:

`a9603d7997c6d8bc3d553f3605369bb0c6e02cecaf15475ca2c7db4fc3ef09ad`

instead of historical:

`2119d9b953cf2fabde0dcab211004a89e385439108847d2e736a6cdea6e82ce4`

The S0 source, S9 source, and runtime-lock blobs are identical between the historical S9 commit and the current branch. Therefore this is a runner-level numerical bit-reproducibility limitation. No mismatched artifact was uploaded.

## V3A same-runtime source-equivalent audit

To avoid comparing different frontend runtimes, the S9 synthetic corpus was regenerated locally under the same frontend runtime used for V2B real audio.

This is **source-equivalent**, not historical-byte-exact.

Observed real-vs-synthetic feature shift:

| Metric | Result |
|---|---:|
| Median absolute SMD | **0.8665** |
| 95th percentile absolute SMD | **1.5249** |
| CQT bins with |SMD| >= 1 | **39.06%** |
| CQT bins with |SMD| >= 2 | **0%** |
| Median Wasserstein distance | **0.2025** |
| 95th percentile Wasserstein | **0.3076** |
| Median robust range overlap | **0.8876** |
| 5th percentile range overlap | **0.5598** |

V3A therefore found a substantial distribution shift and activated the already-frozen affine probes.

## V3C frozen representation probes

All transforms used the original **0.50 / 0.50** thresholds.

| Transform | Trusted hits | High-confidence hits | Negative FP/s | Gain vs identity |
|---|---:|---:|---:|---:|
| Identity | 0 / 56 | 0 / 49 | 0.4395 | 0 |
| Global affine | 1 / 56 | 1 / 49 | 2.9820 | +0.0179 |
| Per-bin affine | 1 / 56 | 1 / 49 | 0.3453 | +0.0179 |

Frozen diagnostic-interest conditions required:
- >= +0.20 absolute trusted joint-admission gain;
- >=25% high-confidence landmark admission;
- <=0.10 negative FP/s.

**No transform passed any complete diagnostic gate.**

Global affine severely increased negative false positives. Per-bin affine slightly reduced negative FPs versus identity, but remained far above the constraint and recovered only one trusted landmark.

## Supported conclusion

There is a material synthetic-vs-real frontend-feature distribution shift.

However, **simple first/second-moment alignment does not restore useful transcription admission**. Therefore the transfer collapse cannot be adequately explained by a basic global or per-bin affine mismatch.

The remaining plausible causes include higher-order feature-distribution differences, synthetic timbre/rendering inadequacy, representation learned from the synthetic task, or other frontend/model interaction effects. This V3 result does not isolate those causes.

## Boundaries preserved

No training or fine-tuning.
No threshold changes.
No decoder changes.
No arbitrary transform search.
No V1.1 tuning.
No P1/P2/P3.
No A2.
No main/Production mutation.

V3D does not run because no transform is diagnostically interesting.

## Decision boundary

The next useful experiment should target **synthetic-to-real representation adequacy**, not additional threshold or affine-normalization tuning.
