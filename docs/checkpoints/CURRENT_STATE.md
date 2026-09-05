# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — GitHub OIDC direct access NOT trusted; prior GET 200 was redirect false-positive; zero model spawn still proven  
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
- Source gate and fresh Preview deploy were GREEN; protected `/ai-tab` check failed before model start. Do not rerun it.
- Historical Preview deployment: `dpl_F6ksguDvc1nVAt33jNxxoVTmyyJA`; no production promotion.

## GUARDED HELPER / SINGLE ARMED RUN

- Helper `.github/scripts/v143-fresh-preview-async-breakthrough-e2e.sh` commit `8d536121bb9a38f4a69add31cbf7515400441c5b`, blob `92d17ee0b01ff72f71abfac1a7a4b36ff7e02792`.
- Single arming workflow commit: `0a07b393bb47123a1142fd46ea6d9a55b04f0486`; armed workflow blob `2a48af6aadda3b90a9c9ea24220ac524dbcb5b41`.
- Exactly one breakthrough run from that arming commit: run `33998283085`, job `101392517265`, conclusion FAILURE.
- Fresh Preview deployment: `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, URL `https://dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`, Preview/Ready.
- Production promotion remained false; no `--prod` or promotion command executed.
- Aggregate artifact `9978732479`, digest `sha256:e245ae0a89d9c174ce1da14e47c31b252ad516b601d7793b2d982489efc16aa6`, retained `modelBearingStartRequestCount=1`, `startStatus=401`, `startCurlExitCode=0`, `startAccepted=false`, `completed=false`, `acknowledged=false`, `referenceFacingInputs=0`, `referenceScoreCalls=0`, `qualityVerdictMade=false`.
- No signed `v143a1.*` token returned; no status poll/ACK; raw request/response/token/status/ACK material deleted.

## MODEL-FREE POST DISAMBIGUATION — ZERO BACKEND/MODEL SPAWN PROVEN

- Diagnostic workflow `.github/workflows/v143-protected-preview-post-routing-diagnosis.yml`, first diagnostic commit `af2cb47b42a085607ed32b4338ee73e45d978558`, run `33998553314`, job `101393220397`.
- It POSTed only `{"transcriptionType":"invalid"}` — no audio URL and no usable analyzer/model request. If Next.js received it, route validation deterministically returns HTTP 400 before analyzer selection/call.
- It instead returned HTTP **401**.
- Therefore the breakthrough start's identical protected-Preview POST transport was blocked before Next.js. It never reached the application route, Modal bridge, `_start_rhythm_job`, FunctionCall spawn, worker, or model.
- **Proven backend model-bearing execution count for run `33998283085` = 0.** Client POST count = 1; backend/model-start count = 0.

## IMPORTANT CORRECTION — PRIOR OIDC “GET 200” PROOF WITHDRAWN

- Redirect-boundary diagnostic commit `da56e7242e0b7f643b68e1d25083d471f1f1eed2`, run `33998609205`, job `101393363970` compared trusted-OIDC GET and malformed POST **without following redirects**.
- Exact results:
  - GET `/ai-tab`: **HTTP 302**, `Location` present, destination host `vercel.com`.
  - malformed POST `/api/analyze-audio-tab`: **HTTP 401**, no `Location` header.
  - diagnostic model starts 0; audio supplied false; analyzer call possible false; reference-facing inputs 0.
- Earlier runs `33982502347` and `33982582372` used/finally interpreted redirect-followed HTTP 200. The new no-redirect evidence proves that final 200 was the Vercel authentication flow/page after a 302, **not successful application access**. Their conclusion “Trusted GitHub OIDC Deployment Protection access GREEN” is **withdrawn**; token mint/refresh mechanics remain proven, but Vercel acceptance does not.
- The breakthrough preflight also used `curl --location`; its reported `protectedPreviewAiTabStatus=200` was likewise a redirect false-positive, not proof the app was reached.
- Root cause now: the GitHub-issued OIDC JWT is currently **not accepted as a trusted Deployment Protection source for this project/deployment**. GET is redirected to Vercel auth; non-GET is rejected 401 before application routing.
- Vercel documentation confirms `x-vercel-trusted-oidc-idp-token` is the intended GitHub Actions header and is not documented as GET-only. Therefore this is trust/configuration/identity acceptance, not a POST-method limitation.

## SAFE ALTERNATIVE UNDER INVESTIGATION — AUTHENTICATED `vercel curl`

- Vercel documentation supports `vercel curl <path> --deployment <preview-url>` and native POST flags after `--`.
- This uses the existing authorized Vercel CLI token to access a specific protected Preview without disabling Deployment Protection, creating a protection bypass secret, promoting production, or exposing credentials.
- Next permitted test is **model-free only**: use `vercel curl` against the exact existing Preview with body `{"transcriptionType":"invalid"}` and require the route's deterministic HTTP 400 response. No audio/model/bridge request.
- If that succeeds, `vercel curl` becomes the candidate protected request transport for the E2E; do not send audio until all remaining configuration and one-start authorization gates are re-proven/checkpointed.

## PREBUILT SECRET WARNING — SEPARATE, NOT CURRENT 401 ROOT CAUSE

- Fresh local prebuild reported one sensitive Preview value could not be pulled and wrote `[SENSITIVE]` placeholder.
- That cannot explain the current 401 because the malformed POST never reached Next.js. Keep it as a separate blocker to verify after protected POST transport is solved, before any future model-bearing request.

## HARD STOPS

- **DO NOT RERUN `33998283085`; DO NOT send another model-bearing start; DO NOT edit the breakthrough trigger to arm again yet.**
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change for access/lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

## NEXT

1. Prove model-free malformed POST through authenticated `vercel curl` to exact Preview; require route HTTP 400 and exact validation error.
2. If GREEN, verify Preview analyzer configuration safely (presence/equality only; no secret values, no audio/model call), including the local-prebuild sensitive placeholder risk.
3. Checkpoint transport/config proof and proposed guarded workflow repair.
4. Only after all model-free gates are GREEN explicitly reconsider whether a second client POST is authorized, noting first client POST provably caused zero backend/model starts.

Current authorization state: **GitHub OIDC token mint/refresh works but Vercel does not trust it for this Preview; earlier redirect-followed 200 access conclusions are withdrawn; single audio POST was rejected before Next.js and caused zero Modal/worker/model execution; no second model-bearing request authorized.**
