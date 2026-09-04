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
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 ROUTING ACTIVE; DOWNLOAD-AUTH FIX GREEN; FULL GOMYWAY WORKER TIMES OUT AT 1200S; 725.802S STAGE GATE LOCALIZES BOTTLENECK TO FIRST DIRECT DEMUCS CPU/SINGLE-THREAD PASS; ORIGINAL 12S SEQUENTIAL CPU1-vs-CPU4 GATE CANCELLED; CONCURRENT 6S MICRO-PROBE CONFOUNDED BY EXTERNAL APP STOP; RETAINED-CALL INSPECTION GREEN WITH NO RECOVERABLE AGGREGATE; SINGLE 6S FROZEN BASELINE CLEANLY TIMES OUT AT 300S WITH CANCEL/CLEANUP GREEN; CPU THREAD-COUNT TWEAK PATH CLOSED; STRUCTURAL ACCELERATION NEXT; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Stable Production state

- current `main`: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`** (re-verified immediately before the single-baseline gate);
- Production deployment: **`dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`**, READY;
- aliases include `dadrocktabs.com` / `www.dadrocktabs.com`;
- V143 bridge: `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`;
- Deployment Protection remains enabled;
- Production runtime has proven `usingV143RhythmAnalyzer=true`;
- **Production worker, bridge, and Vercel configuration were not changed by the Demucs diagnostics below.**

## Authorized Gomyway source

- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`;
- blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`;
- 3,464,988 bytes;
- raw diagnostic clips/stems remain ephemeral only.

## Decisive performance evidence

### Full direct worker — terminal timeout

- run `33890279981`, job `101079989844`;
- direct `dadrock-v143-ai-tab-live / rhythm_v143_request` call;
- worker timeout: **1200 seconds**;
- client wall time including queue/startup: **1744.461 seconds**;
- reference score calls: 0; raw outputs retained: false.

### Stage localization — terminal

- run `33893769468`, job `101091458986`: SUCCESS as bounded diagnostic;
- diagnostic wall: **725.802 seconds**;
- `completedWithinDiagnosticWindow=false`;
- last decisive marker: `separator.direct-demucs.start` at ~0.248 s;
- no `separator.direct-demucs.done` before the window ended;
- current bottleneck is the first direct Demucs6s CPU/single-thread pass before BS-RoFormer/cascade/tab/PDF stages.

Frozen Demucs policy remains CPU-only, single-threaded, deterministic, oneDNN-disabled/conservative ISA, `htdemucs_6s`, Guitar stem, shifts=1, overlap=0.10, segment=6, seed=143.

## Original 12-second CPU1-vs-CPU4 gate — CANCELLED / DO NOT RERUN

- workflow `.github/workflows/v143-demucs-cpu-thread-policy-probe.yml`;
- run **`33894887671`**, job **`101095090913`**;
- cancelled after loop-like/runaway behavior;
- harness problem: `compare_cpu_thread_policy(...)` performs four full Demucs passes sequentially inside one 1100-second Modal call;
- no aggregate artifact;
- no Production change.

## Bounded 6-second concurrent micro-probe — TERMINAL / CONFOUNDED

- workflow `.github/workflows/v143-demucs-cpu-policy-micro-probe.yml`;
- run **`33898012776`**, job **`101105170742`**;
- four independent concurrent calls: frozen x2 + CPU4 x2;
- collector deadline: 300 seconds;
- aggregate terminal type: `RemoteError`;
- cleanup reported diagnostic app had already been stopped at **17:02:50 UTC by `dadrockyt`**, immediately before the collector surfaced `RemoteError` at about **17:02:51 UTC**;
- therefore this run remains confounded and gives no valid CPU1-vs-CPU4 performance verdict;
- reference score calls: 0; raw audio/stem retention: false; Production unchanged.

## Retained-call inspection — TERMINAL / GREEN READ-ONLY

GitHub Actions run **`33913626199`**, job **`101155625317`**, completed successfully using the read-only inspector.

- script `.github/scripts/v143_demucs_retained_call_inspect.py`, commit `22e6556ef20c372625f3fef15537cf3ad6192164`;
- workflow `.github/workflows/v143-demucs-retained-call-inspect.yml`, trigger commit `81be5bbe74ac869ed3d9dd11f9d6de3d0a6cc66d`;
- artifact id **`9952305301`**;
- all four retained call IDs resolve to terminal type **`RemoteError`**;
- `completedAggregateAvailable=false` for all four;
- no timing/hash aggregate is recoverable from the interrupted four-call run;
- new audio execution = false; new function calls spawned = 0;
- reference score calls = 0; raw audio/stem retention = false;
- Production worker/bridge/Vercel changed = false.

## Single 6-second frozen baseline — TERMINAL / CLEAN TIMEOUT

A fresh isolated one-call gate was run without modifying Production:

- isolated app source `analyzer/v143_demucs_single_baseline_probe.py`, commit `ac5385118edf609d48b1cbffcf4113ced5befe94`;
- collector `.github/scripts/v143_demucs_single_baseline_collect.py`, commit `b817610dd1beb344ffee6f63a92d6bf29986a4a7`;
- workflow `.github/workflows/v143-demucs-single-frozen-baseline.yml`, trigger commit `f47cc6de45562b4d29db930a0432dec6a64b4398`;
- GitHub Actions run **`33913842713`**, job **`101156325246`**;
- exactly one `frozen` call on the 6.0-second authorized clip;
- function call id **`fc-01M1Q00SSQNTHAQM8AAKXZWG2J`**;
- local wait began at `19:58:35.360971Z` and failed at `20:03:35.365388Z`;
- hard collection deadline **300.0 seconds** was reached with terminal type **`TimeoutError`**;
- `call.cancel(terminate_containers=True)` was attempted successfully; cancellation error = null;
- aggregate artifact id **`9952542047`** uploaded successfully;
- isolated-app cleanup step completed successfully after the timeout;
- `productionAppTouched=false`;
- reference-facing score calls = 0;
- raw audio/stem retention = false;
- Production worker/bridge/Vercel changed = false.

### Decisive interpretation

This single-call failure is **not confounded by an external app stop**. The diagnostic app remained available through the 300-second collection window, the client deadline fired cleanly, the outstanding call was then cancelled, and cleanup ran afterward.

Therefore:

1. the existing frozen CPU/single-thread Demucs path cannot complete even a 6-second authorized clip within the 300-second bounded window under the current resource envelope;
2. the CPU1-vs-CPU4 thread-count tweak path is now **CLOSED / DO NOT PURSUE**;
3. the next work must be structural acceleration rather than thread-count tuning;
4. no quality or reference-facing accuracy verdict has been produced.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized continuation of non-reference-facing Production work. Authorization covers narrowly scoped V143 worker/bridge fixes and deploys, workflow diagnostics, Vercel configuration/redeploy if required, the existing repository-owned Gomyway audio, and aggregate-only Product/PDF contract checks with raw outputs discarded.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- `main`: unchanged;
- Production V143 routing: ACTIVE;
- Deployment Protection: preserved;
- diagnostic single-baseline app: STOPPED after cleanup;
- reference-facing score calls: 0;
- GOAT restricted bytes: 0;
- GuitarSet prospective sealed reads: 0;
- raw Gomyway transcription/PDF/stems retained: false;
- current quality verdict: **NO QUALITY VERDICT — PERFORMANCE DIAGNOSTICS ONLY**.

## NEXT SAFE ACTION — AUTHORIZED

1. Do **not** run CPU4/thread-count tuning.
2. Search existing repository/checkpoint/test evidence for any completed deterministic frozen Demucs output hash that can serve as an exact-output parity anchor without new reference-facing scoring.
3. If a parity anchor exists, build an isolated **explicit CPU resource allocation** candidate while preserving the frozen deterministic model/seed/shifts/overlap/segment and exact-hash gate.
4. If no usable parity anchor exists, define the smallest reference-free deterministic structural gate that can establish candidate repeatability and a trustworthy output identity anchor before any Production promotion.
5. If explicit CPU resource allocation is still materially too slow, evaluate GPU Demucs in an isolated reference-free diagnostic under deterministic/repeatability and exact-output constraints before any Production change.
6. Do not change Production model, seed, shifts, reference boundaries, Vercel duration, or UI orchestration until a dedicated deterministic/reference-free structural gate demonstrates material speedup and output safety.
7. Reference-facing accuracy remains unarmed.
