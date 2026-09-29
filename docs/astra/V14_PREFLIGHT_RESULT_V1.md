# V14 matched-context bridge — model-free preflight result V1

Date: 2026-09-29 UTC  
Status: **MODEL-FREE CONTRACT/SCHEDULE PASS — EMPIRICAL EXECUTION NOT AUTHORIZED**

## Result

The frozen V14 2-second bridge schedule and recovery gates pass independent model-free verification.

During preflight, one arithmetic typo was caught **before any empirical work**:
- initially recorded 50%-precision-recovery threshold: 0.5756752789195302
- exact threshold: **0.5756752789195536**

The contract and validator were corrected before this receipt was frozen.

## Frozen schedule verification

- positive clips: **273**
- attack groups: **819**
- positive gaps: **546**
- S/M/L gaps: **252 / 225 / 69**
- density: **1.500000/s**
- IOI p10: **0.1061617322 s**
- IOI p50: **0.2520127045 s**
- IOI p90: **0.8704418108 s**
- repeat250: **0.4615384615**
- longGap700: **0.1263736264**
- latest attack: **1.7920413320 s**
- minimum post-last-attack margin: **0.2079586680 s**
- required minimum margin: **0.120 s**
- corrected timing-distance V1: **0.0430642112**

All schedule arithmetic passed.

## Frozen material-recovery gates

- common-test F1 >= **0.586490016794178**
- common-test precision >= **0.5756752789195536**
- recall decline vs successful comparator <= **0.05**
- negative-only FP <= **0.10/s**
- exactly 500 updates/model
- exactly 2 models
- thresholds fixed 0.50/0.50
- no threshold search
- no scientific retry

## Validator package

Committed:
- `astra_backend/synthetic/v14_contract_validator_v1.py`
- `astra_backend/synthetic/test_v14_contract_validator_v1.py`

The current container could not resolve `raw.githubusercontent.com`, and the available GitHub connector does not expose a workflow-dispatch action. Therefore the committed unittest module was **not falsely reported as executed**.

Instead, the exact frozen SHA-based schedule and gate arithmetic were independently recomputed in a model-free Python environment and all corresponding invariants passed after the precision-gate correction.

### Fail-closed requirement for future empirical execution

Before **any** V14 waveform render, dataset generation, optimizer step, or model inference:
1. execute the committed validator and unittest module against the branch contract;
2. require all tests to pass;
3. if any validator/test fails, stop with zero renders and zero optimizer steps.

This requirement is part of the empirical launch boundary.

## Execution counts

- waveform renders: **0**
- datasets generated: **0**
- models trained: **0**
- optimizer steps: **0**
- model inference: **0**
- V2B inference: **0**
- real-audio access: **0**
- workflow dispatches: **0**

## Authorization boundary

The user's authorization has been consumed for opening V14, freezing its contract, implementing the pure validator/tests, and completing this model-free preflight.

**Empirical V14 execution is not authorized.**

A fresh explicit authorization is required before rendering/training. Even after that authorization, validator/tests must pass first and fail closed before any empirical work.
