# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-03 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## Global scientific state — unchanged

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**
- GOAT Zenodo `15690894` / DOI `10.5281/zenodo.15690894` v1 access still awaits explicit owner approval/denial.
- Restricted GOAT bytes admitted/read = **0**; V168 prospective reference-facing score calls = **0**.
- SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`; never rerun/score/weaken/interpolate.
- GuitarSet V3/V4/V5 remain terminal; development hold remains frozen; prospective players `00/01/03` remain sealed and prospective score calls = **0**.
- CPU only for Phase 10–13. No GPU/CUDA/Modal was used.
- `main` and Vercel Production remain untouched.

**Project Progress Score: 72%.**  
**Test Score: PHASE 1–13 GREEN; EXACT-BRANCH VERCEL PREVIEW AUTHORIZED BUT BLOCKED BEFORE DEPLOYMENT BY ACCOUNT/CREDENTIAL CONFIGURATION; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Phases 1–11 — COMPLETE

- Phase 1–7 reference-blind conditioning/shadow/mixture/analyzer chain: all frozen workflow gates **SUCCESS**.
- Phase 8 server observation admission: run `33827081887`, job `100881934408`, **SUCCESS**; final branch gate `33827731955`, job `100883875983`, **SUCCESS**.
- Phase 9 admitted shadow effect: run `33828829026`, job `100887194463`, **SUCCESS**.
- Phase 10 Product-placement candidate: run `33829600963`, job `100889565032`, **SUCCESS**; synthetic placement 0% -> 100%, 7/7 exact.
- Phase 11 live candidate canary: run `33830896322`, job `100893491799`, **SUCCESS**; C1–C12 + 12-case matrix + safety gate + `npm ci` + full Next.js build all passed.

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

Freeze: `docs/checkpoints/SONGSTERR_V143_BUILT_NEXT_CANONICAL_PROMOTION_HTTP_GATE_PHASE13_PREIMPLEMENTATION_FREEZE_20260903.md`.

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

## Exact-branch Vercel Preview — AUTHORIZED / FAIL-CLOSED BLOCKED BEFORE DEPLOYMENT

Authorization freeze:

`docs/checkpoints/SONGSTERR_V143_EXACT_BRANCH_VERCEL_PREVIEW_AUTHORIZATION_FREEZE_20260903.md`

User authorized Preview-only deployment/validation for `v143-contextual-prune-lobo`. Production and `main` remain outside scope.

### Native Git attempt

Vercel project:
- project `dadrock-tabs-android`;
- project ID `prj_6biwsn0iHci6FHNswAUCS8UYrAqF`;
- team ID `team_qJrw8Cuze5bCEg9M3Q67XMWt`;
- existing latest deployment target = Production, untouched.

Branch-local Vercel Git intent was made explicit in `vercel.json` at:

`cd301274743dc63a59678979ea1c3a28704e19ac`

with `git.deploymentEnabled.v143-contextual-prune-lobo=true`, preserving existing cron/header behavior and adding no wildcard rules.

Result:
- no Vercel Preview deployment;
- no Vercel Git check on the branch commit;
- Vercel deployment list remained Production-only;
- therefore the blocker is at the project/Git-integration account layer, not Phase 13 or the branch-local rule.

### Connected deploy-action attempt

The connected Vercel deploy action is currently schema-inconsistent: its exposed callable has no arguments, while its backend requires deployment `target`, `name`, and `files`. The attempted empty invocation failed input validation before deployment. No Preview or Production deployment was created.

### Exact-SHA GitHub Actions fallback

Committed Preview-only workflow:

`.github/workflows/v143-exact-branch-vercel-preview.yml`

Workflow commit:

`fef8f257cca86a292f12566282c616e31b83fdf4`

It is branch restricted, checks out exact `${{ github.sha }}`, asserts branch/SHA before deployment, pins Vercel CLI 59.11.2, pulls Preview configuration, builds, and uses only `vercel deploy --prebuilt` with no Production promotion path.

Attempted run:
- run `33834282584`;
- job `100903471300`;
- exact head `fef8f257cca86a292f12566282c616e31b83fdf4`;
- exact checkout PASS;
- branch/SHA assertion PASS;
- credential guard FAIL-CLOSED: **`VERCEL_TOKEN` repository secret is not configured**;
- Vercel CLI install skipped;
- Vercel pull skipped;
- Vercel build skipped;
- Vercel deploy skipped;
- deployment created = **false**.

Dedicated blocker checkpoint:

`docs/checkpoints/SONGSTERR_V143_EXACT_BRANCH_VERCEL_PREVIEW_BLOCKED_20260903.md`  
Checkpoint commit: `01dbc682b1a92172d642da9140925fb9a0e57dac`.

### External prerequisite now required

Either:
1. enable native Vercel Git Preview deployments for this branch in the connected Vercel project; or
2. add a GitHub Actions repository secret named `VERCEL_TOKEN`, authorized for the existing team/project.

The token must be stored in GitHub Actions Secrets and must not be pasted into chat or committed to source.

Once either prerequisite exists, rerun `V143 Exact Branch Vercel Preview` and accept the resulting deployment only after proving Preview target and exact expected branch/SHA provenance.

## Safety accounting through current head

- Vercel Preview deployment created = false;
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

1. Keep branch `v143-contextual-prune-lobo` and all Phase 1–13 gates frozen.
2. Wait only on the external Vercel Preview prerequisite: native Git Preview enablement or GitHub Actions `VERCEL_TOKEN` secret.
3. Once configured, rerun `V143 Exact Branch Vercel Preview`.
4. Inspect the created deployment; require `target=preview` plus exact branch/SHA provenance before accepting it.
5. Validate `/ai-tab` on that Preview and record deployment/runtime evidence.
6. Do **not** merge `main` or promote/deploy Vercel Production without fresh explicit user authorization.
