import test from 'node:test';
import assert from 'node:assert/strict';

import {
  REQUIRED_STRATA,
  validateTrustFlagHoldoutStudyManifest,
} from '../trustFlagHoldoutProtocol.mjs';

function hashFor(namespace, n) {
  const seed = `${namespace}-${n}`;
  let out = '';
  for (let i = 0; i < 64; i += 1) {
    out += ((seed.charCodeAt(i % seed.length) + i) % 16).toString(16);
  }
  return out;
}

function phaseRows(phase) {
  const rows = [];
  let index = 0;
  for (const [stratum, count] of Object.entries(REQUIRED_STRATA)) {
    for (let i = 0; i < count; i += 1) {
      rows.push({
        id: `${phase}-${stratum}-${i}`,
        stratum,
        sourceAssetHashes: [hashFor(phase, index)],
        groundTruthRoleCondition: stratum,
        provenance: { syntheticFixture: true, phase },
      });
      index += 1;
    }
  }
  return rows;
}

function manifest() {
  return {
    schemaVersion: 1,
    thresholdDefined: false,
    automaticCorrectionAuthorized: false,
    productionDeliveryAuthorized: false,
    calibration: phaseRows('calibration'),
    holdout: phaseRows('holdout'),
  };
}

test('admits balanced disjoint calibration and holdout cohorts without defining a threshold', () => {
  const result = validateTrustFlagHoldoutStudyManifest(manifest());
  assert.equal(result.admitted, true);
  assert.equal(result.calibrationCaseCount, 48);
  assert.equal(result.holdoutCaseCount, 48);
  assert.equal(result.protocolContract.candidateRuleMustBeFrozenBeforeHoldout, true);
  assert.equal(result.protocolContract.automaticCorrectionAuthorized, false);
});

test('rejects a study that already contains a trust threshold', () => {
  const m = manifest();
  m.thresholdDefined = true;
  assert.throws(
    () => validateTrustFlagHoldoutStudyManifest(m),
    /THRESHOLD_UNDEFINED/,
  );
});

test('rejects calibration to holdout source leakage', () => {
  const m = manifest();
  m.holdout[0].sourceAssetHashes = [...m.calibration[0].sourceAssetHashes];
  assert.throws(
    () => validateTrustFlagHoldoutStudyManifest(m),
    /CALIBRATION_HOLDOUT_SOURCE_LEAKAGE/,
  );
});

test('rejects any source hash already used in prior development such as S0', () => {
  const m = manifest();
  const forbidden = m.calibration[3].sourceAssetHashes[0];
  assert.throws(
    () => validateTrustFlagHoldoutStudyManifest(
      m,
      { forbiddenPriorSourceHashes: [forbidden] },
    ),
    /PRIOR_SOURCE_LEAKAGE/,
  );
});

test('rejects underrepresented hard strata', () => {
  const m = manifest();
  m.holdout = m.holdout.filter(
    (row) => !(row.stratum === 'duplicate_role_bass' && row.id.endsWith('-5')),
  );
  assert.throws(
    () => validateTrustFlagHoldoutStudyManifest(m),
    /duplicate_role_bass/,
  );
});

test('rejects duplicate case ids across calibration and holdout', () => {
  const m = manifest();
  m.holdout[0].id = m.calibration[0].id;
  assert.throws(
    () => validateTrustFlagHoldoutStudyManifest(m),
    /duplicate case id/,
  );
});

test('rejects malformed source hashes rather than silently accepting identity drift', () => {
  const m = manifest();
  m.calibration[0].sourceAssetHashes = ['not-a-sha'];
  assert.throws(
    () => validateTrustFlagHoldoutStudyManifest(m),
    /SHA-256/,
  );
});
