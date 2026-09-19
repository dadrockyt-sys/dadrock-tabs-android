const ROLES = new Set(['lead', 'rhythm', 'bass']);
const SOURCE_CONTEXTS = new Set(['mixture', 'isolated-requested-role']);

const CANDIDATES = Object.freeze({
  'whole-mix-basic-pitch': Object.freeze({
    candidateId: 'whole-mix-basic-pitch',
    status: 'baseline-only',
    separation: 'none',
    eventInference: 'basic-pitch-unpinned-main-baseline',
    structureInference: 'none',
    archivedImplementationImported: false,
    capabilities: Object.freeze({
      bassStem: false,
      genericGuitarStem: false,
      leadRhythmDistinction: false,
      polyphonicNoteEvents: true,
      pitchBends: true,
    }),
    fixedBlockers: Object.freeze([
      'BASIC_PITCH_IDENTITY_UNPINNED',
      'MIXTURE_ROLE_EXTRACTION_UNAVAILABLE',
      'STRUCTURE_INFERENCE_UNAVAILABLE',
      'REAL_DEVELOPMENT_EVIDENCE_MISSING',
    ]),
  }),
  'htdemucs6s-basic-pitch': Object.freeze({
    candidateId: 'htdemucs6s-basic-pitch',
    status: 'preferred-development-candidate',
    separation: 'htdemucs_6s-via-audio-separator-0.30.2',
    eventInference: 'basic-pitch-unpinned-main-baseline',
    structureInference: 'none',
    archivedImplementationImported: false,
    capabilities: Object.freeze({
      bassStem: true,
      genericGuitarStem: true,
      leadRhythmDistinction: false,
      polyphonicNoteEvents: true,
      pitchBends: true,
    }),
    fixedBlockers: Object.freeze([
      'BASIC_PITCH_IDENTITY_UNPINNED',
      'DEMUCS_WEIGHT_IDENTITY_AND_TERMS_UNRESOLVED',
      'CPU_RUNTIME_TARGET_UNPROVEN_3300_SECOND_LEGACY_ALLOWANCE',
      'STRUCTURE_INFERENCE_UNAVAILABLE',
      'REAL_DEVELOPMENT_EVIDENCE_MISSING',
    ]),
  }),
  'v5-register-gate': Object.freeze({
    candidateId: 'v5-register-gate',
    status: 'rejected-role-evidence',
    separation: 'none-register-filter-only',
    eventInference: 'archived-protected-v71',
    structureInference: 'archived',
    archivedImplementationImported: false,
    capabilities: Object.freeze({
      bassStem: false,
      genericGuitarStem: false,
      leadRhythmDistinction: false,
      polyphonicNoteEvents: true,
      pitchBends: null,
    }),
    fixedBlockers: Object.freeze([
      'CANDIDATE_REJECTED',
      'REGISTER_IS_NOT_ROLE_EVIDENCE',
      'ARCHIVED_PROTECTED_ANALYZER_DEPENDENCY',
    ]),
  }),
});

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function unique(values) {
  return [...new Set(values)].sort();
}

export function listAstraAudioEngineCandidates() {
  return Object.values(CANDIDATES).map(clone);
}

export function planAstraAudioEngine({ candidateId, role, sourceContext = 'mixture' } = {}) {
  const candidate = CANDIDATES[candidateId];
  if (!candidate) throw new Error('Unknown Astra audio-engine candidate.');
  if (!ROLES.has(role)) throw new Error('role must be lead, rhythm, or bass.');
  if (!SOURCE_CONTEXTS.has(sourceContext)) {
    throw new Error('sourceContext must be mixture or isolated-requested-role.');
  }

  const blockers = [...candidate.fixedBlockers];
  let roleEvidence = 'unavailable';
  let selectedStem = null;

  if (sourceContext === 'isolated-requested-role') {
    roleEvidence = 'caller-declared-isolated-role-requires-authorized-provenance';
    selectedStem = 'input';
    blockers.push('ISOLATED_ROLE_PROVENANCE_REQUIRED');
  } else if (candidateId === 'htdemucs6s-basic-pitch' && role === 'bass') {
    roleEvidence = 'direct-bass-stem-candidate';
    selectedStem = 'bass';
  } else if (candidateId === 'htdemucs6s-basic-pitch' && (role === 'lead' || role === 'rhythm')) {
    roleEvidence = 'generic-guitar-stem-only';
    selectedStem = 'guitar';
    blockers.push('LEAD_RHYTHM_DISTINCTION_UNAVAILABLE');
  } else if (sourceContext === 'mixture') {
    roleEvidence = 'whole-mixture-only';
    selectedStem = 'mixture';
  }

  if (candidate.status === 'baseline-only') blockers.push('BASELINE_NOT_PRODUCT_CANDIDATE');

  const stageGraph = [
    { stage: 'input', implementation: 'authorized-audio-reference', planned: true },
    {
      stage: 'extraction',
      implementation: candidate.separation,
      selectedStem,
      roleEvidence,
      planned: candidate.separation !== 'none-register-filter-only',
    },
    {
      stage: 'events',
      implementation: candidate.eventInference,
      planned: candidate.status !== 'rejected-role-evidence',
    },
    {
      stage: 'structure',
      implementation: candidate.structureInference,
      planned: false,
    },
    { stage: 'tablature', implementation: 'astra-backend-deterministic-pipeline-v1', planned: true },
    { stage: 'delivery', implementation: 'astra-analysis-contract-v1', planned: true },
  ];

  const normalizedBlockers = unique(blockers);
  return {
    planContract: { name: 'jimmy-paige-astra-audio-engine-plan', version: 1 },
    candidateId,
    candidateStatus: candidate.status,
    role,
    sourceContext,
    roleEvidence,
    selectedStem,
    capabilities: clone(candidate.capabilities),
    stageGraph,
    blockers: normalizedBlockers,
    developmentExecutionReady: false,
    customerDeliveryEligible: false,
    invokesModel: false,
    opensAudio: false,
    performsNetworkAccess: false,
    reason: normalizedBlockers.length
      ? 'STATIC_PREFLIGHT_BLOCKED_PENDING_IDENTITY_RIGHTS_RUNTIME_AND_EVIDENCE'
      : 'STATIC_PREFLIGHT_COMPLETE',
  };
}

