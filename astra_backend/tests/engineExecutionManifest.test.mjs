import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

import {
  getFrozenAstraEngineIdentity,
  validateAstraEngineExecutionManifest,
  verifyAstraEngineDependencyLock,
} from '../engineExecutionManifest.mjs';

const manifestUrl = new URL('../../docs/astra/ASTRA_ENGINE_EXECUTION_MANIFEST_V1.json', import.meta.url);
const lockUrl = new URL('../engine/requirements.lock', import.meta.url);

function manifest() {
  return JSON.parse(readFileSync(manifestUrl, 'utf8'));
}

test('frozen identities match the verified upstream refs and model blobs', () => {
  const identity = getFrozenAstraEngineIdentity();
  assert.equal(identity.runtime.separatorEntryPoint, 'demucs-cli-direct');
  assert.equal(identity.runtime.packageLockSha256, 'a5614dbfad0be96aadc0d76297b6a59abe4e09c80bf2d6a484e53a14a58d38a7');
  assert.equal(identity.demucs.packageVersion, '4.0.1');
  assert.equal(identity.demucs.configGitBlob, '651a0fa536038a3e6d650f7b2bcc0b50ff7a4be9');
  assert.equal(identity.basicPitch.modelGitBlob, '85a41befdd036e9b365a052b7c704c6810288b95');
});

test('current bass manifest has a resolved lock but remains blocked before execution', () => {
  const result = validateAstraEngineExecutionManifest(manifest(), { role: 'bass' });
  assert.equal(result.manifestStructurallyValid, true);
  assert.equal(result.exactKnownIdentitiesMatch, true);
  assert.equal(result.developmentExecutionReady, false);
  assert.equal(result.customerDeliveryEligible, false);
  assert.ok(!result.blockers.includes('PACKAGE_LOCK_IDENTITY_MISSING'));
  assert.ok(result.blockers.includes('PACKAGE_INSTALLATION_UNVERIFIED'));
  assert.ok(result.blockers.includes('DEMUCS_WEIGHT_TERMS_UNRESOLVED'));
  assert.ok(result.blockers.includes('MODEL_ARTIFACTS_NOT_VERIFIED_ON_ASTRA'));
});

test('dependency lock is complete, hashed, direct-Demucs, and uses the safe ABI pins', () => {
  const lockText = readFileSync(lockUrl, 'utf8');
  const result = verifyAstraEngineDependencyLock(lockText);
  const digest = createHash('sha256').update(lockText).digest('hex');
  assert.equal(digest, manifest().evidence.packageLock.sha256);
  assert.equal(result.packageCount, 57);
  assert.equal(result.criticalPackages.numpy, '1.26.4');
  assert.equal(result.criticalPackages.torch, '2.11.0+cpu');
  assert.equal(result.criticalPackages.torchaudio, '2.11.0+cpu');
  assert.equal(result.criticalPackages['tflite-runtime'], '2.14.0');
  assert.equal(result.audioSeparatorPresent, false);
  assert.equal(result.tensorflowPresent, false);
});

test('dependency lock rejects ABI drift and wrapper reintroduction', () => {
  const lockText = readFileSync(lockUrl, 'utf8');
  assert.throws(
    () => verifyAstraEngineDependencyLock(lockText.replace('numpy==1.26.4', 'numpy==2.2.6')),
    /frozen Astra identity/,
  );
  assert.throws(
    () => verifyAstraEngineDependencyLock(lockText.replace('demucs==4.0.1', 'audio-separator==0.30.2')),
    /(frozen Astra identity|must not re-enter)/,
  );
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

test('manifest rejects package-lock identity substitution', () => {
  const wrongLock = manifest();
  wrongLock.evidence.packageLock.sha256 = '0'.repeat(64);
  assert.throws(
    () => validateAstraEngineExecutionManifest(wrongLock, { role: 'bass' }),
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
