# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — repaired POST-preflight helper FINAL RE-ARM GREEN; one workflow helper-blob/cleanup edit authorized  
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

## AUTHORITATIVE PINS — FINAL RE-ARM REVERIFIED

- Route `742954146a86aa36485d0bbdb3fbd6691a64a712`.
- `/ai-tab` page `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.
- Bridge `36584355d9b060fc7b7e20acc62524fbc7bf9005`.
- Protocol `1bd55017e16a4e1d8b14c7429492f811a43a28d8`.
- Worker `111bf14a8f91045d3478901f8e36b88a2e7f181a`.
- Scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Approved audio `4dd709e3fa177b4daeed71ca97f0199757729d4b`.
- Repaired helper `.github/scripts/v143-existing-preview-async-breakthrough-e2e.sh` = `433599afec7fff20a31ea79e4c93ef9a6da03b36`.

## LIFECYCLE / CONFIG / TRANSPORT GATES — GREEN

- Async lifecycle/ACK proof `33985474511` GREEN.
- Direct GitHub OIDC is not trusted; do not use it.
- Authenticated `vercel curl` protected POST route transport GREEN (`33998720454`).
- Deployed V143 URL/analyzer token + bridge auth GREEN (`33999203347`).
- Deployed Blob token GREEN with invalid-audio pre-spawn rejection (`33999276060`).
- Local `vercel pull` is incomplete/non-authoritative; no local prebuilt model-bearing attempt.

## BACKEND START ACCOUNTING — ZERO

- Old run `33998283085`: one client real-audio POST blocked by Vercel before Next.js; backend/model starts 0.
- Existing-Preview run `33999522733`: GET `/ai-tab` preflight returned 403 and helper stopped before generating/sending real-audio start.
- Artifact `9979067110`, digest `sha256:6d2dca3fb29075903f166d73141495bfd8eb6916ed973bf037fc9a5152dd1bb6`, proves `backendCapableRealAudioStartRequestCount=0` and no production/reference changes.
- **Proven backend/model starts remain 0.** Do not rerun either prior breakthrough run.

## ROOT CAUSE / REPAIR — MODEL-FREE

- GET page preflight was unnecessary and mismatched the already-proven protected transport.
- Helper repair commit `e24eb3b3ef05f25faa2ddefd1bee66327549b98e`, blob `433599afec7fff20a31ea79e4c93ef9a6da03b36`.
- Repaired preflight is authenticated `vercel curl` POST to `/api/analyze-audio-tab` with only `{"transcriptionType":"invalid"}`.
- It requires HTTP 400 + exact Next route error `Transcription type must be lead, rhythm, or bass.` before any real-audio block.
- No audio URL, valid type, analyzer call, worker spawn, or model path exists in this preflight.
- Local exact repaired bytes passed `bash -n`; GitHub re-fetch confirms blob and preflight block.
- One-start/signed-token/same-token-poll/terminal-ACK/no-retry logic otherwise unchanged.

## EXISTING PREVIEW — FINAL RE-ARM IDENTITY GREEN

- Deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`.
- URL `https://dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`.
- Final Vercel re-read: READY; project `prj_6biwsn0iHci6FHNswAUCS8UYrAqF`; source `cli`; branch `v143-contextual-prune-lobo`; immutable source commit `0a07b393bb47123a1142fd46ea6d9a55b04f0486`.
- No build/deploy/alias/promotion/protection change permitted.

## FINAL RE-ARM AUDIT — GREEN

- Immediately before source audit: `in_progress=0`, `queued=0`, `waiting=0`, `requested=0`, `pending=0` for branch Actions.
- All seven source/audio blobs re-fetched exact.
- Repaired helper re-fetched exact `433599af...`.
- Existing Preview identity/source lineage re-read exact/READY.
- Breakthrough workflow blob before re-arm = `47d94520b317956e632690760d1c3cbf76d3ac5a`.
- Trigger remains only `.github/workflows/v143-fresh-preview-async-breakthrough-e2e.yml`; concurrency group `v143-fresh-preview-async-breakthrough-e2e-single`; `cancel-in-progress: false`.
- Current workflow already has no build/deploy/OIDC/prod path. Only two changes are authorized: update `E2E_SCRIPT_BLOB` to `433599af...` and add raw `preflight-response.json` to `if: always()` cleanup.

## NEXT — ONE RE-ARM EDIT / WATCH ONLY THAT RUN

1. Make exactly one workflow edit with only the helper blob + preflight-response cleanup changes above. That push is the sole re-arm event.
2. Find exactly one breakthrough run at that commit and watch only it.
3. Require source/helper boundary, exact Preview inspect, then model-free POST preflight HTTP 400 + exact route error.
4. If the single approved real-audio start returns HTTP 202 + signed `v143a1.*`, the backend-capable start budget is consumed. **No second start or rerun under any outcome.**
5. Poll same token only; on terminal completed or failed, aggregate -> ACK once -> require transient cleanup -> then pass/fail product/runtime assertions.
6. If start response is ambiguous after the POST, STOP/no second start.
7. Save run ID and every meaningful milestone/result here.

## HARD STOPS

- **DO NOT RERUN `33998283085` OR `33999522733`; DO NOT send ad-hoc real audio.**
- After an accepted repaired start, no second model-bearing start is authorized.
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change for access/preflight symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **FINAL RE-ARM GREEN; backend/model start count 0; exactly one helper-blob/cleanup workflow edit is authorized now.**
