# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-04 (America/Toronto)  
Branch checkpoint: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## Global scientific state — unchanged

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**
- GOAT restricted bytes admitted/read = **0**; V168 prospective reference-facing score calls = **0**.
- SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`; never rerun/score/weaken/interpolate.
- GuitarSet V3/V4/V5 remain terminal; prospective players `00/01/03` remain sealed; prospective score calls = **0**.
- No reference-facing accuracy scoring has been run during Production/Modal performance work.

**Project Progress Score: 79%.**  
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 ROUTING ACTIVE; DOWNLOAD-AUTH FIX GREEN; FULL GOMYWAY WORKER TIMES OUT AT 1200S; 725.802S STAGE GATE LOCALIZES BOTTLENECK TO FIRST DIRECT DEMUCS CPU/SINGLE-THREAD PASS; ORIGINAL 12S SEQUENTIAL CPU1-vs-CPU4 GATE CANCELLED AFTER RUNAWAY/LOOP-LIKE BEHAVIOR; ISOLATED APP STOPPED; BOUNDED 6S CONCURRENT MICRO-PROBE ACTIVE WITH 300S DEADLINE + REMOTE CANCELLATION + ALWAYS-CLEANUP; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Stable Production state

- current `main`: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**;
- Production deployment: **`dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`**, READY;
- aliases include `dadrocktabs.com` / `www.dadrocktabs.com`;
- V143 bridge: `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`;
- Deployment Protection remains enabled;
- Production runtime has proven `usingV143RhythmAnalyzer=true`;
- **Production worker, bridge, and Vercel configuration remain untouched by the current Demucs diagnostics.**

## Authorized Gomyway source

- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`;
- blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`;
- 3,464,988 bytes;
- diagnostic source is public raw GitHub `main` asset;
- raw diagnostic clips/stems are ephemeral only.

## Decisive performance evidence

### Full direct worker — terminal timeout

- workflow run `33890279981`, job `101079989844`;
- direct `dadrock-v143-ai-tab-live / rhythm_v143_request` call;
- worker timeout: **1200 seconds**;
- client wall time including queue/startup: **1744.461 seconds**;
- reference score calls: 0; raw outputs retained: false.

### Stage localization — terminal

- run `33893769468`, job `101091458986`: SUCCESS as bounded diagnostic;
- function call `fc-01M1PK37V22D6NPP741GEJDT6Y`;
- diagnostic wall: **725.802 seconds**;
- `completedWithinDiagnosticWindow=false`;
- last decisive separator marker: `separator.direct-demucs.start` at ~0.248 s;
- no `separator.direct-demucs.done` before diagnostic window ended;
- conclusion: first direct Demucs6s CPU/single-thread pass is the current bottleneck before BS-RoFormer/cascade/tab/PDF stages.

Frozen Demucs policy remains:

- CPU only (`CUDA_VISIBLE_DEVICES=''`);
- `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`;
- deterministic Torch controls;
- oneDNN disabled / conservative CPU capability;
- `htdemucs_6s`, Guitar stem, shifts=1, overlap=0.10, segment=6, seed=143.

## Original 12-second CPU1-vs-CPU4 gate — CANCELLED / DO NOT RERUN

- workflow `.github/workflows/v143-demucs-cpu-thread-policy-probe.yml`;
- run **`33894887671`**, job **`101095090913`**;
- comparison step was cancelled after the diagnostic appeared stuck/looping;
- root harness design issue: `compare_cpu_thread_policy(...)` executes four full Demucs passes sequentially inside one 1100-second Modal function;
- no aggregate artifact was produced;
- no Production change occurred;
- do **not** rerun this sequential four-pass gate.

## Diagnostic app emergency stop — GREEN

- one-shot workflow `.github/workflows/v143-stop-demucs-perf-probe.yml`;
- commit `5f9d33242b0d2357119acbfc4b819c2d7d96921b`;
- run **`33897740674`**, job **`101104268991`**: SUCCESS;
- command stopped only `dadrock-v143-demucs-perf-probe` and terminated its running containers;
- live Production app `dadrock-v143-ai-tab-live` was not touched.

## Bounded 6-second concurrent micro-probe — ACTIVE

Prepared source:

- isolated single-run function `run_cpu_policy_once(...)` already exists in `analyzer/v143_demucs_perf_probe.py`;
- collector `.github/scripts/v143_demucs_micro_probe_collect.py`;
- commit `e47f62a8550f4b68c5aa38e15645845a299c84d4` hardened collector with:
  - 6.0-second clip;
  - four independent concurrent Modal calls: frozen x2 + CPU4 x2;
  - **300-second total collection deadline**;
  - `call.cancel(terminate_containers=True)` on failure/timeout;
  - aggregate-only failure summary;
  - exact SHA repeatability/parity checks;
  - promotion threshold `>=1.25x`;
  - raw audio/stem retention false.

Workflow:

- `.github/workflows/v143-demucs-cpu-policy-micro-probe.yml`;
- trigger commit `2c1f5065c870c7673813ebad93c1ac7debccdfca`;
- run **`33898012776`**, job **`101105170742`**;
- current status at checkpoint: **IN PROGRESS / setup**;
- job timeout: 12 minutes;
- after any outcome, `if: always()` executes `modal app stop dadrock-v143-demucs-perf-probe --env main --yes || true`;
- therefore this replacement must not leave a runaway diagnostic app behind.

Decision policy if the micro-probe completes:

1. frozen runs must be byte-repeatable;
2. CPU4 runs must be byte-repeatable;
3. CPU4 SHA must exactly equal frozen SHA;
4. speedup must be **>=1.25x** before CPU4 is even eligible for longer validation;
5. no Production execution-policy change from this short clip alone.

If the 6-second probe hits its 300-second deadline, treat that as decisive evidence that this CPU-only path is too slow for practical full-song use; do not increase the diagnostic timeout again.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized continuation of non-reference-facing Production work. Authorization covers narrowly scoped V143 worker/bridge fixes and deploys, workflow diagnostics, Vercel configuration/redeploy if required, the existing repository-owned Gomyway audio, and aggregate-only Product/PDF contract checks with raw outputs discarded.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- `main`: unchanged;
- Production V143 routing: ACTIVE;
- Deployment Protection: preserved;
- reference-facing score calls: 0;
- GOAT restricted bytes: 0;
- GuitarSet prospective sealed reads: 0;
- raw Gomyway transcription/PDF/stems retained: false;
- current quality verdict: **NO QUALITY VERDICT — PERFORMANCE DIAGNOSTICS ONLY**.

## NEXT SAFE ACTION — AUTHORIZED

1. Finish bounded micro-probe run `33898012776` / job `101105170742` and inspect aggregate artifact/log outcome.
2. Confirm diagnostic app cleanup step succeeded regardless of probe result.
3. If CPU4 passes exact SHA parity + repeatability + >=1.25x speedup, validate on a longer authorized clip before touching Production.
4. If CPU4 fails parity or the 6-second gate exceeds 300 seconds, do not increase timeout and do not promote it; move to the next isolated acceleration candidate.
5. A strong next candidate is resource-aware execution (explicit CPU allocation with deterministic threading) or later GPU Demucs, each under the same strict hash/repeatability gate.
6. Do not change Production model, seed, shifts, reference boundaries, Vercel duration, or UI orchestration until a dedicated deterministic/reference-free gate demonstrates material speedup.
7. Reference-facing accuracy remains unarmed.
