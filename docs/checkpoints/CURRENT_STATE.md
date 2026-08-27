# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V147 Phase C preregistration/clarification/support are FROZEN. The invalid mutation fixture has been repaired exactly as preregistered, and the one-use pre-audio workflow is now frozen to that repaired test identity. One CPU/generated/reference-free verification run has been triggered by workflow commit `369feb72...`; real-audio decoding/analysis remains STOP pending fresh explicit authorization. Accepted Rhythm family #10 remains active.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU/live/real audio without fresh explicit authorization.
- Gold SHA256 `18fd868ae960dfcddc1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark only, never unseen holdout.
- No automatic promotion.

## Accepted Rhythm baseline — UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Canonical event count `1144`; event/PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; generated measures `113`.
- Scores **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.

## V147 Phase A / B — SEALED
- Phase A GO: run `33034629948`, job `98394561968`; proof SHA `3843912f0c8e5da95c3993783a84762ba01b046120a48db5e5a5c6c16a3d883e`.
- Phase B GO: run `33035123962`, job `98396067875`; proof SHA `07848295a7a0b82cee4701db8ddf4505910d4955c2c6bd9587833cbb1656435a`.

## V147 Phase C — PRE-AUDIO ONLY / NO REAL AUDIO EXECUTION
### Frozen identities
- Phase-C prereg blob `5c19ed572d17cc9a760f1b63ee03c1b2c4543d30`.
- Phase-C clarification blob `6ced1bae4cdaad8306b008827657afbb27a87dbc`.
- Workflow-repair prereg blob `d36b49e3e1519fd68e524a4ec12eba300c14b0da`.
- Test-fixture-repair prereg freeze commit `81f6db17acf9265695c08824037b416515f03b00`; blob `aa74555976b826a4595cf1f472a2be0a173fb3d5`.
- V145 decoder blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- V147 pitch blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
- Phase-C support blob `f4278ffaacaca3f66baf7a3112e2af0f3bc387cf`.
- Phase-C proof harness blob `531384706b8b7444cf7ed22f414b47215e59b653`.
- Canonical helper blob `088d44827fb23e20d9aeeb4944a672989af5846c`.

### Prior reached-test failure — CLOSED
- Run `33036741821`, job `98400937803`: 10 passed, 1 failed on invalid fixture; generated proof did not execute.
- Failure was canonical pitch-position mismatch caused by changing MIDI without fret.
- No real audio/reference/gold/candidate/score/Modal/GPU work occurred.

### Test-fixture repair — APPLIED / FROZEN
- Test repair commit `8fd35df1de2e515703d446f3deafe5a504beae9a`.
- Repaired tests blob `cbcc8fa90480b2a3b12546cf2193519fb46ade87`.
- Exact repair: first mutated V5 event now changes both `midi + 1` and `fret + 1`, preserving guitar-position validity while changing canonical identity.
- Strict expected exception remains `ValueError` matching `V5 source identity mismatch`.
- No support/decoder/proof algorithm or threshold changed.

### One-use workflow — REPAIRED / FROZEN / RUN TRIGGERED
- Workflow commit `369feb721bf2d2c30a27a7318dd6485afa0a1676`.
- Workflow blob `50caa7198f534473f9ced0317f02a8849d6a5396`.
- Only identity changes from previous workflow: old test blob replaced with repaired tests blob `cbcc8fa9...` in the preflight identity check and runtime source-identity gate.
- Workflow no-real-audio/no-reference source guard remains intact.
- This push is the single authorized CPU/generated/reference-free verification trigger. Result not yet recorded in this checkpoint.

## EXPLICIT NEXT STEPS
1. Read only the triggered Phase-C pre-audio verification run result/evidence.
2. If GO, persist exact run/job/artifact/proof/runtime identities; checkpoint; delete/seal the one-use workflow; checkpoint again.
3. If a new substantive failure appears, STOP and checkpoint before any further change.
4. **STOP before actual audio decoding/CQT analysis. Fresh explicit authorization is required for real-audio execution.**
5. Phase D/reference scoring remains unauthorized until separately frozen after a Phase-C real-audio GO artifact.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V147 A GO/SEALED; V147 B GO/SEALED.
- Repaired test and workflow identities are frozen; one CPU/generated/reference-free run is triggered/pending result.
- No calibration/gold/reference access, real-audio decode, analyzer integration, Modal/L4/GPU, main, or Production changes occurred.
