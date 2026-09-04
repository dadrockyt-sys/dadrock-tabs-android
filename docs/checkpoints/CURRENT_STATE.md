# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-04 (America/Toronto)  
Branch checkpoint: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## Global scientific state — unchanged

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**
- GOAT restricted bytes admitted/read = **0**; V168 prospective reference-facing score calls = **0**.
- SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`; never rerun/score/weaken/interpolate.
- GuitarSet V3/V4/V5 remain terminal; prospective players `00/01/03` remain sealed; prospective score calls = **0**.
- No reference-facing score was run during merge/Production/Modal work.

**Project Progress Score: 78%.**  
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 RHYTHM ROUTING PROVEN ACTIVE; FROZEN V143 MODAL L4 WORKER + HTTP BRIDGE RESTORED GREEN; NEXT = REPOINT PRODUCTION TO CORRECT BRIDGE AND RUN AGGREGATE-ONLY GOMYWAY SMOKE; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Closed green foundation

- Phases 1–13 reference-blind V143 chain: **GREEN**. Phase 13 run `33833707924`, job `100901804298`, structured renderer `v143-structured-rhythm`, malformed analysis 400, reference score calls 0.
- Protected real-Vercel Preview: run `33843200741`, job `100929522781`, deployment `dpl_6pXryC9R7M5mJwZA7cUt2qh3bBsp`, `/ai-tab` 200, structured PDF 200, Deployment Protection preserved, reference score calls 0.
- Detailed histories remain under `docs/checkpoints/`.

## User-authorized merge to `main` — COMPLETE

- authorization received 2026-09-04 to merge V143 and begin testing with existing “Are You Gonna Go My Way” audio;
- resolved two-parent merge `ceeccfbbb17968c097bb56136487e7ddeaf1a5a4` preserved newer BTS/SEO/payment/site work while overlaying tested V143 Phase 1–13 path;
- full combined build run `33844133380`, job `100932278526`: **SUCCESS**;
- current `main` source SHA remains **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**.

## Authorized existing Gomyway audio

- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`;
- blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`;
- 3,464,988 bytes.

## Production real-audio diagnostics so far

1. Product static URL returned 404 before analyzer: run `33844432185`, job `100933164743`.
2. Raw-GitHub URL reached Production but legacy analyzer was selected because V143 env was absent: run `33844704674`, job `100933970052`, runtime `usingV143RhythmAnalyzer: false`; route 502; no raw output/PDF retained.
3. Production `ANALYZER_API_URL_V143` was restored and exact current `main` rebuilt/redeployed: run `33879884350`, job `101056165576`; deployment **`dpl_CojGzPaq77YRh5mLpbVTEseuWjrg`**. Deployment Protection remained enabled.
4. Authenticated protected Production smoke: run `33880271454`, job `101057491176`; `/ai-tab` 200; analysis 502. Runtime proved:

```text
usingV143RhythmAnalyzer: true
Modal API returned 404 {}
```

Thus Vercel Production routing/config was fixed, but the configured Modal URL was obsolete.

## Correct V143 Modal topology — recovered and RESTORED GREEN

Frozen history commit `d40f2a2eaecd05a7ac094ce31fa427a1a9eb3096` proves the decoupled Production HTTP endpoint is:

**`https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`**

—not the older `dadrock-v143-ai-tab-live-analyze` worker-app URL.

Frozen source topology:

- `analyzer/v143_modal_live_endpoint.py`
  - app `dadrock-v143-ai-tab-live`;
  - function `rhythm_v143_request`;
  - NVIDIA L4;
  - deterministic separator seed 143;
  - reference-free; professional reference false; runtime labels false.
- `analyzer/v143_modal_http_endpoint.py`
  - app `dadrock-v143-http-bridge`;
  - web function `analyze`;
  - Lead/Bass retain existing legacy path;
  - Rhythm forwards via `modal.Function.from_name('dadrock-v143-ai-tab-live', 'rhythm_v143_request')`;
  - auth remains fail-closed.

### Frozen Modal restoration — SUCCESS

Workflow `.github/workflows/v143-restore-modal-production.yml` on diagnostic branch:

- workflow commit: `cb3785e35c743d0dfe0d976b31b7bcc837d4ec09`;
- run: **`33884039647`**;
- job: **`101059368271`**;
- exact deployed frozen source SHA: **`379ca54cce0f7f962c1e22caebfd6f49b8e4edb9`**;
- Modal environment: `main`;
- worker deployment: **SUCCESS**;
- reference-free worker dependency smoke: **SUCCESS**;
- HTTP bridge deployment: **SUCCESS**;
- bridge unauthenticated POST: **401**, proving endpoint exists and fails closed;
- Deployment Protection changed: **false**;
- reference score calls: **0**.

Worker dependency smoke aggregate:

- `cudaAvailable=true`;
- `deviceName=NVIDIA L4`;
- deterministic separator seed `143`;
- feature count `148`;
- `referenceFree=true`;
- Demucs `htdemucs_6s.yaml`, shifts `1`;
- BS-Roformer `model_bs_roformer_ep_317_sdr_12.9755.ckpt`;
- Basic Pitch, bend evidence/consensus, legato evidence, deterministic provider imports all true;
- `professionalReferenceUsed=false`;
- `runtimeLabelsRequired=false`;
- reference-facing score calls `0`.

Aggregate artifact only: `v143-frozen-modal-production-restore`, artifact id `9941100132`. No reference or transcription artifact was created.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized fresh-chat continuation of the non-reference-facing Production work. Authorization covers exact frozen V143 Modal worker/bridge restoration, Vercel env correction/redeploy as required, workflow edits/reruns, Production Rhythm calls using the existing repository-owned Gomyway audio, preview/PDF contract checks with raw outputs discarded, and GitHub Actions/Vercel log inspection.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- merge to `main`: authorized and complete;
- current `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`;
- Production V143 Rhythm route selection: **ACTIVE / PROVEN**;
- frozen V143 Modal worker: **RESTORED / DEPENDENCY SMOKE GREEN**;
- frozen V143 HTTP bridge: **RESTORED / FAIL-CLOSED 401 GREEN**;
- Deployment Protection: **preserved**;
- reference-facing score calls: **0**;
- GOAT restricted bytes: **0**;
- GuitarSet prospective sealed reads: **0**;
- raw Gomyway transcription/PDF retained: **false**;
- current real-audio verdict: **NO PIPELINE VERDICT YET — INFRASTRUCTURE RESTORED; PRODUCTION STILL NEEDS CORRECT BRIDGE URL + NEW SMOKE**.

## NEXT SAFE ACTION — AUTHORIZED

1. Update Production `ANALYZER_API_URL_V143` to `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run` only.
2. Redeploy exact current `main` if required for the env change to become active.
3. Use authenticated `vercel curl` so Deployment Protection remains enabled.
4. Re-run the aggregate-only Gomyway Rhythm smoke. Require runtime `usingV143RhythmAnalyzer: true`, HTTP 200, and response `rhythmCanaryActive: true` before interpreting pipeline behavior.
5. If analysis reaches 200, pass structured events through Production preview; retain only aggregate quality/placement/PDF contract metadata and delete raw transcription/PDF/request outputs.
6. Report only internal signs of success; **reference-facing accuracy remains unarmed**.
