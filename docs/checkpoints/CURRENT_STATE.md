# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V158 has exactly ONE frozen CPU candidate, independent reference-blind structural QC PASS, and a newly sealed one-shot professional-reference score guard + pre-score identity receipt. The professional reference content has still not been opened for V158: reference-content reads = 0 and reference-facing official score calls = 0. Next allowed action is to create the V158 score workflow exactly once; workflow creation is the sole trigger for the sole official CPU score. The workflow must call the frozen scorer exactly once, freeze the result/consumption receipt, self-remove, and never retry after any reference-facing call. No candidate retuning/replacement/regeneration is allowed. No GPU/Modal/CUDA was used and main/Production remains untouched.**

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
- Frozen professional reference path `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`.
- Reference SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; Git blob metadata `2fbed60b543c0488934d8642c488aa06bf31bbf5`; Guitar 1393 / Bass 547.
- V158 gate: both combined Guitar primary timing-aware pitch F1 >= `0.80` and Bass primary timing-aware pitch F1 >= `0.80`.

## Closed historical versions
- **V154:** score count 1 forever; Guitar F1 `0.04915390813859791`, Bass F1 `0.1116751269035533`; failed.
- **V155:** protocol-invalid duplicate generation; score count 0 forever.
- **V156:** aborted before candidate; score count 0 forever.
- **V157:** sole generation run `33143471258`; candidate SHA256 `f5dc7094b72f8e3a988b1fdd59808cb056461d7e12a6d41508942cf499de3e71`; sole score run `33143986627`; Guitar F1 `0.07692307692307694`, Bass F1 `0.05757575757575757`; score count 1 forever.
- V157 post-score diagnosis frozen at commit `51fcd9b93a495f939ce85a7ec578f7ea3d70c5de`; use only architecture evidence, never exact diagnostic alignment constants.

## V158 sealed generation contracts
- Architecture preregistration: `debug/v158-cpu-autonomous/preregistration.json`; commit `cdb2eca7ec16479a5868f9a3ca18624fc0892c44`; blob `728cf28646db225f3c266a4bb73a6112b1f60330`.
- Numeric implementation contract: `debug/v158-cpu-autonomous/implementation-contract.json`; commit `90c878c50afcd70a6a2f7e58f2605ed2a7b2ba27`; blob `68f01df155cd27077cea3de5a0cd048ddcb7bd76`.
- Sparse-pursuit resolution: `debug/v158-cpu-autonomous/sparse-pursuit-contract-resolution.json`; commit `d07c56e51168d7f07784ad3ed67b4902245a0c4e`; blob `b4b6a5c1f8a88d359a981eb1238907805f2fc2a9`.
- Base helper `validation/v158_cpu_multitrack/transcribe_v158_base.py`; blob `5617ff1a6ea301ecaeb898b123b05d2a8c915388`.
- Canonical transcriber `validation/v158_cpu_multitrack/transcribe_v158.py`; blob `91d65049031506fe44b44e034b1ab04022ba0b91`.
- Independent QC implementation `validation/v158_cpu_multitrack/structural_qc.py`; blob `0bbb08225f0a21bc5bf4889189f22d89953371df`.
- Pre-run identity receipt `debug/v158-cpu-autonomous/pre-run-receipt.json`; blob `e7300529fee191335a6709127e07069210704162`; SHA256 `daec7937b406c3bdf8bd8862b32b78f979f3b17ba2a9a829b09d06348034cff5`.

## V158 sole CPU generation — COMPLETE / FROZEN
- Generation workflow `.github/workflows/v158-generate.yml` was created once at commit `eb4c41d83d0fa77402b18da5eb6655014593c186` and self-removed after success.
- Sole run ID `33145878069`; run number 1; attempt 1; SUCCESS.
- Freeze commit `1164742a49f6b760dbf3f995e91c520493f425d8`.
- Candidate `debug/v158-cpu-autonomous/generated.json`: blob `1ddb1849b3cfefc14b60f6b5ac72af9ffcdc7fa6`; SHA256 `2a9e8bdfbe48f03dc5d3734780aeb937ef0c5654d55a40536069ed30ee46bcc9`; combined Guitar 1701; Bass 465.
- Environment receipt `debug/v158-cpu-autonomous/environment-receipt.json`: blob `9749b5c58952ca56a80df4834ea2ae116471f532`; SHA256 `1bb07ed96cdbcf1dfe5a29aea85da68e43aa63bf2835008ca98a4bae46557d9a`; CPU-only; CUDA unavailable.
- Generation receipt `debug/v158-cpu-autonomous/generation-receipt.json`: blob `3afb6c011065568890e1e48e437882e7848f1aaa`; SHA256 `e05716636d4bf63fd86ab0f3bc97cb2e274fcd600d47a839d32dfff5543ef12f`.
- Structural QC `debug/v158-cpu-autonomous/structural-qc.json`: blob `4cb52d4f17359fa4386945800b09fcf0171a8e30`; PASS; candidate SHA/pins verified; referenceRead false; professional reference paths opened 0; reference-facing score calls 0; human correction false; threshold sweep false; variant selection false; GPU false.

## V158 one-shot score guard — SEALED BEFORE REFERENCE READ
- Guard `validation/v158_cpu_multitrack/run_frontend_reference_score_once.py` added at commit `1800557523ad7fe643be54cc5094537538505007`; Git blob `00b4a5f90f12c5812f48d5581b0b3698de8c46ba`.
- Guard pins candidate SHA/blob, generation receipt SHA/blob, environment receipt SHA/blob, structural-QC blob, scorer blob, freeze commit, and reference Git blob.
- **Important V158 strengthening vs V157:** guard does not open/hash professional reference contents. Reference integrity is verified by frozen Git blob metadata only, so the frozen scorer performs the single permitted professional-reference content read.
- Guard writes `score-receipt.json` with `REFERENCE_CALL_STARTED` and `retry_allowed=false` before invoking the frozen scorer; scorer invocation count is set to 1 before subprocess launch. A scorer failure therefore consumes V158 and forbids retry.
- Guard calls scorer only as `python <frozen scorer> <candidate> <reference> --output <score>` exactly once.
- Guard re-verifies candidate SHA/blob after scoring and records final score SHA/status.

## V158 pre-score identity receipt — SEALED
- `debug/v158-cpu-autonomous/frontend-reference-score/pre-score-receipt.json`.
- Commit `24ae8345665db7d34668d2deb2392f42849b6905`; Git blob `f3475d85070fe786d465a06a737d52daf858d2b4`.
- Schema `dadrock.tabs.v158.pre-score-reference-identity-receipt.v1`; status `SEALED_BEFORE_REFERENCE_SCORE`.
- Pins exact candidate/generation/environment/QC/scorer/guard/freeze/reference identities listed above.
- Records V158 reference-content reads before score = 0; reference-facing score calls before score = 0; GPU false; main/Production untouched.
- Score output directory currently contains only this pre-score receipt; `score.json` and `score-receipt.json` do not exist.

## Current hard boundary
- **Exactly one V158 candidate exists and is frozen forever. Do not modify or replace it.**
- **Independent reference-blind structural QC = PASS.**
- **V158 professional-reference content reads = 0.**
- **V158 reference-facing official score calls = 0.**
- **No GPU execution has occurred.**
- **Do not preview/preflight/open/hash the professional reference before the official scorer.**
- **Do not retry after any reference-facing scorer invocation, regardless of success/failure.**

## Exact next steps — RESUME HERE
1. Re-fetch latest branch head/checkpoint before every write because concurrent continuations may exist.
2. Create `.github/workflows/v158-score-reference-once.yml` exactly once. Workflow creation is the sole score trigger.
3. Workflow must pin branch/candidate/generation/environment/QC/scorer/guard/reference-blob identities, require run number 1 and attempt 1, require no pre-existing `score.json`/`score-receipt.json`, and invoke the V158 guard exactly once.
4. Workflow must preserve the professional reference unopened until the guard launches the frozen scorer; use only `git ls-files -s` for reference preflight.
5. Whether scorer succeeds or fails, freeze/commit the consumption receipt and any score output, then self-remove the workflow. No rerun is permitted.
6. After the sole score, V158 is permanently consumed. If both F1 gates >=0.80, continue to Rhythm/Lead role separation, string/fret assignment, techniques, and professional PDF work. Otherwise stop V158; never retune/regenerate/score a replacement under V158.
7. Fresh explicit authorization remains required immediately before any Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
