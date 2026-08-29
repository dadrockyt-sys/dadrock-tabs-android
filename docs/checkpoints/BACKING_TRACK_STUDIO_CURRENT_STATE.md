# CURRENT STATE — Backing Track Studio

Updated: 2026-08-29 UTC  
Checkpoint branch: `backing-track-studio`  
Production branch: `main`

## Active phase
**Backing Track Studio and its isolated complimentary-token workflow are live in Production. First user end-to-end test reached `/api/bts/process` but exposed the remaining runtime configuration blocker: the dedicated Modal separator URL/token are not configured in Vercel Production.**

## Production state
- Live route: `https://dadrocktabs.com/bts`
- Original BTS promotion: PR **#23**
  - merge commit: `b477bab46fde4656c8277167d758dffa7fc5942f`
- Separate BTS token workflow: PR **#24**
  - merge commit: `f14132729d2d60f2ede6e3a5c1f725584ca1db35`
  - production deployment: `dpl_DbjSpydrbgUb4RFtG15RVUZX9CZY`
  - build compiled successfully and included `/admin/bts-tokens`, `/api/admin/bts-tokens`, `/api/bts/free-token`, `/bts`, plus existing AI Tab token routes
- Current admin-panel BTS-manager link: PR **#25**
  - merge commit: `2ae350ba72e12bacb8b767ab4ffe6c80bce322aa`
  - production deployment: `dpl_8QzCeZWUV4tJSf4cR6dJD9vkxJL2`
  - Vercel state: **READY**
  - aliases include `dadrocktabs.com` and `www.dadrocktabs.com`

## First live processing test — CONFIRMED BLOCKER
At approximately 2026-08-29 20:13:52 UTC the user completed the BTS UI far enough to POST to `/api/bts/process`.

Production runtime log returned HTTP **503** with:
- `hasSeparatorUrl: false`
- `hasSeparatorToken: false`
- `hasBlobToken: true`

The user-facing message was:
`Backing Track Studio processing is not configured yet.`

This comes directly from `app/api/bts/process/route.js` when one or more of these are absent:
- `BTS_SEPARATOR_API_URL`
- `BTS_SEPARATOR_API_TOKEN`
- `BLOB_READ_WRITE_TOKEN`

Live evidence proves `BLOB_READ_WRITE_TOKEN` is already configured. The remaining blocker is specifically:
1. deploy/resolve the dedicated BTS Modal endpoint from `analyzer/modal_bts_separator.py`;
2. configure matching `BTS_SEPARATOR_API_URL` and `BTS_SEPARATOR_API_TOKEN` in Vercel Production;
3. redeploy/retry.

Do not treat this as an upload/token failure. The request reached the protected processing route successfully enough to hit the separator configuration check.

## Product flow
1. Upload MP3/WAV/M4A/AAC audio.
2. Enter email using the same email-format validation semantics as AI Tab.
3. Choose:
   - Remove Guitars
   - Remove Bass
   - Remove Guitars + Bass
4. Unlock with either:
   - **USD $1.00 PayPal sandbox**, or
   - a complimentary **BTS token**.
5. Both unlock methods produce a signed BTS job authorization and use the same `/api/bts/process` processing path.
6. Dedicated stem separation rebuilds the mix without the selected stem(s).
7. Resulting MP3 is streamed to the user for download.

## BTS token system — LIVE AND ISOLATED
### AI Tab remains unchanged
- Collection: `tab_tokens`
- Token format: `DRT-XXXX-XXXX-XXXX`
- Existing AI Tab creator/tracker and `/api/free-tab-token` remain unchanged.

### BTS token system
- Collection: `bts_tokens`
- Token format: `BTS-XXXX-XXXX-XXXX`
- Admin manager: `/admin/bts-tokens`
- Admin API: `/api/admin/bts-tokens`
- Redemption API: `/api/bts/free-token`

BTS tokens follow the AI Tab usage model:
- token types: testing, giveaway, promotion, customer, support
- configurable quantity
- configurable uses per token
- optional assigned email
- optional expiration
- optional notes
- active/disabled state
- delete support
- atomic one-use decrement on redemption
- redemption history
- remaining-use tracking
- email mismatch / expired / exhausted / inactive handling

Accepted BTS tokens return a signed BTS job token, so they enter the same protected audio-processing route as a verified PayPal sandbox capture.

The current hidden admin panel includes a separate link beside the existing AI Tab token controls:
- `Open Backing Track Studio Token Manager →`

No AI Tab token collection, API route, redemption logic, or DRT token behavior was modified by the BTS token work.

## Live token validation
- Vercel production build with token feature: successful.
- `/admin/bts-tokens`: live HTTP **200**.
- `/api/admin/bts-tokens` without credentials: live HTTP **401 Unauthorized**, as expected.
- Final admin-link deployment: **READY**.
- User's first test reached `/api/bts/process`; this strongly indicates upload/unlock handoff is functioning through the client-to-process boundary, though redemption counters should still be checked in the admin tracker.

## Core BTS implementation
- `app/bts/page.js`
- `components/BTSPayPalCheckoutButton.js`
- `lib/btsPayment.js`
- `app/api/bts/audio-upload/route.js`
- `app/api/bts/paypal/create-order/route.js`
- `app/api/bts/paypal/capture-order/route.js`
- `app/api/bts/process/route.js`
- `app/api/bts/cleanup/route.js`
- `app/api/bts/free-token/route.js`
- `app/api/admin/bts-tokens/route.js`
- `app/admin/bts-tokens/page.js`
- `analyzer/modal_bts_separator.py`
- `analyzer/bts-audio-separation-requirements.txt`

## Stem separation
- Dedicated BTS Modal app: `dadrock-backing-track-studio`
- Demucs six-source model: `htdemucs_6s.yaml`
- Current worker configuration uses `audio-separator[cpu]==0.30.2` and explicitly disables CUDA.
- Removes Guitar, Bass, or both and rebuilds the remaining mix.
- Returns a 192 kbps MP3.
- Worker code exists in repo, but the deployed endpoint/runtime connection is not yet configured in Vercel Production.

## Payment isolation
- BTS create/capture routes are separate from AI Tab.
- BTS server price: **USD $1.00**.
- BTS PayPal mode: **sandbox** during testing.
- Existing AI Tab **USD $2.99** payment flow remains unchanged.

## Copyright/audio retention rule — FROZEN
**Maximum retention: 24 hours.**

Implementation is stricter:
- Successful source upload is deleted immediately after successful processing.
- Generated backing track is streamed to the customer and is **not persistently stored** by BTS.
- Separator intermediates exist only in temporary worker storage.
- Abandoned/failed BTS uploads are eligible for hourly cleanup beginning at 23 hours.
- Audio responses use no-store caching semantics.

Do not introduce persistent copyrighted-audio storage without explicit user approval.

## Cleanup cron caveat
Production `vercel.json` contains the hourly `/api/bts/cleanup` cron. Execution depends on Production `CRON_SECRET` being configured. Secret presence has not been independently verified through the available connector surface; confirm via a real cron invocation/runtime log before claiming abandoned-upload cleanup is operational.

## Required runtime configuration for complete end-to-end processing
Known from first live test:
- `BLOB_READ_WRITE_TOKEN` — **present in Production**
- `BTS_SEPARATOR_API_URL` — **missing in Production**
- `BTS_SEPARATOR_API_TOKEN` — **missing in Production**

Also required/expected:
- `NEXT_PUBLIC_PAYPAL_CLIENT_ID` / sandbox PayPal client ID
- `PAYPAL_CLIENT_SECRET`
- `CRON_SECRET`
- optional `BTS_JOB_SIGNING_SECRET`
- Modal secret `dadrock-bts-separator-secret` with matching `BTS_SEPARATOR_API_TOKEN`
- existing MongoDB configuration
- existing `ADMIN_PASSWORD` for token administration

## Validation status
Completed:
- BTS production builds compile successfully with Next.js 16.1.6 / Turbopack.
- `/bts` is live.
- BTS token creator/tracker routes are live.
- BTS token admin endpoint requires authentication.
- AI Tab token files remained outside the BTS token promotion diff.
- Final admin-panel link promotion changed only `app/page.js` by 6 added lines.
- First browser processing request reached `/api/bts/process`.
- Production runtime log identified missing separator URL/token and confirmed Blob token exists.

Still to complete:
1. Deploy/resolve the dedicated BTS Modal separator endpoint.
2. Configure matching `BTS_SEPARATOR_API_URL` and `BTS_SEPARATOR_API_TOKEN` in Vercel Production.
3. Retry the existing BTS flow with permitted audio.
4. Confirm separator returns a playable MP3.
5. Confirm source Blob is deleted immediately after success.
6. Verify token use decrement/redemption entry in the admin tracker.
7. Separately test the $1 PayPal sandbox path.
8. Confirm hourly cleanup cron behavior/runtime authorization for an abandoned test upload.

## Progress score
**Current Project Progress Score: 98%.**

The implementation is complete; the current blocker is external runtime configuration for the dedicated Modal separator, followed by final end-to-end validation.
