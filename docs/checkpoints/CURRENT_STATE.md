# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V160 generation is terminal/PASS and consumed forever. The sole reference-blind CPU candidate passed independent timebase QC and independent structural QC and is authoritative. A separate exactly-one-score professional-reference preregistration is now sealed BEFORE opening scorer/reference content: `debug/v160-cpu-autonomous/score-preregistration.json`, commit `2ee882897ebeeed6aca0a768eba36be78827b741`, blob `8cdc8f8d561124b7d417d5de7ea96fae5e0ec4ed`. V160 professional-reference score count remains 0. Next: scoring-only reviewer audit may now open the frozen scorer/reference, construct and audit `.github/workflows/v160-score.yml`, then arm it exactly once. CPU-only scoring is authorized; GPU/Modal/CUDA remain forbidden without fresh explicit user authorization. main/Production remains untouched.**

## Standing safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before Modal, NVIDIA L4, CUDA, or any GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; they must never influence generation/transcription/QC/candidate repair.
- V159 is closed forever: no re-arm/replay/regeneration/re-QC/score.
- V160 generation is closed forever: no re-arm/replay/regeneration/re-QC/candidate replacement/threshold sweep/variant selection/human correction.
- V160 may receive at most one professional-reference score. No rerun or rescore regardless of result.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Target remains automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Immutable shared scoring identities
Song: Lenny Kravitz — Are You Gonna Go My Way.
- Frozen scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855` — scoring only.
- Frozen professional reference: `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; Git blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7` — scoring only.
- Score gates: Guitar timing-aware pitch F1 >= `0.80`; Bass >= `0.80`; both required before role/string/fret/technique/PDF phase.

## Closed historical scores
- V154: one score forever; Guitar `0.04915390813859791`, Bass `0.1116751269035533`; failed.
- V155: invalid duplicate generation; score count 0 forever.
- V156: aborted before candidate; score count 0 forever.
- V157: one score forever; Guitar `0.07692307692307694`, Bass `0.05757575757575757`; failed.
- V158: one score forever; Guitar `0.007756948933419521`, Bass `0.001976284584980237`; failed/consumed.
- V159: terminal structural-QC runtime failure; score count 0 forever.

## V160 sealed generation identities
- Preregistration blob `cc238bcbf62c5defec410def962124d5012bd506`.
- Numeric contract blob `3d5ef47a998b638683c83ae08c92e45d5422f389`.
- Timebase builder blob `b5aa459381da6a5d5379ed8bdb1a07ba26467b63`.
- Timebase QC blob `a2dba655709572d5c50dd8d4ec8656fa96eb03a3`.
- Transcriber blob `864f0da266816e999cd6c2750dbceb27e870b67a`.
- Structural QC blob `679047e1e26b7ab4dff765dd05745317ce3f43e2`.
- JSON-native test blob `f2cc178c4b6a6a771a0c8f8b1527d9742f13126e`.
- Negative runtime guard blob `e6cd45c7d8bd23a92100847f3a219c84524cbbc2`.
- Static preflight workflow blob `1e2e16a68f72c2f7265a584256fc2402049cf940`; consumed PASS run `33197726025`, run #1 attempt #1, job `98939034732`, head `6e6cff4c73e1a951d4154f1ddbce8550576d8cbb`; never rerun.
- Immutable pre-run receipt blob `699dda80f25e0222dc7ef2f857fa65327f2d49db`.
- Runtime-compatible pre-run envelope blob `a1cd82c8c5b5dc150d051b3f013ff4eb208b36a8`.

## V160 sole generation — TERMINAL STRUCTURAL_QC_PASS
- Generation workflow audited blob `35c644cb4d29341d2f7d0404b896703c7fca2da4`.
- Sole arm commit `a66d4b23ba625ee1583aa9d6f11eb0115efb2de2`; parent `f439f8abf1b270ce4cb85393bde580386ed4be84`.
- Run ID `33205440520`; run #1; attempt #1; job `98965166224`; conclusion success.
- Bot terminal/self-seal commit `4e4b4c57dafeca61bc4a829929f8c4909133cbff`; message `research: freeze sole V160 reference-blind CPU candidate [skip ci]`.
- `.github/workflows/v160-generate.yml` self-deleted and is absent. Never re-arm it.
- CPU environment: Python 3.10.21; Torch 2.8.0+cpu; CUDA unavailable; deterministic CPU `htdemucs_6s`; no GPU/Modal; no professional reference/scorer reads during generation.

## V160 timebase / candidate / QC frozen evidence
- Timebase SHA256 `79e76bd0cea771cb92d163031f4c7645b8f0046ca651acc7e4b63a563bcb7ec8`.
- Timebase-QC artifact SHA256 `45cc89876921b99886cb126bd381e272968f8fc0c6affe672184f0ac81da8aa4`; Git blob `f122b624bb6bdfd629947ec3a5963c7b4373b3c2`; PASS; 448 detected beats.
- Candidate `debug/v160-cpu-autonomous/generated.json`; Git blob `892be048486c843ae5d3268e35f84cd95b4245af`; SHA256 `db6b8428fac758d5c0fd750b797152dbd9c3f7295c3b6c6872ee631ee8c8ff76`; combined Guitar 2276 events; Bass 460 events.
- Generation receipt Git blob `f88c8e9d6b1d84539e1837cd59da0c50262825ec`; SHA256 `3728aefc31d9987db2c1915792b3650094c46e60f1bcf446a3e4ce56de3a18ca`.
- Structural-QC receipt Git blob `5372885dfc9e07dfa8394294deafdf32c8f5a356`; SHA256 `2bb154499a849596f9e6e098df232d69a72379aa8508544dfa748797e23c3f34`; validation PASS; every check true; errors `[]`.
- Terminal freeze Git blob `9690c523290955dcf0ef15074bb6746105ec0810`; outcome `STRUCTURAL_QC_PASS`; candidateAuthoritative=true; eligibleForProfessionalReferenceScoring=true; neverRearmV160=true.
- Generation/QC safety: referenceRead=false; professional reference paths opened=0; reference-facing score calls=0; no prior candidate/score/V159 runtime reads; no GPU/Modal; main/Production=false.

## V160 one-score preregistration — SEALED BEFORE REFERENCE/SCORER OPEN
- File: `debug/v160-cpu-autonomous/score-preregistration.json`.
- Seal commit: `2ee882897ebeeed6aca0a768eba36be78827b741`.
- Git blob: `8cdc8f8d561124b7d417d5de7ea96fae5e0ec4ed`.
- Schema `dadrock.tabs.v160.professional-reference-score-preregistration.v1`; status `SEALED_BEFORE_REFERENCE_OR_SCORER_OPEN`; validation PASS.
- Created from checkpoint head `6457f002225a535e86b5155372bccd39b7d58120`.
- Pins frozen candidate blob/SHA, terminal commit/run/job/workflow identities, structural-QC PASS receipt, frozen scorer blob, frozen professional-reference blob/SHA, and 0.80/0.80 gates.
- Declares scoring CPU-only, workflow path `.github/workflows/v160-score.yml`, intended score receipt `debug/v160-cpu-autonomous/reference-score.json`, workflow creation as sole trigger, expected run #1 attempt #1, maximum score executions 1, no rerun/second arm/duplicate run, no candidate mutation/replacement/re-QC/threshold sweep/variant selection/human correction/post-score retune/rescore.
- Workflow must self-delete and self-seal after the single score. No assistant/manual branch writes while it is active.
- At score-preregistration seal: professionalReferenceRead=false; professionalReferencePathsOpened=0; frozenScorerContentRead=false; referenceFacingScoreCalls=0; candidateModifiedAfterStructuralPass=false; GPU/CUDA/Modal=0; main/Production=false.
- **Only now may scorer/reference content be opened, and only for scoring-workflow audit/execution.**

## Current hard boundary
- V160 professional-reference score count = 0.
- Candidate is irreversibly frozen before reference access.
- Scorer/reference content may now be opened for scoring-only audit and execution, but may not influence any generation artifact.
- Exactly one CPU scoring execution is allowed. Regardless of score, V160 candidate is consumed afterward.
- No GPU/Modal/CUDA without fresh explicit user authorization.
- Never touch `main`/Production without explicit user direction.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint before every write.
2. Scoring-only reviewer audit may now open the frozen scorer and professional reference. Verify their actual Git blobs/SHA still match the preregistration before using content.
3. Inspect frozen scorer CLI/output contract and reference schema only as needed to construct the one-shot CPU scoring workflow. Do not modify scorer/reference/candidate.
4. Reviewer-audit proposed `.github/workflows/v160-score.yml` without creating it. It must trigger only on its own creation, enforce run #1 attempt #1, pin candidate/terminal/structural/prereg/scorer/reference identities, prove score output absent, execute the frozen scorer exactly once, create one immutable score receipt, self-delete, and self-seal by one bot commit.
5. After audit PASS, re-fetch branch/checkpoint + absence proof, substitute exact expected parent SHA, and create `.github/workflows/v160-score.yml` exactly once. That creation commit is the sole score arm.
6. While score workflow is active, no assistant/manual branch writes. Read-only observation only. Never rerun.
7. After its terminal self-seal commit lands, verify score receipt and update this checkpoint. Consume V160 forever regardless of pass/fail.
8. If both Guitar and Bass F1 >=0.80, preregister next role/string/fret/technique/PDF phase. If either misses, design successor under a new preregistration without retuning V160.
9. Fresh explicit authorization remains required before any Modal/NVIDIA L4/CUDA/GPU execution.
