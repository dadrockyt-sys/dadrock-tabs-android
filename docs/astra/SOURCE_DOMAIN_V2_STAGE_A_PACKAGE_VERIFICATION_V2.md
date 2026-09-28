# Astra V2 Stage-A corrected package static verification

Date: 2026-09-28  
Status: **OFFLINE PACKAGE VERIFIED — DISABLED / NON-AUTO-RUNNING — NO WAVEFORM EXECUTION**

## Purpose

Verify the separately versioned corrected Stage-A package required by the frozen test-contract review without executing Stage A.

## Package

Corrected focused tests:
- `astra_backend/synthetic/test_source_domain_v2_stage_a_admission_v2.py`
- git blob: `78c6988e307242f27b31ff973ca7388b7cfeb5f5`

Disabled workflow:
- `.github/workflows/astra-source-domain-v2-stage-a-admission-v2.yml`
- git blob: `bb87c113acc85b2f7e45b66cd618f044a89f95b3`

Scientific runner remains unchanged:
- `astra_backend/synthetic/source_domain_v2_stage_a_admission_v1.py`

Historical failed V1 workflow/test remain untouched.

## Corrected test contract

The V2 test package now has separate cases for:

### Active hum
- `humActive=true`;
- `humFundamentalHz` is required in the override;
- both 50 Hz and 60 Hz are covered;
- `humCombinedRmsRelative` remains absent from the V2 override.

### Inactive hum
- `humActive=false`;
- `humFundamentalHz` is absent from the override;
- `humCombinedRmsRelative` remains absent.

The original frozen Stage-A positions, manifest hash and selected-row logic are still asserted.

No test was executed by this verification step.

## Static workflow safety

The new workflow is intentionally non-auto-running:

- trigger section contains **only** `workflow_dispatch`;
- there is **no** `push`, `pull_request`, `schedule`, `workflow_run`, or repository-dispatch trigger;
- the only job, `stage-a-v2`, has a hard guard:
  `if: ${{ false }}`.

Therefore:
- repository commits cannot auto-start the V2 Stage-A job;
- a manual dispatch while the guard remains false yields no Stage-A execution;
- a later checkpoint must deliberately edit/version the guard before acoustic work can occur.

After the workflow commit, the commit check-runs contained no Stage-A V2 job. Only the unrelated Cloudflare Pages check was present.

## Frozen inputs remain identical

The disabled workflow pins:
- V1 preparation run **36475263654**;
- S9 control SHA-256:
  `16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894`;
- V2 manifest run **36481373445**;
- V2 manifest content SHA-256:
  `2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469`.

The Stage-A sample positions, acoustic gates and ceilings remain unchanged.

## Execution accounting

This package-verification step performed:
- waveform renders **0**;
- synthetic audio seconds **0**;
- Stage-A acoustic runner executions **0**;
- model loads **0**;
- model inference **false**;
- optimizer steps **0**;
- threshold search/retuning **none**;
- P1/P2/P3 access **none**;
- paid compute for scientific work **$0**;
- main/Production mutation **none**.

## Decision

**PASS for offline package construction/static safety verification.**

This is not a Stage-A scientific pass.

## Next boundary

A future checkpoint may decide whether to create a separately versioned **armed** Stage-A V2 workflow for exactly one acoustic admission attempt.

Until that separate arming decision:
- keep the current V2 workflow hard-disabled;
- do not run Stage A;
- do not run Stage B;
- do not load/train a model;
- keep P1/P2 closed and P3 sealed.
