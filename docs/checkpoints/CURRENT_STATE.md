# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V147 Phase C preregistration/clarification/support are FROZEN. The reached-test pre-audio run failed on one invalid mutation fixture (10 passed, 1 failed) before generated proof execution. The narrowly preregistered test-fixture repair has now been applied and checkpointed; only the one-use workflow test-blob identity update remains before one authorized CPU/generated/reference-free verification run. Real-audio decoding/analysis remains STOP pending fresh explicit authorization. Accepted Rhythm family #10 remains active.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU/live/real audio without fresh explicit authorization.
- Gold SHA256 `18fd868ae960dfcddc1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark only, never unseen holdout.
- No automatic promotion.

## Accepted Rhythm baseline — UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Manifest `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`; blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- Canonical event count `1144`; event/PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; generated measures `113`; critical mismatch `1712`.
- Scores **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.

## V145 / V146
- Frozen V145 decoder blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- V146 CLOSED/SEALED after regression; no replay/retuning/promotion.

## V147 Phase A — COMPLETE / GO / SEALED
- Pitch implementation blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
- Run `33034629948`, job `98394561968`: 13 tests passed; proof GO 11/11.
- Proof payload SHA `3843912f0c8e5da95c3993783a84762ba01b046120a48db5e5a5c6c16a3d883e`.

## V147 Phase B — COMPLETE / GO / SEALED
- Run `33035123962`, job `98396067875`: SUCCESS; 8 tests passed; generated proof GO 5/5.
- Proof payload SHA `07848295a7a0b82cee4701db8ddf4505910d4955c2c6bd9587833cbb1656435a`.

## V147 Phase C — PRE-AUDIO ONLY / NO REAL AUDIO EXECUTION
### Frozen protocol identities
- Phase-C prereg blob `5c19ed572d17cc9a760f1b63ee03c1b2c4543d30`.
- Phase-C clarification blob `6ced1bae4cdaad8306b008827657afbb27a87dbc`.
- Workflow-repair prereg blob `d36b49e3e1519fd68e524a4ec12eba300c14b0da`.
- Test-fixture-repair prereg `docs/v147-phase-c-pre-audio-test-fixture-repair-preregistration.md`; freeze commit `81f6db17acf9265695c08824037b416515f03b00`; blob `aa74555976b826a4595cf1f472a2be0a173fb3d5`.
- Support blob `f4278ffaacaca3f66baf7a3112e2af0f3bc387cf` — unchanged.
- V147 pitch blob `49bce8b968406bb0d61ab61394954ef8a8303eb7` — unchanged.
- Proof harness blob `531384706b8b7444cf7ed22f414b47215e59b653` — unchanged.
- Canonical helper blob `088d44827fb23e20d9aeeb4944a672989af5846c` — unchanged.

### Accepted-family identity — unchanged
- Reconstructed accepted family #10 = 1144 events, SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`.
- Historical exact raw source-audio SHA remains `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; raw bytes are not present on branch and have not been read.

### Reached-test run — FAILED CLOSED / NO GENERATED PROOF
- Workflow repair applied at commit `b9868084935c6f221a1fb052e1f13926f1615a4e`; workflow blob `60c56eec4d3991b9183cbf8dce6c9fd853d85304`.
- Run `33036741821`, job `98400937803`: FAILURE.
- Frozen identity checks passed; no-real-audio/no-reference guard passed.
- Pytest: **10 passed, 1 failed**.
- Sole failure came from an internally inconsistent mutation fixture: first event MIDI changed `56 -> 57` while stringIndex `3`, fret `6` stayed unchanged, so canonical validation raised the correct pitch-position mismatch before the intended V5 identity-hash assertion.
- Generated proof command did not execute. Artifact `9632270270` contains failure evidence only; no GO proof/runtime/candidate exists.

### Test-fixture repair — APPLIED / CHECKPOINTED
- Repair commit `8fd35df1de2e515703d446f3deafe5a504beae9a`.
- Repaired tests blob `cbcc8fa90480b2a3b12546cf2193519fb46ade87`.
- Exact authorized change: the same first-event mutation now applies both `midi + 1` and `fret + 1`, preserving the guitar-position invariant while still changing canonical identity.
- Expected assertion remains strict and unchanged: `ValueError` matching `V5 source identity mismatch`.
- No support/decoder/proof algorithm, generated case, threshold, timing, frame, fingering, reconstruction, or canonicalization logic changed.

## EXPLICIT NEXT STEPS
1. Update only `.github/workflows/v147-phase-c-pre-audio-proof.yml` old test blob identity `e99f...` -> repaired test blob `cbcc8fa90480b2a3b12546cf2193519fb46ade87` in its identity checks/runtime gate.
2. That workflow edit may trigger exactly one new CPU/generated/reference-free pre-audio verification run.
3. If GO, persist exact test/proof/runtime/run/artifact identities; checkpoint; delete/seal the one-use workflow; checkpoint again.
4. If a new substantive failure appears, STOP and checkpoint before any further change.
5. **STOP before actual audio decoding/CQT analysis. Fresh explicit authorization is required for real-audio execution.**
6. Phase D/reference scoring remains unauthorized until separately frozen after a Phase-C real-audio GO artifact.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V147 A GO/SEALED; V147 B GO/SEALED.
- Phase-C repaired test identity is frozen at `cbcc8fa9...`; workflow identity update/run has not yet occurred in this checkpoint.
- No calibration/gold/reference access, real-audio decode, analyzer integration, Modal/L4/GPU, main, or Production changes occurred.
