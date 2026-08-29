# CURRENT STATE — Backing Track Studio

Updated: 2026-08-29 UTC  
Checkpoint branch: `backing-track-studio`
Production branch: `main`

## Active phase
**BTS is live at `https://dadrocktabs.com/bts`; a separate BTS token system has now been implemented on the checkpoint branch and is being validated before Production promotion.**

User explicitly authorized moving the completed BTS work to `main`/Production on 2026-08-29, and then requested the AI-tab-style token workflow be added before testing.

## Production promotion
- Pull request: **#23 — Promote Backing Track Studio to main**
- BTS branch head merged: `8c7509be84e4b2d9c70d0af4a8800798e2dc2200`
- Production merge commit: `b477bab46fde4656c8277167d758dffa7fc5942f`
- Vercel production deployment: `dpl_DyBoeXcpAG8oKcQi1qWiP1A5mJso`
- Vercel state: **READY**
- Production build: **successful**
- Live custom-domain verification: `https://dadrocktabs.com/bts` returned **HTTP 200** and rendered the BTS page.

## Working route
- `/bts` -> `dadrocktabs.com/bts`
- Logo: `public/dadrock-tabs-bts-logo.png`

## Frozen product intent
Create a standalone Backing Track Studio using `app/ai-tab/page.js` as the UX blueprint while keeping AI-tab production/payment/token behavior unchanged.

User flow:
1. Upload MP3/WAV/M4A/AAC audio.
2. Use the same email-format validation semantics as `/ai-tab`.
3. Choose:
   - Remove Guitars
   - Remove Bass
   - Remove Guitars + Bass
4. Unlock through either:
   - **USD $1.00** PayPal **sandbox** checkout during testing, or
   - a valid complimentary BTS token.
5. Process with genuine waveform/stem separation through a dedicated Modal worker.
6. Download the resulting MP3 backing track.

## Implemented BTS files
- `app/bts/page.js`
- `components/BTSPayPalCheckoutButton.js`
- `lib/btsPayment.js`
- `app/api/bts/audio-upload/route.js`
- `app/api/bts/paypal/create-order/route.js`
- `app/api/bts/paypal/capture-order/route.js`
- `app/api/bts/process/route.js`
- `app/api/bts/cleanup/route.js`
- `analyzer/modal_bts_separator.py`
- `analyzer/bts-audio-separation-requirements.txt`
- `vercel.json` hourly BTS cleanup cron addition

## BTS token system — IMPLEMENTED ON CHECKPOINT BRANCH
User requested the same token usage behavior as AI Tab, but with a separate BTS creator/tracker.

Isolation design:
- Existing AI Tab collection remains `tab_tokens` and is untouched.
- BTS uses a new collection: `bts_tokens`.
- Existing AI Tab token format remains `DRT-XXXX-XXXX-XXXX`.
- BTS uses a distinct `BTS-XXXX-XXXX-XXXX` format to prevent accidental cross-product redemption.

New files/routes:
- `app/api/admin/bts-tokens/route.js`
  - ADMIN_PASSWORD protected.
  - token types match AI Tab: testing, giveaway, promotion, customer, support.
  - quantity 1–100.
  - uses per token 1–100.
  - optional assigned email.
  - optional expiration.
  - notes.
  - enable/disable/delete.
  - stats for total/active/used/expired/disabled/redemptions.
- `app/api/bts/free-token/route.js`
  - validates BTS token, email assignment, active state, expiration, and uses remaining.
  - atomically decrements one use and records redemption history.
  - returns a signed BTS job authorization so token unlocks use the same `/api/bts/process` path as paid orders.
  - redemption metadata stores email/removal mode/time only; it does not persist uploaded audio/pathnames.
- `app/admin/bts-tokens/page.js`
  - separate BTS token creator and tracker.
  - uses the existing admin password/session convention.
  - displays token status, remaining uses, expiration, notes and redemption history.
- `components/BTSPayPalCheckoutButton.js`
  - now offers **Have a free BTS token?** as an alternative to PayPal after upload.
  - invalid tokens leave PayPal available.
  - accepted tokens invoke the same processing callback with a signed BTS job token.

AI Tab token creator, tracker, redemption route, `tab_tokens` database records and DRT token behavior remain unchanged.

## Waveform/stem separation
BTS uses a dedicated waveform separator based on the proven AI-tab research substrate:
- `audio-separator[gpu]==0.30.2`
- Demucs six-source model `htdemucs_6s.yaml`
- dedicated Modal app `dadrock-backing-track-studio`
- removes Guitar, Bass, or both and rebuilds the remaining mix
- returns 192 kbps MP3

## Payment isolation
- BTS uses dedicated create/capture routes.
- BTS server price is fixed at **USD $1.00**.
- PayPal is **sandbox only** during testing.
- Existing AI-tab payment routes and **USD $2.99** product remain unchanged.
- BTS complimentary tokens do not modify or bypass AI Tab payment/token logic.

## Copyright/audio retention rule — FROZEN
**Maximum retention: 24 hours.**

Implementation is intentionally stricter:
- Successful job: source upload is deleted immediately after processing.
- Generated backing track: streamed to the customer and **not persisted** by BTS.
- Modal intermediates: temporary only and removed when the worker request ends.
- Abandoned/failed uploads: hourly cleanup starts deleting `bts-audio/` blobs at 23 hours so the practical maximum remains under 24 hours.
- Response caching is disabled with `private, no-store`.

Do not introduce persistent copyrighted-audio storage without explicit user approval.

## Production cron status
The BTS cleanup cron is present in Production `vercel.json`.

Important: cleanup execution still depends on Production `CRON_SECRET` being configured. Secret presence has **not** been independently verified from the available connector surface. Do not claim hourly cleanup is functioning until a cron invocation is confirmed or the secret is verified.

## Required runtime configuration for full end-to-end testing
- `NEXT_PUBLIC_PAYPAL_CLIENT_ID` — sandbox client ID
- `PAYPAL_CLIENT_SECRET` — sandbox secret
- `BLOB_READ_WRITE_TOKEN`
- `CRON_SECRET`
- `BTS_SEPARATOR_API_URL` — deployed dedicated Modal BTS endpoint
- `BTS_SEPARATOR_API_TOKEN` — matching token in Vercel and Modal secret
- Optional: `BTS_JOB_SIGNING_SECRET`; falls back to PayPal client secret if absent
- Modal secret expected by worker: `dadrock-bts-separator-secret` containing `BTS_SEPARATOR_API_TOKEN`

Token administration additionally relies on the already-existing `ADMIN_PASSWORD` and MongoDB configuration used by the site.

## Validation status
- Original BTS PR #23 merged successfully into `main`.
- Vercel production build compiled successfully with Next.js 16.1.6 / Turbopack.
- `/bts` and original BTS API routes appeared in the production route manifest.
- Production deployment reached **READY** and `/bts` returned HTTP 200.
- New BTS token additions are currently on `backing-track-studio` pending final branch diff/build validation and promotion.
- Full audio-processing flow has not yet been exercised from the browser.

## Progress score
Five-gate rubric, 20 points each:
1. Scope + isolated branch + checkpoint — complete.
2. Blueprint/dependency/research inspection — complete.
3. BTS page + upload/email/removal UI — complete.
4. Dedicated separator + $1 sandbox PayPal + download delivery + retention + separate token system — implemented.
5. Production deployment/live route — original BTS complete; token addition promotion and end-to-end functional testing remain.

**Current Project Progress Score: 96%.**

## NEXT
1. Validate branch diff for BTS token additions only.
2. Promote the BTS token addition to `main` for the user's pre-test requirement.
3. Verify Vercel build includes `/admin/bts-tokens`, `/api/admin/bts-tokens`, `/api/bts/free-token` and `/bts`.
4. Create a BTS testing token in the separate admin tracker.
5. Test a permitted audio upload and redeem the BTS token.
6. Confirm dedicated Modal separator returns MP3 and source Blob is deleted immediately afterward.
7. Separately test PayPal sandbox $1 checkout.
8. Confirm `CRON_SECRET`/hourly cleanup works for abandoned uploads.
