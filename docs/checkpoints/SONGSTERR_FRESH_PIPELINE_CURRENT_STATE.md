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

Current invariant rules:
- exact frozen `structureIdentity` must match;
- analyzer timing slots are independently recomputed against frozen structure;
- ambiguity/no-candidate evidence stays explicit;
- duplicate MIDI candidates at one onset are rejected;
- missing duration remains unresolved;
- explicit duration/end is preserved only when supplied by evidence;
- analyzer capabilities survive adaptation;
- model/GPU/legacy provenance is recorded honestly;
- model/GPU authorization is execution policy, not a musical score.

Current analyzer declares:
- `roleRelevanceResolved: false`
- `polyphonyResolved: false`
- `instrumentIsolation: none`
- confidence is heuristic, not calibrated probability.

## GUARDED CPU PITCH BASELINE

Latest pitch baseline uses a ±12-semitone CQT analysis guard around the playable range so MIDI 40 is not the transform boundary.

Real fixture facts:
- onsets: **492**
- candidates: **1,130**
- unambiguous pitch selections: **139**
- ambiguous: **353**
- no-candidate: **0**
- pitch-unambiguous rate: **28.25%**
- playable guitar range: 40–88
- analysis range: 28–100
- source separation: none; HPSS only
- model/GPU/legacy scorer: false

Important unresolved quality signal:
- MIDI 40 appears in **97/139** unambiguous pitch selections (~69.8%).
- This is not a CQT-edge artifact anymore.
- It must **not** be interpreted as 97 confirmed guitar E2 notes because role relevance is unresolved in the full mixture.

The 97 MIDI-40 selections are highly repetitive in time:
- common same-pitch reattack gaps are about 0.46 s and 0.93 s, near one/two beats at the detected tempo;
- 56/97 have at least one additional playable pitch candidate;
- common second-candidate interval is +12 semitones (36 cases), with other intervals including 24, 11, 9, 7, etc.

This supports a **role-unresolved** interpretation. It does not prove those events are bass, and it does not justify blanket MIDI demotion or substitution.

## ROLE-BOUNDARY DIAGNOSTIC — LATEST REAL CANARY

New descriptive-only script:
`scripts/songsterr-fresh/inspect_role_boundary_evidence.py`

Commits:
- `df4335ce6dcdbf02916117ba78aea5cb4aa9916f` — diagnostic-only guard-range inspection.
- `39ddf6e626ef0482a0195c26f8314e2ecba03aa3` — wire inspection into exact-fixture canary.

Latest completed canary:
- run **`34222891519`**
- job **`102049950148`**
- tested commit `39ddf6e626ef0482a0195c26f8314e2ecba03aa3`
- conclusion **success**
- artifact **`10054533664`**
- artifact digest `sha256:8c173c11451aea5d477d2e39de651db5506565f03029ac1d53259eca968ae900`

Role-boundary result for the 97 selected MIDI-40 events:
- with a lower guard-range local peak above current -18 dB floor: **27**
- without one: **70**
- strongest lower guard MIDI among those 27 is concentrated around 35–37 but spans 32–38
- E2 minus strongest lower-guard peak level:
  - mean ~9.40 dB
  - median ~9.12 dB
  - p10 ~4.49 dB
  - p90 ~14.30 dB
  - min ~1.15 dB
  - max ~14.59 dB

Decision: **do not add a simplistic lower-guard demotion rule.** It explains only 27/97 suspicious boundary selections and would not resolve instrument role for the other 70.

## CPU RELEASE / DURATION EVIDENCE

Dedicated script:
`scripts/songsterr-fresh/estimate_selected_pitch_releases.py`

Latest dedicated release-stage facts:
- attempted pitch-unambiguous events: 139
- resolved: **103**
- unresolved: **36**
- resolution rate ~74.1%
- unresolved reasons:
  - 33 `NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK`
  - 3 `NO_CLEAR_SUSTAINED_SPECTRAL_RELEASE`
- same-pitch reattack censor count: 104
- mean resolved duration ~0.492 s
- median ~0.302 s
- max ~3.344 s
- next onset is never used as invented duration
- same-pitch reattack is censor-only
- confidence is heuristic.

Important architecture issue discovered: the pitch analyzer v3 also contains its own selected-pitch release estimator, so duration is currently estimated twice. Final adapted evidence therefore reports 122 duration-resolved events even though the dedicated stage itself resolves 103. This duplication is **not accepted as the final architecture**.

Next deterministic cleanup: make the pitch analyzer pitch-only again and make `estimate_selected_pitch_releases.py` the sole duration authority. Do not merge conflicting duration estimates.

## SCORELESS NOTE-EVIDENCE ACCEPTANCE

`noteEvidenceDiagnostics.mjs` is descriptive only. `noteEvidenceEvaluator.mjs` is the sole acceptance owner.

Current complete-tab blockers remain independent:
- `ROLE_RELEVANCE_UNRESOLVED`
- `POLYPHONY_UNRESOLVED`
- `PITCH_EVIDENCE_UNRESOLVED`
- `DURATION_EVIDENCE_INCOMPLETE`
- plus contract/integrity reasons when applicable.

`compositeScoreDefined: false`; `compositeScore: null`.

Latest real pipeline canary intentionally fails closed:
- pitch-resolved source events exercised downstream: 139
- exact MIDI preserved: 139/139
- fretboard path resolves for that provisional subset
- upstream evidence accepted: false
- raw integrity: false while duration/rhythm evidence incomplete
- `deliveryReady: false`
- `structuredRenderEligible: false`

No provisional full-mixture evidence is customer-deliverable.

## CURRENT DETERMINISTIC TEST BASELINE

Latest branch-wide deterministic proof inside real canary run `34222891519`:
- tests: **92**
- pass: **92**
- fail: **0**
- cancelled: **0**
- skipped: **0**
- todo: **0**

This supersedes the stale 91/91 checkpoint value.

## CURRENT ENGINEERING DECISION

The next permitted CPU/reference-blind work is:
1. distinguish **pitch-resolved provisional events** from **role-accepted guitar/bass events** in the clean contract;
2. while `roleRelevanceResolved:false`, no event may be represented as customer-eligible guitar/bass merely because its pitch is locally unambiguous;
3. remove the duplicate duration estimator from the pitch analyzer;
4. keep the dedicated conservative release estimator as sole duration authority;
5. rerun the exact authorized fixture and the full deterministic suite;
6. preserve every candidate and exact selected MIDI; do not re-label E2 as bass or substitute another pitch without evidence.

The next large capability jump after this CPU cleanup is true role/instrument separation + polyphonic note inference. A model/GPU/source-separation-model stage still requires **separate explicit user authorization** before dispatch.

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
