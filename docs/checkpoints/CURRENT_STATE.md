# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 12:47 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO REFERENCE-FACING QUALITY VERDICT** — performance/identity/routing/product-health diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`.
- Async storage authorization: transient structured result + non-sensitive FunctionCall control metadata only; no raw audio/stems/model bytes; TTL <= 900 seconds; no persistent result cache.

## Production baseline

Vercel production remains unchanged:

- `main` `bb992d901e78ab19645f8edc8e330d5a142ebd8e`;
- deployment `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`;
- production route blob `06234db3e1cc1680b18fd62a765862b213ede3db`, synchronous `maxDuration=150`;
- no production Vercel promotion / no whole-branch merge.

Promoted L4 worker remains unchanged:

- `dadrock-v143-ai-tab-live/rhythm_v143_request`;
- live endpoint blob `111bf14a8f91045d3478901f8e36b88a2e7f181a`;
- scheduler blob `fc9b4c45c208d80be7abab64a8959f2a3babcee8`.

### Production HTTP bridge — HARDENED ASYNC CONTROL DEPLOYED / GREEN

- hardened bridge blob `36584355d9b060fc7b7e20acc62524fbc7bf9005`;
- protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`;
- authoritative bridge-only deploy run `33981874155` / job `101348420851`: SUCCESS;
- artifact `9973991338`, digest `sha256:19245242230abd022ef84b463e5d75e4f5745d04e1a4f2cf0d123d1398d39b10`;
- production Vercel changed=false; worker/scheduler changed=false; synthetic Queue/token smoke GREEN; no audio/model/reference scoring.

## Async architecture

Plan `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Rhythm: start -> signed opaque token -> browser polls Vercel -> Vercel polls bridge -> transient Modal Queue -> existing V143 safety/product pipeline -> result -> ACK clears result + control. Lead/Bass stay synchronous.

Current branch Vercel/UI pins:

- route blob `742954146a86aa36485d0bbdb3fbd6691a64a712`;
- `/ai-tab` page blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.

## Modal `oneshot` looping report — FIXED / PROVEN / DEPLOYED

Root cause was not Modal startup. The pre-hardening bridge discarded the `.spawn()` FunctionCall, so an orchestrator that died before result publication could look like `processing` forever.

Hardened bridge now:

- tracks opaque FunctionCall ID in `control-{job_id}`, TTL 900s;
- status uses `FunctionCall.from_id(...).get(timeout=0)`;
- only Modal timeout means genuinely processing;
- remote/completed failure becomes bounded terminal `failed`;
- ACK clears result + control partitions;
- no sensitive request/job/audio/tab/reference data logged.

Proof chain GREEN:

- source gate `33981347482` / `101347008342`, artifact `9973838904`;
- exact isolated bridge transport `33981493357` / `101347398382`;
- decisive fail-fast transition `33981664796` / `101347836824`, artifact `9973957720`, digest `sha256:42f372c35049c6883be633400230534cb4f842dcdd85b6c6c56139ee9527b98a`;
- hardened production bridge deploy/smoke `33981874155` / `101348420851`.

## Preview boundary — RECONFIRMED / READY FOR ONE MODEL-BEARING E2E

Existing protected Preview deployment from routing-correction run `33968019067` / job `101311460970`:

- deployment ID **`dpl_FzuFoFNsaZcaV73RXSTejoH6cLpz`**;
- URL `https://dadrock-tabs-android-q7v7k9mms-stephen-mcnally-s-projects.vercel.app`;
- target `preview`, status Ready;
- source commit `0c023bdf0e395ddf98501317472ea59e99a00eeb`;
- route blob `742954146a86aa36485d0bbdb3fbd6691a64a712`;
- page blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`;
- Preview branch override `ANALYZER_API_URL_V143` points to `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`;
- `ANALYZER_API_TOKEN`, `BLOB_READ_WRITE_TOKEN`, and legacy `ANALYZER_API_URL` present in Preview;
- protected access via `vercel curl` proven;
- invalid HMAC request reached bridge and returned 400;
- Production environment changed=false; production promotion=false.

Although this Preview was built when the bridge source blob was the pre-hardening async revision, its V143 analyzer URL is a dynamic HTTP endpoint URL. That same URL now resolves to the **hardened deployed bridge blob `36584355d9...`**, so no Preview redeploy is required solely for the bridge hardening.

Approved/reused model-bearing source for the single E2E:

- public repository asset `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`;
- Git blob `4dd709e3fa177b4daeed71ca97f0199757729d4b`;
- raw URL previously exercised through the same analyzer path;
- no professional/reference score authorized.

## EXACT NEXT STEP — SINGLE ASYNC BREAKTHROUGH E2E

Create/execute exactly one Preview-only workflow against `dpl_FzuFoFNsaZcaV73RXSTejoH6cLpz`:

1. POST Rhythm start once using the approved public repository source; require HTTP 202 and a signed job token returned promptly.
2. Poll status only; individual Vercel requests remain bounded and may continue beyond the old 150s synchronous wall.
3. Require terminal HTTP 200 with generated tab and existing V143 reference-free runtime/product safety contract.
4. Record aggregate-only start latency, async total completion latency, poll count, whether total exceeded 150s, product-health/safety fields; do not retain raw transcription.
5. ACK exactly once after valid completion; require transient result/control cleanup response.
6. Delete all raw request/completion files from runner; upload aggregate summary only.
7. Do not launch a second model-bearing request on failure; diagnose first.

A GREEN result proves the needed product breakthrough: analysis can complete even when model runtime exceeds Vercel's 150-second synchronous ceiling.

### Hard stops

- **Exactly one model/audio start request.** No duplicate/retry model invocation.
- No Production Vercel environment change/promotion during this E2E.
- No Deployment Protection weakening.
- No model/scheduler change.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL above 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.
