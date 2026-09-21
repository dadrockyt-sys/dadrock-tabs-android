import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

import {
  GUITAR_TECHS_ALIGNMENT_EVIDENCE_RECEIPT_SHA256,
  evaluateGuitarTechsAlignmentEvidence,
  getGuitarTechsAlignmentEvidenceIdentity,
} from '../guitarTechsAlignmentEvidence.mjs';

const receiptBytes = readFileSync(new URL('../../docs/astra/GUITARTECHS_DEVELOPMENT_ALIGNMENT_EVIDENCE_V1.json', import.meta.url));
const receipt = JSON.parse(receiptBytes.toString('utf8'));

const good = {
  receiptSha256: GUITAR_TECHS_ALIGNMENT_EVIDENCE_RECEIPT_SHA256,
  workflowRunId: 35565975272,
  implementationReceiptSha256: 'b33dd0fd220fcef4a459cc47277f48cf90c0acd320e523c3afcea5fc52a8a26f',
  alignmentScriptSha256: 'b084da0900acf9bd4ec61386a4a928350af0e138c9ed36ef3fbafb15539bc330',
  primaryUniverseCaptureCount: 336,
  acceptedPrimaryCaptureCount: 256,
  abstainedPrimaryCaptureCount: 80,
  acceptedPrimaryCaptureKeysSha256: 'f520f5ffe3daf44da9bad1d145adaa1c9ff0bb662141b027f85b8c7bc827eabc',
  abstainedPrimaryCaptureKeysSha256: 'b4221bdc8236eb5f7c3a1cc5dca0f0d5d931d6acff7a56210525f08c0d26c812',
};

test('committed alignment receipt has the frozen exact identity and counts', () => {
  assert.equal(createHash('sha256').update(receiptBytes).digest('hex'), GUITAR_TECHS_ALIGNMENT_EVIDENCE_RECEIPT_SHA256);
  assert.equal(receipt.source.workflowRunId, 35565975272);
  assert.equal(receipt.aggregate.primaryTrainingCaptureAlignments.total, 336);
  assert.equal(receipt.aggregate.primaryTrainingCaptureAlignments.complete, 256);
  assert.equal(receipt.aggregate.primaryTrainingCaptureAlignments.abstained, 80);
  assert.equal(receipt.primaryTrainingPolicy.abstainedPrimaryCapturePaths.length, 80);
  assert.equal(receipt.policy.thresholdsRetunedAfterResults, false);
  assert.equal(receipt.decision.p3Opened, false);
  assert.equal(receipt.decision.trainingRun, false);
});

test('exact evidence clears alignment only for the frozen accepted subset', () => {
  const result = evaluateGuitarTechsAlignmentEvidence(good);
  assert.equal(result.evidenceAccepted, true);
  assert.equal(result.alignmentCorrectionVerified, true);
  assert.equal(result.acceptedPrimaryCaptureCount, 256);
  assert.equal(result.abstainedPrimaryCaptureCount, 80);
  assert.equal(result.requiresExactAbstentionFilter, true);
  assert.equal(result.trainingAuthorizedByThisReceipt, false);
  assert.equal(result.customerDeliveryEligible, false);
});

test('count, set, run and implementation substitutions fail closed', () => {
  assert.ok(evaluateGuitarTechsAlignmentEvidence({...good, acceptedPrimaryCaptureCount: 257}).blockers.includes(
    'GUITAR_TECHS_ALIGNMENT_CAPTURE_COUNT_MISMATCH',
  ));
  assert.ok(evaluateGuitarTechsAlignmentEvidence({...good, acceptedPrimaryCaptureKeysSha256: '0'.repeat(64)}).blockers.includes(
    'GUITAR_TECHS_ALIGNMENT_CAPTURE_SET_IDENTITY_MISMATCH',
  ));
  assert.ok(evaluateGuitarTechsAlignmentEvidence({...good, workflowRunId: 1}).blockers.includes(
    'GUITAR_TECHS_ALIGNMENT_RUN_IDENTITY_MISMATCH',
  ));
  assert.ok(evaluateGuitarTechsAlignmentEvidence({...good, alignmentScriptSha256: '0'.repeat(64)}).blockers.includes(
    'GUITAR_TECHS_ALIGNMENT_IMPLEMENTATION_IDENTITY_MISMATCH',
  ));
});

test('alignment evidence cannot authorize P3 or training', () => {
  const result = evaluateGuitarTechsAlignmentEvidence({...good, p3Opened: true, trainingRun: true});
  assert.ok(result.blockers.includes('GUITAR_TECHS_P3_SEALED'));
  assert.ok(result.blockers.includes('GUITAR_TECHS_TRAINING_NOT_AUTHORIZED_BY_ALIGNMENT_RECEIPT'));
  assert.equal(result.evidenceAccepted, false);
});

test('identity reads are deterministic and defensive', () => {
  const first = getGuitarTechsAlignmentEvidenceIdentity();
  first.acceptedPrimaryCaptureCount = 0;
  assert.equal(getGuitarTechsAlignmentEvidenceIdentity().acceptedPrimaryCaptureCount, 256);
  assert.deepEqual(getGuitarTechsAlignmentEvidenceIdentity(), getGuitarTechsAlignmentEvidenceIdentity());
});
