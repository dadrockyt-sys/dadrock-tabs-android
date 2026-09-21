import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

import {
  GUITAR_TECHS_REAL_TRAINING_RESULT_RECEIPT_SHA256,
  evaluateGuitarTechsRealTrainingResult,
  getGuitarTechsRealTrainingResultIdentity,
} from '../guitarTechsRealTrainingResult.mjs';

const receiptBytes = readFileSync(new URL('../../docs/astra/GUITARTECHS_REAL_TRAINING_DEVELOPMENT_RESULT_V1.json', import.meta.url));

const good = {
  receiptSha256: GUITAR_TECHS_REAL_TRAINING_RESULT_RECEIPT_SHA256,
  workflowRunId: 35569391647,
  p1TrainP2ResultSha256: '024e5d2d3612732e85f2c0b812f223e602fcdf6e69f82ca8d5a2d0d0e89090f0',
  p2TrainP1ResultSha256: 'c6dcc9e557c7e030f523410e705c35e4e7fea3c994e490487c7755e3e2793950',
};

test('committed real-training result has exact frozen identity', () => {
  assert.equal(createHash('sha256').update(receiptBytes).digest('hex'), GUITAR_TECHS_REAL_TRAINING_RESULT_RECEIPT_SHA256);
  const receipt = JSON.parse(receiptBytes.toString('utf8'));
  assert.equal(receipt.source.workflowRunId, 35569391647);
  assert.equal(receipt.decision.modelTrained, true);
  assert.equal(receipt.decision.developmentThresholdsMet, false);
  assert.equal(receipt.decision.p3OpeningEligible, false);
  assert.equal(receipt.aggregate.macroOnsetStringFretF1, 0.21363128628445138);
  assert.equal(receipt.aggregate.macroNoteEventCompleteness, 0.20420847659537342);
});

test('exact result is accepted as evidence but remains a failed development candidate', () => {
  const result = evaluateGuitarTechsRealTrainingResult(good);
  assert.equal(result.evidenceAccepted, true);
  assert.equal(result.developmentAccepted, false);
  assert.equal(result.modelTrained, true);
  assert.equal(result.p3OpeningEligible, false);
  assert.deepEqual(result.blockers, ['GUITAR_TECHS_DEVELOPMENT_THRESHOLDS_NOT_MET']);
});

test('result or run substitutions fail closed', () => {
  assert.ok(evaluateGuitarTechsRealTrainingResult({...good, workflowRunId: 1}).blockers.includes(
    'GUITAR_TECHS_REAL_TRAINING_RUN_IDENTITY_MISMATCH',
  ));
  assert.ok(evaluateGuitarTechsRealTrainingResult({...good, p1TrainP2ResultSha256: '0'.repeat(64)}).blockers.includes(
    'GUITAR_TECHS_REAL_TRAINING_FOLD_RESULT_IDENTITY_MISMATCH',
  ));
});

test('failed candidate cannot open P3 or request customer delivery', () => {
  const result = evaluateGuitarTechsRealTrainingResult({...good, p3Opened: true, customerDeliveryRequested: true});
  assert.ok(result.blockers.includes('GUITAR_TECHS_P3_SEALED'));
  assert.ok(result.blockers.includes('CUSTOMER_DELIVERY_NOT_AUTHORIZED'));
  assert.equal(result.p3OpeningEligible, false);
});

test('identity reads are defensive', () => {
  const first = getGuitarTechsRealTrainingResultIdentity();
  first.macroF1 = 1;
  assert.equal(getGuitarTechsRealTrainingResultIdentity().macroF1, 0.21363128628445138);
});
