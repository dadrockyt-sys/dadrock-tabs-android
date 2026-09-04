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

**Project Progress Score: 80%.**  
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 ROUTING ACTIVE; DOWNLOAD-AUTH FIX GREEN; FULL GOMYWAY WORKER TIMES OUT AT 1200S; 725.802S STAGE GATE LOCALIZES BOTTLENECK TO FIRST DIRECT DEMUCS CPU/SINGLE-THREAD PASS; ORIGINAL 12S SEQUENTIAL CPU1-vs-CPU4 GATE CANCELLED; CONCURRENT 6S MICRO-PROBE CONFOUNDED BY EXTERNAL APP STOP; RETAINED-CALL INSPECTION GREEN WITH NO RECOVERABLE AGGREGATE; SINGLE 6S FROZEN BASELINE CLEANLY TIMES OUT AT 300S WITH CANCEL/CLEANUP GREEN; CPU THREAD-COUNT TWEAK PATH CLOSED; HISTORICAL ONEDNN-OFF EXACT HASH ANCHOR RECOVERED; EXPLICIT `cpu=1.0` NO-GPU FULL-FIXTURE EXACT-ANCHOR GATE GREEN WITH EXACT HASH PARITY AT 666.404S WALL; GPU STRUCTURAL DIAGNOSTIC NEXT; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Stable Production state

- current `main`: **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**;
- Production deployment: **`dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`**, READY;
- aliases include `dadrocktabs.com` / `www.dadrocktabs.com`;
- V143 bridge: `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`;
- Deployment Protection remains enabled;
- Production runtime has proven `usingV143RhythmAnalyzer=true`;
- **Production worker, bridge, and Vercel configuration were not changed by the Demucs diagnostics below.**

## Authorized Gomyway sources

- current bounded source: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`, blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`, 3,464,988 bytes;
- historical approved reference-free host-probe fixture: `public/gomywayfullaitest.m4a`, SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`;
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
- harness problem: four full Demucs passes sequentially inside one long Modal call;
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

- isolated app source `analyzer/v143_demucs_single_baseline_probe.py`, commit `ac5385118edf609d48b1cbffcf4113ced5befe94`;
- collector `.github/scripts/v143_demucs_single_baseline_collect.py`, commit `b817610dd1beb344ffee6f63a92d6bf29986a4a7`;
- workflow `.github/workflows/v143-demucs-single-frozen-baseline.yml`, trigger commit `f47cc6de45562b4d29db930a0432dec6a64b4398`;
- run **`33913842713`**, job **`101156325246`**;
- exactly one `frozen` call on the 6.0-second authorized clip;
- function call id **`fc-01M1Q00SSQNTHAQM8AAKXZWG2J`**;
- hard collection deadline **300.0 seconds** reached with terminal type **`TimeoutError`**;
- `call.cancel(terminate_containers=True)` succeeded without cancellation error;
- aggregate artifact id **`9952542047`** uploaded successfully;
- isolated-app cleanup completed successfully after timeout;
- `productionAppTouched=false`; reference-facing score calls = 0; raw outputs retained = false.

### Decisive interpretation

This failure is not confounded by an external stop. The existing frozen CPU/single-thread Demucs path cannot complete even a 6-second clip within 300 seconds under that GPU-app resource envelope. CPU thread-count tuning is therefore **CLOSED / DO NOT PURSUE**; next work is structural resource/execution acceleration only.

## Historical exact-output anchor recovery — GREEN READ-ONLY

Repository history contains a successful oneDNN-off CPU-only V143 host probe on the approved `public/gomywayfullaitest.m4a` fixture:

- historical workflow run **`32692461330`**, job **`97328477497`**, SUCCESS;
- historical result commit **`34471c7cdd061dbbc5ed807ba473bb2e156bc5f8`**;
- source SHA256 **`215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`**;
- normalized WAV SHA256 **`ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`**;
- oneDNN-off direct Guitar SHA256 **`0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`**;
- decoded PCM-int16 SHA256 **`2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`**;
- expected deterministic shift trace `0,22050,6026`;
- fixture duration reported by separator: **211.44 seconds**;
- historical Demucs separation duration: **10:23** (~623 seconds);
- child runtime: PyTorch **`2.13.0+cu130`**, oneDNN disabled, CPU capability DEFAULT, intra/inter-op threads both 1, no CUDA available/requested.

Compatibility checks:

- `analyzer/v143_production_separator.py` current blob **`05ae1978fa02f8c84ccc1e44547fc4e4cea9798b`**, identical to the historical probe version;
- `analyzer/v143_seeded_audio_separator_cli.py` current blob **`645f324c207d67b32c6d279657805ff8f25c3aa0`**, identical to the oneDNN-off probe version;
- `analyzer/v143_ai_tab_gpu_worker.py` current blob **`e7cdddfbf9e55e46be8397224b11133e7636ebb6`**, identical image/dependency definition (`audio-separator[gpu]==0.44.5`);
- current seeded wrapper retains the same oneDNN-off/single-thread deterministic controls; later changes add aggregate stage timing markers, not separator math.

Historical oneDNN-enabled CPU evidence is **not** the parity target. It was materially faster (~5:04 separation) but produced different Guitar/PCM identities, so deterministic oneDNN-off identity remains the fail-closed contract.

No restricted reference was read or scored to recover this anchor or timing.

## Explicit `cpu=1.0` exact-anchor structural gate — TERMINAL / GREEN

- collector `.github/scripts/v143_demucs_explicit_cpu_anchor_collect.py`, commit **`bdd89936c167993f3ae882b76173094dea2d428c`**;
- workflow `.github/workflows/v143-demucs-explicit-cpu-anchor.yml`, trigger commit **`391ef75d5cf0c4f50a9b9536126cd7a70bdf447f`**;
- GitHub Actions run **`33914759546`**, job **`101159244192`**, SUCCESS;
- function call id **`fc-01M1Q0MFR88FXWAQ1R47TSX77Z`**;
- isolated diagnostic Modal function requested **`cpu=1.0`**, memory 8192, **no GPU**;
- hard collection deadline: 900 seconds;
- measured client wall: **666.404 seconds**;
- source SHA256 exactly matched **`215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`**;
- normalized WAV SHA256 exactly matched **`ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f`**;
- direct Guitar SHA256 exactly matched historical anchor **`0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c`**;
- decoded PCM-int16 SHA256 exactly matched historical anchor **`2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed`**;
- deterministic shift trace exactly matched `0,22050,6026`;
- runtime: PyTorch `2.13.0+cu130`, CPU capability DEFAULT, intra/inter-op threads = 1, oneDNN disabled;
- `structuralInvariantsPassed=true`;
- `exactParityPassed=true`;
- aggregate artifact id **`9953064061`** uploaded successfully;
- isolated diagnostic app cleanup succeeded immediately afterward;
- `productionAppTouched=false`;
- reference-facing score calls = 0;
- raw audio/stem retention = false;
- Production worker/bridge/Vercel changed = false.

### Decisive interpretation

The historical oneDNN-off CPU identity is now independently reproduced exactly under the current code/dependency environment. This is the trustworthy reference-free deterministic identity anchor for any structural acceleration candidate.

The explicit CPU resource envelope still requires **666.404 seconds wall** for the 211.44-second fixture, so it is materially too slow for the product pipeline. CPU thread-count tuning remains closed. The next candidate is GPU Demucs, isolated from Production and gated against this exact CPU identity.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized continuation of non-reference-facing Production work. Authorization covers narrowly scoped V143 worker/bridge fixes and deploys, workflow diagnostics, Vercel configuration/redeploy if required, the existing repository-owned Gomyway audio, and aggregate-only Product/PDF contract checks with raw outputs discarded.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- `main`: unchanged;
- Production V143 routing: ACTIVE;
- Deployment Protection: preserved;
- explicit-CPU diagnostic app: STOPPED after successful cleanup;
- reference-facing score calls: 0;
- GOAT restricted bytes: 0;
- GuitarSet prospective sealed reads: 0;
- raw Gomyway transcription/PDF/stems retained: false;
- current quality verdict: **NO QUALITY VERDICT — PERFORMANCE/IDENTITY DIAGNOSTICS ONLY**.

## NEXT SAFE ACTION — AUTHORIZED

1. Do **not** reopen CPU thread-count tuning or oneDNN-enabled promotion.
2. Search repository history for prior GPU Demucs replay/performance/identity evidence before launching new GPU audio execution.
3. If prior GPU evidence is insufficient, build one isolated reference-free GPU Demucs diagnostic on the approved anchored fixture with deterministic seed/settings, aggregate-only hashes/timing, explicit cancellation, and `always()` cleanup.
4. Keep the exact oneDNN-off CPU Guitar/PCM hashes above as the fail-closed output identity anchor. A mismatch must not be silently accepted or explained away as a promotion pass.
5. Do not change Production model, seed, shifts, reference boundaries, Vercel duration, or UI orchestration until a dedicated deterministic/reference-free structural gate demonstrates material speedup and output safety.
6. Reference-facing accuracy remains unarmed.
