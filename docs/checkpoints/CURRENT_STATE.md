# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V147 Phase C real-audio execution is ACTIVE under explicit user authorization. The frozen pre-audio gate is GO/SEALED; exact source provenance and runner are frozen. One-use run `33038518285` / job `98406611428` has now passed accepted-source preflight and exact historical raw-byte identity verification. The pinned CPU audio stack is installing; audio has NOT yet been decoded and no HPSS/CQT/candidate result has been observed.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- Authorization covers V147 Phase C artifact-first construction only; Phase D/reference/gold scoring remains unauthorized.
- Gold SHA256 `18fd868ae960dfcddc1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; reference files were made unreadable in the Phase-C run before historical audio checkout.
- No automatic promotion, candidate search, alternate candidate, threshold/window tuning, Modal/GPU, or Production integration.

## Accepted Rhythm baseline — UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- 1144 canonical events; accepted event/PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; 113 measures.
- Scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.

## Sealed V147 identities
- Phase-C prereg `5c19ed572d17cc9a760f1b63ee03c1b2c4543d30`; clarification `6ced1bae4cdaad8306b008827657afbb27a87dbc`.
- V145 `2fd979aebb4685e86c7f24a0162f69de306c06e9`; V147 pitch `49bce8b968406bb0d61ab61394954ef8a8303eb7`; Phase-C support `f4278ffaacaca3f66baf7a3112e2af0f3bc387cf`.
- Canonical `088d44827fb23e20d9aeeb4944a672989af5846c`; PDF helper `5e1564216873046237fb545078a04a6b18f72b27`; render contract `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.
- Phase-C pre-audio run `33036984670` / job `98401701852`: 11/11 tests, generated proof GO 6/6; workflow sealed `08a0c76f555c11a70d2e853d4bb94de07aad315c`.

## Phase-C real-audio runner — FROZEN BEFORE AUDIO ACCESS
- `modal/v147_phase_c_real_audio.py`; freeze commit `b04ba0e64ac7e0943135d05ec32fcb1eae69ba3e`; blob `79c631a41ee8863322376604aa1d69e6abe59ca3`.
- Accepted family is materialized/verified before audio byte access.
- Decode contract: mono 22050 Hz `pcm_f32le`; HPSS margin `(1.0,6.0)`; CQT hop 128, 48 bins/octave, fmin MIDI 40, 243 bins.
- Decisions delegate to frozen V147 with authoritative octave weight `0.25`; fixed-time fingering uses frozen support/V145 primitives.
- Only MIDI/string/fret may differ; timing/order/count/measure/metadata fixed.
- One candidate artifact only; deterministic identical replay required; PDF/render fidelity must equal 1.0.

## Exact historical source provenance / BYTE GATE PASSED
- Historical source: `public/gomywayfullaitest.m4a` at commit `74b0f815ff3f66f325220975c410621503de440f`.
- Historical paid run `32805316807`; completed capture commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`; retained evidence artifact `9548666053`.
- Required bytes `3478611`; required SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- One-use Phase-C execution workflow commit `be3dac43fdb559c32ee782b8f4b827822b9cc083`.
- Current Actions run `33038518285`, job `98406611428`.
- Completed successfully in that run, in order:
  1. current execution revision checkout;
  2. pinned Python setup;
  3. frozen runner/upstream identity checks;
  4. accepted family preflight = 1144 events / SHA `4e6f9f...` while `audioRead=false`;
  5. calibration reference files made unreadable;
  6. sparse checkout of only historical `public/gomywayfullaitest.m4a` at `74b0f815...`;
  7. exact raw byte count = `3478611` and SHA256 = `215bd5...` verified **before decode**.
- Current run step: installing pinned CPU stack (`numpy 2.2.6`, `scipy 1.15.3`, `librosa 0.11.0`, `soundfile 0.13.1`, `imageio-ffmpeg 0.6.0`, `numba 0.61.2`, `llvmlite 0.44.0`).
- **At this checkpoint audioDecoded=false; HPSS/CQT not started; candidate not constructed; reference/gold not read; no score run.**

## EXPLICIT NEXT STEPS
1. Allow only run `33038518285` to continue into its single frozen execute step after dependency installation.
2. If execution reaches a result, do not alter any frozen rule based on that result.
3. Persist exact candidate/evidence/artifact/runtime identities; checkpoint and delete/seal one-use workflow.
4. **STOP before Phase D/reference scoring.**
