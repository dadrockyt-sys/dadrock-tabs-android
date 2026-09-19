# Jimmy PAIge Astra — Full-Chain Contract V1

Status: design contract; no production integration or real-audio execution
Date: 2026-09-19 UTC
Active branch: `astra-work`

## Purpose

This contract connects the existing `/ai-tab` product to the Astra backend without treating clean formatting as proof of correct transcription. It preserves the useful product boundary from V143 and the isolated deterministic notation/fingering stages from Songsterr Fresh.

The complete chain is:

```text
authorized audio reference
  -> requested role extraction (bass / rhythm / lead)
  -> note, chord, timing, duration and technique inference
  -> musical structure inference
  -> Astra deterministic rhythm and fretboard pipeline
  -> delivery eligibility decision
  -> preview/full-PDF payload
```

Every stage must expose its own status. A downstream stage cannot convert an unresolved upstream result into a customer-ready result.

## Request contract

The machine-readable request schema is `analyzer-request-v1.schema.json`.

Required fields:

- `contractName = jimmy-paige-astra-analyzer-request`
- `contractVersion = 1`
- `requestId`: server-generated opaque identifier; contains no customer email or filename
- `audioUrl` and `pathname`: server-controlled references to the uploaded object
- `song`, `artist`
- `transcriptionType`: exactly `lead`, `rhythm` or `bass`
- `conditioning`: structure and instrument configuration; unknown values are explicit `auto`, never fabricated defaults presented as inferred facts

The existing page currently supplies the audio reference and selected role. User-facing structure/tuning controls are optional. Server normalization remains authoritative.

## Analyzer result contract

The machine-readable result schema is `analyzer-result-v1.schema.json`.

The response retains frontend-compatible top-level fields:

- `generatedTab`
- `transcriptionType`
- `tuning`
- `tempo`
- `timeSignature`
- `keySignature`
- `techniques`
- `analysisEngine`
- `events`
- `renderEvents`

It adds an `astra` envelope with explicit stage status and delivery authority.

### Result states

- `complete`: every required stage is complete and the delivery gate passed.
- `partial`: useful evidence exists, but the product is incomplete; preview/full PDF remains blocked.
- `abstained`: the system cannot produce defensible tablature for the request.
- `failed`: infrastructure or input processing failed; no musical quality implication may be inferred.

`generatedTab` may be present for internal inspection on `partial`, but customer preview/full-PDF rendering requires all of:

- `astra.delivery.deliveryReady === true`
- `astra.overallStatus === "complete"`
- nonempty `generatedTab`
- nonempty `renderEvents`
- complete structure, playable-position and source-event lineage for every customer-rendered event

## Stage contracts

### 1. Input and provenance

Record request identity, audio byte identity when available, duration, decoded format and processing lineage. Do not store customer audio or credentials in Git. Reject missing, unreadable or unsupported input rather than returning a generic tab.

### 2. Requested-part extraction

The selected role is a product request, not evidence that the extracted stem contains that role.

Required status fields:

- extraction method/version
- requested role
- role-presence decision: `present`, `absent`, `uncertain`
- mixture/stem identities
- separation diagnostics
- known overlap or contamination indicators

The system must abstain when the requested role is absent or cannot be distinguished reliably. Lead and rhythm are musical functions; a separator that emits only a generic guitar stem has not completed role assignment.

### 3. Musical event inference

Each event carries:

- stable event ID
- MIDI pitch
- onset seconds
- offset or duration, or an explicit unresolved duration state
- confidence/evidence fields whose meaning and model identity are versioned
- chord/onset-cluster identity where applicable
- optional technique labels with confidence and provenance

Completeness and correctness are separate. Filtering low-confidence notes may improve precision while making the tab musically incomplete; both must be measured.

### 4. Musical structure

Tempo, meter, pickup, beat grid and feel each carry:

- value or `unresolved`
- source: user, mixture inference, role-stem inference or deterministic derivation
- confidence/evidence identity

Client renderer defaults such as 120 BPM or 4/4 are display fallbacks only. They must never be recorded as inferred musical truth.

### 5. Deterministic tab construction

`astra_backend/` owns structure mapping, rhythm spelling, rests/ties, simultaneous playable shapes, phrase-level fretboard paths and product projection. It must preserve source-event identity and expose every dropped, unresolved or heuristically assigned event.

The following Fresh qualities remain mandatory:

- event preservation is measurable
- pitch reconstruction from selected string/fret equals the supplied MIDI
- simultaneous notes use distinct strings
- physical ambiguity is explicit
- renderer incompatibility blocks structured rendering
- upstream evidence blockers prevent delivery

### 6. Delivery

Delivery is a separate decision. A syntactically valid PDF is not a quality pass.

The delivery envelope records:

- `deliveryReady`
- blockers
- exact analyzer, separator, structure and deterministic-pipeline versions
- benchmark/admission policy version used
- output identities for generated tab and render events

Payment unlocks an already qualified result. Payment must not change notes, thresholds, structure or fingering.

## Async and operational contract

Retain the proven ownership relationship from V143 as an integration requirement:

- result/control lifetime: 1800 seconds
- analyzer/orchestrator timeout ceiling: 1200 seconds
- ownership margin: 600 seconds

These values are documented constraints until the Astra service measures and explicitly revises them. All retries must be idempotent by `requestId`. A timeout returns `failed`, never a partial result labeled complete.

## Compatibility boundary

The current Next.js route on `main` is an observed integration target, not Astra source. Astra development does not modify `main` or live environment routing. A later adapter must map this V1 response to the existing preview/full-PDF calls without importing V143 selection rules, scorers or song-specific fixes.

## Security and privacy boundary

- Analyzer logs use request IDs, never tokens, customer emails or signed audio URLs.
- Audio retention/deletion behavior must match the product promise before production integration.
- Download authorization and payment validation remain server owned.
- Benchmark fixtures must have documented permission and must not be customer uploads.

## Versioning rule

Any semantic change to required fields, delivery eligibility, event meaning or source lineage creates a new contract version. Adding optional diagnostics that cannot affect delivery may retain V1 when documented.
