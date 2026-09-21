import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

function gitBlobSha(bytes) {
  const prefix = Buffer.from(`blob ${bytes.length}\0`);
  return createHash('sha1').update(prefix).update(bytes).digest('hex');
}

test('bounded real-training implementation identities are frozen before media access', () => {
  const script = readFileSync(new URL('../guitartechs_real_training/real_training.py', import.meta.url));
  const corrections = readFileSync(new URL('../../docs/astra/GUITARTECHS_PRIMARY_ALIGNMENT_CORRECTIONS_V1.json', import.meta.url));
  const auth = readFileSync(new URL('../../docs/astra/GUITARTECHS_REAL_TRAINING_AUTHORIZATION_V1.json', import.meta.url));
  const implementation = JSON.parse(readFileSync(new URL('../../docs/astra/GUITARTECHS_REAL_TRAINING_IMPLEMENTATION_V1.json', import.meta.url), 'utf8'));
  assert.equal(gitBlobSha(script), '6ce81a0bd82025357497e4dff780ff888fad7627');
  assert.equal(gitBlobSha(corrections), '9090d465422ebf5d4fdf170693fe0936934f3073');
  assert.equal(createHash('sha256').update(auth).digest('hex'), '175de606db2276dd745d697e1e996e6c533a7ad6542d258ed66e2a8bbb6ea0d0');
  assert.equal(JSON.parse(corrections).acceptedPrimaryCount, 256);
  assert.equal(implementation.source.trainingScriptGitBlob, '6ce81a0bd82025357497e4dff780ff888fad7627');
  assert.equal(implementation.datasetPreparation.alignmentCorrectionMapGitBlob, '9090d465422ebf5d4fdf170693fe0936934f3073');
  assert.equal(implementation.guards.sealedP3MayBeOpened, false);
  assert.equal(implementation.guards.paidComputeAuthorized, false);
  assert.equal(implementation.training.maxIterationsPerFold, 2500);
  assert.equal(implementation.checkpointSelection.captureCount, 10);
});
