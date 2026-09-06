# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-06 — **AUTHORIZED V143 WORKER COMPLETED; CLIENT LOST TRACKING AT 900s TTL; RESULT RECOVERY IN PROGRESS; NO SECOND MODEL RUN.**
Branch: `v143-contextual-prune-lobo`

## HARD AUTHORIZATION BOUNDARY

User authorized exactly:
- **1** additional current-V143 `gomyway` Rhythm model-bearing start;
- **1** professional full-1–113 score only against the completed frozen result from that exact start;
- deterministic preview/full PDF validation from that same completed result.

Current counters:
- replacement live: **0 available / 1 consumed**
- professional full-1–113 score: **1 available / 0 consumed**
- replacement PDF E2E: **0 performed**

Hard stop rules:
- **NO second/replacement/retry Rhythm start** without new explicit user authorization.
- No Lead/Bass model-bearing run.
- No professional score until the exact completed replacement result has been recovered, product-normalized, and frozen.
- No Vercel production deploy/promotion, Deployment Protection weakening, optimizer/training/threshold sweep, or scheduler/model/parameter mutation.

## PINNED REPAIRED BOUNDARY

Old ~7-second 502 root cause was stale production Modal HTTP bridge behavior around zero-timeout pending polls. The repaired bridge was deployed and model-free verified before the authorized replacement start.

Pinned source:
- bridge `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- async protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`
- live worker `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- separator/scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`
- audio `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- professional reference SHA-256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`
- professional reference coverage: measures 1–113; 113 measures; 603 professional events/onsets; 946 notes

Repair deploy:
- workflow run `34041343616`, job `101508549305`, success
- evidence artifact `9991761743`, SHA-256 `02dff61207bac1b42331cd0359e92ab3bcecd252e00c15cbb0011d714f6aa49e`

Green model-free Preview preflight:
- run `34042266658`, job `101511044644`, success
- Preview `dpl_5j26ZS2xq3utrHxW7waCd5NEPaQk`
- URL `https://dadrock-tabs-android-r9uhb2dg9-stephen-mcnally-s-projects.vercel.app`
- source `631544a8668033392300f2739c87232553dbadc0`
- `/ai-tab` HTTP 200, 38016 bytes
- invalid-type analyze probe HTTP 400 as expected
- evidence artifact `9992037110`, SHA-256 `bf83017022ca3cc15ff7e13841615b3223ac64da05b9e8aed1c62ef7e40e186d`

## EXACT AUTHORIZED ONE-SHOT

Runner:
- workflow `.github/workflows/v143-one-shot-final-rhythm-e2e.yml`
- helper `.github/scripts/v143-one-shot-final-rhythm-existing-preview.sh`
- helper blob `e2847e4d05ae1fea781ef07e891fece1bfbecbf0`
- retarget commit `9f4d8b59a15288cab02c7930093f80db57e52df0`
- workflow blob `d803af28820cff23750e503cf2fdea5aa8299d83`
- arm commit `acdf236e5e2649d3beb515fb2fc8a0abf345cc51`

Authorized run:
- GitHub workflow run `34046854397`
- job `101523324268`
- exactly one model-bearing Rhythm start
- start HTTP 202, accepted about `2026-09-06T16:54:33Z`
- same-token polls 1–130 returned HTTP 202
- poll 130 elapsed about 902 s
- poll 131 returned HTTP 502 at about 908 s (`2026-09-06T17:09:35Z`)
- helper stopped with no retry
- same-job ACK HTTP 200, acknowledged=true, transientResultCleared=true
- bounded failure artifact `9993601754`, SHA-256 `9c5661024e59ee70068e87eb286aa8e1095f85455c2203ed64870d7dded7f50e`
- artifact confirms `modelBearingStartRequestCount=1`, `professionalScoreCalls=0`, `pdfE2EPerformed=false`

## CONFIRMED 900-SECOND TRACKING TTL BUG

This is now the confirmed reason the Preview/GitHub client reported failure at ~908 seconds.

`analyzer/v143_async_job_protocol.py` defines:
- `ASYNC_RESULT_TTL_SECONDS = 15 * 60` = **900 seconds**.

`analyzer/v143_modal_http_endpoint.py` uses that same 900-second TTL for the control partition containing the **only tracked orchestrator FunctionCall ID**.

Status behavior:
1. read result partition;
2. read control partition;
3. if control is absent, immediately return failed: `The analyzer job state is no longer available.`

The Modal orchestrator and live worker both allow up to **1200 seconds**, but the only client tracking control expires at **900 seconds**. Therefore any valid run longer than 15 minutes can be falsely reported failed before the worker's 20-minute execution allowance is exhausted.

Observed timing matches this exactly:
- start ~16:54:33Z
- 900 s boundary ~17:09:33Z
- terminal client 502 ~17:09:35Z / elapsed ~908 s

The prior bridge pending-poll bug remains fixed; this is a second, separate async protocol defect.

## EXACT MODAL WORKER — COMPLETED, NOT CRASHED

Read-only Modal log diagnostics proved the exact worker FunctionCall completed all stages.

Exact worker identity:
- app `dadrock-v143-ai-tab-live`
- Function ID `fu-cXv3G2TXumycjiCTABviS7`
- FunctionCall ID `fc-01M1VT9BDS5TYWE52GPYQQ8W9E`
- container `ta-01M1VT9BRA8YRBNK1DKSC329BR`

Stage timeline from exact FunctionCall logs:
- `worker.start` 16:54:41Z
- download done elapsed 0.839 s
- normalize done elapsed 1.464 s
- router start elapsed 1.464 s
- separator direct Demucs + RoFormer started
- RoFormer done elapsed 78.878 s
- direct Demucs done elapsed 722.604 s
- cascade Demucs done elapsed 785.822 s
- separator done elapsed **785.929 s**
- Basic Pitch ran on direct and cascade guitar views
- techniques start elapsed 858.206 s
- techniques done elapsed 933.898 s
- router done elapsed 936.834 s
- **worker.done elapsed 936.836 s** at about `17:10:18Z`

Critical conclusion:
- the exact authorized model worker **completed successfully about 29 seconds after the client had already failed due to the 900-second tracking TTL**;
- the separator did not fail; both Demucs branches and RoFormer completed;
- Basic Pitch and technique enrichment also completed;
- the earlier dashboard observation of “crash-looping” was not evidence that this exact FunctionCall failed; exact FunctionCall logs are authoritative and show `worker.done`.

This is encouraging for the Songsterr-inspired process, but musical quality is **not yet scored** because the structured result still must be recovered and frozen.

## MODAL MEMORY CORRECTION

Do not use the earlier 8 GB hard-cap/OOM theory.
- `memory=8192` in current Modal is a memory request/minimum, not necessarily an 8 GB hard limit; a hard cap requires a `(request, limit)` tuple.
- Exact logs also show the separator and worker completed, so OOM is not the observed failure here.

## READ-ONLY DIAGNOSTICS / RECOVERY

No diagnostic below invoked a function or model, changed a deployment, or consumed score/PDF budget.

1. Broad worker log diagnostic:
- workflow `.github/workflows/v143-modal-crash-log-diagnostic.yml`
- initial commit `f90b4f6611faa440b2febcc11cf0995d7cfebc78`
- run `34047879478`, job `101526097080`, success
- artifact `9993657140`, SHA-256 `a07d24e9456c667f48c2abb8146c7393bfc8bd93347390deebb4ab4932f1f2e7`

2. Exact FunctionCall diagnostic:
- narrowed commit `642df65cbecb03011648721271bbaf04800f492d`
- run `34047990402`, success
- artifact `9993685857`, SHA-256 `e87bf1f0039ff7d0aa871e32009bf899f187f0c6bc04f3880c77a2bb29b59387`
- exact stage log proves worker.done at 936.836 s

3. Direct child FunctionCall result recovery attempt:
- workflow `.github/workflows/v143-recover-completed-functioncall.yml`
- commit `71def911839f7d2be6f26472fccf0734dddad1bd`
- run `34048212996`, job `101526986321`
- read-only retrieval failed with Modal `NotFoundError` because the child FunctionCall output had already been consumed by its parent orchestrator
- no model/score/PDF action occurred

4. Parent orchestrator/result-queue recovery:
- workflow `.github/workflows/v143-recover-orchestrator-queued-result.yml`
- commit `f493cd095b6f2e00a7b6521951975c8c1e9cc7e7`
- run `34048291636`, currently in progress at this checkpoint
- purpose: parse the parent orchestrator FunctionCall ID from `dadrock-v143-http-bridge` logs, read that already-completed parent result, recover its `jobId`, then read/decode the already-written transient completed result queue partition
- **read-only only; no model invocation; professionalScoreCalls=0; pdfE2EPerformed=false**

## SAFE NEXT STEPS

1. Inspect run `34048291636` to terminal.
2. If the exact completed structured worker result is recovered, validate its V143 anti-reference safety contract and hash it.
3. Reproduce the same deterministic Preview product-normalization/render contract on that exact recovered result; do not regenerate analyzer output.
4. Freeze that exact normalized result.
5. Render deterministic preview/full PDFs and verify event fidelity.
6. Only after freeze/PDF identity is proven, consume the **one authorized professional full-1–113 score**.
7. Save final bounded evidence and scrub temporary full structured result material.
8. Independently prepare the smallest async-protocol repair for future runs: tracking/control TTL must safely outlive the 1200-second worker/orchestrator runtime. Do not use that repair to launch another model run without new explicit user authorization.

Current state: **AUTHORIZED MODEL WORKER COMPLETED SUCCESSFULLY. CLIENT FAILURE WAS THE 900-SECOND TRACKING TTL. ONE MODEL START CONSUMED; NO RETRY. PROFESSIONAL SCORE UNUSED. PDF E2E UNUSED. EXACT RESULT RECOVERY IS IN PROGRESS SO THIS SAME COMPLETED RUN MAY STILL BE FROZEN AND SCORED.**
