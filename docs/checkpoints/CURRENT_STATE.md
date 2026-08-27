# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V147 Phase A is COMPLETE/GO/SEALED. V147 Phase B generated pitch-to-decoder integration preregistration is frozen and its new CPU-only adapter/tests/proof are now committed. Frozen V145/V147 upstream blobs were re-verified unchanged after implementation. Repository-native Phase-B proof execution is next. No calibration/gold access, no real audio, no analyzer integration, no Modal/L4/GPU, and no Production changes.**

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
- 1144 events /113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; critical mismatch count 1712.
- Accepted manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.

## V145/V146 status
- Frozen V145 decoder `modal/v145_rhythm_decoder.py`: blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- V146 remains CLOSED/SEALED after its calibration regression; no replay/retuning/promotion.
- Accepted family #10 remains active.

## V147 Phase A — COMPLETE / GO / SEALED
- Original prereg blob `026d3bdbbebd385b7bdd4e896da569091b0265b7`.
- Frozen pitch implementation blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
- Frozen Phase-A tests blob `f71d1da6c52a6a737faca7ab4f8989fb702be96d`.
- Frozen Phase-A proof harness blob `e9d28739cd19f095cb83807fd0b23c2b14b7c966`.
- Successful repaired run `33034629948`, job `98394561968`: 13 tests passed; generated proof GO 11/11.
- Proof payload SHA256 `3843912f0c8e5da95c3993783a84762ba01b046120a48db5e5a5c6c16a3d883e`; proof file SHA256 `2cba17eaf5158fdcbe73f3207eb8a58c6b3100429c1065e524a42c2937cab67d`.
- Phase-A workflow deleted/sealed in commit `da1e7378c238a0715f005b96da5b0a91c7a5d662`.

## V147 Phase B — GENERATED PITCH-TO-DECODER INTEGRATION / FROZEN / IMPLEMENTED / PROOF PENDING
### Frozen preregistration
- `docs/v147-phase-b-generated-decoder-integration-preregistration.md`.
- Freeze commit `1078b0b3ac2ef688065ced5fa7968e214093e5ec`; blob `7d375755824dbf1dfc90fc7f62d85b11fb4d06b4`.
- Scope is generated/direct numeric pitch evidence -> cloned events -> untouched V145 decoder only.
- No audio/reference/analyzer/GPU/Production access is authorized.

### Phase-B implementation identities
- New adapter `modal/v147_phase_b_generated_integration.py`; creation commit `2dad4186ea90904098287154f0016263723ee3f4`; blob `76ce80ef998ca54797b1df8b6fb7ab46440d9a04`.
- New contract tests `modal/tests/test_v147_phase_b_generated_integration.py`; creation commit `19e2c07e4b1d1258361472bd242ac58b7ad95c8e`; blob `9a1fc8671a9e2f43c6c2161d70c0a242f929a4dc`.
- New standalone proof `modal/v147_phase_b_generated_integration_cpu_proof.py`; creation commit `5ceeae807049eb8c1384f811d742291e9016b2e9`; blob `969403fd12963ccfefc4a9d379dbc800656b021e`; schema14711.
- Adapter clones caller events, applies frozen V147 by V145 `source_index`, adds canonical `midi` only for selected alternates, then calls untouched V145 `decode_nearest_timing_path`.
- Tests cover control passthrough, strong -1/+1 end-to-end recovery, ambiguous/missing fail-closed, caller immutability, source cardinality, deterministic serialization, and decoded MIDI/string/fret identity.
- Proof additionally checks frozen V145/V147 source blob identities at runtime and includes them in the GO/STOP gate.

### Frozen upstream identity re-verification after Phase-B implementation
- V145 decoder re-fetched unchanged: `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- V147 pitch hypothesis re-fetched unchanged: `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
- No frozen upstream file was edited in Phase B.

## Frozen validation/render identities
- canonical `088d44827fb23e20d9aeeb4944a672989af5846c`
- freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`
- scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- full-score helper `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`
- PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`
- render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`
- evaluator `d208abb3f180f8375d57d786941ff49d6813de1c`
- accepted manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`
- calibration gold SHA256 `18fd868ae960dfcddc1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.

## EXPLICIT NEXT STEPS
1. Keep V146 and V147 Phase A sealed; accepted family #10 remains active.
2. Execute only the frozen V147 Phase-B CPU/generated/reference-free tests and standalone proof.
3. The one-use workflow must verify frozen upstream blobs and may not read calibration/gold/audio/analyzer data.
4. Persist exact proof/runtime/run/artifact evidence and checkpoint GO/STOP.
5. If any reached frozen case fails, STOP with no retuning or second musical implementation. If GO, delete/seal the one-use workflow and stop.
6. Any real audio, analyzer integration, reference scoring, Modal/GPU, V145 in-place integration, or Production work requires another separately frozen phase.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V147 Phase A remains GO/SEALED.
- V147 Phase B preregistration and implementation are frozen; upstream identities are unchanged.
- **Next: execute one repository-native CPU/generated/reference-free Phase-B proof and record exact evidence.**
