# CURRENT STATE — Backing Track Studio

Updated: 2026-08-29 UTC  
Checkpoint branch: `backing-track-studio`
Production branch: `main`

## Active phase
**BTS has been promoted to `main` and is live at `https://dadrocktabs.com/bts` for user testing.**

User explicitly authorized moving the completed BTS work to `main`/Production on 2026-08-29.

## Production promotion
- Pull request: **#23 — Promote Backing Track Studio to main**
- BTS branch head merged: `8c7509be84e4b2d9c70d0af4a8800798e2dc2200`
- Production merge commit: `b477bab46fde4656c8277167d758dffa7fc5942f`
- Vercel production deployment: `dpl_DyBoeXcpAG8oKcQi1qWiP1A5mJso`
- Vercel state: **READY**
- Production build: **successful**
- Build route manifest explicitly includes:
  - `/bts`
  - `/api/bts/audio-upload`
  - `/api/bts/cleanup`
  - `/api/bts/paypal/create-order`
  - `/api/bts/paypal/capture-order`
  - `/api/bts/process`
- Live custom-domain verification: `https://dadrocktabs.com/bts` returned **HTTP 200** and rendered the BTS page.

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
The BTS cleanup cron is now present in the Production `vercel.json` because the BTS work was explicitly promoted to `main`.

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

The production build does not prove these runtime secrets/endpoints are configured. UI/live-route testing can begin now; full upload -> PayPal -> separation -> download testing must verify runtime configuration through actual use.

## Validation status
- Branch comparison before merge: BTS branch was 28 commits ahead of `main`, 0 behind, with 12 changed files limited to BTS additions plus the BTS `vercel.json` cron entry.
- PR #23 merged successfully into `main`.
- Vercel production build compiled successfully with Next.js 16.1.6 / Turbopack.
- `/bts` and all BTS API routes appeared in the production route manifest.
- Production deployment reached **READY**.
- `https://dadrocktabs.com/bts` returned HTTP 200 and rendered the BTS interface.
- Full paid audio-processing flow has not yet been exercised from the browser.

## Progress score
Five-gate rubric, 20 points each:
1. Scope + isolated branch + checkpoint — complete.
2. Blueprint/dependency/research inspection — complete.
3. BTS page + upload/email/removal UI — complete.
4. Dedicated separator + $1 sandbox PayPal + download delivery + retention — implemented.
5. Production deployment/live route — complete; end-to-end functional testing remains.

**Current Project Progress Score: 95%.**

## NEXT
1. User tests `https://dadrocktabs.com/bts` on Production.
2. Test a permitted audio upload and confirm private Blob authorization succeeds.
3. Complete a PayPal sandbox $1 checkout.
4. Confirm dedicated Modal separator receives the paid job and returns MP3.
5. Confirm generated track downloads and source Blob is deleted immediately afterward.
6. Confirm `CRON_SECRET`/hourly cleanup works for abandoned uploads.
7. Fix any issues found during live testing in the BTS workflow without changing AI-tab behavior.
