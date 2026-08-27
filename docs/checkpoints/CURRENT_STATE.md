# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V147 Phase C REAL-AUDIO ARTIFACT-FIRST CONSTRUCTION = GO / SEALED. Exactly one immutable candidate was constructed from the exact historical audio under the frozen protocol. All structural, position, deterministic-replay, render/PDF-fidelity, and no-reference/no-score gates passed. The one-use execution workflow has been deleted. A fresh durable V147 replay-preservation copy is now REQUIRED/AUTHORIZED from the already-finished 13-file artifact only; no audio replay is authorized. STOP before Phase D/reference/gold scoring.**

## Permanent safety / fixed protocol
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- `/ai-tab` frontend, Bass/Lead, `freezeReady=false`, main, Production untouched.
- Phase C authorization covered artifact-first construction only and is now consumed/sealed.
- Phase D/reference/gold scoring remains unauthorized.
- Gold SHA256 `18fd868ae960dfcddc1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac` was not opened/used.
- No automatic promotion, candidate search, alternate candidate, post-result retuning, Modal/L4/GPU, or Production integration.

## Accepted Rhythm baseline — UNCHANGED
- Family #10 `singleton-onset-replace-be9e9aa7a734e3cd`.
- Accepted canonical event count `1144`; event/PDF SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`; generated measures `113`.
- Accepted scores remain **35.4 / 6.7 / 5.5 / 5.8 / 100 / 100** because Phase C did not score or promote anything.

## Earlier V147 gates — SEALED
- Phase A GO: run `33034629948`, job `98394561968`; proof SHA `3843912f0c8e5da95c3993783a84762ba01b046120a48db5e5a5c6c16a3d883e`.
- Phase B GO: run `33035123962`, job `98396067875`; proof SHA `07848295a7a0b82cee4701db8ddf4505910d4955c2c6bd9587833cbb1656435a`.
- Phase-C pre-audio GO: run `33036984670`, job `98401701852`; 11/11 tests, generated proof GO 6/6; proof payload SHA `c846d59812dc799ab7688afcd8624d177e3a962755d407268c20208264fa2436`; workflow sealed `08a0c76f555c11a70d2e853d4bb94de07aad315c`.

## Frozen Phase-C protocol / source identities
- Real-audio prereg blob `5c19ed572d17cc9a760f1b63ee03c1b2c4543d30`.
- Clarification blob `6ced1bae4cdaad8306b008827657afbb27a87dbc`; authoritative V147 octave weight `0.25`.
- V145 decoder blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- V147 pitch blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`.
- Phase-C support blob `f4278ffaacaca3f66baf7a3112e2af0f3bc387cf`.
- Canonical helper blob `088d44827fb23e20d9aeeb4944a672989af5846c`.
- PDF fidelity helper blob `5e1564216873046237fb545078a04a6b18f72b27`.
- Render contract blob `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.
- Accepted manifest blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- Real-audio runner `modal/v147_phase_c_real_audio.py`; freeze commit `b04ba0e64ac7e0943135d05ec32fcb1eae69ba3e`; blob `79c631a41ee8863322376604aa1d69e6abe59ca3`.

## Exact historical source identity — VERIFIED BEFORE DECODE
- Historical source path `public/gomywayfullaitest.m4a` at commit `74b0f815ff3f66f325220975c410621503de440f`.
- Raw bytes `3478611`.
- Raw SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Historical paid-capture run `32805316807`; completed capture commit `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`; retained evidence artifact `9548666053`.
- Phase-C run verified accepted family #10 to 1144 / `4e6f9f...` before audio checkout, made calibration reference files unreadable, checked out only the exact historical source, then verified byte count + SHA before decode.

## V147 Phase C real-audio execution — GO / SEALED
- Execution workflow creation/run commit `be3dac43fdb559c32ee782b8f4b827822b9cc083`.
- GitHub Actions run `33038518285`, job `98406611428`: **SUCCESS**.
- One-use workflow `.github/workflows/v147-phase-c-real-audio-once.yml` deleted/sealed at commit **`4b125f42dfa447e1fe86741c8f41c09dcaffc895`**.
- Exactly one candidate artifact was persisted; no alternate candidate/search/retry/tuning path was used.

### Runtime / normalized audio identity
- Python `3.12.14`; numpy `2.2.6`; scipy `1.15.3`; librosa `0.11.0`; soundfile `0.13.1`; imageio-ffmpeg `0.6.0`; Node `v22.23.2`.
- Bundled ffmpeg `7.0.2-static`.
- Decode mono `22050 Hz`, `pcm_f32le`.
- Sample count `4662272`; normalized PCM bytes `18649088`; duration `211.44090702947847 s`.
- Normalized PCM SHA256 `d7db833dc498b5533f98b9934fef5cf055003cdb22d15ad7ff39070389d66518`.
- HPSS margin `(1.0,6.0)`.
- CQT `[243,36425]`; hop `128`; 48 bins/octave; fmin MIDI `40` / `82.4068892282175 Hz`; MIDI-bin range `40.0..100.5`.

### Immutable candidate identity
- Candidate event count `1144`.
- Candidate canonical event SHA256 **`ca35c3492295a3079c17c35124df7a483166315e85649e95ded095c6c06b2b77`**.
- Generated measures `113`.
- `candidate.json`: 280933 bytes; SHA256 `c0215690d5bfd9d2d47b8784eee886e942fbd28c499f25c643635c45ff7a9636`.
- `decisions.json`: 954471 bytes; SHA256 `3ec6c42730bf571c29258eca131c4e32da257c1ac6073e5319073818e8ac49b9`.
- `construction-proof.json`: 4589 bytes; SHA256 `16b7d6a258e07900bf033a922b4239c6270900221aa60f433cacd61b9a5bb448`.
- `phase-c-evidence.json`: 6576 bytes; SHA256 `135e655e915ef4008e0544601a382b54c4104038f053ca5f0ffb6f2b121e193e`.
- `pdf-render-evidence.json`: 181386 bytes; SHA256 `4d25a8346a40009ec5bdaf34c89f5d09e41ba9504e4264b0fd7cb21d7c25e4b9`.
- `raw-audio-identity.json` SHA256 `4ed7880b99fdeab8a1830efdbe3519024fcee0bc182213e18151ec0ad491c612`.
- `pip-freeze.txt` SHA256 `14bcc9531c91cdcf5388a0b6c0f996907f46e039627b39adad051aa23b906c69`.

### Observational construction metrics — NOT ACCURACY SCORES
- Events considered / usable evidence `1144 / 1144`; insufficient frames `0`.
- Pitch changes total **247**: down-one `137`, up-one `110`.
- Reasons: `alternate-supported=247`, `original-best=757`, `alternate-fundamental-too-weak=88`, `alternate-score-margin-too-small=49`, `alternate-fundamental-margin-too-small=3`.
- Weak fail-closed `140`; ambiguous `0`; malformed `0`; onset-group fingering fail-closed `0`.
- Position identity violations `0`; timing/metadata invariant violations `0`; input mutation violations `0`; order violations `0`; pitch-delta violations `0`.

### Determinism / render fidelity
- Construction proof payload SHA256 `d749d911ef79be75c8824ba89a5ed00b90f28c88ffb1e0149c4d82b34aaa0d62`.
- Determinism replay proof payload SHA is identical.
- `deterministic=true`.
- Candidate PDF event fidelity `1.0`.
- Frozen/PDF event count `1144 / 1144`; both event SHA `ca35c3492295a3079c17c35124df7a483166315e85649e95ded095c6c06b2b77`.
- `referenceOpenedDuringPdfFidelityCheck=false`; runtime safety verified; runtime labels not required.

### Safety flags — ALL CLEAN
- `referenceRead=false`
- `goldRead=false`
- `calibrationScoreRun=false`
- `candidateSearchRun=false`
- `alternateCandidateConstructed=false`
- `modalGpuUsed=false`
- `productionIntegrated=false`

## Immutable evidence artifact
- Name `v147-phase-c-real-audio-33038518285`; artifact ID `9633030568`.
- Size `179265` bytes; 13 evidence files; raw audio itself was not uploaded.
- GitHub artifact digest independently confirmed SHA256 `ea4c8b3a63b8798ec7bd3a88b1b16964d341064eac231266edc5d4e92a1cb68b`.
- Retention expiry `2026-09-26T04:13:57Z`.

## Durable V147 replay preservation — REQUIRED / AUTHORIZED
- A fresh V147 preservation set is required; the V144 preserved replay data is historical evidence from a different pipeline/front end and must not be substituted for this Phase-C result.
- Preserve only the already-finished 13-file Actions artifact from run `33038518285` / artifact `9633030568`; **do not decode/read the song again, do not recompute HPSS/CQT, and do not construct another candidate.**
- Planned durable path: `debug/v147-phase-c-real-audio/preserved-run-33038518285/`.
- Preserve candidate, per-event `decisions.json` CQT-derived evidence/frame indices, construction/evidence proofs, PDF/freeze evidence, raw-audio identity metadata, pinned environment, execution/preflight logs, and artifact identities.
- Raw `.m4a`, normalized PCM, and full CQT matrix are **not** part of the finished artifact and must not be regenerated merely for preservation.
- The preserved per-event evidence is intended to support future reference-free replay of the V147 decision/fingering stages without real-audio access and without Modal/L4/GPU usage.
- A future experiment that requires changing/recomputing the audio front end itself cannot be satisfied by this replay bundle alone and would require a separately authorized audio-access protocol.
- Preservation is archival/replay-only: candidate SHA `ca35c3492295a3079c17c35124df7a483166315e85649e95ded095c6c06b2b77` remains immutable; no result may be retuned or rescored during preservation.
- Phase D remains STOP throughout preservation.

## Interpretation boundary
- **Phase C GO establishes only that one real-audio-derived candidate was safely and deterministically constructed under the frozen protocol without reference/gold access.**
- It does not establish musical improvement; no candidate accuracy score or accepted-baseline comparison was run.
- Accepted baseline scores therefore remain unchanged.

## EXPLICIT NEXT STEPS
1. Copy and hash-gate the existing 13-file artifact into `debug/v147-phase-c-real-audio/preserved-run-33038518285/` using a one-use archival workflow only; no audio access/recompute is allowed.
2. Persist a preservation manifest binding run `33038518285`, job `98406611428`, artifact `9633030568`, artifact digest `ea4c8b3a63b8798ec7bd3a88b1b16964d341064eac231266edc5d4e92a1cb68b`, candidate SHA, and every preserved file SHA.
3. Delete/seal the one-use archival workflow and checkpoint the preservation commit/blob identities.
4. Keep V147 A/B, Phase-C pre-audio, and Phase-C real-audio construction sealed; do not recreate/rerun deleted one-use workflows.
5. **STOP before Phase D/reference scoring.** A new Phase-D preregistration must freeze candidate/freeze/PDF identities and evaluation order before any reference/gold access.
6. Phase D requires separate explicit authorization after its preregistration is frozen; no automatic promotion.

## Current stop point
- V147 A GO/SEALED; V147 B GO/SEALED; Phase-C pre-audio GO/SEALED; **V147 Phase C REAL-AUDIO = GO/SEALED**.
- Immutable candidate SHA `ca35c3492295a3079c17c35124df7a483166315e85649e95ded095c6c06b2b77`.
- 247 observational ±1 pitch changes; all structural/position/PDF/determinism gates green.
- One-use real-audio workflow sealed at `4b125f42dfa447e1fe86741c8f41c09dcaffc895`.
- Durable replay preservation is authorized from existing artifact only; no new audio work is allowed for preservation.
- Reference/gold/scoring remain untouched and unauthorized.
