# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V147 Phase C real-audio execution is EXPLICITLY AUTHORIZED. Pre-audio support remains GO/SEALED. Exact historical source provenance is recovered, and the new CPU-only real-audio runner is now FROZEN BEFORE AUDIO ACCESS. No audio has yet been checked out/read/decoded; no CQT/candidate/reference/gold/scoring/Modal/GPU/main/Production work has occurred in this execution phase.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- User authorization covers only the already-frozen V147 Phase C real-audio artifact-first execution.
- Phase D/reference/gold scoring remains unauthorized.
- Gold SHA256 `18fd868ae960dfcddc1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; do not open/use during Phase C.
- No automatic promotion.

## Accepted Rhythm baseline — UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- 1144 canonical events; accepted event/PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; 113 measures.
- Scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.

## V147 Phase A / B — SEALED
- Phase A GO run `33034629948`, job `98394561968`; proof SHA `3843912f0c8e5da95c3993783a84762ba01b046120a48db5e5a5c6c16a3d883e`.
- Phase B GO run `33035123962`, job `98396067875`; proof SHA `07848295a7a0b82cee4701db8ddf4505910d4955c2c6bd9587833cbb1656435a`.

## V147 Phase C frozen protocol / source identities
- Real-audio prereg blob `5c19ed572d17cc9a760f1b63ee03c1b2c4543d30`.
- Clarification blob `6ced1bae4cdaad8306b008827657afbb27a87dbc`; authoritative V147 octave weight `0.25`.
- V145 decoder `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- V147 pitch `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
- Phase-C support `f4278ffaacaca3f66baf7a3112e2af0f3bc387cf`.
- Repaired Phase-C tests `cbcc8fa90480b2a3b12546cf2193519fb46ade87`.
- Canonical helper `088d44827fb23e20d9aeeb4944a672989af5846c`.
- PDF fidelity helper `5e1564216873046237fb545078a04a6b18f72b27`.
- Render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.

## Phase C pre-audio support gate — GO / SEALED
- Run `33036984670`, job `98401701852`: 11/11 tests passed; generated proof GO 6/6.
- Proof payload SHA `c846d59812dc799ab7688afcd8624d177e3a962755d407268c20208264fa2436`.
- Artifact `9632361491`; ZIP SHA `114e073a485e743a09d2967b92bc4e441cc6a185dd0cad145c1647d1997f99b8`.
- One-use workflow deleted/sealed at `08a0c76f555c11a70d2e853d4bb94de07aad315c`.

## Exact historical source-audio provenance — RECOVERED
- Required raw SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Required raw byte count `3478611`.
- Historical paid-capture run `32805316807`, trigger `74b0f815ff3f66f325220975c410621503de440f`, run attempt 1.
- Exact historical path `public/gomywayfullaitest.m4a` at trigger commit `74b0f815...`.
- Historical workflow first required that file's SHA to equal `215bd5...`, then passed that exact path to the authorized capture.
- Completed capture commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527` confirms the same SHA/run/trigger and `singlePaidCaptureConsumed=true`.
- Retained artifact `9548666053` is unexpired; ZIP SHA `5104522aab3e6193c6b06fe3abb807994065f858a945a81070c611fc63707d4f`; evidence confirms `candidate.sourceSha256=215bd5...` and `candidate.sourceBytes=3478611`.
- No substitute/re-encode/alternate source is permitted.

## New Phase-C CPU-only runner — FROZEN BEFORE AUDIO ACCESS
- Runner path `modal/v147_phase_c_real_audio.py`.
- Creation/freeze commit `b04ba0e64ac7e0943135d05ec32fcb1eae69ba3e`.
- Frozen runner Git blob `79c631a41ee8863322376604aa1d69e6abe59ca3`.
- Runner preflight verifies all frozen source blobs and materializes accepted family #10 to 1144 / SHA `4e6f9f...` before any audio-byte read.
- Execute mode requires exact raw byte count `3478611` and raw SHA `215bd5...` before decode.
- Decoder is a pinned `imageio-ffmpeg` bundled ffmpeg path producing mono 22050 Hz `pcm_f32le`; normalized PCM SHA/bytes, decoder version, librosa/numpy/scipy/soundfile versions are recorded.
- HPSS/CQT parameters are exactly frozen; evidence decisions delegate to frozen V147 and fixed-time fingering delegates to frozen support/V145 primitives.
- Runner persists one candidate artifact, per-event decisions, deterministic construction proof, Phase-C evidence, render-contract projection evidence, and frozen PDF-fidelity proof.
- Determinism is checked by identical in-memory replay of the same prepared CQT/rules; no alternate candidate/search/tuning is performed or persisted.
- Runner hard-codes `referenceRead=false`, `goldRead=false`, `calibrationScoreRun=false`, `candidateSearchRun=false`, `alternateCandidateConstructed=false`, `modalGpuUsed=false`, `productionIntegrated=false`.

## Frozen execution contract
- Current branch must be checked out at the execution commit; historical audio source must be separately checked out from exact trigger `74b0f815...` only after runner preflight succeeds.
- Before decode independently require source path byte count `3478611` and SHA `215bd5...`.
- Pin Python/audio/numerical versions in the one-use execution workflow; record actual versions/runtime.
- Run exactly one Phase-C real-audio execution; persist immutable artifacts and hashes; then delete/seal workflow.
- **STOP before Phase D/reference scoring.**

## EXPLICIT NEXT STEPS
1. Create one-use CPU execution workflow frozen to runner blob `79c631...` and the other frozen source identities.
2. Workflow order: current checkout -> preflight accepted source/blob identities -> historical source checkout -> raw byte count/SHA gate -> pinned dependency install -> exactly one real-audio execution -> artifact upload.
3. Persist/checkpoint exact run/job/artifact/candidate/evidence identities and delete/seal the workflow.
4. STOP before reference/gold/scoring.

## Current stop point
- V147 A/B GO/SEALED; Phase-C pre-audio GO/SEALED.
- Real-audio execution authorized; exact source provenance recovered.
- Real-audio runner frozen at blob `79c631...` before waveform access.
- **No audio bytes have yet been checked out/read/decoded in this Phase-C execution.**
