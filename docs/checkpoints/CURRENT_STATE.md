# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 08:27 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async wiring authorization is limited to the transient structured-result handoff described below; no raw-audio/stem/model persistence and no long-term result cache.

## Production baseline — unchanged during async wiring

- Vercel/web `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`.
- Production deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, unchanged.
- Production route blob `06234db3e1cc1680b18fd62a765862b213ede3db`, `maxDuration = 150`.
- Production HTTP bridge blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`, unchanged.
- Promoted live worker blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`, scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.
- Worker app/function: `dadrock-v143-ai-tab-live/rhythm_v143_request`.
- No `main` merge; no worker/model changes in async work.

## Closed scheduler/promotion evidence

- Gate 1 structural: run `33942915753`, job `101243642285` — GREEN/CLOSED.
- Gate 2 exact approved-fixture runtime: run `33943100948`, job `101244148835`, artifact `9962641557` — GREEN/CLOSED.
- Gate 3A normal-routing composition: run `33945157629`, job `101249801382`, artifact `9963085825` — GREEN/CLOSED.
- Production worker deploy: run `33945389816`, job `101250418913`, artifact `9963159697` — GREEN/CLOSED.

## Breakthrough diagnosis

One real post-promotion production request:

- run `33965269193`, job `101304165477`, artifact `9969253856`;
- HTTP `504`, `analysisEndToEndSeconds=150.66095`;
- prior equivalent request ~`150.931s` → same Vercel 150s wall.

Log-only follow-up (no second model call):

- run `33965453476`, job `101304658150`, artifact `9969270692`;
- worker start `0.000s`, download done `1.387s`, normalize done `1.969s`;
- separator direct Demucs start `0.306s`, RoFormer start `0.319s`, RoFormer done `84.079s`, cascade Demucs start `84.079s`.

Verdict:

- scheduler/concurrency breakthrough: **YES / live production confirmed**;
- synchronous product latency breakthrough: **NO / Vercel 150s ceiling still blocks result**;
- musical quality: not tested by this performance work.

## Async breakthrough architecture — PLAN CHECKPOINTED

Plan: `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Architecture:

- Rhythm start returns immediately; browser polls status; completed result goes through the existing Vercel anti-leakage/product pipeline; browser then acknowledges cleanup.
- Existing promoted L4 worker remains unchanged.
- Existing bridge gains `start/status/ack`; default `analyze` path remains for rollback/Lead/Bass compatibility.
- Transient result handoff = named Modal Queue, one random partition/job, **900-second (15-minute) partition TTL**.
- Queue stores only zlib-compressed/chunked structured analyzer JSON or bounded generic failure envelope.
- Raw uploaded audio, normalized audio, stems, model bytes, exception traces/credentials are not queued.
- Browser ack clears result partition immediately; TTL is fallback cleanup.
- Lead/Bass remain synchronous in this phase.

## Async protocol implementation — SOURCE-ONLY GATE GREEN

Protocol helper:

- `analyzer/v143_async_job_protocol.py` commit `1b139994b9bf8572093e6644a61b6fde8c14cd89`;
- blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`;
- HMAC-SHA256 signed opaque tokens, random job IDs, TTL `900`, chunk size `700000`, JSON-only fail-closed boundary, zlib result transport.

Branch-only bridge candidate:

- `analyzer/v143_modal_http_endpoint.py` commit `40ca5a9649992f00ff0b3533d6cb21f3c9cf3f89`;
- blob `d874dce2b612e01a88adbf2ebaf953bfe8c3cb05`;
- Queue `dadrock-v143-async-results`;
- `run_rhythm_async_job.spawn(...)` starts lightweight orchestrator;
- orchestrator calls unchanged `dadrock-v143-ai-tab-live/rhythm_v143_request`;
- `start/status/ack` are analyzer-token protected and job-token HMAC protected;
- status uses non-mutating partition inspection; ack clears partition;
- default synchronous `analyze` dispatch and Lead/Bass fallback preserved.

Authoritative strengthened source-only gate:

- gate file `analyzer/v143_async_job_protocol_gate.py`, commit `7d2903fed9ec708a3eea7019b848d4dc315511ca`, blob `1e47351f8476fc0772e502219092bf85cf55d1e9`;
- workflow `.github/workflows/v143-async-job-protocol-gate.yml`;
- run `33965969177`, job `101306044525`: **SUCCESS**;
- artifact `9969426651`, digest `sha256:e37ea0c100d7f1b487669ab018cc336e5e756c2d2d672cb637518a42b7d8def3`;
- proved 15-minute TTL, sub-1MiB chunks, forced multi-chunk exact roundtrip, token roundtrip, tamper rejection, wrong-secret rejection, binary-payload rejection, async Rhythm-only boundary, synchronous fallback/Lead-Bass preservation;
- `modelExecuted=false`, `audioRead=false`, reference inputs/score calls `0`, quality verdict `false`.

## Vercel API async candidate — BRANCH ONLY / NOT DEPLOYED

`app/api/analyze-audio-tab/route.js`:

- commit `4c94ae0e8bf88f8c0f7f0053c0dec5ad32522b79`;
- candidate blob `742954146a86aa36485d0bbdb3fbd6691a64a712`;
- extracted existing completed-result anti-leakage/product pipeline without intentionally changing its semantics;
- Rhythm defaults to `start`; Lead/Bass default to existing synchronous `analyze`;
- `start` returns HTTP 202 + opaque job token;
- `status` returns 202 while processing, then applies the existing V143 safety/product pipeline to completed worker result;
- `ack` clears the transient bridge result partition;
- status/ack do not require Blob credentials; start/analyze still do;
- job token is never intentionally logged.

No UI polling change has landed yet. Production bridge/Vercel remain unchanged.

## NEXT STEP

1. Patch `app/ai-tab/page.js` so `requestTabAnalysis()` transparently polls 202 Rhythm jobs until completed, then acknowledges cleanup; the rest of preview/PDF flow should remain unchanged.
2. Add a no-model Vercel wiring/source gate proving start/status/ack UI/API composition and existing completed-result safety pipeline preservation.
3. Run branch build/static checks; checkpoint exact blobs/results.
4. Only after source/build GREEN: deploy bridge candidate and run no-model protocol smoke.
5. Then deploy Vercel preview, no-model protocol/UI smoke, and exactly one model-bearing preview E2E proving a tab can complete beyond 150 seconds.
6. Production Vercel promotion only after that preview proof is GREEN.

### Hard stops

- No duplicate model-bearing breakthrough request.
- No model/scheduler changes as part of async wiring.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async result storage.
- No async result TTL above 15 minutes; no persistent result cache.
- No whole-branch merge to `main`.
- No production Vercel promotion before preview protocol/E2E proof.
- No weakening exact parity/fail-closed criteria or retention boundaries.
