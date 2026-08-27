# V147 Phase A — Execution-Only Repair Preregistration

Status: **FROZEN BEFORE WORKFLOW REPAIR**

Branch: `v143-contextual-prune-lobo`

## Reason for this revision

V147 Phase A repository-native attempt 1 (run `33034467868`, job `98394054352`) is consumed and remains a failure. Its 13 frozen contract tests passed, but the generated proof harness did not start because the workflow invoked the package file directly:

`python modal/v147_pitch_hypothesis_cpu_proof.py`

That execution mode set Python's import path such that `from modal.v147_pitch_hypothesis import ...` failed with `ModuleNotFoundError: No module named 'modal'`.

No generated proof payload was constructed in attempt 1, and no calibration/gold evidence, Modal/L4/GPU, live audio, or production integration was used.

## Frozen repair scope

This revision authorizes exactly one execution-harness repair:

- replace direct file invocation with package/module invocation from repository root:
  - old: `python modal/v147_pitch_hypothesis_cpu_proof.py --output ...`
  - new: `python -m modal.v147_pitch_hypothesis_cpu_proof --output ...`

No other behavior change is authorized.

The following V147 blobs MUST remain unchanged for the repaired execution:

- implementation `modal/v147_pitch_hypothesis.py`: `49bce8b968406bb0d61ab61394954ef8a8303eb7`
- tests `modal/tests/test_v147_pitch_hypothesis.py`: `f71d1da6c52a6a737faca7ab4f8989fb702be96d`
- proof harness `modal/v147_pitch_hypothesis_cpu_proof.py`: `e9d28739cd19f095cb83807fd0b23c2b14b7c966`
- original V147 preregistration: `026d3bdbbebd385b7bdd4e896da569091b0265b7`

No threshold, candidate family, generated case, evidence representation, scoring rule, gate, or musical code may change.

## Execution constraints

1. CPU/reference-free only.
2. No calibration/gold file read or score.
3. No Modal/L4/GPU.
4. No live audio.
5. No V145 decoder modification.
6. No `/ai-tab` frontend, Bass/Lead, main, Production, or `freezeReady` change.
7. Attempt 1 MUST NOT be rerun or reinterpreted.
8. One fresh repository-native run may be triggered only by the workflow repair commit.
9. Persist exact run/job/artifact identities plus proof/runtime evidence.
10. Delete/seal the single-use workflow after the fresh run is recorded.

## Frozen gate

The original V147 Phase A generated-proof gate remains unchanged. If the repaired execution reaches the frozen generated cases and any gate condition fails, the result is **STOP** with no retuning or second repaired run.

If tests and generated proof both pass unchanged, record **GO for V147 Phase A generated/reference-free contract only**. This does not authorize live/reference evaluation, Modal/GPU execution, V145 integration, or production promotion.
