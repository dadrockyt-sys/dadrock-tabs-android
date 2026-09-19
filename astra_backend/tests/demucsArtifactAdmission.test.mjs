import test from 'node:test';
import assert from 'node:assert/strict';

import {
  evaluateDemucsArtifactAdmission,
  getFrozenDemucsArtifactAdmissionContract,
} from '../demucsArtifactAdmission.mjs';

function observation(overrides = {}) {
  const contract = getFrozenDemucsArtifactAdmissionContract();
  return {
    candidateId: contract.candidateId,
    modelName: contract.modelName,
    fileName: contract.artifact.fileName,
    sourceUrl: contract.artifact.sourceUrl,
    sha256: contract.artifact.sha256,
    artifactBytesObservedOnAstra: false,
    rightsDecisionRecordSha256: null,
    ...overrides,
  };
}

test('contract freezes the one official htdemucs_6s artifact identity', () => {
  const contract = getFrozenDemucsArtifactAdmissionContract();
  assert.equal(contract.contract.version, 1);
  assert.equal(contract.modelName, 'htdemucs_6s');
  assert.equal(contract.artifact.fileName, '5c90dfd2-34c22ccb.th');
  assert.equal(
    contract.artifact.sha256,
    'd2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411',
  );
  assert.equal(contract.rightsDecision.recordSha256, null);
});

test('current exact identity remains blocked before bytes and a frozen rights decision exist', () => {
  const result = evaluateDemucsArtifactAdmission(observation());
  assert.equal(result.artifactIdentityMatches, true);
  assert.equal(result.admittedForDevelopmentExecution, false);
  assert.ok(result.blockers.includes('DEMUCS_WEIGHT_BYTES_NOT_OBSERVED_ON_ASTRA'));
  assert.ok(result.blockers.includes('DEMUCS_WEIGHT_RIGHTS_DECISION_NOT_FROZEN'));
});

test('observing exact bytes cannot substitute for the external rights decision', () => {
  const result = evaluateDemucsArtifactAdmission(observation({ artifactBytesObservedOnAstra: true }));
  assert.equal(result.admittedForDevelopmentExecution, false);
  assert.deepEqual(result.blockers, ['DEMUCS_WEIGHT_RIGHTS_DECISION_NOT_FROZEN']);
});

test('artifact filename, source, and digest substitutions fail closed', () => {
  assert.throws(
    () => evaluateDemucsArtifactAdmission(observation({ fileName: 'renamed.th' })),
    /frozen Demucs artifact identity/,
  );
  assert.throws(
    () => evaluateDemucsArtifactAdmission(observation({ sourceUrl: 'https://example.com/model.th' })),
    /frozen Demucs artifact identity/,
  );
  assert.throws(
    () => evaluateDemucsArtifactAdmission(observation({ sha256: '0'.repeat(64) })),
    /frozen Demucs artifact identity/,
  );
});

test('artifact admission never grants customer delivery or performs runtime work', () => {
  const result = evaluateDemucsArtifactAdmission(observation());
  assert.equal(result.customerDeliveryAllowed, false);
  assert.equal(result.downloadsArtifact, false);
  assert.equal(result.importsModel, false);
  assert.equal(result.invokesModel, false);
  assert.equal(result.opensAudio, false);
  assert.equal(result.performsNetworkAccess, false);
});

test('artifact admission is deterministic and frozen contract copies cannot mutate it', () => {
  const first = getFrozenDemucsArtifactAdmissionContract();
  first.artifact.fileName = 'mutated.th';
  assert.equal(getFrozenDemucsArtifactAdmissionContract().artifact.fileName, '5c90dfd2-34c22ccb.th');
  assert.deepEqual(
    evaluateDemucsArtifactAdmission(observation()),
    evaluateDemucsArtifactAdmission(observation()),
  );
});
