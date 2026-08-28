# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 is permanently consumed after one failed reference score. V155 is protocol-invalid and never scoreable. V156 is permanently aborted before candidate. V157 completed exactly one deterministic reference-blind CPU generation run, independent structural QC PASS, candidate/receipts/QC are FROZEN, and a V157-specific one-use scoring guard + pre-score receipt are now SEALED. V157 score output/receipt are absent and reference-facing score calls remain 0. Next: create the one-use V157 score workflow exactly once and score the frozen candidate exactly once.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; candidate generation/transcription must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Never retune/correct/select a replacement for a consumed scored candidate.
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Immutable shared song / reference identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Historical audio commit `74b0f815ff3f66f325220975c410621503de440f`.
- Audio SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; bytes `3478611`.
- Deterministically normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Source m104 = 2/4 (8 sixteenth steps); others 4/4.
- Meter map SHA256 `1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Rhythm scorer-ready 946 rows; SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`.
- Lead scorer-ready 447 rows; SHA256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`.
- Bass scorer-ready 547 rows; SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`.
- Combined frozen reference `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; Guitar 1393 / Bass 547; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; freeze run `33138868905`, job `98744968281`, commit `46e42ab`.

## V154 — CONSUMED / SCORE COUNT PERMANENTLY 1
- Candidate SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`; Guitar 1089 / Bass 635; generation run `33096559281`, job `98602884120`.
- Score SHA256 `c206f6bc951c6bd9b6cc19e6758c4aef6654f349cc1f5712df1f052e46fa798b`; score run `33139017517`, job `98745430956`.
- Guitar timing-aware pitch F1 `0.04915390813859791` FAIL vs 0.80; Bass `0.1116751269035533` FAIL vs 0.80.
- Root cause: V154 hard-anchored musical step 0 to audio `t=0` via `seconds / STEP_SECONDS`; no audio-derived origin/downbeat and no explicit latency compensation. Diagnostics also show cumulative timebase drift and large residual pitch/polyphony errors.
- Reference-derived `-13.25` steps / diagnostic ~129.01 BPM are diagnosis only and forbidden as generation constants.

## V155 — PROTOCOL INVALID / NEVER SCORE
- Preregistration commit `e5f51474308db460d7317cfbc4204f616ee0b069`; Git blob `9d6979b0d447d137db43017dfd18c9afdcb2a4d2`.
- Duplicate generation runs `33140245244` and `33140267460` violated `singleGenerationRun=true`; nominally identical separation runs produced different bytes.
- V155 professional-reference reads = 0; score calls = **0 forever**.

## V156 — PERMANENTLY ABORTED BEFORE CANDIDATE / NEVER SCORE
- Sole intended run `33142942558`, job `98757604810`, passed deterministic separation but failed before candidate because model receipt scanned the wrong cache and omitted `import os`.
- Candidate/transcription/QC/freeze were skipped. Candidate = NONE; reference reads 0; score calls 0.
- Original workflow deleted; stale concurrent recreation later failed at its first verification step before any candidate and was deleted at commit `ba8681892a842b6e5af7536a24608bf506d32dd8`.
- V156 is permanently closed.

## Frozen V157 musical architecture
- CPU-only `htdemucs_6s`, shifts 1, jobs 1; dedicated Guitar/Bass/Drums; no fallback.
- Seed 0 Python/NumPy/Torch; deterministic Torch algorithms; Torch intra/inter-op threads 1; OMP/MKL/OpenBLAS/NumExpr threads 1; one in-process separation only.
- Audio-derived dynamic beat times + deterministic 4/4 phase + piecewise-linear beat-grid mapping; no `t=0` assumption/reference-derived timing constants.
- Bass: HPSS harmonic + pYIN + onset/voicing/pitch-change segmentation; no Basic Pitch.
- Guitar: dedicated Guitar stem + one fixed Basic Pitch 0.4.0 pass fused with harmonic CQT evidence; no threshold sweep/reference-guided completion.
- Exact dependency pins: Python 3.10; torch 2.8.0+cpu; NumPy 1.26.4; SciPy 1.13.1; SoundFile 0.12.1; Demucs 4.1.0; Basic Pitch 0.4.0; librosa 0.11.0; imageio-ffmpeg 0.6.0.

## V157 — FROZEN CANDIDATE / STRUCTURAL QC PASS
### Setup / implementation seals
- Preregistration `debug/v157-cpu-autonomous/preregistration.json`; commit `d378d8c24b1c2103d20d5e2449e0cf8f49d9d52a`; Git blob `0bcca0fbb53abcc8ad8736d8e5e71e32a14004f6`.
- Canonical transcriber `validation/v157_cpu_multitrack/transcribe_hybrid.py`; Git blob `1d1725e2d79b173bd5fb0bfa7aefc25dce81dd58`.
- Independent structural QC `validation/v157_cpu_multitrack/structural_qc.py`; Git blob `5ff4df5b5c6b700272b349a1bbe709b15e17e794`.
- Frozen inherited reference-blind engine `validation/v155_cpu_multitrack/transcribe_hybrid.py`; Git blob `3357582dd8311b28f4b85f2ebfbc7acb8c9e4fb8`.
- Pre-run identity receipt `debug/v157-cpu-autonomous/pre-run-receipt.json`; Git blob `86e3419203f7001d2431f4bcf62113cbaba67786`; file SHA256 `0144f991b211681e8e0a8860cf08fef3b378ca343ab726544c0ebe5bee824402`; seal commit `c586feab7776cc016daae7ffeba617b242568a38`.

### Sole V157 generation run
- Workflow creation commit `cf4a8191c761faac2ef7978d22c5138a3058ca52`.
- Sole generation run `33143471258`, run number 1, job `98759295729`; conclusion SUCCESS.
- All identity/isolation, exact-audio, dependency, normalization, seeded deterministic separation, branch-refresh, repaired environment receipt, canonical transcription, independent-QC, and self-seal steps passed.
- Generation workflow self-deleted.
- Freeze commit `c26e41d239d44d656bf57cf195ed39416658b680`.
- No GPU/Modal/CUDA; `main`/Production untouched.

### Frozen environment / candidate / QC
- Environment receipt `debug/v157-cpu-autonomous/environment-receipt.json`; Git blob `abdb956a64471211c21eeb5d6971770300dcd45b`; file SHA256 `123d5d2fa09b42914116bf7aae0e30fac43c63561f5a434d6bbe9e602cd27f9a`.
- Authenticated `htdemucs_6s` HF model blob: 54,885,744 bytes; SHA256 `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`.
- Stem SHA256: Guitar `b8685062c59f5c62253029f8294afdaf25f3f8adf8868ae97b47db09ab8838f9`; Bass `f109347354dd9ae4a293189834b1f6d58199a4eebe5d51dfeeedc6707c4a5316`; Drums `7ef184f2fc3b6f7fc12ea5c342bc537f6b69f1680ce36e9d4f7189be85d93e39`.
- Candidate `debug/v157-cpu-autonomous/generated.json`; SHA256 `f5dc7094b72f8e3a988b1fdd59808cb056461d7e12a6d41508942cf499de3e71`; Git blob `3491814f4cc075aaf3eefaecf2d179f57d2d5dae`.
- Counts: combined Guitar 1779; Bass 113; pre-grid excluded 0/0.
- Guitar sources: Basic Pitch 1366 + CQT 413; MIDI 40–88. Bass: pYIN 113; MIDI 37–56.
- Timebase QC: 448 beats; tracker BPM `129.19921875`; median inter-beat BPM `129.19921874999932`; IBI CV `0.027276358719819024`; interval-consistency fraction 1.0; strictly increasing beat times PASS.
- Generation receipt `debug/v157-cpu-autonomous/generation-receipt.json`; Git blob `785c8dc60936d424b1dcad3cdfa6fa733d87653b`; file SHA256 `7501b7639ef5284647af6dc6ad0b0e430254f19d8d419e0fd6f33dede6ffda8c`.
- Independent QC `debug/v157-cpu-autonomous/structural-qc.json`; Git blob `3528adbceb640743cc8f0e472d2cd62c49c1ebc3`; validation PASS.
- QC safety: referenceRead=false; professionalQualityMetricUsed=false; referenceFacingScoreCalls=0; thresholdSweep=false; variantSelection=false; GPU=false; humanCorrection=false; main/Production unchanged.
- Candidate is immutable. Never regenerate/filter/retune/correct/select a replacement V157 candidate.

## V157 — PRE-SCORE GUARD SEALED / SCORE CALLS 0
- Guard: `validation/v157_cpu_multitrack/run_frontend_reference_score_once.py`; staged commit `d9eaecf794199c5abc0e756bf1a9b8e129c94f09`; Git blob `6396ff11f1b2960fb4c80c1633786c3089ec4883`.
- Guard pins exact candidate SHA/Git blob, independent QC blob, frozen reference SHA256, frozen scorer blob, and candidate freeze commit.
- Guard refuses existing score/receipt, verifies candidate/QC/scorer locally before reference access, opens/hash-checks the reference only inside the guarded one-use invocation, invokes the frozen scorer exactly once with no retry, verifies inputs unchanged, then writes a score receipt.
- Pre-score receipt: `debug/v157-cpu-autonomous/frontend-reference-score/pre-score-receipt.json`; seal commit `0068a1d640a37add8a19ffc60545c468b2c0fd68`.
- Pre-score receipt validation PASS; score path absent at seal; score-receipt path absent at seal; reference-facing score calls = 0; scorer invocation count = 0.
- Frozen score inputs:
  - candidate SHA256 `f5dc7094b72f8e3a988b1fdd59808cb056461d7e12a6d41508942cf499de3e71`, Git blob `3491814f4cc075aaf3eefaecf2d179f57d2d5dae`;
  - QC Git blob `3528adbceb640743cc8f0e472d2cd62c49c1ebc3`;
  - reference SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`;
  - scorer Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`;
  - guard Git blob `6396ff11f1b2960fb4c80c1633786c3089ec4883`.
- **V157 reference-facing score calls remain 0.**

## Exact next steps — RESUME HERE
1. Re-fetch latest checkpoint/head immediately before the score-workflow write because concurrent continuations exist.
2. Confirm V157 score/score-receipt still absent and pre-score receipt/guard/candidate/QC identities unchanged.
3. Create `.github/workflows/v157-score-reference-once.yml` exactly once. Workflow creation is the sole score trigger; no later arm edit and no branch writes while active.
4. Workflow must verify exact pre-score/candidate/QC/guard/scorer identities and absence of prior V157 score outputs before invoking the guard.
5. Run the V157 guard exactly once on CPU. This is the single permitted reference-facing score call. No automatic retry if the guard/scorer fails after reference access begins.
6. Freeze score + score receipt and self-delete the workflow. V157 reference-facing score count becomes exactly 1 permanently closed.
7. Evaluate frozen gates: combined Guitar timing-aware pitch F1 >= 0.80 AND Bass timing-aware pitch F1 >= 0.80.
8. If either gate fails, diagnose only after score and move architectural changes to a fresh version; never retune/rescore V157.
9. If both gates pass, resume Rhythm/Lead role separation, string/fret assignment, techniques, and professional PDF work.
10. Save `docs/checkpoints/CURRENT_STATE.md` immediately after the score.
11. Fresh explicit authorization remains required immediately before Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
