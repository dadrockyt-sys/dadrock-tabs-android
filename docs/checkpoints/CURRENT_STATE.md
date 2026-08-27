# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V147 Phase A generated/reference-free contract is COMPLETE/GO/SEALED. V147 Phase B generated pitch-to-decoder integration is now separately authorized and FROZEN BEFORE IMPLEMENTATION. Phase B is CPU/generated/reference-free only and must leave V145/V147 upstream blobs unchanged. No calibration/gold access, no real audio, no analyzer integration, no Modal/L4/GPU, and no Production changes.**

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

## V145 frozen/proven foundation
- Stage1 / decoder `modal/v145_rhythm_decoder.py` blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`; proof run `33026865312` SUCCESS.
- Stage2 blob `5f86f57d0fd10774690d50528d51bad6e0392bf3`; proof run `33027229509` SUCCESS.
- Stage3 adapter blob `434d4b2582991c216df411455f232b8d211337c6`; proof blob `f55dcd1087f108d0d93c4a5a1a86cb5058ef4eb4`; run `33029862099` SUCCESS.
- Stage3 evaluator blob `d208abb3f180f8375d57d786941ff49d6813de1c`; proof blob `81c10bdcc39ce9e371fda60d2c3d107e671b8790`; run `33031101564` SUCCESS.

## V146 artifact-first protocol — CLOSED / SEALED
- Phase A generated artifact: SUCCESS/SEALED; candidate blob `61bda87e4a16b752bfaaf68c2d51e7020f31a7f8`; proof blob `abb8fcd1726bf9b8caa5bf8432adae2c6915a483`.
- Phase B fixed-artifact calibration run `33032332238`: SUCCESS/CONSUMED/SEALED but materially regressed musical metrics.
- V146 metrics: pitch `0.2830626450116009`; pitch/timing `0.044547563805104405`; string/fret/timing `0.0064965197215777265`; chord pitch-set `0.022757697456492636`; exact voicing `0.004016064257028112`; coverage/PDF `1.0`; critical mismatch count 1875.
- No replay, retuning, alternate construction, or promotion authorized.

## V147 Phase A — PITCH HYPOTHESIS BEFORE FINGERING / COMPLETE / GO / SEALED
- Original preregistration `docs/v147-pitch-hypothesis-preregistration.md`; blob `026d3bdbbebd385b7bdd4e896da569091b0265b7`.
- Frozen implementation `modal/v147_pitch_hypothesis.py`; blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
- Frozen tests blob `f71d1da6c52a6a737faca7ab4f8989fb702be96d`.
- Frozen proof harness blob `e9d28739cd19f095cb83807fd0b23c2b14b7c966`; schema14701.
- Attempt 1 run `33034467868` failed closed before proof because of a workflow import-path error after all 13 tests passed; never rerun/reinterpret.
- Execution-only repair prereg blob `a68e94eec9799aa334cce4d19df44ee768c4f21e` froze the only repair before change.
- Repaired run `33034629948`, job `98394561968`: SUCCESS; 13 tests passed; generated proof GO with 11/11 cases.
- Proof payload SHA256 `3843912f0c8e5da95c3993783a84762ba01b046120a48db5e5a5c6c16a3d883e`; proof file SHA256 `2cba17eaf5158fdcbe73f3207eb8a58c6b3100429c1065e524a42c2937cab67d`.
- Evidence persisted under `debug/v147-pitch-hypothesis/`; single-use workflow deleted/sealed in commit `da1e7378c238a0715f005b96da5b0a91c7a5d662`.
- Phase-A GO proves only the generated/reference-free contract, not real-song accuracy.

## V147 Phase B — GENERATED PITCH-TO-DECODER INTEGRATION / FROZEN BEFORE IMPLEMENTATION
- Preregistration: `docs/v147-phase-b-generated-decoder-integration-preregistration.md`.
- Freeze commit `1078b0b3ac2ef688065ced5fa7968e214093e5ec`; prereg blob `7d375755824dbf1dfc90fc7f62d85b11fb4d06b4`.
- Goal: apply frozen V147 pitch decisions to cloned generated Rhythm events, then feed them into untouched V145 `decode_nearest_timing_path` and prove corrected MIDI/string/fret identity end-to-end.
- Frozen upstream blobs MUST remain unchanged:
  - V145 decoder `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
  - V147 pitch hypothesis `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
  - V147 Phase-A tests `f71d1da6c52a6a737faca7ab4f8989fb702be96d`.
  - V147 Phase-A proof harness `e9d28739cd19f095cb83807fd0b23c2b14b7c966`.
- New code may exist only as a separate CPU-only integration adapter/tests/proof; no edits to V145 or Phase-A V147 files.
- Evidence is generated/direct numeric evidence keyed by original V145 `source_index`; no audio.
- Frozen cases: control passthrough, strong -1 and +1 end-to-end recovery, ambiguous fail-closed, malformed/missing fail-closed, caller immutability, cardinality preservation, deterministic output, and frozen-source identity.
- GO requires 0 source-cardinality, position-identity, and input-mutation violations plus all frozen generated cases passing and frozen upstream blob identities matching.
- Any reached-case failure is STOP; no threshold tuning or expectation changes.

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
2. Implement only the separately frozen V147 Phase-B CPU generated integration adapter, contract tests, and standalone proof.
3. Verify V145/V147 frozen upstream blobs remain unchanged and checkpoint all new Phase-B implementation identities before execution.
4. Execute one repository-native CPU/generated/reference-free proof only; no calibration/gold/audio/analyzer/Modal/GPU access.
5. Persist exact proof/runtime/run evidence, checkpoint GO/STOP, delete/seal the one-use workflow, then stop.
6. Any real audio, analyzer integration, reference scoring, GPU/Modal, V145 in-place integration, or Production work requires another separately frozen phase.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V147 Phase A remains GO/SEALED.
- V147 Phase B preregistration is now frozen before implementation.
- **Next: implement the Phase-B generated integration adapter/tests/proof without modifying frozen upstream files.**
