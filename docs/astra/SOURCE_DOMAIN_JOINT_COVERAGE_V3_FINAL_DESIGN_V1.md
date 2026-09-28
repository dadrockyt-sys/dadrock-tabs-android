# Astra source-domain joint-coverage V3 — final model-free coverage protocol

Date: 2026-09-28  
Status: **PROSPECTIVE FINAL SYNTHETIC COVERAGE VERSION — NO MODEL**

## Purpose

Define one final source-domain coverage admission after V2 passed 34/35 checks but failed repeated-family raw first-difference support.

V2 remains failed. V3 is a new experiment version, not a changed V2 verdict.

## Frozen training support

V3 uses the exact V2 training source-domain package:
- 210 training rows;
- 30 per family;
- V2 parameter manifest unchanged;
- V1 source-domain renderer equations unchanged;
- V2 Stage-B deterministic training descriptors/hashes frozen.

No training parameter is regenerated or changed.

## New independent primary challenge

Create exactly **84 challenge renders**:
- 7 families;
- 12 parameter profiles per family.

Each family has six frozen S9/S0 test rows. Each test row appears exactly twice:
- replicate 0;
- replicate 1.

Define family-local challenge slots by sorting:
`(rowIndex ascending, replicate ascending)`
to obtain slots 0..11.

### Continuous parameters

For each of the 12 existing V1/V2 continuous axes, use fixed marginal midpoints:

`u_k = (k + 0.5) / 12`, k=0..11.

For each family and axis independently, permute the 12 strata with deterministic SHA-256-seeded RNG namespace:

`astra-source-domain-joint-v3|challenge|<family>|<axis>`

Map each quantile through the exact unchanged V1 marginal inverse CDF.

Thus every family covers all 12 marginal challenge strata exactly once per continuous axis.

### Categorical parameters

Per family:
- nonlinear active: exactly **6/12**;
- hum active: exactly **4/12**;
- among hum-active slots: exactly **2 at 50 Hz** and **2 at 60 Hz**.

Assignments use the same V3 namespace plus categorical axis name.

No categorical assignment depends on V2 outcomes.

### Per-note behavior

Per-note attack multiplier, note damping jitter, amplitude jitter, component RNG and final noise RNG remain the existing deterministic V1 substreams keyed by original template/variant/event identity.

Replicates vary only the V3 clip-level parameter profile.

## Model-free descriptors

Five family-level challenge-support gates:

1. waveform RMS;
2. spectral centroid;
3. **RMS-normalized first-difference energy**;
4. prepared-CQT positive onset flux;
5. prepared-CQT row displacement from paired frozen control.

Raw first-difference energy remains report-only.

### RMS-normalized first-difference definition

For each row:
- compute median raw attacked-event first-difference energy exactly as before;
- compute full-row waveform RMS;
- if RMS > 0:
  `normalizedFirstDifferenceEnergy = rawFirstDifferenceEnergy / RMS^2`;
- if a row has no labeled attacked event:
  both raw and normalized first-difference descriptor = 0.

This matches the scaling produced by the frozen frontend's `rms_normalize(audio)` operation.

## Frozen training support intervals

Training support uses the exact 210 V2 Stage-B training records already frozen in artifact 10999695803.

For each family and each of the five V3 gate descriptors:
- compute training 5th and 95th percentiles;
- NumPy linear quantile interpolation;
- no V3 training rerender.

For normalized first difference, derive it deterministically from each frozen training record:
`firstDifferenceEnergy / waveformRms^2`.

## V3 challenge gate

For each family and each descriptor:
- compute median of 12 V3 challenge rows;
- require inclusive:
  `trainP05 <= challengeMedian <= trainP95`.

Exactly:
- 7 families × 5 descriptors = **35 checks**;
- require **35/35**.

No tolerance margin.

## Determinism

Render the 84 V3 challenge rows twice:
- exact waveform hashes must match;
- exact feature hashes must match;
- exact descriptor records must match.

Total challenge render operations:
- 168.

Audio:
- 336 synthetic seconds.

## Identity

For every V3 challenge row:
- source row must be one of the 42 frozen test rows;
- state/onset/reference labels duplicated exactly from paired frozen control;
- no training/validation source row;
- renderer does not modify labels;
- prepared features finite;
- positive-note V3 feature row must differ from paired control.

## Old challenges

V1 fixed challenge:
- diagnostic history only.

V2 six-row-per-family primary challenge:
- failed historical admission;
- report-only;
- no gate role in V3;
- not rerendered.

## Hard ceiling

- <= 200 challenge render operations;
- <= 400 synthetic audio seconds;
- <= 30 minutes;
- <= 250 MB persisted artifacts;
- CPU only;
- $0 paid compute;
- models 0;
- inference false;
- optimizer steps 0;
- threshold search/retuning false;
- automatic retry false;
- P1/P2/P3 source access none;
- main/Production mutation none.

## Stop rule

If V3 fails any of the 35 checks:
- freeze failure;
- no V4/V5 source-domain coverage redesign;
- no synthetic model training;
- project returns to the broader representation/data-strategy boundary.

If V3 passes:
- freeze pass;
- one separately preregistered bounded synthetic training experiment may be designed using:
  - frozen S11 architecture;
  - exact V2 training package;
  - V3 primary challenge;
  - ordinary frozen control validation/test;
  - fixed 0.50/0.50 thresholds;
  - no P1/P2/P3.

## Decision

**GO for one final V3 model-free coverage execution only.**
