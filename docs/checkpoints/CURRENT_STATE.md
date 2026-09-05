# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — repaired run `33999522733` STOPPED SAFELY PRE-START on GET `/ai-tab` 403; aggregate proves backend-capable start count 0; next work model-free helper preflight repair only  
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
- Existing-Preview helper before preflight repair: blob `d72faac8c531b6572dc3ce1d2f5ec0f5e1317626`, staging commit `ecbc96793d2f21582ddb5df77163d8a54cee64f0`.

## LIFECYCLE / CONFIG GATES — GREEN

- Async lifecycle/ACK proof `33985474511` SUCCESS: deterministic terminal, ACK clears result/control, TTL 900, no binary async storage, reference calls 0.
- Direct GitHub OIDC protected access is NOT trusted; do not use it.
- Authenticated `vercel curl --deployment <exact-preview-url>` **POST to `/api/analyze-audio-tab`** is GREEN (`33998720454`).
- Fake-token status probe `33999203347` proved deployed V143 URL/analyzer token + bridge auth GREEN with zero model start.
- Invalid-audio fail-fast probe `33999276060` proved deployed Blob token GREEN before job ID/FunctionCall spawn; `audioRead=false`, `workerSpawnPossible=false`, model starts 0.
- Local `vercel pull` is incomplete/non-authoritative; no local prebuilt model-bearing attempt.

## EXACT EXISTING PREVIEW — PINNED / READY

- Deployment `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`.
- URL `https://dadrock-tabs-android-bx51iz9tr-stephen-mcnally-s-projects.vercel.app`.
- Vercel metadata: READY, project `prj_6biwsn0iHci6FHNswAUCS8UYrAqF`, source `cli`, branch `v143-contextual-prune-lobo`, immutable source commit `0a07b393bb47123a1142fd46ea6d9a55b04f0486`.
- No build/deploy/alias/promotion/protection change is permitted.

## REAL-AUDIO / BACKEND START ACCOUNTING

### Historical old attempt `33998283085`

- One client real-audio POST was rejected by Vercel protection before Next.js (HTTP 401).
- No signed token/poll/ACK; later model-free diagnostics proved no app/bridge/orchestrator/worker/model reach.
- Backend/model starts from that run = **0**.

### Repaired existing-Preview attempt `33999522733` — SAFE PRE-START STOP

- Arming commit `f0d764c7cdaf0c7087d09d79473b82e0cf39ecab`; job `101395772704`.
- Exact source/helper boundary passed.
- Exact existing Preview inspect passed: ID `dpl_G2WxxMA782j87H7tLpAy9cCB4ihD`, target Preview, status Ready.
- Helper then used authenticated `vercel curl` **GET `/ai-tab`** as a preflight and received HTTP **403**.
- It exited immediately with `Protected Preview preflight failed before real-audio start; do not send a start.`
- Real-audio start step inside helper was never reached.
- Cleanup step SUCCESS; aggregate-artifact step SUCCESS.
- Artifact `9979067110`, digest `sha256:6d2dca3fb29075903f166d73141495bfd8eb6916ed973bf037fc9a5152dd1bb6`.
- Aggregate summary proves:
  - `previewIdentityVerified=true`
  - `protectedPreviewStatus=403`
  - `backendCapableRealAudioStartRequestCount=0`
  - `startAccepted=false`
  - `completed=false`
  - `acknowledged=false`
  - `productionEnvironmentChanged=false`
  - `productionPromotionPerformed=false`
  - `deploymentProtectionDisabled=false`
  - `referenceFacingInputs=0`, `referenceScoreCalls=0`, `qualityVerdictMade=false`
  - error = `Protected Preview preflight failed before real-audio start.`
- **Backend/model starts from repaired run = 0.**
- Do not rerun run `33999522733`.

## ROOT CAUSE — PRELIGHT METHOD MISMATCH, NOT APP/RUNTIME/MODEL

- The repaired helper introduced a new GET `/ai-tab` preflight that had not been the transport proof.
- Same exact protected Preview was already proven reachable through authenticated `vercel curl` by POSTing a malformed JSON body to `/api/analyze-audio-tab`, which returned exact Next route HTTP 400 (`Transcription type must be lead, rhythm, or bass.`).
- Therefore the current stop is isolated to the **GET page preflight**. It does not invalidate protected POST route transport, deployed analyzer/Blob config, lifecycle, or source pins.
- Do not weaken protection to make GET `/ai-tab` succeed.

## NEXT — MODEL-FREE HELPER PREFLIGHT REPAIR ONLY

1. Do **not** edit/rearm the breakthrough workflow yet and do not send real audio.
2. Update only `.github/scripts/v143-existing-preview-async-breakthrough-e2e.sh` in a non-triggering commit.
3. Replace GET `/ai-tab` preflight with the already-proven model-free authenticated `vercel curl` malformed POST to `/api/analyze-audio-tab` using `{"transcriptionType":"invalid"}`.
4. Require HTTP 400 + exact Next route error `Transcription type must be lead, rhythm, or bass.` before permitting any real-audio start.
5. This preflight must have no audio URL, no valid transcription type, no analyzer call, no worker/model path.
6. Keep all existing source/Preview pins, one-start logic, same-token polling, terminal ACK, cleanup, and aggregate-only artifact behavior unchanged.
7. Run local `bash -n`, compute/fetch exact helper blob, then checkpoint the staged repair.
8. Only after final no-active-run/source/helper/Preview revalidation may one future workflow edit update the helper blob and arm a new attempt. The prior repaired run consumed **zero** backend-capable starts.

## HARD STOPS

- **DO NOT RERUN `33999522733`; DO NOT send ad-hoc real audio; DO NOT edit the breakthrough workflow until repaired helper staging + checkpoint + final pre-arm checks are complete.**
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement or bypass-secret creation.
- No scheduler/model change for this access/preflight symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **run `33999522733` failed safely before any repaired real-audio POST; backend/model start count remains 0. Next permitted action is model-free non-triggering helper preflight repair only.**
