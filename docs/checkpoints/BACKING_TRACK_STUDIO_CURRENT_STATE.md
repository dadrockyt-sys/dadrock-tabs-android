# CURRENT STATE — Backing Track Studio

Updated: 2026-08-30 UTC  
Checkpoint branch: `backing-track-studio`  
Production branch: `main`

## Active phase
**The user has confirmed the live BTS processing flow works end-to-end, including playable/downloadable backing-track generation. BTS is now prepared on `backing-track-studio` to leave PayPal sandbox and use live PayPal at the existing USD $1.00 price. The customer-facing sandbox wording is removed and `/bts` is prepared as an English-only sitemap entry for GSC. No `main` or Production write was made because the standing instruction remains to keep changes isolated until explicit promotion authorization.**

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
- `app/sitemap.js` now includes `https://dadrocktabs.com/bts` as an **English-only** route; no premature localized `/xx/bts` URLs or hreflang entries were added.
- Relevant branch commits:
  - `db3e3e29942bcb1d8a5908bba2f4ccf2184511db` — `Switch BTS PayPal to live mode`
  - `40dd816819f0269a4d2d6f6532100099522747f1` — `Use live PayPal checkout for BTS`
  - `ae98a54e2cd4ddd99574537e4e47f148042840e6` — `Remove BTS sandbox presentation`
  - `9a87024c5ada72dc3b965b16bb793694f589180d` — `Validate live BTS PayPal configuration`
  - `dd48ea4a50b26dcb8076e56eeae37f3b150e9e18` — `Add BTS to English sitemap`
- Route-specific SEO metadata already exists on the branch with canonical `https://dadrocktabs.com/bts`, index/follow, search-focused title/description, and social metadata.
- Manual GSC URL inspection/request indexing can be used once these branch changes are promoted and the live page is rechecked.
- Production live PayPal credential values cannot be inspected through the currently available Vercel connector surface. Before/at promotion, confirm the existing `NEXT_PUBLIC_PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` are the live PayPal app credentials rather than sandbox credentials.

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
- `app/bts/page.js` branch-only update committed as `505847ec073a7231a6d53c968e16cd54195541a9` (`Polish BTS UI for SEO and localization`):
  - uses the existing `components/LanguageSelector.js` in the top-right position;
  - removes the internal workflow explanation box;
  - adds a user-facing note that complex mastered mixes can retain some stem bleed/artifacts;
  - adds a semantic **AI Guitar and Bass Backing Track Maker** section with natural search-intent copy.
- `app/bts/layout.js` added branch-only in commit `8a9eb8faa2e0b5284c37b9fc56771cf36f42b2c9` (`Add BTS route SEO metadata`):
  - BTS-specific title and description;
  - `/bts` canonical;
  - relevant backing-track/stem-separation keywords;
  - Open Graph/Twitter metadata;
  - index/follow robots metadata.
- Locale-prefixed BTS routes are **not enabled yet**. This is intentional so choosing a locale does not create 404/duplicate localized BTS URLs before translations and localized routes are actually implemented.
- Failed temporary workflow was removed in commit `8d881a02e7e341f459363f7e865050d3c8519ff1`.

## Branch-only stem handoff fix — DONE
Commit on `backing-track-studio`:
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

## Frozen AI Tab dependency map + research-separator audit — 2026-08-30 UTC
- Re-fetched this checkpoint first, then re-inspected the active AI Tab research branch before making any separator decision.
- Current `backing-track-studio` head before this audit was `b1794d5354ed2471cde2adc2802dcd2767ae8cbe`.
- Branch comparison at this checkpoint showed `backing-track-studio` is **18 commits ahead and 26 commits behind `main`**. No merge, rebase, sync, or Production action was performed because the user explicitly requires isolation.

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
- No change was made to AI Tab, `main`, Production, or the research branch.

## Isolation status
- All writes in this continuation were made to `backing-track-studio`.
- `main` was not modified.
- No Production deployment was triggered by the live-PayPal/UI/SEO changes.
- No live Modal redeploy was triggered by these changes.

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
   - **USD $1.00 PayPal live checkout** once the branch is promoted, or
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
- Branch target mode is now **live PayPal**.
- BTS uses the existing live PayPal credential pair but its own BTS order/capture validation and signed job-token path.
- Existing AI Tab **USD $2.99** price, routes, and product logic remain unchanged.

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

## Validation status
Completed / user-confirmed:
- `/bts` is live.
- BTS browser processing reaches the dedicated Modal separator.
- Demucs six-stem separation completes.
- The rebuilt backing track is playable in-browser and downloadable as MP3.
- BTS token creator/tracker routes are live and isolated from AI Tab.
- AI Tab payment/token logic remains isolated from BTS.
- Branch UI removes internal workflow implementation copy, exposes the shared 14-language selector, includes SEO-focused content, and contains no customer-facing sandbox labels.
- Branch BTS route metadata has a dedicated title, description, canonical, keyword set, social metadata, and index/follow settings.
- Branch BTS PayPal helper targets `https://api-m.paypal.com` and uses live credential names only.
- Branch validation now explicitly checks live PayPal configuration and rejects sandbox markers.
- Branch sitemap includes `/bts` exactly once as an English-only route.
- AI Tab upload/email/status/delivery dependencies are now explicitly frozen in this checkpoint.
- Active AI Tab research branch was re-inspected and found to contain genuine waveform-separation research, but no generic production worker appropriate to copy into BTS.

Still to complete:
1. **Promote the prepared branch changes to `main`/Production only when explicitly authorized.**
2. After promotion, perform one small real USD $1.00 BTS PayPal transaction to verify live credentials/capture, then refund it if desired through PayPal.
3. After the live page is confirmed, use GSC URL Inspection for `https://dadrocktabs.com/bts` and request indexing.
4. When localization work begins, create real localized BTS routes/content before adding `bts` to `LOCALIZED_ROUTE_ROOTS` or publishing hreflang alternates.
5. Independently confirm hourly cleanup cron runtime authorization if full operational closure is desired.

## Progress score
**Current Project Progress Score: 99%.**

Core BTS functionality is working according to the user's live test. The branch is now prepared for live USD $1 PayPal and GSC-facing SEO; the remaining gate is explicit Production promotion plus a live-payment smoke test.
