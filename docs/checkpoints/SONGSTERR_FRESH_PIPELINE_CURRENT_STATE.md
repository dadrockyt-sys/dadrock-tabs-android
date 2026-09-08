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

The fresh branch does not merge/cherry-pick main. The canary downloads only that exact public blob and verifies `git hash-object` before analysis.

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

Isolation guard: `tests/boundaryGuard.test.mjs` fails if root fresh `.mjs` source imports archived/model/non-local runtime dependencies, performs network fetches, or launches processes.

## REAL-AUDIO STRUCTURE ANALYZER

Scripts:
- `scripts/songsterr-fresh/analyze_full_mixture_structure.py`
- `scripts/songsterr-fresh/build_structure_map.mjs`

Canary workflow:
`.github/workflows/songsterr-fresh-gomyway-midterm-structure-canary.yml`

Properties:
- reference-blind
- CPU-only
- no note inference
- no reference tab
- no V143/Gomyway scorer
- exact authorized blob verification
- pinned Python/librosa/numpy/scipy/soundfile environment
- explicit ffmpeg decode
- raw + adapted JSON artifact upload
- full deterministic regression suite rerun

## IMPORTANT REAL-AUDIO STRUCTURE COMMITS

- `34c8b507865d37415c074db3d631fada403fd3ac` — initial clean full-mixture structure adapter.
- `9c8e420ff2ccf52adca277bb9335c7feb45f5db2` — initial five structure-adapter tests; branch baseline 67/67.
- `73c95d8e3d99df6f31df2f2ed10dc950393bc1bd` — CPU reference-blind full-mixture analyzer.
- `edeb37ccbbb9c79a84786b966ed683ecc6c48e5c` — raw-analysis → frozen-map runner.
- `f868dc8d18d6bda0a0392755f4a74a60220deecb` — first authorized structure canary.
- `0ac5936e0c9640dbd0ab2fbf5bab740e6c24d798` — install ffmpeg explicitly.
- `fb407e1360fa5a563d5b89f7777b5601b900b699` — pinned-librosa beat-tracker API fix.
- `3fdaacf34dc0a137ad2ab5ee0e66be140641dff8` — preserve observed measure-level tempo + scoreless structure acceptance gate.
- `2a598f0f38d755faf0cd3d46543221253f1c8997` — variable-tempo/acceptance tests; branch baseline 69/69.

## FIRST CONSTANT-TEMPO CANARY — REJECTED FOR FREEZE

Successful technical run:
- run `34192022692`
- job `101951858959`
- commit `fb407e1360fa5a563d5b89f7777b5601b900b699`

Raw full-mixture evidence:
- duration: 210.6742857142857 s
- detected beats: 450
- onsets: 620
- global fitted BPM: 130.3589230622599
- tracker BPM: 129.19921875
- tempo confidence: 0.8115688622935878
- beat interval CV: 0.03001200113096819
- selected meter: 4/4
- meter confidence: 0.5675900153317085
- selected bar phase: beat offset 1
- straight feel confidence: 0.65172110832709
- pickup / first detected downbeat: 0.6501587301587302 s
- downbeat confidence: 0.5294700192609527

The first adapter flattened the full song to one BPM. Its observed-beat alignment was:
- MAE: 0.08308248936424577 s
- RMSE: 0.10067310557537887 s
- max: 0.22844553360783593 s

That map was **not frozen**, even though workflow execution succeeded. The error pattern indicated real tempo movement/drift rather than unusable beat detection.

## REFINED MEASURE-TEMPO STRUCTURE — ACCEPTED AND FROZEN

The adapter now derives measure-local tempo segments from consecutive observed downbeats instead of flattening the track to one BPM. Tail timing is explicitly extrapolated from recent observed measures. Raw confidence remains attached.

Scoreless acceptance contract:
`songsterr-fresh-structure-acceptance-v1`

Thresholds:
- tempo confidence ≥ 0.70
- meter confidence ≥ 0.55
- downbeat confidence ≥ 0.50
- feel confidence ≥ 0.55
- beat-interval CV ≤ 0.05
- beat-grid MAE ≤ 0.025 s
- beat-grid RMSE ≤ 0.040 s
- beat-grid max error ≤ 0.080 s

Failures remain independent reason codes; no composite accuracy score is produced.

Latest successful refined canary:
- run: `34192662439`
- job: `101953726302`
- tested commit: `2a598f0f38d755faf0cd3d46543221253f1c8997`
- artifact ID: `10042777518`
- artifact name: `songsterr-fresh-gomyway-midterm-structure`
- artifact digest: `sha256:5ff3ce36f559bcc02efcc985a1fa06966576da0445896326e9408ada955e9b6f`

Refined map:
- `observedMeasureTempoPreserved: true`
- tempo segments: **113**
- observed beats evaluated: **449**
- grid beat starts: **460**
- beat-grid MAE: **0.007136645304000395 s** (~7.14 ms)
- beat-grid RMSE: **0.010631405697639835 s** (~10.63 ms)
- beat-grid max: **0.058049886621325485 s** (~58.05 ms)
- tempo confidence: 0.8115688622935878
- meter confidence: 0.5675900153317085
- downbeat confidence: 0.5294700192609527
- feel confidence: 0.65172110832709
- beat interval CV: 0.03001200113096819
- acceptance: **true**
- failure reasons: `[]`

Improvement versus the rejected flat-BPM map:
- MAE reduced about 91.4%
- RMSE reduced about 89.4%
- max error reduced about 74.6%

### FREEZE DECISION

For this exact authorized fixture, this refined `structureMap` is **accepted and frozen for downstream CPU/reference-blind note-evidence experiments**.

The 4/4 meter and first-downbeat interpretation remain only **moderate confidence**, and that uncertainty must remain attached. Do not use a reference tab or archived knowledge to make them look more certain.

Downstream note evidence is not permitted to rewrite this accepted structure.

## CURRENT TEST BASELINE

Branch-wide deterministic GitHub Actions run:
- run `34192662387`
- job `101953726428`
- commit `2a598f0f38d755faf0cd3d46543221253f1c8997`

Actual TAP result:
- tests: **69**
- pass: **69**
- fail: **0**
- cancelled: **0**
- skipped: **0**
- todo: **0**

This includes all earlier structure/rhythm/playability/path/evaluator/product-shell/orchestration/isolation tests plus seven audio-structure tests, including variable-tempo preservation and explicit weak-structure rejection reasons.

## CURRENT ENGINEERING BOUNDARY / NEXT STEP

The exact authorized fixture now has an accepted/frozen, reference-blind real-audio structure map.

Next permitted step is a **CPU-only, reference-blind note-evidence baseline** against this same audio. It must:
1. consume the frozen structure instead of estimating/revising timing;
2. emit exact candidate MIDI/event evidence with raw confidence/provenance;
3. keep ambiguous/polyphonic evidence explicit rather than silently deleting pitches;
4. use no archived Gomyway/V143 reference/scorer;
5. feed validated evidence into `deterministicPipeline.mjs` only after the note-evidence boundary itself is tested.

A model/GPU/Modal note-inference stage is still outside current authorization and requires separate explicit authorization.

## NON-NEGOTIABLES

- Canonical checkpoint and branch above remain authoritative.
- Timing/measure structure precedes note placement and is now frozen for this fixture.
- Never silently alter detected MIDI/event identity.
- Never drop pitches merely to satisfy fingering/path/legacy renderer.
- Preserve existing `/ai-tab` preview → unlock → full PDF → email/download flow.
- No main/Production changes.
- No accidental Modal/GPU/model/professional-scorer/training activity.
- Keep this checkpoint updated after every meaningful milestone.
