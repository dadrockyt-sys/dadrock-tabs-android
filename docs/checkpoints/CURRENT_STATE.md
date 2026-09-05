# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 08:15 America/Toronto  
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

### Test execution

- Workflow `.github/workflows/v143-production-gomyway-after-download-fix.yml` measurement commit `14c46a4d4a57652ebe7dd2257bb37001ade8a834`.
- Actions run `33965269193`, job `101304165477`.
- Existing public repository asset `gomyway-midterm-source.m4a`, blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`.
- No professional/reference score; `referenceFacingInputs=0`, `referenceScoreCalls=0`, `qualityVerdictMade=false`.
- Raw request/analyzer response deleted after run; aggregate JSON only retained.

Artifact:

- `9969253856`, `v143-production-post-promotion-breakthrough-check`;
- digest `sha256:e47ee1adca9d2c18eb02c19ee82e3685906c6cb4765636944ddd3013bc46e764`.

Measured result:

- `analysisStatus=504`;
- `analysisEndToEndSeconds=150.66095`;
- `generatedTabPresent=false` because Vercel terminated the synchronous request before analyzer completion;
- no product payload/quality fields were returned before timeout.

### Apples-to-apples prior baseline

Previous run using the same workflow/source asset:

- commit `6f9ed2fa38542a691565a93052bb2be5862f3cf7`;
- run `33889779953`, job `101078353122`;
- request elapsed approximately `150.931s` before HTTP 504.

Difference: about `0.270s`, which is not a meaningful product latency improvement; both runs hit the same Vercel `maxDuration=150` wall.

## Log-only post-promotion stage diagnosis — COMPLETE / NO SECOND MODEL RUN

A separate log-only workflow read existing Modal stdout and invoked no audio/model work:

- workflow commit `9e0aec53337309d40d47e43cf177e276e188cf1e`;
- run `33965453476`, job `101304658150`: SUCCESS;
- artifact `9969270692`, digest `sha256:4c52eeeefcec913c2723a4bd79f4b48c8a431b2839395e09513b4835b6291d93`;
- `audioOrModelInvokedByThisDiagnostic=false`.

Live production stage markers for the breakthrough request:

- `worker.start` `0.000s`;
- download done `1.387s`;
- worker normalize done `1.969s`;
- separator input normalize done `0.302s`;
- direct Demucs child started `0.306s`;
- RoFormer started `0.319s`;
- RoFormer completed `84.079s`;
- cascade Demucs child started immediately at `84.079s`.

No `direct-demucs.done`, `cascade-demucs.done`, or `separator.done` marker had appeared in the bounded log read, even after the Vercel 150-second request had already timed out.

## BREAKTHROUGH VERDICT

**Engineering/scheduler breakthrough: YES, confirmed in production.**

- The new scheduler is actually active.
- Direct CPU Demucs and parent GPU RoFormer begin essentially together (`0.306s` vs `0.319s`).
- Cascade Demucs begins immediately when RoFormer completes (`84.079s`).
- This proves the intended cross-view overlap is working in the live production worker; routing/deployment are not the blocker.

**End-user/product latency breakthrough: NO, not yet.**

- The synchronous production route still returns 504 at about `150.66s`, effectively unchanged from the old `150.93s` timeout.
- The remaining bottleneck is the Demucs work after/concurrent with the ~84-second RoFormer stage.
- A scheduler-only optimization cannot help users until the entire synchronous chain completes within the Vercel 150-second ceiling, or the request architecture stops requiring Vercel to hold the connection open for the full model runtime.

**Musical-quality breakthrough: NOT TESTED / NOT IMPLIED BY THIS SCHEDULER CHANGE.**

Gate 2 proved the scheduler preserves exact separator output identities. This scheduler promotion was a performance change, not a musical-quality change. No reference-facing quality score was run.

## PROMOTION STATUS

- Scheduler structural/runtime/composition evidence: **GREEN/CLOSED**.
- Production scheduler worker promotion: **GREEN/CLOSED**.
- Concurrent scheduler behavior in live production: **CONFIRMED**.
- Synchronous production latency threshold (<150s): **NOT MET**.
- Vercel/HTTP bridge/main: **UNCHANGED**.

## NEXT STEP

1. Treat the production 504 as an architecture/performance-boundary problem, not a routing/deployment regression.
2. Do not rerun the same production audio merely for reassurance.
3. Highest-value next investigation is one of:
   - determine the eventual live direct/cascade Demucs completion times from existing logs only; or
   - design an asynchronous job/result-polling handoff so Vercel no longer has to wait for the full separator/runtime chain.
4. Any additional model execution must demonstrate a distinct new property.

### Hard stops

- No duplicate model-bearing breakthrough request.
- No reference-facing scoring/quality verdict/restricted assets.
- No closed performance/cache/concurrency/Gate-2 reruns absent invalidating change.
- No Vercel/bridge/main change without an explicitly checkpointed architecture plan.
- No weakening exact parity/fail-closed criteria or retention boundaries.
