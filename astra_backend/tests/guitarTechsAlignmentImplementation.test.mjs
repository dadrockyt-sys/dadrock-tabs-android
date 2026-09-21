import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

test('Guitar-TECHS alignment implementation is frozen before real alignment', () => {
  const source = readFileSync(new URL('../guitartechs_alignment/align_development.py', import.meta.url));
  const digest = createHash('sha256').update(source).digest('hex');
  assert.equal(digest, 'b084da0900acf9bd4ec61386a4a928350af0e138c9ed36ef3fbafb15539bc330');

  const contractBytes = readFileSync(new URL('../../docs/astra/GUITARTECHS_ALIGNMENT_IMPLEMENTATION_V1.json', import.meta.url));
  assert.equal(createHash('sha256').update(contractBytes).digest('hex'), 'b33dd0fd220fcef4a459cc47277f48cf90c0acd320e523c3afcea5fc52a8a26f');
  const contract = JSON.parse(contractBytes.toString('utf8'));
  assert.equal(contract.scriptSha256, 'b084da0900acf9bd4ec61386a4a928350af0e138c9ed36ef3fbafb15539bc330');
  assert.equal(contract.sourceContractSha256, '09436268922e0d24332b7e3234225d54a0f28e58e23b55ea71227eeab1b1e81f');
  assert.deepEqual(contract.lagEstimator.searchMs, [-100, 100]);
  assert.equal(contract.lagEstimator.stepMs, 1);
  assert.equal(contract.acceptance.minimumMidiOnsetGroups, 30);
  assert.equal(contract.acceptance.minimumMatchedFraction, 0.8);
  assert.equal(contract.acceptance.matchToleranceMs, 20);
  assert.equal(contract.acceptance.maximumMedianAbsoluteResidualMs, 10);
  assert.equal(contract.acceptance.maximumBootstrapLagMadMs, 5);
  assert.equal(contract.guards.p3MayBeOpened, false);
  assert.equal(contract.guards.trainingAuthorized, false);
  assert.equal(contract.guards.customerDeliveryEligible, false);
});
