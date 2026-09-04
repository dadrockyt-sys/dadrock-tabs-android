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
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 ROUTING ACTIVE; DOWNLOAD-AUTH FIX GREEN; DIRECT L4 GOMYWAY TIMES OUT AT WORKER 1200S; 725.802S STAGE GATE LOCALIZES BOTTLENECK TO FIRST DIRECT DEMUCS CPU/SINGLE-THREAD PASS; 12S CPU1-vs-CPU4 STRICT HASH GATE RUNNING; DORMANT 6S CONCURRENT FALLBACK PREPARED; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

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

## Stage localization — TERMINAL / decisive first-stage evidence

Instrumentation-only `V143_STAGE` markers were added around download, normalization, separator stages and request lifecycle without changing models, seeds, execution devices, thread settings, musical data flow, or reference-free flags.

Workflow `V143 Stage Timing Localization`:

- source commit `ba937b01dd71fe828b4fecb3a7c067481177dc6d`;
- run **`33893769468`**, job **`101091458986`**: SUCCESS as a bounded diagnostic;
- function call `fc-01M1PK37V22D6NPP741GEJDT6Y`;
- diagnostic wall time: **725.802 seconds**;
- terminal type: `diagnostic-window-ended`;
- `completedWithinDiagnosticWindow=false`;
- aggregate artifact `v143-stage-timing-localize`, id **`9945355282`**;
- execution policy changed: false;
- reference-facing score calls: 0;
- raw transcription retained: false.

Final markers included:

```text
worker.start                           0.000 s
worker.download.start                  0.001 s
worker.download.done                   0.698 s
worker.normalize.start                 0.699 s
worker.normalize.done                  1.237 s
worker.router.start                    1.237 s
separator.start                        0.000 s
separator.input-normalize.start        0.000 s
separator.input-normalize.done         0.248 s
separator.direct-demucs.start          0.248 s
```

There was **no `separator.direct-demucs.done` marker** before the diagnostic window ended.

The log collection used `call.logs.tail(...)`, which behaved as a following stream rather than the intended quick snapshot and made the loop cadence less clean than designed. However, the job ultimately terminated within the GitHub budget and emitted the bounded aggregate summary above. The terminal evidence agrees with the independent live Modal scrape, so this does **not** weaken the localization result.

Therefore the timeout is localized, with current evidence, to the **first direct Demucs6s pass** before BS-RoFormer, cascade Demucs, candidate extraction, tab generation, Product placement, or PDF rendering are reached.

Current frozen Demucs execution policy is deliberately conservative/deterministic:

- CPU only (`CUDA_VISIBLE_DEVICES=''`);
- `OMP_NUM_THREADS=1`;
- `MKL_NUM_THREADS=1`;
- torch single-thread / deterministic algorithms;
- oneDNN disabled / conservative CPU capability;
- model `htdemucs_6s`, shifts `1`, separator seed `143`.

## Isolated Demucs CPU thread determinism/performance gate — ACTIVE

Initial diagnostic-only commits:

- `9e5534804d794e969acc6019290f7c80581a056d` — adds `analyzer/v143_demucs_perf_probe_cli.py`;
- `c3f0a6721c3745438d26bb9b41e232e94743f5ef` — adds isolated Modal app `dadrock-v143-demucs-perf-probe`;
- `4e3b9d059b9d06bd1d218e0c79457b0b0975ebb7` — adds workflow `.github/workflows/v143-demucs-cpu-thread-policy-probe.yml`.

Active workflow:

- run **`33894887671`**;
- job **`101095090913`**;
- branch head at launch: `4e3b9d059b9d06bd1d218e0c79457b0b0975ebb7`;
- setup, source/safety assertions, isolated app deploy, and public-audio verification: GREEN;
- comparison step started at `2026-09-04T16:24:15Z` and remains running;
- Production worker/bridge/Vercel are untouched by this probe.

Gate design:

- same authorized Gomyway source; ephemeral first 12-second clip;
- same Demucs `htdemucs_6s`, Guitar-only stem, shifts `1`, overlap `0.10`, segment `6`, seed `143`;
- same CPU-only boundary, disabled oneDNN, conservative CPU ISA, and deterministic Torch controls;
- frozen CPU/1-thread baseline runs twice;
- CPU/4-thread candidate runs twice;
- only elapsed seconds + SHA-256 hashes are retained; raw clip/stems stay inside the diagnostic worker;
- strict decision policy requires baseline repeatability, CPU4 repeatability, **exact candidate SHA parity with baseline**, and speedup **>=1.25x**.

### Promotion-threshold bookkeeping correction

The originally deployed 12-second probe source reports `promotionEligible` using `speedup > 1.20`. The workflow does not auto-promote or change Production, so this cannot cause a live policy change. Commit **`2171b12134058dce62155a1647929441a56a4f8e`** corrects future diagnostic source to explicitly use `PROMOTION_SPEEDUP_THRESHOLD = 1.25` and `speedup >= 1.25`. For the active run, ignore its boolean promotion flag and judge the raw returned speedup against the stricter 1.25x threshold manually.

### Dormant 6-second concurrent fallback — PREPARED / NOT DEPLOYED

Because four sequential 12-second Demucs runs may exhaust the diagnostic budget, a stronger fallback is prepared but not deployed:

- commit **`2d53ee30293082ac433d0b2eac7da81e4434186e`** adds isolated `run_cpu_policy_once(...)`, one Demucs run per Modal call;
- commit **`0c2b7472c0ff25f34403dd3c20a3bdc2580eaf3f`** adds `.github/scripts/v143_demucs_micro_probe_collect.py`;
- fallback clip duration: exactly **6.0 seconds**;
- planned calls: two frozen CPU1 and two CPU4, each in a separate worker and eligible to run concurrently;
- repeatability is therefore tested across independent workers, not merely sequential child processes;
- collector retains only call IDs, elapsed/wall times, SHA-256 hashes, byte counts, and aggregate decision flags;
- same strict `>=1.25x` speedup threshold plus exact baseline SHA parity;
- no fallback workflow has been created/triggered yet; no new diagnostic deployment has occurred from these fallback commits.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized continuation of the non-reference-facing Production work. Authorization covers narrowly scoped V143 worker/bridge fixes and deploys, workflow diagnostics, Vercel configuration/redeploy if required, the existing repository-owned Gomyway audio, and aggregate-only Product/PDF contract checks with raw outputs discarded.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- `main`: unchanged and verified;
- Production V143 routing: ACTIVE;
- patched/instrumented V143 worker: DEPLOYED;
- public-audio download failure: cleared;
- direct worker completion: TIMEOUT at 1200 execution seconds;
- stage localization: terminal at 725.802 s, first direct Demucs still incomplete;
- first bottleneck localized: **direct Demucs CPU/single-thread pass**;
- isolated 12s CPU1-vs-CPU4 gate: ACTIVE, no Production policy change;
- 6s concurrent fallback: PREPARED / DORMANT;
- Deployment Protection: preserved;
- reference-facing score calls: 0;
- GOAT restricted bytes: 0;
- GuitarSet prospective sealed reads: 0;
- raw Gomyway transcription/PDF/stems retained: false;
- current real-audio verdict: **NO QUALITY VERDICT — DEMUCS EXECUTION POLICY PERFORMANCE MUST BE REPAIRED WITHOUT LOSING DETERMINISM**.

## NEXT SAFE ACTION — AUTHORIZED

1. Finish run `33894887671` and extract only its aggregate CPU1/CPU4 elapsed times, repeatability hashes, strict parity result, and raw speedup. Apply the manual `>=1.25x` threshold.
2. If the sequential 12-second gate times out or returns no complete aggregate, deploy/trigger the prepared **6-second concurrent micro-probe** instead of increasing any timeout.
3. If CPU4 has exact baseline parity and material speedup, validate the same candidate on a longer clip before any live worker policy change.
4. If CPU4 fails parity, do not promote it. Move to the next isolated deterministic candidate (GPU only as a later option) under the same strict repeatability/hash gate.
5. Do **not** change Production worker execution policy, model, seed, Demucs shifts, reference boundaries, Vercel duration, or UI orchestration until a dedicated gate demonstrates deterministic/reference-free safety and material speedup.
6. Only after the worker itself returns successfully should async Production orchestration or Vercel duration changes be implemented.
7. Reference-facing accuracy remains unarmed.
