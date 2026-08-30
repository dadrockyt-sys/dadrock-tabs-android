# CURRENT STATE — Backing Track Studio

Updated: 2026-08-30 UTC  
Checkpoint branch: `backing-track-studio`  
Production branch: `main`

## Active phase
**Backing Track Studio is live in Production and the live PayPal credential issue is resolved. The user confirmed the PayPal checkout now works correctly after dedicated BTS Live credentials were configured and PR #29 was deployed. Production `/api/bts/paypal/create-order` returned HTTP 200 on the new deployment, and the previous `invalid_client` error exists only on the older deployment. BTS is functionally launched.**

## Final live PayPal verification — 2026-08-30 UTC
- Re-fetched this checkpoint before recording the result, per standing instruction.
- User confirmed the real PayPal flow worked correctly after the dedicated BTS Live credentials were deployed.
- Current Production deployment: `dpl_6UoY1Z265WgCT7ezoJFbXqSANYCi`.
- Current Production/main commit: `e318f105bbffd9c611e145648851e38d0c6802d2`.
- Production runtime logs on the new deployment show:
  - `POST /api/bts/audio-upload` → HTTP 200
  - `POST /api/bts/paypal/create-order` → HTTP 200
  - `GET /bts` → HTTP 200
- A focused runtime-error check still shows the historical PayPal `invalid_client` error only on old deployment `dpl_7kn57qtP86vsT4sKYSa9ZwZcXNdV` at 02:47 UTC; no new `invalid_client` error was observed on the current deployment.
- A capture-order log entry was not returned by the available Vercel log query at the time of this save, so the strongest evidence is the user's successful live checkout confirmation plus the server-side create-order HTTP 200 and absence of the prior authentication failure on the new deployment.

## Dedicated BTS PayPal Live configuration — Production
BTS uses its own PayPal Live credentials and does not reuse the AI Tab sandbox-oriented credentials:
- Browser Client ID: `NEXT_PUBLIC_BTS_PAYPAL_CLIENT_ID`
- Server Secret: `BTS_PAYPAL_CLIENT_SECRET`
- PayPal API endpoint: `https://api-m.paypal.com`
- Price: **USD $1.00** per backing track

Do not change these AI Tab variables as part of BTS work:
- `NEXT_PUBLIC_PAYPAL_CLIENT_ID`
- `PAYPAL_CLIENT_SECRET`
- `PAYPAL_MODE`

The AI Tab USD $2.99 payment/token product remains isolated and unchanged.

## Production release history
- Original BTS promotion: PR #23 — merge `b477bab46fde4656c8277167d758dffa7fc5942f`
- BTS token workflow: PR #24 — merge `f14132729d2d60f2ede6e3a5c1f725584ca1db35`
- Admin BTS-manager link: PR #25 — merge `2ae350ba72e12bacb8b767ab4ffe6c80bce322aa`
- Live PayPal/UI/SEO/stem-handoff release: PR #27 — merge `407a8b5fe6f030fc1976be209c26a2d9d3eea7b5`
- Homepage BTS launch callout: PR #28 — main `323832497eb72d15a0e47aea486c0f633b3d8f43`
- Dedicated BTS Live PayPal credentials: PR #29 — main `e318f105bbffd9c611e145648851e38d0c6802d2`

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

## SEO / launch state
- Live route: `https://dadrocktabs.com/bts`
- Canonical: `https://dadrocktabs.com/bts`
- English `/bts` is included in the sitemap.
- Route metadata is index/follow with BTS-specific title, description, keywords, Open Graph and Twitter metadata.
- Homepage includes the prominent Backing Track Studio launch callout.
- Locale-prefixed BTS routes are intentionally not enabled until real translations/routes are implemented.

## Next follow-on phase — localization and translations
**This is the saved next development phase. Do not begin until the user is ready to resume work.**

Goal: localize Backing Track Studio from English into the other 13 DadRock Tabs languages while preserving the completed English Production flow.

Target locales:
- Spanish — `es`
- Portuguese — `pt`
- Brazilian Portuguese — `pt-br`
- German — `de`
- French — `fr`
- Italian — `it`
- Japanese — `ja`
- Korean — `ko`
- Chinese — `zh`
- Russian — `ru`
- Hindi — `hi`
- Swedish — `sv`
- Finnish — `fi`

When localization work begins:
1. Re-fetch this checkpoint first.
2. Continue on `backing-track-studio`; do not modify `main` or Production until explicitly approved.
3. Reuse DadRock Tabs' existing 14-language routing/i18n conventions rather than inventing a separate BTS localization system.
4. Translate the full BTS customer experience, including headings, upload instructions, removal-mode labels/descriptions, email/rights text, checkout/token UI, processing/download states, error messages, retention/copyright copy, and SEO paragraph.
5. Add locale-specific BTS metadata/SEO copy where appropriate.
6. Decide and implement the correct localized route structure consistent with the rest of dadrocktabs.com.
7. Preserve the BTS payment price, PayPal Live credential isolation, token isolation, processing APIs, retention rules, and English behavior unchanged unless separately approved.
8. Validate all 13 localized versions on mobile as well as desktop before any Production promotion.
9. Only after translations/routes are proven should locale BTS URLs be considered for sitemap/indexing changes.

## Immediate next steps
1. Submit/request indexing for `https://dadrocktabs.com/bts` in Google Search Console if not already done.
2. Monitor real-world BTS usage, PayPal errors, separator failures and user feedback.
3. When the user is ready to resume development, begin the saved **13-language BTS localization and translation phase** above.

## Progress score
**Completed English BTS launch scope: 100%.**  
**Next follow-on phase: 13-language localization — not started.**

The planned English BTS launch scope is complete: upload, email/rights flow, three removal modes, Modal separation, downloadable MP3, isolated BTS tokens, live USD $1.00 PayPal, cleanup/retention controls, SEO, sitemap entry, homepage promotion and Production deployment are all in place. The user has confirmed the PayPal flow now works correctly. The next project phase is localization into the other 13 DadRock Tabs languages when the user is ready to continue.