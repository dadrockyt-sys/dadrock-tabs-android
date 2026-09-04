# V143 EXACT-BRANCH VERCEL PREVIEW — BLOCKED RESULT

Date: 2026-09-03 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`

Status: **`AUTHORIZED / PHASE13_GREEN / PREVIEW_NOT_CREATED / BLOCKED_BY_VERCEL_GIT_OR_CREDENTIAL_CONFIGURATION / FAIL_CLOSED / PRODUCTION_UNTOUCHED`**

## Authorization

The user explicitly authorized the exact-branch Vercel **Preview** authority crossing for `v143-contextual-prune-lobo`.

Authorization freeze:

`docs/checkpoints/SONGSTERR_V143_EXACT_BRANCH_VERCEL_PREVIEW_AUTHORIZATION_FREEZE_20260903.md`

The authorization remains Preview-only. `main`, Vercel Production, Production aliases/domains/environment settings, Modal/GPU/CUDA, restricted/reference assets, and reference-facing scoring remain outside scope.

## Precondition passed

Phase 13 built-Next canonical-promotion HTTP gate is closed green before this attempted authority crossing.

Authoritative Phase 13 evidence:

- run `33833707924`;
- job `100901804298`;
- tested head `ed776202b60ee410beb455db16ee820e260ff17b`;
- full build PASS;
- analysis -> canonical promotion -> Product/PDF HTTP PASS;
- promotion 0 -> 7;
- exact known-truth placement 7/7;
- structured renderer `v143-structured-rhythm`;
- structured PDF bytes 1,665,404;
- final safety enforcement PASS.

Phase 13 result checkpoint:

`docs/checkpoints/SONGSTERR_V143_BUILT_NEXT_CANONICAL_PROMOTION_HTTP_GATE_PHASE13_RESULT_20260903.md`

## Attempt 1 — native Vercel Git Preview wiring

The connected Vercel project was verified as:

- project: `dadrock-tabs-android`;
- project ID: `prj_6biwsn0iHci6FHNswAUCS8UYrAqF`;
- team ID: `team_qJrw8Cuze5bCEg9M3Q67XMWt`;
- framework: Next.js;
- existing latest deployment target: **Production**.

That existing Production deployment was never modified or promoted.

Multiple pushes to `v143-contextual-prune-lobo` had produced no Vercel Preview deployment and no Vercel Git check.

To make branch intent explicit without affecting other branches, `vercel.json` was updated at commit:

`cd301274743dc63a59678979ea1c3a28704e19ac`

with:

```json
"git": {
  "deploymentEnabled": {
    "v143-contextual-prune-lobo": true
  }
}
```

Existing cron and service-worker header configuration was preserved.

No wildcard rule was added because that could broaden or alter deployment behavior for `main`/other branches.

Result after the push:

- Vercel deployment list remained Production-only;
- no Vercel Git check appeared for `cd301274743dc63a59678979ea1c3a28704e19ac`;
- the branch head had only the pre-existing Cloudflare Pages check;
- therefore the suppression is above the branch-local `vercel.json` rule (project/Git integration configuration).

## Attempt 2 — connected Vercel deploy action

The connected deployment action could not be used safely because its exposed tool schema accepts no deployment arguments while the backend rejects invocation unless `target`, `name`, and `files` are supplied.

The empty invocation failed input validation before any deployment was created.

No Production or Preview deployment resulted from this attempt.

## Attempt 3 — exact-SHA GitHub Actions Preview path

A dedicated branch-local Preview workflow was added at commit:

`fef8f257cca86a292f12566282c616e31b83fdf4`

Workflow:

`.github/workflows/v143-exact-branch-vercel-preview.yml`

Frozen properties:

- branch restricted to `v143-contextual-prune-lobo`;
- checkout uses exact `${{ github.sha }}`;
- exact branch and SHA are asserted before deployment;
- Vercel CLI pinned to `59.11.2`;
- `vercel pull --environment=preview`;
- `vercel build`;
- `vercel deploy --prebuilt`;
- no Production flag or promotion command;
- branch/SHA metadata attached to the intended Preview;
- Production promotion authorization remains false.

Canonical attempted workflow run:

- run: `33834282584`;
- job: `100903471300` (`deploy-preview`);
- exact head: `fef8f257cca86a292f12566282c616e31b83fdf4`;
- checkout exact authorized commit: **PASS**;
- branch/SHA match before credential check: **PASS**;
- credential guard: **FAIL CLOSED** because `VERCEL_TOKEN` repository secret is not configured;
- Node/Vercel installation: skipped;
- Vercel project pull: skipped;
- Vercel build: skipped;
- Vercel deploy: skipped;
- deployment created: **false**.

The job log explicitly reports:

`VERCEL_TOKEN repository secret is not configured; failing closed before deployment.`

No token value was exposed because no token exists in the repository Actions secret context.

## Browser/UI fallback

The installed Vercel browser skill describes the `agent-browser` CLI, but that CLI is not present in the runtime. Attempts to obtain it through `npx` did not complete within the runtime limits, so no authenticated Vercel Project Settings browser session could be established.

No Vercel UI setting was modified.

## Safety result

Across the entire Preview attempt:

- Vercel Preview deployment created = **false**;
- Vercel Production deployment created = **false**;
- Preview promoted to Production = **false**;
- existing Production deployment modified = **false**;
- Production alias/domain/env changed = **false**;
- `main` modified = **false**;
- reference/restricted assets read = **false**;
- reference-facing score calls = **0**;
- Modal/GPU/CUDA used = **false**.

## Exact blocker

One of the following external account-level prerequisites must be supplied outside the current tool surface before the authorized Preview can be completed:

1. enable native Vercel Git Preview deployments for `v143-contextual-prune-lobo` in the connected project; **or**
2. configure a GitHub Actions repository secret named `VERCEL_TOKEN` with a Vercel token authorized for team `team_qJrw8Cuze5bCEg9M3Q67XMWt` / project `prj_6biwsn0iHci6FHNswAUCS8UYrAqF`.

The token should be stored directly in GitHub Actions Secrets and should not be pasted into chat or committed to the repository.

Once either prerequisite exists, the already-committed Preview-only workflow can be rerun and the resulting deployment must still be accepted only if inspection proves Preview target plus the expected branch/SHA provenance.

## Next safe action

Do not merge to `main` or deploy/promote Production.

After the external Preview prerequisite is configured, rerun `V143 Exact Branch Vercel Preview`, inspect the resulting deployment, validate `/ai-tab`, record deployment ID/URL/Preview target/branch/SHA/runtime evidence, and then update `CURRENT_STATE.md`.
