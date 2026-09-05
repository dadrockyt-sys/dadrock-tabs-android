# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 12:56 America/Toronto  
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

## Preview async breakthrough E2E — PROTECTION PREFLIGHT BLOCKED / ZERO MODEL STARTS

### Attempt 1 — historical Preview

Workflow `.github/workflows/v143-preview-async-breakthrough-e2e.yml`, commit `27d9af18496888564eec32f8858b29c4b988e4c9`, run `33982105469`, job `101349042393`.

- exact source fingerprints GREEN;
- historical Preview `dpl_FzuFoFNsaZcaV73RXSTejoH6cLpz` still target `preview`, Ready;
- `vercel curl /ai-tab` returned HTTP 403;
- model-bearing step skipped;
- model start count = 0.

### Attempt 2 — fresh Preview

Workflow `.github/workflows/v143-fresh-preview-async-breakthrough-e2e.yml`, commit `58be9aa7b5606783a508917ce4531cfd512d66da`, run `33982235357`, job `101349393362`.

- exact source fingerprints GREEN;
- current Preview branch environment pulled;
- local Next 16.1.6 build GREEN;
- fresh Preview-only deployment GREEN:
  - ID **`dpl_F6ksguDvc1nVAt33jNxxoVTmyyJA`**;
  - URL `https://dadrock-tabs-android-r602jctx9-stephen-mcnally-s-projects.vercel.app`;
  - target `preview`, status Ready;
  - production promotion=false;
- protected `vercel curl /ai-tab` again returned **HTTP 403**;
- model-bearing start step skipped;
- model start count remains **0 total**;
- no job token, audio/model execution, or transcription artifact was created.

Fresh deployment therefore rules out stale Preview state. The remaining blocker is specifically **Deployment Protection automation authentication from GitHub Actions**, not Modal async routing, build output, or deployment freshness.

## Deployment Protection authentication diagnosis

Live Vercel documentation confirms supported protected-automation methods:

1. Protection Bypass for Automation via `VERCEL_AUTOMATION_BYPASS_SECRET` and `x-vercel-protection-bypass` header; or
2. Trusted Sources / GitHub Actions OIDC via `id-token: write`, `core.getIDToken()`, and `x-vercel-trusted-oidc-idp-token` header.

Do not disable/weaken Deployment Protection. Prefer a configured Trusted Sources OIDC path; if unavailable, use only an already-configured automation bypass secret, never expose it and never alter Production protection merely for the test.

## NEXT STEP — AUTH-ONLY PROBE BEFORE THE ONE MODEL START

1. Run a no-model/no-audio protected-access probe against fresh Preview `dpl_F6ksguDvc1nVAt33jNxxoVTmyyJA` using GitHub Actions OIDC as documented by Vercel.
2. If OIDC returns 200, use the same header on start/status/ACK in the single E2E workflow.
3. If OIDC is not trusted, probe whether an existing `VERCEL_AUTOMATION_BYPASS_SECRET` GitHub secret is configured without printing it; if present, use the documented bypass header.
4. Only after protected `/ai-tab` = 200 may the first and only model-bearing Rhythm start occur.
5. Poll same token beyond 150s if required; require terminal tab + safety contract + ACK cleanup.
6. Any post-start failure => diagnose, never rerun model automatically.

Approved source remains `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, Git blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`.

### Hard stops

- **Model/audio start requests so far = 0; budget remaining = 1.**
- No Production Vercel environment change/promotion.
- No Deployment Protection weakening/disablement.
- No model/scheduler change.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL above 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.
