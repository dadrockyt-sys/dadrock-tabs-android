# CURRENT STATE — Backing Track Studio

Updated: 2026-08-29 UTC  
Branch: `backing-track-studio`

## Active phase
**BTS implementation complete in branch; final validation/configuration remains.** `main`/Production remain untouched.

## Working route
- `/bts` -> `dadrocktabs.com/bts`
- Logo: `public/dadrock-tabs-bts-logo.png`

## Frozen product intent
Create a standalone Backing Track Studio using `app/ai-tab/page.js` as the UX blueprint while keeping AI-tab production/payment behavior unchanged.

User flow:
1. Upload MP3/WAV/M4A/AAC audio.
2. Use the same email-format validation semantics as `/ai-tab`.
3. Choose:
   - Remove Guitars
   - Remove Bass
   - Remove Guitars + Bass
4. Pay **USD $1.00** through PayPal **sandbox** during testing.
5. Process with genuine waveform/stem separation through a dedicated Modal worker.
6. Download the resulting MP3 backing track.

## Dependency map — COMPLETE
- `/ai-tab` blueprint inspected.
- Existing AI-tab payment files remain frozen:
  - `components/PayPalCheckoutButton.js`
  - `app/api/paypal/create-order/route.js`
  - `app/api/paypal/capture-order/route.js`
- AI-tab backend remains USD $2.99 and is not modified.
- AI-tab email behavior is format validation, not OTP verification.
- Existing AI-tab analyzer is transcription-oriented and is not used as backing-track generation.

## Waveform/stem research — COMPLETE
The active AI-tab research branch contains genuine waveform separation:
- `analyzer/v143_production_separator.py`
- `analyzer/bass_professional_separator_scaffold.py`
- `audio-separator[gpu]==0.30.2`
- Demucs six-source model `htdemucs_6s.yaml`

BTS reuses this proven substrate in a dedicated worker rather than using note/register filtering.

## Implemented BTS files
- `app/bts/page.js`
  - BTS logo
  - audio upload
  - email validation
  - copyright/permission confirmation
  - Remove Guitars / Remove Bass / Remove Guitars + Bass options
  - upload/status/payment/processing/download UI
- `components/BTSPayPalCheckoutButton.js`
  - dedicated BTS PayPal sandbox checkout
- `lib/btsPayment.js`
  - BTS-only price/product validation
  - USD $1.00
  - product fingerprinting
  - signed paid-job token
- `app/api/bts/audio-upload/route.js`
  - BTS-only private Vercel Blob upload authorization
  - `bts-audio/` namespace
  - 50 MB maximum
- `app/api/bts/paypal/create-order/route.js`
  - sandbox-only PayPal base URL
  - server-fixed USD $1.00
  - BTS-specific order identity
- `app/api/bts/paypal/capture-order/route.js`
  - verifies completed sandbox capture, price, currency, and BTS fingerprint
  - returns signed BTS job token
- `app/api/bts/process/route.js`
  - verifies paid BTS job token
  - resolves private Blob server-side from pathname
  - calls only the dedicated BTS Modal endpoint
  - streams returned MP3 directly to the browser
  - does not persist the generated backing track
  - deletes the uploaded source Blob immediately after processing completes
  - sends `Cache-Control: private, no-store`
- `analyzer/modal_bts_separator.py`
  - dedicated Modal app `dadrock-backing-track-studio`
  - A10G GPU
  - FFmpeg normalization
  - `audio-separator` with `htdemucs_6s.yaml`
  - full six-source waveform separation
  - rebuilds mix excluding Guitar, Bass, or both
  - returns 192 kbps MP3
  - intermediate source/stems/output live only inside a temporary directory
- `analyzer/bts-audio-separation-requirements.txt`
- `app/api/bts/cleanup/route.js`
  - CRON_SECRET-protected BTS-only cleanup
  - scans only `bts-audio/`
  - hourly cleanup threshold is 23 hours so abandoned uploads cannot exceed the 24-hour maximum between hourly runs
- `vercel.json`
  - retains existing daily sync cron
  - adds hourly `/api/bts/cleanup` cron

## Copyright/audio retention rule — FROZEN
User requirement: do not keep copyrighted audio.

**Maximum retention: 24 hours.**

Implementation is intentionally stricter:
- Successful job: source upload is deleted immediately after processing.
- Generated backing track: streamed to the customer and **not persisted** by BTS.
- Modal intermediates: temporary only and removed when the worker request ends.
- Abandoned/failed uploads: hourly cleanup starts deleting `bts-audio/` blobs at 23 hours so the practical maximum remains under 24 hours.
- Response caching is disabled with `private, no-store`.

Do not introduce persistent copyrighted-audio storage without explicit user approval.

## Retention validation
- Vercel documentation confirms cron jobs are configured through the `crons` array in `vercel.json`.
- Vercel documentation confirms cron Route Handlers can be protected using `Authorization: Bearer ${CRON_SECRET}`; BTS cleanup follows that contract.
- Vercel Blob SDK documentation confirms prefix listing/pagination and deletion by URL/pathname are supported.
- Important deployment behavior: Vercel Cron Jobs are production-scheduled. The branch code is ready, but the cleanup cron does not become an active scheduled job until the relevant BTS code/config is deployed to Production. Production must **not** be modified without explicit user direction.
- During development/preview testing, use permitted test audio and ensure test uploads are processed/deleted or manually cleaned if a test is abandoned.

## Isolation / safety rails
- Work only on `backing-track-studio`.
- Do not modify `main` or Production.
- Existing AI-tab $2.99 PayPal behavior remains unchanged.
- Existing AI-tab analyzer endpoints remain unchanged.
- BTS uses dedicated API/payment/Modal environment variables.
- Re-fetch this checkpoint first whenever resuming BTS work.
- Save this checkpoint frequently.

## Required environment/configuration before live testing
- `NEXT_PUBLIC_PAYPAL_CLIENT_ID` — sandbox client ID
- `PAYPAL_CLIENT_SECRET` — sandbox secret
- `BLOB_READ_WRITE_TOKEN`
- `CRON_SECRET`
- `BTS_SEPARATOR_API_URL` — deployed dedicated Modal BTS endpoint
- `BTS_SEPARATOR_API_TOKEN` — matching token in Vercel and Modal secret
- Optional: `BTS_JOB_SIGNING_SECRET`; falls back to PayPal client secret if absent
- Modal secret expected by worker: `dadrock-bts-separator-secret` containing `BTS_SEPARATOR_API_TOKEN`

## Validation status
- GitHub diff confirms BTS work is isolated from `main` and consists of BTS-specific additions plus the branch-only `vercel.json` cron addition.
- No GitHub CI/check run is attached to the latest BTS checkpoint commit.
- Connected Vercel currently shows `main` Production deployments and no BTS preview deployment to inspect.
- Local `git clone`/`next build` could not be run in the execution container because outbound GitHub DNS/network access is blocked.
- No Production deployment or promotion was attempted.

## Progress score
Five-gate rubric, 20 points each:
1. Scope + isolated branch + checkpoint — complete.
2. Blueprint/dependency/research inspection — complete.
3. BTS page + upload/email/removal UI — complete.
4. Dedicated Modal separator + $1 sandbox PayPal + download delivery + retention — implemented.
5. End-to-end validation/build/deployment checks — partially complete; live Modal/PayPal/browser test remains.

**Current Project Progress Score: 85%.**

## NEXT
1. Perform final code-contract review for page -> upload -> payment -> job token -> process route.
2. Deploy the dedicated Modal BTS worker only when BTS secrets are ready; do not deploy the site to Production without explicit user direction.
3. Create/inspect a non-Production BTS preview if the deployment setup permits it.
4. Test `/bts` end-to-end with PayPal sandbox and a permitted audio sample.
5. Verify immediate source Blob deletion after a successful job.
6. Before eventual Production release, verify `CRON_SECRET` exists so the hourly 24-hour cleanup protection becomes active.
7. Re-save this checkpoint after final validation.