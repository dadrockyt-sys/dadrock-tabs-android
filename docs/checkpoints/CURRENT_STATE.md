# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V147 Phase C real-audio execution is EXPLICITLY AUTHORIZED by the user. Pre-audio support gate remains GO/SEALED. Exact historical source provenance has now been recovered before audio access. No audio has yet been downloaded/read/decoded in this checkpoint; no CQT, candidate, reference/gold scoring, Modal/GPU, main, or Production work has occurred.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- User authorization now covers the already-frozen V147 Phase C real-audio artifact-first execution only.
- Phase D/reference/gold scoring remains unauthorized.
- Gold SHA256 `18fd868ae960dfcddc1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; do not open/use during Phase C.
- No automatic promotion.

## Accepted Rhythm baseline — UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- 1144 canonical events; accepted event/PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; 113 measures.
- Scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100**.

## V147 Phase A / B — SEALED
- Phase A GO: run `33034629948`, job `98394561968`; proof SHA `3843912f0c8e5da95c3993783a84762ba01b046120a48db5e5a5c6c16a3d883e`.
- Phase B GO: run `33035123962`, job `98396067875`; proof SHA `07848295a7a0b82cee4701db8ddf4505910d4955c2c6bd9587833cbb1656435a`.

## V147 Phase C frozen protocol identities
- Real-audio prereg blob `5c19ed572d17cc9a760f1b63ee03c1b2c4543d30`.
- Clarification blob `6ced1bae4cdaad8306b008827657afbb27a87dbc`.
- V145 decoder blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- V147 pitch blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`; authoritative `OCTAVE_WEIGHT=0.25`.
- Phase-C support blob `f4278ffaacaca3f66baf7a3112e2af0f3bc387cf`.
- Repaired Phase-C tests blob `cbcc8fa90480b2a3b12546cf2193519fb46ade87`.
- Phase-C CPU proof harness blob `531384706b8b7444cf7ed22f414b47215e59b653`.
- Canonical helper blob `088d44827fb23e20d9aeeb4944a672989af5846c`.

## Phase C pre-audio support gate — GO / SEALED
- Successful run `33036984670`, job `98401701852`: 11/11 tests passed, generated proof GO 6/6.
- Proof payload SHA `c846d59812dc799ab7688afcd8624d177e3a962755d407268c20208264fa2436`.
- Proof file SHA `76435797fa197af90138db6011c3f1a26564c226f4d3e7b0dbf65678ab46db8f`.
- Artifact ID `9632361491`; artifact ZIP SHA `114e073a485e743a09d2967b92bc4e441cc6a185dd0cad145c1647d1997f99b8`.
- One-use workflow deleted/sealed at commit `08a0c76f555c11a70d2e853d4bb94de07aad315c`.

## Exact historical source-audio provenance — RECOVERED BEFORE AUDIO ACCESS
- Frozen required raw-audio SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Historical approved paid-capture run: `32805316807`, workflow `V143 Repaired Timing Precision Candidate Product`, trigger commit `74b0f815ff3f66f325220975c410621503de440f`, run attempt 1.
- Historical workflow path at that trigger: `.github/workflows/v143-repaired-timing-precision-candidate-product.yml`.
- The workflow safety gate explicitly required `sha256sum public/gomywayfullaitest.m4a` to equal the frozen SHA above before Modal execution.
- The same workflow then invoked the one authorized paid capture with `--audio-path public/gomywayfullaitest.m4a`.
- The completed paid-capture commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527` records `approvedAudioSha256` equal to the same frozen SHA, `runId=32805316807`, `triggerSha=74b0f815...`, and `singlePaidCaptureConsumed=true`.
- Retained historical run artifact `9548666053` (`v143-precision-v2-one-shot-32805316807`) is unexpired; its ZIP digest is `5104522aab3e6193c6b06fe3abb807994065f858a945a81070c611fc63707d4f`.
- That retained artifact contains four JSON evidence files, not the audio bytes, but `repaired-timing-precision-candidate-product.json` records `candidate.sourceSha256=215bd5...` and `candidate.sourceBytes=3478611`.
- Therefore the exact historical byte source is the Git blob/file at trigger revision path `public/gomywayfullaitest.m4a`; it may be recovered from that exact commit only and must be independently SHA-verified before decode.
- No substitute encode, alternate file, or re-encoding is permitted.

## Frozen Phase-C real-audio execution contract
- Recover exact bytes from `public/gomywayfullaitest.m4a` at commit `74b0f815ff3f66f325220975c410621503de440f`.
- Before decode, require byte count `3478611` and SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Decode mono at 22050 Hz; HPSS harmonic margin `(1.0,6.0)`; CQT hop 128; 48 bins/octave; fmin MIDI 40; 243 bins.
- Event timing fixed at 129.19921875 BPM, 4 steps/beat; frozen frame window.
- Evidence extraction/decision delegates to frozen V147 exactly: candidates ±1, band ±0.30, baseline ±2.0 excluding ±0.75, DB floor `1e-8`, octave weight `0.25`, thresholds `3.0/3.0/2.0 dB`, fail closed.
- Candidate count/order/timing/measure/metadata remain fixed; only MIDI/string/fret may change; V145 timing lattice forbidden.
- Construct exactly one real-audio-derived candidate, persist immutable artifact/evidence hashes, then STOP before reference/gold/scoring.

## EXPLICIT NEXT STEPS
1. Recover exact raw bytes from the frozen historical Git revision/path and independently verify byte count + SHA before decode.
2. Checkpoint exact recovered-byte identity.
3. Execute the frozen Phase-C decode/HPSS/CQT/candidate construction exactly once; no reference/gold/scorer access.
4. Persist immutable candidate + evidence identities and checkpoint/seal Phase C.
5. **STOP before Phase D/reference scoring.** A separate frozen Phase D protocol and authorization are required.

## Current stop point
- V147 A/B GO/SEALED; Phase-C pre-audio support GO/SEALED.
- User has explicitly authorized Phase-C real-audio execution.
- Exact historical source provenance is recovered and frozen.
- **No audio bytes have yet been downloaded/read/decoded at this checkpoint.**
- No CQT, candidate, calibration/gold/reference, scoring, Modal/L4/GPU, `main`, or Production changes occurred in this authorization phase yet.
