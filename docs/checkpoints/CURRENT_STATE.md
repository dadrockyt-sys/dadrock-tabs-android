# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — SINGLE BACKEND-CAPABLE START ACCEPTED in run `33999777841`; first client poll falsely classified terminal 502 while worker remained active; **EXACT ROOT CAUSE CONFIRMED: Modal 1.5.5 built-in `TimeoutError` was not caught by bridge's distinct `modal.exception.TimeoutError`**; ACK/cleanup GREEN; **NO SECOND START / NO RERUN**  
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

## READ-ONLY EXACT-CALL DIAGNOSIS — CHECKPOINT 4 / EXACT ROOT CAUSE

No new backend-capable request, FunctionCall, workflow rerun, deployment, protection change, audio invocation, or model invocation was performed by this diagnosis. All exact-call runtime evidence came from already-completed log-only workflows; Modal semantics were confirmed from the public Modal 1.5.5 release source.

### Vercel / Actions boundary

- Vercel runtime evidence for deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD` confirms: model-free preflight `400` at ~`23:52:19Z`, accepted start `202` at ~`23:52:21Z`, same-token client status `502` at ~`23:52:32Z`, ACK `200` at ~`23:52:34Z`.
- No Vercel application stack trace/function crash appears in that window. The client `502` came from the bounded bridge/status path, not a Vercel function crash.
- Actions confirms the status HTTP request itself took only `0.555108s`; `~13s` is elapsed async time since start, not a 13-second Vercel request timeout.

### Existing exact-call Modal lifecycle evidence

Broader log-only run `34000077005`, job `101397240115`, completed GREEN and performed only Modal history/container/log reads. It explicitly emitted `diagnosticOnly=true`, `audioOrModelInvokedByThisDiagnostic=false`, `workerSpawnedByThisDiagnostic=false`.

Bridge/orchestrator:
- container `ta-01M1SZSPZ6QQS0DNAEBJSJ8X8R` start time `2026-09-05 23:52:28+00:00`;
- FunctionCall `fc-01M1SZSP90108F9D2EP8K4PWJ8` logged `V143_ASYNC_STAGE orchestrator.start` at `23:52:28`;
- same FunctionCall logged `V143_ASYNC_STAGE worker_call.start` at `23:52:28`;
- Modal bridge status POST completed `200` at `23:52:33`; Next.js translated bridge `status='failed'` to client HTTP `502`;
- ACK POST completed `200` at `23:52:34`.

Worker:
- container `ta-01M1SZSTNZ2VGH7QD6BZ25J3TR` start time `2026-09-05 23:52:34+00:00`;
- FunctionCall `fc-01M1SZST99RMZWN0SPV88WWEEB` logged `V143_STAGE worker.start` at `23:52:36`;
- then download/normalize/router/separator/Demucs/Roformer stages ran;
- Roformer completed at ~`23:54:04` (`separator.roformer.done elapsed=86.850`) and cascade Demucs started;
- worker was still active minutes after the false client terminal response and ACK.

**Lifecycle conclusion:** the accepted async job did not terminally fail at the first status poll. The orchestrator was legitimately blocked inside `_worker_handle().remote(...)` while its GPU worker cold-started. ACK removed bridge-side tracking but did not cancel the remote worker, so execution continued orphaned from the client lifecycle.

### Narrowed-log filter caveat

- Later log-only run `34000153347`, job `101397440154`, recovered `orchestrator.start` / `worker_call.start` but printed `workerFilteredLines=0`.
- That is a filter artifact: its regex includes `V143_ASYNC_STAGE` but omits actual worker marker `V143_STAGE worker.*`.
- Broader run `34000077005` is authoritative for worker execution.

### Authoritative Modal 1.5.5 semantics — exact confirmation

PyPI published `modal-1.5.5` on 2026-08-28. Its provenance identifies source Git origin `712e0bd181ef892d769e26f7bca9fd385d09f606`. The public `modal-labs/modal-client` mirror release commit `c3922a2c5719e5843618e8cd3fcf664cc1ddfeba` is explicitly `Release 1.5.5 of the Python SDK` and carries the same `GitOrigin-RevId: 712e0bd181ef892d769e26f7bca9fd385d09f606`; `py/modal_version/__init__.py` at that commit is exactly `__version__ = "1.5.5"`.

At that exact release commit:
- `_Invocation.poll_function(timeout=...)` raises **bare `TimeoutError()`** when there are no outputs but unfinished inputs remain; `timeout=0` therefore uses this path as an immediate pending poll.
- `py/modal/_functions.py` does **not** import `TimeoutError` from `.exception`; the bare name resolves to Python's built-in `TimeoutError`.
- `py/modal/exception.py` separately defines `class TimeoutError(Error)`, where `Error` is Modal's custom `Exception` subclass. This is a distinct class; it is not an alias/base class for Python's built-in `TimeoutError`.

Pinned bridge blob `36584355d9b060fc7b7e20acc62524fbc7bf9005` does:

`call.get(timeout=0)` -> `except modal.exception.TimeoutError:` => processing -> generic `except Exception:` => bounded terminal failed.

## EXACT ROOT CAUSE — CONFIRMED

**The async bridge catches the wrong timeout exception class for `FunctionCall.get(timeout=0)` under Modal 1.5.5.**

When the orchestrator is still running, Modal 1.5.5 raises Python's built-in `TimeoutError`. The bridge catches only the distinct `modal.exception.TimeoutError`, so the normal pending-poll exception bypasses the intended `processing` branch and falls into generic `except Exception`, returning `status='failed'` / `The analyzer job stopped before it could complete.` Next.js maps that bounded bridge failure to client HTTP `502`.

This exactly explains all observed timing:
- orchestrator begins `worker.remote(...)` at `23:52:28`;
- status poll at `23:52:33` sees the FunctionCall still unfinished and receives built-in `TimeoutError`;
- bridge misclassifies that normal pending condition as terminal failure;
- worker container starts `23:52:34` and user code starts `23:52:36`;
- ACK at `23:52:34` clears tracking but does not cancel the already-dispatched worker;
- worker continues model/separator execution for minutes.

Root cause is now sufficiently established to consider a narrowly scoped bridge repair. No model/scheduler/worker/route change is implicated by this failure.

## NEXT — NARROW MODEL-FREE REPAIR ONLY

1. **Do not edit/rearm/rerun the breakthrough workflow and do not send any real-audio start.**
2. Repair only the bridge status polling timeout catch so Modal 1.5.5's built-in `TimeoutError` is classified `processing`. Prefer the narrowest version-robust catch supported by static tests; do not change worker/model/scheduler behavior.
3. Add/adjust a local/static/model-free regression test that proves an in-flight `FunctionCall.get(timeout=0)` built-in `TimeoutError` returns `processing`, while a true non-timeout exception remains terminal failed.
4. Validate only with static/local/model-free checks or an existing no-audio async smoke seam. **Do not validate with another backend-capable real-audio/model-bearing start.**
5. Checkpoint repair commit, validation evidence, and unchanged safety accounting before any further step.

## HARD STOPS

- **NO SECOND REAL-AUDIO START. NO RERUN OF `33999777841`, `33999522733`, OR `33998283085`.**
- No ad-hoc real-audio request.
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change for this repair.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in retained evidence.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **the one backend-capable start is consumed; exact false-terminal root cause is confirmed as a Modal 1.5.5 timeout exception-class mismatch; only a narrow bridge polling repair plus model-free/static validation is authorized next.**
