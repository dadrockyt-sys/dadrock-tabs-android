# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 — lifecycle GREEN; guarded helper staged; final pre-arm revalidation next  
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

## HISTORICAL BREAKTHROUGH RUN — MODEL BUDGET UNUSED

- Historical trigger commit `58be9aa7b5606783a508917ce4531cfd512d66da` produced run `33982235357`, job `101349393362`.
- Source gate and fresh Preview deploy were GREEN; protected `/ai-tab` preflight returned **403**; model-bearing step was **SKIPPED**.
- Historical breakthrough model starts therefore remain **0**. Do not rerun `33982235357`.
- Historical Preview deployment: `dpl_F6ksguDvc1nVAt33jNxxoVTmyyJA`; no production promotion.

## PROTECTED PREVIEW ACCESS — FIX DERIVED / GREEN PROOF

- Trusted GitHub OIDC proof `33982502347` returned protected Preview HTTP 200 using header `x-vercel-trusted-oidc-idp-token` without weakening Deployment Protection.
- Refreshability proof `33982582372` GREEN: tokens mint on demand from `ACTIONS_ID_TOKEN_REQUEST_URL` using `ACTIONS_ID_TOKEN_REQUEST_TOKEN`; JWT TTL = **300s**; repeated newly-minted tokens returned HTTP 200.
- Breakthrough workflow repair must add `id-token: write`, mint/mask a fresh token for preflight, the single start POST, each same-token status poll, and terminal ACK; never persist OIDC JWTs.
- Protected app requests use direct `curl` to exact fresh Preview URL with the trusted OIDC header. Vercel CLI remains build/deploy/inspect only. No `--prod`, promotion, or protection bypass/disable.

## FAILURE-PATH REPAIR — REQUIRED

- Old workflow exits on terminal failure before ACK/final aggregate evidence; that is not acceptable for the one model-bearing call.
- Backend ACK works for completed or failed terminal jobs and clears transient result + FunctionCall-control state.
- New path must: defer terminal/product assertions -> write aggregate pre-ACK state -> ACK exactly once same signed job token -> require `acknowledged` + `resultCleared` -> write final aggregate `summary.json` -> only then intentionally fail if terminal/product/runtime contract failed -> **do not retry**.
- Raw request/result/token material must always be deleted; artifact must contain aggregate `summary.json` only.

## SAFE STAGING MILESTONE — GUARDED HELPER COMMITTED WITHOUT ARMING

- New helper: `.github/scripts/v143-fresh-preview-async-breakthrough-e2e.sh`.
- Commit: `8d536121bb9a38f4a69add31cbf7515400441c5b`.
- Git blob: `92d17ee0b01ff72f71abfac1a7a4b36ff7e02792`.
- Local exact bytes passed `bash -n`; fetched GitHub blob matches the locally computed Git blob.
- This helper-file commit **cannot trigger** `V143 Fresh Preview Async Breakthrough E2E` because the existing push trigger watches only `.github/workflows/v143-fresh-preview-async-breakthrough-e2e.yml`.
- Helper preserves all seven authoritative source checks, one-start budget, fresh Preview-only deploy, OIDC fresh-token access, same signed-job-token polling, terminal ACK cleanup, aggregate-only summary, no production promotion, and explicit do-not-retry stops after any ambiguous/failed model-bearing start.
- A polling deadline after a real model start does **not** issue another start; it records aggregate state and stops for diagnosis. Terminal failure performs ACK first, then fails the job intentionally.

## LIVE TRIGGER WORKFLOW BEFORE ARMING

- Workflow: `.github/workflows/v143-fresh-preview-async-breakthrough-e2e.yml`.
- Current blob remains `bab50f03b26d728084fe898097b02c2470de2d2e` at last read.
- Trigger is push to `v143-contextual-prune-lobo` only when this workflow YAML path changes.
- Concurrency group: `v143-fresh-preview-async-breakthrough-e2e-single`, `cancel-in-progress: false`.
- Existing permissions currently only `contents: read`; arming edit must add `id-token: write`.

## FINAL PRE-ARM CONTRACT

Immediately before editing the workflow YAML:

1. Confirm branch HEAD contains only safe checkpoint/helper staging since the last pin audit; no source-pin drift.
2. Confirm `in_progress=0`, `queued=0`, `waiting=0`, `requested=0`, `pending=0` for branch Actions and no existing breakthrough run is active.
3. Re-read trigger/concurrency and workflow blob.
4. Make **one** workflow-file commit only. That push is the single arming event.
5. Workflow should pin helper blob `92d17ee0b01ff72f71abfac1a7a4b36ff7e02792`, add `id-token: write`, retain source pins, run helper once, cleanup raw material `if: always()`, upload only aggregate `summary.json` `if: always()`.
6. Watch the resulting run. If model execution starts and later fails, ACK/evidence then STOP. **No rerun and no second model start.**

## HARD STOPS

- No duplicate model-bearing request.
- No production Vercel promotion/change.
- No Deployment Protection weakening/disablement.
- No scheduler/model change for async lifecycle symptom.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL > 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.

Current authorization state: **lifecycle GREEN; historical model-start count 0; OIDC repair proven; failure cleanup repair designed; guarded helper staged without arming; next permitted action is final active/source/trigger revalidation followed by exactly one workflow YAML arming commit if all checks remain clean.**
