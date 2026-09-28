# Astra V2 Stage-A test-contract correction review V1

Date: 2026-09-28  
Status: **REVIEW FROZEN — TECHNICAL TEST CONTRACT CORRECTION JUSTIFIED — NO STAGE-A RERUN**

## Scope

This review follows the frozen pre-execution failure:
- `docs/astra/SOURCE_DOMAIN_V2_STAGE_A_PREEXECUTION_FAILURE_V1.json`

It is limited to the failed focused-test expectation around the V2 hum categorical fields.

No waveform is rendered. No Stage-A acoustic admission is executed. No model is loaded. No optimizer work occurs. P1/P2/P3 remain closed.

## Frozen evidence reviewed

- V2 joint-coverage protocol:
  - `docs/astra/SOURCE_DOMAIN_JOINT_COVERAGE_PROTOCOL_V2.md`
  - `docs/astra/SOURCE_DOMAIN_JOINT_COVERAGE_PROTOCOL_V2.json`
- V2 manifest generator:
  - `astra_backend/synthetic/source_domain_joint_coverage_manifest_v2.py`
- Stage-A runner:
  - `astra_backend/synthetic/source_domain_v2_stage_a_admission_v1.py`
- failed focused test:
  - `astra_backend/synthetic/test_source_domain_v2_stage_a_admission_v1.py`
- pre-execution failure:
  - workflow run 36482951827 / job 109132814201.

## Contract finding

The V2 protocol freezes two separate hum categorical decisions:

1. whether hum is active;
2. when hum is active, whether the fundamental is 50 Hz or 60 Hz.

The manifest generator encodes this as:
- `humActive=false` -> `humFundamentalHz=null`;
- `humActive=true` -> `humFundamentalHz` is exactly 50 or 60.

The Stage-A runner implements the correct mapping:
- always override `humActive`;
- override `humFundamentalHz` **only when hum is active**;
- do not override `humFundamentalHz` when hum is inactive.

This behavior is consistent with the frozen V2 protocol.

## Exact defect in the failed test

The test helper generated its first synthetic row using position 0.

Its helper logic therefore produced:
- `humActive=true`;
- `humFundamentalHz=50`.

But the test then asserted that the override key set was:
- all 12 continuous axes;
- `nonlinearActive`;
- `humActive`;
- **without** `humFundamentalHz`.

That expectation contradicts the same helper row and the frozen protocol.

The failure therefore occurred in the test assertion, not in the V2 renderer mapping.

## Corrected test contract

A future corrected focused test must explicitly cover both cases.

### Case A — active hum

Input:
- `humActive=true`;
- `humFundamentalHz=50` or 60.

Required override:
- all 12 frozen continuous V2 clip-level axes;
- `nonlinearActive`;
- `humActive=true`;
- `humFundamentalHz` exactly equal to the manifest-selected 50 or 60.

Required exclusions:
- `humCombinedRmsRelative` is absent from the V2 manifest override.

### Case B — inactive hum

Input:
- `humActive=false`;
- manifest `humFundamentalHz=null`.

Required override:
- all 12 frozen continuous V2 clip-level axes;
- `nonlinearActive`;
- `humActive=false`.

Required exclusions:
- `humFundamentalHz` absent;
- `humCombinedRmsRelative` absent.

## Why humCombinedRmsRelative remains unoverridden

The V2 joint-coverage protocol changes only the clip-level joint sampling assignment for the explicitly frozen axes/categoricals.

It does not add hum amplitude as a new V2 coverage axis.

The existing V1 renderer already generates `humCombinedRmsRelative` from its deterministic source-parameter substream. Leaving it unoverridden:
- preserves the V1 waveform equation and source semantics;
- does not change a frozen V2 marginal range;
- does not derive anything from V1 model scores or P1/P2;
- leaves the parameter scientifically unchanged from the pre-failure Stage-A implementation.

When hum is inactive, that amplitude has no waveform effect. When hum is active, it remains the same deterministic V1 substream value that the frozen Stage-A runner would have used before the test failed.

## Scientific-change audit

Correcting the test expectation changes **none** of the following:
- V2 manifest content or hash;
- selected Stage-A rows;
- continuous parameter values;
- categorical assignments;
- waveform equations;
- V1 deterministic substreams;
- CQT/frontend;
- labels/references/timing;
- Stage-A gates;
- render/audio/time/storage ceilings;
- Stage-B gates;
- model architecture/loss/sampler;
- thresholds;
- P1/P2/P3 policy.

Therefore the correction is classified as:
**technical verification-contract correction only; scientific configuration unchanged**.

## Retry/versioning decision

The failed V1 Stage-A workflow attempt is preserved and must not be rewritten or rerun as though it never happened.

If Stage A is attempted again, it must be a **separately versioned execution attempt** with:
- a corrected focused-test file or corrected test case under a new version;
- a new workflow filename/name;
- explicit reference to the frozen pre-execution failure and this review;
- the same V1 Stage-A runner scientific logic unless a separate review finds another defect;
- the same frozen manifest/control hashes;
- the same Stage-A sample rows and hard gates;
- one attempt only;
- no automatic retry.

Suggested names:
- `astra_backend/synthetic/test_source_domain_v2_stage_a_admission_v2.py`
- `.github/workflows/astra-source-domain-v2-stage-a-admission-v2.yml`

The original V1 test/workflow remain historical evidence and should not be silently edited to erase the failure.

## Current boundary

This review does **not** authorize execution of the separately versioned Stage-A attempt.

The next allowed work is offline/package-only:
1. create the corrected V2 focused-test file;
2. create the separately versioned V2 workflow in a disabled/non-triggering state;
3. verify by static inspection that the workflow pins the same frozen inputs and cannot auto-run;
4. freeze that package verification.

Only a later checkpoint may arm/run the new Stage-A attempt.

## Decision

**GO for offline construction of a separately versioned corrected Stage-A execution package only.**

No waveform execution is authorized by this review.
