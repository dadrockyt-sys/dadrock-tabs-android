# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-04 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## Global scientific state — unchanged

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**
- GOAT Zenodo `15690894` / DOI `10.5281/zenodo.15690894` v1 access still awaits explicit owner approval/denial.
- Restricted GOAT bytes admitted/read = **0**; V168 prospective reference-facing score calls = **0**.
- SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`; never rerun/score/weaken/interpolate.
- GuitarSet V3/V4/V5 remain terminal; prospective players `00/01/03` remain sealed and prospective score calls = **0**.
- CPU only for Phase 10–13. No GPU/CUDA/Modal was used.
- `main` and Vercel Production remain untouched.

**Project Progress Score: 74%.**  
**Test Score: PHASE 1–13 GREEN; FULL BRANCH BUILD/CANONICAL HTTP GATE GREEN; EXACT-SHA PROTECTED REAL-VERCEL PREVIEW SMOKE CLOSED GREEN; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Phases 1–13 — CLOSED GREEN

- Phase 1–7 reference-blind conditioning/shadow/mixture/analyzer chain: frozen gates **SUCCESS**.
- Phase 8 server observation admission: run `33827081887`, job `100881934408`, **SUCCESS**; final branch gate `33827731955`, job `100883875983`, **SUCCESS**.
- Phase 9 admitted shadow effect: run `33828829026`, job `100887194463`, **SUCCESS**.
- Phase 10 Product-placement candidate: run `33829600963`, job `100889565032`, **SUCCESS**; synthetic placement 0% -> 100%, 7/7 exact.
- Phase 11 live candidate canary: run `33830896322`, job `100893491799`, **SUCCESS**.
- Phase 12 canonical Product/PDF placement: run `33831663771`, job `100895770003`, head `fdd54716641d2df73e5794cd3abadf06e78da208`, **SUCCESS**; renderer `v143-structured-rhythm`; PDF 1,665,393 bytes; placement 0 -> 7; exact 7/7.
- Phase 13 built-Next canonical HTTP gate: run `33833707924`, job `100901804298`, head `ed776202b60ee410beb455db16ee820e260ff17b`, **SUCCESS**; 95/95 static pages; analysis 200; promotion 0 -> 7 exact 7/7; Product/PDF 200; feature `v143-branch-preview-canary`; renderer `v143-structured-rhythm`; PDF 1,665,404 bytes; malformed analysis 400.

Detailed Phase 13 result: `docs/checkpoints/SONGSTERR_V143_BUILT_NEXT_CANONICAL_PROMOTION_HTTP_GATE_PHASE13_RESULT_20260903.md`.

## Independent branch gate after protected-smoke workflow change — GREEN

Application-equivalent commit `d3439a20124e1982facde2732f18b88602e18625` triggered the normal branch build gate:

- run **`33842848801`**;
- job **`100928482970`** (`verify-build-and-route-smoke`);
- conclusion **SUCCESS**.

All stages passed: analyzer-quality verifier, Preview feature verifier, locked install, full Next build, built-server readiness, built Preview route, canonical analysis -> promotion -> Product/PDF HTTP chain, evidence recording, safety enforcement, and shutdown.

## Protected real-Vercel Preview smoke — CLOSED GREEN

A first diagnostic Preview attempt on `d3439a20124e1982facde2732f18b88602e18625` created READY Preview deployment `dpl_Dv8ErpW4BNEA6FEtGgKjU5rwgf1K`, but the smoke command failed before any app route because `--token` was forwarded to native curl. Vercel had already successfully generated a Deployment Protection bypass token, proving the authentication mechanism; no application result was accepted from that attempt.

The corrected exact-SHA gate is authoritative:

- workflow: `.github/workflows/v143-protected-preview-smoke.yml`;
- source commit: **`12567e284d76b5c95240ad823628e311df3fc5e3`**;
- workflow run: **`33843200741`**;
- job: **`100929522781`** (`protected-preview-smoke`);
- conclusion: **SUCCESS**;
- evidence artifact ID: **`9925639186`**;
- exact deployment ID: **`dpl_6pXryC9R7M5mJwZA7cUt2qh3bBsp`**;
- URL: `dadrock-tabs-android-dmjmes0ly-stephen-mcnally-s-projects.vercel.app`;
- Vercel state / readyState: **READY**;
- Vercel inspect target: **preview**;
- connector target: `null` = Preview/non-Production;
- aliases: none;
- exact metadata branch: `v143-contextual-prune-lobo`;
- exact metadata SHA: `12567e284d76b5c95240ad823628e311df3fc5e3`;
- build: **95/95 static pages**.

### Protected HTTP evidence

- authenticated Deployment Protection access method: `vercel-curl-env-token-auto-bypass`;
- Deployment Protection disabled: **false**;
- `GET /ai-tab`: **200**, body **38,016 bytes**;
- `POST /api/generate-tab-preview`: **200**;
- content type: **`application/pdf`**;
- PDF magic: **`%PDF`**;
- feature: **`v143-branch-preview-canary`**;
- renderer: **`v143-structured-rhythm`**;
- PDF bytes: **1,665,759**;
- malformed `POST /api/analyze-audio-tab`: **400**;
- malformed request fails before analyzer: **true**;
- protected smoke `passed`: **true**.

Vercel runtime logs scoped to the exact deployment corroborate the same sequence:

- `06:11:35Z` GET `/ai-tab` -> **200**;
- `06:11:37Z` POST `/api/generate-tab-preview` -> **200**;
- `06:11:41Z` POST `/api/analyze-audio-tab` -> **400**.

No unexpected 5xx appeared in the scoped smoke log set.

Detailed result: `docs/checkpoints/SONGSTERR_V143_REAL_VERCEL_PROTECTED_PREVIEW_SMOKE_RESULT_20260904.md`.

## Safety accounting through this checkpoint

- exact protected Vercel Preview deployment READY = true;
- Deployment Protection disabled = false;
- Vercel Production deployment created/modified by this work = false;
- `--prod` used = false;
- Preview-to-Production promotion = false;
- Production aliases/domains/env changed = false;
- `main` modified = false;
- deterministic reference-blind fixture = true;
- external/reference assets/audio used = false;
- real analyzer invocation requested by protected smoke = false;
- GuitarSet read = false;
- SplitMySong read = false;
- GOAT restricted bytes read = false;
- reference score calls = 0;
- Modal invoked/deployed = false;
- GPU/CUDA = false.

## CURRENT BOUNDARY

The authorized **Preview-only** deployment/testing objective is complete and closed green. The branch now has real protected-Vercel evidence in addition to the built-Next canonical gate.

Production remains outside current authority. **Do not merge to `main`, assign Production aliases, use `--prod`, or promote/deploy Vercel Production without fresh explicit user authorization.**

Reference-facing accuracy scoring also remains disarmed until a lawful holdout exists. GOAT owner approval remains pending; terminal SplitMySong/GuitarSet boundaries remain closed.

## NEXT SAFE ACTION

1. Preserve this state; no additional Preview repair is required by the completed smoke.
2. If future work stays reference-blind, continue only with branch-local/product-quality tasks that do not cross the frozen holdout boundary.
3. If the next desired step is Production promotion or merge to `main`, obtain fresh explicit user authorization first and perform a separately gated promotion review.
4. If the next desired step is reference-facing scoring, wait for a lawful holdout asset; do not reopen terminal SplitMySong/GuitarSet paths or read restricted GOAT bytes without authorization.
