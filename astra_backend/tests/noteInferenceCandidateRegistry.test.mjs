import test from 'node:test';
import assert from 'node:assert/strict';

import {
  PRIMARY_NEXT_NOTE_INFERENCE_CANDIDATE,
  SECONDARY_NOTE_INFERENCE_CANDIDATE,
  buildNoteInferenceDevelopmentPlan,
  getNoteInferenceCandidate,
  listNoteInferenceCandidates,
} from '../noteInferenceCandidateRegistry.mjs';

test('inventory keeps Basic Pitch as the existing frozen baseline', () => {
  const candidate = getNoteInferenceCandidate('basic_pitch_0_4_0');
  assert.equal(candidate.artifact.packageVersion, '0.4.0');
  assert.equal(
    candidate.artifact.modelSha256,
    '3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676',
  );
  assert.equal(candidate.operational.runtimeLockFrozen, true);
  assert.equal(candidate.customerDeliveryEligible, false);
});

test('GuitarProFX TabCNN is primary but remains execution-blocked', () => {
  assert.equal(PRIMARY_NEXT_NOTE_INFERENCE_CANDIDATE, 'tabcnn_guitarprofx_dafx24');
  const candidate = getNoteInferenceCandidate(PRIMARY_NEXT_NOTE_INFERENCE_CANDIDATE);
  assert.equal(candidate.directStringFretOutput, true);
  assert.equal(candidate.artifact.publishedBytes, 3345122);
  assert.equal(candidate.artifact.publishedMd5, 'ce168b2cd426f81a2a78499214e40605');
  assert.equal(
    candidate.artifact.sha256,
    '1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c',
  );
  assert.equal(candidate.artifact.downloadedByAstra, true);
  assert.equal(candidate.artifact.artifactPersistedByAstra, false);
  assert.equal(candidate.operational.runtimeLockFrozen, true);
  assert.equal(candidate.operational.preprocessingIdentityFrozen, true);
  assert.equal(candidate.operational.cpuPathKnown, false);
  assert.equal(candidate.developmentExecutionReady, false);
  assert.ok(candidate.blockers.includes('CHECKPOINT_DESERIALIZATION_NOT_AUTHORIZED'));
  assert.ok(candidate.blockers.includes('TRAINING_DATA_COMMERCIAL_RIGHTS_UNRESOLVED'));
  assert.equal(candidate.customerDeliveryEligible, false);
});

test('MR-MT3 is secondary and its exact selected checkpoint identity is frozen without downloading it', () => {
  assert.equal(SECONDARY_NOTE_INFERENCE_CANDIDATE, 'mr_mt3');
  const candidate = getNoteInferenceCandidate('mr_mt3');
  assert.equal(candidate.source.revision, '826ea84a933f93cd707d11e91af711f1d19c8d79');
  assert.equal(
    candidate.artifact.selectedCheckpointSha256,
    '74b2620009e9455a8f36da8a2b41950da4f12a229652a6cbd3ccb4333920c97f',
  );
  assert.equal(candidate.artifact.selectedCheckpointBytes, 582511409);
  assert.equal(candidate.artifact.downloadedByAstra, false);
  assert.equal(candidate.developmentExecutionReady, false);
});

test('no candidate can claim lead-rhythm distinction on its own', () => {
  for (const candidate of listNoteInferenceCandidates()) {
    assert.equal(candidate.leadRhythmDistinction, false);
    assert.equal(candidate.customerDeliveryEligible, false);
  }
});

test('lead or rhythm development plan fails closed without complete external role evidence', () => {
  for (const candidateId of ['basic_pitch_0_4_0', 'tabcnn_guitarprofx_dafx24', 'mr_mt3']) {
    const plan = buildNoteInferenceDevelopmentPlan({
      candidateId,
      requestedRole: 'lead',
      inputRoleEvidenceStatus: 'abstained',
    });
    assert.ok(plan.blockers.includes('REQUESTED_GUITAR_ROLE_EVIDENCE_UNRESOLVED'));
    assert.equal(plan.customerDeliveryEligible, false);
    assert.equal(plan.contract.invokesModel, false);
    assert.equal(plan.contract.downloadsArtifact, false);
  }
});

test('guitar-only TabCNN rejects bass planning explicitly', () => {
  const plan = buildNoteInferenceDevelopmentPlan({
    candidateId: 'tabcnn_guitarprofx_dafx24',
    requestedRole: 'bass',
    inputRoleEvidenceStatus: 'complete',
  });
  assert.ok(plan.blockers.includes('CANDIDATE_DOES_NOT_SUPPORT_BASS'));
  assert.equal(plan.developmentExecutionReady, false);
});

test('registry rejects unknown candidates and unsupported roles before any action', () => {
  assert.throws(() => getNoteInferenceCandidate('nope'), /UNKNOWN_NOTE_INFERENCE_CANDIDATE/);
  assert.throws(
    () => buildNoteInferenceDevelopmentPlan({
      candidateId: 'basic_pitch_0_4_0',
      requestedRole: 'piano',
    }),
    /requestedRole/,
  );
});

test('registry reads are deterministic and return defensive copies', () => {
  const first = listNoteInferenceCandidates();
  first[0].blockers.push('MUTATION');
  const second = listNoteInferenceCandidates();
  assert.equal(second[0].blockers.includes('MUTATION'), false);
  assert.deepEqual(second, listNoteInferenceCandidates());
});

test('legacy pickle globals are statically verified but deserialization remains unauthorized', () => {
  const candidate = getNoteInferenceCandidate('tabcnn_guitarprofx_dafx24');
  assert.equal(candidate.operational.legacyPickleGlobalsStaticVerified, true);
  assert.equal(candidate.operational.legacyImportSurfaceVerified, true);
  assert.equal(
    candidate.operational.staticCheckpointInspectionReceiptSha256,
    '72ecf7e106bc69ce7ef4aa66888cb544535615ad3a9c8a6246bb09a460da3971',
  );
  assert.ok(candidate.blockers.includes('CHECKPOINT_DESERIALIZATION_NOT_AUTHORIZED'));
  assert.ok(candidate.blockers.includes('TRAINING_DATA_COMMERCIAL_RIGHTS_UNRESOLVED'));
});
