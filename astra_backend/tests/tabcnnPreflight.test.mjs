import test from 'node:test';
import assert from 'node:assert/strict';

import {
  evaluateTabcnnDevelopmentPreflight,
  getExpectedTabcnnPreflightIdentity,
} from '../tabcnnPreflight.mjs';

function completeEvidence() {
  const expected = getExpectedTabcnnPreflightIdentity();
  return {
    source: {
      repository: expected.source.repository,
      revision: expected.source.revision,
      blobs: { ...expected.source.blobs },
    },
    artifact: {
      record: expected.artifact.record,
      file: expected.artifact.file,
      bytes: expected.artifact.bytes,
      downloadedFromOfficialRecord: true,
      md5: expected.artifact.md5,
      publishedMd5Verified: true,
      sha256: expected.artifact.sha256,
    },
    preprocessing: {
      ...expected.preprocessing,
      numericalReproductionVerified: true,
      numericalReproductionReceiptSha256: expected.reproduction.receiptSha256,
      normalizedAudioSha256: expected.reproduction.normalizedAudioSha256,
      featuresSha256: expected.reproduction.featuresSha256,
      modelWindowsSha256: expected.reproduction.modelWindowsSha256,
    },
    runtime: {
      dependencyLockComplete: true,
      dependencyLockSha256: expected.runtime.dependencyLockSha256,
      wheelManifestSha256: expected.runtime.wheelManifestSha256,
      exactPackageVersionsFrozen: true,
      platform: expected.runtime.platform,
      pythonVersion: expected.runtime.pythonVersion,
      numpyVersion: expected.runtime.numpyVersion,
      scipyVersion: expected.runtime.scipyVersion,
      librosaVersion: expected.runtime.librosaVersion,
      torchVersion: expected.runtime.torchVersion,
      cpuSmokeTestPassed: true,
      cpuSmokeReceiptSha256: 'd'.repeat(64),
      wallTimeSeconds: 120,
      peakMemoryMb: 1024,
    },
    rights: {
      checkpointLicenseReviewed: true,
      trainingDataCommercialRightsReviewed: true,
      trainingDataCommercialRightsCleared: true,
      developmentUseAuthorized: true,
    },
  };
}

test('empty preflight fails closed without invoking or downloading anything', () => {
  const result = evaluateTabcnnDevelopmentPreflight();
  assert.equal(result.developmentExecutionReady, false);
  assert.equal(result.customerDeliveryEligible, false);
  assert.equal(result.contract.invokesModel, false);
  assert.equal(result.contract.downloadsArtifact, false);
  assert.equal(result.contract.opensAudio, false);
  assert.ok(result.blockers.includes('SOURCE_IDENTITY_MISMATCH'));
  assert.ok(result.blockers.includes('OFFICIAL_ARTIFACT_NOT_DOWNLOADED'));
  assert.ok(result.blockers.includes('RUNTIME_DEPENDENCY_LOCK_PENDING'));
  assert.ok(result.blockers.includes('TRAINING_DATA_COMMERCIAL_RIGHTS_REVIEW_PENDING'));
});

test('all synthetic receipts can clear development execution but never customer delivery', () => {
  const result = evaluateTabcnnDevelopmentPreflight(completeEvidence());
  assert.equal(result.developmentExecutionReady, true);
  assert.deepEqual(result.blockers, []);
  assert.equal(result.customerDeliveryEligible, false);
  assert.equal(result.contract.grantsCustomerDelivery, false);
  assert.equal(Object.values(result.checks).every(Boolean), true);
});

test('source or preprocessing drift fails closed', () => {
  const evidence = completeEvidence();
  evidence.source.blobs.model = '0'.repeat(40);
  evidence.preprocessing.hopLengthSamples = 256;
  const result = evaluateTabcnnDevelopmentPreflight(evidence);
  assert.equal(result.developmentExecutionReady, false);
  assert.ok(result.blockers.includes('SOURCE_IDENTITY_MISMATCH'));
  assert.ok(result.blockers.includes('PREPROCESSING_CONTRACT_MISMATCH'));
});

test('published MD5 is not enough without official-source download and Astra SHA256', () => {
  const evidence = completeEvidence();
  evidence.artifact.downloadedFromOfficialRecord = false;
  evidence.artifact.sha256 = null;
  const result = evaluateTabcnnDevelopmentPreflight(evidence);
  assert.ok(result.blockers.includes('OFFICIAL_ARTIFACT_NOT_DOWNLOADED'));
  assert.ok(result.blockers.includes('OFFICIAL_ARTIFACT_SHA256_UNVERIFIED'));
  assert.equal(result.developmentExecutionReady, false);
});

test('artifact SHA256 substitution fails closed even when size and published MD5 match', () => {
  const evidence = completeEvidence();
  evidence.artifact.sha256 = '0'.repeat(64);
  const result = evaluateTabcnnDevelopmentPreflight(evidence);
  assert.ok(result.blockers.includes('OFFICIAL_ARTIFACT_SHA256_UNVERIFIED'));
  assert.equal(result.checks.officialArtifactDigestVerified, false);
  assert.equal(result.developmentExecutionReady, false);
});

test('source parity above tolerance blocks even when the frozen receipt is present', () => {
  const evidence = completeEvidence();
  evidence.preprocessing.sourceParityMaxAbsoluteDifference = 1e-5;
  const result = evaluateTabcnnDevelopmentPreflight(evidence);
  assert.ok(result.blockers.includes('PREPROCESSING_SOURCE_PARITY_UNVERIFIED'));
  assert.equal(result.checks.preprocessingNumericallyReproduced, false);
  assert.equal(result.developmentExecutionReady, false);
});

test('runtime budget limits are hard blockers', () => {
  const slow = completeEvidence();
  slow.runtime.wallTimeSeconds = 1200.001;
  assert.ok(
    evaluateTabcnnDevelopmentPreflight(slow).blockers.includes('CPU_WALL_TIME_OUT_OF_BUDGET'),
  );

  const large = completeEvidence();
  large.runtime.peakMemoryMb = 4096.001;
  assert.ok(
    evaluateTabcnnDevelopmentPreflight(large).blockers.includes('CPU_MEMORY_OUT_OF_BUDGET'),
  );
});

test('missing numerical reproduction receipt blocks even when parameters match', () => {
  const evidence = completeEvidence();
  evidence.preprocessing.numericalReproductionReceiptSha256 = null;
  const result = evaluateTabcnnDevelopmentPreflight(evidence);
  assert.ok(result.blockers.includes('PREPROCESSING_REPRODUCTION_IDENTITY_MISMATCH'));
  assert.equal(result.developmentExecutionReady, false);
});

test('runtime lock or wheel substitution fails closed', () => {
  const evidence = completeEvidence();
  evidence.runtime.wheelManifestSha256 = '0'.repeat(64);
  const result = evaluateTabcnnDevelopmentPreflight(evidence);
  assert.ok(result.blockers.includes('RUNTIME_DEPENDENCY_LOCK_PENDING'));
  assert.equal(result.checks.runtimeLockVerified, false);
  assert.equal(result.developmentExecutionReady, false);
});

test('preprocessing receipt or tensor identity substitution fails closed', () => {
  const evidence = completeEvidence();
  evidence.preprocessing.featuresSha256 = '0'.repeat(64);
  const result = evaluateTabcnnDevelopmentPreflight(evidence);
  assert.ok(result.blockers.includes('PREPROCESSING_REPRODUCTION_IDENTITY_MISMATCH'));
  assert.equal(result.checks.preprocessingNumericallyReproduced, false);
  assert.equal(result.developmentExecutionReady, false);
});

test('completed review does not clear unresolved commercial training lineage', () => {
  const evidence = completeEvidence();
  evidence.rights.trainingDataCommercialRightsCleared = false;
  const result = evaluateTabcnnDevelopmentPreflight(evidence);
  assert.ok(result.blockers.includes('TRAINING_DATA_COMMERCIAL_RIGHTS_UNRESOLVED'));
  assert.equal(result.checks.rightsVerified, false);
  assert.equal(result.developmentExecutionReady, false);
});

test('rights checks are independent and all required', () => {
  const evidence = completeEvidence();
  evidence.rights.trainingDataCommercialRightsReviewed = false;
  const result = evaluateTabcnnDevelopmentPreflight(evidence);
  assert.ok(result.blockers.includes('TRAINING_DATA_COMMERCIAL_RIGHTS_REVIEW_PENDING'));
  assert.equal(result.checks.rightsVerified, false);
  assert.equal(result.customerDeliveryEligible, false);
});

test('expected identity is defensive and deterministic', () => {
  const first = getExpectedTabcnnPreflightIdentity();
  first.preprocessing.sampleRateHz = 1;
  const second = getExpectedTabcnnPreflightIdentity();
  assert.equal(second.preprocessing.sampleRateHz, 22050);
  assert.deepEqual(second, getExpectedTabcnnPreflightIdentity());
});
