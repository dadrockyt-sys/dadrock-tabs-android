# V147 Phase C pre-audio test-fixture repair preregistration

Status: **FROZEN BEFORE TEST-FIXTURE CHANGE**
Branch: `v143-contextual-prune-lobo`
Date: 2026-08-26 America/Montreal

## Why this repair exists
The frozen workflow-only repair was applied and the authorized repository-native CPU/generated/reference-free pre-audio run `33036741821` (job `98400937803`) reached the frozen test suite. Frozen identity checks and the no-real-audio/no-reference guard both passed. Pytest then reported **10 passed, 1 failed**.

The single failure was `test_materializer_fails_closed_if_v5_source_changes`. Its fixture changed the first V5 event's `midi` by `+1` but left the corresponding guitar `fret` unchanged. Canonical validation therefore correctly failed earlier with:

`pitch-position mismatch: stringIndex=3 fret=6 midi=57 expected=56`

The test had expected the later identity-gate message `V5 source identity mismatch`. This is a fixture-construction problem, not a failure of fail-closed behavior and not an algorithmic result.

Because the workflow shell stopped at pytest failure, the generated Phase-C proof command did not execute. No proof payload/runtime evidence, candidate, real-audio decode/CQT analysis, reference/gold access, score, Modal/GPU execution, `main`, or Production change occurred.

## Frozen diagnosis
For standard tuning, stringIndex `3` has open MIDI `50`. The original event was internally consistent at fret `6`, MIDI `56`. After changing MIDI to `57`, the fixture must also change fret to `7` to remain a valid guitar position. A canonical-valid but identity-different event then reaches the intended V5 source hash identity guard.

## Exactly authorized changes
After this document is frozen, and before any further CPU proof execution, only these changes are authorized:

1. In `modal/tests/test_v147_phase_c_artifact_support.py`, inside `test_materializer_fails_closed_if_v5_source_changes`, keep the existing `midi + 1` mutation and add exactly `fret + 1` on the same first event. Keep the expected exception type/message unchanged: `ValueError`, matching `V5 source identity mismatch`.
2. Update `.github/workflows/v147-phase-c-pre-audio-proof.yml` only where necessary to replace the old frozen Phase-C test blob identity with the new test-file blob identity produced by change #1. Add/verify this preregistration blob identity if useful for evidence provenance, but do not alter generated proof cases, algorithms, thresholds, source identities, or execution scope.

## Explicitly forbidden changes
- No edits to `modal/v147_phase_c_artifact_support.py`.
- No edits to `modal/v147_pitch_hypothesis.py`.
- No edits to `modal/v145_rhythm_decoder.py`.
- No edits to `modal/v147_phase_c_cpu_proof.py` generated proof logic/cases.
- No threshold, pitch-evidence, frame-selection, timing, fingering, reconstruction, canonicalization, or accepted-family changes.
- No weakening from an exact identity-mismatch assertion to a generic `ValueError` assertion.
- No calibration/gold/reference opening or scoring.
- No real-audio read, decode, HPSS, CQT, analyzer integration, Modal/L4/GPU, `main`, or Production work.

## Frozen identities that remain authoritative
- Phase-C prereg blob `5c19ed572d17cc9a760f1b63ee03c1b2c4543d30`.
- Phase-C clarification blob `6ced1bae4cdaad8306b008827657afbb27a87dbc`.
- Workflow-repair prereg blob `d36b49e3e1519fd68e524a4ec12eba300c14b0da`.
- V145 decoder blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- V147 pitch implementation blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
- Phase-C support blob `f4278ffaacaca3f66baf7a3112e2af0f3bc387cf`.
- Pre-repair Phase-C tests blob `e99f791cd0ab401a9e393ab9b89a6b167cee3c7f` (superseded only by the exact fixture repair authorized here).
- Phase-C proof harness blob `531384706b8b7444cf7ed22f414b47215e59b653`.
- Canonical helper blob `088d44827fb23e20d9aeeb4944a672989af5846c`.

## Execution allowance after repair
After the exact fixture repair and workflow identity update are checkpointed, exactly one new repository-native **CPU/generated/reference-free pre-audio verification run** is authorized. It may run the repaired test suite and unchanged generated proof harness.

If that run passes, persist/checkpoint exact run, job, artifact, proof/runtime identities and then delete/seal the one-use workflow. If it fails for any new substantive reason, STOP and checkpoint the failure before any further change.

**Real-audio Phase C execution remains unauthorized and requires fresh explicit authorization after this pre-audio support gate is sealed.**
