# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — existing-Preview guarded runner staged and pinned; Preview source lineage verified; final pre-arm audit next  
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

- Old helper `.github/scripts/v143-fresh-preview-async-breakthrough-e2e.sh` commit `8d536121bb9a38f4a69add31cbf7515400441c5b`, blob `92d17ee0b01ff72f71abfac1a7a4b36ff7e02792`.
- Arming workflow commit `0a07b393bb47123a1142fd46ea6d9a55b04f0486`; run `33998283085`, job `101392517265`, conclusion FAILURE.
- Fresh Preview `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, URL `https://dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`, Preview/Ready; no production promotion.
- Aggregate artifact `9978732479`, digest `sha256:e245ae0a89d9c174ce1da14e47c31b252ad516b601d7793b2d982489efc16aa6`: client real-audio request count 1, start HTTP 401 before application, no signed token/poll/ACK.
- Model-free routing diagnostics proved the real-audio client POST never reached Next.js, Modal bridge, orchestrator, worker, or model.
- **Backend/model start count remains 0.** Do not rerun `33998283085`.

## PROTECTED TRANSPORT / RUNTIME CONFIG — GREEN MODEL-FREE

- Direct GitHub OIDC request path is NOT accepted by Vercel Deployment Protection; do not use it.
- Authenticated `vercel curl --deployment <exact-preview-url>` is GREEN: model-free malformed POST reached Next route with HTTP 400 (`33998720454`).
- Local `vercel pull` remains incomplete and is not runtime-authoritative (`33998800056`). No local prebuilt model-bearing attempt is authorized.
- Fake-token status probe (`33999203347`) returned HTTP 400 past the route config gate and bridge authorization, proving deployed V143 URL/analyzer token path GREEN with zero model start.
- Invalid-audio fail-fast `start` probe (`33999276060`) returned exact bridge HTTP 400 `A valid audioUrl is required.` before job ID/FunctionCall spawn, proving deployed Blob token presence too. Outputs explicitly preserved `audioRead=false`, `jobIdCreated=false`, `workerSpawnPossible=false`, `modelBearingStartRequestCount=0`, reference inputs 0.
- All three deployed runtime values required by a real Rhythm start are therefore GREEN: `ANALYZER_API_URL_V143`, `ANALYZER_API_TOKEN`, `BLOB_READ_WRITE_TOKEN`.

## EXISTING PINNED PREVIEW — IDENTITY / SOURCE LINEAGE VERIFIED

- Deployment: `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`.
- URL: `dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`.
- Connected Vercel deployment read: state/readyState **READY**, source `cli`, project `prj_6biwsn0iHci6FHNswAUCS8UYrAqF`.
- Vercel deployment metadata pins GitHub ref `v143-contextual-prune-lobo` and exact source commit `0a07b393bb47123a1142fd46ea6d9a55b04f0486` with commit message `test: arm guarded OIDC async breakthrough E2E`.
- No rebuild is required or permitted for the repaired attempt; use this exact existing Preview only.

## SAFE STAGING MILESTONE — EXISTING-PREVIEW RUNNER COMMITTED WITHOUT ARMING

- New helper: `.github/scripts/v143-existing-preview-async-breakthrough-e2e.sh`.
- Commit: `ecbc96793d2f21582ddb5df77163d8a54cee64f0`.
- Git blob: `d72faac8c531b6572dc3ce1d2f5ec0f5e1317626`.
- The fetched GitHub blob exactly matches the locally computed blob; local bytes passed `bash -n` before commit.
- This helper-file commit cannot trigger the breakthrough workflow because that workflow watches only `.github/workflows/v143-fresh-preview-async-breakthrough-e2e.yml`.
- Helper performs no build/deploy/alias/promotion/protection change. It pins source blobs, inspects the exact Preview ID/Ready/Preview state, preflights through authenticated `vercel curl`, sends exactly one backend-capable approved real-audio Rhythm start, then same-token status polling only.
- If the single real-audio POST is ambiguous or does not return HTTP 202 + signed `v143a1.*` token, helper records aggregate state and **stops with no second start**.
- After a usable signed token exists, terminal completed or failed state is summarized, then ACK is sent exactly once with the same token; cleanup is required before any terminal/product/runtime failure is raised.
- Poll deadline also stops without another start. No production/reference-facing operation is added.
- Raw start/status/ACK bodies and the job token are runner-only and must be deleted by workflow `if: always()`; only aggregate `summary.json` may be uploaded.

## FINAL PRE-ARM AUDIT — NEXT

Before touching the breakthrough workflow YAML:

1. Recheck no active/in-progress/queued/waiting/requested/pending **breakthrough** run exists; do not confuse unrelated cleanup/diagnostic workflows with the breakthrough concurrency gate.
2. Re-fetch route/page/bridge/protocol/worker/scheduler/audio blobs and require the seven authoritative pins above.
3. Re-fetch helper and require blob `d72faac8c531b6572dc3ce1d2f5ec0f5e1317626`.
4. Re-read existing Preview deployment metadata and require `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, READY, branch `v143-contextual-prune-lobo`, source commit `0a07b393bb47123a1142fd46ea6d9a55b04f0486`.
5. Re-read breakthrough trigger/concurrency guard. Preserve single group with `cancel-in-progress: false`.
6. Checkpoint final clean pre-arm state before editing the workflow.
7. Make exactly one breakthrough workflow edit. That push is the single repaired arming event. The workflow must use the existing Preview helper/blob, authenticated `vercel curl`, and contain **no build/deploy/prod/promotion/OIDC path**.
8. Watch only the resulting run. If a real start reaches backend and later fails, require ACK/evidence then STOP. No rerun / no second model-bearing start.

## HARD STOPS

- **DO NOT RERUN `33998283085`; do not send any ad-hoc real-audio start; do not edit the breakthrough trigger until the final pre-arm audit is checkpointed.**
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change for access/lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **model-free transport/runtime gates GREEN; existing Preview identity/source lineage GREEN; backend/model start count 0; existing-Preview guarded helper staged at pinned blob `d72faac8...` without arming; next permitted action is final pre-arm validation + checkpoint, followed by exactly one breakthrough workflow arming edit if still clean.**
