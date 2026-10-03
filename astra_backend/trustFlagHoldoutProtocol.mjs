const REQUIRED_STRATA = Object.freeze({
  complementary_both_present: 12,
  target_absent_guitar: 6,
  target_absent_bass: 6,
  duplicate_role_guitar: 6,
  duplicate_role_bass: 6,
  hard_complementary_confuser: 12,
});

const PHASES = ['calibration', 'holdout'];

function assertString(value, field) {
  if (typeof value !== 'string' || value.length === 0) {
    throw new Error(`${field} must be a non-empty string.`);
  }
  return value;
}

function assertSha256(value, field) {
  assertString(value, field);
  if (!/^[a-f0-9]{64}$/.test(value)) {
    throw new Error(`${field} must be a lowercase SHA-256 hex digest.`);
  }
  return value;
}

function normalizeCase(row, phase, index) {
  const id = assertString(row?.id, `${phase}[${index}].id`);
  const stratum = assertString(row?.stratum, `${phase}[${index}].stratum`);
  if (!(stratum in REQUIRED_STRATA)) {
    throw new Error(`${phase}[${index}].stratum is not admitted by protocol.`);
  }
  const sourceAssetHashes = Array.isArray(row?.sourceAssetHashes)
    ? [...new Set(row.sourceAssetHashes.map((hash, i) => (
      assertSha256(hash, `${phase}[${index}].sourceAssetHashes[${i}]`)
    )))]
    : [];
  if (sourceAssetHashes.length === 0) {
    throw new Error(`${phase}[${index}] must declare at least one source asset hash.`);
  }
  return {
    id,
    stratum,
    sourceAssetHashes,
    groundTruthRoleCondition: assertString(
      row?.groundTruthRoleCondition,
      `${phase}[${index}].groundTruthRoleCondition`,
    ),
    provenance: row?.provenance && typeof row.provenance === 'object'
      ? structuredClone(row.provenance)
      : {},
  };
}

function countStrata(rows) {
  const counts = Object.fromEntries(Object.keys(REQUIRED_STRATA).map((key) => [key, 0]));
  for (const row of rows) counts[row.stratum] += 1;
  return counts;
}

function assertMinimumStrata(rows, phase) {
  const counts = countStrata(rows);
  for (const [stratum, minimum] of Object.entries(REQUIRED_STRATA)) {
    if (counts[stratum] < minimum) {
      throw new Error(
        `${phase} requires at least ${minimum} cases in ${stratum}; received ${counts[stratum]}.`,
      );
    }
  }
  return counts;
}

function collectHashes(rows) {
  const out = new Set();
  for (const row of rows) {
    for (const hash of row.sourceAssetHashes) out.add(hash);
  }
  return out;
}

function intersection(a, b) {
  return [...a].filter((value) => b.has(value));
}

export function validateTrustFlagHoldoutStudyManifest(
  manifest = {},
  { forbiddenPriorSourceHashes = [] } = {},
) {
  if (manifest?.schemaVersion !== 1) {
    throw new Error('trust/flag holdout study manifest schemaVersion must be 1.');
  }
  if (manifest?.thresholdDefined !== false) {
    throw new Error('HOLDOUT_ADMISSION_REQUIRES_THRESHOLD_UNDEFINED');
  }
  if (manifest?.automaticCorrectionAuthorized !== false) {
    throw new Error('HOLDOUT_ADMISSION_FORBIDS_AUTOMATIC_CORRECTION');
  }
  if (manifest?.productionDeliveryAuthorized !== false) {
    throw new Error('HOLDOUT_ADMISSION_FORBIDS_PRODUCTION_DELIVERY');
  }

  const normalized = {};
  const ids = new Set();

  for (const phase of PHASES) {
    const rows = Array.isArray(manifest?.[phase]) ? manifest[phase] : [];
    normalized[phase] = rows.map((row, index) => normalizeCase(row, phase, index));
    for (const row of normalized[phase]) {
      if (ids.has(row.id)) throw new Error(`duplicate case id across study: ${row.id}`);
      ids.add(row.id);
    }
    normalized[`${phase}StratumCounts`] = assertMinimumStrata(normalized[phase], phase);
  }

  const calibrationHashes = collectHashes(normalized.calibration);
  const holdoutHashes = collectHashes(normalized.holdout);
  const crossPhase = intersection(calibrationHashes, holdoutHashes);
  if (crossPhase.length > 0) {
    throw new Error(`CALIBRATION_HOLDOUT_SOURCE_LEAKAGE:${crossPhase.sort().join(',')}`);
  }

  const forbidden = new Set(
    forbiddenPriorSourceHashes.map((hash, i) => assertSha256(hash, `forbiddenPriorSourceHashes[${i}]`)),
  );
  const allStudyHashes = new Set([...calibrationHashes, ...holdoutHashes]);
  const priorOverlap = intersection(allStudyHashes, forbidden);
  if (priorOverlap.length > 0) {
    throw new Error(`PRIOR_SOURCE_LEAKAGE:${priorOverlap.sort().join(',')}`);
  }

  return {
    protocolContract: {
      name: 'astra-transcription-trust-flag-holdout-study-admission',
      version: 1,
      thresholdDefined: false,
      calibrationRequiredBeforeCandidateRule: true,
      candidateRuleMustBeFrozenBeforeHoldout: true,
      holdoutOneShotEvaluationRequired: true,
      sourceDisjointFromPriorDevelopmentRequired: true,
      calibrationHoldoutSourceDisjointRequired: true,
      automaticCorrectionAuthorized: false,
      productionDeliveryAuthorized: false,
    },
    requiredMinimumStrata: structuredClone(REQUIRED_STRATA),
    calibrationCaseCount: normalized.calibration.length,
    holdoutCaseCount: normalized.holdout.length,
    calibrationStratumCounts: normalized.calibrationStratumCounts,
    holdoutStratumCounts: normalized.holdoutStratumCounts,
    calibrationDistinctSourceHashCount: calibrationHashes.size,
    holdoutDistinctSourceHashCount: holdoutHashes.size,
    sourceLeakageDetected: false,
    admitted: true,
  };
}

export { REQUIRED_STRATA };
