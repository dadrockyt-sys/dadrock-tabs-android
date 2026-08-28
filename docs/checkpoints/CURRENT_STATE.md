# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 is permanently consumed after one failed reference score. V155 is protocol-invalid/aborted and must never be scored. V156 is permanently ABORTED BEFORE CANDIDATE after its sole run passed deterministic separation but failed model-cache receipt bookkeeping. V157 is now PREREGISTERED / CANONICAL-IMPLEMENTATION READY / PRE-RUN SEALED BEFORE GENERATION. No V157 candidate exists, no professional reference has been read, and V157 reference-facing score calls remain 0. Next: create the V157 generation workflow exactly once; workflow creation itself is the sole trigger.**

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
- Rhythm: 946 rows; SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`.
- Lead: 447 pitched rows; SHA256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`.
- Bass: 547 pitched rows; SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`.
- Combined payload `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; Guitar 1393 / Bass 547; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Lead rendered pages 84–105 were recovered and byte-authenticated; screenshot bytes remain uncommitted.

## V154 — CONSUMED / NEVER RETUNE
- Candidate SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`; Guitar 1089 / Bass 635; generation run `33096559281`, job `98602884120`.
- Score run `33139017517`, job `98745430956`; score SHA256 `c206f6bc951c6bd9b6cc19e6758c4aef6654f349cc1f5712df1f052e46fa798b`; reference-facing score count = **1 permanently closed**.
- Guitar F1 `0.04915390813859791` FAIL vs 0.80; Bass F1 `0.1116751269035533` FAIL.
- Root cause: V154 used `seconds / STEP_SECONDS` with audio t=0 as musical step 0, no audio-derived origin/downbeat and no explicit latency compensation; diagnostics also show small cumulative drift and large residual pitch/polyphony errors.
- Reference-derived `-13.25` steps / ~129.01 BPM are diagnosis only and forbidden as future generation constants.

## V155 — PROTOCOL-INVALID / NEVER SCORE
- Prereg commit `e5f51474308db460d7317cfbc4204f616ee0b069`, blob `9d6979b0d447d137db43017dfd18c9afdcb2a4d2`.
- Workflow accidentally triggered twice (`33140245244` and `33140267460`), violating single-run policy; nominally identical Demucs runs produced different stem/candidate hashes.
- V155 professional-reference reads = 0; V155 score calls = 0 forever. Never compare/select/score V155 outputs.

## V156 — ABORTED BEFORE CANDIDATE / NEVER GENERATE OR SCORE
- Determinism-amended prereg blob `25a0a921e3245049a7f64fd3cb823e6767fe55da`.
- Canonical transcriber blob `961e18f66766e51abb42f46e529730fcaa2807b4`; independent QC blob `3b1018e751deecdfb0efca100c29848256ee1234`; inherited reference-blind engine blob `3357582dd8311b28f4b85f2ebfbc7acb8c9e4fb8`.
- Pre-run receipt blob `4591695763a1e59d6b1b2bfa2600969ff4b0201f`; seal commit `69314570f5e25cd43a679459f42b3c3ba0197965`.
- Sole generation run `33142942558`, run number 1, job `98757604810`.
- PASS before candidate: identity/isolation checks, exact audio, exact pinned CPU deps, deterministic normalization, seeded in-process CPU `htdemucs_6s` separation, branch refresh.
- FAILURE before candidate: environment receipt assumed `~/.cache/torch/hub/checkpoints`; it was empty while Demucs 4.1 used another cache path. Same receipt block also omitted `import os` before using `os.environ`.
- Candidate generation/QC/freeze were skipped; branch `generated.json`, generation receipt, and QC are absent.
- Workflow permanently deleted at commit `138d99ae3d0c0ce8990cfcf79a8d7a175d52ba18`.
- **V156 candidate = NONE; reference reads = 0; score calls = 0.**

## Frozen musical architecture — V157 MUST PRESERVE
- CPU-only `htdemucs_6s`, shifts 1, jobs 1, dedicated Guitar/Bass/Drums, no fallback.
- Seed 0 Python/NumPy/Torch; deterministic Torch algorithms; Torch intra/inter-op threads 1; OMP/MKL/OpenBLAS/NumExpr threads 1; in-process Demucs; exactly one separation.
- Audio-derived dynamic beat times + deterministic 4/4 phase + piecewise-linear beat-grid mapping; no t=0 assumption/reference-derived timing constants.
- Bass = HPSS harmonic + pYIN + onset/voicing/pitch-change segmentation; no Basic Pitch for Bass.
- Guitar = dedicated Guitar stem + one fixed Basic Pitch 0.4.0 pass fused with harmonic CQT evidence; no threshold sweep/reference-guided completion.
- Exact dependency pins: Python 3.10; torch 2.8.0+cpu; NumPy 1.26.4; SciPy 1.13.1; SoundFile 0.12.1; Demucs 4.1.0; Basic Pitch 0.4.0; librosa 0.11.0; imageio-ffmpeg 0.6.0.

## V157 — PREREGISTERED / PRE-RUN SEALED / NO CANDIDATE
- `V157` confirmed unused before naming.
- Preregistration: `debug/v157-cpu-autonomous/preregistration.json`; commit `d378d8c24b1c2103d20d5e2449e0cf8f49d9d52a`; Git blob `0bcca0fbb53abcc8ad8736d8e5e71e32a14004f6`; status `PREREGISTERED_BEFORE_GENERATION`.
- V157 explicitly states V155/V156 generated musical outputs are not inputs and no professional reference influenced the setup repair.
- Only change from V156 is pre-candidate environment/model-cache receipt mechanics: import `os`; recursively scan both `~/.cache/torch/hub/checkpoints` and `~/.cache/huggingface/hub`; resolve symlinks; ignore lock/metadata files; record unique resolved files >=1 MiB with logical path/resolved path/bytes/SHA256; require at least one; do not run a second separation.
- Canonical V157 transcriber: `validation/v157_cpu_multitrack/transcribe_hybrid.py`; Git blob `1d1725e2d79b173bd5fb0bfa7aefc25dce81dd58`.
- Independent V157 structural QC: `validation/v157_cpu_multitrack/structural_qc.py`; Git blob `5ff4df5b5c6b700272b349a1bbe709b15e17e794`.
- Frozen inherited reference-blind musical engine remains `validation/v155_cpu_multitrack/transcribe_hybrid.py`; Git blob `3357582dd8311b28f4b85f2ebfbc7acb8c9e4fb8`.
- Candidate schema `dadrock.tabs.v157.cpu-hybrid-generated.v1`; receipt schema `dadrock.tabs.v157.cpu-hybrid-generation-receipt.v1`; environment receipt schema `dadrock.tabs.v157.cpu-environment-receipt.v1`; QC schema `dadrock.tabs.v157.reference-blind-structural-qc.v1`.
- Pre-run receipt: `debug/v157-cpu-autonomous/pre-run-receipt.json`; seal commit `c586feab7776cc016daae7ffeba617b242568a38`; Git blob `86e3419203f7001d2431f4bcf62113cbaba67786`.
- Boundary audit before seal: V157 `generated.json` absent; V157 generation receipt absent; V157 generation workflow absent.
- **V157 candidate = NONE; professional-reference read = NO; reference-facing score calls = 0.**

## V157 trigger/freeze rules — MUST NOT VIOLATE
- `.github/workflows/v157-generate-reference-blind-once.yml` creation itself is the **single generation trigger**. Never edit/arm it afterward.
- Expected generation run count/run number = exactly 1; duplicate run => abort V157 without scoring.
- Make no unrelated branch writes while the run is active.
- Before candidate creation verify exact audio/prereg/pre-run/transcriber/QC/engine identities and reference isolation.
- Workflow must install exact CPU deps, normalize exact audio, run exactly one seeded in-process deterministic `htdemucs_6s` separation, capture model identities from generic cache roots, record stem hashes/environment, run canonical transcription, run independent QC, freeze one candidate + receipts + QC, and self-delete.
- Reference-facing score calls remain 0 through freeze.

## Exact next steps — RESUME HERE
1. Create `.github/workflows/v157-generate-reference-blind-once.yml` exactly once. Creation is sole trigger; no later arm edit.
2. Make no branch writes while run 1 is active.
3. Verify run number/count = 1 and all pre-candidate identity/isolation checks pass.
4. Let workflow run exact pinned CPU dependencies, deterministic normalization, one seeded in-process Demucs separation, robust cache/model receipt capture, canonical transcription and independent QC.
5. If setup fails before candidate, repair only execution/receipt mechanics allowed by preregistration; if that would require a second V157 generation run, abort V157 and move versions rather than violate trigger policy.
6. If candidate is created and QC fails, freeze failure/end V157; never generate replacement V157 candidate.
7. On success verify candidate/receipt/QC hashes and exactly one workflow run, then checkpoint at V157 score calls 0.
8. Only then create one guarded one-use V157 score workflow and score exactly once against frozen reference/scorer. Never retune consumed V157.
9. Fresh explicit user authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
10. Do not resume Rhythm/Lead role separation, string/fret assignment, techniques, or PDF polishing until a front-end candidate passes acoustic gates.
