# CURRENT STATE — Backing Track Studio

Updated: 2026-08-30 UTC  
Checkpoint branch: `backing-track-studio`  
Production branch: `main`

## Active phase
**Production promotion is complete. The tested BTS live-PayPal/UI/SEO changes were rebased safely onto the then-current `main` through a dedicated release branch and merged via PR #27. Production `/bts` is serving successfully, the production sitemap now contains the English-only `/bts` URL, and a production `/api/bts/cleanup` cron invocation has returned HTTP 200. The remaining launch verification is one real USD $1.00 PayPal checkout/capture (performed by the user, with optional refund) followed by GSC URL Inspection/request indexing.**

## Production promotion — COMPLETE — 2026-08-30 UTC
- Re-fetched this checkpoint before updating it, per standing instruction.
- User explicitly authorized promotion to Production.
- The original direct feature-branch PR **#26** was not merged because `backing-track-studio` had diverged from newer unrelated `main` work and a direct merge risked overwriting that work.
- A clean release branch, `bts-production-release`, was created from then-current `main` SHA `f460e5ee09f2bb0f3945a2a2b83f5252bb1b53f0`.
- Only the intended BTS/GSC production files were brought onto that release branch:
  - `analyzer/modal_bts_separator.py`
  - `app/bts/layout.js`
  - `app/bts/page.js`
  - `app/sitemap.js`
  - `components/BTSPayPalCheckoutButton.js`
  - `lib/btsPayment.js`
  - `validation/bts/validate_bts_contracts.mjs`
- Release commit: `867fa041951aebfb3914e3b758bb71d1e84d9095` — `Promote BTS live PayPal and SEO`.
- Production PR **#27** (`Release Backing Track Studio live PayPal and SEO`) was merged successfully.
- Production merge/current `main` SHA: `bf9051383e5a68a29aa7b71edc0811d23ebb9db7`.
- PR **#26** was then closed unmerged and marked superseded by PR #27.
- Vercel Production deployment observed: `dpl_8XMtBfxJ4EaKiJ7N5F8cQCCR9xeH`.
- Production runtime verification observed `GET /bts` → **HTTP 200** from that `main` deployment.
- Production `https://dadrocktabs.com/sitemap.xml` → **HTTP 200** and visibly contains `<loc>https://dadrocktabs.com/bts</loc>`.
- A production runtime log also observed `GET /api/bts/cleanup` → **HTTP 200**, demonstrating that the production cleanup route/cron authorization path has executed successfully at least once. This does not expose or prove the literal secret value.
- Vercel's available connector does not expose Production secret values. The code now targets PayPal's live endpoint and live credential variable names, but a real USD $1.00 buyer-side transaction is still required before claiming the deployed PayPal credentials/capture path are fully verified live.
- No real-money checkout was initiated by the assistant.

## Live PayPal / GSC readiness continuation — 2026-08-30 UTC
- Re-fetched this checkpoint before making changes, per instruction.
- User confirmed the complete BTS processing flow works and requested removal of the sandbox state before submitting `https://dadrocktabs.com/bts` to Google Search Console.
- BTS remains **USD $1.00 per backing track**.
- `lib/btsPayment.js` now uses PayPal's live API endpoint: `https://api-m.paypal.com`.
- BTS now uses the existing live PayPal credential names already used by DadRock Tabs:
  - `NEXT_PUBLIC_PAYPAL_CLIENT_ID`
  - `PAYPAL_CLIENT_SECRET`
- BTS-specific create/capture routes remain separate, so the existing AI Tab USD $2.99 product and routes are not changed.
- `components/BTSPayPalCheckoutButton.js` now loads the live PayPal client ID only and contains no sandbox customer wording.
- `app/bts/page.js` now shows **Price** instead of **Sandbox test price**, and checkout/status/error copy no longer refers to sandbox.
- BTS contract validation was updated to require the live PayPal endpoint/credentials and to fail if sandbox UI/config markers return.
- `app/sitemap.js` includes `https://dadrocktabs.com/bts` as an **English-only** route; no premature localized `/xx/bts` URLs or hreflang entries were added.
- Relevant branch commits:
  - `db3e3e29942bcb1d8a5908bba2f4ccf2184511db` — `Switch BTS PayPal to live mode`
  - `40dd816819f0269a4d2d6f6532100099522747f1` — `Use live PayPal checkout for BTS`
  - `ae98a54e2cd4ddd99574537e4e47f148042840e6` — `Remove BTS sandbox presentation`
  - `9a87024c5ada72dc3b965b16bb793694f589180d` — `Validate live BTS PayPal configuration`
  - `dd48ea4a50b26dcb8076e56eeae37f3b150e9e18` — `Add BTS to English sitemap`
- Route-specific SEO metadata exists with canonical `https://dadrocktabs.com/bts`, index/follow, search-focused title/description, and social metadata.
- These prepared changes are now promoted to Production through PR #27, and the live page/sitemap have been rechecked.
- Production live PayPal credential values cannot be inspected through the currently available Vercel connector surface; complete verification requires one real USD $1.00 checkout/capture.

## UI / SEO / localization-prep continuation — 2026-08-30 UTC
- User confirmed the live BTS generation flow is working and supplied screenshots showing successful processing/download behavior.
- User reported noticeable guitar bleed in separated audio. This is consistent with source-separation limitations in dense/mastered recordings and is a plausible contributor to some AI Tab transcription difficulty because residual guitar energy can still reach downstream analysis.
- User requested:
  - remove the customer-facing **Isolated BTS workflow** implementation box;
  - remove the top-right **PayPal Sandbox · $1.00 USD** badge;
  - replace that badge with the same DadRock Tabs language selector backed by the site's 14 locales;
  - add a strong natural-language SEO paragraph for searches around backing tracks, guitar removal, bass removal, practice tracks, and AI stem separation;
  - prepare BTS for later translation/localization.
- Existing site locale source confirmed in `lib/i18n.js`: `en`, `es`, `pt`, `pt-br`, `de`, `fr`, `it`, `ja`, `ko`, `zh`, `ru`, `hi`, `sv`, `fi`.
- `app/bts/page.js` update committed as `505847ec073a7231a6d53c968e16cd54195541a9` (`Polish BTS UI for SEO and localization`):
  - uses the existing `components/LanguageSelector.js` in the top-right position;
  - removes the internal workflow explanation box;
  - adds a user-facing note that complex mastered mixes can retain some stem bleed/artifacts;
  - adds a semantic **AI Guitar and Bass Backing Track Maker** section with natural search-intent copy.
- `app/bts/layout.js` added in commit `8a9eb8faa2e0b5284c37b9fc56771cf36f42b2c9` (`Add BTS route SEO metadata`):
  - BTS-specific title and description;
  - `/bts` canonical;
  - relevant backing-track/stem-separation keywords;
  - Open Graph/Twitter metadata;
  - index/follow robots metadata.
- These UI/SEO changes are now in Production via PR #27.
- Locale-prefixed BTS routes are **not enabled yet**. This is intentional so choosing a locale does not create 404/duplicate localized BTS URLs before translations and localized routes are actually implemented.
- Failed temporary workflow was removed in commit `8d881a02e7e341f459363f7e865050d3c8519ff1`.

## Branch-only stem handoff fix — DONE AND PROMOTED
Original commit on `backing-track-studio`:
- `d4fe85a885912a11c54014409f92d82f40668559` — `Harden BTS completed stem handoff on branch`

Changes in `analyzer/modal_bts_separator.py`:
1. Resolve the installed `audio-separator` executable with `shutil.which("audio-separator")` instead of invoking it as `python -m audio_separator`.
2. Run the separator subprocess with `cwd=str(output_dir)` so completed stems remain in the exact directory BTS scans.
3. Treat completed audio files as the source of truth. `audio-separator==0.30.2` may return a non-zero process status after writing all stems, so BTS now fails only when no output audio exists (or an expected named stem cannot be found).
4. Preserve CPU-only behavior and the existing six-source Demucs model.

Live evidence showed all six expected stems were written:
- Bass
- Drums
- Other
- Vocals
- Guitar
- Piano

The hardened worker source was included in the safe Production release through PR #27.

## Frozen AI Tab dependency map + research-separator audit — 2026-08-30 UTC
- Re-fetched this checkpoint first, then re-inspected the active AI Tab research branch before making any separator decision.
- Current `backing-track-studio` head before this audit was `b1794d5354ed2471cde2adc2802dcd2767ae8cbe`.
- Branch comparison at this checkpoint showed `backing-track-studio` was **18 commits ahead and 26 commits behind `main`**. No merge, rebase, sync, or Production action was performed during that audit because the user explicitly required isolation at that stage.

### Frozen `/ai-tab` dependency map
The relevant upload/email/status/delivery chain in `app/ai-tab/page.js` is now explicitly frozen for BTS reference:
1. Audio selection accepts MP3/WAV/M4A/AAC and performs browser-side type/extension checks.
2. Email handling in the AI Tab page is **format validation only** using the same `^[^\s@]+@[^\s@]+\.[^\s@]+$` semantics that BTS now uses; there is no separate email-ownership verification step in this page flow.
3. AI Tab uploads through `@vercel/blob/client` to `/api/audio-upload` with private Blob access and sends song/artist/transcription type/copyright/email metadata in `clientPayload`.
4. Analysis is requested from `/api/analyze-audio-tab`.
5. Watermarked preview delivery is requested from `/api/generate-tab-preview`.
6. Paid unlock is handled by `components/PayPalCheckoutButton.js` and the existing AI Tab PayPal routes; complimentary unlock uses `/api/free-tab-token`.
7. Final PDF creation/delivery is requested from `/api/generate-tab-pdf`; the browser downloads the returned PDF and the AI Tab flow also prepares email delivery.
8. BTS intentionally reuses the **UX pattern and email-format semantics**, not AI Tab payment or delivery APIs. BTS keeps `/api/bts/audio-upload`, `/api/bts/paypal/*`, `/api/bts/free-token`, and `/api/bts/process` separate so the USD $2.99 AI Tab product remains untouched.

### Active research branch inspection
- Active research branch inspected: `v143-contextual-prune-lobo`.
- This branch **does contain genuine waveform/stem-separation research**, including `analyzer/analyze_and_grade_gomyway_gpu_separator_stem_v1.py` and the related separator benchmark grader.
- The research compares a direct six-source Demucs guitar stem with a precomputed **BS-Roformer → Demucs 6-source** guitar stem and grades those waveform stems downstream with identical Basic Pitch settings.
- This is not a reusable production BTS worker: it is a song-specific research benchmark/grader around precomputed stems, and the code explicitly requires `productionSeparatorChanged == false` and `productionPromotionAllowed == false`.
- Therefore **no research-branch separator code was copied into BTS**. The existing dedicated BTS Modal worker remains the smallest production-suitable waveform solution: generic uploaded-audio input, private-Blob validation, six-source Demucs separation, selected stem removal, direct MP3 rebuild, and no persistent generated-audio storage.
- This satisfies the standing requirement to inspect the active AI Tab research branch before choosing/building a BTS separator.
- No change was made to AI Tab or the research branch as part of this BTS release.

## Isolation status
- Feature development and validation remained isolated on `backing-track-studio` until the user explicitly authorized Production promotion.
- Promotion was performed safely through `bts-production-release`, created from the then-current `main`, so newer unrelated Production work was not overwritten.
- PR #27 is merged to `main`; Production was therefore intentionally modified after explicit authorization.
- PR #26 from the divergent feature branch was closed unmerged as superseded.
- Ongoing checkpoint maintenance remains on `backing-track-studio` only; this checkpoint file was not added to the Production release.
- No live Modal redeploy was triggered by the promotion itself.

## Production state
- Live route: `https://dadrocktabs.com/bts`
- Original BTS promotion: PR **#23**
  - merge commit: `b477bab46fde4656c8277167d758dffa7fc5942f`
- Separate BTS token workflow: PR **#24**
  - merge commit: `f14132729d2d60f2ede6e3a5c1f725584ca1db35`
- Current admin-panel BTS-manager link: PR **#25**
  - merge commit: `2ae350ba72e12bacb8b767ab4ffe6c80bce322aa`
- Live PayPal/UI/SEO/stem-handoff release: PR **#27**
  - release commit: `867fa041951aebfb3914e3b758bb71d1e84d9095`
  - merge/current `main` SHA at promotion: `bf9051383e5a68a29aa7b71edc0811d23ebb9db7`
  - Vercel production deployment: `dpl_8XMtBfxJ4EaKiJ7N5F8cQCCR9xeH`

## Product flow
1. Upload MP3/WAV/M4A/AAC audio.
2. Enter email using the same email-format validation semantics as AI Tab.
3. Choose:
   - Remove Guitars
   - Remove Bass
   - Remove Guitars + Bass
4. Unlock with either:
   - **USD $1.00 PayPal live checkout**, or
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

Accepted BTS tokens return a signed BTS job token, so they enter the same protected audio-processing route as a verified PayPal capture.

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

## Stem separation
- Dedicated BTS Modal app: `dadrock-backing-track-studio`
- Demucs six-source model: `htdemucs_6s.yaml`
- Current worker dependency: `audio-separator[cpu]==0.30.2`
- Removes Guitar, Bass, or both and rebuilds the remaining mix.
- Returns a 192 kbps MP3.
- User has confirmed successful playable/downloadable rebuilt tracks.
- Separation is not acoustically perfect: noticeable guitar bleed can remain in dense/mastered recordings, and the customer-facing copy now sets that expectation accurately.

## Payment isolation
- BTS create/capture routes are separate from AI Tab.
- BTS server price remains **USD $1.00**.
- Production code targets **live PayPal** at `https://api-m.paypal.com`.
- BTS uses the existing live PayPal credential variable names but its own BTS order/capture validation and signed job-token path.
- Existing AI Tab **USD $2.99** price, routes, and product logic remain unchanged.
- Because deployed secret values are not inspectable through the available Vercel connector, a real USD $1.00 checkout/capture remains the final proof that Production credentials are actually live and valid.

## Copyright/audio retention rule — FROZEN
**Maximum retention: 24 hours.**

Implementation is stricter:
- Successful source upload is deleted immediately after successful processing.
- Generated backing track is streamed to the customer and is **not persistently stored** by BTS.
- Separator intermediates exist only in temporary worker storage.
- Abandoned/failed BTS uploads are eligible for hourly cleanup beginning at 23 hours.
- Audio responses use no-store caching semantics.

Do not introduce persistent copyrighted-audio storage without explicit user approval.

## Cleanup cron runtime status
Production `vercel.json` contains the hourly `/api/bts/cleanup` cron. A Production runtime log on 2026-08-30 observed `GET /api/bts/cleanup` → **HTTP 200**, so the cleanup route/cron authorization path has executed successfully at least once in Production. The connector still does not expose `CRON_SECRET` itself, so this observation confirms runtime behavior rather than the literal secret value.

## Validation status
Completed / user-confirmed / production-observed:
- `/bts` is live and Production returned **HTTP 200** after PR #27 promotion.
- BTS browser processing reaches the dedicated Modal separator.
- Demucs six-stem separation completes.
- The rebuilt backing track is playable in-browser and downloadable as MP3.
- BTS token creator/tracker routes are live and isolated from AI Tab.
- AI Tab payment/token logic remains isolated from BTS.
- Production UI removes internal workflow implementation copy, exposes the shared 14-language selector, includes SEO-focused content, and contains no customer-facing sandbox labels.
- Production BTS route metadata has a dedicated title, description, canonical, keyword set, social metadata, and index/follow settings.
- Production BTS PayPal helper targets `https://api-m.paypal.com` and uses live credential variable names only.
- Validation explicitly checks live PayPal configuration and rejects sandbox markers.
- Production sitemap returned **HTTP 200** and visibly contains `https://dadrocktabs.com/bts` as the English BTS route.
- Production `/api/bts/cleanup` returned **HTTP 200** in runtime logs.
- AI Tab upload/email/status/delivery dependencies are explicitly frozen in this checkpoint.
- Active AI Tab research branch was re-inspected and found to contain genuine waveform-separation research, but no generic production worker appropriate to copy into BTS.
- Safe release process avoided merging the divergent BTS feature branch directly over newer unrelated `main` work.

Still to complete:
1. Perform one small real **USD $1.00 BTS PayPal transaction** from the customer side to verify the deployed live credentials/capture path, then refund it if desired through PayPal.
2. Use Google Search Console URL Inspection for `https://dadrocktabs.com/bts` and request indexing now that the production page and sitemap entry are confirmed live.
3. When localization work begins, create real localized BTS routes/content before adding `bts` to `LOCALIZED_ROUTE_ROOTS` or publishing hreflang alternates.

## Progress score
**Current Project Progress Score: 99.5%.**

Core BTS functionality is working according to the user's live test, the prepared live-PayPal/UI/SEO changes are promoted safely to Production, the live route and sitemap entry are confirmed, and the cleanup route has executed successfully in Production. The final launch-verification items are a real USD $1.00 PayPal smoke transaction and GSC URL Inspection/request indexing.
