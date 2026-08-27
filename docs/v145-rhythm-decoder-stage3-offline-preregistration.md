# V145 Rhythm Decoder — Stage 3 Offline Trial Preregistration

Date frozen: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Status: **PREREGISTERED BEFORE IMPLEMENTATION AND BEFORE ANY V145 STAGE 3 SCORE**

## Purpose

Stage 3 is one deterministic CPU-only offline benchmark trial of the already-frozen V145 Stage 1 + Stage 2 decoder against the already-saved V5 Rhythm render stream. It is not a search, optimizer, hyperparameter sweep, production promotion, unseen-holdout claim, or live-audio run.

A Stage 3 score may be inspected only after the complete candidate is constructed from generated-only evidence, frozen, passed through the frozen renderer contract, and proved to have PDF event fidelity exactly 1.0. The calibration reference cannot influence candidate construction, candidate selection, adapter fallback behavior, or decoder behavior.

## Immutable inputs

### Generated source
- Path: `debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json`
- Git blob: `fe61f7ad53a4d71348a5113ecc9e3876eaad98d4`
- Raw file SHA256: `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`
- Expected source events: exactly 1209.
- Expected generated measure set: exactly measures 1..113.
- Tempo: exactly `129.19921875` BPM.
- Time signature: `4/4`.
- Grid: 16 steps/measure.
- Tuning: E Standard.

### Frozen decoder
- Stage 1: `modal/v145_rhythm_decoder.py`, blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`.
- Stage 2: `modal/v145_rhythm_sequence_decoder.py`, blob `5f86f57d0fd10774690d50528d51bad6e0392bf3`.
- Stage 1 and Stage 2 may not be edited, retuned, or reselected for Stage 3.

### Frozen validation/render chain
- Canonical: `validation/rhythm_holdout/canonical.py`, blob `088d44827fb23e20d9aeeb4944a672989af5846c`.
- Freeze: `validation/rhythm_holdout/freeze_rhythm_analysis.py`, blob `710bb6a3b15b99d3d11ceb4948d7c7175d208afc`.
- Scorer primitives: `validation/rhythm_holdout/score_rhythm_holdout.py`, blob `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`.
- Full calibration scoring function: `validation/v144_rhythm_calibration/score_selected_conjunction_candidate.py`, blob `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`; Stage 3 may reuse only its fixed `score_full_candidate(events, reference)` function, not its old selected-candidate logic.
- PDF fidelity: `validation/rhythm_holdout/verify_pdf_event_fidelity.py`, blob `5e1564216873046237fb545078a04a6b18f72b27`.
- Renderer contract: `lib/v143RenderContract.js`, blob `ccbb93c48982798cc474309fd981f6ca02d5c8d4`.

### Calibration reference — evaluation only
- Path: `debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json`.
- Raw SHA256: `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Role: calibration benchmark only; not an unseen holdout.
- The reference path is forbidden to the candidate-construction process and may be opened only by the evaluation-only process after the pre-reference freeze/PDF gate passes.

### Accepted comparison baseline — evaluation only
- Manifest: `debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json`, blob `acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68`.
- Accepted candidate name: `singleton-onset-replace-be9e9aa7a734e3cd`.
- Accepted event identity: 1144 events /113 measures / SHA `4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881`.
- Accepted full calibration critical mismatch count: 1712.
- Accepted metrics remain the comparison target only and cannot enter Stage 3 candidate construction.

## Frozen Stage 3 adapter

Implementation path is preregistered as:
`validation/v145_rhythm_decoder/offline_stage3_adapter.py`

Synthetic invariant tests are preregistered as:
`modal/tests/test_v145_rhythm_stage3_offline_adapter.py`

The adapter is reference-free and has no gold/reference/FIT/validation/canary argument or import.

### 1. Deterministic evidence reconstruction

For source event list index `i`:
- Require source `eventIndex` to equal `i`; indices must be exactly 0..1208 with no duplicates.
- Require integer `measure` in 1..113, integer `step` in 0..15, integer MIDI, valid renderer string/fret, and positive integer `durationSteps`.
- Define `sourceStepSeconds = 60.0 / 129.19921875 / 4.0`.
- Define `absoluteStep = (measure - 1) * 16 + step`.
- Feed Stage 2 exactly `{midi, onset=absoluteStep*sourceStepSeconds, duration=durationSteps*sourceStepSeconds, confidence=1.0}` in source-list order.
- No audio, professional reference, historical residual labels, or calibration score enters this reconstruction.

### 2. Decoder call

Call frozen `decode_global_rhythm_sequence` exactly once on the reconstructed 1209-event evidence sequence. No Stage 1/2 parameter is changed. No second decoder trial is allowed after observing any output or score.

### 3. Protected musical metadata

To avoid making technique metadata internally inconsistent, an event is protected from all Stage 3 onset/string/fret edits if the source event has any of:
- a non-empty `techniques` or `rhythmTechniques` list;
- `bendSemitones`, `bendTargetFret`, or `bendTargetMidi`;
- `legatoTargetEventIndex`, `legatoContinuationFromEventIndex`, or `legatoContinuationType`.

Any source event referenced by `legatoTargetEventIndex` or `legatoContinuationFromEventIndex` is also protected.

If any decoded note in one selected Stage 2 common-onset group is protected, the entire decoded common-onset group is preserved byte-for-byte from the source stream.

### 4. Applying an unprotected decoded common-onset group

Decoded notes are grouped by exact Stage 2 selected `onset`. A group is applied atomically or not at all.

For each decoded note in an unprotected group:
- `source_index` must uniquely reference one source event.
- Decoded MIDI must equal source MIDI exactly; otherwise the whole trial fails closed before scoring.
- Convert selected seconds back to the immutable V5 16th-note renderer grid using `candidateAbsoluteStep = floor(decoded.onset / sourceStepSeconds + 0.5)`.
- Require normalized conversion residual `abs(decoded.onset/sourceStepSeconds - candidateAbsoluteStep) <= 0.01`; otherwise preserve the whole group unchanged.
- Require `0 <= candidateAbsoluteStep < 113*16`; otherwise preserve the whole group unchanged.
- Convert to `measure = candidateAbsoluteStep // 16 + 1`, `step = candidateAbsoluteStep % 16`.
- Convert human guitar string 1..6 to renderer `stringIndex = decoded.string - 1`.
- Require renderer string in 0..5, fret in 0..24, and exact physical pitch consistency using renderer open MIDI `(64,59,55,50,45,40)`: `openMidi[stringIndex] + fret == midi`. Otherwise the whole trial fails closed before scoring.

The only fields an applied group may change are `measure`, `step`, `stringIndex`, and `fret`. MIDI, eventIndex, duration fields, techniques, link metadata, bend metadata, attack metadata, sustain metadata, and every other source field are preserved exactly.

### 5. Collision / ordering / coverage safeguards

- Source list order and every `eventIndex` are immutable. No reindexing or link remapping is allowed.
- Event count must remain exactly 1209; no additions or deletions are allowed.
- A proposed group is preserved unchanged if its projected `(measure, step, stringIndex)` cells collide with any source event outside the same decoded group.
- Stage 2 selected groups have strictly increasing selected onsets; two applied groups therefore may not share a projected onset. If a postcondition detects any newly-created duplicate `(measure, step, stringIndex)` cell, the candidate fails closed before scoring.
- Existing source duplicate cells, if any, cannot be made worse; the adapter must compare source and candidate cell multiplicities and reject any increased multiplicity.
- Final generated measure set must equal the source generated measure set exactly and must contain all 113 measures. Otherwise the candidate fails closed before scoring.
- Every output MIDI must equal the same source-index MIDI. Therefore Stage 3 generates no new pitch evidence and deletes no pitch evidence.

### 6. Undecoded events

Every Stage 2 undecoded source event is copied byte-for-byte from the source stream. No alternate decoder or heuristic is attempted.

## Candidate identity / output

The adapter writes a single complete candidate payload containing:
- schema version 14503;
- classification `v145-rhythm-stage3-offline-generated-only-candidate`;
- exact source identity and frozen Stage1/Stage2 identities;
- inferred-grid diagnostics and decoded/undecoded counts;
- protected/applied/preserved-group counts;
- safety flags proving no reference/gold/labels/Modal/GPU/live audio were used;
- `renderEvents` containing exactly 1209 source-corresponding events.

There is no candidate ranking and no alternate Stage 3 candidate.

## Mandatory CPU proof before calibration execution

Before the real saved V5 stream is scored, a branch-scoped CPU proof must:
1. verify the preregistration, Stage1, Stage2, adapter, tests, and frozen dependency blobs;
2. compile Stage1/Stage2/adapter;
3. run Stage1, Stage2, and Stage3 synthetic invariant tests;
4. prove adapter API has no reference/gold/label input and synthetic tests do not read calibration data;
5. persist a proof JSON under `debug/v145-rhythm-decoder/proofs/`;
6. be sealed/deleted after one successful proof run and never replayed.

The CPU proof may not build or score the real Stage 3 candidate.

## One-shot offline execution order

After a successful sealed CPU proof, one one-shot branch workflow may run exactly once in this order:

1. Verify trigger is the sole triggering change and verify all preregistered blobs/hashes.
2. Re-run fixed CPU contract tests.
3. Verify the calibration reference raw SHA256 **without passing its path/content to the candidate constructor**; workflow-level identity verification is not candidate input.
4. Run the Stage 3 adapter on only the pinned V5 generated stream, producing the sole complete candidate.
5. Validate candidate invariants, event count, eventIndex/source correspondence, pitch identity, measure set, and renderer physical positions.
6. Construct a reference-free freeze input from the complete candidate and run frozen `freeze_rhythm_analysis.py`.
7. Pass the candidate events through frozen `validateV143RenderEvents` and produce renderer-event evidence with `referenceOpened=false` / `professionalReferenceUsed=false`.
8. Run frozen `verify_pdf_event_fidelity.py`; require `passed=true`, `pdfEventFidelity=1.0`, frozen event SHA = renderer event SHA, and event count =1209.
9. In a separate evaluation-only process, first call the frozen scorer pre-reference validation (`validate_pre_reference`) on the completed freeze directory. Only after that succeeds may the process open the calibration reference.
10. Evaluation-only process verifies the reference raw SHA256, validates it with frozen `validate_reference`, scores the already-frozen candidate with frozen `score_full_candidate`, and compares it with the immutable accepted-family-#10 calibration manifest.
11. Reverify all immutable input blobs/hashes.
12. Persist only the Stage 3 candidate/report/proof artifacts explicitly preregistered for persistence; delete/seal the one-shot workflow and trigger afterward.

The reference is never opened during candidate construction, renderer validation, freeze, or PDF-event-fidelity proof.

## Stage 3 report semantics

The score report must state:
- `evaluationRole = calibration-benchmark-not-unseen-holdout`;
- `mayClaimUnseenGeneralization = false`;
- the frozen candidate event count/SHA;
- exact V145 candidate gated metrics and critical mismatch count;
- deltas vs accepted family #10 for pitch content, pitch+timing, string/fret+timing, chord pitch-set, exact voicing, measure coverage, and critical mismatches;
- PDF event fidelity exactly 1.0;
- `acceptedBaselineChanged = false`;
- `promotionAllowed = false`.

No Stage 3 score, whether better or worse, automatically promotes anything. A later promotion decision would require a separately preregistered gate and explicit action.

## No retuning / no replay rule

After the one Stage 3 score is revealed:
- do not change Stage1, Stage2, Stage3 adapter constants, protection rules, conversion tolerance, grouping rules, collision behavior, or scoring logic in response to that score;
- do not rerun Stage 3 under an alternate adapter;
- do not use the observed score to claim unseen generalization;
- retain accepted family #10 unless a later separately frozen promotion protocol explicitly succeeds.

## Safety

Stage 3 is CPU-only and uses already-saved repository artifacts. No Modal dependency, L4, GPU, live audio analysis, Production, main, `/ai-tab`, Bass, Lead, or `freezeReady=false` changes are authorized by this preregistration.
