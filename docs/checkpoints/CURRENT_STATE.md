# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 is permanently consumed after one failed reference score. V155 is protocol-invalid/aborted and must never be scored. V156 is the clean successor: determinism-amended preregistration, canonical transcriber, independent structural QC, and immutable pre-run identity receipt are SEALED BEFORE GENERATION. No V156 candidate exists, no V156 professional reference has been read, and V156 reference-facing score calls remain 0. Next: create the V156 generation workflow exactly once; workflow creation itself is the sole trigger.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; candidate generation/transcription must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Song / immutable shared identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Audio: `public/gomywayfullaitest.m4a`; SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Source m104 = 2/4 (8 sixteenth steps); others 4/4.
- Meter map: `research/v154-professional-references/source-meter-to-fixed-grid-mapping.json`; SHA256 `1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648`.
- Frozen scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.

## Frozen professional references
- Rhythm: `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json`; 946 rows; SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`.
- Lead: `research/v154-professional-references/scorer-ready/lead-scorer-ready.json`; 447 pitched rows; SHA256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`.
- Lead timing: `research/v154-professional-references/lead-source-local-attack-timing.json`; SHA256 `a1c30e9a14048fac6da6801d1ace1db203daf8807511f26c76a268e3cbf426c3`.
- Bass: `research/v154-professional-references/scorer-ready/bass-scorer-ready.json`; 547 pitched rows; SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`.
- Bass timing: `research/v154-professional-references/bass-source-local-attack-timing.json`; SHA256 `7d2f4eed21413c6169ec8fcea75274b64c6dc8bb5f3c8de9cbc536b94afab244`.
- Combined reference: `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; Guitar 1393 / Bass 547; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; freeze run `33138868905`, job `98744968281`, commit `46e42ab`.
- Lead rendered pages 84–105 were recovered and byte-authenticated; screenshot bytes remain uncommitted.

## V154 — CONSUMED / NEVER RETUNE
- Candidate: `debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json`; SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`; Guitar 1089 / Bass 635.
- Generation run `33096559281`, job `98602884120`, head `986e2a69a6cb877a203d2f8b04115914dc8fd2e6`.
- Frozen score: `debug/v154-cpu-autonomous/v154-frontend-reference-score/score.json`; SHA256 `c206f6bc951c6bd9b6cc19e6758c4aef6654f349cc1f5712df1f052e46fa798b`.
- Score run `33139017517`, job `98745430956`; reference-facing score count = **1 permanently closed**.
- Combined Guitar primary timing-aware pitch F1 `0.04915390813859791` — FAIL vs 0.80.
- Bass primary timing-aware pitch F1 `0.1116751269035533` — FAIL vs 0.80.
- Never modify, threshold-sweep, correct, select a tuned replacement, or rescore V154.

### V154 frozen diagnostics
- Architecture diagnostic: `debug/v154-cpu-autonomous/v154-frontend-reference-score/architecture-diagnostic.json`; SHA256 `bcc7aa275fb9c8dab3e0e9350043c5d85d48788bc13c672d97ad949d4d5595cd`; run `33139198143`, job `98746009145`.
- Its `measureIndexShiftScanPitchContent` submetric is invalid/no-op and must be disregarded; `globalAbsoluteShiftScan` remains valid.
- Timebase diagnostic: `debug/v154-cpu-autonomous/v154-frontend-reference-score/timebase-diagnostic.json`; SHA256 `ddaddaa4cfff1de1b5e7466813d9e08cfaeb9451b5a08406e820209543fe2f3c`; run `33139677372`, job `98747482513`.
- Root cause: V154 mapped `absolute_step_float = seconds / STEP_SECONDS`, hard-anchoring musical step 0 to audio timestamp 0, with no audio-derived downbeat/phase origin and no explicit latency compensation.
- Valid diagnostic evidence indicates a large shared origin error plus small cumulative drift. Reference-derived `-13.25` steps and diagnostic ~129.01 BPM values are diagnosis only and must never become future generation constants.
- Residual pitch/polyphony error remains large, so timing repair alone is insufficient.

## V155 — PROTOCOL-INVALID / ABORTED / NEVER SCORE
- Preregistration: `debug/v155-cpu-autonomous/preregistration.json`; commit `e5f51474308db460d7317cfbc4204f616ee0b069`; Git blob `9d6979b0d447d137db43017dfd18c9afdcb2a4d2`.
- Sealed `singleCandidate=true` and `singleGenerationRun=true`, but workflow creation and a later arm edit caused two CPU generation runs.
- Run 1 `33140245244`, job `98749260662`: candidate creation passed, freeze/rebase failed; non-authoritative candidate SHA256 `5ca0fd218a6efd5ea8765590b259f8d8510697c8487bf3ef65a3d9339054dc51`; Guitar 1364 / Bass 79.
- Run 2 `33140267460`, job `98749332172`: succeeded and self-deleted workflow; non-authoritative committed candidate SHA256 `cb5275aab111153f098e4f2e8b94ccf88d5d0052e2f528133702e870dac137ea`; Guitar 1359 / Bass 81; freeze commit `58b8c7d00a9c7e868531eb0ecab0c48507c7aa77`.
- The two nominally identical `htdemucs_6s --shifts 1` runs produced different stem/candidate hashes, exposing CPU execution nondeterminism.
- **V155 professional-reference reads = 0; V155 reference-facing score calls = 0 forever.** Never compare/select or score V155 outputs.

## V156 — CLEAN SUCCESSOR / PRE-RUN SEALED / NO CANDIDATE
- V156 was confirmed unused before naming.
- Determinism-amended preregistration: `debug/v156-cpu-autonomous/preregistration.json`; Git blob `25a0a921e3245049a7f64fd3cb823e6767fe55da`.
- Status: `PREREGISTERED_BEFORE_GENERATION_AMENDED_EXECUTION_DETERMINISM`.
- Amendment occurred before any V156 generation/reference access and changes execution determinism only; recognition/timebase quality parameters are unchanged.
- Determinism: seed `0` for Python/NumPy/Torch; deterministic Torch algorithms; Torch intra/inter-op threads 1; OMP/MKL/OpenBLAS/NumExpr threads 1; in-process Demucs after seed initialization; exactly one separation.
- Separation remains CPU `htdemucs_6s`, shifts 1, jobs 1, dedicated Guitar/Bass/Drums, no fallback model.
- Timebase remains audio-derived dynamic beat times + deterministic 4/4 phase + piecewise-linear beat mapping; no `t=0` assumption and no reference-derived timing constants.
- Bass remains HPSS harmonic + pYIN + onset/voicing/pitch-change segmentation; no Basic Pitch for Bass.
- Guitar remains dedicated Guitar stem + one fixed Basic Pitch pass fused with harmonic CQT evidence; no threshold sweep/reference-guided completion.

### V156 canonical implementation identities
- Canonical transcriber: `validation/v156_cpu_multitrack/transcribe_hybrid.py`; Git blob `961e18f66766e51abb42f46e529730fcaa2807b4`.
- Independent structural QC: `validation/v156_cpu_multitrack/structural_qc.py`; Git blob `3b1018e751deecdfb0efca100c29848256ee1234`.
- Frozen inherited reference-blind musical engine: `validation/v155_cpu_multitrack/transcribe_hybrid.py`; Git blob `3357582dd8311b28f4b85f2ebfbc7acb8c9e4fb8`.
- V155 generated musical outputs are not V156 inputs.
- Candidate schema `dadrock.tabs.v156.cpu-hybrid-generated.v1`.
- Generation receipt schema `dadrock.tabs.v156.cpu-hybrid-generation-receipt.v1`.
- Independent QC schema `dadrock.tabs.v156.reference-blind-structural-qc.v1`.
- Exact dependency pins include Python 3.10, torch 2.8.0+cpu, NumPy 1.26.4, SciPy 1.13.1, SoundFile 0.12.1, Demucs 4.1.0, Basic Pitch 0.4.0, librosa 0.11.0, imageio-ffmpeg 0.6.0.

### V156 sealed pre-run identity receipt
- `debug/v156-cpu-autonomous/pre-run-receipt.json`.
- Seal commit `69314570f5e25cd43a679459f42b3c3ba0197965`.
- Pins preregistration `25a0a921...`, canonical transcriber `961e18f6...`, independent QC `3b1018e7...`, inherited engine `3357582d...`, and exact audio SHA256.
- Static contract repair before sealing changed only compatibility with the determinism-amended preregistration status/hash.
- Boundary audit before seal: V156 `generated.json` absent; V156 `generation-receipt.json` absent; V156 generation workflow absent.
- **V156 candidate = NONE; professional-reference read = NO; reference-facing score calls = 0.**
- A failed checkpoint-only workflow `33142810650` had no jobs and changed no experiment state; helper was removed at commit `e07009242144413e8d5af00dfa9493b0d39023c3`.

## V156 trigger/freeze rules — MUST NOT VIOLATE
- `.github/workflows/v156-generate-reference-blind-once.yml` **creation itself is the single generation trigger**.
- Do not perform any later arm edit.
- Expected generation workflow run count = exactly 1. Duplicate run => abort V156 without scoring and move to a fresh version.
- During the generation run, make no unrelated branch writes until it freezes/self-seals.
- Workflow must verify exact audio/preregistration/transcriber/QC/engine identities before candidate creation.
- Workflow must install exact pinned CPU dependencies, enforce deterministic seed/thread policy, deterministically normalize audio, run one in-process seeded Demucs separation, record model checkpoint identity + stem hashes, run canonical transcriber, run independent QC, freeze candidate + receipt + QC, and delete itself.
- Reference-facing score calls remain 0 through candidate/QC freeze.
- Only after verifying exactly one generation run and independent QC PASS may a guarded one-use V156 score workflow be created.
- Score V156 exactly once; never retune or replace a consumed candidate.

## Exact next steps — RESUME HERE
1. Create `.github/workflows/v156-generate-reference-blind-once.yml` **exactly once**. Creation is the sole trigger; do not edit/arm it afterward.
2. Make no unrelated branch writes while that run is active.
3. Verify run number/count = 1 and all pre-candidate identity/isolation checks PASS.
4. Let the workflow perform deterministic CPU normalization + one seeded in-process `htdemucs_6s` separation + canonical transcription + independent structural QC.
5. If setup fails before candidate creation, repair only execution mechanics allowed by preregistration; do not change recognition/timebase quality parameters.
6. If a candidate is created and QC fails, freeze the failure and end V156; do not generate a replacement V156 candidate.
7. On success, verify candidate/receipt/QC hashes and checkpoint with V156 score calls still 0.
8. Only then construct one guarded one-use V156 scorer and score exactly once against the frozen professional reference/scorer.
9. Fresh explicit user authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
10. Do not resume Rhythm/Lead role separation, string/fret assignment, techniques, or PDF polishing until a future front-end candidate passes the acoustic gates.
