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

  astra_guitartechs_tabcnn_v1: Object.freeze({
    id: 'astra_guitartechs_tabcnn_v1',
    family: 'astra-tabcnn-self-trained',
    roleScope: ['generic-guitar'],
    noteOutput: 'six-string-fret-state-frames',
    directStringFretOutput: true,
    leadRhythmDistinction: false,
    source: Object.freeze({
      dataset: 'Guitar-TECHS',
      record: 'https://zenodo.org/records/14963133',
      version: 'v1',
      license: 'CC-BY-4.0',
      trainingPlan: 'docs/astra/GUITARTECHS_TABCNN_TRAINING_CANDIDATE_V1.md',
    }),
    evidence: Object.freeze({
      synchronizedPerStringMidi: true,
      electricGuitarSpecific: true,
      multiplePerformers: true,
      multipleCapturePaths: true,
      p3FullMusicExcerpts: 12,
      blockedPublishedCheckpointUsedForInitialization: false,
    }),
    operational: Object.freeze({
      initialization: 'random-only',
      publishedDatasetIdentityFrozen: true,
      publishedDatasetManifestSha256: 'a3445d799c4a0b17a0078dac0c9387a0e676111367a5f07d608fd55bd8118e52',
      astraArchiveSha256Frozen: true,
      astraDevelopmentArchiveIdentityReceipt: 'docs/astra/GUITARTECHS_DEVELOPMENT_ARCHIVE_IDENTITY_V1.json',
      astraDevelopmentArchiveIdentityReceiptSha256: 'b6a4a577d7a447f4073dba85e6f3a4de7236544a6ed79df20b7f25d49c8602ac',
      trainingMediaDownloadedByAstra: true,
      trainingMediaPersistedByAstra: false,
      splitReceiptFrozen: true,
      splitReceiptSha256: 'd116556c13d250af28900bb1d73d2c0ccd3130246db8bdd2d6d387ac87be799a',
      inventoryEvidenceFrozen: true,
      inventoryEvidenceReceipt: 'docs/astra/GUITARTECHS_DEVELOPMENT_INVENTORY_EVIDENCE_V1.json',
      inventoryEvidenceReceiptSha256: '4d21d578a275587abe18d9f5382074fa9c33bd2f0698c5d10b340788de306bcd',
      fullInventoryWorkflowRunId: 35563511409,
      p2ChordsInventoryRecoveryRunId: 35563847021,
      extractedPerformanceGroupingVerified: true,
      captureViewGroupingVerified: true,
      stringTrackMappingFrozen: true,
      stringTrackMappingPolicy: 'explicit-track-name-never-positional-for-chords',
      techniqueMidiSemanticsFrozen: true,
      p1TuningVerified: true,
      p2TuningFullyVerified: true,
      p2TuningEvidenceReceipt: 'docs/astra/GUITARTECHS_P2_TUNING_EVIDENCE_V1.json',
      p2TuningEvidenceReceiptSha256: '5474eaccdf651c637dc7b3b2145098fe050714b77542b843742ac2f645702715',
      p2OpenMidiLowToHigh: [40, 45, 50, 55, 59, 64],
      p2DStringOpenMidiDirectlyObserved: false,
      p2DStringOpenMidiStructurallyVerified: true,
      labelContractFrozen: true,
      labelAlignmentTrainingContractSha256: '09436268922e0d24332b7e3234225d54a0f28e58e23b55ea71227eeab1b1e81f',
      alignmentPolicyFrozen: true,
      alignmentImplementationFrozen: true,
      alignmentImplementationReceipt: 'docs/astra/GUITARTECHS_ALIGNMENT_IMPLEMENTATION_V1.json',
      alignmentImplementationReceiptSha256: 'b33dd0fd220fcef4a459cc47277f48cf90c0acd320e523c3afcea5fc52a8a26f',
      alignmentScriptSha256: 'b084da0900acf9bd4ec61386a4a928350af0e138c9ed36ef3fbafb15539bc330',
      alignmentEvidenceFrozen: true,
      alignmentEvidenceReceipt: 'docs/astra/GUITARTECHS_DEVELOPMENT_ALIGNMENT_EVIDENCE_V1.json',
      alignmentEvidenceReceiptSha256: '8e65fda2a74f5f5af77ab62be3538715d9ec2c0dcd783de5837a56c5dd42b1ae',
      alignmentWorkflowRunId: 35565975272,
      alignmentAcceptedPrimaryCaptureCount: 256,
      alignmentAbstainedPrimaryCaptureCount: 80,
      alignmentAcceptedPrimaryCaptureKeysSha256: 'f520f5ffe3daf44da9bad1d145adaa1c9ff0bb662141b027f85b8c7bc827eabc',
      alignmentAbstainedPrimaryCaptureKeysSha256: 'b4221bdc8236eb5f7c3a1cc5dca0f0d5d931d6acff7a56210525f08c0d26c812',
      alignmentCorrectionVerified: true,
      trainingRuntimeFrozen: true,
      syntheticTrainingSmokePassed: true,
      syntheticTrainingSmokeReceiptSha256: 'ffb9c4178fe28683e2020083df96678a74e9a66413bb26d52aa5c01d07e49b9d',
      syntheticTrainingSmokeRunId: 35561780492,
      developmentAcquisitionContractFrozen: true,
      developmentAcquisitionContractSha256: '0d8ceae4938cc79b658498a74021a132358683a60f48d09358fcbe935a7bc02c',
      developmentMediaAcquisitionAuthorized: true,
      developmentMediaAcquisitionAuthorizationReceipt: 'docs/astra/GUITARTECHS_DEVELOPMENT_ACQUISITION_AUTHORIZATION_V1.json',
      developmentIdentityWorkflowRunId: 35562765028,
      developmentMetricSchemaFrozen: true,
      developmentMetricThresholdsFrozen: true,
      developmentMetricThresholdsReceipt: 'docs/astra/GUITARTECHS_DEVELOPMENT_METRIC_THRESHOLDS_V1.json',
      developmentMetricThresholdsReceiptSha256: 'fba6c921f17ec2ba3bace55b50823ea33bbf7828b61c0705da78b48ac8cfbe15',
      developmentMetricAcceptedCaptureKeysSha256: 'f520f5ffe3daf44da9bad1d145adaa1c9ff0bb662141b027f85b8c7bc827eabc',
      realTrainingAuthorized: true,
      realTrainingAuthorizationScope: 'guitar-techs-p1-p2-real-training-v1',
      realTrainingAuthorizationReceipt: 'docs/astra/GUITARTECHS_REAL_TRAINING_AUTHORIZATION_V1.json',
      realTrainingAuthorizationReceiptSha256: '175de606db2276dd745d697e1e996e6c533a7ad6542d258ed66e2a8bbb6ea0d0',
      paidComputeAuthorized: false,
      realTrainingImplementationFrozen: true,
      realTrainingImplementationReceipt: 'docs/astra/GUITARTECHS_REAL_TRAINING_IMPLEMENTATION_V1.json',
      realTrainingImplementationReceiptGitBlob: '159d6b60ed25582181efd1d036bf86b47bbd5563',
      realTrainingScriptGitBlob: 'd4a3dd99c4a2c3cda16c10bde1a5dc63f6380254',
      primaryAlignmentCorrectionMapGitBlob: '9090d465422ebf5d4fdf170693fe0936934f3073',
      realTrainingAuthorizationConsumed: true,
      realTrainingRunCompleted: true,
      realTrainingRunId: 35569391647,
      realTrainingDevelopmentResultReceipt: 'docs/astra/GUITARTECHS_REAL_TRAINING_DEVELOPMENT_RESULT_V1.json',
      realTrainingDevelopmentResultReceiptSha256: '3edfcf97766bef89ea56429a7385107d99868dc948d867251bcc5f9066a18112',
      p1TrainP2ModelSha256: '8dc70d94741e0b472e93481f498efafb7627445896594752b217e000f2832a83',
      p2TrainP1ModelSha256: 'd480cadf66fc0d98608c719252c34bdab4c3120252167e8786502b4332264841',
      modelTrained: true,
      developmentEvaluationPassed: false,
      v1TrainingFailureDiagnosisFrozen: true,
      v1TrainingFailureDiagnosisReceipt: 'docs/astra/GUITARTECHS_V1_TRAINING_FAILURE_DIAGNOSIS_V1.json',
      v1TrainingFailureDiagnosisReceiptSha256: 'c9ec7f099b57451bdaaa683c3d644a3f11e340b296916f9771702f4699462848',
      v2SequenceFramesFrozen: 200,
      v2CpuBudgetFrozen: true,
      v2CpuBudgetReceipt: 'docs/astra/GUITARTECHS_V2_CPU_BUDGET_V1.json',
      v2CpuBudgetReceiptSha256: '8705df7cde4456dc17b5973d84404981387a322ea195a3f995a72ae6b236b430',
      v2TrainingImplementationFrozen: true,
      v2TrainingImplementationReceipt: 'docs/astra/GUITARTECHS_V2_TRAINING_IMPLEMENTATION_V1.json',
      v2TrainingImplementationReceiptGitBlob: '32424b78d8423d6a87e37a8ad3f1698fa99073ab',
      v2TrainingScriptGitBlob: '4db5add96c58a8e54868ea06dacb1da724675163',
      v2SamplingScriptGitBlob: '9eb62fde56f592646077afa1e0ff3013a5dc6560',
      v2RealTrainingAuthorized: true,
      v2RealTrainingAuthorizationScope: 'guitar-techs-p1-p2-v2-real-training-v1',
      v2RealTrainingAuthorizationReceipt: 'docs/astra/GUITARTECHS_V2_REAL_TRAINING_AUTHORIZATION_V1.json',
      v2RealTrainingAuthorizationReceiptSha256: '0edfb4656675e31fce0c8cbd1ba42f37619e877b43793d3386781572dea8cb69',
      v2ModelTrained: false,
      v2DevelopmentEvaluationPassed: false,
      v2ResultAdmissionContractFrozen: true,
      v2ResultAdmissionContractReceipt: 'docs/astra/GUITARTECHS_V2_RESULT_ADMISSION_CONTRACT_V1.json',
      v2ResultAdmissionContractReceiptSha256: '58184ff3c60499c2ba6b89ef1042ea3c0eb20603d5a3a10e2eb11700de7a41db',
      p3OpeningEligible: false,
      p3FinalGateSealed: true,
    }),
    blockers: Object.freeze([
      'DEVELOPMENT_THRESHOLDS_NOT_MET',
      'P3_FINAL_GATE_SEALED',
      'LEAD_RHYTHM_DISTINCTION_UNAVAILABLE_WITHOUT_SEPARATE_ROLE_EVIDENCE',
      'CUSTOMER_DELIVERY_NOT_AUTHORIZED',
    ]),
    developmentExecutionReady: false,
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
      staticCheckpointInspectionReceiptSha256: '72ecf7e106bc69ce7ef4aa66888cb544535615ad3a9c8a6246bb09a460da3971',
      legacyPickleGlobalsStaticVerified: true,
      legacyImportSurfaceVerified: true,
      legacyImportSurfaceReceiptSha256: 'b9d795cd0ddfb7e070cba24e57e62a7c8d3723c2dad0b853f69c8efc36662805',
      expectedArtifactScale: 'small-single-digit-megabytes',
    }),
    blockers: Object.freeze([
      'CHECKPOINT_DESERIALIZATION_NOT_AUTHORIZED',
      'TRAINING_DATA_COMMERCIAL_RIGHTS_UNRESOLVED',
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

export const PRIMARY_NEXT_NOTE_INFERENCE_CANDIDATE = 'astra_guitartechs_tabcnn_v1';
export const BLOCKED_REFERENCE_NOTE_INFERENCE_CANDIDATE = 'tabcnn_guitarprofx_dafx24';
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
  if (requestedRole === 'bass' && !candidate.roleScope.includes('bass')) {
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
