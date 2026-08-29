# CURRENT STATE — Backing Track Studio

Updated: 2026-08-29 UTC  
Branch: `backing-track-studio`

## Active phase
**Backing Track Studio initialization / blueprint inspection.** This project is isolated from `main`; `main`/Production must remain untouched unless explicitly requested.

## Working route
- Working route: `/bts` -> `dadrocktabs.com/bts`.
- This is a provisional interpretation of the user's typed `dadrocktabs.com/it's`, based on the project name **Backing Track Studio** and the existing logo filename `public/dadrock-tabs-bts-logo.png`.
- Keep route easy to rename if the user intended a different path.

## Frozen product intent
Create a new Backing Track Studio page using `app/ai-tab/page.js` as the UI/workflow blueprint.

### User flow
1. User uploads an audio file using the same upload approach as `/ai-tab`.
2. Reuse the same email validation/verifier flow as `/ai-tab`.
3. User chooses one removal mode:
   - remove guitars;
   - remove bass;
   - remove both guitars and bass.
4. Reuse the current source-separation model/infrastructure used by `/ai-tab`; Modal performs the separation according to the selected removal mode.
5. Produce a downloadable backing track with the requested instruments removed.
6. Use the existing PayPal **sandbox** testing flow.
7. Test price: **USD $1.00 per backing track**.
8. Use logo: `/dadrock-tabs-bts-logo.png` (existing file under `public/`).

## Implementation principles
- Reuse proven `/ai-tab` patterns/components where practical rather than duplicating unrelated logic.
- Keep Backing Track Studio APIs/routes distinct enough that changes cannot break `/ai-tab`.
- Reuse existing secure Vercel Blob upload conventions and email verification semantics.
- Reuse existing PayPal sandbox integration, but keep BTS product/price/order metadata explicit.
- Reuse existing Modal source-separation infrastructure; do not introduce a new separation model unless required.
- Uploaded audio must be treated as user-provided content and processed only for the requested job.
- Do not alter `main` or Production during development.

## Progress score — STANDING
The user prefers a percentage progress score during work.

Use this five-gate rubric (20 points each):
1. **Project scope + isolated branch + checkpoint frozen** — 20%.
2. **Blueprint/dependency inspection complete** — 20%.
3. **BTS page + upload/email/removal UI implemented** — 20%.
4. **Modal separation + PayPal sandbox $1 flow + download delivery implemented** — 20%.
5. **End-to-end validation/build checks complete and handoff-ready** — 20%.

**Current Project Progress Score: 20%.**

## Known starting assets
- Blueprint: `app/ai-tab/page.js` on `main`.
- BTS logo: `public/dadrock-tabs-bts-logo.png` (~1.72 MB, confirmed by user screenshot).
- Existing project already has Vercel Blob upload, PayPal checkout, and Modal-backed audio processing patterns associated with `/ai-tab`; exact reusable paths are being inspected before implementation.

## NEXT
1. Inspect the current `/ai-tab` page completely enough to identify upload, email verification, checkout, status, and delivery dependencies.
2. Identify exact API routes/components used by `/ai-tab` for Vercel Blob, PayPal sandbox, email verifier, and Modal source separation.
3. Save this checkpoint after the dependency map is frozen.
4. Scaffold `/bts` only after the dependency map is understood.
5. Keep saving this file frequently while work proceeds.
6. Never modify `main`/Production without explicit user direction.
