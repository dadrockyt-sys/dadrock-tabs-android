# CURRENT STATE — Backing Track Studio

Updated: 2026-08-30 UTC  
Checkpoint branch: `backing-track-studio`  
Production branch: `main`

## Active phase
**The BTS live-PayPal credential isolation fix is now fully deployed to Production through PR #29. Vercel deployment `dpl_6UoY1Z265WgCT7ezoJFbXqSANYCi` reached READY, owns the `dadrocktabs.com` alias, and Production `/bts` returned HTTP 200 from that deployment. The remaining launch proof is one real USD $1.00 PayPal checkout/capture by the user, followed by runtime-log confirmation and GSC indexing.**

## Latest continuation — dedicated BTS PayPal Live credentials promoted and deployed — 2026-08-30 UTC
- Re-fetched this checkpoint before this final verification/save, per standing instruction.
- The user's first real USD $1.00 BTS PayPal smoke test had returned **Unable to authenticate with PayPal**.
- Production runtime logs identified the exact PayPal response:
  - `error: 'invalid_client'`
  - `error_description: 'Client Authentication failed'`
- Root cause: BTS was targeting PayPal Live (`https://api-m.paypal.com`) while still using the shared AI Tab PayPal credential names. The inspected AI Tab checkout remains sandbox-oriented, so those credentials could not authenticate against PayPal Live.
- Branch-only BTS isolation was prepared on `backing-track-studio` using:
  - `NEXT_PUBLIC_BTS_PAYPAL_CLIENT_ID`
  - `BTS_PAYPAL_CLIENT_SECRET`
- User confirmed both dedicated variables were added in Vercel for **Production** using real PayPal Live app credentials.
- Vercel automatically redeployed the previous main commit after the environment-variable save (`dpl_CaTYvV12po3GbzQU45fXiZuieV6c`), proving the Production environment change was registered, but that redeploy still contained the old shared-credential code.

## Clean Production release — PR #29
- Clean release branch: `bts-live-paypal-credentials`.
- Main before the release: `323832497eb72d15a0e47aea486c0f633b3d8f43`.
- Release branch was confirmed **ahead 5 / behind 0** relative to main.
- PR #29: **Fix BTS live PayPal credential isolation**.
- Complete changed-file set was inspected before merge and contained exactly:
  1. `app/api/bts/paypal/create-order/route.js`
  2. `app/api/bts/paypal/capture-order/route.js`
  3. `components/BTSPayPalCheckoutButton.js`
  4. `lib/btsPayment.js`
  5. `validation/bts/validate_bts_contracts.mjs`
- Route changes only replace obsolete `sandbox: true` response metadata with `environment: 'live'`.
- Functional payment changes are limited to BTS-specific credential isolation.
- PR #29 was mergeable and squash-merged successfully.
- Production/main commit: `e318f105bbffd9c611e145648851e38d0c6802d2`.
- Production deployment: `dpl_6UoY1Z265WgCT7ezoJFbXqSANYCi`.
- Deployment reached **READY** successfully with Next.js/Turbopack.
- Vercel reports aliases including:
  - `dadrocktabs.com`
  - `www.dadrocktabs.com`
- Live fetch of `https://dadrocktabs.com/bts` returned **HTTP 200** and its generated assets explicitly reference `dpl_6UoY1Z265WgCT7ezoJFbXqSANYCi`, confirming the new Production deployment is serving the BTS page.

## BTS PayPal credential contract — now Production code
### Browser
`components/BTSPayPalCheckoutButton.js` uses only:
- `NEXT_PUBLIC_BTS_PAYPAL_CLIENT_ID`

It no longer reuses `NEXT_PUBLIC_PAYPAL_CLIENT_ID`.

### Server
`lib/btsPayment.js` uses the dedicated BTS Live pair for PayPal OAuth:
- `NEXT_PUBLIC_BTS_PAYPAL_CLIENT_ID`
- `BTS_PAYPAL_CLIENT_SECRET`

BTS remains fixed to:
- PayPal API: `https://api-m.paypal.com`
- Price: **USD $1.00**

### Job signing
BTS job signing prefers:
1. `BTS_JOB_SIGNING_SECRET`
2. `BTS_PAYPAL_CLIENT_SECRET`
3. legacy shared `PAYPAL_CLIENT_SECRET` only as a compatibility fallback

The compatibility fallback is not used for PayPal OAuth and therefore does not undo payment isolation.

## AI Tab isolation — frozen
Do not change these values merely to support BTS:
- `NEXT_PUBLIC_PAYPAL_CLIENT_ID`
- `PAYPAL_CLIENT_SECRET`
- `PAYPAL_MODE`

The existing AI Tab USD $2.99 checkout/token product remains unchanged by PR #29.

## Product flow — frozen
1. Upload MP3/WAV/M4A/AAC audio.
2. Enter email using AI Tab-equivalent format validation semantics.
3. Choose Remove Guitars, Remove Bass, or Remove Guitars + Bass.
4. Unlock with either USD $1.00 PayPal or a complimentary BTS token.
5. Both methods issue a signed BTS job authorization.
6. `/api/bts/process` calls the dedicated Modal separator.
7. Six-source Demucs rebuilds the track without the selected stem(s).
8. Result is streamed as a 192 kbps MP3 for download.

## Core BTS implementation
- `app/bts/page.js`
- `app/bts/layout.js`
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
- `validation/bts/validate_bts_contracts.mjs`

## Stem separation — frozen
- Dedicated Modal app: `dadrock-backing-track-studio`
- Model: `htdemucs_6s.yaml`
- Dependency: `audio-separator[cpu]==0.30.2`
- Removes Guitar, Bass, or both.
- Returns 192 kbps MP3.
- Successful playable/downloadable tracks are user-confirmed.
- Some guitar bleed can remain in dense/mastered recordings; customer-facing copy already sets that expectation.

## Copyright/audio retention — frozen
**Maximum retention: 24 hours.**
- Successful source upload is deleted immediately after successful processing.
- Generated backing track is streamed and is not persistently stored by BTS.
- Separator intermediates stay in temporary worker storage only.
- Failed/abandoned BTS uploads become cleanup-eligible at 23 hours.
- Audio responses use no-store semantics.

Do not introduce persistent copyrighted-audio storage without explicit user approval.

## Production history
- Original BTS promotion: PR #23 — merge `b477bab46fde4656c8277167d758dffa7fc5942f`
- BTS token workflow: PR #24 — merge `f14132729d2d60f2ede6e3a5c1f725584ca1db35`
- Admin BTS-manager link: PR #25 — merge `2ae350ba72e12bacb8b767ab4ffe6c80bce322aa`
- Live PayPal/UI/SEO/stem-handoff release: PR #27 — merge `407a8b5fe6f030fc1976be209c26a2d9d3eea7b5`
- Homepage BTS launch callout: PR #28 — main `323832497eb72d15a0e47aea486c0f633b3d8f43`
- Dedicated BTS Live PayPal credentials: PR #29 — main `e318f105bbffd9c611e145648851e38d0c6802d2`

## Next steps
1. User performs one real USD $1.00 BTS checkout on `https://dadrocktabs.com/bts`.
2. Inspect Production runtime logs for `/api/bts/paypal/create-order` and `/api/bts/paypal/capture-order` to confirm Live OAuth/order/capture success and absence of `invalid_client`.
3. Confirm paid authorization proceeds into the already-proven BTS processing/download path.
4. Request Google Search Console indexing for `https://dadrocktabs.com/bts` once the real-money smoke test is green.

## Progress score
**Current Project Progress Score: 99.9%.**

The dedicated PayPal Live credential fix is in Production code, the correct BTS-only Live credentials are configured in Vercel, the new deployment is READY, and `/bts` is serving successfully from that deployment. The sole remaining functional launch proof is one real USD $1.00 PayPal checkout/capture.