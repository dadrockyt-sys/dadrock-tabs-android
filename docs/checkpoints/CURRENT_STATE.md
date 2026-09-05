# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 12:45 America/Toronto  
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

- hardened bridge blob **`36584355d9b060fc7b7e20acc62524fbc7bf9005`**;
- protocol blob `1bd55017e16a4e1d8b14c7429492f811a43a28d8`;
- previous pre-hardening async bridge blob `e0cecefacead73d69a905fd6bfb2049b21c87bc3`;
- rollback sync bridge blob `9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6`.

Deliberate bridge-only deployment workflow `.github/workflows/v143-deploy-hardened-async-bridge.yml`:

- first run `33981834369` / job `101348311754` correctly **FAILED CLOSED before deploy** because the checkpointed bridge pin was stale (`365843550f...` vs actual Git blob `36584355d9...`); protocol/worker/scheduler pins matched and Modal was not touched;
- exact bridge pin corrected in commit `dedda6b64999a68f390e276cc204608cefb55109`;
- authoritative run `33981874155` / job `101348420851`: **SUCCESS**;
- exact source boundary GREEN: bridge `36584355d9...`, protocol `1bd55017...`, worker `111bf14a...`, scheduler `fc9b4c45...`;
- `modal deploy --env main analyzer/v143_modal_http_endpoint.py` SUCCESS;
- production `dadrock-v143-http-bridge/async_protocol_smoke` SUCCESS;
- app identity `dadrock-v143-http-bridge`, Queue `dadrock-v143-async-results`, signed token roundtrip GREEN, Queue roundtrip/clear GREEN, TTL `900s`;
- artifact `9973991338`, digest `sha256:19245242230abd022ef84b463e5d75e4f5745d04e1a4f2cf0d123d1398d39b10`;
- bridge-only deployment: true; production Vercel changed=false; worker changed=false; scheduler changed=false; audioRead=false; modelExecuted=false; reference inputs/scores `0`; quality verdict false.

## Breakthrough diagnosis — CLOSED

- production synchronous request run `33965269193` / job `101304165477`: HTTP 504 at `150.66095s`;
- previous equivalent ~`150.931s`;
- log-only run `33965453476` proved direct Demucs and RoFormer overlap (`0.306s` / `0.319s`), RoFormer done/cascade start `84.079s`;
- scheduler breakthrough YES; synchronous product breakthrough NO.

## Async architecture

Plan `docs/checkpoints/V143_ASYNC_JOB_ARCHITECTURE_PLAN.md`, commit `e0aef99dcdf931b66c0e1a081160e3cc5c6cb3c2`.

Rhythm: start -> signed opaque token -> browser polls Vercel -> Vercel polls bridge -> transient Modal Queue -> existing V143 safety/product pipeline -> result -> ACK clears result + control. Lead/Bass stay synchronous.

Current branch Vercel/UI pins:

- route blob `742954146a86aa36485d0bbdb3fbd6691a64a712`;
- `/ai-tab` page blob `de39f2715c6875d757ef730c9e3182ccd4aa00a4`.

## Modal `oneshot` report — ROOT CAUSE/FIX

User reported Modal showing an apparent looping/failing `oneshot`. Model-bearing E2E was paused.

No-audio startup discriminators proved the primitive/topology works:

- L4 cold-start `33980499498` / `101344748201`, artifact `9973612728`: GREEN;
- isolated `.spawn()` `33980754694` / `101345414660`, artifact `9973684032`: GREEN;
- spawned orchestrator -> L4 dependency smoke `33980891422` / `101345785629`, artifact `9973722881`: GREEN;
- exact deployed production orchestrator -> exact real worker fail-before-download `33981009987` / `101346107709`, artifact `9973751225`: GREEN, FunctionCall `fc-01M1S9SEY1YY29VYHVWWSSSMX6`, 9.061s, no audio/model.

Actual robustness gap: pre-hardening bridge discarded `.spawn()` FunctionCall. Empty result Queue therefore looked like `processing` forever even if the orchestrator had already failed.

Hardened behavior now deployed:

- tracks opaque FunctionCall ID in `control-{job_id}`, TTL 900s;
- status uses `FunctionCall.from_id(...).get(timeout=0)`;
- only Modal timeout means genuinely processing;
- remote/completed failure becomes bounded terminal `failed`;
- ACK clears result + control partitions;
- no sensitive request/job/audio/tab/reference fields logged;
- worker/scheduler/model unchanged.

### Hardening proof chain — GREEN

- source/no-model gate `33981347482` / `101347008342`, artifact `9973838904`, digest `sha256:a74c088f9a6e412deba9b47f400dc221bf2c992021ca48d2185ec2f7addab9d5`;
- exact isolated hardened bridge transport `33981493357` / `101347398382`: GREEN;
- first fail-fast diagnostic `33981582672` failed only because the diagnostic used an unhydrated cross-app Function object; not product evidence;
- diagnostic corrected in commit `4698572e18618463555b765ea1730d0da1d7e8ca`, workflow update `776252818c7a0fac886f9d646e2b31a542d456a1`;
- decisive corrected fail-fast run `33981664796` / job `101347836824`: **SUCCESS**;
- artifact `9973957720`, digest `sha256:42f372c35049c6883be633400230534cb4f842dcdd85b6c6c56139ee9527b98a`;
- real isolated orchestrator FunctionCall tracked; invalid URL fails before download/model; status reaches terminal `failed` instead of indefinite `processing`; ACK clears both partitions; no audio/model/reference score.

**Reported looping symptom is now addressed in the production bridge.**

## Previously closed async/Vercel evidence — GREEN

- Protocol current-pin `33966778940`, artifact `9969677990`.
- Vercel composition `33966794524`, artifact `9969683328`.
- Preview build `33966323815` / `101306988163`, artifact `9969549184`.
- Preview routing correction `33968019067` / `101311460970`: GREEN / no model/audio.

## NEXT STEP

1. Hardened production bridge is now GREEN; the model-bearing pause due to the oneshot control-loop report is lifted.
2. Reconfirm the current Preview deployment/source identity and preview-only `ANALYZER_API_URL_V143` routing; do not modify Production Vercel.
3. Run **exactly one** model-bearing Preview async Rhythm E2E using the approved public/repository test source. New property to prove: start request returns promptly, status polling survives past 150s, terminal structured tab arrives through Queue, V143 reference-free safety/product pipeline passes, and ACK clears transient state.
4. If GREEN, checkpoint the end-user async breakthrough evidence before any production Vercel promotion.

### Hard stops

- No duplicate model/audio request.
- No Production Vercel environment change/promotion until one Preview async E2E is GREEN.
- No Deployment Protection weakening.
- No model/scheduler change.
- No reference-facing scoring/quality verdict/restricted assets.
- No raw audio/stems/model bytes in async storage/control metadata.
- No TTL above 15 minutes / no persistent result cache.
- No whole-branch merge to `main`.
