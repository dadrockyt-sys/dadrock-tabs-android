# Open-Corpus P3 Reference-Blind Octave Bridge — READY BEFORE INFERENCE

Date: 2026-09-02 UTC  
Branch: `v143-contextual-prune-lobo`

## Boundary status

The P3 bridge is now implementation-ready **before the first P3 candidate inference**.

At this checkpoint:
- P3 reference-note events read: **0**;
- P3 Basic Pitch inference calls on real P3 audio: **0**;
- P3 candidate files generated: **0**;
- P3 reference-facing score calls: **0**;
- V168 prospective reference-facing score calls: **0**;
- GOAT restricted bytes read: **false**;
- GPU/CUDA/Modal use: **none**;
- `main` / Production: **untouched**.

## Frozen scientific preregistration

- `docs/checkpoints/OPEN_CORPUS_P3_REFERENCE_BLIND_OCTAVE_PREREGISTRATION_20260902.md`
- creation commit `75b4ee9613da84d4a097f486d67fec79e18eb40c`.

The preregistration fixes all 12 P3 works and both direct-input + mic/amp capture chains (24 capture-work units), Basic Pitch 0.4.0 defaults, frozen V2 pitch-only correction, prediction-freeze-before-reference boundary, 100 ms primary / 50 ms strict exact-pitch onset scoring, and prospective PASS/FAIL/INCONCLUSIVE rules.

## P3 public archive identity

Metadata-only inventory checkpoint:
- `docs/checkpoints/OPEN_CORPUS_GUITAR_TECHS_P3_METADATA_INVENTORY_20260902.md`
- creation commit `cc1d9d3d4a168e6551935ab0445f20ea1e9134b4`.

Archive:
- Guitar-TECHS Zenodo record `14963133`;
- `P3_music.zip`;
- official MD5 `071ba80aecf00f4a31fbd167b3f22198`;
- observed SHA256 `033489e22600751fb5a1633e7d856b901c6782e0486fa02135e830780d9dbfe2`.

Metadata inventory Actions run `33577994728`, job `100086035966`: **SUCCESS**. It established complete index bindings `01`–`12` for MIDI, direct-input WAV and mic/amp WAV without extracting/reading reference note events.

## Frozen Basic Pitch CPU runtime

Preflight workflow:
- `.github/workflows/open-corpus-basic-pitch-cpu-preflight.yml`
- creation commit `dc1e6ea7be58e3c72d0ea770b0f57f17ba591693`.

Actions run `33578250363`, job `100086839088`: **SUCCESS**.

Verified:
- Python `3.10.21`;
- Basic Pitch `0.4.0`;
- `tflite-runtime 2.14.0`;
- NumPy `1.26.4`;
- model `nmp.tflite` SHA256 `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`;
- TFLite present; TensorFlow/CoreML/ONNX absent;
- synthetic one-second A4 CPU inference PASS with one event;
- P3 audio/reference untouched by preflight;
- CUDA used = false.

## Frozen bridge implementation identities

Frozen V2 evaluator:
- `validation/open_corpus/evaluate_harmonic_candidate_ranking_v2_v169.py`
- Git blob `95e1e7d20a4bb5b15962cb803fa2da4d065743ae`.

Frozen harmonic helper:
- `validation/open_corpus/analyze_guitar_techs_harmonic_octave_v169.py`
- Git blob `c39305df4f875bf6aec0d5e9d5b6448a5f7404df`.

Audio-only candidate generator:
- `validation/open_corpus/generate_p3_reference_blind_octave_candidates_v169.py`
- creation commit `419829793908ebdc9cbeca767532eb165e6d478c`;
- Git blob `e3fe6f88b585405751dad139d82769dd00743d69`.

Reference-only scorer:
- `validation/open_corpus/score_p3_octave_bridge_v169.py`
- creation commit `721fa5ca0262e23a9071c7a837ab16b33e83ed48`;
- Git blob `70ed9ceb69584ce96945688ae45cd9c8ffa3022a`.

Implementation clarification frozen before P3 inference: if an event is too close to an audio boundary for the frozen V2 analysis window to exist, the corrected stream preserves the original Basic Pitch pitch unchanged and increments `boundaryUnscoredCount`. The event is never removed. This rule depends only on audio-window availability, not reference content or outcome direction.

## Static isolation/self-test

Static workflow:
- `.github/workflows/open-corpus-p3-octave-bridge-static.yml`
- creation commit `d696e9d6f7b78478b684e7f2e7a9d78dfef9ab72`.

GitHub Actions:
- run `33578459757`;
- job `100087448155`;
- conclusion **SUCCESS**.

Verified:
- exact four scientific Git blob identities above;
- candidate reference-isolation static guard PASS;
- scorer no-audio/no-generation static guard PASS;
- both scripts compile PASS;
- candidate wrapper self-test `P3_CANDIDATE_WRAPPER_SELF_TEST_PASS`;
- scorer one-to-one onset matcher self-test `P3_SCORER_SELF_TEST_PASS`;
- Basic Pitch model SHA256 reconfirmed exactly;
- V168 reference-facing score calls = 0 throughout.

## Next action now authorized by the preregistration

Create/run the real **two-job CPU workflow exactly once**:

1. candidate job verifies all frozen identities and the P3 archive, extracts only 24 DI/micAmp WAVs, deletes the source ZIP, proves no MIDI exists in its workspace, runs Basic Pitch + frozen V2, freezes/hashes all 24 baseline/corrected candidate files, and uploads candidate JSON only;
2. scoring job starts only after the candidate artifact is finalized, verifies every candidate hash, independently re-downloads the exact P3 archive, extracts only the 12 MIDI references, proves no audio exists in its scoring workspace, scores frozen predictions, and preserves the report;
3. scientific PASS/FAIL/INCONCLUSIVE status must not itself fail the CI job; only integrity/runtime violations should fail CI;
4. checkpoint the first completed outcome before any V3 or retuning.

No P3-driven change to Basic Pitch thresholds, V2 formula/weights/timing, candidate set, scorer tolerance, or success criteria is permitted.

**Project Progress Score: 60%.**  
**Test Score: NOT RUN.**
