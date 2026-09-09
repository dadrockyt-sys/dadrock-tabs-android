# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-08 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the **only canonical fresh-chat checkpoint** for the new Songsterr-inspired pipeline. Do not use the generic checkpoint. Do not resume archived V143/Gomyway implementation, reference tabs, scorer logic, or percentages unless the user explicitly asks.

## PRODUCT TARGET

Build an AI-first guitar/bass tab creator that can go from uploaded audio to a usable finished tab without a mandatory human correction step. Musical identity and timing correctness take priority over cosmetic/composite scores.

Preserve the existing `/ai-tab` journey:

**audio upload → AI analysis → analyzer metadata → technique/render events → watermarked preview PDF → PayPal/free-token unlock → full tab PDF → browser download + email delivery**

Fresh work replaces the transcription brain, not the customer/paywall/PDF journey.

## FOUNDATIONAL ORDER

**full-mixture audio → timing/measure map → structure-conditioned note evidence → rhythm/notation → playable tab → render metadata**

`structureMap` is first-class. Once accepted for a fixture, note inference must not rewrite tempo, meter, downbeats, measures, pickup, feel, or subdivisions.

Never silently change/drop detected MIDI or event identity to improve notation, fingering, path motion, ambiguity coverage, or legacy rendering.

## PROJECT / AUTHORIZATION BOUNDARY

- Work only on `songsterr-fresh-pipeline-v1`.
- Do not modify `main` or Production.
- Old `v143-contextual-prune-lobo` / Gomyway/V143 is archive/evidence only.
- Historical Gomyway/V143 scorer percentages are not fresh acceptance gates.
- No Modal/GPU/model-bearing inference, model source separation, professional scorer, training, or optimizer sweep without separate explicit user authorization.
- A generic “continue” is **not** authorization for model/GPU work.
- CPU-only reference-blind work on the explicitly authorized audio fixture is allowed.
- `songsterr_pipeline/` remains deterministic and process/network-free. Audio/DSP scripts live under `scripts/songsterr-fresh/` and pass validated JSON into the deterministic namespace.

## AUTHORIZED AUDIO FIXTURE

User explicitly authorized `gomywaymidterm` in `public/` on 2026-09-08.

Resolved exact fixture on `main`:
- `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Git blob SHA: `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- size: 3,464,988 bytes

Canaries download only that exact blob and verify `git hash-object`. The fresh branch does not merge/cherry-pick main.

The filename containing “gomyway” authorizes the audio fixture only. It does **not** authorize archived Gomyway/V143 code, scorer knowledge, reference tabs, or reference-based correction.

## FRESH DETERMINISTIC PIPELINE

Namespace: `songsterr_pipeline/`

- `structureMap.mjs` — first-class tempo/meter/feel/pickup/measures/downbeats/beats/subdivisions.
- `structureRhythmNotation.mjs` — map-driven starts/ends, ties, rests, syncopation, stable source identity.
- `contextualRhythmSpelling.mjs` — readable standard/dotted/triplet notation without altering musical identity.
- `playableShapeDecoder.mjs` — exact-MIDI legal shape candidates, unique strings, physical constraints, no pitch dropping.
- `fretboardPathOptimizer.mjs` — phrase-level deterministic path search over legal shapes.
- `structureFretboardPath.mjs` — applies path while protecting MIDI/timing/notation/provenance/rests.
- `freshEvaluator.mjs` — scoreless final-state diagnostics/failure codes; `compositeScore: null`.
- `productShellAdapter.mjs` — existing `/ai-tab` payload bridge; legacy structured rendering only when lossless; upstream evidence blockers fail closed from delivery.
- `deterministicPipeline.mjs` — structure + note events → notation → fretboard path → evaluator → product shell.
- `audioStructureAdapter.mjs` — validates full-mixture structure evidence and creates frozen `structureMap`.
- `structureIdentity.mjs` — deterministic frozen-structure identity.
- `noteEvidenceAdapter.mjs` — exact identity/slot verification, ambiguity preservation, exact MIDI promotion, no synthetic duration.
- `noteEvidenceDiagnostics.mjs` — descriptive-only scoreless ambiguity/duration inventory.
- `noteEvidenceEvaluator.mjs` — sole scoreless note-evidence acceptance boundary.
- `noteEventExposure.mjs` — separates pitch-resolved diagnostic events from role-accepted and complete-tab-eligible events without altering pitch/onset identity.

`tests/boundaryGuard.test.mjs` prevents deterministic source modules from importing archived/model-bearing/non-local runtime dependencies, making network calls, or launching processes.

## ACCEPTED / FROZEN REAL-AUDIO STRUCTURE

Accepted structure canary:
- run `34192662439`
- job `101953726302`
- commit `2a598f0f38d755faf0cd3d46543221253f1c8997`
- artifact `10042777518`
- digest `sha256:5ff3ce36f559bcc02efcc985a1fa06966576da0445896326e9408ada955e9b6f`

Frozen structure:
- identity `fnv1a32:2f493225`, canonicalLength 19653
- duration ~210.67465 s
- 4/4, moderate meter confidence ~0.5676
- pickup/first downbeat ~0.65016 s, moderate confidence ~0.5300
- straight feel confidence ~0.6519
- tempo confidence ~0.8107
- 113 measure-local tempo segments, 115 measures
- 449 observed beats evaluated
- beat-grid MAE ~7.14 ms
- RMSE ~10.63 ms
- max ~58.05 ms
- structure acceptance `true`, failure reasons `[]`

The earlier flat one-BPM map was rejected (~83 ms MAE / ~101 ms RMS / ~228 ms max). The measure-local map is frozen. Moderate meter/downbeat uncertainty remains attached; no reference is allowed to make it appear more certain.

## CPU NOTE-EVIDENCE BOUNDARY

Invariant rules:
- exact frozen `structureIdentity` must match;
- analyzer timing slots are independently recomputed against frozen structure;
- ambiguity/no-candidate evidence stays explicit;
- duplicate MIDI candidates at one onset are rejected;
- missing duration remains unresolved;
- duration may be populated only by the dedicated release-evidence stage;
- analyzer capabilities survive adaptation;
- model/GPU/legacy provenance is recorded honestly;
- model/GPU authorization is execution policy, not a musical score.

Current analyzer declares:
- `roleRelevanceResolved: false`
- `polyphonyResolved: false`
- `instrumentIsolation: none`
- confidence is heuristic, not calibrated probability.

### Event exposure contract

`noteEventExposure.mjs` exposes three separate surfaces:
- `pitchResolvedEvents` — local exact-pitch selections retained for diagnostics/downstream mechanical checks;
- `roleAcceptedEvents` — only exposed when `roleRelevanceResolved === true`;
- `completeTabEligibleEvents` — only exposed when role is resolved **and** `noteEvidenceEvaluator` accepts complete-tab evidence.

Current exact-fixture result:
- pitch-resolved events: **139**
- role-accepted guitar events: **0**
- complete-tab/customer-eligible events: **0**

This is deliberate. A locally unambiguous MIDI pitch is **not** automatically represented as a guitar event when the full mixture has no instrument isolation.

Important commit:
- `8143299b1ac76687d2ccc66ac38a6a86f4e47c88` — note-event exposure contract/tests.

## GUARDED CPU PITCH BASELINE — V4

Current analyzer:
`scripts/songsterr-fresh/analyze_structure_conditioned_notes.py`

Current contract:
`songsterr-fresh-cpu-note-evidence-v4`

Important commit:
- `62cda5baa7bf179347855f1215d5b29fd9f52733` — make pitch analyzer duration-free.

Properties:
- CPU/reference-blind
- frozen-structure-conditioned
- ±12-semitone CQT guard around guitar playable range
- playable guitar range 40–88
- analysis range 28–100
- no model/GPU/source separation
- **no duration estimation at all**
- `durationResolution: 'none'`
- no onset may leave this stage with `durationSeconds` or `sourceEnd`
- `diagnostics.durationEvidence.authority: 'none-in-pitch-analyzer'`
- `resolvedCount: 0`

Real fixture facts:
- onsets: **492**
- candidates: **1,130**
- unambiguous local pitch selections: **139**
- ambiguous: **353**
- no-candidate: **0**
- pitch-unambiguous rate: **28.25%**

Important unresolved quality signal:
- MIDI 40 appears in **97/139** local selections (~69.8%).
- MIDI 40 is also top candidate on 172/492 onsets (~35.0%).
- This is not a CQT transform-edge artifact anymore.
- It must **not** be interpreted as 97 confirmed guitar E2 notes because role relevance is unresolved in the full mixture.

## ROLE-BOUNDARY DIAGNOSTIC — V2 PROVEN

Script:
`scripts/songsterr-fresh/inspect_role_boundary_evidence.py`

Contract:
`songsterr-fresh-role-boundary-inspection-v2`

Important commit:
- `f560c30ea0dc8a9c4ca85093399158b47544fb92` — codifies frozen-structure/repetition/candidate diagnostics and CI identity proof.

Properties:
- CPU/reference-blind and structure-frozen;
- descriptive only: `descriptiveOnly: true`;
- cannot own classification: `changesClassification: false`;
- no pitch substitution/deletion;
- validates the exact structure identity before inspection;
- maps lower-boundary selections back to accepted frozen measure/beat/subdivision slots;
- reports same-pitch reattack spacing and second-candidate relationships;
- CI compares every onset before/after inspection as `(onsetId, classification, selectedMidi, candidate MIDI list)` and fails on any difference.

Exact-fixture reproducible facts for the 97 selected MIDI-40 events:
- all **97/97** map to the frozen structure;
- **92/97** are exact beat-start subdivisions;
- they span **56** unique measures;
- **56/97** have multiple playable pitch candidates;
- **+12 semitones** is the most common second-candidate interval;
- same-pitch reattack histogram contains the expected ~**0.46 s** and ~**0.93 s** bins;
- with a sub-playable guard-range local peak above the -18 dB floor: **27**;
- without one: **70**;
- strongest lower guard MIDI among those 27 spans 32–38, concentrated at 35;
- E2 minus strongest lower guard peak remains approximately:
  - mean ~9.40 dB
  - median ~9.12 dB
  - p10 ~4.49 dB
  - p90 ~14.30 dB
  - min ~1.15 dB
  - max ~14.59 dB

Identity/classification invariant proof passed on the exact fixture: **no onset ID, classification, selected MIDI, or candidate MIDI list changed.**

Decision remains: **do not add a simplistic lower-guard demotion rule and do not relabel MIDI 40 as bass.** These observations establish role uncertainty, not instrument identity.

## SINGLE DURATION AUTHORITY — HARDENED

Pitch analyzer v4 is intentionally duration-free. The sole active duration-evidence stage is:
`scripts/songsterr-fresh/estimate_selected_pitch_releases.py`

Contract:
`songsterr-fresh-cpu-spectral-release-evidence-v2`

It uses selected-pitch sustained spectral decay and treats same-pitch reattack as censor-only. It never invents duration from the next generic onset.

Exact real result:
- attempted local pitch selections: **139**
- resolved durations: **103**
- unresolved: **36**
- resolution rate: **74.10%**
- unresolved reasons:
  - 33 `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
  - 3 `NO_CLEAR_SUSTAINED_SPECTRAL_RELEASE`
- same-pitch reattack censor count: 104
- mean resolved duration ~0.492 s
- median ~0.302 s
- max ~3.344 s
- mean heuristic duration confidence ~0.979
- next onset used as duration: false

Final adapted evidence correctly reports **103** duration-resolved local pitch events, not the previous misleading 122 produced when duration was estimated twice.

Intrinsic single-authority hardening is complete:
- commit `dd676d68e2188103e242eb9e7258adee923cb8a0` — release estimator rejects any non-null upstream `durationSeconds` or `sourceEnd` with `RELEASE_EVIDENCE_REQUIRES_DURATION_FREE_INPUT`;
- commit `dab66b7aba0657628ca31ebdba413758bd54bde2` — exact-fixture CI adds a negative proof that pre-filled duration/end input fails and produces no output;
- release diagnostics declare `soleDurationAuthority: true` and `requiresDurationFreeInput: true`.

The v2 role-diagnostic canary reran the duration guard unchanged and again produced **103 resolved / 36 unresolved**.

Do not reintroduce a second duration estimator or relax the duration-free input guard without a justified architectural change.

## SCORELESS NOTE-EVIDENCE ACCEPTANCE

`noteEvidenceDiagnostics.mjs` is descriptive only. `noteEvidenceEvaluator.mjs` is the sole acceptance owner.

Current exact-fixture complete-tab blockers:
- `ROLE_RELEVANCE_UNRESOLVED`
- `POLYPHONY_UNRESOLVED`
- `PITCH_EVIDENCE_UNRESOLVED`
- `DURATION_EVIDENCE_INCOMPLETE`

`compositeScoreDefined: false`; `compositeScore: null`.

No provisional full-mixture evidence is customer-deliverable.

## LATEST EXACT-FIXTURE REAL CANARY

Workflow:
`.github/workflows/songsterr-fresh-gomyway-midterm-note-evidence-canary.yml`

Latest successful run:
- run **`34307605651`**
- job **`102327436340`**
- tested commit **`f560c30ea0dc8a9c4ca85093399158b47544fb92`**
- conclusion **success**
- artifact **`10087249463`**
- artifact name `songsterr-fresh-gomyway-midterm-note-evidence`
- artifact size 476,899 bytes
- digest **`sha256:1eab46656446bfaafde9884dfff5b8bf1671b4b48c293fa4cf5af3938e193ee5`**

The workflow passed every guarded step:
- exact authorized fixture blob verification;
- accepted frozen structure rebuild and identity check;
- duration-free CPU pitch analysis;
- role-boundary v2 descriptive inspection;
- semantic identity/classification non-mutation proof;
- negative proof that the release stage rejects pre-filled duration/end evidence;
- conservative release evidence;
- note-evidence adaptation;
- deterministic pipeline fail-closed delivery proof;
- full deterministic suite.

Real diagnostic pipeline summary remains:
- source/pitch-resolved events exercised mechanically: **139**
- role-accepted events: **0**
- complete-tab/customer-eligible events: **0**
- exact MIDI preserved: **139/139**
- durations resolved: **103**
- unresolved duration: **36**
- fretboard path resolves for the provisional diagnostic subset
- raw integrity passed: false
- downstream failures:
  - `UNRESOLVED_DURATION`: 36
  - `UNRESOLVED_RHYTHM_SPELLING`: 18
- upstream evidence ready: false
- rawResultReady: false
- deliveryReady: false
- structuredRenderEligible: false

This is the desired fail-closed behavior: exact pitch evidence remains inspectable without being mislabeled as accepted guitar transcription.

## CURRENT DETERMINISTIC TEST BASELINE

Latest exact-audio canary run **`34307605651`**, job **`102327436340`**, reran the deterministic suite at commit `f560c30ea0dc8a9c4ca85093399158b47544fb92`.

TAP:
- tests: **96**
- pass: **96**
- fail: **0**
- cancelled: **0**
- skipped: **0**
- todo: **0**

## CURRENT ENGINEERING DECISION / NEXT STEP

Completed CPU/reference-blind hardening milestones:
1. frozen structure contract and identity;
2. duration-free guarded pitch analyzer;
3. event-exposure separation: pitch-resolved vs role-accepted vs customer-eligible;
4. sole duration authority plus intrinsic rejection of pre-filled durations;
5. descriptive-only role-boundary v2 diagnostics tied directly to the frozen structure;
6. exact-fixture CI proof that role inspection cannot mutate onset/classification/selected-MIDI/candidate-MIDI identity;
7. exact authorized fixture and full deterministic suite green with exposure **139 / 0 / 0** and duration split **103 / 36**.

Current evidence does **not** justify a CPU heuristic that assigns instrument role or polyphony. In particular, the MIDI-40 repetition/beat/candidate evidence is useful as a warning signal but does not prove bass identity and must not be used to rewrite MIDI.

The next major capability jump is true **role/instrument separation plus polyphonic note inference**. A model/GPU/source-separation-model stage still requires **separate explicit user authorization** before dispatch. Until that authorization exists, preserve the current fail-closed boundary rather than fabricating role certainty from full-mixture heuristics.

## NON-NEGOTIABLES

- Canonical checkpoint/branch above remain authoritative.
- Frozen structure precedes note placement and cannot be rewritten downstream.
- Never silently alter detected MIDI/event identity.
- Never drop pitches merely to satisfy fingering/path/legacy rendering.
- Preserve existing `/ai-tab` preview → unlock → full PDF → email/download flow.
- No `main`/Production changes.
- No accidental Modal/GPU/model/professional-scorer/training activity.
- Real-audio work stays inside the exact authorized fixture.
- Archived V143/Gomyway implementation remains untouched unless the user explicitly asks to resume it.
- Keep this checkpoint updated after every meaningful milestone.
