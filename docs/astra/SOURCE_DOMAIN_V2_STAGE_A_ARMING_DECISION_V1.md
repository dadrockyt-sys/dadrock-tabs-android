# Astra V2 Stage-A arming decision V1

Date: 2026-09-28
Status: **GO — ONE CORRECTED SYNTHETIC/MODEL-FREE STAGE-A ATTEMPT MAY BE ARMED**

## Basis

The first Stage-A workflow attempt did not render audio; it failed in a focused unit-test expectation before acoustic execution.

The defect has since been reviewed and classified as a technical verification-contract error only:
- active hum rows must include the manifest-selected 50/60 Hz frequency;
- inactive hum rows must not override hum frequency;
- no scientific parameter, manifest row, renderer equation, gate, range, threshold or model setting changes.

The corrected V2 package was statically verified in a hard-disabled state.

## Authorization basis

The user's current instruction is to continue and run at discretion until a boundary requiring explicit authorization is reached.

This attempt:
- uses only repo-owned synthetic data;
- uses no P1/P2/P3 media;
- loads no model;
- performs no inference;
- performs no optimizer steps;
- uses CPU/$0 scientific compute;
- remains on astra-work;
- does not mutate main/Production.

Therefore no additional user authorization is required for this one synthetic/model-free attempt.

## Frozen one-shot scope

Launch identity:
`source-domain-v2-stage-a-20260928-canonical-01`

Exact frozen inputs:
- V1 preparation run: 36475263654
- S9 control SHA-256:
  `16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894`
- V2 manifest run: 36481373445
- V2 manifest content SHA-256:
  `2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469`

Exact scientific runner:
- `astra_backend/synthetic/source_domain_v2_stage_a_admission_v1.py`

Corrected focused tests:
- `astra_backend/synthetic/test_source_domain_v2_stage_a_admission_v2.py`

The selected rows, acoustic gates and execution ceilings are unchanged from the frozen V2 waveform/prepared-feature admission design.

## One-shot execution rule

A new workflow version may run **only** when this exact launch-marker path is created:
- `docs/astra/SOURCE_DOMAIN_V2_STAGE_A_LAUNCH_V1.json`

The workflow must:
- validate the exact launch identity;
- validate the frozen manifest/control hashes;
- run corrected focused tests first;
- run Stage A at most once;
- upload the result whether scientific pass or fail when an output exists;
- have no automatic retry;
- not trigger from later result/checkpoint commits.

If preflight or Stage A fails, freeze the failure and stop.
If Stage A passes, freeze the pass and then proceed only to the already-prospective Stage-B model-free preparation package; no model training follows automatically.

## Decision

**ARM exactly one corrected Stage-A V2 synthetic/model-free attempt.**
