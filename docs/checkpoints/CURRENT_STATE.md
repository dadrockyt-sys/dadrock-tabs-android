# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — authenticated `vercel curl` protected POST GREEN; pulled Preview env incomplete; Vercel metadata exposes no env-key listing; model-free runtime config probe authorized next  
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

## PREVIEW ENV CLASSIFICATION — LOCAL PULL INCOMPLETE

- Rhythm `start` requires `ANALYZER_API_URL_V143`, `ANALYZER_API_TOKEN`, and `BLOB_READ_WRITE_TOKEN` before bridge call.
- Model-free classification commit `a824ef08137540b42fce51ff9fa462974f34aeb2`, run `33998800056`, job `101393870080`.
- Authenticated malformed POST was re-proven HTTP 400 / route reached / model starts 0.
- `vercel pull --environment=preview --git-branch=v143-contextual-prune-lobo` classified without printing values:
  - `ANALYZER_API_URL_V143 = sensitive_placeholder`
  - `ANALYZER_API_TOKEN = missing`
  - `BLOB_READ_WRITE_TOKEN = missing`
  - `secretValuesPrinted=false`, `modelBearingStartRequestCount=0`, `audioUrlSupplied=false`, `analyzerCallPossible=false`.
- `.vercel` was deleted in `always()` cleanup.
- This proves only that the **locally pulled Preview env used for a prebuilt build is incomplete/unsafe**. It does not prove Vercel-managed cloud runtime env lacks those values.
- No further local `vercel build --prebuilt` model-bearing attempt is authorized.

## VERCEL METADATA INSPECTION — ENV-KEY METADATA UNAVAILABLE THROUGH CONNECTED APP

- Connected Vercel project read confirms project `prj_6biwsn0iHci6FHNswAUCS8UYrAqF`, team `team_qJrw8Cuze5bCEg9M3Q67XMWt`, framework Next.js, Node 24.x, and latest deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD` READY.
- The connected project/deployment interface does not expose an environment-variable key listing or scopes, so the preferred metadata-only distinction cannot be completed through this connection without retrieving values.
- Do not infer absence from that limitation.

## NEXT — MODEL-FREE RUNTIME CONFIG PROBE

1. Extend the existing diagnostic workflow `.github/workflows/v143-protected-preview-post-routing-diagnosis.yml` only; do not touch the breakthrough trigger.
2. Use authenticated `vercel curl` against the exact existing Preview and POST `operation=status`, `transcriptionType=rhythm`, and a deliberately fake nonempty `jobToken`.
3. Supply **no audio URL/path/song/artist**, so `needsAudioRequest=false`; this operation cannot create/spawn a job or execute the model.
4. Interpret strictly:
   - HTTP 503 + `The audio analyzer is not configured.` => Vercel runtime lacks selected V143 URL and/or analyzer token.
   - Any bridge-origin response (for example invalid/unauthorized fake token) => route runtime config passed and bridge was reached; still zero model start because `status` never spawns.
5. Record status/error class only; no secrets/values. Keep `modelBearingStartRequestCount=0`, `audioUrlSupplied=false`, `analyzerStartOperationSent=false`, `referenceFacingInputs=0`.
6. If existing prebuilt Preview runtime config is missing, next investigate a **cloud source build/deploy** model-free Preview because Vercel-managed cloud builds may receive sensitive runtime env that `vercel pull` cannot materialize.
7. Checkpoint the exact result before any further deployment/workflow design.

## HARD STOPS

- **DO NOT RERUN `33998283085`; DO NOT send another model-bearing start; DO NOT edit the breakthrough trigger to arm again yet.**
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change for access/lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **authenticated protected POST transport GREEN; direct GitHub OIDC trust path not green; locally pulled Preview env incomplete; Vercel metadata cannot expose env-key scopes; first audio POST caused zero backend/model execution; next permitted action is the model-free fake-token status probe only.**
