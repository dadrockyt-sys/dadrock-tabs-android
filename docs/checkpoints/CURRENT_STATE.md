# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — run `33999522733` safe pre-start stop; model-free POST route preflight repair staged at helper blob `433599af...`; final re-arm audit next  
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

- Branch async route `742954146a86aa36485d0bbdb3fbd6691a64a712`.
- `/ai-tab` page `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.
- Hardened bridge `36584355d9b060fc7b7e20acc62524fbc7bf9005`.
- Protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`.
- V143 worker `111bf14a8f91045d3478901f8e36b88a2e7f181a`.
- Scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Approved audio blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`.

## LIFECYCLE / CONFIG GATES — GREEN

- Async lifecycle/ACK proof `33985474511` SUCCESS: deterministic terminal, ACK clears result/control, TTL 900, no binary async storage, reference calls 0.
- Direct GitHub OIDC protected access is NOT trusted; do not use it.
- Authenticated `vercel curl --deployment <exact-preview-url>` POST to `/api/analyze-audio-tab` is GREEN (`33998720454`).
- Fake-token status probe `33999203347` proved deployed V143 URL/analyzer token + bridge auth GREEN with zero model start.
- Invalid-audio fail-fast probe `33999276060` proved deployed Blob token GREEN before job ID/FunctionCall spawn; model starts 0.
- Local `vercel pull` is incomplete/non-authoritative; no local prebuilt model-bearing attempt.

## EXACT EXISTING PREVIEW — PINNED / READY

- Deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`.
- URL `https://dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`.
- Vercel metadata: READY, project `prj_6biwsn0iHci6FHNswAUCS8UYrAqF`, source `cli`, branch `v143-contextual-prune-lobo`, immutable source commit `0a07b393bb47123a1142fd46ea6d9a55b04f0486`.
- No build/deploy/alias/promotion/protection change is permitted.

## BACKEND START ACCOUNTING — STILL ZERO

### Historical old attempt `33998283085`
- One real-audio client POST rejected by Vercel protection before Next.js; no app/bridge/worker/model reach. Backend/model starts = **0**.

### Existing-Preview attempt `33999522733`
- Arming commit `f0d764c7cdaf0c7087d09d79473b82e0cf39ecab`; job `101395772704`.
- Exact source/helper boundary + exact Preview inspect passed.
- Authenticated `vercel curl` GET `/ai-tab` preflight returned HTTP 403, so helper exited before generating/sending the real-audio start body.
- Artifact `9979067110`, digest `sha256:6d2dca3fb29075903f166d73141495bfd8eb6916ed973bf037fc9a5152dd1bb6` proves `backendCapableRealAudioStartRequestCount=0`, `startAccepted=false`, no production/reference changes.
- **Backend/model starts = 0.** Do not rerun `33999522733`.

## ROOT CAUSE — GET PAGE PREFLIGHT ONLY

- The failed GET `/ai-tab` check was new and unnecessary.
- The exact protected API route POST transport was already proven model-free with authenticated `vercel curl`: malformed `{"transcriptionType":"invalid"}` -> HTTP 400 + exact Next route error `Transcription type must be lead, rhythm, or bass.`.
- Do not weaken protection to make page GET succeed.

## MODEL-FREE PREFLIGHT REPAIR — STAGED / NON-TRIGGERING

- Updated only `.github/scripts/v143-existing-preview-async-breakthrough-e2e.sh`.
- Commit `e24eb3b3ef05f25faa2ddefd1bee66327549b98e`.
- New helper blob `433599afec7fff20a31ea79e4c93ef9a6da03b36`, matching locally computed Git blob after `bash -n` success.
- Re-fetched helper confirms preflight now uses authenticated `vercel curl` POST to `/api/analyze-audio-tab` with exactly `{"transcriptionType":"invalid"}` and no audio URL.
- Preflight requires HTTP 400 + exact route error before the real-audio start block can execute.
- Invalid transcription type fails in the Next route before analyzer fetch; therefore this preflight has no analyzer/worker/model path.
- Existing one-real-audio-start budget, signed-token validation, same-token polling, terminal ACK, STOP/no-retry behavior remain unchanged.
- This helper-only commit cannot trigger the breakthrough workflow because trigger watches only `.github/workflows/v143-fresh-preview-async-breakthrough-e2e.yml`.
- New raw preflight response file `preflight-response.json` must be added to workflow `if: always()` cleanup at the next arming edit; it must never be uploaded.

## NEXT — FINAL RE-ARM AUDIT, THEN ONE WORKFLOW EDIT IF CLEAN

1. Recheck `in_progress`, `queued`, `waiting`, `requested`, `pending` branch Actions; require no active breakthrough run.
2. Re-fetch all seven source/audio blobs; require exact authoritative pins above.
3. Re-fetch repaired helper; require blob `433599afec7fff20a31ea79e4c93ef9a6da03b36`.
4. Re-read exact existing Preview; require deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, READY, branch/source commit exact.
5. Re-read breakthrough workflow/concurrency.
6. Checkpoint clean re-arm state before workflow edit.
7. Make exactly one workflow edit: update `E2E_SCRIPT_BLOB` to `433599af...` and add `preflight-response.json` to always-cleanup. No other behavioral change is needed.
8. That edit is the sole new arming event. Watch only its run.
9. If real-audio start is accepted, start budget is consumed permanently for this diagnostic phase; no second start/rerun under any failure outcome.

## HARD STOPS

- **DO NOT RERUN `33999522733`; DO NOT send ad-hoc real audio; DO NOT edit the breakthrough workflow until final re-arm audit + checkpoint are complete.**
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change for this access/preflight symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **backend/model start count remains 0; model-free POST preflight repair is staged and pinned; next permitted action is final re-arm validation + checkpoint, then one workflow helper-blob/cleanup arming edit if clean.**
