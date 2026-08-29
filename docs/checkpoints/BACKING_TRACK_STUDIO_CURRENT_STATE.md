# CURRENT STATE — Backing Track Studio

Updated: 2026-08-29 UTC  
Checkpoint branch: `backing-track-studio`  
Production branch: `main`

## Active phase
**BTS is live in Production, and the latest user test proves Demucs completed six-stem waveform separation. The post-separation handoff/rebuild hardening has now been ported and validated on `backing-track-studio` only. No `main`, Vercel Production, or live Modal deployment change was made in this continuation.**

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

The branch head after the fix is `d4fe85a885912a11c54014409f92d82f40668559`.

## Isolation status
- All writes in this continuation were made to `backing-track-studio`.
- `main` was read only for comparison and was not modified.
- No Production deployment was triggered.
- No live Modal redeploy was triggered.

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
- Latest live evidence confirms the model produced all six stems.
- Branch-only worker now contains hardened stem handoff logic matching that observed output behavior.

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

## Required runtime configuration for complete end-to-end processing
Previously confirmed during live testing:
- `BLOB_READ_WRITE_TOKEN` — present in Production.
- `BTS_SEPARATOR_API_URL` / `BTS_SEPARATOR_API_TOKEN` — were initially missing; later live test reached the separator and completed Demucs, so the current request path is reaching Modal.

Also required/expected:
- `NEXT_PUBLIC_PAYPAL_CLIENT_ID` / sandbox PayPal client ID
- `PAYPAL_CLIENT_SECRET`
- `CRON_SECRET`
- optional `BTS_JOB_SIGNING_SECRET`
- Modal secret `dadrock-bts-separator-secret` with matching `BTS_SEPARATOR_API_TOKEN`
- existing MongoDB configuration
- existing `ADMIN_PASSWORD` for token administration

## Validation status
Completed:
- BTS production builds compiled successfully with Next.js 16.1.6 / Turbopack during the prior promotion cycle.
- `/bts` is live.
- BTS token creator/tracker routes are live.
- BTS token admin endpoint requires authentication.
- AI Tab token/payment logic remains isolated from BTS.
- Browser processing reached `/api/bts/process` and the dedicated Modal separator.
- Latest live log proves Demucs six-stem separation completed and wrote Guitar/Bass/Drums/Vocals/Other/Piano WAVs.
- Branch-only post-separation handoff fix is committed and passes static/simulated filename validation.

Still to complete:
1. **Do not deploy yet without explicit user authorization**, because this continuation is branch-only.
2. When authorized, promote/deploy the tested worker fix.
3. Retry the BTS flow with permitted audio and confirm a playable MP3 download.
4. Confirm source Blob deletion immediately after success.
5. Verify token decrement/redemption entry in the admin tracker.
6. Separately test the $1 PayPal sandbox path.
7. Confirm hourly cleanup cron behavior/runtime authorization for an abandoned test upload.

## Progress score
**Current Project Progress Score: 99%.**

The code fix for the observed failure is prepared and validated on the isolated branch. The final 1% is deployment plus end-to-end verification of download, deletion, token accounting, PayPal sandbox, and cleanup behavior.
