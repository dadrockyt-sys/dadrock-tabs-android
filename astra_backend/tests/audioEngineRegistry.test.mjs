import test from 'node:test';
import assert from 'node:assert/strict';

import {
  listAstraAudioEngineCandidates,
  planAstraAudioEngine,
} from '../audioEngineRegistry.mjs';

test('registry exposes the bounded baseline, preferred development candidate, and rejected register gate', () => {
  const candidates = listAstraAudioEngineCandidates();
  assert.deepEqual(candidates.map((item) => item.candidateId), [
    'whole-mix-basic-pitch',
    'htdemucs6s-basic-pitch',
    'v5-register-gate',
  ]);
  assert.deepEqual(candidates.map((item) => item.status), [
    'baseline-only',
    'preferred-development-candidate',
    'rejected-role-evidence',
  ]);
});

test('bass plan identifies the direct stem candidate while retaining every execution blocker', () => {
  const plan = planAstraAudioEngine({
    candidateId: 'htdemucs6s-basic-pitch',
    role: 'bass',
    sourceContext: 'mixture',
  });

  assert.equal(plan.selectedStem, 'bass');
  assert.equal(plan.roleEvidence, 'direct-bass-stem-candidate');
  assert.equal(plan.capabilities.bassStem, true);
  assert.equal(plan.developmentExecutionReady, false);
  assert.equal(plan.customerDeliveryEligible, false);
  assert.ok(plan.blockers.includes('DEMUCS_WEIGHT_IDENTITY_AND_TERMS_UNRESOLVED'));
  assert.ok(plan.blockers.includes('CPU_RUNTIME_TARGET_UNPROVEN_3300_SECOND_LEGACY_ALLOWANCE'));
});

test('lead and rhythm plans cannot promote a generic guitar stem into role truth', () => {
  for (const role of ['lead', 'rhythm']) {
    const plan = planAstraAudioEngine({
      candidateId: 'htdemucs6s-basic-pitch',
      role,
      sourceContext: 'mixture',
    });
    assert.equal(plan.selectedStem, 'guitar');
    assert.equal(plan.roleEvidence, 'generic-guitar-stem-only');
    assert.equal(plan.capabilities.leadRhythmDistinction, false);
    assert.ok(plan.blockers.includes('LEAD_RHYTHM_DISTINCTION_UNAVAILABLE'));
  }
});

test('whole-mix Basic Pitch remains a baseline and cannot claim role extraction', () => {
  const plan = planAstraAudioEngine({
    candidateId: 'whole-mix-basic-pitch',
    role: 'bass',
  });
  assert.equal(plan.selectedStem, 'mixture');
  assert.equal(plan.roleEvidence, 'whole-mixture-only');
  assert.ok(plan.blockers.includes('BASELINE_NOT_PRODUCT_CANDIDATE'));
  assert.ok(plan.blockers.includes('MIXTURE_ROLE_EXTRACTION_UNAVAILABLE'));
});

test('historical register gate is rejected as role evidence for every role', () => {
  for (const role of ['lead', 'rhythm', 'bass']) {
    const plan = planAstraAudioEngine({ candidateId: 'v5-register-gate', role });
    assert.equal(plan.candidateStatus, 'rejected-role-evidence');
    assert.equal(plan.stageGraph.find((item) => item.stage === 'extraction').planned, false);
    assert.ok(plan.blockers.includes('REGISTER_IS_NOT_ROLE_EVIDENCE'));
  }
});

test('isolated role still requires authorized provenance and does not self-authorize execution', () => {
  const plan = planAstraAudioEngine({
    candidateId: 'whole-mix-basic-pitch',
    role: 'lead',
    sourceContext: 'isolated-requested-role',
  });
  assert.equal(plan.selectedStem, 'input');
  assert.equal(plan.roleEvidence, 'caller-declared-isolated-role-requires-authorized-provenance');
  assert.ok(plan.blockers.includes('ISOLATED_ROLE_PROVENANCE_REQUIRED'));
  assert.equal(plan.invokesModel, false);
  assert.equal(plan.opensAudio, false);
});

test('preflight is deterministic and returns copies that cannot mutate the registry', () => {
  const first = listAstraAudioEngineCandidates();
  first[0].capabilities.bassStem = true;
  const second = listAstraAudioEngineCandidates();
  assert.equal(second[0].capabilities.bassStem, false);
  assert.deepEqual(
    planAstraAudioEngine({ candidateId: 'htdemucs6s-basic-pitch', role: 'bass' }),
    planAstraAudioEngine({ candidateId: 'htdemucs6s-basic-pitch', role: 'bass' }),
  );
});

test('unknown candidates and unsupported roles fail before any execution plan is formed', () => {
  assert.throws(
    () => planAstraAudioEngine({ candidateId: 'imaginary-model', role: 'lead' }),
    /Unknown/,
  );
  assert.throws(
    () => planAstraAudioEngine({ candidateId: 'whole-mix-basic-pitch', role: 'drums' }),
    /role must/,
  );
});

