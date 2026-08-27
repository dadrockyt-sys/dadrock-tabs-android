# V146 Rhythm — Phase B Fixed-Artifact Calibration Evaluation Preregistration

Date frozen: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Status: **FROZEN AFTER PHASE A ARTIFACT SEALING AND BEFORE V146 CALIBRATION ACCESS**

## Purpose

Score exactly one already-persisted V146 generated-only artifact against the existing V144 professional Rhythm calibration reference. Phase B performs no candidate construction, reconstruction, search, ranking, fallback, retuning, alternate selection, or promotion. It consumes only the exact artifact sealed by V146 Phase A.

This is a calibration benchmark, not an unseen holdout. The result is observational evidence only. Accepted family #10 remains unchanged regardless of score unless a separate later promotion protocol is frozen and succeeds.

## Exact immutable Phase A artifact

Candidate:
- path `debug/v146-rhythm-artifact/generated-only-candidate.json`
- Git blob `61bda87e4a16b752bfaaf68c2d51e7020f31a7f8`
- canonical event count `1209`
- generated measure count `113`
- canonical event SHA256 `2de0a686cfd797a19aa02af735aa2bfaf0e65245ec85a5148c71f8b8b3a77c40`

Construction proof:
- path `debug/v146-rhythm-artifact/generated-only-candidate-proof.json`
- Git blob `abb8fcd1726bf9b8caa5bf8432adae2c6915a483`
- schemaVersion `14601`
- Phase A run `33031802198`, job `98385781107`, SUCCESS
- persistence commit `e5d7d9dd9bdce8bf0eeee7f2a8207475ddbd31d3`
- Phase A workflow deletion/sealing commit `a79e9717e0dbebdd730dfabaef068c78b45a5109`

Phase A evidence states: one decoder call, 1209 decoded notes, 891 decoded groups, 871 changed events, stringIndex changes871, fret changes871, measure changes0, step changes0, referenceFree=true, acceptedManifestRead=false, realGoldRead=false, calibrationScoreRun=false, alternateCandidateConstructed=false, acceptedBaselineChanged=false, modalGpuUsed=false, liveAudioBenchmarkRun=false.

## Frozen evaluation chain

- Canonical helper `validation/rhythm_holdout/canonical.py` blob `088d44827fb23e20d9aeeb4944a672989af5846c`.
- Freeze `validation/rhythm_holdout/freeze_rhythm_analysis.py` blob `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`.
- PDF fidelity `validation/rhythm_holdout/verify_pdf_event_fidelity.py` blob `5e1564216873046237fb545078a04a6b18f72b27`.
- Renderer contract `lib/v143RenderContract.js` blob `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.
- Evaluator `validation/v145_rhythm_decoder/score_offline_stage3_candidate.py` blob `d208abb3f180f8375d57d786941ff49d6813de1c`.
- Evaluator tests blob `d8b3770ac7f3ba18123122f19fad895257998c25`.
- Evaluator CPU proof blob `81c10bdcc39ce9e371fda60d2c3d107e671b8790`; run `33031101564`, job `98383566164`, SUCCESS.
- Scorer primitives `validation/rhythm_holdout/score_rhythm_holdout.py` blob `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`.
- Full-score helper `validation/v144_rhythm_calibration/score_selected_conjunction_candidate.py` blob `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`.

## Accepted comparison identity

- Accepted family #10 manifest path `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`.
- Manifest Git blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- Name `singleton-onset-replace-be9e9aa7a734e3cd`.
- Event count1144 / measures113 / event+PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`.
- Critical mismatch count1712.
- Accepted metrics: pitchContentF1 `0.35406698564593303`; pitchTimingTolerantF1 `0.06698564593301436`; stringFretTimingTolerantF1 `0.05454545454545454`; chordPitchSetTolerantF1 `0.0580511402902557`; exactVoicingTolerantF1 `0.0580511402902557`; measureCoverageRecall1.0; PDF fidelity1.0.

## Calibration reference

- Path `debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json`.
- Raw SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Calibration benchmark only; no unseen-generalization claim.

## Mandatory Phase B order

1. Verify the exact Phase A candidate/proof Git blobs and all frozen evaluation dependencies. Do not read accepted manifest or gold yet.
2. Independently canonicalize the persisted candidate and require exactly 1209 events, measures1..113, eventIndex0..1208, event SHA `2de0a686...`, and safe generated-only flags. Require the construction proof points to the same event SHA and states no calibration access.
3. Create a temporary freeze-input wrapper directly from the persisted candidate `renderEvents`; do not reconstruct or mutate candidate events.
4. Run the frozen freeze tool.
5. Run the frozen V143 renderer contract against the exact persisted candidate events and produce temporary renderer-event evidence.
6. Run frozen PDF-event-fidelity verification. Require fidelity exactly1.0 and candidate/frozen/PDF event count1209 + event SHA `2de0a686...` identical.
7. Only after steps1–6 pass may the frozen evaluator be invoked. The evaluator itself must run its proven order: candidate-only validation -> `validate_pre_reference` -> candidate/freeze/PDF identity -> accepted family #10 manifest -> gold bytes SHA check -> reference validation -> exactly one score.
8. Verify report schema14504/classification `v145-rhythm-stage3-offline-calibration-score`, evaluation role `calibration-benchmark-not-unseen-holdout`, candidate identity exact, PDF fidelity1.0, referenceOpenedOnlyAfterPreReferenceGate=true, candidateMutatedDuringEvaluation=false, acceptedBaselineChanged=false, promotionAllowed=false, modalGpuUsed=false, liveAudioBenchmarkRun=false.
9. Write one V146 Phase B proof containing workflow IDs, exact candidate/proof identities, PDF fidelity identity, score report metrics/deltas, and safety flags. Observed score may not trigger another candidate or branch of execution.
10. Persist only the calibration score report and Phase B proof. Temporary freeze/render files are not persisted.
11. Seal/delete the Phase B workflow after the one execution. Never replay Phase B.

## Frozen outputs

- Score report `debug/v146-rhythm-artifact/calibration-score.json`.
- Phase B proof `debug/v146-rhythm-artifact/calibration-evaluation-proof.json`.

Both output paths must be absent before Phase B execution.

## Interpretation / promotion

- This single score is the calibration result for the exact sealed V146 artifact only.
- No automatic promotion, fallback, alternate candidate, or retuning is authorized.
- Even if every metric improves, family #10 remains the accepted baseline until a separate promotion protocol is frozen and passes.
- If Phase B fails at any gate, fail closed and do not rerun this exact Phase B execution.

## Safety

- CPU only.
- No Modal/L4/GPU.
- No live audio.
- No `/ai-tab` frontend, Bass, Lead, `freezeReady=false`, main, or Production changes.
