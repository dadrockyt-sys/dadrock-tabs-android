# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 is permanently consumed after one failed reference score. V155 is protocol-invalid and never scoreable. V156 is permanently aborted before candidate. V157 completed exactly one reference-blind deterministic CPU generation run, independent structural QC PASS, candidate/receipts/QC are FROZEN, generation workflow self-deleted, and V157 reference-facing score calls remain 0. Next: seal one guarded one-use V157 scorer against the already-frozen professional reference/scorer, then score V157 exactly once.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; candidate generation/transcription must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Song / immutable shared identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Audio SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; historical source commit `74b0f815ff3f66f325220975c410621503de440f`; bytes `3478611`.
- Deterministically normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Source m104 = 2/4 (8 sixteenth steps); others 4/4.
- Meter map SHA256 `1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.

## Frozen professional references
- Rhythm 946 rows; SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31a4349eaa2c439f1b8662acd91618ab31bdca321555` is INVALID TYPO — use authoritative value below.
- Rhythm authoritative SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`.
- Lead 447 pitched rows; SHA256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`.
- Bass 547 pitched rows; SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`.
- Combined payload `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; Guitar 1393 / Bass 547; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Lead rendered pages 84–105 recovered and byte-authenticated; screenshot bytes remain uncommitted.

## V154 — CONSUMED / NEVER RETUNE
- Candidate SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`; Guitar 1089 / Bass 635; generation run `33096559281`, job `98602884120`.
- Score run `33139017517`, job `98745430956`; score SHA256 `c206f6bc951c6bd9b6cc19e6758c4aef6654f349cc1f5712df1f052e46fa798b`; reference-facing score count = **1 permanently closed**.
- Guitar F1 `0.04915390813859791` FAIL vs 0.80; Bass F1 `0.1116751269035533` FAIL.
- Root cause: V154 used `seconds / STEP_SECONDS`, hard-anchoring musical step 0 to audio t=0; no audio-derived origin/downbeat; diagnostics also show small cumulative drift and large residual pitch/polyphony errors.
- Reference-derived `-13.25` steps / diagnostic ~129.01 BPM are diagnosis only and forbidden future generation constants.

## V155 — PROTOCOL-INVALID / NEVER SCORE
- Prereg commit `e5f51474308db460d7317cfbc4204f616ee0b069`, blob `9d6979b0d447d137db43017dfd18c9afdcb2a4d2`.
- Two generation runs (`33140245244`, `33140267460`) violated single-run policy; nominally identical Demucs runs produced different bytes.
- V155 reference reads = 0; score calls = 0 forever.

## V156 — ABORTED BEFORE CANDIDATE / NEVER SCORE
- Sole run `33142942558`, job `98757604810`, run number 1.
- Deterministic separation PASS; environment receipt failed before candidate because cache lookup assumed Torch cache while Demucs 4.1 used Hugging Face cache; receipt block also omitted `import os`.
- Candidate/QC/freeze skipped; workflow later deleted.
- V156 candidate = NONE; reference reads = 0; score calls = 0 forever.

## Frozen musical architecture carried into V157
- CPU `htdemucs_6s`, shifts 1, jobs 1; dedicated Guitar/Bass/Drums; no fallback.
- Seed 0 Python/NumPy/Torch; deterministic Torch algorithms; Torch intra/inter-op threads 1; OMP/MKL/OpenBLAS/NumExpr threads 1; in-process Demucs; exactly one separation.
- Audio-derived dynamic beat times + deterministic 4/4 phase + piecewise-linear beat grid; no t=0 assumption/reference-derived timing constants.
- Bass = HPSS harmonic + pYIN + onset/voicing/pitch-change segmentation; no Basic Pitch for Bass.
- Guitar = dedicated Guitar stem + one fixed Basic Pitch 0.4.0 pass fused with harmonic CQT evidence; no threshold sweep/reference-guided completion.
- Exact pins: Python 3.10; torch 2.8.0+cpu; NumPy 1.26.4; SciPy 1.13.1; SoundFile 0.12.1; Demucs 4.1.0; Basic Pitch 0.4.0; librosa 0.11.0; imageio-ffmpeg 0.6.0.

## V157 — FROZEN CANDIDATE / STRUCTURAL QC PASS / PRE-SCORE
### Sealed setup
- Preregistration `debug/v157-cpu-autonomous/preregistration.json`; commit `d378d8c24b1c2103d20d5e2449e0cf8f49d9d52a`; Git blob `0bcca0fbb53abcc8ad8736d8e5e71e32a14004f6`.
- Canonical transcriber `validation/v157_cpu_multitrack/transcribe_hybrid.py`; Git blob `1d1725e2d79b173bd5fb0bfa7aefc25dce81dd58`.
- Independent structural QC `validation/v157_cpu_multitrack/structural_qc.py`; Git blob `5ff4df5b5c6b700272b349a1bbe709b15e17e794`.
- Frozen inherited reference-blind engine `validation/v155_cpu_multitrack/transcribe_hybrid.py`; Git blob `3357582dd8311b28f4b85f2ebfbc7acb8c9e4fb8`.
- Pre-run receipt `debug/v157-cpu-autonomous/pre-run-receipt.json`; Git blob `86e3419203f7001d2431f4bcf62113cbaba67786`; seal commit `c586feab7776cc016daae7ffeba617b242568a38`.

### Sole generation run
- Workflow creation commit `cf4a8191c761faac2ef7978d22c5138a3058ca52`.
- Sole V157 generation run `33143471258`, run number `1`, job `98759295729`; conclusion **SUCCESS**.
- Head-SHA audit shows the other workflow on the creation commit was only unrelated `cleanup-tab-preview`; there was exactly one V157 generation run.
- Generation workflow self-deleted on successful freeze.
- Freeze commit `c26e41d2` (full branch commit begins `c26e41d2`; resolve full SHA if needed before scoring receipts).

### Frozen candidate / environment / QC
- Candidate `debug/v157-cpu-autonomous/generated.json`.
- Candidate SHA256 `f5dc7094b72f8e3a988b1fdd59808cb056461d7e12a6d41508942cf499de3e71`; Git blob `3491814f4cc075aaf3eefaecf2d179f57d2d5dae`.
- Counts: combined Guitar **1779**; Bass **113**; pre-grid excluded 0/0.
- Generation receipt `debug/v157-cpu-autonomous/generation-receipt.json`; Git blob `785c8dc60936d424b1dcad3cdfa6fa733d87653b`; receipt SHA256 `7501b7639ef5284647af6dc6ad0b0e430254f19d8d419e0fd6f33dede6ffda8c`.
- Environment receipt `debug/v157-cpu-autonomous/environment-receipt.json`; Git blob `abdb956a64471211c21eeb5d6971770300dcd45b`; embedded environment-receipt SHA256 `123d5d2fa09b42914116bf7aae0e30fac43c63561f5a434d6bbe9e602cd27f9a`.
- Independent QC `debug/v157-cpu-autonomous/structural-qc.json`; Git blob `3528adbceb640743cc8f0e472d2cd62c49c1ebc3`; validation **PASS**.
- QC stream sources: Guitar 1366 Basic Pitch + 413 CQT = 1779; Bass 113 pYIN.
- Guitar MIDI 40–88; Bass MIDI 37–56.
- Timebase QC: 448 tracked beats; tracker tempo `129.19921875`; median inter-beat BPM `129.19921874999932`; interval CV `0.027276358719819024`; interval-band fraction 1.0; strictly increasing beat times PASS.
- Demucs model blob authenticated from Hugging Face cache: 54,885,744 bytes; SHA256 `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`.
- Stem SHA256: Guitar `b8685062c59f5c62253029f8294afdaf25f3f8adf8868ae97b47db09ab8838f9`; Bass `f109347354dd9ae4a293189834b1f6d58199a4eebe5d51dfeeedc6707c4a5316`; Drums `7ef184f2fc3b6f7fc12ea5c342bc537f6b69f1680ce36e9d4f7189be85d93e39`.
- **V157 candidate generation reference read = false; professional-reference paths opened = 0; reference-facing score calls = 0; GPU/Modal/CUDA = false; main/Production unchanged.**
- Candidate is now immutable/consumed for the upcoming one-time score. No retuning, filtering, correction, threshold sweep, or variant replacement is allowed from this point.

## Exact next steps — RESUME HERE
1. Resolve/record the full V157 freeze commit SHA and verify branch head/candidate/QC identities remain unchanged.
2. Build a V157-specific guarded one-use score wrapper/workflow that pins candidate SHA256 `f5dc7094...`, candidate Git blob `3491814f...`, QC PASS/blob `3528adbc...`, reference payload SHA256 `b39a203a...`, and frozen scorer blob `9644e657...`.
3. Before scoring, mechanically assert V157 score output/receipt do not already exist and scorer invocation count for V157 is zero.
4. Score frozen V157 exactly once against the already-frozen professional reference using the frozen scorer. No threshold tuning/variant selection/candidate rewriting.
5. Freeze score + score receipt and self-delete one-use score workflow. V157 reference-facing score count becomes exactly 1 permanently closed.
6. Check frozen gates: combined Guitar timing-aware pitch F1 >= 0.80 AND Bass timing-aware pitch F1 >= 0.80.
7. If either gate fails, diagnose only after score and move to a fresh version; never retune V157.
8. If both gates pass, then resume Rhythm/Lead role separation, string/fret assignment, techniques, and professional PDF work.
9. Save this checkpoint again immediately after the one-time score.
10. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
