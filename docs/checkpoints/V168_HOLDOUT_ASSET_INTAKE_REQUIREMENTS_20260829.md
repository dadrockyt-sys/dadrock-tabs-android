# V168 — External holdout asset intake requirements

Date: 2026-08-29 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **PROSPECTIVE INTAKE CONTRACT / NO ASSETS ADMITTED / SCORING NOT ARMED**

This document supplements, but does not modify, the frozen V168 preregistration and frozen base holdout admission validator.

## Purpose

The repository currently has no admissible independent cross-song professional Guitar holdout set. Before any future external asset can be admitted, its manifest must pass both:

1. frozen base validator `validation/v168_holdout/validate_holdout_asset_manifest_v168.py` (blob `c9e0b00ffe9cddf8138e63843afa98a715fed579`); and
2. prospective provenance companion `validation/v168_holdout/validate_holdout_asset_provenance_v168.py`.

Both validators operate on metadata only. Neither may open source-audio bytes, professional reference note/event bytes, generated candidates, or scorer code.

## Required manifest identity

The manifest remains the already-frozen schema:
- `schema = dadrock.tabs.v168.holdout-asset-manifest.v1`
- `version = V168`
- `status = HOLDOUT_ASSETS_FROZEN_BEFORE_CANDIDATE_GENERATION`
- exactly the two frozen policy IDs in their frozen order;
- minimum holdout songs = 2;
- Lenny Kravitz — Are You Gonna Go My Way excluded as calibration data;
- V168 reference-facing score calls before asset freeze = 0.

The companion additionally requires:
- `provenanceGate = dadrock.tabs.v168.holdout-provenance-gate.v1`;
- `acquisitionMetadataFrozenBeforeAdmission = true`;
- `sourceReferencePairBindingsFrozen = true`;
- `provenanceReviewedWithoutComparativeScores = true`.

## Per-song source-audio requirements

Each song must include the frozen source identity already required by the base validator plus:
- non-secret `storageLocator` with a frozen locator type/label;
- provenance `origin`;
- `acquisitionMethod`;
- `rightsOrUseBasis` describing why the asset may be used for this private/internal research evaluation;
- `provenance.metadataFrozen = true`;
- `acquiredBeforeAdmissionDecision = true`.

Allowed locator types are intentionally descriptive rather than secret-bearing:
- `repository_path`
- `private_artifact`
- `user_supplied`
- `licensed_source`

Do not put passwords, tokens, private download URLs, or other secrets in the public manifest.

## Per-song professional-reference requirements

In addition to the frozen base contract (`kind=professional_scorer_ready`, combined Guitar covered, uncertainty frozen, candidate generation cannot read note events), each reference must include:
- non-secret frozen storage locator;
- provenance origin/acquisition/use-basis metadata frozen before admission;
- non-empty `preparedBy` provenance label;
- `derivedFromModelOrCandidateOutput = false`;
- `preparedIndependentlyOfV167Calibration = true`;
- `referenceBytesAccessibleToCandidateGeneration = false`;
- `frozenV154ScorerCompatible = true` before admission;
- `sourceAudioSha256` exactly equal to that song's frozen source-audio SHA256.

Ordinary DadRock lesson/tab assets, model outputs, generated candidates, synthetic self-reference, or V167 calibration components are not professional holdout ground truth by assumption.

## Frozen source/reference pair binding

Each song must contain `pairBinding` proving the professional reference belongs to the exact source recording:
- `sourceAudioSha256` equals the source identity;
- `professionalReferenceSha256` equals the professional-reference identity;
- `sameRecording = true`;
- `bindingFrozen = true`.

This prevents accidentally pairing a valid reference with a different master, live version, edit, remaster, or timebase.

## Prospective quality gate

Before comparative scores are available, each song must record:
- `combinedGuitarCoverageReviewed = true`;
- `timingGridCompatibilityReviewed = true`;
- `uncertaintyPolicyFrozen = true`;
- `qualityDecisionMadeWithoutComparativeScores = true`.

Any timing transform needed to satisfy the frozen V154 scorer contract must be frozen prospectively before candidate scoring; holdout score direction cannot be used to alter it.

## Admission sequence

1. Acquire at least two genuinely independent songs and professional scorer-ready combined-Guitar references.
2. Freeze source/reference identities and provenance metadata without comparative scoring.
3. Bind each reference to its exact source recording by SHA256.
4. Run the frozen base admission validator.
5. Run the frozen prospective provenance companion.
6. Only if both gates pass for the complete >=2-song manifest may a future candidate-generation implementation be staged.
7. Candidate generation remains reference-blind; freeze both Policy A/B outputs for every admitted song before any scorer/reference read.
8. Only then may a separate scorer workflow be considered.

Until all of the above is satisfied, V168 remains **HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED** with **0 reference-facing score calls**.

## Unchanged boundaries

- V167 is closed and must not be reopened for more Lenny calibration.
- No holdout-driven rule/threshold/selector changes.
- No adverse-result song exclusion.
- No per-event reference choices or direct reference-event copying.
- CPU only under current authorization.
- Fresh explicit authorization is required before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
