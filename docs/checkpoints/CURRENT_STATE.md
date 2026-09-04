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
**Test Score: PHASE 1–13 GREEN; EXACT-BRANCH VERCEL PREVIEW READY; PROTECTED REAL-VERCEL ROUTE SMOKE IN PROGRESS; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

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

Canonical deployed application source:
- exact deployed SHA: **`df3042180e57df1031a2a529961388a6419d1bc5`**;
- workflow run **`33836754320`**, job **`100910747161`**;
- deployment ID **`dpl_HEQHX2nfFhYJzsMMEsAa8ePhcQpX`**;
- hostname `dadrock-tabs-android-a45v6ibzb-stephen-mcnally-s-projects.vercel.app`;
- state / readyState **READY**;
- target `null` = Preview/non-Production;
- Vercel Git branch `v143-contextual-prune-lobo`;
- Vercel Git SHA `df3042180e57df1031a2a529961388a6419d1bc5`;
- Production target/promotion **not used**.

The later branch head at continuation start was `5cf7218f222d4f38423d6af2b559646d20d7fe18`. A compare from `df304218...` to that head showed **2 commits ahead and only `docs/checkpoints/CURRENT_STATE.md` changed**. Therefore no runtime/config/workflow drift invalidated the canonical READY deployment.

## Protected real-Vercel Preview smoke — continuation state

Direct connector fetches to the protected Preview return **302** to Vercel SSO. A temporary `_vercel_share` URL is generated successfully, but the available fetch path does not retain the SSO cookie; this is a tooling/auth-cookie limitation, not an application-route failure.

Current Vercel documentation confirms `vercel curl` can issue requests to a specific Preview deployment and automatically handle deployment-protection bypass when authenticated with the existing `VERCEL_TOKEN`.

### Frozen implementation plan

Extend only `.github/workflows/v143-exact-branch-vercel-preview.yml` on this authorized branch to add an authenticated **Preview-only** post-deploy smoke using pinned Vercel CLI `59.11.2` and the already-configured repository secret `VERCEL_TOKEN`.

The smoke must:
1. preserve exact branch/SHA guards and `--prebuilt` Preview-only deployment;
2. use `vercel curl ... --deployment "$VERCEL_PREVIEW_URL"` rather than disabling protection;
3. verify `/ai-tab` returns 200 through authenticated protection bypass;
4. POST a deterministic, reference-blind structured Rhythm fixture directly to `/api/generate-tab-preview` (safe equivalent to the Phase 13 canonical Product/PDF payload; no external/reference audio and no analyzer invocation required);
5. verify HTTP 200, `application/pdf`, `%PDF`, nontrivial byte count, feature `v143-branch-preview-canary`, renderer `v143-structured-rhythm`;
6. verify malformed `/api/analyze-audio-tab` fails closed with 400 before analyzer invocation;
7. optionally preserve a fallback Product/PDF check if it remains deterministic and reference-blind;
8. write/upload exact smoke evidence with branch, SHA, deployment URL/ID if available, statuses, headers, PDF bytes, and all safety counters;
9. never use `--prod`, aliases, promotion, Production mutation, `main`, GOAT/GuitarSet/SplitMySong, restricted/reference audio, Modal, GPU, CUDA, or reference scoring.

Changing the Preview workflow file will create a newer exact branch SHA and will intentionally trigger both the exact-branch Preview workflow and the normal branch build gate. Any new Preview deployment remains non-Production and must be verified against that exact new SHA.

## Safety accounting through this checkpoint

- exact branch/SHA Vercel Preview deployment READY = true;
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

1. Patch `.github/workflows/v143-exact-branch-vercel-preview.yml` with the authenticated `vercel curl` smoke above.
2. Let the branch-scoped push triggers run; inspect the exact new Preview run and the normal branch build gate.
3. Read preserved smoke evidence and Vercel Preview runtime logs for `/ai-tab`, `/api/analyze-audio-tab`, and `/api/generate-tab-preview`.
4. If green, create a dedicated exact-branch protected Preview result checkpoint and update this file with exact run/job/deployment/route/PDF evidence.
5. If a branch-only defect appears, patch only the attributable Preview/runtime issue and re-run on the exact new head.
6. **Do not merge to `main`, assign Production aliases, use `--prod`, or promote/deploy Vercel Production without fresh explicit user authorization.**
7. No reference-facing accuracy score until a lawful holdout exists; GOAT owner approval remains pending; terminal SplitMySong/GuitarSet phases remain closed.
