# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V147 Phase A is COMPLETE/GO/SEALED. V147 Phase B generated pitch-to-decoder integration has completed its single authorized repository-native CPU/generated/reference-free proof with GO. Exact proof/runtime/run evidence is persisted. The one-use workflow must now be deleted/sealed, then STOP. No calibration/gold access, no real audio, no analyzer integration, no Modal/L4/GPU, no V145 in-place integration, and no Production changes occurred.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU/live audio without fresh explicit authorization.
- Gold SHA256 `18fd868ae960dfcddc1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark only, never unseen holdout.
- No automatic promotion. Family #10 remains accepted unless a separate later promotion protocol is frozen and succeeds.

## Accepted Rhythm baseline — UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- **Pitch Content 35.4%**, **Pitch + timing 6.7%**, **String/fret + timing 5.5%**, **Chord/voicing 5.8%**, **Measure coverage 100%**, **PDF event fidelity 100%**.
- Exact: pitch `0.35406698564593303`; pitch/timing `0.06698564593301436`; string/fret/timing `0.05454545454545454`; chord pitch-set `0.0580511402902557`; exact voicing `0.0580511402902557`; coverage/PDF `1.0`.
- Accepted manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.

## V145/V146 status
- Frozen V145 decoder `modal/v145_rhythm_decoder.py`: blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- V146 remains CLOSED/SEALED after regression; no replay/retuning/promotion.
- Accepted family #10 remains active.

## V147 Phase A — COMPLETE / GO / SEALED
- Original prereg blob `026d3bdbbebd385b7bdd4e896da569091b0265b7`.
- Frozen pitch implementation blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
- Successful repaired run `33034629948`, job `98394561968`: 13 tests passed; generated proof GO 11/11.
- Proof payload SHA256 `3843912f0c8e5da95c3993783a84762ba01b046120a48db5e5a5c6c16a3d883e`.
- Phase-A workflow deleted/sealed in commit `da1e7378c238a0715f005b96da5b0a91c7a5d662`.

## V147 Phase B — GENERATED PITCH-TO-DECODER INTEGRATION / GO / EVIDENCE PERSISTED
### Frozen preregistration
- `docs/v147-phase-b-generated-decoder-integration-preregistration.md`.
- Freeze commit `1078b0b3ac2ef688065ced5fa7968e214093e5ec`; blob `7d375755824dbf1dfc90fc7f62d85b11fb4d06b4`.
- Scope: generated/direct numeric pitch evidence -> cloned events -> untouched V145 decoder only.

### Frozen implementation identities
- Adapter `modal/v147_phase_b_generated_integration.py`; commit `2dad4186ea90904098287154f0016263723ee3f4`; blob `76ce80ef998ca54797b1df8b6fb7ab46440d9a04`.
- Tests `modal/tests/test_v147_phase_b_generated_integration.py`; commit `19e2c07e4b1d1258361472bd242ac58b7ad95c8e`; blob `9a1fc8671a9e2f43c6c2161d70c0a242f929a4dc`.
- Proof harness `modal/v147_phase_b_generated_integration_cpu_proof.py`; commit `5ceeae807049eb8c1384f811d742291e9016b2e9`; blob `969403fd12963ccfefc4a9d379dbc800656b021e`; schema14711.
- Frozen upstream V145/V147 blobs re-verified unchanged before execution.

### Single authorized repository-native execution — SUCCESS / GO / CONSUMED
- Workflow creation commit `dcdde07273bfc3c287f3b285015447c84d055601`; workflow blob `2cc156feff078328b5bf11641f2dea12e4b4e42d`.
- Run `33035123962`, job `98396067875`: **SUCCESS**.
- Artifact `9631715259`, 3476 bytes, digest `sha256:b08ad3adbce6269ef7337361ff123c0d364f63ac12ec74c7204ac3e94b936279`.
- Frozen upstream hash-check step: SUCCESS.
- Contract tests: **8 passed in 0.06s**.
- Generated integration proof: **GO**, `5/5` proof cases passed.
- Metrics: inputEvents `5`; normalizedEvidence `5`; decisions `5`; pitchChanges `2`; controlFlips `0`; strongAlternates `2`; strongAlternatesRecovered `2`; ambiguousCases `1`; ambiguousKept `1`; malformedCases `1`; malformedKept `1`; sourceCardinalityViolations `0`; positionIdentityViolations `0`; inputMutationViolations `0`; deterministic `true`; frozenSourceIdentityMatch `true`.
- Proof payload SHA256 `07848295a7a0b82cee4701db8ddf4505910d4955c2c6bd9587833cbb1656435a`.
- Formatted proof file SHA256 `e88f8e6e67494acf9aa97389f91fc27156cc3c834cf2e9d717f638f47796a366`.
- Runtime: Python `3.12.14`; pytest `9.1.1`; Linux/X64; pytestExitCode `0`; proofExitCode `0`; gate `GO`.
- Runtime source identities: V145 decoder `2fd979a...`; V147 pitch `49bce8b...`; Phase-B adapter `76ce80e...`; tests `9a1fc86...`; proof harness `969403f...`.
- Flags: referenceFree=true; calibrationReferenceRead=false; goldRead=false; realAudioRead=false; analyzerIntegrated=false; modalGpuUsed=false; productionIntegrated=false.

### Persisted Phase-B evidence
- `debug/v147-phase-b-generated-integration/generated-integration-proof.json`; persistence commit `55fe97a0998cdc4c91047bbb0206ab4b70afb1b5`; Git blob `11152ad896e06f8c2fc9390412b3cc6638a6c590`.
- `debug/v147-phase-b-generated-integration/runtime-evidence.json`; persistence commit `59cec8ff6093c00567c89affe74f2475360731a1`; Git blob `63006002f550e9a12f885b668ce58a81a116e90d`.
- `debug/v147-phase-b-generated-integration/success-execution-record.json`; persistence commit `daa79937664d8c039941baafbfe50274335dfb8b`; Git blob `9af3564475ad69d7610657c190f04fb0773cd441`.
- Phase-B GO proves only the generated/reference-free pitch-to-decoder integration contract. It does not prove real-song accuracy.

## Frozen validation/render identities
- canonical `088d44827fb23e20d9aeeb4944a672989af5846c`
- freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`
- scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- full-score helper `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`
- PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`
- render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`
- evaluator `d208abb3f180f8375d57d786941ff49d6813de1c`
- accepted manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.

## EXPLICIT NEXT STEPS
1. Keep V146 and V147 Phase A sealed; accepted family #10 remains active.
2. V147 Phase-B run `33035123962` is consumed; do not rerun.
3. Delete/seal `.github/workflows/v147-phase-b-generated-integration-proof.yml` now that exact evidence is persisted.
4. Checkpoint the deletion and STOP Phase B at generated/reference-free GO.
5. Any real audio, analyzer integration, reference scoring, Modal/GPU, V145 in-place integration, or Production work requires a separately authorized and frozen next phase before execution.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V147 Phase A remains GO/SEALED.
- V147 Phase B generated/reference-free pitch-to-decoder integration is **GO** with exact evidence persisted.
- **Next: delete/seal the single-use Phase-B workflow, checkpoint deletion, then STOP.**
