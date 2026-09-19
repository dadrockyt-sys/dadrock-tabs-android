const ROLES = new Set(['bass', 'lead', 'rhythm']);

const CANDIDATES = Object.freeze([
  Object.freeze({
    id: 'spleeter-5stems-v2.3.0',
    family: 'spleeter',
    source: Object.freeze({
      repository: 'deezer/spleeter',
      revision: 'v2.3.0@e65ece8',
      artifactIdentity: 'spleeter:5stems',
      artifactSha256: null,
    }),
    capabilities: Object.freeze({
      bassStem: true,
      genericGuitarStem: false,
      leadStem: false,
      rhythmStem: false,
    }),
    rights: Object.freeze({
      modelArtifactTerms: 'MIT-pretrained-models-explicit',
      developmentEvaluationPermitted: true,
      commercialInferencePermitted: true,
      upstreamWeightRightsResolved: true,
    }),
    runtime: Object.freeze({
      cpuExecutionClaimed: true,
      within1200SecondsVerifiedOnAstra: false,
      deployment: 'TensorFlow Spleeter runtime',
    }),
    lineage: Object.freeze({
      dependsOnFrozenHtdemucs6s: false,
      independentOfFrozenDemucsWeight: true,
    }),
    disposition: 'REJECTED_NO_GUITAR_STEM',
  }),
  Object.freeze({
    id: 'open-unmix-umxhq-v1.0.0',
    family: 'open-unmix',
    source: Object.freeze({
      repository: 'sigsep/open-unmix-pytorch',
      revision: 'v1.0.0@3f6a421',
      artifactIdentity: 'umxhq',
      artifactSha256: null,
    }),
    capabilities: Object.freeze({
      bassStem: true,
      genericGuitarStem: false,
      leadStem: false,
      rhythmStem: false,
    }),
    rights: Object.freeze({
      modelArtifactTerms: 'repository-MIT; exact pretrained-weight commercial terms not separately frozen by Astra',
      developmentEvaluationPermitted: false,
      commercialInferencePermitted: false,
      upstreamWeightRightsResolved: false,
    }),
    runtime: Object.freeze({
      cpuExecutionClaimed: true,
      within1200SecondsVerifiedOnAstra: false,
      deployment: 'PyTorch Open-Unmix runtime',
    }),
    lineage: Object.freeze({
      dependsOnFrozenHtdemucs6s: false,
      independentOfFrozenDemucsWeight: true,
    }),
    disposition: 'REJECTED_NO_GUITAR_STEM',
  }),
  Object.freeze({
    id: 'stemsplit-htdemucs6s-onnx',
    family: 'htdemucs_6s-conversion',
    source: Object.freeze({
      repository: 'StemSplitio/htdemucs-6s-onnx',
      revision: '52c122c298c21fb0c74e7f04fe6e5d9c1f6dceef',
      artifactIdentity: 'htdemucs_6s.onnx',
      artifactSha256: '48f8e84945579f8ab340e083339e9221e03785dbe733a52c388200b6d3ca779a',
      artifactSizeBytes: 258159781,
    }),
    capabilities: Object.freeze({
      bassStem: true,
      genericGuitarStem: true,
      leadStem: false,
      rhythmStem: false,
    }),
    rights: Object.freeze({
      modelArtifactTerms: 'downstream repository labels conversion MIT',
      developmentEvaluationPermitted: false,
      commercialInferencePermitted: false,
      upstreamWeightRightsResolved: false,
    }),
    runtime: Object.freeze({
      cpuExecutionClaimed: true,
      within1200SecondsVerifiedOnAstra: false,
      deployment: 'ONNX Runtime CPU provider; no PyTorch required at inference',
    }),
    lineage: Object.freeze({
      dependsOnFrozenHtdemucs6s: true,
      independentOfFrozenDemucsWeight: false,
    }),
    disposition: 'BLOCKED_UPSTREAM_HTDEMUCS6S_WEIGHT_RIGHTS',
  }),
  Object.freeze({
    id: 'adityalakhani-htdemucs6s-guitar-ft',
    family: 'htdemucs_6s-finetune',
    source: Object.freeze({
      repository: 'adityalakhani/htdemucs-6s-guitar-ft',
      revision: '3c3272339025ddb0ef899e939637b93c54186431',
      artifactIdentity: 'guitar_htdemucs_6s.pt',
      artifactSha256: '4fde369e41582ba5c2759b6ab926a44af467c64d4566bf914374ab267b19260e',
      artifactSizeBytes: 329654071,
    }),
    capabilities: Object.freeze({
      bassStem: true,
      genericGuitarStem: true,
      leadStem: false,
      rhythmStem: false,
    }),
    rights: Object.freeze({
      modelArtifactTerms: 'downstream model labels Apache-2.0; base htdemucs_6s lineage and training-data commercial implications unresolved by Astra',
      developmentEvaluationPermitted: false,
      commercialInferencePermitted: false,
      upstreamWeightRightsResolved: false,
    }),
    runtime: Object.freeze({
      cpuExecutionClaimed: true,
      within1200SecondsVerifiedOnAstra: false,
      deployment: 'Demucs 4.0.1 + PyTorch/Torchaudio; 44.1 kHz stereo',
    }),
    lineage: Object.freeze({
      dependsOnFrozenHtdemucs6s: true,
      independentOfFrozenDemucsWeight: false,
    }),
    disposition: 'BLOCKED_UPSTREAM_AND_TRAINING_RIGHTS_CHAIN',
  }),
]);

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export function listAstraSeparationRightsCandidates() {
  return CANDIDATES.map(clone);
}

export function evaluateAstraSeparationRightsCandidate(candidateId, { role = 'bass' } = {}) {
  if (!ROLES.has(role)) throw new Error('role must be bass, lead, or rhythm.');
  const candidate = CANDIDATES.find((entry) => entry.id === candidateId);
  if (!candidate) throw new Error('Unknown Astra separation-rights candidate.');

  const blockers = [];
  if (!candidate.capabilities.bassStem) blockers.push('BASS_STEM_UNAVAILABLE');
  if (!candidate.capabilities.genericGuitarStem) blockers.push('GUITAR_STEM_UNAVAILABLE');
  if (candidate.rights.developmentEvaluationPermitted !== true) {
    blockers.push('DEVELOPMENT_MODEL_ARTIFACT_RIGHTS_UNRESOLVED');
  }
  if (candidate.rights.commercialInferencePermitted !== true) {
    blockers.push('COMMERCIAL_MODEL_ARTIFACT_RIGHTS_UNRESOLVED');
  }
  if (candidate.rights.upstreamWeightRightsResolved !== true) {
    blockers.push('UPSTREAM_WEIGHT_RIGHTS_UNRESOLVED');
  }
  if (candidate.runtime.cpuExecutionClaimed !== true) blockers.push('CPU_EXECUTION_NOT_CLAIMED');
  if (candidate.runtime.within1200SecondsVerifiedOnAstra !== true) {
    blockers.push('RUNTIME_BUDGET_UNVERIFIED');
  }

  if (role === 'lead' && candidate.capabilities.leadStem !== true) {
    blockers.push('LEAD_RHYTHM_DISTINCTION_UNAVAILABLE');
  }
  if (role === 'rhythm' && candidate.capabilities.rhythmStem !== true) {
    blockers.push('LEAD_RHYTHM_DISTINCTION_UNAVAILABLE');
  }

  const normalizedBlockers = [...new Set(blockers)].sort();
  const inventoryQualified = candidate.capabilities.bassStem === true
    && candidate.capabilities.genericGuitarStem === true
    && candidate.rights.developmentEvaluationPermitted === true
    && candidate.rights.commercialInferencePermitted === true
    && candidate.rights.upstreamWeightRightsResolved === true
    && candidate.runtime.cpuExecutionClaimed === true;

  return {
    candidate: clone(candidate),
    role,
    inventoryQualified,
    developmentExecutionReady: false,
    customerDeliveryEligible: false,
    blockers: normalizedBlockers,
    downloadsArtifact: false,
    importsModel: false,
    invokesModel: false,
    opensAudio: false,
    performsNetworkAccess: false,
  };
}
