# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 13:02 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async storage authorization: transient structured result + non-sensitive FunctionCall control metadata only; no raw audio/stems/model bytes; TTL <= 900 seconds; no persistent result cache.

## Production baseline — UNCHANGED

- Vercel `main` `bb992d901e78ab19645f8edc8e330d5a142ebd8e`, deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, synchronous route blob `06234db3e1cc1680b18fd62a765862b213ede3db` / `maxDuration=150`.
- No production Vercel promotion and no whole-branch merge.
- L4 worker unchanged: `dadrock-v143-ai-tab-live/rhythm_v143_request`, live blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`, scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Hardened production HTTP bridge deployed GREEN: bridge blob `36584355d9b060fc7b7e20acc62524fbc7bf9005`, protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`; deploy run `33981874155` / job `101348420851`, artifact `9973991338`.

## Async architecture / branch pins

Plan `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Rhythm: start -> signed opaque token -> browser polls Vercel -> Vercel polls bridge -> transient Modal Queue -> existing V143 safety/product pipeline -> result -> ACK clears result + control. Lead/Bass stay synchronous.

- route blob `742954146a86aa36485d0bbdb3fbd6691a64a712`;
- `/ai-tab` page blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.

## Modal `oneshot` report — FIXED / PROVEN / DEPLOYED

Root robustness gap was pre-hardening loss of `.spawn()` FunctionCall state: an orchestrator dying before Queue publication could appear `processing` forever. Hardened bridge tracks opaque FunctionCall ID, polls with `FunctionCall.from_id(...).get(timeout=0)`, returns terminal bounded failure for dead calls, and ACK clears result + control partitions.

Proofs GREEN:

- source gate `33981347482` / `101347008342`, artifact `9973838904`;
- isolated hardened bridge `33981493357` / `101347398382`;
- decisive fail-fast transition `33981664796` / `101347836824`, artifact `9973957720`;
- hardened production bridge deploy/smoke `33981874155` / `101348420851`.

## Preview async breakthrough E2E — PREVIOUS PREFLIGHTS / ZERO MODEL STARTS

Attempt 1: run `33982105469`, job `101349042393`, historical Preview Ready but unauthenticated `vercel curl` = 403; model step skipped.

Attempt 2: run `33982235357`, job `101349393362`:

- exact source pins GREEN;
- local Next 16.1.6 build GREEN;
- fresh Preview-only deployment **`dpl_F6ksguDvc1nVAt33jNxxoVTmyyJA`**, URL `https://dadrock-tabs-android-r602jctx9-stephen-mcnally-s-projects.vercel.app`, target preview / Ready;
- unauthenticated `vercel curl /ai-tab` = 403;
- model step skipped;
- model/audio start count remains **0 total**.

## Deployment Protection authentication — TRUSTED GITHUB OIDC GREEN / REFRESHABLE

Vercel's documented Trusted Sources method was proven without changing or disabling Deployment Protection.

Initial trusted-source proof:

- workflow `.github/workflows/v143-preview-protection-oidc-probe.yml`;
- commit `75146e2e03d770b983862149feadcc5026552803`;
- run `33982502347`, job `101350110959`: SUCCESS;
- artifact `9974159307`, digest `sha256:d247d08eb2d4d478406056c387e915c33ccfcd0909cfbfa48583821546f4f362`;
- `id-token: write`, `core.getIDToken()`, header `x-vercel-trusted-oidc-idp-token`;
- protected fresh Preview `/ai-tab` = HTTP 200;
- token masked/not retained; model/audio starts=0.

Refreshability proof:

- workflow `.github/workflows/v143-preview-oidc-refresh-probe.yml`;
- commit `363fdaee439fdb6680943920796b753cfa1e4294`;
- run **`33982582372`**, job `101350332422`: source probe step SUCCESS;
- artifact **`9974183273`**, digest `sha256:e5086c0e7a5a81c173a148285b44396a7a86b724903e0b67f091da40d3e81306`;
- direct shell token mint via GitHub's `ACTIONS_ID_TOKEN_REQUEST_URL` / `ACTIONS_ID_TOKEN_REQUEST_TOKEN` proven;
- first OIDC token TTL = **300 seconds**, protected Preview HTTP 200;
- second independently minted token TTL = **300 seconds**, protected Preview HTTP 200;
- `refreshableTrustedOidc=true`, tokens retained=false, Deployment Protection disabled=false;
- modelBearingStartRequests=0, audioRead=false, modelExecuted=false, reference inputs/scores=0.

**Conclusion:** every long-poll request can mint a fresh trusted OIDC token. Protection authentication will not expire during the single model-bearing async job.

## NEXT STEP — ONE MODEL-BEARING ASYNC BREAKTHROUGH E2E

Use existing fresh Preview `dpl_F6ksguDvc1nVAt33jNxxoVTmyyJA`.

1. Exact source/safety pins pass before start.
2. Mint fresh trusted OIDC token and POST **exactly one** Rhythm start using approved source `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, Git blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`.
3. Require HTTP 202 + signed `v143a1.*` job token.
4. For every status poll, mint a new OIDC token, then poll only the same analysis job token.
5. Permit total analysis time beyond 150s; each individual Vercel request remains short.
6. Require terminal 200 + generated tab + V143 reference-free safety/product contract.
7. Mint fresh OIDC token and ACK once; require result/control cleanup.
8. Delete request/token/result files; persist aggregate summary only.
9. If the one model-bearing job fails after start, do not launch another; diagnose first.

### Hard stops

- **Model/audio start requests so far = 0; budget remaining = 1.**
- No Production Vercel environment change/promotion.
- No Deployment Protection weakening/disablement.
- No model/scheduler change.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL above 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.
