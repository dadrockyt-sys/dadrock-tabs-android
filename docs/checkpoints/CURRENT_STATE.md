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
**Test Score: PHASE 1–13 GREEN; EXACT-BRANCH VERCEL PREVIEW READY; AUTHENTICATED PROTECTED-SMOKE MECHANISM PROVEN BUT FIRST WORKFLOW INVOCATION HIT CLI ARGUMENT-PLACEMENT BUG BEFORE APP ROUTE; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Phases 1–11 — COMPLETE

- Phase 1–7 reference-blind conditioning/shadow/mixture/analyzer chain: all frozen workflow gates **SUCCESS**.
- Phase 8 server observation admission: run `33827081887`, job `100881934408`, **SUCCESS**; final branch gate `33827731955`, job `100883875983`, **SUCCESS**.
- Phase 9 admitted shadow effect: run `33828829026`, job `100887194463`, **SUCCESS**.
- Phase 10 Product-placement candidate: run `33829600963`, job `100889565032`, **SUCCESS**; synthetic placement 0% -> 100%, 7/7 exact.
- Phase 11 live candidate canary: run `33830896322`, job `100893491799`, **SUCCESS**.

## Phase 12 — CANONICAL PRODUCT/PDF PLACEMENT PROMOTION CLOSED GREEN

Canonical workflow run `33831663771`, job `100895770003`, tested head `fdd54716641d2df73e5794cd3abadf06e78da208`, **SUCCESS**. R1–R16 = 16/16 PASS; matrix = 12/12 PASS; renderer = `v143-structured-rhythm`; structured PDF bytes = **1,665,393**; deterministic promotion = **0 -> 7**; exact known-truth placement = **7/7**.

Result: `docs/checkpoints/SONGSTERR_FULL_MIXTURE_PRODUCT_PLACEMENT_CANONICAL_PROMOTION_V1_PHASE12_RESULT_20260903.md`.

## Phase 13 — BUILT-NEXT CANONICAL PROMOTION HTTP GATE CLOSED GREEN

Authoritative run `33833707924`, job `100901804298`, tested head `ed776202b60ee410beb455db16ee820e260ff17b`, **SUCCESS**. Full Next build 95/95 static pages; analysis HTTP 200; Rhythm canary active; canonical promotion `PROMOTED_PLACEMENT_ONLY`; placement **0 -> 7**; exact **7/7**; Product/PDF HTTP 200; feature `v143-branch-preview-canary`; renderer `v143-structured-rhythm`; PDF bytes **1,665,404**; malformed analysis fails closed 400.

Result: `docs/checkpoints/SONGSTERR_V143_BUILT_NEXT_CANONICAL_PROMOTION_HTTP_GATE_PHASE13_RESULT_20260903.md`.

## Exact-branch Vercel Preview — READY

User authorization remains Preview-only for `v143-contextual-prune-lobo`; Production and `main` remain outside scope.

Earlier canonical READY deployment:
- exact deployed SHA `df3042180e57df1031a2a529961388a6419d1bc5`;
- workflow run `33836754320`, job `100910747161`;
- deployment `dpl_HEQHX2nfFhYJzsMMEsAa8ePhcQpX`;
- READY, target `null` / Preview;
- Production target/promotion not used.

At continuation start, branch head `5cf7218f222d4f38423d6af2b559646d20d7fe18` was only two checkpoint-only commits ahead of `df304218...`; no runtime drift invalidated that Preview.

## Protected real-Vercel Preview smoke — ATTEMPT 1 DIAGNOSTIC

Authenticated protected-route smoke was added to `.github/workflows/v143-exact-branch-vercel-preview.yml` in commit:

- **`d3439a20124e1982facde2732f18b88602e18625`** — `preview: add authenticated protected-route smoke`.

This push triggered:
- exact Preview run **`33842848820`**, job **`100928483010`** (`deploy-preview`);
- normal branch build run **`33842848801`**, job **`100928482970`** (`verify-build-and-route-smoke`).

Exact Preview deployment created by attempt 1:
- deployment ID **`dpl_Dv8ErpW4BNEA6FEtGgKjU5rwgf1K`**;
- URL `dadrock-tabs-android-l8viklzvp-stephen-mcnally-s-projects.vercel.app`;
- exact metadata branch `v143-contextual-prune-lobo`;
- exact metadata SHA `d3439a20124e1982facde2732f18b88602e18625`;
- state / readyState **READY**;
- `vercel inspect` target **preview**;
- connector target `null` = non-Production;
- aliases = none;
- full Vercel build completed, including 95/95 static pages and the `/ai-tab`, `/api/analyze-audio-tab`, `/api/generate-tab-preview`, and `/api/generate-tab-pdf` routes.

Preview run steps through deployment and inspection all passed. The new smoke step then failed **before reaching the application route** because of Vercel CLI global-option placement:

1. `vercel curl` authenticated successfully enough to retrieve the project;
2. Vercel CLI reported deployment protection was active;
3. Vercel CLI automatically generated the required deployment-protection bypass token successfully;
4. then underlying curl received the Vercel CLI token option and failed with: **`curl: option --token=***: is unknown`**;
5. exit code = **2**.

Meaning: the selected authenticated protection-bypass mechanism is valid and protection remained enabled. The failure is a workflow command-line syntax defect, not an `/ai-tab` or Product/PDF application failure. No app-route result from this attempt is accepted.

Failed-run artifact `v143-exact-branch-vercel-preview` was preserved as artifact ID **`9925517026`**. Because the first request stopped at CLI parsing, `protectedPreviewSmokePresent=false`; no false application PASS was recorded.

### Narrow correction frozen

Move `--token="$VERCEL_TOKEN"` to Vercel's documented global CLI position for all three smoke calls:

`vercel --token="$VERCEL_TOKEN" curl <path> --deployment "$VERCEL_PREVIEW_URL" -- <native curl flags>`

No runtime/Product/transcription code change is needed or authorized by this diagnostic.

After the correction, rerun the exact-SHA Preview workflow and normal branch build gate; accept only evidence tied to the corrected exact SHA.

## Protected smoke contract — unchanged

The corrected smoke must:
1. preserve exact branch/SHA guards and `--prebuilt` Preview-only deployment;
2. keep Vercel Deployment Protection enabled and use authenticated `vercel curl` bypass;
3. verify `/ai-tab` returns 200;
4. POST a deterministic reference-blind structured Rhythm fixture directly to `/api/generate-tab-preview` with no external/reference audio and no analyzer invocation;
5. verify HTTP 200, `application/pdf`, `%PDF`, nontrivial bytes, feature `v143-branch-preview-canary`, renderer `v143-structured-rhythm`;
6. verify malformed `/api/analyze-audio-tab` fails closed with 400 before analyzer invocation;
7. preserve exact smoke evidence and inspect Preview runtime logs;
8. never use `--prod`, aliases, promotion, Production mutation, `main`, GOAT/GuitarSet/SplitMySong, restricted/reference audio, Modal, GPU, CUDA, or reference scoring.

## Safety accounting through this checkpoint

- exact branch/SHA Vercel Preview deployment READY = true;
- attempt-1 deployment was Preview/non-Production = true;
- Deployment Protection disabled = false;
- Vercel Production deployment created/modified by this work = false;
- Preview-to-Production promotion = false;
- Production aliases/domains/env changed = false;
- `main` modified = false;
- external/reference assets read = false;
- GuitarSet read = false;
- SplitMySong read = false;
- GOAT restricted bytes read = false;
- reference score calls = 0;
- Modal invoked/deployed = false;
- GPU/CUDA = false.

## NEXT SAFE ACTION

1. Apply only the global Vercel CLI `--token` placement correction in `.github/workflows/v143-exact-branch-vercel-preview.yml`.
2. Inspect exact corrected Preview and branch-build runs on the new SHA.
3. If protected route smoke is green, inspect Vercel Preview runtime logs for `/ai-tab`, `/api/analyze-audio-tab`, and `/api/generate-tab-preview`.
4. Create a dedicated protected Preview result checkpoint and update this file with exact run/job/deployment/route/PDF evidence.
5. **Do not merge to `main`, assign Production aliases, use `--prod`, or promote/deploy Vercel Production without fresh explicit user authorization.**
6. No reference-facing accuracy score until a lawful holdout exists; GOAT owner approval remains pending; terminal SplitMySong/GuitarSet phases remain closed.
