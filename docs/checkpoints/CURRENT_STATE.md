# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — protected Preview POST itself returns 401; single model-bearing POST never reached Next/Modal; zero worker/model spawn proven  
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

## HISTORICAL BREAKTHROUGH RUN — PRE-MODEL ONLY

- Historical trigger commit `58be9aa7b5606783a508917ce4531cfd512d66da` produced run `33982235357`, job `101349393362`.
- Source gate and fresh Preview deploy were GREEN; protected `/ai-tab` preflight returned **403**; model-bearing step was **SKIPPED**.
- Historical Preview deployment: `dpl_F6ksguDvc1nVAt33jNxxoVTmyyJA`; no production promotion. Do not rerun it.

## PROTECTED PREVIEW GET ACCESS — GREEN

- Trusted GitHub OIDC proof `33982502347` returned protected Preview GET HTTP 200 using `x-vercel-trusted-oidc-idp-token` without weakening Deployment Protection.
- Refreshability proof `33982582372` GREEN; on-demand JWT TTL = **300s**.
- Armed workflow grants `id-token: write`, mints/masks fresh JWTs, and uses direct `curl` against the exact protected Preview. Vercel CLI is build/deploy/inspect only. No production target/promotion command was added.

## GUARDED HELPER / ARMED WORKFLOW

- Helper `.github/scripts/v143-fresh-preview-async-breakthrough-e2e.sh` commit `8d536121bb9a38f4a69add31cbf7515400441c5b`, blob `92d17ee0b01ff72f71abfac1a7a4b36ff7e02792`; exact bytes passed `bash -n` before staging.
- Single arming workflow commit: `0a07b393bb47123a1142fd46ea6d9a55b04f0486`, message `test: arm guarded OIDC async breakthrough E2E`.
- Armed workflow blob: `2a48af6aadda3b90a9c9ea24220ac524dbcb5b41`.
- Trigger remains workflow-path-only push on `v143-contextual-prune-lobo`; concurrency remains `v143-fresh-preview-async-breakthrough-e2e-single`, `cancel-in-progress: false`.
- Final pre-arm active-state check was clean and all authoritative source/helper pins passed before any Preview/start work.

## SINGLE ARMED RUN — CLIENT START REQUEST BLOCKED BEFORE APPLICATION

- Exactly one breakthrough run was created from the arming commit: run `33998283085`, job `101392517265`, conclusion **FAILURE**.
- Fresh Preview deployment: `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, URL `https://dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`, Preview/Ready.
- Production promotion remained false; no `--prod` or promotion command executed.
- Protected Preview `/ai-tab` GET preflight succeeded: **HTTP 200**.
- The helper then sent exactly one Rhythm `operation=start` POST using approved audio + freshly minted trusted GitHub OIDC token.
- Aggregate artifact `9978732479`, digest `sha256:e245ae0a89d9c174ce1da14e47c31b252ad516b601d7793b2d982489efc16aa6`, retained:
  - `modelBearingStartRequestCount=1`
  - `startStatus=401`
  - `startCurlExitCode=0`
  - `startAccepted=false`
  - `terminalState=start-response-unusable`
  - `completed=false`
  - `acknowledged=false`
  - `productionEnvironmentChanged=false`
  - `productionPromotionPerformed=false`
  - `deploymentProtectionDisabled=false`
  - `referenceFacingInputs=0`
  - `referenceScoreCalls=0`
  - `qualityVerdictMade=false`.
- No signed `v143a1.*` token returned; no status poll/ACK was attempted. Runner raw request/response/token/status/ACK material was deleted.

## MODEL-FREE POST DISAMBIGUATION — DECISIVE

- Separate diagnostic workflow `.github/workflows/v143-protected-preview-post-routing-diagnosis.yml` commit `af2cb47b42a085607ed32b4338ee73e45d978558` was created solely to test the same protected Preview POST transport.
- Diagnostic run `33998553314`, job `101393220397`.
- Request body was only `{"transcriptionType":"invalid"}` — **no audio URL, no usable operation, no analyzer/model request**. The Next route would return its fixed HTTP 400 validation response before analyzer selection/call if the request reached application code.
- The diagnostic instead returned **HTTP 401** before that expected route-level 400.
- Therefore the protected Preview POST request is being rejected **before the Next.js route executes**. This removes the earlier Modal-token-mismatch hypothesis for the breakthrough start.
- Consequently the single model-bearing POST from run `33998283085` also stopped at the same protected-Preview POST boundary and **never reached `/api/analyze-audio-tab` application code**.
- Since the application route never executed, it could not call the Modal bridge; `_start_rhythm_job` was never reached; no job ID/control record/orchestrator/worker/model execution could have been spawned by this start.
- **Proven backend model-bearing execution count for the armed run = 0.** The client start-request budget was used once, but the model/backend-start budget remains unused.
- Model-free diagnostic itself: audio bytes 0, analyzer calls 0, worker/model calls 0, reference-facing inputs 0.

## CURRENT ROOT CAUSE — PROTECTED PREVIEW POST AUTHORIZATION

- Trusted GitHub OIDC access is proven for protected GET requests, but direct POST requests carrying a fresh `x-vercel-trusted-oidc-idp-token` currently return 401 before application routing.
- The prior local-prebuild `[SENSITIVE]` secret warning is **not the cause of this 401**, because the malformed diagnostic never reached application code or any environment-variable-dependent analyzer path. Keep that warning noted separately for future prebuilt-runtime verification, but do not conflate it with this blocker.
- Vercel runtime-log queries showing no function invocation are now consistent with the route-not-reached diagnosis, though the decisive evidence is the malformed POST returning 401 instead of the route's deterministic 400.

## HARD STOP / AUTHORIZATION

- **DO NOT RERUN `33998283085`; DO NOT send another model-bearing start yet; DO NOT edit the breakthrough trigger to arm again.**
- Zero backend/model execution is now proven, but the one-start client contract must still be explicitly reconsidered only after the protected-POST access method is fixed and proven model-free.
- No production promotion/change, no protection weakening/disablement, no reference-facing scoring, no scheduler/model changes.

## NEXT — FIX/PROVE PROTECTED POST ACCESS WITHOUT AUDIO

1. Determine the correct Vercel Trusted GitHub OIDC request semantics for non-GET methods. Investigate redirects/cookies/header handling and documented automated-agent access without weakening Deployment Protection.
2. Use only malformed/model-free POST probes until the same protected Preview endpoint returns the route's expected HTTP 400. No audio, bridge, or model call during this proof.
3. Prefer a request mode that preserves trusted auth across any Vercel redirect/cookie exchange; do not expose/store OIDC JWTs.
4. Once model-free POST access is GREEN, separately verify the prebuilt Preview has required analyzer configuration by presence/equality-safe checks that do not print secrets and do not call the model.
5. Checkpoint the exact repair and proof. Only then decide whether a second client start can be explicitly authorized given that the first provably never crossed the application boundary.

## HARD STOPS

- No second model-bearing POST until model-free protected POST access is GREEN and checkpoint authorization is revisited.
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement.
- No scheduler/model change for access/lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **single client start POST returned 401 at Vercel protection before Next.js; zero Modal/worker/model execution proven; protected GET OIDC works but protected POST OIDC path is blocked; no second model-bearing request authorized until model-free POST access is repaired and re-proven.**
