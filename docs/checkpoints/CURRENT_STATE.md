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
**Test Score: PHASE 1–13 GREEN; EXACT-BRANCH VERCEL PREVIEW IS NOW READY ON THE AUTHORIZED BRANCH/SHA; PROTECTED PREVIEW ROUTE SMOKE STILL TO BE COMPLETED; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

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

## Exact-branch Vercel Preview — AUTHORIZED / READY

Authorization freeze:
`docs/checkpoints/SONGSTERR_V143_EXACT_BRANCH_VERCEL_PREVIEW_AUTHORIZATION_FREEZE_20260903.md`.

User authorized Preview-only deployment/validation for `v143-contextual-prune-lobo`. Production and `main` remain outside scope.

### Preview deployment mechanism

- `.github/workflows/v143-exact-branch-vercel-preview.yml`;
- branch restricted to `v143-contextual-prune-lobo`;
- exact SHA checkout/assertion;
- repository secret `VERCEL_TOKEN` configured by user without exposing it in chat/source;
- pinned Vercel CLI `59.11.2`;
- `vercel pull --environment=preview`;
- `vercel build`;
- `vercel deploy --prebuilt` only;
- no `--prod` or promotion path.

### Earlier packaging failures — resolved

Attempt at `fef8f257cca86a292f12566282c616e31b83fdf4` reached Vercel but failed because `/api/debug/v7-polished-proof` traced to **424.34 MB** > Vercel 250 MB function limit.

A narrow dynamic-import fix moved the failure to the real `/api/generate-tab-pdf` function (**426.03 MB**), proving the remaining issue was branch research-asset trace pollution rather than Phase 12/13 promotion logic.

Subsequent route-specific output-tracing isolation excluded non-runtime research assets from PDF function traces while preserving the actual DadRock PDF logo/runtime dependency. No Product/PDF behavior, transcription logic, `main`, or Production authority was changed.

### Canonical READY Preview

Deployed application source:
- branch: `v143-contextual-prune-lobo`;
- exact deployed SHA: **`df3042180e57df1031a2a529961388a6419d1bc5`**;
- commit message: `preview: isolate PDF traces from public research tree`.

Note: later commits that only update `docs/checkpoints/CURRENT_STATE.md` may make the Git branch head newer than this deployed application SHA. A fresh chat must re-fetch the branch and inspect any newer commits rather than assuming the branch head should equal `df304218...`.

GitHub Actions Preview workflow:
- workflow: `V143 Exact Branch Vercel Preview`;
- run: **`33836754320`**;
- job: **`100910747161`** (`deploy-preview`);
- event: push;
- deployed/tested head SHA: `df3042180e57df1031a2a529961388a6419d1bc5`;
- run conclusion: **SUCCESS**;
- job conclusion: **SUCCESS**.

Every deployment step passed:
1. exact authorized checkout — PASS;
2. branch/SHA/Preview-only authority guard — PASS;
3. Node setup — PASS;
4. pinned Vercel CLI install — PASS;
5. Preview project configuration pull — PASS;
6. exact branch Preview build — PASS;
7. exact prebuilt artifact Preview deployment — PASS;
8. wait + Vercel deployment inspect — PASS;
9. exact-SHA evidence record — PASS;
10. evidence preservation — PASS.

Vercel deployment:
- deployment ID: **`dpl_HEQHX2nfFhYJzsMMEsAa8ePhcQpX`**;
- hostname: `dadrock-tabs-android-a45v6ibzb-stephen-mcnally-s-projects.vercel.app`;
- state / readyState: **READY**;
- target: `null` = Preview/non-Production deployment;
- source: CLI;
- project: `dadrock-tabs-android`;
- framework: Next.js;
- region: `iad1`;
- Vercel Git metadata branch: `v143-contextual-prune-lobo`;
- Vercel Git metadata SHA: `df3042180e57df1031a2a529961388a6419d1bc5`;
- explicit `dadrockBranch` metadata matches;
- explicit `dadrockCommit` metadata matches;
- aliases: none;
- Production target/promotion: **not used**.

### Protected-route verification status

A direct connector fetch of the READY Preview `/ai-tab` endpoint returned **302** to Vercel SSO because Preview Deployment Protection is active. This is expected protection behavior and is **not** an application-route failure.

Vercel authenticated-share access was generated, but this connector request path still redirected through the SSO cookie flow, so the actual protected `/ai-tab` page and protected Product/PDF HTTP route have **not yet been accepted as externally smoke-tested on the real Vercel Preview**.

The equivalent compiled local built-Next path remains green from Phase 13.

## Safety accounting through current checkpoint

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

## NEXT SAFE ACTION — FRESH CHAT HANDOFF

1. Re-read this file and re-fetch the current `v143-contextual-prune-lobo` branch head before making changes. The canonical READY Preview is tied to application SHA `df3042180e57df1031a2a529961388a6419d1bc5`; newer **checkpoint-only** commits do not invalidate that deployment, but any newer runtime/config/workflow changes must be inspected and, if relevant, redeployed/tested.
2. Treat deployment `dpl_HEQHX2nfFhYJzsMMEsAa8ePhcQpX` as the canonical exact-branch READY Preview for this checkpoint.
3. Complete **protected real-Vercel Preview smoke validation** without changing Production:
   - access the Preview through an authenticated Vercel session/share mechanism that can retain the SSO cookie;
   - verify `/ai-tab` loads successfully;
   - verify the Preview branch feature is active;
   - exercise a deterministic/reference-blind analysis fixture or safe equivalent through the real Preview route;
   - verify promoted canonical `renderEvents` reach the real Preview Product/PDF route;
   - verify structured renderer `v143-structured-rhythm` and nontrivial PDF bytes;
   - do not use restricted/reference audio, GOAT, GuitarSet, SplitMySong, Modal, GPU, CUDA, or reference scoring.
4. Inspect Vercel Preview runtime logs during/after that smoke for 4xx/5xx/function errors attributable to `/ai-tab`, `/api/analyze-audio-tab`, `/api/generate-tab-preview`, or `/api/generate-tab-pdf`.
5. If the real Preview smoke is green, create a dedicated exact-branch Vercel Preview result checkpoint under `docs/checkpoints/` and update this file with the exact deployment/run/job/route/PDF evidence.
6. If the Preview smoke exposes a branch-only defect, patch only the attributable Preview/runtime issue, rerun both the normal branch build gate and exact-SHA Preview workflow on the same new head, and re-test.
7. **Do not merge to `main`, assign Production aliases, use `--prod`, or promote/deploy Vercel Production without fresh explicit user authorization.**
8. No reference-facing accuracy score until a lawful holdout exists; GOAT owner approval remains pending; terminal SplitMySong/GuitarSet phases remain closed.
