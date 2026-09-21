const THRESHOLDS = Object.freeze({
  receiptSha256: 'fba6c921f17ec2ba3bace55b50823ea33bbf7828b61c0705da78b48ac8cfbe15',
  alignmentEvidenceReceiptSha256: '8e65fda2a74f5f5af77ab62be3538715d9ec2c0dcd783de5837a56c5dd42b1ae',
  acceptedCaptureKeysSha256: 'f520f5ffe3daf44da9bad1d145adaa1c9ff0bb662141b027f85b8c7bc827eabc',
  onsetToleranceMs: 50,
  eachFold: Object.freeze({
    precisionMin: 0.75,
    recallMin: 0.60,
    f1Min: 0.67,
    completenessMin: 0.60,
    frameAccuracyMin: 0.70,
    abstentionRateMax: 0.10,
    eachContentF1Min: 0.55,
  }),
  aggregate: Object.freeze({
    macroF1Min: 0.70,
    macroCompletenessMin: 0.65,
    f1GapMax: 0.10,
    frameAccuracyGapMax: 0.10,
  }),
  contentClasses: Object.freeze(['chords', 'scales', 'singlenotes', 'PalmMute']),
});

export const GUITAR_TECHS_DEVELOPMENT_METRIC_THRESHOLDS_RECEIPT_SHA256 = THRESHOLDS.receiptSha256;

export function getGuitarTechsDevelopmentMetricThresholds() {
  return structuredClone(THRESHOLDS);
}

function finiteUnit(value) {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 1;
}

function validateFold(name, fold, blockers) {
  if (!fold || typeof fold !== 'object') {
    blockers.push(`${name}_MISSING`);
    return;
  }
  for (const [field, suffix] of [
    ['precision', 'PRECISION_INVALID'],
    ['recall', 'RECALL_INVALID'],
    ['f1', 'F1_INVALID'],
    ['completeness', 'COMPLETENESS_INVALID'],
    ['frameAccuracy', 'FRAME_ACCURACY_INVALID'],
    ['abstentionRate', 'ABSTENTION_INVALID'],
  ]) {
    if (!finiteUnit(fold[field])) blockers.push(`${name}_${suffix}`);
  }
  if (!fold.contentF1 || typeof fold.contentF1 !== 'object') {
    blockers.push(`${name}_CONTENT_F1_MISSING`);
  } else {
    for (const content of THRESHOLDS.contentClasses) {
      if (!finiteUnit(fold.contentF1[content])) blockers.push(`${name}_${content.toUpperCase()}_F1_INVALID`);
    }
  }
}

export function evaluateGuitarTechsDevelopmentMetrics({
  thresholdReceiptSha256,
  alignmentEvidenceReceiptSha256,
  acceptedCaptureKeysSha256,
  p1TrainP2Validate,
  p2TrainP1Validate,
  p3Opened = false,
} = {}) {
  const blockers = [];
  if (thresholdReceiptSha256 !== THRESHOLDS.receiptSha256) blockers.push('GUITAR_TECHS_METRIC_THRESHOLD_RECEIPT_MISMATCH');
  if (alignmentEvidenceReceiptSha256 !== THRESHOLDS.alignmentEvidenceReceiptSha256
      || acceptedCaptureKeysSha256 !== THRESHOLDS.acceptedCaptureKeysSha256) {
    blockers.push('GUITAR_TECHS_METRIC_EVALUATION_POPULATION_MISMATCH');
  }
  validateFold('P1_TRAIN_P2_VALIDATE', p1TrainP2Validate, blockers);
  validateFold('P2_TRAIN_P1_VALIDATE', p2TrainP1Validate, blockers);
  if (p3Opened === true) blockers.push('GUITAR_TECHS_P3_SEALED');

  if (blockers.length === 0) {
    const folds = [
      ['P1_TRAIN_P2_VALIDATE', p1TrainP2Validate],
      ['P2_TRAIN_P1_VALIDATE', p2TrainP1Validate],
    ];
    for (const [name, fold] of folds) {
      if (fold.precision < THRESHOLDS.eachFold.precisionMin) blockers.push(`${name}_PRECISION_BELOW_THRESHOLD`);
      if (fold.recall < THRESHOLDS.eachFold.recallMin) blockers.push(`${name}_RECALL_BELOW_THRESHOLD`);
      if (fold.f1 < THRESHOLDS.eachFold.f1Min) blockers.push(`${name}_F1_BELOW_THRESHOLD`);
      if (fold.completeness < THRESHOLDS.eachFold.completenessMin) blockers.push(`${name}_COMPLETENESS_BELOW_THRESHOLD`);
      if (fold.frameAccuracy < THRESHOLDS.eachFold.frameAccuracyMin) blockers.push(`${name}_FRAME_ACCURACY_BELOW_THRESHOLD`);
      if (fold.abstentionRate > THRESHOLDS.eachFold.abstentionRateMax) blockers.push(`${name}_ABSTENTION_ABOVE_THRESHOLD`);
      for (const content of THRESHOLDS.contentClasses) {
        if (fold.contentF1[content] < THRESHOLDS.eachFold.eachContentF1Min) {
          blockers.push(`${name}_${content.toUpperCase()}_F1_BELOW_THRESHOLD`);
        }
      }
    }
    const macroF1 = (p1TrainP2Validate.f1 + p2TrainP1Validate.f1) / 2;
    const macroCompleteness = (p1TrainP2Validate.completeness + p2TrainP1Validate.completeness) / 2;
    const f1Gap = Math.abs(p1TrainP2Validate.f1 - p2TrainP1Validate.f1);
    const frameAccuracyGap = Math.abs(p1TrainP2Validate.frameAccuracy - p2TrainP1Validate.frameAccuracy);
    if (macroF1 < THRESHOLDS.aggregate.macroF1Min) blockers.push('TWO_FOLD_MACRO_F1_BELOW_THRESHOLD');
    if (macroCompleteness < THRESHOLDS.aggregate.macroCompletenessMin) blockers.push('TWO_FOLD_MACRO_COMPLETENESS_BELOW_THRESHOLD');
    if (f1Gap > THRESHOLDS.aggregate.f1GapMax) blockers.push('CROSS_PERFORMER_F1_GAP_ABOVE_THRESHOLD');
    if (frameAccuracyGap > THRESHOLDS.aggregate.frameAccuracyGapMax) blockers.push('CROSS_PERFORMER_FRAME_ACCURACY_GAP_ABOVE_THRESHOLD');
  }

  const uniqueBlockers = [...new Set(blockers)].sort();
  return {
    accepted: uniqueBlockers.length === 0,
    blockers: uniqueBlockers,
    thresholds: getGuitarTechsDevelopmentMetricThresholds(),
    p3OpeningAuthorized: false,
    customerDeliveryEligible: false,
  };
}
