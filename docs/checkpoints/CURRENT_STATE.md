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
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 ROUTING ACTIVE; DOWNLOAD-AUTH FIX GREEN; DIRECT L4 GOMYWAY TIMES OUT AT WORKER 1200S; STAGE LOGS LOCALIZE BOTTLENECK TO FIRST DIRECT DEMUCS CPU/SINGLE-THREAD PASS; NEXT = DIAGNOSTIC-ONLY DETERMINISM/PERFORMANCE GATE BEFORE ANY EXECUTION-POLICY CHANGE; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Stable Production state

- current `main`: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**;
- Production deployment: **`dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`**, READY;
- aliases include `dadrocktabs.com` / `www.dadrocktabs.com`;
- V143 bridge: `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`;
- Deployment Protection remains enabled;
- Vercel team plan: Pro;
- Production runtime has proven `usingV143RhythmAnalyzer=true`.

## Authorized existing Gomyway audio

- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`;
- blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`;
- 3,464,988 bytes;
- diagnostic source: public raw GitHub `main` asset.

## Download-auth repair — GREEN / DEPLOYED

- Blob bearer now forwards only to HTTPS `blob.vercel-storage.com` / subdomains;
- raw GitHub/public origins receive no Blob credential;
- `liveV143.referenceRuntimeInputUsed=false` added for current `main` safety contract;
- predeploy gate run `33889340784`, job `101076898337`: SUCCESS;
- patched worker deploy run `33889490536`, job `101077392412`: SUCCESS;
- reference score calls: 0.

## Real-audio timing evidence

### Production request after download fix

- run `33889779953`, job `101078353122`;
- protected `/ai-tab`: 200;
- analysis returned HTTP 504 at ~151 seconds, matching `export const maxDuration = 150`;
- old immediate download failure was no longer observed;
- raw analysis/request/PDF deleted; aggregate artifact only; reference score calls 0.

### Direct L4 Gomyway timing — TERMINAL

- workflow `.github/workflows/v143-direct-l4-gomyway-timing.yml`;
- run `33890279981`, job `101079989844`;
- direct `dadrock-v143-ai-tab-live / rhythm_v143_request` call;
- terminal: **FunctionTimeoutError**;
- worker execution timeout: **1200 seconds**;
- measured client wall time: **1744.461 seconds** including queue/startup;
- aggregate artifact only; raw transcription/PDF retained false; reference score calls 0.

**Conclusion:** Vercel’s 150-second limit is not the root problem. The worker itself does not finish within 20 execution minutes, so merely raising Vercel duration or adding async polling would not yet make the pipeline successful.

## Stage localization — decisive first-stage evidence

Instrumentation-only commit line added `V143_STAGE` markers around download, normalization, separator stages and request lifecycle without changing models, seeds, execution devices, thread settings, musical data flow, or reference-free flags.

Independent live Modal stage-log scrape for the Gomyway call showed:

```text
request.start                         ~0.012 s
download.start                        ~0.013 s
download.done                         ~0.710 s   (3,464,988 bytes)
normalize.start                       ~0.711 s
normalize.done                        ~1.249 s   (~42.9 MB WAV)
separator.normalize-input.start       ~0.000 s
separator.normalize-input.done        ~0.248 s
separator.direct-demucs.start         ~0.248 s
```

Repeated later scrapes still showed **no `separator.direct-demucs.done` marker**.

Therefore the timeout is localized, with current evidence, to the **first direct Demucs6s pass** before BS-RoFormer, cascade Demucs, candidate extraction, tab generation, Product placement, or PDF rendering are reached.

Current frozen Demucs execution policy is deliberately conservative/deterministic:

- CPU only (`CUDA_VISIBLE_DEVICES=''`);
- `OMP_NUM_THREADS=1`;
- `MKL_NUM_THREADS=1`;
- torch single-thread / deterministic algorithms;
- oneDNN disabled / conservative CPU capability;
- model `htdemucs_6s`, shifts `1`, separator seed `143`.

### Stage-localization workflow harness bug

Workflow `V143 Stage Timing Localization`, job `101091458986`, remains stuck in its collection step because its diagnostic code treats `call.logs.tail(...)` as a bounded snapshot. The tail API follows the log stream and can block before the intended 720-second loop deadline advances. This is a **diagnostic harness bug**, not analyzer evidence. Independent Modal log scraping supplied the localization above. Do not interpret the stuck GitHub job as a worker result.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized continuation of the non-reference-facing Production work. Authorization covers narrowly scoped V143 worker/bridge fixes and deploys, workflow diagnostics, Vercel configuration/redeploy if required, the existing repository-owned Gomyway audio, and aggregate-only Product/PDF contract checks with raw outputs discarded.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- `main`: unchanged and verified;
- Production V143 routing: ACTIVE;
- patched/instrumented V143 worker: DEPLOYED;
- public-audio download failure: cleared;
- direct worker completion: TIMEOUT at 1200 execution seconds;
- first bottleneck localized: **direct Demucs CPU/single-thread pass**;
- Deployment Protection: preserved;
- reference-facing score calls: 0;
- GOAT restricted bytes: 0;
- GuitarSet prospective sealed reads: 0;
- raw Gomyway transcription/PDF/stems retained: false;
- current real-audio verdict: **NO QUALITY VERDICT — DEMUCS EXECUTION POLICY PERFORMANCE MUST BE REPAIRED WITHOUT LOSING DETERMINISM**.

## NEXT SAFE ACTION — AUTHORIZED

1. Build a **diagnostic-only Demucs determinism/performance gate** using a short clip derived from the same authorized Gomyway asset; keep clip/stems ephemeral and retain only elapsed times + SHA-256 hashes.
2. Establish the frozen CPU/single-thread baseline on that short clip, ideally twice, to prove repeatability and obtain a baseline hash/runtime.
3. Test acceleration candidates one at a time without references or scoring, prioritizing the smallest execution-policy changes (e.g. CPU ISA/thread changes) before GPU.
4. Require each candidate to be repeatable across two runs; prefer exact SHA parity with the frozen baseline. If hash differs, do not promote it merely because it is faster.
5. Do **not** change Production worker execution policy, model, seed, Demucs shifts, reference boundaries, Vercel duration, or UI orchestration until a dedicated gate demonstrates deterministic/reference-free safety and material speedup.
6. If no safe acceleration fits the worker budget, then design async orchestration only after the worker itself can finish successfully.
7. Reference-facing accuracy remains unarmed.
