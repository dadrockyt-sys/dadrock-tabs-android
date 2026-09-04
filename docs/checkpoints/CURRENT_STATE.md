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

**Project Progress Score: 79%.**  
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 ROUTING ACTIVE; DOWNLOAD-AUTH FIX GREEN; DIRECT L4 GOMYWAY TIMES OUT AT WORKER 1200S; STAGE LOGS LOCALIZE BOTTLENECK TO FIRST DIRECT DEMUCS CPU/SINGLE-THREAD PASS; ISOLATED CPU1-vs-CPU4 STRICT HASH PERFORMANCE GATE RUNNING; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

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

Instrumentation-only `V143_STAGE` markers were added around download, normalization, separator stages and request lifecycle without changing models, seeds, execution devices, thread settings, musical data flow, or reference-free flags.

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

Workflow `V143 Stage Timing Localization`, job `101091458986`, used `call.logs.tail(...)` as if it were a bounded snapshot. The tail API follows the log stream and can block before the intended 720-second loop deadline advances. This is a **diagnostic harness bug**, not analyzer evidence. Independent Modal log scraping supplied the localization above. Do not interpret that GitHub job as a worker result.

## Isolated Demucs CPU thread determinism/performance gate — ACTIVE

Three diagnostic-only commits on `v143-contextual-prune-lobo`:

- `9e5534804d794e969acc6019290f7c80581a056d` — adds `analyzer/v143_demucs_perf_probe_cli.py`;
- `c3f0a6721c3745438d26bb9b41e232e94743f5ef` — adds isolated Modal app `dadrock-v143-demucs-perf-probe`;
- `4e3b9d059b9d06bd1d218e0c79457b0b0975ebb7` — adds workflow `.github/workflows/v143-demucs-cpu-thread-policy-probe.yml`.

Active workflow:

- run **`33894887671`**;
- job **`101095090913`**;
- branch head at launch: `4e3b9d059b9d06bd1d218e0c79457b0b0975ebb7`;
- setup, source/safety assertions, isolated app deploy, and public-audio verification: GREEN;
- comparison step currently running.

Gate design:

- same authorized Gomyway source; ephemeral first 12-second clip;
- same Demucs `htdemucs_6s`, Guitar-only stem, shifts `1`, overlap `0.10`, segment `6`, seed `143`;
- same CPU-only boundary, disabled oneDNN, conservative CPU ISA, and deterministic Torch controls;
- frozen CPU/1-thread baseline runs twice;
- CPU/4-thread candidate runs twice;
- only elapsed seconds + SHA-256 hashes are retained; raw clip/stems stay inside the diagnostic worker;
- promotion requires baseline repeatability, CPU4 repeatability, **exact candidate SHA parity with baseline**, and material speedup (gate threshold >=1.25x);
- Production worker, HTTP bridge, Vercel, model, and reference boundaries are untouched by this probe.

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
- isolated CPU1-vs-CPU4 gate: ACTIVE, no Production policy change;
- Deployment Protection: preserved;
- reference-facing score calls: 0;
- GOAT restricted bytes: 0;
- GuitarSet prospective sealed reads: 0;
- raw Gomyway transcription/PDF/stems retained: false;
- current real-audio verdict: **NO QUALITY VERDICT — DEMUCS EXECUTION POLICY PERFORMANCE MUST BE REPAIRED WITHOUT LOSING DETERMINISM**.

## NEXT SAFE ACTION — AUTHORIZED

1. Finish run `33894887671` and extract only its aggregate CPU1/CPU4 elapsed times, repeatability hashes, strict parity result, and promotion verdict.
2. If CPU4 has exact baseline parity and material speedup, validate the same candidate on a longer clip before any live worker policy change.
3. If CPU4 fails parity, do not promote it. Move to the next isolated deterministic candidate (GPU only as a later option) under the same strict repeatability/hash gate.
4. If the four-run 12-second gate itself cannot finish within its diagnostic budget, rerun the exact policy comparison on a 6-second clip rather than increasing Production timeouts.
5. Do **not** change Production worker execution policy, model, seed, Demucs shifts, reference boundaries, Vercel duration, or UI orchestration until a dedicated gate demonstrates deterministic/reference-free safety and material speedup.
6. Only after the worker itself returns successfully should async Production orchestration or Vercel duration changes be implemented.
7. Reference-facing accuracy remains unarmed.
