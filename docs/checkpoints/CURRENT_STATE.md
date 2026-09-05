# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — FINAL PRE-ARM GREEN for one existing-Preview authenticated-`vercel curl` breakthrough attempt  
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

## AUTHORITATIVE SOURCE PINS — FINAL PRE-ARM REVERIFIED

- Production `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`; production deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`; synchronous route blob `06234db3e1cc1680b18fd62a765862b213ede3db`.
- Branch async route `742954146a86aa36485d0bbdb3fbd6691a64a712` — re-fetched exact.
- `/ai-tab` page `de39f2715c6875d757ef730c9e3182ccd4aa00a4` — re-fetched exact.
- Hardened bridge `36584355d9b060fc7b7e20acc62524fbc7bf9005` — re-fetched exact.
- Protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8` — re-fetched exact.
- V143 worker `111bf14a8f91045d3478901f8e36b88a2e7f181a` — re-fetched exact.
- Scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8` — re-fetched exact.
- Approved audio `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, blob `4dd709e3fa177b4daeed71ca97f0199757729d4b` — re-fetched exact.

## LIFECYCLE GATE — GREEN / DO NOT REOPEN WITHOUT NEW EVIDENCE

- Startup diagnosis `33985149949` / job `101357179709` SUCCESS with no model/audio/reference-facing invocation.
- Isolated async control proof `33985474511` / job `101358067142` SUCCESS; artifact `9975020241`, digest `sha256:b701ad58e32d538336f21279289bb189aca4324ec5029242d1f08246d4e1a493`.
- Proven: tracked start, deterministic terminal state, ACK clears result/control, TTL 900, no audio/model bytes in transient transport, reference-facing calls 0.

## FIRST ARMED RUN — CLIENT AUDIO POST BLOCKED BY PROTECTION / ZERO BACKEND STARTS

- Old arming workflow commit `0a07b393bb47123a1142fd46ea6d9a55b04f0486`; run `33998283085`, job `101392517265`, FAILURE.
- Fresh Preview produced there: `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, URL `dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`.
- Aggregate artifact `9978732479`, digest `sha256:e245ae0a89d9c174ce1da14e47c31b252ad516b601d7793b2d982489efc16aa6`: client real-audio POST count 1, HTTP 401 before application, no signed token/poll/ACK.
- Later model-free diagnostics proved this POST never reached Next.js/bridge/orchestrator/worker/model.
- **Proven backend/model start count remains 0.** Do not rerun `33998283085`.

## PROTECTED TRANSPORT / DEPLOYED RUNTIME — ALL MODEL-FREE GATES GREEN

- Direct GitHub OIDC access is not accepted by Vercel protection; do not use it.
- Authenticated `vercel curl --deployment <exact-preview-url>` reached the protected Next route model-free (`33998720454`).
- Local `vercel pull` is incomplete and not runtime-authoritative (`33998800056`); no local prebuilt model-bearing attempt is authorized.
- Fake-token status probe `33999203347` proved deployed V143 URL + analyzer token + bridge auth are usable, zero audio/start/model.
- Invalid-audio fail-fast probe `33999276060` returned exact bridge HTTP 400 `A valid audioUrl is required.` before job ID/FunctionCall spawn, proving deployed Blob token too; `audioRead=false`, `jobIdCreated=false`, `workerSpawnPossible=false`, model starts 0.
- Critical deployed runtime values are GREEN: `ANALYZER_API_URL_V143`, `ANALYZER_API_TOKEN`, `BLOB_READ_WRITE_TOKEN`.

## EXISTING PREVIEW — FINAL IDENTITY / SOURCE LINEAGE REVERIFIED

- Deployment ID: `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`.
- URL: `dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`.
- Final connected Vercel read immediately before this checkpoint: state/readyState **READY**, project `prj_6biwsn0iHci6FHNswAUCS8UYrAqF`, source `cli`.
- Immutable deployment metadata: GitHub ref `v143-contextual-prune-lobo`, exact source commit `0a07b393bb47123a1142fd46ea6d9a55b04f0486`, commit message `test: arm guarded OIDC async breakthrough E2E`.
- No rebuild/deploy/promotion/protection change is permitted for repaired attempt.

## REPAIRED EXISTING-PREVIEW RUNNER — STAGED / PINNED / NON-TRIGGERING

- Helper `.github/scripts/v143-existing-preview-async-breakthrough-e2e.sh`.
- Staging commit `ecbc96793d2f21582ddb5df77163d8a54cee64f0`.
- Final re-fetched helper blob `d72faac8c531b6572dc3ce1d2f5ec0f5e1317626`; local exact bytes passed `bash -n` before commit.
- Helper performs no build/deploy/alias/promotion/OIDC request path. It verifies source blobs + exact Preview ID/Ready/Preview state, uses authenticated `vercel curl` for preflight, exactly one backend-capable approved real-audio Rhythm start, same-token polling only, then one ACK on terminal response.
- Ambiguous/unaccepted real-audio start => aggregate evidence + STOP; no second start.
- Terminal completed or failed => aggregate state -> ACK once -> require cleanup -> then fail after cleanup if product/runtime result is not green.
- Poll deadline => STOP/no second start.
- Raw request/response/token files are runner-only and must be removed `if: always()`; aggregate `summary.json` only may be uploaded.

## FINAL PRE-ARM AUDIT — GREEN

- Branch Actions immediately before source audit: `in_progress=0`, `queued=0`, `waiting=0`, `requested=0`, `pending=0`; therefore no active breakthrough run exists.
- All seven authoritative source/audio blobs re-fetched and exact after that check.
- Helper blob re-fetched exact after source checks.
- Existing Preview identity/source lineage re-read and exact after source checks.
- Breakthrough workflow re-read: current blob `2a48af6aadda3b90a9c9ea24220ac524dbcb5b41`; push trigger remains scoped only to `.github/workflows/v143-fresh-preview-async-breakthrough-e2e.yml`; concurrency group remains `v143-fresh-preview-async-breakthrough-e2e-single`; `cancel-in-progress: false`.
- The current workflow still contains obsolete local build/direct-OIDC logic. It must be replaced, not rerun.

## NEXT — ONE REPAIRED ARMING EDIT ONLY

1. Immediately recheck there is no active breakthrough execution after this checkpoint-only push.
2. Make exactly one edit to `.github/workflows/v143-fresh-preview-async-breakthrough-e2e.yml`. That push is the repaired arming event.
3. New workflow must pin existing Preview ID/URL/source commit, all seven source blobs, and helper blob `d72faac8c531b6572dc3ce1d2f5ec0f5e1317626`.
4. It must install pinned Vercel CLI only, then run the staged helper exactly once. **No `vercel pull`, `vercel build`, `vercel deploy`, `--prod`, alias/promotion, direct OIDC header, protection change, or second start path.**
5. Cleanup raw start/status/ACK bodies + job token `if: always()`; upload aggregate `summary.json` only `if: always()`.
6. Watch only the run created by that workflow commit.
7. If the real start is accepted, no other model-bearing start is authorized. If it later fails, require terminal ACK/evidence and STOP; no rerun.
8. Checkpoint the arming run ID and every meaningful milestone/result.

## HARD STOPS

- **DO NOT RERUN `33998283085`; do not send ad-hoc real-audio requests; only the one workflow arming edit below may create the repaired backend-capable start.**
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change for access/lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **FINAL PRE-ARM GREEN. Backend/model start count remains 0. Next permitted action is one and only one repaired breakthrough workflow edit targeting the already-proven existing Preview through authenticated `vercel curl`; that edit is the sole arming event.**
