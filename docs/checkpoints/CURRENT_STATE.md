# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

## Active phase
**V160 generation is terminal/PASS and consumed forever. The authoritative candidate has a separately sealed exactly-one-score preregistration. After that seal, the frozen scorer/reference were opened only for scoring-workflow review; their identities matched exactly. The proposed `.github/workflows/v160-score.yml` has now passed reviewer audit WITHOUT being created, and `reference-score.json` / `score-terminal-freeze.json` remain absent. V160 professional-reference score count is still 0. Next: re-fetch branch/checkpoint + absence proof, substitute the exact checkpoint head as `EXPECTED_PARENT_HEAD`, re-audit that exact final workflow text, then create the score workflow exactly once. That creation commit is the sole score arm. While it runs: read-only observation only.**

## Standing safety — MUST PRESERVE
- CPU-only work and CPU scoring are authorized at assistant discretion.
- Fresh explicit user authorization is required immediately before Modal, NVIDIA L4, CUDA, or any GPU execution.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; they must never influence generation/transcription/QC/candidate repair.
- V159 is closed forever: no re-arm/replay/regeneration/re-QC/score.
- V160 generation is closed forever: no re-arm/replay/regeneration/re-QC/candidate replacement/threshold sweep/variant selection/human correction.
- V160 may receive at most one professional-reference scoring execution. No rerun/rescore regardless of result.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Target remains automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Frozen shared score identities
Song: Lenny Kravitz — Are You Gonna Go My Way.
- Frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen professional reference `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`; Git blob `2fbed60b543c0488934d8642c488aa06bf31bbf5`; SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Score gates: combined Guitar timing-aware pitch F1 >= `0.80`; Bass >= `0.80`; both required for role/string/fret/technique/PDF phase.
- Frozen scorer primary tolerance = `0.50` grid steps; gross diagnostic tolerance = `2.00` grid steps; maximum-cardinality then minimum-total-absolute-timing-error matching within measure/MIDI; scoring writes no corrections; post-score retuning forbidden.

## Historical closed score results
- V154: Guitar `0.04915390813859791`, Bass `0.1116751269035533`; one score forever; failed.
- V155: invalid duplicate generation; score count 0 forever.
- V156: aborted before candidate; score count 0 forever.
- V157: Guitar `0.07692307692307694`, Bass `0.05757575757575757`; one score forever; failed.
- V158: Guitar `0.007756948933419521`, Bass `0.001976284584980237`; one score forever; failed/consumed.
- V159: terminal structural-QC runtime failure; score count 0 forever.

## V160 terminal generation evidence
- Generation workflow blob `35c644cb4d29341d2f7d0404b896703c7fca2da4`.
- Sole arm commit `a66d4b23ba625ee1583aa9d6f11eb0115efb2de2`; run `33205440520`, run #1 attempt #1, job `98965166224`; success.
- Terminal bot commit `4e4b4c57dafeca61bc4a829929f8c4909133cbff`; generation workflow self-deleted; never re-arm.
- Candidate `debug/v160-cpu-autonomous/generated.json`; Git blob `892be048486c843ae5d3268e35f84cd95b4245af`; SHA256 `db6b8428fac758d5c0fd750b797152dbd9c3f7295c3b6c6872ee631ee8c8ff76`; combined Guitar 2276 events; Bass 460 events.
- Timebase-QC SHA256 `45cc89876921b99886cb126bd381e272968f8fc0c6affe672184f0ac81da8aa4`; PASS; 448 beats.
- Structural-QC receipt blob `5372885dfc9e07dfa8394294deafdf32c8f5a356`; SHA256 `2bb154499a849596f9e6e098df232d69a72379aa8508544dfa748797e23c3f34`; PASS; every check true; errors `[]`.
- Terminal freeze blob `9690c523290955dcf0ef15074bb6746105ec0810`; outcome `STRUCTURAL_QC_PASS`; candidateAuthoritative=true; eligibleForProfessionalReferenceScoring=true; neverRearmV160=true.
- Generation/QC reference reads=0; score calls=0; CUDA/GPU/Modal=0; main/Production untouched.

## V160 exactly-one-score preregistration — SEALED BEFORE ANY SCORE-AUDIT READ
- `debug/v160-cpu-autonomous/score-preregistration.json`.
- Seal commit `2ee882897ebeeed6aca0a768eba36be78827b741`; Git blob `8cdc8f8d561124b7d417d5de7ea96fae5e0ec4ed`.
- Schema `dadrock.tabs.v160.professional-reference-score-preregistration.v1`; status `SEALED_BEFORE_REFERENCE_OR_SCORER_OPEN`; validation PASS.
- Pins candidate blob/SHA, generation terminal commit/run/job/workflow, structural-QC PASS identity, frozen scorer blob, professional-reference blob/SHA, and 0.80/0.80 gates.
- CPU score workflow path frozen as `.github/workflows/v160-score.yml`; score report path frozen as `debug/v160-cpu-autonomous/reference-score.json`.
- Workflow creation is sole trigger; expected run #1 attempt #1; maximum score executions=1; rerun/second arm/duplicate run forbidden.
- Candidate mutation/replacement/re-QC, threshold sweep, variant selection, human correction, post-score retune and post-score rescore all forbidden.
- Score workflow must self-delete/self-seal. No assistant/manual branch writes while active.
- At preregistration seal: scorer/reference content had not been opened and score calls=0.

## Scoring-only reviewer access — ALLOWED AFTER SEAL / COMPLETE
- Frozen scorer content was opened after the one-score preregistration seal solely to audit the scoring workflow; actual Git blob matched `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Frozen reference was opened after the seal solely to verify scoring input/schema; actual Git blob matched `2fbed60b543c0488934d8642c488aa06bf31bbf5`. No score was executed during review.
- Reference payload advertises combined Guitar 1393, rhythm 946, lead 447, Bass 547 before scorer exclusions; scorer itself validates private-scoring authorization and normalizes exclusions.
- Candidate remained unchanged throughout reviewer access.

## Proposed V160 one-shot score workflow reviewer audit — PASS / NOT ARMED
- Proposed path `.github/workflows/v160-score.yml`; currently absent (404).
- Proposed score report `debug/v160-cpu-autonomous/reference-score.json`; absent (404).
- Proposed terminal score freeze `debug/v160-cpu-autonomous/score-terminal-freeze.json`; absent (404).
- Proposed YAML parses successfully; 367 lines / 17,972 bytes before final parent-SHA substitution; reviewer-source SHA256 `44c3690aca3c0ed970b4f2a7b8b8a8a2727eb65d027302cdc2f11833affb1160` with placeholder parent.
- Trigger: single push path on its own workflow file only; no manual dispatch or PR trigger.
- Guard: run #1 attempt #1 only; exact parent + one changed path; branch head lock; exact candidate Git blob/SHA; structural-QC blob/SHA; terminal-freeze blob; score-prereg blob; frozen scorer blob; professional-reference blob/SHA; score/score-terminal absent; generation workflow absent.
- Guard verifies score preregistration status/contract/gates/safety and generation terminal/structural PASS before score.
- Static self-check proves the frozen scorer command occurs exactly once in the workflow.
- Execution: CPU-only Python; no dependency install required; frozen scorer invoked exactly once as `generated reference --output reference-score.json`.
- No generated candidate/transcriber/timebase/QC path is writable by the score workflow. Candidate/scorer/reference identities are rechecked after scorer execution.
- Score report validation checks frozen schema, song identity, exact 0.80 gates, 0.50/2.00 tolerances, write-no-corrections policy, and F1 bounds. Gate PASS/FAIL is evaluated only after the single score exists.
- Terminal receipt `score-terminal-freeze.json` records run/head, one-score execution count, all frozen identities, score report blob/SHA, Guitar/Bass F1, gate outcome, candidateConsumed=true, scoreOpportunityConsumed=true, neverRerunOrRescoreV160=true, and safety flags.
- Terminal step requires branch still at score arm head, deletes the score workflow, stages only score report + score terminal freeze + workflow deletion, makes one `[skip ci]` bot commit, and never permits a second score.
- Valid score execution may end in quality `SCORE_GATE_PASS` or `SCORE_GATE_FAIL`; both are terminal valid score outcomes. Runtime/guard failure is also terminal/no-rerun.

## Current hard boundary
- V160 score count = 0.
- Candidate is frozen before all reference-facing work and cannot change.
- Scorer/reference audit reads have occurred only after score preregistration; no scoring call has yet occurred.
- Exactly one CPU scorer invocation remains allowed.
- After score workflow arm, no assistant/manual branch writes until its own terminal self-seal commit lands.
- No GPU/Modal/CUDA without fresh explicit user authorization.
- Never touch `main`/Production without explicit user direction.

## Exact next steps — RESUME HERE
1. Re-fetch branch head/checkpoint before arm write.
2. Re-prove `.github/workflows/v160-score.yml`, `reference-score.json`, and `score-terminal-freeze.json` are absent and candidate/structural/terminal/prereg/scorer/reference identities still match.
3. Substitute that exact checkpoint head as `EXPECTED_PARENT_HEAD` in the already-audited score workflow; re-run the reviewer/static checks on the exact final text. No other semantic change is permitted.
4. Create `.github/workflows/v160-score.yml` exactly once. That creation commit is the sole V160 score arm.
5. While score workflow is active: read-only observation only; no checkpoint/manual branch writes; never rerun.
6. Observe sole run to terminal completion; preserve run/job/head identities.
7. After workflow self-seal commit lands and workflow is absent, verify `reference-score.json` + `score-terminal-freeze.json`, then checkpoint exact F1/gate result. V160 is consumed forever regardless of result.
8. If both Guitar and Bass >=0.80, preregister next role/string/fret/technique/PDF phase. If either misses, successor design may use frozen score evidence under a new preregistration; never retune V160.
9. Fresh explicit authorization remains required before any Modal/NVIDIA L4/CUDA/GPU execution.
