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

Previously observed descriptive facts for those 97 MIDI-40 selections:
- 92/97 fall on exact beat-start subdivisions;
- common same-pitch reattack gaps are about 0.46 s and 0.93 s, near one/two beats at the detected tempo;
- they span 56 measures;
- 56/97 have at least one additional playable pitch candidate;
- +12 semitones is the most common second-candidate interval among those events.

These observations support a **role-unresolved** interpretation. They do not prove those events are bass and do not justify blanket MIDI demotion/substitution. The next CPU-only task is to make these observations reproducible inside the role-boundary diagnostic and prove that diagnostic cannot change pitch/classification identity.

## ROLE-BOUNDARY DIAGNOSTIC

Script:
`scripts/songsterr-fresh/inspect_role_boundary_evidence.py`

Current v1 properties:
- descriptive only;
- no classification changes;
- no pitch substitution/deletion;
- inspects sub-playable guard peaks for lower-boundary MIDI 40 selections.

For the 97 MIDI-40 selections:
- with lower guard-range local peak above -18 dB floor: **27**
- without one: **70**
- strongest lower guard MIDI among those 27 spans 32–38, concentrated at 35
- E2 minus strongest lower guard peak:
  - mean ~9.40 dB
  - median ~9.12 dB
  - p10 ~4.49 dB
  - p90 ~14.30 dB
  - min ~1.15 dB
  - max ~14.59 dB

Decision: **do not add a simplistic lower-guard demotion rule.** It explains only 27/97 suspicious boundary selections and does not resolve instrument role for the other 70.

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

Verified exact-fixture proof:
- run **`34224308657`**
- job **`102054571754`**
- tested commit **`dab66b7aba0657628ca31ebdba413758bd54bde2`**
- conclusion **success**
- artifact **`10055091265`**
- digest **`sha256:0d2e4092e66764acb75a9de92beaf2ab58bdb8ad3c80df2cdb9fba10f61a31df`**
- event exposure remained **139 pitch-resolved / 0 role-accepted / 0 customer-eligible**
- duration split remained **103 resolved / 36 unresolved**
- deterministic suite remained **96/96**.

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
- run **`34224308657`**
- job **`102054571754`**
- tested commit **`dab66b7aba0657628ca31ebdba413758bd54bde2`**
- conclusion **success**
- artifact **`10055091265`**
- digest **`sha256:0d2e4092e66764acb75a9de92beaf2ab58bdb8ad3c80df2cdb9fba10f61a31df`**

Real diagnostic pipeline summary:
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

Latest branch-wide deterministic proof:
- run **`34223492248`**, job **`102051925490`** — 96/96 after event-exposure contract.
- latest exact-audio canary run **`34224308657`**, job **`102054571754`** independently reran the same suite and also passed **96/96**.

TAP:
- tests: **96**
- pass: **96**
- fail: **0**
- cancelled: **0**
- skipped: **0**
- todo: **0**

## CURRENT ENGINEERING DECISION / NEXT STEP

Permitted CPU/reference-blind work now:
1. duration single-authority hardening is complete; preserve it as an invariant;
2. deepen **descriptive-only** role diagnostics so beat-position/repetition/candidate-relationship observations are generated directly from the exact frozen structure and pitch evidence;
3. add CI proof that role inspection does not alter onset IDs, classifications, selected MIDI, or candidate MIDI identity;
4. rerun the exact authorized fixture and full deterministic suite; expected musical exposure remains 139 pitch-resolved / 0 role-accepted / 0 customer events and the 103/36 duration split unless evidence changes for a justified reason;
5. preserve every candidate and exact selected MIDI; do not relabel E2 as bass or substitute another pitch without evidence.

The next major capability jump is true role/instrument separation plus polyphonic note inference. A model/GPU/source-separation-model stage still requires **separate explicit user authorization** before dispatch.

## NON-NEGOTIABLES

- Canonical checkpoint/branch above remain authoritative.
- Frozen structure precedes note placement and cannot be rewritten downstream.
- Never silently alter detected MIDI/event identity.
- Never drop pitches merely to satisfy fingering/path/legacy rendering.
- Preserve existing `/ai-tab` preview → unlock → full PDF → email/download flow.
- No main/Production changes.
- No accidental Modal/GPU/model/professional-scorer/training activity.
- Real-audio work stays inside the exact authorized fixture.
- Keep this checkpoint updated after every meaningful milestone.
