import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

test('V2 CPU budget is exact, bounded and authorizes no real training', () => {
  const bytes = readFileSync(new URL('../../docs/astra/GUITARTECHS_V2_CPU_BUDGET_V1.json', import.meta.url));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), '8705df7cde4456dc17b5973d84404981387a322ea195a3f995a72ae6b236b430');
  const receipt = JSON.parse(bytes.toString('utf8'));
  assert.equal(receipt.selected.sequenceFrames, 200);
  assert.equal(receipt.selected.batchSequences, 32);
  assert.equal(receipt.selected.microbatchSequences, 1);
  assert.equal(receipt.selected.epochsPerFold, 1000);
  assert.equal(receipt.selected.maxOptimizerStepsPerFold, 2000);
  assert.equal(receipt.selected.supervisedFramePositionsPerFold.P1, 8200000);
  assert.equal(receipt.selected.supervisedFramePositionsPerFold.P2, 8000000);
  assert.equal(receipt.selected.validationCheckpointsPerFold, 50);
  assert.equal(receipt.selected.runnerTimeoutMinutes, 345);
  assert.equal(receipt.guards.realTrainingAuthorized, false);
  assert.equal(receipt.guards.p3MayBeOpened, false);
});
