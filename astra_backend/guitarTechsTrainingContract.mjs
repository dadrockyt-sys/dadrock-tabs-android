const CONTRACT = Object.freeze({
  receiptSha256: '09436268922e0d24332b7e3234225d54a0f28e58e23b55ea71227eeab1b1e81f',
  alignment: Object.freeze({
    lagMinMs: -100,
    lagMaxMs: 100,
    lagStepMs: 1,
    matchToleranceMs: 20,
    minimumMidiOnsetGroups: 30,
    minimumMatchedFraction: 0.8,
    maximumMedianAbsoluteResidualMs: 10,
    bootstrapStrata: 5,
    maximumBootstrapLagMadMs: 5,
    maximumAbsoluteAppliedCorrectionMs: 100,
    p3MayInfluenceAlignment: false,
  }),
  training: Object.freeze({
    initialization: 'random-only',
    optimizer: 'Adadelta',
    learningRate: 1.0,
    batchSize: 32,
    maxIterationsPerFold: 2500,
    validationCheckpointsPerFold: 50,
    seed: 20260921,
    dependencyLockSha256: '0e711709b063a705ad11570f6b7ef4dfe5bcc2d433d98707a1a74897dbb25bc0',
    wheelManifestSha256: '0796acee36cea76e9784e602da190223a14a89907381882b401986763c371567',
    paidComputeAuthorized: false,
    realTrainingAuthorized: false,
  }),
  metrics: Object.freeze([
    'onset-string-fret-precision',
    'onset-string-fret-recall',
    'onset-string-fret-f1',
    'note-event-completeness',
    'frame-string-fret-accuracy',
    'abstention-rate',
    'per-content-class-results',
    'cross-performer-consistency',
  ]),
});

export function getGuitarTechsLabelAlignmentTrainingContract() {
  return structuredClone(CONTRACT);
}

export function evaluateGuitarTechsPretrainingReadiness({
  publishedManifestSha256,
  splitReceiptSha256,
  stringTrackMapVerified = false,
  tuningMetadataFrozen = false,
  alignmentCorrectionVerified = false,
  syntheticBackwardSmokePassed = false,
  developmentMetricThresholdsFrozen = false,
  trainingAuthorized = false,
  p3Opened = false,
} = {}) {
  const blockers = [];
  if (publishedManifestSha256 !== 'a3445d799c4a0b17a0078dac0c9387a0e676111367a5f07d608fd55bd8118e52') {
    blockers.push('PUBLISHED_DATASET_MANIFEST_MISMATCH');
  }
  if (splitReceiptSha256 !== 'd116556c13d250af28900bb1d73d2c0ccd3130246db8bdd2d6d387ac87be799a') {
    blockers.push('SPLIT_RECEIPT_MISMATCH');
  }
  if (stringTrackMapVerified !== true) blockers.push('STRING_TRACK_MAP_UNVERIFIED');
  if (tuningMetadataFrozen !== true) blockers.push('TUNING_METADATA_UNFROZEN');
  if (alignmentCorrectionVerified !== true) blockers.push('ALIGNMENT_CORRECTION_UNVERIFIED');
  if (syntheticBackwardSmokePassed !== true) blockers.push('SYNTHETIC_BACKWARD_SMOKE_PENDING');
  if (developmentMetricThresholdsFrozen !== true) blockers.push('DEVELOPMENT_METRIC_THRESHOLDS_UNFROZEN');
  if (trainingAuthorized !== true) blockers.push('REAL_TRAINING_NOT_AUTHORIZED');
  if (p3Opened === true) blockers.push('P3_OPENED_BEFORE_DEVELOPMENT_FREEZE');

  const uniqueBlockers = [...new Set(blockers)].sort();
  return {
    contract: {
      name: 'astra-guitar-techs-pretraining-readiness',
      version: 1,
      downloadsMedia: false,
      opensMedia: false,
      trainsModel: false,
      grantsCustomerDelivery: false,
    },
    expected: getGuitarTechsLabelAlignmentTrainingContract(),
    readyForRealTraining: uniqueBlockers.length === 0,
    blockers: uniqueBlockers,
    customerDeliveryEligible: false,
  };
}
