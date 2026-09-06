# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-06 — **AUTHORIZED V143 RUN RECOVERED + FROZEN; PDF E2E PASSED; PROFESSIONAL SCORE 1/1 CONSUMED; MODEL-FREE TIMING REPAIR COMMITTED; NO RETRIES AUTHORIZED.**
Branch: `v143-contextual-prune-lobo`

This file is the authoritative fresh-chat handoff. It supersedes older stale instructions that said the professional score was still available.

## HARD AUTHORIZATION / BUDGET BOUNDARY

User authorized exactly:
- **1** replacement current-V143 `gomyway` Rhythm model-bearing start;
- **1** professional full-1–113 score against the completed frozen result from that exact start;
- deterministic preview/full PDF validation from that same completed result.

Current counters:
- replacement live: **0 available / 1 consumed**
- professional full-1–113 score: **0 available / 1 consumed**
- replacement PDF E2E: **1 performed / passed**

**DO NOT** issue another model start or another professional score without new explicit user authorization.

Also do not:
- run Lead/Bass model-bearing analysis;
- deploy/promote the Vercel app to production;
- weaken Deployment Protection;
- run optimizer/training/threshold sweeps;
- mutate scheduler/model/parameters as part of evaluation;
- rerun any failed model or scoring workflow merely to get a green CI result.

## REPAIRED PREVIEW / SOURCE BOUNDARY

Pinned repaired Preview:
- deployment `dpl_5j26ZS2xq3utrHxW7waCd5NEPaQk`
- Preview source `631544a8668033392300f2739c87232553dbadc0`
- analyze route blob `a3d02876d2c4efeb6f5258586046bc95cfc132b6`
- repaired async bridge blob `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- async protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`
- live worker blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- separator/scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`
- audio blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`

Repair validation:
- bridge deploy run `34041343616`, job `101508549305`, success
- bridge artifact `9991761743`, SHA-256 `02dff61207bac1b42331cd0359e92ab3bcecd252e00c15cbb0011d714f6aa49e`
- green model-free Preview preflight run `34042266658`, job `101511044644`, success
- preflight artifact `9992037110`, SHA-256 `bf83017022ca3cc15ff7e13841615b3223ac64da05b9e8aed1c62ef7e40e186d`

## EXACT AUTHORIZED MODEL RUN — 1/1 CONSUMED

Runner:
- `.github/workflows/v143-one-shot-final-rhythm-e2e.yml`
- helper `.github/scripts/v143-one-shot-final-rhythm-existing-preview.sh`
- helper blob `e2847e4d05ae1fea781ef07e891fece1bfbecbf0`
- retarget commit `9f4d8b59a15288cab02c7930093f80db57e52df0`
- arm commit `acdf236e5e2649d3beb515fb2fc8a0abf345cc51`
- workflow run `34046854397`
- job `101523324268`

Observed path:
- exactly one Rhythm `operation:"start"` accepted HTTP 202 around `2026-09-06T16:54:33Z`;
- same-token polls 1–130 returned 202;
- poll 131 returned 502 at ~908 s;
- same-job ACK HTTP 200, `acknowledged=true`, `transientResultCleared=true`;
- bounded artifact `9993601754`, SHA-256 `9c5661024e59ee70068e87eb286aa8e1095f85455c2203ed64870d7dded7f50e`.

### Confirmed async tracking defect

`ASYNC_RESULT_TTL_SECONDS = 900` and the control state holding the parent orchestrator FunctionCall ID used that same 900-second lifetime while the worker/orchestrator runtime budget is 1200 seconds.

Timing matched the failure:
- start ~16:54:33Z
- 900-second tracking boundary ~17:09:33Z
- client 502 ~17:09:35Z

This is separate from the earlier pending-poll bridge bug, which was already repaired.

## EXACT MODAL WORKER — COMPLETED SUCCESSFULLY

Read-only exact FunctionCall evidence:
- worker Function ID `fu-cXv3G2TXumycjiCTABviS7`
- worker FunctionCall `fc-01M1VT9BDS5TYWE52GPYQQ8W9E`
- container `ta-01M1VT9BRA8YRBNK1DKSC329BR`
- exact worker logs prove `worker.done elapsed=936.836` at about `17:10:18Z`
- separator completed at ~785.929 s
- Basic Pitch and technique enrichment completed
- worker completed ~29 seconds after the client-side 900-second tracking record expired

Diagnostic workflow/artifact:
- run `34047990402`
- artifact `9993685857`
- SHA-256 `e87bf1f0039ff7d0aa871e32009bf899f187f0c6bc04f3880c77a2bb29b59387`

### User-observed Modal symptom

User reported that Modal was showing a **“reporting function crash-looping”** condition.

Treat that as a diagnostic clue only. Do **not** reinterpret it as proof that the exact Rhythm worker failed, because the exact worker FunctionCall above completed successfully and the completed result was recovered.

Fresh-chat diagnosis should determine read-only which Modal function/UI entry was crash-looping (reporter/diagnostic/helper vs worker/orchestrator) before changing any source. No new model invocation is permitted for this diagnosis.

## SAME-RUN RESULT RECOVERY — SUCCESS, READ-ONLY

The already-completed parent orchestrator/result queue was recovered without invoking a new model/function path.

Recovery:
- workflow `.github/workflows/v143-recover-orchestrator-queued-result.yml`
- commit `f493cd095b6f2e00a7b6521951975c8c1e9cc7e7`
- run `34048291636`
- job `101527199470`
- conclusion success
- parent orchestrator FunctionCall `fc-01M1VT98JAEX2NZ83DSM5GJQ8A`
- job ID `K7aeTJDV7fp7l5R5UwsOvJkrC_mCDQt0`
- artifact `9993769594`
- artifact ZIP SHA-256 `342b151824ad7091f69692f24c038d2749f73abbd0d3ca5d1718cca6ebfa24e9`
- recovered worker-result SHA-256 `185a19dcd58df7bece23a75b300bb3f9fbf6d6322bf61b52b1e667b5ba684293`

Recovered result:
- generated tab present
- E Standard
- ~129.199 BPM
- 4/4
- 925 raw events
- anti-reference/runtime-safety contract passed

## PRODUCT NORMALIZATION / FREEZE / PDF — PASSED

Workflow:
- `.github/workflows/v143-freeze-recovered-completed-result.yml`
- commit `613d2442adccacfd65217352709a9e8fb70090c0`
- run `34048512501`
- job `101527783467`
- conclusion success
- artifact `9993835360`
- artifact ZIP SHA-256 `d2b70b285a4cb67aa823e167521193e86b7eb7c71f2e013f8d9e51abc864f061`

Normalization/freeze evidence:
- analysis engine `v143-reference-free-rhythm`
- raw events **925**
- canonical render events **925**
- canonical render event JSON SHA-256 `d0fe880f7ae69e44308da610ecf1c9a06e40ca7401eeeac5414fdab16efe0a56`
- render survival **100%**
- playable string/fret **925/925 = 100%**
- musical placement **925/925 = 100%**
- pitch validity **925/925 = 100%**
- all 16 sixteenth-grid steps represented
- technique events 55 (5.9% in normalization evidence)
- sustain coverage 925/925
- frozen event count **925**
- frozen canonical event SHA-256 `f5b526e608fc552925b252ecdbf7d0a6e918b04f423374798d2772939af3e2af`
- frozen snapshot SHA-256 `896058d729496abb3cd5ccdabfddfcec71e2798b6abbdb904bd9a8dbd695d433`
- professional reference remained unopened during freeze/PDF generation

PDF evidence:
- PDF event count **925**
- PDF event SHA-256 `f5b526e608fc552925b252ecdbf7d0a6e918b04f423374798d2772939af3e2af`
- PDF event fidelity **1.0**
- renderer projection exactly equal=true
- full PDF: 1,725,543 bytes, 6 pages, SHA-256 `ec81954f600cc775af30400fb6deadb797156e347e9fbc256fddbae5a93d0a94`
- preview PDF: 1,686,440 bytes, 6 pages, SHA-256 `415f9009229a5890bbe1ff5d59d6e82f513ce6bc77398e52e447be2dac39de9f`

## PROFESSIONAL FULL-1–113 SCORE — 1/1 CONSUMED

Scoring source pins:
- professional reference blob `248741bade9665a34648c59a2994bd27d73fc406`
- professional reference SHA-256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- reference coverage: measures 1–113, 113 measures, 603 professional events/onsets, 946 notes
- reference completeness verifier blob `2504581dd72b6c375fbc0b68d4d396fce58deb87`
- scorer blob `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`
- final gate/orchestrator blob `c6a84434eefa768a924395b76d1d25b4e5a51307`
- frozen input artifact run `34048512501`, artifact `v143-recovered-freeze-pdf`
- expected frozen event SHA-256 `f5b526e608fc552925b252ecdbf7d0a6e918b04f423374798d2772939af3e2af`

Scoring workflow:
- `.github/workflows/v143-score-recovered-frozen-result.yml`
- workflow blob `86c8ce916fcac70076e0c1fa0a0069f46c232acc`
- preparation/trigger commit `6869200bee98d38b681630b378016b7818815e6e`
- run `34048719525`
- job `101528345557`
- workflow conclusion **failure**
- immutable scoring boundary passed
- exact frozen artifact download passed
- frozen identity verification passed
- **the authorized scoring step began and produced the professional score JSON**, therefore the professional score budget is consumed regardless of CI conclusion
- evidence artifact `9993890158`
- evidence ZIP SHA-256 `3b227fe9df1dcd7853962bd67281e434e920482b70da9f432e9bdd129945859d`

Saved score evidence contains:
- `rhythm-reference-completeness.json` — passed, complete 1–113 reference, 946 playable notes
- `rhythm-professional-holdout-score.json` — completed professional comparison
- no final gate JSON / bounded wrapper file was preserved in this failed workflow

### Professional score result

`near100ProfessionalGatePassed = false`
`rhythmComplete = false`
`criticalMismatchCount = 1581`

Gated metrics:
- measure coverage recall: **0.9823008849557522**
- pitch-content F1: **0.30892570817744525**
- pitch-timing tolerant F1: **0.05879208979155532**
- string/fret timing tolerant F1: **0.02672367717797969**
- chord pitch-set tolerant F1: **0.004136504653567736**
- exact voicing tolerant F1: **0.004136504653567736**
- PDF event fidelity: **1.0**

Coverage mismatch:
- generated unique measure count: 113
- matched professional measures: 111/113
- missing professional measures: **88, 99**
- extra generated measures: **114, 115**

Critical mismatch breakdown:
- gross unmatched generated notes: **779**
- gross unmatched reference notes: **800**
- missing reference measures: **2**

The score proves the PDF/render plumbing is exact, but the recovered musical event stream is **not close to the professional reference under the pinned holdout scorer**. This is not a near-100 breakthrough on the current professional gate.

## IMPORTANT INTERPRETATION

Do not conflate three different outcomes:
1. **Infrastructure breakthrough:** yes — repaired async polling, exact worker completion, result recovery, deterministic product normalization, and PDF event fidelity all worked.
2. **Professional musical breakthrough:** no — the one authorized professional holdout score is far below the near-100 thresholds.
3. **Modal crash-loop UI symptom:** unresolved diagnostic clue — investigate read-only, but it does not erase the exact completed worker evidence.

## FRESH-CHAT NEXT STEPS — EXECUTE IN THIS ORDER

1. **Read this file first** and confirm branch `v143-contextual-prune-lobo`.
2. Treat both irreversible budgets as exhausted:
   - model start **1/1 consumed**;
   - professional score **1/1 consumed**.
   Do not rerun either workflow without new explicit user authorization.
3. Inspect score run `34048719525`, job `101528345557`, and artifact `9993890158` **read-only**. Use the already-produced `rhythm-professional-holdout-score.json` as the authoritative one-score result; do not repair CI and rerun the scorer.
4. Diagnose why the professional comparison is so low using only the frozen 925-event stream and the already-produced score/reference evidence. Start with deterministic, model-free analysis of:
   - measure/bar alignment and why measures 88/99 are missing while 114/115 are extra;
   - whether a bar-count / beat-grid shift causes downstream timing mismatches;
   - pitch-class/pitch-content disagreement by measure;
   - string/fret mapping disagreement vs pitch agreement;
   - chord grouping/voicing representation vs the professional reference;
   - whether the professional reference targets a materially different rhythm-guitar layer/arrangement than the analyzed stream.
5. Separate **scorer/representation/alignment defects** from **actual transcription-quality defects**. Do not tune thresholds or modify the professional reference to make the result pass.
6. Investigate the user-reported Modal **“reporting function crash-looping”** condition using read-only function/app logs and exact FunctionCall identities. Determine which function is looping. Do not invoke a new model/function call to diagnose it.
7. Prepare the smallest async tracking TTL repair so parent control/result tracking safely outlives the 1200-second worker/orchestrator runtime. Prefer a bounded value comfortably above 1200 seconds and preserve cleanup semantics. This repair can be source-tested/model-free, but **do not launch another live model run** without new authorization.
8. Save this checkpoint again after the model-free score diagnosis and TTL/reporting-function diagnosis, including any confirmed root causes and exact source blobs/commits.
9. Before proposing a future live validation, present the user with the deterministic diagnosis and explain exactly what a new run would test. A new model start or professional score requires fresh explicit authorization.

## CURRENT STATE

**Infrastructure path succeeded end-to-end after recovery: exact worker completion, same-run result recovery, 925-event product normalization, and 1.0 PDF event fidelity. The single professional holdout score has now been consumed and failed the near-100 gate by a wide margin. No model retry and no score retry are authorized. Next work is model-free diagnosis of musical/scoring alignment, the 900-second async tracking TTL defect, and the user-observed Modal reporting-function crash-loop symptom.**

## CONTINUATION — NOTE / FRET DIAGNOSIS (2026-09-06)

No new model start or professional score run has been authorized or executed during this continuation.

Deterministic frozen-result diagnosis:
- measure coverage: **111/113 = 98.23%**;
- pitch-content F1: **30.89%**;
- pitch+timing tolerant F1: **5.879%**;
- string/fret+timing tolerant F1: **2.672%**;
- chord pitch-set / exact-voicing tolerant F1: **0.414%**;
- PDF event fidelity: **100%**.

Opening evidence already shows the mismatch before fret rendering: the professional reference begins at measure 1 / step 0 with a simultaneous multi-string chord, while the frozen analyzer's first event is measure 1 / step 12. Therefore the next repair target is generic onset/grid anchoring plus preservation of simultaneous/polyphonic pitch groups before string/fret assignment.

The professional reference remains post-freeze diagnostic evidence only. Do not feed it into runtime analyzer logic and do not hardcode holdout-specific pitches, frets, measures, offsets, or thresholds.

Planned model-free repair sequence:
1. trace the exact onset/quantization, chord grouping, and pitch-to-position code paths;
2. verify source commits cannot trigger live model/scorer workflows;
3. add synthetic regression tests for step-0 anchoring, simultaneous-note preservation, unique-string chord voicing, plausible fret span, and smooth adjacent-chord movement;
4. patch the smallest generic musical-representation defects;
5. run only model-free tests;
6. checkpoint again before any future live validation proposal.

## CONTINUATION — BAR-PHASE ROOT CAUSE (2026-09-06)

No new model start and no new professional score were run. Branch source inspection and artifact analysis were read-only/model-free.

Branch safety / source boundary:
- continuation began from branch head `6e20ae4c66ff85ec16963bd96b1b077134f66edd` (`docs: checkpoint v143 note fret diagnosis`);
- `.github/workflows/v143-score-recovered-frozen-result.yml` is push-path-limited to its own workflow file;
- `.github/workflows/v143-one-shot-final-rhythm-e2e.yml` is push-path-limited to its own one-shot workflow file;
- therefore normal source/test/checkpoint commits are safe as long as those one-shot trigger files are not modified.

Deterministic timing diagnosis from the already-frozen/recovered output:
- the first generated playable event is `gridGlobalStep=0`, `measure=1`, `step=12`, `timeSeconds≈0.10449`, MIDI 57;
- the pinned professional reference begins at measure 1 / step 0, also with MIDI 57 present;
- generated event labels satisfy a +12-sixteenth offset relative to `gridGlobalStep`, consistent with `firstBeatInMeasure=3` (the fourth beat) and therefore a three-beat bar-phase rotation;
- conceptually restoring phase 0 maps global step 0→m1s0, global step 8→m1s8, global step 16→m2s0, etc.;
- this phase error is upstream of string/fret mapping, so fret changes alone cannot repair the dominant opening timing mismatch.

Confirmed source root cause in `analyzer/v143_reference_free_timing.py`:
- `_bar_phase_from_accents(...)` computes mean local accent for each beat modulo 4;
- it unconditionally selects the strongest modulo-4 phase and returns `(-best_phase) % 4`;
- confidence is calculated after selection, but there is no confidence gate, no conservative fallback, and no start-of-audio prior;
- consequently a repeating accent pattern can rotate an otherwise usable beat grid even when bar-phase evidence is ambiguous.

Repair discipline:
- the recovered result does not serialize enough bar-confidence diagnostics to justify a holdout-derived threshold;
- do not invent or tune a threshold from this one professional song/reference;
- next repair should be generic and model-free: preserve the accent estimator, add conservative phase selection for weak/ambiguous evidence, and validate it with synthetic regression cases that include both ambiguous phase evidence and clearly dominant nonzero phase evidence;
- after timing regression coverage, continue the planned simultaneous-note/chord-voicing tests and the separate async TTL/reporting-function diagnosis.

## CONTINUATION — MODEL-FREE BAR-PHASE REPAIR (2026-09-06)

No new model start and no professional score were run.

Committed repair:
- source commit `2ecc8e165db8d0afcd83901ab131d0c63223daef` — `fix: make v143 bar phase conservative`;
- timing source blob `5b95e419eb25360e72fe6c6aeb26f8c410b3b6ee`;
- regression commit `f387377b538342f284e03b617ce6f4f13e31e6b0` — `test: add model-free v143 timing regression`;
- validator path `validation/v143_model_free_regression/verify_reference_free_timing.py`;
- validator blob `1f6443e9bc301bb5b9f926fd55fffde60e163971`.

Repair behavior:
- the original mean-accent phase scoring remains intact;
- a nonzero phase is now applied only when its best-vs-runner accent advantage is repeatably separated across complete 4-beat cycles;
- separation is evaluated as a paired per-cycle mean difference divided by its standard error;
- the fixed criterion is two standard errors (`BAR_PHASE_MIN_SEPARATION_Z = 2.0`), a generic evidence rule not derived from `gomyway` or the professional reference;
- ambiguous nonzero evidence falls back to phase 0 and reports zero bar confidence for that overridden selection;
- clearly dominant nonzero phases remain supported, so the patch does not globally force all uploads to start on a downbeat.

Model-free regression coverage:
- ambiguous phase-1 advantage → conservative phase 0 → first grid slot measure 1 / step 0;
- clear phase 1 → preserved → first grid slot measure 1 / step 12;
- clear phase 2 → preserved → first grid slot measure 1 / step 8;
- clear phase 0 → remains measure 1 / step 0;
- fewer than 8 tracked beats still raises `ValueError`;
- equivalent local deterministic cases passed without importing any professional reference and without invoking any model path.

Commit isolation check from checkpoint `ddd90b159522170093cab7ccca1702546a730822` to `f387377b538342f284e03b617ce6f4f13e31e6b0`:
- only `analyzer/v143_reference_free_timing.py` and the new model-free validator changed;
- neither one-shot live workflow nor professional scorer workflow changed;
- a repository housekeeping workflow (`cleanup-tab-preview.yml`) auto-triggered on the push and concluded failure with no jobs; it was not rerun and no model/scorer workflow was invoked.

Next safe work:
1. inspect simultaneous/polyphonic candidate preservation and guitar voicing with synthetic/model-free cases;
2. inspect and repair the 900-second async result/control TTL so it safely exceeds the 1200-second runtime budget;
3. investigate the user-observed Modal reporting-function crash-loop symptom read-only;
4. checkpoint again before any future validation proposal.
