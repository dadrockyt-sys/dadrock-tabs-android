# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-08 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

This is the **only canonical fresh-chat checkpoint** for the new Songsterr-inspired pipeline. Do not use the generic checkpoint for this project. Do not resume archived V143/Gomyway implementation or scoring unless the user explicitly asks.

## PRODUCT TARGET

Build an AI-first guitar/bass tab creator that can go from uploaded audio to a usable finished tab without a mandatory human correction step. Musical identity and timing correctness take priority over cosmetic or composite scores.

Preserve the existing `/ai-tab` customer journey:

**audio upload → AI analysis → analyzer metadata → technique/render events → watermarked preview PDF → PayPal/free-token unlock → full tab PDF → browser download + email delivery**

Fresh work replaces the transcription brain, not the customer/paywall/PDF journey.

## FOUNDATIONAL ORDER

Non-negotiable order:

**full-mixture audio → timing/measure map → structure-conditioned note evidence → rhythm/notation → playable tab → render metadata**

`structureMap` is first-class. Once accepted for a fixture, note inference must not rewrite tempo, meter, downbeats, measure boundaries, pickup, feel, or subdivisions.

Never silently change/drop detected MIDI or event identity to improve notation, fingering, path motion, or compatibility with a legacy renderer.

## PROJECT BOUNDARY

- Branch: `songsterr-fresh-pipeline-v1` only.
- Do not modify `main` or Production.
- Old `v143-contextual-prune-lobo` and Gomyway/V143 code are archive/evidence only.
- Historical Gomyway/V143 scorer percentages/gates are not fresh acceptance criteria.
- No Modal/GPU/model-bearing note inference, professional scorer, training, or optimizer sweep without separate explicit authorization.
- CPU-only reference-blind processing of the explicitly authorized audio fixture is allowed.
- `songsterr_pipeline/` remains deterministic and process/network-free; audio/DSP scripts live under `scripts/songsterr-fresh/` and pass validated JSON into the deterministic namespace.

## AUTHORIZED AUDIO FIXTURE

On 2026-09-08 the user explicitly authorized `gomywaymidterm` in the public folder.

Resolved exact fixture on `main`:
- path: `public/jimmy-paige-midterm-v1/gomyway-midterm-source.m4a`
- Git blob SHA: `4dd709e3fa177b4daeed71ca97f0199757729d4b`
- size: 3,464,988 bytes

The fresh branch does not merge/cherry-pick main. Canaries download only that exact public blob and verify `git hash-object` before analysis.

The filename containing “gomyway” authorizes the audio fixture only. It does **not** authorize archived Gomyway/V143 code, scorer knowledge, reference tabs, or reference-based correction.

## CURRENT FRESH DETERMINISTIC PIPELINE

Namespace: `songsterr_pipeline/`

- `structureMap.mjs` — tempo/meter/feel/pickup/measures/downbeats/beats/subdivisions with confidence/provenance and change-boundary validation.
- `structureRhythmNotation.mjs` — map-driven starts/ends, ties, rests, syncopation, displacement diagnostics, stable source identity.
- `contextualRhythmSpelling.mjs` — readable standard/dotted/triplet values while protecting musical identity.
- `playableShapeDecoder.mjs` — exact-MIDI legal shape candidates, unique strings, physical constraints, role-aware policies, no pitch dropping.
- `fretboardPathOptimizer.mjs` — deterministic phrase-level path search over legal shapes.
- `structureFretboardPath.mjs` — applies the path while protecting MIDI/timing/notation/provenance/rests.
- `freshEvaluator.mjs` — scoreless raw diagnostics and independent failure codes; `compositeScore: null`, legacy scorer import false.
- `productShellAdapter.mjs` — maps the clean result into the existing `/ai-tab` payload; legacy structured render projection is emitted only when lossless, otherwise complete text fallback is retained.
- `deterministicPipeline.mjs` — composes structure + note evidence → event/rhythm schema → contextual rhythm → fretboard path → evaluator → product-shell.
- `audioStructureAdapter.mjs` — validates full-mixture structure evidence and builds the frozen first-class map.
- `structureIdentity.mjs` — deterministic frozen-structure identity contract.
- `noteEvidenceAdapter.mjs` — validates reference-blind structure-conditioned pitch evidence, verifies exact frozen-structure identity and nearest structure slots, preserves ambiguous/no-candidate evidence, promotes only explicitly unambiguous top MIDI evidence, and never fabricates missing duration.

Isolation guard: `tests/boundaryGuard.test.mjs` fails if root fresh `.mjs` source imports archived/model/non-local runtime dependencies, performs network fetches, or launches processes.

## ACCEPTED/FROZEN REAL-AUDIO STRUCTURE

Structure scripts:
- `scripts/songsterr-fresh/analyze_full_mixture_structure.py`
- `scripts/songsterr-fresh/build_structure_map.mjs`

Structure canary:
`.github/workflows/songsterr-fresh-gomyway-midterm-structure-canary.yml`

Latest successful refined structure canary:
- run: `34192662439`
- job: `101953726302`
- tested commit: `2a598f0f38d755faf0cd3d46543221253f1c8997`
- artifact ID: `10042777518`
- artifact name: `songsterr-fresh-gomyway-midterm-structure`
- artifact digest: `sha256:5ff3ce36f559bcc02efcc985a1fa06966576da0445896326e9408ada955e9b6f`

Refined map:
- frozen structure identity: `fnv1a32:2f493225`
- duration: ~210.67465 s
- selected meter: 4/4, moderate confidence ~0.5676
- pickup / first detected downbeat: ~0.65016 s, moderate confidence ~0.5295
- straight feel confidence: ~0.6517
- tempo confidence: ~0.8116
- observed measure tempo preserved: true
- tempo segments: 113
- observed beats evaluated: 449
- beat-grid MAE: ~7.14 ms
- beat-grid RMSE: ~10.63 ms
- beat-grid max: ~58.05 ms
- structure acceptance: true
- failure reasons: `[]`

The earlier one-global-BPM map was rejected for freeze because it had ~83 ms MAE / ~101 ms RMS / ~228 ms max beat-grid miss. The measure-local tempo map reduced those errors by roughly 91% / 89% / 75% respectively.

### FREEZE DECISION

For this exact authorized fixture, the refined `structureMap` is **accepted and frozen** for downstream CPU/reference-blind note-evidence experiments.

The 4/4 meter and first-downbeat interpretation remain only moderate confidence. That uncertainty stays attached. No reference tab or archived knowledge may be used to make it appear more certain.

Downstream note evidence is not permitted to rewrite this accepted structure.

## CPU NOTE-EVIDENCE BOUNDARY

New files/commits:
- `48a00cf40c22a6ad4b80a94ac248e448cd841937` — frozen structure identity contract.
- `576887ceaba8be3f33b7c569608946d58a9ce6d6` — structure-conditioned note-evidence adapter.
- `b348f12b1e8b2f741481839ee9336055b47607bf` — initial six note-evidence boundary tests.
- `e6affb7a268f53f8e900b12dffa7f86807808723` — accepted/frozen structure → note-evidence context builder.
- `bf01bdd339a7159057849843b0205f46312ee914` — verify analyzer timing slots and remove synthetic duration inference.
- `8a0e5d4b8b4a9d33b21d43a8c649c399a8a068a2` — tests for slot verification and exact/unresolved duration evidence.
- `01e8f86e063f30b89528134381ebf27aa3c677c8` — preserve actual model/GPU/legacy execution provenance instead of stamping false values.
- `eeb1887c2b855261f105bc6658db8d82804fd525` — CPU-only full-mixture harmonic-CQT note-evidence analyzer.
- `e49614e2f16ffbbc38bb61e358b4919cdedd5c86` — CPU canary note-evidence validator.
- `5d8146559debd3557c1f8662f4a9f7b0f94f7951` — first frozen-structure real-audio note-evidence canary workflow.

Boundary behavior:
- exact `structureIdentity` must match the frozen map;
- analyzer-supplied nearest structure slots are recomputed/verified by the deterministic adapter;
- ambiguous and no-candidate onsets remain explicit;
- only explicitly `unambiguous` highest-confidence MIDI is promoted;
- duplicate MIDI candidates inside one onset are rejected;
- missing duration remains unresolved;
- duration/end are preserved only when explicitly supplied by evidence;
- adapter records actual model/GPU/legacy provenance rather than assuming false.

## CPU NOTE-EVIDENCE ANALYZER — FIRST BASELINE

Script:
`scripts/songsterr-fresh/analyze_structure_conditioned_notes.py`

Purpose: collect a conservative reference-blind baseline, not claim transcription accuracy.

Current v1 behavior:
- CPU-only;
- consumes the accepted/frozen structure context;
- hard-checks expected structure signature `fnv1a32:2f493225`;
- full-mixture onset detection;
- harmonic/percussive filtering only — **no instrument source separation**;
- role-conditioned CQT pitch range (first canary uses guitar MIDI 40–88);
- preserves up to six local pitch candidates per onset;
- confidence values are explicitly `heuristic-not-calibrated-probability`;
- strong competing pitch evidence stays ambiguous rather than forcing a note;
- no duration inference in this first baseline;
- no model, GPU, reference tab, or legacy V143 scorer.

Raw evidence is passed through `build_note_evidence.mjs`, which rejects model/GPU/legacy provenance for the current CPU-only canary before adapting it into the deterministic boundary.

## CURRENT TEST BASELINE

Branch-wide deterministic GitHub Actions proof after hardening note evidence:
- run: `34219737107`
- job: `102039769518`
- tested commit: `01e8f86e063f30b89528134381ebf27aa3c677c8`

Actual TAP result:
- tests: **77**
- pass: **77**
- fail: **0**
- cancelled: **0**
- skipped: **0**
- todo: **0**

The two tests added beyond the 75/75 note-evidence baseline prove:
1. an analyzer cannot claim a nearest timing slot that disagrees with the frozen `structureMap`;
2. explicit duration evidence is preserved exactly while missing duration remains unresolved with no synthetic duration.

## ACTIVE REAL-AUDIO NOTE CANARY

Workflow:
`.github/workflows/songsterr-fresh-gomyway-midterm-note-evidence-canary.yml`

Run started from commit `5d8146559debd3557c1f8662f4a9f7b0f94f7951`:
- run: `34219793694`
- job: `102039951929`

The workflow:
1. checks out only `songsterr-fresh-pipeline-v1`;
2. downloads and Git-blob-verifies the exact authorized audio;
3. decodes to mono 22.05 kHz WAV;
4. installs the same pinned CPU/librosa stack;
5. rebuilds the structure reference-blind and requires accepted/frozen context;
6. requires exact frozen signature `fnv1a32:2f493225`;
7. runs CPU-only guitar-range note evidence;
8. validates it through `noteEvidenceAdapter.mjs`;
9. reruns the deterministic suite;
10. uploads raw/adapted JSON artifacts.

At this checkpoint the note canary is still running. Do **not** claim its musical note result until the completed artifact/log has been inspected.

## CURRENT ENGINEERING BOUNDARY / NEXT DECISION

The exact authorized fixture has an accepted/frozen timing map and a hardened CPU note-evidence boundary.

Once the first note-evidence canary completes, inspect raw evidence before deciding what to do next. In particular, distinguish:
- workflow/contract success;
- evidence coverage;
- ambiguity rate;
- structure displacement;
- whether full-mixture harmonic CQT is useful enough to justify feeding any promoted events into `deterministicPipeline.mjs`.

Do not turn a green workflow into an accuracy claim. Do not tune thresholds against a reference tab.

A model/GPU/Modal note-inference stage is still outside current authorization and requires separate explicit authorization.

## NON-NEGOTIABLES

- Canonical checkpoint and branch above remain authoritative.
- Timing/measure structure precedes note placement and is frozen for this fixture.
- Never silently alter detected MIDI/event identity.
- Never drop pitches merely to satisfy fingering/path/legacy renderer.
- Preserve existing `/ai-tab` preview → unlock → full PDF → email/download flow.
- No main/Production changes.
- No accidental Modal/GPU/model/professional-scorer/training activity.
- Real-audio work stays inside the explicitly authorized fixture scope.
- Keep this checkpoint updated after every meaningful milestone.
