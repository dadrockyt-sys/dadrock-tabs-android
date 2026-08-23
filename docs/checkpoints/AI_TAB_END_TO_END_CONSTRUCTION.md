# DadRock `/ai-tab` — End-to-End Construction Map

Updated: 2026-08-22
Branch: `v143-contextual-prune-lobo`

## Product definition

> **User audio → Bass / Lead / Rhythm selection → upload/page workflow → requested-part separation/processing → authenticated notes + playable positions + techniques + timing + metadata → professional preview TAB PDF → purchased/unlocked professional full TAB PDF.**

This tracks the whole product, not only the current V143 Rhythm canary.

## Stage map

| Stage | Current state | Evidence / implementation | Next requirement |
| --- | --- | --- | --- |
| User audio + rights confirmation | CONTRACT PROVEN | `app/ai-tab/page.js`, `/api/audio-upload`, end-to-end contract CI | Real Preview validation later. |
| Bass / Lead / Rhythm selection | CONTRACT PROVEN | UI + upload/analyzer/PDF routes preserve all three values | Preserve through all new instrument tracks. |
| Private upload | WIRED | Private Vercel Blob | Validate exact deployed Preview later. |
| Analyzer request routing | FAIL-CLOSED SPLIT | Lead/Bass legacy; Rhythm V143 when configured | Add new instrument identities only after proof. |
| Rhythm separation | REAL-AUDIO PROVEN | Deterministic two-view guitar separation | Freeze proven settings. |
| Bass separation | INACTIVE CONTRACT PROVEN | Direct Demucs6s Bass + BS-RoFormer Instrumental → Demucs6s Bass | Approved real-audio Bass canary later; no routing yet. |
| Lead separation | NOT STARTED PROFESSIONALLY | Lead/Rhythm share the physical Guitar stem | Future Lead must use separated guitar views + Lead-specific musical selection, not a fake Lead stem. |
| Rhythm notes/timing/techniques | REAL-AUDIO PROVEN | Authenticated measure/step/string/fret/MIDI, sustain, bends/legato | Finish built-Next + Preview integration. |
| Bass notes/timing/techniques | LEGACY ONLY | Legacy Basic Pitch/full-mix baseline; new scaffold currently separation-only | Build reference-free Bass analysis + quality gate after separation canary. |
| Lead notes/timing/techniques | LEGACY ONLY | No authenticated structured Lead identity | Build reference-free Lead analysis + quality gate. |
| Rhythm structured render contract | PROVEN | Existing V143 Rhythm contract + professional renderer | Keep fail-closed. |
| Bass structured render contract | INACTIVE CONTRACT PROVEN | Four-string `G-D-A-E`, MIDI/fret consistency, max fret 24 | Build actual Bass PDF renderer only after real-audio analyzer proof. |
| Analysis normalization | FAIL-CLOSED | Legacy metadata normalizes but no structured events unless proven reference-free identity | Generalize only after new engine proof. |
| Browser metadata transport | PROVEN | Fresh analysis forwarded to Preview and full routes | Preserve same payload. |
| Preview/full renderer parity | CONTRACT PROVEN | Both routes share feature helper + `createJimmyPaigeProfessionalPdf` | Deployed Preview validation later. |
| Purchased/unlocked PDF | WIRED | PayPal/free-token verification + full PDF/email | Do not automate side-effectful route in branch validation. |
| Production promotion | DISABLED | Evidence carries `productionPromotionAuthorized:false` | Separate explicit decision only after Preview proof. |

## Whole-product contract evidence

Verifier:

`analyzer/verify_ai_tab_end_to_end_contract.mjs`

Evidence:

`debug/v143-contextual-prune/ai-tab-end-to-end-contract.json`

Latest schema-2:

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

## Rhythm professional eligibility

Rhythm is currently the only instrument allowed into structured professional engraving. It must prove all of:

1. request is Rhythm;
2. dedicated V143 analyzer selected;
3. `liveV143.referenceFree === true`;
4. quality gate passes;
5. authenticated structured events survive;
6. engine identity is `v143-reference-free-rhythm`;
7. professional PDF may route to `v143-structured-rhythm`.

Any failure stays fallback-labeled.

## Bass professional construction

### Separation substrate — passed, inactive

Files:

```text
analyzer/bass_professional_separator_scaffold.py
analyzer/verify_bass_professional_separator_scaffold.py
.github/workflows/bass-professional-separator-scaffold.yml
```

Evidence:

`debug/v143-contextual-prune/bass-professional-separator-scaffold.json`

Bot commit:

`70c5411d2e72f06923e88075e6f48f9555a8c0e5`

```text
passed: true
directPath: audio -> Demucs6s Bass
cascadePath: audio -> BS-RoFormer Instrumental -> Demucs6s Bass
demucsSingleStem: Bass
demucsShifts: 1
demucsOverlap: 0.10
demucsSegmentSize: 6
deterministicSeed: 143
referenceFree: true
diagnosticOnly: true
analyzerRoutingEnabled: false
professionalStructuredIdentityEnabled: false
realAudioBassCanaryPassed: false
```

### Four-string render contract — passed, inactive

Files:

```text
lib/bassProfessionalRenderContract.js
analyzer/verify_bass_professional_render_contract.mjs
.github/workflows/bass-professional-render-contract.yml
```

Evidence:

`debug/v143-contextual-prune/bass-professional-render-contract.json`

Bot commit:

`4bd524c79feb621c497d8917128b36e971d85d1b`

```text
passed: true
tuning: Standard Bass
stringLabels: G, D, A, E
openMidi: 43, 38, 33, 28
stringCount: 4
maximumFret: 24
stepsPerMeasure: 16
validFixtureEvents: 4
projectedFixtureEvents: 4
invalidFixtureEventsRejected: 5
pitchStringFretConsistencyRequired: true
diagnosticOnly: true
productionCandidate: false
pdfRendererEnabled: false
analyzerRoutingEnabled: false
professionalStructuredIdentityEnabled: false
realAudioBassCanaryPassed: false
productionModified: false
productionPromotionAuthorized: false
```

This contract exists specifically so future Bass tablature cannot accidentally be rendered on the six-string Rhythm/Guitar staff.

### Historical diagnostics excluded

`analyzer/bass_technique_diagnostics_v7.py` explicitly identifies itself as:

`reference-guided-bass-technique-diagnostic-only`

It is read-only historical/benchmark diagnostic logic and must **not** be reused as evidence for the new reference-free Bass professional path.

## Lead professional construction

Lead and Rhythm do not have separate Demucs source stems; both are within the Guitar stem. Therefore future Lead construction should use the proven reference-free guitar separation substrate but implement an independent Lead-specific musical selection/analysis layer.

Do not create or claim a fictitious `Lead` source stem.

## Requirements before Bass or Lead structured activation

Each instrument must independently prove:

- requested-part separation/selection appropriate to the instrument;
- pitch validity;
- playable string/fret validity;
- measure/subdivision timing;
- attacks/durations/sustain;
- instrument-relevant techniques;
- tuning/tempo/meter/key metadata;
- conservative quality/survival thresholds;
- distinct fail-closed engine identity;
- approved real-audio canary;
- professional Preview/full-PDF evidence.

Only then may normalization or PDF routing accept a new structured identity.

## Confirmed customer flow

1. Select Lead, Rhythm, or Bass.
2. Choose permitted audio and confirm rights.
3. Private upload through `/api/audio-upload`.
4. Call `/api/analyze-audio-tab` with selected type.
5. Store `generatedTab` + fresh analysis metadata.
6. Send same metadata to `/api/generate-tab-preview`.
7. Show Preview.
8. PayPal/free-token supplies unlock reference.
9. Send same tab + metadata to `/api/generate-tab-pdf`.
10. Server verifies unlock, creates full PDF, returns download and may email it.

Automated branch testing stops before real payment, token redemption, or customer email.

## Current order

1. Finish staged built-Next Rhythm HTTP gate.
2. Close exact-branch Vercel Preview wiring when authenticated deployment is possible.
3. Validate real uploaded-audio Rhythm through actual Preview only after runtime keys are confirmed.
4. Preserve Rhythm as reference implementation.
5. Advance Bass from inactive contracts to an isolated approved real-audio canary; keep routing/identity/rendering disabled until it passes.
6. Start a separate reference-free Lead professional analysis track using guitar views.
7. Extend structured identities only after real-audio analyzer + PDF evidence.
8. Make Production promotion a separate explicit decision.

## Non-negotiables

- Never manufacture timing/placement in browser or PDF code.
- Never relabel legacy output as professional structured output.
- Never use historical reference-guided diagnostics as new reference-free evidence.
- Never weaken Rhythm quality gates to make another instrument pass.
- Preserve Lead/Bass legacy customer behavior until replacements are independently proven.
- Keep Bass separation/render scaffolds inactive until real-audio proof.
- Preview/full PDF use the same authenticated analysis.
- Keep Production promotion disabled until separately authorized.
