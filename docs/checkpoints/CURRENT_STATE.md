# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — protected `vercel curl` transport GREEN; deployed Preview V143 URL/token runtime gate GREEN; Blob runtime presence remains to prove model-free  
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

## SINGLE ARMED RUN — CLIENT POST BLOCKED BEFORE APPLICATION / ZERO BACKEND STARTS

- Helper `.github/scripts/v143-fresh-preview-async-breakthrough-e2e.sh` commit `8d536121bb9a38f4a69add31cbf7515400441c5b`, blob `92d17ee0b01ff72f71abfac1a7a4b36ff7e02792`.
- Single arming workflow commit `0a07b393bb47123a1142fd46ea6d9a55b04f0486`; run `33998283085`, job `101392517265`, conclusion FAILURE.
- Fresh Preview `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, URL `https://dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`, Preview/Ready; no production promotion.
- Aggregate artifact `9978732479`, digest `sha256:e245ae0a89d9c174ce1da14e47c31b252ad516b601d7793b2d982489efc16aa6`: client `modelBearingStartRequestCount=1`, `startStatus=401`, `startCurlExitCode=0`, `startAccepted=false`, no signed token/poll/ACK, production/reference fields unchanged.
- Subsequent model-free routing diagnostics proved the direct protected-Preview POST 401 occurred before Next.js; therefore the audio POST never reached application, Modal bridge, orchestrator, worker, or model.
- **Proven backend/model start count from run `33998283085` = 0.** Client audio POST count = 1. Do not rerun it.

## IMPORTANT CORRECTION — DIRECT GITHUB OIDC ACCESS NOT GREEN

- Redirect diagnostic run `33998609205`, job `101393363970`: no-redirect GET `/ai-tab` = HTTP 302 to `vercel.com`; malformed POST = HTTP 401.
- Earlier redirect-followed `200` interpretations in `33982502347`, `33982582372`, and the breakthrough preflight are withdrawn as application-access proofs. GitHub OIDC mint/refresh mechanics are proven, but Vercel does not accept that identity as trusted for this Preview.
- Do not use direct trusted-OIDC curl for the next E2E unless Vercel trust configuration is separately repaired/proven.

## AUTHENTICATED `vercel curl` PROTECTED POST — GREEN

- Corrected diagnostic commit `3d3a5ece92c0e5937b93682cff5dc101f7212f01`, run `33998720454`, job `101393652639` — SUCCESS.
- Model-free malformed POST against the exact protected Preview returned HTTP **400** with exact route error `Transcription type must be lead, rhythm, or bass.`
- Proven: `nextRouteReached=true`, `analyzerCallPossible=false`, `modelBearingStartRequestCount=0`, `audioUrlSupplied=false`, `referenceFacingInputs=0`.
- Therefore authenticated `vercel curl --deployment <exact-preview-url>` is the correct protected request transport without weakening protection, bypass-secret creation, production promotion, or model execution.

## PREVIEW ENV CLASSIFICATION — LOCAL PULL INCOMPLETE, DEPLOYED RUNTIME PARTLY GREEN

- Rhythm `start` route config requires `ANALYZER_API_URL_V143`, `ANALYZER_API_TOKEN`, and `BLOB_READ_WRITE_TOKEN`.
- Local-pull classification commit `a824ef08137540b42fce51ff9fa462974f34aeb2`, run `33998800056`, job `101393870080`: `ANALYZER_API_URL_V143=sensitive_placeholder`, `ANALYZER_API_TOKEN=missing`, `BLOB_READ_WRITE_TOKEN=missing`, no values printed. This proves only local materialization is incomplete.
- Connected Vercel project metadata confirms the correct project/team/latest Preview but exposes no env-key/scope listing; absence cannot be inferred.

### Model-free deployed runtime probe — V143 URL + analyzer token GREEN

- Diagnostic commit `fe608775454b532c65a4336fc426d82545abd464` updated only `.github/workflows/v143-protected-preview-post-routing-diagnosis.yml`; breakthrough workflow untouched.
- Run `33999203347`, job `101394927457` completed expected overall FAILURE only because the later local-pull classifier intentionally remains red.
- Authenticated malformed POST re-proved route transport HTTP 400.
- Fake-token request used `operation=status`, `transcriptionType=rhythm`, fake nonempty `jobToken`, **no audio**, and no start operation.
- Runtime probe returned HTTP **400**, class `route_config_gate_passed_or_bridge_response`.
- Because the route returns 503 before bridge fetch when selected V143 URL or analyzer token is absent, HTTP 400 proves the deployed Preview has nonempty selected V143 URL + analyzer token and reached the bridge.
- The bridge returns 401 on analyzer-token authorization mismatch; the observed 400 therefore also strongly indicates the deployed analyzer token passed bridge authorization and the fake job token failed later in bounded token parsing.
- Safety outputs: `modelBearingStartRequestCount=0`, `audioUrlSupplied=false`, `analyzerStartOperationSent=false`, `workerSpawnPossible=false`, `referenceFacingInputs=0`, `secretValuesPrinted=false`.
- **No worker/model start occurred.**

## REMAINING CONFIG QUESTION — BLOB TOKEN ONLY

- The status probe intentionally does not require `BLOB_READ_WRITE_TOKEN`, so deployed runtime Blob-token presence is still unproven.
- A safe fail-fast probe can test it without audio/model execution using the already-established production one-shot pattern: authenticated `vercel curl`, `operation=start`, all required text fields present, but `audioUrl=INVALID-NO-AUDIO` (not `http://` or `https://`).
- Route behavior: if Blob token is absent, fail at route config gate with HTTP 503. If Blob token is present, request reaches the hardened bridge; `_start_rhythm_job` authorizes then `_validate_rhythm_start_payload` rejects the invalid URL **before job ID creation / FunctionCall spawn / worker/model execution**, returning bounded HTTP 400.
- This is a **model-free fail-fast config probe**, not a model-bearing start. It must use no real audio URL and retain `audioRead=false`, `workerSpawnPossible=false`, `modelBearingStartRequestCount=0`, `referenceFacingInputs=0`.

## NEXT — ONE MODEL-FREE BLOB RUNTIME PROBE ONLY

1. Extend only `.github/workflows/v143-protected-preview-post-routing-diagnosis.yml`; do not touch/rearm the breakthrough workflow.
2. Re-prove malformed authenticated POST transport first.
3. Preserve the fake-token status probe.
4. Add exactly one fail-fast `operation=start` using `audioUrl=INVALID-NO-AUDIO`, nonempty pathname/song/artist, Rhythm type; do not use approved/real audio or any Blob URL.
5. Require either:
   - HTTP 503 => deployed runtime Blob token/config missing; stop and diagnose cloud runtime configuration.
   - HTTP 400 from bridge invalid-audio validation => all three critical runtime values are available and bridge auth is usable; worker/model spawn remains zero.
6. Print classifications only; delete response; no secrets.
7. Checkpoint result before considering any repair to breakthrough transport/build strategy.

## HARD STOPS

- **DO NOT RERUN `33998283085`; DO NOT send another model-bearing start; DO NOT edit the breakthrough trigger to arm again yet.**
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change for access/lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **authenticated protected POST transport GREEN; direct GitHub OIDC trust path not green; deployed Preview V143 URL/analyzer-token path GREEN via model-free bridge probe; local pull incomplete; Blob runtime token remains the only config question; next permitted action is one invalid-audio fail-fast start probe with guaranteed pre-spawn bridge rejection.**
