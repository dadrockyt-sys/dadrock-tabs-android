# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-05 00:53 America/Toronto  
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

All workflow steps passed:

- exact branch checkout: SUCCESS;
- exact source/safety gate: SUCCESS;
- Python + pinned Modal CLI: SUCCESS;
- Modal authentication: SUCCESS;
- worker-only Modal deployment: SUCCESS;
- no-audio dependency smoke: SUCCESS;
- aggregate evidence upload: SUCCESS.

Pre-deploy exact source pins matched:

- live endpoint `111bf14a8f91045d3478901f8e36b88a2e7f181a`
- scheduler `fc9b4c45c208d80be7abab64a8959f2a3babcee8`
- deterministic wrapper `28b3e6fe0eb761178b142cf7dcbda533f0bf918d`
- deterministic provider `3c6dcf9b8e7360ba1dd886810f3c14c05ac0579b`
- stem provider `cd180bfb35e8110f031504035af5f11e502c3dc6`
- request adapter `6d1787f34a3b7ca781ced8e5695993a3777406a8`
- Rhythm router `7849f33cd3b849283ccebfda9f721cc40704231e`.

Deployment artifact:

- artifact `9963159697` (`v143-patched-worker-deploy`);
- digest `sha256:627a21923b70c8273b2eceeae64edb17010955b752e0264dbf8a53e2055d855a`.

Aggregate smoke evidence:

- `workerSourceCommit=86f83f6bba33bbe7378ba1eed7294be884e30e45`;
- `seededSchedulerBlob=fc9b4c45c208d80be7abab64a8959f2a3babcee8`;
- `liveEndpointBlob=111bf14a8f91045d3478901f8e36b88a2e7f181a`;
- `cudaAvailable=true`; `deviceName="NVIDIA L4"`;
- `deterministicSeparatorSeed=143`; `demucsShifts=1`;
- Demucs model `htdemucs_6s.yaml`;
- BS-RoFormer model `model_bs_roformer_ep_317_sdr_12.9755.ckpt`;
- feature count `148`;
- Basic Pitch / bend evidence / bend consensus / legato evidence / deterministic provider imports all true;
- audio-download auth policy gate true;
- `referenceFree=true`;
- `professionalReferenceUsed=false`;
- `referenceRuntimeInputUsed=false`;
- `runtimeLabelsRequired=false`;
- `approvedFixtureInvoked=false`;
- `audioBytesRead=false`;
- `separatorModelExecuted=false`;
- `referenceFacingInputs=0`;
- `referenceFacingAccuracyScored=false`;
- `referenceScoreCalls=0`;
- `qualityVerdictMade=false`;
- `rawAudioRetained=false`; `stemBytesRetained=false`;
- `bridgeDeploymentChanged=false`; `vercelDeploymentChanged=false`; `mainMergePerformed=false`.

## PROMOTION STATUS

- Scheduler structural evidence: **GREEN / CLOSED**.
- Exact approved-fixture scheduler runtime evidence: **GREEN / CLOSED**.
- Normal-routing source composition evidence: **GREEN / CLOSED**.
- Pre-production normal-routing evidence boundary: **GREEN / CLOSED**.
- **Production seeded-scheduler worker promotion: GREEN / CLOSED.**
- Vercel/HTTP bridge/main: **UNCHANGED**.
- Rollback remains available at `2ab73f0e445c1584fc6dce0112e3091985b4a575`; no rollback indicated.

## NEXT STEP

1. Do not rerun any closed promotion/model/performance gate merely for reassurance.
2. If additional validation is desired, it must target a genuinely new post-promotion property and remain within retention/reference boundaries; a duplicate model-bearing approved-fixture request is not justified by current evidence.
3. Preserve this promoted worker state as the production baseline for subsequent V143 work.

### Hard stops

- No reference-facing scoring/quality verdict/restricted assets.
- No closed performance/cache/concurrency/Gate-2 reruns absent an invalidating change.
- No duplicate model-bearing normal-route/approved-fixture execution absent a unique demonstrated need.
- No Vercel/bridge/main change as part of this closed worker promotion.
- No weakening exact parity/fail-closed criteria or retention boundaries.
