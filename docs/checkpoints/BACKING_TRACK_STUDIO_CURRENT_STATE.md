# CURRENT STATE — Backing Track Studio

Updated: 2026-08-29 UTC  
Checkpoint branch: `backing-track-studio`  
Production branch: `main`

## Active phase
**BTS is live in Production, and the latest user test proves Demucs completed six-stem waveform separation. The remaining defect is in the post-separation stem handoff/rebuild path. Work in this continuation is isolated to `backing-track-studio`; do not modify `main`, Vercel Production, or the live Modal deployment.**

## Continuation note — 2026-08-29 22:18 UTC
- Re-fetched this checkpoint first, per instruction.
- Confirmed `backing-track-studio` head was still `23f5fda9436281b2357ac73a9ce147aaad6146e5` (`Record first BTS live processing blocker`), so the branch does **not** yet contain later worker hardening that appeared on `main` during the live test cycle.
- User screenshot from approximately 22:07 UTC shows `audio-separator` logged **Separation complete!** and wrote all six expected files:
  - `normalized_(Bass)_htdemucs_6s.wav`
  - `normalized_(Drums)_htdemucs_6s.wav`
  - `normalized_(Other)_htdemucs_6s.wav`
  - `normalized_(Vocals)_htdemucs_6s.wav`
  - `normalized_(Guitar)_htdemucs_6s.wav`
  - `normalized_(Piano)_htdemucs_6s.wav`
- Therefore this is no longer a model/separation failure. The failure is after successful stem generation, before/during BTS stem discovery/rebuild.
- Read-only comparison against `main` found later worker changes that are not on the BTS branch yet: use the installed `audio-separator` CLI directly, run it with `cwd` set to the requested stem output directory, and treat written stem files as source of truth even if audio-separator exits non-zero after completion.
- Next action: port the smallest safe worker hardening to `backing-track-studio`, validate the branch code/contracts, then update this checkpoint again. No Production deploy will be triggered from this continuation.

## Production state already established before this continuation
- Live route: `https://dadrocktabs.com/bts`
- Original BTS promotion: PR **#23**
  - merge commit: `b477bab46fde4656c8277167d758dffa7fc5942f`
- Separate BTS token workflow: PR **#24**
  - merge commit: `f14132729d2d60f2ede6e3a5c1f725584ca1db35`
- Current admin-panel BTS-manager link: PR **#25**
  - merge commit: `2ae350ba72e12bacb8b767ab4ffe6c80bce322aa`

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

Accepted BTS tokens return a signed BTS job token, so they enter the same protected audio-processing route as a verified PayPal sandbox capture.

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
- Current worker dependency: `audio-separator[cpu]==0.30.2`
- Removes Guitar, Bass, or both and rebuilds the remaining mix.
- Returns a 192 kbps MP3.
- Latest live evidence confirms the model produced all six stems; current work is hardening the handoff from produced stems to the rebuild step.

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
Previously confirmed during live testing:
- `BLOB_READ_WRITE_TOKEN` — present in Production
- `BTS_SEPARATOR_API_URL` / `BTS_SEPARATOR_API_TOKEN` — were initially missing; later live test reached the deployed separator, so the request path is now reaching Modal.

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
- BTS production builds compiled successfully with Next.js 16.1.6 / Turbopack.
- `/bts` is live.
- BTS token creator/tracker routes are live.
- BTS token admin endpoint requires authentication.
- AI Tab token files remained isolated from BTS token logic.
- Browser processing request reached `/api/bts/process` and then the dedicated Modal separator.
- Latest live log proves Demucs six-stem separation completed and wrote Guitar/Bass/Drums/Vocals/Other/Piano WAVs.

Still to complete:
1. Port the post-separation handoff hardening to `backing-track-studio` only.
2. Validate branch syntax/contracts without changing Production.
3. When explicitly authorized later, deploy/promote the tested branch worker fix.
4. Retry the BTS flow with permitted audio and confirm a playable MP3.
5. Confirm source Blob deletion immediately after success.
6. Verify token decrement/redemption entry in the admin tracker.
7. Separately test the $1 PayPal sandbox path.
8. Confirm hourly cleanup cron behavior/runtime authorization for an abandoned test upload.

## Progress score
**Current Project Progress Score: 98%.**

The implementation is essentially complete. The currently isolated engineering task is the stem-output handoff/rebuild fix plus final end-to-end validation.
