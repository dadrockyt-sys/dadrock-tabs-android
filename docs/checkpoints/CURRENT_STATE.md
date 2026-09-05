# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — repaired existing-Preview breakthrough ARMED as run `33999522733`; checkout only at checkpoint time; no repaired backend-capable start yet  
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

## AUTHORITATIVE PINS — FINAL PRE-ARM GREEN

- Branch async route `742954146a86aa36485d0bbdb3fbd6691a64a712`.
- `/ai-tab` page `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.
- Hardened bridge `36584355d9b060fc7b7e20acc62524fbc7bf9005`.
- Protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`.
- V143 worker `111bf14a8f91045d3478901f8e36b88a2e7f181a`.
- Scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Approved audio blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`.
- Repaired helper `.github/scripts/v143-existing-preview-async-breakthrough-e2e.sh` blob `d72faac8c531b6572dc3ce1d2f5ec0f5e1317626`, staging commit `ecbc96793d2f21582ddb5df77163d8a54cee64f0`; local exact bytes passed `bash -n`.

## LIFECYCLE / CONFIG GATES — GREEN

- Async lifecycle/ACK proof `33985474511` SUCCESS: deterministic terminal, ACK clears result/control, TTL 900, no binary async storage, reference calls 0.
- Direct GitHub OIDC protected access is NOT trusted; do not use it.
- Authenticated `vercel curl --deployment <exact-preview-url>` is GREEN (`33998720454`).
- Fake-token status probe `33999203347` proved deployed V143 URL/analyzer token + bridge auth GREEN with zero model start.
- Invalid-audio fail-fast probe `33999276060` proved deployed Blob token GREEN before job ID/FunctionCall spawn; `audioRead=false`, `workerSpawnPossible=false`, model starts 0.
- Local `vercel pull` remains incomplete and is not runtime-authoritative; no local prebuilt model-bearing attempt.

## FIRST REAL-AUDIO CLIENT ATTEMPT — BLOCKED BEFORE APP / BACKEND START COUNT STILL 0

- Old run `33998283085` sent one real-audio client POST but got Vercel-protection HTTP 401 before Next.js; no signed token/poll/ACK.
- Subsequent diagnostics proved it never reached app/bridge/orchestrator/worker/model.
- **Proven backend/model starts before repaired run = 0.** Do not rerun `33998283085`.

## EXACT EXISTING PREVIEW — PINNED / READY

- Deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`.
- URL `https://dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`.
- Vercel re-read immediately pre-arm: READY; project `prj_6biwsn0iHci6FHNswAUCS8UYrAqF`; source `cli`; GitHub ref `v143-contextual-prune-lobo`; immutable source commit `0a07b393bb47123a1142fd46ea6d9a55b04f0486`.
- Repaired attempt reuses this deployment only. No build/deploy/alias/promotion/protection change.

## REPAIRED WORKFLOW / ONE-START CONTRACT

- Breakthrough workflow path remains `.github/workflows/v143-fresh-preview-async-breakthrough-e2e.yml` with concurrency `v143-fresh-preview-async-breakthrough-e2e-single`, `cancel-in-progress: false`.
- Final pre-arm active states were all zero (`in_progress`, `queued`, `waiting`, `requested`, `pending`).
- One repaired arming edit committed as `f0d764c7cdaf0c7087d09d79473b82e0cf39ecab`.
- New workflow contains no `vercel pull`, build, deploy, `--prod`, promotion, alias, direct OIDC request path, or protection change. It installs Vercel CLI 59.11.2 and runs the pinned existing-Preview helper exactly once.
- Helper preflights exact Preview via authenticated `vercel curl`, then allows exactly one backend-capable approved real-audio Rhythm `start`.
- Accepted start must be HTTP 202 + `analysisJob.status=processing` + signed `v143a1.*` token; after that, status-only polling uses the same token and **no second start is possible**.
- Ambiguous/unaccepted start after POST => aggregate evidence + STOP/no second start.
- Terminal completed or failed => aggregate evidence -> ACK exactly once -> require result cleanup -> then product/runtime assertion or deliberate failure. No retry.
- Raw start/status/ACK bodies + job token deleted `if: always()`; artifact may contain aggregate `summary.json` only.

## ACTIVE REPAIRED RUN

- Arming commit `f0d764c7cdaf0c7087d09d79473b82e0cf39ecab` produced exactly one breakthrough run: **`33999522733`**.
- Job: `101395772704`.
- At this checkpoint: job `in_progress`; checkout step in progress; source gate/helper/start step not yet run.
- The only other run at the arming commit is unrelated cleanup workflow.
- **No repaired backend-capable real-audio start had occurred at this checkpoint.**

## NEXT — WATCH THIS RUN ONLY

1. Follow run `33999522733` / job `101395772704` only. Do not edit/rearm/rerun the breakthrough workflow.
2. Require exact source/helper boundary pass and exact existing Preview Ready/preflight 200.
3. If the one real-audio start returns 202 + signed token, checkpoint immediately: backend-capable start budget is consumed; no second start authorized under any outcome.
4. Poll same token only. If terminal completed or failed, require one ACK + transient cleanup, then inspect aggregate summary only.
5. If start response is ambiguous/unaccepted after application access, STOP; no second start.
6. If model/worker execution begins and later fails, ACK/evidence then STOP and diagnose exact call before any future authorization.
7. Save every meaningful milestone/result back here.

## HARD STOPS

- **NO SECOND REAL-AUDIO START / NO RERUN OF `33999522733`.**
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change for access/lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **one repaired breakthrough run is armed and must be watched exclusively. At checkpoint time it had not reached the backend-capable start step.**
