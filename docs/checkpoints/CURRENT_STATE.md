# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — authenticated `vercel curl` protected POST GREEN; pulled Preview env classifies V143 URL as sensitive placeholder and analyzer/blob tokens missing; zero model spawn preserved  
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
- Aggregate artifact `9978732479`, digest `sha256:e245ae0a89d9c174ce1da14e47c31b252ad516b601d7793b2d982489efc16aa6`: `modelBearingStartRequestCount=1`, `startStatus=401`, `startCurlExitCode=0`, `startAccepted=false`, no signed token/poll/ACK, production/reference fields unchanged.
- Model-free malformed POST run `33998553314` proved the same direct protected-Preview POST path returns 401 before Next.js, so the audio POST never reached the application, Modal bridge, orchestrator, worker, or model.
- **Proven backend/model start count from run `33998283085` = 0.** Client POST count = 1.

## IMPORTANT CORRECTION — DIRECT GITHUB OIDC ACCESS NOT GREEN

- Redirect diagnostic run `33998609205`, job `101393363970`: no-redirect GET `/ai-tab` = HTTP 302 to `vercel.com`; malformed POST = HTTP 401.
- Earlier redirect-followed `200` interpretations in `33982502347`, `33982582372`, and the breakthrough preflight are withdrawn as application-access proofs. GitHub OIDC mint/refresh mechanics are proven, but Vercel does not accept that identity as trusted for this Preview.
- Do not use direct trusted-OIDC curl for the next E2E unless Vercel trust configuration is separately repaired/proven.

## AUTHENTICATED `vercel curl` PROTECTED POST — GREEN

- First CLI diagnostic `33998673175` / job `101393529937` made no HTTP request because `--token` was forwarded to native curl; syntax-only failure.
- Corrected diagnostic commit `3d3a5ece92c0e5937b93682cff5dc101f7212f01`, run `33998720454`, job `101393652639` — SUCCESS.
- Exact model-free proof against the existing protected Preview:
  - malformed POST status = **HTTP 400**
  - exact route error = `Transcription type must be lead, rhythm, or bass.`
  - `nextRouteReached=true`
  - `analyzerCallPossible=false`
  - `modelBearingStartRequestCount=0`
  - `audioUrlSupplied=false`
  - `referenceFacingInputs=0`.
- Therefore authenticated `vercel curl --deployment <exact-preview-url>` is a valid protected request transport without weakening/disablement, bypass-secret creation, production promotion, or model execution.
- Candidate E2E transport repair remains: authenticated `vercel curl` for preflight/start/status/ACK instead of direct GitHub-OIDC curl. **Do not arm yet.**

## PREVIEW ENV CLASSIFICATION — MODEL-FREE BLOCKERS CONFIRMED

- Pinned route requires, for a Rhythm `start`, these three critical Preview runtime values before any bridge call:
  - `ANALYZER_API_URL_V143`
  - `ANALYZER_API_TOKEN`
  - `BLOB_READ_WRITE_TOKEN`.
- Model-free classification workflow commit `a824ef08137540b42fce51ff9fa462974f34aeb2`, run `33998800056`, job `101393870080`.
- The run first re-proved protected POST transport GREEN: malformed POST HTTP 400, route reached, analyzer call impossible, audio supplied false, model starts 0.
- `vercel pull --environment=preview --git-branch=v143-contextual-prune-lobo` then emitted exactly one unpullable Secret warning and classifications only; no secret value was printed:
  - `ANALYZER_API_URL_V143 = sensitive_placeholder`
  - `ANALYZER_API_TOKEN = missing`
  - `BLOB_READ_WRITE_TOKEN = missing`
  - `secretValuesPrinted=false`
  - `modelBearingStartRequestCount=0`
  - `audioUrlSupplied=false`
  - `analyzerCallPossible=false`.
- `.vercel` was deleted in the `always()` cleanup step.
- Interpretation is deliberately limited: this proves the **locally pulled Preview env used by a prebuilt build is unsafe/incomplete** for the V143 Rhythm start path. It does **not yet prove** the two missing keys are absent from Vercel-managed runtime env on a cloud-built Preview; they may be unavailable to `vercel pull` due to scoping/secret handling.
- Therefore no further `vercel build --prebuilt` model-bearing attempt is authorized.

## NEXT — DISTINGUISH LOCAL-PULL LIMITATION FROM VERCEL RUNTIME CONFIG

1. Inspect Vercel project/environment metadata for the three critical key names/scopes without retrieving/printing values.
2. Use a model-free runtime probe if needed: a `status` operation with a fake nonempty job token can safely test whether Rhythm analyzer URL/token configuration reaches the route's config gate; it carries no audio and cannot start a worker/model. Prefer metadata inspection first.
3. Determine whether a **cloud source build/deploy** (rather than local `--prebuilt`) preserves Vercel-managed sensitive Preview runtime env. Any fresh Preview proof must remain model-free and use authenticated `vercel curl`.
4. Checkpoint the exact cloud-build/config proof and only then design the breakthrough workflow repair.
5. Only after transport + runtime config are GREEN explicitly reconsider a second client POST, noting the first client POST provably caused zero backend/model starts.

## HARD STOPS

- **DO NOT RERUN `33998283085`; DO NOT send another model-bearing start; DO NOT edit the breakthrough trigger to arm again yet.**
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change for access/lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **authenticated protected POST transport GREEN; direct GitHub OIDC trust path not green; locally pulled Preview env is incomplete for V143 start; first audio POST caused zero backend/model execution; no second model-bearing request authorized pending Vercel-managed runtime config/cloud-build proof.**
