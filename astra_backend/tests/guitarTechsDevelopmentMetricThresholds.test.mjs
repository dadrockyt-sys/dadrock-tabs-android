import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

import {
  GUITAR_TECHS_DEVELOPMENT_METRIC_THRESHOLDS_RECEIPT_SHA256,
  evaluateGuitarTechsDevelopmentMetrics,
  getGuitarTechsDevelopmentMetricThresholds,
} from '../guitarTechsDevelopmentMetricThresholds.mjs';

const receiptBytes = readFileSync(new URL('../../docs/astra/GUITARTECHS_DEVELOPMENT_METRIC_THRESHOLDS_V1.json', import.meta.url));
const fold = (overrides = {}) => ({
  precision: 0.80,
  recall: 0.70,
  f1: 0.74,
  completeness: 0.70,
  frameAccuracy: 0.78,
  abstentionRate: 0.05,
  contentF1: {chords: 0.68, scales: 0.78, singlenotes: 0.82, PalmMute: 0.70},
  ...overrides,
});
const good = {
  thresholdReceiptSha256: GUITAR_TECHS_DEVELOPMENT_METRIC_THRESHOLDS_RECEIPT_SHA256,
  alignmentEvidenceReceiptSha256: '8e65fda2a74f5f5af77ab62be3538715d9ec2c0dcd783de5837a56c5dd42b1ae',
  acceptedCaptureKeysSha256: 'f520f5ffe3daf44da9bad1d145adaa1c9ff0bb662141b027f85b8c7bc827eabc',
  p1TrainP2Validate: fold(),
  p2TrainP1Validate: fold({f1: 0.71, frameAccuracy: 0.74}),
};

test('committed metric-threshold receipt has the exact frozen identity', () => {
  assert.equal(createHash('sha256').update(receiptBytes).digest('hex'), GUITAR_TECHS_DEVELOPMENT_METRIC_THRESHOLDS_RECEIPT_SHA256);
  const receipt = JSON.parse(receiptBytes.toString('utf8'));
  assert.equal(receipt.acceptanceThresholds.eachFold.onsetStringFretPrecisionMin, 0.75);
  assert.equal(receipt.acceptanceThresholds.eachFold.onsetStringFretRecallMin, 0.60);
  assert.equal(receipt.acceptanceThresholds.eachFold.onsetStringFretF1Min, 0.67);
  assert.equal(receipt.acceptanceThresholds.twoFoldAggregate.macroOnsetStringFretF1Min, 0.70);
  assert.equal(receipt.checkpointSelection.postResultThresholdRetuningAllowed, false);
  assert.equal(receipt.evaluationPopulation.p3MayInfluenceThresholds, false);
});

test('clean two-fold metrics can pass without authorizing P3 or delivery', () => {
  const result = evaluateGuitarTechsDevelopmentMetrics(good);
  assert.equal(result.accepted, true);
  assert.deepEqual(result.blockers, []);
  assert.equal(result.p3OpeningAuthorized, false);
  assert.equal(result.customerDeliveryEligible, false);
});

test('each fold and each content class fail closed independently', () => {
  const result = evaluateGuitarTechsDevelopmentMetrics({
    ...good,
    p1TrainP2Validate: fold({precision: 0.74, contentF1: {chords: 0.54, scales: 0.78, singlenotes: 0.82, PalmMute: 0.70}}),
  });
  assert.ok(result.blockers.includes('P1_TRAIN_P2_VALIDATE_PRECISION_BELOW_THRESHOLD'));
  assert.ok(result.blockers.includes('P1_TRAIN_P2_VALIDATE_CHORDS_F1_BELOW_THRESHOLD'));
  assert.equal(result.accepted, false);
});

test('cross-performer inconsistency and aggregate weakness fail', () => {
  const result = evaluateGuitarTechsDevelopmentMetrics({
    ...good,
    p1TrainP2Validate: fold({f1: 0.78, completeness: 0.66, frameAccuracy: 0.82}),
    p2TrainP1Validate: fold({f1: 0.67, completeness: 0.60, frameAccuracy: 0.70}),
  });
  assert.ok(result.blockers.includes('CROSS_PERFORMER_F1_GAP_ABOVE_THRESHOLD'));
  assert.ok(result.blockers.includes('CROSS_PERFORMER_FRAME_ACCURACY_GAP_ABOVE_THRESHOLD'));
  assert.ok(result.blockers.includes('TWO_FOLD_MACRO_COMPLETENESS_BELOW_THRESHOLD'));
});

test('missing/nonfinite metrics, population substitutions and P3 fail closed', () => {
  assert.ok(evaluateGuitarTechsDevelopmentMetrics({...good, p1TrainP2Validate: fold({f1: Number.NaN})}).blockers.includes('P1_TRAIN_P2_VALIDATE_F1_INVALID'));
  assert.ok(evaluateGuitarTechsDevelopmentMetrics({...good, acceptedCaptureKeysSha256: '0'.repeat(64)}).blockers.includes('GUITAR_TECHS_METRIC_EVALUATION_POPULATION_MISMATCH'));
  assert.ok(evaluateGuitarTechsDevelopmentMetrics({...good, p3Opened: true}).blockers.includes('GUITAR_TECHS_P3_SEALED'));
});

test('threshold reads are deterministic and defensive', () => {
  const first = getGuitarTechsDevelopmentMetricThresholds();
  first.eachFold.f1Min = 0;
  assert.equal(getGuitarTechsDevelopmentMetricThresholds().eachFold.f1Min, 0.67);
});
