# CURRENT STATE — Backing Track Studio

Updated: 2026-08-29 UTC  
Branch: `backing-track-studio`

## Active phase
**BTS implementation complete in branch; validation/configuration remains.** `main`/Production remain untouched.

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
  - resolves the private Blob server-side from pathname
  - calls only the dedicated BTS Modal endpoint
  - streams returned MP3 directly to the browser
  - does not persist the generated backing track
  - deletes the uploaded source Blob immediately after processing completes
- `analyzer/modal_bts_separator.py`
  - dedicated Modal app `dadrock-backing-track-studio`
  - A10G GPU
  - FFmpeg normalization
  - `audio-separator` with `htdemucs_6s.yaml`
  - full six-source waveform separation
  - rebuilds mix excluding Guitar, Bass, or both
  - returns 192 kbps MP3
- `analyzer/bts-audio-separation-requirements.txt`
- `app/api/bts/cleanup/route.js`
  - cron-authenticated BTS-only cleanup
  - scans only `bts-audio/`
  - deletes any upload at or beyond 24 hours old
- `vercel.json`
  - retains existing daily sync cron
  - adds hourly `/api/bts/cleanup` cron

## Copyright/audio retention rule — FROZEN
User requirement: do not keep copyrighted audio.

**Maximum retention: 24 hours.**

Implementation is intentionally stricter:
- Successful job: source upload is deleted immediately after processing.
- Generated backing track: streamed to the customer and **not persisted** by BTS.
- Modal intermediate source/stems/output live only in a temporary directory and disappear when the request ends.
- Abandoned or failed uploads: hourly BTS cleanup removes any `bts-audio/` Blob that reaches 24 hours.
- Response uses `Cache-Control: private, no-store`.

This 24-hour maximum applies to BTS audio storage; do not introduce persistent copyrighted-audio storage without explicit user approval.

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

## Progress score
Five-gate rubric, 20 points each:
1. Scope + isolated branch + checkpoint — complete.
2. Blueprint/dependency/research inspection — complete.
3. BTS page + upload/email/removal UI — complete.
4. Dedicated Modal separator + $1 sandbox PayPal + download delivery + retention — implemented.
5. End-to-end validation/build/deployment checks — pending.

**Current Project Progress Score: 80%.**

## NEXT
1. Run local/static/build validation on `backing-track-studio`.
2. Fix any build/runtime issues found without changing AI-tab files.
3. Validate BTS payment fingerprint/job-token contracts.
4. Validate cleanup route and cron configuration.
5. Deploy the dedicated Modal BTS worker only when environment/secrets are ready; do not deploy Production site unless explicitly requested.
6. Test `/bts` end-to-end with sandbox payment and a permitted audio sample.
7. Re-save this checkpoint after validation.