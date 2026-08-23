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
| User audio selection | WIRED / CONTRACT PROVEN | `app/ai-tab/page.js` accepts MP3/WAV/M4A/AAC and requires copyright confirmation; end-to-end contract CI passes. | Keep limits/types synchronized with upload route. |
| Instrument selection | WIRED / CONTRACT PROVEN | Lead, Rhythm and Bass are explicit choices and server-validated. | Preserve all three choices throughout every downstream contract. |
| Private audio upload | WIRED / CONTRACT PROVEN | `app/ai-tab/page.js` → `/api/audio-upload` → private Vercel Blob. | Validate on real Preview once deployment auth is available. |
| Analyzer request routing | WIRED / FAIL-CLOSED SPLIT | Lead/Bass → legacy `ANALYZER_API_URL`; Rhythm may use `ANALYZER_API_URL_V143`. | Never silently route Lead/Bass through Rhythm. |
| Rhythm requested-part separation | PROVEN REAL AUDIO | Deterministic two-view guitar separation through V143 frozen/seeded separator. | Preserve frozen settings and fail-closed identity. |
| Lead requested-part separation | LEGACY / NOT STARTED PROFESSIONALLY | Legacy Basic Pitch operates on normalized full mix. | Build an inactive Lead separation scaffold, then real-audio proof before routing. |
| Bass requested-part separation | INACTIVE SCAFFOLD CONTRACT PROVEN | `bass_professional_separator_scaffold.py`: direct Demucs6s Bass plus BS-RoFormer Instrumental → Demucs6s Bass; routing/identity disabled. | Later run a separate approved real-audio Bass separation canary; do not activate yet. |
| Rhythm note / timing / technique analysis | PROVEN REAL AUDIO | V143 canary produced authenticated measure/step/string/fret/MIDI, sustain, bends and legato evidence. | Close built-Next HTTP integration, then actual Vercel Preview integration. |
| Lead note / timing / technique analysis | PARTIAL / LEGACY | Legacy output has note timing/string/fret heuristics but no authenticated measure-grid identity or rich professional metadata. | Establish Lead analyzer, quality gate, and structured event contract. |
| Bass note / timing / technique analysis | PARTIAL / LEGACY | Legacy Bass has Basic Pitch/full-mix events, heuristic fretboard assignment, bend-only technique evidence; professional Bass scaffold currently covers separation only. | Build Bass note/timing/technique pipeline and quality gate after separation canary. |
| Analysis normalization | WIRED / FAIL-CLOSED | Legacy events normalize for metadata; structured `renderEvents` only appear for proven V143 reference-free identity. | Generalize only after another instrument earns independent identity. |
| Browser metadata transport | PROVEN | Fresh analyzer result is stored and forwarded to both Preview/full routes. | Preserve same authenticated analysis for both PDFs. |
| Professional Preview PDF | RHYTHM DIRECTLY PROVEN; BUILT-HTTP GATE IN PROGRESS | Structured Rhythm mode `v143-structured-rhythm`; safe polished fallback retained. | Finish bounded built-Next HTTP gate, then real Preview test. |
| Purchased/unlocked full PDF | WIRED; RENDERER PARITY CONTRACT PROVEN | Full route verifies unlock and shares the same professional feature helper and `createJimmyPaigeProfessionalPdf` with Preview. | Avoid real payment/token/email automation; later validate safe deployed integration. |
| Production promotion | DISABLED | Current evidence keeps `productionPromotionAuthorized:false`. | Separate explicit Production decision only after Preview proof. |

## Whole-product contract evidence

Verifier:

`analyzer/verify_ai_tab_end_to_end_contract.mjs`

Workflow:

`.github/workflows/ai-tab-end-to-end-contract.yml`

Evidence:

`debug/v143-contextual-prune/ai-tab-end-to-end-contract.json`

Latest schema-2 result:

```text
passed: true
instrumentChoices: lead, rhythm, bass
userAudioUploadWired: true
copyrightGateWired: true
analyzerRequestWired: true
previewPdfWired: true
fullPdfUnlockWired: true
analysisMetadataTransportWired: true
previewAndFullProfessionalFeatureGateShared: true
previewAndFullProfessionalRendererShared: true
rhythmDedicatedV143RouteFailClosed: true
rhythmStructuredProfessionalRendererFailClosed: true
leadLegacyPreserved: true
bassLegacyPreserved: true
leadStructuredProfessionalIdentityPresent: false
bassStructuredProfessionalIdentityPresent: false
missingPlacementManufacturedForLegacy: false
productionModified: false
productionPromotionAuthorized: false
```

This proves the customer-facing Bass/Lead/Rhythm pipeline is connected while professional structured identity remains fail-closed.

## Current professional structured-render eligibility

### Rhythm

Rhythm is the only instrument currently allowed into structured professional engraving.

Eligibility remains fail-closed:

1. request is Rhythm;
2. dedicated V143 analyzer is selected;
3. `liveV143.referenceFree === true`;
4. analyzer quality gate passes;
5. authenticated `renderEvents` survive the contract;
6. engine identity is `v143-reference-free-rhythm`;
7. PDF may route to `v143-structured-rhythm`.

Any failure stays fallback-labeled and polished rendering remains available.

### Bass

Bass customer routing remains legacy, but an inactive professional separation scaffold now exists.

Files:

```text
analyzer/bass_professional_separator_scaffold.py
analyzer/verify_bass_professional_separator_scaffold.py
.github/workflows/bass-professional-separator-scaffold.yml
```

Evidence:

`debug/v143-contextual-prune/bass-professional-separator-scaffold.json`

Bot evidence commit:

`70c5411d2e72f06923e88075e6f48f9555a8c0e5`

Passed contract:

```text
directPath: audio -> Demucs6s Bass
cascadePath: audio -> BS-RoFormer Instrumental -> Demucs6s Bass
demucsSingleStem: Bass
demucsShifts: 1
demucsOverlap: 0.10
demucsSegmentSize: 6
deterministicSeed: 143
referenceFree: true
diagnosticOnly: true
productionCandidate: false
analyzerRoutingEnabled: false
professionalStructuredIdentityEnabled: false
realAudioBassCanaryPassed: false
noteTimingTechniqueQualityProven: false
productionModified: false
productionPromotionAuthorized: false
passed: true
```

This is intentionally **not** a Bass analyzer and is not connected to `/api/analyze-audio-tab`.

### Lead

Lead remains legacy and no professional separation scaffold has yet been activated or claimed.

### Requirements before Lead or Bass can become structured

Each must independently prove:

- requested-part separation;
- note/pitch validity;
- playable string/fret validity;
- authenticated measure/subdivision timing;
- attacks, durations and sustain;
- instrument-relevant techniques;
- tuning, tempo, meter and key metadata;
- conservative quality/survival thresholds;
- distinct fail-closed engine identity;
- approved real-audio canary;
- professional Preview and full-PDF render evidence.

Only after those proofs should `jimmyPaigeAnalysisPayload` or professional PDF routing accept a new Lead/Bass structured identity.

## Confirmed browser/customer flow

`app/ai-tab/page.js` currently performs:

1. select Lead, Rhythm or Bass;
2. choose permitted audio and confirm rights;
3. private upload through `/api/audio-upload`;
4. call `/api/analyze-audio-tab` with selected type;
5. store `generatedTab` plus fresh analysis metadata;
6. send same metadata to `/api/generate-tab-preview`;
7. show Preview before unlock;
8. PayPal/free-token provides unlock reference;
9. send same tab + metadata to `/api/generate-tab-pdf`;
10. server verifies unlock, creates full PDF, returns download and may email it.

Preview and full routes are now contract-verified to share both the professional feature gate and professional renderer helper.

Automated branch tests must stop before real payment, token redemption or customer email.

## Current highest-priority construction order

1. Finish/read the bounded built-Next Rhythm HTTP gate.
2. Close real Vercel Preview wiring when an exact-branch authenticated deployment path is available.
3. Validate real uploaded-audio Rhythm through actual Preview only after required Preview runtime keys are confirmed.
4. Preserve Rhythm as the proven reference implementation.
5. Keep the Bass scaffold inactive; next Bass milestone is an isolated approved real-audio separation canary, not routing.
6. Build a separate inactive Lead professional separation scaffold when Rhythm integration is stable.
7. Build instrument-specific note/timing/technique/quality pipelines.
8. Extend structured renderer identities only after each instrument earns real-audio analyzer + PDF evidence.
9. Validate purchased/unlocked full-PDF integration without weakening payment/token/email protections.
10. Make Production promotion a separate explicit decision.

## Non-negotiable construction rules

- Never manufacture missing musical timing/placement in browser or PDF code.
- Never relabel legacy output as professional structured output merely to obtain parity.
- Never weaken Rhythm quality gates to make another instrument pass.
- Keep Lead/Bass legacy customer behavior available until a replacement is independently proven.
- Keep the new Bass scaffold inactive until real-audio evidence exists.
- Preview and full PDF must derive from the same authenticated analysis result.
- Keep structured professional rendering fail-closed.
- Keep Production promotion disabled until separately authorized.
