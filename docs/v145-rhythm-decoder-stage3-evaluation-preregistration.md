# V145 Rhythm Decoder — Stage 3 Evaluation Harness Preregistration

Date frozen: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Status: **FROZEN BEFORE EVALUATION-HARNESS IMPLEMENTATION AND BEFORE ANY REAL STAGE 3 CANDIDATE OR SCORE**

This addendum freezes only the evaluation process that follows the already-frozen/generated-only Stage 3 adapter. It does not alter Stage 1, Stage 2, the Stage 3 adapter, or any candidate-construction rule.

## Frozen implementation path

`validation/v145_rhythm_decoder/score_offline_stage3_candidate.py`

Synthetic evaluation-order tests:

`modal/tests/test_v145_rhythm_stage3_offline_score.py`

## Immutable dependencies

- Candidate adapter blob: `434d4b2582991c216df411455f232b8d211337c6`.
- Stage 3 adapter CPU proof blob: `f55dcd1087f108d0d93c4a5a1a86cb5058ef4eb4`.
- Frozen scorer primitives: `validation/rhythm_holdout/score_rhythm_holdout.py`, blob `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`.
- Frozen full-score helper: `validation/v144_rhythm_calibration/score_selected_conjunction_candidate.py`, blob `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`; only `score_full_candidate(events, reference)` may be reused.
- Frozen canonical helper blob `088d44827fb23e20d9aeeb4944a672989af5846c`.
- Frozen PDF-fidelity helper blob `5e1564216873046237fb545078a04a6b18f72b27`.
- Accepted comparison manifest: `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`, blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- Calibration reference: `debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json`, raw SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.

## Evaluation API and mandatory order

The evaluation harness takes exactly five positional paths:
1. completed Stage 3 freeze directory;
2. completed Stage 3 candidate JSON;
3. calibration-reference JSON path;
4. accepted-family-#10 manifest path;
5. output score-report path.

It must perform these operations in this order:

1. Load/validate only the candidate JSON and candidate identity fields. Do not open the calibration reference or accepted calibration manifest yet.
2. Call frozen `score_rhythm_holdout.validate_pre_reference(freeze_dir)`. This must prove the freeze manifest/snapshot are reference-free, PDF fidelity has already been verified, PDF event fidelity is exactly `1.0`, and the frozen/PDF event SHA identities match.
3. Canonicalize candidate `renderEvents`; require exactly 1209 events, candidate event SHA equal candidate metadata, frozen event count/SHA equal candidate count/SHA, exactly 113 generated measures, source eventIndex sequence 0..1208, and candidate safety flags `referenceFree=true`, `professionalReferenceUsed=false`, `referenceRuntimeInputUsed=false`, `goldInputUsed=false`, `acceptedBaselineChanged=false`.
4. Only after steps 1–3 pass may the harness read any calibration material.
5. Read the accepted-family-#10 manifest and require exact accepted identity: name `singleton-onset-replace-be9e9aa7a734e3cd`, selected event count 1144, selected event SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`, 113 measures, PDF fidelity 1.0, full calibration critical mismatch count 1712, and accepted metric values exactly as recorded below.
6. Read calibration-reference bytes only now; require SHA256 exactly `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; parse and pass frozen `score_rhythm_holdout.validate_reference`.
7. Score the already-frozen candidate exactly once with frozen `score_full_candidate(frozen_events, reference)`.
8. Attach PDF event fidelity `1.0` to the candidate gated metrics and compute candidate-minus-accepted deltas for every gated metric plus critical mismatch delta.
9. Write one deterministic report; no candidate construction, fallback, search, ranking, mutation, alternate score, or promotion decision may occur in this process.

## Accepted comparison constants

- pitchContentF1 `0.35406698564593303`
- pitchTimingTolerantF1 `0.06698564593301436`
- stringFretTimingTolerantF1 `0.05454545454545454`
- chordPitchSetTolerantF1 `0.0580511402902557`
- exactVoicingTolerantF1 `0.0580511402902557`
- measureCoverageRecall `1.0`
- pdfEventFidelity `1.0`
- criticalMismatchCount `1712`

The implementation must compare the manifest values to these frozen constants before using them.

## Mandatory report fields

- schemaVersion `14504`;
- classification `v145-rhythm-stage3-offline-calibration-score`;
- evaluationRole `calibration-benchmark-not-unseen-holdout`;
- mayClaimUnseenGeneralization `false`;
- candidate event count/SHA;
- PDF event fidelity exactly `1.0`;
- candidate gated metrics and critical mismatch count;
- exact deltas vs accepted family #10;
- `referenceOpenedOnlyAfterPreReferenceGate=true`;
- `candidateMutatedDuringEvaluation=false`;
- `acceptedBaselineChanged=false`;
- `promotionAllowed=false`;
- `modalGpuUsed=false`;
- `liveAudioBenchmarkRun=false`.

## Synthetic proof requirements

Before the real one-shot trial, synthetic tests must prove:
- the pre-reference gate is called before either accepted manifest or reference bytes are read;
- a failed pre-reference gate prevents both reads;
- candidate/freeze identity mismatch prevents both calibration reads;
- wrong accepted manifest identity fails;
- wrong gold SHA fails before parsing/scoring;
- one valid synthetic path scores exactly once and leaves the candidate unchanged;
- report always states acceptedBaselineChanged=false and promotionAllowed=false.

No synthetic proof may read the real V144 calibration gold.

## Safety / no-retune rule

The evaluation harness cannot alter the frozen Stage 3 candidate. Its result is benchmark evidence only. Regardless of score, no automatic promotion is permitted and the accepted family #10 baseline remains unchanged. No Modal/L4/GPU/live audio, main, Production, `/ai-tab`, Bass, Lead, or `freezeReady=false` work is authorized here.
