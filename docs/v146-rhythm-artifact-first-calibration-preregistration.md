# V146 Rhythm — Artifact-First Calibration Protocol Preregistration

Date frozen: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Status: **FROZEN BEFORE V146 GENERATED-ONLY ARTIFACT CONSTRUCTION AND BEFORE ANY V146 CALIBRATION ACCESS**

## Why this is a materially new protocol

The consumed V145 real Stage3 one-shot coupled workflow identity, candidate construction, freeze/PDF proof, calibration access, scoring, and persistence into one execution. It failed closed at workflow identity before candidate construction. That execution is consumed and must never be replayed.

V146 changes the execution unit itself, not the decoder or musical tuning: it separates generated-only candidate construction from calibration evaluation into two independently frozen phases. Phase A cannot access calibration material at all and persists a fixed candidate artifact plus construction proof. A future Phase B may score only that already-persisted artifact under a separately preregistered evaluation protocol. No Phase B is authorized by this document.

The V145 infrastructure failure may inform this safer CI separation only. It is not musical evidence and does not alter Stage1/Stage2/adapter parameters.

## Reused immutable musical components

No musical/model code is changed for V146 Phase A.

- Stage 1 `modal/v145_rhythm_decoder.py` blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- Stage 2 `modal/v145_rhythm_sequence_decoder.py` blob `5f86f57d0fd10774690d50528d51bad6e0392bf3`.
- Stage 3 generated-only adapter `validation/v145_rhythm_decoder/offline_stage3_adapter.py` blob `434d4b2582991c216df411455f232b8d211337c6`.
- Adapter tests `modal/tests/test_v145_rhythm_stage3_offline_adapter.py` blob `3eee7ae5253ad0eecbeb492eaa24216f0fa21fee`.
- Adapter CPU proof `debug/v145-rhythm-decoder/proofs/cpu-stage3-offline-adapter-proof.json` blob `f55dcd1087f108d0d93c4a5a1a86cb5058ef4eb4`.
- Canonical helper `validation/rhythm_holdout/canonical.py` blob `088d44827fb23e20d9aeeb4944a672989af5846c`.

## Immutable generated source

- Path `debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json`.
- Git blob `fe61f7ad53a4d71348a5113ecc9e3876eaad98d4`.
- Raw SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`.
- Exactly 1209 source events.
- Exactly measures 1..113.
- Tempo `129.19921875`, 4/4, E Standard.

## Phase A — generated-only artifact construction

Phase A is authorized by this preregistration. It must:

1. Verify the exact immutable Stage1/Stage2/adapter/test/proof/canonical/source identities above.
2. Compile and run the already-frozen Stage1/Stage2/adapter CPU contract tests.
3. Invoke `offline_stage3_adapter.py` exactly once against the immutable V5 source.
4. Write exactly one candidate artifact to `debug/v146-rhythm-artifact/generated-only-candidate.json`.
5. Independently verify the candidate:
   - schemaVersion `14503`;
   - classification `v145-rhythm-stage3-offline-generated-only-candidate`;
   - evaluationRole `generated-only-pre-reference-candidate`;
   - instrument Rhythm;
   - exactly 1209 events;
   - eventIndex exactly 0..1208 in source order;
   - MIDI sequence identical to immutable V5 source;
   - exactly measures 1..113;
   - candidate metadata event SHA equals canonical event SHA;
   - safety `referenceFree=true`, `professionalReferenceUsed=false`, `referenceRuntimeInputUsed=false`, `goldInputUsed=false`, `acceptedBaselineChanged=false`, `modalGpuUsed=false`, `liveAudioBenchmarkRun=false`.
6. Compute generated-only descriptive construction evidence only: candidate event SHA, changed-event count vs source, counts of changes to measure/step/stringIndex/fret, adapter statistics already emitted by the frozen adapter, and generated measure count. These values may describe the artifact but may not trigger alternate construction or tuning.
7. Persist a construction proof to `debug/v146-rhythm-artifact/generated-only-candidate-proof.json`.
8. Persist only those two V146 files. No freeze, renderer/PDF benchmark, accepted baseline read, gold read, score, ranking, fallback, alternate candidate, promotion decision, or live-audio operation occurs in Phase A.

## Phase A calibration-isolation rule

Phase A workflow/code must not read, parse, hash, `git hash-object`, `cat`, mention as a command argument, or otherwise inspect:
- `debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json`;
- `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`.

Phase A does not import or invoke `score_offline_stage3_candidate.py`, `score_rhythm_holdout.py`, or `score_selected_conjunction_candidate.py`.

## Phase A output/proof contract

Candidate path:
- `debug/v146-rhythm-artifact/generated-only-candidate.json`

Proof path:
- `debug/v146-rhythm-artifact/generated-only-candidate-proof.json`

Proof schemaVersion `14601`, proofType `v146-rhythm-generated-only-candidate-artifact`, and fields must include:
- immutable source raw SHA256;
- Stage1/Stage2/adapter blobs;
- candidate event count/SHA;
- generated measure count;
- changed-event and changed-field counts;
- adapter stats copied from candidate;
- `decoderCallCount=1`;
- `referenceFree=true`;
- `acceptedManifestRead=false`;
- `realGoldRead=false`;
- `calibrationScoreRun=false`;
- `candidateSearchRun=false`;
- `alternateCandidateConstructed=false`;
- `acceptedBaselineChanged=false`;
- `promotionAllowed=false`;
- `modalGpuUsed=false`;
- `liveAudioBenchmarkRun=false`.

Both output paths must be absent before Phase A. Phase A runs exactly once. After success, its workflow is deleted/sealed and the candidate/proof become immutable inputs to any separately preregistered Phase B.

## Phase B boundary — NOT YET AUTHORIZED

No calibration evaluation is authorized by this document. A future Phase B must be separately preregistered only after Phase A candidate/proof identities are known and sealed. It must consume exactly the persisted V146 candidate; it may not reconstruct, mutate, search, rank, or select another candidate.

## Promotion / interpretation

- Phase A produces no score.
- It cannot change the accepted baseline.
- Accepted family #10 remains **35.4% pitch / 6.7% pitch+timing / 5.5% string-fret+timing / 5.8% chord-voicing / 100% coverage / 100% PDF fidelity**.
- Any future calibration score remains benchmark evidence only until a distinct promotion protocol is frozen and succeeds.

## Safety

- CPU only.
- No Modal/L4/GPU.
- No live audio.
- No `/ai-tab` frontend, Bass, Lead, `freezeReady=false`, main, or Production changes.
- No musical parameter changes from the consumed V145 execution outcome.
