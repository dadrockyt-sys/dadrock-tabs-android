# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — SINGLE BACKEND-CAPABLE START ACCEPTED in run `33999777841`; first client poll was falsely classified terminal 502 while the Modal worker later started and continued executing; ACK/cleanup GREEN; **NO SECOND START / NO RERUN**; exact timeout semantics under read-only diagnosis  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## FROZEN BOUNDARIES

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async storage: transient structured result + non-sensitive FunctionCall control metadata only; no raw audio/stems/model bytes; TTL <= 900s; no persistent result cache.
- No production Vercel promotion/change; no Deployment Protection weakening; no whole-branch merge.
- Do not touch unrelated musical/reference issues or `core/engine/chord_mapping.py` octave folding.

## AUTHORITATIVE PINS

- Route `742954146a86aa36485d0bbdb3fbd6691a64a712`.
- `/ai-tab` page `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.
- Bridge `36584355d9b060fc7b7e20acc62524fbc7bf9005`.
- Protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`.
- V143 worker `111bf14a8f91045d3478901f8e36b88a2e7f181a`.
- Scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Approved audio `4dd709e3fa177b4daeed71ca97f0199757729d4b`.
- Repaired helper `.github/scripts/v143-existing-preview-async-breakthrough-e2e.sh` = `433599afec7fff20a31ea79e4c93ef9a6da03b36`.

## LIFECYCLE / CONFIG / TRANSPORT GATES — GREEN

- Async lifecycle/ACK proof `33985474511` GREEN.
- Direct GitHub OIDC is not trusted; do not use it.
- Authenticated `vercel curl` protected POST route transport GREEN (`33998720454`).
- Deployed V143 URL/analyzer token + bridge auth GREEN (`33999203347`).
- Deployed Blob token GREEN with invalid-audio pre-spawn rejection (`33999276060`).
- Local `vercel pull` is incomplete/non-authoritative; no local prebuilt model-bearing attempt.

## PRIOR BREAKTHROUGH ATTEMPTS — BACKEND STARTS 0

- `33998283085`: real-audio client POST blocked by Vercel before Next.js; backend/model starts 0. Do not rerun.
- `33999522733`: exact Preview inspect passed, but GET `/ai-tab` preflight returned 403; helper stopped before real-audio start. Artifact `9979067110`, digest `sha256:6d2dca3fb29075903f166d73141495bfd8eb6916ed973bf037fc9a5152dd1bb6`; backend/model starts 0. Do not rerun.

## REPAIRED POST-PREFLIGHT / EXISTING PREVIEW

- Helper repair commit `e24eb3b3ef05f25faa2ddefd1bee66327549b98e`, blob `433599afec7fff20a31ea79e4c93ef9a6da03b36`.
- Model-free preflight is authenticated `vercel curl` POST to `/api/analyze-audio-tab` with only `{"transcriptionType":"invalid"}`; requires HTTP 400 + exact Next route error before any real-audio block.
- Exact existing Preview: deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, URL `https://dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`, READY, branch `v143-contextual-prune-lobo`, immutable source commit `0a07b393bb47123a1142fd46ea6d9a55b04f0486`.
- No build/deploy/alias/promotion/protection change was made.

## SINGLE ACCEPTED BACKEND-CAPABLE RUN — `33999777841`

- Re-arm workflow commit: `67e5224d9a72c11ce5ff5aa26538cd9cbe86a612`.
- Job: `101396439738`.
- Workflow conclusion: FAILURE **by deliberate post-ACK stop after the client observed a bridge terminal-failure response**.
- Exact source/helper one-start boundary passed.
- Exact Preview inspect passed: ID `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, target Preview, status Ready.
- Model-free protected route preflight GREEN: `protectedPreviewRoutePreflightStatus=400`, `protectedPreviewRouteReached=true`.

### Start budget is consumed

- Exactly one approved real-audio Rhythm start was sent through authenticated `vercel curl`.
- Start result: `startStatus=202`, `startCurlExitCode=0`, `startRequestSeconds=4.102068`, `startAccepted=true`.
- `backendCapableRealAudioStartRequestCount=1`.
- A usable signed `v143a1.*` job token was returned and then used only for status/ACK; raw token was deleted and not retained.
- **From this point forward, NO SECOND BACKEND-CAPABLE REAL-AUDIO START and NO RERUN of `33999777841` are authorized under any outcome.**

### Client-observed terminal classification

- First same-token status poll returned `HTTP 502` after ~13 seconds: `pollCount=1`, `terminalRequestSeconds=0.555108`, `asyncTotalSeconds=13.075462102890015`.
- Client classification: `terminalState=failed`, `completed=false`, `analysisJobCompleted=false`, `generatedTabPresent=false`.
- Bounded error retained: `The analyzer job stopped before it could complete.`
- **Later Modal logs prove this client/bridge terminal classification was false: the worker subsequently started and continued running.**
- This is not a reference-facing quality result and no quality verdict was made.

### ACK / cleanup GREEN

- Helper preserved aggregate pre-ACK state, then ACKed exactly once with the same signed token.
- ACK result: `ackStatus=200`, `ackCurlExitCode=0`, `ackRequestSeconds=0.396544`, `acknowledged=true`, `transientResultCleared=true`, `bridgeAckContractClearsControl=true`.
- After ACK/cleanup, helper intentionally failed with `The single async job reached terminal failure after ACK/cleanup. STOP: diagnose exact call, no retry.`
- Raw preflight/start/status/ACK request/response material, job token, and inspect log were deleted in `if: always()` cleanup.
- Aggregate artifact only: ID `9979140544`, zip digest `sha256:dd5eaf0db145b4b8947b95b01e565893294508dda84c13e6452bf3b9771feca7`, size 1347 bytes.

### Frozen safety/product accounting from run

- `productionEnvironmentChanged=false`
- `productionPromotionPerformed=false`
- `deploymentProtectionDisabled=false`
- `rawTranscriptionRetained=false`
- `referenceFacingInputs=0`
- `referenceFacingAccuracyScored=false`
- `referenceScoreCalls=0`
- `qualityVerdictMade=false`

## READ-ONLY EXACT-CALL DIAGNOSIS — CHECKPOINT 3

No new backend-capable request, FunctionCall, workflow rerun, deployment, protection change, audio invocation, or model invocation was performed by this diagnosis. All Modal evidence below comes from already-completed log-only diagnostic workflows.

### Vercel / Actions boundary

- Vercel runtime evidence for deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD` confirms: model-free preflight `400` at ~`23:52:19Z`, accepted start `202` at ~`23:52:21Z`, same-token client status `502` at ~`23:52:32Z`, ACK `200` at ~`23:52:34Z`.
- No Vercel application stack trace/function crash appears in that window. The client `502` came from the bounded bridge/status path, not a Vercel function crash.
- Actions confirms the status HTTP request itself took only `0.555108s`; `~13s` is elapsed async time since start, not a 13-second Vercel request timeout.

### Source-level 502 mapping

- Pinned route forwards bridge `status === 'failed'` as HTTP `502` with bridge bounded error.
- Exact retained error `The analyzer job stopped before it could complete.` maps to the bridge branch where no result envelope is available and `modal.FunctionCall.from_id(...).get(timeout=0)` raises an exception that is **not caught by the bridge's `except modal.exception.TimeoutError` clause**; generic `except Exception` then labels the orchestrator call failed.
- Earlier Checkpoint 2 inferred from source alone that the orchestrator had terminally failed. **That inference is now superseded by direct Modal logs below.**

### Existing exact-call Modal log evidence — decisive lifecycle correction

Broader log-only run `34000077005`, job `101397240115`, completed GREEN and performed only Modal history/container/log reads. It explicitly emitted `diagnosticOnly=true`, `audioOrModelInvokedByThisDiagnostic=false`, `workerSpawnedByThisDiagnostic=false`.

Bridge/orchestrator evidence:
- bridge/orchestrator container `ta-01M1SZSPZ6QQS0DNAEBJSJ8X8R` start time `2026-09-05 23:52:28+00:00`;
- orchestrator FunctionCall `fc-01M1SZSP90108F9D2EP8K4PWJ8` logged `V143_ASYNC_STAGE orchestrator.start` at `23:52:28`;
- same FunctionCall logged `V143_ASYNC_STAGE worker_call.start` at `23:52:28`;
- bridge status POST completed `200` at Modal at `23:52:33` (the Next.js layer translated its bounded `status='failed'` payload to client HTTP `502`);
- bridge ACK POST completed `200` at `23:52:34`.

Worker evidence for the same accepted job:
- worker container `ta-01M1SZSTNZ2VGH7QD6BZ25J3TR` start time `2026-09-05 23:52:34+00:00`;
- worker FunctionCall `fc-01M1SZST99RMZWN0SPV88WWEEB` logged `V143_STAGE worker.start` at `23:52:36`;
- it immediately logged download start/done, normalize start/done, router start, separator start, input normalization, direct Demucs start, and Roformer start;
- audio download completed in ~`0.780s`, normalization in ~`1.397s` from worker user-code start;
- separator/model startup logs continued well after the client's `502` and after ACK;
- Roformer completed at ~`23:54:04` (`separator.roformer.done elapsed=86.850`) and cascade Demucs then started;
- the worker was still active minutes later when the read-only diagnostic collected logs.

**Decisive lifecycle conclusion:** the accepted async job did not terminally fail at the first status poll. The bridge falsely classified a still-in-flight orchestrator/worker as terminal failed. The orchestrator had entered `worker.remote(...)`; the GPU worker cold-started several seconds later and executed substantial download/normalization/separator/model work. ACK cleared bridge-side transient control/result metadata but did not cancel the already-dispatched worker, which therefore continued orphaned from the client lifecycle.

### Narrowed-log filter caveat

- Later log-only run `34000153347`, job `101397440154`, correctly recovered `orchestrator.start` and `worker_call.start` but printed `workerFilteredLines=0`.
- That zero is a filtering artifact: the workflow's `SIGNAL` regex includes `V143_ASYNC_STAGE` but omits the worker's actual `V143_STAGE worker.*` marker.
- Therefore `workerFilteredLines=0` must **not** be used as evidence that the worker failed to start; broader run `34000077005` directly proves it did start.

## CURRENT ROOT-CAUSE CANDIDATE — TIMEOUT EXCEPTION CLASS MISMATCH

The remaining exact question is why a normal pending `FunctionCall.get(timeout=0)` fell through the bridge's generic `except Exception` instead of the intended `modal.exception.TimeoutError` running branch.

Current strongest candidate:
- while the orchestrator was legitimately still pending/cold-starting its remote worker, `FunctionCall.get(timeout=0)` raised a timeout/poll-not-ready exception class different from `modal.exception.TimeoutError`;
- the bridge catches only `modal.exception.TimeoutError`, so that normal pending condition was caught by generic `except Exception` and mislabeled terminal failure;
- direct timing strongly supports a poll-state bug: bridge status returned failure at `23:52:33`, worker container started at `23:52:34`, and worker user code began at `23:52:36`.

This candidate is **not yet promoted to exact root cause** until Modal 1.5.5 `FunctionCall.get(timeout=0)` exception semantics are confirmed from authoritative source/documentation.

## NEXT — READ-ONLY SEMANTICS CONFIRMATION ONLY

1. **Do not edit/rearm/rerun the breakthrough workflow and do not send any real-audio start.**
2. Read authoritative Modal client/source/docs for the exact exception raised by `FunctionCall.get(timeout=0)` when a call is still pending, with focus on Modal client 1.5.5 used by the bridge deployment/diagnostic tooling.
3. If the exception-class mismatch is confirmed, checkpoint it as exact root cause before any bridge code repair.
4. If not confirmed, continue read-only examination of FunctionCall poll semantics/version behavior; do not infer terminal worker failure from the already disproven client `502` classification.
5. Any eventual repair must first be statically/model-free validated; **no repair may be validated with a second model-bearing start in this diagnostic phase.**

## HARD STOPS

- **NO SECOND REAL-AUDIO START. NO RERUN OF `33999777841`, `33999522733`, OR `33998283085`.**
- No ad-hoc real-audio request.
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change before exact-call diagnosis.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in retained evidence.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **the one backend-capable start is consumed; client terminal 502 is proven false by existing Modal lifecycle logs; worker execution did occur and continued after ACK; only read-only confirmation of the polling/timeout root cause is authorized now.**
