# V145 Rhythm Decoder — Stage 3 Real Offline Calibration One-Shot Preregistration

Date frozen: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Status: **FROZEN BEFORE REAL V5 STAGE 3 CANDIDATE CONSTRUCTION AND BEFORE REAL CALIBRATION GOLD ACCESS**

## Purpose

Execute exactly one CPU-only offline V145 Stage 3 calibration trial using the already-frozen generated-only adapter and already-proven evaluation harness. This is a calibration benchmark, not an unseen holdout, search, tuning loop, candidate ranking exercise, production promotion, live-audio benchmark, or Modal/GPU run.

Regardless of the observed score, this one-shot may not be replayed, retuned, used to choose an alternate candidate, or automatically promoted. Accepted family #10 remains unchanged unless a separate later promotion protocol is frozen and succeeds.

## Immutable generated-only construction chain

- V5 source: `debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json`
  - Git blob `fe61f7ad53a4d71348a5113ecc9e3876eaad98d4`
  - raw SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`
  - exactly 1209 events / measures 1..113 / tempo `129.19921875` / `4/4` / E Standard.
- Stage 1 `modal/v145_rhythm_decoder.py` blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- Stage 2 `modal/v145_rhythm_sequence_decoder.py` blob `5f86f57d0fd10774690d50528d51bad6e0392bf3`.
- Stage 3 adapter `validation/v145_rhythm_decoder/offline_stage3_adapter.py` blob `434d4b2582991c216df411455f232b8d211337c6`.
- Adapter tests blob `3eee7ae5253ad0eecbeb492eaa24216f0fa21fee`.
- Adapter CPU proof `debug/v145-rhythm-decoder/proofs/cpu-stage3-offline-adapter-proof.json` blob `f55dcd1087f108d0d93c4a5a1a86cb5058ef4eb4`.

The adapter is invoked exactly once against the immutable V5 source. It has no calibration-reference input and may not add/delete events or generate new MIDI pitches. Candidate event count, eventIndex sequence, MIDI inventory, and measures 1..113 remain preserved according to the frozen adapter contract.

## Immutable freeze/render/evaluation chain

- Canonical `validation/rhythm_holdout/canonical.py` blob `088d44827fb23e20d9aeeb4944a672989af5846c`.
- Freeze `validation/rhythm_holdout/freeze_rhythm_analysis.py` blob `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`.
- Scorer primitives `validation/rhythm_holdout/score_rhythm_holdout.py` blob `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`.
- Full-score helper `validation/v144_rhythm_calibration/score_selected_conjunction_candidate.py` blob `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`.
- PDF fidelity `validation/rhythm_holdout/verify_pdf_event_fidelity.py` blob `5e1564216873046237fb545078a04a6b18f72b27`.
- Renderer contract `lib/v143RenderContract.js` blob `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.
- Stage 3 evaluator `validation/v145_rhythm_decoder/score_offline_stage3_candidate.py` blob `d208abb3f180f8375d57d786941ff49d6813de1c`.
- Evaluation tests blob `d8b3770ac7f3ba18123122f19fad895257998c25`.
- Evaluation CPU proof `debug/v145-rhythm-decoder/proofs/cpu-stage3-evaluation-harness-proof.json` blob `81c10bdcc39ce9e371fda60d2c3d107e671b8790`, run `33031101564`, job `98383566164`, SUCCESS.

## Calibration inputs — forbidden until pre-reference gates pass

- Accepted family #10 manifest: `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`, blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- Calibration gold: `debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json`, raw SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.

The one-shot workflow must not read, `cat`, parse, `sha256sum`, `git hash-object`, or otherwise inspect either calibration input before candidate construction, freeze, renderer validation, and PDF fidelity have passed. The frozen evaluator is the only component authorized to open these calibration inputs, and only in its proven order: candidate-only validation -> `validate_pre_reference` -> candidate/freeze/PDF identity -> accepted manifest -> gold bytes/hash/validation -> exactly one score.

## Frozen real one-shot order

1. Require the exact sole trigger commit and verify every non-calibration dependency blob above.
2. Run the existing frozen CPU tests only; do not access calibration inputs.
3. Invoke the Stage 3 adapter exactly once against the immutable V5 render stream and write one candidate JSON.
4. Independently verify candidate safety: schema/classification, 1209 events, eventIndex 0..1208, MIDI preserved, exactly measures 1..113, acceptedBaselineChanged=false, gold/reference flags false.
5. Create a freeze-input wrapper around the candidate render events with Rhythm metadata and anti-leakage flags. No calibration data is used.
6. Run frozen freeze logic.
7. Validate the candidate event stream through the frozen V143 renderer contract and emit renderer-event evidence.
8. Run frozen PDF-event fidelity verification and require exactly `1.0`, identical event count, and identical event SHA across candidate/freeze/PDF evidence.
9. Only now invoke the frozen Stage 3 evaluator. It must perform its own pre-reference gate before reading the accepted manifest and calibration gold, hash the gold before parsing, validate the reference, and score the already-frozen candidate exactly once.
10. Require report schema `14504`, classification `v145-rhythm-stage3-offline-calibration-score`, role `calibration-benchmark-not-unseen-holdout`, PDF fidelity `1.0`, referenceOpenedOnlyAfterPreReferenceGate=true, candidateMutatedDuringEvaluation=false, acceptedBaselineChanged=false, promotionAllowed=false, modalGpuUsed=false, liveAudioBenchmarkRun=false.
11. Reverify all immutable generated-only/evaluation dependencies after scoring. Do not inspect score values to choose another action.
12. Persist only the candidate JSON and score-report JSON. Do not persist temporary freeze/render files.
13. Seal workflow and trigger after the single run. Never replay.

## Frozen output paths

- Candidate: `debug/v145-rhythm-decoder/stage3/offline-candidate.json`.
- Score report: `debug/v145-rhythm-decoder/stage3/offline-calibration-score.json`.

Both paths must be absent before the one-shot trigger. If either already exists, fail closed.

## Trigger / promotion policy

The workflow may be registered before arming, but its calibration job must run only when the exact commit message is `v145 execute stage3 offline calibration one-shot` and the trigger path is the sole changed file. The trigger must bind the exact frozen workflow blob and the immediately preceding checkpoint commit.

No promotion decision is part of this workflow. `promotionAllowed` remains false regardless of score. Family #10 remains the accepted calibration baseline after this run.

## Safety

- CPU only.
- No Modal/L4/GPU.
- No live audio.
- No `/ai-tab` frontend, Bass, Lead, `freezeReady=false`, main, or Production changes.
- No candidate search/ranking/retuning/replay.
- Calibration benchmark only; no unseen-generalization claim.
