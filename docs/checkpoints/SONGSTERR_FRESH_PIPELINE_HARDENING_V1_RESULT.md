# Songsterr Fresh Pipeline Hardening V1 — Result

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: `PASS_CODE_ONLY_HARDENING_V1`

## Scope and authority

The user instructed: `Lets fix the weak points of this pipeline and make it work.`

This work hardened the fresh transcription/evidence pipeline after the repaired EGFxSet smoke exposed an extra Basic Pitch MIDI-68 event alongside the expected MIDI-40 event.

This hardening **does not rewrite the historical repaired EGFxSet smoke FAIL**. It did not execute EGFxSet audio, Basic Pitch, another model, a new candidate, a reference tab, V143/Gomyway, or any closed/reserved dataset line. It is deterministic/code-only plus synthetic DSP validation.

Global authorization remains unchanged:

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

## Historical diagnostic remains frozen

The repaired EGFxSet one-shot remains:

- run `34936227380`
- job `104274605954`
- exactly one successful Basic Pitch invocation
- emitted MIDI set `{40,68}`
- MIDI 40 matched the independent open-low-E label
- MIDI 68 was an extra event
- `PASS_RUNTIME`
- `FAIL_PITCH`
- `FAIL_POSITION`
- overall `FAIL_NON_AUTHORIZING_SMOKE`

That result remains valid under its prospectively frozen all-events smoke rule and is not post-filtered into a PASS.

## Weak point 1 — raw model proposal was effectively auto-promoted

Audit finding:

The raw Basic Pitch transcription stage correctly preserved every model event, but the legacy model-note evidence builder converted every Basic Pitch event directly to `classification: unambiguous`. That meant a model emission could become a promoted note without an independent corroboration decision.

### Fix

Prospective semantics were frozen in:
`docs/checkpoints/SONGSTERR_FRESH_MODEL_NOTE_QUALIFICATION_V1_PRE.md`.

The deterministic evidence adapter now supports four explicit states:

- `unambiguous`: independently corroborated; may promote;
- `rejected`: independently rejected; preserved but never promoted;
- `ambiguous`: insufficient qualification; not promoted and unresolved;
- `no-candidate`: no pitch candidate; not promoted and unresolved.

Rejected evidence is not deleted. Candidate MIDI, timing, confidence and provenance remain inspectable. `unresolvedOnsetCount` now means truly unresolved evidence (`ambiguous + no-candidate`), not proposals that have already been explicitly rejected.

Only `unambiguous` evidence can enter `promotedEvents`.

## Weak point 2 — no exact qualification population/identity contract

A new builder was added:
`scripts/songsterr-fresh/build_qualified_isolated_polyphonic_note_evidence.mjs`.

It fails closed unless the qualification sidecar:

- binds to the exact immutable Basic Pitch note-identity SHA;
- has exactly one qualification row per raw proposal;
- has no duplicate, missing, extra or mismatched note identity;
- matches each note's `noteId`, MIDI and start time;
- uses only `corroborated`, `rejected` or `insufficient` status;
- explicitly declares `candidateConfidenceUsedForDecision:false`;
- explicitly declares `independentOfBasicPitchCandidateConfidence:true`;
- does not use a reference tab.

Mapping is deterministic:

- `corroborated` -> `unambiguous`
- `rejected` -> `rejected`
- `insufficient` -> `ambiguous`

`polyphonyResolved:true` is allowed only when every raw model proposal has been either corroborated or explicitly rejected.

A bridge CLI was also added:
`scripts/songsterr-fresh/adapt_qualified_note_evidence_v1.mjs`, allowing qualified raw evidence to enter the existing adapter/evaluator/canary path without restoring auto-promotion.

## Weak point 3 — tempting but invalid confidence threshold fix

No Basic Pitch confidence cutoff was introduced.

The observed EGFxSet values (`~0.7906` for MIDI 40 and `~0.3487` for MIDI 68) were not used to choose a post-hoc threshold. Basic Pitch candidate confidence remains diagnostic-only.

Synthetic tests deliberately invert candidate confidences and verify that qualification/promotion does not change.

## Weak point 4 — independent note-birth evidence needed

Prospective DSP semantics were frozen in:
`docs/checkpoints/SONGSTERR_FRESH_MODEL_NOTE_QUALIFIER_DSP_V1_PRE.md`.

A model-free qualifier was added:
`scripts/songsterr-fresh/qualify_basic_pitch_note_births_v1.py`.

It reuses the already-existing frozen V6 onset-birth DSP constants from:
`scripts/songsterr-fresh/onset_birth_corroboration_v6.py`.

No threshold was retuned from the EGFxSet result.

The qualifier:

- never invokes Basic Pitch or another model;
- never reads Basic Pitch candidate confidence for the decision;
- uses deterministic mono conversion and deterministic resampling when required;
- uses existing complex spectral onset-innovation / harmonic-template / NNLS / candidate-necessity evidence;
- preserves exact proposal identity;
- supplies deterministic zero left-padding only when required for clip-start pre-context;
- never fabricates future/right-edge audio;
- maps corroborated birth -> `corroborated`;
- maps explicit non-corroboration -> `rejected`;
- normally maps incomplete evidence -> `insufficient`;
- prospectively maps full-context, adequate-RMS `INSUFFICIENT_LOW_ONSET_INNOVATION` to `rejected`, because the narrower question is whether a proposed **new note birth** occurred and essentially no onset innovation is negative birth evidence.

No MIDI-specific exception exists.

## Synthetic DSP result

The frozen synthetic qualifier test demonstrates:

- true E2 birth -> `corroborated`;
- proposal for MIDI 68 (the fifth-harmonic frequency relation used by the test) during the already-sustaining E2 -> `rejected`;
- reversing Basic Pitch candidate confidences does not change either status;
- near-left-boundary events receive deterministic pre-context and reach a real finite DSP decision;
- missing right-edge context remains `insufficient` rather than being padded/fabricated.

The first boundary test revision incorrectly required left-padding to force `corroborated`; the fixed DSP legitimately produced a finite rejection under the unchanged necessity threshold. The test contract was corrected to require **successful finite evaluation**, not a forced positive classification. No DSP threshold was changed.

## Weak point 5 — playable fingering was conflated with physical string/fret certainty

Prospective semantics were frozen in:
`docs/checkpoints/SONGSTERR_FRESH_PHYSICAL_POSITION_AMBIGUITY_V1_PRE.md`.

The deterministic core now counts every complete one-event-per-string playable assignment for an onset cluster while preserving the existing preferred-shape score and tie-break.

Existing `shapeResolved` remains backward compatible and means a complete playable layout exists.

New metadata separates physical certainty:

- `shapeCandidateCount`
- `physicalShapeResolved`
- `positionSelectionMethod`
  - `unique-physical-layout`
  - `heuristic-preferred-layout`
  - `unassigned`

The existing preferred playable string/fret rendering remains available for UX, but when multiple valid layouts exist it is explicitly labeled heuristic rather than physical truth.

Synthetic tests verify:

- standard-tuned MIDI 40 has exactly one layout: string 6 / fret 0, physically resolved;
- MIDI 64 has multiple playable layouts: preferred layout preserved but physical shape unresolved;
- a multi-note ambiguous cluster also remains playable while physical certainty is false;
- exact MIDI is preserved in every case.

## Final combined regression

Workflow:
`.github/workflows/songsterr-model-note-qualification-v1-tests.yml`

Workflow commit:
`7027810ff9fc8f21f06ad17141319c54acd8139c`

Run:
`34938422696`

Job:
`104281318739`

Attempt:
`1`

Conclusion:
`success`

All final steps passed:

1. candidate confidence remains diagnostic-only;
2. model-note qualification V1 structural/fail-closed tests;
3. physical-position ambiguity V1 tests;
4. Python 3.10.21 setup;
5. frozen DSP test dependencies NumPy 1.26.4 / SciPy 1.15.3;
6. independent DSP note-birth qualifier V1 tests.

Earlier qualification structural run `34937351248`, job `104278056617`, also passed all seven structural cases.

Corrected standalone DSP run `34937884519`, job `104279687264`, passed all four synthetic DSP cases.

## Archived workflow note

An old pre-existing Gomyway workflow is broadly branch-triggered and was awakened automatically by ordinary branch pushes during this engineering work. Its output was not used, inspected for pipeline conclusions, or treated as reopened work. Archived V143/Gomyway remains closed.

## Result

**PASS_CODE_ONLY_HARDENING_V1**

The fresh pipeline no longer has to treat every Basic Pitch emission as a note. Basic Pitch is now a proposal generator; exact, independently qualified evidence controls promotion. False/harmonic proposals can remain fully visible in provenance while being explicitly rejected instead of entering the transcription. Fretboard layout metadata also now distinguishes a merely playable heuristic assignment from uniquely determined physical position.

This is a code/synthetic result, not correctness validation.

## Next real validation boundary

No real validation is authorized by this checkpoint.

A high-value next test, if separately and explicitly authorized, does **not** require another Basic Pitch inference. It can reuse:

- the exact previously verified EGFxSet WAV identity; and
- the immutable repaired-run Basic Pitch JSON (`sha256:24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`)

and run only the newly frozen independent qualifier -> qualified builder -> adapter/evaluator path.

That future test must be frozen as a new real-audio validation before execution. It cannot alter the historical smoke result, and no thresholds or status rules may be changed after seeing its output.
