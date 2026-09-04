# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-03 (America/Toronto)  
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

**Project Progress Score: 72%.**  
**Test Score: PHASE 1–13 GREEN; EXACT-BRANCH VERCEL PREVIEW AUTHORIZED AND FIRST DEPLOYMENT ATTEMPT REACHED VERCEL WITH EXACT PROVENANCE BUT HIT AN UNRELATED DEBUG-FUNCTION PACKAGING LIMIT; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Phases 1–11 — COMPLETE

- Phase 1–7 reference-blind conditioning/shadow/mixture/analyzer chain: all frozen workflow gates **SUCCESS**.
- Phase 8 server observation admission: run `33827081887`, job `100881934408`, **SUCCESS**; final branch gate `33827731955`, job `100883875983`, **SUCCESS**.
- Phase 9 admitted shadow effect: run `33828829026`, job `100887194463`, **SUCCESS**.
- Phase 10 Product-placement candidate: run `33829600963`, job `100889565032`, **SUCCESS**; synthetic placement 0% -> 100%, 7/7 exact.
- Phase 11 live candidate canary: run `33830896322`, job `100893491799`, **SUCCESS**.

## Phase 12 — CANONICAL PRODUCT/PDF PLACEMENT PROMOTION CLOSED GREEN

Canonical workflow:
- run `33831663771`;
- job `100895770003`;
- tested head `fdd54716641d2df73e5794cd3abadf06e78da208`;
- **SUCCESS**;
- R1–R16 = 16/16 PASS;
- matrix = 12/12 PASS;
- structured renderer = `v143-structured-rhythm`;
- structured PDF bytes = **1,665,393**;
- deterministic promotion = **0 -> 7**;
- exact known-truth placement = **7/7**.

Result: `docs/checkpoints/SONGSTERR_FULL_MIXTURE_PRODUCT_PLACEMENT_CANONICAL_PROMOTION_V1_PHASE12_RESULT_20260903.md`.

## Phase 13 — BUILT-NEXT CANONICAL PROMOTION HTTP GATE CLOSED GREEN

Authoritative workflow:
- run `33833707924`;
- job `100901804298`;
- tested head `ed776202b60ee410beb455db16ee820e260ff17b`;
- **SUCCESS**;
- analyzer-quality verifier PASS;
- Preview feature verifier PASS;
- locked install PASS;
- full Next build PASS, 95/95 static pages;
- built server readiness PASS;
- existing route smoke PASS;
- analysis -> canonical promotion -> Product/PDF HTTP PASS;
- final safety enforcement PASS.

Canonical HTTP proof:
- analysis status **200**;
- Rhythm canary active = true;
- promotion = `PROMOTED_PLACEMENT_ONLY`;
- canonical placement **0 -> 7**;
- exact known-truth placement **7/7**;
- canonical generated tab unchanged = true;
- Product/PDF status **200**;
- feature = `v143-branch-preview-canary`;
- renderer = `v143-structured-rhythm`;
- structured PDF bytes = **1,665,404**;
- malformed analysis request fails closed with **400**.

Result: `docs/checkpoints/SONGSTERR_V143_BUILT_NEXT_CANONICAL_PROMOTION_HTTP_GATE_PHASE13_RESULT_20260903.md`.  
Result checkpoint commit: `977c6113521e4942a57d047ccbb1e962bf7b7e2d`.

## Exact-branch Vercel Preview — AUTHORIZED / DEPLOYMENT PACKAGING FIX IN VALIDATION

Authorization freeze:
`docs/checkpoints/SONGSTERR_V143_EXACT_BRANCH_VERCEL_PREVIEW_AUTHORIZATION_FREEZE_20260903.md`.

User authorized Preview-only deployment/validation for `v143-contextual-prune-lobo`. Production and `main` remain outside scope.

Branch-local Git intent:
- `vercel.json` commit `cd301274743dc63a59678979ea1c3a28704e19ac` sets `git.deploymentEnabled.v143-contextual-prune-lobo=true` with no wildcard rule.
- Native Vercel Git integration still emitted no Preview check/deployment.

Exact-SHA Preview workflow:
- `.github/workflows/v143-exact-branch-vercel-preview.yml`;
- workflow commit `fef8f257cca86a292f12566282c616e31b83fdf4`;
- branch restricted;
- exact SHA checkout/assertion;
- pinned Vercel CLI `59.11.2`;
- `vercel pull --environment=preview`;
- Preview build;
- `vercel deploy --prebuilt` only;
- no `--prod` or promotion path.

### Attempt 1 — fail closed before deployment

Run `33834282584`, original job `100903471300`:
- exact checkout PASS;
- branch/SHA assertion PASS;
- `VERCEL_TOKEN` absent -> fail closed before Vercel CLI/build/deploy;
- deployment created = false.

User then configured GitHub Actions secret `VERCEL_TOKEN` without exposing it in chat/source.

### Attempt 2 — exact Preview artifact reached Vercel; unrelated packaging limit

Same workflow run, rerun job `100906445715`:
- exact checkout `fef8f257cca86a292f12566282c616e31b83fdf4` PASS;
- branch/SHA/Preview-only authority guard PASS;
- Vercel token guard PASS;
- pinned Vercel CLI install PASS;
- Preview project configuration pull PASS;
- exact branch Preview build PASS;
- Vercel accepted deployment `dpl_CBH5ZoCRuHAejxyb6UjHgZ9b38U3`;
- deployment URL `dadrock-tabs-android-lwbjccpfk-stephen-mcnally-s-projects.vercel.app`;
- Git metadata exact branch = `v143-contextual-prune-lobo`;
- Git metadata exact SHA = `fef8f257cca86a292f12566282c616e31b83fdf4`;
- explicit metadata `dadrockBranch` / `dadrockCommit` also matched;
- Vercel deployment failed before readiness with `NOW_SANDBOX_WORKER_MAX_UNCOMPRESSED_FUNCTION_SIZE`;
- offending unrelated development-only function: `/api/debug/v7-polished-proof` = **424.34 MB** uncompressed > 250 MB;
- Production modified = false;
- Production promotion = false.

Vercel build log reached `Using prebuilt build artifacts from .vercel/output` and `Deploying outputs...` before rejecting the oversized debug function.

The debug route is identical to `main` and explicitly returns 404 when `NODE_ENV=production`, but it had a top-level import of `createTabPdfPolishedV7`. The branch also contains large research artifacts under `public/` that are absent from `main`; the PDF stack reads the DadRock logo from `public/`, making the disabled debug route's trace unnecessarily large on this branch.

Narrow packaging fix:
- commit `68f1ced54b3888890ba11f11120b48479b8a57a4`;
- only `app/api/debug/v7-polished-proof/route.js` changed;
- removed top-level V7 PDF import;
- dynamically loads `createTabPdfPolishedV7` only after the existing production 404 guard;
- canonical analysis/Product/PDF runtime path unchanged;
- no large-function beta enabled;
- no Production setting changed.

This fix is now awaiting branch-build + exact-Preview validation.

## Safety accounting through current checkpoint

- at least one Vercel Preview-targeted deployment artifact reached Vercel, but READY Preview has **not** yet been accepted;
- exact branch/SHA provenance for the failed deployment was proven;
- Vercel Production deployment created/modified = false;
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

1. Validate commit `68f1ced54b3888890ba11f11120b48479b8a57a4` through the normal branch build gate.
2. Validate the exact-SHA Vercel Preview workflow triggered by that commit.
3. Accept only a Vercel deployment that reaches READY and proves Preview target plus exact branch/SHA provenance.
4. Test `/ai-tab` and the Preview Product/PDF route on that deployment.
5. Record a dedicated exact-branch Vercel Preview result checkpoint and update this file.
6. Do **not** merge `main` or promote/deploy Vercel Production without fresh explicit user authorization.
