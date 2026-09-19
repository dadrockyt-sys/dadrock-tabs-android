import test from 'node:test';
import assert from 'node:assert/strict';

import {
  evaluateAstraSeparationRightsCandidate,
  listAstraSeparationRightsCandidates,
} from '../separationCandidateRightsRegistry.mjs';

test('7A registry freezes the screened candidate identities and no candidate is inventory-qualified', () => {
  const candidates = listAstraSeparationRightsCandidates();
  assert.deepEqual(
    candidates.map((candidate) => candidate.id),
    [
      'spleeter-5stems-v2.3.0',
      'open-unmix-umxhq-v1.0.0',
      'stemsplit-htdemucs6s-onnx',
      'adityalakhani-htdemucs6s-guitar-ft',
    ],
  );
  assert.equal(
    candidates.some((candidate) => evaluateAstraSeparationRightsCandidate(candidate.id).inventoryQualified),
    false,
  );
});

test('Spleeter has explicit MIT pretrained-model terms but fails the required guitar-stem capability', () => {
  const result = evaluateAstraSeparationRightsCandidate('spleeter-5stems-v2.3.0');
  assert.equal(result.candidate.rights.commercialInferencePermitted, true);
  assert.equal(result.candidate.capabilities.bassStem, true);
  assert.equal(result.candidate.capabilities.genericGuitarStem, false);
  assert.ok(result.blockers.includes('GUITAR_STEM_UNAVAILABLE'));
  assert.equal(result.inventoryQualified, false);
});

test('Open-Unmix umxhq cannot promote other into guitar and remains rights-conservative', () => {
  const result = evaluateAstraSeparationRightsCandidate('open-unmix-umxhq-v1.0.0');
  assert.equal(result.candidate.capabilities.genericGuitarStem, false);
  assert.ok(result.blockers.includes('GUITAR_STEM_UNAVAILABLE'));
  assert.ok(result.blockers.includes('COMMERCIAL_MODEL_ARTIFACT_RIGHTS_UNRESOLVED'));
});

test('StemSplit ONNX conversion keeps exact artifact identity but cannot cure unresolved base-weight rights', () => {
  const result = evaluateAstraSeparationRightsCandidate('stemsplit-htdemucs6s-onnx');
  assert.equal(
    result.candidate.source.artifactSha256,
    '48f8e84945579f8ab340e083339e9221e03785dbe733a52c388200b6d3ca779a',
  );
  assert.equal(result.candidate.capabilities.genericGuitarStem, true);
  assert.equal(result.candidate.lineage.dependsOnFrozenHtdemucs6s, true);
  assert.ok(result.blockers.includes('UPSTREAM_WEIGHT_RIGHTS_UNRESOLVED'));
  assert.equal(result.inventoryQualified, false);
});

test('guitar fine-tune cannot self-authorize through its downstream Apache label', () => {
  const result = evaluateAstraSeparationRightsCandidate('adityalakhani-htdemucs6s-guitar-ft');
  assert.equal(
    result.candidate.source.artifactSha256,
    '4fde369e41582ba5c2759b6ab926a44af467c64d4566bf914374ab267b19260e',
  );
  assert.equal(result.candidate.lineage.dependsOnFrozenHtdemucs6s, true);
  assert.ok(result.blockers.includes('UPSTREAM_WEIGHT_RIGHTS_UNRESOLVED'));
  assert.ok(result.blockers.includes('COMMERCIAL_MODEL_ARTIFACT_RIGHTS_UNRESOLVED'));
});

test('generic guitar output never becomes lead or rhythm role evidence', () => {
  for (const role of ['lead', 'rhythm']) {
    const result = evaluateAstraSeparationRightsCandidate('stemsplit-htdemucs6s-onnx', { role });
    assert.ok(result.blockers.includes('LEAD_RHYTHM_DISTINCTION_UNAVAILABLE'));
    assert.equal(result.customerDeliveryEligible, false);
  }
});

test('7A screening performs no model, audio, download, or network runtime work', () => {
  for (const candidate of listAstraSeparationRightsCandidates()) {
    const result = evaluateAstraSeparationRightsCandidate(candidate.id);
    assert.equal(result.developmentExecutionReady, false);
    assert.equal(result.customerDeliveryEligible, false);
    assert.equal(result.downloadsArtifact, false);
    assert.equal(result.importsModel, false);
    assert.equal(result.invokesModel, false);
    assert.equal(result.opensAudio, false);
    assert.equal(result.performsNetworkAccess, false);
  }
});

test('unknown candidate and unsupported role fail closed', () => {
  assert.throws(
    () => evaluateAstraSeparationRightsCandidate('not-a-candidate'),
    /Unknown Astra separation-rights candidate/,
  );
  assert.throws(
    () => evaluateAstraSeparationRightsCandidate('spleeter-5stems-v2.3.0', { role: 'other' }),
    /role must be bass, lead, or rhythm/,
  );
});
