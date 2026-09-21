import test from 'node:test';
import assert from 'node:assert/strict';

import {
  evaluateGuitarTechsPretrainingReadiness,
  getGuitarTechsLabelAlignmentTrainingContract,
} from '../guitarTechsTrainingContract.mjs';

test('contract freezes alignment bounds and source-aligned initial training hyperparameters', () => {
  const contract = getGuitarTechsLabelAlignmentTrainingContract();
  assert.equal(contract.alignment.lagMinMs, -100);
  assert.equal(contract.alignment.lagMaxMs, 100);
  assert.equal(contract.alignment.p3MayInfluenceAlignment, false);
  assert.equal(contract.training.initialization, 'random-only');
  assert.equal(contract.training.optimizer, 'Adadelta');
  assert.equal(contract.training.learningRate, 1.0);
  assert.equal(contract.training.batchSize, 32);
  assert.equal(contract.training.maxIterationsPerFold, 2500);
  assert.equal(contract.training.paidComputeAuthorized, false);
  assert.equal(contract.training.realTrainingAuthorized, false);
});

test('pretraining readiness fails closed on unknown tuning/alignment/smoke/metrics', () => {
  const result = evaluateGuitarTechsPretrainingReadiness({
    publishedManifestSha256: 'a3445d799c4a0b17a0078dac0c9387a0e676111367a5f07d608fd55bd8118e52',
    splitReceiptSha256: 'd116556c13d250af28900bb1d73d2c0ccd3130246db8bdd2d6d387ac87be799a',
  });
  assert.ok(result.blockers.includes('STRING_TRACK_MAP_UNVERIFIED'));
  assert.ok(result.blockers.includes('TUNING_METADATA_UNFROZEN'));
  assert.ok(result.blockers.includes('ALIGNMENT_CORRECTION_UNVERIFIED'));
  assert.ok(result.blockers.includes('SYNTHETIC_BACKWARD_SMOKE_PENDING'));
  assert.ok(result.blockers.includes('DEVELOPMENT_METRIC_THRESHOLDS_UNFROZEN'));
  assert.ok(result.blockers.includes('REAL_TRAINING_NOT_AUTHORIZED'));
  assert.equal(result.readyForRealTraining, false);
});

test('opening P3 before development freeze is always a blocker', () => {
  const result = evaluateGuitarTechsPretrainingReadiness({
    publishedManifestSha256: 'a3445d799c4a0b17a0078dac0c9387a0e676111367a5f07d608fd55bd8118e52',
    splitReceiptSha256: 'd116556c13d250af28900bb1d73d2c0ccd3130246db8bdd2d6d387ac87be799a',
    stringTrackMapVerified: true,
    tuningMetadataFrozen: true,
    alignmentCorrectionVerified: true,
    syntheticBackwardSmokePassed: true,
    developmentMetricThresholdsFrozen: true,
    trainingAuthorized: true,
    p3Opened: true,
  });
  assert.ok(result.blockers.includes('P3_OPENED_BEFORE_DEVELOPMENT_FREEZE'));
  assert.equal(result.readyForRealTraining, false);
});

test('synthetic complete evidence can clear real-training readiness but not customer delivery', () => {
  const result = evaluateGuitarTechsPretrainingReadiness({
    publishedManifestSha256: 'a3445d799c4a0b17a0078dac0c9387a0e676111367a5f07d608fd55bd8118e52',
    splitReceiptSha256: 'd116556c13d250af28900bb1d73d2c0ccd3130246db8bdd2d6d387ac87be799a',
    stringTrackMapVerified: true,
    tuningMetadataFrozen: true,
    alignmentCorrectionVerified: true,
    syntheticBackwardSmokePassed: true,
    developmentMetricThresholdsFrozen: true,
    trainingAuthorized: true,
    p3Opened: false,
  });
  assert.equal(result.readyForRealTraining, true);
  assert.deepEqual(result.blockers, []);
  assert.equal(result.customerDeliveryEligible, false);
});
