# V143 Async Job Architecture Plan

Updated: 2026-09-05 America/Toronto
Branch: `v143-contextual-prune-lobo`

## Goal

Remove the synchronous Vercel `maxDuration = 150` wall from Rhythm Guitar analysis without changing the proven V143 model stack or separator outputs.

The promoted production worker remains the compute backend:

- app `dadrock-v143-ai-tab-live`
- function `rhythm_v143_request`
- live endpoint blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- seeded scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`

No scheduler/model/quality change is part of this wiring work.

## Architecture

### Start

1. Browser uploads audio exactly as today.
2. Browser POSTs `/api/analyze-audio-tab`.
3. For Rhythm only, Vercel validates/normalizes the request but does **not** wait for model completion.
4. Vercel calls the existing V143 HTTP bridge with `operation=start`.
5. Bridge creates a random async job id, signs it with the analyzer secret, and spawns a lightweight bridge-side orchestrator.
6. Orchestrator calls the already-deployed `rhythm_v143_request` worker and returns immediately to the bridge start request.
7. Vercel responds `202` with an opaque signed job token and polling interval.

Lead/Bass remain on the existing synchronous legacy path in this phase.

### Temporary result handoff

- A named Modal Queue is used only as a transient handoff channel.
- One queue partition per random job id.
- Partition TTL: **15 minutes maximum**.
- Raw uploaded audio, normalized audio, stems, and model files are never written to the queue.
- Only the structured analyzer JSON result or a bounded failure envelope is queued.
- Result JSON is zlib-compressed and chunked to remain below Modal Queue item-size limits.
- The user explicitly authorized this async wiring after the architecture was proposed; that authorization is scoped to the transient structured-result handoff needed for this job flow, not persistent caching or long-term retention.

### Poll

1. Browser polls `/api/analyze-audio-tab` with `operation=status` + signed job token.
2. Vercel calls the bridge with the same operation/token.
3. Bridge validates the HMAC before looking up the queue partition.
4. Empty partition => `processing` and Vercel returns `202` quickly.
5. Completed partition => bridge reconstructs the structured analyzer result and returns it to Vercel.
6. Vercel applies the **existing** V143 anti-leakage safety contract and existing structured/product placement pipeline before returning the final tab.

### Acknowledge / cleanup

- After the browser successfully receives the final structured tab, it calls `operation=ack`.
- Bridge validates the signed token and clears that job partition immediately.
- If the browser disappears or ack fails, the partition expires automatically at 15 minutes.
- No persistent production result cache is introduced.

## Security / fail-closed rules

- Existing `ANALYZER_API_TOKEN` authorization remains mandatory for every bridge operation.
- Public clients never receive the raw Modal function-call id.
- Job tokens are signed capabilities (`job id + HMAC`) and tampering fails closed.
- Async operations are Rhythm-only; Lead/Bass cannot accidentally route into V143.
- Existing reference-free runtime contract remains mandatory before any completed Rhythm result enters the product path.
- No reference-facing scoring, restricted assets, or quality verdicts.

## Implementation order

1. Add pure async token/envelope helpers + queue orchestrator/start/status/ack operations to `analyzer/v143_modal_http_endpoint.py`.
2. Add a branch-only structural/unit gate proving authorization, HMAC fail-closed behavior, queue payload boundaries, and preservation of the existing synchronous dispatch path.
3. Refactor `app/api/analyze-audio-tab/route.js` minimally so Rhythm start/status/ack use the bridge async operations while the existing completed-result postprocessing remains authoritative.
4. Update `app/ai-tab/page.js` to poll a returned job token, show progress, and ack only after a successful result.
5. Build/test branch source before any production change.
6. Deploy the bridge first and verify start/status protocol without invoking audio/model work.
7. Deploy a Vercel preview and test the UI/API protocol without a model-bearing request.
8. Only after protocol gates are GREEN, run **one** real end-to-end Rhythm job to prove the new property: request survives beyond 150 seconds and eventually returns a tab.
9. Promote Vercel only after that preview proof is GREEN; checkpoint rollback points before production promotion.

## Rollback

- Worker rollback remains `2ab73f0e445c1584fc6dce0112e3091985b4a575`; this async work should not require worker modification.
- HTTP bridge rollback target is current blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`.
- Vercel production remains deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM` until preview protocol/e2e gates pass.

## Hard stops

- No whole-branch merge to `main`.
- No model/scheduler changes as part of async wiring.
- No duplicate model-bearing tests.
- No raw audio/stems in async result storage.
- No result partition TTL above 15 minutes.
- No persistent result cache.
- No production Vercel promotion before preview proof.
