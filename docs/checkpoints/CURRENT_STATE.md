# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-04 (America/Toronto)  
Branch checkpoint: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## Global scientific state — unchanged

- **V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**
- GOAT restricted bytes admitted/read = **0**; V168 prospective reference-facing score calls = **0**.
- SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`; never rerun/score/weaken/interpolate.
- GuitarSet V3/V4/V5 remain terminal; prospective players `00/01/03` remain sealed; prospective score calls = **0**.
- No reference-facing score was run during merge/Production/Modal work.

**Project Progress Score: 78%.**  
**Test Score: PHASE 1–13 GREEN; PROTECTED REAL-VERCEL PREVIEW GREEN; MAIN MERGE/BUILD/DEPLOY GREEN; PRODUCTION V143 RHYTHM ROUTING PROVEN ACTIVE; FROZEN V143 MODAL L4 WORKER + HTTP BRIDGE RESTORED GREEN; CORRECT BRIDGE NOW LIVE IN PRODUCTION; REAL-AUDIO BLOCKER IS V143 WORKER DOWNLOAD AUTH POLICY; REFERENCE-FACING ACCURACY SCORE NOT RUN.**

## Closed green foundation

- Phases 1–13 reference-blind V143 chain: **GREEN**. Phase 13 run `33833707924`, job `100901804298`, structured renderer `v143-structured-rhythm`, malformed analysis 400, reference score calls 0.
- Protected real-Vercel Preview: run `33843200741`, job `100929522781`, deployment `dpl_6pXryC9R7M5mJwZA7cUt2qh3bBsp`, `/ai-tab` 200, structured PDF 200, Deployment Protection preserved, reference score calls 0.
- Detailed histories remain under `docs/checkpoints/`.

## User-authorized merge to `main` — COMPLETE

- authorization received 2026-09-04 to merge V143 and begin testing with existing “Are You Gonna Go My Way” audio;
- resolved two-parent merge `ceeccfbbb17968c097bb56136487e7ddeaf1a5a4` preserved newer BTS/SEO/payment/site work while overlaying tested V143 Phase 1–13 path;
- full combined build run `33844133380`, job `100932278526`: **SUCCESS**;
- current `main` source SHA remains **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**.

## Authorized existing Gomyway audio

- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`;
- blob SHA `4dd709e3fa177b4daeed71ca97f0199757729d4b`;
- 3,464,988 bytes.

## Production real-audio diagnostics

1. Product static URL returned 404 before analyzer: run `33844432185`, job `100933164743`.
2. Raw-GitHub URL reached Production but legacy analyzer was selected because V143 env was absent: run `33844704674`, job `100933970052`, runtime `usingV143RhythmAnalyzer: false`; route 502.
3. Production V143 env restored and exact current `main` rebuilt/redeployed: run `33879884350`, job `101056165576`; deployment `dpl_CojGzPaq77YRh5mLpbVTEseuWjrg`.
4. Protected authenticated smoke proved V143 selected but obsolete Modal URL returned 404: run `33880271454`, job `101057491176`, runtime `usingV143RhythmAnalyzer: true`.
5. Frozen Modal topology restored from exact SHA `379ca54cce0f7f962c1e22caebfd6f49b8e4edb9`: run `33884039647`, job `101059368271`; L4 dependency smoke green; bridge unauthenticated POST = 401; reference score calls = 0.
6. Correct bridge env update required non-interactive `vercel env update --yes`; exact current `main` rebuilt and deployed successfully in run **`33884535351`**, job **`101060978549`**.

### Current Production deployment

- deployment: **`dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM`**;
- source: exact unchanged `main` **`bb992d901e78ab19645f8edc8e330d5a142ebd8e`**;
- target/status: Production / Ready;
- aliases include `dadrocktabs.com` and `www.dadrocktabs.com`;
- protected authenticated `/ai-tab`: **200**;
- Deployment Protection remained enabled.

### Restored-bridge Gomyway attempt — reached correct V143 stack, then 502 download failure

Run `33884535351`, job `101060978549`:

- Production `ANALYZER_API_URL_V143` updated to restored decoupled bridge `https://dadrockyt--dadrock-v143-http-bridge-analyze.modal.run`;
- exact current `main` build: **SUCCESS**;
- exact prebuilt Production deployment: **SUCCESS**;
- protected `/ai-tab`: **200**;
- Gomyway Rhythm analysis: **502**;
- safe aggregate error: **`The analyzer could not download the audio file.`**;
- runtime on exact deployment proves:

```text
usingV143RhythmAnalyzer: true
analyzerData: { detail: 'The analyzer could not download the audio file.' }
```

This is the first failure after both Vercel V143 selection and the correct frozen Modal worker/bridge topology were proven active.

Aggregate artifact only: `v143-production-restored-bridge-gomyway-v2`, artifact id `9941326017`. Raw analyzer output/tab/PDF was not retained. Preview was intentionally skipped because analysis was not 200.

## Downloader root-cause candidate — strong code-level evidence

The frozen V143 L4 worker function `_download_blob_to_path(audio_url, blob_token, destination)` currently does:

```python
headers = {}
if blob_token:
    headers['Authorization'] = f'Bearer {blob_token}'
requests.get(audio_url, headers=headers, timeout=120)
```

Current Vercel `/api/analyze-audio-tab` always sends `BLOB_READ_WRITE_TOKEN` to the selected analyzer when configured. Therefore a raw public GitHub URL is currently requested by the worker with a **Vercel Blob bearer token attached to a non-Vercel host**. The exact same raw GitHub URL was already reachable from GitHub Actions, while the worker download fails after receiving the blob token.

Safe repair direction: send the Blob bearer token only to Vercel Blob hosts (`blob.vercel-storage.com` or subdomains) and send no Authorization header to public/non-Blob hosts such as `raw.githubusercontent.com`. This also prevents credential forwarding to arbitrary audio hosts.

## Latent runtime-contract compatibility issue found before next deploy

Current `main` verifies all four V143 anti-leakage flags before structured rendering:

- `referenceFree === true`;
- `professionalReferenceUsed === false`;
- `referenceRuntimeInputUsed === false`;
- `runtimeLabelsRequired === false`.

The restored frozen worker currently emits the first, second and fourth flags, but does **not** emit `referenceRuntimeInputUsed`. Once download succeeds, current `main` would therefore fail closed at the next layer unless the worker explicitly emits `referenceRuntimeInputUsed: false`.

Adding that explicit false flag is metadata compatibility only; it does not authorize or introduce any reference input.

## Fresh-chat authorization — EXPLICIT

The user explicitly authorized continuation of the non-reference-facing Production work. Authorization covers exact V143 Modal worker/bridge restoration and narrowly scoped fixes required to exercise the existing reference-free pipeline with the repository-owned Gomyway audio, Vercel env correction/redeploy as required, workflow edits/reruns, preview/PDF contract checks with raw outputs discarded, and GitHub Actions/Vercel log inspection.

It **does not** authorize reference-facing accuracy scoring, restricted GOAT access, sealed GuitarSet prospective access, reopening SplitMySong terminal work, or weakening fail-closed/safety boundaries.

## Safety/accounting now

- merge to `main`: authorized and complete;
- current `main`: `bb992d901e78ab19645f8edc8e330d5a142ebd8e`;
- Production deployment: `dpl_5BdFAMHeiaA3rQ9QGUdHneY1rexM` READY;
- Production V143 Rhythm route selection: **ACTIVE / PROVEN**;
- correct frozen HTTP bridge: **ACTIVE / PROVEN**;
- frozen L4 worker: **ACTIVE / DEPENDENCY SMOKE GREEN**;
- Deployment Protection: **preserved**;
- reference-facing score calls: **0**;
- GOAT restricted bytes: **0**;
- GuitarSet prospective sealed reads: **0**;
- raw Gomyway transcription/PDF retained: **false**;
- current real-audio verdict: **NO PIPELINE QUALITY VERDICT YET — REQUEST REACHES RESTORED V143; WORKER DOWNLOAD AUTH POLICY BLOCKS AUDIO INGEST**.

## NEXT SAFE ACTION — AUTHORIZED

1. Add a tiny testable audio-download auth policy: Blob bearer authorization is allowed only for `blob.vercel-storage.com` and `*.blob.vercel-storage.com`; public/non-Blob URLs receive no Authorization header.
2. Unit-test the policy for raw GitHub, Vercel public Blob, Vercel private Blob, deceptive suffix hosts, malformed URLs, and empty token.
3. Update `v143_modal_live_endpoint.py` to use that policy and explicitly emit `liveV143.referenceRuntimeInputUsed = false`.
4. Redeploy only the V143 L4 worker from the checkpoint branch; the restored HTTP bridge need not change for Rhythm.
5. Re-run the worker dependency smoke and then the authenticated aggregate-only Production Gomyway smoke against current Production.
6. Require `usingV143RhythmAnalyzer: true`, analysis 200, `rhythmCanaryActive: true`, and all four runtime safety flags before any pipeline interpretation.
7. If analysis reaches 200, generate Production structured preview; retain only aggregate quality/placement/PDF contract metadata and delete raw transcription/PDF/request outputs.
8. Report only internal signs of success; **reference-facing accuracy remains unarmed**.
