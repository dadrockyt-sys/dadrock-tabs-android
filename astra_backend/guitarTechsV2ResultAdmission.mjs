import { evaluateGuitarTechsDevelopmentMetrics } from './guitarTechsDevelopmentMetricThresholds.mjs';

const CONTRACT = Object.freeze({
  receiptSha256: '58184ff3c60499c2ba6b89ef1042ea3c0eb20603d5a3a10e2eb11700de7a41db',
  authorizationReceiptSha256: '0edfb4656675e31fce0c8cbd1ba42f37619e877b43793d3386781572dea8cb69',
  thresholdsReceiptSha256: 'fba6c921f17ec2ba3bace55b50823ea33bbf7828b61c0705da78b48ac8cfbe15',
  alignmentAcceptedCaptureKeysSha256: 'f520f5ffe3daf44da9bad1d145adaa1c9ff0bb662141b027f85b8c7bc827eabc',
  v2CpuBudgetReceiptSha256: '8705df7cde4456dc17b5973d84404981387a322ea195a3f995a72ae6b236b430',
  failureDiagnosisReceiptSha256: 'c9ec7f099b57451bdaaa683c3d644a3f11e340b296916f9771702f4699462848',
  candidateId: 'astra_guitartechs_tabcnn_v2',
  seed: 20260921,
  preparedCaptureCounts: Object.freeze({P1: 136, P2: 120}),
  folds: Object.freeze({
    'p1-train-p2-validate': Object.freeze({
      trainPerformer: 'P1', validationPerformer: 'P2', epochs: 1000, optimizerSteps: 2000,
      sequenceFrames: 200, batchSequences: 32, microbatchSequences: 1,
      validationCheckpoints: 50, trainingPerformanceCount: 41,
      validationCaptureCount: 120, supervisedFramePositions: 8200000,
    }),
    'p2-train-p1-validate': Object.freeze({
      trainPerformer: 'P2', validationPerformer: 'P1', epochs: 1000, optimizerSteps: 2000,
      sequenceFrames: 200, batchSequences: 32, microbatchSequences: 1,
      validationCheckpoints: 50, trainingPerformanceCount: 40,
      validationCaptureCount: 136, supervisedFramePositions: 8000000,
    }),
  }),
});

export const GUITAR_TECHS_V2_RESULT_ADMISSION_CONTRACT_SHA256 = CONTRACT.receiptSha256;

export function getGuitarTechsV2ResultAdmissionContract() {
  return structuredClone(CONTRACT);
}

function validateBalance(name, balance, expectedPerformances, blockers) {
  if (!balance || typeof balance !== 'object') {
    blockers.push(`${name}_PRETRAINING_LABEL_BALANCE_MISSING`);
    return;
  }
  if (balance.canonicalPerformanceCount !== expectedPerformances) {
    blockers.push(`${name}_PRETRAINING_PERFORMANCE_COUNT_MISMATCH`);
  }
  if (!(typeof balance.activeFractionOfValid === 'number' && Number.isFinite(balance.activeFractionOfValid)
      && balance.activeFractionOfValid > 0 && balance.activeFractionOfValid <= 1)) {
    blockers.push(`${name}_PRETRAINING_ACTIVE_FRACTION_INVALID`);
  }
  if (!Array.isArray(balance.perString) || balance.perString.length !== 6
      || balance.perString.some((row) => !(row && Number.isFinite(row.active) && row.active > 0))) {
    blockers.push(`${name}_PRETRAINING_STRING_ACTIVITY_INVALID`);
  }
  const required = ['chords', 'scales', 'singlenotes', 'PalmMute'];
  if (!balance.perContent || typeof balance.perContent !== 'object'
      || required.some((content) => !(balance.perContent[content]
        && Number.isFinite(balance.perContent[content].active)
        && balance.perContent[content].active > 0))) {
    blockers.push(`${name}_PRETRAINING_CONTENT_ACTIVITY_INVALID`);
  }
}

function validateFold(name, fold, expected, blockers) {
  if (!fold || typeof fold !== 'object') {
    blockers.push(`${name}_RESULT_MISSING`);
    return;
  }
  if (fold.schema !== 'astra-guitar-techs-real-training-fold-v2'
      || fold.candidateId !== CONTRACT.candidateId
      || fold.fold !== name
      || fold.trainPerformer !== expected.trainPerformer
      || fold.validationPerformer !== expected.validationPerformer) {
    blockers.push(`${name}_IDENTITY_MISMATCH`);
  }
  for (const [field, value] of Object.entries({
    seed: CONTRACT.seed,
    epochs: expected.epochs,
    optimizerSteps: expected.optimizerSteps,
    sequenceFrames: expected.sequenceFrames,
    batchSequences: expected.batchSequences,
    microbatchSequences: expected.microbatchSequences,
    validationCheckpoints: expected.validationCheckpoints,
    trainingPerformanceCount: expected.trainingPerformanceCount,
    validationCaptureCount: expected.validationCaptureCount,
    supervisedFramePositions: expected.supervisedFramePositions,
  })) {
    if (fold[field] !== value) blockers.push(`${name}_${field.toUpperCase()}_MISMATCH`);
  }
  if (!fold.preparedCaptureCounts
      || fold.preparedCaptureCounts.P1 !== CONTRACT.preparedCaptureCounts.P1
      || fold.preparedCaptureCounts.P2 !== CONTRACT.preparedCaptureCounts.P2) {
    blockers.push(`${name}_PREPARED_CAPTURE_COUNTS_MISMATCH`);
  }
  if (fold.budgetReceiptSha256 !== CONTRACT.v2CpuBudgetReceiptSha256
      || fold.failureDiagnosisReceiptSha256 !== CONTRACT.failureDiagnosisReceiptSha256) {
    blockers.push(`${name}_SOURCE_RECEIPT_MISMATCH`);
  }
  if (!fold.guards || fold.guards.p3Opened !== false
      || fold.guards.publishedCheckpointLoaded !== false
      || fold.guards.paidComputeUsed !== false
      || fold.guards.customerDeliveryEligible !== false) {
    blockers.push(`${name}_GUARD_VIOLATION`);
  }
  if (!fold.selected || !Number.isInteger(fold.selected.epoch)
      || fold.selected.epoch < 20 || fold.selected.epoch > 1000
      || fold.selected.epoch % 20 !== 0) {
    blockers.push(`${name}_SELECTED_CHECKPOINT_INVALID`);
  }
  if (!fold.fullValidationMetrics || typeof fold.fullValidationMetrics !== 'object') {
    blockers.push(`${name}_FULL_VALIDATION_METRICS_MISSING`);
  }
  validateBalance(name, fold.pretrainingLabelBalance, expected.trainingPerformanceCount, blockers);
}

export function evaluateGuitarTechsV2TrainingResults({
  admissionContractSha256,
  authorizationReceiptSha256,
  p1TrainP2Validate,
  p2TrainP1Validate,
  p3Opened = false,
  customerDeliveryRequested = false,
} = {}) {
  const blockers = [];
  if (admissionContractSha256 !== CONTRACT.receiptSha256) blockers.push('GUITAR_TECHS_V2_RESULT_ADMISSION_CONTRACT_MISMATCH');
  if (authorizationReceiptSha256 !== CONTRACT.authorizationReceiptSha256) blockers.push('GUITAR_TECHS_V2_AUTHORIZATION_RECEIPT_MISMATCH');
  validateFold('p1-train-p2-validate', p1TrainP2Validate, CONTRACT.folds['p1-train-p2-validate'], blockers);
  validateFold('p2-train-p1-validate', p2TrainP1Validate, CONTRACT.folds['p2-train-p1-validate'], blockers);
  if (p3Opened === true) blockers.push('GUITAR_TECHS_P3_SEALED');
  if (customerDeliveryRequested === true) blockers.push('CUSTOMER_DELIVERY_NOT_AUTHORIZED');

  let metricDecision = null;
  if (blockers.length === 0) {
    metricDecision = evaluateGuitarTechsDevelopmentMetrics({
      thresholdReceiptSha256: CONTRACT.thresholdsReceiptSha256,
      alignmentEvidenceReceiptSha256: '8e65fda2a74f5f5af77ab62be3538715d9ec2c0dcd783de5837a56c5dd42b1ae',
      acceptedCaptureKeysSha256: CONTRACT.alignmentAcceptedCaptureKeysSha256,
      p1TrainP2Validate: p1TrainP2Validate.fullValidationMetrics,
      p2TrainP1Validate: p2TrainP1Validate.fullValidationMetrics,
      p3Opened: false,
    });
    blockers.push(...metricDecision.blockers);
  }

  const uniqueBlockers = [...new Set(blockers)].sort();
  const developmentAccepted = uniqueBlockers.length === 0 && metricDecision?.accepted === true;
  return {
    evidenceAccepted: !uniqueBlockers.some((b) => b.includes('MISMATCH')
      || b.includes('MISSING') || b.includes('INVALID') || b.includes('VIOLATION')),
    developmentAccepted,
    blockers: uniqueBlockers,
    modelTrainingEvidenceComplete: blockers.length === (metricDecision?.blockers?.length || 0),
    p3OpeningEligibleForSeparateAuthorization: developmentAccepted,
    p3OpeningAuthorizedByThisContract: false,
    customerDeliveryEligible: false,
  };
}
