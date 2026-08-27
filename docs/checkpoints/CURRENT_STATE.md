# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V147 Phase C preregistration/clarification/support are FROZEN. The repaired pre-audio run reached pytest and FAILED CLOSED on one test-fixture construction issue (10 passed, 1 failed) before generated proof execution. A narrow test-fixture-only repair is now FROZEN BEFORE CHANGE. Real-audio decoding/analysis remains STOP pending fresh explicit authorization. Accepted Rhythm family #10 remains active.**

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
- Exact: pitch `0.35406698564593303`; pitch/timing `0.06698564593301436`; string/fret/timing `0.05454545454545454`; chord pitch-set `0.0580511402902557`; exact voicing `0.0580511402902557`; coverage/PDF `1.0`.

## V145 / V146
- Frozen V145 decoder blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- V146 CLOSED/SEALED after regression; no replay/retuning/promotion.

## V147 Phase A — COMPLETE / GO / SEALED
- Prereg blob `026d3bdbbebd385b7bdd4e896da569091b0265b7`.
- Pitch implementation blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
- Run `33034629948`, job `98394561968`: 13 tests passed; proof GO 11/11.
- Proof payload SHA `3843912f0c8e5da95c3993783a84762ba01b046120a48db5e5a5c6c16a3d883e`.
- Workflow deleted/sealed `da1e7378c238a0715f005b96da5b0a91c7a5d662`.

## V147 Phase B — COMPLETE / GO / SEALED
- Prereg freeze commit `1078b0b3ac2ef688065ced5fa7968e214093e5ec`; blob `7d375755824dbf1dfc90fc7f62d85b11fb4d06b4`.
- Adapter `76ce80ef998ca54797b1df8b6fb7ab46440d9a04`; tests `9a1fc8671a9e2f43c6c2161d70c0a242f929a4dc`; proof harness `969403fd12963ccfefc4a9d379dbc800656b021e`.
- Run `33035123962`, job `98396067875`: SUCCESS; 8 tests passed; generated proof GO 5/5.
- Proof payload SHA `07848295a7a0b82cee4701db8ddf4505910d4955c2c6bd9587833cbb1656435a`.
- Workflow deleted/sealed `7259c433589d505d9e9de56f45b0e1db9d4c975e`.

## V147 Phase C — REAL-AUDIO ARTIFACT-FIRST / PRE-AUDIO CONTRACT FROZEN / NO AUDIO EXECUTION
### Protocol
- Prereg `docs/v147-phase-c-real-audio-artifact-preregistration.md`; freeze commit `9a452bc29f6e1edcad9ef2a45a1c2a52267277b4`; blob `5c19ed572d17cc9a760f1b63ee03c1b2c4543d30`.
- Clarification `docs/v147-phase-c-preregistration-clarification.md`; freeze `fe16ac54a80cadd6f0b59bbec6251a24236fc476`; blob `6ced1bae4cdaad8306b008827657afbb27a87dbc`.
- Authoritative V147 blob uses octave weight `0.25`; all CQT evidence extraction/decision math delegates to that frozen implementation.
- Historical exact raw source-audio SHA `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`, from sealed V144 workflow blob `a9bef022032f2d5195dc54ba2a5bd9d7629686da`.
- Raw source audio bytes are not present on branch; no substitute permitted.

### Frozen accepted-family reconstruction chain — reference-free
1. V5 1209 events SHA `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
2. Triple prune -> 1144 / SHA `68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3`.
3. Same-string pitch shift -> SHA `b6e1f8a8be150943d7224c74f9193b1b4050454620063846f6f5f5c773d4cbf6`.
4. Pitch-position shift -> SHA `5b36270aaeafa73b2e25722e2576a40424ce5951dcfd2b5d769746bd9eb07e0d`.
5. Singleton replacement -> accepted 1144 / SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`.

### Frozen pre-audio support identities
- Support `modal/v147_phase_c_artifact_support.py`; blob `f4278ffaacaca3f66baf7a3112e2af0f3bc387cf`.
- Pre-repair tests `modal/tests/test_v147_phase_c_artifact_support.py`; blob `e99f791cd0ab401a9e393ab9b89a6b167cee3c7f`.
- Proof harness `modal/v147_phase_c_cpu_proof.py`; blob `531384706b8b7444cf7ed22f414b47215e59b653`; schema `14721`.
- No audio decode/CQT creation exists in this support code.

### Workflow repair and reached-test run
- Workflow-repair prereg `docs/v147-phase-c-pre-audio-workflow-repair-preregistration.md`; freeze commit `4db0900fbcd140c6b68ed5bf240c990225293f76`; blob `d36b49e3e1519fd68e524a4ec12eba300c14b0da`.
- Frozen repair applied at commit `b9868084935c6f221a1fb052e1f13926f1615a4e`; repaired workflow blob `60c56eec4d3991b9183cbf8dce6c9fd853d85304`.
- Run `33036741821`, job `98400937803`: FAILURE after reaching pytest.
- Frozen identity verification passed. No-real-audio/no-reference guard passed.
- Pytest result: **10 passed, 1 failed**.
- Sole failure: `test_materializer_fails_closed_if_v5_source_changes` changed first-event MIDI `56 -> 57` but left stringIndex `3`, fret `6`, so canonical validation correctly raised `pitch-position mismatch: stringIndex=3 fret=6 midi=57 expected=56` before the intended V5 hash-identity gate.
- Workflow shell stopped at pytest failure, so generated proof did **not** execute. Uploaded artifact `9632270270` contains only the failure evidence path; no GO proof/runtime exists.
- No candidate, real-audio read/decode, CQT, reference/gold access, score, Modal/GPU, `main`, or Production work occurred.

### Test-fixture-only repair — FROZEN BEFORE CHANGE
- Prereg `docs/v147-phase-c-pre-audio-test-fixture-repair-preregistration.md`.
- Freeze commit `81f6db17acf9265695c08824037b416515f03b00`.
- Frozen prereg blob `aa74555976b826a4595cf1f472a2be0a173fb3d5`.
- Authorized test change only: in `test_materializer_fails_closed_if_v5_source_changes`, retain the existing first-event `midi + 1` mutation and add exactly `fret + 1` on that same event so the mutated event remains a valid guitar position and reaches the intended exact V5 identity-hash guard.
- Keep expected exception unchanged: `ValueError` matching `V5 source identity mismatch`; do **not** weaken to generic fail-closed acceptance.
- Authorized workflow change only: replace old test blob identity with the new repaired test blob identity (and optionally verify this repair-prereg blob for provenance). No generated proof cases/logic or frozen algorithm identities may change.
- Exactly one new CPU/generated/reference-free pre-audio verification run is authorized after repair/checkpoint. If it passes, persist evidence and seal/delete workflow. If a new substantive failure appears, STOP/checkpoint.

## Frozen Phase-C front end for later separately authorized audio execution
- mono 22050 Hz; HPSS margin `(1.0,6.0)`; CQT hop 128; 48 bins/octave; fmin MIDI 40; 243 bins.
- time mapping 129.19921875 BPM, 4 steps/beat; frozen frame window.
- V147 candidate ±1; band ±0.30; baseline ±2.0 excluding ±0.75; DB floor `1e-8`; octave weight `0.25`; thresholds `3.0/3.0/2.0 dB`; fail closed.
- timing/order/count/measure/metadata fixed; only MIDI/string/fret may change; V145 timing lattice forbidden.

## Frozen validation/render identities
- canonical `088d44827fb23e20d9aeeb4944a672989af5846c`
- freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`
- scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- full-score helper `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`
- PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`
- render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`
- evaluator `d208abb3f180f8375d57d786941ff49d6813de1c`

## EXPLICIT NEXT STEPS
1. Keep V146, V147 A, and V147 B sealed; family #10 remains accepted.
2. Apply exactly the frozen test-fixture repair (`midi +1`, `fret +1` on the same first V5 event); checkpoint new test blob.
3. Update only the one-use workflow test-blob identity (and provenance guard if added); checkpoint workflow blob.
4. Execute exactly one new CPU/generated/reference-free pre-audio verification run. No real audio may be supplied/read.
5. If GO, persist exact run/job/artifact/proof/runtime identities; checkpoint; delete/seal workflow; checkpoint again.
6. **STOP before actual audio decoding/CQT analysis. Fresh explicit authorization is required for real-audio execution.**
7. Phase D/reference scoring remains unauthorized until a separately frozen protocol after a Phase-C real-audio GO artifact.

## Current stop point
- Accepted scores **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V147 A GO/SEALED; V147 B GO/SEALED.
- Phase C pre-audio reached tests; 10/11 passed; one invalid mutation fixture blocked the intended identity-gate assertion.
- Test-fixture repair is frozen before change at `81f6db17...`; no repair has yet been applied in this checkpoint.
- No calibration/gold/reference access, real-audio decode, analyzer integration, Modal/L4/GPU, main, or Production changes occurred.
