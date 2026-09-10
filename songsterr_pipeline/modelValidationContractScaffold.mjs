const CONTRACT = Object.freeze({
  name: 'songsterr-fresh-model-validation-contract-scaffold',
  version: 1,
  ownsAcceptanceDecision: false,
  externalValidationAuthorityDefined: false,
  diagnosticEvidenceCanClearValidation: false,
  mutatesModelValidationComplete: false,
  referenceBlind: true,
});

function nonEmptyStringOrNull(value) {
  return typeof value === 'string' && value.trim().length > 0 ? value.trim() : null;
}

function boolean(value) {
  return value === true;
}

function normalizeDiagnostics(diagnostics) {
  const input = diagnostics && typeof diagnostics === 'object' ? diagnostics : {};
  const reproducibility = input.reproducibility && typeof input.reproducibility === 'object'
    ? input.reproducibility
    : {};
  const pitchSupport = input.independentPitchSupport && typeof input.independentPitchSupport === 'object'
    ? input.independentPitchSupport
    : {};

  return {
    reproducibility: {
      sameRuntimeStemBytesIdentical: boolean(reproducibility.sameRuntimeStemBytesIdentical),
      crossRunNoteIdentityStable: boolean(reproducibility.crossRunNoteIdentityStable),
      crossRunProbePayloadStable: boolean(reproducibility.crossRunProbePayloadStable),
    },
    independentPitchSupport: {
      present: boolean(pitchSupport.present),
      descriptiveOnly: boolean(pitchSupport.descriptiveOnly),
      referenceBlind: boolean(pitchSupport.referenceBlind),
      pitchIdentityPreserved: boolean(pitchSupport.pitchIdentityPreserved),
      acceptanceThresholdDefined: boolean(pitchSupport.acceptanceThresholdDefined),
      thresholdSweepUsed: boolean(pitchSupport.thresholdSweepUsed),
    },
  };
}

export function buildModelValidationContractScaffold({
  noteInferenceIdentity = null,
  diagnostics = {},
} = {}) {
  return {
    contract: { ...CONTRACT },
    identity: {
      noteInferenceIdentity: nonEmptyStringOrNull(noteInferenceIdentity),
    },
    validation: {
      validated: false,
      status: 'pending-independent-model-validation-contract',
      acceptanceAuthority: null,
      blocker: 'MODEL_EVIDENCE_VALIDATION_PENDING',
    },
    diagnostics: normalizeDiagnostics(diagnostics),
    requiredIndependentEvidence: [
      'externally-defined-validation-authority',
      'independent-evidence-not-derived-from-basic-pitch-self-consistency',
      'identity-bound-validation-result',
    ],
    hardGuards: {
      diagnosticsOwnAcceptanceDecision: false,
      reproducibilityIsAccuracy: false,
      independentPitchSupportIsGroundTruth: false,
      writesModelValidationComplete: false,
      changesPitchIdentity: false,
      definesAcceptanceThreshold: false,
      performsThresholdSweep: false,
      invokesModel: false,
      performsNetworkAccess: false,
      spawnsProcesses: false,
      usesReferenceTab: false,
      importsArchivedV143Logic: false,
    },
  };
}
