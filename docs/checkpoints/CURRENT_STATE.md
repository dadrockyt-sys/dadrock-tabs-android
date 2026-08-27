# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V147 Phase A generated/reference-free contract is COMPLETE/GO and SEALED. Exact repository-native proof/runtime/run evidence is persisted and the single-use workflow has been deleted. Accepted Rhythm family #10 remains active. No calibration/gold access, no Modal/L4/GPU/live audio, no V145 integration, and no production promotion occurred. STOP here unless a separately authorized/frozen next phase is created.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- No Modal/L4/GPU/live audio without fresh explicit authorization.
- Gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; calibration benchmark only, never unseen holdout.
- No automatic promotion. Family #10 remains accepted unless a separate later promotion protocol is frozen and succeeds.

## Accepted Rhythm baseline — UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- **Pitch Content 35.4%**, **Pitch + timing 6.7%**, **String/fret + timing 5.5%**, **Chord/voicing 5.8%**, **Measure coverage 100%**, **PDF event fidelity 100%**.
- Exact: pitch `0.35406698564593303`; pitch/timing `0.06698564593301436`; string/fret/timing `0.05454545454545454`; chord pitch-set `0.0580511402902557`; exact voicing `0.0580511402902557`; coverage/PDF `1.0`.
- 1144 events /113 measures / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; critical mismatch count 1712.
- Accepted manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68` (re-verified unchanged after V146 sealing).

## V145 frozen/proven foundation
- Stage1 blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`; proof run `33026865312` SUCCESS.
- Stage2 blob `5f86f57d0fd10774690d50528d51bad6e0392bf3`; proof run `33027229509` SUCCESS.
- Stage3 adapter blob `434d4b2582991c216df411455f232b8d211337c6`; proof blob `f55dcd1087f108d0d93c4a5a1a86cb5058ef4eb4`; run `33029862099` SUCCESS.
- Stage3 evaluator blob `d208abb3f180f8375d57d786941ff49d6813de1c`; proof blob `81c10bdcc39ce9e371fda60d2c3d107e671b8790`; run `33031101564` SUCCESS.
- Frozen evaluator order: candidate-only validation -> pre-reference freeze/PDF gate -> candidate/freeze/PDF identity -> accepted manifest -> only then gold hash/validate -> exactly one score.

## First real V145 execution — CONSUMED / FAILED CLOSED / SEALED
- Run `33031523386`, job `98384901171`: workflow identity failure before candidate/calibration work.
- No candidate, gold read, score, or result existed. Workflow/trigger sealed. Never retry that execution.

## V146 artifact-first protocol — CLOSED / SEALED
### Overall preregistration
- `docs/v146-rhythm-artifact-first-calibration-preregistration.md`; creation commit `86729595bab64ac80b82180532ee4dc94fca9817`; blob `0125201e86389b21dee3ceb2e7ecd25dc67dfe84`.
- V146 separates generated-only artifact construction from later evaluation; no musical parameter changed from V145.

### Phase A — GENERATED-ONLY ARTIFACT / SUCCESS / SEALED
- Workflow creation commit `246d7dba0f7b3d2955feed90446353de8302da6f`; workflow blob `63812af5182795995129b961f8926b9a2b04dd1d`.
- Run `33031802198`, job `98385781107`: SUCCESS; persistence commit `e5d7d9dd9bdce8bf0eeee7f2a8207475ddbd31d3`; workflow deletion `a79e9717e0dbebdd730dfabaef068c78b45a5109`.
- Candidate `debug/v146-rhythm-artifact/generated-only-candidate.json`; Git blob `61bda87e4a16b752bfaaf68c2d51e7020f31a7f8`.
- Construction proof `debug/v146-rhythm-artifact/generated-only-candidate-proof.json`; blob `abb8fcd1726bf9b8caa5bf8432adae2c6915a483`; schema14601.
- Candidate: **1209 events /113 measures / canonical event SHA `2de0a686cfd797a19aa02af735aa2bfaf0e65245ec85a5148c71f8b8b3a77c40`**.
- Generated-only changes vs V5 source: 871 events changed; stringIndex871; fret871; measure0; step0. MIDI/event count/order/measure set preserved.
- Phase A proof: referenceFree=true, acceptedManifestRead=false, realGoldRead=false, calibrationScoreRun=false, alternateCandidateConstructed=false, acceptedBaselineChanged=false, modalGpuUsed=false.

### Phase B — FIXED-ARTIFACT CALIBRATION / SUCCESS / CONSUMED / SEALED
- Prereg `docs/v146-rhythm-phase-b-calibration-evaluation-preregistration.md`; creation commit `791aef9a0e8f48cd7d1e3672b2fa0b2469fa6a2c`; frozen prereg blob `82bd04d819f26106a831f67a1a61ccba6e876c08`.
- Workflow creation commit `0008c69cc05e7dac67eb9684ef022e10dc375336`; workflow blob `1331b350525865008907b1f9107b9363a2cc91dc`.
- Run `33032332238`, job `98387433761`, attempt1: **SUCCESS**.
- Persistence commit `6e6bc3fd0831b149d3e99323c20162ccd32fddc8`; workflow deletion/sealing `9f2f1aeef4a730e919cceee2eccc31c3a25dfd37`.
- Score `debug/v146-rhythm-artifact/calibration-score.json`; blob `bed3325573e86748c3fc409d4bca00970e087ce2`.
- Proof `debug/v146-rhythm-artifact/calibration-evaluation-proof.json`; blob `7bfd6fe6eee33cd2012652c4aeb2186ed5657b5b`; schema14602.
- V146 metrics: pitch `0.2830626450116009`; pitch/timing `0.044547563805104405`; string/fret/timing `0.0064965197215777265`; chord pitch-set `0.022757697456492636`; exact voicing `0.004016064257028112`; coverage/PDF `1.0`; critical mismatch count1875.
- Candidate minus accepted: pitch `-0.07100434063433214`; pitch/timing `-0.02243808212790995`; string/fret/timing `-0.048048934823876815`; chord pitch-set `-0.03529344283376307`; exact voicing `-0.05403507603322759`; critical mismatches `+163`.
- Interpretation: V146 materially regressed musical calibration metrics. No replay, retuning, alternate construction, or promotion is authorized.

## V147 Phase A — PITCH HYPOTHESIS BEFORE FINGERING / COMPLETE / GO / SEALED
- Original preregistration: `docs/v147-pitch-hypothesis-preregistration.md`; initial freeze commit `a0bb5412be8830fca27726ad2067a713e8441089`; aggregation clarification `d1dcb96943af758cdd54843637366701f25b4b22`; prereg blob `026d3bdbbebd385b7bdd4e896da569091b0265b7`.
- Frozen implementation `modal/v147_pitch_hypothesis.py`; blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
- Frozen tests `modal/tests/test_v147_pitch_hypothesis.py`; blob `f71d1da6c52a6a737faca7ab4f8989fb702be96d`.
- Frozen proof harness `modal/v147_pitch_hypothesis_cpu_proof.py`; blob `e9d28739cd19f095cb83807fd0b23c2b14b7c966`; schema14701.
- Candidate family `{midi-1,midi,midi+1}` within `[40,88]`; fail closed on missing/non-finite/tied/weak/ambiguous evidence.
- No V145 decoder, threshold, generated case, evidence representation, scoring rule, or production path changed.

### Repository-native attempt 1 — CONSUMED / FAILED CLOSED BEFORE PROOF
- Workflow creation commit `aa7c3dc69367749a228137b7e2cb14cbf72c8610`.
- Run `33034467868`, job `98394054352`, artifact `9631482983`: **FAILURE**.
- Tests: `13 passed in 0.14s`; generated proof did not execute because direct file invocation caused `ModuleNotFoundError: No module named 'modal'`.
- Exact failed execution record: `debug/v147-pitch-hypothesis/phase-a-attempt1-execution-record.json`; commit `69f8019154014b8fa19de9b5eeebc92e1eb8ba71`.
- Attempt 1 remains consumed and MUST NOT be rerun/reinterpreted.

### Execution-only repair — FROZEN BEFORE CHANGE
- Repair prereg: `docs/v147-phase-a-execution-repair-preregistration.md`; freeze commit `a26525ec9a1320d320ca6afa5f649ee281e2af1c`; blob `a68e94eec9799aa334cce4d19df44ee768c4f21e`.
- Authorized change: direct file invocation -> module invocation only.
- Workflow repair commit `5782eabd3b515f0cca022522cd628fce55a548cc`; workflow blob `03dcefc46af1a9629eb222fb9beceea83b93930f`.
- Implementation/test/proof blobs re-verified unchanged after repair.

### Repaired repository-native execution — SUCCESS / GO / CONSUMED
- Run `33034629948`, job `98394561968`, attempt1: **SUCCESS**.
- Artifact `9631542077`, size 2980 bytes, digest `sha256:7df04ef5e771000c966bef807ab624f9de108f8c76701163a4312e2aaa9d4825`.
- Tests: **13 passed in 0.13s**.
- Frozen generated proof: **GO**, `11/11` cases passed.
- Metrics: correctControls `1`; correctControlsFlipped `0`; deliberateMislabels `2`; deliberateMislabelsRecovered `2`; ambiguousCases `3`; ambiguousCasesKept `3`; rangeViolations `0`; malformedCases `3`; malformedFailClosed `3`; deterministic `true`.
- Proof payload SHA256 `3843912f0c8e5da95c3993783a84762ba01b046120a48db5e5a5c6c16a3d883e`.
- Formatted proof file SHA256 `2cba17eaf5158fdcbe73f3207eb8a58c6b3100429c1065e524a42c2937cab67d`.
- Runtime: Python `3.12.14`; numpy `2.5.2`; pytest `9.1.1`; Linux/X64; `pytestExitCode=0`; `proofExitCode=0`; gate `GO`.
- Runtime confirms implementation/test/proof blobs exactly `49bce8...`, `f71d1d...`, `e9d287...`.
- Flags: referenceFree=true; calibrationReferenceRead=false; goldRead=false; modalGpuUsed=false; liveAudioUsed=false; productionIntegrated=false.

### Persisted V147 evidence
- `debug/v147-pitch-hypothesis/cpu-generated-proof.json`; commit `89e84eedccd40db615d46d22074e410697094b20`; Git blob `32611047a69222dbf6a3e8ad6d3d60241c029ad8`.
- `debug/v147-pitch-hypothesis/runtime-evidence.json`; commit `23f79fcd0e953b29cdd8e9b488ccce0530e72a45`; Git blob `5e8ee384ec1abf028147478f61388465f50a4fdb`.
- `debug/v147-pitch-hypothesis/phase-a-success-execution-record.json`; commit `7e28caeef508bdbfd860d4b6cc0a7c8941072eaf`; Git blob `bf9324d383d610920cd9361ead75c66f9fc29644`.
- Workflow deletion/sealing commit: `da1e7378c238a0715f005b96da5b0a91c7a5d662`.
- The Phase-A GO is **only** for the frozen generated/reference-free contract. It does not establish real-song accuracy and does not authorize live/reference evaluation, Modal/GPU execution, V145 integration, or production promotion.

## Frozen validation/render identities
- canonical `088d44827fb23e20d9aeeb4944a672989af5846c`
- freeze `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`
- scorer `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- full-score helper `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`
- PDF fidelity `5e1564216873046237fb545078a04a6b18f72b27`
- render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`
- evaluator `d208abb3f180f8375d57d786941ff49d6813de1c`
- accepted manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`
- calibration gold SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.

## EXPLICIT NEXT STEPS
1. Keep V146 sealed; accepted family #10 remains active.
2. Keep V147 Phase A sealed at generated/reference-free **GO**; do not rerun either repository-native execution.
3. Do not integrate V147 into V145 or Production under the current authorization.
4. Any later live/reference/Modal/GPU evaluation, real-song accuracy check, decoder integration, or production promotion requires a separately authorized and frozen next phase before execution.
5. Continue saving this checkpoint frequently whenever work resumes on this branch.

## Current stop point
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.
- V146 remains consumed/closed/sealed with regression.
- V147 Phase A generated/reference-free contract is **GO and SEALED** with exact repository-native evidence persisted.
- Single-use workflow is deleted/sealed in commit `da1e7378c238a0715f005b96da5b0a91c7a5d662`.
- No calibration/gold, Modal/L4/GPU, live audio, V145 integration, main, or Production changes occurred.
- **STOP. Next work requires a newly authorized/frozen phase.**
