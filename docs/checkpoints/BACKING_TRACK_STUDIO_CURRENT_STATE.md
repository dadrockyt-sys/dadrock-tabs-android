# CURRENT STATE — Backing Track Studio

Updated: 2026-08-30 UTC  
Checkpoint branch: `backing-track-studio`  
Production branch: `main`

## Active phase
**The user now reports the live BTS flow is working successfully end-to-end, including playable/downloadable backing-track generation. A branch-only UI/SEO/localization-prep pass is underway on `backing-track-studio`: internal implementation copy is removed, the top sandbox badge is replaced with the existing 14-language selector, and BTS-specific search copy/metadata are added. No `main` or Production write was made in this continuation.**

## UI / SEO / localization-prep continuation — 2026-08-30 UTC
- Re-fetched this checkpoint before making changes, per instruction.
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
- Locale-prefixed BTS routes are **not enabled yet**. This is intentional so choosing a locale does not create 404/duplicate localized BTS URLs before translations and localized routes are actually implemented. The shared selector is now visually present and ready for the next localization phase.
- A temporary one-time Actions patch workflow was attempted but GitHub recorded a startup failure with zero jobs on this branch. It made no BTS code change; direct branch file updates were used instead. Remove the temporary workflow file before finishing this continuation.

## Continuation note — 2026-08-29 22:18–22:21 UTC
- Re-fetched this checkpoint first, per instruction.
- Confirmed `backing-track-studio` initially remained at `23f5fda9436281b2357ac73a9ce147aaad6146e5` (`Record first BTS live processing blocker`), so it did not contain the later live-test worker hardening.
- User screenshot from approximately 22:07 UTC shows `audio-separator` logged **Separation complete!** and wrote all six expected files:
  - `normalized_(Bass)_htdemucs_6s.wav`
  - `normalized_(Drums)_htdemucs_6s.wav`
  - `normalized_(Other)_htdemucs_6s.wav`
  - `normalized_(Vocals)_htdemucs_6s.wav`
  - `normalized_(Guitar)_htdemucs_6s.wav`
  - `normalized_(Piano)_htdemucs_6s.wav`
- Therefore the model itself is working. The observed failure was after successful stem generation, before/during stem discovery/rebuild.
- Read-only comparison against `main` identified the minimal hardening used during the live debug cycle.

## Branch-only stem handoff fix — DONE
Commit on `backing-track-studio`:
- `d4fe85a885912a11c54014409f92d82f40668559` — `Harden BTS completed stem handoff on branch`

Changes in `analyzer/modal_bts_separator.py`:
1. Resolve the installed `audio-separator` executable with `shutil.which("audio-separator")` instead of invoking it as `python -m audio_separator`.
2. Run the separator subprocess with `cwd=str(output_dir)` so completed stems remain in the exact directory BTS scans.
3. Treat completed audio files as the source of truth. `audio-separator==0.30.2` may return a non-zero process status after writing all stems, so BTS now fails only when no output audio exists (or an expected named stem cannot be found).
4. Preserve CPU-only behavior and the existing six-source Demucs model.

Local static validation performed against the exact committed worker text:
- Python `py_compile`: **PASS**.
- AST parse: **PASS**.
- Required hardening markers (`shutil.which`, output-directory `cwd`, file-source-of-truth handling): **PASS**.
- Six expected stem names: **PASS**.
- CPU-only contract: **PASS**.
- Simulated discovery using the exact six filenames visible in the user's screenshot mapped all six stems successfully: **PASS**.

## Isolation status
- All writes in this continuation were made to `backing-track-studio`.
- `main` was not modified.
- No Production deployment was triggered by these UI/SEO changes.
- No live Modal redeploy was triggered by these UI/SEO changes.

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
- Live evidence confirms the model produced all six stems and the user later confirmed a successful playable/downloadable rebuilt track.
- Separation is not acoustically perfect: the user reports noticeable guitar bleed in at least one test. This is now reflected in customer-facing expectation copy rather than implying perfect isolation.

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

## Validation status
Completed / user-confirmed:
- `/bts` is live.
- BTS browser processing reaches the dedicated Modal separator.
- Demucs six-stem separation completes.
- The rebuilt backing track is playable in-browser and downloadable as MP3 according to the user's latest successful test.
- BTS token creator/tracker routes are live and isolated from AI Tab.
- AI Tab payment/token logic remains isolated from BTS.
- Branch-only UI now removes internal workflow implementation copy, exposes the shared 14-language selector, and includes SEO-focused content.
- Branch-only BTS route metadata now has a dedicated title, description, canonical, keyword set, social metadata, and index/follow settings.

Still to complete:
1. Remove the failed temporary one-time workflow file from `backing-track-studio`.
2. Re-fetch/inspect the final branch files after cleanup.
3. Do not promote these UI/SEO changes to `main`/Production without explicit user authorization.
4. When localization work begins, create real localized BTS routes/content before adding `bts` to `LOCALIZED_ROUTE_ROOTS` or publishing hreflang alternates.
5. Independently confirm source Blob deletion and hourly cleanup cron runtime authorization if full operational closure is desired.

## Progress score
**Current Project Progress Score: 99%.**

Core BTS functionality is working according to the user's live test. The remaining work is branch cleanup/verification, optional operational cleanup verification, and explicit authorization before promoting the new UI/SEO/localization-prep changes.
