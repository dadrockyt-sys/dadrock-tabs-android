#!/usr/bin/env node

import { evaluateNoteEvidence } from '../../songsterr_pipeline/noteEvidenceEvaluator.mjs';

function makeEvidence({ confidence, modelValidationComplete, durationComplete }) {
  const onsets = [40, 52].map((midi, index) => ({
    onsetId: `test-${index}`,
    classification: 'unambiguous',
    structureDisplacementSeconds: 0,
    candidates: [{ midi, confidence }],
  }));
  const promotedEvents = durationComplete
    ? [
        { start: 1.0, midi: 40, duration: 0.5 },
        { start: 2.0, midi: 52, duration: 0.5 },
      ]
    : [];
  return {
    adapterContract: {
      referenceBlind: true,
      structureFrozen: true,
      structureIdentityVerified: true,
      nearestStructureSlotsVerified: true,
      syntheticDurationInference: false,
      legacyV143ScorerImported: false,
      modelInvoked: true,
    },
    provenance: {
      modelValidationComplete,
    },
    capabilities: {
      roleRelevanceResolved: true,
      polyphonyResolved: true,
      durationResolution: durationComplete ? 'complete' : 'none',
      instrumentIsolation: 'diagnostic-test',
      confidenceCalibration: 'basic-pitch-note-amplitude-not-calibrated-probability',
    },
    onsets,
    promotedEvents,
    metrics: {
      onsetCount: onsets.length,
      promotedEventCount: promotedEvents.length,
      unresolvedOnsetCount: 0,
      durationResolvedEvidenceCount: durationComplete ? promotedEvents.length : 0,
    },
  };
}

function acceptanceProjection(result) {
  return {
    acceptedForCompleteTab: result.acceptedForCompleteTab,
    failureReasons: result.failureReasons,
    capabilities: result.capabilities,
    inventory: result.inventory,
  };
}

function assertConfidenceOnlyChangesDiagnostics(options) {
  const low = evaluateNoteEvidence(makeEvidence({ ...options, confidence: 0.01 }));
  const high = evaluateNoteEvidence(makeEvidence({ ...options, confidence: 0.99 }));

  if (JSON.stringify(acceptanceProjection(low)) !== JSON.stringify(acceptanceProjection(high))) {
    throw new Error('CANDIDATE_CONFIDENCE_CHANGED_ACCEPTANCE_SEMANTICS');
  }
  if (low.diagnostics.topConfidence.mean === high.diagnostics.topConfidence.mean) {
    throw new Error('CANDIDATE_CONFIDENCE_DIAGNOSTIC_DID_NOT_CHANGE');
  }
  if (low.evaluatorContract.compositeScoreDefined !== false || high.evaluatorContract.compositeScoreDefined !== false) {
    throw new Error('CANDIDATE_CONFIDENCE_MUST_NOT_ENTER_COMPOSITE_SCORE');
  }
  return { low, high };
}

const pending = assertConfidenceOnlyChangesDiagnostics({
  modelValidationComplete: false,
  durationComplete: false,
});
if (!pending.low.failureReasons.includes('MODEL_EVIDENCE_VALIDATION_PENDING')) {
  throw new Error('PENDING_CASE_MUST_REMAIN_VALIDATION_BLOCKED');
}

const otherwiseComplete = assertConfidenceOnlyChangesDiagnostics({
  modelValidationComplete: true,
  durationComplete: true,
});
if (otherwiseComplete.low.acceptedForCompleteTab !== true || otherwiseComplete.high.acceptedForCompleteTab !== true) {
  throw new Error('CONFIDENCE_MUST_NOT_BLOCK_OTHERWISE_COMPLETE_EVIDENCE');
}

console.log(JSON.stringify({
  contract: 'songsterr-fresh-candidate-confidence-diagnostic-only-test-v1',
  candidateConfidenceUsedForAcceptance: false,
  candidateConfidenceDiagnosticsOnly: true,
  validationPendingInvariant: true,
  otherwiseCompleteInvariant: true,
}));
