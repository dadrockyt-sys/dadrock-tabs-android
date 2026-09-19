const REVIEW = Object.freeze({
  id: 'banquet-query-bandit-2025-07-29',
  project: 'Banquet / query-bandit',
  source: Object.freeze({
    repository: 'kwatcharasupat/query-bandit',
    revision: '79ed5bb75e5c3a40cd319d9d990cee913fc65c26',
    repositoryLicense: 'MIT',
    licenseBlob: '227afbe7329cc553d2335a4cf5fd099473e9aad8',
    readmeBlob: 'd7287cebeeb4abbecad6bf7174a2430f8c720298',
    inferenceSourceBlob: '9b4d19e75817187a70231ca0a7552d5633c0a7d8',
    trainingConfigBlob: '21b67e06ba8487218bfef1c4780adf17ce2ecc95',
    modelConfigBlob: '0b157abc2f64b334803b6d89fd7b6ae28a0d5b31',
    queryEncoderBlob: 'a213f7854800d25349ceb584073ae7d748d9877c',
  }),
  artifact: Object.freeze({
    repository: 'Zenodo',
    recordId: '13694558',
    doi: '10.5281/zenodo.13694558',
    recommendedFile: 'ev-pre-aug.ckpt',
    publishedMd5: '4dfb91d6d27c2dfd4992a15070915541',
    publishedSizeMb: 645.5,
    sha256VerifiedByAstra: null,
    downloadedByAstra: false,
  }),
  capabilities: Object.freeze({
    bassClasses: Object.freeze(['bass_guitar', 'bass_synthesizer']),
    guitarClasses: Object.freeze([
      'clean_electric_guitar',
      'distorted_electric_guitar',
      'acoustic_guitar',
    ]),
    genericBassPossible: true,
    genericGuitarPossible: true,
    leadStem: false,
    rhythmStem: false,
  }),
  runtime: Object.freeze({
    explicitCpuPathInSource: true,
    cpuControl: 'use_cuda=false',
    sampleRateHz: 44100,
    queryLengthSeconds: 10,
    runtimeBudgetVerifiedOnAstra: false,
  }),
  queryDependency: Object.freeze({
    separateQueryAudioRequired: true,
    authorizedReferenceQueryLibraryDefined: false,
    referenceBlindProductPathSatisfied: false,
    labelOnlyPathIdentifiedInReviewedSource: false,
    precomputedEmbeddingProductPathFrozen: false,
  }),
  rights: Object.freeze({
    repositorySoftwareCommercialUsePermitted: true,
    exactCheckpointLicenseIdentifiedByAstra: false,
    developmentEvaluationPermittedForCheckpoint: false,
    commercialInferencePermittedForCheckpoint: false,
    trainingDataCommercialChainReviewed: false,
  }),
});

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export function getBanquetIndependentCandidateReview() {
  return clone(REVIEW);
}

export function evaluateBanquetIndependentCandidate({ role = 'bass' } = {}) {
  if (!['bass', 'lead', 'rhythm'].includes(role)) {
    throw new Error('role must be bass, lead, or rhythm.');
  }

  const blockers = [];
  if (REVIEW.artifact.sha256VerifiedByAstra === null) {
    blockers.push('BANQUET_CHECKPOINT_SHA256_NOT_VERIFIED_ON_ASTRA');
  }
  if (!REVIEW.rights.exactCheckpointLicenseIdentifiedByAstra) {
    blockers.push('BANQUET_CHECKPOINT_LICENSE_UNRESOLVED');
  }
  if (!REVIEW.rights.developmentEvaluationPermittedForCheckpoint) {
    blockers.push('BANQUET_DEVELOPMENT_RIGHTS_UNRESOLVED');
  }
  if (!REVIEW.rights.commercialInferencePermittedForCheckpoint) {
    blockers.push('BANQUET_COMMERCIAL_INFERENCE_RIGHTS_UNRESOLVED');
  }
  if (!REVIEW.rights.trainingDataCommercialChainReviewed) {
    blockers.push('BANQUET_TRAINING_RIGHTS_CHAIN_UNREVIEWED');
  }
  if (!REVIEW.runtime.runtimeBudgetVerifiedOnAstra) {
    blockers.push('RUNTIME_BUDGET_UNVERIFIED');
  }
  if (REVIEW.queryDependency.separateQueryAudioRequired
      && !REVIEW.queryDependency.authorizedReferenceQueryLibraryDefined) {
    blockers.push('AUTHORIZED_QUERY_AUDIO_NOT_DEFINED');
  }
  if (!REVIEW.queryDependency.referenceBlindProductPathSatisfied) {
    blockers.push('REFERENCE_BLIND_PRODUCT_PATH_UNRESOLVED');
  }
  if (role === 'lead' || role === 'rhythm') {
    blockers.push('LEAD_RHYTHM_DISTINCTION_UNAVAILABLE');
  }

  return {
    review: clone(REVIEW),
    role,
    technicallyPromisingForBassAndGenericGuitar: true,
    developmentExecutionReady: false,
    customerDeliveryEligible: false,
    blockers: [...new Set(blockers)].sort(),
    downloadsArtifact: false,
    importsModel: false,
    invokesModel: false,
    opensAudio: false,
    performsNetworkAccess: false,
  };
}
