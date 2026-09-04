# V143 EXACT-BRANCH VERCEL PREVIEW — AUTHORIZATION FREEZE

Date: 2026-09-03 (America/Toronto)  
Branch: `v143-contextual-prune-lobo`

Status: **AUTHORIZED / PREVIEW-ONLY / MAIN+PRODUCTION_FROZEN**

## User authorization

The user explicitly authorized the next frozen authority crossing after Phase 12 closure.

This authorization is interpreted narrowly as permission to wire, create, inspect, and validate a **Vercel Preview deployment sourced from the exact `v143-contextual-prune-lobo` branch**.

Authorization begins from branch head:

`f85d8bcde3ee3f44dca9a4d2546378f2f584a8fa`

## Authorized operations

- inspect the connected Vercel project and existing Git linkage;
- inspect Preview deployments and branch metadata;
- create or trigger a Vercel **Preview** deployment for `v143-contextual-prune-lobo` when needed;
- validate the resulting Preview build/runtime behavior;
- add branch-local deterministic validation/checkpoint artifacts needed to prove the Preview boundary;
- update branch checkpoints with exact deployment evidence.

## Still forbidden without fresh explicit authorization

- merge or commit to `main`;
- Production deployment;
- `vercel --prod` or equivalent production target;
- promote any Preview deployment to Production;
- assign or modify Production aliases/domains;
- modify Production environment variables or Production project settings;
- use Modal/GPU/CUDA;
- read restricted/reference assets (GOAT/GuitarSet/SplitMySong or other sealed reference bytes);
- run reference-facing scoring;
- weaken any previously frozen anti-leakage, quality, or scientific boundary.

## Safety intent

The exact-branch Preview is a deployment/runtime integration gate only. It must remain reference-blind and may not be represented as a production promotion or transcription-accuracy validation.
