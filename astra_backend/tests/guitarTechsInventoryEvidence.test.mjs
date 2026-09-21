import test from 'node:test';
import assert from 'node:assert/strict';

import {
  GUITAR_TECHS_INVENTORY_EVIDENCE_RECEIPT_SHA256,
  evaluateGuitarTechsInventoryEvidence,
  getGuitarTechsInventoryEvidenceIdentity,
} from '../guitarTechsInventoryEvidence.mjs';

const good = {
  receiptSha256: GUITAR_TECHS_INVENTORY_EVIDENCE_RECEIPT_SHA256,
  fullInventoryRunId: 35563511409,
  p2ChordsRecoveryRunId: 35563847021,
  archiveCount: 8,
  performanceGroupCount: 92,
  chordStringIdentityPolicy: 'explicit-track-name-never-positional',
};

test('exact frozen P1/P2 inventory evidence clears grouping and string-map gates only', () => {
  const result = evaluateGuitarTechsInventoryEvidence(good);
  assert.equal(result.evidenceAccepted, true);
  assert.equal(result.performanceGroupingVerified, true);
  assert.equal(result.captureViewGroupingVerified, true);
  assert.equal(result.stringTrackMappingVerified, true);
  assert.equal(result.techniqueMidiSemanticsReviewed, true);
  assert.equal(result.p1TuningVerified, true);
  assert.equal(result.p2TuningFullyVerified, false);
  assert.ok(result.nextBlockers.includes('P2_D_STRING_TUNING_NOT_FULLY_VERIFIED'));
  assert.ok(result.nextBlockers.includes('TRAINING_NOT_AUTHORIZED'));
  assert.equal(result.customerDeliveryEligible, false);
});

test('receipt and run substitutions fail closed', () => {
  assert.ok(evaluateGuitarTechsInventoryEvidence({...good, receiptSha256: '0'.repeat(64)}).blockers.includes(
    'GUITAR_TECHS_INVENTORY_RECEIPT_IDENTITY_MISMATCH',
  ));
  assert.ok(evaluateGuitarTechsInventoryEvidence({...good, fullInventoryRunId: 1}).blockers.includes(
    'GUITAR_TECHS_INVENTORY_RUN_IDENTITY_MISMATCH',
  ));
});

test('group-count or positional chord mapping substitutions fail closed', () => {
  assert.ok(evaluateGuitarTechsInventoryEvidence({...good, performanceGroupCount: 91}).blockers.includes(
    'GUITAR_TECHS_INVENTORY_GROUPING_MISMATCH',
  ));
  assert.ok(evaluateGuitarTechsInventoryEvidence({...good, chordStringIdentityPolicy: 'track-index'}).blockers.includes(
    'GUITAR_TECHS_STRING_TRACK_MAPPING_POLICY_MISMATCH',
  ));
});

test('inventory receipt cannot authorize P3, alignment or training', () => {
  const result = evaluateGuitarTechsInventoryEvidence({
    ...good,
    p3Opened: true,
    alignmentRun: true,
    trainingRun: true,
  });
  assert.ok(result.blockers.includes('GUITAR_TECHS_P3_SEALED'));
  assert.ok(result.blockers.includes('GUITAR_TECHS_ALIGNMENT_NOT_AUTHORIZED_BY_INVENTORY_RECEIPT'));
  assert.ok(result.blockers.includes('GUITAR_TECHS_TRAINING_NOT_AUTHORIZED_BY_INVENTORY_RECEIPT'));
  assert.equal(result.evidenceAccepted, false);
});

test('identity reads are defensive and deterministic', () => {
  const first = getGuitarTechsInventoryEvidenceIdentity();
  first.canonicalTrackNamesHighToLow.push('MUTATION');
  const second = getGuitarTechsInventoryEvidenceIdentity();
  assert.deepEqual(second.canonicalTrackNamesHighToLow, ['e', 'B', 'G', 'D', 'A', 'E']);
  assert.deepEqual(second, getGuitarTechsInventoryEvidenceIdentity());
});
