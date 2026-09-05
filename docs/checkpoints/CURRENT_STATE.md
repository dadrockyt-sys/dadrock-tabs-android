# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 07:11 America/Toronto  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Older dedicated checkpoints remain authoritative; omission here does not revoke frozen boundaries.

## Frozen boundaries

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`; V167 CLOSED / TERMINAL.**
- GOAT restricted bytes = **0**; reference-facing score calls = **0**.
- SplitMySong terminal `FAIL_CLOSED_NO_CANDIDATE`; GuitarSet `00/01/03` sealed.
- **NO QUALITY VERDICT** — performance/identity/routing diagnostics only.
- Persistent production cache remains `BLOCKED_BY_RETENTION_POLICY`; no persistent user-audio/stem/result retention without explicit permission.

## Production — SEEDED SCHEDULER WORKER PROMOTED / GREEN

Unchanged surfaces:

- Vercel/web `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`; route blob `06234db3e1cc1680b18fd62a765862b213ede3db`.
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
- `MODEL_BEARING_E2E_NOT_JUSTIFIED`; normal-routing pre-production evidence boundary **GREEN/CLOSED**.
- Production plan `docs/checkpoints/V143_SEEDED_SCHEDULER_PRODUCTION_PLAN.md`, commit `b84d7c05cac15bc2d3196278502029a196412541`.

## Production worker promotion — GREEN / CLOSED

Deliberate serialized deployment:

- workflow `.github/workflows/v143-deploy-patched-worker.yml` blob `39e44d4275578da20c9110ea29ce1a538ab3169f`;
- trigger/source commit `86f83f6bba33bbe7378ba1eed7294be884e30e45`;
- Actions run `33945389816`;
- job `101250418913`: **SUCCESS**;
- deploy target was only `modal deploy --env main analyzer/v143_modal_live_endpoint.py`.

Deployment artifact `9963159697` (`v143-patched-worker-deploy`), digest `sha256:627a21923b70c8273b2eceeae64edb17010955b752e0264dbf8a53e2055d855a`, verifies scheduler blob `fc9b4c45...`, live endpoint `111bf14a...`, NVIDIA L4, deterministic seed 143, frozen model identities, reference-free safety, and no audio/model execution during smoke.

## Post-promotion breakthrough check — ONE PRODUCTION REQUEST / IN PROGRESS

User explicitly requested a test for a possible breakthrough. This creates a genuinely new post-promotion property: **real synchronous production-route latency after the seeded scheduler promotion**.

- Test workflow `.github/workflows/v143-production-gomyway-after-download-fix.yml` updated in commit `14c46a4d4a57652ebe7dd2257bb37001ade8a834`.
- Workflow now records exact curl `time_total` as `analysisEndToEndSeconds`, promoted worker/scheduler identity metadata, reference-free contract, and product-health signals only.
- It does **not** perform professional/reference scoring and explicitly records `qualityVerdictMade=false`.
- Raw analyzer response/request are deleted; only aggregate JSON is retained.
- Current Actions run `33965269193`, job `101304165477`.
- Preflight checkout/source/Node/Vercel setup/protected route access all **SUCCESS**.
- Step `Analyze Gomyway through promoted V143 worker and measure latency` currently **IN PROGRESS**.

### Apples-to-apples prior production baseline

Previous run of the same workflow/source asset:

- commit `6f9ed2fa38542a691565a93052bb2be5862f3cf7`;
- run `33889779953`, job `101078353122`;
- analysis request started at `2026-09-04T15:30:10.176Z` and returned HTTP `504` at `15:32:41.107Z`;
- elapsed wall approximately **150.931 seconds**, matching the current Vercel route `maxDuration = 150` ceiling;
- no tab/payload was returned before timeout.

### Breakthrough criterion

- **Major production latency breakthrough:** current promoted request returns HTTP 200 + generated tab + safety contract before the ~150-second Vercel ceiling.
- If current request still returns 504 around 150 seconds, the new scheduler may still be materially faster internally, but it has **not** crossed the synchronous production-route threshold. In that case retrieve aggregate Modal stage logs without another model invocation to measure the actual post-promotion worker timeline.

## PROMOTION STATUS

- Scheduler structural evidence: **GREEN / CLOSED**.
- Exact approved-fixture scheduler runtime evidence: **GREEN / CLOSED**.
- Normal-routing source composition evidence: **GREEN / CLOSED**.
- Production seeded-scheduler worker promotion: **GREEN / CLOSED**.
- Post-promotion synchronous production latency breakthrough check: **IN PROGRESS**.
- Vercel/HTTP bridge/main: **UNCHANGED**.

## NEXT STEP

1. Observe run `33965269193` to terminal state; do not retrigger.
2. Inspect aggregate breakthrough artifact for exact `analysisEndToEndSeconds`, status, tab presence, and safety contract.
3. Compare against prior ~150.931-second 504 baseline.
4. If still 504, fetch recent aggregate-only Modal stage markers without invoking audio/model again to determine internal scheduler/worker completion time and next bottleneck.

### Hard stops

- No second model-bearing breakthrough request while run `33965269193` is unresolved.
- No reference-facing scoring/quality verdict/restricted assets.
- No closed performance/cache/concurrency/Gate-2 reruns.
- No Vercel/bridge/main change merely to make this measurement pass.
- No weakening exact parity/fail-closed criteria or retention boundaries.
