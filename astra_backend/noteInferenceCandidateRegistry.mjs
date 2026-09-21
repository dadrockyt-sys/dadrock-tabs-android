const CANDIDATES = Object.freeze({
  basic_pitch_0_4_0: Object.freeze({
    id: 'basic_pitch_0_4_0',
    family: 'basic-pitch',
    roleScope: ['generic-guitar', 'bass', 'multi-instrument-note-events'],
    noteOutput: 'midi-note-events',
    directStringFretOutput: false,
    leadRhythmDistinction: false,
    artifact: Object.freeze({
      packageVersion: '0.4.0',
      modelSha256: '3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676',
      requirementsLockSha256: 'a5614dbfad0be96aadc0d76297b6a59abe4e09c80bf2d6a484e53a14a58d38a7',
    }),
    rights: Object.freeze({
      softwareLicense: 'Apache-2.0',
      modelArtifactStatus: 'verified-existing-development-baseline',
      trainingDataCommercialReview: 'not-required-for-current-baseline-decision',
    }),
    operational: Object.freeze({
      cpuPathKnown: true,
      runtimeLockFrozen: true,
      developmentExecutionReady: true,
    }),
    blockers: Object.freeze([
      'GENERALIZATION_NOT_VALIDATED',
      'LEAD_RHYTHM_DISTINCTION_UNAVAILABLE_WITHOUT_SEPARATE_ROLE_EVIDENCE',
      'CUSTOMER_DELIVERY_NOT_AUTHORIZED',
    ]),
    customerDeliveryEligible: false,
  }),

  tabcnn_guitarprofx_dafx24: Object.freeze({
    id: 'tabcnn_guitarprofx_dafx24',
    family: 'tabcnn-guitarprofx',
    roleScope: ['generic-guitar'],
    noteOutput: 'six-string-fret-state-frames',
    directStringFretOutput: true,
    leadRhythmDistinction: false,
    source: Object.freeze({
      repository: 'robust-guitar-tabs/code',
      revision: 'f50309ad06dc734ddae5e3a0eda756fca221e2e7',
      repositoryLicense: 'CC0-1.0',
      repositoryLicenseBlob: '1625c1793607996fcfc46420e8aa2f3d2b7efd1e',
      repositoryReadmeBlob: '0ab556f527c038b589cf2c2b1a53750b052e97eb',
    }),
    artifact: Object.freeze({
      record: 'https://zenodo.org/records/11406378',
      file: 'best_TabCNN_tablature_trancription_model',
      publishedBytes: 3345122,
      publishedMd5: 'ce168b2cd426f81a2a78499214e40605',
      publishedLicense: 'CC-BY-4.0',
      sha256: '1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c',
      downloadedByAstra: true,
      artifactPersistedByAstra: false,
      identityReceipt: 'docs/astra/TABCNN_ARTIFACT_RECEIPT_V1.json',
    }),
    evidence: Object.freeze({
      intendedModel: 'TabCNN trained with GuitarProFX augmentation',
      guitarSpecific: true,
      polyphonicTablature: true,
      officialDepositIncludesWeights: true,
      externalOnnxConversionAcceptedAsAuthority: false,
    }),
    operational: Object.freeze({
      cpuPathKnown: false,
      runtimeLockFrozen: true,
      preprocessingIdentityFrozen: true,
      runtimePlatform: 'linux-x86_64',
      pythonVersion: '3.10.15',
      dependencyLockSha256: '0e711709b063a705ad11570f6b7ef4dfe5bcc2d433d98707a1a74897dbb25bc0',
      wheelManifestSha256: '0796acee36cea76e9784e602da190223a14a89907381882b401986763c371567',
      preprocessingReceiptSha256: '3a9474ccad43f1b06b76bc2e4b836642c355565a1d86a608aed8780a0bf8c333',
      expectedArtifactScale: 'small-single-digit-megabytes',
    }),
    blockers: Object.freeze([
      'LEGACY_PICKLE_COMPATIBILITY_PATH_NOT_VERIFIED',
      'CHECKPOINT_LICENSE_REVIEW_PENDING',
      'TRAINING_DATA_COMMERCIAL_RIGHTS_CHAIN_NOT_REVIEWED',
      'DEVELOPMENT_USE_NOT_AUTHORIZED',
      'CPU_RUNTIME_MEMORY_NOT_MEASURED',
      'NO_PROSPECTIVE_SECOND_SONG_NOTE_BENCHMARK',
      'LEAD_RHYTHM_DISTINCTION_UNAVAILABLE_WITHOUT_SEPARATE_ROLE_EVIDENCE',
      'CUSTOMER_DELIVERY_NOT_AUTHORIZED',
    ]),
    developmentExecutionReady: false,
    customerDeliveryEligible: false,
  }),

  mr_mt3: Object.freeze({
    id: 'mr_mt3',
    family: 'mr-mt3',
    roleScope: ['multi-instrument-note-events', 'generic-guitar', 'bass'],
    noteOutput: 'multi-track-midi-events',
    directStringFretOutput: false,
    leadRhythmDistinction: false,
    source: Object.freeze({
      repository: 'gudgud96/MR-MT3',
      revision: '826ea84a933f93cd707d11e91af711f1d19c8d79',
      repositoryLicense: 'MIT',
      repositoryLicenseBlob: 'c9c472bdc3f68c27698aef2cde08418ae0d1ab7b',
      repositoryReadmeBlob: 'b8d837a1bbbcb8a8ac72d5fc49926dd2c3c74b22',
    }),
    artifact: Object.freeze({
      modelRepository: 'gudgud1014/MR-MT3',
      selectedCheckpoint: 'continual/exp_segmemV2_prev_context=0_MT3_1e-5_ep100_norandom.ckpt',
      selectedCheckpointSha256: '74b2620009e9455a8f36da8a2b41950da4f12a229652a6cbd3ccb4333920c97f',
      selectedCheckpointBytes: 582511409,
      modelRepositoryLicenseMetadata: 'MIT',
      downloadedByAstra: false,
    }),
    evidence: Object.freeze({
      multiInstrument: true,
      pretrainedCheckpointPublished: true,
      repositoryReadmeTrainingInputs: ['Slakh', 'ComMU', 'NSynth'],
    }),
    operational: Object.freeze({
      cpuPathKnown: 'framework-support-only-not-benchmarked',
      runtimeLockFrozen: false,
      preprocessingIdentityFrozen: false,
      runtimeStack: 'PyTorch-plus-TensorFlow/T5 research stack',
    }),
    blockers: Object.freeze([
      'CHECKPOINT_BYTES_NOT_VERIFIED_BY_ASTRA',
      'TRAINING_DATA_COMMERCIAL_RIGHTS_CHAIN_NOT_REVIEWED',
      'RUNTIME_LOCK_NOT_FROZEN',
      'CPU_RUNTIME_MEMORY_NOT_MEASURED',
      'NO_PROSPECTIVE_SECOND_SONG_NOTE_BENCHMARK',
      'LEAD_RHYTHM_DISTINCTION_UNAVAILABLE_WITHOUT_SEPARATE_ROLE_EVIDENCE',
      'CUSTOMER_DELIVERY_NOT_AUTHORIZED',
    ]),
    developmentExecutionReady: false,
    customerDeliveryEligible: false,
  }),
});

export const PRIMARY_NEXT_NOTE_INFERENCE_CANDIDATE = 'tabcnn_guitarprofx_dafx24';
export const SECONDARY_NOTE_INFERENCE_CANDIDATE = 'mr_mt3';

export function listNoteInferenceCandidates() {
  return Object.values(CANDIDATES).map((candidate) => structuredClone(candidate));
}

export function getNoteInferenceCandidate(id) {
  const candidate = CANDIDATES[id];
  if (!candidate) throw new Error('UNKNOWN_NOTE_INFERENCE_CANDIDATE');
  return structuredClone(candidate);
}

export function buildNoteInferenceDevelopmentPlan({
  candidateId,
  requestedRole,
  inputRoleEvidenceStatus = 'unknown',
} = {}) {
  if (!['lead', 'rhythm', 'bass'].includes(requestedRole)) {
    throw new Error('requestedRole must be lead, rhythm, or bass.');
  }
  if (!['complete', 'abstained', 'unknown'].includes(inputRoleEvidenceStatus)) {
    throw new Error('inputRoleEvidenceStatus must be complete, abstained, or unknown.');
  }

  const candidate = getNoteInferenceCandidate(candidateId);
  const blockers = new Set(candidate.blockers ?? []);

  if ((requestedRole === 'lead' || requestedRole === 'rhythm')
      && inputRoleEvidenceStatus !== 'complete') {
    blockers.add('REQUESTED_GUITAR_ROLE_EVIDENCE_UNRESOLVED');
  }
  if (candidateId === 'tabcnn_guitarprofx_dafx24' && requestedRole === 'bass') {
    blockers.add('CANDIDATE_DOES_NOT_SUPPORT_BASS');
  }

  return {
    contract: {
      name: 'astra-note-inference-development-plan',
      version: 1,
      offlineOnly: true,
      invokesModel: false,
      performsNetworkAccess: false,
      downloadsArtifact: false,
      opensAudio: false,
    },
    candidateId,
    requestedRole,
    inputRoleEvidenceStatus,
    candidate,
    developmentExecutionReady: candidate.developmentExecutionReady === true
      && blockers.size === 0,
    blockers: [...blockers].sort(),
    customerDeliveryEligible: false,
  };
}
