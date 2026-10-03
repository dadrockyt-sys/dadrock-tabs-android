# Transcription Uncertainty Presentation Contract V1

Date: 2026-10-02  
Branch: `astra-work`

## Status

Implemented and unit-tested successfully.

GitHub Actions run: `37092615121` — **success**  
Head commit: `7b92c09a858a12b72968bfadc530b5e370a04d7d`

Implementation:
- `astra_backend/transcriptionUncertaintyPresentation.mjs`
- `astra_backend/tests/transcriptionUncertaintyPresentation.test.mjs`
- `.github/workflows/astra-transcription-uncertainty-presentation-v1.yml`

## Contract

The uncertainty presentation layer consumes already-produced note evidence, note-event exposure, and optional diagnostic context. It does not alter audio and does not alter note pitch/onset identity.

It explicitly defines:
- reference-blind presentation;
- frozen-structure requirement;
- no composite confidence score;
- no automatic correction;
- no automatic stem mutation;
- no automatic role reassignment;
- no thresholds learned from S0.

Presentation states:
- `complete_tab_eligible`
- `evidence_visible_review_required`
- `no_reliable_note_evidence`

Important fail-closed behavior:
- duplicate-class pair state -> notes remain visible, but complete-tab eligibility is blocked with `PAIR_ROLE_AMBIGUITY_DUPLICATE_CLASS_CANDIDATE`;
- missing/silent pair member -> `PAIR_MEMBER_MISSING_OR_SILENT`;
- ambiguous pair -> `PAIR_ROLE_RELATIONSHIP_AMBIGUOUS`;
- existing note-evidence evaluator failure reasons are surfaced unchanged.

Cross-stem diagnostics may be attached only when marked `descriptiveOnly: true`; they cannot silently own an acceptance gate.

## Why this follows the S0 evidence

Cross-Stem Transcription Overlap V1 did not find a unique same-note-overlap signature for S0M10. Only event-density symmetry strongly isolated the fixture, and one positive fixture is insufficient to freeze an automatic threshold.

Therefore the correct next behavior is to preserve detected evidence and expose uncertainty rather than automatically modify or hide it.

## Boundaries

This module is not connected to production delivery. It is a research/development contract only.

No claim is made that flagged notes are wrong. A flag means the system has evidence that role assignment or transcription completeness is unresolved enough that a complete automatic tab should not be silently presented as settled.
