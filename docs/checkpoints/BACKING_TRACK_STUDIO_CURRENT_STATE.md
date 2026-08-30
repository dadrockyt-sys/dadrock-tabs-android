# CURRENT STATE — Backing Track Studio

Updated: 2026-08-30 UTC  
Checkpoint branch: `backing-track-studio`  
Production branch: `main`

## Active phase
**BTS core functionality is live and working, but the first real USD $1.00 PayPal smoke test exposed a live-credential mismatch. Production currently sends the shared AI Tab PayPal credentials to PayPal's live API, and PayPal returns `invalid_client`. A branch-only fix is now prepared on `backing-track-studio` that gives BTS its own live PayPal client ID/secret so AI Tab sandbox behavior remains unchanged. No Production/main change has been made for this fix.**

## Latest continuation — live PayPal `invalid_client` diagnosis — 2026-08-30 UTC
- Re-fetched this checkpoint before making changes, per standing instruction.
- User supplied a Production screenshot showing the BTS PayPal buttons rendering, followed by **Unable to authenticate with PayPal.**
- Production Vercel runtime errors for `/api/bts/paypal/create-order` were inspected.
- Exact PayPal response observed in Production:
  - `error: 'invalid_client'`
  - `error_description: 'Client Authentication failed'`
- The failing Production deployment was `dpl_7kn57qtP86vsT4sKYSa9ZwZcXNdV`.
- Root cause confirmed in repository code:
  - BTS was changed to PayPal live endpoint `https://api-m.paypal.com`.
  - BTS was still reading the shared AI Tab variables:
    - `NEXT_PUBLIC_PAYPAL_CLIENT_ID`
    - `PAYPAL_CLIENT_SECRET`
  - AI Tab's existing PayPal route still defaults to sandbox unless `PAYPAL_MODE === 'live'`.
  - AI Tab customer UI still explicitly presents sandbox behavior.
  - Therefore the shared credentials are the AI Tab sandbox credential set, and pairing those credentials with PayPal's live API causes `invalid_client`.

## Branch-only fix prepared
Commits on `backing-track-studio`:
- `2477123a1f855592a530d05bed45260591656a04` — `Isolate BTS live PayPal credentials`
- `78200c728369edb1538f1d3b04ac097551ad745b` — `Use dedicated BTS PayPal client ID`
- `34aa081116c82e8d21424e5e48002eed610d5d1f` — `Validate isolated BTS live PayPal credentials`

Changes:
1. `lib/btsPayment.js`
   - BTS remains fixed to `https://api-m.paypal.com`.
   - BTS now reads only dedicated live payment credentials:
     - `NEXT_PUBLIC_BTS_PAYPAL_CLIENT_ID`
     - `BTS_PAYPAL_CLIENT_SECRET`
   - Missing dedicated live credentials produce a clear BTS-specific configuration error.
   - Job signing now prefers `BTS_JOB_SIGNING_SECRET`, then `BTS_PAYPAL_CLIENT_SECRET`, while retaining the old shared secret only as a compatibility fallback so existing BTS token/job behavior is not broken before a dedicated signing secret is confirmed.
2. `components/BTSPayPalCheckoutButton.js`
   - Browser PayPal SDK now uses `NEXT_PUBLIC_BTS_PAYPAL_CLIENT_ID`.
   - SDK script ID is BTS-specific (`dadrock-bts-paypal-sdk`).
   - Existing BTS token alternative remains available if PayPal is not configured.
3. `validation/bts/validate_bts_contracts.mjs`
   - Validation now requires the dedicated BTS live PayPal variables.
   - Validation rejects accidental reuse of `NEXT_PUBLIC_PAYPAL_CLIENT_ID` in BTS live checkout.
   - Existing checks still require USD $1.00, live endpoint, BTS-only routes, token isolation, cleanup, and six-source separation.

## Required Vercel configuration before Production promotion
Add the real PayPal **Live** app credentials to Vercel using these new BTS-only names:
- `NEXT_PUBLIC_BTS_PAYPAL_CLIENT_ID` = PayPal Live Client ID
- `BTS_PAYPAL_CLIENT_SECRET` = PayPal Live Secret

Recommended if not already present:
- `BTS_JOB_SIGNING_SECRET` = a separate strong random signing secret

Important:
- Do **not** replace `NEXT_PUBLIC_PAYPAL_CLIENT_ID` or `PAYPAL_CLIENT_SECRET` just to fix BTS.
- Do **not** set `PAYPAL_MODE=live` as a BTS workaround.
- Those shared values belong to the existing AI Tab PayPal flow, which is still sandbox-oriented in the inspected code. Changing them could unintentionally alter the AI Tab USD $2.99 product.
- The Vercel connector available in this workspace can inspect runtime/build/deployment state but does not expose an environment-variable write action, so the new live credential values must be added in Vercel outside this connector before the BTS live smoke test can succeed.

## Production status before this fix
- Live route: `https://dadrocktabs.com/bts`
- BTS processing/token flow: working and user-confirmed.
- BTS cleanup cron: Production `/api/bts/cleanup` has returned HTTP 200.
- BTS sitemap entry: live English `/bts` is present.
- BTS SEO/UI release: live through PR #27.
- Homepage BTS launch callout: live through PR #28.
- PayPal buttons render in Production, but server-side order creation currently fails at OAuth authentication because the deployed credential pair is not valid for PayPal live.

## Production history
- Original BTS promotion: PR #23
  - merge commit `b477bab46fde4656c8277167d758dffa7fc5942f`
- BTS token workflow: PR #24
  - merge commit `f14132729d2d60f2ede6e3a5c1f725584ca1db35`
- Admin BTS-manager link: PR #25
  - merge commit `2ae350ba72e12bacb8b767ab4ffe6c80bce322aa`
- Live PayPal/UI/SEO/stem-handoff release: PR #27
  - release commit `867fa041951aebfb3914e3b758bb71d1e84d9095`
  - merge commit `407a8b5fe6f030fc1976be209c26a2d9d3eea7b5`
- Homepage BTS launch callout: PR #28
  - main commit `323832497eb72d15a0e47aea486c0f633b3d8f43`
  - Production deployment `dpl_7kn57qtP86vsT4sKYSa9ZwZcXNdV`

## Product flow — frozen
1. Upload MP3/WAV/M4A/AAC audio.
2. Enter email using AI Tab-equivalent format validation semantics.
3. Choose:
   - Remove Guitars
   - Remove Bass
   - Remove Guitars + Bass
4. Unlock with either:
   - USD $1.00 BTS PayPal checkout, or
   - complimentary BTS token.
5. Both unlock methods issue a signed BTS job authorization.
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

## Isolation rules — still active
- Continue working on `backing-track-studio` unless the user explicitly authorizes a clean Production release.
- Do not merge/sync the divergent feature branch directly over `main`.
- For any future Production fix, use a clean release branch created from current `main` and copy only the intended BTS changes.
- Do not modify the AI Tab USD $2.99 payment/token product while fixing BTS.
- Do not modify Production/main without explicit user approval.

## Next steps
1. Add the two BTS-only PayPal **Live** credentials in Vercel:
   - `NEXT_PUBLIC_BTS_PAYPAL_CLIENT_ID`
   - `BTS_PAYPAL_CLIENT_SECRET`
2. Build/test the branch or a clean preview with those credentials.
3. Confirm `/api/bts/paypal/create-order` no longer returns `invalid_client`.
4. After explicit user approval, promote only the three intended BTS PayPal-isolation files to a clean release branch from current `main`.
5. Run one real USD $1.00 transaction and verify capture + BTS processing.
6. Request GSC indexing for `https://dadrocktabs.com/bts` after the payment smoke test is green.

## Progress score
**Current Project Progress Score: 99%.**

Core BTS generation, token unlock, SEO, sitemap, cleanup, UI, and homepage launch are live. The remaining launch blocker is now precisely identified: dedicated PayPal Live credentials must be configured for the new BTS-only variable names and then the branch fix can be safely promoted and smoke-tested.
