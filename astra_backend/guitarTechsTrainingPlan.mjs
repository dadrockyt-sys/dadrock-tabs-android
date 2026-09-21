const GUITAR_TECHS_PLAN = Object.freeze({
  contract: Object.freeze({
    name: 'astra-guitar-techs-tabcnn-training-plan',
    version: 1,
    invokesModel: false,
    downloadsTrainingMedia: false,
    opensTrainingMedia: false,
    trainsModel: false,
    mutatesProduction: false,
    grantsCustomerDelivery: false,
  }),
  candidateId: 'astra_guitartechs_tabcnn_v1',
  architecture: Object.freeze({
    family: 'tabcnn-compatible',
    initialization: 'random-only',
    forbiddenInitializationArtifact: 'tabcnn_guitarprofx_dafx24',
    output: 'six-string-fret-state-frames',
    roleScope: ['generic-guitar'],
  }),
  dataset: Object.freeze({
    name: 'Guitar-TECHS',
    record: 'https://zenodo.org/records/14963133',
    version: 'v1',
    license: 'CC-BY-4.0',
    publishedIdentityManifest: 'docs/astra/GUITARTECHS_DATASET_MANIFEST_V1.json',
    publishedIdentityManifestSha256: 'a3445d799c4a0b17a0078dac0c9387a0e676111367a5f07d608fd55bd8118e52',
    authoritativeLicenseEvidence: Object.freeze([
      'https://guitar-techs.github.io/',
      'https://zenodo.org/records/14963133',
    ]),
    publishedArchives: Object.freeze({
      P1: Object.freeze([
        Object.freeze({ file: 'P1_chords.zip', bytes: 981741162, md5: 'be9ef8bbdceb1912d565254e607a6d94' }),
        Object.freeze({ file: 'P1_scales.zip', bytes: 453349723, md5: '9c0b98e8fb42a522df727ea8bf545e4f' }),
        Object.freeze({ file: 'P1_singlenotes.zip', bytes: 108626613, md5: 'ca0c4674dde3805574685a313f7c39eb' }),
        Object.freeze({ file: 'P1_techniques.zip', bytes: 326280863, md5: '18634a41a6db5a8de10d07eb3122a872' }),
      ]),
      P2: Object.freeze([
        Object.freeze({ file: 'P2_chords.zip', bytes: 1150819056, md5: 'eb6f74dd19162237189281688ad7ad2e' }),
        Object.freeze({ file: 'P2_scales.zip', bytes: 471254783, md5: '96664853872f51e5f8aa4447313b7cf5' }),
        Object.freeze({ file: 'P2_singlenotes.zip', bytes: 116133457, md5: '40fbf03d8b04bb2cf42df20f36dc2254' }),
        Object.freeze({ file: 'P2_techniques.zip', bytes: 395839610, md5: 'f4189251ce50be25f06a173b2c2bba00' }),
      ]),
      P3: Object.freeze([
        Object.freeze({ file: 'P3_music.zip', bytes: 129505089, md5: '071ba80aecf00f4a31fbd167b3f22198' }),
      ]),
    }),
  }),
  splitPolicy: Object.freeze({
    receipt: 'docs/astra/GUITARTECHS_SPLIT_RECEIPT_V1.json',
    receiptSha256: 'd116556c13d250af28900bb1d73d2c0ccd3130246db8bdd2d6d387ac87be799a',
    groupingUnit: 'underlying-performance',
    keepAllCaptureChannelsTogether: true,
    randomClipSplitForbidden: true,
    developmentFolds: Object.freeze([
      Object.freeze({
        id: 'p1-train-p2-validate',
        trainPerformers: Object.freeze(['P1']),
        validationPerformers: Object.freeze(['P2']),
      }),
      Object.freeze({
        id: 'p2-train-p1-validate',
        trainPerformers: Object.freeze(['P2']),
        validationPerformers: Object.freeze(['P1']),
      }),
    ]),
    hyperparametersFreezeBeforeFinalFit: true,
    finalFitPerformers: Object.freeze(['P1', 'P2']),
    sealedGeneralizationGate: Object.freeze({
      performers: Object.freeze(['P3']),
      archive: 'P3_music.zip',
      content: '12 full musical excerpts',
      mayOpenBeforeFreeze: false,
      purpose: 'single-use final source-disjoint generalization evaluation',
    }),
  }),
  contractReceipt: Object.freeze({
    path: 'docs/astra/GUITARTECHS_LABEL_ALIGNMENT_TRAINING_CONTRACT_V1.json',
    sha256: '09436268922e0d24332b7e3234225d54a0f28e58e23b55ea71227eeab1b1e81f',
  }),
  labelPolicy: Object.freeze({
    source: 'synchronized-per-string-midi',
    temporalAlignmentCorrectionRequired: true,
    publishedMaxAlignmentUncertaintyMs: 100,
    tuningMetadataMustBeFrozenBeforeFretConversion: true,
    silentClassRequired: true,
  }),
  preprocessingPolicy: Object.freeze({
    reuseFrozenTabcnnContractAsStartingPoint: true,
    sourceParityRequired: true,
    parameterRetuningAllowedOnlyInsideDevelopmentFolds: true,
    p3GateMayNotInfluencePreprocessing: true,
  }),
  blockers: Object.freeze([
    'DATASET_ASTRA_SHA256_NOT_FROZEN',
    'TRAINING_MEDIA_NOT_ACQUIRED',
    'EXTRACTED_PERFORMANCE_GROUPING_NOT_VERIFIED',
    'ALIGNMENT_CORRECTION_NOT_VERIFIED',
    'TUNING_METADATA_NOT_FROZEN',
    'SYNTHETIC_TRAINING_SMOKE_PENDING',
    'DEVELOPMENT_METRIC_THRESHOLDS_NOT_FROZEN',
    'TRAINING_NOT_AUTHORIZED',
    'MODEL_NOT_TRAINED',
    'P3_FINAL_GATE_SEALED',
    'CUSTOMER_DELIVERY_NOT_AUTHORIZED',
  ]),
  developmentExecutionReady: false,
  customerDeliveryEligible: false,
});

export function getGuitarTechsTrainingPlan() {
  return structuredClone(GUITAR_TECHS_PLAN);
}

export function assertGuitarTechsPlanIntegrity(plan = getGuitarTechsTrainingPlan()) {
  if (plan.architecture.initialization !== 'random-only') {
    throw new Error('BLOCKED_CHECKPOINT_INITIALIZATION_FORBIDDEN');
  }
  if (plan.splitPolicy.keepAllCaptureChannelsTogether !== true
      || plan.splitPolicy.randomClipSplitForbidden !== true) {
    throw new Error('CAPTURE_CHANNEL_LEAKAGE_RISK');
  }
  if (plan.splitPolicy.sealedGeneralizationGate.performers.join(',') !== 'P3'
      || plan.splitPolicy.sealedGeneralizationGate.mayOpenBeforeFreeze !== false) {
    throw new Error('P3_FINAL_GATE_MUST_REMAIN_SEALED');
  }
  return true;
}
