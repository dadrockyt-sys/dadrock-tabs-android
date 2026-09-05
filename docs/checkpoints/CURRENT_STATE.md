# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — authenticated `vercel curl` transport GREEN; deployed Preview V143 URL/token/Blob runtime config GREEN; zero backend/model starts preserved; next E2E repair can target existing pinned Preview  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## FROZEN BOUNDARIES

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async storage: transient structured result + non-sensitive FunctionCall control metadata only; no raw audio/stems/model bytes; TTL <= 900s; no persistent result cache.
- No production Vercel promotion/change; no whole-branch merge while proving first E2E.
- Do not touch unrelated musical/reference issues or `core/engine/chord_mapping.py` octave folding.

## AUTHORITATIVE SOURCE PINS

- Production `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`; production deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`; synchronous route blob `06234db3e1cc1680b18fd62a765862b213ede3db`.
- V143 worker blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`; scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Hardened bridge `36584355d9b060fc7b7e20acc62524fbc7bf9005`; protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`.
- Branch async route `742954146a86aa36485d0bbdb3fbd6691a64a712`; `/ai-tab` page `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.
- Approved audio `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`.

## LIFECYCLE GATE — GREEN / DO NOT REOPEN WITHOUT NEW EVIDENCE

- Startup diagnosis `33985149949` / job `101357179709` SUCCESS with no model/audio/reference-facing invocation.
- Isolated async control proof `33985474511` / job `101358067142` SUCCESS; artifact `9975020241`, digest `sha256:b701ad58e32d538336f21279289bb189aca4324ec5029242d1f08246d4e1a493`.
- Proven: one tracked start, deterministic terminal state, ACK clears result/control, TTL 900, no audio/model bytes in transient transport, reference-facing calls 0.

## FIRST ARMED RUN — CLIENT AUDIO POST BLOCKED BY PROTECTION / ZERO BACKEND STARTS

- Helper `.github/scripts/v143-fresh-preview-async-breakthrough-e2e.sh` commit `8d536121bb9a38f4a69add31cbf7515400441c5b`, blob `92d17ee0b01ff72f71abfac1a7a4b36ff7e02792`.
- Arming workflow commit `0a07b393bb47123a1142fd46ea6d9a55b04f0486`; run `33998283085`, job `101392517265`, conclusion FAILURE.
- Fresh Preview `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, URL `https://dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`, Preview/Ready; no production promotion.
- Aggregate artifact `9978732479`, digest `sha256:e245ae0a89d9c174ce1da14e47c31b252ad516b601d7793b2d982489efc16aa6`: client `modelBearingStartRequestCount=1`, `startStatus=401`, `startAccepted=false`, no signed token/poll/ACK, production/reference fields unchanged.
- Model-free routing diagnostics later proved that direct protected POST was rejected before Next.js. Therefore the real-audio client request never reached app, Modal bridge, orchestrator, worker, or model.
- **Backend/model start count from run `33998283085` = 0.** Client real-audio POST count = 1. Do not rerun that workflow attempt.

## DIRECT GITHUB OIDC ACCESS — NOT ACCEPTED BY VERCEL PROTECTION

- Redirect diagnostic `33998609205`: no-redirect GET `/ai-tab` = 302 to `vercel.com`; malformed POST = 401.
- Earlier redirect-followed 200 interpretations are withdrawn as app-access proof. GitHub OIDC mint/refresh mechanics are proven, but that identity is not trusted for this Preview.
- Do not use the direct `x-vercel-trusted-oidc-idp-token` request path for the next E2E.

## AUTHENTICATED `vercel curl` PROTECTED REQUEST TRANSPORT — GREEN

- Corrected model-free diagnostic commit `3d3a5ece92c0e5937b93682cff5dc101f7212f01`, run `33998720454`, job `101393652639` — SUCCESS.
- Exact protected Preview malformed POST returned HTTP 400 + Next route validation error; no audio/model call possible.
- `vercel curl --deployment <exact-preview-url>` is therefore the approved protected request transport. It requires no Deployment Protection weakening/disablement, bypass secret, or production promotion.

## LOCAL `vercel pull` ENV — INCOMPLETE BUT NOT RUNTIME-AUTHORITATIVE

- Run `33998800056` classified local pulled Preview env without printing values:
  - `ANALYZER_API_URL_V143=sensitive_placeholder`
  - `ANALYZER_API_TOKEN=missing`
  - `BLOB_READ_WRITE_TOKEN=missing`.
- This is only a local materialization limitation. Do not use local `vercel build --prebuilt` as evidence for runtime env absence.
- Connected Vercel project metadata exposes no env-key/scope list, so runtime was tested model-free instead.

## DEPLOYED PREVIEW RUNTIME CONFIG — ALL THREE CRITICAL VALUES GREEN, MODEL-FREE

### V143 URL + analyzer token

- Diagnostic commit `fe608775454b532c65a4336fc426d82545abd464`; run `33999203347`, job `101394927457`.
- Fake-token `operation=status`, Rhythm, no audio/start operation returned HTTP **400**, class `route_config_gate_passed_or_bridge_response`.
- Route would return 503 before bridge if selected V143 URL or analyzer token were absent; bridge would return 401 if analyzer-token authorization mismatched. Observed 400 proves selected URL/token config passed and fake job token failed later at bridge parsing.
- Safety: model starts 0, no audio, no start operation, worker spawn impossible, reference inputs 0.

### Blob token

- Diagnostic commit `9776de2b2a55c93d7b996c91804befb1a6d0c6a1`; run `33999276060`, job `101395123695`.
- Authenticated malformed POST and fake-token status probe both re-passed.
- Exactly one fail-fast config request used `operation=start` but `audioUrl=INVALID-NO-AUDIO`, nonempty text fields, Rhythm. No real/Blob audio URL was supplied.
- Result: HTTP **400**, exact class `all_route_runtime_config_present_bridge_fail_fast_green`, with bridge validation error `A valid audioUrl is required.`
- This proves route config passed **including `BLOB_READ_WRITE_TOKEN`**, selected V143 URL/token were usable, and request reached the hardened bridge.
- `_start_rhythm_job` authorizes and validates URL before job ID creation / FunctionCall spawn. Observed invalid-URL rejection therefore proves `jobIdCreated=false`, `workerSpawnPossible=false`, `audioRead=false`, `modelBearingStartRequestCount=0`, `referenceFacingInputs=0`, no secret values printed.
- Overall diagnostic workflow conclusion remains expected FAILURE only because the local-pull classifier intentionally stays red; model-free runtime steps themselves were SUCCESS.

## BREAKTHROUGH BLOCKER STATUS

- Protected request transport: **GREEN via authenticated `vercel curl`**.
- Existing fresh Preview: **GREEN / Ready / exact source deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`**.
- V143 runtime URL: **GREEN**.
- Analyzer token + bridge auth: **GREEN**.
- Blob token runtime presence: **GREEN**.
- Async lifecycle/ACK: **GREEN**.
- Proven backend/model start count so far: **0**.
- The remaining work is workflow transport/build strategy only; no model/runtime/scheduler change is indicated.

## NEXT — DESIGN ONE SAFE EXISTING-PREVIEW BREAKTHROUGH ATTEMPT

1. **Do not rebuild locally.** Reuse exact existing fresh Preview `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD` / `dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`, whose protected transport and runtime config were just proven model-free.
2. Stage a new/updated helper script in a non-triggering commit first. It must use authenticated `vercel curl --deployment "$PREVIEW_URL"` for preflight, the one real-audio start, every same-token status poll, and one terminal ACK.
3. Pin/inspect the exact existing Preview before the start; require Ready/Preview and the expected deployment ID/source lineage. No `vercel build`, `vercel deploy`, `--prod`, alias/promotion, or protection change.
4. Preserve exactly one **backend-capable real-audio start budget** for the repaired attempt. Historical backend/model starts remain 0; the prior client audio POST was blocked before application.
5. Require HTTP 202 + signed `v143a1.*` token; after a usable token exists, never send another start. Poll same token only.
6. On terminal completed **or failed**, produce aggregate pre-ACK evidence, ACK exactly once, require result cleanup, write final aggregate evidence, then fail after cleanup if terminal/product/runtime contract is not green.
7. On ambiguous start response after the real-audio POST, STOP with no second start because it may have reached backend.
8. Delete raw start/status/ACK bodies and job token on runner `if: always()`; upload aggregate summary only.
9. Recheck no active breakthrough run, source pins, existing Preview identity, and helper blob before editing the breakthrough workflow. The breakthrough workflow edit is the one arming event.
10. Checkpoint the staged helper and final pre-arm state before arming.

## HARD STOPS

- **DO NOT RERUN `33998283085`; do not send any ad-hoc real-audio start; do not edit the breakthrough trigger until helper + final pre-arm checks are checkpointed.**
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change for access/lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **all model-free protected transport/runtime config gates GREEN on the existing pinned fresh Preview; backend/model start count remains 0; next permitted work is non-triggering helper staging for a single existing-Preview authenticated-`vercel curl` breakthrough attempt, then checkpoint + final pre-arm validation before one workflow arming edit.**
