import test from 'node:test';
import assert from 'node:assert/strict';

import {
  evaluateGuitarTechsDevelopmentAcquisitionRequest,
  getGuitarTechsDevelopmentAcquisitionContract,
} from '../guitarTechsDevelopmentAcquisition.mjs';

function exactDevelopmentArchives() {
  return getGuitarTechsDevelopmentAcquisitionContract()
    .developmentArchives.map((archive) => ({ ...archive }));
}

function authorized(overrides = {}) {
  const contract = getGuitarTechsDevelopmentAcquisitionContract();
  return {
    record: contract.record,
    version: contract.version,
    authorizationScope: contract.authorizationScope,
    developmentMediaAcquisitionAuthorized: true,
    requestedArchives: [exactDevelopmentArchives()[0]],
    ...overrides,
  };
}

test('contract itself is no-action and keeps P3 sealed', () => {
  const result = evaluateGuitarTechsDevelopmentAcquisitionRequest();
  assert.equal(result.contract.downloadsMedia, false);
  assert.equal(result.contract.opensMedia, false);
  assert.equal(result.contract.extractsMedia, false);
  assert.equal(result.contract.trainsModel, false);
  assert.equal(result.contract.opensP3, false);
  assert.equal(result.p3Sealed, true);
  assert.equal(result.customerDeliveryEligible, false);
});

test('exact P1/P2 subset still requires explicit scoped authorization', () => {
  const request = authorized({ developmentMediaAcquisitionAuthorized: false });
  const result = evaluateGuitarTechsDevelopmentAcquisitionRequest(request);
  assert.equal(result.acquisitionPlanAccepted, false);
  assert.ok(result.blockers.includes('GUITAR_TECHS_DEVELOPMENT_MEDIA_ACQUISITION_NOT_AUTHORIZED'));
});

test('P3 is categorically rejected even when authorization is true', () => {
  const contract = getGuitarTechsDevelopmentAcquisitionContract();
  const result = evaluateGuitarTechsDevelopmentAcquisitionRequest(authorized({
    requestedArchives: [{ ...contract.sealedArchives[0] }],
  }));
  assert.equal(result.acquisitionPlanAccepted, false);
  assert.ok(result.blockers.includes('GUITAR_TECHS_P3_SEALED'));
  assert.equal(result.p3Sealed, true);
});

test('unknown or substituted P1/P2 identity fails closed', () => {
  const substituted = exactDevelopmentArchives()[0];
  substituted.bytes += 1;
  let result = evaluateGuitarTechsDevelopmentAcquisitionRequest(authorized({
    requestedArchives: [substituted],
  }));
  assert.ok(result.blockers.includes('GUITAR_TECHS_DEVELOPMENT_ARCHIVE_IDENTITY_MISMATCH'));

  result = evaluateGuitarTechsDevelopmentAcquisitionRequest(authorized({
    requestedArchives: [{ file: 'P4_surprise.zip', bytes: 1, md5: '0'.repeat(32), performer: 'P4', category: 'music' }],
  }));
  assert.ok(result.blockers.includes('GUITAR_TECHS_DEVELOPMENT_ARCHIVE_IDENTITY_MISMATCH'));
});

test('duplicate archive requests fail closed', () => {
  const archive = exactDevelopmentArchives()[0];
  const result = evaluateGuitarTechsDevelopmentAcquisitionRequest(authorized({
    requestedArchives: [{ ...archive }, { ...archive }],
  }));
  assert.ok(result.blockers.includes('GUITAR_TECHS_DEVELOPMENT_ARCHIVE_DUPLICATE'));
});

test('authorized exact development subset is accepted only as a no-action plan', () => {
  const result = evaluateGuitarTechsDevelopmentAcquisitionRequest(authorized());
  assert.equal(result.acquisitionPlanAccepted, true);
  assert.equal(result.fullDevelopmentSetSelected, false);
  assert.deepEqual(result.blockers, []);
  assert.ok(result.nextRequiredEvidence.includes('COMPUTE_ASTRA_SHA256_BEFORE_EXTRACTION'));
  assert.equal(result.contract.downloadsMedia, false);
});

test('all eight exact P1/P2 archives are recognized as the full development set', () => {
  const result = evaluateGuitarTechsDevelopmentAcquisitionRequest(authorized({
    requestedArchives: exactDevelopmentArchives(),
  }));
  assert.equal(result.acquisitionPlanAccepted, true);
  assert.equal(result.fullDevelopmentSetSelected, true);
  assert.equal(result.requestedArchiveCount, 8);
  assert.equal(result.p3Sealed, true);
});

test('contract reads are deterministic and defensive', () => {
  const first = getGuitarTechsDevelopmentAcquisitionContract();
  first.developmentArchives[0].bytes = 1;
  const second = getGuitarTechsDevelopmentAcquisitionContract();
  assert.equal(second.developmentArchives[0].bytes, 981741162);
  assert.deepEqual(second, getGuitarTechsDevelopmentAcquisitionContract());
});
