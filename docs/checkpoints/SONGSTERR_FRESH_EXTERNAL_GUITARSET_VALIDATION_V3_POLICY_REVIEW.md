# Songsterr Fresh — External GuitarSet Validation V3 Policy Review

Status: **CLOSED / REJECTED AS ADMISSION AUTHORITY / RETAINED AS RESEARCH DIAGNOSTIC**

Recorded: 2026-09-11 America/Toronto

Result record:
- `docs/checkpoints/SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3_RESULT.md`
- result-record commit `91b021f6b3f43cee73dc58d1aebf29492a547928`

Preregistration:
- `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V3.md`
- commit `2dfd8c5d52093c36c0924e5f0b57eb2b2284e7d0`

Frozen execution source:
- branch `songsterr-fresh-pipeline-v1`
- commit `783c3b572aff4edd9d6298e9131dffd02454a61e`

## Question reviewed

Did the frozen V3 external-validation protocol establish sufficient independent evidence to allow the unchanged V2 corroborator to become model-evidence admission authority?

## Decision

**NO. V3 is rejected as admission authority and retained only as a frozen research diagnostic.**

The preregistered gates were not met. No post-hoc relaxation, threshold adjustment, track exclusion, scorer modification, or reinterpretation is permitted under V3.

## Evidence considered

The valid GuitarSet v1.1.0 execution completed all 357 locked tracks under the frozen source/runtime/provenance contract.

Observed primary result:
- 62,438 decoded events
- 11,252 V3-positive events
- 10,019 correct V3-positive events
- point precision `0.8904194809811589`
- one-sided 95% Wilson lower bound `0.8854816094599652`.

Frozen pooled gate:
- one-sided 95% Wilson lower bound `>= 0.9900`.

Observed result: **FAIL**.

Every player stratum `00..05` and both mode strata `comp`/`solo` also failed the preregistered point-precision requirement `>=0.9500`, despite each satisfying the minimum positive-count requirement.

Therefore the failure is not a marginal sample-size issue and is not confined to a single player or one of the two locked modes.

## Policy interpretation

The external corpus did what V3 was designed to do: it provided independent annotated evidence rather than relying on reproducibility, protected-song agreement, Basic Pitch confidence, or synthetic fixtures alone.

That evidence shows the frozen V2-positive rule does **not** reach the accuracy level preregistered for customer admission on this corpus.

The following are explicitly prohibited conclusions:
- the 89.04% point precision is not “close enough” to the 99% Wilson gate;
- the gate may not be lowered after seeing the result;
- the three preregistered exclusions may not be expanded;
- player/mode failures may not be ignored or averaged away;
- historical protected-song V1/V2 observations may not override the external result;
- Basic Pitch confidence, event count, CPU association, exact hashes, C-S reproducibility, or downstream agreement may not be used to rescue V3;
- the protected song may not be run under V3 to search for a favorable outcome.

## First-attempt execution failure

The first official launch failed on the first track before inference because the harness dereferenced the supplied venv Python symlink to system Python, which lacked NumPy. That attempt produced no completed inference JSON and no GuitarSet correctness result.

The subsequent valid run preserved the exact frozen repository source, model/scoring/matching policy, dataset identities, exclusions, tolerances, and pass gates; it only used a regular-file copy of the same pinned venv Python executable so the child process remained inside the pinned environment.

This environment-path correction does not change the substantive external-validation result or policy decision.

## Current authority state

Remain fail-closed:
- `modelValidationComplete:false`
- customer-eligible events: `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research remains paused
- persistent Policy C remains `UNENROLLED`.

V3 must not run the protected authorized song. A new protected-song C-S epoch is **not authorized** from this V3 result.

## Successor boundary

Any future successor must be a **new preregistered version** and may not be described as a patch or retuning of V3.

Before any successor result is viewed, its method, allowed development evidence, corpus role, thresholds, matching policy, and promotion gates must be frozen anew. V3's observed GuitarSet errors may be used only as historical research evidence for a separately authorized successor; they cannot alter V3 itself.

No successor workstream is opened by this policy review alone.
