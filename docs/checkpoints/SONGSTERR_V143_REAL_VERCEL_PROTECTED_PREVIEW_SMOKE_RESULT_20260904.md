# SONGSTERR V143 — REAL VERCEL PROTECTED PREVIEW SMOKE RESULT

Date: 2026-09-04 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`  
Status: **CLOSED GREEN**

## Purpose

Close the remaining real-hosting Preview boundary after Phase 13 by proving that the exact authorized branch can be built and deployed to a **protected Vercel Preview**, then exercised through Vercel Deployment Protection without weakening protection, touching Production, using reference audio, or invoking reference-facing scoring.

## Authoritative corrected gate

- workflow: `.github/workflows/v143-protected-preview-smoke.yml`
- source commit: **`12567e284d76b5c95240ad823628e311df3fc5e3`**
- commit message: `preview: add corrected protected Preview smoke gate`
- workflow run: **`33843200741`**
- job: **`100929522781`** (`protected-preview-smoke`)
- conclusion: **SUCCESS**
- artifact: **`v143-protected-preview-smoke`**
- artifact ID: **`9925639186`**
- artifact SHA-256 reported by Actions: `ec0fbc1845a3aec922907e2eba2c64a03124fa6b3c932f07e0b8c71e8cdad155`

Every job step passed, including exact-SHA checkout/authority, pinned Vercel CLI install, Preview pull/build, prebuilt Preview deployment, Preview-target inspection, deterministic fixture creation, protected route exercise, evidence verification, and artifact preservation.

## Exact Vercel Preview deployment

- deployment ID: **`dpl_6pXryC9R7M5mJwZA7cUt2qh3bBsp`**
- URL: `https://dadrock-tabs-android-dmjmes0ly-stephen-mcnally-s-projects.vercel.app`
- Vercel state / readyState: **READY**
- Vercel CLI inspect target: **preview**
- connector target: `null` = Preview/non-Production
- aliases: **none**
- region: `iad1`
- source: CLI
- metadata branch: `v143-contextual-prune-lobo`
- metadata SHA: `12567e284d76b5c95240ad823628e311df3fc5e3`
- `dadrockBranch`: `v143-contextual-prune-lobo`
- `dadrockCommit`: `12567e284d76b5c95240ad823628e311df3fc5e3`

The Vercel build completed successfully with Next.js 16.1.6/Turbopack and generated **95/95 static pages**. Relevant routes were present: `/ai-tab`, `/api/analyze-audio-tab`, `/api/generate-tab-preview`, `/api/generate-tab-pdf`.

## Deployment Protection boundary

Deployment Protection remained enabled. The gate used authenticated `vercel curl` with the repository `VERCEL_TOKEN` supplied through the environment; no protection setting was disabled and no public alias was created.

A first diagnostic attempt on prior commit `d3439a20124e1982facde2732f18b88602e18625` had already proven that Vercel CLI could automatically generate the required deployment-protection bypass token, but that attempt failed before any app route because `--token` was placed where native curl received it (`curl: option --token=***: is unknown`). That attempt is not counted as application evidence.

The corrected gate removed the misplaced per-command token argument and succeeded through protection on all intended requests.

## Protected real-Vercel HTTP evidence

Deterministic, reference-blind Product/PDF fixture:

| Check | Result |
|---|---:|
| `/ai-tab` | **HTTP 200** |
| `/ai-tab` body | **38,016 bytes** |
| `/api/generate-tab-preview` | **HTTP 200** |
| Product content type | **`application/pdf`** |
| Product PDF magic | **`%PDF`** |
| Product feature | **`v143-branch-preview-canary`** |
| Product renderer | **`v143-structured-rhythm`** |
| Product PDF bytes | **1,665,759** |
| malformed `/api/analyze-audio-tab` | **HTTP 400** |
| malformed request fails before analyzer | **true** |
| protected smoke `passed` | **true** |

The structured Rhythm fixture was generated inside the workflow and contained only deterministic synthetic tab/render-event data. It did not contain or reference external audio.

## Vercel runtime-log corroboration

Runtime logs scoped to deployment `dpl_6pXryC9R7M5mJwZA7cUt2qh3bBsp` show exactly the expected smoke requests:

- `06:11:35Z` — `GET /ai-tab` -> **200** (`edge-middleware`, cache `PRERENDER`)
- `06:11:37Z` — `POST /api/generate-tab-preview` -> **200** (`serverless`, cache `MISS`)
- `06:11:41Z` — `POST /api/analyze-audio-tab` -> **400** (`serverless`, cache `MISS`)

No unexpected 5xx result appeared in the scoped smoke runtime log set.

## Independent branch gate corroboration

The workflow change that introduced the first protected-smoke attempt also triggered the normal branch build gate on application-equivalent source commit `d3439a20124e1982facde2732f18b88602e18625`:

- workflow run: **`33842848801`**
- job: **`100928482970`** (`verify-build-and-route-smoke`)
- conclusion: **SUCCESS**

All branch-gate stages passed: analyzer-quality verifier, Preview feature verifier, locked dependency install, full Next build, built-server readiness, built Preview route, canonical analysis-to-promotion-to-Product/PDF HTTP chain, compact evidence recording, safety enforcement, and shutdown.

Between `d3439a...` and corrected protected-smoke commit `12567e...`, only checkpoint/workflow infrastructure changed; no Product/analyzer runtime implementation was modified.

## Safety accounting

- actual Vercel Preview deployment used = **true**
- Deployment Protection disabled = **false**
- Production target used = **false**
- `--prod` used = **false**
- Preview promoted to Production = **false**
- Production aliases/domains/env modified = **false**
- `main` modified = **false**
- deterministic reference-blind fixture = **true**
- external/reference audio used = **false**
- real analyzer invocation requested by protected smoke = **false**
- malformed analysis rejected before analyzer = **true**
- GuitarSet read = **false**
- SplitMySong read = **false**
- GOAT restricted bytes read = **false**
- reference-facing score calls = **0**
- Modal invoked/deployed = **false**
- GPU/CUDA used = **false**

## Result

**REAL VERCEL PROTECTED PREVIEW SMOKE = CLOSED GREEN.**

The exact authorized branch has now been demonstrated through the real Vercel Preview boundary with Deployment Protection intact:

- page route reachable through authenticated protection bypass;
- structured Rhythm Product/PDF route returns the expected canary renderer and valid PDF;
- malformed analysis request fails closed with 400 before analyzer work;
- Vercel runtime logs corroborate the same request/status sequence;
- no Production/main/reference/scoring boundary was crossed.

## Next boundary

This result does **not** authorize Production promotion or merge to `main`. Production remains a separate decision requiring fresh explicit user authorization.

Reference-facing accuracy scoring also remains disarmed until a lawful holdout asset exists. V168 therefore remains `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; terminal SplitMySong/GuitarSet boundaries remain unchanged.
