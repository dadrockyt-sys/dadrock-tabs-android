# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-08 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the **only canonical fresh-chat checkpoint** for the new Songsterr-inspired pipeline. Do not use the generic checkpoint. Do not resume archived V143/Gomyway implementation or scoring unless the user explicitly asks.

## PRODUCT TARGET

Build an AI-first guitar/bass tab creator that can go from uploaded audio to a usable finished tab without a mandatory human correction step. Musical identity and timing correctness take priority over cosmetic/composite scores.

Preserve the existing `/ai-tab` journey:

**audio upload → AI analysis → analyzer metadata → technique/render events → watermarked preview PDF → PayPal/free-token unlock → full tab PDF → browser download + email delivery**

Fresh work replaces the transcription brain, not the product/paywall/PDF journey.

## FOUNDATIONAL ORDER

**full-mixture audio → timing/measure map → structure-conditioned note evidence → rhythm/notation → playable tab → render metadata**

`structureMap` is first-class. Once accepted for a fixture, note inference must not rewrite tempo, meter, downbeats, measures, pickup, feel, or subdivisions.

Never silently change/drop detected MIDI or event identity to improve notation, fingering, path motion, or legacy rendering.

## PROJECT BOUNDARY

- Work only on `songsterr-fresh-pipeline-v1`.
- Do not modify `main` or Production.
- Old `v143-contextual-prune-lobo` / Gomyway/V143 code is archive/evidence only.
- Historical Gomyway/V143 scorer percentages are not fresh acceptance gates.
- No Modal/GPU/model-bearing inference, professional scorer, training, or optimizer sweep without separate explicit authorization.
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
- `freshEvaluator.mjs` — scoreless raw diagnostics/failure codes; `compositeScore: null`.
- `productShellAdapter.mjs` — maps clean state into existing `/ai-tab`; legacy structured rendering only when lossless.
- `deterministicPipeline.mjs` — structure + note events → notation → fretboard path → evaluator → product shell.
- `audioStructureAdapter.mjs` — validates full-mixture structure evidence and creates frozen `structureMap`.
- `structureIdentity.mjs` — deterministic frozen-structure identity.
- `noteEvidenceAdapter.mjs` — verifies exact structure identity/slots, preserves ambiguity, promotes only explicitly unambiguous top MIDI, and never fabricates duration.
- `noteEvidenceDiagnostics.mjs` — scoreless note-evidence completeness/ambiguity diagnostics and explicit no-human-correction blockers.

`tests/boundaryGuard.test.mjs` prevents the deterministic namespace from importing archived/model-bearing/non-local runtime dependencies, making network calls, or launching processes.

## ACCEPTED / FROZEN REAL-AUDIO STRUCTURE

Scripts:
- `scripts/songsterr-fresh/analyze_full_mixture_structure.py`
- `scripts/songsterr-fresh/build_structure_map.mjs`

Workflow:
`.github/workflows/songsterr-fresh-gomyway-midterm-structure-canary.yml`

Accepted run:
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

The earlier flat one-BPM map was rejected despite technical execution because alignment was ~83 ms MAE / ~101 ms RMS / ~228 ms max. The measure-local map is the accepted/frozen timing source.

The moderate 4/4/downbeat uncertainty stays attached. No reference is allowed to make it appear more certain.

## CPU NOTE-EVIDENCE BOUNDARY

Important commits:
- `48a00cf40c22a6ad4b80a94ac248e448cd841937` — frozen structure identity.
- `576887ceaba8be3f33b7c569608946d58a9ce6d6` — note-evidence adapter.
- `b348f12b1e8b2f741481839ee9336055b47607bf` — first six note-evidence boundary tests.
- `e6affb7a268f53f8e900b12dffa7f86807808723` — frozen structure → note-evidence context.
- `bf01bdd339a7159057849843b0205f46312ee914` — independently verify analyzer timing slots and remove synthetic duration inference.
- `8a0e5d4b8b4a9d33b21d43a8c649c399a8a068a2` — slot/duration boundary tests.
- `01e8f86e063f30b89528134381ebf27aa3c677c8` — preserve actual model/GPU/legacy provenance.
- `eeb1887c2b855261f105bc6658db8d82804fd525` — CPU full-mixture harmonic-CQT note analyzer.
- `e49614e2f16ffbbc38bb61e358b4919cdedd5c86` — CPU note-evidence validator.
- `5d8146559debd3557c1f8662f4a9f7b0f94f7951` — first real note-evidence canary workflow.
- `a2f7d373e50c874e1853f7f66087becbc86bd03b` / `ec661bc4937d2773e7b5787b7e19834f722fc17a` — raw note-evidence diagnostics + explicit finite-duration fix.
- `a51f79ffb34bdf0d63908fb48f193b72208165bc` — diagnostics tests.
- `2204a7cc2b0b5805e37c40f9f9a2845ec82e0d55` — real promoted-evidence deterministic pipeline runner.
- `e742a2fb833b49888f73690b369ef4cbefcf780c` — fail-closed real-audio note-evidence integration workflow.

Boundary rules:
- exact frozen `structureIdentity` must match;
- nearest timing slot is independently recomputed from the frozen map;
- ambiguity/no-candidate evidence stays explicit;
- only explicitly `unambiguous` highest-confidence MIDI is promoted;
- duplicate MIDI candidates in one onset are rejected;
- missing duration remains unresolved;
- explicit duration/end is preserved only when actually supplied;
- actual model/GPU/legacy provenance is recorded, never falsely stamped.

## REAL-AUDIO NOTE EVIDENCE — BASELINES

### First v1 baseline
Run `34219793694`, job `102039951929`, commit `5d8146559debd3557c1f8662f4a9f7b0f94f7951`, artifact `10053290067`.

- onsets 492
- candidates 1,325
- unambiguous 209
- ambiguous 283
- no-candidate 0
- unambiguous rate ~42.48%
- promoted provisional events 209
- explicit duration evidence 0
- structure displacement mean ~10.96 ms, max ~58.05 ms

This was a technical boundary pass, not a transcription acceptance.

### Current guarded-range v2 baseline + fail-closed integration
Latest successful run:
- run `34220474993`
- job `102042151346`
- tested commit `e742a2fb833b49888f73690b369ef4cbefcf780c`
- artifact ID `10053569332`
- artifact size 205,028 bytes
- artifact digest `sha256:1c52a35e733ba7a9f3945061d82c7377cb1b168c7bb9aa36831b8efee893ec8f`

Analyzer contract: `songsterr-fresh-cpu-note-evidence-v2`.

Current raw evidence:
- onsets: **492**
- candidates: **1,130**
- unambiguous: **139**
- ambiguous: **353**
- no-candidate: **0**
- unambiguous rate: **28.25%**
- promoted provisional events: **139**
- explicit duration evidence: **0**
- analysis MIDI range: 28–100
- playable guitar range: 40–88
- spectral guard: 12 semitones
- source separation: none; harmonic/percussive filtering only
- model/GPU/legacy scorer: false

The lower promotion rate versus v1 is intentionally more conservative; do not treat it as an accuracy regression without reference-independent evidence.

Pitch distribution needs further reference-blind scrutiny: 97/139 promoted events are MIDI 40, with additional concentration at MIDI 42/43. This may indicate playable-boundary/source-role contamination in the full mixture. It is **not** being declared wrong from reference knowledge.

Scoreless evidence diagnostics for the current run:
- unresolved role evidence: 353
- single-candidate ambiguous: 96
- competing-candidate ambiguous: 257
- harmonic-relation ambiguous: 61
- octave-relation ambiguous: 57
- close-interval ambiguous: 80
- promoted with explicit duration: 0
- promoted missing duration: 139
- blockers:
  - `UNRESOLVED_ROLE_NOTE_EVIDENCE`
  - `PROMOTED_EVENTS_MISSING_DURATION_EVIDENCE`
- `noHumanCorrectionReady: false`
- no composite score is defined.

Top/second competing intervals are varied (including 7, 9, 10, 12 semitones and others), so competitors cannot safely be collapsed as octave/harmonic artifacts.

### REAL DETERMINISTIC PIPELINE FAIL-CLOSED PROOF

The same run fed only the 139 explicitly promoted provisional MIDI events through the full deterministic pipeline against frozen structure:
- source events: 139
- final events: 139
- exact MIDI preserved: 139/139
- fretboard path resolved: true
- unresolved durations: 139
- raw integrity: false
- evaluator failure: `UNRESOLVED_DURATION` count 139
- `deliveryReady: false`
- `structuredRenderEligible: false`

This is the intended behavior: incomplete real evidence cannot become a customer-deliverable tab merely because pitch/fretboard processing succeeds.

## CURRENT DETERMINISTIC TEST BASELINE

Latest branch-wide proof from the real-audio fail-closed run:
- run `34220474993`
- job `102042151346`
- commit `e742a2fb833b49888f73690b369ef4cbefcf780c`

TAP:
- tests **81**
- pass **81**
- fail **0**
- cancelled **0**
- skipped **0**
- todo **0**

This supersedes the prior 77/77 baseline.

## CURRENT ENGINEERING BOUNDARY / NEXT CPU STEP

The timing map is accepted/frozen. CPU pitch evidence is structurally integrated and safely fails closed, but it is not yet a complete or accepted guitar transcription.

Next CPU/reference-blind work may include:
1. conservative selected-pitch decay/release duration evidence; never use `next onset = note duration` as a shortcut;
2. preserve unresolved duration when a release is unclear;
3. evaluate low playable-boundary concentration / role contamination without a reference tab;
4. improve ambiguity diagnostics using temporal continuity and harmonic conflict while preserving every candidate;
5. rerun the real fail-closed pipeline and only relax delivery blockers when raw evidence genuinely resolves them.

A model/GPU/source-separation-model stage remains outside current authorization and requires separate explicit authorization.

## NON-NEGOTIABLES

- Canonical checkpoint/branch above remain authoritative.
- Frozen structure precedes note placement and cannot be rewritten downstream.
- Never silently alter detected MIDI/event identity.
- Never drop pitches merely to satisfy fingering/path/legacy rendering.
- Preserve the existing `/ai-tab` preview → unlock → full PDF → email/download flow.
- No main/Production changes.
- No accidental Modal/GPU/model/professional-scorer/training activity.
- Real-audio work stays inside the exact authorized fixture.
- Keep this checkpoint updated after every meaningful milestone.
