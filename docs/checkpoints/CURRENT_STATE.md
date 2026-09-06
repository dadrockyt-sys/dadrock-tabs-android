# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-06 — **AUTHORIZED V143 RESULT RECOVERED + FROZEN; PDF E2E EXACT; PROFESSIONAL SCORE NOT YET CONSUMED.**
Branch: `v143-contextual-prune-lobo`

## HARD AUTHORIZATION BOUNDARY

User authorized exactly:
- **1** additional current-V143 `gomyway` Rhythm model-bearing start;
- **1** professional full-1–113 score only against the completed frozen result from that exact start;
- deterministic preview/full PDF validation from that same completed result.

Current counters:
- replacement live: **0 available / 1 consumed**
- professional full-1–113 score: **1 available / 0 consumed**
- replacement PDF E2E: **1 performed / passed**

Do not issue any second/replacement/retry model start. No Lead/Bass model run. No second professional score. No Vercel production promotion/deploy, Deployment Protection weakening, optimizer/training/threshold sweep, or scheduler/model/parameter mutation.

## REPAIRED PREVIEW / ASYNC BOUNDARY

Pinned source:
- Preview deployment `dpl_5j26ZS2xq3utrHxW7waCd5NEPaQk`
- Preview source `631544a8668033392300f2739c87232553dbadc0`
- route `a3d02876d2c4efeb6f5258586046bc95cfc132b6`
- repaired bridge `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- async protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`
- live worker `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- separator/scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`
- audio blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- professional reference SHA-256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- professional reference: measures 1–113; 113 measures; 603 professional events/onsets; 946 notes

Bridge repair deploy:
- run `34041343616`, job `101508549305`, success
- artifact `9991761743`, SHA-256 `02dff61207bac1b42331cd0359e92ab3bcecd252e00c15cbb0011d714f6aa49e`

Green model-free Preview preflight:
- run `34042266658`, job `101511044644`, success
- artifact `9992037110`, SHA-256 `bf83017022ca3cc15ff7e13841615b3223ac64da05b9e8aed1c62ef7e40e186d`

## EXACT AUTHORIZED MODEL RUN

- runner `.github/workflows/v143-one-shot-final-rhythm-e2e.yml`
- helper `.github/scripts/v143-one-shot-final-rhythm-existing-preview.sh`, blob `e2847e4d05ae1fea781ef07e891fece1bfbecbf0`
- retarget commit `9f4d8b59a15288cab02c7930093f80db57e52df0`
- arm commit `acdf236e5e2649d3beb515fb2fc8a0abf345cc51`
- workflow run `34046854397`, job `101523324268`
- exactly one Rhythm start; HTTP 202 around `2026-09-06T16:54:33Z`
- same-token polls 1–130 returned 202; poll 131 returned 502 at ~908 s
- same-job ACK HTTP 200; acknowledged=true; transientResultCleared=true
- bounded artifact `9993601754`, SHA-256 `9c5661024e59ee70068e87eb286aa8e1095f85455c2203ed64870d7dded7f50e`

## CONFIRMED CLIENT FAILURE CAUSE: 900-SECOND TRACKING TTL

`ASYNC_RESULT_TTL_SECONDS = 900`, and the control partition holding the only orchestrator FunctionCall ID used the same 900-second TTL while worker/orchestrator timeout is 1200 seconds. When that control expired, status returned `The analyzer job state is no longer available.`

Timing matches exactly:
- start ~16:54:33Z
- 900-second boundary ~17:09:33Z
- client 502 ~17:09:35Z / ~908 seconds

This is separate from the earlier pending-poll bridge bug, which was already repaired.

## EXACT MODAL WORKER COMPLETED SUCCESSFULLY

Read-only exact FunctionCall diagnostics:
- worker Function ID `fu-cXv3G2TXumycjiCTABviS7`
- worker FunctionCall `fc-01M1VT9BDS5TYWE52GPYQQ8W9E`
- container `ta-01M1VT9BRA8YRBNK1DKSC329BR`
- exact worker logs prove `worker.done elapsed=936.836` at about `17:10:18Z`
- separator done ~785.929 s
- Basic Pitch and technique enrichment completed
- worker completed ~29 seconds after the client lost the 900-second tracking record

Exact FunctionCall diagnostic artifact:
- run `34047990402`
- artifact `9993685857`
- SHA-256 `e87bf1f0039ff7d0aa871e32009bf899f187f0c6bc04f3880c77a2bb29b59387`

Do not use the earlier OOM theory; exact worker logs show successful completion, and integer `memory=8192` is not established here as an 8 GB hard cap.

## SAME-RUN RESULT RECOVERY — SUCCESS

The child FunctionCall output was already consumed by its parent orchestrator, so direct child `get()` returned NotFound without invoking anything. The already-completed parent orchestrator/result queue was then recovered read-only.

Successful recovery:
- workflow `.github/workflows/v143-recover-orchestrator-queued-result.yml`
- commit `f493cd095b6f2e00a7b6521951975c8c1e9cc7e7`
- run `34048291636`, job `101527199470`, success
- parent orchestrator FunctionCall `fc-01M1VT98JAEX2NZ83DSM5GJQ8A`
- job ID `K7aeTJDV7fp7l5R5UwsOvJkrC_mCDQt0`
- artifact `9993769594`, ZIP SHA-256 `342b151824ad7091f69692f24c038d2749f73abbd0d3ca5d1718cca6ebfa24e9`
- recovered worker-result SHA-256 `185a19dcd58df7bece23a75b300bb3f9fbf6d6322bf61b52b1e667b5ba684293`
- recovered result: generated tab present, E Standard, ~129.199 BPM, 4/4, 925 events
- full anti-reference safety contract passed
- no new function/model invocation

## EXACT PRODUCT NORMALIZATION / FREEZE / PDFs — SUCCESS

Workflow:
- `.github/workflows/v143-freeze-recovered-completed-result.yml`
- commit `613d2442adccacfd65217352709a9e8fb70090c0`
- run `34048512501`
- job `101527783467`
- conclusion **success**
- artifact `9993835360`
- artifact ZIP SHA-256 `d2b70b285a4cb67aa823e167521193e86b7eb7c71f2e013f8d9e51abc864f061`

The workflow checked out exact Preview source `631544a...`, verified exact route/product/render/quality/promotion/freeze/PDF source blobs, verified recovered result SHA, and then used the same V143 product/render contract before freezing.

Product-normalization evidence:
- analysis engine `v143-reference-free-rhythm`
- raw events **925**
- canonical render events **925**
- canonical render event JSON SHA-256 `d0fe880f7ae69e44308da610ecf1c9a06e40ca7401eeeac5414fdab16efe0a56`
- quality gate **passed**
- render survival **100%**
- playable string/fret **925/925 = 100%**
- musical placement **925/925 = 100%**
- pitch validity **925/925 = 100%**
- measure range first 1, last 115, **113 unique measures**
- all 16 sixteenth-grid steps represented
- technique events 55 (5.9%): bend, bend-release, hammer-on, pull-off, slide-down, slide-up
- sustain coverage 925/925
- placement promotion did **not** modify placement: `AUTHENTICATED_RENDER_EVENTS_PRESENT`
- reference remained unopened

Frozen identity:
- event count **925**
- canonical frozen event SHA-256 `f5b526e608fc552925b252ecdbf7d0a6e918b04f423374798d2772939af3e2af`
- frozen snapshot SHA-256 `896058d729496abb3cd5ccdabfddfcec71e2798b6abbdb904bd9a8dbd695d433`
- unique measure count **113**
- professionalReferenceUsed=false
- referenceOpenedDuringFreeze=false
- v143RuntimeSafetyVerified=true

PDF identity:
- PDF event count **925**
- PDF event SHA-256 `f5b526e608fc552925b252ecdbf7d0a6e918b04f423374798d2772939af3e2af`
- PDF event fidelity **1.0**
- renderer projection exactly equal=true
- full PDF: 1,725,543 bytes, 6 pages, SHA-256 `ec81954f600cc775af30400fb6deadb797156e347e9fbc256fddbae5a93d0a94`
- preview PDF: 1,686,440 bytes, 6 pages, SHA-256 `415f9009229a5890bbe1ff5d59d6e82f513ce6bc77398e52e447be2dac39de9f`
- reference remained unopened during PDF validation

## NEXT IRREVERSIBLE ACTION

Run **exactly one** professional full-1–113 score against this exact frozen stream only. Before execution, pin scorer/orchestrator/reference identities and the freeze artifact. Once the score command begins, set professional score to **0 available / 1 consumed**, regardless of pass/fail. Do not perform any second score.

After scoring:
1. preserve bounded score evidence;
2. update this checkpoint with exact metrics/verdict/artifact/hash;
3. then prepare the smallest future async TTL repair so tracking safely outlives the 1200-second worker/orchestrator runtime, but do not launch another model run.

Current state: **SAME AUTHORIZED MODEL RUN RECOVERED, PRODUCT-VALIDATED, FROZEN, AND PDF-VERIFIED EXACTLY. MODEL START 1/1 CONSUMED. PDF E2E PASSED. PROFESSIONAL SCORE STILL 0/1 CONSUMED AND IS THE NEXT/ONLY REMAINING EVALUATION ACTION.**
