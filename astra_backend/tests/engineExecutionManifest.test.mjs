import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

import {
  getFrozenAstraEngineIdentity,
  validateAstraEngineExecutionManifest,
} from '../engineExecutionManifest.mjs';

const manifestUrl = new URL('../../docs/astra/ASTRA_ENGINE_EXECUTION_MANIFEST_V1.json', import.meta.url);

function manifest() {
  return JSON.parse(readFileSync(manifestUrl, 'utf8'));
}

test('frozen identities match the verified upstream refs and model blobs', () => {
  const identity = getFrozenAstraEngineIdentity();
  assert.equal(identity.audioSeparator.upstreamCommit, '99840eea955a19305413639c21ee58e320a1fd14');
  assert.equal(identity.demucs.packageVersion, '4.0.1');
  assert.equal(identity.demucs.configGitBlob, '651a0fa536038a3e6d650f7b2bcc0b50ff7a4be9');
  assert.equal(identity.basicPitch.modelGitBlob, '85a41befdd036e9b365a052b7c704c6810288b95');
});

test('current bass manifest is structurally valid but blocked before execution', () => {
  const result = validateAstraEngineExecutionManifest(manifest(), { role: 'bass' });
  assert.equal(result.manifestStructurallyValid, true);
  assert.equal(result.exactKnownIdentitiesMatch, true);
  assert.equal(result.developmentExecutionReady, false);
  assert.equal(result.customerDeliveryEligible, false);
  assert.ok(result.blockers.includes('PACKAGE_LOCK_IDENTITY_MISSING'));
  assert.ok(result.blockers.includes('DEMUCS_WEIGHT_TERMS_UNRESOLVED'));
  assert.ok(result.blockers.includes('MODEL_ARTIFACTS_NOT_VERIFIED_ON_ASTRA'));
});

test('lead and rhythm remain blocked by the unresolved role distinction', () => {
  for (const role of ['lead', 'rhythm']) {
    const result = validateAstraEngineExecutionManifest(manifest(), { role });
    assert.ok(result.blockers.includes('LEAD_RHYTHM_DISTINCTION_UNAVAILABLE'));
  }
});

test('validator performs no audio, model, or network work', () => {
  const result = validateAstraEngineExecutionManifest(manifest(), { role: 'bass' });
  assert.equal(result.invokesModel, false);
  assert.equal(result.opensAudio, false);
  assert.equal(result.performsNetworkAccess, false);
});

test('substituting a package or model identity fails closed', () => {
  const wrongPackage = manifest();
  wrongPackage.execution.demucs.packageVersion = '4.1.0';
  assert.throws(
    () => validateAstraEngineExecutionManifest(wrongPackage, { role: 'bass' }),
    /frozen Astra identity/,
  );

  const wrongModel = manifest();
  wrongModel.execution.basicPitch.modelGitBlob = '0'.repeat(40);
  assert.throws(
    () => validateAstraEngineExecutionManifest(wrongModel, { role: 'bass' }),
    /frozen Astra identity/,
  );
});

test('historical weight observation cannot be relabeled as Astra verification', () => {
  const current = manifest();
  current.evidence.modelArtifactsVerifiedOnAstra = false;
  const result = validateAstraEngineExecutionManifest(current, { role: 'bass' });
  assert.ok(result.blockers.includes('MODEL_ARTIFACTS_NOT_VERIFIED_ON_ASTRA'));
});

test('development manifest can never authorize customer delivery', () => {
  const unsafe = manifest();
  unsafe.policy.customerDeliveryAllowed = true;
  assert.throws(
    () => validateAstraEngineExecutionManifest(unsafe, { role: 'bass' }),
    /must remain false/,
  );
});

test('validation is deterministic and the frozen identity accessor returns copies', () => {
  const first = getFrozenAstraEngineIdentity();
  first.demucs.modelName = 'mutated';
  assert.equal(getFrozenAstraEngineIdentity().demucs.modelName, 'htdemucs_6s');
  assert.deepEqual(
    validateAstraEngineExecutionManifest(manifest(), { role: 'bass' }),
    validateAstraEngineExecutionManifest(manifest(), { role: 'bass' }),
  );
});
