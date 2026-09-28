# Astra source-domain V2 Stage-B failure analysis V1

Date: 2026-09-28
Status: **FROZEN POST-HOC ANALYSIS — V2 REMAINS FAILED — ONE FINAL PROSPECTIVE SYNTHETIC MEASUREMENT VERSION JUSTIFIED**

## Frozen V2 outcome

Stage B V2 failed its preregistered 35/35 family/descriptor coverage gate:
- run 36485375684
- job 109140893933
- artifact 10999695803
- artifact digest `sha256:a38a2a2a400cc3e2c470c9fd8ccf46ac8e6b9a346ffb57292aa4384b2615e6ca`
- result SHA-256 `d1f4ee0580ca98094fb12adabf76f437e6e3769c85b1fbc7f741205c9a3b13d2`
- passed **34/35**
- failed only:
  - family `repeated`
  - descriptor `firstDifferenceEnergy`
  - training p95 **0.0026163426**
  - challenge median **0.0028062511**

No retry or gate waiver is allowed. V2 remains failed.

## Distribution localization

Repeated-family primary challenge raw first-difference values are bimodal:
- low group approximately 0.000296, 0.000415, 0.000426
- high group approximately 0.005187, 0.005562, 0.005768

The three high rows exceed the V2 repeated-family training maximum (~0.003947), so the miss is not merely an arithmetic median artifact.

All other 34 source/prepared coverage checks passed.

## Frontend scaling review

Frozen preprocessing applies:
`normalized_audio = audio / rms(audio)`

before CQT extraction.

For a uniform scale factor, first-difference energy scales quadratically. Therefore the first-difference energy after the frozen RMS normalization is exactly proportional to:

`raw_first_difference_energy / waveform_rms^2`.

The original Stage-B raw first-difference gate is therefore sensitive to waveform global RMS/crest-factor differences that the model frontend removes before feature extraction.

This does not make the original gate invalid; it was prospectively defined as a source-level descriptor and must remain failed historically.

## Frozen-record diagnostic only

Using only already-frozen V2 Stage-B row records, no rerendering:

Repeated family:
- RMS-normalized first-difference training p05: **0.00238007**
- training p95: **0.04709534**
- primary-challenge median: **0.03656379**

Thus the frontend-aligned normalized challenge median lies inside training support.

Applying the same diagnostic across all seven families places every family challenge median inside the corresponding normalized-first-difference training p05-p95 interval.

This calculation is post-hoc and is **not** used to pass V2.

## Relation to previously frozen real-domain measurement

The earlier authorized P1/P2 integrity audit prospectively computed both raw-resampled and RMS-normalized-resampled attack metrics before this Stage-B failure.

From its frozen artifact, RMS-normalized first-difference energy event-weighted medians are approximately:
- P1: **0.17188**
- P2: **0.03120**

The normalized measure is therefore not newly invented to rescue Stage B; it is an existing model-free diagnostic already present in the real-domain audit implementation.

The real-domain distributions remain heterogeneous and are not used to tune a synthetic numeric threshold.

## Project decision

Do not:
- pass V2 retroactively;
- train a model on V2;
- relax 35/35;
- change the V2 result;
- drop the repeated family;
- substitute V2 challenge rows;
- fit synthetic parameter ranges to P1/P2.

One final prospective synthetic measurement version is justified because:
1. its normalization operation is already fixed by model preprocessing;
2. the same normalized raw diagnostic predates the Stage-B failure in the real audit;
3. the V2 six-row-per-family challenge is small for a nonlinear renderer.

## V3 boundary

V3 must be the final source-domain coverage iteration before either synthetic training or a stop.

It must:
- keep the 210 V2 training rows and all source parameter ranges unchanged;
- keep renderer equations unchanged;
- use a new independently specified larger primary challenge: 12 source-domain variants per family;
- generate challenge parameters from fixed marginal midpoints and a new fixed namespace, not from V2 failure values;
- gate the same five conceptual dimensions, but use **RMS-normalized first-difference energy** instead of raw first-difference energy;
- retain raw first-difference as report-only;
- keep waveform RMS, spectral centroid, prepared-CQT flux and prepared-CQT displacement gates;
- require 35/35 family/descriptor checks;
- use no model, no P1/P2/P3 source access;
- stop synthetic redesign if V3 fails.

A V3 pass may justify one separately preregistered bounded synthetic training experiment. A V3 failure means no further synthetic coverage redesign.
