# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — SINGLE BACKEND-CAPABLE START ACCEPTED in run `33999777841`; first poll terminal 502; ACK/cleanup GREEN; **NO SECOND START / NO RERUN**; read-only exact-call diagnosis next  
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
- Worker `111bf14a8f91045d3478901f8e36b88a2e7f181a`.
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
- Workflow conclusion: FAILURE **by deliberate post-ACK stop after terminal job failure**.
- Exact source/helper one-start boundary passed.
- Exact Preview inspect passed: ID `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, target Preview, status Ready.
- Model-free protected route preflight GREEN: `protectedPreviewRoutePreflightStatus=400`, `protectedPreviewRouteReached=true`.

### Start budget is consumed

- Exactly one approved real-audio Rhythm start was sent through authenticated `vercel curl`.
- Start result: `startStatus=202`, `startCurlExitCode=0`, `startRequestSeconds=4.102068`, `startAccepted=true`.
- `backendCapableRealAudioStartRequestCount=1`.
- A usable signed `v143a1.*` job token was returned and then used only for status/ACK; raw token was deleted and not retained.
- **From this point forward, NO SECOND BACKEND-CAPABLE REAL-AUDIO START and NO RERUN of `33999777841` are authorized under any outcome.**

### Terminal failure

- First same-token status poll returned `HTTP 502` after ~13 seconds: `pollCount=1`, `terminalRequestSeconds=0.555108`, `asyncTotalSeconds=13.075462102890015`.
- Terminal classification: `terminalState=failed`, `completed=false`, `analysisJobCompleted=false`, `generatedTabPresent=false`.
- Bounded error retained: `The analyzer job stopped before it could complete.`
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

## CURRENT ROOT-CAUSE QUESTION

The accepted async job reached a bounded terminal failure extremely quickly (~13s), before any completed product payload. The next task is to determine **where that one FunctionCall/job failed and whether worker/model execution began**. This must be diagnosed from existing evidence only.

## NEXT — READ-ONLY EXACT-CALL DIAGNOSIS ONLY

1. **Do not edit/rearm/rerun the breakthrough workflow and do not send any real-audio start.**
2. Inspect Vercel runtime logs for deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD` around `2026-09-05T23:52:18Z`–`23:52:36Z` to classify route/bridge start/status/ACK behavior.
3. Inspect existing Modal bridge/orchestrator/worker logs for the same exact window using read-only/log-only tooling. Do not spawn a FunctionCall, invoke audio, or execute a model as part of diagnosis.
4. Determine whether the accepted FunctionCall failed before worker execution, during audio download, during separator/model startup, or later. Preserve only bounded error/control evidence; no raw audio/stems/model bytes.
5. Read route/bridge/worker source as needed to map the observed HTTP 502/error to the exact failure layer.
6. Checkpoint the exact root cause before proposing any code/config repair. **No repair may be validated with a second model-bearing start in this diagnostic phase.**

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

Current authorization state: **the one backend-capable start is consumed; terminal 502 + ACK/cleanup are proven; only read-only diagnosis of this exact call is authorized now.**
