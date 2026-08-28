# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V158 is permanently CONSUMED after its sole official professional-reference score. The one-shot CPU score run completed successfully as protocol, but the candidate failed both 0.80 gates: combined Guitar F1 `0.007756948933419521`, Bass F1 `0.001976284584980237`. The frozen scorer ran exactly once; the guard itself performed 0 professional-reference content reads; the candidate SHA/blob were unchanged before/after; retry is forbidden; the score workflow self-removed. Never retune, modify, regenerate, replace, or rescore V158. No GPU/Modal/CUDA was used and main/Production remains untouched. Safe next work is reference-blind post-score architecture diagnosis using only already-frozen V158 candidate/generation/QC/score artifacts (no professional-reference reopen), then freeze that diagnosis before any future-version preregistration.**

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
- Audio SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; bytes `3478611`.
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
- Independent structural QC: blob `4cb52d4f17359fa4386945800b09fcf0171a8e30`; PASS; referenceRead false; reference-facing score calls 0 at QC; human correction false; threshold sweep false; variant selection false; GPU false.

## V158 one-shot score protocol — COMPLETE / SELF-SEALED
- Guard `validation/v158_cpu_multitrack/run_frontend_reference_score_once.py`: commit `1800557523ad7fe643be54cc5094537538505007`; blob `00b4a5f90f12c5812f48d5581b0b3698de8c46ba`.
- Pre-score receipt `debug/v158-cpu-autonomous/frontend-reference-score/pre-score-receipt.json`: commit `24ae8345665db7d34668d2deb2392f42849b6905`; blob `f3475d85070fe786d465a06a737d52daf858d2b4`; status `SEALED_BEFORE_REFERENCE_SCORE`.
- Pre-score boundary was reference-content reads 0; reference-facing score calls 0.
- V158 guard strengthened V157 mechanics: it verified reference integrity via Git blob metadata only and never opened/hashed professional-reference contents itself.
- Score workflow `.github/workflows/v158-score-reference-once.yml` was created exactly once at commit `3973d14323df7782edaac5336aaa83b411c8f4a2`; creation was the sole trigger.
- Sole score workflow run `33147577735`; run number 1; attempt 1; conclusion SUCCESS.
- All preflight identity checks and immediate pre-call branch-stability checks passed.
- Frozen scorer invocation count = exactly 1. Guard reference-content reads = 0. Retry allowed = false.
- Score/consumption freeze commit `8681e0d80b3f5c9f0e7a3dd0c0b71dbfc0d77b19` (`v158: freeze sole reference score consumption [skip ci]`).
- Score workflow self-removed and is absent from current branch.

## V158 sole official score — FAILED GATE / FROZEN
- Score file `debug/v158-cpu-autonomous/frontend-reference-score/score.json`; Git blob `1a4d113d7d3c3f1fdf4106bc0cada9b2914ce2cd`; SHA256 from receipt `e0043db204849842c1425adeac89696c250cf8e6daf748b39473c77220c9bdf4`.
- Consumption receipt `debug/v158-cpu-autonomous/frontend-reference-score/score-receipt.json`; Git blob `a311305775bc9b26d2ff82f5a55c4cc0e5e8b378`; status `COMPLETE_CONSUMED`; scorer return code 0.
- Candidate SHA256 before/after identical `2a9e8bdfbe48f03dc5d3734780aeb937ef0c5654d55a40536069ed30ee46bcc9`; candidate Git blob before/after identical `1ddb1849b3cfefc14b60f6b5ac72af9ffcdc7fa6`.
- Combined Guitar primary timing-aware pitch: matched 12 / generated 1701 / reference 1393; precision `0.007054673721340388`; recall `0.008614501076812634`; F1 `0.007756948933419521`.
- Combined Guitar gross timing-aware pitch: matched 52; F1 `0.03361344537815126`; diagnostic pitch-content-by-measure matched 121; F1 `0.07821590174531351`.
- Bass primary timing-aware pitch: matched 1 / generated 465 / reference 547; precision `0.002150537634408602`; recall `0.0018281535648994515`; F1 `0.001976284584980237`.
- Bass gross timing-aware pitch: matched 7; F1 `0.01383399209486166`; diagnostic pitch-content-by-measure matched 13; F1 `0.02569169960474308`.
- Both required 0.80 gates failed by a very large margin. Do not proceed to Rhythm/Lead role split, string/fret assignment, techniques, or professional PDF for V158.

## Current hard boundary
- **V158 is consumed forever; official score count = 1 forever.**
- **Do not rerun the score workflow or scorer.**
- **Do not reopen the professional reference for V158 diagnosis.**
- **Do not modify/retune/regenerate/replace/select a variant of the V158 candidate.**
- **Use only frozen candidate/generation/QC/score artifacts for any post-score diagnosis.**
- **No GPU execution has occurred. main/Production untouched.**

## Exact next steps — RESUME HERE
1. Re-fetch latest branch head/checkpoint before every write because concurrent continuations may exist.
2. Perform a **reference-blind V158 post-score architecture diagnosis** using only the frozen V158 candidate, generation/environment/QC receipts, implementation code/contracts, and the already-frozen aggregate `score.json`; do not read the professional reference again and do not call the scorer.
3. Diagnose architecture-level failure modes only. Do not derive or reuse exact professional-reference note alignments/timings/pitches as tuning constants.
4. Freeze the diagnosis as a new V158 diagnostic artifact/receipt and update this checkpoint. V158 remains immutable/consumed.
5. Only after diagnosis is frozen may a future version be preregistered. Any future candidate must be generated independently/reference-blind and scored at most once under its own sealed one-shot protocol.
6. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
