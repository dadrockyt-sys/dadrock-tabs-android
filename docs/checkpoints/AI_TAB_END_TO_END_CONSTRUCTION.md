# DadRock `/ai-tab` — End-to-End Construction Map

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`

## Product definition

The project is the complete customer-facing construction of `dadrocktabs.com/ai-tab`:

> User audio → Bass / Lead / Rhythm selection → upload and page workflow → requested-part separation / processing → authenticated notes + playable positions + techniques + timing + metadata → professional preview TAB PDF → purchased/unlocked professional full TAB PDF.

This document tracks the whole product, not only the current V143 Rhythm canary.

## End-to-end stage map

| Stage | Current state | Evidence / implementation | Next construction requirement |
| --- | --- | --- | --- |
| User audio selection | WIRED | `app/ai-tab/page.js` accepts MP3/WAV/M4A/AAC and requires copyright confirmation. | Keep limits/types synchronized with upload route. |
| Instrument selection | WIRED | Lead, Rhythm and Bass are explicit UI choices and validated server-side. | Preserve all three choices throughout every downstream contract. |
| Private audio upload | WIRED | `app/ai-tab/page.js` → `/api/audio-upload` → private Vercel Blob. | Validate on real Preview once deployment auth is available. |
| Analyzer request routing | WIRED / SPLIT | `/api/analyze-audio-tab` routes Lead/Bass to legacy `ANALYZER_API_URL`; Rhythm can opt into `ANALYZER_API_URL_V143`. | Do not silently route Lead/Bass through Rhythm. Add instrument-specific professional identities only after their analyzers are proven. |
| Rhythm requested-part separation | PROVEN | V143 uses deterministic seeded separation through `v143_rhythm_deterministic_stem_provider.py` → `v143_deterministic_separator.py`. | Preserve frozen separator settings and fail-closed identity. |
| Lead requested-part separation | LEGACY / NOT YET PROFESSIONAL-CONTRACT PROVEN | Lead remains on the legacy analyzer path. | Build and validate a Lead-specific professional separation + analysis contract before structured engraving activation. |
| Bass requested-part separation | LEGACY / NOT YET PROFESSIONAL-CONTRACT PROVEN | Bass remains on the legacy analyzer path. | Build and validate a Bass-specific professional separation + analysis contract before structured engraving activation. |
| Rhythm note / timing / technique analysis | PROVEN CANARY | V143 real-audio canary produced authenticated measure/step/string/fret/MIDI events, sustain and observed bends/legato techniques. | Close built Next HTTP integration, then actual Vercel Preview integration. |
| Lead note / timing / technique analysis | PARTIAL / LEGACY | Legacy analyzer output is normalized for browser metadata but has no authenticated structured-render identity. | Establish Lead quality gates and structured render-event contract. |
| Bass note / timing / technique analysis | PARTIAL / LEGACY | Legacy analyzer output is normalized for browser metadata but has no authenticated structured-render identity. | Establish Bass quality gates and structured render-event contract. |
| Analysis normalization | WIRED / FAIL-CLOSED | `lib/jimmyPaigeAnalysisPayload.js` normalizes legacy events but only exposes `renderEvents` when V143 reference-free identity is proven. | Generalize only when Lead/Bass have their own proven identities; never infer missing placement in browser/PDF code. |
| Browser metadata transport | PROVEN | Fresh analyzer response is stored and forwarded to preview/full PDF routes; stale analysis is cleared before generation. | Keep preview and full PDF using the same authenticated analysis payload. |
| Professional preview PDF | RHYTHM PROVEN DIRECTLY; BUILT-HTTP GATE IN PROGRESS | `/api/generate-tab-preview`; structured Rhythm renderer is `v143-structured-rhythm`; safe fallback remains polished renderer. | Finish bounded built-Next HTTP gate, then real Vercel Preview route test. |
| Purchased/unlocked full PDF | WIRED; PROFESSIONAL RHYTHM RENDERER PROVEN DIRECTLY | `/api/generate-tab-pdf` verifies PayPal/free-token unlock, creates full PDF, downloads it and emails a copy. | Do not automate payment/token/email during branch validation. Validate renderer route only after safe Preview strategy exists. |
| Production promotion | DISABLED | All current V143 evidence carries `productionPromotionAuthorized: false`. | Separate explicit production decision only after Preview end-to-end proof. |

## Current professional structured-render eligibility

### Rhythm

Rhythm is the only instrument currently allowed to enter the V143 structured professional engraving path.

The eligibility chain is deliberately fail-closed:

1. The request is Rhythm.
2. The dedicated V143 analyzer URL is selected.
3. The analyzer identifies itself with `liveV143.referenceFree === true`.
4. The analyzer quality gate passes.
5. Authenticated `renderEvents` survive the render contract.
6. `analysisEngine` becomes `v143-reference-free-rhythm`.
7. Professional PDF routing may use `v143-structured-rhythm`.

If any requirement fails, the response is fallback-labeled and polished safe rendering remains available.

### Lead and Bass

Lead and Bass currently remain legacy by design.

They must **not** become structured simply because their normalized events contain pitch/string/fret data. A professional instrument path must prove, at minimum:

- requested-part separation appropriate to the selected instrument;
- note/pitch validity;
- playable instrument position validity;
- authenticated measure and subdivision placement;
- attacks, durations and sustain;
- instrument-relevant techniques/articulations;
- tuning, tempo and meter metadata;
- quality/survival thresholds;
- a distinct fail-closed analysis-engine identity;
- real-audio canary evidence;
- professional preview and full-PDF render evidence.

Only after that evidence exists should `jimmyPaigeAnalysisPayload` and the professional renderer accept a new Lead or Bass structured engine identity.

## Confirmed browser/customer flow

`app/ai-tab/page.js` currently performs the expected customer sequence:

1. User selects Lead, Rhythm or Bass.
2. User chooses permitted audio and confirms rights.
3. Audio uploads privately through `/api/audio-upload`.
4. Browser calls `/api/analyze-audio-tab` with the selected transcription type.
5. The returned `generatedTab` and analysis metadata are stored together.
6. Browser sends the same analysis metadata to `/api/generate-tab-preview`.
7. The preview PDF is shown before unlock.
8. PayPal or free-token unlock supplies an unlock reference.
9. Browser sends the same generated tab + analysis metadata to `/api/generate-tab-pdf`.
10. Server verifies the unlock, creates the full PDF, returns it for download and sends the PDF by email.

Automated branch tests must stop before real payment, token redemption or customer email.

## Current highest-priority construction order

1. Finish the bounded built-Next Rhythm HTTP gate.
2. Close real Vercel Preview wiring when an exact-branch authenticated deployment path is available.
3. Validate real uploaded-audio Rhythm through the actual Preview application path using the approved fixture only after required Preview runtime keys are confirmed.
4. Preserve Rhythm as the proven reference implementation.
5. Start a separate Lead professional analyzer track using the same fail-closed principles.
6. Start a separate Bass professional analyzer track using the same fail-closed principles.
7. Extend structured renderer identities only after each instrument earns real-audio analyzer + PDF evidence.
8. Validate purchased/unlocked full-PDF behavior without weakening payment/token/email protections.
9. Make Production promotion a separate explicit decision.

## Non-negotiable construction rules

- Never manufacture missing musical timing/placement in browser or PDF code.
- Never relabel legacy output as professional structured output merely to obtain parity.
- Never weaken Rhythm quality gates to make another instrument pass.
- Keep Lead/Bass legacy behavior available until a replacement path is independently proven.
- Preview and full PDF must derive from the same authenticated analysis result.
- Keep structured professional rendering fail-closed.
- Keep Production promotion disabled until separately authorized.
