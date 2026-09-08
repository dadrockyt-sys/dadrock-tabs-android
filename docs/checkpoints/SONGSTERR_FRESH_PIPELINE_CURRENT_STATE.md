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

- `structureMap.mjs` — tempo/meter/feel/pickup/measures/downbeats/beats/subdivisions with confidence/provenance.
- `structureRhythmNotation.mjs` — map-driven starts/ends, ties, rests, syncopation, stable source identity.
- `contextualRhythmSpelling.mjs` — readable standard/dotted/triplet notation without altering musical identity.
- `playableShapeDecoder.mjs` — exact-MIDI legal shape candidates, unique strings, physical constraints, no pitch dropping.
- `fretboardPathOptimizer.mjs` — phrase-level deterministic path search over legal shapes.
- `structureFretboardPath.mjs` — applies the path while protecting MIDI/timing/notation/provenance/rests.
- `freshEvaluator.mjs` — scoreless final-state diagnostics/failure codes; `compositeScore: null`.
- `productShellAdapter.mjs` — maps clean state into existing `/ai-tab`; legacy structured rendering only when lossless; upstream evidence blockers fail closed from delivery.
- `deterministicPipeline.mjs` — structure + note events → notation → fretboard path → evaluator → product shell.
- `audioStructureAdapter.mjs` — validates full-mixture structure evidence and creates frozen `structureMap`.
- `structureIdentity.mjs` — deterministic frozen-structure identity.
- `noteEvidenceAdapter.mjs` — verifies exact structure identity/slots, preserves ambiguity, promotes only explicitly unambiguous top MIDI, never fabricates duration, and now preserves analyzer capability declarations/raw diagnostics.
- `noteEvidenceDiagnostics.mjs` — **descriptive-only** scoreless inventory of ambiguity/harmonic/interval/duration evidence. It does not own readiness or acceptance.
- `noteEvidenceEvaluator.mjs` — **sole note-evidence acceptance boundary**. It is scoreless and uses independent failure reasons for role relevance, polyphony, unresolved pitch, duration completeness, and contract integrity.

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
- observed measure tempo preserved: true
- 113 tempo segments, 115 measures
- 449 observed beats evaluated
- beat-grid MAE ~7.14 ms
- RMSE ~10.63 ms
- max ~58.05 ms
- structure acceptance `true`, failure reasons `[]`

The earlier flat one-BPM map was rejected because alignment was ~83 ms MAE / ~101 ms RMS / ~228 ms max. The measure-local map is the accepted/frozen timing source.

The moderate 4/4/downbeat uncertainty stays attached. No reference is allowed to make it appear more certain.

## CPU NOTE-EVIDENCE BOUNDARY

Important recent commits:
- `48a00cf40c22a6ad4b80a94ac248e448cd841937` — frozen structure identity.
- `576887ceaba8be3f33b7c569608946d58a9ce6d6` — note-evidence adapter.
- `bf01bdd339a7159057849843b0205f46312ee914` — verify analyzer timing slots / remove synthetic duration inference.
- `01e8f86e063f30b89528134381ebf27aa3c677c8` — preserve actual model/GPU/legacy provenance.
- `5de5a247f8a1b136ad259d2eaedc50565eb4416c` — guarded-range CPU pitch analyzer v2; removes playable-range CQT edge bias.
- `2fd74862e66898f9d7505da282ee0f43542cdbc9` — initial scoreless note-evidence evaluator.
- `83202778cc1ba25e5e5b0fd0b5d8929f0d485e73` — analyzer explicitly declares unresolved CPU capabilities.
- `6936e671f13db38662c822d3b655a9be2eb35cf4` — adapter preserves capabilities and raw analyzer diagnostics.
- `130dd082bd998f0d6cb0a21992161201f67bde27` / `1185eba63ff3bb616f17df9fc3938ece852a1a72` — diagnostics refactored to descriptive-only inventory + tests.
- `90336f88cc5d3cc0a91b10da450564a1d277b264` — evaluator becomes sole acceptance owner.
- `5841697b92c1d218e90647f03fb85d992ee749af` — real deterministic canary now gates through evaluator.
- `2ad2779e1e6c2c07fb32f6347e3e9124354faade` — workflow assertions use authoritative evaluator.
- `3d3e74dffbb9dcf9c1697489d3a69fbf1d89f174` — capability/diagnostic preservation test.
- `7690bb9b69911bb4016f2a12e2545dad8aa7179c` / `9a8150570e68d881a6406804f0c111afcd3997a8` — execution authorization kept outside musical evaluator + test.
- `c2f7a3d4a7154abbe06174e1e4c58aa815030b64` — conservative selected-pitch spectral release evidence script.
- `8e6e824c7bc6c79564be5db8e53bce2764b2f020` — workflow adds CPU release-evidence canary.

Boundary rules:
- exact frozen `structureIdentity` must match;
- nearest timing slot is independently recomputed from frozen structure;
- ambiguity/no-candidate evidence stays explicit;
- duplicate candidate MIDI at one onset is rejected;
- missing duration remains unresolved;
- explicit duration/end is preserved only when supplied by evidence;
- analyzer capabilities are explicit and survive adaptation;
- model/GPU provenance is recorded honestly;
- whether a model/GPU execution is authorized is an execution-policy boundary, not a musical-quality failure reason inside the general evaluator.

## GUARDED CPU PITCH BASELINE — CURRENT MUSICAL EVIDENCE

Latest completed guarded/fail-closed baseline before release-duration experiment:
- run `34220474993`
- job `102042151346`
- commit `e742a2fb833b49888f73690b369ef4cbefcf780c`
- artifact `10053569332`
- digest `sha256:1c52a35e733ba7a9f3945061d82c7377cb1b168c7bb9aa36831b8efee893ec8f`

Pitch analyzer v2:
- onsets: **492**
- candidates: **1,130**
- unambiguous: **139**
- ambiguous: **353**
- no-candidate: **0**
- unambiguous rate: **28.25%**
- provisional promoted events: **139**
- explicit duration evidence at that stage: **0**
- analysis MIDI range: 28–100
- playable guitar range: 40–88
- spectral guard: 12 semitones
- source separation: none; HPSS only
- model/GPU/legacy scorer: false

The guard fix removed an actual playable-range boundary artifact and made the analyzer more conservative. It did **not** solve role relevance: 97/139 provisional promoted events remain MIDI 40 even though MIDI 40 is no longer the CQT analysis boundary. That concentration is genuine full-mixture low-frequency evidence and cannot honestly be labeled guitar versus bass with the current no-isolation CPU method.

Raw ambiguity facts from the guarded artifact:
- candidate-count distribution across 492 onsets: 1→150, 2→194, 3→71, 4→35, 5→13, 6→29
- multi-candidate onsets: 342
- octave-related competitor present on 131 multi-candidate onsets (~38.3%)
- top/second intervals include 12 semitones (97), 7 (37), 9 (31), 11 (24), 3 (22), 8 (22), plus others
- competing peaks cannot safely be collapsed into “harmonics”; some may be real chord tones

Therefore the current pitch schema still has unresolved **role relevance** and **polyphony**. Threshold relaxation is not an acceptable substitute.

## SCORELESS NOTE-EVIDENCE ACCEPTANCE

`noteEvidenceDiagnostics.mjs` is descriptive only. `noteEvidenceEvaluator.mjs` is the sole acceptance owner.

Current complete-tab failures are independent, not blended into a percentage:
- `ROLE_RELEVANCE_UNRESOLVED`
- `POLYPHONY_UNRESOLVED`
- `PITCH_EVIDENCE_UNRESOLVED`
- `DURATION_EVIDENCE_INCOMPLETE` when duration evidence remains incomplete
- plus contract/integrity reasons when applicable

`compositeScoreDefined: false`; `compositeScore: null`.

A future explicitly authorized model/GPU analyzer is not automatically a musical failure; authorization is enforced before execution. The CPU canary itself explicitly rejects unexpected model/GPU/legacy provenance.

## REAL DETERMINISTIC FAIL-CLOSED PROOF

The prior guarded run fed only the 139 provisional promoted MIDI events through the complete deterministic path against frozen structure:
- source events: 139
- final events: 139
- exact MIDI preserved: 139/139
- fretboard path resolved: true
- unresolved durations at that stage: 139
- raw integrity: false
- `deliveryReady: false`
- `structuredRenderEligible: false`

Current product-shell integration also supports an upstream note-evidence gate. Even if downstream MIDI/fretboard integrity is clean, failed upstream evidence keeps delivery disabled.

## CURRENT DETERMINISTIC TEST BASELINE

Latest branch-wide deterministic GitHub Actions proof:
- run `34221271087`
- job `102044696313`
- tested commit `9a8150570e68d881a6406804f0c111afcd3997a8`

TAP:
- tests **91**
- pass **91**
- fail **0**
- cancelled **0**
- skipped **0**
- todo **0**

This supersedes the previous 81/81 and 86/86 baselines.

Coverage now explicitly proves:
- analyzer capabilities/raw diagnostics survive adaptation;
- descriptive diagnostics do not own acceptance;
- evaluator is the sole scoreless note-evidence acceptance boundary;
- role/polyphony/pitch/duration blockers remain independent;
- product-shell upstream blockers fail closed from delivery;
- execution authorization is separate from musical evaluation.

## ACTIVE CPU RELEASE-EVIDENCE EXPERIMENT

Script:
`scripts/songsterr-fresh/estimate_selected_pitch_releases.py`

Purpose: add duration evidence only to already-unambiguous provisional MIDI events when that selected pitch shows a clear sustained spectral decay.

Rules:
- CPU-only and reference-blind;
- cannot create or change MIDI candidates;
- cannot rewrite frozen structure;
- **never** uses `next onset = note duration`;
- requires selected-pitch onset/floor contrast and sustained spectral drop;
- unresolved release remains unresolved;
- confidence is explicitly heuristic, not a calibrated probability;
- role relevance and polyphony stay unresolved regardless of duration coverage.

Current workflow run after adding this stage:
- run `34221520816`
- tested commit `8e6e824c7bc6c79564be5db8e53bce2764b2f020`
- status at this checkpoint: in progress

Do not claim its duration coverage until the run completes and artifact/log are inspected.

## CURRENT ENGINEERING BOUNDARY / NEXT DECISION

The clean CPU path has established:
1. accepted/frozen real-audio structure;
2. reference-blind guarded pitch candidates;
3. exact identity/timing handshakes;
4. ambiguity preservation;
5. sole scoreless acceptance gating;
6. fail-closed product delivery;
7. an active conservative spectral-release experiment.

Even if the release experiment improves duration coverage, current full-mixture CPU evidence still cannot truthfully resolve guitar-vs-bass role relevance or multi-pitch chord/polyphony decisions. Do not feed the provisional events to customers as a complete tab.

After finishing and recording the CPU release canary, the next material capability jump is likely role/instrument separation + polyphonic note inference. A model/GPU/source-separation-model stage requires **separate explicit user authorization** before dispatch.

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
