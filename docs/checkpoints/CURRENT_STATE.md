# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V158 is permanently CONSUMED and its reference-blind post-score architecture diagnosis is now FROZEN. The sole official score failed badly (combined Guitar F1 `0.007756948933419521`, Bass F1 `0.001976284584980237`). The dominant proven structural failure is a catastrophic V158 timebase: structural QC recorded `2986` tracked beats across approximately `216.45 s`, implying about `827.72 BPM` and a mean tracked-beat interval of about `72.49 ms`. The strongest reference-blind root-cause hypothesis is V158 feeding a signed robust-z fused onset envelope directly into `librosa.beat.beat_track`; the sole generation run emitted `RuntimeWarning: invalid value encountered in log1p` from librosa rhythm processing. A second architecture problem is coupling Viterbi bar-phase state transitions to absolute beat ordinal, allowing the phase model to stretch/compress the time coordinate. V158 must never be retuned, regenerated, replaced, or rescored. Next safe work is to preregister V159 as a fresh timebase-first CPU architecture satisfying the frozen diagnosis requirements before writing V159 implementation code. No GPU/Modal/CUDA was used and main/Production remains untouched.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; generation/transcription must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Never retune/correct/select a replacement for a consumed scored candidate.
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Immutable shared song / scoring identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Historical audio commit `74b0f815ff3f66f325220975c410621503de440f`.
- Audio SHA256 `215bd5a657c5326f08f132e358595a95c30b39bb7493a52c2f910d5a608149f` is INVALID TYPO — do not use. The authoritative audio SHA256 remains `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; bytes `3478611`.
- Normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Source m104 = 2/4 (8 sixteenth steps), others 4/4; meter map SHA256 `1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648`.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; Git blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`; Guitar 1393 / Bass 547.
- Front-end gate remains combined Guitar primary timing-aware pitch F1 >= `0.80` AND Bass primary timing-aware pitch F1 >= `0.80` before role split/string/fret/technique/PDF work.

## Closed historical versions
- **V154:** score count 1 forever; Guitar F1 `0.04915390813859791`, Bass F1 `0.1116751269035533`; failed.
- **V155:** protocol-invalid duplicate generation; score count 0 forever.
- **V156:** aborted before candidate; score count 0 forever.
- **V157:** score count 1 forever; Guitar F1 `0.07692307692307694`, Bass F1 `0.05757575757575757`; failed. Frozen post-score diagnosis commit `51fcd9b93a495f939ce85a7ec578f7ea3d70c5de`; exact diagnostic alignment constants remain forbidden future-generation inputs.
- **V158:** score count 1 forever; Guitar F1 `0.007756948933419521`, Bass F1 `0.001976284584980237`; failed and consumed.

## V158 frozen generation identity
- Sole generation workflow run `33145878069`; run number 1; attempt 1; SUCCESS; workflow self-removed.
- Candidate freeze commit `1164742a49f6b760dbf3f995e91c520493f425d8`.
- Candidate `debug/v158-cpu-autonomous/generated.json`: blob `1ddb1849b3cfefc14b60f6b5ac72af9ffcdc7fa6`; SHA256 `2a9e8bdfbe48f03dc5d3734780aeb937ef0c5654d55a40536069ed30ee46bcc9`; combined Guitar 1701; Bass 465.
- Environment receipt: blob `9749b5c58952ca56a80df4834ea2ae116471f532`; SHA256 `1bb07ed96cdbcf1dfe5a29aea85da68e43aa63bf2835008ca98a4bae46557d9a`; CPU-only; CUDA unavailable.
- Generation receipt: blob `3afb6c011065568890e1e48e437882e7848f1aaa`; SHA256 `e05716636d4bf63fd86ab0f3bc97cb2e274fcd600d47a839d32dfff5543ef12f`.
- Independent structural QC: blob `4cb52d4f17359fa4386945800b09fcf0171a8e30`; PASS under the V158 contract, but its contract lacked a beat-density/tempo-consistency sanity gate. It recorded beatCount `2986`, state counts `0:924`, `1:821`, `2:828`, `3:413`.

## V158 one-shot score protocol — COMPLETE / SELF-SEALED
- Guard `validation/v158_cpu_multitrack/run_frontend_reference_score_once.py`: commit `1800557523ad7fe643be54cc5094537538505007`; blob `00b4a5f90f12c5812f48d5581b0b3698de8c46ba`.
- Pre-score receipt `debug/v158-cpu-autonomous/frontend-reference-score/pre-score-receipt.json`: commit `24ae8345665db7d34668d2deb2392f42849b6905`; blob `f3475d85070fe786d465a06a737d52daf858d2b4`; status `SEALED_BEFORE_REFERENCE_SCORE`.
- Pre-score boundary: reference-content reads 0; reference-facing score calls 0.
- Score workflow `.github/workflows/v158-score-reference-once.yml` created exactly once at commit `3973d14323df7782edaac5336aaa83b411c8f4a2`; sole run `33147577735`; run number 1; attempt 1; SUCCESS.
- Frozen scorer invocation count exactly 1; guard professional-reference content reads 0; retry false.
- Score/consumption freeze commit `8681e0d80b3f5c9f0e7a3dd0c0b71dbfc0d77b19`; workflow self-removed.

## V158 sole official score — FAILED GATE / FROZEN
- Score `debug/v158-cpu-autonomous/frontend-reference-score/score.json`; blob `1a4d113d7d3c3f1fdf4106bc0cada9b2914ce2cd`; SHA256 `e0043db204849842c1425adeac89696c250cf8e6daf748b39473c77220c9bdf4`.
- Consumption receipt `debug/v158-cpu-autonomous/frontend-reference-score/score-receipt.json`; blob `a311305775bc9b26d2ff82f5a55c4cc0e5e8b378`; status `COMPLETE_CONSUMED`; scorer return code 0; retry false.
- Candidate SHA/blob before and after score identical.
- Combined Guitar primary: matched 12 / generated 1701 / reference 1393; F1 `0.007756948933419521`. Gross F1 `0.03361344537815126`; measure/pitch diagnostic F1 `0.07821590174531351`.
- Bass primary: matched 1 / generated 465 / reference 547; F1 `0.001976284584980237`. Gross F1 `0.01383399209486166`; measure/pitch diagnostic F1 `0.02569169960474308`.
- Both 0.80 gates failed. Never proceed with V158 to Rhythm/Lead role split, string/fret assignment, techniques, or PDF.

## V158 post-score architecture diagnosis — FROZEN
- Artifact `debug/v158-cpu-autonomous/post-score-architecture-diagnosis.json`.
- Freeze commit `8f2e03032cc5b323afd0b4668660199425bc585f`; Git blob `d7c5720b27f74f1f710b96a6b0da70569ae48bbc`.
- Schema `dadrock.tabs.v158.reference-blind-post-score-architecture-diagnosis.v1`; status `FROZEN_POST_SCORE_DIAGNOSIS`.
- Diagnosis professional-reference payload reads = 0; additional score calls = 0; candidate modification/regeneration = false; threshold sweep = false; GPU = false; main/Production = false.
- **PROVEN critical failure:** 2,986 tracked beats across ~216.45s = `827.7200277200278 BPM` implied beat density; mean tracked beat interval `0.07248827863362357 s`; about `746.5` nominal four-beat bars. This makes the musical coordinate system unusable.
- **Strongest root-cause hypothesis:** sealed V158 code directly passes `0.5 * (robust_z(mix onset) + robust_z(drums onset))` to `librosa.beat.beat_track`, while the sealed contract explicitly permits negative values (`no positive clipping`). Sole generation emitted `RuntimeWarning: invalid value encountered in log1p` from `librosa/feature/rhythm.py:450` during timebase construction.
- **Second architecture defect:** V158 converts Viterbi phase-state deltas into absolute beat ordinal. Same-state transitions add zero and skip-one transitions add two, so a downbeat/bar-phase model can alter time scale. Absolute beat ordinal and bar-phase inference must be decoupled.
- Guitar overgeneration (1701 vs 1393, +22.1%; 370 harmonic-track additions) and Bass undercount (465 vs 547, -15.0%) are secondary unresolved recognition risks. Do not tune either from V158 aggregate score because the broken timebase dominates and aggregate score is not source-conditional.

## Frozen requirements carried into V159
1. Beat-tracker input must be finite and nonnegative by construction. Signed robust-z features may be used for bar/downbeat evidence, not as direct beat-strength input.
2. Absolute beat ordinal must advance exactly once per accepted beat. Bar/downbeat-state inference may label phase/boundaries only; it may not add/delete/duplicate/stretch/compress beat ordinal.
3. Reference-blind structural QC must reject pathological beat density before candidate freeze using audio duration, detected beat times, and tracker-internal tempo evidence only.
4. QC must record duration, beat count, mean/median IBI, implied BPM, tracker tempo, tempo-consistency diagnostics, state transition counts, and grid extent.
5. NaN/Inf or runtime warnings attributable to rhythm/timebase construction must fail timebase QC before candidate authority.
6. Do not sweep/tune Guitar or Bass thresholds from V158 score. V159 must have one preregistered configuration and one independently generated candidate.

## Current hard boundary
- **V158 is consumed forever; official score count = 1 forever.**
- **V158 diagnosis is frozen; do not amend it to fit future outcomes.**
- **Do not rerun V158 scorer, reopen its professional reference for diagnosis, modify its candidate, or derive exact reference alignments/constants.**
- **No GPU execution has occurred. main/Production untouched.**
- V159 may use architecture-level lessons in the frozen diagnosis, but not professional-reference note/timing/pitch corrections.

## Exact next steps — RESUME HERE
1. Re-fetch latest branch head/checkpoint before every write because concurrent continuations may exist.
2. Create and freeze a **V159 reference-blind CPU preregistration** before writing V159 implementation code. It must explicitly inherit all six frozen requirements above.
3. V159 timebase architecture should use a finite nonnegative beat envelope, keep absolute beat index independent of bar-phase state, and define reference-blind pre-candidate timebase QC that can abort before any authoritative candidate is emitted.
4. Seal V159 numeric implementation contract before canonical transcriber code. Do not choose constants from V158 professional score details; use generic audio/music reasoning only.
5. Only after V159 preregistration + numeric contract + code + pre-run identity receipt are all sealed may a single CPU generation workflow be armed. Exactly one fresh V159 candidate, reference-blind.
6. After independent structural/timebase QC passes and candidate freezes, professional reference may be accessed exactly once by a V159 one-shot scorer. Never retry/retune that candidate after scoring.
7. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
