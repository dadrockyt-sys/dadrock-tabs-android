import test from 'node:test';
import assert from 'node:assert/strict';

import {
  GUITAR_TECHS_P2_TUNING_EVIDENCE_SHA256,
  evaluateGuitarTechsP2TuningEvidence,
  getGuitarTechsP2TuningEvidenceIdentity,
} from '../guitarTechsTuningEvidence.mjs';

const good = {
  receiptSha256: GUITAR_TECHS_P2_TUNING_EVIDENCE_SHA256,
  sourceInventoryReceiptSha256: '4d21d578a275587abe18d9f5382074fa9c33bd2f0698c5d10b340788de306bcd',
  sourceFullInventoryRunId: 35563511409,
  openMidiHighToLow: [64, 59, 55, 50, 45, 40],
  dObservedUniqueMidi: Array.from({length: 22}, (_, index) => 51 + index),
};

test('exact shared-schema missing-open endpoint evidence verifies P2 tuning', () => {
  const result = evaluateGuitarTechsP2TuningEvidence(good);
  assert.equal(result.evidenceAccepted, true);
  assert.equal(result.tuningVerified, true);
  assert.deepEqual(result.openMidiLowToHigh, [40, 45, 50, 55, 59, 64]);
  assert.equal(result.tuning, 'E2 A2 D3 G3 B3 E4');
  assert.equal(result.dStringOpenMidiDirectlyObserved, false);
  assert.equal(result.dStringOpenMidiStructurallyVerified, true);
  assert.equal(result.customerDeliveryEligible, false);
});

test('D-sharp substitution and changed missing-endpoint pattern fail closed', () => {
  assert.ok(evaluateGuitarTechsP2TuningEvidence({
    ...good,
    openMidiHighToLow: [64, 59, 55, 51, 45, 40],
  }).blockers.includes('GUITAR_TECHS_P2_TUNING_OPEN_STRING_MISMATCH'));
  assert.ok(evaluateGuitarTechsP2TuningEvidence({
    ...good,
    dObservedUniqueMidi: Array.from({length: 22}, (_, index) => 52 + index),
  }).blockers.includes('GUITAR_TECHS_P2_D_STRING_MISSING_ENDPOINT_PATTERN_MISMATCH'));
});

test('source or receipt substitution fails closed', () => {
  assert.ok(evaluateGuitarTechsP2TuningEvidence({
    ...good,
    receiptSha256: '0'.repeat(64),
  }).blockers.includes('GUITAR_TECHS_P2_TUNING_RECEIPT_IDENTITY_MISMATCH'));
  assert.ok(evaluateGuitarTechsP2TuningEvidence({
    ...good,
    sourceFullInventoryRunId: 1,
  }).blockers.includes('GUITAR_TECHS_P2_TUNING_SOURCE_IDENTITY_MISMATCH'));
});

test('tuning receipt cannot use P3, model prediction, or authorize training', () => {
  const result = evaluateGuitarTechsP2TuningEvidence({
    ...good,
    usesP3: true,
    usesModelPrediction: true,
    trainingRun: true,
  });
  assert.ok(result.blockers.includes('GUITAR_TECHS_P3_SEALED'));
  assert.ok(result.blockers.includes('GUITAR_TECHS_TUNING_MUST_NOT_USE_MODEL_PREDICTION'));
  assert.ok(result.blockers.includes('GUITAR_TECHS_TRAINING_NOT_AUTHORIZED_BY_TUNING_RECEIPT'));
  assert.equal(result.evidenceAccepted, false);
});

test('identity reads are defensive', () => {
  const first = getGuitarTechsP2TuningEvidenceIdentity();
  first.openMidiHighToLow[0] = 0;
  assert.deepEqual(getGuitarTechsP2TuningEvidenceIdentity().openMidiHighToLow, [64, 59, 55, 50, 45, 40]);
});
