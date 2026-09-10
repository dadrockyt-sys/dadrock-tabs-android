import test from 'node:test';
import assert from 'node:assert/strict';

import { buildModelValidationContractScaffold } from '../modelValidationContractScaffold.mjs';
import { evaluateNoteEvidence } from '../noteEvidenceEvaluator.mjs';

function completeModelEvidence(modelValidationContractScaffold) {
  return {
    adapterContract: {
      referenceBlind: true,
      structureFrozen: true,
      structureIdentityVerified: true,
      nearestStructureSlotsVerified: true,
      syntheticDurationInference: false,
      legacyV143ScorerImported: false,
      modelInvoked: true,
      gpuInvoked: false,
    },
    capabilities: {
      roleRelevanceResolved: true,
      polyphonyResolved: true,
      durationResolution: 'complete',
      instrumentIsolation: 'model-isolated-guitar',
      confidenceCalibration: 'declared',
    },
    onsets: [
      {
        onsetId: 'model-0',
        sourceStart: 0.5,
        nearestStructureSlot: 0.5,
        structureDisplacementSeconds: 0,
        classification: 'unambiguous',
        selectedMidi: 64,
        durationSeconds: 0.25,
        candidates: [{ midi: 64, confidence: 0.91 }],
      },
    ],
    promotedEvents: [{ midi: 64, start: 0.5, duration: 0.25 }],
    metrics: {
      onsetCount: 1,
      promotedEventCount: 1,
      unresolvedOnsetCount: 0,
      durationResolvedEvidenceCount: 1,
    },
    provenance: {
      modelValidationComplete: false,
      modelValidationContractScaffold,
    },
  };
}

function strongestDiagnostics() {
  return {
    reproducibility: {
      sameRuntimeStemBytesIdentical: true,
      crossRunNoteIdentityStable: true,
      crossRunProbePayloadStable: true,
    },
    independentPitchSupport: {
      present: true,
      descriptiveOnly: true,
      referenceBlind: true,
      pitchIdentityPreserved: true,
      acceptanceThresholdDefined: false,
      thresholdSweepUsed: false,
    },
  };
}

test('model-validation scaffold is fail-closed by construction', () => {
  const result = buildModelValidationContractScaffold();
  assert.equal(result.contract.ownsAcceptanceDecision, false);
  assert.equal(result.contract.externalValidationAuthorityDefined, false);
  assert.equal(result.contract.diagnosticEvidenceCanClearValidation, false);
  assert.equal(result.validation.validated, false);
  assert.equal(result.validation.acceptanceAuthority, null);
  assert.equal(result.validation.blocker, 'MODEL_EVIDENCE_VALIDATION_PENDING');
  assert.equal(result.hardGuards.writesModelValidationComplete, false);
});

test('reproducibility plus independent pitch support cannot clear validation', () => {
  const result = buildModelValidationContractScaffold({
    noteInferenceIdentity: 'sha256:example-note-identity',
    diagnostics: strongestDiagnostics(),
  });
  assert.equal(result.identity.noteInferenceIdentity, 'sha256:example-note-identity');
  assert.equal(result.diagnostics.reproducibility.crossRunNoteIdentityStable, true);
  assert.equal(result.diagnostics.independentPitchSupport.present, true);
  assert.equal(result.validation.validated, false);
  assert.equal(result.validation.blocker, 'MODEL_EVIDENCE_VALIDATION_PENDING');
  assert.equal(result.hardGuards.reproducibilityIsAccuracy, false);
  assert.equal(result.hardGuards.independentPitchSupportIsGroundTruth, false);
});

test('diagnostic input cannot smuggle an acceptance decision into the scaffold', () => {
  const result = buildModelValidationContractScaffold({
    diagnostics: {
      ...strongestDiagnostics(),
      validated: true,
      modelValidationComplete: true,
      acceptanceAuthority: 'self-consistency',
      independentPitchSupport: {
        ...strongestDiagnostics().independentPitchSupport,
        validated: true,
        modelValidationComplete: true,
      },
    },
  });
  assert.equal(result.validation.validated, false);
  assert.equal(result.validation.acceptanceAuthority, null);
  assert.equal('validated' in result.diagnostics, false);
  assert.equal('modelValidationComplete' in result.diagnostics, false);
  assert.equal('validated' in result.diagnostics.independentPitchSupport, false);
  assert.equal('modelValidationComplete' in result.diagnostics.independentPitchSupport, false);
});

test('the scaffold defines no acceptance threshold and cannot rewrite pitch identity', () => {
  const result = buildModelValidationContractScaffold({
    noteInferenceIdentity: '  fnv1a32:abc123  ',
    diagnostics: strongestDiagnostics(),
  });
  assert.equal(result.identity.noteInferenceIdentity, 'fnv1a32:abc123');
  assert.equal(result.hardGuards.changesPitchIdentity, false);
  assert.equal(result.hardGuards.definesAcceptanceThreshold, false);
  assert.equal(result.hardGuards.performsThresholdSweep, false);
  assert.ok(result.requiredIndependentEvidence.includes('identity-bound-validation-result'));
});

test('model-validation scaffold is deterministic', () => {
  const input = {
    noteInferenceIdentity: 'sha256:stable',
    diagnostics: strongestDiagnostics(),
  };
  assert.deepEqual(
    buildModelValidationContractScaffold(input),
    buildModelValidationContractScaffold(input),
  );
});

test('support-only scaffold cannot clear the real evaluator model-validation blocker', () => {
  const scaffold = buildModelValidationContractScaffold({
    noteInferenceIdentity: 'sha256:stable',
    diagnostics: strongestDiagnostics(),
  });
  const result = evaluateNoteEvidence(completeModelEvidence(scaffold));
  assert.equal(scaffold.validation.validated, false);
  assert.equal(result.acceptedForCompleteTab, false);
  assert.ok(result.failureReasons.includes('MODEL_EVIDENCE_VALIDATION_PENDING'));
  assert.equal(result.diagnostics.modelValidationComplete, false);
});
