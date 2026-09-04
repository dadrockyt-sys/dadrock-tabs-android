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
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 ROUTING ACTIVE; DOWNLOAD-AUTH FIX GREEN; FULL GOMYWAY WORKER TIMES OUT AT 1200S; 725.802S STAGE GATE LOCALIZES BOTTLENECK TO FIRST DIRECT DEMUCS CPU/SINGLE-THREAD PASS; ORIGINAL 12S SEQUENTIAL CPU1-vs-CPU4 GATE CANCELLED; DIAGNOSTIC APP STOPPED; BOUNDED 6S CONCURRENT MICRO-PROBE TERMINATED SAFELY WITH `RemoteError` AFTER AN EXTERNAL APP STOP, SO NO VALID CPU1/CPU4 PERFORMANCE VERDICT YET; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Stable Production state

- current `main`: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**;
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

## Emergency diagnostic app stop — GREEN

- workflow `.github/workflows/v143-stop-demucs-perf-probe.yml`;
- commit `5f9d33242b0d2357119acbfc4b819c2d7d96921b`;
- run **`33897740674`**, job **`101104268991`**: SUCCESS;
- stopped only `dadrock-v143-demucs-perf-probe`;
- live Production app `dadrock-v143-ai-tab-live` untouched.

## Bounded 6-second concurrent micro-probe — TERMINAL / CONFOUNDED

Safety hardening:

- collector `.github/scripts/v143_demucs_micro_probe_collect.py`;
- commit `e47f62a8550f4b68c5aa38e15645845a299c84d4`;
- 6.0-second clip;
- four independent concurrent calls: frozen x2 + CPU4 x2;
- 300-second total collection deadline;
- `call.cancel(terminate_containers=True)` on failure/timeout;
- aggregate-only summary;
- strict exact-SHA repeatability/parity + `>=1.25x` speedup threshold;
- workflow cleanup always stops the diagnostic app.

Terminal run:

- workflow `.github/workflows/v143-demucs-cpu-policy-micro-probe.yml`;
- trigger commit `2c1f5065c870c7673813ebad93c1ac7debccdfca`;
- run **`33898012776`**, job **`101105170742`**;
- setup/deploy: GREEN;
- bounded probe step: FAILURE;
- aggregate artifact id: **`9946663368`**;
- aggregate terminal type: **`RemoteError`**;
- `completed=false`;
- `remoteCallsCancelled=true`;
- reference-facing score calls: 0;
- raw audio/stem retention: false;
- Production worker/bridge/Vercel changed: false.

Function call IDs retained for diagnostics only:

- `fc-01M1PNPXNEST24KNCBC2XN054Z`
- `fc-01M1PNPXRQ51CWRASTG0E8FT3A`
- `fc-01M1PNPXVP2A7YAJZ6WDCTVMA8`
- `fc-01M1PNPXYXRPD6C0EWPWS7DNT4`

### Critical interpretation

The collector surfaced `RemoteError` at about **17:02:51 UTC**. The cleanup step immediately afterward reported the app was **already stopped at 17:02:50 UTC by `dadrockyt`**. Therefore the failed micro-probe is **confounded by an app stop immediately before the RemoteError**.

Do **not** interpret this run as proof that:

- the 6-second frozen baseline exceeded the 300-second deadline;
- CPU4 failed repeatability/parity;
- CPU4 was slower/faster;
- the collector timeout fired.

The only valid terminal conclusions are:

1. the replacement harness did not loop indefinitely;
2. all outstanding calls were cancelled;
3. the diagnostic app is stopped;
4. no Production system was touched;
5. CPU1-vs-CPU4 performance remains unresolved.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized continuation of non-reference-facing Production work. Authorization covers narrowly scoped V143 worker/bridge fixes and deploys, workflow diagnostics, Vercel configuration/redeploy if required, the existing repository-owned Gomyway audio, and aggregate-only Product/PDF contract checks with raw outputs discarded.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- `main`: unchanged;
- Production V143 routing: ACTIVE;
- Deployment Protection: preserved;
- diagnostic Demucs app: STOPPED;
- reference-facing score calls: 0;
- GOAT restricted bytes: 0;
- GuitarSet prospective sealed reads: 0;
- raw Gomyway transcription/PDF/stems retained: false;
- current quality verdict: **NO QUALITY VERDICT — PERFORMANCE DIAGNOSTICS ONLY**.

## NEXT SAFE ACTION — AUTHORIZED

1. Do **not** restart the four-call micro-probe immediately.
2. First inspect the retained function-call logs for the four IDs above to determine whether any individual 6-second run completed or where each stopped; this requires no new audio execution.
3. Then replace the multi-call gate with a **single 6-second frozen baseline call** with an explicit short hard deadline, explicit progress markers, remote cancellation, and `always()` app cleanup.
4. Only if that single baseline completes cleanly should CPU4 be tested in a separate single-call run.
5. If a 6-second frozen run cannot complete within the short bounded window, stop pursuing CPU thread-count tweaks and move to a more structural acceleration candidate (explicit CPU resource allocation and deterministic threading, then GPU Demucs if needed) under exact-hash gates.
6. Do not change Production model, seed, shifts, reference boundaries, Vercel duration, or UI orchestration until a dedicated deterministic/reference-free gate demonstrates material speedup.
7. Reference-facing accuracy remains unarmed.
