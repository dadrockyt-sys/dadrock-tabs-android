# CURRENT STATE — Backing Track Studio

Updated: 2026-08-29 UTC  
Branch: `backing-track-studio`

## Active phase
**Dependency map frozen; ready to scaffold `/bts`.** This project is isolated from `main`; `main`/Production must remain untouched unless explicitly requested.

## Working route
- Working route: `/bts` -> `dadrocktabs.com/bts`.
- Use the existing logo at `public/dadrock-tabs-bts-logo.png`.

## Frozen product intent
Create a new Backing Track Studio page using `app/ai-tab/page.js` as the UI/workflow blueprint.

### User flow
1. User uploads an audio file using the same upload approach as `/ai-tab`.
2. Reuse the same email-validation semantics as `/ai-tab`.
3. User chooses one removal mode:
   - Remove Guitars;
   - Remove Bass;
   - Remove Guitars + Bass.
4. Process the uploaded audio through Modal using genuine waveform/stem separation.
5. Produce a downloadable backing track with the requested instrument stem(s) removed.
6. Use PayPal **sandbox** during testing.
7. Test price: **USD $1.00 per backing track**.
8. Keep BTS payment/API logic isolated so the existing AI-tab USD $2.99 product is unchanged.

## Implementation principles
- Reuse proven `/ai-tab` UX patterns where practical, but keep BTS product APIs/payment paths dedicated.
- Reuse the existing Vercel Blob upload approach.
- Do not reuse transcription note/register filtering as backing-track generation.
- Reuse the proven research separator substrate where appropriate instead of introducing an unrelated model stack.
- Uploaded audio is user-provided content and is processed only for the requested job.
- Do not alter `main` or Production during development.

## Frozen `/ai-tab` dependency map

### Page / state flow
- Blueprint: `app/ai-tab/page.js`.
- Client-side page controls file selection, email input, status/progress, payment unlock, generated-object URL, and browser download.
- `/ai-tab` uses a staged UX: upload -> analyze/preview -> payment -> generate/deliver. BTS can use the same visual/status language but has a simpler upload -> choose removal -> email -> payment -> stem processing -> download flow.

### Audio upload
`/ai-tab` currently uses:
1. `POST /api/audio-upload` with `{ filename, contentType, size }`.
2. The route creates a private Vercel Blob target under `ai-tab-audio/...` and returns the upload URL / source URL.
3. The browser `PUT`s the file bytes to the returned URL with the source content type.
4. The page calls `POST /api/audio-upload/complete` with the resolved blob URL and file metadata.
5. The resulting private Blob URL is then handed to server-side processing.

Relevant route:
- `app/api/audio-upload/route.js`

BTS implementation decision:
- Preserve the same upload interaction/style.
- Prefer a BTS-specific upload namespace/route if code changes are needed, so no AI-tab upload behavior is changed.

### AI processing / Modal handoff
Current AI-tab analysis route:
- `app/api/analyze-audio-tab/route.js`
- Resolves private Vercel Blob audio with `BLOB_READ_WRITE_TOKEN`.
- Sends the source audio to the Modal analyzer as multipart form data.
- Returns transcription/chord/note-event JSON.

Important: this route is transcription-oriented and does **not** produce a backing-track waveform. BTS requires a dedicated processing route that returns audio bytes or a BTS-owned downloadable artifact.

### Email semantics
- Current `/ai-tab` page validates email client-side with a normal email-format regex.
- The visible current flow does **not** perform an OTP/code challenge before checkout; its current “verification” semantics are valid-format confirmation plus use of that address for the paid result.
- The email is locked/used as part of the paid generation flow.
- `app/api/generate-tab-pdf/route.js` uses Resend first and Nodemailer as a fallback to deliver the generated PDF, while also returning the PDF to the browser.

BTS implementation decision:
- Match the existing AI-tab email-format validation/confirmation behavior unless a separate verifier is introduced later.
- Do not claim OTP verification exists when it does not.
- Backing-track delivery can be a browser download; email may remain checkout/job metadata unless a safe link-delivery path is added later.

### Status + download behavior
- `/ai-tab` maintains explicit upload/analysis/generation states and creates a browser object URL from the generated binary response.
- BTS should mirror this pattern: processing state -> binary audio response -> `URL.createObjectURL()` -> downloadable backing-track link.
- This avoids making the BTS MVP dependent on persistent storage of the processed track.

### PayPal
Existing pieces:
- `components/PayPalCheckoutButton.js`
- `app/api/paypal/create-order/route.js`
- `app/api/paypal/capture-order/route.js`

Critical isolation findings:
- The existing AI-tab button currently creates/captures through the PayPal JS SDK and hardcodes **USD $2.99** in the client component.
- Existing backend create-order logic also hardcodes **USD $2.99**.
- Therefore BTS must not modify those files to change the price.

BTS implementation decision:
- Add a dedicated BTS PayPal button/component.
- Add dedicated BTS create/capture routes (for example `/api/bts/paypal/create-order` and `/api/bts/paypal/capture-order`).
- Freeze BTS testing amount to **USD $1.00** server-side.
- Continue using PayPal sandbox credentials/base URL during development.

## Research-branch waveform separator inspection — COMPLETE
The active AI-tab research lineage contains genuine waveform/audio-stem separation; BTS does **not** need to invent a separator from scratch.

### Proven reusable research pieces
- `analyzer/audio-separation-requirements-20260814.txt`
  - includes `audio-separator[gpu]==0.30.2`.
- `analyzer/v143_production_separator.py`
  - genuine audio-stem separation using `audio-separator`.
  - normalizes arbitrary source audio to PCM WAV via FFmpeg.
  - Guitar path uses Demucs 6-source model `htdemucs_6s.yaml` with `--single_stem Guitar`.
  - optional cascade uses BS-RoFormer instrumental model `model_bs_roformer_ep_317_sdr_12.9755.ckpt` before Demucs Guitar extraction.
- `analyzer/bass_professional_separator_scaffold.py`
  - genuine Bass stem extraction with the same Demucs 6-source model and `--single_stem Bass`.
  - direct Bass path plus optional BS-RoFormer -> Demucs Bass cascade.
- `analyzer/analyze_and_grade_gomyway_gpu_separator_stem_v1.py`
  - consumes separator-produced waveform stems for downstream grading, confirming these are actual audio files/stems rather than note-register filtering.

### BTS separator decision
Use the smallest dedicated BTS Modal worker built on the already-proven `audio-separator` / Demucs 6-source substrate:
- normalize uploaded source audio;
- separate the full 6-source stem set once;
- reconstruct the backing track by summing all stems except Guitar, Bass, or both according to the selected mode;
- encode a downloadable audio result (MP3 preferred for transfer size; WAV may be used internally);
- keep this BTS worker/API separate from the frozen AI-tab analyzer endpoint.

Why full-stem reconstruction instead of subtracting a single estimated stem from the original:
- it gives one deterministic source-of-truth stem set for all three removal modes;
- it avoids phase/codec differences that can make `original - estimated_stem` less reliable;
- `htdemucs_6s` already exposes both Guitar and Bass identities in the research substrate.

The BS-RoFormer cascade remains optional for later quality experiments; the BTS MVP should start with direct Demucs 6-source separation because it is the smallest path that natively supports both requested instruments.

## Planned BTS file boundaries
- `app/bts/page.js` — BTS UI only.
- `components/BTSPayPalCheckoutButton.js` — BTS $1 sandbox checkout only.
- `app/api/bts/process/route.js` — BTS source fetch -> Modal -> downloadable audio response.
- `app/api/bts/paypal/create-order/route.js` — BTS sandbox order creation, server-fixed USD $1.00.
- `app/api/bts/paypal/capture-order/route.js` — BTS sandbox capture.
- `analyzer/modal_bts_separator.py` — dedicated Modal waveform/stem worker.
- `analyzer/bts-audio-separation-requirements.txt` — minimal BTS worker dependencies if required.

## Progress score — STANDING
The user prefers a percentage progress score during work.

Use this five-gate rubric (20 points each):
1. **Project scope + isolated branch + checkpoint frozen** — complete.
2. **Blueprint/dependency inspection complete** — complete.
3. **BTS page + upload/email/removal UI implemented** — pending.
4. **Modal separation + PayPal sandbox $1 flow + download delivery implemented** — pending.
5. **End-to-end validation/build checks complete and handoff-ready** — pending.

**Current Project Progress Score: 40%.**

## Safety rails
- Work only on `backing-track-studio`.
- Never modify `main` or Production without explicit user direction.
- Re-fetch this checkpoint first when resuming work in a new chat/session.
- Save back to this checkpoint frequently while working.
- Existing AI-tab $2.99 payment behavior is frozen and must remain unchanged.
- Existing AI-tab production analyzer endpoint is frozen and must remain unchanged.

## NEXT
1. Scaffold `app/bts/page.js` using the AI-tab visual/upload/status blueprint and the BTS logo.
2. Add removal choices: Guitar, Bass, Guitar + Bass.
3. Add dedicated BTS $1 PayPal sandbox component/routes.
4. Add dedicated BTS processing route and Modal stem-removal worker using the frozen Demucs 6-source substrate.
5. Save this checkpoint again after scaffolding/API work.
6. Run available build/static checks and inspect branch diffs before handoff.