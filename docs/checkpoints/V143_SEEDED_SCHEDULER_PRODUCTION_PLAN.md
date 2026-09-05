# V143 Seeded Scheduler — Production Integration / Deploy Plan

Date: 2026-09-05 America/Toronto  
Branch: `v143-contextual-prune-lobo`

## Decision

Use a **worker-only Modal redeploy** from the already-proven branch source. Do **not** merge the divergent branch into `main`, do **not** redeploy Vercel, and do **not** redeploy the HTTP bridge.

The branch is 139 commits ahead and 227 commits behind `main`, so a whole-branch merge is explicitly rejected as an integration mechanism.

## Why worker-only is sufficient

The normal-routing composition proof established these exact source identities:

- Vercel route `app/api/analyze-audio-tab/route.js` blob `06234db3e1cc1680b18fd62a765862b213ede3db`;
- HTTP bridge `analyzer/v143_modal_http_endpoint.py` blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`;
- live worker `analyzer/v143_modal_live_endpoint.py` blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`;
- deterministic wrapper `analyzer/v143_deterministic_separator.py` blob `28b3e6fe0eb761178b142cf7dcbda533f0bf918d`;
- seeded scheduler candidate `analyzer/v143_seeded_separator.py` blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.

The current `main` Vercel route already has blob `06234db...`; no Vercel source change is required.

The bridge dynamically resolves Modal app `dadrock-v143-ai-tab-live`, function `rhythm_v143_request`; no bridge source change is required.

The live endpoint blob immediately before the scheduler candidate and now is the same `111bf14a...`. The candidate production delta is therefore the scheduler implementation packaged into the worker image, not a request-contract change.

## Exact promotion target

Deploy only:

`modal deploy --env main analyzer/v143_modal_live_endpoint.py`

from a branch commit that satisfies all of the following exact pins before deployment:

- `analyzer/v143_modal_live_endpoint.py` = `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- `analyzer/v143_seeded_separator.py` = `fc9b4c45c208d80be7abab64a8959f2a3babcee8`
- `analyzer/v143_deterministic_separator.py` = `28b3e6fe0eb761178b142cf7dcbda533f0bf918d`
- `analyzer/v143_rhythm_deterministic_stem_provider.py` = `3c6dcf9b8e7360ba1dd886810f3c14c05ac0579b`
- `analyzer/v143_rhythm_stem_provider.py` = `cd180bfb35e8110f031504035af5f11e502c3dc6`
- `analyzer/v143_vercel_audio_request_adapter.py` = `6d1787f34a3b7ca781ced8e5695993a3777406a8`
- `analyzer/v143_modal_rhythm_router.py` = `7849f33cd3b849283ccebfda9f721cc40704231e`

The deploy workflow must fail closed if any pin differs.

## Promotion trigger

Harden `.github/workflows/v143-deploy-patched-worker.yml` in the same commit that triggers deployment:

- keep deployment serialized (`cancel-in-progress: false`);
- pin exact source Git-blob identities above before any Modal write;
- record the deployment source commit;
- deploy only `dadrock-v143-ai-tab-live` through `v143_modal_live_endpoint.py`;
- do not deploy/stop the HTTP bridge;
- do not touch Vercel;
- do not invoke an approved audio fixture or separator model as part of deployment verification.

Because that existing workflow triggers only when its own file changes, the hardening commit is the deliberate production promotion trigger.

## Post-deploy verification — no audio/model recomputation

Run the existing `rhythm_dependency_smoke` on deployed app `dadrock-v143-ai-tab-live` and require:

- `cudaAvailable=true`;
- `deviceName="NVIDIA L4"`;
- deterministic separator seed `143`;
- `referenceFree=true`;
- frozen Demucs/BS-RoFormer model identifiers and `demucsShifts=1`;
- Basic Pitch, bend evidence, bend consensus, legato evidence, and deterministic provider imports all true.

Preserve aggregate deployment evidence only. Do not upload audio/stems/events/generated tabs/reference material.

The Vercel route and bridge are unchanged and already source-pinned by Gate 3A, so no extra model-bearing end-to-end request is justified solely for promotion.

## Rollback

Concrete source rollback target: commit `2ab73f0e445c1584fc6dce0112e3091985b4a575`.

At that commit:

- live endpoint blob remains `111bf14a8f91045d3478901f8e36b88a2e7f181a`;
- seeded separator blob is the pre-candidate serialized implementation `250534e516cad36e49cae35b6eab2b88654be2d3`.

If deployment or no-model dependency smoke fails because of the candidate deployment, redeploy `analyzer/v143_modal_live_endpoint.py` from that exact rollback commit. Do not alter Vercel or the bridge as part of rollback.

## Promotion evidence already closed

- Gate 1 scheduler structure: GREEN/CLOSED.
- Gate 2 exact approved-fixture runtime: GREEN/CLOSED.
- Gate 3A normal-routing source composition: GREEN/CLOSED.
- Additional pre-deploy model-bearing E2E: `MODEL_BEARING_E2E_NOT_JUSTIFIED`.
- Normal-routing pre-production promotion evidence boundary: GREEN/CLOSED.

## Safety invariants

- reference-facing inputs = `0`;
- reference score calls = `0`;
- quality verdict made = `false`;
- GOAT restricted bytes = `0`;
- GuitarSet sealed assets untouched;
- SplitMySong remains terminal;
- no persistent user-audio/stem/result retention;
- Vercel deployment unchanged;
- HTTP bridge deployment unchanged;
- `main` merge not required for this worker-only promotion.

## Execution order

1. Checkpoint this plan.
2. Harden the existing worker deployment workflow with exact source pins and no-model verification.
3. Let that workflow-file commit deliberately trigger one serialized worker-only production deployment.
4. Inspect terminal workflow result + aggregate deployment artifact.
5. If GREEN, checkpoint production worker promotion CLOSED/GREEN.
6. If deployment/smoke fails, diagnose first; rollback to `2ab73f...` only if the deployed candidate is implicated.
