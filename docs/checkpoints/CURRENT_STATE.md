# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 is permanently consumed after one failed reference score. V155 is protocol-invalid and never scoreable. V156 is permanently aborted before candidate. V157 completed exactly one deterministic reference-blind CPU generation run, independent structural QC PASS, then was scored exactly once under its sealed guard. BOTH V157 FRONT-END GATES FAILED. V157 is now permanently consumed: reference-facing score count = 1 forever, candidate must never be retuned/corrected/replaced/rescored. Next: post-score diagnosis only, then preregister a genuinely new reference-blind architecture/version.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; generation/transcription must not read them.
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
- Guitar F1 `0.04915390813859791`; Bass F1 `0.1116751269035533`; both FAIL vs 0.80.
- Root cause: V154 hard-anchored musical step 0 to audio `t=0`; diagnostics showed origin error + cumulative timebase drift + large residual pitch/polyphony errors.
- Reference-derived `-13.25` steps / diagnostic ~129.01 BPM remain diagnosis-only, forbidden generation constants.

## V155 — PROTOCOL INVALID / NEVER SCORE
- Preregistration commit `e5f51474308db460d7317cfbc4204f616ee0b069`; blob `9d6979b0d447d137db43017dfd18c9afdcb2a4d2`.
- Duplicate generation runs `33140245244` and `33140267460` violated single-run policy; nominally identical separation produced different bytes.
- V155 reference reads = 0; score calls = **0 forever**.

## V156 — PERMANENTLY ABORTED BEFORE CANDIDATE
- Intended run `33142942558`, job `98757604810`, passed deterministic separation but failed before candidate because model receipt scanned wrong cache and omitted `import os`.
- Candidate = NONE; reference reads 0; score calls 0. V156 permanently closed.
- A stale concurrent recreation later failed before any audio/candidate work and was deleted at `ba8681892a842b6e5af7536a24608bf506d32dd8`.

## Frozen V157 architecture / generation
- CPU `htdemucs_6s`, shifts 1, jobs 1; dedicated Guitar/Bass/Drums; no fallback.
- Seed 0 Python/NumPy/Torch; deterministic Torch algorithms; Torch intra/inter-op threads 1; OMP/MKL/OpenBLAS/NumExpr 1; one in-process separation.
- Audio-derived dynamic beat times + deterministic 4/4 phase + piecewise-linear beat grid; no `t=0` assumption/reference-derived timing constants.
- Bass: HPSS harmonic + pYIN + onset/voicing/pitch-change segmentation; no Basic Pitch.
- Guitar: dedicated Guitar stem + fixed Basic Pitch 0.4.0 pass fused with harmonic CQT evidence; no threshold sweep/reference-guided completion.
- Preregistration `debug/v157-cpu-autonomous/preregistration.json`; Git blob `0bcca0fbb53abcc8ad8736d8e5e71e32a14004f6`.
- Canonical transcriber blob `1d1725e2d79b173bd5fb0bfa7aefc25dce81dd58`; independent QC blob `5ff4df5b5c6b700272b349a1bbe709b15e17e794`; inherited reference-blind engine blob `3357582dd8311b28f4b85f2ebfbc7acb8c9e4fb8`.
- Pre-run receipt Git blob `86e3419203f7001d2431f4bcf62113cbaba67786`; file SHA256 `0144f991b211681e8e0a8860cf08fef3b378ca343ab726544c0ebe5bee824402`; seal commit `c586feab7776cc016daae7ffeba617b242568a38`.
- Sole generation run `33143471258`, run number 1, job `98759295729`; SUCCESS; generation workflow self-deleted.
- Candidate freeze commit `c26e41d239d44d656bf57cf195ed39416658b680`.
- Environment receipt Git blob `abdb956a64471211c21eeb5d6971770300dcd45b`; SHA256 `123d5d2fa09b42914116bf7aae0e30fac43c63561f5a434d6bbe9e602cd27f9a`.
- Authenticated `htdemucs_6s` model blob SHA256 `d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411`, bytes 54,885,744.
- Stem SHA256: Guitar `b8685062c59f5c62253029f8294afdaf25f3f8adf8868ae97b47db09ab8838f9`; Bass `f109347354dd9ae4a293189834b1f6d58199a4eebe5d51dfeeedc6707c4a5316`; Drums `7ef184f2fc3b6f7fc12ea5c342bc537f6b69f1680ce36e9d4f7189be85d93e39`.
- Frozen candidate `debug/v157-cpu-autonomous/generated.json`; SHA256 `f5dc7094b72f8e3a988b1fdd59808cb056461d7e12a6d41508942cf499de3e71`; Git blob `3491814f4cc075aaf3eefaecf2d179f57d2d5dae`.
- Candidate counts: combined Guitar 1779; Bass 113; pre-grid excluded 0/0.
- Guitar sources Basic Pitch 1366 + CQT 413; Bass pYIN 113.
- Timebase QC: 448 beats; tracker BPM `129.19921875`; median inter-beat BPM `129.19921874999932`; IBI CV `0.027276358719819024`; interval-consistency 1.0.
- Generation receipt SHA256 `7501b7639ef5284647af6dc6ad0b0e430254f19d8d419e0fd6f33dede6ffda8c`; Git blob `785c8dc60936d424b1dcad3cdfa6fa733d87653b`.
- Independent structural QC `debug/v157-cpu-autonomous/structural-qc.json`; Git blob `3528adbceb640743cc8f0e472d2cd62c49c1ebc3`; PASS; pre-score reference calls 0.

## V157 one-use scoring protocol — COMPLETE / PERMANENTLY CLOSED
- Guard `validation/v157_cpu_multitrack/run_frontend_reference_score_once.py`; Git blob `6396ff11f1b2960fb4c80c1633786c3089ec4883`; staged commit `d9eaecf794199c5abc0e756bf1a9b8e129c94f09`.
- Pre-score receipt `debug/v157-cpu-autonomous/frontend-reference-score/pre-score-receipt.json`; Git blob `d7d6fc5a7eb15a18a8a79293aaa057a44a1dde5a`; seal commit `0068a1d640a37add8a19ffc60545c468b2c0fd68`; score calls 0 at seal.
- Pre-score checkpoint commit `aeba8811031d336bd8e93a8a61bd6514f2a740e3`.
- Score workflow creation/sole trigger commit `7f564677f6d9956434710266c296f56d1b2c39ed`.
- Sole score run `33143986627`, run number 1, job `98760898781`; SUCCESS.
- Guard/scorer invocation count = exactly 1; no automatic retry; candidate/reference/scorer identities stayed frozen.
- Score workflow self-deleted; score freeze commit `19317e7e44687e910088892cf9bf3e1157efc45c`.
- Score `debug/v157-cpu-autonomous/frontend-reference-score/score.json`; Git blob `d32e92ccabb37d1ab71697324f13a556793d63f2`; SHA256 `ffd66347990eff113814f207c303773734e79c0461fa4e4d129f1de8472594d8`.
- Score receipt `debug/v157-cpu-autonomous/frontend-reference-score/score-receipt.json`; Git blob `d1e3145cae8b12e612012533e9060d21c95ccf24`; validation PASS; `referenceFacingScoreCalls=1`; `scorerInvocationCountInWrapper=1`.
- **V157 reference-facing score count = 1 permanently closed. Never score V157 again.**

## V157 frozen score — BOTH FRONT-END GATES FAIL
### Combined Guitar
- Generated 1779 / reference 1393.
- Primary ±0.5-step same-MIDI: matched 122; precision `0.06857785272625071`; recall `0.08758076094759512`; **F1 `0.07692307692307694` — FAIL vs 0.80**.
- Gross ±2-step: matched 345; precision `0.19392917369308602`; recall `0.24766690595836324`; F1 `0.21752837326607818`.
- Pitch-content-by-measure diagnostic: matched 717; precision `0.403035413153457`; recall `0.5147164393395549`; F1 `0.4520807061790668`.
- Matched primary timing deltas are exactly 0 because V157 snaps generated notes to integer steps and the exact primary matches land on identical source-grid steps; this does NOT mean overall timing is solved.

### Bass
- Generated 113 / reference 547.
- Primary ±0.5-step same-MIDI: matched 19; precision `0.168141592920354`; recall `0.03473491773308958`; **F1 `0.05757575757575757` — FAIL vs 0.80**.
- Gross ±2-step: matched 47; precision `0.415929203539823`; recall `0.08592321755027423`; F1 `0.14242424242424245`.
- Pitch-content-by-measure diagnostic: matched 74; precision `0.6548672566371682`; recall `0.13528336380255943`; F1 `0.22424242424242424`.
- Bass is severely under-generated (113 vs 547 reference events), so recognition/segmentation recall is a major failure independent of strict timing.

## Immediate diagnosis implications — DO NOT RETUNE V157
- V157 improves Guitar strict F1 over V154 (`0.0769` vs `0.0492`) but remains far below the 0.80 gate.
- V157 Bass strict F1 (`0.0576`) is worse than V154 (`0.1117`) because the new pYIN segmentation is far too sparse, despite comparatively higher Bass precision.
- Guitar pitch-content-by-measure F1 (`0.4521`) is similar to V154 (`0.4633`), showing the hybrid CQT/Basic-Pitch architecture did not materially solve underlying Guitar pitch/polyphony content.
- Gross timing relaxation lifts Guitar to `0.2175` and Bass to `0.1424`; timing/grid placement remains relevant, but the large pitch-content and count errors show timing alone cannot solve V157.
- No V157 correction, threshold sweep, candidate filtering, segmentation retune, grid shift, variant generation, or rescoring is permitted.

## Exact next steps — RESUME HERE
1. Re-fetch latest checkpoint/head before writes because concurrent continuations exist.
2. Run **post-score diagnostic only** on the frozen V157 candidate/reference. Diagnostics may read both because scoring is complete, but must not call the official scorer again, write a corrected candidate, select variants, or feed exact reference-derived corrections into a future generator.
3. Diagnose separately:
   - V157 timebase/bar-phase alignment vs the frozen reference (architecture evidence only);
   - Guitar Basic-Pitch retained events vs CQT-only completion, octave/register/polyphony/false-positive patterns;
   - Bass pYIN segmentation sparsity, repeated-note/onset recall, pitch range/register, and whether event-count failure dominates before timing.
4. Freeze/checkpoint diagnostic findings; V157 score count stays 1.
5. Preregister a fresh successor version before any new generation. It must be a genuine architecture change based on general/reference-blind principles, not a V157 threshold sweep or hardcoded correction.
6. Any future candidate must again be generated exactly once reference-blind, independently QC’d/frozen before reference access, and scored once under a newly sealed protocol.
7. Do not resume Rhythm/Lead role separation, string/fret assignment, techniques, or PDF work until a future front-end candidate passes both acoustic gates.
8. Fresh explicit authorization remains required immediately before Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
