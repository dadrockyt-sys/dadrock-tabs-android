import test from 'node:test';
import assert from 'node:assert/strict';

import {
  evaluateGuitarTechsDatasetAdmission,
  getExpectedGuitarTechsPublishedIdentity,
} from '../guitarTechsDatasetIdentity.mjs';

function completeEvidence() {
  const expected = getExpectedGuitarTechsPublishedIdentity();
  return {
    record: expected.record,
    version: expected.version,
    license: { ...expected.license },
    archives: expected.archives.map((archive) => ({ ...archive })),
    manifestSha256: expected.manifestSha256,
    splitReceiptSha256: expected.splitReceiptSha256,
    astraArchiveSha256Complete: true,
    trainingMediaAcquired: true,
    extractedPerformanceGroupingVerified: true,
  };
}

test('published identity is frozen while media admission remains blocked without bytes', () => {
  const evidence = completeEvidence();
  evidence.astraArchiveSha256Complete = false;
  evidence.trainingMediaAcquired = false;
  evidence.extractedPerformanceGroupingVerified = false;
  const result = evaluateGuitarTechsDatasetAdmission(evidence);
  assert.equal(result.metadataIdentityVerified, true);
  assert.equal(result.trainingMediaAdmissionReady, false);
  assert.ok(result.blockers.includes('GUITAR_TECHS_ASTRA_SHA256_PENDING'));
  assert.ok(result.blockers.includes('GUITAR_TECHS_MEDIA_NOT_ACQUIRED'));
  assert.ok(result.blockers.includes('GUITAR_TECHS_EXTRACTED_GROUPING_PENDING'));
  assert.equal(result.customerDeliveryEligible, false);
});

test('record, license, archive or split substitution fails closed', () => {
  const record = completeEvidence();
  record.record = 'https://example.invalid';
  assert.ok(evaluateGuitarTechsDatasetAdmission(record).blockers.includes('GUITAR_TECHS_RECORD_IDENTITY_MISMATCH'));

  const license = completeEvidence();
  license.license.indexBlob = '0'.repeat(40);
  assert.ok(evaluateGuitarTechsDatasetAdmission(license).blockers.includes('GUITAR_TECHS_LICENSE_EVIDENCE_MISMATCH'));

  const archive = completeEvidence();
  archive.archives[0].bytes += 1;
  assert.ok(evaluateGuitarTechsDatasetAdmission(archive).blockers.includes('GUITAR_TECHS_PUBLISHED_ARCHIVE_IDENTITY_MISMATCH'));

  const split = completeEvidence();
  split.splitReceiptSha256 = '0'.repeat(64);
  assert.ok(evaluateGuitarTechsDatasetAdmission(split).blockers.includes('GUITAR_TECHS_SPLIT_RECEIPT_MISMATCH'));
});

test('synthetic complete evidence can clear dataset admission but never customer delivery', () => {
  const result = evaluateGuitarTechsDatasetAdmission(completeEvidence());
  assert.equal(result.metadataIdentityVerified, true);
  assert.equal(result.trainingMediaAdmissionReady, true);
  assert.deepEqual(result.blockers, []);
  assert.equal(result.customerDeliveryEligible, false);
});

test('expected identity is deterministic and defensive', () => {
  const first = getExpectedGuitarTechsPublishedIdentity();
  first.archives[0].bytes = 1;
  const second = getExpectedGuitarTechsPublishedIdentity();
  assert.equal(second.archives[0].bytes, 981741162);
  assert.deepEqual(second, getExpectedGuitarTechsPublishedIdentity());
});
