# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 08:20 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`; no persistent user-audio/stem/result retention without explicit permission.

## Production — SEEDED SCHEDULER WORKER PROMOTED / GREEN

Unchanged surfaces:

- Vercel/web `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`; route blob `06234db3e1cc1680b18fd62a765862b213ede3db` with `maxDuration = 150`.
- Vercel deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`, READY / unchanged.
- HTTP bridge source blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`; bridge deployment unchanged; it dynamically resolves `dadrock-v143-ai-tab-live`.
- `main` merge performed: false.

Promoted worker candidate:

- worker deploy source commit `86f83f6bba33bbe7378ba1eed7294be884e30e45`;
- live endpoint blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`;
- seeded scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`;
- scheduler implementation lineage commit `6772a0ca1d700ea6861cd4401b51e093144c8d26`;
- rollback source commit `2ab73f0e445c1584fc6dce0112e3091985b4a575`, same live endpoint blob with prior serialized scheduler blob `250534e516cad36e49cae35b6eab2b88654be2d3`.

## Closed promotion evidence

- Gate 1 structural: run `33942915753` / job `101243642285` — **GREEN/CLOSED**.
- Gate 2 exact approved-fixture runtime: run `33943100948` / job `101244148835` / artifact `9962641557` — **GREEN/CLOSED**.
- Gate 3A normal-routing composition: run `33945157629` / job `101249801382` / artifact `9963085825` (`sha256:9084a0d17ca44154e66a89f78546b6e210e3a302110e9e560c99b9f20a39ad09`) — **GREEN/CLOSED**.
- Production worker deployment run `33945389816` / job `101250418913` / artifact `9963159697` — **GREEN/CLOSED**.

## Post-promotion breakthrough check — COMPLETE

User explicitly requested one real production test for a possible breakthrough. This test targeted the new property that had not been proven pre-deploy: **synchronous production-route latency after scheduler promotion**.

- Measurement commit `14c46a4d4a57652ebe7dd2257bb37001ade8a834`; run `33965269193`, job `101304165477`.
- Artifact `9969253856`, digest `sha256:e47ee1adca9d2c18eb02c19ee82e3685906c6cb4765636944ddd3013bc46e764`.
- `analysisStatus=504`; `analysisEndToEndSeconds=150.66095`; no tab reached Vercel before timeout.
- Prior apples-to-apples run was ~`150.931s` → same Vercel ceiling; no meaningful synchronous product-latency gain.
- No professional/reference score; `referenceFacingInputs=0`, `referenceScoreCalls=0`, `qualityVerdictMade=false`.

## Log-only post-promotion stage diagnosis — COMPLETE

- Log-only commit `9e0aec53337309d40d47e43cf177e276e188cf1e`; run `33965453476`, job `101304658150`; artifact `9969270692`.
- No audio/model invocation by the diagnostic.
- Live markers: worker start `0.000s`; download `1.387s`; worker normalize `1.969s`; separator normalize `0.302s`; direct Demucs start `0.306s`; RoFormer start `0.319s`; RoFormer done `84.079s`; cascade Demucs start `84.079s`.
- Scheduler overlap is therefore active in production; synchronous Vercel waiting is the product blocker.

## BREAKTHROUGH VERDICT

- **Engineering/scheduler breakthrough: YES / CONFIRMED IN PRODUCTION.**
- **End-user synchronous latency breakthrough: NO / VERCEL 150s CEILING STILL HIT.**
- Musical-quality breakthrough: not tested and not implied by the scheduler-only change.

## Async breakthrough architecture — PLAN CHECKPOINTED / IMPLEMENTATION AUTHORIZED

User explicitly instructed: “Lets get this wiring correct and make the breakthrough we need.” This follows the proposed async architecture and authorizes implementation of the transient result handoff required for start/poll completion.

Plan: `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Chosen architecture:

- promoted `dadrock-v143-ai-tab-live/rhythm_v143_request` worker remains unchanged;
- existing HTTP bridge gains Rhythm-only `start`, `status`, and `ack` operations;
- bridge start spawns a lightweight orchestrator instead of waiting for the worker;
- browser receives a signed opaque job token immediately through Vercel;
- browser polls Vercel; Vercel polls bridge; bridge reads only transient structured-result state;
- result handoff uses a workspace-only Modal Queue partition with **15-minute maximum TTL**;
- raw audio, normalized audio, stems, and model bytes never enter the queue;
- structured result is compressed/chunked for queue size limits;
- result partition is cleared on successful browser receipt/ack; TTL is the fail-safe cleanup;
- no persistent result cache is introduced;
- Lead/Bass remain on the current synchronous legacy path;
- existing V143 anti-leakage/product postprocessing in Vercel remains authoritative after async completion.

Implementation/deployment order is fail-closed: bridge source + pure gate → Vercel route/UI source + build → bridge protocol deploy/test without model → Vercel preview protocol test without model → exactly one model-bearing preview e2e proving completion beyond 150s → production promotion only if GREEN.

Production remains unchanged at this checkpoint.

## NEXT STEP

1. Implement branch-only async bridge helpers/orchestrator/start/status/ack while preserving the current default synchronous endpoint.
2. Add and run a no-model structural/unit gate for HMAC authorization, queue boundaries, TTL, chunking, and synchronous fallback preservation.
3. Checkpoint exact bridge blob/gate result before any bridge deployment.
4. Then wire Vercel API + `/ai-tab` polling UI and build/test branch source.

### Hard stops

- No duplicate model-bearing breakthrough request.
- No model/scheduler changes as part of async wiring.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async result storage.
- No async result TTL above 15 minutes; no persistent result cache.
- No whole-branch merge to `main`.
- No production Vercel promotion before preview protocol/e2e proof.
- No weakening exact parity/fail-closed criteria or retention boundaries.
